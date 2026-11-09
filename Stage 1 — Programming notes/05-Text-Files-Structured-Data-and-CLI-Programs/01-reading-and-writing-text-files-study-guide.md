# Reading and Writing Text Files — Complete Study Guide

**Source lesson:** `01-reading-and-writing-text-files.md`  
**Roadmap position:** Stage 1 → Module 05 — Text Files, Structured Data, and CLI Programs → Lesson 01  
**Purpose:** Complete lesson explanation, roadmap/level assessment, and solutions to all 21 progressive exercises plus the 18-question knowledge check.

---

# Part A — Complete lesson summary and teaching notes

## 1. Why files matter

A Python variable normally exists in the program's memory while the program runs. When the process ends, that in-memory value is gone. A **file** stores information persistently so it remains available after the program stops. Files also let programs exchange information with people, other programs, and systems.

| Storage | Lifetime | Typical purpose |
|---|---|---|
| Variable / RAM | Usually while the program runs | Temporary computation |
| Text or other file | Survives program termination | Logs, simple persistence, configuration, data exchange |
| Database | Survives program termination | Structured, queryable, concurrent data |

RAM operations are much faster than disk I/O. File operations also depend on external conditions: the path may be wrong, the file may be missing, permissions may deny access, the disk may be full, or the content may use an unexpected encoding.

The chapter's central engineering rule is:

```text
validate at the boundary → transform into reliable Python data → process
```

Validate an external file as soon as it enters the program. Convert its content into a clear internal representation such as `str` or `list[str]`. Then keep business logic separate from file operations.

## 2. What is file I/O?

I/O means **Input/Output**.

- Reading: data flows from the file into the program.
- Writing: data flows from the program into a file.
- Appending: new data is added after existing file content.

The normal lifecycle is **open → use → close**. An open file consumes an operating-system resource, so it must be closed reliably.

The operating-system path is conceptually:

```text
Python program → operating system → filesystem → physical storage
```

Python asks the OS to perform file operations; it does not directly manipulate the physical disk.

## 3. Text files and binary files

At the hardware level, every file is a sequence of bytes.

- A **text file** stores bytes intended to represent readable characters under an encoding. Examples: `.txt`, `.log`, `.csv`, `.py`, `.json`, `.md`.
- A **binary file** stores bytes intended for non-text interpretation, such as image pixels, audio data, or compiled program data. Examples: `.jpg`, `.png`, `.pdf`, `.zip`.

Python's `open()` has two broad interpretations:

- Text mode (`"t"`, the default) decodes bytes into Python `str` when reading and encodes `str` into bytes when writing.
- Binary mode (`"b"`) works with raw `bytes` and does not perform text decoding/encoding.

This lesson teaches text mode. Binary file processing is outside its scope.

## 4. Paths, `open()`, and file objects

A **path** identifies a location. It is just data, often a string. A **file object** is the open connection to the file at that location. The object tracks state such as the cursor and exposes methods such as `read()`, `write()`, `seek()`, and `close()`.

```python
path = "greeting.txt"
f = open(path, "r", encoding="utf-8")

print(type(path))  # <class 'str'>
print(type(f))     # <class '_io.TextIOWrapper'>

f.close()
```

The path string is not the file object. Calling `open()` asks Python and the OS to establish an open connection and returns a file object.

Opening a file does **not** load all its contents into memory. It establishes the connection and positions the cursor at the beginning. Reading methods load content. This distinction is important when working with very large files.

### `open()` signature

```python
open(file, mode='r', buffering=-1, encoding=None, errors=None,
     newline=None, closefd=True, opener=None)
```

- `file`: path string (or, in the later `pathlib` lesson, a `Path` object).
- `mode`: intended access: read, write, append, create, etc. Write it explicitly.
- `buffering`: controls buffering. The default `-1` is appropriate for nearly all beginner code.
- `encoding`: byte-to-character translation rule. Specify the known encoding explicitly; UTF-8 is common when the file is known to be UTF-8 or your program controls the format.
- `errors`: policy for undecodable/ unencodable data. Default `"strict"` raises an error. Do not casually use `"ignore"` or `"replace"` because that can hide data corruption.
- `newline`: controls newline translation. Default `None` enables universal newline handling. Full details belong to the later encoding/newline lesson.
- `closefd`: controls whether closing a file object also closes a low-level descriptor. Rarely relevant when passing ordinary paths.
- `opener`: advanced custom OS-level opening behavior; recognize it, but do not use it at this stage.

The standard pattern is:

```python
with open("example.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

`with` opens the file, binds the returned object to `f`, and closes it when the indented block ends. If the file is missing, `FileNotFoundError` is raised before the body runs. If an exception occurs inside the body, the file is still closed and the exception continues propagating.

## 5. File modes — learn the differences precisely

| Mode | Must already exist? | Creates if missing? | Existing content | Read? | Write? |
|---|---:|---:|---|---:|---:|
| `"r"` | Yes | No | Preserved | Yes | No |
| `"w"` | No | Yes | **Erased immediately** (truncated) | No | Yes |
| `"a"` | No | Yes | Preserved; writes go to end | No | Yes |
| `"x"` | Must not exist | Yes | Raises `FileExistsError` if present | No | Yes |

Important modifiers:

- `"+"` adds the other capability: `"r+"` reads and writes; `"w+"`, `"a+"`, and `"x+"` can also read.
- `"b"` means binary mode: `bytes` rather than `str`.
- `"t"` means text mode and is the default.

Common combined modes include `"rb"`, `"wb"`, `"ab"`, `"r+"`, `"w+"`, `"a+"`, and `"x+"`.

**The destructive behavior of `"w"` is critical.** Opening an existing file in `"w"` truncates it to zero length immediately, even if you never call `write()`:

```python
with open("important_notes.txt", "w", encoding="utf-8") as f:
    pass

with open("important_notes.txt", "r", encoding="utf-8") as f:
    print(repr(f.read()))  # ''
```

Use `"w"` only when replacing the content is intended. Use `"a"` when preserving existing content and adding to the end. Use `"x"` when the file must be new and overwriting an existing file should be an error.

The lesson's safe examples use a disposable practice directory:

```python
import os

