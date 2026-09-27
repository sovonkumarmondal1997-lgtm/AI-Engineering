# Idempotency and Repeatable Jobs in Python

This chapter is part of **Stage 1 — Programming & Computational Thinking → 10 — Production Habits for Python Programs**.

The central production question is:

> **What happens if this program runs again?**

A beginner often imagines:

```text
input → process → output → done
```

Production work is more like:

```text
input → process → side effect → crash
                         ↓
                       retry
                         ↓
                     run again
```

A process can fail even after some of its work has already succeeded. That is why important jobs should be designed for reruns, retries, partial failures, and recovery.

> **Core production habit:** Never assume an important job runs exactly once. Design its externally visible behavior so repetition is safe and predictable within the application's failure model.

**Scope boundary:** this chapter focuses on Python/application-level idempotency, repeatability, deterministic processing, duplicate prevention, job state, retries, file/data processing, batch jobs, and Applied AI/data workloads. It does not attempt to teach distributed consensus, Kafka internals, Kubernetes job orchestration, advanced locking, or full payment infrastructure.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain what a job is and why jobs fail;
- distinguish retry, rerun, determinism, repeatability, and idempotency;
- identify side effects that can be duplicated;
- give logical operations stable identities;
- use sets and dictionaries for simple local completion tracking;
- explain why check-before-process is useful but incomplete;
- identify crash windows and partial failures;
- represent job states explicitly;
- choose appropriate overwrite, append, update, reuse, or skip semantics;
- design deterministic transformations where practical;
- reason about file and CSV processing;
- design retry-aware batch processing;
- test the second execution rather than only the first;
- reason about resumable LLM, embedding, and evaluation workloads;
- use logs to reconstruct job, attempt, and record activity.

The learning loop is:

```text
Understand
→ Predict
→ Implement
→ Test normal case
→ Test edge cases
→ Simulate failure
→ Rerun
→ Debug
→ Refactor
→ Document
→ Explain aloud
```

---

## 2. Why Jobs Need to Be Safe to Rerun

Imagine an invoice processor:

```python
def process_invoice(invoice):
    result = calculate_total(invoice)
    save_result(result)
```

Suppose `save_result()` succeeds, but the process crashes before the scheduler receives a success signal.

A scheduler may later run the job again.

That creates:

```text
Attempt 1 → result saved
Attempt 1 → process crashes
Attempt 2 → same invoice processed
```

The key question is not:

> Did the first process fail?

It is:

> **What externally visible work happened before it failed?**

A rerun can otherwise create:

- duplicate records;
- duplicate output files;
- duplicate notifications;
- repeated external requests;
- repeated expensive inference;
- inconsistent job state.

A safe job therefore treats reruns as a normal design case.

---

## 3. What Is a Job?

A **job** is a unit of work that can start, make progress, succeed, fail, and potentially run again.

A job can be:

```text
CLI command
Python script
scheduled task
batch process
data transformation
ingestion process
AI evaluation
model inference batch
embedding generation
```

The basic shape is:

```text
Input
  ↓
Processing
  ↓
Output / Side Effect
```

Examples:

```text
CSV → validate → transform → output CSV

records → process → result store

documents → embed → vector/result storage

prompts → infer → evaluation results
```

A job gives you a concrete boundary for questions such as:

```text
What identifies this job?
What identifies its records?
What does "completed" mean?
What happens after a crash?
What happens on a second run?
```

---

## 4. Why Jobs Fail

Jobs can fail because of:

```text
invalid input
configuration errors
programming bugs
missing files
permission problems
network failures
external service failures
timeouts
process crashes
machine restarts
resource exhaustion
```

Failure does not tell you how much work happened.

For example:

```text
100 records
   ↓
records 1–70 processed
   ↓
failure
```

The process failed, but records 1–70 may already exist outside the process.

Therefore:

> **A failed process is not necessarily an operation with zero side effects.**

That idea drives the rest of this chapter.

---

## 5. Why Jobs Are Retried

A **retry** is another attempt after a failure or uncertain outcome.

Reasons include:

- transient network errors;
- timeouts;
- temporary dependency failures;
- process crashes;
- scheduled retry policies;
- manual recovery;
- CI/CD reruns.

Conceptually:

```text
Attempt 1
   ↓
failure / unknown outcome
   ↓
Attempt 2
   ↓
success
```

The dangerous case is:

```text
Attempt 1
   ↓
external system performs action
   ↓
response is lost
   ↓
caller sees timeout
   ↓
Attempt 2
   ↓
external action happens again
```

Retry logic says:

> “Try again.”

Idempotent design says:

> “Trying again does not create an unwanted additional externally relevant effect.”

These are different responsibilities.

---

## 6. What Does "Run Again" Mean?

“Run again” can mean several things.

### Manual rerun

An engineer starts yesterday's job again.

### Automatic retry

A scheduler restarts a failed operation.

### Resume

The process continues from a checkpoint rather than restarting all work.

### Reprocessing

The same source data is deliberately processed again because the transformation changed.

These cases have different intentions.

For example:

```text
retry
= same logical operation, another attempt

rerun
= execute the job again

reprocess
= intentionally process the input again under a new purpose/configuration
```

A production design should know which behavior is intended.

---

## 7. What Is Repeatability?

A repeatable job behaves predictably when run again with the same intended inputs and assumptions.

```text
Input A
  ↓
Run 1
  ↓
Logical Output X

Input A
  ↓
Run 2
  ↓
Logical Output X
```

Repeatability commonly depends on:

```text
input
code version
configuration
dependencies
environment
external state
randomness
time
output semantics
```

Repeatability does **not** always mean identical bytes.

A report can include a current timestamp and still be logically repeatable if the timestamp is intentionally treated as run metadata.

Distinguish:

```text
same logical result
```

from:

```text
byte-for-byte identical artifact
```

The correct standard depends on the application.

---

## 8. What Is Determinism?

A deterministic computation gives the same result for the same relevant inputs and state.

```python
def double(value: int) -> int:
    return value * 2


print(double(10))
print(double(10))
```

Both results are:

```text
20
20
```

Compare:

```python
import random


def choose_score() -> int:
    return random.randint(1, 100)
```

Two calls can return different values.

Other common sources of nondeterminism are:

```text
current time
random IDs
changing configuration
changing external data
unspecified ordering
external service responses
```

The standard `random` module provides pseudo-random generation; uncontrolled randomness can make repeated computations differ.

Determinism helps repeatability:

```text
deterministic computation
        ↓
better repeatability
```

But:

```text
deterministic computation
≠
idempotent side effects
```

A job can calculate the same value every time and still append that value to a file repeatedly.

---

## 9. What Is Idempotency?

A practical engineering definition is:

> **An operation is idempotent when applying the same logical operation multiple times produces the same externally relevant final state as applying it once.**

Example:

```text
set status = "completed"
```

First application:

```text
pending → completed
```

Second application:

```text
completed → completed
```

The final state is unchanged by repetition.

Contrast:

```text
append "completed" to a list
```

First:

```text
[]
→
["completed"]
```

Second:

```text
["completed"]
→
["completed", "completed"]
```

The second operation changes external state again.

The key phrase is:

> **same logical operation**

Two independent business operations should not be collapsed merely because their data looks similar.

---

## 10. Mathematical Idea vs Engineering Meaning

The mathematical shorthand is:

```text
f(f(x)) = f(x)
```

Engineering asks a more practical question:

```text
Apply operation once
→ state S

Apply the same logical operation again
→ state S
```

Production engineers usually care about:

```text
stored results
files
records
status
messages
external resources
```

These are externally visible effects.

The useful habit is:

> **Define idempotency with respect to a specific operation, identity, and external state.**

Avoid saying simply:

> “This system is idempotent.”

Instead say:

> “Processing a transaction with this stable transaction ID is idempotent with respect to the result store.”

That statement is easier to test and defend.

---

## 11. Idempotent vs Non-Idempotent Operations

| Operation | Usually idempotent? | Reason |
|---|---|---|
| Set a value to `10` | Yes | Repetition reaches the same state |
| Replace a file with the same logical content | Often | Final logical state can remain the same |
| Delete an already absent item | Often | Final state remains absent |
| Add `1` to a counter | No | Every execution changes state |
| Append a row | Usually no | Duplicates accumulate |
| Send an email | Usually no | Each execution can send another message |
| Create a fresh random ID | No | Each execution creates new identity |
| Pure calculation `x * 2` | Yes | Same input produces same result |

“Usually” matters. Idempotency is semantic.

For any operation, ask:

```text
What is the logical identity?
What is the external state?
What does the first execution do?
What does the second execution do?
```

---

## 12. Safe Reruns

A safe rerun means:

> Running the job again after success or partial failure does not corrupt state or create unexpected duplicates.

Unsafe:

```text
read input
→ append result
→ crash
→ rerun
→ append result again
```

Safer:

```text
read input
→ identify record
→ compute result
→ store result under stable identity
→ rerun
→ reuse/update/replace existing result
```

Possible techniques include:

```text
stable IDs
deterministic transformations
replace/update semantics
processed markers
completion state
checkpoints
reconciliation
```

No single pattern fits every side effect.

---

## 13. Duplicate Side Effects

A side effect changes something observable outside a pure calculation.

Examples:

```text
write a file
insert a record
send an email
publish a message
call an external API
create an AI inference result
store an embedding
update job state
```

