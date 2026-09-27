# Production Habits for Python Programs — Practice Questions

## Purpose

This practice set assesses whether you can apply the production habits taught in the eight completed lessons of `10-Production-Habits-for-Python-Programs`:

1. `01-configuration-and-env-files.md`
2. `02-safe-and-useful-logging.md`
3. `03-validation-errors-and-exit-codes.md`
4. `04-idempotency-and-repeatable-jobs.md`
5. `05-safe-file-writes.md`
6. `06-profiling-and-measuring-before-optimizing.md`
7. `07-dependency-upgrades-and-supply-chain-awareness.md`
8. `08-readmes-runbooks-and-release-basics.md`

The questions are grounded in the learned concepts, APIs, examples, workflows, anti-patterns, debugging methods, trade-offs, and production principles. The set is deliberately cumulative: Basic questions test foundations; Moderate questions combine concepts; Hard questions simulate realistic engineering problems; Advanced questions integrate the whole module.

## How to Use These Questions

Follow the learning loop:

```text
Understand
→ Predict
→ Implement
→ Test normal case
→ Test edge cases
→ Debug
→ Refactor
→ Document
→ Explain aloud
```

Read the **Problem** and **Task** before the **Solution**. For coding questions, attempt the implementation before reading the reference solution. For production scenarios, write down assumptions, failure modes, and verification steps.

## Difficulty Levels

- **Basic — 11 questions:** practical application of one or two learned concepts.
- **Moderate — 11 questions:** combines several learned concepts in realistic Python engineering work.
- **Hard — 11 questions:** requires diagnosis, implementation, or design across multiple production habits.
- **Advanced — 11 questions:** integrated production scenarios requiring trade-offs, failure handling, verification, and operational reasoning.

---

# Section 1 — Basic

## Question 1 — Safe Environment Configuration

### Difficulty
Basic

### Problem
A CLI application needs a `MODEL_NAME` setting from the environment:

```python
import os
model_name = os.environ["MODEL_NAME"]
print(model_name)
```

On a new machine the variable is missing, and the user gets an unclear traceback.

### Task
Explain the failure and redesign the boundary so a missing or empty value produces a deliberate configuration failure.

### Solution
Read environment values as external input. Use `os.getenv()`, validate presence and non-empty content, then raise a configuration-specific error or otherwise translate it at the CLI boundary into a clear message and non-zero exit status.

The application should not continue into normal business logic with missing configuration.


### Solution Code

```python
import os

def read_model_name() -> str:
    value = os.getenv("MODEL_NAME")
    if value is None or not value.strip():
        raise ValueError("MODEL_NAME is required")
    return value.strip()

print(read_model_name())
```
### Explanation
The important idea is separating retrieval from validation. `os.environ["MODEL_NAME"]` is valid Python but it raises `KeyError` when the key is absent. A production program should decide what that missing configuration means and communicate it intentionally.

### Key Takeaway
External configuration is an input boundary: read it, validate it, and fail early.

---
## Question 2 — Replace Print-Only Failure Handling

### Difficulty
Basic

### Problem
A batch program reports failures like this:

```python
try:
    process_batch()
except Exception:
    print("batch failed")
```

### Task
Show a better pattern for operational diagnostics and explain what should happen to the exception.

### Solution
Use the logging system for operational evidence and avoid silently swallowing the exception. At an appropriate boundary:

```python
try:
    process_batch()
except Exception:
    logger.exception("Batch processing failed")
    raise
```

A top-level CLI can later translate the exception into its documented exit behavior.


### Solution Code

```python
import logging

logger = logging.getLogger(__name__)

def process_batch() -> None:
    raise RuntimeError("simulated failure")

try:
    process_batch()
except Exception:
    logger.exception("Batch processing failed")
    raise
```
### Explanation
`logger.exception()` records useful exception information from inside an exception handler. Re-raising preserves the failure instead of making the application appear successful. This follows the separation of concerns: logging records evidence; exception handling controls behavior.

### Key Takeaway
Log the failure clearly, preserve its semantics, and let the correct boundary decide the final outcome.

---
## Question 3 — Validate Before Converting

### Difficulty
Basic

### Problem
A command accepts an age as text:

```python
raw_age = input("Age: ")
age = int(raw_age)
```

### Task
Write a function that rejects empty input, rejects non-integers, rejects negative ages, and returns an integer for valid input.

### Solution
Separate parsing from domain validation:

1. Reject missing/empty input.
2. Convert using `int()`.
3. Catch the conversion `ValueError`.
4. Apply the rule that age must be non-negative.
5. Return the trusted integer.


### Solution Code

```python
def parse_age(raw_age: str) -> int:
    if not raw_age.strip():
        raise ValueError("age is required")

    try:
        age = int(raw_age)
    except ValueError as exc:
        raise ValueError("age must be an integer") from exc

    if age < 0:
        raise ValueError("age must be non-negative")

    return age
```
### Explanation
This creates a clean boundary:

```text
raw text
→ parse
→ validate
→ trusted integer
```

Malformed text such as `abc` and a valid integer that violates a business rule such as `-5` are different failures, even though both should be rejected.

### Key Takeaway
Parse → validate → return trusted data.

---
## Question 4 — Recognize an Idempotent Operation

### Difficulty
Basic

### Problem
A job performs one of these operations repeatedly:

```text
1. Set status = "completed"
2. Add 1 to a counter
3. Append "completed" to a list
4. Replace a file with the same intended content
```

### Task
Identify which operations are idempotent or commonly idempotent under the stated semantics, and explain why.

### Solution
1. Setting `status = "completed"` is idempotent: repeating it leaves the same final state.
2. Incrementing a counter is not idempotent: every repetition changes the state.
3. Appending to a list is usually not idempotent because duplicates accumulate.
4. Replacing a file with the same intended content can be idempotent at the logical state level, provided the file update itself is safely implemented.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
Idempotency is about repeated application of the same logical operation and the resulting externally relevant state. The underlying write mechanism may still require crash-safe design.

### Key Takeaway
Ask what the final externally visible state is after the same logical operation runs again.

---
## Question 5 — Why `w` Mode Is Dangerous

### Difficulty
Basic

### Problem
This code updates an important state file:

```python
with open("state.json", "w", encoding="utf-8") as file:
    file.write(new_content)
```

### Task
Explain the risk of opening the existing file in `"w"` mode before complete new content is ready.

### Solution
Opening an existing file in `"w"` mode truncates its previous contents. If the process fails after truncation but before the new content is completely written, the destination can be empty or incomplete.

For important files, a safer pattern is:

```text
prepare complete content
→ write temporary file
→ complete write
→ replace destination
```

The previous valid file remains in place until the replacement step.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
`"w"` is useful when replacement semantics are intentional, but it is risky when the destination itself is the only valid copy. The lesson is not “never use w”; it is “understand the failure window and choose the update protocol deliberately.”

### Key Takeaway
Preserve the last known-good destination until the new version is ready to publish.

---
## Question 6 — Choose the Right Performance Tool

### Difficulty
Basic

### Problem
You have three situations:

A. Measure elapsed time of a whole function during a normal run.
B. Compare two tiny Python operations under repeated controlled conditions.
C. Find which functions inside a program consume the most execution time.

### Task
Choose an appropriate standard-library tool for each case.

### Solution
A → `time.perf_counter()`.

B → `timeit`.

C → `cProfile` plus `pstats`.

These tools answer different questions: elapsed duration, controlled microbenchmarking, and function-level time attribution.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
A timer tells you how long a defined region took. A benchmark is designed to compare operations under repeatable conditions. A profiler helps locate where a larger program spends time.

### Key Takeaway
Choose the tool according to the performance question you need answered.

