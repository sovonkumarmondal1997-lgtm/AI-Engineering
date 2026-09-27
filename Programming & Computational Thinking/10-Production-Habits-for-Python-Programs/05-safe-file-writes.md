# Safe File Writes in Python

> **Stage 1 — Programming & Computational Thinking → Module 10 — Production Habits for Python Programs → 05 — Safe File Writes**

A normal file write can be correct when everything goes well and still be unsafe when the program crashes at the wrong moment.

This chapter teaches safe file-update thinking: how Python writes files, what can go wrong during a write, and how to stage a complete candidate before publishing it as the official destination.

> **Central engineering question:** What happens if the program crashes while writing this file?

> **Second question:** How can we preserve the previous known-good file until the new version is ready?
## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain `open()`, file modes, `write()`, and `writelines()`;
- use explicit UTF-8 encoding and appropriate newline handling;
- explain why `with open(...)` helps with resource cleanup;
- explain truncation, append semantics, and partial writes;
- explain temporary-file staging and atomic replacement;
- use `os.replace()` correctly for a same-filesystem replacement pattern;
- distinguish buffering, `flush()`, `fsync()`, atomicity, and durability;
- safely update text, JSON, CSV, configuration, metadata, and state files;
- handle `OSError`-family failures without swallowing bugs;
- clean up temporary artifacts;
- connect safe writes to idempotent and repeatable jobs;
- test both normal and failure behavior;
- debug file-write failures systematically;
- explain exactly what a safe-write helper guarantees and what it does not.
## 2. Why Safe File Writes Matter

Imagine a program updating a configuration file with 100 valid lines. It opens the file with `"w"` and starts writing the new version. Halfway through, the process crashes.

Conceptually:

```text
OLD VALID FILE
      ↓
open(..., "w")
      ↓
existing contents truncated
      ↓
write new contents
      ↓
CRASH
      ↓
destination may contain incomplete new state
```

The old version was destroyed before the new version was ready.

A safer publication model is:

```text
prepare new content
      ↓
write candidate to temporary file
      ↓
candidate complete
      ↓
replace destination
```

If candidate generation or candidate writing fails, the destination can remain at its previous known-good state.

This matters for:

- configuration;
- checkpoints;
- job state;
- manifests;
- model metadata;
- evaluation results;
- inference results;
- generated reports;
- local indexes.

The goal is not to make every file "indestructible." The goal is to make important file updates behave predictably under failure.
## 3. How Python Writes Files

Start with:

```python
with open("example.txt", "w", encoding="utf-8") as file:
    file.write("Hello\n")
```

Break it down:

```text
open()
  ↓
path + mode + encoding
  ↓
file object
  ↓
write()
  ↓
with block ends
  ↓
close/cleanup
```

A useful conceptual I/O path is:

```text
Python string
   ↓
text I/O
   ↓
encoding to bytes
   ↓
buffering
   ↓
OS/filesystem
   ↓
storage
```

This is a conceptual model rather than a promise about every internal implementation.

### Predict before running

```python
from pathlib import Path

path = Path("example.txt")

with path.open("w", encoding="utf-8") as file:
    file.write("first\n")
    file.write("second\n")
```

Final logical content:

```text
first
second
```

Stage 1 habit:

> Predict the file state before executing the program.
## 4. Opening Files for Writing

The relevant `open()` parameters are:

```python
open(
    file,
    mode="r",
    buffering=-1,
    encoding=None,
    errors=None,
    newline=None,
    closefd=True,
    opener=None,
)
```

For this lesson, focus on:

| Parameter | Why it matters |
|---|---|
| `file` | target path or descriptor |
| `mode` | write/append/create/update semantics |
| `buffering` | controls buffering policy |
| `encoding` | converts text to bytes |
| `errors` | controls encoding error behavior |
| `newline` | controls text newline handling |

Example:

```python
from pathlib import Path

path = Path("notes.txt")

with path.open("w", encoding="utf-8") as file:
    file.write("hello\n")
```

For binary files, use a binary mode and `bytes`:

```python
with open("payload.bin", "wb") as file:
    file.write(b"\x00\x01\x02")
```

Do not treat text and binary I/O as interchangeable.
## 5. File Modes

The most important modes for writing are:

| Mode | Meaning | Important behavior |
|---|---|---|
| `"w"` | write | creates or truncates |
| `"a"` | append | writes at the end |
| `"x"` | exclusive create | fails if the file exists |
| `"r+"` | read/write | no initial truncation |
| `"w+"` | read/write | creates or truncates |
| `"a+"` | read/append | creates if absent, appends writes |

Memorize first:

```text
w = replace/truncate
a = append
x = create new or fail
```

Example:

```python
from pathlib import Path

path = Path("marker.txt")

with path.open("x", encoding="utf-8") as file:
    file.write("created\n")
```

Running that code again raises `FileExistsError`.

Mode selection is only one part of correctness. It tells Python how to open the path; it does not define your entire failure-recovery protocol.
## 6. `write()` and `writelines()`

`write()` writes text and returns the number of characters accepted by the text I/O layer:

```python
with open("notes.txt", "w", encoding="utf-8") as file:
    count = file.write("hello\n")

print(count)
```

`write()` does not automatically add newlines:

```python
with open("notes.txt", "w", encoding="utf-8") as file:
    file.write("first")
    file.write("second")
```

Final content:

```text
firstsecond
```

`writelines()` accepts an iterable of strings:

```python
lines = ["first\n", "second\n"]

with open("notes.txt", "w", encoding="utf-8") as file:
    file.writelines(lines)
```

It also does not insert missing newline characters.

Use these APIs for content generation, then separately think about how the destination should be published.
## 7. Encoding and Newlines

For production text files, make the intended encoding explicit:

```python
from pathlib import Path

path = Path("message.txt")

path.write_text(
    "Hello — नमस्ते — こんにちは\n",
    encoding="utf-8",
)
```

Python strings are Unicode text; the file contains encoded bytes.

An encoding error can occur:

```python
text = "café"

with open("message.txt", "w", encoding="ascii") as file:
    file.write(text)
```

The lesson is:

> Choose the encoding deliberately.

For CSV, use the standard newline pattern:

```python
import csv

with open("people.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["name", "age"])
    writer.writerow(["Asha", 30])
```

`newline` controls text newline translation. Keep CSV handling deliberate because the `csv` module expects to manage row termination itself.
## 8. Context Managers and File Handles

Prefer:

```python
with open("data.txt", "w", encoding="utf-8") as file:
    file.write("important data\n")
```

The `with` statement manages the resource lifetime and closes the file when the block finishes, including normal exception paths.

Conceptually:

```text
open
 ↓
use
 ↓
leave block
 ↓
close
```

Manual cleanup is possible:

```python
file = open("data.txt", "w", encoding="utf-8")
try:
    file.write("hello\n")
finally:
    file.close()
```

For ordinary file handling, the context-manager form is clearer.

Critical distinction:

```text
with open(...)
= good resource management

with open(...)
≠ automatically atomic destination replacement

close()
≠ automatically durable persistence
```

Context managers solve lifecycle management. Safe replacement and durability require separate design.
## 9. What Can Go Wrong During a Write?

A write can fail because of:

- missing or invalid paths;
- insufficient permissions;
- destination is a directory;
- parent directory does not exist;
- encoding errors;
- storage-space problems;
- unrelated application exceptions;
- process termination;
- machine or environment restart;
- interruption during a long operation.

The important pattern is:

```text
old valid destination
      ↓
update begins
      ↓
failure
      ↓
destination may not contain intended new state
```

The exact final state depends on the platform, filesystem, buffering, timing, and failure mode.

Production code should avoid assuming that a direct write is automatically crash-safe.
## 10. Truncation and Data Loss

Opening an existing file with `"w"` truncates it before the new contents are fully written.

```python
with open("important.txt", "w", encoding="utf-8") as file:
    file.write("new version\n")
```

Dangerous sequence:

```text
OLD VALID FILE
      ↓
open(..., "w")
      ↓
truncate
      ↓
write new version
      ↓
failure
      ↓
old contents no longer provide the previous version
```

The exact damaged contents vary with the failure.

A safer design keeps the old destination untouched while constructing the candidate:

```text
destination = last known-good version

temporary file = candidate version

only publish candidate after it is complete
```

This is one of the most important production habits in this chapter.
## 11. Partial Writes and Data Corruption

Suppose the intended JSON is:

```json
{"status": "completed", "count": 1000}
```

A failed direct write might conceptually leave:

```text
{"status": "completed", "cou
```

That is incomplete.

A file can also be:

- incomplete;
- syntactically invalid;
- syntactically valid but semantically wrong;
- partially updated;
- replaced by incorrect data.

Do not call every wrong file "corruption" without qualification. Use precise terms.

Structured formats are especially sensitive:

```python
import json

with open("state.json", "r", encoding="utf-8") as file:
    state = json.load(file)
```

An incomplete JSON document may cause `json.JSONDecodeError`.

Safe writing protects the publication boundary. It does not prove that the generated business data is correct.
## 12. Append vs Replace

Append:

```python
with open("results.txt", "a", encoding="utf-8") as file:
    file.write("result for record 123\n")
```

can be correct for an append-only event log.

But a rerunnable output file can become:

```text
result for record 123
result for record 123
```

after a retry or rerun.

For a whole-file result, a safer model is:

```text
generate complete result
      ↓
stage result
      ↓
replace destination
```

Important distinction:

> `"a"` preserves old contents; that does not mean append is correct for your application's semantics.

Connect this with idempotency:

```text
safe file publication
+
idempotent logical processing
=
safer reruns
```
## 13. Exclusive Creation

Use `"x"` when an existing path should be treated as a failure:

```python
with open("first-run.marker", "x", encoding="utf-8") as file:
    file.write("created\n")
```

Second run:

```text
file already exists
   ↓
FileExistsError
```

Useful scenarios:

- create-once marker files;
- detect unexpected prior state;
- prevent accidental overwrite.

Do not use `"x"` as a general solution to safe replacement. It is specifically about exclusive creation, not publishing a complete candidate over an existing destination.
## 14. Temporary Files