Pure computation:

```text
input → calculate → return
```

Side effect:

```text
input → calculate → change external state
```

Pure calculations are generally easier to rerun. Side effects need deliberate semantics.

Ask:

```text
What happens if this executes twice?
```

That single question catches many production bugs.

---

## 14. Idempotency Keys and Stable Identifiers

A stable identifier represents the same logical operation across attempts.

Common forms:

```text
job_id
operation_id
record_id
request_id
document_id
event_id
task_id
```

Example:

```python
operation_id = "invoice-12345"
```

A retry should preserve that identity:

```text
Attempt 1 → invoice-12345
Attempt 2 → invoice-12345
Attempt 3 → invoice-12345
```

Do not do:

```python
import uuid

operation_id = str(uuid.uuid4())
```

on every retry and expect duplicate detection to work.

A stable key must survive attempts.

Important nuance:

> An idempotency key does not automatically make an operation idempotent. The state or service receiving the key must use it to enforce the intended duplicate behavior.

---

## 15. Check-Before-Process Patterns

The simplest teaching model is:

```text
receive ID
   ↓
check state
   ↓
already completed?
 ↙         ↘
yes        no
 ↓          ↓
skip      process
            ↓
      record completion
```

Example:

```python
processed: set[str] = set()


def process(operation_id: str) -> str:
    if operation_id in processed:
        return "already processed"

    processed.add(operation_id)
    return "processed"


print(process("invoice-123"))
print(process("invoice-123"))
```

Expected:

```text
processed
already processed
```

### Why this is only a teaching example

The set is in memory.

Restarting Python loses it:

```text
process exits
↓
set disappears
↓
new process starts with empty set
```

Two workers also do not automatically share it.

Most importantly, the following crash window remains:

```text
check
↓
side effect
↓
CRASH
↓
record completion
```

So “check first” is useful but not a universal guarantee.

---

## 16. The Crash Window

Consider:

```text
check → not processed
      ↓
side effect succeeds
      ↓
process crashes
      ↓
completion marker never recorded
```

After restart:

```text
state says "not processed"
        ↓
rerun
        ↓
side effect repeats
```

The central lesson is:

> **The time between a side effect and recording completion is a correctness boundary.**

Production designs must define how that boundary is handled.

This is why idempotency cannot be reduced to:

```python
if key in state:
    skip()
```

The state itself must be meaningful, durable when required, and correctly ordered with respect to the external effect.

---

## 17. Recording Job State

Explicit job states make recovery easier to reason about.

```python
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
```

Usage:

```python
status = JobStatus.PENDING

if status is JobStatus.PENDING:
    status = JobStatus.RUNNING

print(status.value)
```

Output:

```text
running
```

Python's `Enum` provides named symbolic members bound to values. citeturn695273search11

A state should have a clear meaning.

For example:

```text
COMPLETED
= all required work and outputs satisfy the defined success criteria
```

Do not use state values as decoration. They should drive human and recovery decisions.

---

## 18. Job State Transitions

A minimal lifecycle is:

```text
PENDING
   ↓
RUNNING
   ↓
COMPLETED
```

Failure:

```text
RUNNING
   ↓
FAILED
```

Rerun:

```text
FAILED
   ↓
RUNNING
```

Real systems may add:

```text
RETRYING
CANCELLED
PARTIALLY_COMPLETED
```

The exact states are application-specific.

What matters is that every transition has a clear condition.

For example:

```text
PENDING → RUNNING
= execution has begun

RUNNING → COMPLETED
= success criteria satisfied

RUNNING → FAILED
= job cannot satisfy success criteria
```

---

## 19. Partial Failure

A partial failure occurs when some work succeeds and some does not.

```text
100 records
   ↓
70 processed
   ↓
failure
```

Recovery questions:

```text
Did records 1–70 really complete?
Did record 71 partially change state?
Should 1–70 be skipped?
Can 71 be retried safely?
What about 72–100?
```

Possible approaches:

```text
restart all
resume from checkpoint
retry failed records
reconcile by stable IDs
```

Restarting all work is acceptable when earlier operations are idempotent and the cost is reasonable.

Checkpointing is useful when there is a meaningful completed boundary.

Record-level recovery is useful when individual records can be identified and processed independently.

---

## 20. Checkpoints

A checkpoint records a recovery boundary:

```text
processed through record 1000
```

Then:

```text
crash
 ↓
restart
 ↓
read checkpoint
 ↓
resume
```

But what does “processed” mean?

```text
read?
validated?
transformed?
written?
committed?
```

Those are different guarantees.

A correct checkpoint should answer:

> **What state can I safely assume is true when I resume?**

Example:

```text
checkpoint = "records 1–100 were successfully written"
```

is stronger and clearer than:

```text
checkpoint = "read index 100"
```

Checkpointing reduces repeated work, but it does not automatically make a job idempotent.


## 21. Overwrite vs Append

Append:

```python
with open("results.txt", "a", encoding="utf-8") as file:
    file.write("result\n")
```

Every execution adds another result.

Overwrite:

```python
with open("results.txt", "w", encoding="utf-8") as file:
    file.write("result\n")
```

A later execution replaces the file contents under normal file semantics.

Neither is universally correct.

Use append when the data is intentionally append-only.

Use replacement/update semantics when a file represents the current complete result for a logical input.

The next lesson, `05-safe-file-writes.md`, focuses on crash-safe file writing. This chapter only establishes the idempotency question:

> **What should happen to an output file when the job runs again?**

Python's `Path.write_text()` similarly overwrites an existing file with the same path under ordinary semantics. citeturn695273search4

---

## 22. Deterministic Output Paths

Compare:

```text
output_001.csv
output_002.csv
output_003.csv
```

with:

```text
results/customer-123.csv
```

A stable path is easier to associate with a logical record.

```python
from pathlib import Path

customer_id = "customer-123"
output_path = Path("results") / f"{customer_id}.csv"

print(output_path)
```

Output:

```text
results/customer-123.csv
```

Useful `pathlib` APIs include:

```python
output_path.exists()
output_path.is_file()
output_path.read_text(encoding="utf-8")
output_path.write_text("data", encoding="utf-8")
```

`Path.exists()` checks whether a path exists, while `Path.is_file()` checks whether it refers to a regular file. citeturn695273search5

Stable paths improve predictability, but they do not by themselves provide atomic or crash-safe writes.

---

## 23. Safe File-Based Jobs

Naive append:

```python
from pathlib import Path


def append_results(path: Path, rows: list[str]) -> None:
    with path.open("a", encoding="utf-8") as file:
        for row in rows:
            file.write(row + "\n")
```

Repeated execution duplicates the rows.

A replacement-style teaching implementation:

```python
from pathlib import Path


def write_results(path: Path, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(rows) + "\n"
    path.write_text(content, encoding="utf-8")
```

Now:

```text
same input
+
same destination
+
replacement semantics
```

makes reruns easier to reason about.

But the write can still be interrupted. A crash during writing can leave an incomplete artifact.

That is intentionally deferred to the safe-file-write lesson.

---

## 24. Repeatable CSV Processing

A common pipeline is:

```text
transactions.csv
    ↓
validate
    ↓
transform
    ↓
write
```

Example input:

```text
transaction_id,amount
T1,10
T2,20
```

Deterministic transform:

```python
def double_amount(amount: int) -> int:
    return amount * 2
```

Result:

```text
T1,20
T2,40
```

Stable record IDs then give you a way to recognize the same logical transaction.

A simple local store:

```python
results: dict[str, int] = {}


def process_transaction(transaction_id: str, amount: int) -> int:
    existing = results.get(transaction_id)

    if existing is not None:
        return existing

    result = double_amount(amount)
    results[transaction_id] = result
    return result
```

The design question is not just “how do I detect duplicates?”

It is:

> What should happen if the same ID appears again with a different input value?

That should be explicitly defined by the data contract.

---

## 25. Idempotency with Database-Like Concepts

Four useful concepts are:

```text
unique identifier
duplicate detection
upsert
processed marker
```

An **upsert** can be understood conceptually as:

```text
if record does not exist:
    create it
else:
    update/reuse it
```

For example:

```text
record_id = T123

first attempt → create T123
retry          → find/update T123
```

A conceptual operation might look like:

```sql
UPSERT result WHERE record_id = 'T123'
```

This is deliberately not a database course. The important application-level principle is:

> **A stable identifier plus deliberate existing-record semantics is the foundation of duplicate-safe state updates.**

---

## 26. Batch Jobs

Batch work may involve:

```text
10 records
1,000 records
1,000,000 records
all files received today
all evaluation cases for a model version
```

Useful scopes:

```text
job
batch
record
side effect
```

A large job might be:

```text
Job
├── Batch 1
├── Batch 2
├── Batch 3
└── Batch 4
```

Ask whether recovery should happen at:

```text
job level
batch level
record level
```

Record-level recovery is often useful when records are independent.

It is less suitable when record ordering or dependencies are important.

---

## 27. Job-Level vs Record-Level Idempotency

### Job-level

The entire logical job can be repeated safely.

```text
job_id = daily-transactions-2026-09-24
```

### Record-level

Each logical record can be repeated safely.

```text
transaction_id = T123
```

A production batch often needs both:

```text
job identity
+
record identity
```

Example:

```text
job: daily-transactions-2026-09-24
   ↓
T1
T2
T3
...
```