---
## Question 7 — Direct vs Transitive Dependency

### Difficulty
Basic

### Problem
A project imports `requests`. Its resolved environment also contains `urllib3`, although application code never imports `urllib3` directly.

### Task
Classify the dependencies and explain why `urllib3` still matters.

### Solution
`requests` is a direct dependency because the project explicitly relies on it. `urllib3` is a transitive dependency if it is required by `requests`.

It still matters because the resolved dependency graph includes it. Its version can affect compatibility, reproducibility, security review, upgrades, and runtime behavior.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
Your application does not depend only on packages that appear in `import` statements. It depends on the resolved software graph needed to construct a working environment.

### Key Takeaway
Transitive dependencies are still part of the system you ship.

---
## Question 8 — README or Runbook?

### Difficulty
Basic

### Problem
A new engineer asks:

1. “What is this application and how do I install and run it?”
2. “The scheduled batch job failed. What exact steps should I follow to diagnose and recover it?”

### Task
Identify the primary documentation artifact for each question and explain the difference.

### Solution
The README is the primary entry point for the first question: purpose, prerequisites, installation, configuration, usage, testing, and orientation.

A runbook is the primary artifact for the second: preconditions, procedure, verification, failure handling, escalation, evidence, and rollback as appropriate.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
The two documents are related but have different operational jobs. The README helps a developer or user understand and use the project; the runbook guides an operator through a known operational situation.

### Key Takeaway
Documentation should be selected by audience and purpose.

---
## Question 9 — Safe Boolean Configuration Parsing

### Difficulty
Basic

### Problem
A developer writes:

```python
debug = bool(os.getenv("DEBUG"))
```

### Task
Explain the bug and provide an explicit parser for values such as `true`, `false`, `1`, and `0`.

### Solution
Environment variables are strings. In Python, every non-empty string is truthy, so `"false"` would become `True`.

A better parser normalizes the text and accepts explicit values:

```python
def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("expected a boolean value")
```


### Solution Code

```python
def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("expected a boolean value")
```
### Explanation
The configuration contract needs to distinguish the word “false” from a non-empty Python string. Explicit parsing makes invalid configuration fail instead of silently changing program behavior.

### Key Takeaway
Never use raw string truthiness as a Boolean configuration contract.

---
## Question 10 — Use Lazy Logging Formatting

### Difficulty
Basic

### Problem
A hot loop contains:

```python
logger.debug(f"Processing record {record_id}")
```

DEBUG logging is normally disabled.

### Task
Rewrite the message using the logging style taught in the logging chapter and explain the reason.

### Solution
Use:

```python
logger.debug("Processing record_id=%s", record_id)
```

The logging system receives a template and arguments separately, so message formatting can be deferred until the record is actually emitted.


### Solution Code

```python
import logging

logger = logging.getLogger(__name__)
record_id = "record-123"
logger.debug("Processing record_id=%s", record_id)
```
### Explanation
This is the logging module's intended parameterized style. It avoids eagerly building a formatted string when the DEBUG record will not be emitted and is especially appropriate in frequently executed code.

### Key Takeaway
Use lazy logging arguments for routine parameterized messages.

---
## Question 11 — Release vs Deployment

### Difficulty
Basic

### Problem
A team prepares version `1.2.0`, builds an artifact, and deploys it to production. A teammate says, “The release and deployment are the same thing.”

### Task
Explain the distinction and one reason the distinction matters.

### Solution
A release is a specific, identifiable software version prepared for users or deployment. Deployment is the act of putting that selected release/artifact into an environment.

The distinction matters because a release can exist before deployment, and traceability/rollback require knowing both what was released and what is running.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
The source chapter distinguishes source code, commits, build artifacts, releases, and deployments. Keeping them separate makes operations and incident investigation more precise.

### Key Takeaway
Release identifies a version; deployment puts that version into an environment.

---

# Section 2 — Moderate

## Question 12 — Configuration Failure at the CLI Boundary

### Difficulty
Moderate

### Problem
A CLI expects `TIMEOUT_SECONDS` from the environment:

```python
timeout = int(os.getenv("TIMEOUT_SECONDS", "30"))
run(timeout)
```

With `TIMEOUT_SECONDS=abc`, the user gets a traceback.

### Task
Design the expected-failure path so malformed configuration is rejected early, the message goes to `stderr`, and the process exits non-zero.

### Solution
Separate parsing from the top-level CLI handling.

1. Read the string.
2. Convert to `int`.
3. Validate the value.
4. Raise a specific configuration error.
5. Catch that expected error in `main()`.
6. Print a concise message to `stderr`.
7. Return a documented non-zero code and let `sys.exit()` communicate it.

Keep unexpected programmer defects out of the configuration-error bucket.


### Solution Code

```python
import os
import sys

class ConfigurationError(Exception):
    pass

def load_timeout() -> int:
    raw = os.getenv("TIMEOUT_SECONDS", "30")
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(
            "TIMEOUT_SECONDS must be an integer"
        ) from exc
    if value <= 0:
        raise ConfigurationError(
            "TIMEOUT_SECONDS must be greater than 0"
        )
    return value

def main() -> int:
    try:
        timeout = load_timeout()
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 4
    run(timeout)
    return 0

def run(timeout: int) -> None:
    print(f"running with timeout={timeout}")

if __name__ == "__main__":
    sys.exit(main())
```
### Explanation
This combines configuration, validation, exceptions, stderr, and exit codes. The top-level boundary is the right place to decide the user-facing message and process status.

### Key Takeaway
A predictable CLI turns expected configuration failure into safe human output and a machine-visible non-zero result.

---
## Question 13 — Log an Expected Failure Without Swallowing It

### Difficulty
Moderate

### Problem
A data job has:

```python
try:
    config = load_config()
    process(config)
except ConfigurationError:
    logger.error("config failed")
    return
```

### Task
Improve the handling so diagnostics remain useful and the failure is not silently converted into success.

### Solution
If the current layer can meaningfully recover, handle the specific exception there. Otherwise log useful evidence and propagate the exception:

```python
try:
    config = load_config()
except ConfigurationError:
    logger.exception("Application configuration failed")
    raise
```

A top-level CLI can later translate `ConfigurationError` into a user-facing message and exit code.


### Solution Code

```python
import logging

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    pass

def load_config():
    raise ConfigurationError("MODEL_NAME is missing")

def start() -> None:
    try:
        config = load_config()
    except ConfigurationError:
        logger.exception("Application configuration failed")
        raise
    process(config)

def process(config) -> None:
    print(config)
```
### Explanation
“Log and return” can hide the failure from the caller. `logger.exception()` is useful in an exception handler because it records exception information. The final action should match the responsibility of the current layer.

### Key Takeaway
Handle where recovery is meaningful; otherwise preserve the exception.

---
## Question 14 — Retry After an Unknown Outcome

### Difficulty
Moderate

### Problem
A job calls an external service with `operation_id="invoice-123"`. The service may complete the operation, but the response times out. The retry code generates a new random ID.

### Task
Explain the risk and redesign the logical retry identity.

### Solution
A timeout does not prove that the first attempt had no side effect. If the first request succeeded and only the response was lost, generating a new ID makes the retry look like a different logical operation.

Use the same stable logical operation ID for the retry and rely on duplicate-safe semantics at the side-effect boundary.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
The source chapter calls this the unknown-outcome problem. A stable ID connects attempts that represent the same logical operation. An ID alone does not make an operation idempotent; the receiving operation must actually use it to prevent or reconcile duplicates.

### Key Takeaway
Reuse the same logical identity when retrying the same operation.

---
## Question 15 — Safe JSON State Update

### Difficulty
Moderate

### Problem
A job directly writes a new `state.json`:

```python
with open("state.json", "w", encoding="utf-8") as file:
    json.dump(state, file)
```

The process can crash while writing.

### Task
Describe a safer update protocol and explain what it protects and what it does not guarantee.

### Solution
Use:

```text
state in memory
→ generate complete candidate
→ write temporary file in destination directory
→ finish write
→ sync if durability requirements justify it
→ os.replace(temp, destination)
→ cleanup
```

This leaves the old destination in place until the candidate is complete. It protects the publication boundary from normal partial-write exposure. It does not by itself guarantee durable persistence after every possible power-loss scenario.


### Solution Code

```python
import json
import os
import tempfile
from pathlib import Path

def safe_write_json(path: Path, state: dict) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temp:
        temp_path = Path(temp.name)
        json.dump(state, temp, indent=2, sort_keys=True)
        temp.flush()

    try:
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)
```
### Explanation
The key distinction is atomicity versus durability. Temporary-file plus replacement protects the destination from being replaced by an incomplete candidate; `flush()` and `fsync()` have different roles and requirements.

### Key Takeaway
Publish only complete candidate state; choose durability controls according to actual requirements.

---
## Question 16 — Benchmark the Target, Not the Setup

### Difficulty
Moderate

### Problem
You want to compare two aggregation approaches. The benchmark is:

```python
def benchmark():
    data = list(range(10_000))
    return sum(data)
```

### Task
Explain what can mislead the result and rewrite it so the measured region focuses on aggregation.

### Solution
Move stable setup outside the measured callable:

```python
data = list(range(10_000))

def benchmark_sum():
    return sum(data)
```

Then use `timeit` to measure repeated calls to `benchmark_sum()`.

If the real production question includes data construction, benchmark that workflow separately. The key is to measure the question you actually care about.


### Solution Code

```python
import timeit

data = list(range(10_000))

def benchmark_sum() -> int:
    return sum(data)

duration = timeit.timeit(benchmark_sum, number=10_000)
print(duration)
```
### Explanation
Benchmark setup and target work answer different questions. If list construction is included accidentally, a benchmark comparing two aggregation implementations can become dominated by unrelated setup.

### Key Takeaway
Isolate the operation that the benchmark is intended to compare.

---
## Question 17 — Dependency Conflict

### Difficulty
Moderate

### Problem
A project has:

```text
Library A → Helper >= 1,<2
Library B → Helper >= 2,<3
```

### Task
Explain why dependency resolution can fail and how you would investigate it.

### Solution
The two requirements have no overlapping version. A resolver cannot select one Helper version that satisfies both constraints.

Investigate by:
1. confirming direct dependencies;
2. inspecting the resolved dependency tree;
3. checking newer compatible versions of A or B;
4. reading release notes;
5. changing constraints deliberately;
6. re-resolving and running the full test suite.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
This is a dependency-graph constraint problem, not merely a failed install. The correct response is to understand which dependency creates each requirement before changing versions.

### Key Takeaway
Resolve the graph deliberately; do not force an arbitrary transitive version.

---
## Question 18 — README Configuration Contract

### Difficulty
Moderate

### Problem
A README says only:

```text
Set the required environment variables before starting the app.
```

### Task
Rewrite the documentation guidance so a developer can understand required/optional configuration without receiving real secrets.

### Solution
Document the contract explicitly:

```markdown
## Configuration

| Variable | Required | Default | Purpose |
|---|---|---|---|
| MODEL_NAME | Yes | — | Model identifier |
| API_KEY | Yes | — | Runtime credential |
| LOG_LEVEL | No | INFO | Minimum log level |

Do not commit real credentials. Use placeholders in `.env.example`.
```

The exact variable names depend on the application; the important structure is required/optional status, defaults, purpose, and safe secret handling.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
Good configuration documentation reduces guessing. It also separates documentation of the secret's existence from disclosure of the secret value.

### Key Takeaway
Document the configuration contract, never the secret itself.

---
## Question 19 — Runbook With Preconditions and Verification

### Difficulty
Moderate

### Problem
An operational document says:

```text
1. Restart the batch job.
2. Check that it worked.
```

### Task
Rewrite the procedure conceptually using preconditions, explicit action, verification, failure handling, and escalation.

### Solution
A better procedure is:

1. Identify the failed job ID and inspect its latest logs.
2. Confirm no replacement run is already processing the same logical work.
3. Confirm the retry is permitted by the job's idempotency/recovery rules.
4. Start the documented retry.
5. Verify expected job state and output.
6. If state is unknown, duplicate processing is suspected, or the procedure fails, stop and escalate with the required evidence.

The runbook should define what the operator must check before acting, not only the action itself.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
A runbook is an operational safety boundary. Verification proves the action worked; escalation prevents operators from improvising when assumptions no longer hold.

### Key Takeaway
Every operational action needs preconditions and a way to prove the expected result.

---
## Question 20 — Rerunnable Batch Output

### Difficulty
Moderate

### Problem
A batch job processes transactions and appends one result row to `results.csv` per record. A crash causes the scheduler to rerun the entire batch, producing duplicates.

### Task
Propose a record-level idempotency design and a safer output approach.

### Solution
Give each logical transaction a stable record ID. Define result semantics around that key:

```text
completed record_id
→ reuse/skip/update according to the contract

new record_id
→ process and publish result
```

For file output, consider deterministic regeneration and safe replacement of a complete result file, or an explicitly keyed representation that prevents duplicates. Do not blindly append on every retry.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
The design needs both logical identity and a clear rule for existing results. A set of processed IDs is only a teaching model; production recovery must also account for crash windows and state persistence.

### Key Takeaway
Stable identity + duplicate-safe output semantics make reruns predictable.

---
## Question 21 — Functional Tests Pass, Performance Regresses

### Difficulty
Moderate

### Problem
A refactor passes all functional tests, but a representative batch job that used to take about 2 seconds now takes about 3 seconds.

### Task
Describe the evidence-based investigation before deciding whether to keep the change.

### Solution
Establish a baseline under the same workload, repeat the measurements, and inspect variance. If the source is unclear, profile with `cProfile` and `pstats`.

Use the workflow:

```text
baseline
→ measure
→ profile
→ bottleneck
→ hypothesis
→ one change
→ tests
→ measure again
→ compare
→ keep/revert
```

Also check memory and I/O if relevant.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
Functional correctness does not imply good performance. The performance regression should be investigated against the workload and environment that matter, rather than judged by one local timing.

### Key Takeaway
Correctness comes first, but performance decisions still need measured evidence.

---
## Question 22 — Safe Dependency Upgrade

### Difficulty
Moderate

### Problem
A developer wants to upgrade a direct dependency because a new patch release is available.

### Task
Give a disciplined upgrade workflow that covers compatibility, locking, testing, review, and rollback.

### Solution
1. Identify why the upgrade is needed.
2. Inspect the current resolved version.
3. Read release notes/changelog.
4. Check compatibility with the supported Python/application version.
5. Update the declaration if appropriate.
6. Resolve/update lock information.
7. Review direct and transitive changes.
8. Run unit/integration/application tests and lint/type checks.
9. Benchmark important paths when relevant.
10. Review security implications.
11. Make the change easy to identify and revert.
12. Deploy with verification and use rollback if necessary.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
A patch-level version number is not a perfect compatibility guarantee. The source module treats upgrades as controlled engineering changes, not just installation operations.

### Key Takeaway
Upgrade systematically, inspect the graph, test behavior, and preserve rollback.

---

# Section 3 — Hard

## Question 23 — Production CLI Startup Contract

### Difficulty
Hard

