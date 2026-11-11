# Function Design Review and Refactoring Checklist

> **Purpose:** a practical review instrument for functions in scripts, libraries, data pipelines, services, and AI-enabled applications. Use it to find concrete risks, agree on a safe refactoring sequence, and collect evidence—not to enforce style by arithmetic.
>
> **Baseline:** Python 3.12+. Examples use pytest where useful. The roadmap’s Lesson 07 is the scope authority; this guide applies it as a review workflow rather than repeating an introductory functions lesson.

## Learning objectives

By the end, you should be able to:

- Review function names, responsibilities, signatures, return contracts, documentation, and tests.
- Distinguish a style preference from a correctness, security, reliability, or compatibility risk.
- Identify side effects, hidden dependencies, mutation, nondeterminism, unsafe retries, and unclear abstraction boundaries.
- Evaluate complexity and performance without blindly optimizing or applying line-count rules.
- Review public APIs, asynchronous behavior, concurrency, observability, resource ownership, and security boundaries.
- Apply data/AI-specific checks for reproducible transformations, train/serve parity, prompt construction, and tool-call schemas.
- Refactor incrementally with characterization tests and measurable before/after evidence.
- Write actionable review comments and a prioritized review report.

## 1. Scope and prerequisites

This checklist consolidates the function-related concepts from Stage 1: control flow and function signatures; scope and global state; pure functions and side effects; exception validation; collections and algorithmic complexity; file/CSV/JSON/CLI boundaries; testing; typing; higher-order functions and callable objects; decorators; production practices; security; and code-reading/refactoring.

It assumes you can read ordinary Python functions, annotations, exceptions, iterables, context managers, and pytest tests. It does not require a specific architecture or framework. The goal is to improve the function under review while preserving intended behavior.

### Evidence boundary for the project exercise

The project tree names four Stage 1 overview projects:

- `01-personal-expense-ledger-cli.md`
- `02-log-investigation-and-reliability-cli.md`
- `03-data-quality-and-transformation-pipeline.md`
- `04-rule-based-risk-review-engine.md`

The tree and module roadmap establish these project names and broad themes; they do **not** provide the implementation of any particular function. The project walkthrough later therefore uses clearly labeled *illustrative candidate functions* inferred from each project theme. It does not claim that those functions exist in the project source. For a real review, open the actual project implementation and cite exact file paths and line ranges.

## 2. How to use this checklist

1. **Set context.** Identify the function’s caller, inputs, outputs, side effects, trust boundary, and compatibility expectations. Read adjacent tests and call sites before proposing changes.
2. **State the intended behavior.** Write down invariants and observable behavior. Separate intended behavior from accidental behavior; characterization tests may need to preserve behavior temporarily even when it is undesirable.
3. **Review in three passes.** Begin with correctness and public contract, then inspect dependencies/complexity, then examine advanced operational and security risks. Not every function needs every advanced control, but each skipped item should be consciously not applicable.
4. **Record evidence.** Use a test, a concrete input/output example, a call-site search, a profiler, a type-check result, or a security reproduction. “Feels too long” is not enough.
5. **Prioritize by impact and likelihood.** Correctness, data loss, security, privacy, and production outages outrank cosmetic style. Do not let an aggregate score hide a critical defect.
6. **Refactor in small steps.** Characterize, make one conceptual change, run focused tests, then run the relevant broader suite. Keep each diff reviewable.
7. **Close the loop.** Document remaining risks, tests run, before/after metrics, and follow-up work. Avoid claiming a test, tool, or source inspection happened unless it did.

### Severity and priority guide

| Priority | Meaning | Typical response |
|---|---|---|
| **P0 — Critical** | Credible path to data loss, unauthorized access, secret exposure, command/code injection, or severe production outage. | Block release; contain or fix before merge. |
| **P1 — High** | Incorrect business result, unsafe retry, broken public contract, serious reliability/concurrency bug, or unbounded resource use. | Fix before merge unless an explicit, approved mitigation exists. |
| **P2 — Medium** | Material maintainability/testability/performance issue or likely edge-case bug with limited scope. | Fix in this change when safe; otherwise create a tracked follow-up. |
| **P3 — Low** | Local clarity, consistency, or minor cleanup with no meaningful current risk. | Optional; avoid expanding a risky refactor just to satisfy style. |
| **N/A** | The criterion does not apply to this function. | Record a short reason for security, concurrency, API, or resource criteria when their relevance is not obvious. |

A useful finding names **location + observed behavior + impact + suggested action + evidence**. Severity is about impact, not how easy the fix is.

### Review record template

```text
Function / file / commit:
Caller and purpose:
Inputs, outputs, side effects:
Trust boundary / data sensitivity:
Compatibility constraints:
Tests and tools actually run:
Findings (priority, evidence, action):
Refactoring sequence:
Before/after metrics (with measurement method):
Remaining risks / follow-ups:
Reviewer decision:
```

## 3. Beginner review: contract, clarity, and basic tests

Use these questions for every public function and for private functions with meaningful complexity.

### B1. Name and purpose

- [ ] Does the name describe an action or predicate using the domain’s established vocabulary (`parse_invoice`, `is_eligible`, `write_checkpoint`)?
- [ ] Can the function’s purpose be explained in one direct sentence without an ambiguous “and then” chain?
- [ ] Does the name reveal side effects where useful (`send_email`, `save_record`, `delete_expired_rows`)?
- [ ] Does it avoid vague names such as `process`, `handle`, `do_stuff`, or misleading names such as `get_*` for a destructive operation?

**Warning signs:** the name describes implementation details but not intent; callers must inspect the body to know whether it mutates data or performs I/O; similar names mean different things across modules.

**Recommended action:** rename first when safe; extract helpers by intent, not simply to move lines. Search all call sites and update tests/docs in the same focused change.