If the job reruns, record identity can prevent already completed transactions from being duplicated.

Do not assume that a job ID alone protects every side effect inside the job.

---

## 28. Retries + Idempotency

Consider:

```text
Attempt 1
   ↓
timeout
   ↓
Attempt 2
```

The safe assumption is:

```text
Attempt 1 may have succeeded.
```

A retry becomes safer when:

```text
same logical operation ID
+
same side-effect semantics
+
duplicate-aware downstream state
```

The identity must remain stable.

Do not interpret:

```text
retry_count += 1
```

as an idempotency mechanism.

A retry counter records attempts; it does not prevent duplicate effects.

---

## 29. Retry Without Idempotency

Unsafe:

```python
def send_result(result: dict[str, object]) -> None:
    external_service_create_result(result)
```

Failure sequence:

```text
Attempt 1
   ↓
service creates result
   ↓
response times out
   ↓
caller thinks failure occurred
   ↓
Attempt 2
   ↓
service creates second result
```

The unknown outcome is the real problem.

Ask:

> Could the previous attempt have succeeded?

If yes, the retry design must tolerate that possibility.

---

## 30. Idempotent Retry Design

Simplified pattern:

```python
def process(operation_id: str) -> dict[str, object]:
    existing = lookup_result(operation_id)

    if existing is not None:
        return existing

    result = compute_result()
    save_result(operation_id, result)
    return result
```

This expresses:

```text
stable identity
→ lookup
→ reuse if present
→ compute if absent
→ store under same identity
```

### Limitation

This can race under concurrency:

```text
Worker A → lookup → missing
Worker B → lookup → missing
Worker A → compute
Worker B → compute
```

Therefore:

> **A check-then-act sequence is not automatically an atomic uniqueness guarantee.**

A stronger production design may require durable coordinated state or an atomic uniqueness constraint.

---

## 31. Concurrency and Duplicates

Two workers can both observe:

```text
not processed
```

before either records completion.

Timeline:

```text
Worker A → check → not found
Worker B → check → not found
Worker A → process
Worker B → process
```

The local code may be correct in each worker and still produce a duplicate globally.

The important vocabulary is:

```text
check-then-act race
atomic uniqueness
coordinated state
```

You do not need advanced distributed locking to understand the beginner-level lesson:

> **If more than one actor can perform the same side effect, local in-memory checks may not be sufficient.**

---

## 32. Configuration and Repeatability

Repeatability depends on more than source input.

A practical model:

```text
Input
+
Code version
+
Configuration
+
Dependencies
+
Environment
+
Relevant external state
```

For AI jobs, configuration may include:

```text
model name
model version
prompt template version
generation parameters
tool configuration
```

For data jobs:

```text
input location
filter window
schema rules
output location
```

The earlier `01-configuration-and-env-files.md` lesson covers configuration itself. Here the connection is:

> **If you cannot identify the assumptions that affect a job's result, reproducing that result becomes harder.**

---

## 33. Logging + Idempotency

Logging provides evidence; idempotency controls repeated effects.

Useful safe context includes:

```text
job_id
operation_id
record_id
attempt
status
processed_count
skipped_count
failed_count
```

Example:

```python
import logging

logger = logging.getLogger(__name__)


def log_attempt(job_id: str, attempt: int) -> None:
    logger.info(
        "Processing job_id=%s attempt=%d",
        job_id,
        attempt,
    )
```

Logs can show:

```text
job=2026-09-24 attempt=1 processed=700 failed=1
job=2026-09-24 attempt=2 skipped=700 processed=300 failed=0
```

Do not log raw sensitive payloads just to make duplicate debugging easier.

A useful three-part model is:

```text
State / idempotency
        ↓
what happens

Logging
        ↓
what evidence is recorded

Recovery
        ↓
how the next attempt proceeds
```

---

## 34. Validation + Idempotency

Validation should generally happen before unintended side effects.

```text
external input
    ↓
validate
    ↓
stable identity
    ↓
check existing state
    ↓
process
    ↓
store result
```

Why?

A malformed record should ideally fail before it causes:

```text
invalid output
unnecessary model inference
partial state
confusing retry behavior
```

Boundary validation from the previous lesson therefore supports idempotent design:

> **Reject known-invalid work before committing avoidable side effects.**

---

## 35. Applied AI/Data Workloads

### LLM batch inference

```text
1,000 tasks
   ↓
model inference
   ↓
1,000 results
```

If the process crashes after 700:

```text
restart
```

A naive design repeats all 1,000.

A resumable design uses:

```text
task_id
   ↓
check result
   ↓
reuse completed
   ↓
infer missing
```

### Embedding pipelines

```text
document_id
   ↓
chunk identity
   ↓
embedding
   ↓
result storage
```

Stable document/chunk identity helps reruns find the correct logical result.

### Evaluation pipelines

```text
evaluation_case_id
+
model/version/configuration
   ↓
evaluation result
```

A useful logical result key often includes the dimensions that define what “the same evaluation” means.

The exact dimensions are application-specific.

---

## 36. Idempotency and Expensive AI Operations

Repeated AI work can lead to:

```text
duplicate inference
duplicate embeddings
duplicate evaluations
duplicate stored results
wasted compute
unnecessary token usage
```

The engineering problem is unnecessary repetition.

A useful summary is:

```text
submitted
completed previously
processed now
skipped
failed
```

For example:

```text
submitted=1000
previously_completed=700
processed_now=300
skipped=700
failed=0
```

Do not make provider-specific pricing claims. The general engineering lesson is enough:

> **A resumable job can avoid repeating work that has already completed.**

---

## 37. Common Idempotency Anti-Patterns

### Anti-pattern 1 — Blindly appending output

**Problem:** repeated runs accumulate duplicate rows.

**Why dangerous:** downstream systems may treat duplicates as legitimate.

**Bad example:**

```python
with open("results.txt", "a", encoding="utf-8") as file:
    file.write("result\n")
```

**Better approach:** define whether output is append-only or keyed/replaced.

**Production lesson:** output semantics must be deliberate.

### Anti-pattern 2 — New ID on every retry

**Problem:** each attempt appears to be a new operation.

**Why dangerous:** duplicate detection loses logical identity.

**Bad example:**

```python
import uuid

operation_id = str(uuid.uuid4())
```

generated independently for each attempt.

**Better approach:** create the logical ID once and reuse it across attempts.

**Production lesson:** stable identity survives retries.

### Anti-pattern 3 — Assuming retry means no prior effect

**Problem:** timeout is treated as proof of total failure.

**Why dangerous:** the previous effect may already exist.

**Better approach:** treat ambiguous outcomes as potentially successful effects.

**Production lesson:** communication failure is not equivalent to side-effect failure.

### Anti-pattern 4 — Check-before-process without crash analysis

**Problem:** the design stops at duplicate lookup.

**Why dangerous:** side effect and completion marker can become inconsistent.

**Better approach:** reason about the entire state transition.

**Production lesson:** check-then-act is only one piece of the design.

### Anti-pattern 5 — No stable record ID

**Problem:** reruns have no identity boundary.

**Why dangerous:** the system cannot reliably recognize logical duplicates.

**Better approach:** define a stable ID as part of the data contract.

**Production lesson:** identity is a first-class design decision.

### Anti-pattern 6 — Job status says completed while output is incomplete

**Problem:** status is optimistic instead of truthful.

**Why dangerous:** recovery may skip work that is actually missing.

**Better approach:** define completion from actual success criteria.

**Production lesson:** state must mean something operationally.

### Anti-pattern 7 — Marking complete before side effect

**Problem:** completion state is recorded too early.

**Why dangerous:** a rerun can skip missing output.

**Better approach:** align the state transition with the real completion guarantee.

**Production lesson:** never publish a false success state.

### Anti-pattern 8 — Ignoring crash recovery after side effect

**Problem:** side effect can succeed before completion state is durable.

**Why dangerous:** duplicate side effect on retry.

**Better approach:** understand the guarantees of the underlying side effect and storage.

**Production lesson:** explicitly analyze the crash window.

### Anti-pattern 9 — Ignoring partial failure

**Problem:** all records are treated as one giant atomic operation.

**Why dangerous:** recovery repeats large amounts of work or creates duplicates.

**Better approach:** use record identities, checkpoints, or deliberate batch boundaries.

**Production lesson:** partial failure is normal in long-running jobs.

### Anti-pattern 10 — Deterministic calculation mistaken for idempotent job

**Problem:** pure computation is deterministic but output append is not.

**Why dangerous:** identical results can still be duplicated.

**Better approach:** separate computation from side-effect semantics.

**Production lesson:** determinism and idempotency are different properties.

### Anti-pattern 11 — Reprocessing the entire batch by default

**Problem:** successful work is repeated.

**Why dangerous:** extra time, compute, and duplicate risk.

**Better approach:** recover by meaningful record or batch boundaries.

**Production lesson:** rerun policy should be explicit.

### Anti-pattern 12 — No operation identity in logs

**Problem:** operators cannot reconstruct which work was repeated.

**Why dangerous:** incident diagnosis becomes guesswork.

**Better approach:** log safe job/operation/record IDs and attempt counts.

**Production lesson:** observable identity supports recovery.

---

## 38. Determinism vs Idempotency vs Repeatability