### Problem
A production CLI reads `MODEL_NAME`, `TIMEOUT_SECONDS`, and `LOG_LEVEL` from the environment, accepts `--input`, and writes a JSON report. Some paths print failures, another logs an error and returns 0, and malformed configuration fails deep inside processing.

### Task
Design the execution contract for parsing, validation, logging, error messages, output streams, and exit codes.

### Solution
Use one clear top-level boundary:

```text
parse CLI
→ load/validate configuration
→ validate input
→ log safe startup context
→ execute
→ summarize
→ exit 0
```

Expected failures should be translated deliberately:
- configuration/input failure → clear `stderr` + documented non-zero code;
- recoverable/known operational failure → appropriate log and non-zero result;
- unexpected defect → diagnostic logging/traceback + non-zero result.

Lower layers should raise meaningful exceptions rather than catching everything. The CLI boundary should decide the final process-facing behavior.


### Solution Code

```python
import logging
import os
import sys

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    pass

def load_config() -> dict:
    model = os.getenv("MODEL_NAME")
    if not model or not model.strip():
        raise ConfigurationError("MODEL_NAME is required")

    raw_timeout = os.getenv("TIMEOUT_SECONDS", "30")
    try:
        timeout = int(raw_timeout)
    except ValueError as exc:
        raise ConfigurationError(
            "TIMEOUT_SECONDS must be an integer"
        ) from exc

    if timeout <= 0:
        raise ConfigurationError(
            "TIMEOUT_SECONDS must be greater than 0"
        )

    return {"model_name": model.strip(), "timeout": timeout}

def main() -> int:
    try:
        config = load_config()
        logger.info("Starting with model=%s", config["model_name"])
        # CLI parsing and input validation would happen at this boundary too.
        run(config)
        return 0
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 4
    except Exception:
        logger.exception("Unexpected application failure")
        return 1

def run(config: dict) -> None:
    logger.info("Processing with timeout=%d", config["timeout"])

if __name__ == "__main__":
    sys.exit(main())
```
### Explanation
This integrates configuration, validation, logging, and exit-code design. It also provides the behavior that a README and runbook can document and automate reliably.

### Key Takeaway
One application boundary should own predictable CLI communication and process status.

---
## Question 24 — Crash-Safe and Rerunnable Result Publishing

### Difficulty
Hard

### Problem
A job processes 10,000 records and publishes `results.json`. It can crash after 7,000 results and is routinely rerun with the same input.

### Task
Design an application-level approach that avoids duplicate output, protects the previous valid file, and makes reruns predictable.

### Solution
Use stable record IDs and deterministic transformation rules. Define how an existing result is treated when a logical task is retried. For the published JSON file:

```text
generate complete candidate
→ write temporary file in destination directory
→ finish write
→ optionally sync for required durability
→ os.replace(candidate, destination)
```

Track job/record completion state separately if resume behavior is needed. Avoid append-only publication for a file that represents one logical complete result set.


### Solution Code

```python
from pathlib import Path
import json
import os
import tempfile

def publish_results(path: Path, results: dict[str, dict]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temp:
        temp_path = Path(temp.name)
        json.dump(results, temp, indent=2, sort_keys=True)
        temp.flush()

    try:
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)
```
### Explanation
Idempotency answers “is this the same logical work?” Safe file writes answer “can I publish the new state without exposing an incomplete destination?” Both are required for a robust rerunnable batch result.

### Key Takeaway
Stable identity and safe publication solve different parts of the rerun problem.

---
## Question 25 — Profile Before Rewriting the Loop

### Difficulty
Hard

### Problem
A Python data pipeline has a nested loop and appears slow. A developer rewrites the loop immediately using a compact comprehension, but total job time does not improve.

### Task
Describe an evidence-based investigation with timing, profiling, and a before/after comparison.

### Solution
First measure the representative end-to-end workload with `time.perf_counter()`. Then profile the whole program with `cProfile` and inspect the profile with `pstats`, especially `cumtime` and `tottime`.

If file I/O or JSON serialization dominates, changing the loop may have negligible effect. If a small function is called millions of times and its cumulative cost is substantial, reducing that cost may be a good optimization hypothesis.

After identifying the bottleneck, make one meaningful change, run functional tests, benchmark again, compare distributions, and keep or revert based on measured evidence.


### Solution Code

```python
import cProfile
import pstats

def run_pipeline(data):
    return [sum(value * 2 for value in row) for row in data]

profiler = cProfile.Profile()
profiler.enable()
result = run_pipeline([[1, 2, 3] for _ in range(10_000)])
profiler.disable()

pstats.Stats(profiler).strip_dirs().sort_stats("cumtime").print_stats(20)
print(len(result))
```
### Explanation
Call count alone does not define cost, and source-code complexity alone does not define a bottleneck. `cumtime` and `tottime` answer different questions and should be interpreted in context.

### Key Takeaway
Profile the real workflow before optimizing a suspicious-looking line.

---
## Question 26 — Faster CPU, Higher Memory

### Difficulty
Hard

### Problem
A refactor reduces CPU runtime, but `tracemalloc` shows much higher peak traced memory because the new version builds large intermediate lists.

### Task
Explain how you would evaluate the trade-off and decide whether the change is worthwhile.

### Solution
Measure both relevant dimensions against the same workload:

```text
before: runtime + current/peak traced memory
after:  runtime + current/peak traced memory
```

Use snapshots when you need to identify allocation sources and `get_traced_memory()` for current/peak traced-memory observations.

Then compare the result with the application's performance budget and memory headroom. A runtime improvement is not automatically an improvement if it causes unacceptable memory pressure or operational instability.


### Solution Code

```python
import tracemalloc

def build_intermediate(n: int) -> list[int]:
    return [value * 2 for value in range(n)]

tracemalloc.start()
tracemalloc.reset_peak()
data = build_intermediate(100_000)
current, peak = tracemalloc.get_traced_memory()
print(f"current={current} peak={peak}")
tracemalloc.stop()
```
### Explanation
This is a time/space trade-off. Profiling and memory measurement are complementary: the CPU can improve while the application's resource risk increases.

### Key Takeaway
Keep an optimization only when the overall performance objective improves without violating relevant memory constraints.

---
## Question 27 — Transitive Vulnerability During Upgrade

### Difficulty
Hard

### Problem
A security advisory affects a transitive package. Your application declares only A and B, but the resolved environment contains the affected package through A. The application tests currently pass.

### Task
Design a defensive investigation and remediation workflow without assuming the application is automatically exploitable.

### Solution
1. Identify the affected package and versions.
2. Inspect the dependency tree and determine which direct dependency introduced it.
3. Check the resolved version and lock information.
4. Review release notes for A and potential fixes.
5. Look for a compatible upgrade path.
6. Update and re-resolve intentionally.
7. Review the resulting dependency diff.
8. Run unit/integration tests and important application workflows.
9. Consider whether the affected package is actually used/exposed in the relevant application path.
10. Prepare rollback if behavior changes.

Do not force an arbitrary version just because it removes the advisory; compatibility and application usage still matter.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
The source lesson distinguishes “known vulnerability exists” from “application is definitely exploitable.” Risk depends on affected versions, application use, exposure, and remediation context. The key engineering job is tracing the transitive package back to a controlled dependency change.

### Key Takeaway
Trace security findings through the dependency graph, remediate deliberately, and verify.

---
## Question 28 — Documentation Drift After a CLI Change

### Difficulty
Hard

### Problem
The application changed from:

```bash
python app.py
```

to:

```bash
python -m app
```

Code and tests were updated, but the README and recovery runbook still use the old command.

### Task
Design the documentation update and the engineering process change that prevents similar drift.

### Solution
Update the README usage/installation examples and the runbook's operational procedure and verification steps.

Then treat behavior-changing code changes as documentation-review triggers:

```text
code behavior change
→ tests
→ documentation review
→ release notes/changelog review
```

Where the command appears in multiple operational documents, search and review all relevant occurrences during the change.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
The source lesson calls this documentation drift: software changes while instructions remain stale. A technically correct README can still be operationally wrong if its commands no longer match the application.

### Key Takeaway
Documentation must evolve with observable software behavior.

---
## Question 29 — Failed Deployment: Use Evidence and Verification

### Difficulty
Hard

### Problem
A release deployment command succeeds, but post-deployment verification finds the application unhealthy. An operator wants to immediately run the same deployment again.

### Task
Describe the safer investigation path using release identity, logging, runbooks, verification, and rollback.

### Solution
1. Identify the exact release/artifact deployed.
2. Inspect post-deployment verification results.
3. Review relevant logs and known failure symptoms.
4. Determine whether the problem is configuration, dependency, or application behavior.
5. Follow documented recovery steps if a known condition applies.
6. If the release cannot be safely recovered, execute the documented rollback to the previous known-good release.
7. Verify the rolled-back version.
8. Preserve evidence and record the outcome.

Do not equate a successful deployment command with a healthy application.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
The deployment tool reports that deployment happened; the verification procedure answers whether the application behaves as expected. Release traceability connects the incident to a specific change.

### Key Takeaway
Deployment completion is not health; verify behavior and use rollback when the release is not acceptable.

---
## Question 30 — AI Batch Pipeline Reliability Review

### Difficulty
Hard

### Problem
An LLM batch pipeline is:

```text
configuration
→ input validation
→ prompt construction
→ model/API call
→ response parsing
→ output file
```

It retries requests, sometimes receives malformed responses, and can crash while writing output.

### Task
Design a Stage 1 reliability approach that integrates the learned production habits.

### Solution
Use:
- validated startup configuration;
- boundary validation for input and model/tool response data;
- stable task/record IDs reused across retries;
- explicit duplicate-safe result semantics;
- safe logs with job/task/attempt/status context and no secrets;
- safe temporary-file publication for important output;
- tests for malformed responses, retries, partial failures, and repeated execution;
- README usage/configuration/troubleshooting;
- a runbook for recovery and safe retry;
- versioned releases with verification and rollback.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
This combines the same patterns used by ordinary data/CLI software. Model-generated structured output should be validated before downstream use because it is external data from the application's perspective.

### Key Takeaway
AI workloads still need ordinary boundary validation, failure handling, idempotency, safe persistence, and documentation.

---
## Question 31 — Define a Meaningful Checkpoint

### Difficulty
Hard

### Problem
A batch job writes a checkpoint after reading each record. After a crash, the checkpoint says “read through record 100,” but logs show only records 1–90 were fully transformed and written.

### Task
Explain why the checkpoint is unsafe and redefine its meaning for recovery.

### Solution
The checkpoint is based on “read” rather than the externally relevant completion state. A safe checkpoint should describe a condition the recovery logic can rely on.

For this workflow, a better meaning would be:

```text
processed through record 90
```

where “processed” is explicitly defined to mean the required transformation and output publication completed successfully.

Recovery should use that semantic definition, not simply the largest record number that was read.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
A checkpoint is only useful if it corresponds to a trustworthy state boundary. Advancing it before required side effects complete can cause data to be skipped after recovery.

### Key Takeaway
Checkpoint semantics must describe what is actually guaranteed completed.

---
## Question 32 — Diagnose a Corrupted State File

### Difficulty
Hard

### Problem
After a crash, `job-state.json` contains:

```text
{"job_id":"job-42","status":"com
```

The old implementation directly opened the file with `"w"` and wrote JSON in place.

### Task
Identify the likely cause, redesign the update, and describe how you would test the failure path.

### Solution
The direct truncating write likely removed the previous contents and failed before the new JSON was complete.

Use:

```text
construct state in memory
→ serialize candidate
→ write temporary file beside destination
→ finish write
→ optional sync according to durability needs
→ os.replace()
→ cleanup
```

Tests should verify that a successful update produces valid JSON and that an injected write failure leaves the previous destination unchanged and does not leave unwanted temporary artifacts.


### Solution Code

```python
import json
import os
import tempfile
from pathlib import Path

def safe_update_state(path: Path, state: dict) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as temp:
        temp_path = Path(temp.name)
        json.dump(state, temp, indent=2, sort_keys=True)
        temp.flush()

    try:
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)
```
### Explanation
Atomic replacement moves the risky write away from the published destination. It improves update integrity but should not be described as an absolute guarantee against every hardware or filesystem failure.

### Key Takeaway
Write the new state completely before publishing it over the last known-good state.

---
## Question 33 — Noisy Benchmark After an Optimization

### Difficulty
Hard

### Problem
Before an optimization:

```text
1.00, 1.03, 1.01, 1.04, 1.02
```

After it:

```text
0.98, 1.20, 1.01, 0.99, 1.05
```

The engineer says the optimization is proven because the minimum dropped from 1.00 to 0.98.

### Task
Explain why the conclusion is too strong and design a better measurement plan.

### Solution
The samples overlap substantially and the after-set contains an outlier. A minimum alone does not prove a meaningful improvement.

Repeat the benchmark with:
- identical representative inputs;
- equivalent setup;
- controlled measurement of the target;
- enough repeated runs to characterize variability;
- awareness of scheduling, CPU frequency, caches, garbage collection, warm-up, background load, and I/O variability.

Use `timeit.repeat()` for suitable microbenchmarks and profile the larger workflow when the bottleneck location is unknown.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
Benchmark numbers are measurements under conditions, not universal constants. The source chapter explicitly warns against optimizing from one favorable statistic or one run.

### Key Takeaway
Interpret the distribution of measurements, not just the best number.

---

# Section 4 — Advanced

## Question 34 — End-to-End Incident: AI Batch Pipeline

### Difficulty
Advanced

### Problem
A production AI batch pipeline has these symptoms:

- a required environment variable is missing on some machines;
- invalid records fail deep inside processing;
- logs have no stable job/task identity;
- a timeout retry can duplicate work;
- direct `"w"` writes can leave incomplete JSON;
- a recent dependency upgrade changed behavior;
- the batch is slower;
- the README lacks recovery instructions;
- the runbook has no rollback verification.

### Task
Design a complete engineering response covering investigation, corrective design, testing, documentation, release, deployment verification, and rollback.

### Solution
**Investigation:** identify release/artifact, job/task IDs, current configuration, retry history, output state, dependency diff, and performance baseline.

**Configuration/validation:** validate required settings and input records at their boundaries.

**Logging:** add safe job/task/attempt/status context and exception diagnostics without secrets.

**Idempotency:** define stable task IDs and duplicate-safe retry semantics.

**File safety:** generate complete candidate output, stage it in a temporary file, and replace the destination only after the write is complete.

**Performance:** measure a representative workload, profile with `cProfile`/`pstats`, use `tracemalloc` if memory is relevant, then make one evidence-based optimization.

**Dependencies:** inspect declared/resolved state, release notes, direct/transitive changes, and test compatibility.

**Documentation:** update README, add a runbook for failure/retry/recovery, and prepare release notes.

**Release/deployment:** create an identifiable artifact, complete handoff, deploy, verify, and roll back if necessary.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
Each technique solves a different problem. The integrated workflow is more important than any individual tool: configuration/validation protect inputs, logging preserves evidence, idempotency handles repetition, safe writes protect published state, profiling identifies real cost, dependency management controls changes, and runbooks/releases make recovery operational.

### Key Takeaway
Production reliability comes from composing simple, testable engineering habits.

---
## Question 35 — Design a Safe Python CLI Contract

### Difficulty
Advanced

