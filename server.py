"""CrossbowReviewer-9B: Jev-style code review decisions. No text generation: every question ends in an answer slot,
the logits of its option letters are read there, divided by a fitted temperature and softmaxed.

Model: https://huggingface.co/riposta/CrossbowReviewer-9B (full weights; fine-tuned from Qwen/Qwen3.5-9B-Base).

Backends:
  transformers (default)   safetensors weights, one forward pass per request (GPU, Apple MPS or CPU)
  llamacpp                 GGUF weights through a running llama-server; one request per slot on a growing token
                           prefix, and llama-server's prompt cache means each slot only evaluates its new tokens

  uv run uvicorn server:app --port 8000
  BACKEND=llamacpp LLAMA_URL=http://127.0.0.1:8080 uv run uvicorn server:app --port 8000
"""
import json
import math
import os
import string
import threading
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, model_validator
from transformers import AutoTokenizer

from rules import options, questions_for

MODEL = os.environ.get("MODEL", "riposta/CrossbowReviewer-9B")  # Hugging Face repo id or a local directory
BACKEND = os.environ.get("BACKEND", "transformers")
LLAMA_URL = os.environ.get("LLAMA_URL", "http://127.0.0.1:8080")
LETTERS = string.ascii_uppercase  # 26 options max (Jev allows 255)
HEADER = "You are a code review decision engine. Each question is answered with a single option letter.\n\nState:\n"


def render_question(name, q):
    lines = [f"{LETTERS[i]}. {o}" + (f": {q['criteria'][o]}" if q["type"] != "noul" else "")
             for i, o in enumerate(options(q))]
    return f"\n\n### {name}\n{q['instructions']}\n" + "\n".join(lines) + "\nAnswer:"


def encode(tok, state, questions):
    """Token ids for one request and the position of each answer slot (the model was trained on exactly this)."""
    ids = tok.encode(HEADER + json.dumps(state, ensure_ascii=False, indent=1), add_special_tokens=False)
    slots = []
    for name, q in questions.items():
        ids += tok.encode(render_question(name, q), add_special_tokens=False)
        slots.append(len(ids) - 1)
    return ids, slots


def decision_config(model):
    path = Path(model, "decision_config.json")
    if not path.exists():  # model from the Hugging Face Hub
        from huggingface_hub import hf_hub_download
        path = Path(hf_hub_download(model, "decision_config.json"))
    return json.loads(path.read_text())


class Decider:
    """Shared decision logic; backends only supply the option-letter logits at each slot."""

    def __init__(self, model=MODEL):
        self.tok = AutoTokenizer.from_pretrained(model)
        self.temperature = decision_config(model)["temperature"]
        self.letter_ids = [self._single_token(" " + c) for c in LETTERS]

    def _single_token(self, text):
        ids = self.tok.encode(text, add_special_tokens=False)
        assert len(ids) == 1, f"{text!r} is not a single token: {ids}"
        return ids[0]

    def slot_logits(self, state, questions):
        raise NotImplementedError

    def decide(self, state, questions):
        result = {}
        for (name, q), logits in zip(questions.items(), self.slot_logits(state, questions)):
            scaled = [z / self.temperature for z in logits]
            top = max(scaled)
            exp = [math.exp(z - top) for z in scaled]
            p = [e / sum(exp) for e in exp]
            opts = options(q)
            best = max(range(len(opts)), key=p.__getitem__)
            result[name] = {"choice": opts[best], "confidence": p[best], "distribution": dict(zip(opts, p))}
        return result


class TransformersDecider(Decider):
    def __init__(self, model=MODEL):
        super().__init__(model)
        import torch
        from transformers import AutoModelForCausalLM
        self.torch = torch
        dev = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        dtype = torch.float32 if dev == "cpu" else torch.bfloat16
        self.model = AutoModelForCausalLM.from_pretrained(model, dtype=dtype).to(dev).eval()

    def slot_logits(self, state, questions):
        torch = self.torch
        ids, slots = encode(self.tok, state, questions)
        dev = self.model.device
        with torch.no_grad():  # lm_head runs only at the slots, not over the vocabulary at every position
            logits = self.model(input_ids=torch.tensor([ids], device=dev),
                                logits_to_keep=torch.tensor(slots, device=dev)).logits[0]
        return [logits[i, self.letter_ids[:len(options(q))]].float().tolist() for i, q in enumerate(questions.values())]


class LlamaCppDecider(Decider):
    def __init__(self, model=MODEL, url=LLAMA_URL):
        super().__init__(model)
        import httpx
        self.http = httpx.Client(base_url=url, timeout=600)

    def slot_logits(self, state, questions):
        ids, slots = encode(self.tok, state, questions)
        out = []
        for q, slot in zip(questions.values(), slots):
            # temperature < 0: plain softmax of the logits, no sampler; the same token ids as the transformers path
            r = self.http.post("/completion", json={"prompt": ids[:slot + 1], "n_predict": 1, "n_probs": 64,
                                                    "temperature": -1, "cache_prompt": True})
            r.raise_for_status()
            top = {t["id"]: t["logprob"] for t in r.json()["completion_probabilities"][0]["top_logprobs"]}
            floor = min(top.values()) - 5  # a letter outside the top 64 is far less likely than the last listed token
            # log-probabilities differ from logits by one constant per slot, which cancels in the softmax
            out.append([top.get(self.letter_ids[i], floor) for i in range(len(options(q)))])
        return out


class Question(BaseModel):
    type: Literal["choice", "score", "noul"]
    instructions: str
    criteria: dict[str, str] = {}

    @model_validator(mode="after")
    def check_criteria(self):
        n = len(self.criteria)
        if self.type == "choice" and not 2 <= n <= len(LETTERS):
            raise ValueError(f"choice needs 2-{len(LETTERS)} criteria")
        if self.type == "score" and not 2 <= n <= 10:
            raise ValueError("score needs 2-10 levels")
        return self


class SystemOneRequest(BaseModel):
    state: dict
    questions: dict[str, Question] | None = None  # None -> built-in review questions for state['language']


app = FastAPI()
_decider = None
_lock = threading.Lock()  # one request at a time


@app.post("/v1/systemone")
def systemone(req: SystemOneRequest):
    global _decider
    questions = ({n: q.model_dump() for n, q in req.questions.items()} if req.questions
                 else questions_for(req.state.get("language")))
    with _lock:
        if _decider is None:
            _decider = LlamaCppDecider() if BACKEND == "llamacpp" else TransformersDecider()
        return {"decisions": _decider.decide(req.state, questions)}