| Concept | Main question |
|---|---|
| Determinism | Does the same relevant input/state produce the same computation result? |
| Repeatability | Can I execute the job again and get predictable behavior? |
| Idempotency | Does repeating the same logical operation leave the same externally relevant final state? |

Key distinctions:

```text
deterministic computation
≠
idempotent side effect
```

and:

```text
repeatable job
≠
byte-for-byte identical output
```

Example:

```python
def calculate(value: int) -> int:
    return value * 2
```

is deterministic.

But:

```python
def run(value: int, path: str) -> None:
    result = calculate(value)

    with open(path, "a", encoding="utf-8") as file:
        file.write(f"{result}\n")
```

can produce duplicate side effects even though the calculation is deterministic.

Think of the concepts as complementary:

```text
Determinism
    ↓
same computation

Repeatability
    ↓
predictable rerun

Idempotency
    ↓
safe repeated logical effect
```

---

## 39. Testing Idempotency

The basic strategy is:

```text
run once
   ↓
capture final state
   ↓
run again
   ↓
compare final state
```

Simple example:

```python
results: dict[str, int] = {}


def process(task_id: str, value: int) -> int:
    existing = results.get(task_id)

    if existing is not None:
        return existing

    result = value * 2
    results[task_id] = result
    return result


first = process("task-1", 10)
second = process("task-1", 10)

assert first == second
assert len(results) == 1
```

The second assertion is essential.

Testing only:

```python
assert first == second
```

can miss side-effect duplication.

Also test:

```text
output files
result count
duplicate rows
completion markers
job state
number of attempted side effects
```

---

## 40. Testing Partial Failure

Inject a controlled failure.

```python
class InjectedFailure(RuntimeError):
    pass


def process_records(
    records: list[str],
    processed: set[str],
    *,
    fail_on: str | None = None,
) -> None:
    for record_id in records:
        if record_id in processed:
            continue

        if record_id == fail_on:
            raise InjectedFailure(record_id)

        processed.add(record_id)
```

Test the first attempt:

```python
import pytest


def test_partial_failure() -> None:
    records = ["r1", "r2", "r3", "r4"]
    processed: set[str] = set()

    with pytest.raises(InjectedFailure):
        process_records(records, processed, fail_on="r4")

    assert processed == {"r1", "r2", "r3"}
```

Then recovery:

```python
def test_recovery_after_partial_failure() -> None:
    records = ["r1", "r2", "r3", "r4"]
    processed = {"r1", "r2", "r3"}

    process_records(records, processed)

    assert processed == {"r1", "r2", "r3", "r4"}
```

This is a local state demonstration. A real external side effect may not have such simple semantics.

---

## 41. Testing Retries

Test:

```text
attempt 1 → failure
attempt 2 → success
```

Example:

```python
def run_with_retry(operation, *, max_attempts: int) -> int:
    attempts = 0

    while attempts < max_attempts:
        attempts += 1

        try:
            return operation()
        except RuntimeError:
            if attempts == max_attempts:
                raise

    raise AssertionError("unreachable")
```

Test:

```python
def test_retry_then_success() -> None:
    calls = 0

    def operation() -> int:
        nonlocal calls
        calls += 1

        if calls == 1:
            raise RuntimeError("temporary failure")

        return 42

    assert run_with_retry(operation, max_attempts=2) == 42
    assert calls == 2
```

Also test the side effect. A retry test that checks only the returned value does not prove duplicate safety.

---

## 42. Debugging Rerun Problems

Use this workflow:

```text
1. Identify the job
2. Identify the logical operation
3. Identify the input
4. Determine what completed
5. Determine what failed
6. Inspect persisted output/state
7. Identify retry/rerun attempts
8. Look for duplicate side effects
9. Determine whether the operation is truly idempotent
10. Add regression coverage
```

Read the evidence before changing code.

Useful logs may show:

```text
job_id
operation_id
record_id
attempt
status
counts
failure reason
```

Reconstruct the timeline.

For example:

```text
attempt=1 record=T1 processed
attempt=1 record=T2 processed
attempt=1 record=T3 timeout
attempt=2 record=T1 skipped
attempt=2 record=T2 skipped
attempt=2 record=T3 processed
```

That log tells you much more than:

```text
job failed
job retried
job completed
```

---

## 43. Complete Production Example

### Production-Style Repeatable Data Processing Job

This teaching example models:

```text
input records
    ↓
stable record IDs
    ↓
validation
    ↓
deterministic transformation
    ↓
idempotency check
    ↓
result storage
    ↓
job summary
```

The implementation deliberately uses an in-memory dictionary so that the lesson remains understandable.

```python
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ValidationError(ValueError):
    """Raised when a transaction violates the job contract."""


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    amount: int


@dataclass
class JobState:
    job_id: str
    status: JobStatus = JobStatus.PENDING
    processed_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0


class ResultStore:
    """Teaching-scale result store keyed by stable transaction ID."""

    def __init__(self) -> None:
        self._results: dict[str, int] = {}

    def get(self, transaction_id: str) -> int | None:
        return self._results.get(transaction_id)

    def save(self, transaction_id: str, result: int) -> None:
        self._results[transaction_id] = result

    def snapshot(self) -> dict[str, int]:
        return dict(self._results)


def validate(transaction: Transaction) -> None:
    if not transaction.transaction_id.strip():
        raise ValidationError("transaction_id is required")

    if not isinstance(transaction.amount, int):
        raise ValidationError("amount must be an integer")

    if transaction.amount < 0:
        raise ValidationError("amount must be non-negative")


def transform(transaction: Transaction) -> int:
    return transaction.amount * 2


def process_job(
    job: JobState,
    transactions: list[Transaction],
    store: ResultStore,
    *,
    fail_on: str | None = None,
) -> None:
    job.status = JobStatus.RUNNING

    logger.info(
        "job=%s status=%s",
        job.job_id,
        job.status.value,
    )

    try:
        for transaction in transactions:
            try:
                validate(transaction)
            except ValidationError as exc:
                job.failed_count += 1
                logger.error(
                    "job=%s record=%s validation_failed reason=%s",
                    job.job_id,
                    transaction.transaction_id or "<missing>",
                    exc,
                )
                continue

            existing = store.get(transaction.transaction_id)

            if existing is not None:
                job.skipped_count += 1
                logger.info(
                    "job=%s record=%s skipped=already_processed",
                    job.job_id,
                    transaction.transaction_id,
                )
                continue

            if transaction.transaction_id == fail_on:
                raise RuntimeError(
                    f"simulated failure for {transaction.transaction_id}"
                )

            result = transform(transaction)
            store.save(transaction.transaction_id, result)
            job.processed_count += 1

            logger.info(
                "job=%s record=%s processed",
                job.job_id,
                transaction.transaction_id,
            )

        job.status = (
            JobStatus.FAILED
            if job.failed_count
            else JobStatus.COMPLETED
        )

    except Exception:
        job.status = JobStatus.FAILED
        logger.exception(
            "job=%s unexpected_failure",
            job.job_id,
        )
        raise

    finally:
        logger.info(
            "job=%s status=%s processed=%d skipped=%d failed=%d",
            job.job_id,
            job.status.value,
            job.processed_count,
            job.skipped_count,
            job.failed_count,
        )
```

### Configure logging

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)
```

### First run

```python
transactions = [
    Transaction("T1", 10),
    Transaction("T2", 20),
    Transaction("T3", 30),
]

store = ResultStore()

first_job = JobState("daily-2026-09-24")

process_job(first_job, transactions, store)

print(store.snapshot())
```

Expected logical state:

```text
T1 → 20
T2 → 40
T3 → 60
```

### Second run

```python
second_job = JobState("daily-2026-09-24-rerun")

process_job(second_job, transactions, store)

print(store.snapshot())
```

The second run should skip existing record IDs.

### Simulate partial failure

```python
store = ResultStore()
failed_job = JobState("daily-2026-09-24-attempt-1")

try:
    process_job(
        failed_job,
        transactions,
        store,
        fail_on="T3",
    )
except RuntimeError:
    pass

print("after failure:", store.snapshot())
```

Expected logical state:

```text
T1 → 20
T2 → 40
```

### Recover

```python
retry_job = JobState("daily-2026-09-24-attempt-2")

process_job(
    retry_job,
    transactions,
    store,
)

print("after retry:", store.snapshot())
```

Now:

```text
T1 → 20
T2 → 40
T3 → 60
```

The retry reuses the stable IDs and skips T1/T2 because their results already exist.

### What the example demonstrates

```text
validation
stable record identity
deterministic computation
existing-result lookup
duplicate prevention
job state
logging
partial failure
rerun
recovery
```

### What it does not guarantee

This store is:

```text
in memory
single process
single worker
not durable across restart
not concurrency safe
```

It also has a possible crash window around any real external side effect.

The exact guarantee is:

> Within the lifetime of this Python process, the `ResultStore` contains at most one result per transaction ID.

That precision is important. Production engineering means knowing what your code guarantees and what it does not.

---

## 44. Production Design Patterns

### Pattern 1 — Deterministic transformation

```text
same input
→ same logical output
```

Solves inconsistent computation.

Limitation: it does not prevent duplicate side effects.

### Pattern 2 — Stable operation ID

```text
same logical operation
→ same ID
```

Solves identity across retries.

Limitation: downstream state must use the identity.

### Pattern 3 — Replace/update semantics

```text
same record
→ update existing result
```

Solves duplicate accumulation when “one current result per record” is the desired contract.

Limitation: the underlying write needs appropriate durability/coordination guarantees.

### Pattern 4 — Completion marker

```text
processed(record_id)
```

Solves recognition of completed work.

Limitation: side-effect ordering and crash windows matter.

### Pattern 5 — Checkpointing

```text
processed through N
```

Solves unnecessary reprocessing of large completed ranges.

Limitation: the checkpoint must have a precise meaning.

### Pattern 6 — Retry-safe processing

```text
same logical operation ID
→ reuse existing result
```

Solves duplicate work under expected retry behavior.

Limitation: the external operation must support the intended semantics.

### Pattern 7 — Separate computation from side effects

```text
input
 ↓