A temporary file is a staging location for a candidate version.

The core pattern:

```text
write new content
      ↓
temporary file
      ↓
complete successfully
      ↓
replace destination
```

Why this is safer:

```text
destination
= last known-good version

temporary file
= unpublished candidate
```

Python's `tempfile` module provides:

```python
import tempfile

tempfile.NamedTemporaryFile
tempfile.TemporaryDirectory
tempfile.mkstemp
```

For atomic replacement, create the temporary file in the destination's directory whenever practical.

This avoids unnecessary cross-filesystem operations and makes the replacement boundary easier to reason about.
## 15. `NamedTemporaryFile`

`tempfile.NamedTemporaryFile()` creates a temporary file with a visible name.

```python
import tempfile

with tempfile.NamedTemporaryFile(
    mode="w",
    encoding="utf-8",
    delete=False,
    suffix=".tmp",
) as file:
    file.write("candidate\n")
    temporary_name = file.name

print(temporary_name)
```

A safe replacement helper often sets `delete=False` because it needs the temporary pathname after the file object is closed:

```text
create
→ write
→ close
→ os.replace(temp_name, destination)
```

### Platform caveat

Reopening or deleting an already-open named temporary file has platform-specific behavior. Windows has stricter sharing/deletion considerations than POSIX systems.

A simple portable strategy is:

1. create the temporary file in the target directory;
2. write it;
3. close it;
4. replace the destination;
5. clean up the temporary path if replacement did not happen.

Do not rely on a single temporary-file snippet without understanding its lifecycle.
## 16. `TemporaryDirectory`

`TemporaryDirectory()` is useful when a workflow needs an isolated temporary directory:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = Path(directory) / "candidate.txt"
    path.write_text("candidate\n", encoding="utf-8")
    print(path.read_text(encoding="utf-8"))
```

Its main teaching value here is lifecycle management.

For one file that must later be renamed into a destination, `NamedTemporaryFile()` or `mkstemp()` in the destination directory is generally more directly aligned with the safe-replacement protocol.
## 17. Temporary File Location and Same-Filesystem Replacement

For an atomic replacement design, prefer:

```text
/data/.results.json.tmp
        ↓
/data/results.json
```

over an unrelated temporary location such as:

```text
/tmp/results.json.tmp
        ↓
/data/results.json
```

The source and destination may be on different filesystems.

`os.replace()` can fail when source and destination are on different filesystems.

Practical rule:

> **Create the temporary candidate beside the final destination when you need same-filesystem replacement.**

This is a design constraint, not just a style preference.
## 18. Atomic Replacement

Atomic replacement is about what a reader observes at the destination.

Desired publication:

```text
OLD FILE
   ↓
candidate prepared elsewhere
   ↓
candidate complete
   ↓
replace destination
   ↓
NEW FILE
```

The goal is not to expose:

```text
half old + half new
```

at the destination.

Think:

```text
reader
  ↓
old version
  OR
new version
```

subject to the operating system/filesystem semantics of the replacement operation.

Atomicity does not mean:

- content is semantically correct;
- all concurrent updates are coordinated;
- data is guaranteed to survive every power failure.

It is one reliability property in a larger design.
## 19. `os.replace()`

Use:

```python
import os

os.replace(source, destination)
```

Example:

```python
from pathlib import Path
import os

source = Path(".state.json.tmp")
destination = Path("state.json")

os.replace(source, destination)
```

When successful, the destination path refers to the replacement.

Why it matters:

```text
write candidate completely
        ↓
os.replace()
        ↓
publish candidate
```

Important limitations:

- source and destination may need to be on the same filesystem;
- permissions can still cause failure;
- it does not establish every durability guarantee;
- it does not coordinate multiple writers;
- it does not verify business correctness.

Use `os.replace()` for the publication step—not as a substitute for a complete reliability design.
## 20. Atomicity vs Durability

### Atomicity

Question:

> **Can the reader observe a partially updated destination?**

A safe replacement pattern aims for:

```text
old OR new
```

rather than an intermediate destination.

### Durability

Question:

> **After a crash or power loss, how strongly must the completed update survive?**

These are different:

```text
atomicity ≠ durability
```

A replacement can be atomic while persistence after sudden power loss still needs separate consideration.

Different files justify different durability policies:

```text
cache
→ low durability requirement

job checkpoint
→ higher durability requirement
```

Never use "atomic" as shorthand for "survives every crash."
## 21. Buffering

A useful conceptual model is:

```text
Python code
   ↓
Python buffer
   ↓
OS
   ↓
filesystem
   ↓
storage
```

Python and lower layers can buffer data.

Therefore:

```python
file.write(content)
```

means the data was accepted by the file object's write path. It does not automatically mean that a physical storage device has made the update durable.

Buffering exists for performance and I/O efficiency.

Production lesson:

```text
write()
= send data into the I/O path

flush()
= push Python-level buffered data onward

fsync()
= request synchronization through OS/filesystem semantics
```

Keep those concepts separate.
## 22. `flush()`

Use:

```python
file.flush()
```

Example:

```python
with open("progress.txt", "w", encoding="utf-8") as file:
    file.write("step 1 completed\n")
    file.flush()
```

`flush()` asks the buffered file object to push its buffered data onward.

It is useful when:

- a reader needs data sooner;
- you need Python buffering emptied before a later operation;
- you are preparing for a synchronization step.

But:

```text
flush()
≠
stable-storage durability
```

For a stronger durability request:

```python
file.flush()
os.fsync(file.fileno())
```

may be appropriate, depending on requirements and platform semantics.
## 23. `os.fsync()` and Durability

Use:

```python
import os

os.fsync(file.fileno())
```

`file.fileno()` exposes the underlying file descriptor when supported.

Conceptually:

```text
Python file object
      ↓
file descriptor
      ↓
OS-level synchronization
```

Example:

```python
with open("critical-state.txt", "w", encoding="utf-8") as file:
    file.write("important state\n")
    file.flush()
    os.fsync(file.fileno())
```

Why not always call it?

- synchronization can have performance cost;
- not every file requires strong persistence;
- exact durability guarantees are platform/filesystem/storage dependent.

`fsync()` is a tool for an explicit durability requirement, not a magic "no data can ever be lost" switch.
## 24. `flush()` vs `fsync()`

| Operation | Main purpose |
|---|---|
| `flush()` | push Python-level buffering onward |
| `os.fsync()` | request synchronization through OS/filesystem semantics |

Correct conceptual sequence:

```text
file.write()
    ↓
file.flush()
    ↓
os.fsync(file.fileno())   # when required
```

Incorrect shortcut:

```text
flush() = durable
```

Better:

```text
flush() = buffering boundary

fsync() = synchronization request

durability = system-level guarantee that must be defined and tested for the environment
```
## 25. Safe Write Pattern

The fundamental pattern is:

```text
1. Prepare new content
2. Create temporary file beside destination
3. Write complete content
4. Flush if appropriate
5. fsync if durability requirements justify it
6. Close temporary file
7. Atomically replace destination
8. Clean up temporary path if replacement did not occur
```

The most important invariant is:

> **The official destination is not the construction area for an incomplete candidate.**

This turns:

```text
destination = work area
```

into:

```text
destination = published state
temporary = work area
```
## 26. Complete Safe Text Write Function

```python
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def safe_write_text(
    path: Path,
    content: str,
    *,
    durable: bool = False,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

            temp_file.write(content)
            temp_file.flush()

            if durable:
                os.fsync(temp_file.fileno())

        os.replace(temp_path, path)
        temp_path = None

    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass
```

### Line-by-line reasoning

`Path(path)` normalizes the input to a `Path`.

`path.parent.mkdir(...)` ensures the parent exists in this teaching helper. A production application may intentionally choose to fail when the directory is missing instead.

`temp_path` records ownership of the temporary artifact.

`NamedTemporaryFile(..., dir=path.parent)` creates the candidate beside the destination.

`delete=False` keeps the candidate pathname available after closing.

`write()` creates the candidate content.

`flush()` pushes Python buffering onward.

`fsync()` is optional because durability is a requirement decision.

`os.replace()` publishes only the completed candidate.

Setting `temp_path = None` means replacement has consumed the candidate path.

The `finally` block cleans up a candidate that was not successfully published.

### Guarantees

For the modeled failure path, the destination is not truncated while the candidate is being constructed.

### Non-guarantees

This helper is not:

- a multi-writer transaction;
- a universal power-loss guarantee;
- a backup system;
- a content validator;
- a distributed consistency protocol.
## 27. Safe JSON Writes

A direct JSON update is easy:

```python
import json
from pathlib import Path

state = {"status": "completed", "count": 1000}

with Path("state.json").open("w", encoding="utf-8") as file:
    json.dump(state, file)
```

The dangerous sequence is:

```text
valid state.json
    ↓
open(..., "w")
    ↓
truncate
    ↓
json.dump
    ↓
failure
    ↓
incomplete JSON possible
```

### Safer approach

Serialize before publication:

```python
import json

content = json.dumps(
    state,
    ensure_ascii=False,
    indent=2,
    sort_keys=True,
) + "\n"
```

Then:

```python
safe_write_text(Path("state.json"), content)
```

Serialization failure therefore happens before the destination is changed.

### Useful parameters

`ensure_ascii=False` keeps Unicode characters readable.

`indent=2` makes a small state file easier to inspect.

`sort_keys=True` provides stable key ordering, which can improve reproducibility and diffs.

Remember:

```text
stable JSON bytes
≠
atomic file update
```
## 28. JSON Loading and Validation Before Replacement

Safe writes should be paired with validation.

```python
import json
from pathlib import Path

path = Path("state.json")

with path.open("r", encoding="utf-8") as file:
    state = json.load(file)

if not isinstance(state, dict):
    raise ValueError("state must be a JSON object")

if state.get("status") not in {"pending", "running", "completed", "failed"}:
    raise ValueError("invalid status")
```

The workflow becomes:

```text
read
 ↓
parse
 ↓
validate
 ↓
modify in memory
 ↓
serialize
 ↓
safe write
```

This protects against publishing obviously invalid state.

It does not protect against logically incorrect values that satisfy your incomplete validation rules.
## 29. Safe CSV Writes

Use the standard library:

```python
import csv
```

Relevant APIs:

```python
csv.writer
csv.DictWriter
writerow
writerows
```

Example:

```python
import csv

rows = [
    {"id": "1", "amount": "10.50"},
    {"id": "2", "amount": "20.00"},
]

with open("results.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["id", "amount"],
    )
    writer.writeheader()
    writer.writerows(rows)
```

For important output, stage it:

```text
generate rows
   ↓
temporary CSV
   ↓
all rows written
   ↓
replace results.csv
```

A reusable pattern:

```python
from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path


def safe_write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, object]],
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )
            writer.writeheader()
            writer.writerows(rows)
            file.flush()

        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
