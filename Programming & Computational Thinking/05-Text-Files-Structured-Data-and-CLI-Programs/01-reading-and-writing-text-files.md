Reading and Writing Text Files
===============================

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what a file is, what file I/O is, and why it exists as a
  distinct category from ordinary in-memory computation.
- Explain the relationship between a path, `open()`, and a Python file
  object, and why the file object is not the file itself.
- Use `open()` correctly, including choosing the right mode and
  explicitly specifying encoding.
- Explain every core file mode (`r`, `w`, `a`, `x`, and their `+`/`b`
  variants) and predict exactly what happens when a file does or does
  not already exist.
- Read text safely using `read()`, `read(size)`, `readline()`,
  `readlines()`, and direct iteration — and choose correctly among them
  for a given situation.
- Understand the file cursor, and use `tell()` and `seek()` correctly.
- Write and append text safely, understanding exactly when newlines are
  and are not added automatically.
- Explain why context managers (`with open(...) as f:`) are the
  standard, correct way to handle files, including under exceptions.
- Recognize and handle the standard file-related exceptions, and
  distinguish an expected operational error from a genuine programmer
  bug.
- Process files that are too large to hold in memory, using streaming
  and chunked reads.
- Explain buffering and flushing at a conceptual, practically useful
  level.
- Separate file I/O from business/domain logic, and explain why that
  separation matters for testing, reuse, and maintainability.
- Test file-processing code using temporary files, without touching
  real project data.
- Debug file-I/O failures using a systematic, repeatable workflow.
- Design a small, reliable text-file processing utility from scratch.

## 2. Prerequisites

This chapter assumes you have already completed Stage 1's earlier
modules and are comfortable with:

- Variables, values, and expressions
  ([Values, Expressions, Statements, and Variables](../01-Computational-Thinking-and-Program-Design/02-values-expressions-statements-and-variables.md)).
- Strings, including indexing, slicing, and basic formatting
  ([Strings, Indexing, Slicing, and Formatting](../02-Python-Core-Language-and-Data-Types/04-strings-indexing-slicing-and-formatting.md)).
- Lists, tuples, dictionaries, and sets
  ([Lists](../02-Python-Core-Language-and-Data-Types/05-lists-mutation-copying-and-aliasing.md),
  [Tuples](../02-Python-Core-Language-and-Data-Types/06-tuples-and-unpacking.md),
  [Dictionaries](../02-Python-Core-Language-and-Data-Types/07-dictionaries-and-lookups.md),
  [Sets](../02-Python-Core-Language-and-Data-Types/08-sets-and-unique-values.md)).
- Conditionals and loops
  ([Conditionals, Guards, and Boolean Logic](../03-Control-Flow-Functions-Scope-and-Errors/01-conditionals-guards-and-boolean-logic.md),
  [For/While Loops and Loop Control](../03-Control-Flow-Functions-Scope-and-Errors/02-for-while-loops-and-loop-control.md)).
- Functions, parameters, return values, and scope
  ([Functions, Parameters, and Return Values](../03-Control-Flow-Functions-Scope-and-Errors/03-functions-parameters-and-return-values.md),
  [Scope, Lifetime, and Global State](../03-Control-Flow-Functions-Scope-and-Errors/05-scope-lifetime-and-global-state.md)).
- Exceptions, `try`/`except`, and writing useful errors
  ([Exceptions, Validation, and Useful Errors](../03-Control-Flow-Functions-Scope-and-Errors/07-exceptions-validation-and-useful-errors.md)).
- Basic type hints on function signatures
  (introduced across Modules 1.2–1.3).
- Basic, systematic debugging habits — forming a hypothesis, running the
  smallest possible experiment, and checking it, rather than guessing.

**You are not assumed to know anything about files yet.** Every file-
specific concept in this chapter — `open()`, file objects, modes,
cursors, context managers, encoding — is explained from first
principles, starting from "what is a file" and building upward.

## 3. Why Text-File I/O Matters

Every program you have written so far has had exactly one weakness:
the moment it finished running, everything it had computed disappeared.
This module's stated outcome is *"you can build reliable small tools
that process real files and communicate clearly through a CLI"* — and
that begins here, with the single most fundamental way a program
reaches outside itself: reading and writing plain text files.

This chapter is also where an important engineering mindset first
becomes necessary, one that will recur throughout this entire module and
the rest of the roadmap: **files, command-line arguments, environment
variables, and JSON are all untrusted input.** They come from outside
your program's control — a file might not exist, might be empty, might
be enormous, might be encoded differently than you expect, might be
missing permissions, or might simply have been edited by someone (or
something) you never anticipated. The correct engineering response is
not to hope nothing goes wrong. It is to build code around three
deliberate stages:

```
validate at the boundary  →  transform into a reliable internal representation  →  process
```

**Validate at the boundary** means checking assumptions (does the file
exist? can it be opened? is it readable text?) at the exact point where
outside data first enters your program — not several function calls
later. **Transform into a reliable internal representation** means
converting raw file content into ordinary, well-understood Python data
(strings, lists of strings) as early as possible, so that the rest of
your program never has to think about files again. **Process** means
your actual logic — filtering, counting, transforming — operates
entirely on that already-validated, already-in-memory data. This
chapter builds the mechanical skills (`open()`, reading, writing,
context managers, error handling) that make this boundary-first
discipline possible, and the design habits (§23, §40) that make it your
default, not an afterthought.

## 4. What Is a File?

### 4.1 A real-world analogy first

A thought in your head is fast to have and fast to change, but the
moment you stop thinking about it, it can be gone entirely. A notebook
on your desk is slower to write in and slower to read from, but it is
still there tomorrow, whether or not you are thinking about it right
now. A **variable** in a running Python program is the thought. A
**file** is the notebook.

### 4.2 File vs. variable vs. memory vs. database

| | Variable / memory | File | Database |
|---|---|---|---|
| **Lifetime** | Only while the program runs | Survives after the program ends | Survives after the program ends |
| **Speed** | Extremely fast (RAM) | Much slower (disk I/O, §4.7) | Slower than memory, usually faster than raw files for querying |
| **Structure** | Whatever Python objects you built | Raw bytes/text — you define the structure | Enforced schema, with built-in query support |
| **Shared across programs?** | No | Yes — other programs can open and change it | Yes, with real concurrency support |
| **When to reach for it** | Temporary computation | Simple persistence, logs, config, exchanging data between programs | Structured, queryable, concurrent, large-scale data |

Databases are a much later topic in this roadmap. For now, a file is
the simplest possible form of **persistent data**: data that survives
after the variable that would normally hold it disappears.

### 4.3 Persistent vs. in-memory (temporary) data

Every variable you have written holds **in-memory** (or *volatile*)
data — it lives in RAM, and RAM is wiped the instant your program (or
your computer) stops running. A file holds **persistent** data — it
lives on disk, which is specifically built to keep its contents with no
power at all. This is the entire reason file I/O exists: **programs
need a way to remember things between runs, and to exchange information
with other programs, humans, and systems.**

### 4.4 What "file I/O" means

**I/O** stands for **Input/Output** — any exchange of data between your
program and something *outside* it. Reading a file is **input** (data
flows from the file into your program); writing a file is **output**
(data flows from your program into the file). §6 develops this fully.

### 4.5 Connecting to Stage 0: program, operating system, filesystem, storage

You already know, at a Stage 0 level, that a running program does not
touch physical hardware directly — it asks the **operating system** to
do so on its behalf. File access is exactly this pattern applied to
storage:

```
your Python program → operating system → filesystem → physical storage
```

This chapter does not re-teach that architecture in full — it only
uses it as the backdrop for why file operations behave the way they do
(§7 makes this concrete for Python specifically; §36 revisits the full
picture once you have the vocabulary to appreciate it).

### 4.6 What a text file is, at a first pass

A **text file** is a file whose bytes are meant to be interpreted as
human-readable characters — letters, digits, punctuation, whitespace.
Open one in a plain text editor, and it looks like readable text:
`.txt`, `.py`, `.md`, `.csv`, `.log`. §5 develops the text-vs-binary
distinction fully; this chapter is about text files only.

### 4.7 Why file I/O is slower than in-memory operations

Reading or writing a variable means talking directly to RAM, built for
extreme speed. Reading or writing a file means asking the operating
system to talk to a physical storage device on your behalf — a round
trip that, even on a fast modern SSD, is dramatically slower than
touching RAM directly, often by a factor of thousands. This is not a
Python limitation; it reflects real hardware, in every language.
**Practical consequence:** file I/O is something you do deliberately,
not casually inside a tight loop (§37 mistake 14 returns to this
directly).

### 4.8 Why file operations can fail

`2 + 2` cannot meaningfully fail. A file operation can, because it
depends on things entirely outside your program's control: does the
file exist? does your program have permission? is there disk space? is
another program holding it open? This is precisely why §27 (error
handling) and §29 (safe file handling) are treated as first-class
material in this chapter, not an afterthought.

## 5. Text Files vs Binary Files

### 5.1 Characters and bytes

A **character** is a single unit of human-readable text — a letter, a
digit, an emoji. A **byte** is one small unit of raw storage — the
actual physical unit a computer stores and moves. Every file, at the
hardware level, is just a sequence of bytes; the difference between
file *types* is entirely about how those bytes are meant to be
**interpreted**.

### 5.2 Text files

A text file's bytes are meant to represent characters, according to a
translation rule called an **encoding** (§25 introduces this properly).
Typical text files: `.txt`, `.log`, `.csv`, `.py`, `.json`, `.md`.

### 5.3 Binary files

A binary file's bytes are meant for something other than direct
character-by-character reading — an image's pixel data, an audio
waveform, a compiled program. Open one in a plain text editor and you
get unreadable, garbled symbols, because the bytes were never meant to
be read as characters. Typical binary files: `.jpg`, `.png`, `.pdf`,
`.zip`.

### 5.4 Why Python has separate text and binary modes

Because the *meaning* of the same underlying bytes is completely
different between the two cases, Python's `open()` needs to know, up
front, which interpretation to apply: text mode (`"t"`, the default)
automatically decodes bytes into Python `str` characters as you read,
and encodes `str` back into bytes as you write, using the encoding you
specify (§25). Binary mode (`"b"`) skips this translation entirely,
handing you raw `bytes` objects instead. **This chapter focuses
entirely on text mode** — binary mode is mentioned only in §9's mode
table for completeness and recognition; working with genuinely binary
data (images, PDFs, compressed archives) is a separate, later skill,
outside this chapter's scope.

## 6. What Is File I/O?

### 6.1 Input and output, restated precisely for files

- **Read operation** — data flows from the file, on disk, into your
  program, as Python `str` values.
- **Write operation** — data flows from your program, as Python `str`
  values, out to the file on disk.
- **Append operation** — a specific kind of write that adds new data
  after whatever the file already contains, rather than replacing it
  (§19 develops this fully).

### 6.2 The basic lifecycle: open → use → close

Every file interaction in this chapter follows the same shape:

1. **Open** the file — tell the operating system which file, and what
   you intend to do with it (§8, §9).
2. **Use** it — one or more read or write operations (§12–§18).
3. **Close** it — release the connection and the resources behind it
   (§20), ideally using a context manager (§21) rather than closing
   manually.

### 6.3 Why the operating system treats file access as a resource

Every operating system enforces a limit on how many files can be open
*simultaneously* by a single program — because keeping a file open
consumes real, finite bookkeeping resources (memory for tracking the
open connection, and a slot in a system-wide table of open files). This
is exactly why "close what you open" is not merely tidy style — it is
returning a limited, shared resource, exactly as returning a borrowed
tool to a shared toolbox lets someone else use it next. §20 and §36
return to this directly.

## 7. Python File Objects

### 7.1 The chain of responsibility

```
your program → open() → file object → Python I/O layer → operating system → filesystem
```

You never talk to the disk directly. You call Python's built-in
`open()`, which asks the operating system to open the file on your
behalf, and hands you back a **file object** — your program's remote
control for that open file.

### 7.2 A file object is not the file itself

This distinction is critical, and worth stating explicitly:

- A **path** (a string like `"notes.txt"`, or later a `Path` object,
  §24) *identifies a location* — it is just data, and it exists whether
  or not anything is currently reading it.
- A **file object** *represents an open connection* to whatever is at
  that location — it has state (a cursor position, §16; whether it is
  open or closed, §35), and it provides the operations (`read()`,
  `write()`, `seek()`, and the rest of §34) that actually touch the
  file's content.

```python
path = "greeting.txt"            # just a string -- a location, nothing more
f = open(path, "r", encoding="utf-8")   # an open connection to that location
print(type(path))   # <class 'str'>
print(type(f))       # <class '_io.TextIOWrapper'>
f.close()
```