pure calculation
 ↓
side-effect boundary
```

Solves some reasoning complexity.

Limitation: the side effect still needs its own repeatability contract.

### Pattern 8 — Record-level recovery

```text
job
 ↓
record identity
 ↓
retry only missing/failed work
```

Solves unnecessary whole-batch repetition.

Limitation: not every workflow permits independent record retries.

---

## 45. Coding Example Requirements

Every major example should make clear:

```text
What problem are we solving?
Why does the naive approach fail?
What makes the improved approach safer?
What happens on first run?
What happens on second run?
What happens after partial failure?
What happens during retry?
What limitations remain?
```

Good teaching code is:

- syntactically valid;
- runnable;
- progressive;
- realistic;
- explicit about assumptions.

A large code block without explanation is not a good production-learning example.

---

## 46. Function/API Coverage Requirement

This lesson focuses on APIs that are directly useful for idempotent/repeatable jobs.

### File and path operations

```python
open()
Path.exists()
Path.is_file()
Path.read_text()
Path.write_text()
```

`Path.read_text()` reads decoded text from a path and `Path.write_text()` writes text to a path, overwriting an existing file with the same name under ordinary semantics. citeturn695273search4

### Collections and state

```python
set.add()
key in set
dict.get()
key in dict
```

Example:

```python
processed: set[str] = set()
processed.add("T1")

if "T1" in processed:
    print("already processed")
```

### Enum

```python
from enum import Enum
```

Used for explicit job lifecycle states.

### Randomness

```python
import random

random.random()
random.randint(1, 10)
```

Used here only to demonstrate nondeterministic computation.

### Logging

```python
logging.getLogger()
logger.info()
logger.warning()
logger.error()
logger.exception()
```

Used to record safe operational context.

### Testing

```python
import pytest

pytest.raises(...)
assert ...
```

### Subprocess testing

```python
import subprocess

result = subprocess.run(...)
result.returncode
result.stdout
result.stderr
```

Use subprocess testing when the process boundary itself is part of what you are testing.

---

## 47. Concept → Internal Mechanics → Practice

### Idempotency

```text
What?
Repeated logical operation has the same externally relevant final state.

Why?
Retries and reruns happen.

Python/application mechanics?
Stable identity + result lookup + defined write semantics.

Practice?
Run twice and inspect final state.
```

### Repeatability

```text
What?
Rerun behaves predictably.

Why?
Recovery and debugging need reproducibility.

Mechanics?
Control assumptions such as input, code, configuration, time, and randomness.

Practice?
Run the same transformation twice.
```

### Determinism

```text
What?
Same relevant input/state → same computation result.

Why?
Stable results are easier to reproduce.

Practice?
Remove uncontrolled randomness from a transformation.
```

### Stable identifiers

```text
What?
Same logical operation → same ID.

Why?
Duplicate detection needs identity.

Practice?
Build IDs from logical record fields.
```

### Job state

```text
What?
Explicit lifecycle state.

Why?
Recovery needs to know what happened.

Practice?
Model PENDING/RUNNING/COMPLETED/FAILED.
```

### Partial failure

```text
What?
Some work succeeded before the job failed.

Why?
Recovery cannot assume all-or-nothing behavior.

Practice?
Inject a failure and rerun.
```

### Checkpoint

```text
What?
A meaningful recovery boundary.

Why?
Avoid unnecessary reprocessing.

Practice?
State exactly what the checkpoint guarantees.
```

### Retry

```text
What?
Another attempt.

Why?
Transient or uncertain failures happen.

Danger?
Previous attempt may have had an effect.

Practice?
Test retry plus duplicate-safe final state.
```

---

## 48. Exercises

## Beginner

### Exercise 1 — Identify Idempotency

**Problem:** Classify these operations:

```text
A. set status = "active"
B. increment a counter
C. append a row
D. replace a report with the same content
```

**Requirements:** Explain the reason for each classification.

**Hints:** Focus on externally relevant final state.

**Expected behavior:** You should distinguish state-setting from state-changing operations.

**Solution:**

```text
A → idempotent
B → non-idempotent
C → usually non-idempotent
D → often idempotent with respect to final contents
```

**Explanation:** Repeated assignment reaches the same state. Increment and append create new changes. Replacement can restore the same final artifact.

---

### Exercise 2 — Create a Stable Operation ID

**Problem:** Build an ID from customer and invoice IDs.

**Requirements:** Same logical inputs must produce the same ID.

**Hints:** Do not generate a new random value on every call.

**Expected behavior:** Two calls with the same inputs return equal strings.

**Solution:**

```python
def operation_id(customer_id: str, invoice_id: str) -> str:
    return f"{customer_id}:{invoice_id}"


assert operation_id("C1", "INV7") == operation_id("C1", "INV7")
```

**Explanation:** The ID represents the logical operation, not the execution attempt.

---

### Exercise 3 — Track Processed Records

**Problem:** Skip records already seen in this process.

**Requirements:** Use a set.

**Hints:** Membership testing is the key operation.

**Expected behavior:** First call processes; second call skips.

**Solution:**

```python
processed: set[str] = set()


def process(record_id: str) -> str:
    if record_id in processed:
        return "skipped"

    processed.add(record_id)
    return "processed"


assert process("r1") == "processed"
assert process("r1") == "skipped"
```

**Explanation:** A set is simple for local duplicate tracking, but not durable across restarts.

---

### Exercise 4 — Deterministic Transformation

**Problem:** Multiply an amount by 100.

**Requirements:** The function must be deterministic.

**Hints:** Avoid time and randomness.

**Expected behavior:** `12` always produces `1200`.

**Solution:**

```python
def normalize(amount: int) -> int:
    return amount * 100


assert normalize(12) == 1200
assert normalize(12) == 1200
```

**Explanation:** Same input produces the same result.

---

## Intermediate

### Exercise 5 — Result Store by ID

**Problem:** Store one result per record ID.

**Requirements:** Reuse the existing result.

**Solution:**

```python
results: dict[str, int] = {}


def process(record_id: str, value: int) -> int:
    existing = results.get(record_id)

    if existing is not None:
        return existing

    result = value * 2
    results[record_id] = result
    return result
```

**Explanation:** The dictionary provides local identity-based result lookup.

---

### Exercise 6 — Represent Job Status

**Problem:** Create explicit states.

**Requirements:** Use an enum with:

```text
PENDING
RUNNING
COMPLETED
FAILED
```

**Solution:**

```python
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
```

**Explanation:** Explicit state is easier to reason about than scattered strings.

---

### Exercise 7 — Simulate Partial Failure

**Problem:** Process five records and fail on record 4.

**Requirements:** Preserve completed records.

**Solution:**

```python
processed: set[str] = set()


def process(records: list[str], fail_on: str) -> None:
    for record_id in records:
        if record_id in processed:
            continue

        if record_id == fail_on:
            raise RuntimeError(record_id)

        processed.add(record_id)


records = ["r1", "r2", "r3", "r4", "r5"]

try:
    process(records, "r4")
except RuntimeError:
    pass

assert processed == {"r1", "r2", "r3"}
```

**Explanation:** The job made partial progress before failure.

---

### Exercise 8 — Prove the Second Run

**Problem:** Run the same operation twice and verify one stored result.

**Requirements:** Check both return value and store size.

**Solution:**

```python
results: dict[str, int] = {}


def process(task_id: str, value: int) -> int:
    if task_id in results:
        return results[task_id]

    results[task_id] = value * 10
    return results[task_id]


first = process("task-1", 7)
second = process("task-1", 7)

assert first == second
assert len(results) == 1
```

**Explanation:** The state assertion proves that the second call did not create an additional logical result.

---

## Advanced

### Exercise 9 — Identify the Crash Window

**Problem:** Analyze:

```text
check
→ side effect
→ mark complete
```

**Requirements:** Identify where a crash can cause a duplicate.

**Solution:** The dangerous interval is after the side effect succeeds but before completion is recorded.

**Explanation:** On restart, state may falsely indicate that the work never happened.

---

### Exercise 10 — Job-Level vs Record-Level Identity

**Problem:** A daily job processes 10,000 transactions.

**Requirements:** Propose both a job ID and record IDs.

**Solution:**

```text
job_id = daily-transactions-2026-09-24

record_id = transaction-123
record_id = transaction-124
...
```

**Explanation:** Job identity identifies the batch; record identity enables targeted duplicate detection.

---

### Exercise 11 — AI Evaluation Key

**Problem:** Define an identity using:

```text
case_id
prompt_version
model_version
```

**Solution:**

```python
def evaluation_key(
    case_id: str,
    prompt_version: str,
    model_version: str,
) -> str:
    return f"{case_id}:{prompt_version}:{model_version}"
