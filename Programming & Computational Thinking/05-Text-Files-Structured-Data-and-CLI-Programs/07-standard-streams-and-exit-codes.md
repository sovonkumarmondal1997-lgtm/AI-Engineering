# Standard Streams and Exit Codes

## Learning Objectives

By the end of this chapter you will be able to:

- Explain, from first principles, what a stream is and why input and
  output are modeled as streams rather than one-shot values.
- Explain stdin, stdout, and stderr precisely — what each is, who
  connects them to what, and why none of them means "the terminal" or
  "the keyboard" by definition.
- Explain how the operating system, the shell, and Python each play a
  distinct role in setting up and using standard streams.
- Use `sys.stdin`, `sys.stdout`, and `sys.stderr` directly, including
  `read()`, `readline()`, `readlines()`, `write()`, `writelines()`,
  `flush()`, `isatty()`, `fileno()`, `readable()`, `writable()`, and
  `seekable()`.
- Explain EOF (end of file) as a stream condition, not a physical
  object, and explain why reading from stdin can appear to "hang."
- Use shell redirection (`>`, `>>`, `<`, `2>`, `2>>`, `&>`) and pipes
  (`|`), and explain precisely which of that behavior is the shell's
  responsibility versus Python's.
- Explain why stdout and stderr are kept separate, and design CLI
  programs that respect that separation so they compose safely into
  pipelines.
- Distinguish text streams from binary streams, and use
  `sys.stdin.buffer` / `sys.stdout.buffer` correctly.
- Explain buffering and flushing, and use `flush=True` deliberately
  rather than out of superstition.
- Use `isatty()` to detect interactive versus non-interactive
  execution, and explain why that matters for color, progress bars,
  and machine-readable output.
- Explain exit codes/exit status: what they are, why `0` conventionally
  means success, and why non-zero does not have one universal meaning.
- Use `sys.exit()`, understand its relationship to `SystemExit`, and
  design a `main() -> int` / `raise SystemExit(main())` architecture.
- Explain how `argparse` uses stderr and exit codes for its own error
  handling, and how that differs from application/domain errors.
- Design CLI output so machine-readable data (stdout) stays clean of
  diagnostics (stderr).
- Use `subprocess.run()` to invoke a child process and inspect its
  `returncode`, `stdout`, and `stderr`, including `capture_output`,
  `text`, `check`, and `input`.
- Explain file descriptors (`fd 0`, `1`, `2`) at a conceptual level
  without confusing them with Python's higher-level stream objects.
- Explain the difference between Python-level stream redirection
  (`sys.stdout = ...`, `contextlib.redirect_stdout`) and OS-level
  redirection, and why the two do not always produce the same result
  for subprocesses.
- Test CLI programs' stdout, stderr, and exit status with pytest,
  understanding the difference between `capsys` and `capfd`.
- Debug common standard-stream problems systematically.
- Recognize the classic mistakes beginners make with streams and exit
  codes, and design around them.
- Explain why standard streams and exit codes are the backbone of
  automation, CI/CD, containers, and orchestration — and, specifically,
  of production data and AI/ML pipelines.

## Prerequisites

This chapter assumes you have already worked through
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)
(file objects, reading/writing text),
[05-encodings-and-newlines.md](05-encodings-and-newlines.md) (text vs.
bytes, encoding/decoding), and
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)
(building a CLI's argument-parsing layer, and the `main(argv) -> int`
pattern this chapter now extends). No prior knowledge of operating
systems, processes, file descriptors, shells, pipelines, or CI/CD is
assumed — every one of those ideas is built from scratch below.

## 1. What Is a Stream?

Start with the plainest possible question: what is data, moving from
one place to another?

- **Data** is just information represented in some computer-readable
  form — text, numbers, bytes.
- **Input** is data flowing *into* a program.
- **Output** is data flowing *out of* a program.

A **stream** is a way of modeling input or output not as one big,
already-complete chunk of data, but as a **flow of data over time** —
data that can be read or written piece by piece, without either side
needing to know, in advance, how much there will be in total or where
it ultimately comes from or goes to. The word "stream" is a deliberate
metaphor: like a stream of water, you can dip into it at any point and
receive some of what's flowing, without needing the whole river
collected in a bucket first.

```
INPUT STREAM:   USER  ──(data flows in)──▶  PROGRAM
OUTPUT STREAM:  PROGRAM ──(data flows out)──▶  USER
```

Applied to the three streams this chapter is about:

```
USER → stdin  → PROGRAM     (input flowing in)
PROGRAM → stdout → USER     (normal output flowing out)
PROGRAM → stderr → USER     (error/diagnostic output flowing out)
```

Why model I/O this way instead of "just pass in a string and get a
string back"? Because a stream lets a program **start producing output
before all the input has even arrived**, and lets it **process input
of any size — a few bytes or many gigabytes — without needing it all
in memory at once**. §30 returns to this in depth once you have the
vocabulary to appreciate why it matters for real data pipelines.

A few distinctions worth fixing early, because beginners routinely
conflate them:

- **Stream vs. file.** A file is one possible *source or destination*
  for a stream — but a stream can just as easily be connected to a
  keyboard, a network socket, another running program, or nothing
  persistent at all. Every file is *streamable*, but not every stream
  is a file.
- **Stream vs. terminal.** A terminal is a program that displays text
  and accepts keystrokes. It is one possible thing a stream can be
  connected to — but, as §2 and §10 show, the exact same program's
  streams might instead be connected to a file or another program
  entirely, with no terminal involved at all.
- **Stream vs. string.** A string is a value that already exists,
  completely, in memory. A stream is a *channel* you read from or
  write to, incrementally; you can accumulate everything a stream
  produces into a single string (`sys.stdin.read()` does this, §5),
  but the stream itself is not a string.
- **Stream vs. bytes.** Bytes are raw numeric data. A stream can carry
  either raw bytes (a *binary* stream) or decoded text (a *text*
  stream) — §13 covers exactly how Python distinguishes the two and
  when each is appropriate.

## 2. The Three Standard Streams

A normal command-line process is conventionally started with **three**
standard streams — stdin, stdout, and stderr — before it runs a single
line of its own code. Their actual connections depend on how the
process was launched:

| Stream | Direction | Python object | Typical purpose | Default interactive destination |
|---|---|---|---|---|
| **stdin** ("standard input") | into the process | `sys.stdin` | receiving input | the terminal keyboard |
| **stdout** ("standard output") | out of the process | `sys.stdout` | the program's normal, intended output | the terminal screen |
| **stderr** ("standard error") | out of the process | `sys.stderr` | diagnostics, warnings, error messages | the terminal screen |

"Standard" here means: a normal command-line process gets these three,
conventionally, regardless of what the program itself does — a program does not have
to request them, open them, or configure them to have them available.
This is what makes them useful as a *default* communication channel:
any program can assume stdin/stdout/stderr exist, without knowing
anything about where they actually lead.

That last point is the single most important idea in this whole
chapter, so it is worth stating as a rule up front, before any code:

> **The exact OS-level destination of each stream depends entirely on
> how the process was launched and what the shell (or parent process)
> connected each stream to.** A program itself has no built-in way of
> knowing, just from the existence of `sys.stdout`, whether its output
> is currently going to a human's screen, a file, or another program.

This is why "stdout means the terminal" and "stdin means the keyboard"
are both wrong, even though they are true in the single most common
*interactive* case. §10–§12 show concretely how the shell can connect
each stream to something else entirely, and §15 shows how a program
can actually detect which situation it's in.

## 3. Standard Streams and the Operating System

To go one level deeper: what does "a process automatically has three
streams" actually mean, mechanically?

A **process** is a running instance of a program — when you type
`python app.py` and press Enter, the operating system creates a new
process to run it. Every process needs some way to read input and
produce output; the operating system provides this through **process
I/O**: a set of open communication channels the process can read from
or write to.

On Unix-like systems (Linux, macOS, and — relevantly for you — the
Linux environment inside WSL2), each of these open channels is
identified by a small non-negative integer called a **file
descriptor**. When a new process starts, the operating system
conventionally sets up three file descriptors before any of the
process's own code runs:

```
fd 0  →  standard input   (stdin)
fd 1  →  standard output  (stdout)
fd 2  →  standard error   (stderr)
```

These specific numbers — 0, 1, 2 — are a **POSIX/Unix convention**,
not a law of physics; they are simply the numbers every Unix-like
operating system, and every tool built on top of it, agrees to use for
this purpose. (Windows uses a different underlying mechanism — handles,
not small integer file descriptors in the POSIX sense — but Python
provides the same portable `sys.stdin`/`sys.stdout`/`sys.stderr`
interface regardless, which is exactly why this chapter teaches the
Python-level model as the thing to rely on, and treats the raw
descriptor numbers as background knowledge rather than something your
code should depend on directly.)

Two levels worth keeping distinct from here on:

```
OS-LEVEL CONCEPT (Unix/POSIX convention):
    0 → standard input
    1 → standard output
    2 → standard error

PYTHON-LEVEL CONCEPT (portable, high-level):
    sys.stdin
    sys.stdout
    sys.stderr
```

Python does not require you to work with the numbers `0`, `1`, `2`
directly for ordinary programs — it wraps the underlying OS resources
in the higher-level `sys.stdin`/`sys.stdout`/`sys.stderr` objects, which
behave like the file objects you already know from
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md),
and which work the same way whether the underlying OS uses POSIX file
descriptors or Windows handles underneath. §36 returns to file
descriptors specifically, once you have more context for why they
occasionally matter even at the Python level.

## 4. Python's `sys.stdin`, `sys.stdout`, and `sys.stderr`

Python exposes the three standard streams as attributes of the `sys`
module:

```python
import sys

print(type(sys.stdin))
print(type(sys.stdout))
print(type(sys.stderr))
```

```bash
python app.py
# <class '_io.TextIOWrapper'>
# <class '_io.TextIOWrapper'>
# <class '_io.TextIOWrapper'>
```

All three are, by default, **text-mode file-like objects** — the same
family of object `open(path, "r")` gives you, supporting the same
general interface. This is deliberate: it means everything you already
know about reading and writing file objects (§ references throughout
this section point back to
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md))
transfers directly to standard streams, with almost nothing new to
learn about the *mechanics* of reading and writing.

`print("hello")` and `sys.stdout.write("hello\n")` are closely related,
but not identical:

```python
print("hello")                 # writes "hello\n" to sys.stdout, using print()'s own conveniences
sys.stdout.write("hello\n")    # writes exactly the bytes/characters you give it — no automatic newline
```

`print()` is a convenience wrapper: it adds a trailing newline
automatically (controlled by `end=`, §7), can print multiple items
separated by spaces (controlled by `sep=`), and can be redirected to a
different stream via `file=` (§8). `sys.stdout.write()` is the lower-
level operation `print()` itself eventually calls — it writes exactly
the string you pass, with no added newline, no separators, and returns
the number of characters written.

The methods and attributes available on these stream objects — the
same ones available on any text-mode file object:

| Method/attribute | Purpose |
|---|---|
| `read(size=-1)` | Read and return up to `size` characters (or everything, if omitted) |
| `readline()` | Read and return one line; the line terminator is included when present (`""` at EOF) |
| `readlines()` | Read and return *all* remaining lines as a `list[str]`; terminators are included when present (the final line may lack one) |
| `write(s)` | Write string `s`; returns the number of characters written |
| `writelines(lines)` | Write an iterable of strings, with **no** automatic newlines added between them |
| `flush()` | Force any buffered data to actually be sent onward now (§14) |
| `isatty()` | `True` if this stream is connected to a terminal/TTY device and is considered interactive (§15) |
| `fileno()` | The underlying OS file descriptor's integer, if one exists (§36) |
| `readable()` | Whether reading is currently supported on this stream |
| `writable()` | Whether writing is currently supported on this stream |
| `seekable()` | Whether the stream supports seeking to an arbitrary position |

`readable()`, `writable()`, and `seekable()` matter because **not every
stream supports every operation** — `sys.stdin` is normally readable
but not writable; `sys.stdout` is normally writable but not readable;
and none of the three standard streams is normally seekable (you
cannot jump backward and forward in a live input/output flow the way
you can in an already-saved file on disk). Checking these
programmatically, rather than assuming, is the safe way to inspect a
stream's actual capabilities before relying on them:

```python
import sys

print("stdin readable:", sys.stdin.readable())
print("stdin writable:", sys.stdin.writable())
print("stdout writable:", sys.stdout.writable())
print("stdin seekable:", sys.stdin.seekable())

print("stdin isatty:", sys.stdin.isatty())
print("stdout isatty:", sys.stdout.isatty())
print("stderr isatty:", sys.stderr.isatty())
```

Exact capabilities can vary depending on how the stream was connected
(an interactive terminal behaves slightly differently from a redirected
file, which behaves differently again from a pipe) — which is exactly
why checking is safer than assuming, and exactly the topic of §15.

Resist the urge to reach for low-level descriptor manipulation
(§36–§37) before you're comfortable with this ordinary, file-like
interface — the overwhelming majority of real CLI programs never need
anything beyond the table above.

## 5. Reading from stdin

Python offers several ways to read standard input, each suited to a
different shape of input.

**`input()`** — the simplest, most familiar option:

```python
name = input("Enter your name: ")
print(f"Hello, {name}")
```

Conceptually, `input()` writes its optional prompt to stdout, then
reads **one line** from stdin, and returns it **with the trailing
newline already stripped**. It is built for the common interactive
case — asking a human one question at a time — and is a thin,
convenient layer over the same underlying `sys.stdin` this whole
chapter is about.

**`sys.stdin.readline()`** — reads exactly one line, but — unlike
`input()` — *keeps* the line terminator when one is present (if the
final line does not end with a newline, the returned string does not
contain one), or returns an empty string, `""`, at EOF (§6), and takes
no prompt argument:

```python
line = sys.stdin.readline()
print(repr(line))   # e.g. "hello\n"
```

**`sys.stdin.readlines()`** — reads **everything** remaining and
returns it as a `list[str]`, one entry per line. Line terminators are included when present; the
final line may not contain one:

```python
lines = sys.stdin.readlines()
print(len(lines), "lines received")
```

**`sys.stdin.read()`** — reads **everything** remaining as a single
string, with no line splitting at all:

```python
everything = sys.stdin.read()
print(len(everything), "characters received")
```

**Iterating directly over `sys.stdin`** — the most common pattern for
line-by-line processing, and the one you will use most in real CLI
tools:

```python
for line in sys.stdin:
    process(line.rstrip("\n"))
```

This is both the most memory-efficient option (§30) and the most
idiomatic — it reads and yields one line at a time, without holding
the whole input in memory the way `readlines()` does.

| Approach | Reads | Returns | Use when |
|---|---|---|---|
| `input()` | one line, minus newline | `str` | simple, one-shot interactive prompts |
| `sys.stdin.readline()` | one line, with its newline when present | `str` (or `""` at EOF) | manual, single-line control |
| `sys.stdin.readlines()` | everything | `list[str]` | need every line available as a list right away, input is known to be small |
| `sys.stdin.read()` | everything | `str` | need the whole input as one blob (e.g. one JSON document) |
| `for line in sys.stdin:` | one line at a time, streaming | (loop variable) | line-oriented processing of input of any size |

## 6. EOF

**EOF** stands for **End Of File** — but despite the name, it does not
require an actual file on disk. EOF is a **condition of a stream**: it
means "there is currently no more data available to read from this
stream, and none is coming." It applies just as much to stdin
connected to a keyboard, a pipe, or a redirected file as it does to an
actual file object.

- When stdin is a **file redirected in** (`python app.py < data.txt`),
  EOF happens naturally once every byte of `data.txt` has been read.
- When stdin is a **pipe** (`producer | python app.py`), EOF happens
  once the producer process finishes and closes its own stdout.
- When stdin is an **interactive terminal**, there is no natural "end"
  — a human could type forever — so the terminal driver provides a way
  to *signal* EOF manually. On most Unix-like terminals (including the
  bash shell inside WSL2), this is conventionally Ctrl+D pressed at the
  start of a line; other environments and shells may use different
  keys or mechanisms, so treat the exact key as an environment
  convention rather than a Python behavior.

In Python, EOF shows up as a specific, checkable value for each reading
method:

```python
line = sys.stdin.readline()
if line == "":            # readline() returns "" exactly at EOF
    print("no more input")

data = sys.stdin.read()   # read() simply returns everything up to EOF, then stops
```

Iterating with `for line in sys.stdin:` stops automatically once EOF is
reached — no explicit check needed; the loop just ends.

Why this matters in practice: **`sys.stdin.read()` (and
`readlines()`, and the `for` loop) will wait — block — until EOF
actually happens**, however long that takes. If you run a script that
reads all of stdin and you launch it directly in an interactive
terminal with no redirection, it will appear to "hang," because it's
correctly waiting for you to either type input and signal EOF
yourself, or provide input some other way. This is not a bug — it is
the stream correctly doing what you told it to do. Understanding this
one behavior resolves a large fraction of "my script just hangs"
confusion for beginners.

This is also exactly why EOF matters for automation: a pipeline stage,
a script, or a CI job that reads all of stdin will naturally, correctly
terminate its read once the upstream process finishes and closes its
output — no special signaling code is needed on either side; EOF *is*
the signal.

## 7. Writing to stdout

`print()` is the everyday tool for producing normal program output; it
writes to `sys.stdout` by default.

```python
print("hello")          # writes "hello\n"
print("hello", end="")  # writes "hello"  (no trailing newline)
print("a", "b", "c")    # writes "a b c\n"  (space-separated by default, via sep=)
```