### B2. Single responsibility, size, and nesting

- [ ] Does the function have one cohesive responsibility and one clear reason to change?
- [ ] Does it avoid combining parsing, business rules, database/file/network I/O, formatting, and logging in one body?
- [ ] Are branches and nesting easy to follow? Can invalid or exceptional cases exit early?
- [ ] Are extracted helpers named after a meaningful operation rather than `step_1` or `do_part`?

**Warning signs:** several unrelated `try` blocks, multiple output formats, multiple persistence operations, repeated conditionals, deeply nested branches, or a function that needs a long comment to explain its phases.

**Guidance:** the roadmap suggests functions are *ideally* under roughly 20–30 lines and nesting at most 2–3 levels. These are prompts to inspect, not hard limits. A 40-line cohesive parser may be clearer than six tiny helpers; a 12-line function with tangled state and security-sensitive branching may be too complex.

### B3. Guard clauses and early returns

- [ ] Are invalid states rejected close to the boundary?
- [ ] Do guard clauses make the main path visible?
- [ ] Are early returns semantically consistent and resource-safe?

```python
def normalize_identifier(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return value.casefold()
```

This is appropriate only when the domain defines the identifier as case-insensitive. Do not apply whole-string case folding to email addresses or human display names by default: email local-part semantics and display-name preservation may require a different policy.

Do not replace every `if` with a guard mechanically. Preserve cleanup, transaction, and resource-lifetime behavior.

### B4. Parameter design

- [ ] Is the number of parameters reasonable for the concept? The roadmap's suggested **3–4 parameters** is a review prompt, not a universal cap; a coherent signature with more parameters can be justified.
- [ ] Does a boolean flag switch between two different operations (`process(data, strict=True)`)? Would separate functions or a strategy be clearer?
- [ ] Are defaults useful, stable, and safe?
- [ ] Are mutable defaults avoided (`items=[]`, `options={}`)?
- [ ] Are optional/configuration parameters keyword-only when positional order would be easy to confuse?
- [ ] Are units and semantics explicit (`timeout_seconds`, `amount_cents`, `limit`) rather than ambiguous (`timeout`, `value`)?
- [ ] Is `**kwargs` used for deliberate forwarding rather than hiding an unstable signature?

**Warning signs:** many related scalar arguments, sentinel values with undocumented meaning, positional booleans, caller-specific combinations, or a function with a dozen unrelated options.

**Recommended action:** introduce a small parameter object when fields form one meaningful, validated concept. Do not create a dataclass just to avoid three clear parameters.

### B5. Return contract and `None`

- [ ] Is the return type consistent and accurately annotated?
- [ ] Is `None` a deliberate result with documented meaning, rather than an accidental fall-through?
- [ ] Are error codes mixed with valid data (for example, `-1` sometimes means “not found”)?
- [ ] Does the function mutate a value and return it as well without a clear reason?
- [ ] Would a result object or explicit exception make multiple outcomes clearer?

**Warning signs:** return values vary among `str`, `dict`, `None`, and `False`; callers must infer what each means; exceptions are swallowed and replaced by an empty result.

### B6. Docstrings and type hints

- [ ] Do public functions have useful annotations, including return type?
- [ ] Does a docstring explain intent, non-obvious semantics, units, side effects, exceptions, and relevant examples?
- [ ] Does it avoid merely restating the function name?
- [ ] Are annotations honest about `Iterable` versus `Sequence`, optional values, and possible exceptions?

The roadmap recommends a summary, parameter meaning/units, return value, raised exceptions, and an example for public functions where useful. Do not force boilerplate that adds no information.

### B7. Baseline tests

- [ ] Is there a happy-path test?
- [ ] Are boundaries tested (empty input, zero, one item, maximum/minimum, timezone boundary, or other domain boundary)?
- [ ] Is invalid input tested?
- [ ] Is there a regression test for each fixed bug?
- [ ] Do tests assert observable behavior instead of implementation details?

**Evidence to collect:** test names, examples of boundary values, reproducible bug case, return contract, and relevant caller expectations.

## 4. Intermediate review: behavior, dependencies, and cost

### I1. Purity, side effects, and mutation

- [ ] Can the computation be expressed independently of I/O?
- [ ] Are side effects visible in names, interfaces, or documentation?
- [ ] Are clock, randomness, filesystem, network clients, environment, and database dependencies explicit or deliberately encapsulated?
- [ ] Does the function mutate input arguments? If yes, is that contract necessary, documented, and tested?
- [ ] Can a pure transformation be extracted without changing observable behavior?

Prefer a functional core (deterministic computation) with an imperative shell (I/O and orchestration). Pure functions are easier to test, cache, retry, and reason about—but not every function needs to be pure.

### I2. Validation and exceptions

- [ ] Are untrusted values validated at the boundary where assumptions become necessary?
- [ ] Are exception types specific enough for callers to respond correctly?
- [ ] Do error messages explain the invalid value/context without leaking secrets?
- [ ] Does the code avoid `except Exception: return None` or catching errors only to lose diagnostic context?
- [ ] Are resources closed via context managers and cleanup paths reliable?

Use `ValueError` for a valid type with an invalid value, `TypeError` when a caller supplies an object of the wrong type where runtime validation is appropriate, and domain-specific exceptions when they improve caller handling. Avoid catching exceptions merely because a failure is possible; catch at a boundary where you can recover, translate, or add context.

Never use `assert` to validate untrusted input: Python can remove assertions under optimization. Assertions are for internal invariants that should indicate a programming defect.

### I3. Abstraction levels and parameter semantics

