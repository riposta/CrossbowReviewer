"""Code review questions in Jev systemone form. Every rule is a noul: "yes" = the code is compliant.
Language-specific idioms carry "languages" and are asked only for code in those languages."""

LANGUAGES = ["java", "python", "typescript", "javascript", "go", "csharp", "rust"]

CATEGORIES = {
    "principles": {
        "srp": "Single Responsibility Principle: does each class/module have exactly one reason to change?",
        "ocp": "Open/Closed Principle: can behaviour be extended without modifying existing code?",
        "lsp": "Liskov Substitution Principle: are subtypes usable wherever their base types are, without breaking contracts?",
        "isp": "Interface Segregation Principle: is no client forced to depend on methods it does not use?",
        "dip": "Dependency Inversion Principle: does high-level code depend on abstractions rather than concrete implementations?",
        "dry": "DRY: is the code free of duplicated logic or knowledge?",
        "kiss": "KISS: is the code as simple as the problem allows, without needless complexity?",
        "yagni": "YAGNI: is the code free of speculative features, abstractions or configuration nobody uses?",
        "demeter": "Law of Demeter: does the code talk only to its direct collaborators (no a.getB().getC().run() chains)?",
        "composition_over_inheritance": "Is composition preferred over inheritance where inheritance is not a true is-a relationship?",
        "separation_of_concerns": "Are concerns (I/O, business logic, presentation, persistence) kept separate?",
        "cohesion_coupling": "Are modules highly cohesive and loosely coupled?",
        "encapsulation": "Is internal state properly encapsulated (no leaking of mutable internals, minimal public surface)?",
        "tell_dont_ask": "Tell, Don't Ask: does the code tell objects what to do instead of pulling their data to decide for them?",
        "cqs": "Command-Query Separation: do methods either change state or return data, but not both?",
        "fail_fast": "Does the code fail fast on invalid state or arguments instead of continuing silently?",
        "least_astonishment": "Principle of Least Astonishment: does the code behave the way its names and signatures suggest?",
    },
    "patterns": {
        "patterns_fit": "Are design patterns used appropriately: they fit the problem, are implemented correctly, and are not used for their own sake?",
        "god_object": "Is the code free of god objects that know or do too much?",
        "singleton_abuse": "Is the code free of singleton abuse and mutable global state?",
        "service_locator": "Is the code free of the service locator anti-pattern (dependencies are explicit)?",
        "anemic_domain": "Is the domain model free of anemia (behaviour lives with the data it operates on)?",
        "feature_envy": "Is the code free of feature envy (methods using another object's data more than their own)?",
        "primitive_obsession": "Is the code free of primitive obsession (domain concepts have their own types)?",
        "long_parameter_list": "Is the code free of long parameter lists?",
        "data_clumps": "Is the code free of data clumps (the same group of values passed around together)?",
        "shotgun_surgery": "Is the code free of shotgun surgery (one change does not require edits in many places)?",
        "refused_bequest": "Is the code free of refused bequest (subclasses use what they inherit)?",
        "type_switch": "Is the code free of switches/if-chains on type where polymorphism fits better?",
        "speculative_generality": "Is the code free of speculative generality (hooks, parameters, abstract classes with a single use)?",
    },
    "correctness": {
        "null_safety": "Is null/None/undefined handled safely?",
        "off_by_one": "Is the code free of off-by-one and boundary errors?",
        "resource_leaks": "Are all resources (files, connections, locks) reliably released?",
        "equals_hashcode": "Are equality and hashing implemented consistently where objects are compared or used as keys?",
        "mutability": "Is the code free of bugs caused by shared mutable state?",
        "numeric": "Is numeric handling correct (no overflow, no floating point for money, correct rounding)?",
        "time_handling": "Is time handled correctly (time zones, monotonic clocks, no naive local times)?",
        "concurrency": "Is the code free of race conditions, deadlocks and thread-safety issues?",
    },
    "error_handling": {
        "swallowed_exceptions": "Is the code free of swallowed or ignored errors?",
        "exceptions_for_control_flow": "Is the code free of exceptions used for normal control flow?",
        "error_context": "Do errors carry enough context (cause, relevant values) to diagnose the failure?",
        "cleanup_on_failure": "Is state left consistent and cleaned up when an operation fails midway?",
    },
    "security": {
        "injection": "Is the code free of injection vulnerabilities (SQL, command, LDAP, template)?",
        "xss": "Is the code free of cross-site scripting (output is escaped for its context)?",
        "hardcoded_secrets": "Is the code free of hardcoded secrets, keys and passwords?",
        "input_validation": "Is untrusted input validated at trust boundaries?",
        "weak_crypto": "Is the code free of weak or misused cryptography (MD5/SHA1 for passwords, ECB, static IVs, custom crypto)?",
        "path_traversal": "Is the code free of path traversal vulnerabilities?",
        "unsafe_deserialization": "Is the code free of unsafe deserialization of untrusted data?",
        "ssrf": "Is the code free of server-side request forgery (user-controlled URLs are restricted)?",
        "authz_check": "Are authorization checks present where protected resources or actions are accessed?",
        "sensitive_logging": "Is the code free of logging sensitive data (passwords, tokens, personal data)?",
        "auth_session": "Are authentication and sessions handled securely (bcrypt/argon2 password hashing, token expiry, no session fixation)?",
        "csrf": "Are state-changing requests protected against CSRF?",
        "xxe": "Is XML parsing safe from XXE (external entities disabled)?",
        "open_redirect": "Is the code free of open redirects to user-controlled URLs?",
        "insecure_randomness": "Are security-sensitive values (tokens, ids, salts) generated with a cryptographically secure RNG?",
        "tls_verification": "Is the code free of disabled TLS or certificate verification?",
        "security_misconfig": "Is the code free of insecure defaults (debug mode, permissive CORS, wildcard permissions)?",
        "mass_assignment": "Is the code free of mass assignment (request data bound directly onto entities)?",
        "idor": "Are object references checked against the current user (no insecure direct object references)?",
        "toctou": "Is the code free of check-then-use (TOCTOU) races on security decisions or files?",
        "redos": "Is the code free of regular expressions vulnerable to catastrophic backtracking (ReDoS)?",
        "error_disclosure": "Do errors shown to users avoid leaking internals (stack traces, SQL, file paths)?",
        "least_privilege": "Does the code follow least privilege (no unnecessary permissions, scopes or elevated rights)?",
    },
    "performance": {
        "n_plus_one": "Is the code free of N+1 queries or calls?",
        "algorithmic_complexity": "Is the algorithmic complexity appropriate (no avoidable quadratic or worse work)?",
        "alloc_in_loop": "Is the code free of avoidable allocations or expensive work repeated inside loops?",
        "blocking_in_async": "Is the code free of blocking calls inside async/event-loop code?",
        "unbounded_growth": "Is the code free of unbounded growth (caches, queues, collections without limits)?",
    },
    "readability": {
        "naming": "Are names clear and intention-revealing?",
        "function_size": "Are functions short and focused on one thing?",
        "nesting_depth": "Is nesting shallow (guard clauses instead of deep if/else pyramids)?",
        "magic_numbers": "Is the code free of unexplained magic numbers and strings?",
        "dead_code": "Is the code free of dead, commented-out or unreachable code?",
        "comments_why_not_what": "Do comments explain why rather than restate what the code does?",
    },
    "clean_code": {
        "single_abstraction_level": "Does each function operate at a single level of abstraction?",
        "flag_arguments": "Is the code free of boolean flag arguments that make a function do two things?",
        "hidden_side_effects": "Is the code free of hidden side effects (functions do only what their names say)?",
        "output_arguments": "Is the code free of output arguments (results are returned, not written into parameters)?",
        "null_returns": "Does the code avoid returning or passing null where an empty value, Optional/Result or exception fits?",
        "encapsulated_conditionals": "Are complex conditions extracted into well-named functions or variables?",
        "negative_conditionals": "Is the code free of confusing negative or double-negative conditions?",
        "consistent_vocabulary": "Is there one word per concept (not get/fetch/retrieve mixed for the same thing)?",
        "small_classes": "Are classes small, with few instance variables that most methods use?",
        "stepdown_order": "Is the code ordered top-down so it reads like a narrative (callers above callees, related code together)?",
        "temporal_coupling": "Is the code free of hidden temporal coupling (methods that must be called in an undocumented order)?",
    },
    "testability": {
        "hidden_dependencies": "Is the code free of hidden dependencies (statics, direct instantiation of collaborators in logic)?",
        "injectable_time_random": "Are time, randomness and environment injectable rather than read directly?",
    },
    "testing": {  # about test code; "yes" when the snippet contains no tests
        "test_aaa": "Do tests follow Arrange-Act-Assert with a clear setup, one action and assertions? (yes if no tests)",
        "test_one_behavior": "Does each test verify one behaviour and have a name describing it? (yes if no tests)",
        "test_independence": "Are tests independent of each other and of execution order? (yes if no tests)",
        "test_determinism": "Are tests deterministic (no real clock, randomness, network or sleeps)? (yes if no tests)",
        "test_meaningful_assertions": "Do tests make meaningful assertions (not only 'no exception' or assertTrue(true))? (yes if no tests)",
        "test_edge_cases": "Do tests cover edge cases and failure paths, not only the happy path? (yes if no tests)",
        "test_mocking": "Is mocking appropriate (unit under test and value objects not mocked, no assertions on implementation details)? (yes if no tests)",
        "test_logic": "Are tests free of logic (loops, conditionals, computed expected values)? (yes if no tests)",
        "test_fixtures": "Is test data minimal and local (no mystery guests, no giant shared fixtures)? (yes if no tests)",
    },
    "api_design": {
        "backward_compat": "Does the change preserve backward compatibility of public APIs?",
        "immutable_dto": "Are data transfer / value objects immutable?",
        "clear_contracts": "Are contracts clear (types, preconditions, documented errors)?",
        "idempotency": "Are operations that may be retried idempotent?",
    },
}

