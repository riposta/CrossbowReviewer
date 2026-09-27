# CrossbowReviewer

A code reviewer that makes **decisions, not comments**. The inference server runs
[**CrossbowReviewer-9B**](https://huggingface.co/riposta/CrossbowReviewer-9B), a Qwen3.5-9B fine-tune. In one forward
pass it answers up to 107 rules about a code file: SOLID and design principles, patterns, correctness, security,
performance, readability, testing, API design and language idioms. Each answer comes with a calibrated probability.
The API follows the [Jev](https://docs.typesafe.ai/concepts/system-one) `/v1/systemone` request schema.

- **Model, benchmarks, limitations:** [huggingface.co/riposta/CrossbowReviewer-9B](https://huggingface.co/riposta/CrossbowReviewer-9B)
- **Languages:** Java, Python, TypeScript, JavaScript, Go, C#, Rust
- **Backends:**
  - **transformers:** BF16 safetensors, ~0.2 s per file on an A100.
  - **llama.cpp:** Q8_0 GGUF, fits a 12 GB GPU or a Mac.

## Quick start

```bash
uv run uvicorn server:app --port 8000     # transformers backend; first request downloads the model
```

llama.cpp backend (Q8_0 GGUF, 9.5 GB):

```bash
huggingface-cli download riposta/CrossbowReviewer-9B gguf/CrossbowReviewer-9B-Q8_0.gguf \
  tokenizer.json tokenizer_config.json decision_config.json --local-dir CrossbowReviewer-9B
llama-server -m CrossbowReviewer-9B/gguf/CrossbowReviewer-9B-Q8_0.gguf --port 8080 -ngl 99 -c 16384
BACKEND=llamacpp LLAMA_URL=http://127.0.0.1:8080 MODEL=./CrossbowReviewer-9B uv run uvicorn server:app --port 8000
```

The two backends return the same decisions: 79/79 identical choices on a parity set, with a mean probability
difference of 0.004.

## API

```bash
curl -s localhost:8000/v1/systemone -H 'content-type: application/json' -d '{
  "state": {"language": "python",
            "code": "def find(db, name):\n    return db.execute(f\"SELECT * FROM users WHERE name = '\''{name}'\''\")"},
  "questions": {
    "injection": {"type": "noul", "instructions": "Is the code free of injection vulnerabilities (SQL, command, LDAP, template)?"},
    "severity": {"type": "score", "instructions": "How severe is the most important issue?",
                 "criteria": {"1": "None or cosmetic", "2": "Minor", "3": "Moderate", "4": "Major", "5": "Critical"}}}}'
```

```json
{"decisions": {
  "injection": {"choice": "no", "confidence": 0.99, "distribution": {"yes": 0.01, "no": 0.99}},
  "severity":  {"choice": "5", "confidence": 0.61, "distribution": {"1": 0.01, "2": 0.02, "3": 0.06, "4": 0.30, "5": 0.61}}}}
```

- **Without `questions`,** the server asks every rule for `state.language`, or only the language-agnostic rules when
  `language` is missing.
- **Question types:** `noul` (yes/no; `yes` = compliant), `choice` (2–26 named options) and `score` (2–10 levels).
- **Invalid requests** return HTTP 422.
- **Environment:** `MODEL` (a Hugging Face repo id or a local directory), `BACKEND` (`transformers` | `llamacpp`) and
  `LLAMA_URL`.

## How it works

Each question ends in an answer slot (`Answer:`). The server reads the logits of the allowed option letters at every
slot, divides them by the temperature from the model's `decision_config.json` and applies a softmax. No answer text is
generated.
- **transformers backend:** all slots come from one forward pass.
- **llama.cpp backend:** one request per slot on a growing token prefix. `llama-server`'s prompt cache means only the
  new tokens are evaluated.

## Rules

`rules.py` holds 120 rules in 12 categories and 2 aggregate questions (`primary_category`, `severity`).

| Category | Rules | Examples |
| --- | --- | --- |
| security | 23 | injection, xss, hardcoded_secrets, csrf, xxe, idor, ssrf, redos |
| idioms | 18 | Java Optional, Python mutable defaults, TS any, JS ===, Go goroutine leaks, C# async void, Rust unwrap |
| principles | 17 | SOLID, DRY, KISS, YAGNI, Law of Demeter, CQS, fail fast |
| patterns | 13 | pattern fit, god object, singleton abuse, feature envy, primitive obsession |
| clean_code | 11 | single abstraction level, flag arguments, hidden side effects, temporal coupling |
| testing | 9 | AAA, determinism, mocking, edge cases |
| correctness | 8 | null safety, off-by-one, resource leaks, concurrency, numeric |
| readability | 6 | naming, function size, nesting depth, magic numbers |
| performance | 5 | N+1, algorithmic complexity, blocking in async |
| error_handling | 4 | swallowed exceptions, error context, cleanup on failure |
| api_design | 4 | backward compatibility, immutable DTOs, idempotency |
| testability | 2 | hidden dependencies, injectable time/randomness |

## Results

![Three tests](https://huggingface.co/riposta/CrossbowReviewer-9B/resolve/main/docs/assets/three_tests.png)

The model beats Jev on real open-source code (balanced accuracy 0.78 vs 0.72) and is very well calibrated (ECE 0.006).
Reasoning models are more accurate, but take 25–55× longer.

![Quality vs latency](https://huggingface.co/riposta/CrossbowReviewer-9B/resolve/main/docs/assets/quality_vs_latency.png)

**Known weakness: security taint traps.** On OWASP Benchmark (human labels) the model recognizes only 26% of the
safe-but-scary-looking cases, and Jev and the base model are no better. Use it for design and quality rules, and
route a `no` on data-flow security rules (`injection`, `path_traversal`, `xss`, `ssrf`, `open_redirect`) to a
reasoning model.

![OWASP traps](https://huggingface.co/riposta/CrossbowReviewer-9B/resolve/main/docs/assets/owasp_traps.png)

## License

Apache 2.0.