os.makedirs("practice_files", exist_ok=True)
os.chdir("practice_files")
```

Do not run destructive practice against real project or personal files. A relative path is interpreted relative to the **current working directory**, not necessarily the directory containing the script.

Opening examples and likely failures:

```python
open("existing.txt", "r", encoding="utf-8")  # succeeds if it exists and is readable
open("does_not_exist.txt", "r", encoding="utf-8")  # FileNotFoundError
open("log.txt", "x", encoding="utf-8")  # FileExistsError if it already exists
open("/root/secret.txt", "w", encoding="utf-8")  # may raise PermissionError
open("practice_files", "r", encoding="utf-8")  # IsADirectoryError if this is a directory
```

## 6. Four ways to read text

Every read starts at the current cursor position.

### `read()`

`f.read()` returns all remaining content as **one string**. It advances the cursor to EOF and loads the requested content into memory.

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    data = f.read()
print(data)
```

`f.read(size)` reads up to `size` **characters** in text mode:

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    print(repr(f.read(5)))  # 'Hello'
    print(repr(f.read(5)))  # ', fil'
    print(repr(f.read()))   # remaining characters
```

At end-of-file (EOF), `read()` returns `""`. A second `read()` after consuming the whole file therefore returns an empty string; it does not restart automatically.

`read()` does not return a list of lines. Iterating over its result iterates over individual characters.

### `readline()`

`f.readline()` reads exactly the next line. The returned string normally includes its trailing `"\n"`. At EOF it returns `""`.

```python
with open("multi_line.txt", "r", encoding="utf-8") as f:
    line1 = f.readline()
    line2 = f.readline()
```

A blank line is usually `"\n"`; EOF is `""`. Do not confuse them. A loop can detect EOF as follows:

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    while True:
        line = f.readline()
        if line == "":
            break
        print(repr(line))
```

### `readlines()`

`f.readlines()` reads all remaining lines into a `list[str]`. Each entry normally retains its newline. It loads the whole file into memory and creates list/string overhead, so use it only when the file is small enough and you genuinely need an indexable list or multiple passes.

### Direct iteration — the normal line-by-line choice

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(repr(line))
```

A file object is iterable. Each iteration yields one line, advances the cursor, and avoids loading the entire file into memory. For ordinary line-oriented processing, prefer `for line in f:`.

| Method | Result | Memory |
|---|---|---|
| `read()` | One string | Entire requested content |
| `read(size)` | One bounded string | Up to requested characters |
| `readline()` | One line string | One line |
| `readlines()` | List of all remaining lines | Whole file plus list overhead |
| `for line in f` | One line per iteration | One line at a time |

Newline cleanup: `.strip()` removes leading/trailing whitespace, not just newline characters. `line.rstrip("\n")` removes only trailing newline characters and preserves other whitespace.

```python
line = "  indented text  \n"
print(repr(line.strip()))       # 'indented text'
print(repr(line.rstrip("\n")))  # '  indented text  '
```

## 7. The file cursor: `tell()` and `seek()`

A file object tracks where the next read or write happens. This is its **cursor** or file position. In read mode it starts at position `0`; reads move it forward.

- `f.tell()` returns the current position as an integer.
- In text mode, treat that number as an **opaque position marker**. Save it and pass it back to `seek()`; do not assume it is a portable character or byte count.
- `f.seek(0)` reliably returns to the start.
- Seeking to a value previously returned by `tell()` is also meaningful. Arbitrary arithmetic offsets are not a beginner text-mode technique.

```python
with open("example.txt", "r", encoding="utf-8") as f:
    print(f.tell())       # 0
    print(f.readline())   # first line
    position = f.tell()   # save the current position
    f.seek(0)              # return to start
    print(f.readline())   # first line again
```

A second `read()` returns `""` if the first one already consumed the file. Use `seek(0)` if you deliberately need to read the same open file again.

## 8. Writing, `writelines()`, and appending

### `write()`

`f.write(text)` writes a `str` at the current cursor and returns the number of characters written. Passing a non-string such as an integer raises `TypeError`.

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("A")
    f.write("B")
    f.write("C")
```

The file contains `"ABC"`. **`write()` never inserts a newline automatically.** Include `"\n"` yourself:

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("First line\n")
    f.write("Second line\n")