```

The final CSV is published only after all rows have been produced.
## 30. Safe Configuration and State File Updates

Configuration and state files are examples where a half-written document can break the next program invocation.

Example configuration:

```json
{
  "log_level": "INFO",
  "timeout": 30
}
```

A safe update is:

```text
load existing configuration
      ↓
validate
      ↓
modify in memory
      ↓
serialize complete representation
      ↓
temporary file
      ↓
replace original
```

State files are similar:

```text
job-state.json
checkpoint.json
metadata.json
manifest.json
```

A damaged state file can prevent recovery logic from determining:

```text
what has run?
what completed?
what is pending?
```

This is why state files deserve careful publication semantics.
## 31. File Permissions and Security

Write failures can include:

- `PermissionError`;
- `FileNotFoundError`;
- `IsADirectoryError`;
- `NotADirectoryError`;
- other `OSError` instances.

Example:

```python
from pathlib import Path

try:
    Path("/protected/output.txt").write_text(
        "hello\n",
        encoding="utf-8",
    )
except PermissionError as exc:
    print(f"write permission denied: {exc}")
except OSError as exc:
    print(f"file operation failed: {exc}")
```

### `os.access()`

A pre-check can be useful:

```python
import os

if os.access("output.txt", os.W_OK):
    print("appears writable")
```

But it is not a guarantee.

```text
check
 ↓
environment changes
 ↓
write
 ↓
failure
```

Production rule:

> Perform the real operation and handle the real exception.

Also avoid exposing sensitive path or file contents in logs unless necessary.
## 32. Path Validation

Relevant `pathlib` APIs:

```python
from pathlib import Path

path = Path("data/results.json")

path.exists()
path.is_file()
path.is_dir()
path.parent
path.name
```

Example:

```python
from pathlib import Path

path = Path("data/results.json")

if not path.parent.is_dir():
    raise FileNotFoundError(
        f"parent directory does not exist: {path.parent}"
    )
```

Use these checks for diagnostics and explicit business rules.

Do not assume they eliminate races.

This can be unsafe:

```python
if not path.exists():
    path.write_text("created\n", encoding="utf-8")
```

Another process can create the file between the check and the write.

Use `"x"` when exclusive creation is the actual requirement.
## 33. Write Exceptions

Typical file-write failures:

| Exception | Example situation |
|---|---|
| `FileNotFoundError` | parent path missing |
| `PermissionError` | operation denied |
| `IsADirectoryError` | destination is a directory |
| `NotADirectoryError` | path component is not a directory |
| `UnicodeEncodeError` | text cannot be encoded |
| `OSError` | broader OS-level failure |

Example:

```python
from pathlib import Path