- [ ] Does each function work at roughly one abstraction level?
- [ ] Are business rules separated from formatting, transport, storage, and CLI presentation?
- [ ] Are abstract input types appropriate (`Iterable[T]`, `Mapping[K, V]`) while output types are concrete when callers need predictable behavior?
- [ ] Are source/destination, units, ordering, and ownership obvious from names or types?
- [ ] Would a parameter object improve coherence, validation, and call-site readability?
- [ ] Are there too many `Any`, stringly-typed mode names, magic tuples, or generic `dict[str, object]` contracts?

A helper should hide a concept, not just a few lines. Abstraction that adds indirection without naming a stable idea is not an improvement.

### I4. Determinism, idempotence, and retries

- [ ] Are current time, randomness, environment, locale, global configuration, and external services hidden dependencies?
- [ ] If deterministic output is expected, are those dependencies injected or seeded?
- [ ] Is the function idempotent when a caller may retry it?
- [ ] If it is not idempotent, does it use idempotency keys, deduplication, transactions, or an explicit at-most-once/at-least-once strategy?
- [ ] Are retries limited to transient failures, bounded by attempts/deadline, and safe for the operation?

**Critical distinction:** “same input produces same output” is determinism. “Repeating the operation has the same externally observable effect as doing it once” is idempotence. A deterministic `charge_card(order_id)` can still charge twice.

### I5. Complexity and control flow

- [ ] Is branching complexity proportional to the domain rules?
- [ ] Are long `if`/`elif` chains better represented by a dispatch table, `match`, or polymorphic strategy?
- [ ] Is recursion appropriate for the problem and bounded by input size? Could iteration avoid recursion-depth risk?
- [ ] Are loop invariants and early-exit conditions clear?
- [ ] Does a helper reduce cognitive complexity instead of scattering it across multiple functions?

Cyclomatic complexity is a useful signal about independent paths, not a direct measure of correctness or maintainability. Review the branch semantics and tests, not just a metric.

### I6. Performance sanity

- [ ] Is membership checked against a list repeatedly where a set/dict would suit the semantics?
- [ ] Is immutable string/tuple concatenation repeated in a loop where a join/list builder is clearer?
- [ ] Is parsing, regex compilation, schema loading, or model initialization repeated unnecessarily?
- [ ] Is a large collection materialized when streaming would suffice—or streamed when multiple passes are needed?
- [ ] Are nested loops truly necessary, or is an index/grouping pass possible?
- [ ] Has the suspected bottleneck been measured on representative data before optimization?

**Evidence:** input sizes, runtime profile, memory profile, algorithmic reasoning, and a benchmark that represents realistic usage. Do not claim a speedup from code appearance alone.

### I7. Safe incremental refactoring

- [ ] Is the current behavior captured before changing structure?
- [ ] Does each step make one conceptual change?
- [ ] Are renames and extraction separated from behavior changes when practical?
- [ ] Are public call sites, serialization formats, and tests updated together?
- [ ] Are tests rerun after every step and the full relevant suite before merge?

Recommended sequence: characterize with tests → rename → extract intent-named helper → introduce a parameter object if warranted → split boolean-flag behavior → inject dependencies → simplify dispatch → optimize only with evidence. The order can change when risk demands it; tests precede risky structural changes.

## 5. Advanced review: contracts, APIs, operations, and security

### A1. Preconditions, postconditions, and invariants

- [ ] Are preconditions explicit at public boundaries?
- [ ] Are postconditions and state invariants documented or tested?
- [ ] Are assertions used only for internal invariants, not user input?
- [ ] Could `Literal`, `NewType`, enums, value objects, or `typing.assert_never` make invalid states harder to represent?
- [ ] Do property-based tests check general rules, not only selected examples?

Use stronger type constructs when they improve the domain model and static analysis. `NewType` adds static distinction, not runtime validation. A `Literal` annotation does not validate runtime input by itself. Keep runtime boundary validation where required.

### A2. Public API evolution and compatibility

- [ ] Is the function public, externally called, serialized, registered as a callback, or used in a plugin interface?
- [ ] Could parameter renames, positional order changes, default changes, return-type changes, or exception changes break callers?
- [ ] Is a deprecation path needed before removing a parameter or behavior?
- [ ] Are sync and async APIs named and documented clearly, without blocking the event loop?
- [ ] Is resource ownership explicit: who opens, closes, commits, or cancels?
- [ ] Are thread-safety, reentrancy, and shared-state assumptions documented where callers need them?

Do not add a compatibility layer for a private function with no meaningful callers unless there is a reason. Conversely, a one-line public function may be a critical compatibility surface.

### A3. Async, concurrency, and cancellation

- [ ] Does `async def` avoid blocking calls such as `time.sleep`, synchronous network I/O, or CPU-heavy loops on the event loop?
- [ ] Is cancellation propagated rather than accidentally swallowed?
- [ ] Are locks, transactions, and cleanup correct when cancellation occurs?
- [ ] Is shared mutable state protected or avoided?
- [ ] Are functions safe to call concurrently or reentrantly as documented?
- [ ] Are timeouts and bounded queues used where waiting could otherwise be indefinite?

An `async def` function is not automatically non-blocking. Use async-compatible libraries or move appropriate blocking work to a worker thread/process. Do not catch `BaseException` to suppress cancellation or process-control signals.

### A4. Observability and exception context

- [ ] Are logs structured with stable fields such as operation, job/run ID, record ID (when safe), and outcome?
- [ ] Are metrics and tracing added at meaningful boundaries rather than every tiny helper?
- [ ] Is useful context attached to exceptions without destroying the original cause (`raise NewError(...) from exc`)?
- [ ] Are errors counted once at an appropriate boundary instead of being logged and re-raised at every layer?
- [ ] Are secrets, credentials, tokens, personal data, and raw sensitive payloads excluded or redacted?

Observability should answer what happened, where, and with which safe correlation identifier. It should not create a second data-exfiltration channel.

### A5. Security and trust boundaries

Mark functions that accept external input or reach dangerous sinks. Review:

- [ ] **Untrusted input:** validation, size limits, encoding, schema checks, and malformed-input handling.
- [ ] **Injection:** parameterized SQL, safe subprocess argument lists, no shell interpolation of untrusted strings, context-aware output encoding.
- [ ] **Paths:** resolve/containment checks when users influence paths; defend against traversal and symlink races where the threat model requires it.
- [ ] **Deserialization:** do not use `pickle` on untrusted data; validate JSON/schema after parsing; bound input sizes/depth where needed.
- [ ] **Secrets:** avoid secrets in logs, exceptions, URLs, test fixtures, and command-line arguments visible to process listings.
- [ ] **Authorization:** check access at the boundary that has the needed identity/context; do not confuse validation with authorization.
- [ ] **Subprocesses and network:** timeouts, least privilege, allowlists, bounded output, and explicit failure handling.
- [ ] **Resource exhaustion:** limits on rows, bytes, recursion, decompression, regex work, and external calls.

A trust-boundary function should be small enough to audit, but extracting a helper does not itself make a sink safe. Review the complete data flow from source to sink.

### A6. Automated quality gates

Use tooling as a repeatable signal, not as a substitute for design review.

- **Ruff complexity:** `C90` rules include McCabe complexity checks; `C901` flags functions above the configured threshold when enabled.
- **Ruff design/style:** `PLR` covers selected Pylint refactor/design warnings; `FBT` flags boolean traps; `ARG` flags unused arguments; `B` covers bugbear checks; `ANN` covers selected missing annotations; `D` covers docstring conventions. Rule families overlap with other tools; configure intentionally.
- **Type checking:** use mypy strict on new or migrated modules when the codebase can support it. Resolve errors instead of broadly suppressing them; annotate third-party boundaries honestly.
- **Docstring coverage:** `interrogate` can measure docstring presence, but coverage does not prove quality.
- **Complexity ratchet:** set a threshold and prevent new violations or regressions; avoid arbitrary mass rewrites just to satisfy a number.
- **Tests:** pytest, coverage, and property-based testing (for example, Hypothesis) where the behavior benefits.
- **Security:** dependency/security scanners and targeted tests complement manual trust-boundary review.

Example `pyproject.toml` fragment (adapt to the repository’s existing configuration; do not replace it blindly):

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "B", "C90", "PLR", "FBT", "ARG", "ANN", "D"]
# Start with the rules the team can maintain. Add exceptions narrowly and explain them.