```

Within one open, repeated writes continue from the current cursor. Truncation occurs when `"w"` opens an existing file, not before every `write()` call.

### `writelines()`

`f.writelines(iterable_of_strings)` writes each string back-to-back. It does not add separators or newline characters:

```python
lines = ["one", "two", "three"]
with open("output.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)

# Content is 'onetwothree', not three separate lines.
```

Correct it by including newlines in the strings:

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.writelines(line + "\n" for line in lines)
```

### Append mode

`"a"` creates a file if missing and places writes at its current end if it exists. It does not erase old content:

```python
with open("activity_log.txt", "a", encoding="utf-8") as f:
    f.write("Program started\n")
```

Repeated program runs add new entries. Append mode still does not add newlines automatically. If the old final line has no newline, prepend `"\n"` when the new text must begin on a separate line.

Append mode alone is not a concurrency guarantee: multiple processes writing simultaneously may interleave output. That issue is introduced in §43.

## 9. Closing files and context managers

`f.close()` closes the connection, flushes Python's buffered data to the OS, and releases OS resources. It does not guarantee physical storage durability in every failure scenario.

Forgetting to close a file can:
- leave buffered data unwritten,
- leak limited OS resources,
- cause access/locking problems on some platforms.

Manual close is fragile:

```python
f = open("data.txt", "r", encoding="utf-8")
data = f.read()
f.close()
```

If an exception happens before `close()`, cleanup is skipped.

Use a context manager:

```python
with open("data.txt", "r", encoding="utf-8") as f:
    data = f.read()
```

Python closes the file as the block exits, normally or through an exception. The exception is not hidden; it continues propagating after cleanup. This is the standard pattern for every file open in this chapter.

## 10. Read → process → write and reusable functions

The chapter demonstrates five pipelines:

1. Read a complete small text file, call `.upper()`, and write the transformed string.
2. Read lines, keep only lines for which `line.strip() != ""`, and write the remaining lines.
3. Keep lines containing a keyword using `"error" in line.lower()`.
4. Count whitespace-separated words using `len(text.split())`.
5. Create a summary using `len(lines)` and `sum(len(line.split()) for line in lines)` and write it to `summary.txt`.

The shared architecture is:

```text
read_text_file() → process_text() → write_text_file()
       I/O             pure logic          I/O
```

Separating these steps improves:
- **Testing:** transformation functions can be tested using ordinary strings.
- **Readability:** each step has one responsibility.
- **Reuse:** logic works with text from files, network responses, or test strings.
- **Debugging:** isolate read, transformation, and write failures.
- **Maintenance:** changing the input source does not require rewriting the business logic.

The lesson introduces reusable functions:

```python
def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def append_text_file(path: str, content: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)


def count_lines(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def find_lines_containing(path: str, keyword: str) -> list[str]:
    matches = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if keyword in line:
                matches.append(line.rstrip("\n"))
    return matches
```

These helpers use context managers and explicit UTF-8. The low-level helpers let errors propagate. A caller that understands the use case decides whether a missing file deserves a fallback.

## 11. Type hints

Type hints document the expected values and returned values:

```python
def read_text_file(path: str) -> str:
    ...

def count_lines(path: str) -> int:
    ...
```

The chapter also introduces:

```python
from typing import TextIO, Iterable

def process_lines(file: TextIO) -> int:
    return sum(1 for _ in file)

def non_blank_lines(lines: Iterable[str]) -> list[str]:
    return [line for line in lines if line.strip() != ""]
```

- `TextIO` describes an already-open text file object. The caller owns opening and closing it.
- `Iterable[str]` means any iterable that yields strings, such as a list of lines or a file object.
- `path: str` is sufficient for this chapter. `pathlib.Path` is the next lesson and is not required here.

## 12. Encoding and Unicode

A **character** is a text symbol. **Unicode** assigns characters code points. A **byte** is the stored/transmitted unit. An **encoding** defines how characters map to bytes.

- Encoding: Python `str` → bytes when writing.
- Decoding: bytes → Python `str` when reading.

UTF-8 represents essentially all characters used in modern written languages and is widely used. Use `encoding="utf-8"` when that is the known encoding or the format your program controls. Do not rely on platform-dependent defaults.

The lesson's mismatch example writes `"Café résumé 日本語"` using UTF-8, then attempts to read it as ASCII. This raises `UnicodeDecodeError`, because ASCII cannot decode the UTF-8 bytes representing those characters. The exception is preferable to silently guessing incorrectly.

Full encoding detection, byte-order marks, detailed `errors=`, and newline mechanics are deferred to the dedicated lesson.

## 13. Newline basics

A text file is a continuous sequence of characters. A line boundary is represented by a newline character, usually `"\n"` in Python strings.

```python
text = "First line\nSecond line\nThird line"
print(text)
```

Nothing in `write()` adds a line break automatically. Linux/macOS conventionally use `\n`; Windows traditionally uses `\r\n` on disk. Python's default text mode performs universal newline translation for common use cases. The `newline=` parameter's full behavior is deferred.

## 14. File-related exceptions and catch-vs-propagate

| Exception | Meaning / common cause |
|---|---|
| `FileNotFoundError` | Path missing, typo, wrong working directory |
| `PermissionError` | OS denies access |
| `IsADirectoryError` | Directory opened as if it were a file |
| `NotADirectoryError` | A file path used where a directory was expected |
| `UnicodeDecodeError` | Bytes do not match the chosen decoding |
| `UnicodeEncodeError` | Text cannot be encoded with the chosen encoding |
| `OSError` | General parent category for many OS/file failures |

A missing configuration file may be an expected, recoverable condition:

```python
try:
    with open("config.txt", "r", encoding="utf-8") as f:
        config_text = f.read()
except FileNotFoundError:
    config_text = ""
```

If decoding fails and there is no valid fallback, report context and re-raise:

```python
try:
    with open("data.txt", "r", encoding="utf-8") as f:
        text = f.read()
except UnicodeDecodeError as error:
    print(f"Could not decode {error}; check the file's actual encoding")
    raise
```

**Catch vs. propagate:**
- Catch an expected operational condition when you know a sensible recovery action.
- Let programmer bugs surface with their traceback. A wrong type, typo, or logic error is not a missing-file fallback.

Never use `except Exception: pass` as a general error eraser. It can hide permission errors, decoding errors, `NameError`, and genuine defects. Catch the specific exception you anticipated. Do not silently discard file failures; communicate why a fallback happened.

## 15. Safe file handling and partial output

Rules:
- Be certain before opening an important file in `"w"`.
- Confirm the path and working directory before destructive operations.
- Preserve the input by writing transformations to a separate output file.
- Validate and process before writing where practical.
- Verify generated output by reading it back.
- Practice only in disposable directories.

Risky pattern:

```python
with open("output.txt", "w", encoding="utf-8") as f:
    for record in records:
        f.write(process(record) + "\n")
```

If `process()` fails halfway through, the output is partial.

Safer against **processing failures**:

```python
processed_lines = [process(record) + "\n" for record in records]

with open("output.txt", "w", encoding="utf-8") as f:
    f.writelines(processed_lines)
```

All processing completes before the output file is opened. This costs memory because all results are retained. It does **not** protect against a failure during the actual write after truncation. True all-or-nothing replacement uses a temporary file followed by replacement/rename; the implementation is deferred to a later production lesson.

## 16. Large files, streaming, and chunks

Reading a multi-gigabyte file into one string may exhaust RAM or severely slow the machine. For line-oriented files, stream:

```python
matching_count = 0
with open("huge_file.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "ERROR" in line:
            matching_count += 1
print(f"Found {matching_count} matching lines")
```

The program holds one line at a time, processes it, then moves on. This is **streaming**.

For files that are not naturally line-oriented, use bounded chunks:

```python
chunk_size = 8192
with open("huge_file.txt", "r", encoding="utf-8") as f:
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        process(chunk)
```

`read(size)` returns up to that many characters in text mode. At EOF it returns `""`, so `if not chunk` ends the loop. An 8192-character chunk is a reasonable starting point, not a universal rule.

A chunk can end in the middle of a word, line, or logical record. Your processing must handle a boundary split if the task requires complete records. For line-oriented data, `for line in f` is simpler.

## 17. Buffering and `flush()`

Buffering means Python and the OS temporarily collect writes in memory and send them in larger batches. Disk I/O is slower than memory operations; batching many small writes reduces overhead.

The default `buffering=-1` is normally right. `buffering=1` requests line buffering (flush after newline) in the lesson's example. Do not tune buffering before measuring a real bottleneck.

`f.flush()` sends Python's buffered data to the operating system:

```python
with open("progress.log", "a", encoding="utf-8") as f:
    f.write("Step 1 complete\n")
    f.flush()
    do_something_slow()
    f.write("Step 2 complete\n")
```

This is useful when another program/user should see progress promptly or before an operation that might crash. It does **not** guarantee the OS has physically committed the bytes to storage hardware. Normal scripts can rely on context-manager closure to flush Python's buffer.

## 18. File-object methods and properties

Methods introduced by the chapter:

| Member | Purpose | Important note |
|---|---|---|
| `read()` / `read(size)` | Read remaining text / bounded characters | Loads requested content |
| `readline()` | Read next line | `""` at EOF |
| `readlines()` | Read remaining lines into list | High memory for large files |
| `write(text)` | Write one string | Returns character count; no newline added |
| `writelines(items)` | Write strings back-to-back | No separators/newlines added |
| `seek(offset)` | Move cursor | In text mode, use `0` or saved `tell()` value |
| `tell()` | Get cursor marker | Treat text-mode result as opaque |
| `flush()` | Flush Python buffer to OS | Not a physical durability guarantee |
| `close()` | Close and release resources | Use `with` instead |
| `readable()` | Whether mode supports reading | Does not mean content exists |
| `writable()` | Whether mode supports writing | Does not mean writing will succeed |
| `seekable()` | Whether cursor repositioning is supported | Not all streams are seekable |
| `fileno()` | Low-level OS descriptor number | Advanced; not every file-like object has one |

Example:

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    print(f.readable())  # True
    print(f.writable())  # False
    print(f.seekable())  # True
```

Properties:

- `f.name`: path/name used to open the file.
- `f.mode`: mode string, e.g. `"r"`.
- `f.closed`: `False` while open, `True` after closure.
- `f.fileno()`: low-level OS descriptor, included for recognition only.

## 19. OS architecture behind file I/O

```text
Python code
    ↓
Python file object
    ↓
Python I/O layer (buffering, encoding/decoding)
    ↓
operating system (system calls)
    ↓
filesystem
    ↓
physical storage
```

The file object tracks mode and cursor. Python's I/O layer handles text translation and buffering. The OS performs system calls and enforces access controls. The filesystem tracks file organization and permissions. Physical storage holds the bytes.

This explains why:
- opening reserves an OS resource and closing releases it;
- buffering reduces expensive trips through the layers;
- `PermissionError` is an OS/filesystem access issue;
- `UnicodeDecodeError` is a Python text-decoding issue.

## 20. Common mistakes to avoid

1. Forgetting to close a file — use `with`.
2. Manually opening/closing without `finally` or a context manager — exceptions can skip `close()`.
3. Typing `"w"` instead of `"r"` or `"a"` — existing data is erased immediately.
4. Treating `read()` as a list of lines — it returns one string; use file iteration for lines.
5. Assuming `writelines()` inserts newlines — it does not.
6. Reading twice without resetting the cursor — use `seek(0)` when needed.
7. Loading a huge file with `readlines()` — stream line by line.
8. Omitting encoding — explicitly specify the known encoding.
9. Catching every exception — catch only expected, specific failures.
10. Silently ignoring file errors — communicate fallback and cause.
11. Mixing I/O and business logic — separate read, pure transform, and write.
12. Writing output before processing/validation is complete — avoid partial output caused by processing failure.
13. Using `line[:-1]` to remove a newline — the final line may not have one; use `rstrip("\n")`.
14. Opening/closing inside a tight loop — open once and write many times.
15. Ignoring the exception message — inspect and report the actual message.

## 21. Debugging workflow

Use this repeatable sequence:

1. Identify the exact failing operation and line.
2. Print the exact path and current working directory (`os.getcwd()`).
3. Check `os.path.exists(path)`.
4. Check `os.path.isfile(path)` and `os.path.isdir(path)`.
5. Verify the mode string, especially `"w"` versus `"r"`/`"a"`.
6. Verify the file's actual encoding.
7. Check OS permissions.
8. If a read is unexpectedly empty, inspect `f.tell()`.
9. Read the complete traceback and exact exception message.
10. Reproduce with a tiny, known two- or three-line file.
11. Change one variable at a time.
12. Verify the fix and document the root cause.

The debugging loop is:

```text
Goal → assumptions → smallest experiment → observe → explain
     → change one variable → verify → document
```

If a read unexpectedly returns `""`, check whether the cursor is already at EOF. If only certain files raise `UnicodeDecodeError`, compare their actual source encoding with the encoding supplied to `open()`.

## 22. Testing with temporary files

Never let filesystem tests modify real project data. Use pytest's `tmp_path` fixture to get a fresh temporary directory for each test; pytest cleans it up.

Examples from the chapter:

```python
def test_write_text_file_then_read_it_back(tmp_path):
    file_path = tmp_path / "output.txt"
    write_text_file(str(file_path), "Hello, test!")
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == "Hello, test!"
```

Append and overwrite tests check the exact resulting text. `file_path.touch()` creates an empty file. `pytest.raises(FileNotFoundError)` verifies that a missing-file error is propagated. The lesson also demonstrates a wrong-encoding test, a line-filtering test, and a 5,000-line generated-file count test.

The key testing habits are: isolate tests in temporary locations, check exact outputs, cover normal and edge cases, and test expected failures explicitly. The full pytest framework is taught later; this chapter uses only the basic patterns needed here.

## 23. Separating I/O from domain logic

The lesson's bad example places opening, error handling, filtering, transforming, writing, and user reporting in one function. That makes the function hard to test and reuse.

The improved shape has:
- `read_text_file(path)` — I/O, returns text.
- `process_text(text)` — pure transformation, returns transformed text.
- `write_text_file(path, content)` — I/O.
- `run(input_path, output_path)` — coordinates the steps.

The sample transformation uses `splitlines()`, strips lines, uppercases non-blank lines, and joins them with `"\n"`. It returns `""` for empty or all-blank input. The lesson checks this with plain `assert` statements:

```python
assert process_text("") == ""
assert process_text("  \n\n \t \n") == ""
assert process_text(" a \n\n b\n") == "A\nB\n"
```

This makes the transform independently testable without touching a file.

## 24. Real-world uses and production design

Text files remain useful in production:

- application logs and audit records;
- small configuration files;
- generated reports;
- data ingestion and ETL preprocessing;
- evaluation datasets and prompt templates;
- experiment outputs, metrics, and model artifacts;
- batch processing of large text records;
- command-line tools;
- debugging traces and captured output.

The same pattern underlies AI/ML data preparation, evaluation pipelines, LLM trace capture, and experiment artifacts. The chapter makes this conceptual connection; it does not introduce AI-specific libraries.

A reliable pipeline is:

```text
Input → Read → Validate → Transform → Write → Verify
```

Validate as soon as data crosses the boundary. For example, `load_records(path)` reads text, rejects empty/whitespace-only input with a clear `ValueError`, and returns a list of non-blank lines. Production code should fail clearly when assumptions are violated.

Other design qualities:
- memory awareness: stream large inputs;
- testability: test each stage independently;
- reproducibility: same input should yield the same output;
- separation of concerns: keep I/O, validation, transformation, and verification distinct;
- idempotency: repeated runs on the same input should ideally yield the same result, not append duplicate data accidentally.

For truly safe replacement, write to a temporary file, finish successfully, then replace the destination. This protects the original if the write fails. The implementation is deferred to the later safe-file-writes lesson.

## 25. Concurrency

Two individually correct programs can still corrupt shared output if they write to the same file simultaneously. Two `"w"` opens can truncate/overwrite one another. Concurrent appends can interleave pieces of different records on some systems/configurations.

A **race condition** occurs when correctness depends on unpredictable timing between independent operations. File locking is one class of mechanism that coordinates access, but implementation is outside this chapter.

Do not assume ordinary `"w"` or `"a"` mode is a concurrency-control mechanism.

## 26. Four mini-project briefs in the source

These are project specifications, not additional numbered progressive exercises.

1. **Basic Text File Reader:** read and print a file; count lines and words; gracefully handle a missing file. Test normal, empty, blank-only, and one-long-line inputs.
2. **Text File Transformer:** read an input file, remove blank lines/normalize a chosen issue, and write to a separate output file. Never modify the input. Test messy, already-clean, empty, and no-final-newline cases.
3. **Large Text File Analyzer:** stream line by line; count total and matching lines; calculate match percentage; write a report. Handle empty input without division by zero, one line, all matches, and no matches.
4. **Reliable Text Processing Utility:** implement reusable typed functions (`read_text_file`, `write_text_file`, `append_text_file`, `count_lines`, `find_lines_containing`); use context managers; document catch/propagate decisions; test success and failure cases; stream at least one function; separate I/O from processing.

---

# Part B — Roadmap and current-level assessment

## 1. Where this lesson fits

The retrieved roadmap places the lesson in:

```text
Stage 1 — Programming & Computational Thinking/
├── 00-Stage-1-Overview/
├── 01-Computational-Thinking-and-Program-Design/
├── 02-Python-Core-Language-and-Data-Types/
├── 03-Control-Flow-Functions-Scope-and-Errors/
├── 04-Problem-Solving-Collections-and-Algorithmic-Habits/
├── 05-Text-Files-Structured-Data-and-CLI-Programs/
│   ├── 01-reading-and-writing-text-files.md       ← current lesson
│   ├── 02-pathlib-and-portable-paths.md
│   ├── 03-csv-files.md
│   ├── 04-json-and-serialization.md
│   ├── 05-encodings-and-newlines.md
│   ├── 06-command-line-arguments-with-argparse.md
│   ├── 07-standard-streams-and-exit-codes.md
│   ├── 08-logging-versus-print.md
│   ├── 09-environment-configuration-and-input-validation.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Modules-Packages-Dependencies-and-Code-Quality/
├── 07-Testing-and-Systematic-Debugging/
└── 08-Object-Oriented-Design-Data-Modelling-and-Functional-Style/
```

Stage 1's broader roadmap contains 24 modules, 212 numbered lessons, and four stage-level projects. The four projects are: Personal Expense Ledger CLI; Log Investigation and Reliability CLI; Data Quality and Transformation Pipeline; Rule-Based Risk Review Engine.

## 2. Your current learning level

Your recorded progress shows that you have worked through:

- Python fundamentals, strings, lists, tuples, dictionaries, sets, conversion, mutability, and immutability.
- Conditionals, guards, loops, `break`, and `continue`.
- Functions, parameters, return values, defaults, keyword-only arguments, and docstrings.
- Scope, lifetime, global state, pure functions, and side effects.
- Exceptions, validation, and useful error messages.
- Searching, counting, filtering, mapping, aggregation, grouping, deduplication, and sorting.
- Big-O, data-structure selection, comprehensions, recursion, parsing, and regular expressions.
- Module 03 and Module 04 practice problems.

**Assessment: beginner progressing toward intermediate.** You are not starting from zero: the concepts needed for this file lesson—loops, strings, collections, functions, type hints, and specific exception handling—are already part of your studied foundation. The new subject is filesystem interaction: paths, file objects, modes, cursors, encoding, context managers, and safe persistence.

The roadmap lists later Module 05 lessons and Module 07 testing as planned curriculum; that does not mean they are already completed. The solutions below therefore use the current lesson's file APIs and previously learned Python constructs. Basic `tmp_path`/`pytest.raises` syntax is used only where the source exercise explicitly asks for it; no advanced pytest features are assumed.

---

# Part C — All 21 progressive exercises solved

All examples use a disposable directory named `practice_files`. Run the setup once, then use the paths shown. Do not point these exercises at important personal or project files.

```python
import os

os.makedirs("practice_files", exist_ok=True)
```

## Level 1 — Beginner

### Exercise 1 — Create a file with three lines in one `write()`

```python
lines = ["First line", "Second line", "Third line"]
content = "\n".join(lines)

with open("practice_files/three_lines.txt", "w", encoding="utf-8") as f:
    f.write(content)
```

- Line 1 creates a list containing the three desired lines.
- Line 2 joins them using `"\n"` between each pair.
- The `with` statement opens the practice file in `"w"` mode and UTF-8 text mode.
- `f.write(content)` writes the complete string in one call.
- `join()` does not add a newline after `"Third line"`; that is acceptable because the requirement says exactly three lines, not a trailing newline.

### Exercise 2 — Read and print the complete file

```python
with open("practice_files/three_lines.txt", "r", encoding="utf-8") as f:
    content = f.read()

print(content)
```

- `"r"` opens the existing file without changing it.
- `f.read()` returns the remaining file content as one string.
- The `with` block closes the file.
- `print()` displays the three lines. It is separate from reading.

### Exercise 3 — Append a fourth line safely

```python
with open("practice_files/three_lines.txt", "a", encoding="utf-8") as f:
    f.write("\nFourth line")
```

- `"a"` preserves the first three lines and writes at the end.
- The original file has no final newline because Exercise 1 used `"\n".join(...)`.
- Therefore the appended string begins with `"\n"` to separate the fourth line.
- Running this exact append code twice creates two appended entries; the file then has five lines, with the fourth and fifth lines both reading `"Fourth line"`.

### Exercise 4 — Count lines by iteration, including an empty file

```python
def count_lines(path: str) -> int:
    total = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            total += 1
    return total

print(count_lines("practice_files/three_lines.txt"))
```

- `total` starts at zero.
- The file is opened once in read mode.
- Each iteration yields one line, so incrementing `total` counts lines.
- An empty file yields no iterations and returns `0`.
- This does not use `readlines()` and therefore does not load all lines into memory.

### Exercise 5 — Count whitespace-separated words

```python
def count_words(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return len(text.split())

print(count_words("practice_files/three_lines.txt"))
```

- The function opens the file and reads its text.
- `split()` without an argument separates on whitespace and ignores repeated spaces/newlines at the edges.
- `len()` counts the resulting tokens.
- A whitespace-only file produces an empty list from `split()`, so the answer is `0`.
- This definition follows the exercise: a word is a whitespace-delimited token.

### Exercise 6 — Print each line without its trailing newline

```python
with open("practice_files/three_lines.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.rstrip("\n"))
```

- The loop reads one line at a time.
- `rstrip("\n")` removes only trailing newline characters.
- Unlike `strip()`, it preserves meaningful leading/trailing spaces.
- It also works when the final line has no newline; it does not delete its last real character.

## Level 2 — Intermediate

### Exercise 7 — Filter lines by keyword without retaining non-matches

```python
def filter_lines(path: str, keyword: str) -> list[str]:
    matches = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if keyword in line:
                matches.append(line.rstrip("\n"))
    return matches

print(filter_lines("practice_files/app.log", "ERROR"))
```

- `matches` stores only lines that satisfy the condition.
- The file is streamed line by line.
- The `if` checks whether the keyword occurs in the current line.
- Only matching lines are appended; non-matching lines are not stored in the result.
- `rstrip("\n")` returns the matched text without its line terminator.
- Replace the example path with a practice file you create.

### Exercise 8 — Reverse characters within each line

```python
def reverse_each_line(path: str) -> list[str]:
    reversed_lines = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            clean_line = line.rstrip("\n")
            reversed_lines.append(clean_line[::-1])
    return reversed_lines
```

- The result list stores transformed lines.
- Iteration reads one line at a time.
- `rstrip("\n")` removes the line terminator but preserves spaces.
- `[::-1]` reverses the characters in that line.
- Each reversed line is appended in the original line order.
- A blank line becomes an empty string; it does not crash or disappear.

### Exercise 9 — Combine several input files in order

This implementation chooses an all-or-nothing **processing policy**: read all inputs successfully before opening the output. If any input is missing, the output is not opened or truncated.

```python
def combine_files(paths: list[str], output_path: str) -> None:
    combined_parts = []

    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            combined_parts.append(f.read())

    combined_text = "".join(combined_parts)

    with open(output_path, "w", encoding="utf-8") as output:
        output.write(combined_text)
```

- `combined_parts` collects each complete input string in the supplied order.
- The loop opens and reads each input file.
- If an input is missing, `FileNotFoundError` propagates before the output is opened.
- `join()` combines the parts without inventing separators. If separate files need line breaks between them, the input files or explicit joining rule must provide them.
- Only after every read succeeds does `"w"` open the output.
- A failure during the final write can still leave partial output; this is not atomic replacement.

### Exercise 10 — Create a line/word/character summary

```python
def create_summary(input_path: str, output_path: str) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    line_count = len(text.splitlines())
    word_count = len(text.split())
    character_count = len(text)

    summary = (
        f"Lines: {line_count}\n"
        f"Words: {word_count}\n"
        f"Characters: {character_count}\n"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)
```

- Read the input once into `text` (appropriate for a small practice file).
- `splitlines()` counts logical lines without retaining newline characters.
- `split()` counts whitespace-separated words.
- `len(text)` counts Python string characters, including spaces and newline characters.
- The formatted summary puts each statistic on its own line.
- The output is written to a separate path so the input remains untouched.
- For a large file, this whole-file approach would need to be redesigned as a streaming counter.

### Exercise 11 — Return a default for missing files, propagate other errors

```python
def read_or_default(path: str, default: str = "") -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return default
```

- `default` is the fallback value and defaults to an empty string.
- The function tries to open and read the requested file.
- Only `FileNotFoundError` is caught.
- A missing file returns the caller's chosen default.
- `PermissionError`, `UnicodeDecodeError`, and other exceptions are not caught; they propagate to the caller as required.

### Exercise 12 — Check empty-file behavior

Use the same functions from Exercises 4–7 and 10 against an empty file:

```python
empty_path = "practice_files/empty.txt"

with open(empty_path, "w", encoding="utf-8") as f:
    pass

print(count_lines(empty_path))             # 0
print(count_words(empty_path))             # 0
print(filter_lines(empty_path, "ERROR"))   # []
```

- Opening in `"w"` creates/truncates the disposable practice file.
- The `pass` statement intentionally writes nothing.
- Line counting returns `0` because the loop has no iterations.
- Word counting returns `0` because `split()` returns `[]`.
- Filtering returns `[]` because no line matches.
- The same principle applies to printing lines (prints nothing) and summary generation (reports zero counts).

### Exercise 13 — Reuse the §23 helper functions

First define the common helpers:

```python
def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
```

Then rewrite filtering, line reversal, combining, and summary generation to call these helpers:

```python
def filter_text_file(input_path: str, output_path: str, keyword: str) -> None:
    text = read_text_file(input_path)
    kept = [line for line in text.splitlines() if keyword in line]
    write_text_file(output_path, "\n".join(kept))


def reverse_text_file(input_path: str, output_path: str) -> None:
    text = read_text_file(input_path)
    reversed_lines = [line[::-1] for line in text.splitlines()]
    write_text_file(output_path, "\n".join(reversed_lines))


def combine_text_files(paths: list[str], output_path: str) -> None:
    parts = [read_text_file(path) for path in paths]
    write_text_file(output_path, "".join(parts))


def summary_text_file(input_path: str, output_path: str) -> None:
    text = read_text_file(input_path)
    summary = (
        f"Lines: {len(text.splitlines())}\n"
        f"Words: {len(text.split())}\n"
        f"Characters: {len(text)}\n"
    )
    write_text_file(output_path, summary)
```

- The helpers own file opening/closing and encoding.
- The other functions focus on the transformation and coordination.
- `splitlines()` removes line terminators before filtering/reversing; `join()` rebuilds line separators.
- These versions are concise and suitable for small files. They load the whole input; use streaming for large inputs.
- The combination function preserves the exact text of each file and adds no extra separator.

## Level 3 — Advanced within this chapter

### Exercise 14 — Stream at least 100,000 lines and find the longest

```python
def longest_line(path: str) -> str:
    longest = ""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            candidate = line.rstrip("\n")
            if len(candidate) > len(longest):
                longest = candidate
    return longest
```

- Only one line is read at a time.
- `candidate` removes the trailing newline so it is not counted as part of the line content.
- Compare its length with the current longest line.
- Replace `longest` only when a longer line appears.
- Memory remains bounded by the current line plus the longest line, not the whole file.
- Generate a 100,000-line test file separately; the function itself works the same way for any size.

### Exercise 15 — Count characters with chunked `read(size)`

```python
def count_characters_in_chunks(path: str, chunk_size: int = 8192) -> int:
    total = 0
    with open(path, "r", encoding="utf-8") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            total += len(chunk)
    return total
```

- `total` accumulates the number of characters.
- `read(chunk_size)` reads at most that many text characters.
- An empty string means EOF, so the loop stops.
- `len(chunk)` counts the characters in the current chunk.
- The function never calls unbounded `read()` and never iterates by lines.
- Only one chunk is held at a time.

### Exercise 16 — Avoid partial output if processing fails

```python
def write_processed_records(records: list[str], output_path: str) -> None:
    processed_lines = []

    for record in records:
        processed_lines.append(record.strip().upper() + "\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(processed_lines)
```

- Build every transformed record before opening the destination.
- If transformation raises, the output file has not yet been opened or truncated.
- Once processing completes, open the output once and write all prepared lines.
- This protects against **processing** errors only. A disk/write failure after opening can still leave a partial file.
- The source's true all-or-nothing solution is a temporary file followed by replacement, taught later.

### Exercise 17 — Test relevant exceptions and document the policy

For `read_or_default()` from Exercise 11, the policy is: catch `FileNotFoundError` only; allow other file errors to propagate.

```python
import pytest


def test_missing_file_uses_default(tmp_path):
    missing_path = tmp_path / "missing.txt"
    assert read_or_default(str(missing_path), "DEFAULT") == "DEFAULT"


def test_directory_path_error_propagates(tmp_path):
    with pytest.raises(IsADirectoryError):
        read_or_default(str(tmp_path))


def test_not_a_directory_error_propagates(tmp_path):
    file_path = tmp_path / "ordinary.txt"
    write_text_file(str(file_path), "content")
    child_path = file_path / "child.txt"

    with pytest.raises(NotADirectoryError):
        read_or_default(str(child_path))


def test_decode_error_propagates(tmp_path):
    path = tmp_path / "utf8.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("café")

    with pytest.raises(UnicodeDecodeError):
        with open(path, "r", encoding="ascii") as f:
            f.read()
```

- The first test confirms that a missing file returns the requested default.
- The directory tests show that path-type errors are not mistaken for a missing file.
- The decoding test writes UTF-8 content and then reads it as ASCII, which raises `UnicodeDecodeError`.
- `pytest.raises(...)` asserts that the specified exception occurs.
- `PermissionError` and other low-level `OSError` cases should also propagate. Reproducing a permission denial reliably depends on the operating system and account permissions, so document the expected behavior and test it only in an environment where access can genuinely be denied.
- The important contract is that the helper catches one specific expected condition and does not hide unrelated failures.

### Exercise 18 — Separate I/O from domain logic

```python
def clean_text(text: str) -> str:
    lines = text.splitlines()
    cleaned = [line.strip().upper() for line in lines if line.strip()]
    if not cleaned:
        return ""
    return "\n".join(cleaned) + "\n"


def clean_file(input_path: str, output_path: str) -> None:
    original = read_text_file(input_path)
    cleaned = clean_text(original)
    write_text_file(output_path, cleaned)
```

- `clean_text()` receives only a string and returns a string.
- It removes blank lines, trims each retained line, and uppercases it.
- The pure function does not open files or print anything.
- `clean_file()` coordinates I/O by calling the reader, transformation, and writer in order.
- Test `clean_text()` directly with ordinary strings; no filesystem setup is needed.

### Exercise 19 — Basic pytest tests for Levels 1, 2, and 3

The following is a compact test suite using the chapter's `tmp_path` and `pytest.raises` patterns:

```python
import pytest


def test_count_lines(tmp_path):
    path = tmp_path / "lines.txt"
    write_text_file(str(path), "one\ntwo\n")
    assert count_lines(str(path)) == 2


def test_filter_lines(tmp_path):
    path = tmp_path / "log.txt"
    write_text_file(str(path), "OK\nERROR: disk\nOK\n")
    assert filter_lines(str(path), "ERROR") == ["ERROR: disk"]


def test_chunk_character_count(tmp_path):
    path = tmp_path / "text.txt"
    write_text_file(str(path), "abcdefghij")
    assert count_characters_in_chunks(str(path), chunk_size=3) == 10


def test_missing_file_raises_from_reader(tmp_path):
    path = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        read_text_file(str(path))
```

- The first test checks a beginner-level line counter.
- The second tests an intermediate filtering function.
- The third tests an advanced chunked reader using a chunk size of three.
- The fourth verifies the low-level reader propagates `FileNotFoundError`.
- `tmp_path` keeps test data outside your real project and cleans it up after the test.

### Exercise 20 — Replace `readlines()` on a huge file with streaming

**Broken version:**

```python
with open("huge_log.txt", "r", encoding="utf-8") as f:
    all_lines = f.readlines()
```

This loads the entire file into memory as a list of strings. A sufficiently large file can consume excessive RAM.

**Memory-safe version:**

```python
error_count = 0

with open("huge_log.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "ERROR" in line:
            error_count += 1

print(error_count)
```

- Start a counter at zero.
- Read one line per iteration.
- Increment only when the line contains `"ERROR"`.
- Discard each line after processing.
- The program does not retain all lines, so memory use stays bounded by the current line and small program state.

### Exercise 21 — Design the reliable text-processing utility

A compact implementation of the required functions:

```python
def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def append_text_file(path: str, content: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)


def count_lines(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def find_lines_containing(path: str, keyword: str) -> list[str]:
    matches = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if keyword in line:
                matches.append(line.rstrip("\n"))
    return matches
```

- Each function has one responsibility and a type hint.
- Each function that opens a file uses `with`.
- Each function specifies UTF-8.
- `count_lines()` and `find_lines_containing()` stream line by line.
- These low-level helpers let file errors propagate. The caller decides whether a missing file should be reported, retried, or replaced by a default.
- A complete project submission should add tests for normal reads/writes/appends, missing files, empty files, and malformed/unreadable text; document the error policy; and include a short usage explanation.
- The implementation is intentionally not presented as a complete production package: atomic replacement, path abstraction, CLI, logging, and advanced test organization belong to later lessons.

---

# Part D — Knowledge check answer key (all 18)

1. **Why does file I/O exist?** To move data between a running program and persistent external storage, so data can survive program termination and be exchanged with other systems.
2. **Why doesn't `open()` load content?** It establishes an open connection and returns a file object. A read method is required to transfer content into Python memory.
3. **What does the three-write example print?** `onetwothree` on one line. Each `write()` continues at the cursor and none includes `\n`.
4. **What does the two-`readline()` example print?** It prints `line1` and `line2`, each followed by a newline; `print()` adds its own newline too, so blank display spacing appears between the printed lines.
5. **Missing file with modes:** `"r"` raises `FileNotFoundError`; `"w"` creates an empty file; `"x"` creates it if absent (and raises `FileExistsError` if it exists).
6. **Why do two `"w"` opens not raise?** `"w"` is defined to create or truncate; `"x"` specifically refuses to open an existing file.
7. **After reading a 20-character file fully:** `tell()` reports the end position marker (do not treat it as a portable text character count); another `read()` returns `""`.
8. **What does `seek(0)` do?** Resets the cursor to the start, allowing the file to be read again.
9. **Missing read-mode file exception:** `FileNotFoundError`.
10. **Should low-level `read_text_file()` catch missing-file errors?** Usually not. It is a reusable primitive and does not know the caller's recovery policy. Let the exception propagate so the caller can decide.
11. **Why is iteration more memory-efficient than `readlines()`?** Iteration yields one line at a time; `readlines()` retains every line in a list.
12. **Why avoid repeated open/close in a loop?** Each operation incurs OS/resource overhead. Open once around the loop when writing many records to the same file.
13. **First check for `UnicodeDecodeError` on only some files:** verify those files' actual encoding against the encoding supplied to `open()`.
14. **Counter returns zero unexpectedly:** reproduce with a tiny known file; verify path and content; inspect `f.tell()` before reading; ensure no earlier read consumed the cursor; then verify the loop/count condition one variable at a time.
15. **Memory-bounded `last_line(path)`:**

```python
def last_line(path: str) -> str:
    last = ""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            last = line.rstrip("\n")
    return last
```

The loop retains only the latest line, so it does not load the entire file. Empty file returns `""`.

16. **Check whether a file has zero characters without reading it all:**

```python
def is_empty_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        return f.read(1) == ""
```

Read at most one character. If that returns `""`, EOF was reached immediately.

17. **Separate I/O from summarizing:** read the file in an I/O function, pass the resulting string/lines to a pure summary function, then write the report in another I/O function. Benefit: test the summary logic with an in-memory string, without creating a file.
18. **Concurrent appends:** records may interleave or become mixed depending on timing/system behavior. Do not assume append mode alone guarantees atomic, coordinated multi-process writes.

---

# Final revision sheet

- **Default safe open:** `with open(path, "r", encoding="utf-8") as f:`
- **Read small file:** `f.read()`
- **Read one line:** `f.readline()`
- **Read all lines into a list:** `f.readlines()` — only for manageable files.
- **Stream lines:** `for line in f:`
- **Read bounded text:** `f.read(size)`
- **Reset cursor:** `f.seek(0)`
- **Inspect cursor:** `f.tell()` (opaque marker in text mode).
- **Write fresh:** `"w"` — truncates existing content.
- **Append:** `"a"` — preserves old content, writes at end.
- **Create only if absent:** `"x"`.
- **Write multiple strings:** `writelines()` — does not add newlines.
- **Close safely:** use `with`, not manual close.
- **Encoding:** explicitly specify the known encoding, commonly UTF-8.
- **Large line-oriented files:** iterate line by line.
- **Large non-line-oriented files:** read bounded chunks and handle chunk boundaries.
- **Error policy:** catch specific expected operational errors; let programming bugs and unhandled failures surface.
- **Safe transformation:** preserve input, write to a separate output, verify the result.
- **Architecture:** read → validate → transform → write → verify.
- **Tests:** use temporary files/directories, not real project data.
- **Debugging:** inspect the exact path, working directory, mode, encoding, cursor, and traceback; reproduce with the smallest input.

## Completion checklist

- [ ] I can explain files, persistence, and file I/O.
- [ ] I can distinguish text from binary files.
- [ ] I understand paths, `open()`, and file objects.
- [ ] I can predict `r`, `w`, `a`, `x`, and recognize `+`/`b` variants.
- [ ] I can use `read`, `readline`, `readlines`, and iteration correctly.
- [ ] I understand EOF, the cursor, `tell()`, and `seek()`.
- [ ] I know that `write()` and `writelines()` never add newlines automatically.
- [ ] I use context managers and explicit encodings.
- [ ] I can distinguish expected operational errors from programmer bugs.
- [ ] I can preserve input data and avoid partial output from processing failures.
- [ ] I can stream large files or process bounded chunks.
- [ ] I understand buffering and the limits of `flush()`.
- [ ] I can write reusable typed file helpers and separate I/O from logic.
- [ ] I can test with temporary files and debug failures systematically.
- [ ] I understand why concurrent writers require coordination.

**Next lesson in the roadmap:** `02-pathlib-and-portable-paths.md`. This guide intentionally stops at string paths and the text-file operations covered here.