IDIOMS = {  # category "idioms": id -> (languages, question)
    "java_optional": (["java"], "Is Optional used correctly (return types only, no Optional.get() without check, no Optional fields/params)?"),
    "java_streams": (["java"], "Are streams used idiomatically (no side effects in map/filter, no stream where a loop is clearer)?"),
    "py_mutable_default": (["python"], "Is the code free of mutable default arguments?"),
    "py_context_managers": (["python"], "Are context managers (with) used for resources?"),
    "ts_any": (["typescript"], "Is the code free of unjustified any and unsafe type assertions?"),
    "ts_non_null": (["typescript"], "Is the code free of unjustified non-null assertions (!)?"),
    "js_strict_equality": (["javascript"], "Does the code use strict equality (===) and avoid implicit coercion?"),
    "js_unhandled_promise": (["javascript", "typescript"], "Are all promises awaited or handled (no floating promises)?"),
    "js_var": (["javascript"], "Is the code free of var (let/const used)?"),
    "go_error_wrap": (["go"], "Are errors checked and wrapped with context (fmt.Errorf %w)?"),
    "go_goroutine_leak": (["go"], "Is the code free of goroutine leaks (every goroutine can terminate)?"),
    "go_context": (["go"], "Is context.Context propagated and respected for cancellation?"),
    "cs_async_void": (["csharp"], "Is the code free of async void (except event handlers)?"),
    "cs_dispose": (["csharp"], "Are IDisposable objects disposed (using)?"),
    "cs_sync_over_async": (["csharp"], "Is the code free of sync-over-async (.Result, .Wait())?"),
    "rust_unwrap": (["rust"], "Is the code free of unwrap/expect on recoverable errors?"),
    "rust_clone": (["rust"], "Is the code free of needless clone() used to appease the borrow checker?"),
    "rust_unsafe": (["rust"], "Is unsafe absent, or minimal and justified with a SAFETY comment?"),
}