```

**Explanation:** The key captures the dimensions that define one logical evaluation result in this simplified design.

---

### Exercise 12 — Test Partial Recovery

**Problem:** Records 1–3 succeed and 4 fails. Rerun without failure.

**Requirements:** Do not duplicate 1–3.

**Solution:**

```python
results: dict[str, int] = {}


def process(record_id: str, value: int) -> int:
    if record_id in results:
        return results[record_id]

    results[record_id] = value * 2
    return results[record_id]


records = [("r1", 10), ("r2", 20), ("r3", 30)]

for record_id, value in records:
    process(record_id, value)

assert len(results) == 3

for record_id, value in records:
    process(record_id, value)

assert len(results) == 3
```

**Explanation:** The dictionary key prevents duplicate logical result entries in this local model.

---

## 49. Mini Project

# Repeatable and Idempotent Data Processing CLI

Build a self-contained job around:

```text
transactions.csv
```

Flow:

```text
Input
 ↓
Validation
 ↓
Stable Record ID
 ↓
Deterministic Processing
 ↓
Result Storage
 ↓
Completion Tracking
 ↓
Safe Rerun
 ↓
Summary
```

### Project Goal

Create a Python program that processes transactions safely under repeated execution.

### Requirements

Input fields:

```text
transaction_id
amount
```

Rules:

```text
transaction_id must be non-empty
amount must be a non-negative integer
```

Transformation:

```text
result = amount * 2
```

Required behavior:

- valid input succeeds;
- invalid data is rejected;
- the same transaction ID represents the same logical record;
- repeated runs do not create duplicate result entries;
- partial failure can be simulated;
- retry can finish incomplete work;
- status is explicit;
- logging includes safe identifiers;
- tests prove the second run is safe.

### Architecture

```text
CLI
 ↓
load input
 ↓
validate
 ↓
derive stable ID
 ↓
lookup existing result
 ↙                 ↘
exists              new
 ↓                    ↓
skip/reuse          transform
                       ↓
                    store
                       ↓
                 completion
                       ↓
                    summary
```

### Data Model

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    amount: int
```

### Step-by-Step Tasks

**Task 1 — Load records**

Start with a list of `Transaction` objects so the core behavior is easy to test.

**Task 2 — Validate**

Reject missing IDs, negative amounts, and wrong types.

**Task 3 — Define identity**

Use `transaction_id` as the logical record identity.

**Task 4 — Transform**

Use deterministic processing.

```python
def transform(amount: int) -> int:
    return amount * 2
```

**Task 5 — Store by ID**

Use:

```python
dict[str, int]
```

for the teaching implementation.

**Task 6 — Skip existing results**

Check the stable ID before creating a new result.

**Task 7 — Inject failure**

Allow a controlled failure at a known record.

**Task 8 — Rerun**

Rerun the same records after failure.

**Task 9 — Summarize**

Track:

```text
processed
skipped
failed
status
```

**Task 10 — Test**

Test:

```text
normal run
second run
partial failure
retry
```

### Failure Scenarios

#### Scenario A — Normal Run

```text
T1 → success
T2 → success
T3 → success
```

Expected:

```text
processed=3
skipped=0
failed=0
status=completed
```

#### Scenario B — Rerun

Expected:

```text
processed=0
skipped=3
failed=0
status=completed
```

#### Scenario C — Partial Failure

Inject:

```text
fail_on=T3
```

Expected:

```text
T1 stored
T2 stored
T3 failed
```

#### Scenario D — Recovery

Run again with no injected failure.

Expected:

```text
T1 skipped
T2 skipped
T3 processed
```

### CLI Wrapper and Process Behavior

Because this mini-project is described as a CLI, the final layer should separate reusable job logic from process-level behavior.

A small CLI can use `argparse` to parse a failure-injection option:

```python
import argparse
import sys


class ExitCode:
    SUCCESS = 0
    GENERAL_ERROR = 1
    VALIDATION_ERROR = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a repeatable transaction-processing job."
    )
    parser.add_argument(
        "--fail-on",
        default=None,
        help="Simulate a failure for a transaction ID.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    transactions = [
        Transaction("T1", 10),
        Transaction("T2", 20),
        Transaction("T3", 30),
    ]
    results: dict[str, int] = {}

    try:
        job = run(
            Job("cli-run"),
            transactions,
            results,
            fail_on=args.fail_on,
        )
    except RuntimeError:
        return ExitCode.GENERAL_ERROR

    if job.failed:
        return ExitCode.VALIDATION_ERROR

    return ExitCode.SUCCESS


if __name__ == "__main__":
    sys.exit(main())
```

The important design separation is:

```text
main()
   ↓
parse CLI arguments
   ↓
call application logic
   ↓
translate final application result
   ↓
return exit code
```

Then the operating-system boundary is:

```python
sys.exit(main())
```

`sys.exit()` raises `SystemExit`; when that exception reaches the interpreter without being intercepted, the process terminates with the requested exit status. An integer `0` conventionally represents successful termination and a non-zero status represents failure. citeturn695273search0turn695273search1

For automation, keeping `main()` responsible for returning an integer makes the reusable application logic easier to test than calling `sys.exit()` deep inside processing functions.

A real CLI should also use a defined persistent result store if the goal is restart recovery across separate processes. The in-memory `results` dictionary in this teaching example resets on every process start, so it demonstrates the application-level design but does not provide durable cross-process idempotency.

### Process-Level Exit Test

When the process boundary itself is part of the contract, use a subprocess test:

```python
import subprocess
import sys


def test_cli_failure_returns_nonzero() -> None:
    result = subprocess.run(
        [sys.executable, "app.py", "--fail-on", "T2"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
```

`subprocess.run()` returns a `CompletedProcess` object whose `returncode`, `stdout`, and `stderr` expose the process result and captured streams when requested.

The key assertion is not merely that Python raised an exception. It is that the **actual command-line process communicated failure to its caller**.

### Reference Solution

```python
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    amount: int


@dataclass
class Job:
    job_id: str
    status: JobStatus = JobStatus.PENDING
    processed: int = 0
    skipped: int = 0
    failed: int = 0


def validate(transaction: Transaction) -> None:
    if not transaction.transaction_id.strip():
        raise ValidationError("transaction_id is required")

    if not isinstance(transaction.amount, int):
        raise ValidationError("amount must be an integer")

    if transaction.amount < 0:
        raise ValidationError("amount must be non-negative")


def transform(transaction: Transaction) -> int:
    return transaction.amount * 2


def run(
    job: Job,
    transactions: list[Transaction],
    results: dict[str, int],
    *,
    fail_on: str | None = None,
) -> Job:
    job.status = JobStatus.RUNNING

    try:
        for transaction in transactions:
            try:
                validate(transaction)
            except ValidationError as exc:
                job.failed += 1
                logger.error(
                    "job=%s record=%s validation_failed reason=%s",
                    job.job_id,
                    transaction.transaction_id or "<missing>",
                    exc,
                )
                continue

            if transaction.transaction_id in results:
                job.skipped += 1
                logger.info(
                    "job=%s record=%s skipped",
                    job.job_id,
                    transaction.transaction_id,
                )
                continue

            if transaction.transaction_id == fail_on:
                raise RuntimeError(
                    f"simulated failure for {transaction.transaction_id}"
                )

            results[transaction.transaction_id] = transform(
                transaction
            )
            job.processed += 1

            logger.info(
                "job=%s record=%s processed",
                job.job_id,
                transaction.transaction_id,
            )

        job.status = (
            JobStatus.FAILED
            if job.failed
            else JobStatus.COMPLETED
        )

    except Exception:
        job.status = JobStatus.FAILED
        logger.exception(
            "job=%s unexpected_failure",
            job.job_id,
        )
        raise

    logger.info(
        "job=%s status=%s processed=%d skipped=%d failed=%d",
        job.job_id,
        job.status.value,
        job.processed,
        job.skipped,
        job.failed,
    )

    return job
```

### Example Workflow

```python
transactions = [
    Transaction("T1", 10),
    Transaction("T2", 20),
    Transaction("T3", 30),
]

results: dict[str, int] = {}

first = run(Job("attempt-1"), transactions, results)

second = run(Job("attempt-2"), transactions, results)

assert first.processed == 3
assert second.skipped == 3
assert results == {"T1": 20, "T2": 40, "T3": 60}
```

### Partial Failure

```python
results: dict[str, int] = {}

try:
    run(
        Job("failure-attempt"),
        transactions,
        results,
        fail_on="T3",
    )
except RuntimeError:
    pass

assert results == {"T1": 20, "T2": 40}
```

### Recovery

```python
retry = run(
    Job("retry-attempt"),
    transactions,
    results,
)

assert results == {"T1": 20, "T2": 40, "T3": 60}
assert retry.skipped == 2
assert retry.processed == 1
```

### Testing Strategy

Test at four levels:

```text
validation
→ input contract

first run
→ expected result

second run
→ no duplicate logical output

recovery
→ partial failure followed by retry
```

Example:

```python
def test_idempotent_rerun() -> None:
    transactions = [
        Transaction("T1", 10),
        Transaction("T2", 20),
    ]
    results: dict[str, int] = {}

    first = run(Job("first"), transactions, results)
    second = run(Job("second"), transactions, results)

    assert first.processed == 2
    assert second.skipped == 2
    assert len(results) == 2
```