```text
<class 'str'>
<class '_io.TextIOWrapper'>
```

### 7.3 Opening a file does not load its contents

`open()` only establishes the connection — it locates the file, checks
that the requested operation is currently possible (§10), and returns a
file object positioned at the very start. **No content is loaded into
memory until you explicitly call a reading method** (§11–§15). This is
the conceptual foundation for §30: opening a 10 GB file is cheap;
*reading all of it with `read()`* is what can be dangerous.

## 8. `open()`

### 8.1 The full signature

```python
open(file, mode='r', buffering=-1, encoding=None, errors=None,
     newline=None, closefd=True, opener=None)
```

`file` and `mode` are positional-or-keyword and used in nearly every
call; everything after them has a sensible default and is used only
occasionally. Each is explained below: what it means, why it exists,
when a beginner should actually care, an example, and any important
caveat.

### 8.2 `file`

**What it means:** the path to the file you want to open — a string
(or, once you reach [02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md),
a `Path` object; both work identically with `open()`).
**Why it exists:** `open()` needs to know *which* file, obviously.
**When to care:** always — this argument is mandatory.
**Example:** `open("notes.txt", "r", encoding="utf-8")`.
**Caveat:** a **relative** path (like `"notes.txt"`, with no leading
`/` or drive letter) is interpreted relative to your program's current
working directory — not necessarily the directory your script file
lives in. §38's debugging workflow lists confirming this as an early
step, precisely because it is a common source of `FileNotFoundError`.

### 8.3 `mode`

**What it means:** what you intend to do with the file — read, write,
append, and so on (§9 covers every mode in full).
**Why it exists:** the operating system needs to know your intent
*before* granting access, so it can prepare (or refuse) the correct
kind of access.
**When to care:** always — write it explicitly, every time, even though
it defaults to `"r"`, so the intent is visible to any reader of your
code.
**Example:** `open("notes.txt", "w", encoding="utf-8")`.
**Caveat:** getting this one character wrong is the single most
consequential file-handling mistake possible — §9.4 shows exactly why.

### 8.4 `buffering`

**What it means:** how aggressively Python batches your reads/writes
before actually touching the disk (§32 develops this fully).
**Why it exists:** to make repeated small operations dramatically
faster than touching disk on every single call.
**When to care:** almost never, as a beginner — the default (`-1`,
"choose automatically") is correct for nearly all code.
**Example:** `open("notes.txt", "w", encoding="utf-8", buffering=1)`
(line-buffered — flush after every newline).
**Caveat:** manually tuning this without first measuring a real
performance problem is premature optimization — §32.4 states this
directly.

### 8.5 `encoding`

**What it means:** the rule for translating between the file's raw
bytes and Python's `str` characters (§25 covers this fully).
**Why it exists:** text files are bytes on disk; something must define
how those bytes map to characters, and that mapping is not universal.
**When to care:** always — omitting it silently falls back to a
platform-dependent default, which can make identical code behave
differently on different machines.
**Example:** `open("notes.txt", "r", encoding="utf-8")`.
**Caveat:** `"utf-8"` is an excellent, very common choice, and the
right one whenever the file is known to be UTF-8 or you control the
format. The correct encoding ultimately depends on the actual file
you are reading, so use the encoding you know the data to have.

### 8.6 `errors`

**What it means:** what to do when a byte sequence cannot be decoded
under the chosen `encoding`.
**Why it exists:** real-world files occasionally contain bytes that do
not cleanly match the declared encoding; Python needs a policy for that
case.
**When to care:** occasionally — know that it exists and what the
default does.
**Example:**
```python
open("data.txt", "r", encoding="utf-8", errors="strict")   # default: raise UnicodeDecodeError immediately
open("data.txt", "r", encoding="utf-8", errors="replace")  # swap bad bytes for a placeholder character
```
**Caveat:** prefer letting the default `"strict"` behavior raise
`UnicodeDecodeError` (§27) and handling it deliberately, over silently
discarding or replacing bad data with `"ignore"`/`"replace"` as a quick
fix.

### 8.7 `newline`

**What it means:** how line-ending characters are translated between
what is on disk and what your code sees (fully covered in
[05-encodings-and-newlines.md](05-encodings-and-newlines.md)).
**Why it exists:** different operating systems have historically
disagreed about which exact byte sequence means "end of line" (§26).
**When to care:** rarely, as a beginner — the default (`None`, meaning
"universal newline translation") is correct for nearly all code you
will write in this chapter.
**Example:** `open("notes.txt", "r", encoding="utf-8", newline="")`
(disables translation entirely — occasionally needed when working with
formats, like CSV, that manage their own line endings).
**Caveat:** this chapter deliberately stops at "know it exists and what
its default does" — full mechanics are the dedicated file's job.

### 8.8 `closefd`

**What it means:** whether closing the file object should also close
the underlying low-level operating-system file descriptor.
**Why it exists:** relevant only in the rare case where `file` is
passed as an already-open low-level integer file descriptor rather than
a path string.
**When to care:** almost never in this chapter's scope.
**Example:** not shown — genuinely outside beginner/intermediate needs.
**Caveat:** included here purely so the parameter is recognizable if
you ever see it in someone else's code or in the official
documentation.

### 8.9 `opener`

**What it means:** a custom function giving you full control over
exactly how the file gets opened at the operating-system level.
**Why it exists:** advanced use cases — sandboxed file access, custom
permission logic, opening files atomically with specific low-level
flags.
**When to care:** essentially never, until real advanced/production
needs arise, well beyond this chapter.
**Example:** not shown.
**Caveat:** recognize it exists; do not feel obligated to use it.

### 8.10 The basic safe pattern

```python
with open("example.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

- **`with open(...) as f:`** — opens the file and guarantees it will be
  closed afterward, no matter what happens inside the block (§21 covers
  this in full depth).
- **`"r"`** — read mode; the file must already exist (§9.2).
- **`encoding="utf-8"`** — explicit, safe text decoding (§25).
- **`f.read()`** — reads the entire remaining content as one string
  (§12), advancing the cursor to the end of the file (§16).
- **If the file does not exist:** `open()` raises `FileNotFoundError`
  immediately, before the block's body ever runs (§10.3, §27).
- **If an exception occurs inside the block:** the file is still closed
  correctly, and the exception continues propagating normally (§21.3
  demonstrates this explicitly).
- **Why this exact pattern is preferred:** it is short, it is
  unambiguous about intent, and it is impossible to accidentally forget
  to close the file — the single most common structural bug this
  chapter addresses (§20.2, §37 mistakes 1–2).

## 9. File Modes

### 9.1 What a mode is

The **mode** string tells the operating system, up front, exactly what
you intend to do with a file, so it can prepare — or refuse — the
correct kind of access.

### 9.2 The core modes, compared

| Mode | File must exist? | Creates file? | Truncates existing content? | Can read? | Can write? | Typical use |
|---|---|---|---|---|---|---|
| `"r"` | **Yes** — raises `FileNotFoundError` if missing | No | No | Yes | No | Reading a file you expect to already exist |
| `"w"` | No | Yes | **Yes, immediately** | No | Yes | Starting a file completely fresh |
| `"a"` | No | Yes | No — writes go after existing content | No | Yes | Adding to an existing file, e.g. logs |
| `"x"` | **Must NOT exist** — raises `FileExistsError` if present | Yes | N/A | No | Yes | Creating a brand-new file, refusing to overwrite |

### 9.3 Read/write/text/binary modifiers

| Modifier | Meaning |
|---|---|
| `"+"` | Adds the *other* capability — `"r+"` also writes, `"w+"`/`"a+"`/`"x+"` also read |
| `"b"` | Binary mode — returns/accepts `bytes`, not `str` (outside this chapter's scope, §5.4) |
| `"t"` | Text mode — the default; rarely written explicitly |

| Combined mode | Meaning |
|---|---|
| `"rb"` | Read, binary |
| `"wb"` | Write, binary (truncates) |
| `"ab"` | Append, binary |
| `"r+"` | Read and write; file must exist; does **not** truncate |
| `"w+"` | Read and write; **truncates immediately** |
| `"a+"` | Read and write; writes always go to the end |
| `"x+"` | Read and write; file must **not** already exist |

This chapter builds fluency in `"r"`, `"w"`, `"a"`, and `"x"` in text
mode — the `+`/`b` variants are included for completeness and
recognition.

### 9.4 Why `"w"` can destroy existing content — shown explicitly

```python
# Suppose important_notes.txt currently contains:
#   "Meeting notes from March, do not lose this!"

with open("important_notes.txt", "w", encoding="utf-8") as f:
    pass   # do nothing at all -- not even a single write() call

with open("important_notes.txt", "r", encoding="utf-8") as f:
    print(repr(f.read()))
```

```text
''
```

**The instant `open("important_notes.txt", "w", ...)` successfully
opened the file, its entire previous content was erased — before a
single `write()` call happened.** This is called **truncation**: `"w"`
cuts the file to zero length the moment it opens an existing file. This
is documented, intentional behavior, not a bug — but it is the single
most common way beginners accidentally destroy real data, which is
precisely why §29 exists as its own dedicated section.

### 9.5 Why `"a"` is different

```python
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("Started process\n")

with open("log.txt", "a", encoding="utf-8") as f:
    f.write("Process finished\n")

with open("log.txt", "r", encoding="utf-8") as f:
    print(f.read())
```

```text
Started process
Process finished
```

Every open in `"a"` mode positions the cursor at the file's *current*
end — nothing existing is ever overwritten, only added to. §19
develops append mode's use cases fully.

### 9.6 Why `"x"` exists

```python
open("brand_new_file.txt", "x", encoding="utf-8")
```

If `brand_new_file.txt` already exists, this raises `FileExistsError`
**immediately**, instead of silently overwriting or silently
succeeding — useful whenever accidentally overwriting an existing file
would itself be a bug worth surfacing loudly (§10.5).

## 10. Opening and Creating Files

### 10.1 A safe practice setup

Every example in this chapter that creates or modifies files assumes a
dedicated, disposable **practice directory** — never real personal
files or real project files (§29 makes this an explicit rule).

```python
import os

os.makedirs("practice_files", exist_ok=True)
os.chdir("practice_files")
```

Full, portable path handling is
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
subject — here, `os.makedirs`/`os.chdir` exist only to set up a safe
sandbox.

### 10.2 Opening an existing file

```python
with open("existing.txt", "r", encoding="utf-8") as f:
    ...
```

Works cleanly as long as `existing.txt` genuinely exists and is
readable.

### 10.3 Why `"r"` fails on a missing file — `FileNotFoundError`

```python
open("does_not_exist.txt", "r", encoding="utf-8")
```

```text
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'does_not_exist.txt'
```

This is intentional: `"r"` means "I expect this file to already exist;
tell me immediately if it does not" — exactly the behavior you want,
since silently creating an empty file when you expected real data would
hide a real bug.

### 10.4 Why `"w"` creates-or-truncates

`"w"` means "I want a fresh, empty file, whether or not one already
exists" — so it creates the file if missing, and truncates it (§9.4) if
present, unifying both cases into one guarantee: **after `open(...,
"w", ...)` succeeds, the file exists and is empty.**

### 10.5 `FileExistsError` from `"x"` mode

```python
open("log.txt", "x", encoding="utf-8")   # assume log.txt already exists from §9.5
```

```text
Traceback (most recent call last):
  ...
FileExistsError: [Errno 17] File exists: 'log.txt'
```

### 10.6 `PermissionError`

```python
open("/root/secret.txt", "w", encoding="utf-8")
```

```text
Traceback (most recent call last):
  ...
PermissionError: [Errno 13] Permission denied: '/root/secret.txt'
```

Raised when the operating system itself refuses the requested access.
This is not a Python bug to work around — the OS's real access controls
genuinely forbid the operation.

### 10.7 A directory passed where a file was expected

```python
open("practice_files", "r", encoding="utf-8")   # practice_files is a directory
```

```text
Traceback (most recent call last):
  ...
IsADirectoryError: [Errno 21] Is a directory: 'practice_files'
```

A very common cause is a typo or a variable accidentally holding a
directory path — §38's debugging checklist lists "confirm this path
really points at a file" as an early, cheap check for exactly this
reason.

## 11. Reading Text Files

There are four standard ways to pull text out of an open file object —
`read()`, `readline()`, `readlines()`, and direct iteration — each with
a genuinely different behavior, memory cost, and best use case. §12–§15
teach each in full depth; this section previews all four together so
you can see the shape of the whole picture before going deep on any
one.

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    text = f.read()              # entire remaining content, one string

with open("greeting.txt", "r", encoding="utf-8") as f:
    line = f.readline()           # exactly the next one line

with open("greeting.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()         # every remaining line, as a list

with open("greeting.txt", "r", encoding="utf-8") as f:
    for line in f:                # one line at a time, memory-efficient
        print(line)
```