[tool.ruff.lint.mccabe]
max-complexity = 10
```

A practical rollout can begin with `E`, `F`, and `B`, then add complexity/design/documentation families in stages. `ANN` and `D` can produce substantial migration work in an established codebase. Strict mypy configuration is configured separately and should be trialed against representative modules. Keep the CI command and tool versions pinned and visible.

Example commands (run only in the project's environment, with the tools installed and configuration adapted to the repository):

```bash
ruff check path/to/package
mypy --strict path/to/new_or_migrated_module.py
pytest -q
interrogate -v path/to/package
```

These commands are examples of possible quality gates, not evidence that any of these tools ran for this lesson. In an existing repository, prefer its pinned environment, configured paths, baseline, and CI commands rather than introducing a second configuration blindly.

### A7. Data/AI-specific review

- [ ] Are preprocessing and feature transformations deterministic and versioned when reproducibility matters?
- [ ] Is the same transformation implementation used in training and serving, or is parity tested explicitly?
- [ ] Are null handling, dtype, units, category vocabulary, timezone, and schema evolution explicit?
- [ ] Are model-specific computations separated from generic feature preparation and I/O?
- [ ] Are prompt-building functions pure, versioned, and tested for required structure, escaping, and adversarial input?
- [ ] Are tool-call functions schema-validated, permission-checked, time-bounded, and safe to retry where possible?
- [ ] Are model/tool outputs treated as untrusted until validated?
- [ ] Are examples and logs free of private records, credentials, and sensitive prompt content?

Do not rely on prompt instructions as a security boundary. Enforce authorization and validation in code around the tool or data access.

## 6. Twenty-item review checklist and scoring

Use this compact checklist for the roadmap’s three-function exercise. Mark each item **Pass**, **Finding**, or **N/A** and attach evidence. Score only if the team benefits from a summary; the findings and risk priorities remain primary.

| # | Review item | Evidence to look for |
|---:|---|---|
| 1 | Clear name and single-sentence purpose | Name, docstring, call sites |
| 2 | Cohesive responsibility and suitable size/nesting | Branch map, phases, helper intent |
| 3 | Guard clauses and understandable control flow | Boundary branches and main path |
| 4 | Sensible parameter count/order/defaults | Signature and call sites |
| 5 | No boolean trap, mutable default, or ambiguous sentinel | Signature, tests |
| 6 | Consistent return contract and explicit `None` | Annotation, every return path |
| 7 | Useful docstring and public type hints | API docs, type checker |
| 8 | Happy-path, boundary, invalid-input, regression tests | Test names and coverage gaps |
| 9 | Side effects and mutation are explicit | I/O calls, argument writes, docs |
| 10 | Dependencies are explicit/testable | Clock, random, client, environment use |
| 11 | Validation and exceptions are appropriate | Error paths and messages |
| 12 | Abstraction levels and parameter semantics are clear | Business/I/O/formatting boundaries |
| 13 | Determinism, idempotence, and retry safety are understood | Repeated-call tests, side effects |
| 14 | Complexity and recursion are justified | Complexity report, branch tests |
| 15 | Performance and memory behavior are reasonable | Complexity reasoning/profile/benchmark |
| 16 | Refactoring is incremental and behavior-preserving | Characterization tests, commit sequence |
| 17 | Contracts and type constructs fit the domain | Preconditions, invariants, type design |
| 18 | API, async, resource, concurrency behavior is documented | Callers, cancellation, ownership |
| 19 | Observability is useful and secret-safe | Log fields, exception context, redaction |
| 20 | Security and data/AI trust boundaries are handled | Source-to-sink review, schema/permission tests |

### Optional score interpretation

For a lightweight summary, assign 1 for Pass, 0 for Finding, and exclude N/A from the denominator. Report `passes / applicable items`, but **never** use a percentage alone to approve a change. A P0 security defect cannot be offset by nineteen passing style checks. If a criterion is only partially satisfied, mark Finding and describe the partial evidence rather than awarding false precision.

## 7. Anti-pattern catalogue

| Anti-pattern | Diagnosis / warning sign | Refactoring direction | Main risk |
|---|---|---|---|
| God function | Parses, validates, computes, persists, formats, and reports in one body | Extract cohesive pure rules; keep orchestration explicit | P1–P2 |
| Hidden global dependency | Reads global client, clock, environment, or mutable cache | Inject dependency or isolate adapter | P1–P2 |
| Output-parameter mutation | Caller passes empty list/dict to be filled | Return a value unless mutation is an intentional contract | P2 |
| Boolean trap | `run(data, True)` changes algorithm or semantics | Separate functions or named policy/enum | P2 |
| Stringly-typed options | Magic strings control behavior without validation | Enum, `Literal`, strategy, or validated config | P2 |
| Swallowed exception | `except Exception: return []` hides data loss | Catch narrowly, translate with context, or propagate | P1 |
| Mixed I/O and logic | Business rules depend on files/network/printing | Functional core + I/O shell | P2 |
| Accidental generator exhaustion | Iterates once for count/logging then again for processing | Materialize deliberately or stream once | P1–P2 |
| Lambda soup | Nested anonymous callbacks obscure names, tracebacks, and contracts | Named helper, partial, closure, or callable object with rationale | P3–P2 |
| Deep nesting | Main path is buried in conditions | Guard clauses, extracted decisions, dispatch | P2 |
| Copy-paste variants | Similar functions drift in bug fixes | Share stable rule or parameterize meaningful variation | P2 |
| Speculative parameters | Unused or generic options added “for future use” | Remove until a real caller needs them | P3 |
| Repeated parsing in a loop | Same schema/regex/config compiled for each record | Parse/compile once at correct lifetime | P2; measure |
| Hidden nondeterminism | Calls `datetime.now()` or random directly in core logic | Inject clock/seed or return explicit timestamped result | P1–P2 |
| Unsafe retry | Repeats non-idempotent side effect after timeout | Idempotency key, transaction, dedupe, or no automatic retry | P0–P1 |
| `assert` for external validation | Invalid user data passes under `python -O` | Explicit validation and exceptions | P1 |
| Broad `**kwargs` | Signature and accepted options are unknowable | Explicit parameters or documented forwarding boundary | P2 |
| Recursive traversal without limits | Untrusted/deep input can exhaust recursion | Iterative traversal, depth limit, schema constraints | P1–P2 |
| Blocking async function | `async def` calls blocking I/O or `time.sleep` | Async-native client or worker offload | P1 |
| Secret-rich logging | Logs full payloads, tokens, prompts, or credentials | Redact/allowlist structured fields | P0–P1 |

## 8. Step-by-step refactoring workflow

### Step 1 — Understand callers and contract

- Find all call sites, including CLI commands, callbacks, entry points, scheduled jobs, tests, and dynamically registered functions.
- Record observable behavior: return values, exceptions, ordering, mutation, logs, I/O, transaction boundaries, and timing assumptions.
- Identify whether the function is public, persisted/serialized, or called by external consumers.

### Step 2 — Add characterization tests

Write tests around current behavior before restructuring. Include the reported bug and important edge cases. Characterization tests may document undesirable behavior; decide explicitly whether to preserve or change it. When correcting a bug, add a regression test for the desired behavior and update any characterization expectation accordingly.

### Step 3 — Make low-risk clarity changes

Rename vague local variables/functions, simplify conditions, add missing annotations, and use guard clauses without changing behavior. Run focused tests. Avoid combining a broad rename, algorithm change, and API change in one diff.

### Step 4 — Extract by intent and separate effects

Extract pure business logic from I/O/formatting. Keep the original orchestration function as a thin adapter where useful. Do not create many one-line helpers that merely mirror each line of the old function.

### Step 5 — Improve the signature and dependencies

Split boolean-flag behavior when operations are genuinely different. Introduce a parameter object only when parameters form a coherent concept. Inject clocks, random generators, clients, or filesystem boundaries when tests or reliability require control. Prefer explicit dependencies over a global service locator.

### Step 6 — Simplify decision logic and verify complexity

Use dispatch tables or polymorphism when they make the domain easier to extend; use simple `if` statements when they remain clearer. Avoid replacing a readable branch with a complicated abstraction just to lower a metric.

### Step 7 — Optimize only with evidence

Capture a baseline on representative input, profile, and change one bottleneck. Compare output equivalence and performance with repeated measurements. Include memory and latency distribution where relevant; one timing run is weak evidence.

### Step 8 — Re-run quality gates and review the diff

Run focused tests, the relevant full test suite, type checks, lint, and security tests configured by the project. Inspect the final diff for accidental public API changes, leaked secrets, unbounded work, changed exception behavior, and incomplete docs.

### Step 9 — Report outcomes honestly

Record exact commands and outcomes. State when a tool was unavailable or a test was not run. Compare before/after line count, parameters, complexity, test coverage/count, runtime, and memory only when each metric was actually measured. Metrics are signals; code clarity and behavior preservation still require review.

## 9. Worked example: flawed pipeline function

### 9.1 Flawed version

This illustrative function combines parsing, validation, normalization, side effects, and mixed return types. It is intentionally flawed; it is not quoted from the Stage 1 project source.

```python
from pathlib import Path
import json