### Production Improvements

A real system may later need:

```text
durable state
durable results
atomic uniqueness
safe file writes
real CSV parsing
configuration
CLI argument parsing
subprocess tests
stronger crash recovery
metrics
operational documentation
```

Those are future refinements. The teaching implementation intentionally does not claim these guarantees.

---

## 50. Interview Questions

### Basic

#### 1. What is idempotency?

**How to Think:** Repetition and final state.

**Answer:** Repeating the same logical operation produces the same externally relevant final state as performing it once.

**Why It Matters:** Retries and reruns become safer.

#### 2. What is a repeatable job?

**How to Think:** Predictability under another execution.

**Answer:** A job that can run again under the same assumptions with predictable behavior.

**Why It Matters:** Recovery and manual reruns become easier.

#### 3. Why are retries dangerous?

**How to Think:** Unknown outcome.

**Answer:** A previous attempt may have already performed its side effect before reporting failure.

**Why It Matters:** The retry can create duplicates.

#### 4. What is a side effect?

**How to Think:** External state change.

**Answer:** An observable change such as writing a file, creating a record, or sending a request.

**Why It Matters:** Side effects need deliberate repeatability semantics.

#### 5. What is deterministic behavior?

**How to Think:** Same inputs.

**Answer:** Same relevant input and state produce the same computation result.

**Why It Matters:** Determinism supports repeatability.

### Intermediate

#### 6. What is an idempotency key?

**How to Think:** Identity across attempts.

**Answer:** A stable identifier representing the same logical operation across retries/reruns.

**Why It Matters:** It enables duplicate recognition.

#### 7. Why are stable identifiers useful?

**How to Think:** Deduplication needs identity.

**Answer:** They allow separate attempts to be associated with the same logical record or operation.

**Why It Matters:** Recovery becomes tractable.

#### 8. What is partial failure?

**How to Think:** Some work completed.

**Answer:** A job fails after completing only part of its work.

**Why It Matters:** Recovery must distinguish completed from incomplete work.

#### 9. What is a checkpoint?

**How to Think:** Recovery boundary.

**Answer:** A recorded point whose meaning tells recovery what work can safely be assumed complete.

**Why It Matters:** It can reduce unnecessary reprocessing.

#### 10. Why can append-based processing cause duplicates?

**How to Think:** Every run adds new output.

**Answer:** Append does not inherently recognize that the logical result already exists.

**Why It Matters:** Reruns can multiply records.

#### 11. Deterministic vs idempotent?

**How to Think:** Computation versus side effect.

**Answer:** Determinism concerns computation results; idempotency concerns repeated logical effects on external state.

**Why It Matters:** A deterministic computation can still be written repeatedly.

### Advanced

#### 12. What happens if a process crashes after a side effect but before recording completion?

**How to Think:** State inconsistency.

**Answer:** The external effect may exist while completion state says it does not.

**Why It Matters:** Retry can duplicate the effect.

#### 13. Why is check-before-process insufficient?

**How to Think:** Crash window and concurrency.

**Answer:** A side effect can happen after the check and before completion is recorded, or two workers can pass the same check.

**Why It Matters:** A check is not the same as atomic coordination.

#### 14. How would you make an LLM batch job resumable?

**How to Think:** Stable task identity.

**Answer:** Use stable task IDs, store results keyed by those IDs, reuse completed results, and process missing work on recovery.

**Why It Matters:** It reduces repeat work and improves recovery.

#### 15. How would you prevent duplicate embeddings?

**How to Think:** Document/chunk identity.

**Answer:** Assign stable document and chunk identities and define update/reuse semantics for existing embeddings.

**Why It Matters:** Reruns do not unintentionally multiply logical records.

#### 16. How would you test idempotency?

**How to Think:** Compare external state.

**Answer:** Run twice and compare the final state, record count, files, markers, and side-effect count.

**Why It Matters:** Equal return values alone may hide duplicates.

#### 17. What is the limitation of an in-memory set?

**How to Think:** Restart and multi-worker behavior.

**Answer:** It disappears on process restart and is not automatically shared across workers.

**Why It Matters:** It is not a durable production solution.

---

## 51. Architecture Questions

### 1. How would you design a Python batch job that can safely be rerun?

**Structured answer:**

```text
define logical job identity
define record identity
validate inputs
make transformations deterministic where useful
define side-effect semantics
track meaningful completion
handle partial failure
test second execution
log job/record identity
```

**Assumption:** A single-process teaching model. Multi-worker systems require stronger coordination.

### 2. How would you design record-level idempotency?

Define a stable record ID and a rule for existing results:

```text
new ID → create
existing ID → reuse/update/skip
```

The rule must match the business semantics.

### 3. How would you design job-level idempotency?

Give the logical job a stable ID:

```text
daily-transactions-2026-09-24
```

Then define what a repeated job means:

```text
reuse
reconcile
resume
reprocess intentionally
```

### 4. What happens when a job crashes halfway through?

Inspect actual state rather than assuming all work failed.

Use:

```text
record IDs
status
checkpoints
output inspection
logs
```

to determine recovery.

### 5. How would you recover from partial failure?

Possible designs:

```text
restart safely if processing is idempotent
resume from a reliable checkpoint
retry failed records
reconcile existing results by stable identity
```

### 6. How would you handle retries with unknown outcomes?

Assume the earlier attempt may have succeeded. Reuse the same logical identity and ensure the side-effecting operation has duplicate-safe semantics.

### 7. How would you prevent duplicate AI inference results?

Key results by stable task identity and reuse stored results on a repeat attempt.

### 8. How would you make an embedding pipeline safe to rerun?

Define stable document/chunk identity, deterministic chunking where practical, and explicit update/reuse semantics.

### 9. How would you make a CLI safe for scheduled automation?

Define:

```text
predictable input contract
clear failure behavior
stable output semantics
meaningful logs
consistent exit behavior
```

### 10. What should logs contain to diagnose duplicate processing?

Where safe:

```text
job_id
operation_id
record_id
attempt
status
processed
skipped
failed
important failure context
```

### 11. What are the limitations of an in-memory idempotency set?

It has no restart durability, no cross-worker coordination, and no protection against side-effect/completion crash windows.

### 12. Why might concurrent workers still produce duplicates?

Because both workers can pass a non-atomic existence check before either records state.

The production solution depends on the underlying storage and concurrency model.

---

## 52. Debugging Scenarios

### Scenario 1 — Duplicate Records After Rerun

**Problem**

```text
Run 1 crashes after 70%.
Run 2 creates duplicates.
```

**How to Think**

Identify which records from Run 1 already exist.

**Diagnosis**

Compare output/state by stable record ID. If Run 2 blindly appends all records, the rerun semantics are wrong.

**Solution**

Use stable IDs and appropriate reuse/update/replace semantics.

**Production Lesson**

A rerun should be a tested behavior, not an emergency surprise.

### Scenario 2 — Same Job Creates Different Results

**Problem**

The same input generates different results.

**How to Think**

Look for nondeterminism.

**Diagnosis**

Check:

```text
randomness
current time
changing configuration
external state
ordering
model/version changes
```

**Solution**

Control or record the relevant sources of variation.

**Production Lesson**

Repeatability requires known assumptions.

### Scenario 3 — Retry Creates Duplicate Side Effect

**Problem**

A timeout causes a second external result.

**How to Think**

The first request may have succeeded.

**Diagnosis**

Inspect external state and request identity.

**Solution**

Use stable logical identity and duplicate-aware downstream behavior.

**Production Lesson**

Unknown outcome must be part of retry design.

### Scenario 4 — Check-Before-Process Still Duplicates

**Problem**

Two workers create the same result.

**How to Think**

Draw both timelines.

**Diagnosis**

Both observed “not found.”

**Solution**

Use a coordinated/atomic uniqueness mechanism appropriate to the storage system.

**Production Lesson**

Local checks are not global coordination.

### Scenario 5 — Checkpoint Is Wrong

**Problem**

Recovery skips records that were never fully written.

**How to Think**

Define what the checkpoint represents.

**Diagnosis**

The checkpoint means “read through N,” not “results through N are complete.”

**Solution**

Track a checkpoint tied to a meaningful completion guarantee.

**Production Lesson**

Checkpoint names must have precise semantics.

### Scenario 6 — AI Inference Work Repeats

**Problem**

A batch rerun recomputes already completed tasks.

**How to Think**

Look for stable task identity and result lookup.

**Diagnosis**

Task IDs are missing or a new ID is generated for every attempt.

**Solution**

Use stable task IDs and stored-result reuse.

**Production Lesson**

Recovery design can reduce unnecessary expensive computation.

### Scenario 7 — Job Says Complete but Output Is Missing

**Problem**

Status says `completed`; output is incomplete.

**How to Think**

Inspect state transition ordering.

**Diagnosis**

Completion was recorded before the real completion condition.

**Solution**

Tie status to a concrete success criterion.

**Production Lesson**

A status that lies is worse than a status that says failure.

---

## 53. Knowledge Check

### Question 1

Why is appending to an output file often unsafe for rerunnable jobs?

**Answer:** Because every execution can add another copy of the same logical result.

### Question 2

Why is generating a new random operation ID on every retry problematic?

**Answer:** The retry appears to be a new operation, so duplicate detection cannot associate it with the earlier attempt.

### Question 3