QUESTIONS = {
    **{rid: {"type": "noul", "instructions": text, "category": cat}
       for cat, rules in CATEGORIES.items() for rid, text in rules.items()},
    **{rid: {"type": "noul", "instructions": text, "category": "idioms", "languages": langs}
       for rid, (langs, text) in IDIOMS.items()},
    "primary_category": {
        "type": "choice",
        "instructions": "Which category contains the most important issue in this code?",
        "criteria": {"none": "No significant issue"} | {c: c.replace("_", " ") for c in [*CATEGORIES, "idioms"]},
    },
    "severity": {
        "type": "score",
        "instructions": "How severe is the most important issue?",
        "criteria": {
            "1": "None or cosmetic",
            "2": "Minor: worth a comment",
            "3": "Moderate: should be fixed before merge",
            "4": "Major: bug, security or maintainability risk",
            "5": "Critical: must not be merged",
        },
    },
}

RULES = [n for n, q in QUESTIONS.items() if q["type"] == "noul"]


def questions_for(language=None):
    """Questions for code in this language; unknown/None -> only language-agnostic ones (no idioms)."""
    return {n: q for n, q in QUESTIONS.items() if "languages" not in q or language in q["languages"]}


def options(q):
    return ["yes", "no"] if q["type"] == "noul" else list(q["criteria"])