### Problem
A production CLI accepts `--input`, `--output`, and `--environment` and reads `MODEL_TIMEOUT` and `API_KEY` from the environment. It will be used by both humans and CI/CD automation.

### Task
Design the program contract for parsing, configuration, validation, logging, secrets, stdout/stderr, exit codes, and documentation.

### Solution
Use `argparse` for the command-line contract and validate environment values separately. Reject malformed configuration and inputs before normal processing.

Use named logging with safe context and never log `API_KEY`. Send concise expected-error messages to `stderr`. Reserve `stdout` for normal command output as appropriate.

Define `0` as success and deliberate non-zero meanings for documented failure classes. Allow unexpected defects to retain diagnostic information.

Document the complete contract in the README; document recovery and operational failure handling in the runbook; identify the deployed version and rollback path in release/deployment documentation.


### Solution Code

```python
import logging
import os
import sys

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    pass

def load_timeout() -> int:
    raw = os.getenv("MODEL_TIMEOUT", "30")
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(
            "MODEL_TIMEOUT must be an integer"
        ) from exc
    if value <= 0:
        raise ConfigurationError(
            "MODEL_TIMEOUT must be greater than 0"
        )
    return value

def main() -> int:
    try:
        timeout = load_timeout()
        logger.info("CLI started timeout=%d", timeout)
        # argparse/input validation would occur here.
        return 0
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 4

if __name__ == "__main__":
    sys.exit(main())
```
### Explanation
This design lets humans understand the failure while automation receives a predictable process status. It also makes the behavior documentable and testable.

### Key Takeaway
A production CLI is an interface to both people and automation; make its contract explicit.

---
## Question 36 — Concurrency Plus Crash Window

### Difficulty
Advanced

### Problem
Two workers execute:

```python
if operation_id in processed:
    return

perform_side_effect()
processed.add(operation_id)
```

The process can also crash between the side effect and the completion marker.

### Task
Explain both duplicate-processing mechanisms and state the production lesson.

### Solution
There are two separate windows.

**Crash window:** the side effect can succeed, but the process crashes before `processed.add()`. A retry sees no marker and repeats the side effect.

**Concurrency race:** Worker A and Worker B can both observe “not processed” before either adds the identifier, so both perform the work.

The lesson from the source chapter is not to add more local checks. Stable identity is necessary but insufficient. Production semantics must ensure that the state used to recognize completion and the side-effect behavior are coordinated according to the application's concurrency model.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
The chapter intentionally introduces concurrency only as vocabulary. The key reasoning skill is recognizing that a non-atomic “check then act” sequence is not a complete guarantee under concurrency or crash failure.

### Key Takeaway
Check-before-process is a useful pattern, not a universal idempotency guarantee.

---
## Question 37 — Performance Regression With Multiple Signals

### Difficulty
Advanced

### Problem
A new implementation is 18% faster in a local benchmark, but production reports higher latency and memory usage. `cProfile` shows lower cumulative time in one function, while `tracemalloc` shows new large allocations.

### Task
Design the investigation and decision process.

### Solution
1. Reproduce the workload with representative inputs.
2. Establish a trustworthy baseline.
3. Measure wall-clock time and CPU time when useful.
4. Profile the actual workflow with `cProfile`.
5. Inspect `pstats` using `cumtime` and `tottime`.
6. Use `tracemalloc` snapshots/current/peak measurements to investigate allocation growth.
7. Check whether I/O, serialization, setup, or input size differs from the local benchmark.
8. Run functional and end-to-end checks.
9. Compare the result with a defined performance budget.
10. Evaluate maintainability as well as speed.
11. Keep or revert based on relevant evidence.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
A microbenchmark can improve while the full workflow gets worse. The correct target is the performance characteristic that matters under representative workload and operating conditions.

### Key Takeaway
Optimize the system metric that matters, not the easiest local benchmark.

---
## Question 38 — Dependency Conflict and Release Safety

### Difficulty
Advanced

### Problem
A production AI application declares direct dependencies A and B. A new A release requires a newer transitive helper than B currently permits. The upgrade also contains an important fix, and the project uses lock information.

### Task
Design the resolution, testing, release, deployment, and rollback workflow.

### Solution
Inspect the dependency tree and identify the exact incompatible constraints. Review release notes for A and B and determine whether a compatible B version or another supported combination exists.

Update the dependency set deliberately, refresh the lock information, and review all direct/transitive changes.

Run unit/integration tests, critical AI application workflows, and performance-sensitive workloads when relevant. Prepare a traceable release artifact, use the deployment runbook, verify behavior after deployment, and retain the previous known-good release for rollback.

Do not force a transitive helper version simply because the top-level upgrade is desirable.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
The lock state improves reproducibility but does not solve compatibility by itself. The release process converts the dependency change into a controlled, reversible production change.

### Key Takeaway
Dependency graph resolution, testing, traceability, and rollback are one lifecycle.

---
## Question 39 — Production Documentation Pack

### Difficulty
Advanced

### Problem
A Python data-processing application serves developers, scheduled operators, and release engineers. A single 300-line README currently contains setup instructions, recovery commands, historical changes, and deployment notes.

### Task
Redesign the documentation structure using the module's artifact distinctions.

### Solution
Use:

**README:** project purpose, prerequisites, installation, configuration, usage, examples, inputs/outputs, testing, structure, and common troubleshooting.

**Runbook:** operational purpose, preconditions, expected state, procedure, verification, failure handling, rollback, escalation, and evidence.

**Changelog:** historical meaningful changes by version.

**Release notes:** the important changes and operational impact of one specific release.

**Deployment handoff:** release identity, change summary, configuration/dependency/data impacts, deployment steps, verification, rollback, and ownership.

Cross-link these artifacts so the reader can move from orientation to operation to release without guessing.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
The problem is not document length. It is that multiple audiences and jobs are competing for one artifact. Separating them improves discoverability and maintainability.

### Key Takeaway
Good documentation is structured information flow between people and the software lifecycle.

---
## Question 40 — Failed Release With Rollback

### Difficulty
Advanced

### Problem
Version `2.0.0` is deployed successfully from the deployment tool's perspective, but verification finds unhealthy behavior. The release changed code and configuration defaults. Version `1.9.3` is still available as an identifiable known-good release.

### Task
Describe what must be checked before rollback and how verification fits into the recovery path.

### Solution
Identify the current release/artifact and configuration first. Inspect logs and verification evidence.

Before rollback, check:
- the old release artifact is available;
- the previous code is compatible with the current configuration;
- no state/data change makes code rollback unsafe.

If rollback is appropriate, deploy `1.9.3` using the documented procedure, restore compatible configuration as required, and perform post-rollback verification.

Record the failure, deployed release, evidence, and rollback result for traceability. Update the runbook/release documentation if the incident exposes a missing procedure.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
A Git tag or version identifies a source state, but safe rollback depends on deployable artifacts and compatibility with configuration/state. This is why rollback planning belongs in release preparation, not only after an incident begins.

### Key Takeaway
Rollback is a release-and-state problem, not merely a source-code problem.

---
## Question 41 — AI Evaluation Pipeline: Dependency Change Plus Partial Failure

### Difficulty
Advanced

### Problem
An LLM evaluation pipeline:

```text
load dataset
→ validate cases
→ call model client
→ parse output
→ score
→ write results
```

After a client-library upgrade, response parsing changes and some runs fail after partial completion.

### Task
Design the engineering and runbook response.

### Solution
Identify the deployed release, dependency version, evaluation run ID, and affected case IDs.