def process(path, strict=False, errors=[]):
    try:
        rows = json.loads(Path(path).read_text())
        out = []
        for row in rows:
            if "amount" in row:
                if row["amount"] >= 0:
                    row["name"] = row.get("name", "").strip().lower()
                    out.append(row)
                elif strict:
                    errors.append(str(row))
            elif strict:
                errors.append(str(row))
        print(f"processed {len(out)} rows")
        return out if out else None
    except Exception:
        return []
```

### 9.2 Review findings

| Priority | Finding | Evidence / impact | Action |
|---|---|---|---|
| P1 | Broad exception swallowing | Parse, filesystem, and programming failures become `[]`; caller cannot distinguish failure from valid empty output | Propagate or translate expected failures with context; do not catch all exceptions here |
| P1 | Mutable default | `errors` persists across calls and across callers | Remove output parameter; return explicit validation results or raise a domain error |
| P1 | Input mutation | Modifies each input row in place | Create normalized output records or document and test mutation contract |
| P1 | Mixed return type | Returns `None`, `[]`, or list | Return one stable type and define empty result |
| P2 | Boolean flag | `strict` changes validation policy implicitly | Separate validation policy or use explicit configuration |
| P2 | Mixed abstraction levels | File I/O, JSON parse, business validation, normalization, printing | Split loading, pure transformation, and reporting |
| P2 | Weak validation | Assumes top-level list, row mapping, amount numeric, name string | Validate schema and report useful errors |
| P2 | Uncontrolled output | `print` prevents library reuse and complicates tests | Return result; caller owns logging/CLI output |
| P2 | Poor API clarity | No annotations/docstring, vague name/parameters | Add types and document behavior |
| P2 | Ambiguous policy | Negative amount is silently dropped in non-strict mode | Define whether to reject, skip, or report invalid records |

### 9.3 Corrected version

This design separates file access from deterministic transformation. The example uses a simple all-or-nothing validation policy so its contract is explicit. A production pipeline may choose a richer result object containing accepted rows and structured row-level errors; do not silently change the policy without product/domain agreement.

```python
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TypeAlias
import json
import math

Row: TypeAlias = Mapping[str, object]
NormalizedRow: TypeAlias = dict[str, object]


def normalize_row(row: Row, *, row_number: int) -> NormalizedRow:
    """Validate and normalize one row.

    Raises:
        ValueError: if required fields or their values are invalid.
    """
    amount = row.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError(f"row {row_number}: 'amount' must be numeric")
    if isinstance(amount, float) and not math.isfinite(amount):
        raise ValueError(f"row {row_number}: 'amount' must be finite")
    if amount < 0:
        raise ValueError(f"row {row_number}: 'amount' must be non-negative")

    name = row.get("name", "")
    if not isinstance(name, str):
        raise ValueError(f"row {row_number}: 'name' must be a string")

    # Return a new mapping; do not mutate the caller's object.
    return {**row, "name": name.strip().casefold(), "amount": amount}


def normalize_rows(rows: Sequence[Row]) -> list[NormalizedRow]:
    """Normalize rows in order; fail on the first invalid row."""
    return [normalize_row(row, row_number=i) for i, row in enumerate(rows, start=1)]