The lower-level equivalent, using the stream object directly:

```python
sys.stdout.write("hello\n")   # writes exactly this string; no automatic newline, no sep
```

Key `print()` parameters relevant to this chapter:

- **`end=`** — what to print *instead of* the default trailing
  newline. `end=""` suppresses it entirely; useful when building up
  output incrementally without an unwanted blank line.
- **`sep=`** — the separator placed between multiple positional
  arguments (default `" "`).
- **`flush=`** — force the output to be sent immediately rather than
  sitting in a buffer (§14 covers *why* this is ever needed).
- **`file=`** — which stream to write to (default `sys.stdout`; §8 uses
  this for stderr).

stdout should generally carry **exactly the program's intended
output** — the data or result the program exists to produce — and
nothing else. §9 makes the case for this rule in full; for now, the
rule to hold onto is simple: if a downstream reader (a human, another
program, a test) needs the *result*, it belongs on stdout.

## 8. Writing to stderr

Everything a program needs to say that is **not** its actual output —
progress updates, warnings, error messages — belongs on **stderr**,
Python's second standard output stream, reserved by convention for
diagnostics.

```python
import sys

print("this is an error message", file=sys.stderr)
sys.stderr.write("this is also an error message\n")
```

Why a *second* output stream exists at all, rather than one stream for
everything: stdout and stderr let a program produce two independent
channels of output, so that a human or another program consuming the
*result* (stdout) is never forced to also wade through — or
accidentally consume as if it were data — the program's own
commentary about what it's doing (stderr). §9 makes this concrete with
exactly the failure mode this separation prevents.

```python
print("result data")                                   # stdout — the actual output
print("warning: something happened", file=sys.stderr)  # stderr — a diagnostic, not the result
```

Both lines might appear identically, interleaved, on your terminal
screen when you run this normally — because, in the default
interactive case, *both* streams happen to be connected to the same
terminal (§2's table). The distinction only becomes *visible* once one
of the streams is redirected somewhere else — which is precisely the
situation every real automated use of a CLI program is in.

## 9. stdout vs. stderr

This is one of the most important practical ideas in the entire
chapter, so it earns a dedicated, example-heavy section.

**Bad design** — mixing diagnostics into stdout:

```python
print("Loading...")
print("ERROR: invalid input")
print("result data")
```

**Better design** — output on stdout, diagnostics on stderr:

```python
print("result data")                          # stdout
print("Loading...", file=sys.stderr)          # stderr
print("ERROR: invalid input", file=sys.stderr) # stderr
```

Why the difference matters, concretely, consider chaining two programs
together with a pipe (§11 covers pipes in full):

```bash
program_a | program_b
```

This connects `program_a`'s **stdout** directly to `program_b`'s
**stdin** — `program_b` will treat *everything* it receives on that
channel as data to process. If `program_a` writes a line like
`"Loading..."` or `"ERROR: invalid input"` to **stdout** instead of
stderr, `program_b` has no way to distinguish that line from real data
— it will try to parse `"ERROR: invalid input"` as if it were a valid
row of CSV, or a valid line of JSON, and fail in a confusing way that
has nothing to do with the actual problem.

Because `program_a`'s **stderr** is *not* connected to `program_b`'s
stdin by a plain pipe (§11 shows exactly what stderr does in that
setup), keeping diagnostics on stderr means they simply do not
interfere with the data flowing through the pipeline at all — they
remain visible to a human watching the terminal, without ever reaching
`program_b`'s input.

This is the single rule to internalize for the rest of this chapter,
and for every CLI you build from here on:

> **stdout carries the program's actual output. stderr carries
> everything else the program wants to say about itself.** If another
> program might ever consume your output, this separation is not
> optional politeness — it is the difference between a tool that works
> in a pipeline and one that silently corrupts every pipeline it's
> placed in.

## 10. Shell Redirection

The **shell** — the program (typically `bash`, on Ubuntu/WSL2) that
reads what you type and starts other programs — can **redirect** any
of a new process's standard streams to a file, instead of leaving them
connected to the terminal. This is a **shell** feature, resolved
*before* your Python program starts, exactly like the shell parsing
covered in
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
§4 — Python does not perform the shell's redirection setup; the process
starts with its standard streams already connected as arranged by the
shell or parent process. Python can still inspect some properties of
those connections.

| Syntax | Meaning |
|---|---|
| `command > file` | Redirect stdout to `file`, **overwriting** it |
| `command >> file` | Redirect stdout to `file`, **appending** to it |
| `command < file` | Redirect stdin to read from `file` |
| `command 2> file` | Redirect stderr to `file`, overwriting it |
| `command 2>> file` | Redirect stderr to `file`, appending to it |
| `command > file 2>&1` | Redirect stdout to `file`, then also send stderr to wherever stdout now points |
| `command &> file` | A bash shorthand: redirect *both* stdout and stderr to `file` (bash-specific; not identical across every shell) |

Examples:

```bash
python app.py > output.txt          # stdout goes to output.txt; stderr still shows on screen
python app.py 2> errors.txt         # stderr goes to errors.txt; stdout still shows on screen
python app.py > output.txt 2> errors.txt   # each stream goes to its own file
python app.py < input.txt           # stdin is read from input.txt instead of the keyboard
```

The `2` in `2>` is the file descriptor number for stderr (§3's `fd 0/1/2`
convention) — the shell is quite literally saying "redirect file
descriptor 2." Plain `>` and `<` implicitly mean "file descriptor 1"
and "file descriptor 0" respectively — this is not a coincidence; it's
the same numbering convention showing up directly in shell syntax.

Restated as the boundary this chapter keeps returning to:

```
SHELL RESPONSIBILITY:
    deciding what each stream is connected to
    (terminal, file, pipe, /dev/null, another process)

PYTHON RESPONSIBILITY:
    reading from / writing to whichever stream it was handed,
    with no idea (unless it checks, §15) what's on the other end
```

`argparse` (from the previous chapter) never sees or handles any of
this — by the time your Python process starts and `parse_args()` runs,
every redirection the shell was going to do has already happened.

## 11. Pipes

A **pipe** (`|`) connects one process's **stdout directly to another
process's stdin**, without either end touching a file on disk.

```bash
python producer.py | python consumer.py
```

```
producer.py's stdout
        ↓  (pipe)
consumer.py's stdin
```

Each side of the pipe is a genuinely separate, independently-running
process; the operating system moves data from one to the other as it's
produced, without buffering the *entire* output somewhere first (this
is exactly the "flow over time," not "one big finished chunk," idea
from §1, now connecting two real processes).

Critically — and this is where §9's rule pays off directly — **only
stdout is connected by a plain pipe**. `producer.py`'s **stderr**
remains connected to whatever it was connected to before the pipe was
set up (typically, still the terminal), completely separate from
`consumer.py`'s stdin:

```
producer.py stdout  ──▶  consumer.py stdin      (via the pipe)
producer.py stderr  ──▶  (still the terminal, unless separately redirected)
```

This is precisely why a producer that keeps diagnostics on stderr
(§8–§9) is *safe* to pipe into another program, and one that mixes
diagnostics into stdout is not: the pipe faithfully delivers *whatever
is on stdout* to the consumer's stdin, diagnostics included, if they
were mistakenly put there.

## 12. Pipeline Design

Putting §10–§11 together gives the classic Unix design principle this
chapter has been building toward: a well-behaved CLI program should

- read data from **stdin** when it makes sense to (§31),
- write its actual, intended result to **stdout**,
- write diagnostics — progress, warnings, errors — to **stderr**, and
- return a **meaningful exit status** (§17 onward) so whatever called
  it can tell success from failure without parsing text.

A conceptual multi-stage pipeline:

```
source → filter → transform → aggregate
```

```bash
cat data.txt | python filter.py | python transform.py | python aggregate.py
```

Each arrow here is a pipe, connecting one stage's stdout to the next
stage's stdin. `cat` is worth naming explicitly: it is a small,
standard **shell/OS utility** (not a Python feature, and not something
this chapter's Python examples ever need to reimplement) whose entire
job is to print a file's contents to stdout — a natural first stage
for feeding a file into a pipeline of Python programs.

Every stage in a pipeline like this can be developed, tested, and
debugged **independently** — this is the entire payoff of designing
programs around standard streams in the first place: small, focused
programs, each doing one job, composed together at run time by the
shell, with none of them needing to know anything about the others.

## 13. Text vs. Binary Streams

[05-encodings-and-newlines.md](05-encodings-and-newlines.md) covered
the general distinction between `str` (decoded text) and `bytes` (raw
data) in depth; this section covers only how that distinction shows up
specifically for standard streams.

By default, `sys.stdin`, `sys.stdout`, and `sys.stderr` are **text
streams** — reading from them gives you `str`, and writing to them
requires `str`. Internally, each wraps an underlying **binary**
stream, accessible through a `.buffer` attribute where available (the
standard streams normally expose `.buffer`, but code should not assume
every replacement file-like object has this attribute):

```python
sys.stdin.buffer    # the underlying binary input stream
sys.stdout.buffer   # the underlying binary output stream
sys.stderr.buffer   # the underlying binary output stream
```

```python
data = sys.stdin.buffer.read()      # reads raw bytes, no decoding at all
sys.stdout.buffer.write(data)       # writes raw bytes, no encoding at all
```

When is binary access appropriate?

- **Arbitrary bytes that are not text at all** — image data, compressed
  data, serialized binary formats — where decoding as text would be
  meaningless or actively lossy.
- **Exact byte preservation** — a program that must pass data through
  unmodified (a filter that copies stdin to stdout byte-for-byte)
  should use `.buffer` so it never risks a decode/re-encode round trip
  silently altering bytes that don't correspond to valid text in the
  assumed encoding.
- **Binary protocols** built on top of stdin/stdout, where the format
  itself defines byte layout rather than character encoding.

The risk of *not* thinking about this: reading binary data through the
default *text* interface forces Python to decode it using some
encoding (§05's whole chapter on exactly this) — and if the bytes
aren't valid text in that encoding, you get a `UnicodeDecodeError`
(or, worse, silently wrong characters, depending on the error-handling
mode) for data that was never meant to be interpreted as text at all.
For ordinary line-oriented CLI tools working with CSV, JSON, or plain
text, the default text-mode streams are exactly right — reach for
`.buffer` only when the data genuinely isn't text.

## 14. Buffering and Flushing

**Buffering** means: rather than sending every single byte of output
to its destination the instant your code calls `write()`, Python (and
the OS beneath it) often collects output into a temporary in-memory
holding area — a **buffer** — and sends it onward in larger batches.

Why buffer at all? Every actual "send this data onward" operation
(a **system call**, at the OS level) has real overhead. If a program
wrote to disk, or to a pipe, one single character at a time, that
overhead would dominate — buffering collects many small writes into
fewer, larger ones, which is dramatically more efficient for both
disk-backed files and most other destinations.

The cost of buffering: output may not become *visible* to whoever is
reading it immediately after your code calls `write()` or `print()` —
it may sit in the buffer for a while first. This is invisible in the
most common interactive case (where Python's stdout is commonly
**line-buffered** when connected to a terminal — flushed automatically
after each newline), which is exactly why beginners rarely notice
buffering exists until output is redirected or piped, at which point
Python may switch to **block buffering** — larger, less frequent
flushes — because there's no longer a human watching a screen line by
line and the efficiency tradeoff shifts.

`flush()` forces whatever is currently sitting in the buffer to be sent
onward right now, without waiting for the buffer to fill or the
process to end:

```python
print("Starting...", flush=True)      # force this to appear immediately
sys.stdout.flush()                    # force whatever's currently buffered out
```

When flushing matters in practice: a long-running process reporting
progress that should appear in real time (to a human watching, or to
a monitoring system tailing output) needs explicit flushing if its
stdout is not connected to an interactive terminal where line-
buffering would have handled it automatically. When flushing does
*not* matter: for a short program whose output all appears before it
exits, buffered output is flushed automatically when the process
terminates normally — there is no lost data, only a difference in
*timing* of when it becomes visible.

Do not treat buffering as "Python always makes you wait" — the exact
behavior depends on the specific stream and how it's connected
(terminal vs. pipe vs. file), which is precisely why §69 revisits this
at scale, and why flushing should be a deliberate choice (used where
real-time visibility genuinely matters), not a reflex added to every
`print()` call out of uncertainty.

## 15. TTY and `isatty()`

A **TTY** ("teletypewriter," a name inherited from actual hardware
terminals decades ago) is the technical term for an **interactive
terminal** — a program is running with a TTY attached when a human is
directly typing into it and watching its output live, as opposed to
its input or output being a file or a pipe.

```python
import sys

if sys.stdout.isatty():
    print("Interactive terminal")
else:
    print("Output is redirected or piped")
```

`isatty()` tells you, for one specific stream, whether that particular
stream is connected to a terminal/TTY device and is considered
interactive by the underlying stream (it does not prove a human is
actually watching). Each
stream is checked independently — it's entirely possible for stdin to
be a TTY (a human typing) while stdout is redirected to a file, or the
reverse.

Production uses of this check:

- **Progress bars and spinners** — meaningful for a human watching a
  live terminal; meaningless (and often visually broken) if stdout is
  actually a file or another program's input.
- **Color and terminal formatting** (§16) — should generally only be
  emitted when the destination is a real terminal that can render it;
  otherwise a downstream file or program receives raw escape-sequence
  garbage mixed into its data.
- **Interactive prompts** — a program that calls `input()` expecting a
  human to respond should generally check whether stdin is actually a
  TTY first, since there is no human to answer if stdin is a pipe or a
  redirected file.
- **Choosing output mode** — some real tools (`ls`, `git diff`, many
  data tools) automatically switch between a human-friendly, colorized,
  columnar format when writing to a TTY, and a plain, machine-
  consumable format otherwise.

The underlying principle, worth stating directly: **a program should
not blindly emit terminal-specific formatting when its output might be
consumed by another program instead of a human** — exactly the same
concern §9 raised about diagnostics contaminating stdout, now applied
to visual formatting instead of text content.

## 16. Terminal Output and Control Sequences

Terminals can display more than plain characters — colored text, bold
text, and cursor movement are achieved through special character
sequences called **ANSI escape sequences**, embedded directly in the
output text and interpreted by the terminal itself (not by Python).

```python
print("\033[31mThis text is red\033[0m")
```

`\033[31m` switches to red text; `\033[0m` resets formatting back to
normal. A terminal that understands ANSI sequences renders this as
colored text; a program or file that receives this same output as
*data* (not as something meant for a terminal) sees exactly those raw
characters — `\033[31m` and all — mixed into whatever it was trying to
read as data.

This is the whole reason §15's `isatty()` check matters here directly:

```
HUMAN-ORIENTED OUTPUT   →  fine to include color, cursor movement, progress
MACHINE-ORIENTED OUTPUT →  must stay plain — no escape sequences, no formatting
```

This chapter deliberately does not go further into terminal control
sequences — the goal here is only to establish *why* they exist and
*why* a CLI tool must not emit them unconditionally, not to teach
terminal programming.

## 17. Exit Codes / Exit Status

When any process finishes — successfully or not — it reports a single
small integer back to whatever started it (the shell, or another
program): its **exit code**, also called its **exit status**. This is
the process's one, final, structured way of saying "here's how it
went," independent of anything it printed.

```
PROCESS RUNS
    ↓
PROCESS FINISHES
    ↓
PROCESS RETURNS AN EXIT STATUS (a small integer)
    ↓
OS / SHELL / PARENT PROCESS receives it
    ↓
CAN DECIDE: did this succeed or fail?
```

The near-universal convention across Unix-like systems (and respected
by Python and virtually every serious CLI tool):

- **`0`** conventionally means **success** — the process completed
  without error.
- **Any non-zero value** conventionally indicates **some kind of
  failure or abnormal condition**.

Two things worth being precise about, because both are commonly
overstated:

- **Non-zero does not have one single universal meaning.** `1` in one
  program might mean "generic failure"; `1` in a different program
  might mean something specific to that program's own convention. §25
  covers designing your *own* meaningful exit-code scheme.
  There is no single Python-wide or OS-wide law dictating what every
  non-zero number must mean beyond "not success."
- **Exit statuses are integers, but the range and interpretation of
  non-zero values are platform- and convention-dependent.** For
  portable CLI design, prefer small, documented status values and avoid
  relying on large or negative values.

## 18. `sys.exit()` and `SystemExit`

`sys.exit()` is how a Python program requests its own termination with
a specific exit status.

```python
sys.exit()      # exits with status 0 (success) — same as sys.exit(None)
sys.exit(0)     # exits with status 0, explicitly
sys.exit(1)     # exits with status 1 (a generic non-zero failure, by convention)
sys.exit(2)     # exits with status 2 (argparse itself uses this for usage errors — §26)
```

Mechanically, **`sys.exit()` does not immediately kill the process
itself — it raises the built-in `SystemExit` exception.** If nothing
catches that exception, it propagates all the way up, the Python
interpreter recognizes it as a request to terminate, and the process
exits with the given status. This is why `sys.exit()` can, in
principle, be intercepted — like any other exception:

```python
try:
    sys.exit(1)
except SystemExit as exc:
    print("caught it:", exc.code)   # caught it: 1
    # execution continues normally past this point — the process does NOT exit here
```

This matters for two very different reasons:

- **It explains argparse's testability** (from the previous chapter):
  `pytest.raises(SystemExit)` works precisely because `parse_args()`'s
  errors are `sys.exit()` calls underneath, raising a perfectly normal,
  catchable exception — not some untestable, hard OS-level kill.
- **It is a caution, not an invitation.** Catching `SystemExit`
  broadly, in application code, defeats its entire purpose (see §43's
  mistake list) — it exists specifically so a deliberate "stop now"
  request from deep in a call stack can propagate all the way up
  without every intermediate function needing to explicitly check for
  and forward a "should I stop?" signal.

## 19. `main()` Return Values vs. `sys.exit()`

For application code, a strong production pattern — the one this
chapter (and the previous one) has been building toward — is to keep
process termination at the CLI boundary: `main()` returns an exit
status, and the top-level entry point converts it to process
termination:

```python
def main() -> int:
    ...
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Line by line: `main()` is declared to **return an integer** — a
regular Python function return, nothing special about it at the
language level. Only at the very bottom, in the `if __name__ ==
"__main__":` guard, is that returned integer handed to
`raise SystemExit(...)` — which is exactly equivalent to calling
`sys.exit(main())`, since `sys.exit()` is implemented in terms of
raising `SystemExit` in the first place.

Compare this to a naive version:

```python
def main():
    print("done")
```

against:

```python
def main() -> int:
    ...
    return 0

raise SystemExit(main())
```

The naive version has no way to communicate success or failure at all
— whatever called it (a shell script, a test, a CI job) has no exit
status to inspect beyond "did it crash with an unhandled exception."
The `main() -> int` version separates two genuinely different
concerns: **what `main()` computed** (an ordinary return value, freely
testable — a test can call `main([...])` and assert on the returned
integer with no process involved at all, §41) from **how the process
as a whole terminates** (one line, in one place, at the very bottom of
the script, the only place that actually needs to know about
`SystemExit`).

## 20. String Exit Arguments

`sys.exit()` accepts more than just integers.

```python
sys.exit("something went wrong")
```

This differs from `sys.exit(1)` in an important, specific way: passing
a **non-integer** argument causes Python to **print that argument to
stderr**, and the process exits with status **`1`** (a generic
failure). Effectively, `sys.exit("message")` is shorthand for "print
this to stderr, then exit with a generic failure status" — it bundles
the diagnostic message and the exit request into one call.

```python
# roughly equivalent to:
print("something went wrong", file=sys.stderr)
sys.exit(1)
```

Why write it out the long way instead, for production CLIs? Because
the long form gives you **independent control** over the diagnostic
message and the exit status — `sys.exit("message")` always exits with
status `1`, with no way to say "print this message but exit with
status `3`" in one call. For anything beyond a quick script, explicit
control over both — a specific message, and a specific, meaningful
status (§25) — is worth the extra line.

## 21. Exit Codes and Shells

The shell that launched your program can inspect the exit status it
returned. On POSIX-like shells (bash, the default on Ubuntu/WSL2), the
special variable `$?` holds the exit status of the **most recently
completed command**:

```bash
python app.py
echo $?
```

If `app.py` succeeded, this prints `0`. If it failed with, say,
`sys.exit(2)`, this prints `2`.

The shell also provides conditional chaining based on exit status —
these are **shell features**, not Python syntax, and are worth knowing
about conceptually even though this chapter's Python examples don't
need to produce them:

```bash
command && next_command      # run next_command only if command succeeded (exit 0)
command || recovery_command  # run recovery_command only if command FAILED (non-zero exit)
```

This is the mechanism that lets a shell script — or a CI configuration
built out of shell commands — make decisions based purely on exit
status, with no need to inspect or parse any of the command's actual
output text at all.

## 22. Exit Codes and Automation

This is where exit codes stop being a curiosity and become load-
bearing infrastructure. Consider a data-validation script as part of a
larger, unattended pipeline:

```bash
python validate_data.py
```

- **Exit code `0`** → the pipeline can safely continue to its next
  stage.
- **Exit code non-zero** → the pipeline can (and should) stop, fail
  the job, alert someone, or trigger a retry — automatically, with no
  human reading any text.

Why **printing `"ERROR"` to the screen is not sufficient** for
automation: nothing is watching the screen. A cron job, a CI runner, an
orchestrator (§53) — none of them "read" your program's printed output
the way a human would, by default. What they *do* reliably observe,
because the operating system itself reports it, is the numeric exit
status. A program that prints "ERROR: something failed!" in bright red
text but still exits with status `0` will, from the perspective of
every piece of automation built to check exit status (which is nearly
all of it), be reported as **having succeeded** — a genuinely dangerous
and surprisingly common bug.

This is the concrete, practical payoff of everything from §17 onward:
**exit codes are how a program tells automated systems, reliably and
without ambiguity, whether it did its job.**

## 23. Exit Codes in CI/CD

A conceptual continuous-integration (CI) pipeline is, at its core, a
sequence of commands, each gated by the previous one's exit status:

```
checkout
  ↓
install dependencies
  ↓
run tests
  ↓
run lint
  ↓
run type checking
  ↓
build
  ↓
deploy
```

Each stage is, underneath, a command run in a shell — and each command
communicates whether it succeeded purely through its exit status.
`pytest` exits non-zero if any test fails; `ruff` (a linter) exits
non-zero if it finds lint violations; `mypy` (a type checker) exits
non-zero on type errors; build and deployment tools exit non-zero on
their own respective failures. A CI system's job, at the level that
matters here, is simple: **run each command, check its exit status,
and stop (or mark the whole pipeline failed) the moment any command
returns non-zero.**

Exactly *which* non-zero value each of these tools uses, and for
precisely which condition, is specific to that tool's own documented
convention — this chapter does not claim a single shared meaning
across `pytest`, `ruff`, `mypy`, and every other tool; the one thing
they all agree on, by convention, is that `0` means "this stage
passed" and anything else means "this stage did not."

## 24. Error Handling and Exit Codes

Three genuinely different things are easy to conflate, and worth
carefully separating:

```
PYTHON EXCEPTION        — a language-level event signaling something went wrong
        ↓
CLI ERROR MESSAGE        — human-readable text explaining what went wrong (→ stderr)
        ↓
PROCESS EXIT STATUS      — the numeric signal automation actually checks (→ sys.exit code)
```

A raised exception, left uncaught, *does* eventually produce a non-
zero exit status (Python prints a traceback to stderr and exits with
status `1`) — but an uncaught exception's traceback is not designed
for end users, and relying on Python's default uncaught-exception
behavior means you have no control over the exit status used (always
`1`, regardless of what actually went wrong) or the message shown
(a full traceback, not a clean explanation).

The production-oriented pattern: **catch the exception deliberately,
print a clean diagnostic to stderr, and return a specific,
meaningful exit status**:

```python
import sys
from pathlib import Path


def main() -> int:
    try:
        data = Path("input.csv").read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Line by line: the `try` block attempts the real work; the `except
FileNotFoundError as exc` clause catches specifically the failure this
code anticipates (not a bare `except:`, which would also swallow
genuinely unexpected bugs — see §43's mistake list); `print(f"error:
{exc}", file=sys.stderr)` reports the problem on the correct stream
(§8–§9); `return 2` gives `main()`'s caller (ultimately,
`raise SystemExit(main())`) a specific, meaningful, non-zero status,
distinct from a generic `1`.

## 25. Exit-Code Design

Beyond the universal `0 = success` convention, how should a program
choose *which* non-zero value to use for *which* failure? This is an
**application-level design decision** — Python does not mandate a
universal mapping, and no single scheme is "the" Python standard.

A reasonable, self-consistent example convention — explicitly labeled
as one possible scheme, not a rule:

```
0  =  success
2  =  invalid CLI usage           (bad arguments — matches argparse's own convention, §26)
3  =  input/data problem          (the input itself is invalid or malformed)
4  =  configuration problem       (missing/invalid config, env vars, etc.)
5  =  external dependency failure (a network call, a database, another service failed)
```

Whatever scheme you choose for a given tool, the value is in
**consistency and documentation** — every exit code your tool can
produce should be intentional, stable across releases (since scripts
and CI configurations may come to depend on it), and ideally documented
in the tool's own `--help` output or README, so that whatever consumes
your tool's exit status can make reliable decisions based on it.

## 26. `argparse` and Exit Codes

Connecting directly to
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md):
`argparse` has its own, built-in exit-code behavior, entirely separate
from whatever your own application logic decides to return.

- **Invalid command-line usage** — a missing required argument, an
  invalid choice, an unrecognized flag — causes `parse_args()` to print
  a usage message and error to **stderr**, and exit with status **`2`**
  (this is why the example convention in §25 reused `2` for the same
  meaning — deliberately matching argparse's own established
  convention, rather than picking an arbitrary different number for
  the same *kind* of problem).
- **`--help`** prints help text to **stdout** and exits with status
  **`0`** — asking for help is not a failure.
- **`--version`** (§48 of the previous chapter) behaves the same way:
  prints and exits with status `0`.
- **`parser.error(message)`** (used for cross-argument validation,
  §43–§44 of the previous chapter) reports the message on stderr and
  exits with status `2`, exactly like argparse's own built-in parsing
  errors — this is precisely why `parser.error()` is preferred over a
  bare `raise ValueError(...)` for argument-related problems: it
  produces output and an exit status indistinguishable, in shape, from
  every other argparse-detected usage error.

The distinction worth holding onto: **a CLI syntax error** (the user
typed something argparse itself cannot make sense of) is fundamentally
different from an **application/domain error** (the command line was
perfectly valid, but the *data* it points to turns out to be invalid).

```bash
python app.py --unknown          # CLI syntax error — argparse's own job, exit 2
python app.py input.csv          # valid syntax; input.csv exists but contains invalid business data
                                  # — this is YOUR code's job to detect and report (§24–§25)
```

argparse can only ever catch the first kind. The second kind is
exactly what §24's `try`/`except`/`return`-status pattern exists to
handle.

## 27. `parser.error()` and stderr

Restating §26's `parser.error()` behavior with the standard-stream
model made explicit:

```python
parser.error("invalid value for --count")
```

Internally, this prints the parser's usage line, then
`"{prog}: error: invalid value for --count"`, to **stderr** — not
stdout — and then terminates the process with exit status `2`. This
is a direct, concrete instance of §9's separation rule: an error about
*how the program was invoked* is a diagnostic, not the program's
output, so it belongs on stderr, and argparse itself follows that rule
consistently.

## 28. `print()` and stderr

A focused look at the one line that does the actual work behind every
"send this to stderr" example so far:

```python
print("Processing...", file=sys.stderr)
```

`print()` writes to `sys.stdout` **by default** — `file=sys.stderr`
overrides that default for this one call, with everything else about
`print()` (multiple arguments, `sep=`, `end=`, `flush=`) working
identically regardless of which stream it targets.

When is this the right tool? Any time you want a **one-off diagnostic
line**, formatted the same easy way you'd format normal output —
progress messages, a quick warning, a simple error report in a small
script. When might it be *inappropriate*? Once a program's diagnostic
needs grow — multiple severity levels, timestamps, structured
formatting, the ability to turn diagnostics on/off by verbosity — a
scattering of `print(..., file=sys.stderr)` calls throughout the
codebase becomes hard to manage consistently; that growing need is
exactly what
[08-logging-versus-print.md](08-logging-versus-print.md), the next
chapter, exists to address (§46 previews the connection).

## 29. Machine-Readable vs. Human-Readable Output

A production CLI concept that follows directly from everything above:
distinguish output meant for a **human to read** from output meant for
**another program to parse**.

**Human-oriented CLI output:**
```
Processing 100 files...
Done!
```

**Machine-oriented CLI output:**
```json
{"status": "success", "files_processed": 100}
```

Both of these are entirely reasonable outputs for the *same* command —
the difference is *who's consuming stdout*. The critical rule, direct
from §9: **when a program's output might be consumed by another
program (a script, a pipeline stage, a test), stdout should carry
*only* the machine-readable data — clean, parseable, with no
extraneous human-oriented commentary mixed in.**

```python
import json
import sys

result = {"status": "success", "files_processed": 100}

print(json.dumps(result))                                  # stdout: exactly one JSON document
print("warning: skipped 2 unreadable files", file=sys.stderr)  # stderr: a diagnostic, not data
```

A consumer piping this command's output into `json.loads(...)` (or
into a tool like `jq`) can rely on stdout containing *only* valid
JSON, with every diagnostic safely routed elsewhere.

## 30. Streaming Large Data

Returning to §1's original motivation for modeling I/O as streams at
all: what's the actual, concrete benefit for a real CLI program?

**Read everything into memory first:**
```python
lines = sys.stdin.readlines()   # holds ALL lines in memory before processing begins
for line in lines:
    process(line)
```

**Process incrementally, streaming:**
```python
for line in sys.stdin:          # holds only ONE line in memory at a time
    process(line)
```

For a small input, these behave identically from the outside. For a
very large input — a multi-gigabyte log file, a dataset too large to
fit comfortably in RAM — the difference is the difference between
"works" and "crashes with a memory error, or grinds the whole machine
to a halt from swapping." Streaming line-by-line also reduces
**latency**: the first output can be produced as soon as the first
input line has been processed, rather than only after the entire input
has finished arriving — meaningful for a pipeline stage feeding
another stage downstream, which can then start its own work sooner
too.

This connects directly to a concept worth knowing the *name* of, even
at a high level: **backpressure** — in a pipeline of streaming stages,
if a downstream stage is slower than an upstream one, data naturally
accumulates somewhere (in OS-level pipe buffers, primarily) until the
downstream stage catches up; well-designed streaming pipelines rely on
the OS's own pipe mechanism to naturally pace a fast producer against a
slow consumer, rather than needing to buffer unbounded amounts of data
in application memory.

For data engineering and AI/ML work specifically — the long-term goal
this course is building toward — this is not an academic concern:
dataset preprocessing, log analysis, and ETL stages routinely deal with
inputs too large to load wholesale, making the streaming pattern
(§5's `for line in sys.stdin:`) the default, not the exception.

## 31. File-or-stdin Input

A common, genuinely useful CLI pattern: let the same program accept
input either from an **explicit file path** or from **stdin**, so it
works both as a standalone tool and as a pipeline stage.

```bash
python process.py data.csv          # read from a named file
cat data.csv | python process.py    # read from stdin instead
```

A simple, explicit implementation:

```python
import sys
from pathlib import Path


def get_input_lines(input_path: str | None):
    if input_path:
        with Path(input_path).open("r", encoding="utf-8") as handle:
            yield from handle
    else:
        yield from sys.stdin
```

If a path was given, open and read *that* file; otherwise, fall back
to reading from stdin. Keep this pattern this simple and explicit at
first — resist the temptation to build a more "clever" abstraction
(a unified "input source" class, automatic format detection, and so
on) before you've actually needed one; §32 shows the one small,
genuinely standard extension worth knowing.

## 32. The `"-"` Convention

Many established Unix-style command-line tools accept the single
character `"-"` as a stand-in for "standard input" (when reading) or
"standard output" (when writing), instead of a real filename.

```bash
python process.py -
```

This is a **widely used convention**, not a rule Python or the
operating system enforces automatically — nothing makes `"-"` mean
stdin unless the *program itself* is written to check for it and treat
it specially:

```python
import sys
from pathlib import Path


def open_input(path: str):
    if path == "-":
        return sys.stdin
    return Path(path).open("r", encoding="utf-8")
```

Adopting this convention in your own tools is a nice, low-cost way to
make them feel familiar to anyone used to standard Unix tooling — but
it is an explicit design choice your code has to implement, not
something that happens automatically just because a user typed a
dash.

## 33. Subprocess Communication

So far, this chapter has focused on *one* process's own standard
streams. Python's `subprocess` module lets one process — yours —
**start another process** and communicate with it through exactly the
same three streams, from the outside.

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "--version"],
    capture_output=True,
    text=True,
)