Every one of these reads **from the current cursor position onward**
(§16) — this single fact underlies nearly every "why did my second read
return nothing" bug you will encounter.

## 12. `read()`

### 12.1 What it is and why it exists

**Syntax:** `f.read()` or `f.read(size)`.

`read()` exists for the simplest possible case: "give me the file's
text as one Python string."

### 12.2 No argument — the whole remaining file

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    data = f.read()
print(data)
```

```text
Hello, file!
```

**Return value:** a single `str`. **Cursor behavior:** moves from
wherever it started to the very end of the file. **Memory behavior:**
the entire remaining content is loaded into memory at once — fine for
small files, dangerous for huge ones (§30).

### 12.3 `read(size)` — a bounded number of characters

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    print(repr(f.read(5)))    # 'Hello'
    print(repr(f.read(5)))    # ', fil'
    print(repr(f.read()))     # 'e!\n'   -- everything remaining
```

In text mode, `size` is a count of **characters**, not bytes. Each call
picks up exactly where the previous one left the cursor (§16).

### 12.4 What happens at end of file (EOF), and why a second `read()` can return `''`

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    first = f.read()
    second = f.read()

print(repr(first))
print(repr(second))
```

```text
'Hello, file!\n'
''
```

The first `read()` consumed the entire file and left the cursor at the
very end. The second `read()` starts *from there* — and since nothing
remains after the end of the file, it returns an empty string, not an
error and not the content again. This is one of the most common sources
of "my code reads an empty string for no reason" bugs — §16.4 shows the
fix (`seek(0)`), and §38's debugging checklist lists checking cursor
position explicitly.

### 12.5 Common mistakes with `read()`

Assuming `read()` returns a list of lines — it returns **one string**,
newline characters and all. Iterating over that string with `for line
in content:` yields individual *characters*, not lines — a mistake
detailed fully in §37.

## 13. `readline()`

### 13.1 What it is

**Syntax:** `f.readline()` — reads exactly the next single line.

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    first_line = f.readline()
print(repr(first_line))
```

```text
'Hello, file!\n'
```

### 13.2 Newline handling and EOF behavior