def write_report(path: Path, report: str) -> None:
    try:
        path.write_text(report, encoding="utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("report contains unsupported text") from exc
    except OSError:
        raise
```

The point of translating an exception is not to hide its cause. It is to give the caller a meaningful application-level abstraction.

Do not turn every exception into:

```python
try:
    write_output()
except Exception:
    pass
```

That loses information.
## 34. Failure Cleanup

Track temporary-file ownership explicitly:

```python
temp_path = None

try:
    temp_path = create_candidate()
    write_candidate(temp_path)
    publish(temp_path, destination)
    temp_path = None
finally:
    if temp_path is not None:
        cleanup(temp_path)
```

The invariant is:

```text
temp_path != None
→ candidate still belongs to cleanup

temp_path == None
→ candidate was successfully published or otherwise consumed
```

Use:

```python
path.unlink(missing_ok=True)
```

when a best-effort cleanup is appropriate and supported by your Python version.

Do not accidentally make cleanup remove the actual destination:

```text
temp_path
≠
destination
```

Name variables clearly and keep the two paths separate.
## 35. Complete Failure Flow

Success:

```text
create temp
   ↓
write complete candidate
   ↓
flush / sync as required
   ↓
close candidate
   ↓
replace destination
```

Failure before replacement:

```text
create temp
   ↓
write fails
   ↓
destination is still old version
   ↓
cleanup temp
   ↓
report failure
```

Replacement failure:

```text
candidate ready
   ↓
os.replace fails
   ↓
destination may still be old version
   ↓
cleanup candidate if possible
   ↓
report failure
```

The exact post-failure state should be verified by tests for your target environment.

Core invariant for a whole-file update:

> **Do not publish an incomplete candidate.**
## 36. Safe Writes in Batch Jobs

Consider:

```text
input.csv
    ↓
process 1,000 records
    ↓
results.csv
```

Unsafe direct write:

```text
write results.csv directly
    ↓
700 records written
    ↓
crash
    ↓
partial result
```

Safer whole-batch approach:

```text
process complete batch
    ↓
results.tmp
    ↓
write every row
    ↓
optional sync
    ↓
replace results.csv
```

If the process fails before replacement, the previous destination can remain valid.

For very large jobs, staging an entire batch may consume too much temporary storage. You can then combine:

```text
record-level idempotency
+
partitioned output
+
checkpoints
+
safe replacement
```

The correct strategy depends on workload size and recovery requirements.
## 37. Safe Writes in Applied AI Systems

Important AI artifacts can be ordinary files:

```text
model-metadata.json
evaluation-results.json
embedding-manifest.json
inference-results.json
agent-state.json
```

### Evaluation results

If an evaluation run crashes while writing thousands of records, a partial final file can make downstream analysis unreliable.

### Embedding manifests

A manifest may contain:

```text
document_id
chunk_count
embedding_version
status
```

If it is damaged, the next ingestion run may make the wrong recovery decision.

### Batch inference

A batch result should ideally move through:

```text
generate result
   ↓
validate result
   ↓
stage output
   ↓
publish
```

### Agent state

An agent workflow may persist:

```text
last_completed_step
checkpoint_id
tool-output reference
status
```

Safe state publication can reduce failures during recovery.

The reliability principle is general:

> AI artifacts are data, and data files still need ordinary failure-aware engineering.
## 38. Safe Writes and Idempotency

Safe writes and idempotency solve different problems.

```text
safe write
= protect file-update integrity

idempotency
= protect against repeated logical operations
```

Example:

```text
job reruns
   ↓
same result generated
   ↓
same output path
   ↓
safe replacement
```

The safe replacement prevents partial destination updates.

The idempotency design determines whether the rerun itself represents the same logical operation.

A robust pattern is:

```text
stable operation identity
      ↓
determine work
      ↓
generate complete output
      ↓
safe candidate write
      ↓
publish
```

Safe writes are therefore a reliability building block inside larger repeatable-job designs.
## 39. Logging for Safe Writes

Useful logs can describe the update phases:

```text
state update started
temporary file created
candidate written
candidate synchronized
destination replaced
temporary cleanup complete
state update failed
```

Example:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("starting state update path=%s", path)

try:
    safe_write_text(path, content)
except OSError:
    logger.exception("state update failed path=%s", path)
    raise

logger.info("state update completed path=%s", path)
```

Do not log sensitive file content.

Also do not log:

```text
"replacement completed"
```

before the actual `os.replace()` call succeeds.

Logging is evidence:

```text
error handling → decides behavior
logging → records evidence
safe write → protects update boundary
```
## 40. Validation Before Publication

Safe writes should be paired with explicit validation:

```python
def validate_state(state: dict) -> None:
    if not isinstance(state, dict):
        raise TypeError("state must be a dictionary")

    if state.get("status") not in {
        "pending",
        "running",
        "completed",
        "failed",
    }:
        raise ValueError("state.status is invalid")

    count = state.get("processed_records")

    if not isinstance(count, int):
        raise TypeError("processed_records must be an integer")

    if count < 0:
        raise ValueError("processed_records must be non-negative")
```

Then:

```text
validate
   ↓
serialize
   ↓
safe write
```

The ordering prevents obviously invalid state from being published.

This connects the previous production habit:

```text
03 — validation, errors, and exit codes
```

with this one:

```text
05 — safe file writes
```

You validate the candidate before you publish it.
## 41. Complete Safe JSON State Writer

```python
from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_state(state: dict) -> None:
    if not isinstance(state, dict):
        raise TypeError("state must be a dictionary")

    job_id = state.get("job_id")
    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("job_id must be a non-empty string")

    if state.get("status") not in {
        "pending",
        "running",
        "completed",
        "failed",
    }:
        raise ValueError("invalid status")

    count = state.get("processed_records")
    if not isinstance(count, int):
        raise TypeError("processed_records must be an integer")

    if count < 0:
        raise ValueError("processed_records must be non-negative")


def save_state(
    path: Path,
    state: dict,
    *,
    durable: bool = False,
) -> None:
    validate_state(state)

    content = json.dumps(
        state,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)

            file.write(content)
            file.flush()

            if durable:
                os.fsync(file.fileno())

        logger.info("publishing state path=%s", path)
        os.replace(temporary_path, path)
        temporary_path = None
        logger.info("state published path=%s", path)

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
```

### Problem being solved

Keep `path` at its old valid version until the complete JSON candidate has been generated and written.

### First run

```text
no destination
→ candidate written
→ replacement
→ state.json created
```

### Replacement run

```text
old destination
→ candidate written
→ replacement
→ old version replaced by complete new version
```

### Failure during candidate creation

```text
old destination
→ candidate write fails
→ old destination remains
→ candidate cleaned
```

### Remaining limitations

This does not solve:

- multiple simultaneous writers;
- all possible power-loss durability guarantees;
- multi-file transactions;
- semantic bugs in state generation.

That boundary must be documented in production code.
## 42. Common Anti-Patterns

### Anti-pattern 1 — Directly opening important files with `"w"`

**Problem:** old contents are truncated first.

**Why dangerous:** a later failure can leave incomplete state.

**Bad example:**

```python
with open("state.json", "w", encoding="utf-8") as file:
    file.write(content)
```

**Better approach:** stage the candidate and replace only after success.

**Production lesson:** do not construct an important new version in the official destination.

---

### Anti-pattern 2 — Assuming `close()` guarantees durability

**Problem:** treating cleanup as persistence.

**Why dangerous:** closing a file does not establish every stable-storage guarantee.

**Better approach:** define whether stronger synchronization is required.

**Production lesson:** cleanup and durability are separate concerns.

---

### Anti-pattern 3 — Using append for rerunnable output

**Problem:** repeated executions accumulate duplicate logical results.

**Bad example:**

```python
with open("results.txt", "a", encoding="utf-8") as file:
    file.write(result)
```

**Better approach:** whole-file replacement or record-keyed output.

**Production lesson:** preserve semantics, not just bytes.

---

### Anti-pattern 4 — Writing JSON directly to the final destination

**Problem:** serialization/write failure can leave incomplete JSON.

**Better approach:** serialize completely, stage, then replace.

**Production lesson:** publish only complete candidates.

---

### Anti-pattern 5 — Ignoring encoding

**Problem:** behavior depends on environment defaults.

**Better approach:** specify UTF-8 when appropriate.

**Production lesson:** file contracts should be explicit.

---

### Anti-pattern 6 — Ignoring exceptions

**Problem:** output can fail silently.

**Bad example:**

```python
try:
    write_output()
except OSError:
    pass
```

**Better approach:** recover intentionally or propagate the error.

**Production lesson:** a failed persistent state transition is important evidence.

---

### Anti-pattern 7 — Delete original, then write new

**Problem:** creates a window with no valid destination.

**Better approach:** keep old file, prepare new file elsewhere, replace.

**Production lesson:** preserve last known-good state.

---

### Anti-pattern 8 — Temporary file on another filesystem

**Problem:** `os.replace()` may fail across filesystems.

**Better approach:** stage beside destination.

**Production lesson:** temp-file location matters.

---

### Anti-pattern 9 — `flush()` treated as durability

**Problem:** Python buffering and storage persistence are conflated.

**Better approach:** use `fsync()` when required.

**Production lesson:** know the layer each API addresses.

---

### Anti-pattern 10 — `fsync()` used everywhere without a requirement

**Problem:** unnecessary performance cost.

**Better approach:** define durability requirements first.

**Production lesson:** reliability controls are trade-offs.

---

### Anti-pattern 11 — Permission check treated as guarantee

**Problem:** the environment can change between check and operation.

**Better approach:** perform the real write and handle its exception.

**Production lesson:** pre-checks do not replace correct error handling.

---

### Anti-pattern 12 — Temporary files never cleaned

**Problem:** stale artifacts accumulate.

**Better approach:** clean candidates in `finally` and define recovery policy for abnormal termination.

**Production lesson:** temporary files have lifecycle ownership.

---

### Anti-pattern 13 — Repeating safe-write code everywhere

**Problem:** duplicated reliability logic becomes inconsistent.

**Better approach:** central reusable helper.

**Production lesson:** correctness patterns should be standardized.

---

### Anti-pattern 14 — Atomicity and durability treated as synonyms

**Problem:** false confidence about crash survival.

**Better approach:** document both independently.

**Production lesson:** never promise a guarantee you have not established.
## 43. Testing Safe File Writes

A production-oriented file writer needs tests for both success and failure.

At minimum test:

- successful creation;
- replacement of an existing file;
- missing parent directory;
- write/serialization failure;
- temporary-file cleanup;
- preservation of the old file after failure;
- final content completeness;
- JSON parsing after the write;
- CSV row completeness.

Use `pytest` and its `tmp_path` fixture.

```python
def test_safe_write_creates_file(tmp_path):
    path = tmp_path / "result.txt"

    safe_write_text(path, "hello\n")

    assert path.read_text(encoding="utf-8") == "hello\n"
```

### Why `tmp_path`?

It gives the test an isolated temporary directory so the test does not overwrite project files.

Test replacement:

```python
def test_safe_write_replaces_existing_file(tmp_path):
    path = tmp_path / "result.txt"
    path.write_text("OLD\n", encoding="utf-8")

    safe_write_text(path, "NEW\n")

    assert path.read_text(encoding="utf-8") == "NEW\n"
```

The most valuable tests validate observable invariants.
## 44. Testing Failure Before Replacement

The most important application-level failure test is:

```text
old valid file
      ↓
candidate write fails
      ↓
old valid file remains
```

A controlled test double can simulate the failure:

```python
from pathlib import Path

def write_candidate_then_fail(path: Path, content: str) -> None:
    candidate = path.parent / f".{path.name}.tmp"

    try:
        candidate.write_text(content, encoding="utf-8")
        raise OSError("simulated failure before replacement")
    finally:
        candidate.unlink(missing_ok=True)
```

Test:

```python
import pytest

def test_old_file_survives_failure(tmp_path):
    path = tmp_path / "state.txt"
    path.write_text("OLD\n", encoding="utf-8")

    with pytest.raises(OSError, match="simulated"):
        write_candidate_then_fail(path, "NEW\n")

    assert path.read_text(encoding="utf-8") == "OLD\n"
```

This does not simulate physical power loss. It verifies a critical software-level invariant:

> **Failure before publication does not modify the destination.**
## 45. Testing Temporary-File Cleanup

After success, no candidate should remain:

```python
def test_temp_file_is_not_left_after_success(tmp_path):
    path = tmp_path / "state.json"

    safe_write_text(path, '{"ok": true}\n')

    leftovers = [
        item.name
        for item in tmp_path.iterdir()
        if item.name.startswith(".state.json.")
    ]

    assert leftovers == []
```

After controlled failure, the same invariant should hold.

When writing low-level failure tests, distinguish:

```text
ordinary Python exception
    ↓
finally cleanup can run

abrupt process termination
    ↓
Python cleanup may not run
```

Therefore a unit test proves ordinary application behavior. It is not a universal crash simulation.

For critical systems, higher-level integration/failure-injection testing may be required.
## 46. Testing Atomic Replacement Behavior

Test the two important state transitions:

```text
success
OLD → NEW

failure before replacement
OLD → OLD
```

Example:

```python
def test_success_publishes_new_version(tmp_path):
    path = tmp_path / "state.txt"
    path.write_text("OLD\n", encoding="utf-8")

    safe_write_text(path, "NEW\n")

    assert path.read_text(encoding="utf-8") == "NEW\n"
```

Failure test:

```python
def test_failure_before_publish_keeps_old_version(tmp_path):
    path = tmp_path / "state.txt"
    path.write_text("OLD\n", encoding="utf-8")

    try:
        write_candidate_then_fail(path, "NEW\n")
    except OSError:
        pass

    assert path.read_text(encoding="utf-8") == "OLD\n"
```

Test the **invariant**, not the specific temporary filename or internal implementation sequence.
## 47. Testing JSON and CSV Outputs

For JSON, parse the final file:

```python
import json

def test_safe_json_is_valid(tmp_path):
    path = tmp_path / "state.json"

    content = json.dumps(
        {"status": "completed", "count": 100},
        sort_keys=True,
    )

    safe_write_text(path, content + "\n")

    loaded = json.loads(path.read_text(encoding="utf-8"))

    assert loaded["status"] == "completed"
    assert loaded["count"] == 100
```

For CSV, read it through `csv.DictReader`:

```python
import csv

def test_safe_csv_contains_all_rows(tmp_path):
    path = tmp_path / "results.csv"

    safe_write_csv(
        path,
        ["id", "value"],
        [
            {"id": "1", "value": "A"},
            {"id": "2", "value": "B"},
        ],
    )

    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows == [
        {"id": "1", "value": "A"},
        {"id": "2", "value": "B"},
    ]
```

The test verifies that the final published file is complete and parseable.
## 48. Testing Atomicity vs Real Crash Testing

A normal test cannot perfectly reproduce:

```text
machine loses power
```

or every:

```text
filesystem failure
```

Use layers of testing:

```text
unit test
   ↓
failure injection
   ↓
integration test
   ↓
process termination testing
   ↓
environment-specific durability testing
```

### What unit tests can prove well

- the candidate is generated;
- the old file remains when candidate creation fails;
- the final file contains complete data;
- cleanup happens on expected exception paths.

### What unit tests do not prove

They cannot by themselves establish every OS/filesystem/storage guarantee after sudden power loss.

That is an important engineering boundary.
## 49. Debugging Safe File Writes

Use this workflow:

```text
1. Identify destination path
2. Inspect parent directory
3. Check whether destination is a file/directory
4. Check permissions and ownership
5. Check file mode
6. Check encoding
7. Read exception type/message
8. Determine whether truncation occurred
9. Determine whether a temp file was created
10. Determine whether replacement occurred
11. Inspect final content
12. Add regression coverage
```

### Common symptom: empty file

Check whether:

```python
open(path, "w")
```

happened before the failure.

### Common symptom: invalid JSON

Check whether JSON was written directly to the destination.

### Common symptom: temp files accumulate

Check `finally` cleanup and consider abnormal process termination.

### Common symptom: replacement fails

Check:

```text
path correctness
same filesystem
destination type
permissions
platform behavior
```

Use evidence from exceptions and logs before changing the implementation.
## 50. Complete Production Example — Safe JSON State File Writer

The example below combines:

```text
validation
+
complete serialization
+
temporary-file staging
+
UTF-8
+
flush
+
optional fsync
+
os.replace
+
cleanup
+
logging
```

```python
from __future__ import annotations

import json
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JobState:
    job_id: str
    status: str
    processed_records: int


ALLOWED_STATUS = {
    "pending",
    "running",
    "completed",
    "failed",
}


def validate_state(state: JobState) -> None:
    if not state.job_id.strip():
        raise ValueError("job_id must not be empty")

    if state.status not in ALLOWED_STATUS:
        raise ValueError("invalid status")

    if state.processed_records < 0:
        raise ValueError("processed_records must be non-negative")


def serialize_state(state: JobState) -> str:
    validate_state(state)

    return json.dumps(
        {
            "job_id": state.job_id,
            "status": state.status,
            "processed_records": state.processed_records,
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def save_state(
    path: Path,
    state: JobState,
    *,
    durable: bool = False,
) -> None:
    content = serialize_state(state)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            file.write(content)
            file.flush()

            if durable:
                os.fsync(file.fileno())

        logger.info("publishing state path=%s", path)
        os.replace(temporary_path, path)
        temporary_path = None
        logger.info("state published path=%s", path)

    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
```

### How the program flows

```text
JobState
   ↓
validate_state
   ↓
serialize_state
   ↓
temporary candidate
   ↓
write
   ↓
flush
   ↓
optional fsync
   ↓
close
   ↓
os.replace
```

### What happens if serialization fails?

The destination has not yet been changed.

### What happens if temporary-file writing fails?

The destination has not yet been replaced. Cleanup attempts to remove the candidate.

### What happens if replacement succeeds?

The destination points to the complete candidate.

### What happens if replacement fails?

The destination may remain the old version; the candidate is cleaned up when possible, and the caller gets the failure.

### What this example does not solve

- concurrent writers;
- multi-file transactions;
- all power-loss scenarios;
- semantic mistakes in the state;
- guaranteed recovery from an abruptly killed process at every possible instant.

The correct production lesson is not "this code is perfect." It is:

> **This code makes its failure boundary explicit and documents its guarantees.**
## 51. Production Example — Loading, Updating, and Publishing State

A complete state workflow can be:

```python
from __future__ import annotations

import json
from pathlib import Path


def load_state(path: Path) -> JobState:
    with path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    if not isinstance(raw, dict):
        raise ValueError("state JSON must contain an object")

    try:
        state = JobState(
            job_id=raw["job_id"],
            status=raw["status"],
            processed_records=raw["processed_records"],
        )
    except KeyError as exc:
        raise ValueError(f"missing state field: {exc.args[0]}") from exc

    validate_state(state)
    return state


def mark_completed(path: Path) -> None:
    current = load_state(path)

    updated = JobState(
        job_id=current.job_id,
        status="completed",
        processed_records=current.processed_records,
    )

    save_state(path, updated)
```

The overall state transition is:

```text
read published state
       ↓
parse
       ↓
validate
       ↓
create new state in memory
       ↓
serialize
       ↓
safe-write candidate
       ↓
publish new state
```

The program never edits one JSON field directly in the final file. It creates a complete next state and then publishes that state.
## 52. Mini Project — Crash-Safe JSON State File Manager

### Project Goal

Build a local manager for:

```text
application-state.json
```

Example:

```json
{
  "job_id": "job-001",
  "status": "completed",
  "processed_records": 1000
}
```

### Requirements

Your implementation must:

- load existing state;
- validate state;
- update state in memory;
- serialize a complete state;
- write a temporary file beside the destination;
- use UTF-8;
- use `os.replace()`;
- handle failures;
- clean up temporary files;
- log important operations;
- support optional durability;
- include tests;
- explain atomicity;
- explain durability;
- document limitations.

### Architecture

```text
caller / CLI
     ↓
State Manager
     ↓
validate
     ↓
serialize
     ↓
safe-write helper
     ├── temp file
     ├── write
     ├── flush
     ├── optional fsync
     ├── close
     └── os.replace
```

### Step-by-Step Tasks

#### Task 1 — Define the state model

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class JobState:
    job_id: str
    status: str
    processed_records: int
```

#### Task 2 — Validate

Require:

```text
job_id = non-empty string
status = allowed state
processed_records = non-negative integer
```

#### Task 3 — Load

Use `json.load()` and map the JSON into `JobState`.

#### Task 4 — Modify

Create a new `JobState` rather than mutating the persisted JSON text.

#### Task 5 — Serialize

Use stable JSON:

```python
json.dumps(
    state,
    ensure_ascii=False,
    indent=2,
    sort_keys=True,
)
```

#### Task 6 — Stage

Create the temporary file in the destination directory.

#### Task 7 — Publish

Call:

```python
os.replace(temp_path, destination)
```

#### Task 8 — Test failure before publish

Prove that the old destination remains unchanged.

#### Task 9 — Test cleanup

Prove that expected temporary artifacts are removed.

#### Task 10 — Add durability mode

Make `fsync()` optional and document the reason.

### Expected Behavior

Success:

```text
old state → new complete state
```

Candidate failure:

```text
old state → old state
```

Replacement failure:

```text
old state remains when replacement did not occur
candidate cleaned when possible
```

### Reference Solution

```python
from __future__ import annotations

import json
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JobState:
    job_id: str
    status: str
    processed_records: int


ALLOWED_STATUS = {
    "pending",
    "running",
    "completed",
    "failed",
}


def validate_state(state: JobState) -> None:
    if not isinstance(state.job_id, str) or not state.job_id.strip():
        raise ValueError("job_id must be a non-empty string")

    if state.status not in ALLOWED_STATUS:
        raise ValueError("invalid status")

    if not isinstance(state.processed_records, int):
        raise TypeError("processed_records must be an integer")

    if state.processed_records < 0:
        raise ValueError("processed_records must be non-negative")


def serialize_state(state: JobState) -> str:
    validate_state(state)

    payload = {
        "job_id": state.job_id,
        "status": state.status,
        "processed_records": state.processed_records,
    }

    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def save_state(
    path: Path,
    state: JobState,
    *,
    durable: bool = False,
) -> None:
    content = serialize_state(state)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            file.write(content)
            file.flush()

            if durable:
                os.fsync(file.fileno())

        os.replace(temporary_path, path)
        temporary_path = None

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
```

### Testing Strategy

Test creation:

```python
def test_save_state_creates_valid_json(tmp_path):
    import json

    path = tmp_path / "application-state.json"

    state = JobState(
        job_id="job-001",
        status="completed",
        processed_records=1000,
    )

    save_state(path, state)

    loaded = json.loads(path.read_text(encoding="utf-8"))

    assert loaded == {
        "job_id": "job-001",
        "status": "completed",
        "processed_records": 1000,
    }
```

Test validation:

```python
import pytest


def test_negative_count_is_rejected(tmp_path):
    path = tmp_path / "application-state.json"

    bad_state = JobState(
        job_id="job-001",
        status="completed",
        processed_records=-1,
    )

    with pytest.raises(
        ValueError,
        match="non-negative",
    ):
        save_state(path, bad_state)
```

Test old-file preservation before publication using failure injection.

### Production Improvements

Possible future improvements:

- schema versioning;
- concurrent-writer coordination;
- stale-temp recovery;
- stronger durability protocol;
- backups;
- integrity checks;
- atomic multi-file publication;
- operational metrics.

Only add these when required by the actual workload.
## 53. Coding Example Requirements

Every major concept must have a Python example where code improves understanding.

Examples should be:

- syntactically valid;
- runnable with the stated Python version/assumptions;
- progressive from simple to advanced;
- explained rather than dumped;
- realistic enough to expose production trade-offs.

For important examples, explicitly answer:

```text
What problem are we solving?
Why is the naive approach unsafe?
What happens if the program succeeds?
What happens if it fails halfway?
What happens to the old file?
Why is the safer design better?
What guarantees does it provide?
What does it NOT guarantee?
```

### Example progression

```text
write one string
    ↓
compare file modes
    ↓
use pathlib
    ↓
temporary file
    ↓
os.replace()
    ↓
flush()
    ↓
optional fsync()
    ↓
safe text helper
    ↓
safe JSON/CSV
    ↓
state-file manager
    ↓
tests and failure injection
```

This progression is deliberate. Learn the invariant first and optimize the implementation later.
## 54. Function/API Coverage Requirement

The APIs directly relevant to this topic include the following.

### File handling

```python
open()
file.write()
file.writelines()
file.flush()
file.close()
file.fileno()
```

### `pathlib`

```python
from pathlib import Path

Path()
Path.exists()
Path.is_file()
Path.is_dir()
Path.parent
Path.name
Path.read_text()
Path.write_text()
```

### OS operations

```python
import os

os.replace()
os.fsync()
os.access()
```

### Temporary files

```python
import tempfile

tempfile.NamedTemporaryFile()
tempfile.TemporaryDirectory()
tempfile.mkstemp()
```

### JSON

```python
import json

json.dump()
json.dumps()
json.load()
json.loads()
```

### CSV

```python
import csv

csv.writer()
csv.DictWriter()
writerow()
writerows()
```

### Testing

```python
import pytest

pytest.raises()
tmp_path
```

### Important API notes

You do not need to memorize every optional parameter.

You do need to understand the behaviors that influence:

```text
creation
truncation
append
encoding
newline handling
buffering
cleanup
replacement
durability
testing
```

#### `Path.write_text()`

Convenient for small whole-file writes:

```python
from pathlib import Path

Path("message.txt").write_text(
    "hello\n",
    encoding="utf-8",
)
```

It is not itself a temporary-file-plus-replacement protocol.

#### `Path.read_text()`

Useful for tests and simple reads:

```python
text = Path("message.txt").read_text(encoding="utf-8")
```

#### `tempfile.mkstemp()`

Useful when you want direct control over a unique temporary path and file descriptor:

```python
import os
import tempfile
from pathlib import Path

directory = Path(".")
fd, name = tempfile.mkstemp(
    prefix=".candidate.",
    suffix=".tmp",
    dir=directory,
    text=True,
)

try:
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write("candidate\n")
        file.flush()
finally:
    Path(name).unlink(missing_ok=True)
```

The example illustrates that low-level APIs transfer more resource-management responsibility to your code.

#### `TemporaryDirectory()`

Useful for isolated multi-file temporary work:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = Path(directory) / "one.txt"
    path.write_text("one\n", encoding="utf-8")
```

Use the simplest API that satisfies the reliability requirement.
## 55. Important Technical Accuracy Requirements

### `"w"` mode

Opening an existing file with `"w"` truncates it.

### `"a"` mode

Append mode preserves existing contents but can be wrong for rerunnable result files because repeated executions can accumulate duplicate logical output.

### `"x"` mode

Exclusive creation fails if the destination already exists. It is not a general replacement strategy.

### `flush()`

`flush()` pushes buffered data from the Python file object toward the underlying stream. It is not a universal stable-storage durability guarantee.

### `fsync()`

`os.fsync()` requests synchronization according to the operating system/filesystem semantics. It is not a magical guarantee against every storage or hardware failure.

### `os.replace()`

It is useful for replacement/rename semantics and, on platforms with the relevant guarantees, atomic publication of a file within the same filesystem. It is not equivalent to durable persistence.

### Temporary files

For atomic replacement, the temporary file should generally be created in the same directory/filesystem as the destination.

### Permissions

`os.access()` or another pre-check does not guarantee that the later operation will succeed. The actual operation must still be handled.

### Crash safety

A normal successful Python write does not automatically mean the application has a crash-safe update protocol.

### Platform differences

Temporary-file reopening/deletion behavior and durability guarantees can vary by operating system and filesystem.

Do not write documentation such as:

```text
"this function guarantees the file can never be lost"
```

unless you have an environment-specific basis for that exact guarantee.
## 56. Concept → Internal Mechanics → Practice

For each major concept, use:

```text
1. What is it?
2. Why does it exist?
3. Simple analogy
4. Technical definition
5. How Python implements it
6. Small example
7. What happens internally
8. Failure scenario
9. Production use
10. Practice exercise
```

### Truncation

**What is it?**

Removing the existing contents as part of opening in `"w"` mode.

**Why does it exist?**

Because `"w"` is intended to create a fresh writable file representation.

**Failure scenario**

The program truncates the destination and then crashes before the replacement content is complete.

**Production use**

Recognize the danger before updating configuration/state files.

### Temporary-file staging

**What is it?**

Writing the candidate new version somewhere other than the official destination.

**Why?**

The old version remains available while the new version is being prepared.

**Failure scenario**

Candidate write fails; destination stays unchanged.

**Production use**

State, configuration, metadata, reports, batch outputs.

### Atomic replacement

**What is it?**

Publishing the complete candidate through a replacement operation.

**Failure scenario**

Replacement fails; the candidate is not the official destination.

**Production use**

Prevent readers from consuming a file that is being constructed in place.

### Durability

**What is it?**

The persistence strength required after crash/power-loss conditions.

**Failure scenario**

A completed operation was not synchronized strongly enough for the system's requirement.

**Production use**

Critical state and checkpoint files.

### Practice

For every file your own code writes, complete this sentence:

> "If the process stops here, the destination contains ________."

If you cannot fill it in, inspect the write protocol before shipping.
## 57. Exercises

### Beginner Exercise 1 — Write a Text File

**Problem**

Write `hello.txt` containing:

```text
Hello, Python!
```

**Requirements**

- use `with open()`;
- use UTF-8;
- read the file back;
- verify the content.

**Hints**

Use `"w"` to create the file and `"r"` to read it.

**Expected behavior**

The read-back value equals the written value.

**Solution**

```python
from pathlib import Path

path = Path("hello.txt")

with path.open("w", encoding="utf-8") as file:
    file.write("Hello, Python!\n")

assert path.read_text(encoding="utf-8") == "Hello, Python!\n"
```

**Explanation**

The exercise establishes ordinary file writing before introducing safe replacement.

---

### Beginner Exercise 2 — Compare `"w"` and `"a"`

**Problem**

Create a file with one line, then append another.

**Requirements**

- first use `"w"`;
- then use `"a"`;
- inspect the final file.

**Hints**

Use the same `Path`.

**Expected behavior**

```text
first
second
```

**Solution**

```python
from pathlib import Path

path = Path("modes.txt")

with path.open("w", encoding="utf-8") as file:
    file.write("first\n")

with path.open("a", encoding="utf-8") as file:
    file.write("second\n")

assert path.read_text(encoding="utf-8") == "first\nsecond\n"
```

**Explanation**

The second operation preserves the first line.

---

### Beginner Exercise 3 — UTF-8 Text

**Problem**

Write and read text containing non-ASCII characters.

**Requirements**

Use UTF-8 on both operations.

**Hints**

Keep the text in a variable.

**Expected behavior**

The round-trip is identical.

**Solution**

```python
from pathlib import Path

text = "Hello — नमस्ते — こんにちは\n"
path = Path("unicode.txt")

path.write_text(text, encoding="utf-8")

assert path.read_text(encoding="utf-8") == text
```

**Explanation**

Both sides use the same explicit encoding.

---

### Beginner Exercise 4 — Exclusive Creation

**Problem**

Create a marker only if it does not already exist.

**Requirements**

Use `"x"` and demonstrate the second run fails.

**Hints**

Catch `FileExistsError`.

**Expected behavior**

The first call creates the file. The second call reports that the path already exists.

**Solution**

```python
from pathlib import Path

path = Path("first-run.marker")

with path.open("x", encoding="utf-8") as file:
    file.write("created\n")

try:
    with path.open("x", encoding="utf-8") as file:
        file.write("created again\n")
except FileExistsError:
    print("marker already exists")
```

**Explanation**

Exclusive creation is useful for create-once semantics. It does not solve safe replacement.

---

### Intermediate Exercise 5 — Implement Safe Text Replacement

**Problem**

Implement a safe text writer.

**Requirements**

- accept `Path` and `str`;
- use a temporary file in the destination directory;
- use UTF-8;
- use `os.replace()`;
- clean up on failure.

**Hints**

Track the temporary path.

**Expected behavior**

A successful call produces the new content. A pre-replacement failure leaves the old destination unchanged.

**Solution**

```python
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def safe_write_text(path: Path, content: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            file.write(content)
            file.flush()

        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
```

**Explanation**

The destination is not opened with `"w"`. It is replaced only after the candidate file is complete.

---

### Intermediate Exercise 6 — Safe JSON

**Problem**

Write a dictionary as safe JSON.

**Requirements**

- validate the payload type;
- use `json.dumps()`;
- use `sort_keys=True`;
- use the safe writer.

**Hints**

Serialize before the file update.

**Expected behavior**

A serialization failure leaves the destination untouched.

**Solution**

```python
import json
from pathlib import Path


def write_json(path: Path, payload: dict) -> None:
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")

    content = json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"

    safe_write_text(path, content)
```

**Explanation**

Validation and serialization happen before publication.

---

### Intermediate Exercise 7 — Safe CSV

**Problem**

Write dictionaries to CSV safely.

**Requirements**

- use `csv.DictWriter`;
- use UTF-8;
- use `newline=""`;
- stage the candidate;
- replace the destination.

**Solution**

```python
import csv
import os
import tempfile
from pathlib import Path


def safe_write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, object]],
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            file.flush()

        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
```

**Explanation**

The final CSV is published only after all rows are written.

---

### Advanced Exercise 8 — Add Optional Durability

**Problem**

Add a `durable` option to the safe text writer.

**Requirements**

When `durable=True`, flush the file and call `os.fsync(file.fileno())`.

**Expected behavior**

Both normal and durability-aware modes produce the same final logical content. The second requests stronger synchronization.

**Solution**

```python
import os
import tempfile
from pathlib import Path


def safe_write_text(
    path: Path,
    content: str,
    *,
    durable: bool = False,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            file.write(content)
            file.flush()

            if durable:
                os.fsync(file.fileno())

        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
```

**Explanation**

Durability is made explicit instead of assumed.

---

### Advanced Exercise 9 — Prove Old-File Preservation

**Problem**

Inject a failure after candidate creation but before replacement.

**Requirements**

- create an old destination;
- create a candidate;
- raise a controlled exception;
- assert the destination remains old;
- assert the candidate is removed.

**Solution**

```python
from pathlib import Path
import pytest


def write_candidate_then_fail(path: Path, content: str) -> None:
    candidate = path.parent / f".{path.name}.tmp"

    try:
        candidate.write_text(content, encoding="utf-8")
        raise OSError("simulated failure before replacement")
    finally:
        candidate.unlink(missing_ok=True)


def test_old_file_survives(tmp_path):
    path = tmp_path / "state.txt"
    path.write_text("OLD\n", encoding="utf-8")

    with pytest.raises(OSError, match="simulated"):
        write_candidate_then_fail(path, "NEW\n")

    assert path.read_text(encoding="utf-8") == "OLD\n"
```

**Explanation**

This is controlled failure injection. It is not a physical crash simulation. It tests the software invariant we care about.

---

### Advanced Exercise 10 — Explain the Guarantee

**Problem**

Explain the difference among atomicity, buffering, and durability.

**Requirements**

Answer in one paragraph and with a small diagram.

**Expected behavior**

Your answer should separate the concepts.

**Solution**

```text
write()
  ↓
Python buffering

flush()
  ↓
push buffered data onward

fsync()
  ↓
request stronger synchronization

os.replace()
  ↓
publish the prepared candidate
```

Atomicity asks whether the destination is published as an old-or-new file rather than a partially constructed destination. Durability asks how strongly the completed update survives failures.

**Explanation**

The most common production mistake is treating all four operations as different names for "save the file." They are not.
## 58. Mini Project — Deliverables and Acceptance Tests

The **Crash-Safe JSON State File Manager** from the previous section is complete when it satisfies these acceptance tests.

### Acceptance Test 1 — First creation

```text
destination does not exist
        ↓
save valid state
        ↓
destination exists
        ↓
JSON parses
```

### Acceptance Test 2 — Replacement

```text
destination = OLD
        ↓
save valid NEW state
        ↓
destination = NEW
```

### Acceptance Test 3 — Invalid candidate

```text
destination = OLD
        ↓
invalid state
        ↓
save rejected
        ↓
destination = OLD
```

### Acceptance Test 4 — Candidate write failure

```text
destination = OLD
        ↓
candidate write fails
        ↓
destination = OLD
```

### Acceptance Test 5 — Cleanup

```text
candidate created
        ↓
failure
        ↓
candidate removed when ordinary cleanup runs
```

### Acceptance Test 6 — Durability policy

The project must document:

```text
durable=False
→ ordinary safe replacement

durable=True
→ request synchronization before publication
```

The documentation must explicitly avoid claiming universal power-loss guarantees.

### Acceptance Test 7 — Observable logging

The logs should identify the phase:

```text
publishing state
state published
state update failed
```

Do not log full sensitive state.

### Acceptance Test 8 — Concurrency limitation

The project documentation must state:

> Multiple concurrent writers are outside the guarantees of the basic helper.

### Final project explanation

A strong project report can summarize:

```text
Input
  ↓
Validation
  ↓
Serialization
  ↓
Temporary candidate
  ↓
Write
  ↓
Flush / optional sync
  ↓
Replace
  ↓
Final state
```

and for failure:

```text
Candidate fails
  ↓
Destination remains last known-good state
  ↓
Candidate cleanup
  ↓
Error reported
```

That is the practical skill this lesson is designed to build.
## 59. Interview Questions

### Basic

#### Question 1 — What does `open(..., "w")` do?

**How to Think:** Ask what happens to an existing destination.

**Answer:** It opens for writing and truncates an existing file.

**Why It Matters:** Truncation can destroy the previous valid version before the new one is complete.

---

#### Question 2 — What is the difference between `"w"` and `"a"`?

**How to Think:** Replace versus append.

**Answer:** `"w"` truncates/rewrites; `"a"` appends to existing content.

**Why It Matters:** Append can create duplicate output on reruns.

---

#### Question 3 — Why use `with open()`?

**How to Think:** Resource lifetime.

**Answer:** It manages closing the file as the block exits, including exception paths.

**Why It Matters:** Reliable cleanup is fundamental to correct file handling.

---

#### Question 4 — What does `write()` return?

**Answer:** For text I/O, it returns the number of characters written by that call.

**Why It Matters:** It describes the Python-level write, not storage durability.

---

#### Question 5 — What is UTF-8?

**Answer:** A Unicode encoding used to represent text as bytes.

**Why It Matters:** Explicit encoding improves reproducibility across environments.

### Intermediate

#### Question 6 — What is a partial write?

**Answer:** A file update that leaves only part of the intended representation in the target.

**Why It Matters:** Structured files can become unusable.

---

#### Question 7 — Why use a temporary file?

**Answer:** To construct the candidate without modifying the official destination until the candidate is ready.

**Why It Matters:** Failures before publication can leave the old file available.

---

#### Question 8 — What is atomic replacement?

**Answer:** Publishing a prepared candidate through a replacement operation so readers should observe the old or new destination rather than an in-progress construction, subject to platform semantics.

**Why It Matters:** It reduces exposure to partially written destination files.

---

#### Question 9 — What does `os.replace()` do?

**Answer:** It renames/replaces the source at the destination, replacing an existing file when permitted.

**Why It Matters:** It is a common publication primitive for safe whole-file updates.

---

#### Question 10 — What does `flush()` do?

**Answer:** It pushes buffered data from the Python file object toward its underlying stream.

**Why It Matters:** It is not a stable-storage durability guarantee.

---

#### Question 11 — What does `os.fsync()` do?

**Answer:** It requests synchronization of file data/state through OS/filesystem semantics.

**Why It Matters:** Some critical files justify stronger persistence requests.

### Advanced

#### Question 12 — Why is atomicity different from durability?

**Answer:** Atomicity concerns the visibility of the update at the destination; durability concerns persistence after failure.

**Why It Matters:** A file can have atomic replacement semantics without satisfying every power-loss durability requirement.

---

#### Question 13 — Why should the temp file be near the destination?

**Answer:** Same-directory/same-filesystem staging supports replacement without a cross-filesystem move.

**Why It Matters:** Cross-filesystem operations can fail and do not provide the same atomic rename semantics.

---

#### Question 14 — Why is `flush()` not enough for power-loss safety?

**Answer:** It addresses Python-level buffering but does not establish the strongest possible storage persistence guarantee.

**Why It Matters:** Critical state may need explicit synchronization.

---

#### Question 15 — When would `fsync()` be appropriate?

**Answer:** When the business consequence of losing a completed update justifies the synchronization cost.

**Why It Matters:** It should be requirements-driven.

---

#### Question 16 — How would you preserve the last known-good state?

**Answer:** Never truncate or delete it before the candidate is complete; stage the candidate and replace the destination only after success.

**Why It Matters:** This is the core crash-safe publication pattern.

---

#### Question 17 — Does atomic replacement solve concurrent writers?

**Answer:** No. It publishes candidates safely but does not decide which concurrent logical update should win or prevent lost updates.

**Why It Matters:** Atomicity and concurrency control are distinct.

---

#### Question 18 — How would you test a safe-write helper?

**Answer:** Use isolated temporary directories, test creation/replacement, inject failures before replacement, verify old-file preservation, verify cleanup, and parse final JSON/CSV outputs.

**Why It Matters:** Tests should prove the recovery invariants, not merely the happy path.
## 60. Architecture Questions

### 1. How would you safely update a configuration file?

**Structured answer**

Validate the requested configuration, build the complete new representation in memory, write it to a temporary file beside the destination, synchronize if required, close it, replace the destination, and log the outcome.

**Simplified assumption**

One writer at a time.

---

### 2. How would you prevent readers from seeing partial JSON?

**Structured answer**

Do not write the JSON directly to the destination. Prepare a complete candidate and publish it with `os.replace()`.

**Limitation**

Concurrent writers remain a separate problem.

---

### 3. What happens if the process crashes halfway through a direct `"w"` write?

**Structured answer**

The destination may already have been truncated and may contain incomplete new data.

**Design response**

Move the construction work to a temporary file.

---

### 4. How would you preserve the previous valid file?

**Structured answer**

Keep the destination untouched until candidate generation and writing succeed.

---

### 5. How would you design a checkpoint file?

**Structured answer**

Define a schema, validate it, serialize complete state, stage it, synchronize according to the durability requirement, replace the destination, and test failure paths.

**Limitation**

Checkpoint correctness also depends on what the checkpoint means relative to actual work.

---

### 6. What is atomicity versus durability?

**Structured answer**

Atomicity is about update visibility as an old-or-new destination. Durability is about survival of completed updates under specified failure conditions.

---

### 7. When does `fsync()` matter?

**Structured answer**

When the consequences of losing a completed file update after a crash/power event justify stronger synchronization.

---

### 8. Why not use `/tmp` for every candidate?

**Structured answer**

The temp file may be on another filesystem, causing `os.replace()` to fail or forcing a non-atomic copy/move strategy.

---

### 9. How does safe writing support repeatable jobs?

**Structured answer**

It lets the job regenerate a complete output and publish it as one destination update rather than accumulating partial or duplicate final output.

---

### 10. How would you design output for an AI evaluation pipeline?

**Structured answer**

Use stable evaluation IDs, deterministic serialization where useful, temporary-file staging, atomic publication, and explicit state/recovery rules.

---

### 11. What if two processes write the same file?

**Structured answer**

Recognize that atomic replacement is not enough. Add writer coordination, versioning, or a storage mechanism designed for concurrent updates.

---

### 12. How would you test the design?

**Structured answer**

Test success, old-file preservation on controlled failure, candidate cleanup, JSON/CSV parseability, and integration behavior in the target environment.

The architecture question is not "Can I write this file?" It is:

> **What state is visible after every failure point?**
## 61. Debugging Scenarios

### Scenario 1 — JSON file suddenly becomes invalid

**Problem**

A previously valid `state.json` occasionally cannot be parsed.

**How to Think**

Inspect how it is written.

**Diagnosis**

Look for direct:

```python
open(path, "w")
json.dump(...)
```

and correlate failures with process interruption.

**Solution**

Generate complete JSON and publish it via a temporary-file replacement strategy.

**Production Lesson**

Do not construct important structured state in place.

---

### Scenario 2 — Existing file becomes empty after a crash

**Problem**

The old file was valid; after a failed update it is empty.

**How to Think**

Think "truncate first."

**Diagnosis**

Find `"w"` opening of the destination before the new content was complete.

**Solution**

Stage the candidate before touching the destination.

**Production Lesson**

Opening in `"w"` is itself a meaningful state change.

---

### Scenario 3 — Rerunning creates duplicate output

**Problem**

Rows or result lines appear twice.

**How to Think**

Check append semantics and idempotency.

**Diagnosis**

Look for `"a"` or repeated appending without stable record identity.

**Solution**

Use replacement for whole-file output or keyed record-level semantics.

**Production Lesson**

Append is a semantic choice, not just an I/O shortcut.

---

### Scenario 4 — Temporary files accumulate

**Problem**

Thousands of candidates remain.

**How to Think**

Check cleanup ownership.

**Diagnosis**

Look for missing `finally`, abnormal termination, or a path that is no longer tracked.

**Solution**

Centralize cleanup and define stale-candidate recovery if necessary.

**Production Lesson**

Temporary storage is part of the system lifecycle.

---

### Scenario 5 — `flush()` used but a power failure lost data

**Problem**

The developer believed `flush()` guaranteed durable storage.

**How to Think**

Separate buffering from durability.

**Diagnosis**

Review whether the durability requirement was defined and whether synchronization was part of the protocol.

**Solution**

Use `fsync()` when justified and document the platform-specific assumptions.

**Production Lesson**

Never translate `flush()` into "saved forever."

---

### Scenario 6 — Two processes lose each other's changes

**Problem**

Both writers report success but one logical update is missing.

**How to Think**

Atomic replacement protects each writer's publication, not logical concurrency.

**Diagnosis**

Reconstruct:

```text
A reads old
B reads old
A prepares A'
B prepares B'
A replaces
B replaces
```

**Solution**

Add coordination/version checks or change the storage design.

**Production Lesson**

Atomic publication is not synchronization among writers.

---

### Scenario 7 — `os.replace()` fails

**Problem**

The candidate exists but replacement raises `OSError`.

**How to Think**

Inspect the actual paths and environment.

**Diagnosis**

Check:

```text
same filesystem?
correct source?
correct destination?
destination is directory?
permissions?
platform restrictions?
```

**Solution**

Stage in the destination directory, handle `OSError`, and preserve the candidate/destination state according to the cleanup policy.

**Production Lesson**

The publication step itself can fail and belongs in the failure matrix.
## 62. Knowledge Check

### Question 1

Why is opening an existing file with `"w"` dangerous?

**Answer**

Because it truncates the existing file before the replacement content is fully prepared.

### Question 2

Why is a temporary file safer?

**Answer**

It separates candidate construction from official publication.

### Question 3

Why should the candidate usually be in the same directory?

**Answer**

It supports same-filesystem replacement and avoids cross-filesystem rename limitations.

### Question 4

What does `os.replace()` protect against?

**Answer**

It lets the program publish a prepared candidate as the destination through a replacement operation instead of constructing the destination in place.

### Question 5

What does `os.replace()` not guarantee?

**Answer**

It does not provide every durability guarantee, concurrency guarantee, or semantic correctness guarantee.

### Question 6

Why is `flush()` different from `fsync()`?

**Answer**

`flush()` addresses Python-level buffering; `fsync()` requests stronger OS-level synchronization semantics.

### Question 7

Why can append break repeatable output?

**Answer**

A repeated run can append a second copy of the same logical results.

### Question 8

Why is `os.access()` not a guarantee?

**Answer**

The environment can change after the check and before the actual write.

### Question 9

Why should validation happen before publication?

**Answer**

An invalid candidate should fail before becoming official persistent state.

### Question 10

Why should tests verify the old file after controlled failure?

**Answer**

Because the core reliability requirement is often that failed candidate construction must not destroy the last known-good destination.
## 63. Important Distinctions

### `"w"` vs `"a"`

```text
w = replace/truncate
a = append
```

### Direct destination write vs staged replacement

```text
Direct:
application → destination

Safer:
application → temporary candidate → destination replacement
```

### Atomicity vs durability

```text
Atomicity:
old OR new destination state

Durability:
how strongly the completed state persists after specified failures
```

### `flush()` vs `fsync()`

```text
flush()
= push Python buffering onward

fsync()
= request synchronization through OS/filesystem semantics
```

### Safe write vs idempotency

```text
safe write
= file-update integrity

idempotency
= repeated logical operation safety
```

### Safe write vs concurrency control

```text
safe replacement
≠
multi-writer coordination
```

### Candidate state vs published state

```text
temporary file
= candidate

destination
= published state
```

### Close vs durability

```text
close()
= release the Python file resource

durability
= persistence property with separate system-level considerations
```

### Permission check vs successful operation

```text
pre-check
≠
guaranteed later success
```

### Stable serialization vs safe publication

```text
sort_keys=True
= stable JSON key ordering

os.replace()
= publication mechanism
```

These are complementary tools, not interchangeable ones.
## 64. Production Principles

### Principle 1

> **Never assume a direct file write is crash-safe.**

For important state, analyze what happens during truncation and partial writing.

### Principle 2

> **Preserve the last known-good file whenever practical.**

The old file is valuable recovery state.

### Principle 3

> **Generate complete new content before replacing the destination.**

Validation and serialization should happen before publication.

### Principle 4

> **Use temporary-file plus replacement patterns for important atomic updates.**

This keeps candidate construction away from published state.

### Principle 5

> **Understand atomicity and durability separately.**

A correct replacement protocol still needs an explicit durability policy if durability matters.

### Principle 6

> **Use `fsync()` based on actual requirements.**

Synchronization can cost performance and its exact guarantees are system-dependent.

### Principle 7

> **Treat encoding and newline behavior deliberately.**

Make the file format and text representation explicit.

### Principle 8

> **Clean up temporary artifacts after expected failures.**

Temporary candidates need lifecycle ownership.

### Principle 9

> **Test failure paths, not only successful writes.**

The failure path tells you whether the design actually preserves the required invariant.

### Principle 10

> **Combine safe writes with idempotent job design when output may be regenerated.**

Safe file publication and safe repeated processing solve different parts of the same production problem.
## 65. Final Mental Model

The fundamental safe-write flow is:

```text
Generate complete content
        ↓
Create temporary file
        ↓
Write content completely
        ↓
Flush
        ↓
Sync if durability requires it
        ↓
Close temporary file
        ↓
Atomically replace destination
        ↓
Clean up
```

Failure before publication:

```text
Generate content
        ↓
temporary write fails
        ↓
original destination remains available
        ↓
candidate cleanup
        ↓
failure reported
```

### Safe file update formula

```text
Safe File Write
=
complete new content
+
temporary candidate
+
same-filesystem staging
+
atomic replacement
+
appropriate durability strategy
+
failure cleanup
+
explicit encoding
+
tests
```

### The final question

Before shipping a file-writing function, ask:

> **What will the destination contain if the process stops immediately before the write, during the write, immediately after the candidate is synchronized, and immediately around replacement?**

Then document the answer.

That question is more valuable than memorizing a single code snippet.
## 66. Completion Checklist

### Fundamentals

- [ ] I understand how Python writes files.
- [ ] I understand `open()`.
- [ ] I understand `"w"`, `"a"`, and `"x"`.
- [ ] I understand the other important update modes.
- [ ] I understand `write()`.
- [ ] I understand `writelines()`.
- [ ] I understand UTF-8 encoding.
- [ ] I understand newline handling.
- [ ] I understand context managers.
- [ ] I understand closing files.

### Failure Safety

- [ ] I understand truncation.
- [ ] I understand partial writes.
- [ ] I understand the danger of direct destination writes.
- [ ] I understand temporary files.
- [ ] I understand `NamedTemporaryFile`.
- [ ] I understand `TemporaryDirectory`.
- [ ] I understand same-filesystem staging.
- [ ] I understand atomic replacement.
- [ ] I understand `os.replace()`.
- [ ] I understand temporary cleanup.

### Durability

- [ ] I understand buffering.
- [ ] I understand `flush()`.
- [ ] I understand `file.fileno()`.
- [ ] I understand `os.fsync()`.
- [ ] I understand why `flush()` is not durability.
- [ ] I understand why atomicity is not durability.
- [ ] I can choose a durability policy based on requirements.

### Formats and Applications

- [ ] I can safely update text files.
- [ ] I can safely update JSON.
- [ ] I can safely update CSV.
- [ ] I can safely update configuration files.
- [ ] I can safely update job-state files.
- [ ] I can safely update AI evaluation/inference artifacts.

### Security and Permissions

- [ ] I understand permission-related errors.
- [ ] I understand the limits of `os.access()`.
- [ ] I know that the actual write still needs exception handling.
- [ ] I avoid logging sensitive file contents.

### Reliability

- [ ] I understand the relationship between safe writes and idempotency.
- [ ] I understand safe reruns.
- [ ] I can identify a crash window.
- [ ] I know why append can create duplicates.
- [ ] I know why atomic replacement does not solve concurrency.
- [ ] I can explain last-known-good versus candidate state.

### Testing

- [ ] I can use `pytest`.
- [ ] I can use `tmp_path`.
- [ ] I can test successful writes.
- [ ] I can test replacement.
- [ ] I can test failure before replacement.
- [ ] I can test old-file preservation.
- [ ] I can test temporary cleanup.
- [ ] I can parse the final JSON/CSV output.
- [ ] I understand that unit tests do not prove every physical crash scenario.

### Production Readiness

- [ ] I can explain exactly what my safe-write helper guarantees.
- [ ] I can explain what it does not guarantee.
- [ ] I can design a failure matrix.
- [ ] I can choose staging, replacement, and durability techniques deliberately.
- [ ] I can debug a file-write incident from evidence.
## 67. Final Self-Review

### Coverage

This chapter teaches:

- `open()`;
- file modes;
- `write()`;
- `writelines()`;
- encoding;
- newlines;
- context managers;
- closing;
- truncation;
- append;
- exclusive creation;
- partial writes;
- temporary files;
- `NamedTemporaryFile`;
- `TemporaryDirectory`;
- `mkstemp()`;
- same-filesystem staging;
- atomic replacement;
- `os.replace()`;
- buffering;
- `flush()`;
- `fileno()`;
- `os.fsync()`;
- atomicity;
- durability;
- JSON writes;
- JSON serialization stability;
- CSV writes;
- configuration/state updates;
- permissions;
- `os.access()`;
- path validation;
- write exceptions;
- cleanup;
- idempotency relationship;
- batch jobs;
- Applied AI use cases;
- concurrency caveats;
- testing;
- debugging;
- production design.

### Practicality

The file contains:

- beginner examples;
- intermediate examples;
- advanced examples;
- bad versus good implementations;
- failure scenarios;
- complete production examples;
- exercises with solutions;
- mini-project;
- interview questions;
- architecture questions;
- debugging scenarios;
- knowledge checks;
- completion checklist.

### Technical Accuracy

The chapter keeps these distinctions explicit:

```text
"w"
= truncates existing destination

flush()
≠
durable persistence

fsync()
= synchronization request

os.replace()
= replacement/publication primitive

atomicity
≠
durability

permission pre-check
≠
guaranteed write

atomic replacement
≠
concurrency control
```

The chapter avoids claiming that Python's ordinary file APIs provide universal power-loss guarantees.

### Beginner Accessibility

The progression is:

```text
basic write
→ modes
→ failure
→ truncation
→ temporary files
→ replacement
→ buffering
→ durability
→ structured files
→ testing
→ production design
```

Every major code example is accompanied by explanation and a statement of important limitations.
## 68. Final File-Scope Verification

Requested target:

```text
10-Production-Habits-for-Python-Programs/05-safe-file-writes.md
```

The task specification requires that this lesson be contained in one Markdown file and that no other project, Python, configuration, README, exercise, solution, or folder files be created or modified.

This artifact therefore contains:

```text
explanations
+
examples
+
exercises
+
solutions
+
mini-project
+
interview questions
+
architecture questions
+
debugging scenarios
+
knowledge checks
+
production principles
+
completion checklist
+
self-review
```

all in this one Markdown document.

No auxiliary files are required for the lesson itself.