print(result.returncode)   # the child process's exit status
print(result.stdout)       # everything the child wrote to its stdout
print(result.stderr)       # everything the child wrote to its stderr
```

Key `subprocess.run()` parameters, in the context of standard streams:

- **`capture_output=True`** — capture the child's stdout and stderr
  into the returned object's `.stdout`/`.stderr` attributes, instead
  of letting them pass through to your own process's streams
  (Python's default, if you don't capture, is for the child to inherit
  your own stdout/stderr directly).
- **`text=True`** — decode the captured output as text (`str`) rather
  than leaving it as raw `bytes` — the same text-vs-binary distinction
  from §13, now applied to a subprocess's output.
- **`input=`** — a string (with `text=True`) or bytes to send to the
  child process's **stdin**, as if it had been piped in.
- **`check=True`** — covered fully in §34.

This chapter deliberately covers only the slice of `subprocess`
relevant to standard streams and exit codes — it is not a full
`subprocess` tutorial.

## 34. `subprocess.run()` and `check=True`

By default, `subprocess.run()` does **not** raise an exception just
because the child process exited with a non-zero status — it simply
records that status in `.returncode`, leaving it up to you to check:

```python
result = subprocess.run([sys.executable, "validate.py", "data.csv"], capture_output=True, text=True)

if result.returncode != 0:
    print(f"validation failed: {result.stderr}", file=sys.stderr)
```

`check=True` changes this: if the child process exits non-zero,
`subprocess.run()` itself raises `subprocess.CalledProcessError`
instead of returning normally:

```python
import subprocess
import sys