The returned string **includes its trailing `\n`** (except possibly the
file's very last line, if it has none). At end of file, `readline()`
returns an **empty string `''`** — not `None`, not an error — which is
exactly what makes this idiom work:

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    while True:
        line = f.readline()
        if line == "":       # end of file reached
            break
        print(repr(line))
```

### 13.3 Repeated calls and cursor movement

```python
with open("multi_line.txt", "r", encoding="utf-8") as f:
    line1 = f.readline()
    line2 = f.readline()

print(repr(line1))
print(repr(line2))
```

```text
'First line\n'
'Second line\n'
```

Each call advances the cursor past exactly the line just read (§16), so
the next call naturally continues from there.

### 13.4 Common mistake

Confusing an empty string (`''`, end of file) with a genuinely blank
line (`'\n'`, a truthy string containing one character) — `if line ==
"":` correctly detects end-of-file, but `if not line.strip():` would
incorrectly treat a blank *line within the file* the same as
end-of-file.

## 14. `readlines()`

### 14.1 What it is

**Syntax:** `f.readlines()` — reads every remaining line into a list.

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
print(lines)
```

```text
['Hello, file!\n']
```

### 14.2 Return value and memory implications

**Return value:** a `list[str]`, one entry per line, each still
including its trailing `\n`. **Memory behavior:** reads the entire file
at once (like bare `read()`), then additionally builds a full list of
string objects — meaningfully *more* memory overhead than `read()`
alone, for the same file.

### 14.3 When it is useful, and when it is not

Useful when you genuinely need every line available as an indexable,
multi-pass list, *and* the file is small enough that loading it whole
is not a concern. Inappropriate for very large files, where line-by-line
iteration (§15) accomplishes the same task with dramatically less
memory (§30 quantifies this directly).

## 15. Iterating Over Files

### 15.1 Why file objects are iterable

**Syntax:** `for line in f:`

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(repr(line))
```

```text
'Hello, file!\n'
```

A file object implements the same iterator protocol you already know
from lists and `range()` — each step of the loop reads and yields
exactly one line, **without ever holding the whole file in memory at
once**. The cursor advances one line at a time, exactly as with
repeated `readline()` calls, but without you having to check for `''`
yourself.

### 15.2 Newline handling

Exactly like `readline()` and `readlines()`, each yielded line
**includes its trailing `\n`** — Python does not strip it
automatically. `.strip()` removes it (along with any other leading or
trailing whitespace); `line.rstrip("\n")` removes only the trailing
newline, preserving other whitespace exactly:

```python
line = "  indented text  \n"
print(repr(line.strip()))          # 'indented text'
print(repr(line.rstrip("\n")))      # '  indented text  '
```

### 15.3 Decision table — `for line in f` vs. `read()` vs. `readlines()`

| Approach | Loads entire file into memory? | Result shape | Best for |
|---|---|---|---|
| `f.read()` | Yes (or up to `size` chars) | One string | Small files, or you need the whole text as one string |
| `f.readlines()` | Yes | A `list[str]` | Small files where you need indexable, multi-pass line access |
| `for line in f:` | **No** — one line at a time | One line per loop step | The default choice for almost all line-by-line processing, especially large files |

**Default recommendation for this entire chapter and beyond:** reach
for `for line in f:` unless you have a specific, deliberate reason to
need the whole file as one string or one list.

## 16. File Cursor and Position

### 16.1 What the cursor is

Every open file object tracks exactly **where** the next read or write
will happen — the **file position**, or **cursor** (unrelated to your
mouse). Opening a file in `"r"` mode places the cursor at position 0
(the very start); reading moves it forward.

### 16.2 `tell()` — asking where the cursor is

**Syntax:** `f.tell()` — returns the current cursor position as an
`int`.

In text mode, treat that number as an **opaque position value**: it is
meant to be saved and later passed to `seek()`, not interpreted. It is
not reliably a count of characters read, nor of bytes consumed, nor a
portable textual offset (it can differ with encoding and newline
translation). `0` at the start of the file is the one value you can
rely on by meaning.

### 16.3 `seek()` — moving the cursor

**Syntax:** `f.seek(offset)` — moves the cursor to `offset`. In text
mode, `seek(0)` (back to the start) and `seek()` to a value previously
returned by `tell()` are the reliably meaningful cases; arbitrary
arithmetic offsets are a binary-mode technique outside this chapter's
scope.

### 16.4 The mandatory worked example

```python
with open("example.txt", "r", encoding="utf-8") as f:
    print(f.tell())          # 0  -- at the very start
    print(f.readline())       # 'First line\n'
    print(f.tell())            # 11 -- moved forward past the first line
    f.seek(0)                  # reset the cursor back to the start
    print(f.readline())        # 'First line\n'  -- the same line, read again
```

```text
0
First line

11
First line

```

**Explaining the output line by line:** the cursor starts at `0`.
`readline()` reads the first line and prints it (with its `\n`, hence
the blank line after it in the output). `tell()` now reports a new,
non-zero position — `11` for this particular simple ASCII file, which
happens to match the length of `'First line\n'`, but that match is a
coincidence of this example, not something to rely on for text files in
general. What matters is that this value could be saved and handed to
`seek()` later. `seek(0)`
explicitly resets the cursor back to the very start. The following
`readline()` therefore reads the *same* first line again, from the
beginning, rather than continuing on to the second line.

### 16.5 Why a second read can return unexpected results

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    data = f.read()
    data_again = f.read()

print(repr(data))
print(repr(data_again))
```

```text
'Hello, file!\n'
''
```

Directly §12.4's example, restated in cursor terms: after the first
`read()`, the cursor sits at the end of the file, so the second
`read()` has nothing left to read. `f.seek(0)` between the two calls
fixes this by explicitly resetting the cursor.

### 16.6 Practical use cases

Resetting a file object to read it again without reopening it
(`seek(0)`); remembering a position to return to later
(`position = f.tell()` now, `f.seek(position)` later); diagnosing
"unexpectedly empty read" bugs by printing `f.tell()` immediately before
a suspicious read (§38's debugging checklist includes this explicitly).
Beyond these, cursor manipulation is used rarely in everyday text
processing — most real programs read a freshly opened file once and
move on.

## 17. Writing Text

### 17.1 `write()`

**Syntax:** `f.write(text)`

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello")
```

**Return value:** the number of characters written (an `int`) — most
code ignores this, but it exists. **Requirement:** the argument must
be a `str`; writing anything else (an `int`, for example) raises
`TypeError`. **Write position:** writing happens at the current cursor
position, exactly like reading (§16).

### 17.2 `write()` never adds a newline automatically

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("A")
    f.write("B")
    f.write("C")

with open("output.txt", "r", encoding="utf-8") as f:
    print(repr(f.read()))
```

```text
'ABC'
```

Three separate `write()` calls with no `\n` produced one unbroken line
— exactly as documented. If you want each call to start a new line,
include `\n` yourself:

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("First line\n")
    f.write("Second line\n")
```

### 17.3 Repeated writes and overwriting behavior

Within a single `"w"`-mode open, repeated `write()` calls simply
continue appending to what was already written *during this same open*
— truncation (§9.4) only happens once, the moment the file is opened,
not again on every `write()` call. Opening the *same* file again in
`"w"` mode later, however, truncates it again from scratch.

## 18. `writelines()`

### 18.1 What it does

**Syntax:** `f.writelines(iterable_of_strings)`

```python
with open("output.txt", "w", encoding="utf-8") as f:
    lines = ["one\n", "two\n", "three\n"]
    f.writelines(lines)
```

`writelines()` writes every string in the given iterable, one after
another, with nothing inserted between them — functionally equivalent
to calling `write()` once per item.

### 18.2 The critical misconception, shown explicitly

**`writelines()` does NOT add newline characters for you**, despite its
name sounding like it should.

```python
# The incorrect assumption:
with open("output.txt", "w", encoding="utf-8") as f:
    lines = ["one", "two", "three"]
    f.writelines(lines)

with open("output.txt", "r", encoding="utf-8") as f:
    print(repr(f.read()))
```

```text
'onetwothree'
```

No newlines appear anywhere, because none of the strings in `lines`
contained one, and `writelines()` never inserts them on your behalf.

### 18.3 The corrected version

```python
with open("output.txt", "w", encoding="utf-8") as f:
    lines = ["one", "two", "three"]
    f.writelines(line + "\n" for line in lines)
```

Each string is explicitly given its own trailing `\n` before being
passed to `writelines()` — here, via a generator expression, which
`writelines()` accepts just as readily as a literal list.

## 19. Appending

### 19.1 Why append mode exists, restated precisely

`"w"` guarantees "start from an empty file." `"a"` guarantees "add to
whatever is already there, without disturbing it." Python enforces this
distinction at the mode level rather than leaving it to careful
programmer discipline alone.

### 19.2 Creating a file if missing, adding if it exists

```python
with open("activity_log.txt", "a", encoding="utf-8") as f:
    f.write("Program started\n")
```

The first time this runs, `activity_log.txt` does not exist yet — `"a"`
creates it, exactly like `"w"` would. Every subsequent run appends
after everything already there.

### 19.3 Repeated appends across separate program runs

```python
# Run 1:
with open("activity_log.txt", "a", encoding="utf-8") as f:
    f.write("Run 1: started\n")

# Run 2 (a later, separate execution):
with open("activity_log.txt", "a", encoding="utf-8") as f:
    f.write("Run 2: started\n")
```

```text
Run 1: started
Run 2: started
```

This is precisely the shape of a real logging use case — a program that
runs repeatedly and needs each run's activity recorded without erasing
the record of every previous run (logging's own dedicated treatment is
[08-logging-versus-print.md](08-logging-versus-print.md)).

### 19.4 Newline management

Exactly the same rule as `write()` (§17.2) applies here: append mode
does not insert newlines for you. Omitting a trailing `\n` means the
next appended entry runs directly onto the end of the previous one.

### 19.5 A brief note on concurrent appends

If two entirely separate programs (or two threads/processes) append to
the *same* file at exactly the same moment, `"a"` mode does not, by
itself, guarantee their writes won't interleave unpredictably. For a
single program appending to its own file over time — this chapter's
overwhelming focus — this is not a practical concern. §43 develops the
concurrency picture fully; this note exists only so append mode is not
mistaken for an automatic safety guarantee under *any* amount of
simultaneous access.

## 20. `close()`

### 20.1 What it does

**Syntax:** `f.close()`

```python
f = open("output.txt", "w", encoding="utf-8")
f.write("Some content")
f.close()
```

Closing tells the operating system your program is done with the file:
any data still sitting in Python's internal **buffer** gets flushed out
and handed to the operating system (§33), and the operating-system
resources reserved for keeping the file open (§6.3) are released. This
does not by itself guarantee the bytes have reached physical storage
(§33.3).

### 20.2 What happens if you never close a file

- **Buffered data may never actually reach disk** — some of what you
  `write()`d can be silently lost (§32).
- **Resource leakage** — every OS limits how many files a program can
  have open at once; repeatedly opening without closing can eventually
  cause an otherwise-normal `open()` call to fail.
- **File-locking issues on some platforms** — an unclosed file object
  can prevent other programs from accessing the same file.

### 20.3 Why this pattern is fragile

```python
f = open("data.txt", "r", encoding="utf-8")
data = f.read()
f.close()
```

If an exception is raised *between* `open()` and `close()` — for
example, inside `f.read()`, or in processing logic in between —
**`close()` is never reached**, and the file is left open regardless of
your intentions. §21 is Python's standard, structural fix for exactly
this problem.

## 21. Context Managers

### 21.1 The single most important pattern in this chapter

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    contents = f.read()

print(contents)
```

```text
Hello, file!
```

`with open(...) as f:` opens the file, runs the indented block with `f`
bound to the file object, and **guarantees** the file is closed the
moment the block ends — whether it ends normally, or because an
exception was raised partway through.

### 21.2 What `with` means, from first principles

`with` starts a **context** — a block of code with a defined beginning
and end, where Python guarantees a specific cleanup action happens at
the end, no matter how the block finishes.

- **Entering the context:** `open(...)` runs, and its return value is
  bound to the name after `as` (here, `f`).
- **Leaving the context:** the moment execution reaches the end of the
  indented block, for *any* reason, the file is automatically closed
  before control moves on.

**How this actually works, conceptually:** any object usable after
`with` defines two special behaviors Python calls automatically — one
that runs when the block is *entered* (setting things up — here,
`open()` has already done that before `with` even sees the object), and
one that runs when the block is *exited*, for any reason, including an
exception (here, calling `close()`). You do not need to write these
yourself, or fully understand how they are implemented, to use `with`
correctly — you only need to trust the guarantee: **whatever runs
inside a `with open(...) as f:` block, the file is closed by the time
the block ends.** (The full general mechanism behind *any* object
supporting `with` — not just files — is
[Context Managers](../09-Advanced-Production-Oriented-Python-Foundations/03-context-managers.md)'s
own dedicated subject later in the roadmap.)

### 21.3 Why the file still gets closed when an exception occurs

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Before the error\n")
    raise ValueError("Something went wrong!")
    f.write("This line never runs\n")
```

```text
Traceback (most recent call last):
  ...
ValueError: Something went wrong!
```

Even though a `ValueError` interrupted execution partway through the
block, **`f` was still properly closed** before the exception
propagated upward.

### 21.4 Side by side, one final time

```python
# FRAGILE -- correct only if nothing ever raises in between
f = open("data.txt", "r", encoding="utf-8")
data = f.read()
f.close()
```

```python
# RECOMMENDED -- correct unconditionally
with open("data.txt", "r", encoding="utf-8") as f:
    data = f.read()
```

Both produce identical results in the "nothing goes wrong" case. Only
the second is *guaranteed* correct in every case. **From this point
forward, every example in this chapter uses `with open(...) as f:`.**

## 22. Reading → Processing → Writing

### 22.1 Five progressively realistic pipelines

**Uppercase transformation:**
```python
with open("input.txt", "r", encoding="utf-8") as f:
    original_text = f.read()

transformed_text = original_text.upper()

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(transformed_text)
```

**Removing blank lines:**
```python
with open("input.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

non_blank_lines = [line for line in lines if line.strip() != ""]

with open("output.txt", "w", encoding="utf-8") as f:
    f.writelines(non_blank_lines)
```

**Filtering lines containing a keyword:**
```python
with open("input.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

matching_lines = [line for line in lines if "error" in line.lower()]

with open("output.txt", "w", encoding="utf-8") as f:
    f.writelines(matching_lines)
```

**Word counting:**
```python
with open("input.txt", "r", encoding="utf-8") as f:
    text = f.read()

word_count = len(text.split())
print(f"Word count: {word_count}")
```

**Creating a summary file:**
```python
with open("input.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

summary = f"Lines: {len(lines)}\nWords: {sum(len(line.split()) for line in lines)}\n"

with open("summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)
```

### 22.2 The shape every one of these shares

```
read_text_file()   →   process_text()   →   write_text_file()
    (I/O)                (pure logic)          (I/O)
```

Every example above separates three distinct steps: **read completely,
transform completely, write completely** — never interleaving "read a
bit, transform it, write it" inside one tangled block.

### 22.3 Why this separation improves testing, readability, reuse, debugging, and maintenance

- **Testing** — the transformation step (uppercasing, filtering,
  counting) can be tested with plain Python strings, no file involved
  at all (§39 makes this concrete).
- **Readability** — each step answers one question ("what did we read?"
  "what did we compute?" "what did we write?") instead of all three at
  once.
- **Reuse** — the same transformation logic can be applied to text that
  came from anywhere — a file, a network response, a hardcoded test
  string — because it does not know or care where its input came from.
- **Debugging** — a wrong result narrows immediately to "the read was
  wrong," "the transform was wrong," or "the write was wrong," rather
  than requiring you to untangle all three at once.
- **Maintenance** — changing *how* input arrives (a different file
  format, a different source) touches only the read step; changing the
  actual logic touches only the transform step.

§40 develops this principle into a fully worked before/after example.

## 23. Reusable File-I/O Functions

### 23.1 A small, focused function set

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

### 23.2 Inputs, outputs, side effects, exceptions, and responsibility

| Function | Input | Output | Side effect | Exceptions allowed to propagate |
|---|---|---|---|---|
| `read_text_file` | a path | file content as `str` | reads from disk | `FileNotFoundError`, `PermissionError`, `UnicodeDecodeError`, and related `OSError`s |
| `write_text_file` | a path, content | `None` | truncates/creates the file | `PermissionError`, `IsADirectoryError`, and related `OSError`s |
| `append_text_file` | a path, content | `None` | creates/appends to the file | same as `write_text_file` |
| `count_lines` | a path | an `int` | reads from disk | same as `read_text_file` |
| `find_lines_containing` | a path, a keyword | a `list[str]` | reads from disk | same as `read_text_file` |

Each function has exactly **one clear responsibility**, a small,
predictable parameter list, and a predictable return value — it never
returns the raw file object itself, which would force every caller to
also understand file-closing responsibility. None of them catch
exceptions internally — §28.3 explains exactly why that is the correct
default, not an oversight.

### 23.3 Bad design: one giant function

```python
# BAD -- one function trying to do everything
def handle_file(path, mode, content=None, keyword=None):
    if mode == "read":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    elif mode == "write":
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    elif mode == "append":
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
    elif mode == "count":
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    elif mode == "search":
        with open(path, "r", encoding="utf-8") as f:
            return [line for line in f if keyword in line]
```

This single function has an unpredictable return type (`str`, `None`,
`int`, or `list[str]`, depending on a *string* argument the caller must
remember exactly), an ever-growing parameter list as more operations
get added, and no clear single responsibility — it is harder to test,
harder to name correctly, and harder to reason about than five small
functions, each doing one thing.

## 24. Type Hints

### 24.1 Straightforward parameter and return types

```python
def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def count_lines(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)
```

These read exactly as plainly as they look: `read_text_file` takes a
`str` (a path) and returns a `str`; `count_lines` takes a `str` and
returns an `int`.

### 24.2 `path: str` today, `Path` soon

Every function so far types a path as `str`, which is completely
correct and exactly what `open()` accepts directly. Once
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)
introduces `pathlib.Path` — a more robust way to represent file
locations — a natural refinement becomes:

```python
from pathlib import Path


def read_text_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
```

`open()` accepts a `Path` object exactly as readily as a string — this
hint simply documents, precisely, what kind of value the function
expects. That full refinement belongs to that next file; `str` is the
correct, sufficient choice for this chapter.

### 24.3 `TextIO` — typing an already-open file object

```python
from typing import TextIO


def process_lines(file: TextIO) -> int:
    return sum(1 for _ in file)
```

`TextIO` (from the standard `typing` module) is the type-hint name for
"an open file object in text mode." This pattern is useful specifically
when a function should not be responsible for opening or closing the
file itself (the caller controls that, typically with its own `with`
block) — used more sparingly than the path-based functions in §23,
which are the more common, self-contained shape.

### 24.4 `Iterable[str]` — typing "anything you can loop over for lines"

```python
from typing import Iterable


def non_blank_lines(lines: Iterable[str]) -> list[str]:
    return [line for line in lines if line.strip() != ""]
```

`Iterable[str]` means "anything you can loop over that produces
strings" — a list of lines, or a file object itself, both satisfy this
type. This hint communicates precisely that `non_blank_lines` does not
care *how* it received its lines, only that it can iterate over them —
directly reflecting §22.3's separation-of-concerns principle in the
function's own signature.

## 25. Encoding Basics

### 25.1 Characters, Unicode, bytes

A **character** is a single unit of human-readable text. **Unicode** is
a standard that assigns every character used in essentially every
written language a unique number (a "code point"). A **byte** is the
raw unit computers actually store and transmit. An **encoding** is the
specific rule for translating between Unicode characters and the actual
bytes stored on disk.

### 25.2 Encoding and decoding

**Encoding** turns `str` characters into bytes (what happens when
Python writes text to a file). **Decoding** turns bytes back into `str`
characters (what happens when Python reads text from a file). Every
`open()` call in text mode performs one of these automatically, using
whichever encoding you specify.

### 25.3 UTF-8

**UTF-8** correctly represents essentially every character in every
written language in use today and is the dominant standard across the
modern web, most operating systems, and most file formats. Unless you
have a specific, deliberate reason to use something else,
**`encoding="utf-8"` is the right explicit choice whenever the file is
known to be UTF-8 or you control the format** (the usual case in this
roadmap). The correct encoding depends on the actual data, and Python's
default text encoding can be platform-dependent — so, when you know the
expected encoding, state it explicitly rather than relying on the
default. That is a habit worth building from day one.

### 25.4 Why encoding mismatches cause failures

```python
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("Café résumé 日本語")

with open("notes.txt", "r", encoding="ascii") as f:
    text = f.read()
```

```text
Traceback (most recent call last):
  ...
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 3: ordinal not in range(128)
```

The file was correctly written as UTF-8, but reading it back while
claiming it is ASCII (a far more limited encoding) causes Python to
encounter bytes it cannot interpret, and it raises
`UnicodeDecodeError` rather than silently guessing wrong — exactly the
outcome you want.

### 25.5 Where this chapter's coverage stops

This section covers what you need to safely use `open()` day to day:
pass the known encoding (usually `encoding="utf-8"`) explicitly, and understand, conceptually,
why that parameter exists and what breaks when it is wrong or omitted.
The full picture — encoding detection, `errors=` in complete detail,
byte-order marks, and platform interactions — belongs entirely to
[05-encodings-and-newlines.md](05-encodings-and-newlines.md).

## 26. Newline Basics

### 26.1 `"\n"` and line boundaries

A text file, at the byte level, has no inherent concept of "lines" — it
is one continuous sequence of characters. **Line boundaries are
represented by a special character embedded directly in that
sequence**: `\n`, the newline character. A text editor displaying a
file as multiple lines is doing exactly one thing: breaking the display
wherever it finds a `\n`.

```python
text = "First line\nSecond line\nThird line"
print(text)
```

```text
First line
Second line
Third line
```

### 26.2 Why newline behavior matters when writing files

Every write example in §17–§19 depended on this directly: forgetting to
include `\n` in a written string produces one unbroken line instead of
separate lines. Nothing but an explicit `\n` character ever creates a
line break in a text file.

### 26.3 Windows vs. Linux/macOS, conceptually

Different operating systems historically disagree about exactly which
byte sequence means "newline" on disk: Linux and macOS use a single
`\n`; Windows traditionally uses `\r\n` (carriage return + line feed).
Python's `open()` handles this translation automatically in text mode
by default — code written using `\n` behaves correctly across
platforms without you having to think about `\r\n` explicitly, for the
overwhelming majority of cases. **This chapter deliberately stops
here** — the full mechanics of the `newline=` parameter and when you
would ever need to override the default belong entirely to
[05-encodings-and-newlines.md](05-encodings-and-newlines.md).

## 27. Error Handling

### 27.1 The exceptions you will actually encounter

| Exception | Meaning | Common cause | How to diagnose |
|---|---|---|---|
| `FileNotFoundError` | The path does not exist | Typo, wrong working directory, file not yet created | Print the exact path and current working directory (§38) |
| `PermissionError` | The OS refuses the requested access | Read-only file opened for writing, protected directory | Check file/directory permissions outside Python |
| `IsADirectoryError` | You opened a directory as if it were a file | A path variable accidentally points at a folder | `os.path.isdir(path)` |
| `NotADirectoryError` | You treated a file as if it were a directory | A directory-only operation attempted on a file's path | `os.path.isfile(path)` |
| `UnicodeDecodeError` | Bytes could not be decoded with the given encoding | Wrong `encoding=`, or genuinely non-text data opened in text mode | Confirm the file's actual source/encoding |
| `UnicodeEncodeError` | A `str` could not be encoded to bytes | Rare with UTF-8, since it supports virtually all characters | Confirm `encoding=` on the write side |
| `OSError` | The general parent category for most low-level file/OS failures | Base class of everything above (plus rarer OS failures) | Read the exact message text |

### 27.2 Each one, with an example and a catch-or-not judgment

```python
# FileNotFoundError -- often worth catching, with a sensible fallback
try:
    with open("config.txt", "r", encoding="utf-8") as f:
        config_text = f.read()
except FileNotFoundError:
    config_text = ""   # a missing config file is an expected, recoverable case
```

```python
# UnicodeDecodeError -- usually worth catching only if you have a real recovery plan
try:
    with open("data.txt", "r", encoding="utf-8") as f:
        text = f.read()
except UnicodeDecodeError as error:
    print(f"Could not decode {error}; check the file's actual encoding")
    raise
```

Re-raising (`raise`, with no arguments, inside an `except` block) after
logging or printing context is a legitimate pattern: it lets you add
useful diagnostic information without silently swallowing the failure.

### 27.3 The anti-pattern: blindly catching everything

```python
# BAD -- catches everything, hides the real problem
try:
    with open("config.txt", "r", encoding="utf-8") as f:
        config_text = f.read()
except Exception:
    pass
```

This also silently swallows `PermissionError`, `UnicodeDecodeError`, a
genuine bug elsewhere inside the block, or even a typo'd variable name
raising `NameError` — every one of these gets treated identically to
"the file simply doesn't exist yet," which is almost certainly not what
you want, and makes real bugs far harder to find later. **Never write
`except Exception:` (or worse, a bare `except:`) as a general-purpose
"make errors go away" tool** — catch the specific exception you
anticipated and know how to recover from.

## 28. Catch vs Propagate

### 28.1 An important engineering distinction

Not every error should be caught where it occurs. The key question is:
**is this an expected operational condition, or a programmer bug?**

- An **expected operational error** is a condition your program can
  reasonably anticipate happening during normal use, for reasons
  outside your code's control — a config file that might not exist yet,
  a user-supplied path that might be wrong. These are worth catching,
  close to where they happen, with a deliberate, sensible response.
- A **programmer bug** is a mistake in the code itself — a typo, a
  logic error, calling a function with the wrong type. These should
  **not** be caught and silently hidden — they should surface loudly,
  with a full traceback, so they get noticed and fixed.

### 28.2 A worked example: a CLI tool

```python
def load_config(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Config file not found at '{path}'; using default settings.")
        return ""
```

Here, `load_config` catches `FileNotFoundError` deliberately, because a
missing config file is a genuinely expected situation for a tool a user
might run before creating one, and it has a clear, sensible fallback: a
friendly message and default settings. This is exactly the "expected
operational error" case.

### 28.3 What should *not* be caught here

```python
# BAD -- hides a genuine bug behind a generic message
def load_config(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        print("Something went wrong.")
        return ""
```

If `path` were accidentally passed as an `int` instead of a `str`,
`open()` would raise `TypeError` — a genuine programmer bug, not a
missing-file situation. Catching it here and printing a vague "something
went wrong" hides the actual defect instead of surfacing it where it
can be found and fixed. §23's reusable functions (§23.1) deliberately
let all exceptions propagate for exactly this reason: a low-level,
reusable helper function is rarely the right place to decide what
"recovery" should look like for every possible caller.

## 29. Safe File Handling

### 29.1 The core discipline

- **Never open an important file in `"w"` mode without being certain**
  that truncation (§9.4) is genuinely what you want.
- **Understand `"w"` fully before using it** — it is the single most
  destructive mode in everyday use, and the destruction happens
  silently, with no confirmation.
- **Inspect your assumptions before any destructive operation** —
  confirm a path points where you think it does, confirm you are
  working in the directory you think you are (§38).
- **Preserve original data during transformations** — write results to
  a *separate* output file (§22's pattern: read from `input.txt`, write
  to `output.txt`) rather than overwriting the original input in place.
- **Validate input before acting on it**, rather than discovering
  problems midway through a destructive operation.
- **Avoid partial output where possible** — build a complete result in
  memory, and only write once processing has fully succeeded (§29.2).
- **Verify generated output** — read it back and check it looks right,
  especially while still building confidence in new code.
- **Use dedicated practice files/directories** (§10.1) for every
  example and exercise in this chapter.
- **Never practice destructive file operations against real personal
  files or real project files.**

### 29.2 Avoiding partial or corrupt output

```python
# RISKY -- if something raises partway through, output.txt is left half-written
with open("output.txt", "w", encoding="utf-8") as f:
    for record in records:
        f.write(process(record) + "\n")   # if process() raises on record 500 of 1000, output is incomplete
```

```python
# SAFER -- nothing touches the output file until all processing has succeeded
processed_lines = [process(record) + "\n" for record in records]

with open("output.txt", "w", encoding="utf-8") as f:
    f.writelines(processed_lines)
```

This trades a small amount of memory (holding all processed lines at
once) for protection against **processing failures**: if `process()`
raises, `output.txt` has not been opened yet, so it is untouched. It is
**not** atomic output replacement — the write itself can still fail
(disk full, I/O error, crash) after `"w"` has already truncated the
file, leaving it partial. True all-or-nothing replacement is the
temporary-file strategy of §42.4.

## 30. Large Files and Memory

### 30.1 Why `content = f.read()` can be dangerous

If a file is 5 GB and your machine has 8 GB of RAM, `f.read()`
attempts to place the *entire* 5 GB of text into memory as one giant
string — on top of whatever memory your program, your operating
system, and every other running program already need. The likely
outcomes range from severe slowdown to an outright crash. This is not a
hypothetical edge case — real log files and real exported datasets
routinely reach sizes exactly like this.

### 30.2 Comparing the three approaches

```
f.read()          →  entire file loaded into one big string, all at once
for line in f:      →  one line at a time, processed, discarded, then the next
f.read(size)        →  one bounded chunk at a time, processed, discarded, then the next
```

For a 50 MB file, `read()` requires roughly 50 MB (or more) of memory
held simultaneously, before your processing even starts. `for line in
f:` and `f.read(size)` require only roughly the size of one
line/chunk at any given moment.

### 30.3 A practical large-file example

```python
matching_count = 0
with open("huge_file.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "ERROR" in line:
            matching_count += 1

print(f"Found {matching_count} matching lines")
```

This processes a file of *any* size — 1 KB or 100 GB — using
essentially the same small, constant amount of memory throughout. This
shape — **file → one line/chunk at a time → process → discard, repeat**
— is called **streaming**, and it is this chapter's single most
important habit for real-world data work.

## 31. Chunked Reading

### 31.1 `read(size)` in a loop

```python
chunk_size = 8192
with open("huge_file.txt", "r", encoding="utf-8") as f:
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        process(chunk)
```

### 31.2 Why the loop terminates

`f.read(chunk_size)` returns progressively smaller chunks as the file
nears its end, and returns an **empty string** once nothing remains
(exactly §12.4's EOF behavior) — `if not chunk:` (an empty string is
falsy) catches this and exits the loop.

### 31.3 Chunk size and memory benefits

`chunk_size` bounds how much memory any single iteration uses — `8192`
(characters, in text mode) is a common, reasonable default, chosen
because it balances a small memory footprint against not making so many
tiny reads that per-call overhead dominates. Exactly like §30's
line-by-line streaming, only one chunk is ever held in memory at a
time, regardless of the file's total size.

### 31.4 When chunked reading is useful, and an important caveat

Chunked reading is the right tool for files that are not naturally
line-oriented — a single enormous line with no newlines at all, or data
where "line" is not a meaningful unit. **Important caveat, specific to
text mode:** a chunk boundary is **not** guaranteed to fall on a
meaningful semantic boundary (a word, a line, a record) — a chunk can
end in the middle of a word or a line, and your processing logic must
account for that if it matters for your task. For genuinely
line-oriented text, `for line in f:` (§15, §30.2) is simpler and
already handles line boundaries correctly on its own.

## 32. Buffering

### 32.1 What buffering means

**Buffering** means Python (and the operating system beneath it) does
not send every single `write()` call straight to physical disk
instantly. Written data first accumulates in a temporary, fast,
in-memory holding area (the **buffer**), and is sent to disk in larger,
less frequent batches.

### 32.2 Why buffering exists

Recall §4.7: touching disk is dramatically slower than touching memory.
If Python physically wrote to disk on *every single* `write()` call, a
program making thousands of small writes would spend enormous amounts
of time waiting on disk I/O. Batching many small writes into fewer,
larger physical operations makes I/O dramatically faster in the common
case.

### 32.3 Python ↔ OS interaction, and the `buffering` parameter

```python
open("file.txt", "w", encoding="utf-8", buffering=-1)   # default: automatically chosen, sensible buffer size
open("file.txt", "w", encoding="utf-8", buffering=1)     # line-buffered: flush after every newline
```

Python's own buffer sits in front of the operating system's own
separate buffering layer — data can leave Python's buffer and still not
be physically on disk yet, because the OS is buffering it further
(§33.3 returns to this).

### 32.4 Why beginners should not manually tune buffering

`buffering=-1` (the default) is correct for nearly all code, including
every example in this chapter. Manually tuning it is a genuine,
occasionally valuable production optimization — but it should follow
*measuring* a real, specific performance problem
([Profiling and Measuring Before Optimizing](../10-Production-Habits-for-Python-Programs/06-profiling-and-measuring-before-optimizing.md),
much later in the roadmap), never come before it.

## 33. `flush()`

### 33.1 What it does

**Syntax:** `f.flush()`

```python
with open("progress.log", "a", encoding="utf-8") as f:
    f.write("Step 1 complete\n")
    f.flush()
    do_something_slow()
    f.write("Step 2 complete\n")
```

`flush()` forces any data currently sitting in Python's internal buffer
(§32) to be handed off to the operating system immediately, rather than
waiting for the buffer to fill naturally or for the file to close.

### 33.2 When explicit `flush()` is genuinely useful

A long-running process writing a progress log, where you want each
line visible to someone tailing the log file in real time, rather than
appearing in a delayed burst; just before an operation that might crash
the program outright, since a hard crash can skip `close()`'s automatic
flush. For ordinary scripts that read, process, write, and exit
normally, the automatic flush on `close()` (§20.1), especially via a
`with` block (§21), is entirely sufficient.

### 33.3 An important, honest caveat about durability

`flush()` guarantees your data has left Python's own buffer and been
handed to the operating system — it does **not** guarantee the
operating system has physically written those bytes all the way down to
storage hardware in every possible failure scenario (the OS has its own
buffering layer too). Treat `flush()` as "make this visible to other
programs reading the file right now," not as an absolute guarantee
against every conceivable power-loss scenario.

## 34. File Object Methods and Properties

A single reference table for every text-file-object member this
chapter uses or has introduced.

| Member | What it does | Syntax | Return value | Common mistake | Limitation |
|---|---|---|---|---|---|
| `read()` / `read(size)` | Read all (or up to `size` characters) from the cursor onward | `f.read()` | `str` | Assuming it returns a list of lines (§12.5) | Loads everything requested into memory at once |
| `readline()` | Read the next single line | `f.readline()` | `str`, `''` at EOF | Confusing `''` (EOF) with a blank line `'\n'` (§13.4) | One line per call — verbose for whole-file reads |
| `readlines()` | Read all remaining lines as a list | `f.readlines()` | `list[str]` | Using it on a huge file (§14.3) | Loads everything into memory as a list |
| `write(text)` | Write a string at the cursor | `f.write("hi\n")` | `int` (characters written) | Forgetting the `\n` (§17.2) | Argument must already be a `str` |
| `writelines(iterable)` | Write many strings back-to-back | `f.writelines(lines)` | `None` | Assuming it adds newlines (§18.2) | No newlines are inserted automatically |
| `seek(offset)` | Move the cursor | `f.seek(0)` | new position (`int`) | Using non-`0`/non-`tell()` offsets in text mode | Reliable mainly for `0` and prior `tell()` values in text mode |
| `tell()` | Report the current cursor position | `f.tell()` | `int` | Not checking it when a read looks wrong (§16.6) | None significant for this chapter's use |
| `flush()` | Force buffered data out now | `f.flush()` | `None` | Assuming it guarantees physical durability (§33.3) | Does not bypass the OS's own buffering |
| `close()` | Close the file, release resources | `f.close()` | `None` | Forgetting to call it (use `with` instead, §21) | Cannot be undone; further operations raise `ValueError` |
| `readable()` | Whether reading is currently supported | `f.readable()` | `bool` | Assuming it means "file has content" | Reflects mode, not content |
| `writable()` | Whether writing is currently supported | `f.writable()` | `bool` | Same as above | Reflects mode, not content |
| `seekable()` | Whether `seek()`/`tell()` are supported | `f.seekable()` | `bool` | Rarely checked in beginner code | Some streams (not covered here) are not seekable |
| `fileno()` | The low-level OS file descriptor number | `f.fileno()` | `int` | Assuming every file-like object has one | Advanced/rarely needed directly; §35.4 |

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    print(f.readable())    # True
    print(f.writable())    # False -- opened in "r" mode
    print(f.seekable())    # True
```

```text
True
False
True
```

**Practical use:** `readable()`/`writable()`/`seekable()` are primarily
useful when writing generic, reusable code that needs to *check* a file
object's capabilities before attempting an operation, rather than
simply assuming — genuinely useful in library-style code, rarely needed
in everyday scripts where you already know exactly how you opened the
file.

## 35. File Object Properties

### 35.1 `.name`

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    print(f.name)
```

```text
greeting.txt
```

The path or name the file object was opened with — useful for logging
or error messages that need to identify which file is involved.

### 35.2 `.mode`

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    print(f.mode)
```

```text
r
```

The mode string the file was opened with (§9) — useful when a function
receives an already-open file object and needs to confirm it was opened
the way it expects.

### 35.3 `.closed`

```python
with open("greeting.txt", "r", encoding="utf-8") as f:
    print(f.closed)   # False -- still inside the with block

print(f.closed)         # True -- the with block already closed it
```

```text
False
True
```

`True` once the file has been closed — useful for confirming a
context manager (or explicit `close()` call) actually ran.

### 35.4 `fileno()`, with a portability caveat

`f.fileno()` returns the low-level, operating-system-assigned integer
identifying this open file — used by advanced code that needs to
interoperate directly with lower-level OS or C-library APIs. **Not
every file-like object has one** — some in-memory or specialized
stream-like objects you may encounter later in the roadmap deliberately
do not support `fileno()` and raise an error if you call it. This
chapter mentions it purely for recognition; it is not a technique you
need to reach for in ordinary text-file work.

## 36. File I/O and OS Resources

### 36.1 The full conceptual architecture

```
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

### 36.2 Connecting each layer to what this chapter has already shown

- **Python code** calls `open()`, `read()`, `write()` — the surface
  this entire chapter teaches.
- **The Python file object** (§7) is the object those calls happen on —
  it tracks the cursor (§16) and mode (§9), and exposes the methods
  cataloged in §34.
- **The Python I/O layer** performs buffering (§32) and encoding/
  decoding (§25) before anything reaches the operating system.
- **The operating system** performs the actual low-level request — this
  is a **system call**, the same general mechanism your Stage 0 study of
  processes and operating systems already introduced as *how* any
  program asks the OS to do anything on its behalf; file access is one
  concrete, everyday example of it.
- **The filesystem** is the operating system's own bookkeeping structure
  for organizing what files exist, where their data physically lives,
  and who is allowed to access them.
- **Physical storage** is the actual hardware (an SSD or hard drive)
  where bytes are ultimately, durably kept.

### 36.3 Why this explains behavior you have already seen

- **Opening a file consumes a resource** (§6.3, §20.2) — because the
  operating system must reserve bookkeeping space to track the open
  connection, at the OS layer of this diagram.
- **Closing releases it** (§20.1) — reversing exactly that reservation.
- **Buffering exists** (§32) — because crossing every one of these
  layers, all the way down to physical storage, on every single small
  operation, would be far too slow; batching reduces how often the full
  round trip happens.
- **Errors can occur at multiple layers** (§27) — a `PermissionError`
  originates at the filesystem/OS layer (access control); a
  `UnicodeDecodeError` originates entirely within Python's own I/O
  layer (a translation problem, not an OS-level refusal) — the same
  diagram explains why these feel like fundamentally different kinds of
  failure.

This section does not repeat Stage 0's operating-systems material in
full — it exists only to connect what you already know about processes,
system calls, and storage to the specific, concrete behavior you have
now seen directly, throughout this entire chapter.

## 37. Common Beginner Mistakes

**1. Forgetting to close a file.**
```python
# BAD
f = open("data.txt", "w", encoding="utf-8")
f.write("some data")
# f.close() never called
```
→ **Why it fails:** risks lost buffered data (§32) and resource
leakage (§20.2).
```python
# BETTER
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("some data")
```
→ **Explanation:** closing is automatic and guaranteed, even under an
exception (§21.3).

**2. Not using `with`.**
```python
# BAD
f = open("data.txt", "r", encoding="utf-8")
data = f.read()
f.close()
```
→ **Why it fails:** fragile under exceptions (§20.3).
```python
# BETTER
with open("data.txt", "r", encoding="utf-8") as f:
    data = f.read()
```

**3. Using `"w"` accidentally.**
```python
# BAD -- meant "r", typed "w"
f = open("important_data.txt", "w", encoding="utf-8")
```
→ **Why it fails:** immediately erases `important_data.txt` (§9.4),
before a single `write()` call.
→ **Explanation:** always pause and double-check the mode character
before running code that opens an existing file in `"w"` mode.

**4. Assuming `read()` returns a list of lines.**
```python
# BAD
content = f.read()
for line in content:
    print(line)    # prints one CHARACTER at a time, not one line!
```
→ **Why it fails:** `read()` returns one `str` (§12.2); iterating a
string yields characters, not lines.
```python
# BETTER
for line in f:
    print(line)
```

**5. Assuming `writelines()` adds `"\n"` automatically.**
Directly §18.2's worked example — `writelines()` never inserts
newlines; each string must already include its own.

**6. Reading the same file twice without `seek()`.**
Directly §12.4's / §16.5's worked example — the second `read()` returns
`''` because the cursor is already at the end.

**7. Loading huge files into memory.**
```python
# BAD, for a genuinely large file
with open("huge_log.txt", "r", encoding="utf-8") as f:
    all_lines = f.readlines()
```
→ **Better:** iterate line by line instead (§15, §30), never holding
more than one line in memory at a time.

**8. Ignoring encoding.**
```python
# RISKY -- relies on a platform-dependent default (§8.5)
with open("notes.txt", "r") as f:
    text = f.read()
```
→ **Better:** pass the known encoding explicitly — usually `encoding="utf-8"` (§25.3).

**9. Catching `Exception` everywhere.**
Directly §27.3's worked example — swallows every possible error
identically, hiding real bugs. **Better:** catch only the specific,
anticipated exception (§28.1).

**10. Silently ignoring file errors.**
```python
# BAD -- the problem simply vanishes
try:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
except OSError:
    data = None
    # nothing recorded anywhere that this happened
```
→ **Better:** at minimum, log or print that a fallback occurred and
why, so silent data loss never happens invisibly.

**11. Mixing file I/O and business logic.**
```python
# BAD -- reading, transforming, and writing all tangled together
with open("input.txt", "r", encoding="utf-8") as f:
    with open("output.txt", "w", encoding="utf-8") as out:
        for line in f:
            if line.strip():
                out.write(line.upper())
```
→ **Better:** separate I/O from logic (§22.3, §40) — read completely,
transform with a pure function, write completely.

**12. Writing output before validation is complete.**
Directly §29.2's worked example — writing incrementally risks a
half-finished file if something fails partway through. **Better:**
validate/process fully in memory first, then write once, completely.

**13. Assuming every line ends exactly the same way.**
```python
# RISKY -- assumes every line has a trailing "\n" to strip
for line in f:
    clean = line[:-1]   # chops off the last character unconditionally!
```
→ **Why it fails:** a file's very last line may have no trailing
newline at all, in which case this silently deletes a real character
of content.
```python
# BETTER
for line in f:
    clean = line.rstrip("\n")
```

**14. Repeatedly opening/closing unnecessarily in a tight loop.**
```python
# BAD -- reopens the same file on every iteration
for record in records:
    with open("output.txt", "a", encoding="utf-8") as f:
        f.write(str(record) + "\n")
```
→ **Why it fails:** every open/close round-trips through the operating
system (§4.7, §6.3) — for a loop of any real size, this is dramatically
slower than necessary.
```python
# BETTER -- open once, write many times
with open("output.txt", "a", encoding="utf-8") as f:
    for record in records:
        f.write(str(record) + "\n")
```

**15. Not checking the actual exception message.**
```python
# BAD -- reacts to "some OSError happened" without reading what it says
try:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
except OSError:
    print("File error.")
```
→ **Better:**
```python
try:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
except OSError as error:
    print(f"File error: {error}")
```
→ **Explanation:** the exception's own message (§27.1's table; §38 step
9) almost always names the specific underlying problem directly —
discarding it throws away the most useful diagnostic information you
have.

## 38. Debugging File I/O

### 38.1 A systematic, twelve-step workflow

1. **Identify the exact operation** that failed — which line, which
   function, which `open()` call.
2. **Check the path assumption** — print the exact path string your
   code is about to open, alongside your program's current working
   directory (`import os; print(os.getcwd())`).
3. **Check whether the file exists**, using that exact path
   (`os.path.exists(path)`), separate from whether `open()` succeeds.
4. **Check whether it is actually a file** — `os.path.isfile(path)`
   versus `os.path.isdir(path)` (§10.7).
5. **Check the mode** you actually passed — re-read the exact `mode`
   string; a stray `"w"` where `"r"`/`"a"` was intended is a common,
   high-impact typo (§9.4, mistake §37 category 3).
6. **Check the encoding** — confirm the encoding you are reading with
   actually matches the encoding the file was written with (§25.4).
7. **Check permissions** — can your user account actually read or write
   at this location, independent of Python.
8. **Check the cursor position**, if reads are behaving unexpectedly —
   print `f.tell()` immediately before a suspicious read (§16.6).
9. **Read the traceback completely** — the exact exception type and
   message (§27.1) usually points directly at the category of problem.
10. **Reproduce with the smallest possible file** — a tiny, disposable
    test file with two or three lines of known content.
11. **Change one variable at a time** — never adjust several guesses at
    once before re-testing.
12. **Verify the fix, and document what the root cause actually was.**

### 38.2 The Stage 0 engineering loop, applied here

```
Goal → assumptions → smallest experiment → observe → explain
    → change one variable → verify → document
```

This is the same general debugging discipline this roadmap has used
since Stage 0: state clearly what you expect, state clearly what you
are assuming, test the smallest possible piece of that assumption
directly, and change exactly one thing at a time before re-testing.

### 38.3 Two worked debugging scenarios

**Scenario A — "My `read()` call returns an empty string, but I know
the file has content."**
Step 8: print `f.tell()` right before the `read()` call. If it is not
`0`, something earlier in the code already consumed the file (§16.5) —
fix with `f.seek(0)`, or, more often, simply avoid reading the same
file object twice without a clear reason.

**Scenario B — "My program raises `UnicodeDecodeError` on some files
but not others."**
Step 6: the specific files that fail were very likely written with a
different encoding than the `encoding="utf-8"` your code assumes.
Confirm by trying one specific failing file in isolation, and comparing
its origin/source against the files that succeed.

## 39. Testing File I/O

### 39.1 Why real temporary files/directories, not your project files

Tests that touch the filesystem should never read or write inside your
actual project — they should use a **temporary directory**, created
fresh for each test and automatically cleaned up afterward. `pytest`
provides exactly this via its built-in `tmp_path` fixture: a
ready-to-use, automatically-cleaned-up temporary directory, handed
directly to any test function that asks for it by name (full `pytest`
mechanics belong to
[pytest: Assertions, Fixtures, and Parametrization](../07-Testing-and-Systematic-Debugging/02-pytest-assertions-fixtures-and-parametrization.md);
here, `tmp_path` is used purely as a safe testing tool).

### 39.2 Testing a successful read and a successful write

```python
def test_write_text_file_then_read_it_back(tmp_path):
    file_path = tmp_path / "output.txt"

    write_text_file(str(file_path), "Hello, test!")

    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == "Hello, test!"
```

### 39.3 Testing append and overwrite behavior

```python
def test_append_adds_to_existing_content(tmp_path):
    file_path = tmp_path / "log.txt"
    write_text_file(str(file_path), "first\n")

    append_text_file(str(file_path), "second\n")

    assert read_text_file(str(file_path)) == "first\nsecond\n"


def test_write_overwrites_existing_content(tmp_path):
    file_path = tmp_path / "data.txt"
    write_text_file(str(file_path), "old content")

    write_text_file(str(file_path), "new content")

    assert read_text_file(str(file_path)) == "new content"
```

### 39.4 Testing an empty file and a missing file

```python
def test_reading_an_empty_file_returns_empty_string(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.touch()

    assert read_text_file(str(file_path)) == ""


import pytest


def test_read_text_file_raises_for_missing_file(tmp_path):
    missing_path = tmp_path / "does_not_exist.txt"

    with pytest.raises(FileNotFoundError):
        read_text_file(str(missing_path))
```

### 39.5 Testing invalid encoding and line filtering

```python
def test_reading_with_wrong_encoding_raises(tmp_path):
    file_path = tmp_path / "notes.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("café")

    with pytest.raises(UnicodeDecodeError):
        with open(file_path, "r", encoding="ascii") as f:
            f.read()


def test_find_lines_containing_filters_correctly(tmp_path):
    file_path = tmp_path / "log.txt"
    write_text_file(str(file_path), "ok\nERROR: disk full\nok\nERROR: timeout\n")

    matches = find_lines_containing(str(file_path), "ERROR")

    assert matches == ["ERROR: disk full", "ERROR: timeout"]
```

### 39.6 Testing a larger, generated file

```python
def test_count_lines_on_a_larger_generated_file(tmp_path):
    file_path = tmp_path / "many_lines.txt"
    lines = [f"line {i}\n" for i in range(5000)]
    write_text_file(str(file_path), "".join(lines))

    assert count_lines(str(file_path)) == 5000
```

A "large-ish" test file, in practice, means large enough to
meaningfully exercise line-by-line logic without being slow to generate
and clean up on every test run — not a genuine multi-gigabyte file,
which is impractical inside a test suite.

## 40. Separating I/O from Domain Logic

### 40.1 The bad version, made concrete

```python
# BAD -- everything mixed together in one function
def process_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File not found: {path}")
        return

    result_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            result_lines.append(stripped.upper())

    with open("output.txt", "w", encoding="utf-8") as f:
        for line in result_lines:
            f.write(line + "\n")

    print(f"Processed {len(result_lines)} lines")
```

This one function is responsible for opening a file, handling a
missing-file error, filtering, transforming, writing output, *and*
reporting to the user — six distinct responsibilities, impossible to
test independently, and impossible to reuse any single piece of without
dragging along the rest.

### 40.2 The improved version

```python
def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def process_text(text: str) -> str:
    lines = text.splitlines()
    cleaned = [line.strip().upper() for line in lines if line.strip()]
    return "\n".join(cleaned) + "\n"


def write_text_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def run(input_path: str, output_path: str) -> None:
    text = read_text_file(input_path)
    result = process_text(text)
    write_text_file(output_path, result)
```

`process_text` is entirely pure — a `str` in, a `str` out, no file
involved at all, and therefore testable directly with in-memory strings
(§39.2's pattern, applied here with no file needed whatsoever for this
particular function).

### 40.3 Why this improves testability, reuse, debugging, and maintainability

- **Single responsibility** — each function does exactly one thing:
  read, transform, or write.
- **Testability** — `process_text` can be tested with a hardcoded
  string, with zero filesystem setup.
- **Reuse** — `process_text` works identically on text from any source
  — a file, a network response, user-typed input — because it never
  assumed where its input came from.
- **Debugging** — a wrong final result narrows immediately to "the read
  was wrong," "the transform was wrong," or "the write was wrong."
- **Maintainability** — handling a missing file differently, or
  changing the transformation rules, each touches exactly one function,
  not a single large tangled block.

## 41. Real-World Applications

Text-file handling appears throughout real software engineering — not
as a beginner exercise left behind once "real" work starts:

- **Application logs** — programs append (§19) a running, permanent
  record of what happened, for later debugging and auditing.
- **Configuration-like text** — small text files read once at startup
  to control a program's behavior (fully developed later, in
  [09-environment-configuration-and-input-validation.md](09-environment-configuration-and-input-validation.md)).
- **Generated reports** — a program processes data and writes a
  human-readable text summary as its output.
- **Data ingestion and ETL preprocessing** — reading raw text data,
  transforming it, writing it forward into the next pipeline stage —
  exactly §22's read-transform-write pattern, at production scale.
- **Evaluation datasets and prompt datasets** — training examples,
  evaluation cases, and prompt templates in AI/ML work are very often
  stored and exchanged as plain or line-delimited text.
- **Experiment outputs and model/evaluation artifacts** — results,
  logs, and metrics from a training or evaluation run, written out for
  later inspection.
- **Batch-processing inputs** — a large volume of text records
  processed the same way, one at a time, exactly the streaming pattern
  from §30–§31.
- **Command-line tools** — nearly every CLI program that "does
  something with a file" (later, §06–§07 in this module) is,
  underneath, built directly on this chapter's mechanics.
- **Debugging artifacts** — captured output, traces, or dumps written
  to disk for later inspection.

**Looking ahead to Applied AI work specifically:** the exact same
foundations — read a text source, transform it reliably, write a
dependable output — underlie training-data preparation, evaluation
pipelines, capturing and inspecting LLM traces, experiment artifacts,
model evaluation outputs, and data-quality pipelines. This chapter does
not introduce any AI-specific libraries or tools; the connection here is
conceptual: **everywhere those systems eventually get used, this
chapter's foundations are what they are built on top of.**

## 42. Production-Oriented Design

### 42.1 The full pattern

```
Input
    ↓
Read
    ↓
Validate
    ↓
Transform
    ↓
Write
    ↓
Verify
```

This is §3's boundary-first principle, restated as a concrete pipeline:
raw input is read, checked against your assumptions (**boundary
validation** — exactly the "validate at the boundary" idea from §3,
applied specifically to what you read from a file), transformed by pure
logic, written out, and finally verified.

### 42.2 Boundary validation, made concrete

```python
def load_records(path: str) -> list[str]:
    text = read_text_file(path)

    if not text.strip():
        raise ValueError(f"{path} is empty; expected at least one record")

    return [line for line in text.splitlines() if line.strip()]
```

The check happens immediately after reading, before any further
processing trusts the content — exactly "transform into a reliable
internal representation" from §3: by the time `load_records` returns,
every caller can safely assume the result is a non-empty list of
non-blank strings, without re-checking.

### 42.3 Explicit errors and predictable outputs

A production-oriented function should fail with a clear, specific
exception (or a documented return value) the moment an assumption is
violated — never silently produce a partially-wrong result (§29.2,
§37 mistake 10).

### 42.4 Safe output strategy, conceptually

```
write to a temporary file
    ↓
finish successfully
    ↓
replace the real output file with the temporary one
```

If writing fails partway through, the *original* output file (if any)
is never touched — only the temporary file is left incomplete, and can
simply be discarded. This chapter introduces the idea at a conceptual
level only; the concrete implementation (using the standard library to
write safely and rename atomically) is
[Safe File Writes](../10-Production-Habits-for-Python-Programs/05-safe-file-writes.md)'s
own dedicated subject, much later in the roadmap.

### 42.5 Memory awareness, testability, reproducibility, separation of concerns, idempotency

- **Memory awareness** — choosing streaming (§30) over `read()` for
  large inputs is a deliberate design decision, not an afterthought.
- **Testability** — every stage of §42.1's pipeline should be testable
  independently, exactly as §40 demonstrated.
- **Reproducibility** — given the same input, the same pipeline should
  produce the same output every time, with no dependency on machine-
  specific state.
- **Separation of concerns** — I/O, validation, transformation, and
  output verification each remain their own distinct step.
- **Idempotency, conceptually** — running the same pipeline twice on
  the same input should ideally produce the same result both times
  (rather than, for example, silently appending duplicate data) — a
  property far easier to reason about when each stage is small and
  clearly bounded.

## 43. Concurrency Considerations

### 43.1 Why correct Python code is not automatically safe

Everything in this chapter has assumed a single program, acting alone,
on a file. Real systems are often not that simple: **if two separate
processes write to the same file at the same time, the result can be
wrong even though each process's own code is individually correct.**
Python's file objects do not, by themselves, coordinate with other,
separate programs also touching the same file.

### 43.2 Two processes writing the same file

Opening a file in `"w"` mode truncates it (§9.4). If Process A and
Process B both do so and then write, the resulting contents depend on
timing and on filesystem and process behavior: the writers can
overwrite or interfere with each other, and one's intended output can be
partially or entirely lost, with no error raised to either process.
Ordinary `"w"` or `"a"` usage is not a concurrency-control mechanism.

### 43.3 Append operations and race conditions

Append mode (§19.5) is *somewhat* safer for simple, single-line writes
on many systems, but it is not a strict guarantee: under heavy
concurrent writing, interleaved output (parts of two different lines
mixed together) is possible on some systems and configurations. A
**race condition** is the general name for this class of bug: the
correctness of the result depends on the precise, unpredictable timing
of two or more independent operations.

### 43.4 File locking, conceptually

Some operating systems and libraries provide **file locking** — a
mechanism letting one program signal "I am using this file right now;
wait your turn" to other programs. This chapter does not teach how to
implement locking — only that it exists, conceptually, as the class of
tool that solves this specific problem when it genuinely matters.

### 43.5 The one takeaway for this chapter's scope

**Multiple independent writers can create correctness problems, even
when every individual program's code is entirely correct in isolation.**
For a single program working with its own files — this chapter's
overwhelming focus, and the overwhelming majority of the exercises and
projects ahead — this is not a practical daily concern. It becomes one
the moment your code is expected to run alongside other processes
touching the same files, which is a real, common situation in
production systems, and worth recognizing by name now, well before it
becomes a live problem to solve.

## 44. Mini Projects

Each project below is intentionally left with real implementation work
remaining — a problem statement, requirements, and guidance, not a
finished solution.

### Project 1 — Basic Text File Reader

**Objective:** build a small script that reads a text file and reports
basic statistics about it.

**Requirements:** open a text file; read its contents; count lines;
count words; handle a missing file gracefully (§28's "expected
operational error" pattern).

**Milestones:** (1) reading and printing raw content; (2) line
counting; (3) word counting; (4) a friendly message instead of a raw
traceback when the file is missing.

**Expected behavior:** running against a normal multi-line file prints
its content along with accurate line and word counts.

**Edge cases:** an empty file; a file with only blank lines; a file
with one very long line and no newlines at all.

**Tests to write:** a normal file; an empty file; a missing file
(expecting your graceful-handling path, not a crash).

**Debugging scenarios:** a word count that looks wrong — print
intermediate values (§38 step 11: change one variable at a time) to
find where the count diverges from your expectation.

**Production improvements:** accept the file path as a command-line
argument instead of hardcoding it (a natural bridge toward
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)).

### Project 2 — Text File Transformer

**Objective:** read an input file, clean it up, and write the result to
a *separate* output file, preserving the original.

**Requirements:** read the input; remove blank lines; normalize some
simple text issue of your choosing (trailing whitespace, repeated
blank lines); write to a different output path (§29.1); never modify
the input file.

**Milestones:** (1) read-then-write-unchanged, to confirm the pipeline
works; (2) add blank-line removal; (3) add your chosen normalization;
(4) verify against a deliberately messy test file.

**Expected behavior:** the output file is a cleaned version of the
input; the input file is untouched.

**Edge cases:** a completely empty input file; a file that is entirely
blank lines; a file with no trailing newline on its last line.

**Tests to write:** a messy file with the exact issues you clean up; an
already-clean file (output should equal input); an empty file.

**Debugging scenarios:** output looks identical to input — check
whether your cleanup logic is actually being called and its result
actually used (§37 mistake 5's category of "computed but discarded"
bug, applied here).

**Production improvements:** report a short summary of what changed
(how many blank lines removed) — a preview of
[08-logging-versus-print.md](08-logging-versus-print.md).

### Project 3 — Large Text File Analyzer

**Objective:** analyze a text file too large to comfortably load
entirely into memory.

**Requirements:** process strictly line-by-line (§30–§31) — no
`read()`/`readlines()` on the whole file; count lines matching a given
condition; calculate summary statistics (total lines, matches, match
percentage); write a report to an output file.

**Milestones:** (1) line counting alone; (2) the matching condition;
(3) the summary percentage; (4) generate a genuinely large test file
(§39.6's approach) and confirm performance stays reasonable.

**Expected behavior:** correct counts and percentage regardless of file
size, using bounded memory throughout.

**Edge cases:** an empty file (percentage must not divide by zero); a
file with exactly one line; every line matching; no line matching.

**Tests to write:** each edge case above, plus a normal mixed-content
file with a known, hand-counted number of matches.

**Debugging scenarios:** counts off by one — verify with a tiny, fully
hand-traced 3-line file first (§38 step 10) before trusting the logic
against a large generated file.

**Production improvements:** report progress periodically during a
long-running scan (a preview of streaming-with-feedback, relevant again
once logging is covered).

### Project 4 — Reliable Text Processing Utility

**Objective:** build a small, genuinely reusable library of text-file
utility functions, to the standard this chapter has modeled throughout.

**Requirements:** reusable functions at minimum matching §23
(`read_text_file`, `write_text_file`, `append_text_file`,
`count_lines`, `find_lines_containing`); full type hints (§24); every
file-opening function uses a context manager (§21); deliberate,
documented catch-vs-propagate decisions (§28) for each function; a
`pytest` suite covering successful cases, missing files, empty files,
and at least one deliberately malformed input (§39); memory-aware
processing for at least one function (§30–§31); a clean separation
between I/O and processing (§40); a short, honest summary of what the
utility does and how to use it, ready to expand into full documentation
later.

**Milestones:** (1) implement and manually test each function in
isolation; (2) add type hints throughout; (3) write the test suite;
(4) deliberately break one function (introduce one of §37's mistakes on
purpose) and confirm your tests actually catch it.

**Expected behavior:** every function behaves exactly as documented,
including its documented failure modes.

**Edge cases / tests:** every case already covered across §39's
examples, applied consistently across every function.

**Debugging scenarios:** a test that should fail but passes — check
whether the test is actually exercising the code you think it is.

**Production improvements:** this project is the direct foundation for
[Safe File Writes](../10-Production-Habits-for-Python-Programs/05-safe-file-writes.md)
later in the roadmap, where §42.4's "write completely or not at all"
guarantee is built out fully with temporary files and atomic renames.

## 45. Progressive Exercises

### Level 1 — Beginner

1. **Create a text file** and write three lines to it in a single
   `write()` call, using `"\n".join(...)`. Note that `join` adds no
   newline after the last item, so the file has no trailing newline.
   *Expected behavior:* reading the file back shows exactly three lines.
2. **Read text** from the file above and print its full content.
3. **Append text** — add a fourth line without disturbing the first
   three (since the file has no trailing newline, your appended text
   must begin with `"\n"` to start a new line). *Edge case:* run your append code twice in a row — does the
   file now have five lines?
4. **Count lines** using iteration (§15), not `readlines()`. *Edge
   case:* an empty file.
5. **Count words** across an entire file. For this exercise, a word is
   a whitespace-delimited token as produced by `str.split()`. *Edge case:* a file
   containing only whitespace.
6. **Print each line** of a file, with its trailing newline stripped.

### Level 2 — Intermediate

7. **Filter lines** containing a given keyword, returning them with
   newlines stripped. *Constraint:* do not load lines you will not
   ultimately keep into your final result.
8. **Transform lines** — write a function that reverses the character
   order within each line (not the line order). *Edge case:* a blank
   line within the file.
9. **Combine text files** — given a list of paths, write their combined
   contents, in order, into one output file. *Edge case:* decide,
   deliberately, what should happen if one input file is missing
   partway through.
10. **Create a summary file** reporting line count, word count, and
    character count for a given input file.
11. **Handle missing files** — write a function that returns a sensible
    default if a file does not exist, but lets other exceptions (like
    `PermissionError`) propagate (§28.1).
12. **Handle empty files** — confirm each of your Level 1–2 functions
    behaves sensibly (not with a crash) when given a genuinely empty
    file.
13. **Use reusable functions** — rewrite exercises 7–10 to build on
    §23's `read_text_file`/`write_text_file` rather than opening files
    directly each time.

### Level 3 — Advanced

14. **Stream a large file** — generate a file with at least 100,000
    lines, then find the single longest line without ever loading the
    whole file into memory (§30).
15. **Process chunks** — implement a function using `read(size)` (§31)
    that counts total characters in a file without using `read()` with
    no argument and without iterating line by line.
16. **Write safe output** — rewrite a write-heavy function from an
    earlier exercise so that a *processing* error partway through
    cannot leave the output file half-written (§29.2). Note this
    protects against processing failures only, not failures of the write
    itself; true all-or-nothing replacement uses the temporary-file
    strategy (§42.4).
17. **Handle expected exceptions** — take one function from an earlier
    exercise and deliberately test it against every relevant exception
    from §27.1, documenting which you chose to catch and which you let
    propagate, and why (§28).
18. **Separate I/O from domain logic** — take the "BAD" giant-function
    shape from §40.1 (written fresh, on a task of your choosing) and
    refactor it into the improved shape from §40.2.
19. **Write pytest tests** — build a test suite (§39) covering at least
    one function each from Levels 1, 2, and 3, including at least one
    `pytest.raises(...)` test.
20. **Debug broken file-processing code** — take the "BROKEN" sample
    from §37 mistake 7 (loading a huge file with `readlines()`),
    rewrite it to be memory-safe, and write one sentence explaining why
    the original was risky.
21. **Design a reliable file-processing utility** — implement Project 4
    (§44) in full, if you have not already.

## 46. Interview Questions

Answer each in your own words before checking your understanding
against this chapter's relevant section.

1. What is file I/O? (§6)
2. What is a text file? (§5.2)
3. What does `open()` return? (§7.2, §8)
4. What is a file object? (§7)
5. What is the difference between `r`, `w`, `a`, and `x`? (§9.2)
6. Why is `w` dangerous? (§9.4)
7. What happens when a file does not exist, under each of `r`, `w`,
   `a`, and `x`? (§9.2, §10)
8. What is the difference between `read()`, `readline()`, and
   `readlines()`? (§12–§14)
9. Why can `read()` be dangerous for large files? (§30.1)
10. Why is iterating over a file useful? (§15)
11. What does `seek()` do? (§16.3)
12. What does `tell()` do? (§16.2)
13. Why does a second `read()` sometimes return an empty string? (§12.4,
    §16.5)
14. What does `write()` return? (§17.1)
15. Does `writelines()` add newline characters? (§18.2)
16. Why use `with open(...)`? (§21)
17. What happens if an exception occurs inside a `with` block? (§21.3)
18. What is encoding? (§25.1–§25.2)
19. Why is UTF-8 commonly used? (§25.3)
20. What is buffering? (§32.1)
21. What does `flush()` do? (§33.1)
22. What is the difference between an expected operational error and a
    programmer bug? (§28.1)
23. Why avoid `except Exception: pass`? (§27.3)
24. How would you process a 10 GB text file? (§30–§31)
25. How would you test file-processing code? (§39)
26. How would you separate file I/O from business logic? (§40)
27. How would you safely transform a file without corrupting the
    original? (§29.1, §42.4)
28. What can happen if multiple processes write to the same file?
    (§43)

## 47. Knowledge Check

**A. Conceptual**
1. In your own words, explain why file I/O exists as a distinct
   category from ordinary computation.
2. Explain why opening a file does not load its contents into memory.

**B. Code-reading**
3. What does the following print, and why?
```python
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("one")
    f.write("two")
    f.write("three")

with open("data.txt", "r", encoding="utf-8") as f:
    print(f.read())
```

**C. Predict-the-output**
4. What does this print?
```python
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("line1\nline2\nline3\n")

with open("data.txt", "r", encoding="utf-8") as f:
    print(f.readline())
    print(f.readline())
```

**D. File-mode questions**
5. What happens when you open a nonexistent file with `"r"`? With
   `"w"`? With `"x"`?
6. Why does opening a file with `"w"` twice in a row (with no writes in
   between) not raise an error, unlike opening it with `"x"` twice?

**E. Cursor/seek/tell questions**
7. After `f.read()` on a 20-character file, what does `f.tell()`
   report? What does `f.read()` return if called again immediately
   after?
8. What does `f.seek(0)` accomplish, and when would you need it?

**F. Error-handling questions**
9. Which exception is raised by `open("missing.txt", "r", encoding="utf-8")`
   if `missing.txt` does not exist?
10. Should a reusable, low-level `read_text_file(path)` function catch
    `FileNotFoundError` internally? Why or why not?

**G. Memory/performance questions**
11. Why does `for line in f:` use less memory than `f.readlines()` on a
    large file?
12. Why is repeatedly opening and closing the same file inside a loop
    slower than opening it once?

**H. Debugging scenarios**
13. A program raises `UnicodeDecodeError` on one specific file but not
    others. What is the most likely first thing to check?
14. A function that should count 100 lines returns 0 every time. Given
    §37 mistake 15's advice, what is the first thing you should do
    before guessing at a fix?

**I. Small coding tasks**
15. Write a function `last_line(path)` that returns a file's last line
    (newline stripped) — consider whether you can do this while only
    holding a small, bounded amount of data in memory at a time.
16. Write a function `is_empty_file(path)` that returns `True` if a
    file has zero characters, without reading its entire content just
    to check.

**J. Design questions**
17. You need to write a function that reads a file, computes a
    summary, and writes a report. Describe how you would structure it
    to separate I/O from the summarizing logic, and name one concrete
    testing benefit that separation gives you.
18. Two separate programs might append to the same log file at
    overlapping times. What could go wrong, and what does this chapter
    say you should *not* assume about append mode in that situation?

## 48. Final Mastery Checklist

You should be able to confidently say:

- [ ] I understand what a text file is, and how it differs from a
      binary file.
- [ ] I understand file I/O, and why it exists as a distinct category
      from in-memory computation.
- [ ] I understand Python file objects, and why a file object is not
      the file itself.
- [ ] I can use `open()` correctly, including choosing an explicit
      encoding every time.
- [ ] I understand file modes — `r`, `w`, `a`, `x`, and text vs. binary
      — and can predict exactly what happens for each, whether or not
      the file already exists.
- [ ] I can safely read text files, choosing the right approach
      (`read()`, `readline()`, `readlines()`, or iteration) for a given
      situation.
- [ ] I can write text files, understanding that newlines are never
      added automatically.
- [ ] I can append text safely, and understand how it differs from
      write mode.
- [ ] I understand `read()`, `readline()`, `readlines()`, and file
      iteration, and can justify a choice between them.
- [ ] I understand `seek()` and `tell()`, and why a second `read()` can
      unexpectedly return an empty string.
- [ ] I understand `write()` and `writelines()`, including the
      "no automatic newlines" misconception.
- [ ] I understand `close()`, and why forgetting it is risky.
- [ ] I understand context managers (`with open(...) as f:`) deeply,
      including why they guarantee cleanup even under exceptions.
- [ ] I can recognize and handle the standard file exceptions, and I
      distinguish an expected operational error from a programmer bug.
- [ ] I understand basic encoding (UTF-8) and basic newline behavior,
      at the level this chapter establishes.
- [ ] I can process large files without unnecessary memory usage, using
      streaming and chunked reads.
- [ ] I understand buffering and `flush()` conceptually, including
      flush's honest limitations around physical durability.
- [ ] I can design reusable, focused file-I/O functions with clear
      type hints.
- [ ] I can separate file I/O from business/domain logic, by default.
- [ ] I can test file-processing code using temporary files, without
      touching real project data.
- [ ] I can debug file-I/O failures systematically, using a repeatable
      checklist rather than guessing.
- [ ] I understand, at a conceptual level, why multiple writers can
      create correctness problems even in correct Python code.
- [ ] I can design a small, reliable text-file processing utility —
      with reusable functions, type hints, context managers, and
      deliberate error handling — from scratch.

With this foundation in place, you are ready for
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md),
where the plain string paths used throughout this chapter are replaced
with a far more robust, portable way of representing file locations.