def load_rows(path: Path) -> list[NormalizedRow]:
    """Load JSON rows from path and normalize them.

    Raises:
        OSError: if the file cannot be read.
        json.JSONDecodeError: if the file is not valid JSON.
        ValueError: if the top-level schema or a row is invalid.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("input JSON must contain a top-level list")
    if not all(isinstance(row, dict) for row in payload):
        raise ValueError("every row must be a JSON object")
    return normalize_rows(payload)
```

**Typing note:** `isinstance(row, dict)` narrows the JSON-decoded values enough for this runtime example, while the function annotations document the intended shape. In a stricter application, validate fields with a schema/model layer and narrow to a dedicated `TypedDict` or domain type. JSON permits booleans as a distinct value even though `bool` subclasses `int`; the amount check explicitly excludes booleans.

The corrected design deliberately does not print, swallow errors, or expose a mutable `errors` parameter. For this illustration, `name` is treated as a case-insensitive canonical field; that is not appropriate for every domain. If it is a human display name, preserve its display casing and, if needed, derive a separate normalized comparison key. A CLI adapter can catch known errors, log safe context, choose an exit code, and print a summary. If partial acceptance is a requirement, implement it as a named policy with a structured result rather than hiding it behind a boolean flag.

### 9.4 Tests

Save the corrected functions in `pipeline.py`, then place these tests in `test_pipeline.py`.

```python
import json
import pytest
from pipeline import normalize_row, normalize_rows, load_rows


def test_normalize_row_trims_and_casefolds_without_mutating_input():
    original = {"name": "  ALICE ", "amount": 12}
    result = normalize_row(original, row_number=1)
    assert result == {"name": "alice", "amount": 12}
    assert original == {"name": "  ALICE ", "amount": 12}
    assert result is not original


def test_normalize_rows_empty_input_returns_empty_list():
    assert normalize_rows([]) == []


@pytest.mark.parametrize("amount", [-1, "12", True, None, float("nan"), float("inf")])
def test_invalid_amount_is_rejected(amount):
    with pytest.raises(ValueError, match="amount"):
        normalize_row({"name": "x", "amount": amount}, row_number=3)


def test_non_string_name_is_rejected():
    with pytest.raises(ValueError, match="name"):
        normalize_row({"name": 42, "amount": 1}, row_number=1)


def test_load_rows_rejects_non_list_json(tmp_path):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps({"name": "x", "amount": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="top-level list"):
        load_rows(path)


def test_load_rows_loads_and_normalizes(tmp_path):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps([{"name": " Bob ", "amount": 5}]), encoding="utf-8")
    assert load_rows(path) == [{"name": "bob", "amount": 5}]
```

Expected test intent: the function returns stable types, normalizes without mutating the input, rejects invalid values, validates the top-level schema, and reads UTF-8 explicitly. The tests should be run in the project environment; do not infer execution results merely from reading the code.

### 9.5 Before/after comparison

| Dimension | Flawed version | Corrected design |
|---|---|---|
| Responsibilities | File I/O, parsing, validation, mutation, printing, error policy | Pure normalization separated from file adapter |
| Return contract | `list`, `None`, or empty list used for failures | Normalized list on success; documented exceptions on failure |
| State | Mutable default accumulates errors | No hidden shared default state |
| Input mutation | Mutates row dictionaries | Returns new row dictionaries |
| Failure behavior | Any exception is swallowed | Expected validation errors are explicit; I/O/JSON errors remain visible |
| Testability | Requires capturing print and managing filesystem/error side effects together | Pure core tests plus narrow adapter tests |
| API | Untyped `path`, boolean mode, output parameter | Typed `Path`, explicit function responsibilities |
| Policy | Silent skipping depends on `strict` | Fail-fast policy is explicit; partial acceptance can be designed separately |

Do not claim a numeric complexity or runtime improvement without running the selected tools and measuring representative inputs. The corrected version has more lines, but clearer boundaries and contracts; fewer lines are not the objective.

## 10. Applying the checklist to three Stage 1 project themes

The project tree lists the projects below, but the implementation source is not included in the source material inspected for this guide. Each candidate is therefore a **hypothetical review target**, not a finding about the actual project.

### Example A — `01-personal-expense-ledger-cli.md`

**Illustrative candidate:** `summarize_expenses(transactions, start_date, end_date, include_pending=False)`.

Review questions:

- Are monetary values represented consistently (for example integer minor units or a carefully chosen decimal representation), not mixed floats and strings?
- Are date boundaries and timezone semantics explicit and tested at start/end boundaries?
- Does the function only calculate a summary, or does it also read files and print a table?
- Does `include_pending` change a minor policy or switch to a different operation? Is the default documented?
- Are refunds, empty periods, duplicate transactions, and malformed entries covered by tests?

Evidence to collect: source and call sites, currency/rounding policy, tests for date boundaries, and whether input records are mutated. Do not assume a bug exists until the source demonstrates it.

### Example B — `02-log-investigation-and-reliability-cli.md`

**Illustrative candidate:** `parse_log_line(line)` or `summarize_failures(lines)`.

Review questions:

- Does parsing return a typed record or an ambiguous tuple/dict with undocumented keys?
- Are malformed lines represented consistently (specific exception, structured parse result, or explicit skip policy)?
- Is the input iterable consumed once or accidentally traversed twice?
- Are timestamps/timezones and severity labels normalized consistently?
- Does the function mix parsing with printing, logging, and aggregation?
- Are large logs processed incrementally and protected against pathological line lengths?

Evidence to collect: malformed-line examples, log format assumptions, memory behavior for large inputs, parser tests, and the exact error-handling policy.

### Example C — `03-data-quality-and-transformation-pipeline.md`

**Illustrative candidate:** `validate_and_transform_records(records, strict=True)`.

Review questions:

- Are schema validation, row transformation, aggregation, and persistence separated?
- Is the transformation deterministic and shared with serving/consuming code where consistency matters?
- Are nulls, dtypes, units, duplicate keys, and schema evolution explicit?
- Is `strict` a boolean trap that silently changes output shape or failure behavior?
- Are partial failures and row-level error reports represented structurally?
- Does it mutate input rows or materialize a huge iterable unnecessarily?

Evidence to collect: input/output schema, row-level acceptance policy, deterministic fixtures, representative-size memory/runtime profile, and regression tests for known data defects.

### How to complete the real exercise

For each actual project, select one function from source and record: file path/line range; signature; callers; the 20 checklist outcomes; prioritized findings; a minimal characterization test; small refactoring commits; before/after lines, parameters, complexity, and test count; and a concise PR review note. If the project has no suitable function, explain why and choose another. Never invent line numbers, test results, metrics, or implementation findings from a project title alone.

## 11. Review-comment examples

### Useful comments

**P1 — swallowed parse failures**

> `parse_records()` currently converts every exception into an empty list. That makes malformed input indistinguishable from a valid file with zero records and can produce a successful-looking but incomplete report. Could we catch the expected parse exception at the CLI boundary, preserve the cause, and return a non-zero exit status? Please add a regression test for malformed JSON.

**P2 — boolean trap**

> The `strict` flag changes both row rejection and the output shape, so callers must understand two contracts behind one function name. Could we make the policy explicit (for example, separate fail-fast and collect-errors functions or a validated policy object)? Tests should cover both intended behaviors before changing call sites.

**P2 — hidden clock dependency**

> This calculation reads the current time internally, which makes boundary tests time-sensitive and can produce different results across retries. Could we pass an explicit `now` value or clock dependency and add a test at the cutoff boundary?

**P3 — naming clarity**

> Would `normalize_transaction()` better express the result than `process()`? The call site currently does not reveal whether this function validates, mutates, or persists the transaction.

### Weak comments to avoid

- “This is ugly.”
- “Never write a function over 20 lines.”
- “Use a class because there are many arguments.”
- “This must be faster” without a profile or benchmark.
- “Add more tests” without naming the missing behavior or a test case.

A good comment is respectful, specific, actionable, and proportional to the risk. Ask a question when the domain policy is uncertain; do not frame an unverified assumption as a fact.

## 12. Exercises and solutions

### Exercise 1 — Split a boolean flag and mixed return type

Refactor this function so each public function has a clear purpose and a stable return type.

```python
def format_or_skip(value, uppercase=False):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.upper() if uppercase else text.lower()
```

**Solution:** decide the domain contract first. If the operation is normalization, use one explicit normalized output type; if “skip” is a separate filtering decision, keep it separate.

```python
def normalize_text(value: str) -> str:
    """Trim text and normalize it to lowercase."""
    return value.strip().casefold()


def should_keep_text(value: str | None) -> bool:
    """Return whether a supplied optional text value is non-empty after trimming."""
    return value is not None and bool(value.strip())
```

This removes the mode flag and mixed `None`/`str` return. It also intentionally narrows the normalization input type instead of silently converting arbitrary objects to strings. If arbitrary objects are truly supported, document that contract and name the conversion.

### Exercise 2 — Find the hidden dependency

```python
from datetime import datetime, timezone


def is_expired(expires_at: datetime) -> bool:
    return expires_at <= datetime.now(timezone.utc)
```

**Solution:** inject the comparison instant so the business rule is deterministic and easy to test.

```python
from datetime import datetime


def is_expired(expires_at: datetime, *, now: datetime) -> bool:
    """Return whether expires_at is at or before now.

    Callers must supply timezone-aware datetimes; the comparison is by instant.
    """
    if expires_at.utcoffset() is None or now.utcoffset() is None:
        raise ValueError("expires_at and now must be timezone-aware")
    return expires_at <= now
```

Python's definition of an aware `datetime` requires a non-`None` UTC offset; checking only `tzinfo is not None` is insufficient for a custom `tzinfo`. Aware datetimes with different offsets can be compared as instants, so requiring the same timezone convention is a policy choice rather than a comparison requirement. Normalize to UTC if that makes the application's contract clearer. Add tests for naive values and just-before, exactly-at, and just-after the boundary.

### Exercise 3 — Prevent quadratic membership checks

```python
def keep_allowed(records, allowed_ids):
    return [row for row in records if row["id"] in allowed_ids]
```

**Question:** What would you inspect before changing this?

**Solution:** determine the types, sizes, ordering requirements, duplicate semantics, and whether `allowed_ids` is a one-shot iterable. If it is a reusable list/set-like collection and repeated membership is the bottleneck, build a set once:

```python
from collections.abc import Hashable, Iterable, Mapping


def keep_allowed(
    records: Iterable[Mapping[str, object]],
    allowed_ids: Iterable[Hashable],
) -> list[Mapping[str, object]]:
    """Keep records whose required ``id`` is in the allowed-ID set.

    Each record must contain ``id``, and each record ID must be hashable.
    """
    allowed = set(allowed_ids)
    return [row for row in records if row["id"] in allowed]
```

This changes membership behavior to require hashable IDs and materializes `allowed_ids`. The annotation constrains the allowed-ID input, but a general `Mapping[str, object]` cannot express that one selected value (`row["id"]`) is hashable; validate that field at the boundary or use a domain-specific row type in production. A missing `id` raises `KeyError`, and an unhashable record ID raises `TypeError`. If IDs are unhashable, the iterable is enormous, or streaming constraints matter, this is not a drop-in change. Benchmark with representative input before claiming a performance win.

### Exercise 4 — Write a review note

A function is 55 lines, has 7 parameters, reads the clock internally, catches all exceptions, and has one happy-path test. Write three prioritized findings and a safe first step.

**One acceptable answer:**

1. **P1:** broad exception handling may hide failed processing; identify expected exceptions and add a malformed-input regression test before changing handling.
2. **P1/P2 depending on operation:** hidden clock makes boundary behavior nondeterministic; inject `now` and test cutoffs.
3. **P2:** seven parameters may represent multiple concepts; inspect call sites and group related validated configuration only if it improves clarity.

First step: map callers and observable behavior, then add characterization tests for the happy path, boundary conditions, invalid input, and the known failure mode. Do not split the function or redesign the signature before learning its contract.

## 13. Self-check

You are ready to apply this lesson when you can answer these without relying on line count alone:

1. What is the difference between a cohesive 35-line function and a problematic 15-line function?
2. How do you distinguish determinism from idempotence?
3. Why is `except Exception: return []` dangerous in a data pipeline?
4. When is a parameter object useful, and when does it merely add indirection?
5. Why should tests be added before a risky refactor?
6. Why is `assert` inappropriate for validating untrusted input?
7. Which failures should be retried, and what makes a side effect safe to retry?
8. What evidence is needed before claiming a function is too slow?
9. What must an async function do to avoid blocking the event loop and mishandling cancellation?
10. What does a secure review of a path or subprocess function need to inspect beyond the function body?
11. How can Ruff, type checking, and docstring coverage help without replacing human review?
12. Which Stage 1 project function would you choose for a real review, and what source evidence would you collect first?

## 14. Completion checklist

- [ ] I read the function and its callers before proposing changes.
- [ ] I can state the intended contract and identify compatibility constraints.
- [ ] I reviewed naming, responsibility, nesting, parameters, defaults, return behavior, docs, types, and tests.
- [ ] I checked side effects, mutation, hidden dependencies, validation, exceptions, determinism, idempotence, and retries.
- [ ] I considered complexity, performance, memory, and whether measurement is necessary.
- [ ] I checked relevant API, async, resource, concurrency, observability, and security concerns.
- [ ] I reviewed data/AI-specific reproducibility and schema concerns where applicable.
- [ ] Each finding includes priority, evidence, impact, and a recommended action.
- [ ] Refactoring steps are small and backed by tests.
- [ ] Tool and test outcomes are reported only when actually run.
- [ ] Before/after metrics include a method and are not used as inflexible quality laws.
- [ ] The review explains remaining risks and follow-up work.

**Final principle:** the checklist is a structured conversation about behavior, risk, and maintainability—not a scorecard that can replace engineering judgment. A successful refactor makes the function’s contract easier to understand, its behavior easier to test, and its failure modes easier to control while preserving the behavior that callers rely on.