Why does deterministic computation not automatically make side effects idempotent?

**Answer:** The same computed value can still be appended, inserted, or sent repeatedly.

### Question 4

What happens if a process crashes after a side effect but before completion is recorded?

**Answer:** External state may show the effect while recorded state says it has not happened; a retry may repeat the side effect.

### Question 5

Why can an in-memory set fail in production?

**Answer:** It disappears during restart and is not automatically shared among workers.

### Question 6

What is job-level versus record-level idempotency?

**Answer:** Job-level concerns repeating the whole logical job; record-level concerns repeating individual logical records.

### Question 7

Why does partial failure make batch processing difficult?

**Answer:** The job can contain a mixture of completed, incomplete, and potentially partially applied work.

### Question 8

What is the difference between retry and rerun?

**Answer:** A retry is usually another attempt after failure or uncertainty; a rerun is executing the job again, often manually or through scheduling.

### Question 9

What must a stable identifier represent?

**Answer:** The logical operation or record whose repeated attempts should be recognized as the same work.

### Question 10

Why should you test the second execution?

**Answer:** The first execution proves the normal path; the second reveals duplicate behavior and rerun safety.

---

## 54. Important Distinctions

### Retry vs Rerun

```text
Retry
= another attempt at the operation

Rerun
= execute the job again
```

Both can expose duplicate-side-effect bugs.

### Determinism vs Repeatability

```text
Determinism
= same relevant inputs produce same computation result

Repeatability
= rerunning behaves predictably
```

### Repeatability vs Idempotency

```text
Repeatability
= repeated execution is predictable

Idempotency
= repeated logical application leaves the same externally relevant final state
```

### Job-Level vs Record-Level Idempotency

```text
Job-level
= the logical batch can be repeated safely

Record-level
= individual logical records/operations can be repeated safely
```

### Checkpoint vs Completion

These are different:

```text
"read through record 100"
```

versus:

```text
"records 1–100 were successfully written"
```

The second is a stronger statement.

### Stable ID vs Random Attempt ID

```text
stable logical ID
= same logical operation → same ID

random attempt ID
= every execution can look new
```

Stable identity is what duplicate recognition depends on.

---

## 55. Production Principles

### Principle 1 — Assume jobs can fail.

Define recovery before failure happens.

### Principle 2 — Assume jobs can be retried.

Do not build correctness on exactly-once invocation.

### Principle 3 — Assume jobs can be rerun manually.

Operators need safe recovery paths.

### Principle 4 — Give logical operations stable identities.

Identity makes duplicate recognition possible.

### Principle 5 — Make transformations deterministic where practical.

Control or record relevant randomness, time, configuration, and ordering.

### Principle 6 — Design side effects deliberately.

Choose whether repetition should:

```text
skip
reuse
replace
update
append
```

### Principle 7 — Track meaningful completion state.

State should correspond to a concrete guarantee.

### Principle 8 — Design for partial failure.

Long jobs should have an explicit recovery strategy.

### Principle 9 — Test the second run.

A job is not sufficiently tested if only the first execution has coverage.

### Principle 10 — A retry is safe only when the operation tolerates repetition.

Adding a retry loop to a non-idempotent operation does not make it idempotent.

---

## 56. Final Mental Model

Keep this model:

```text
                INPUT
                  ↓
               VALIDATE
                  ↓
          STABLE OPERATION ID
                  ↓
         CHECK EXISTING STATE
              ↙         ↘
          EXISTS        NEW
             ↓            ↓
          RETURN       PROCESS
                           ↓
                      WRITE RESULT
                           ↓
                   RECORD COMPLETION
```

Failure:

```text
PROCESS
   ↓
 CRASH
   ↓
RESTART
   ↓
SAME OPERATION ID
   ↓
CHECK STATE
   ↓
SAFE RECOVERY
```

A useful summary:

```text
Good repeatable job
=
predictable input
+
stable identity
+
deterministic processing
+
safe side effects
+
meaningful state
+
failure-aware design
+
retry-safe behavior
```

Term-by-term:

```text
Determinism
= Will the computation produce the same logical result?

Repeatability
= Can I run the job again and reason about the outcome?

Idempotency
= Will repeating the same logical operation avoid an additional unwanted external effect?

Stable identity
= How do I recognize the same logical work?

Checkpoint
= What completed by a precisely defined boundary?

Job state
= What lifecycle state is the job in?
```

Not every production system can make every layer perfectly “exactly once.” The practical goal is to define the failure model and make the **required externally visible behavior safe and predictable within that model**.

---

## 57. Completion Checklist

### Fundamentals

- [ ] I understand what a job is.
- [ ] I understand why jobs fail.
- [ ] I understand why jobs are retried.
- [ ] I understand why reruns can create duplicates.
- [ ] I understand side effects.
- [ ] I can distinguish retry from rerun.

### Core Concepts

- [ ] I understand repeatability.
- [ ] I understand determinism.
- [ ] I understand idempotency.
- [ ] I can distinguish determinism from idempotency.
- [ ] I can distinguish repeatability from idempotency.
- [ ] I understand job-level idempotency.
- [ ] I understand record-level idempotency.
- [ ] I understand stable identifiers.
- [ ] I understand idempotency keys.

### Design

- [ ] I can create a stable operation ID.
- [ ] I understand check-before-process.
- [ ] I understand its crash-window limitation.
- [ ] I understand job state.
- [ ] I understand state transitions.
- [ ] I understand checkpoints.
- [ ] I understand partial failure.
- [ ] I can reason about overwrite versus append.
- [ ] I can design safer reruns.
- [ ] I understand the limitations of in-memory state.
- [ ] I can recognize concurrency duplicate risks.

### Python

- [ ] I can use sets for local processed-state tracking.
- [ ] I can use dictionaries for ID-based result lookup.
- [ ] I can build deterministic transformations.
- [ ] I can use `pathlib`.
- [ ] I can represent job state with `Enum`.
- [ ] I can log safe job and record identity.
- [ ] I can inject failures for testing.

### Testing

- [ ] I test the first run.
- [ ] I test the second run.
- [ ] I test partial failure.
- [ ] I test retry behavior.
- [ ] I inspect externally relevant state.
- [ ] I verify that duplicate output is not created.

### Production

- [ ] I understand duplicate side effects.
- [ ] I understand unknown outcomes.
- [ ] I understand crash windows.
- [ ] I understand why check-before-process is not sufficient by itself.
- [ ] I can design job-level and record-level identity.
- [ ] I can design a repeatable batch job.
- [ ] I can debug duplicate processing.
- [ ] I can state what my implementation actually guarantees.
- [ ] I avoid claiming “exactly once” without evidence.

### Applied AI

- [ ] I can design a resumable LLM batch job.
- [ ] I understand duplicate inference risk.
- [ ] I understand stable identities for embeddings.
- [ ] I understand stable identities for evaluation results.
- [ ] I can reason about repeated AI computation.
- [ ] I understand how configuration/model versions affect result identity.

### Explanation

- [ ] I can explain idempotency to a beginner.
- [ ] I can explain the crash-window problem.
- [ ] I can explain why stable IDs matter.
- [ ] I can explain record-level recovery.
- [ ] I can explain why deterministic code is not automatically an idempotent job.

---

## 58. Final Self-Review

### Concept Coverage

This chapter teaches:

- jobs;
- failure;
- retries;
- reruns;
- repeatability;
- determinism;
- idempotency;
- side effects;
- stable identifiers;
- idempotency keys;
- check-before-process;
- crash windows;
- job state;
- partial failure;
- checkpoints;
- overwrite versus append;
- batch processing;
- job-level idempotency;
- record-level idempotency;
- retry-safe design;
- concurrency risks;
- file-based processing;
- CSV/data processing;
- Applied AI workloads;
- testing;
- debugging;
- production design.

### Practical Coverage

Included:

- beginner examples;
- intermediate examples;
- advanced examples;
- bad versus better implementations;
- failure scenarios;
- exercises with solutions;
- complete production-style example;
- mini-project;
- interview questions;
- architecture questions;
- debugging scenarios;
- knowledge checks;
- completion checklist.

### Python API Coverage

Relevant introduced APIs are explained in context:

```text
open()
Path.exists()
Path.is_file()
Path.read_text()
Path.write_text()
set.add()
set membership
dict.get()
Enum
random.random()
random.randint()
logging.getLogger()
logger.info()
logger.warning()
logger.error()
logger.exception()
pytest.raises()
subprocess.run()
returncode
stdout
stderr
```

### Production Quality

The learner is expected to understand:

```text
why retries are dangerous
why reruns are normal
how duplicate side effects happen
why stable identity matters
why partial failure matters
why check-before-process is incomplete
how to test the second execution
how to reason about recovery
how concurrency changes the problem
```

### Beginner Accessibility

The chapter:

- starts from failure scenarios;
- explains terminology before relying on jargon;
- progresses from simple local Python examples to production reasoning;
- calls out teaching simplifications;
- avoids pretending that an in-memory demonstration is a durable distributed solution.

---

## 59. Final File-Scope Verification

The only intended target is:

```text
10-Production-Habits-for-Python-Programs/04-idempotency-and-repeatable-jobs.md
```

No companion exercise file, solution file, Python file, configuration file, or folder is required for this lesson.

The target artifact is intentionally self-contained.

> **Final scope statement:** only the requested Markdown lesson is intended to be delivered for this task.