Then:
1. inspect dependency/release notes and the dependency diff;
2. inspect logs for parsing failures and partial completion;
3. validate actual response shapes before scoring;
4. determine which case IDs completed;
5. use stable evaluation-case identity when retrying;
6. keep result publication safe;
7. decide whether to roll back the dependency/release or fix the parser;
8. run regression/integration tests on representative responses;
9. update README/troubleshooting/runbook guidance;
10. document the release impact and verify deployment after remediation.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
This combines dependency management with validation, idempotency, logging, safe persistence, and operational documentation. It does not assume the library upgrade is the only possible cause; evidence must connect the change to the observed behavior.

### Key Takeaway
Treat AI client-library upgrades as application behavior changes and make recovery repeatable.

---
## Question 42 — Full Local-to-Production Lifecycle

### Difficulty
Advanced

### Problem
You inherit a working Python CLI with weak configuration handling, print-only diagnostics, direct file output, undocumented setup, and no release procedure.

### Task
Design the end-to-end production lifecycle using only the eight learned modules.

### Solution
A coherent lifecycle is:

```text
configuration contract
→ validation
→ safe logging
→ idempotent processing
→ safe file writes
→ measurement/profiling
→ dependency declaration/lock
→ tests
→ README
→ runbook
→ version/release
→ artifact
→ deployment handoff
→ verification
→ rollback
```

Prioritize:
1. explicit configuration and boundary validation;
2. predictable failure and logging behavior;
3. stable identities and safe reruns;
4. safe file publication;
5. baseline/profiling where performance matters;
6. controlled dependency state and upgrades;
7. documented setup and operations;
8. versioned release with verification and rollback.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
Production readiness is a connected lifecycle. Logging without recovery, a lock file without tests, or a README without operational procedures each leaves important gaps.

### Key Takeaway
Production software is code plus the tested, documented, measurable, and recoverable way the code is operated.

---
## Question 43 — Multi-Failure Debugging Scenario

### Difficulty
Advanced

### Problem
An overnight job reports SUCCESS but output contains duplicate records. Logs have no job ID. Scheduler history shows an automatic retry after a timeout. The application also received a dependency upgrade yesterday.

### Task
Build a diagnosis from evidence to root cause candidates and define corrective actions.

### Solution
**Evidence**
- scheduler history proves a retry occurred;
- missing job/operation IDs make correlation harder;
- duplicate output suggests repeated side effects;
- a timeout leaves the first attempt's outcome uncertain;
- append-like output can accumulate duplicates;
- the dependency upgrade is a possible behavior change, but not yet a proven cause.

**Corrective actions**
- stable job/record IDs;
- duplicate-safe retry semantics;
- safe output publication;
- useful logs with attempt/status identity;
- explicit success/failure exit behavior;
- dependency review and regression tests;
- a runbook for retry/recovery.

Do not claim the dependency caused the duplicates until evidence connects it to the observed behavior.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
This is a debugging exercise in disciplined reasoning. Start with the event sequence and observable facts, then use the module's production tools to eliminate uncertainty.

### Key Takeaway
Reconstruct what actually happened before assigning causality or changing code.

---
## Question 44 — Final Integrated Production Assessment

### Difficulty
Advanced

### Problem
A Python batch AI application processes a daily dataset, calls an external model service, writes JSON results, and ships as a versioned release.

A new deployment has these findings:

- a required environment variable is missing on some machines;
- invalid records fail deep inside processing;
- logs lack stable job/task identity;
- timeout retries may duplicate work;
- direct `"w"` output writes can leave incomplete data after a crash;
- a recent dependency upgrade is present;
- the batch now takes longer;
- the README lacks setup/configuration details;
- the runbook lacks rollback verification;
- the deployment handoff does not clearly identify the deployed version.

### Task
Produce a complete engineering response organized as: investigation plan, design corrections, verification plan, release plan, and operational documentation plan. Explain trade-offs and how you would prove the final system is safer and more predictable.

### Solution
**Investigation:** identify the deployed release/artifact; compare configuration; reconstruct retries with job/task IDs; inspect output state; review dependency changes; establish a performance baseline; capture documentation gaps.

**Design corrections:** validate configuration and input at boundaries; log safe operational context; introduce stable task identity; make retries duplicate-safe; stage important JSON writes in temporary files and publish with replacement; define appropriate durability requirements.

**Performance:** profile the representative workflow with `cProfile`/`pstats`; use `timeit` for isolated candidates; use `tracemalloc` if memory is implicated; optimize only after identifying a bottleneck.

**Dependency control:** inspect declared and resolved state, review release notes, test the upgrade, and make rollback easy.

**Verification:** test normal and failure paths, repeated execution, retry behavior, file-failure behavior, CLI exit behavior, dependency compatibility, and representative performance.

**Release/deployment:** update version/changelog/release notes, build an identifiable artifact, complete handoff, deploy, and perform post-deployment verification.

**Operations:** README covers setup/configuration/usage/testing/troubleshooting; runbook covers failed jobs, safe retry, output verification, rollback, escalation, and evidence; rollback considers configuration/state compatibility.

**Trade-offs:** use stronger durability controls only where requirements justify their cost; avoid excessive logging or dependency complexity; preserve correctness and maintainability.

### Solution Code

No code is required for this conceptual or design-oriented question.

### Explanation
This final assessment requires integration across all eight lessons. The correct answer is not a particular framework or platform; it is a disciplined sequence that makes boundaries, failure modes, recovery behavior, dependency changes, performance evidence, documentation, and release state explicit.

### Key Takeaway
Production engineering means making normal behavior, failure behavior, and recovery behavior explicit, observable, testable, and reversible where practical.

---

# Practice Coverage Matrix

The matrix reflects the actual coverage of the 44 questions. A check mark means the question materially tests that source module.

| Question | Configuration | Logging | Validation | Idempotency | Safe File Writes | Profiling | Dependencies | README / Runbook / Release |
|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | ✓ |  | ✓ |  |  |  |  |  |
| 2 |  | ✓ |  |  |  |  |  |  |
| 3 |  |  | ✓ |  |  |  |  |  |
| 4 |  |  |  | ✓ | ✓ |  |  |  |
| 5 |  |  |  |  | ✓ |  |  |  |
| 6 |  |  |  |  |  | ✓ |  |  |
| 7 |  |  |  |  |  |  | ✓ |  |
| 8 |  |  |  |  |  |  |  | ✓ |
| 9 | ✓ |  | ✓ |  |  |  |  |  |
| 10 |  | ✓ |  |  |  |  |  |  |
| 11 |  |  |  |  |  |  |  | ✓ |
| 12 | ✓ |  | ✓ |  |  |  |  | ✓ |
| 13 | ✓ | ✓ | ✓ |  |  |  |  |  |
| 14 |  |  |  | ✓ |  |  |  |  |
| 15 |  |  |  | ✓ | ✓ |  |  |  |
| 16 |  |  |  |  |  | ✓ |  |  |
| 17 |  |  |  |  |  |  | ✓ | ✓ |
| 18 | ✓ |  |  |  |  |  |  | ✓ |
| 19 |  | ✓ | ✓ | ✓ |  |  |  | ✓ |
| 20 |  |  |  | ✓ | ✓ |  |  |  |
| 21 |  |  |  |  |  | ✓ |  | ✓ |
| 22 |  |  |  |  |  | ✓ | ✓ | ✓ |
| 23 | ✓ | ✓ | ✓ |  |  |  |  | ✓ |
| 24 |  |  |  | ✓ | ✓ |  |  |  |
| 25 |  |  |  |  |  | ✓ |  |  |
| 26 |  |  |  |  |  | ✓ |  |  |
| 27 |  |  |  |  |  |  | ✓ | ✓ |
| 28 |  |  | ✓ |  |  |  |  | ✓ |
| 29 |  | ✓ |  |  |  |  | ✓ | ✓ |
| 30 | ✓ | ✓ | ✓ | ✓ | ✓ |  |  | ✓ |
| 31 |  | ✓ |  | ✓ | ✓ |  |  |  |
| 32 |  |  | ✓ | ✓ | ✓ |  |  |  |
| 33 |  |  |  |  |  | ✓ |  |  |
| 34 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 35 | ✓ | ✓ | ✓ |  |  |  |  | ✓ |
| 36 |  | ✓ |  | ✓ |  |  |  |  |
| 37 |  |  |  |  |  | ✓ |  |  |
| 38 |  |  |  |  |  | ✓ | ✓ | ✓ |
| 39 | ✓ | ✓ |  |  |  |  | ✓ | ✓ |
| 40 | ✓ | ✓ |  |  |  |  | ✓ | ✓ |
| 41 |  | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| 42 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 43 |  | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| 44 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Coverage Notes