try:
    subprocess.run([sys.executable, "validate.py", "data.csv"], check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as exc:
    print(f"validation failed (exit {exc.returncode}): {exc.stderr}", file=sys.stderr)
```

`check=True` is generally the right default for production automation
scripts: it means a failing subprocess produces a clear, catchable
exception immediately, rather than silently continuing and requiring
every single call site to remember to check `.returncode` manually —
exactly the same "fail loudly and immediately" principle §24 applied
to your *own* program's exit status, now applied to a *child*
process's exit status instead.

## 35. Buffering and Subprocesses

At a more advanced level: a parent and child process communicating
through pipes are subject to the same buffering behavior (§14)
independently, on *each* side of the pipe. This has two practical
consequences worth knowing about, even if you rarely need to reason
about them directly when using the high-level `subprocess.run()`:

- **Visibility timing** — if a child process buffers its output
  (because it isn't writing to an interactive terminal — §14's
  block-buffering case), the parent capturing that output may not see
  any of it until the child either flushes or finishes.
- **Careful handling for very interactive, bidirectional
  communication** — designs where a parent needs to send input and
  read output from a child *while it's still running* (not simply
  "run it, then collect everything at the end," which is what
  `subprocess.run()` does) need to manage stdin/stdout/stderr streams
  and buffering carefully, since naive approaches can deadlock (both
  sides waiting on each other) if a pipe's buffer fills up while
  nobody is reading it. `subprocess.run()`'s straightforward
  "run to completion, then hand back everything" model exists
  precisely to avoid this class of problem for the common case; the
  lower-level `subprocess.Popen` interface exposes the raw streams
  directly for the cases that genuinely need bidirectional,
  in-progress communication, at the cost of taking on this
  responsibility yourself.

For the overwhelming majority of CLI and automation work — running one
command, waiting for it, checking its result — `subprocess.run()` as
shown in §33–§34 is sufficient and avoids this entire class of problem.

## 36. File Descriptors

Returning to and deepening §3's OS-level model: a **file descriptor**
is a small non-negative integer that a process uses, on Unix-like
systems, to refer to an open resource it can read from or write to — a
file, a pipe, a socket, or (relevantly here) a standard stream.

```
stdin  → file descriptor 0
stdout → file descriptor 1
stderr → file descriptor 2
```

Python exposes each stream's underlying descriptor via `.fileno()`:

```python
import sys

print(sys.stdin.fileno())   # 0
print(sys.stdout.fileno())  # 1
print(sys.stderr.fileno())  # 2
```

These specific values (`0`, `1`, `2`) are extremely reliable in
practice for the three *standard* streams, precisely because they are
set up by convention before your program even starts — but do not
generalize from this to "any file object's `.fileno()` is predictable"
: any *other* file you open yourself gets whatever descriptor number
the OS happens to assign next, which varies run to run.

The distinction worth holding firmly: a **file descriptor** is a raw
OS-level integer handle; a **Python file object** (`sys.stdout`, or
whatever `open()` returns) is a much richer, higher-level Python object
built *on top of* one — with buffering, text encoding/decoding,
convenience methods, and Python's own object lifecycle, none of which
exist at the raw file-descriptor level. `.fileno()` is the bridge
between the two, used only when something genuinely needs the raw
number (most commonly, when interoperating with lower-level `os`
functions, §37, or certain subprocess/pipe plumbing).

## 37. OS-Level Stream Access

At the lowest practical level, Python's `os` module exposes functions
that work **directly with file descriptor integers**, bypassing the
higher-level file-object interface entirely:

```python
import os

data = os.read(0, 1024)     # read up to 1024 raw bytes directly from fd 0 (stdin)
os.write(1, b"hello\n")     # write raw bytes directly to fd 1 (stdout)
```

`os.dup(fd)` duplicates a file descriptor (creating a second
descriptor pointing at the same underlying resource); `os.dup2(fd,
fd2)` makes `fd2` become a duplicate of `fd`, closing whatever `fd2`
previously pointed to first — this is, at the OS level, literally how
shell redirection (§10) is implemented under the hood: the shell
`dup2`s a newly-opened file onto descriptor 1 (or 2) before the child
process's own code starts running.

**Do not reach for these in ordinary CLI applications.** Every one of
these functions works with raw bytes and raw integers, with none of
the conveniences (buffering, text decoding, `readline()`, error
handling) the higher-level `sys.stdin`/`sys.stdout` objects provide.
They are shown here so that the OS-level model from §3 and §36 has a
concrete, real anchor in actual Python code you might one day encounter
— not as a technique to adopt for everyday programs. If you ever find
yourself reaching for `os.read`/`os.write` in application code, it's
worth pausing to check whether the higher-level stream interface
(§4–§9) can express the same thing more simply and safely.

## 38. Python-Level Stream Redirection

It is possible to simply **reassign** `sys.stdout` (or `sys.stdin`,
`sys.stderr`) to a different object entirely, at the Python level:

```python
import sys
import io

original_stdout = sys.stdout
sys.stdout = io.StringIO()

print("captured, not printed to the terminal")

captured_text = sys.stdout.getvalue()
sys.stdout = original_stdout   # restore it

print("this appears normally again")
print(captured_text)
```

This is genuinely useful — most commonly in **tests**, where capturing
what a function printed, without it actually reaching the real
terminal, lets a test assert on the captured text directly (§39's
`contextlib` versions do this more safely; §40's pytest `capsys` does
it for you automatically).

The distinction to hold onto, carefully: this is **Python-level**
redirection — it changes what the name `sys.stdout` refers to, *inside
this one Python process*. It has **nothing to do** with OS-level
redirection (§10, §37) — it does not touch file descriptor 1, does not
affect any C-level code that might write directly to the real
stdout, and — importantly — **does not affect any subprocess you
launch**, since a subprocess inherits actual OS-level file descriptors
from the parent process, not Python variable bindings. Reassigning
`sys.stdout` in the parent process has no effect whatsoever on what a
child process launched via `subprocess` considers "its" stdout to be.

## 39. `contextlib.redirect_stdout` / `redirect_stderr`

`contextlib.redirect_stdout` and `redirect_stderr` are the safer,
standard-library way to do exactly what §38 did manually — temporarily
redirect a stream, guaranteed to restore it afterward even if an
exception occurs partway through:

```python
import io
from contextlib import redirect_stdout

buffer = io.StringIO()

with redirect_stdout(buffer):
    print("this is captured, not printed")

captured_text = buffer.getvalue()
print("outside the block again:", captured_text.strip())
```

`redirect_stderr` works identically, for `sys.stderr`.

When these are genuinely useful:

- **Testing** — capturing what a function under test printed, for
  assertion, without needing pytest's own fixtures.
- **Capturing output from legacy or third-party code** that only knows
  how to `print()`, when you need that output as a string instead
  (e.g., to log it, transform it, or include it in a report).
- **Controlled application behavior** — temporarily silencing or
  redirecting output from a specific block of code, deliberately and
  narrowly scoped with `with`.

The limitations, stated as plainly as §38's: these context managers
**redirect Python-level stream objects only**. They do **not**
automatically redirect every possible OS-level write — code that
writes directly to file descriptor 1 via `os.write(1, ...)` (§37),
bypassing `sys.stdout` entirely, is unaffected; and **subprocesses
launched from inside the `with` block do not inherit this redirection**
unless you separately arrange (via `subprocess.run(..., stdout=...)`)
for the child's stdout to be captured too. This distinction — Python-
level vs. OS-level — is exactly why pytest offers *two* different
capturing mechanisms, covered next.

## 40. Testing Standard Streams

Testing a CLI program's stdout, stderr, and exit status is a natural
extension of the previous chapter's `main(argv)` testing pattern.

```python
from mytool.cli import main


def test_success_prints_result(capsys):
    status = main(["--input", "data.csv"])

    captured = capsys.readouterr()
    assert status == 0
    assert "result" in captured.out
    assert captured.err == ""


def test_missing_file_reports_error(capsys):
    status = main(["--input", "does-not-exist.csv"])

    captured = capsys.readouterr()
    assert status != 0
    assert "error" in captured.err
    assert captured.out == ""
```

`capsys` is a pytest fixture that captures `sys.stdout` and
`sys.stderr` **at the Python level** — the same mechanism §38–§39 just
covered — and makes them available through
`capsys.readouterr().out` / `.err`. It is fast, simple, and correct
for the overwhelming majority of CLI tests, because most CLI code
writes through `print()`/`sys.stdout`/`sys.stderr` directly.

`capfd` is the alternative, capturing **at the file-descriptor level**
(fd 1 and fd 2, §36) instead — meaning it also captures output written
by C extensions, by `os.write()` directly (§37), and by **subprocesses**
launched during the test, none of which `capsys` sees (because none of
those write through Python's `sys.stdout` object at all).

| Fixture | Captures | Use when |
|---|---|---|
| `capsys` | Python-level `sys.stdout`/`sys.stderr` writes | Testing ordinary Python code (the common case) |
| `capfd` | OS-level file descriptor 1/2 writes | Testing code that spawns subprocesses, or calls into C extensions that write directly |

Reach for `capfd` specifically when a test needs to observe output
that bypasses `sys.stdout`/`sys.stderr` entirely — otherwise `capsys`
is simpler and is the right default.

## 41. CLI Testing Strategy

A systematic test matrix worth applying to any real CLI program, in
the same spirit as
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
own testing sections:

| Case | stdin | stdout | stderr | exit code |
|---|---|---|---|---|
| 1. valid input | well-formed data | expected result | empty | `0` |
| 2. empty input | nothing (immediate EOF) | empty or documented "no data" result | possibly a warning | `0` or a documented non-zero, depending on design |
| 3. malformed input | invalid data | empty | clear error message | non-zero |
| 4. missing file | n/a | empty | "file not found"-style message | non-zero |
| 5. invalid argument | n/a | empty | argparse usage error | `2` (argparse's convention, §26) |
| 6. permission problem | n/a | empty | clear permission error | non-zero |
| 7. unexpected exception | n/a | empty (ideally) | clean diagnostic, **not** a raw traceback | non-zero |

Each row exists to verify a specific claim this chapter has made:
success stays quiet on stderr; failures stay quiet on stdout (§9);
every kind of failure produces a *distinguishable*, non-zero status
(§24–§25); and — for case 7 specifically — that unexpected exceptions
are caught and reported cleanly rather than leaking an unhandled
traceback to end users (§24's `try`/`except` pattern is precisely what
makes this last row pass).

## 42. Debugging Standard Stream Problems

A systematic checklist for the recurring standard-stream failure
modes:

**Output appears in the wrong place / pipeline receives invalid data**
→ Check whether diagnostics are being written to stdout instead of
stderr (§9). Run the command alone (without the pipe) and inspect
stdout and stderr separately (`command > out.txt 2> err.txt`, §10) to
see exactly what's on each stream.

**Command hangs, apparently doing nothing**
→ It is very likely waiting for EOF on stdin (§6) — check whether the
command expects piped/redirected input and is instead connected to an
interactive terminal with no input forthcoming. Provide input, redirect
from a file, or press the terminal's EOF key (commonly Ctrl+D on
Ubuntu/WSL2's bash) to confirm this diagnosis.

**Output appears late, or not until the process ends**
→ Check buffering (§14) — is the destination a pipe or file (block-
buffered) rather than an interactive terminal (commonly line-buffered)?
Add `flush=True` where real-time visibility matters, and confirm with
`isatty()` (§15) what kind of stream you're actually connected to.

**Process reports success despite an obvious failure**
→ Check the actual exit status (`echo $?`, §21), not just what was
printed — confirm the code path that failed is actually returning (or
`sys.exit`-ing with) a non-zero value, rather than falling through to
`return 0` regardless (§43's mistake list covers this directly).

**CI says the command failed, but it "looks fine" when run locally**
→ Compare exit status explicitly (`echo $?`) rather than trusting
visual output; check whether the local run and the CI run differ in
whether streams are connected to a TTY (`isatty()`, §15) — a program
that behaves differently under redirection than interactively is
exactly the failure mode §12's design principle exists to prevent.

**stderr is unexpectedly empty despite an apparent problem**
→ Check whether the failure is being caught somewhere and silently
discarded (a bare `except: pass`, §43's mistake list) instead of being
reported.

**stdout is unexpectedly empty**
→ Check whether output is being sent to stderr by mistake, whether an
exception is occurring *before* the intended `print()` call is
reached, or whether buffered output was never flushed before an abrupt
process termination.

Tools and techniques to reach for while debugging, referenced
throughout this list: `echo $?` (§21), explicit redirection to
separate files (§10), `isatty()` (§15), `flush()` (§14), Python's
`logging` module for structured diagnostics (briefly previewed in
§46), subprocess `.returncode` inspection (§34), and pytest's
`capsys`/`capfd` (§40) for reproducing the exact behavior in a test.

## 43. Common Beginner Mistakes

1. **Mixing errors into stdout.** *Wrong:* `print("ERROR: bad input")`
   with no `file=sys.stderr`. *Why wrong:* corrupts any pipeline
   consuming this program's output (§9). *Correct:*
   `print("ERROR: bad input", file=sys.stderr)`.

2. **Assuming stdout always goes to the terminal.** *Wrong:* designing
   output assuming a human is always watching. *Why wrong:* stdout is
   frequently redirected or piped (§2, §10–§11). *Correct:* design for
   the possibility that stdout is a file or another program's input.

3. **Assuming stdin always comes from the keyboard.** Same underlying
   mistake, applied to input — stdin can be a file or a pipe (§2, §11).

4. **Forgetting that stdin may be a pipe/file.** A related, common
   consequence: writing code that only ever works when run
   interactively, and breaks silently (or hangs) the first time it's
   used in a script.

5. **Reading stdin until EOF without understanding why it waits.**
   *Wrong:* calling `sys.stdin.read()` in an interactive terminal and
   being confused when the program appears to hang. *Correct
   understanding:* it is correctly waiting for EOF (§6) — provide
   input and signal EOF, or redirect from a file.

6. **Assuming `print()` means "display on screen."** *Correct
   understanding:* `print()` writes to `sys.stdout`; where that
   *appears* depends entirely on what stdout is connected to (§2, §7).

7. **Assuming stderr is only for Python exceptions.** *Correct
   understanding:* stderr is the conventional destination for *any*
   diagnostic — warnings, progress messages, and deliberate error
   reports, not solely uncaught tracebacks (§8).

8. **Ignoring exit codes entirely.** *Wrong:* a script that never
   calls `sys.exit()` and never returns a meaningful status from
   `main()`, so it falls through normally and exits with status `0`
   even if it printed an error message. *Why wrong:* automation checking this program's exit
   status can never detect its failures (§22).

9. **Returning `1` for every possible situation without a reason.**
   *Why wrong:* loses the ability to distinguish different failure
   *kinds* (§25) — automation, and humans reading logs, can no longer
   tell "bad input" from "missing dependency" from "config error" just
   from the exit status.

10. **Using `sys.exit()` deep inside business logic unnecessarily.**
    *Why wrong:* unnecessarily couples ordinary domain logic to process termination,
    making it harder to test and reuse because callers must handle
    `SystemExit` rather than an ordinary return value or exception. *Correct:* raise a regular
    exception; let `main()` (§19, §24) be the one place that translates
    it into an exit status.

11. **Using low-level file descriptors too early.** *Why wrong:*
    `os.read`/`os.write` (§37) discard every convenience the
    higher-level stream objects provide, for no benefit in ordinary
    CLI code.

12. **Forgetting flush behavior.** *Wrong:* assuming output written a
    moment ago must already be visible somewhere else (a log file
    being tailed, another process reading a pipe). *Correct:* flush
    explicitly (§14) when real-time visibility genuinely matters.

13. **Assuming `isatty()` always returns `True`.** *Why wrong:* it
    reflects the *actual* current connection (§15) — assuming it's
    always a terminal breaks the moment the program is redirected,
    piped, or run in CI/a container (§52), none of which are TTYs.

14. **Printing progress information to stdout in a machine-readable
    CLI.** *Why wrong:* directly violates §29's separation — a
    consumer expecting clean JSON (or CSV, or any parseable format) on
    stdout receives corrupted, unparseable data instead.

15. **Treating shell redirection syntax as Python syntax.** *Wrong:*
    expecting `>`, `<`, `|`, `2>` to mean something inside a Python
    string or to be interpretable by `argparse`. *Correct
    understanding:* these are resolved entirely by the shell, before
    Python ever runs (§10).

16. **Assuming Python-level stream redirection affects child
    processes.** *Wrong:* reassigning `sys.stdout` and expecting a
    `subprocess.run(...)` call afterward to somehow write into it.
    *Correct understanding:* §38–§39 — Python-level redirection has no
    effect on OS-level descriptors a subprocess inherits.

17. **Confusing exceptions with process exit status.** *Correct
    understanding:* §24 — an exception is a language-level event; an
    exit status is the OS-level final report; the two are related only
    because your code (or Python's own default handling) chooses to
    convert one into the other.

18. **Using string output to indicate failure but returning exit code
    `0`.** *Why wrong:* the single most dangerous variant of mistake
    8 — automation checking exit status will report success even
    though the printed text says "failed" (§22).

19. **Catching every exception and hiding useful failures.** *Wrong:*
    a bare `except:` (or `except Exception:`) that silently swallows
    everything, including genuinely unexpected bugs, and continues as
    if nothing happened. *Correct:* catch specific, anticipated
    exceptions (§24), and let unexpected ones propagate (or be caught
    once, logged clearly, and reported with a non-zero status) rather
    than disappearing silently.

20. **Building a CLI that works interactively but breaks in
    pipelines.** The cumulative failure mode of mistakes 1–3, 6, 13,
    and 14 together — a program developed and tested only by running
    it directly in a terminal, never verified under redirection or in
    a pipe, where several of its assumptions quietly stop holding.

## 44. Bad vs. Good CLI Design

**Bad — diagnostics mixed into stdout, breaking pipelines:**
```python
print("Loading...")
print("ERROR: invalid data")
print(json.dumps(result))
```

**Good — clean separation:**
```python
print(json.dumps(result))                          # stdout: the actual output
print("Loading...", file=sys.stderr)                # stderr: a diagnostic
print("ERROR: invalid data", file=sys.stderr)        # stderr: a diagnostic
```

**Bad — `sys.exit()` buried inside business logic:**
```python
def process():
    ...
    sys.exit(1)   # kills the whole process from deep inside domain logic
```

**Good — exceptions from domain logic, translated to exit status at
the top:**
```python
def process():
    ...
    raise ValueError("invalid record at line 42")


def main() -> int:
    try:
        process()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The architectural point behind both "good" examples is the same one
this chapter keeps returning to: **`process()` (or any function like
it) should have no idea a CLI, an exit status, or even `sys.exit`
exists.** It does its job and reports a problem the normal Python way
— an exception. Exactly **one** place in the program — `main()`, and
specifically the boundary in §19's `raise SystemExit(main())` line —
is responsible for turning that into stdout/stderr output and a
process-level exit status. This keeps `process()` trivially testable
(call it directly, assert it raises `ValueError` with pytest's
`pytest.raises`) and keeps the "how does this talk to the OS" concern
in exactly one, easy-to-audit location.

## 45. Production CLI Architecture

Putting every layer of this chapter together into one pipeline,
directly extending
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
own `parse → validate → dispatch → domain logic` shape:

```
parse arguments            (argparse — previous chapter)
        ↓
validate input             (cross-argument checks, file existence)
        ↓
build configuration        (a typed Config object, not a raw Namespace)
        ↓
run domain logic           (pure business logic — no I/O streams, no argparse)
        ↓
produce normal output  →  stdout
        ↓
diagnostics             →  stderr
        ↓
return status
        ↓
raise SystemExit(main())
```

The three layers worth keeping visually and structurally separate:

- **CLI layer** — parsing, `main()`, stream I/O, exit-status
  translation. This is the *only* layer that should import `sys`,
  call `print()`, or know that `sys.exit`/`SystemExit` exist.
- **Domain/application layer** — the actual logic (validating a
  record, transforming data, running a computation). Communicates
  success/failure through ordinary Python return values and
  exceptions — nothing about streams or exit codes.
- **I/O layer** — reading/writing files, calling external services.
  Sits underneath the domain layer, and is itself unaware of the CLI.

This is not a new lesson invented for this chapter — it is the direct,
necessary extension of the previous chapter's architecture once a
program actually needs to communicate results, diagnostics, and
success/failure to the outside world, not just parse its own
arguments.

## 46. Standard Streams and Logging

`print()`, stdout, and stderr, as covered in this chapter, are a
perfectly adequate way to communicate with the outside world for many
programs — but they have real limits: no severity levels (is this an
informational message or a genuine error?), no built-in timestamps, no
easy way to turn verbosity up or down, and no structured place to send
output other than "whichever stream you picked at the `print()` call
site."

Python's `logging` module, the subject of the next chapter
([08-logging-versus-print.md](08-logging-versus-print.md)), builds on
top of exactly the same underlying concepts this chapter established —
by default, Python's logging system sends output to stderr, using the
same standard-stream model — while adding severity levels (`DEBUG`,
`INFO`, `WARNING`, `ERROR`, `CRITICAL`), configurable formatting,
timestamps, and the ability to route different messages to different
destinations (a file, a monitoring system, the console) without
changing the code that calls the logger.

The conceptual bridge to hold onto going into that chapter: **stdout is
the program's actual output; stderr conventionally carries
diagnostics; `logging` is a more capable, structured way of producing
those diagnostics once `print(..., file=sys.stderr)` calls scattered
through a codebase stop being enough.** This chapter does not attempt
to teach `logging` itself — that is the next chapter's full job.

## 47. Security Considerations

Standard streams and exit codes intersect with security in a few
specific, practical ways:

- **Never print secrets to stdout or stderr.** Both streams are
  routinely captured, logged, and stored — by CI systems, by log
  aggregators, by anyone redirecting output to a file (§10) — often
  for much longer than the process itself runs. A password, API key,
  or token printed "just for debugging" can end up persisted somewhere
  you don't control and can't easily delete.
- **Command-line arguments themselves can expose sensitive values** —
  this was covered in depth in
  [06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
  security section, and applies directly here too: a secret passed as
  a CLI argument can be visible to other users on the same system for
  as long as the process runs, independent of what it prints.
- **Pipelines and redirection can record output persistently.** A
  command run as `mytool | tee log.txt` (or any redirection to a file)
  turns transient terminal output into a persistent artifact — treat
  anything your program writes to stdout/stderr as potentially
  long-lived, not necessarily ephemeral.
- **Sanitize error messages.** An exception message containing a raw
  file path, an internal stack trace, a database connection string, or
  other internal detail can leak more about your system's internals
  than intended if printed directly to a user-facing stderr message —
  especially in a CLI tool distributed beyond a small, trusted team.
  Show a clean, user-facing message; reserve full internal detail for
  a controlled logging destination (§46) rather than stderr shown to
  every user.
- **Understand what subprocesses inherit.** By default, a subprocess
  started with `subprocess.run()` (§33) inherits the parent's
  environment variables and, unless explicitly captured, its
  stdout/stderr — meaning secrets available to the parent process are,
  by default, also available to any child process it starts. Be
  deliberate about what a subprocess actually needs, rather than
  assuming isolation that isn't there by default.

## 48. Performance Considerations

- **Buffering exists for performance** (§14) — it reduces the number
  of actual system calls needed to move a given amount of data, which
  matters more as output volume grows.
- **Streaming avoids unnecessary memory usage** (§30) — for large
  inputs, line-by-line processing keeps memory proportional to one
  line, not to the entire input.
- **Excessive, unnecessary flushing can hurt performance.** Calling
  `flush()` (or `print(..., flush=True)`) after every single line of a
  high-volume output stream defeats the purpose of buffering entirely,
  reintroducing the per-write overhead buffering exists to avoid.
  Reserve explicit flushing for cases where real-time visibility is
  genuinely required (§14) — a progress indicator, a health-check
  response — not as a habit applied to every write.
- **Line-by-line processing has its own overhead** relative to reading
  larger chunks at once — for extremely high-throughput scenarios, the
  right chunk size is a real tuning question, but for the overwhelming
  majority of CLI and data-processing tools, `for line in
  sys.stdin:`'s line-oriented streaming is both simple and fast enough.
- **stdout/stderr volume matters.** A program that logs excessively —
  especially to stderr, at a fine-grained "every record" level — can
  itself become the bottleneck, particularly once that output is being
  captured, forwarded, and stored by some other system (§46, §53) at
  the other end.

## 49. Cross-Platform Considerations

You are developing on **Linux, via WSL2** — a genuine Linux
environment — which is the most directly POSIX-compliant, predictable
environment for everything in this chapter. Still, it's worth knowing
what does and doesn't generalize:

- **File descriptor conventions** (fd 0/1/2, §3, §36) are a POSIX/Unix
  convention, shared by Linux and macOS. Windows uses a different
  underlying mechanism (handles), but Python's `sys.stdin` /
  `sys.stdout` / `sys.stderr` present the *same* portable interface on
  every platform Python supports — this is precisely why this chapter
  teaches primarily at the Python level, treating raw descriptor
  numbers as background context rather than something your code
  should depend on directly.
- **Shell redirection syntax** (§10) as shown (`>`, `2>`, `|`) is bash
  syntax, used by the default shell on Linux/WSL2/macOS. Windows'
  `cmd.exe` and PowerShell have their own, different redirection
  syntax (PowerShell's is closer to bash's in spirit but not
  identical) — the *concept* of redirection generalizes; the *exact
  syntax* does not.
- **Checking exit status from the shell** (§21's `echo $?`) is
  bash/POSIX-shell syntax. PowerShell uses `$LASTEXITCODE` (for native
  executables) or `$?` (a boolean, with different semantics than
  bash's numeric `$?`); `cmd.exe` uses `%ERRORLEVEL%`. Again, the
  underlying *concept* — a numeric exit status the calling shell can
  inspect — is the same across platforms; the syntax to inspect it is
  not.
- **Terminal/TTY behavior** (§15–§16) exists conceptually on every
  major platform, but the exact mechanisms and available escape-
  sequence support can differ, particularly on older Windows consoles
  (modern Windows Terminal has broad ANSI support; this chapter
  doesn't attempt to catalog every historical exception).
- **The Python-level abstractions in this chapter — `sys.stdin`,
  `sys.stdout`, `sys.stderr`, `sys.exit()`, `subprocess.run()` — are
  designed to be portable**, working the same way (from your code's
  perspective) regardless of platform. Writing code against these
  interfaces, rather than against raw OS-specific mechanisms, is
  exactly how you get code that behaves consistently on Linux, macOS,
  and Windows without needing separate code paths.

## 50. Real-World Use Cases

For each, note how stdin, stdout, stderr, and exit codes are typically
used:

1. **Data ingestion CLI** — stdin/file for raw records in; stdout for
   a machine-readable ingestion summary; stderr for per-record
   warnings; exit code reflects whether ingestion as a whole succeeded.
2. **CSV validation CLI** — file or stdin for the CSV; stdout for a
   pass/fail summary (often JSON); stderr for specific row-level
   validation errors; non-zero exit if any row failed.
3. **JSON transformation CLI** — stdin for input JSON, stdout for
   transformed JSON — a classic pipeline filter (§12); stderr for
   malformed-input diagnostics.
4. **ETL pipeline stage** — reads from the previous stage's stdout
   (via a pipe) or a file; writes to stdout for the next stage; exit
   code determines whether the orchestrator (§53) proceeds to the next
   stage.
5. **Log processing tool** — streams potentially huge log files
   line-by-line from stdin (§30); stdout for extracted/aggregated
   results; stderr for parse warnings on malformed log lines.
6. **ML dataset preprocessing** — file or stdin for raw records;
   stdout for processed records (often JSON Lines, one record per
   line — a naturally streaming format); stderr for records rejected
   during cleaning; exit code reflects whether preprocessing completed
   within acceptable failure thresholds.
7. **Model evaluation CLI** — reads predictions and ground truth (file
   or stdin); stdout for a machine-readable metrics summary; stderr
   for warnings about missing or misaligned records; exit code can
   reflect whether evaluation itself succeeded (distinct from whether
   the model's *scores* were good).
8. **Batch inference tool** — streams input records in, streams
   predictions out — another natural fit for line-oriented stdin/stdout
   streaming (§30); stderr for per-record inference failures; exit
   code reflects whether the batch run completed.
9. **AI evaluation pipeline stage** — composes with other stages via
   pipes (§11–§12), exactly like any other ETL stage; machine-readable
   stdout is what makes automatic composition with the next stage
   possible at all.
10. **Deployment validation command** — checks a deployed system's
    health/configuration; stdout for a validation report; exit code
    `0`/non-zero is exactly what a deployment script or CI job (§23)
    uses to decide whether to proceed or roll back.
11. **CI validation script** — any script run as a CI step; its exit
    code, and *only* its exit code, is what determines whether that
    step (and often the whole pipeline) is marked passed or failed
    (§23).
12. **Production health-check CLI** — stdout for a status summary
    (often consumed by another automated system); exit code `0` means
    healthy, non-zero means unhealthy — frequently the *only* signal an
    orchestrator (§53) actually inspects, with the printed text purely
    for humans debugging after the fact.

## 51. Applied AI Engineering Connection

Every one of §50's use cases points at the same underlying reason this
chapter matters specifically for an Applied AI Engineer: **the tools
you build — dataset validators, preprocessing steps, training-job
wrappers, evaluation harnesses, batch inference scripts, deployment
checks — are rarely run once, by hand, and read by a human on the
spot.** They are run by other programs: schedulers, CI pipelines,
orchestration systems, other scripts, and — increasingly — by
autonomous agents and tool-calling systems that invoke a command and
need a reliable, structured way to know what happened.

A concrete example, tying the whole chapter together:

```bash
python validate_dataset.py data.jsonl
```

```
stdin:      not used here (data.jsonl is a named file, not piped in)
stdout:     a machine-readable validation summary, e.g. {"valid": true, "records": 10000}
stderr:     warnings/errors — e.g. "warning: 3 records missing 'label' field"
exit code:  0  → validation passed, safe for the pipeline to continue
            non-zero → validation failed; the pipeline should stop, alert, or retry
```

This exact shape — clean machine-readable stdout, diagnostics on
stderr, a meaningful exit code — is what makes this script a **reliable
building block** other systems can depend on without ever needing to
parse its printed text to figure out whether it "really" succeeded.
Every layer above it — a CI job, an orchestrator (§53), a container
scheduler (§52), or an agent deciding whether to proceed to the next
step of a multi-step task — can make that decision correctly using
nothing but the exit code, exactly as designed since §22.

## 52. Containers

A **container** (Docker being the most common example) runs a program
as an isolated process — and that process still has exactly the same
three standard streams, and still reports an exit status when it
finishes, as any other process. This is not a special containerized
concept — it is the exact same OS-level model from §3, simply running
inside an isolated environment.

Why this matters more, not less, inside containers: a containerized
application typically has **no terminal, no interactive user, and no
GUI at all** — its stdout and stderr, captured by the container
runtime, are frequently the *only* way to observe what it did, and its
exit status is frequently the *only* signal the surrounding
orchestration system (§53) uses to decide whether the container
"succeeded." Container logs, in most container platforms, are
literally just captured stdout and stderr — this is a direct,
practical continuation of everything §7–§9 covered, now with the
"reader" being a log-aggregation system instead of a human at a
terminal.

This chapter does not teach Docker itself — only the standard-stream
and exit-code behavior every containerized process shares with every
other process this chapter has discussed.

## 53. Orchestration

Generalizing beyond any one specific tool: an **orchestrator** — a
workflow engine, a scheduler, a CI/CD system, or any system whose job
is to run a sequence of tasks and react to their outcomes — follows
essentially the same conceptual loop everywhere:

```
Task
 ↓
run process
 ↓
capture stdout/stderr
 ↓
inspect exit code
 ↓
decide success/failure
 ↓
retry / alert / continue
```

Whether the specific system is a workflow engine like the kind used
for data pipelines, a CI/CD platform, a batch job scheduler, or a
custom production automation script, the mechanism it relies on is
identical to everything this chapter has built up to: run a process,
capture its two output streams, check its exit status, and make a
decision based on that status — usually completely independent of
whatever the process actually printed. This chapter deliberately
avoids tying this concept to one specific named orchestration product,
since the underlying model — the same one from §22's automation
discussion — is common to essentially all of them.

## 54. Advanced Process Model

A fuller picture of the parent/child relationship `subprocess` (§33)
sits on top of:

```
PARENT PROCESS
    │
    ├── starts ──▶ CHILD PROCESS
    │
    ├── connects child's stdin  ──▶ (inherited, a pipe, or a file)
    ├── connects child's stdout ──▶ (inherited, a pipe, or a file)
    ├── connects child's stderr ──▶ (inherited, a pipe, or a file)
    │
    └── waits, then receives the child's exit status
```

When a parent process starts a child without explicitly configuring
its streams, the child **inherits** the parent's own stdin/stdout/
stderr by default — meaning, unless told otherwise, a child writes to
exactly wherever the parent's own output was already going. When a
parent uses `subprocess.run(..., capture_output=True)` (§33), it
instead creates **pipes** connecting the child's stdout/stderr back to
the parent, letting the parent read whatever the child produced as
data, rather than having it pass straight through.

This is the general mechanism `subprocess.run()` builds a convenient,
high-level interface on top of — the same pipe concept from §11,
between the same conceptual roles (a producer and a consumer of a
stream), just with Python code, rather than the shell, wiring up which
process gets which end of which pipe.

## 55. Exit Status vs. Signal Termination

One further distinction worth knowing at a conceptual level, without
overcomplicating it: a process can end in (at least) two genuinely
different ways.

- **Normal termination with an exit status** — everything this chapter
  has covered: the process runs its code to completion (or calls
  `sys.exit()`/lets an exception propagate to the top) and reports a
  small integer status, as described throughout §17–§25.
- **Termination by a signal** — on systems that support POSIX-style
  signals (Linux, macOS), a running process can also be interrupted
  or killed *from outside itself* — for example, a user pressing
  Ctrl+C sends an interrupt signal to the foreground process, or an
  external tool sends a termination signal directly. This is a
  related but distinct concept from a *self-chosen* exit status: the
  process didn't decide to return a particular number; it was stopped
  by an external event.

These two concepts are related in visible, but **platform/shell-
specific**, ways: on many POSIX shells, a process killed by a signal
is commonly reported to the shell with an exit status conventionally
computed as `128 + <signal number>` — this is a **bash/shell
convention for reporting signal termination through the same numeric
`$?` channel**, not a universal Python-level semantic, and not
guaranteed to look identical on every shell or every platform.

This chapter does not go further into signal handling itself (catching
`SIGINT`, `SIGTERM`, and so on) — that is a distinct, more advanced
topic. The one idea worth taking from this section is simply: **not
every non-zero (or unusual) exit status necessarily means "the program
detected an error and returned a status" — some indicate the process
was stopped from the outside instead**, and shells have their own
conventions, not Python's, for surfacing that distinction through the
same `$?`-style mechanism.

## 56. API Reference

**`sys` module**

| API | Purpose | Notes |
|---|---|---|
| `sys.stdin` | The process's standard input stream (text mode by default) | §4–§6 |
| `sys.stdout` | The process's standard output stream (text mode by default) | §4, §7 |
| `sys.stderr` | The process's standard error stream (text mode by default) | §4, §8 |
| `sys.exit(status=None)` | Raise `SystemExit(status)`, requesting process termination | §18–§20 |
| `SystemExit` | The exception `sys.exit()` raises; catchable like any exception | §18 |

**Stream methods/attributes** (apply to `sys.stdin`/`stdout`/`stderr`,
and to any text-mode file object)

| API | Purpose | Notes |
|---|---|---|
| `read(size=-1)` | Read up to `size` characters, or everything if omitted | §5 |
| `readline()` | Read one line; the line terminator is included when present. Returns `""` at EOF | §5–§6 |
| `readlines()` | Read all remaining lines as a `list[str]` | §5 |
| `write(s)` | Write `s`; returns character count written | §7 |
| `writelines(lines)` | Write an iterable of strings, no automatic newlines added | §7 |
| `flush()` | Force buffered data out now | §14 |
| `isatty()` | Whether this stream is connected to a terminal/TTY device | §15 |
| `fileno()` | The underlying OS file descriptor's integer | §36 |
| `readable()` / `writable()` / `seekable()` | Whether the corresponding operation is supported | §4 |
| `.buffer` | The underlying binary stream, for `sys.stdin`/`stdout`/`stderr` (normally present; replacement file-like objects such as `io.StringIO` may lack it) | §13 |

**`print()`**

| Parameter | Purpose | Section |
|---|---|---|
| `file=` | Which stream to write to (default `sys.stdout`) | §8, §28 |
| `end=` | What to print instead of the default trailing newline | §7 |
| `sep=` | Separator between multiple positional arguments | §7 |
| `flush=` | Force immediate flushing of this call's output | §14 |

**`contextlib`**

| API | Purpose | Notes |
|---|---|---|
| `redirect_stdout(new_target)` | Temporarily redirect `sys.stdout` within a `with` block | §39 — Python-level only |
| `redirect_stderr(new_target)` | Temporarily redirect `sys.stderr` within a `with` block | §39 — Python-level only |

**`subprocess`**

| API | Purpose | Notes |
|---|---|---|
| `subprocess.run(args, **kwargs)` | Run a command, wait for it to finish, return a `CompletedProcess` | §33–§34 |
| `capture_output=True` | Capture the child's stdout/stderr instead of inheriting the parent's | §33 |
| `text=True` | Decode captured output as `str` instead of `bytes` | §33 |
| `input=` | Data to send to the child's stdin | §33 |
| `check=True` | Raise `CalledProcessError` on a non-zero child exit status | §34 |
| `CompletedProcess.returncode` | The child process's exit status | §33 |
| `CompletedProcess.stdout` / `.stderr` | Captured output (if `capture_output=True`) | §33 |
| `subprocess.CalledProcessError` | Raised by `run(..., check=True)` on non-zero exit | §34 |

**`os` (low-level)**

| API | Purpose | Notes |
|---|---|---|
| `os.read(fd, n)` | Read up to `n` raw bytes from file descriptor `fd` | §37 — rarely needed directly |
| `os.write(fd, data)` | Write raw bytes to file descriptor `fd` | §37 — rarely needed directly |
| `os.dup(fd)` | Duplicate a file descriptor | §37 |
| `os.dup2(fd, fd2)` | Make `fd2` a duplicate of `fd`, closing `fd2`'s prior target | §37 — the mechanism behind shell redirection |

**pytest**

| Fixture | Captures | Section |
|---|---|---|
| `capsys` | Python-level `sys.stdout`/`sys.stderr` | §40 |
| `capfd` | OS-level file descriptors 1/2 (also captures subprocess/C-level output) | §40 |

## 57. Function-by-Function Reference

A focused, example-anchored pass over every function named in the
project brief, beyond the table form of §56:

- **`sys.exit()`** — raises `SystemExit`; the sole standard way for
  Python code to *request* process termination with a specific status
  (§18–§20). `sys.exit()` with no argument, or `sys.exit(None)`, means
  status `0`; an integer argument becomes that exact status; any other
  argument is printed to stderr and results in status `1`.
- **`sys.stdin.read()`** — blocks until EOF, then returns everything
  read as one `str` (§5–§6). Use for "the whole input is one logical
  unit" (e.g., one JSON document).
- **`sys.stdin.readline()`** — returns one line, including its
  line terminator when present, or `""` exactly at EOF (§5–§6). Use for manual,
  one-line-at-a-time control.
- **`sys.stdin.readlines()`** — blocks until EOF, then returns every
  remaining line as a `list[str]` (§5). Use only when you need
  everything as a list and the input is known to be small.
- **`sys.stdin.isatty()`** — `True` if stdin is connected to a
  terminal/TTY device right now (§15). Use before assuming a human is
  available to answer an `input()` prompt.
- **`sys.stdin.fileno()`** — returns stdin's underlying OS file
  descriptor integer, conventionally `0` (§36). Rarely needed directly.
- **`sys.stdout.write()`** — writes exactly the given string, with no
  automatic newline, returning the character count (§7). Lower-level
  than `print()`.
- **`sys.stdout.writelines()`** — writes each string in an iterable,
  one after another, with **no** newlines inserted between them unless
  each string already includes its own (§4, §7) — a common source of
  confusion versus `print()`'s automatic per-call newline.
- **`sys.stdout.flush()`** — forces buffered output out immediately
  (§14). Use when real-time visibility matters more than efficiency.
- **`sys.stdout.isatty()`** — `True` if stdout is connected to a
  terminal/TTY device (§15). Use before emitting color/progress bars.
- **`sys.stdout.fileno()`** — stdout's descriptor, conventionally `1`
  (§36).
- **`sys.stderr.write()` / `.writelines()` / `.flush()` / `.isatty()` /
  `.fileno()`** — identical semantics to their `stdout` counterparts
  above, applied to the diagnostics stream (§8, conventionally
  descriptor `2`).
- **`print(..., file=...)`** — redirects a single `print()` call to a
  specific stream, most commonly `sys.stderr` (§8, §28).
- **`print(..., flush=...)`** — forces that call's output to be
  flushed immediately (§14).
- **`raise SystemExit(...)`** — functionally identical to calling
  `sys.exit(...)`; used explicitly in the `main() -> int` /
  `raise SystemExit(main())` pattern (§19) to make the "this is where
  the process actually terminates" boundary visible at a glance.
- **`contextlib.redirect_stdout()` / `redirect_stderr()`** — context
  managers that temporarily reassign `sys.stdout`/`sys.stderr` for the
  duration of a `with` block, safely restoring them afterward even on
  an exception (§39).
- **`subprocess.run()`** — runs a command to completion and returns a
  `CompletedProcess` describing what happened (§33–§34).
- **`returncode`, `stdout`, `stderr`** (on `CompletedProcess`) — the
  child's exit status and (if captured) its two output streams (§33).
- **`input=`** (on `subprocess.run()`) — data sent to the child's
  stdin, as if piped in (§33).
- **`capture_output=True`, `text=True`, `check=True`** — control
  whether output is captured, whether it's decoded as text, and
  whether a non-zero exit raises `CalledProcessError` (§33–§34).
- **`capsys`** (pytest fixture) — captures Python-level stdout/stderr
  for a test, via `capsys.readouterr()` (§40).
- **`capfd`** (pytest fixture) — captures OS-level file descriptor
  1/2 output, including from subprocesses (§40).
- **`os.read()` / `os.write()`** — raw, byte-level reads/writes against
  a file descriptor integer, bypassing Python's higher-level stream
  objects entirely (§37).
- **`os.dup()` / `os.dup2()`** — duplicate file descriptors; the
  mechanism underlying shell redirection itself (§10, §37).

## 58. Complete Beginner Examples

**Example 1 — Read one line from stdin**
```python
import sys

line = sys.stdin.readline()
print(f"You entered: {line.rstrip()}")
```
Run: `python app.py`, then type a line and press Enter.
*Shell:* connects your keyboard to stdin (the default, interactive
case). *Python:* `readline()` reads up to and including the newline
you typed. *Expected exit code:* `0`.

**Example 2 — Read all of stdin**
```python
import sys

everything = sys.stdin.read()
print(f"Received {len(everything)} characters")
```
Run: `python app.py < some_file.txt`. *Shell:* redirects `some_file.txt`
onto stdin (§10). *Python:* `read()` blocks until EOF — which, for a
redirected file, happens naturally once the file's contents are
exhausted (§6). *Expected exit code:* `0`.

**Example 3 — Copy stdin to stdout**
```python
import sys

for line in sys.stdin:
    sys.stdout.write(line)
```
Run: `cat data.txt | python app.py`. *Shell:* pipes `cat`'s stdout into
this program's stdin (§11). *Python:* iterates line by line, writing
each one straight through, unmodified — a minimal, streaming filter
(§12, §30). *Expected exit code:* `0`.

**Example 4 — Send diagnostics to stderr**
```python
import sys

print("Starting processing...", file=sys.stderr)
print("result: 42")
```
Run: `python app.py > out.txt 2> err.txt`, then inspect both files
separately. *Expected:* `out.txt` contains only `"result: 42"`;
`err.txt` contains only `"Starting processing..."` — a direct,
observable demonstration of §9's separation. *Expected exit code:* `0`.

**Example 5 — Return success explicitly**
```python
def main() -> int:
    print("done")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```
Run: `python app.py; echo $?`. *Expected output:* `done`, then `0`.

**Example 6 — Return failure explicitly**
```python
import sys


def main() -> int:
    print("something went wrong", file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
```
Run: `python app.py; echo $?`. *Expected:* the message on stderr
(visible on screen, since stderr wasn't redirected), then `1` printed
by `echo $?`.

**Example 7 — `main() -> int`, combining several ideas**
```python
import sys


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("error: expected at least one argument", file=sys.stderr)
        return 2
    print(f"Processing: {args[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
Run: `python app.py` (no arguments) → prints an error to stderr, exits
`2`. Run: `python app.py data.csv` → prints
`"Processing: data.csv"` to stdout, exits `0`.

**Example 8 — File path from argparse, or stdin if omitted**
```python
import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=None, help="Input file (omit to read stdin)")
    return parser


def read_input(path: str | None) -> str:
    if path is None:
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    text = read_input(args.path)
    print(f"Read {len(text)} characters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
Run: `python app.py data.csv` (reads the named file) **or**
`cat data.csv | python app.py` (reads stdin instead, since `path` was
omitted and defaults to `None`) — directly combining §31's pattern
with the previous chapter's `nargs="?"` (optional positional argument).
*Expected exit code:* `0` in both cases.

## 59. Intermediate Examples

**1. Line counter CLI**
```python
import sys


def main(argv: list[str] | None = None) -> int:
    count = sum(1 for _ in sys.stdin)
    print(count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
`cat data.txt | python linecount.py` — streams input line by line
(§30), never holding the whole file in memory, and reports just the
count on stdout.

**2. CSV validator with clean stream separation**
```python
import csv
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    path = Path(argv[0])

    problems = 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for i, row in enumerate(reader, start=1):
            if not row.get("id"):
                print(f"warning: row {i} missing 'id'", file=sys.stderr)
                problems += 1

    print(f"validated: {i} rows, {problems} problems")
    return 0 if problems == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
```
Diagnostics per row go to stderr as they're found; a single summary
line goes to stdout; the exit code (using the §25 example convention's
`3 = input/data problem`) reflects whether any problems were found.

**3. JSON transformation pipeline stage**
```python
import json
import sys


def main(argv: list[str] | None = None) -> int:
    for line in sys.stdin:
        record = json.loads(line)
        record["processed"] = True
        print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
A streaming JSON Lines filter — one JSON object per line in, one out —
composable directly into a pipeline (§11–§12): `cat data.jsonl | python
transform.py | python next_stage.py`.

**4. A command that emits warnings but still succeeds**
```python
import sys


def main(argv: list[str] | None = None) -> int:
    total = 0
    skipped = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            skipped += 1
            continue
        total += 1

    if skipped:
        print(f"warning: skipped {skipped} blank lines", file=sys.stderr)

    print(total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
Demonstrates that a warning on stderr does not, by itself, need to
change the exit status — this program still reports success (`0`)
because skipping blank lines is not treated as a failure by design.

**5. A command with multiple, distinct exit statuses**
```python
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("error: missing path argument", file=sys.stderr)
        return 2

    path = Path(argv[0])
    if not path.exists():
        print(f"error: not found: {path}", file=sys.stderr)
        return 3

    if not path.is_file():
        print(f"error: not a file: {path}", file=sys.stderr)
        return 3

    print(path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
Three distinct failure conditions, three distinct (but consistently
chosen) exit codes — a small, direct application of §25.

## 60. Advanced Examples

**1. Streaming JSON Lines processor with a summary on stderr**
```python
import json
import sys


def main(argv: list[str] | None = None) -> int:
    valid = 0
    invalid = 0
    for line_number, line in enumerate(sys.stdin, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            print(f"warning: line {line_number} is not valid JSON", file=sys.stderr)
            invalid += 1
            continue
        print(json.dumps(record))
        valid += 1

    print(f"processed {valid} valid, {invalid} invalid records", file=sys.stderr)
    return 0 if invalid == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
```
Valid records stream straight to stdout, one per line — a clean,
machine-readable output any downstream pipeline stage can consume
directly (§29); every diagnostic, including the final summary, is
kept on stderr.

**2. CLI with machine-readable stdout and rich diagnostics on stderr**
```python
import json
import sys


def main(argv: list[str] | None = None) -> int:
    records = list(sys.stdin)
    result = {"status": "success", "record_count": len(records)}

    if not records:
        print("warning: no input records received", file=sys.stderr)

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**3. A subprocess pipeline built in Python instead of the shell**
```python
import subprocess
import sys


def main(argv: list[str] | None = None) -> int:
    validate = subprocess.run(
        [sys.executable, "validate.py", "data.csv"],
        capture_output=True, text=True,
    )
    if validate.returncode != 0:
        print(f"validation failed: {validate.stderr}", file=sys.stderr)
        return validate.returncode

    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**4. A parent process capturing a child's stdout and stderr**
```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr); sys.exit(3)"],
    capture_output=True, text=True,
)

print("child stdout:", result.stdout.strip())
print("child stderr:", result.stderr.strip())
print("child exit code:", result.returncode)
```
Output:
```
child stdout: out
child stderr: err
child exit code: 3
```
Demonstrating, in one runnable example, that a child's stdout, stderr,
and exit status are all independently observable from the parent
without any of them interfering with each other.

**5. A testable CLI using `main(argv)`**
```python
import sys
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(argv) if argv is not None else sys.argv[1:]
    if not argv:
        print("error: missing argument", file=sys.stderr)
        return 2
    print(argv[0].upper())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**6. pytest tests for the CLI above**
```python
def test_success(capsys):
    status = main(["hello"])
    captured = capsys.readouterr()
    assert status == 0
    assert captured.out == "HELLO\n"
    assert captured.err == ""


def test_missing_argument(capsys):
    status = main([])
    captured = capsys.readouterr()
    assert status == 2
    assert "error" in captured.err
    assert captured.out == ""
```

**7. A production-style validation command**
```python
import json
import sys
from pathlib import Path


def validate_record(record: dict) -> list[str]:
    errors = []
    if "id" not in record:
        errors.append("missing 'id'")
    if "value" not in record:
        errors.append("missing 'value'")
    return errors


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    path = Path(argv[0]) if argv else None

    lines = path.open("r", encoding="utf-8") if path else sys.stdin

    total = 0
    failed = 0
    with lines if path else _noop_context(lines) as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            total += 1
            record = json.loads(line)
            errors = validate_record(record)
            if errors:
                failed += 1
                print(f"line {line_number}: {'; '.join(errors)}", file=sys.stderr)

    print(json.dumps({"total": total, "failed": failed}))
    return 0 if failed == 0 else 3


class _noop_context:
    def __init__(self, handle):
        self.handle = handle

    def __enter__(self):
        return self.handle

    def __exit__(self, *exc_info):
        return False


if __name__ == "__main__":
    raise SystemExit(main())
```
(The small `_noop_context` helper exists only so `sys.stdin` — which
should not be closed by a `with` block the way an opened file should —
and a real file can share one `with`-based code path; a simplification
worth naming explicitly, per this chapter's own code-quality
requirements.)

## 61. End-to-End Mini Project — Streaming Data Quality CLI

**Requirements:** a tool, `dq_check.py`, that:
- accepts an optional file path positional argument; reads stdin if
  omitted (§31–§32),
- processes input **line-by-line**, treating each line as one JSON
  record (JSON Lines format); blank/whitespace-only lines are ignored
  and are not counted as records,
- writes each **valid** record straight through to stdout, unchanged,
- writes a warning to **stderr** for each malformed or invalid record,
  without stopping the whole run,
- returns exit code `0` if every record was valid, `3` if at least one
  record failed (using the §25 example convention),
- supports a machine-readable `--json-summary` flag that, instead of
  passing records through, prints only a final JSON summary to stdout,
- is built around `main(argv) -> int` and is fully testable.

**Architecture:**
```
build_parser()          — argparse: optional path, --json-summary flag
        ↓
open_input(path)         — file or stdin (§31)
        ↓
iter_records(handle)      — yields (line_number, parsed_or_None, raw_line)
        ↓
validate_record(record)    — pure function: list of error strings
        ↓
main(argv)                  — wires it all together, handles output mode, returns status
```

**Implementation:**
```python
"""dq_check.py — a streaming data-quality checker for JSON Lines input."""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a JSON Lines stream, record by record.",
    )
    parser.add_argument(
        "path", nargs="?", default=None,
        help="Input file (JSON Lines). Omit to read from stdin.",
    )
    parser.add_argument(
        "--json-summary", action="store_true",
        help="Print only a final JSON summary to stdout, instead of passing records through.",
    )
    return parser


def open_input(path: str | None):
    if path is None:
        return sys.stdin
    return Path(path).open("r", encoding="utf-8")


def validate_record(record: object) -> list[str]:
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    errors = []
    if "id" not in record:
        errors.append("missing 'id'")
    if "value" not in record:
        errors.append("missing 'value'")
    return errors


def iter_records(handle) -> Iterator[tuple[int, dict | None, str]]:
    for line_number, raw_line in enumerate(handle, start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError:
            yield line_number, None, stripped
            continue
        yield line_number, record, stripped


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    handle = open_input(args.path)
    total = 0
    failed = 0

    try:
        for line_number, record, raw_line in iter_records(handle):
            total += 1

            if record is None:
                print(f"line {line_number}: not valid JSON", file=sys.stderr)
                failed += 1
                continue

            errors = validate_record(record)
            if errors:
                print(f"line {line_number}: {'; '.join(errors)}", file=sys.stderr)
                failed += 1
                continue

            if not args.json_summary:
                print(raw_line)
    finally:
        if handle is not sys.stdin:
            handle.close()

    if args.json_summary:
        print(json.dumps({"total": total, "failed": failed}))

    return 0 if failed == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
```

**Sample input** (`data.jsonl`):
```
{"id": 1, "value": "a"}
{"id": 2}
not json at all
{"id": 3, "value": "c"}
```

**Running it:**
```bash
python dq_check.py data.jsonl
```

**Expected stdout:**
```
{"id": 1, "value": "a"}
{"id": 3, "value": "c"}
```

**Expected stderr:**
```
line 2: missing 'value'
line 3: not valid JSON
```

**Expected exit code:** `3` (two of four records failed).

**Pipeline usage:**
```bash
cat data.jsonl | python dq_check.py 2> problems.log | python next_stage.py
echo "$?"
```
Only the valid records reach `next_stage.py`'s stdin (§11); every
problem is captured separately in `problems.log` (§10) without
touching the pipeline's data flow at all.

**Debugging scenarios:**
- If `python dq_check.py` (no path, run interactively with no
  redirection) appears to hang, this is expected — it's correctly
  waiting on stdin for EOF (§6); either redirect a file in, pipe data
  in, or type input and signal EOF manually.
- If a downstream pipeline stage receives corrupted-looking JSON, check
  whether a warning line is accidentally being printed to stdout
  instead of stderr — verify with `python dq_check.py data.jsonl 2>
  /dev/null` and confirm stdout alone still parses cleanly.

**Test strategy:**
```python
import json

from dq_check import main, validate_record


def test_validate_record_reports_missing_fields():
    assert validate_record({}) == ["missing 'id'", "missing 'value'"]
    assert validate_record({"id": 1, "value": "x"}) == []


def test_all_valid_records_pass_through(tmp_path, capsys):
    input_file = tmp_path / "data.jsonl"
    input_file.write_text('{"id": 1, "value": "a"}\n', encoding="utf-8")

    status = main([str(input_file)])
    captured = capsys.readouterr()

    assert status == 0
    assert json.loads(captured.out.strip()) == {"id": 1, "value": "a"}
    assert captured.err == ""


def test_invalid_record_reported_on_stderr_and_nonzero_exit(tmp_path, capsys):
    input_file = tmp_path / "data.jsonl"
    input_file.write_text('{"id": 1}\n', encoding="utf-8")

    status = main([str(input_file)])
    captured = capsys.readouterr()

    assert status == 3
    assert "missing 'value'" in captured.err
    assert captured.out == ""


def test_json_summary_mode(tmp_path, capsys):
    input_file = tmp_path / "data.jsonl"
    input_file.write_text('{"id": 1, "value": "a"}\n{"id": 2}\n', encoding="utf-8")

    status = main([str(input_file), "--json-summary"])
    captured = capsys.readouterr()

    summary = json.loads(captured.out.strip())
    assert summary == {"total": 2, "failed": 1}
    assert status == 3
```

**Production improvements worth naming, not implementing here:**
replacing the ad hoc `print(..., file=sys.stderr)` diagnostics with the
`logging` module (§46, the next chapter's full subject) for
configurable severity and formatting; adding a `--fail-fast` flag to
stop at the first invalid record; making the exit-code scheme
explicit and documented in `--epilog` text (from the previous
chapter); and validating that `--json-summary` and any future
`--quiet`-style flag interact sensibly rather than silently
conflicting.

## 62. Coding Exercises

**Level 1 — Beginner**
1. Write a script that prints `"hello"` to stdout, and separately, one
   that prints `"warning"` to stderr — verify each independently using
   redirection (`> out.txt`, `2> err.txt`).
2. Write a script that reads one line from stdin with `input()` and
   echoes it back.
3. Write a script that reads all of stdin with `sys.stdin.read()` and
   prints the character count — run it both interactively (typing
   input, then signaling EOF) and with a redirected file.
4. Write a script that checks `sys.stdout.isatty()` and prints a
   different message depending on the result — verify both branches by
   running it directly and by redirecting its output to a file.
5. Write a script that returns exit code `0` on one code path and a
   distinct non-zero code on another, and verify both with `echo $?`.

**Level 2 — Intermediate**
1. Write a line-counting CLI that streams stdin (does not load it all
   into memory) and prints the count to stdout.
2. Write a CLI accepting an optional file-path positional argument,
   falling back to stdin when omitted (§31).
3. Write a CLI that cleanly separates its result (stdout) from at
   least one deliberate diagnostic (stderr), and verify the separation
   using `2>/dev/null` and `>/dev/null` respectively.
4. Write a validation CLI returning three distinct, documented exit
   codes for three distinct failure conditions.
5. Write a CLI using `main(argv) -> int` and `raise SystemExit(main())`,
   and write at least three pytest tests for it using `capsys`.

**Level 3 — Advanced**
1. Write a streaming JSON Lines transformation CLI that can be chained
   with itself in a pipeline (`... | python transform.py | python
   transform.py`).
2. Write a script that uses `subprocess.run(..., capture_output=True,
   text=True)` to invoke another Python script and print its
   `returncode`, `stdout`, and `stderr` separately.
3. Write a script that uses `subprocess.run(..., check=True)` and
   handles `CalledProcessError` cleanly, reporting a specific exit code
   of its own based on the child's failure.
4. Write a pytest test using `capfd` (not `capsys`) that captures
   output produced by a `subprocess.run()` call made during the test,
   and explain in a comment why `capsys` alone would not have captured
   it.
5. Write a "pipe-safe" CLI — one that behaves identically whether run
   interactively or inside a pipe with both ends redirected — and
   write a short explanation of what you specifically checked to
   verify pipe-safety.

For each: state the exact command you'd run, the expected stdout,
stderr, and exit code, and which concept from this chapter it
exercises. Solutions are not provided — verify your own understanding
against the relevant section.

## 63. Debugging Exercises

**1. Diagnostics contaminating stdout**
```python
print("Loading data...")
print("ERROR: bad row at line 4")
print("result: 42")
```
*Observed behavior:* a downstream pipeline stage expecting only
`"result: 42"` on stdin receives three lines instead and fails to
parse.
*Debugging questions:* which of these three lines is the program's
actual output? Which stream should the other two be on?
*Corrected:*
```python
import sys
print("result: 42")
print("Loading data...", file=sys.stderr)
print("ERROR: bad row at line 4", file=sys.stderr)
```
*Explanation:* only the actual result belongs on stdout (§9).

**2. Missing flush**
```python
import time
print("starting...", end="")
time.sleep(5)
print(" done")
```
*Observed behavior:* when this script's output is redirected to a
file being watched with `tail -f`, `"starting..."` doesn't appear
until the whole script finishes, five seconds later.
*Debugging questions:* is stdout connected to a terminal or a file in
this scenario? What does that change about buffering (§14)?
*Corrected:* `print("starting...", end="", flush=True)`.
*Explanation:* redirected stdout is commonly block-buffered rather
than line-buffered; without an explicit flush, "starting..." sits in
the buffer until the process ends.

**3. Wrong exit code (always zero)**
```python
def main() -> int:
    try:
        risky_operation()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
    return 0

raise SystemExit(main())
```
*Observed behavior:* automation treats every run as successful, even
when `risky_operation()` failed and an error was printed.
*Debugging questions:* what does `main()` return on the failure path?
*Corrected:*
```python
def main() -> int:
    try:
        risky_operation()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0
```
*Explanation:* printing an error does not, by itself, change the exit
status — §22, §43 (mistake 18).

**4. Swallowed exception**
```python
try:
    process_all()
except:
    pass

print("done")
```
*Observed behavior:* the script always prints `"done"` and exits `0`,
even when `process_all()` raised a genuine, unexpected error partway
through.
*Debugging questions:* what exception types is this `except:` clause
catching? What information about the failure has been discarded?
*Corrected:*
```python
import sys

try:
    process_all()
except SomeExpectedError as exc:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(1)
```
*Explanation:* a bare `except:` hides genuinely unexpected bugs, not
just anticipated failure modes — §43 (mistake 19).

**5. stdin waiting for EOF, mistaken for a hang**
```python
data = sys.stdin.read()
print(len(data))
```
*Observed behavior:* run directly (`python app.py`, no redirection,
no pipe), the program appears to freeze.
*Debugging questions:* is stdin connected to anything providing an
end? What is `read()` documented to do until it sees EOF (§6)?
*Corrected understanding (not a code change):* provide input via
redirection (`python app.py < file.txt`) or a pipe, or type input and
signal EOF manually if genuinely interactive input is intended.

**6. Incorrect subprocess handling**
```python
result = subprocess.run(["python", "validate.py", "data.csv"])
print("validation succeeded")
```
*Observed behavior:* this line prints even when `validate.py` actually
failed.
*Debugging questions:* is `result.returncode` being checked anywhere?
*Corrected:*
```python
result = subprocess.run(["python", "validate.py", "data.csv"])
if result.returncode != 0:
    print("validation failed", file=sys.stderr)
    raise SystemExit(result.returncode)
print("validation succeeded")
```
*Explanation:* `subprocess.run()` without `check=True` never raises on
a non-zero child exit by itself — §34.

**7. Incorrect stream capture in a test**
```python
def test_prints_result():
    subprocess.run(["python", "app.py"])
    # trying to assert on stdout here, with no capture configured at all
```
*Observed behavior:* the test has no way to inspect what `app.py`
printed.
*Debugging questions:* was `capture_output=True` passed? If using
pytest's own fixtures instead, is `capsys` sufficient, or does this
scenario (a subprocess) actually need `capfd` (§40)?
*Corrected:*
```python
def test_prints_result():
    result = subprocess.run(["python", "app.py"], capture_output=True, text=True)
    assert "expected text" in result.stdout
```

**8. `sys.exit()` called deep inside business logic**
```python
def validate(record):
    if "id" not in record:
        sys.exit(1)   # kills the whole process from inside a small helper
    return True
```
*Observed behavior:* a single bad record in a batch immediately
terminates the entire run, with no chance for `main()` to report a
clean summary or continue processing other records.
*Debugging questions:* should this function have any power to
terminate the whole process at all?
*Corrected:*
```python
def validate(record) -> bool:
    return "id" in record
```
with the calling code in `main()` deciding what to do about failed
records — collect them, count them, and decide the overall exit status
once, at the top (§43, mistake 10).

## 64. Interview Questions

1. What is stdin, precisely — not "the keyboard," but the accurate
   definition?
2. What is stdout, and what is the one rule about what it should
   contain?
3. What is stderr, and what is it conventionally used for?
4. Why are stdout and stderr kept as two separate streams instead of
   one?
5. What is a pipe, and what exactly does it connect?
6. What is an exit code / exit status?
7. Why is `0` commonly used to mean success?
8. What does `sys.exit()` do, mechanically?
9. What is `SystemExit`, and how does it relate to `sys.exit()`?
10. Why is `main() -> int` combined with `raise SystemExit(main())` a
    useful pattern?
11. Why should diagnostics normally go to stderr rather than stdout?
12. What is a file descriptor?
13. What do file descriptors `0`, `1`, and `2` conventionally
    represent?
14. What does `isatty()` tell a program, and why does that matter?
15. What is buffering, and why does it exist?
16. Why can a program's output behave differently once it's piped or
    redirected compared to running interactively?
17. What is the difference between Python-level stream redirection
    (`sys.stdout = ...` or `contextlib.redirect_stdout`) and OS-level
    redirection (the shell's `>`)?
18. What is the difference between pytest's `capsys` and `capfd`?
19. How does `subprocess.run()` expose a child process's stdout,
    stderr, and exit status?
20. Why do CI systems rely on exit codes rather than parsing printed
    output?
21. How would you design a "pipe-safe" CLI program?
22. How would you process an input stream far too large to fit in
    memory?
23. Why should machine-readable output (e.g. JSON) on stdout stay free
    of any other text?
24. How should a CLI program communicate an error to both a human and
    an automated system at the same time?
25. What happens, conceptually, when a child process a parent is
    waiting on returns a non-zero exit status?

**Answer key**

1. stdin is a process's standard input stream — a channel data can
   flow *into* the process through; what it's actually connected to
   (keyboard, file, pipe) depends on how the process was launched, not
   on any fixed meaning of "stdin" itself (§2–§3).
2. stdout is a process's standard output stream; the rule is that it
   should carry the program's actual, intended output — the result —
   and nothing else (§7, §9).
3. stderr is a process's standard error stream, conventionally used for
   diagnostics: warnings, progress messages, and error reports — not
   only uncaught exceptions (§8).
4. So that a program's actual result (stdout) can be consumed reliably
   by another program without that consumer having to filter out
   diagnostic noise mixed in with the data (§9).
5. A pipe (`|`) connects one process's stdout directly to another
   process's stdin, letting data flow between two running processes
   without an intermediate file (§11).
6. A small integer a finished process reports to whatever started it,
   summarizing whether (and sometimes how) it succeeded or failed
   (§17).
7. It's a widely followed Unix/POSIX convention, respected by Python
   and virtually every serious CLI tool — not a law enforced by the
   hardware or the OS kernel itself (§17).
8. It raises the `SystemExit` exception with the given status; if
   nothing catches it, the interpreter terminates the process with
   that status (§18).
9. `SystemExit` is the exception `sys.exit()` raises; it can, like any
   exception, be caught — which is exactly what makes CLI code built
   around it testable with `pytest.raises(SystemExit)` (§18).
10. It cleanly separates "what did the program compute" (an ordinary,
    testable return value) from "how does the process actually
    terminate" (one line, in one place) (§19).
11. Because a program's result may be consumed by another program via
    a pipe, and that consumer would otherwise have no way to
    distinguish diagnostic text from real data (§9, §11).
12. A small integer handle a process uses, on Unix-like systems, to
    refer to an open resource (file, pipe, socket, or standard stream)
    it can read from or write to (§36).
13. `0` conventionally means stdin, `1` conventionally means stdout,
    and `2` conventionally means stderr (§3, §36).
14. Whether that particular stream is currently connected to a real,
    interactive terminal — used to decide whether it's safe to emit
    things like color, progress bars, or interactive prompts (§15).
15. Collecting output into a temporary in-memory area and sending it
    onward in batches rather than one write at a time, because each
    actual send has real overhead that buffering amortizes (§14).
16. Because Python (and the OS) may switch buffering strategy depending
    on what a stream is connected to — commonly line-buffered for an
    interactive terminal, block-buffered otherwise — changing when
    output actually becomes visible (§14).
17. Python-level redirection (reassigning `sys.stdout`, or using
    `contextlib.redirect_stdout`) only changes what that name refers to
    inside the running Python process, and has no effect on the actual
    OS file descriptor or on any subprocess; OS-level redirection (the
    shell's `>`) reconfigures the actual file descriptor before the
    process even starts, affecting everything the process (and
    anything it spawns) writes (§10, §38–§39).
18. `capsys` captures Python-level `sys.stdout`/`sys.stderr` writes;
    `capfd` captures at the OS file-descriptor level, additionally
    catching output from subprocesses or C-level code that bypasses
    Python's stream objects entirely (§40).
19. A `CompletedProcess` object returned by `subprocess.run()` exposes
    `.returncode` for the exit status and, if `capture_output=True`,
    `.stdout`/`.stderr` for the captured output (§33).
20. Because exit codes are a reliable, structured, numeric signal
    checked automatically by the OS/shell — no automated system needs
    to parse arbitrary human-oriented text to determine success or
    failure (§22–§23).
21. By reading from stdin when appropriate, writing only the actual
    result to stdout, sending every diagnostic to stderr, and returning
    a meaningful, non-zero exit code on any failure (§12, §45).
22. By streaming it — reading and processing it incrementally (e.g.
    `for line in sys.stdin:`) rather than loading the whole thing into
    memory with `read()`/`readlines()` first (§30).
23. Because any diagnostic text mixed into machine-readable stdout
    output would break whatever is trying to parse it (JSON, CSV, or
    any other structured format) as a single, well-formed document
    (§29).
24. By printing a clean, human-readable message to stderr for a person
    to read, *and* returning a specific, meaningful, non-zero exit
    status for automation to check — the two channels serve different
    audiences and should both be used deliberately (§24–§25, §51).
25. The parent process's `subprocess.run()` call returns normally (by
    default) with that non-zero value in `.returncode` for the parent
    to inspect and act on; if `check=True` was passed, the parent
    instead receives a `CalledProcessError` exception immediately
    (§34).

## 65. Architecture Questions

1. **Design a CLI that supports both files and stdin.** Accept an
   optional positional path argument (`nargs="?"`, previous chapter);
   fall back to `sys.stdin` when it's omitted (§31); keep the actual
   reading logic (whichever source it came from) unaware of which one
   was used.
2. **Design a CLI that composes into Unix-style pipelines.** Read line
   by line from stdin when no file is given; write only the
   transformed result to stdout, one unit per line if the format
   supports it (e.g. JSON Lines); route every diagnostic to stderr;
   return a meaningful, non-zero exit code on any failure (§12, §45).
3. **Prevent diagnostics from corrupting JSON output.** Never call
   `print()` (or write) to stdout except for the final, complete
   result; route every warning, progress message, and error
   exclusively through `sys.stderr` (§9, §29) — and, ideally, test this
   explicitly by asserting `captured.out` parses as valid JSON on its
   own, with `captured.err` checked separately (§40–§41).
4. **How does a CI system determine success?** By running the command
   and inspecting its exit status — `0` means the step passed;
   non-zero means it failed and (depending on configuration) the
   pipeline stops or is marked failed (§22–§23).
5. **How would you test stdout, stderr, and exit status together?**
   Build the CLI around `main(argv) -> int`; call it directly in tests
   with an explicit argument list; use `capsys` (or `capfd` if
   subprocesses are involved) to capture output; assert on `.out`,
   `.err`, and the returned status independently (§40–§41).
6. **How would you process very large input without loading it into
   memory?** Iterate over `sys.stdin` line by line (or, for binary
   data, read fixed-size chunks via `sys.stdin.buffer.read(size)`) so
   memory usage stays proportional to one unit of work, not to the
   whole input (§30).
7. **How would you design a subprocess-based pipeline?** Use
   `subprocess.run()` per stage, checking `.returncode` (or
   `check=True`) after each one before proceeding to the next; capture
   each stage's stdout/stderr independently so a failure in one stage
   is attributable and doesn't get silently absorbed into the next
   (§33–§34, §54).
8. **How would you expose errors to both humans and automation?**
   A clear message on stderr for a human reading logs, plus a specific,
   documented, non-zero exit code for automation to branch on — never
   relying on parsing the human-oriented message text as the
   "real" signal (§24–§25, §51).
9. **How do standard streams work inside a container?** Identically to
   any other process (§3) — the container runtime typically captures
   stdout/stderr as the container's logs, and the process's exit
   status is typically what the surrounding orchestration system
   checks to determine whether the container's task succeeded (§52).
10. **Design a production-grade data validation CLI.** Combine: file-
    or-stdin input (§31); streaming, line-by-line processing (§30);
    clean, structured (e.g. JSON) results on stdout; per-record
    warnings on stderr; a small, documented, consistent set of exit
    codes (§25); a `main(argv) -> int` entry point with a full pytest
    suite covering success, partial failure, and total failure cases
    (§41, §61).

## 66. Knowledge Check

**Multiple choice**

1. What does `sys.stdin.readline()` return exactly at EOF?
   (a) `None`  (b) raises an exception  (c) `""`  (d) blocks forever

2. What is the conventional file descriptor number for stderr?
   (a) `0`  (b) `1`  (c) `2`  (d) it varies randomly

3. Which of these does `subprocess.run(..., check=True)` do on a
   non-zero child exit?
   (a) nothing different  (b) raises `CalledProcessError`
   (c) retries automatically  (d) returns `None`

**True/false**

4. `print()` always displays text on the user's screen. (True/False)
5. A pipe connects one process's stdout to another process's stdin,
   but not its stderr, by default. (True/False)
6. `sys.exit(1)` can, in principle, be caught with
   `except SystemExit:`. (True/False)
7. `capsys` and `capfd` in pytest capture output identically in every
   case. (True/False)

**Short answer**

8. In one or two sentences, explain why stdout and stderr are kept
   separate.
9. What does `isatty()` actually check?

**Code-output**

10. What does this print, and to which stream?
```python
import sys
print("a", file=sys.stdout)
print("b", file=sys.stderr)
```

11. What is the exit status of this script?
```python
import sys
sys.exit("oops")
```

**Debugging**

12. A script hangs when run with no arguments and no redirection, but
    works fine as `python app.py < input.txt`. What's the most likely
    cause?

**Architecture**

13. Why should `sys.exit()` generally not be called from deep inside a
    small helper function that's also used by non-CLI code?

---

**Answer key**

1. **(c)** `""` — `readline()` at EOF returns an empty string, not
   `None` and not an exception (§5–§6).
2. **(c)** `2` — the POSIX convention for stderr (§3, §36).
3. **(b)** it raises `subprocess.CalledProcessError` (§34).
4. **False** — `print()` writes to `sys.stdout` by default; where that
   output actually *appears* depends on what stdout is connected to
   (§2, §7).
5. **True** — a plain pipe connects only stdout to the next process's
   stdin; stderr remains connected to whatever it was before (§11).
6. **True** — `sys.exit()` works by raising `SystemExit`, which, like
   any exception, can be caught (§18).
7. **False** — `capsys` captures only Python-level stream writes;
   `capfd` additionally captures OS-level/file-descriptor writes,
   including from subprocesses (§40).
8. So that a program's actual output (stdout) can be consumed reliably
   by another program (via a pipe) without diagnostic text mixed in
   corrupting that data (§9).
9. Whether a specific stream is currently connected to a real,
   interactive terminal, as opposed to a file, a pipe, or another
   program (§15).
10. `"a"` is written to stdout; `"b"` is written to stderr — both may
    appear on the same terminal screen by default, but they are two
    independent streams, distinguishable the moment either is
    redirected separately (§9–§10).
11. `1` — passing a non-integer to `sys.exit()` prints it to stderr and
    results in exit status `1` (§20).
12. The script is almost certainly blocking on a `sys.stdin.read()` (or
    equivalent) call, correctly waiting for EOF; run with no
    redirection and no piped input, an interactive terminal provides
    no natural EOF until one is signaled manually (§6).
13. Because it kills the entire process outright, which is
    inappropriate (and often outright broken) for a helper that might
    also be called from a test, a library context, or any other
    non-CLI caller that should be able to handle a failure as a normal
    exception instead of having the whole process terminated out from
    under it (§43, mistake 10; §44).

## 67. Common Confusions

- **stdin vs. `input()`** — `input()` is a convenient, one-line-at-a-
  time wrapper built on top of stdin; `sys.stdin` is the underlying
  stream itself, with more ways to read from it (§5).
- **stdout vs. `print()`** — `print()` is a convenience function that
  writes to stdout (by default); stdout is the underlying stream
  `print()` targets (§4, §7).
- **stdout vs. stderr** — two independent output streams with
  different conventional purposes (result vs. diagnostics), not two
  names for the same thing (§9).
- **stream vs. file** — a file is one possible thing a stream can be
  connected to; not every stream is a file (§1).
- **stream vs. terminal** — a terminal is one possible thing a stream
  can be connected to, in the interactive case only (§1–§2).
- **file descriptor vs. file object** — a file descriptor is a raw OS-
  level integer handle; a file object (`sys.stdout`, or what `open()`
  returns) is a much richer Python object built on top of one (§36).
- **Python stream vs. OS file descriptor** — the same distinction,
  restated: Python-level redirection changes what a name refers to
  inside the process; OS-level redirection changes what the actual
  descriptor points to, affecting subprocesses too (§38–§39).
- **exception vs. exit code** — an exception is a language-level event
  during execution; an exit code is the final, numeric status the
  whole process reports when it's done — related only because your
  code (or Python's default handling) chooses to convert one into the
  other (§24).
- **return from `main()` vs. `sys.exit()`** — a plain function return
  is testable and has no side effects on the process; `sys.exit()`
  raises `SystemExit`, intended to actually end the process — the
  recommended pattern uses the former throughout `main()`'s own logic
  and the latter exactly once, at the very top level (§19).
- **`sys.exit()` vs. `raise SystemExit`** — functionally identical;
  `sys.exit(x)` is implemented in terms of raising `SystemExit(x)`
  (§18).
- **shell redirection vs. Python redirection** — the shell's `>`/`<`/
  `2>` reconfigures actual OS file descriptors before your process
  starts; Python-level redirection only changes what a name refers to
  within the running process (§10, §38).
- **`capsys` vs. `capfd`** — Python-level capture vs. OS-file-
  descriptor-level capture (§40).
- **TTY vs. pipe** — a TTY is an interactive terminal a human is
  directly using; a pipe connects two processes with no human directly
  involved on either end (§1, §11, §15).
- **interactive input vs. redirected input** — the same stdin API
  (`sys.stdin`) behaves identically from your code's point of view in
  both cases, but the *source* and EOF behavior differ (§6, §15).
- **human output vs. machine-readable output** — content meant for a
  person to read on screen versus content meant to be parsed by
  another program; the same stream (stdout) can carry either, but not
  safely both at once in the same invocation (§29).

## 68. Internal Mechanics

What actually happens, step by step, when you run:

```bash
python app.py
```

```
1. The shell (bash) parses what you typed into command-line tokens.
2. The shell asks the operating system to start a new process for
   Python, with app.py as an argument.
3. The OS creates the new process and, before any of its own code
   runs, sets up its three standard streams — by default, inherited
   from the shell's own streams (fd 0/1/2, all still connected to your
   terminal in this plain, no-redirection case).
4. Standard streams are connected: fd 0 → the terminal's input,
   fd 1 → the terminal's output, fd 2 → the terminal's output as well.
5. The Python interpreter starts inside this new process.
6. Python initializes sys.stdin, sys.stdout, and sys.stderr as text-
   mode stream objects wrapping those inherited file descriptors.
7. Your application code (app.py) executes.
8. Your code writes output — via print(), sys.stdout.write(), etc.
9. Your code finishes (returns from main(), or an unhandled exception
   propagates, or sys.exit() is called).
10. The process terminates and reports its exit status to the OS.
11. The shell receives that exit status and records it (accessible via
    $? on a POSIX shell, §21).
```

Now consider what changes for two common variations:

```bash
python app.py | other_command
```
Step 3–4 change: rather than fd 1 pointing at the terminal, the shell
sets it up (via the same `dup2`-style mechanism from §37) to point at
one end of a newly created pipe, whose other end is connected to
`other_command`'s fd 0. Steps 1–2 and 5–11 are otherwise unchanged —
your Python code never needs to know the difference; it simply writes
to `sys.stdout` exactly as before.

```bash
python app.py > output.txt
```
Step 3–4 change again: fd 1 is instead connected to the newly opened
(or truncated, for `>`) file `output.txt`. Everything from step 5
onward is, once again, identical from your program's own point of
view — this is the entire point of the standard-stream abstraction:
your code writes to "stdout" without needing to know, or care, exactly
what that turns out to mean for any particular run.

```bash
python app.py 2> error.txt
```
The same idea, applied to fd 2 (stderr) instead of fd 1 — stdout
remains connected to the terminal in this case, while only diagnostics
are redirected to the file.

## 69. Performance and Scale

How the concepts in this chapter behave differently as data size
grows:

- **Tiny CLI tools** (a few lines of input/output) — buffering,
  streaming, and flushing choices are essentially invisible; any
  reasonable approach performs indistinguishably.
- **Medium data files** (megabytes) — streaming (`for line in
  sys.stdin:`, §30) versus loading everything at once
  (`readlines()`) starts to show a measurable, if modest, difference
  in memory footprint; both usually still "work," but streaming is
  already the better habit to have formed.
- **Very large files / streaming pipelines** (gigabytes and up) —
  loading everything into memory first can genuinely fail (memory
  exhaustion) or severely degrade performance (swapping); line-by-line
  (or fixed-size chunk, for binary data) streaming is no longer just
  good practice — it is frequently the only approach that works at
  all.
- **High-volume logs / very chatty diagnostics** — writing a stderr
  line for every single record, at high volume, can itself become a
  meaningful performance cost (and a noisy, hard-to-use log); batching
  diagnostics, or downgrading verbosity, becomes worth considering
  (a concern the `logging` module, next chapter, is specifically built
  to help manage, via levels).
- **Throughput vs. latency** — a fully-buffered pipeline (each stage
  collects everything before passing it on) can maximize raw
  throughput for some workloads at the cost of end-to-end latency
  (nothing downstream sees *any* output until an upstream stage
  finishes entirely); a streaming pipeline (small buffers, frequent
  flushes) reduces latency (downstream stages can start working sooner)
  at a potential small throughput cost from more frequent, smaller
  operations. Most CLI and data-pipeline tools should default to
  streaming, reserving deliberate batching for cases where profiling
  shows it actually matters.
- **Backpressure** (§30) — in a multi-stage pipe-connected pipeline, a
  slow downstream stage naturally limits how fast an upstream stage's
  writes can proceed, via the OS's own pipe buffering — this is a
  built-in, "for free" mechanism, not something your code typically
  needs to implement itself for a straightforward shell pipeline.

For data engineering and AI/ML workloads specifically, this is exactly
why dataset preprocessing, log analysis, and batch inference tools
default to line-oriented (or record-oriented, e.g. JSON Lines)
streaming formats and I/O patterns — the practices this whole chapter
has been building toward are not incidental CLI style choices; they
are what makes such tools able to scale to real production data sizes
at all.

## 70. Production Checklist

**Input**
- [ ] Does the program support stdin where that makes sense (§31)?
- [ ] Is EOF handled correctly — no assumption that input is always
      "complete" before reading begins (§6)?
- [ ] Is input validated before being trusted (connecting to
      [09-environment-configuration-and-input-validation.md](09-environment-configuration-and-input-validation.md))?

**Output**
- [ ] Is stdout reserved strictly for the program's intended output
      (§7, §9)?
- [ ] Is stderr used consistently for diagnostics (§8)?
- [ ] Is machine-readable output (if any) kept completely clean of any
      other text (§29)?

**Exit status**
- [ ] Does success return/exit `0`?
- [ ] Are failures non-zero, and does every failure path actually
      return/exit non-zero (§43, mistake 8–9)?
- [ ] Are the specific non-zero values meaningful and documented
      (§25)?
- [ ] Are exceptions caught deliberately and translated into a clean
      message and exit status, rather than left to produce a raw
      traceback (§24)?

**Streaming**
- [ ] Does the program avoid loading unnecessarily large input fully
      into memory (§30)?
- [ ] Is buffering behavior understood, not assumed (§14)?
- [ ] Is `flush()`/`flush=True` used deliberately, where real-time
      visibility genuinely matters — and not sprinkled everywhere out
      of habit (§14, §48)?

**Testing**
- [ ] Is stdout tested (§40–§41)?
- [ ] Is stderr tested?
- [ ] Is exit status tested?
- [ ] Are non-interactive (piped/redirected) cases specifically tested,
      not just the interactive case (§41, §43 mistake 20)?

**Automation**
- [ ] Does CI (or whatever automation calls this tool) correctly
      detect failure via exit status alone (§22–§23)?
- [ ] If this tool invokes subprocesses itself, is their `.returncode`
      (or `check=True`) actually checked (§34)?
- [ ] Are failures observable — in stderr, in logs — for someone
      debugging after the fact?

**Security**
- [ ] Are secrets excluded from stdout, stderr, and CLI arguments
      (§47)?
- [ ] Are error messages sanitized of unnecessary internal detail
      before being shown to end users (§47)?

**Portability**
- [ ] Does the program rely on Python's own `sys`/`subprocess`
      abstractions rather than platform-specific mechanisms, where
      portability matters (§49)?

## 71. Mastery Checklist

- [ ] I can explain what a stream is, in my own words, without saying
      "file" or "terminal" as if they were synonyms for it.
- [ ] I can explain what stdin is.
- [ ] I can explain what stdout is.
- [ ] I can explain what stderr is.
- [ ] I can explain why stdout and stderr are kept separate.
- [ ] I can explain how Python exposes standard streams via `sys`.
- [ ] I can explain what a file descriptor is.
- [ ] I know what fd 0, 1, and 2 conventionally mean.
- [ ] I can explain how `input()` relates to stdin.
- [ ] I can read from `sys.stdin` using at least three different
      approaches, and know when to use each.
- [ ] I can write to stdout using both `print()` and
      `sys.stdout.write()`.
- [ ] I can write to stderr using `print(..., file=sys.stderr)`.
- [ ] I can explain what EOF means, and why reading stdin can appear
      to hang.
- [ ] I can explain what a pipe is.
- [ ] I can explain shell redirection conceptually, and use `>`, `<`,
      `2>` correctly.
- [ ] I can explain buffering.
- [ ] I can explain what `flush()` does and when it's actually needed.
- [ ] I can explain what `isatty()` does and why it matters.
- [ ] I can explain what an exit code is.
- [ ] I can explain why `0` conventionally means success, and why
      non-zero doesn't have one universal meaning.
- [ ] I can explain how `sys.exit()` works, including its relationship
      to `SystemExit`.
- [ ] I can explain why `main() -> int` combined with
      `raise SystemExit(main())` is a useful pattern.
- [ ] I can explain how `argparse` uses stderr and exit codes for its
      own errors, and how that differs from application errors.
- [ ] I can use `subprocess.run()` and inspect a child's `returncode`,
      `stdout`, and `stderr`.
- [ ] I can explain the difference between stdout and stderr in the
      context of a subprocess.
- [ ] I can explain the difference between pytest's `capsys` and
      `capfd`.
- [ ] I can design a pipe-safe CLI program.
- [ ] I can design a meaningful, documented, application-specific
      exit-code scheme.
- [ ] I can explain how these concepts apply to production data and
      AI/ML pipelines, containers, and CI/CD.