The questions intentionally overlap modules. For example, configuration questions may also test validation and logging; safe-rerun questions may also test safe file writes; release questions may also test dependencies and operational documentation. The matrix records that intentional overlap rather than forcing each question into one category.

---

# Final Module Completion Check

Before moving forward, I should be able to:

### Configuration
- [ ] Configure a Python application safely.
- [ ] Distinguish configuration from code, data, and secrets.
- [ ] Read environment variables with appropriate defaults or required-value behavior.
- [ ] Convert configuration strings into the intended types.
- [ ] Validate configuration at startup.
- [ ] Centralize configuration so parsing and validation are predictable.
- [ ] Avoid exposing secrets in logs or documentation.

### Logging
- [ ] Use the `logging` module for operational evidence.
- [ ] Choose appropriate log levels.
- [ ] Use named loggers and understand hierarchy/propagation.
- [ ] Include useful job/request/operation context safely.
- [ ] Use exception logging when appropriate.
- [ ] Use lazy logging formatting.
- [ ] Avoid logging passwords, API keys, tokens, and unnecessary sensitive payloads.
- [ ] Keep diagnostic logging separate from user-facing CLI output where appropriate.

### Validation / Errors / Exit Codes
- [ ] Validate external input at the boundary.
- [ ] Distinguish missing, malformed, invalid, operational, and unexpected failures.
- [ ] Use appropriate exception types.
- [ ] Raise and catch exceptions deliberately.
- [ ] Understand propagation and exception chaining.
- [ ] Write useful and safe error messages.
- [ ] Validate CLI arguments.
- [ ] Understand `sys.exit()` and `SystemExit`.
- [ ] Use predictable non-zero exit behavior for failures.
- [ ] Understand stdout vs stderr.

### Idempotency / Repeatable Jobs
- [ ] Explain repeatability, determinism, and idempotency.
- [ ] Identify duplicate side effects.
- [ ] Give logical operations stable identifiers.
- [ ] Understand idempotency keys.
- [ ] Understand the limitations of check-before-process.
- [ ] Reason about crash windows and unknown outcomes.
- [ ] Design job and record state.
- [ ] Design for partial failure and meaningful checkpoints.
- [ ] Distinguish job-level from record-level idempotency.
- [ ] Make retries safe where the underlying operation supports duplicate-safe semantics.

### Safe File Writes
- [ ] Understand `open()` modes, especially `w`, `a`, and `x`.
- [ ] Understand truncation and partial writes.
- [ ] Use context managers for ordinary file handling.
- [ ] Understand temporary-file staging.
- [ ] Understand same-filesystem considerations.
- [ ] Use `os.replace()` appropriately for atomic publication.
- [ ] Distinguish atomicity from durability.
- [ ] Explain `flush()`, `fileno()`, and `os.fsync()`.
- [ ] Safely update JSON/CSV/state files.
- [ ] Test failure cleanup and preservation of the previous valid destination.

### Profiling / Measurement
- [ ] Explain latency, throughput, wall-clock time, CPU time, and memory usage.
- [ ] Use `time.perf_counter()` for elapsed-duration measurement.
- [ ] Understand `time.process_time()`.
- [ ] Use `timeit.timeit()` and `timeit.repeat()` for appropriate microbenchmarks.
- [ ] Design benchmarks that isolate their target.
- [ ] Understand warm-up, caches, garbage collection, scheduling, CPU frequency, and I/O noise.
- [ ] Use `cProfile` and `pstats`.
- [ ] Interpret `ncalls`, `tottime`, `cumtime`, and `percall`.
- [ ] Use `tracemalloc` and snapshots for Python allocation investigation.
- [ ] Establish a baseline and measure again after optimization.
- [ ] Preserve correctness while optimizing.

### Dependencies / Supply Chain
- [ ] Distinguish direct and transitive dependencies.
- [ ] Read a dependency graph.
- [ ] Understand `pyproject.toml` dependency declarations.
- [ ] Explain version specifiers and SemVer limitations.
- [ ] Distinguish declared requirements from resolved versions.
- [ ] Explain lock-file purpose and limits.
- [ ] Use basic `uv` project/dependency workflows.
- [ ] Separate runtime and development dependencies appropriately.
- [ ] Plan and test dependency upgrades.
- [ ] Review dependency diffs, including transitive changes.
- [ ] Understand typosquatting and dependency confusion conceptually.
- [ ] Understand malicious/compromised packages and vulnerable dependencies.
- [ ] Understand provenance, integrity/hashes, dependency inventory, SBOM, and CI checks at a foundational level.
- [ ] Prepare a rollback plan.

### README / Runbook / Release
- [ ] Write a useful README for project orientation and use.
- [ ] Document prerequisites, installation, configuration, usage, inputs/outputs, testing, and common troubleshooting.
- [ ] Distinguish README, runbook, changelog, release notes, and deployment handoff.
- [ ] Write runbook preconditions, procedures, verification, failure handling, escalation, and rollback.
- [ ] Distinguish source code, commit, artifact, release, and deployment.
- [ ] Understand versioning and Semantic Versioning.
- [ ] Prepare changelog and release notes.
- [ ] Prepare deployment handoff information.
- [ ] Verify behavior after deployment.
- [ ] Understand why rollback can be complicated by configuration or state changes.
- [ ] Maintain release traceability.
- [ ] Recognize documentation drift as an engineering problem.

### Integrated Production Reasoning
- [ ] Start from evidence instead of guessing.
- [ ] Make boundaries and failure modes explicit.
- [ ] Design normal paths and failure paths together.
- [ ] Assume retries/reruns can happen when appropriate.
- [ ] Protect important side effects and published files.
- [ ] Measure before optimizing and measure again afterward.
- [ ] Treat dependency changes as production changes.
- [ ] Keep operational knowledge in discoverable documentation.
- [ ] Make releases identifiable and recoverable.
- [ ] Explain how to verify that a change actually worked.

# Final Assessment Standard

The goal of these 44 questions is not only to produce correct answers. You should be able to explain:

```text
What is the boundary?
What can fail?
What evidence will I collect?
What should the program do?
What should the operator do?
How will I verify success?
How will I recover if it fails?
```

A strong mental model for the complete module is:

```text
CONFIGURE
    ↓
VALIDATE
    ↓
LOG SAFELY
    ↓
PROCESS PREDICTABLY
    ↓
MAKE RERUNS SAFE
    ↓
PERSIST OUTPUT SAFELY
    ↓
MEASURE / PROFILE
    ↓
MANAGE DEPENDENCIES
    ↓
DOCUMENT OPERATION
    ↓
RELEASE
    ↓
DEPLOY
    ↓
VERIFY
    ↓
ROLL BACK / RECOVER WHEN NECESSARY
```

# File-Scope Note

This practice set is self-contained. No separate exercise or solution files are required.
