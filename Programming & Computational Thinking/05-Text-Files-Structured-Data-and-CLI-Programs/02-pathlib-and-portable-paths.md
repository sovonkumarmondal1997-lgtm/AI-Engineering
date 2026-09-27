# pathlib and Portable Paths

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what a filesystem path is, why it exists, and how the
  operating system uses it to locate resources.
- Distinguish files, directories, and paths, and distinguish absolute
  from relative paths.
- Explain the current working directory and why relying on it blindly
  is dangerous.
- Explain why `pathlib` exists, and what problems it solves compared to
  building paths out of raw strings.
- Create `Path` objects, combine them safely, and inspect their
  components (`.name`, `.stem`, `.suffix`, `.parent`, `.parts`, and
  more).
- Navigate directory trees with `.iterdir()`, `.glob()`, and
  `.rglob()`.
- Test whether a path exists and distinguish files from directories,
  symlinks, and other filesystem object types.
- Create directories and files safely, and read/write text through
  `pathlib`.
- Inspect file metadata via `.stat()`, and rename, replace, and delete
  filesystem objects correctly.
- Work with symbolic links, and understand the difference between
  `.absolute()` and `.resolve()`.
- Build portable, project-relative paths that work correctly on Linux,
  macOS, Windows, and WSL2.
- Validate user-provided paths and defend against path traversal.
- Understand TOCTOU (time-of-check to time-of-use) race conditions at a
  conceptual level, and why "check then act" is often the wrong shape.
- Handle filesystem exceptions correctly, without blindly catching
  everything.
- Test filesystem code with `pytest`'s `tmp_path` fixture.
- Design reusable, testable path-handling functions with clear type
  hints, and understand `os.PathLike` interoperability.
- Diagnose common filesystem/path bugs systematically.

## 2. Why This Topic Matters

Module 1.5's outcome is *"you can build reliable small tools that
process real files and communicate clearly through a CLI."*
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)
taught you how to open, read, and write a file once you already know
its path. This chapter answers the question that comes *before* that:
**how do you correctly, safely, and portably describe *where* a file
is?**

That question turns out to be far less trivial than it looks. A path
typed as a plain string works fine on your machine, today — and then
quietly breaks the moment someone runs your program from a different
directory, on a different operating system, or with a path containing
something you did not anticipate. `pathlib`, Python's modern,
object-oriented way of representing filesystem paths, exists precisely
to make these problems structurally harder to create in the first
place.

This chapter is also where this roadmap's boundary-validation
discipline — introduced in the previous chapter for file *contents* —
extends to file *locations*. A path, exactly like a file's content, is
untrusted input the moment it comes from a user, a configuration file,
an environment variable, or a command-line argument. §25 and §26 build
directly on this: a path that is not validated can let a program read
or write somewhere it was never meant to touch.

## 3. Prerequisites

This chapter assumes the Python fundamentals from Modules 1.1–1.4
(variables, strings, functions, exceptions, basic type hints) and the
file-I/O foundations from
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)
— specifically `open()`, file modes, context managers, and the standard
file exceptions. It does **not** assume any prior filesystem
terminology: "filesystem," "directory," "root," "absolute path," and
every other term used here is defined from first principles before it
is used.

## 4. Filesystem and Path Fundamentals

### 4.1 What is a filesystem?

A **filesystem** is the system your operating system uses to organize
and keep track of data on a storage device — which bytes belong to
which file, what that file is named, and how files are grouped into
folders. You never interact with the raw storage device directly; you
interact with it entirely through the filesystem's naming and
organizing scheme.

### 4.2 What is a file, what is a directory?

A **file** is a named collection of data stored on disk (already
covered in depth for *text* files in
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)).
A **directory** (also called a **folder**) is a named container that
holds files *and other directories* — this nesting is exactly what
lets a filesystem organize thousands of files into a navigable
structure instead of one enormous flat list.

### 4.3 What is a path?

A **path** is a string of instructions describing exactly how to
*locate* one specific file or directory within that nested structure —
"start here, go into this directory, then that one, then find this
file." A path is not the file. A path is not even guaranteed to point
at anything that currently exists — it is simply a *description of a
location*, exactly like a street address describes a location whether
or not a house is currently standing there. §36 develops this
distinction fully.

### 4.4 Why programs need paths

A running program cannot say "read that file I'm thinking of" — every
operation that touches the filesystem needs an exact, unambiguous
location to act on. Paths are that unambiguous description, handed from
your code to the operating system every time a file is opened, created,
inspected, moved, or deleted.

### 4.5 A concrete example directory tree

```
project/
├── data/
│   ├── customers.csv
│   └── transactions.csv
├── src/
│   └── main.py
└── README.md
```

### 4.6 Path components, explained on a real example

Take `data/customers.csv`, relative to `project/`:

- **`data`** — a directory name; the first step of the path.
- **`/`** — a **directory separator** (also called a **path
  separator**) — the character marking a boundary between one
  component and the next. On Linux and macOS this is `/`; on Windows it
  is traditionally `\` (§22–§23 cover this difference, and how
  `pathlib` handles it for you).
- **`customers.csv`** — the final component: a **file name**, itself
  made of two parts:
  - **`customers`** — the **stem** (the name without its extension).
  - **`.csv`** — the **file extension** (or **suffix**) — a convention
    (not an operating-system requirement) hinting at the file's format.

Extending the example: `data/customers.csv`'s **parent directory** is
`data` — the directory that directly contains it. `project`'s parent,
in turn, is whatever directory contains `project` itself, and so on,
all the way up to the filesystem's **root** — the topmost directory,
which has no parent of its own (`/` on Linux/macOS; a drive letter's
top, like `C:\`, on Windows).

### 4.7 Absolute vs. relative paths

An **absolute path** fully describes a location starting from the
filesystem's root, with no ambiguity about where it begins:

```
Linux/macOS:  /home/user/project/data/customers.csv
Windows:      C:\Users\User\project\data\customers.csv
```

A **relative path** describes a location *relative to some starting
point that is not stated in the path itself*:

```
data/customers.csv
```

This relative path only means something once you know what it is
*relative to* — which is exactly what §8 (current working directory)
covers next. `.` refers to "the current location itself"; `..` refers
to "one directory up, toward the parent." `data/../data/customers.csv`
and `data/customers.csv` describe the same location.

## 5. pathlib Fundamentals

### 5.1 The problem with string-based paths

Before `pathlib` existed (and still today, in older or legacy code),
paths were commonly built directly as strings:

```python
# Fragile, string-based path building
folder = "data/"
filename = "customers.csv"
file_path = folder + filename        # "data/customers.csv" -- worked, by luck
```

This looks harmless until it isn't:

```python
folder = "data"     # no trailing slash this time
filename = "customers.csv"
file_path = folder + filename         # "datacustomers.csv" -- WRONG, silently
```

String concatenation has no idea what a "correct path" looks like — it
is just gluing text together, and it is entirely your responsibility to
get every separator exactly right, every time. Two other real problems
compound this: **platform-specific separators** (`/` on Linux/macOS,
`\` on Windows — a hardcoded `/` breaks on Windows, and vice versa),
and the fact that a plain string offers **no path-aware operations at
all** — asking "what's the file extension?" or "what's the parent
directory?" means writing your own string-slicing logic, by hand, for
every single question.

### 5.2 The standard-library alternative: `os.path`

Python has long provided `os.path` specifically to address the
separator problem:

```python
import os

file_path = os.path.join("data", "customers.csv")   # correct on every platform
```

`os.path.join()` genuinely solves the separator problem — it is not
"wrong," and §34 discusses exactly when you will still legitimately
encounter or use it. But it still works entirely with **plain strings**
— every operation (`os.path.basename()`, `os.path.dirname()`,
`os.path.splitext()`, and so on) is a separate top-level function you
call *on* a string, rather than something the path itself knows how to
do.

### 5.3 The `pathlib` philosophy

```python
from pathlib import Path

base = Path("data")
file_path = base / "customers.csv"
print(file_path)
```

```text
data/customers.csv
```

`pathlib` represents a path as a genuine **object** — something with
its own type, its own methods, and its own overloaded operators —
rather than as a plain string you must remember to manipulate
correctly by hand. This is the single biggest philosophical shift: a
`Path` object *knows* it represents a filesystem path, and provides
operations (joining, inspecting, checking existence, reading, writing,
and more — this entire chapter) directly as part of what it is.

### 5.4 Why `/` is overloaded for path composition

```python
Path("data") / "customers.csv"
```

Python lets a class customize what its operators mean for its own
instances (you will formalize this general mechanism, called *operator
overloading*, much later in
[Encapsulation, Abstraction, and Composition](../08-Object-Oriented-Design-Data-Modelling-and-Functional-Style/01-encapsulation-abstraction-and-composition.md)).
`pathlib`'s `Path` class defines what `/` means specifically for path
objects: "join this path with the next component, inserting the
correct separator for the current operating system automatically." The
result reads almost exactly like the path itself — `Path("data") /
"customers.csv"` visually mirrors `data/customers.csv` — while being
immune to the missing-separator bug from §5.1, because `pathlib`, not
you, decides exactly how the join happens.

### 5.5 `PurePath`, `Path`, and their platform-specific subclasses

`pathlib` actually provides a small family of related classes:

| Class | Does filesystem I/O? | Represents | When you'd choose it |
|---|---|---|---|
| `PurePath` | **No** — pure computation only | Whichever path flavor matches the current OS | Rare — mostly a shared base class |
| `PurePosixPath` | **No** | Linux/macOS-style paths (`/`) | Manipulating POSIX-style paths on any OS, without touching disk (e.g. analyzing Linux server paths from a Windows machine) |
| `PureWindowsPath` | **No** | Windows-style paths (`\`, drive letters) | Manipulating Windows-style paths on any OS, without touching disk |
| `Path` | **Yes** | Whichever path flavor matches the current OS | **The practical, default choice for almost all application code** |
| `PosixPath` | **Yes** | Linux/macOS-style paths | Rarely instantiated directly — `Path()` becomes this automatically on Linux/macOS |
| `WindowsPath` | **Yes** | Windows-style paths | Rarely instantiated directly — `Path()` becomes this automatically on Windows |

```python
from pathlib import Path

p = Path("data/customers.csv")
print(type(p))
```

```text
<class 'pathlib.PosixPath'>      # on Linux/macOS/WSL2
<class 'pathlib.WindowsPath'>    # on Windows
```

`Path(...)` is a **factory** — you call it as if it were a plain
class, but it automatically hands you back the correct concrete
subclass (`PosixPath` or `WindowsPath`) for the machine your code is
actually running on. **This is the single most important practical
fact in this entire section: write `Path(...)` in your code, always,
and let it figure out the platform on its own** — you almost never need
to name `PosixPath` or `WindowsPath` directly. The `Pure*` classes
exist for the specific, uncommon case of needing to *reason about* a
path belonging to a *different* operating system than the one your
code is currently running on, without ever touching that other
system's actual filesystem (for example, validating the shape of a
Windows-style path while your analysis script runs on Linux).

## 6. Path Construction

### 6.1 The basic constructors

```python
from pathlib import Path

Path()                              # the current directory, "."
Path("data")                        # a single relative component
Path("data", "customers.csv")       # multiple components, joined for you
Path("data/customers.csv")          # a single string containing a separator -- also works
```

All of the last three produce a path representing `data/customers.csv`
— `pathlib` accepts either several separate components as separate
arguments, or one string already containing separators; it does not
require you to pick one style consistently.

### 6.2 `Path.cwd()` and `Path.home()` — previewed here, developed fully in §8 and §10

```python
Path.cwd()     # the current working directory, as an absolute Path
Path.home()    # the current user's home directory, as an absolute Path
```

### 6.3 Joining paths with `/`

```python
base = Path("data")
raw_dir = base / "raw"
customers_file = raw_dir / "customers.csv"

print(customers_file)
```

```text
data/raw/customers.csv
```

`/` can be chained freely, and the right-hand side can be a plain
string (as shown) or another `Path` object — both work identically.

### 6.4 Why this is preferable to a raw string

```python
# Fragile
file_path_str = "data/raw/customers.csv"

# Robust
file_path = Path("data") / "raw" / "customers.csv"
```

The `Path` version is immune to the missing-separator bug (§5.1), reads
clearly as a sequence of deliberate steps, and — critically — is
immediately usable with every method the rest of this chapter teaches
(`.exists()`, `.read_text()`, `.parent`, and so on), none of which a
plain string supports on its own.

### 6.5 Common mistake: mixing `/` with an absolute-looking string

```python
Path("data") / "/etc/passwd"
```

```text
PosixPath('/etc/passwd')
```

**Edge case worth knowing:** if the right-hand operand of `/` is itself
an absolute path, the result is *just that absolute path* — the
left-hand side is discarded entirely, exactly mirroring how
`os.path.join()` has always behaved. This is rarely what you want by
accident, and is precisely why §25 (validation) and §26 (path
traversal) both insist on checking, not assuming, where a
user-influenced path ultimately points.

## 7. Path Components

### 7.1 The properties, on one running example

```python
from pathlib import Path

p = Path("/home/user/project/data/report.csv")

print(p.name)        # 'report.csv'
print(p.stem)         # 'report'
print(p.suffix)        # '.csv'
print(p.suffixes)       # ['.csv']
print(p.parent)          # PosixPath('/home/user/project/data')
print(p.parts)            # ('/', 'home', 'user', 'project', 'data', 'report.csv')
print(p.anchor)            # '/'
print(p.root)                # '/'
print(p.drive)                # ''  -- empty on POSIX; a drive letter on Windows
```

```text
report.csv
report
.csv
['.csv']
/home/user/project/data
('/', 'home', 'user', 'project', 'data', 'report.csv')
/
/

```

### 7.2 What each one means

- **`.name`** — the final path component: the file (or directory)
  name, including any extension.
- **`.stem`** — `.name`, with the *last* extension removed.
- **`.suffix`** — the last extension, including its leading dot (an
  empty string `''` if there is none).
- **`.suffixes`** — a `list` of *every* extension, for names with more
  than one (e.g. `Path("archive.tar.gz").suffixes` is `['.tar',
  '.gz']`).
- **`.parent`** — a new `Path` representing the directory that directly
  contains this one; §7.3 shows how repeated `.parent` navigates
  further up.
- **`.parts`** — a `tuple` of every individual component, useful for
  programmatic inspection or iteration.
- **`.anchor`** — the combination of `.drive` and `.root` together —
  effectively "everything before the first real path component."
- **`.root`** — the root marker alone (`'/'` on POSIX; `'\\'` on
  Windows for a path with a drive, or empty for a relative path).
- **`.drive`** — the Windows drive letter or UNC share (e.g. `'C:'`);
  always `''` on Linux/macOS, since POSIX filesystems have no concept
  of drive letters.

### 7.3 `.parents` — walking upward

```python
p = Path("/home/user/project/data/report.csv")

print(p.parents[0])   # /home/user/project/data
print(p.parents[1])   # /home/user/project
print(p.parents[2])   # /home/user

for ancestor in p.parents:
    print(ancestor)
```

`.parents` is an indexable, iterable sequence of every ancestor
directory, from the nearest (`p.parent`, i.e. `p.parents[0]`) up to the
filesystem root. (**Version note:** slicing `.parents` — e.g.
`p.parents[1:3]` — is supported starting in Python 3.10; on earlier
versions, only single-index access like `p.parents[1]` works.)

### 7.4 Linux vs. Windows differences in these properties

On a Windows path like `WindowsPath("C:/Users/User/report.csv")`,
`.drive` is `'C:'`, `.root` is `'\\'`, and `.anchor` is `'C:\\'`. On
Linux/macOS, `.drive` is always `''`, since there is no drive-letter
concept — `.root` alone (`'/'`) carries the entire "where absolute
paths begin" meaning.

## 8. Current Working Directory

### 8.1 What the current working directory is

Every running process (your Python program included) has a **current
working directory (cwd)** — the directory relative paths are
interpreted against by default. `Path.cwd()` returns it as an absolute
`Path`:

```python
from pathlib import Path

print(Path.cwd())
```

```text
/home/user/project
```

### 8.2 Why it matters — relative paths only mean something in context

```python
data_path = Path("data/customers.csv")
```

This relative path means "`customers.csv`, inside a `data` directory,
**located inside whatever the current working directory happens to
be**" — it says nothing at all about an absolute location on its own.

### 8.3 A realistic failure: running from the wrong directory

Suppose `src/main.py` contains `data_path = Path("data/customers.csv")`
and `data/` genuinely exists as a sibling of `src/`, at
`project/data/`. Running:

```bash
cd project
python src/main.py
```

resolves `data/customers.csv` against `project/` (the cwd) — correctly
finding `project/data/customers.csv`. But running instead from inside
`src/`:

```bash
cd project/src
python main.py
```

resolves the *exact same relative path* against `project/src/` instead
— looking for a nonexistent `project/src/data/customers.csv`, and
raising `FileNotFoundError`. **The code did not change at all between
these two runs — only the cwd did.** This is one of the single most
common sources of "it works on my machine but not when someone else
runs it" bugs in real projects.

### 8.4 Why cwd varies across CLI tools, IDEs, tests, and notebooks

The current working directory is set by *whatever process launched
your program*, not by your script's own location: a terminal's cwd is
wherever you last `cd`'d to; many IDEs set the cwd to the currently
open project's root folder, regardless of which specific file is
running; `pytest` typically runs with the cwd set to wherever you
invoked it from; a Jupyter notebook's cwd is typically wherever the
notebook server itself was started — none of these are guaranteed to
match the folder your source file physically lives in.

### 8.5 `Path.cwd()` vs. `Path(__file__).resolve().parent`

```python
Path.cwd()                          # wherever the process happened to be launched from
Path(__file__).resolve().parent      # the directory containing THIS source file, regardless of cwd
```

`__file__` is a variable Python automatically sets inside a script to
that script's own file path. `Path(__file__).resolve().parent` (§9
explains `.resolve()` fully) therefore gives you a path anchored to
**where your code lives**, immune to §8.3's failure mode entirely —
this is exactly §9's subject.

**Important caveat:** `__file__` is not always defined — in an
interactive REPL session and in some notebook environments, referencing
`__file__` raises `NameError`. Code relying on `Path(__file__)` should
be a `.py` script, not something run interactively without adaptation.

## 9. Project-Relative Paths

### 9.1 The standard, professional pattern

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
```

This is the idiomatic way real Python projects anchor their paths:
compute one absolute base directory, once, relative to the source
file's own known location — then build every other path the program
needs *from* that fixed anchor.

### 9.2 The calculation depends on exactly where the source file lives

If `main.py` lives directly inside `project/src/`, then
`Path(__file__).resolve().parent` is `project/src` — so
`BASE_DIR / "data"` gives `project/src/data`, **not**
`project/data`. If you actually want `project/data` (a sibling of
`src/`, not a child of it), you need one more `.parent`:

```python
BASE_DIR = Path(__file__).resolve().parent.parent   # project/, one level above src/
DATA_DIR = BASE_DIR / "data"                          # project/data
```

**This is worth verifying deliberately, every time** — the exact
number of `.parent` calls needed depends entirely on your project's
real folder layout, and getting it wrong by one level is a common,
easy-to-make mistake.

### 9.3 Why blindly using `Path.cwd()` can break

```python
# FRAGILE -- assumes the program is always launched from project/
DATA_DIR = Path.cwd() / "data"
```

Exactly §8.3's failure mode: this line's meaning depends entirely on
*how the program happens to be launched*, not on anything the program
itself controls.

### 9.4 Four different sources of "where should this path point," and when each is right

- **Project-relative paths** (`Path(__file__).resolve().parent`, §9.1)
  — correct for locating files that are *part of the project itself*
  (bundled data, templates, default config) and must be found
  regardless of cwd.
- **Configuration-based paths** — a path read from a config file (fully
  developed in
  [09-environment-configuration-and-input-validation.md](09-environment-configuration-and-input-validation.md))
  — correct when *where to read/write* should be adjustable without
  editing code.
- **Environment-provided paths** — a path read from an environment
  variable — correct for deployment-specific locations (a different
  data directory in production vs. on a developer's laptop) that should
  not be hardcoded anywhere.
- **User-provided paths** — a path typed by a user, or passed as a CLI
  argument (§06's subject) — correct for interactive tools, but *must*
  be validated (§25) before being trusted.

## 10. Path Resolution

### 10.1 `.absolute()` — a simple, syntactic operation

```python
p = Path("data/report.csv")
print(p.absolute())
```

```text
/home/user/project/data/report.csv
```

`.absolute()` simply **prepends the current working directory** to a
relative path — a purely syntactic operation. It does **not** touch the
filesystem, does **not** resolve `..` or `.` components, and does
**not** follow symbolic links.

### 10.2 `.resolve()` — genuinely touches the filesystem

```python
p = Path("../data/./file.txt")
print(p.resolve())
```

```text
/home/user/project/data/file.txt
```

`.resolve()` does everything `.absolute()` does, *plus*: it eliminates
`.` and `..` components by actually consulting the filesystem, and it
**follows symbolic links** (§18) to their real, final target. **Do not
treat `.resolve()` as merely "a fancier `.absolute()`"** — because it
consults the real filesystem and follows real symlinks, its result can
depend on what currently, actually exists on disk, not purely on the
text of the path itself.

### 10.3 Strict vs. non-strict resolution

```python
Path("does/not/exist.txt").resolve()                 # succeeds -- returns a normalized absolute path anyway
Path("does/not/exist.txt").resolve(strict=True)        # raises FileNotFoundError
```

By default (`strict=False`, the default since Python 3.6), `.resolve()`
does not require the path to actually exist — it normalizes as much as
it can and returns a best-effort absolute path regardless.
`strict=True` instead requires every component to genuinely exist,
raising `FileNotFoundError` if not — useful when you specifically need
"resolve, and confirm this is real" as one combined step.

### 10.4 `.expanduser()` — resolving `~`

```python
p = Path("~/notes.txt")
print(p)                    # ~/notes.txt  -- '~' is NOT expanded automatically
print(p.expanduser())        # /home/user/notes.txt
```

`Path` does **not** automatically expand a leading `~` (a shell
convention meaning "the current user's home directory") — `pathlib`
treats `~` as a perfectly ordinary character in a path component until
you explicitly call `.expanduser()`.

### 10.5 `.relative_to()` and `.is_relative_to()`

```python
base = Path("/home/user/project")
target = Path("/home/user/project/data/report.csv")

print(target.relative_to(base))         # data/report.csv
print(target.is_relative_to(base))       # True
```

`.relative_to()` computes the relative path from `base` to `target`,
raising `ValueError` if `target` is not actually inside `base`.
`.is_relative_to()` answers the yes/no version of the same question
without raising. **Version note:** `.is_relative_to()` was added in
Python 3.9 — on earlier versions, you must call `.relative_to()`
inside a `try`/`except ValueError` instead. §26 puts `.is_relative_to()`
to direct, practical use for path-traversal defense. **Another version
note:** `.relative_to()` gained an optional `walk_up=True` keyword
argument in Python 3.12, allowing it to compute a relative path that
walks *upward* (using `..`) even when `target` is not strictly inside
`base` — before 3.12, `.relative_to()` only succeeds when `target`
truly is a descendant of `base`.

## 11. Filesystem Inspection

### 11.1 `.exists()`

```python
Path("data/customers.csv").exists()   # True or False
```

Returns `True` if *something* exists at this path — file, directory,
or otherwise — `False` if nothing does, or if the path cannot currently
be checked (for example, a component along the way lacks permission to
even be examined — this returns `False` rather than raising, in
typical cases).

### 11.2 `.is_file()` and `.is_dir()`

```python
p = Path("data/customers.csv")

if p.is_file():
    print("It's a file")
elif p.is_dir():
    print("It's a directory")
else:
    print("Doesn't exist, or isn't a regular file/directory")
```

**Why checking the type matters:** a path can exist without being the
kind of thing you expect — attempting to `open()` a directory raises
`IsADirectoryError` (already covered in
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§18.1), a failure `.is_file()` lets you anticipate and handle
deliberately instead of discovering by accident.

### 11.3 `.is_symlink()`

```python
Path("latest_release").is_symlink()
```

`True` if the path itself is a symbolic link (§18), regardless of
whether the link's *target* exists — this is an important distinction
from `.exists()`, which follows the link and reports on the *target*.

### 11.4 Rarer, platform-specific type checks

| Method | Checks for | Notes |
|---|---|---|
| `.is_mount()` | Whether the path is a mount point (a filesystem attached at this location) | POSIX-oriented; Windows support was added in Python 3.12 |
| `.is_block_device()` | A block device file (e.g. `/dev/sda`) | POSIX-only concept; rarely relevant to application code |
| `.is_char_device()` | A character device file (e.g. `/dev/tty`) | POSIX-only concept; rarely relevant to application code |
| `.is_fifo()` | A named pipe | POSIX-only concept; used in inter-process communication scenarios |
| `.is_socket()` | A Unix domain socket file | POSIX-only concept; used in inter-process communication scenarios |

These five exist for completeness and low-level systems programming —
you are unlikely to need them in typical application, data, or AI
engineering code, but they are genuine, documented `pathlib` methods,
included here so you recognize them if you ever encounter them.

## 12. Directory Traversal

### 12.1 `.iterdir()` — direct children only

```python
for entry in Path("data").iterdir():
    print(entry)
```

```text
data/customers.csv
data/transactions.csv
data/raw
```

`.iterdir()` yields each *direct* child of a directory — files,
subdirectories, and (on some platforms) other filesystem object types
— **one level deep only**, in no particular guaranteed order.

### 12.2 `.glob()` — pattern matching within a directory

```python
list(Path("data").glob("*.csv"))
```

```text
[PosixPath('data/customers.csv'), PosixPath('data/transactions.csv')]
```

`.glob(pattern)` yields every child (at the depth the pattern
specifies) matching a **glob pattern** — a simplified wildcard syntax,
not a full regular expression:

| Pattern piece | Meaning |
|---|---|
| `*` | Any number of characters (not crossing a `/`) |
| `?` | Exactly one character |
| `[abc]` | Any one character among `a`, `b`, or `c` |
| `**` | Any number of directories, recursively (only meaningful with `.glob()`, not implied automatically) |

```python
Path("data").glob("*.csv")            # direct children only, matching *.csv
Path("data").glob("**/*.json")         # every .json file, at any depth, recursively
```

### 12.3 `.rglob()` — recursive shorthand

```python
list(Path("data").rglob("*.json"))
```

`Path("data").rglob("*.json")` is exactly equivalent to
`Path("data").glob("**/*.json")` — a shorter way to say "search
recursively, at every depth."

### 12.4 Ordering is not guaranteed

```python
sorted(Path("data").iterdir())
```

**`.iterdir()`, `.glob()`, and `.rglob()` do not guarantee any
particular, deterministic order** — the order reflects whatever the
underlying filesystem happens to return, which can vary by platform,
filesystem type, and even between runs. Whenever deterministic output
matters (tests, reports, reproducible logs), **sort explicitly**, as
shown above.

### 12.5 Hidden files, symbolic links, and performance

On Linux/macOS, filenames beginning with `.` are conventionally
"hidden" from typical directory listing tools, but `.iterdir()` and
`.glob("*")` **do include them** — `pathlib` performs no hiding on
your behalf; filter explicitly (e.g. `if not entry.name.startswith("."):`)
if you want that behavior. `.glob()`/`.rglob()` follow symbolic links
by default when descending into directories, which can matter for both
correctness (accidentally traversing outside the intended tree) and
performance (traversing a symlink cycle) — §18 and §29 return to this.
For very large directory trees, `.rglob()`'s cost is directly
proportional to the number of files and directories visited — §29
covers this fully.

## 13. Directory Creation

### 13.1 `.mkdir()` — the basics

```python
Path("data").mkdir()
```

Creates exactly one new directory. **What happens when things are not
this simple:**

```python
Path("data/raw").mkdir()           # raises FileNotFoundError if "data" does not already exist
Path("data").mkdir()                 # raises FileExistsError if "data" already exists
```

### 13.2 `parents=True` and `exist_ok=True`

```python
Path("data/raw/2024").mkdir(parents=True)               # creates every missing intermediate directory too
Path("data").mkdir(exist_ok=True)                          # does not raise if "data" already exists
Path("data/raw/2024").mkdir(parents=True, exist_ok=True)     # the common, safe combination
```

`parents=True` makes `.mkdir()` behave like "make sure this whole path
exists, creating any missing directories along the way" rather than
"create exactly one directory, whose parent must already exist."
`exist_ok=True` makes `.mkdir()` treat "it's already there" as success
rather than an error — the combination of both is the standard,
idiomatic way to ensure a directory exists, regardless of whether this
is the first time your program has run.

### 13.3 `mode` — a brief, honest note

```python
Path("data").mkdir(mode=0o755)
```

`mode` sets the new directory's permission bits (on POSIX systems) —
`0o755` is a common default meaning "owner can read/write/enter; others
can read/enter." §24 covers permissions conceptually; full permission
management is outside this chapter's scope. Note that the *actual*
resulting permissions can be further limited by the operating system's
own default umask — `mode` is a request, not an absolute guarantee, on
some systems.

### 13.4 Race conditions during directory creation

```python
# TWO separate processes, running this at nearly the same moment:
Path("data").mkdir(exist_ok=True)
```

Even with `exist_ok=True`, if two processes race to create the same
directory at almost exactly the same instant, one can still encounter
an `OSError` in rare circumstances, depending on platform and timing —
`exist_ok=True` eliminates the *common* "it already exists, and that's
fine" case, but does not provide an absolute, universal guarantee under
every possible concurrent scenario. §27 develops this class of problem
(TOCTOU) fully.

## 14. File Creation

### 14.1 `.touch()`

```python
Path("example.txt").touch()
```

Creates a new, empty file if none exists at this path. If a file
**already** exists there, the default behavior is to simply update its
modification timestamp (§16), leaving its content completely
untouched.

### 14.2 `exist_ok` and why `touch()` is not "safe create"

```python
Path("example.txt").touch(exist_ok=True)    # default: succeed silently either way
Path("example.txt").touch(exist_ok=False)    # raise FileExistsError if it already exists
```

**Critical distinction:** `.touch()`'s *default* behavior
(`exist_ok=True`) means calling it on an existing file does **not**
raise an error and does **not** erase its content — but it also gives
you **no guarantee that you are the one who just created a brand-new,
empty file.** If your intent is genuinely "create this file only if it
does not already exist, and fail loudly otherwise," `touch(exist_ok=False)`
is the correct call — mirroring exactly the "x" mode guarantee from
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§9.6.

### 14.3 `mode` and race conditions

`.touch()` also accepts a `mode` parameter (§13.3's same POSIX
permission-bits concept). Like `.mkdir()`, `.touch(exist_ok=False)`
still cannot provide an absolute guarantee against every possible
concurrent-access timing scenario — §27 covers this properly.

## 15. File Reading/Writing Integration

This section connects `pathlib` to file I/O — it does not repeat
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
full treatment of reading and writing; it explains only how `pathlib`
integrates with what that chapter already taught.

### 15.1 `.read_text()` and `.write_text()`

```python
from pathlib import Path

text = Path("notes.txt").read_text(encoding="utf-8")

Path("notes.txt").write_text("Hello", encoding="utf-8")
```

These are convenience methods: each one **opens the file, performs the
one operation, and closes the file again — all in a single call**,
equivalent to:

```python
with Path("notes.txt").open("r", encoding="utf-8") as f:
    text = f.read()

with Path("notes.txt").open("w", encoding="utf-8") as f:
    f.write("Hello")
```

Both accept `encoding=` (§25 of the previous chapter's own
[Encoding Basics](01-reading-and-writing-text-files.md#25-encoding-basics)
section covers *why* this should almost always be `"utf-8"`, explicit)
and `errors=`. `write_text()` also accepts `newline=` (added in Python
3.10).

### 15.2 `.open()` — pathlib's bridge back to ordinary file objects

```python
with Path("notes.txt").open("r", encoding="utf-8") as f:
    for line in f:
        print(line)
```

`Path.open(...)` behaves exactly like the built-in `open(...)` you
already know — same modes, same parameters, same returned file object
— the only difference is that you call it as a method *on* the path
object, rather than passing the path *to* a free function.

### 15.3 When `read_text()`/`write_text()` are convenient, and when `.open()` is preferable

`read_text()`/`write_text()` are ideal for small files where you
genuinely want the entire content in one call, with no manual
`with`/`close()` bookkeeping. `.open()` (used exactly like plain
`open()`, with a `with` block) is preferable whenever you need
line-by-line iteration, streaming/chunked processing for large files,
or multiple operations within the same open connection — exactly the
large-file and streaming concerns
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§30–§31 already cover in full; `pathlib` does not change any of that
guidance, it only changes how you spell the `open()` call itself.

## 16. Metadata

### 16.1 `.stat()`

```python
info = Path("data/customers.csv").stat()

print(info.st_size)     # size, in bytes
print(info.st_mtime)      # last-modified time, as a Unix timestamp (float)
print(info.st_ctime)       # platform-dependent -- see below
print(info.st_mode)         # file type + permission bits, packed into one integer
```

`.stat()` asks the operating system for a structured record of
low-level information about the file or directory — the same
underlying information the `os.stat()` function provides, wrapped by
`pathlib` for convenience.

### 16.2 The most useful attributes

- **`st_size`** — the size, in bytes.
- **`st_mtime`** — the last-*modified* time (content changed), as
  seconds since the Unix epoch — convert to something readable with
  `datetime.fromtimestamp(info.st_mtime)`.
- **`st_ctime`** — on Linux, this is the last time the file's
  *metadata* changed (permissions, ownership — not necessarily
  content); on Windows, this instead reports the file's **creation**
  time. **This is a genuine, important platform difference — do not
  assume `st_ctime` universally means "creation time."**
- **`st_mode`** — an integer packing together the file type and
  permission bits; typically inspected via the `stat` standard-library
  module's helper functions rather than decoded by hand.

### 16.3 `.lstat()` — the symlink-aware variant

```python
Path("latest_release").stat()     # follows the symlink; reports the TARGET's metadata
Path("latest_release").lstat()      # does NOT follow the symlink; reports the LINK's own metadata
```

`.stat()` transparently follows symbolic links (§18) and reports on
whatever the link ultimately points *to*. `.lstat()` reports on the
symlink object itself — its own size (typically just the length of the
target path text), its own timestamps — without following it.

## 17. Rename/Replace/Delete

### 17.1 `.rename()`

```python
old = Path("old.txt")
new = Path("new.txt")

old.rename(new)
```

Renames (or moves, if `new` is in a different directory) `old` to
`new`. **Platform-dependent behavior when `new` already exists:** on
POSIX systems (Linux/macOS), `.rename()` silently overwrites an
existing destination; on Windows, it **raises `FileExistsError`**
instead. This inconsistency is exactly why §17.2 exists.

### 17.2 `.replace()`

```python
old.replace(new)
```

`.replace()` behaves like `.rename()`, but **guarantees consistent
"overwrite if it exists" behavior across every platform** — making it
the more portable, predictable choice whenever overwriting an existing
destination is genuinely intended. Both `.rename()` and `.replace()`
return a new `Path` object pointing at the destination.

### 17.3 Cross-filesystem limitations and atomicity

Both `.rename()` and `.replace()` are typically **atomic** (the
operation either fully completes or does not happen at all — never
leaving a half-renamed state) **when the source and destination are on
the same filesystem/volume**. Renaming across genuinely different
filesystems (for example, between two separate mounted drives) may not
be atomic, and on some platforms/filesystem combinations may fail
outright or fall back to a non-atomic copy-then-delete. §28 builds
directly on this fact for a genuinely production-safe write pattern.

### 17.4 `.unlink()` and `.rmdir()`

```python
Path("file.txt").unlink()          # deletes a file
Path("empty_dir").rmdir()            # deletes a directory -- ONLY if it is empty
```

`.rmdir()` **only removes a genuinely empty directory** — calling it on
a directory that still contains anything raises `OSError` (specifically
`OSError: [Errno 39] Directory not empty` on Linux). Deleting a
directory *and everything inside it* recursively is **not** a `pathlib`
capability at all — it belongs to `shutil.rmtree()` (§19, §34) — a
deliberate design choice, since recursive deletion is dangerous enough
that it should never be one accidental method call away.

### 17.5 Common deletion exceptions

```python
Path("file.txt").unlink(missing_ok=False)   # the default: raises FileNotFoundError if it's already gone
Path("file.txt").unlink(missing_ok=True)     # silently succeeds either way (Python 3.8+)
```

| Exception | Raised by | Typical cause |
|---|---|---|
| `FileNotFoundError` | `.unlink()`, `.rmdir()` | Already deleted, or never existed |
| `PermissionError` | `.unlink()`, `.rmdir()` | Insufficient OS-level permission |
| `IsADirectoryError` | `.unlink()` | Called on a directory instead of a file |
| `NotADirectoryError` | `.rmdir()` | Called on a file instead of a directory |
| `OSError` (directory not empty) | `.rmdir()` | The directory still contains something |

### 17.6 Safe deletion principles

Confirm the type (`.is_file()`/`.is_dir()`) before deleting, so you get
a clear, anticipated exception rather than a confusing one; prefer
`missing_ok=True` only when "already gone" is a genuinely acceptable
outcome for your program's logic, not as a reflex to silence errors;
never delete based on a user-provided path without the validation §25
and §26 both require.

## 18. Symbolic Links

### 18.1 What a symbolic link is

A **symbolic link** (or **symlink**) is a special filesystem entry that
does not contain real data itself — it simply *points at* another path
(its **target**). Opening, reading, or writing through a symlink
transparently operates on whatever it points to, as if the symlink
were the real thing.

### 18.2 Creating and inspecting symlinks

```python
Path("latest").symlink_to("release-2.3")    # creates "latest" as a link pointing at "release-2.3"

Path("latest").is_symlink()                    # True
Path("latest").readlink()                        # PosixPath('release-2.3') -- the link's raw target
```

`.readlink()` (added in Python 3.9) returns the target the symlink
points at, *without* following it further — the raw text of where the
link says to go.

### 18.3 Relative vs. absolute symlinks

A symlink's target can itself be a relative path (interpreted relative
to the *symlink's own location*, not your program's cwd) or an
absolute path. A relative-target symlink remains correct if the whole
containing directory tree is moved together; an absolute-target symlink
breaks if the target's absolute location ever changes.

### 18.4 Broken symlinks

```python
Path("latest").symlink_to("does_not_exist")

Path("latest").is_symlink()   # True -- the LINK itself exists
Path("latest").exists()         # False -- the link's TARGET does not exist
```

**This distinction matters:** `.exists()` follows the link and reports
on the target, while `.is_symlink()` reports on the link object
itself — a broken symlink is `is_symlink() == True` and
`exists() == False` simultaneously, and code that only checks
`.exists()` will simply treat a broken symlink as "nothing here,"
without any indication that a dangling link is actually present.

### 18.5 `.stat()` vs. `.lstat()`, revisited, and `.resolve()`

Directly connecting back to §16.3 and §10.2: `.stat()` follows
symlinks (reporting the target's metadata); `.lstat()` does not
(reporting the link's own metadata); `.resolve()` follows symlinks all
the way to their final, real target when computing an absolute,
normalized path.

### 18.6 A brief, honest security note

Symbolic links are one of the mechanisms behind a category of attack
called a **symlink attack** — where a program that blindly trusts a
path (without confirming it is not secretly a symlink pointing
somewhere unintended) can be tricked into reading or writing a
completely different location than the one it believes it is
operating on. §26 covers path-traversal defense generally; be aware
that a *validated-looking* path can still, in principle, be a symlink
in disguise — production systems handling genuinely untrusted paths
often need to account for this explicitly, beyond this chapter's
introductory scope.

## 19. Copy and Move — `pathlib` and `shutil`

### 19.1 Why `pathlib` does not do this itself

`pathlib` is fundamentally about **representing and manipulating
paths**, and performing the *simple* filesystem operations naturally
tied to a single path (§13, §14, §17, §18). Copying a file's *entire
content* to a new location, or copying an entire directory tree, is a
meaningfully more involved operation (potentially touching many files,
needing to handle partial failures, needing to preserve or not preserve
metadata) — this is deliberately `shutil`'s responsibility, not
`pathlib`'s.

### 19.2 The standard combination

```python
from pathlib import Path
from shutil import copy2, copytree, move

source = Path("data/customers.csv")
destination = Path("backup/customers.csv")

copy2(source, destination)          # copies content AND metadata (timestamps, permissions)
copytree(Path("data"), Path("backup/data"))    # copies an entire directory tree
move(source, destination)             # moves a file or directory (across filesystems if needed)
```

Every `shutil` function shown here accepts `Path` objects directly —
there is no need to convert to `str` first (§21 covers exactly why this
interoperability works).

### 19.3 `shutil.copy()` vs. `shutil.copy2()`

`copy()` copies a file's content and its permission bits.
`copy2()` additionally attempts to preserve metadata like modification
timestamps — generally the more complete, and more commonly used,
choice when the goal is a faithful duplicate.

## 20. Path Transformations

### 20.1 `.with_name()`

```python
p = Path("data/report.csv")
print(p.with_name("summary.csv"))
```

```text
data/summary.csv
```

Returns a **new** `Path`, identical to `p` except with the final
component entirely replaced.

### 20.2 `.with_stem()`

```python
p = Path("data/report.csv")
print(p.with_stem("summary"))
```

```text
data/summary.csv
```

Replaces only the stem, keeping the existing suffix. **Version note:**
`.with_stem()` was added in Python 3.9 — on earlier versions, the
equivalent must be built manually with `.with_name(new_stem + p.suffix)`.

### 20.3 `.with_suffix()`

```python
p = Path("data/report.csv")
print(p.with_suffix(".json"))
```

```text
data/report.json
```

### 20.4 The critical distinction: these do **not** touch the filesystem

**`p.with_suffix(".json")` does not rename the file on disk.** It
returns a brand-new `Path` *object*, representing a different
hypothetical location — the original file, if one exists, is
completely untouched. Actually renaming requires explicitly calling
`.rename()` (§17.1) with the transformed path:

```python
p = Path("data/report.csv")
new_path = p.with_suffix(".json")   # just a new Path VALUE -- nothing has happened on disk yet
p.rename(new_path)                    # THIS is what actually renames the file
```

### 20.5 `.with_segments()` — a brief mention

**Version note:** `.with_segments()` was added in Python 3.12,
primarily to support library authors building custom `Path` subclasses
— it is not something typical application code needs to call directly,
and is included here purely for recognition if you encounter it.

## 20b. `.relative_to()` and `.is_relative_to()`, revisited

Already introduced in §10.5 as part of path resolution — they are
mentioned again here because they are, in a real sense, also
*transformations* (computing a new, relative representation of an
existing path) and *comparisons* (§26 relies on `.is_relative_to()`
directly for security validation).

## 21. Path Matching

### 21.1 `Path.match()`

```python
Path("data/report.csv").match("*.csv")           # True
Path("data/report.csv").match("data/*.csv")        # True
Path("data/report.csv").match("*.json")              # False
```

`.match()` tests whether **this single path** matches a glob-style
pattern (§12.2's same wildcard syntax) — it does not search a
directory at all; it is a pure yes/no check against one already-known
path.

### 21.2 Comparing `.glob()`, `.rglob()`, and `.match()`

| Method | What it does | Searches the filesystem? |
|---|---|---|
| `.glob(pattern)` | Finds children of a directory matching a pattern | **Yes** |
| `.rglob(pattern)` | Finds descendants at any depth matching a pattern | **Yes** |
| `.match(pattern)` | Tests whether one specific, already-known path matches a pattern | **No** |

`.glob()`/`.rglob()` answer "what files out there match this pattern?"
`.match()` answers "does this one path (which I already have) match
this pattern?" — a subtle but important difference in purpose.

### 21.3 A caveat about `**` in `.match()`

**Version-sensitive behavior worth knowing:** historically (through
Python 3.12), `.match()` treated `**` no differently from a single `*`
— it did **not** support recursive matching the way `.glob("**/...")`
does. Python 3.13 changed `.match()` to support `**` recursively and
added a `case_sensitive` keyword parameter, matching `.glob()`'s
behavior more closely. If recursive-depth matching is genuinely needed
and you cannot assume Python 3.13+, prefer `.rglob()` (which reliably
supports recursion on every supported version) over relying on
`.match("**/...")`.

## 22. PathLike and Interoperability

### 22.1 `os.PathLike`

```python
import os
from pathlib import Path

path = Path("data/file.txt")

print(isinstance(path, os.PathLike))   # True
```

`os.PathLike` is an **abstract interface** — any object implementing it
(via a special `__fspath__` method) can be used anywhere a path is
expected, without needing to first be converted to a plain string.
`Path` objects implement this interface, which is *exactly* why
functions like the built-in `open()`, `shutil.copy2()`, and
essentially the entire standard library accept `Path` objects directly
— they were written to accept anything satisfying `os.PathLike`, not
only literal strings.

### 22.2 `os.fspath()`

```python
os.fspath(path)   # 'data/file.txt' -- the plain string form
```

`os.fspath()` explicitly converts any `PathLike` object (including a
`Path`) into its plain-string representation — occasionally needed for
the rare API that genuinely requires a literal `str` and does not
itself accept `PathLike` objects.

### 22.3 Why this matters practically

Because of this interoperability, you can pass a `Path` object directly
into essentially every standard-library and well-behaved third-party
function that deals with files — `open()`, `shutil` functions,
`subprocess` arguments, and more — **without manually calling `str()`
first, in the overwhelming majority of cases.** §23 develops exactly
when explicit conversion is still genuinely necessary.

## 23. Str vs. Path

### 23.1 A direct comparison

| | String path (`"data/file.txt"`) | `Path` object (`Path("data/file.txt")`) |
|---|---|---|
| **Readability** | Manual string concatenation risk (§5.1) | `/`-based composition, reads as intended steps |
| **Composition** | Manual, error-prone | Built-in, correct-by-construction |
| **Portability** | You must handle separators yourself | Handled automatically per-platform |
| **Available operations** | None — just a plain string | `.exists()`, `.is_file()`, `.parent`, `.stat()`, and everything else in this chapter |
| **Interoperability** | Universally accepted | Accepted almost everywhere via `os.PathLike` (§22) |

### 23.2 `str(path)` and when conversion is genuinely required

```python
str(Path("data/file.txt"))   # 'data/file.txt'
```

Use `str(path)` (or `os.fspath(path)`, functionally equivalent for this
purpose) when you must hand a path to something that specifically,
genuinely requires a plain `str` — some older third-party libraries not
yet updated for `PathLike` support, string formatting/logging where you
want the textual form, or building a value that must literally be a
`str` for an unrelated reason (e.g. as a dictionary key compared
against other plain strings).

### 23.3 Why repeatedly converting back and forth makes code harder to reason about

```python
# AVOID -- converting to str and back repeatedly, losing Path's benefits along the way
def process(path_str: str) -> None:
    path = Path(path_str)
    ...
    next_str = str(path.parent)
    do_something_else(next_str)
```

Every conversion back to `str` throws away everything `pathlib` gives
you (§23.1) until the next `Path(...)` call rebuilds it. **The
idiomatic habit: keep `Path` objects as `Path` objects internally,
throughout your own code, and convert to `str` only at the exact
boundary where an external API genuinely demands it** — never as a
routine, in-between step. §36's reusable functions consistently model
this habit.

## 24. Cross-Platform Portability

### 24.1 Why this is wrong in supposedly portable Python

```python
# WRONG -- hardcodes a Windows-specific, absolute, machine-specific path
path = "C:\\Users\\John\\data\\file.txt"
```

This fails outright on Linux/macOS (no `C:\` concept exists there), and
even on *other* Windows machines, since it assumes a specific
username (`John`) and drive layout that will not generally match.

### 24.2 What actually differs across platforms

- **Path separators** — `/` (POSIX) vs. `\` (Windows, though Windows
  also accepts `/` in most contexts).
- **Drive letters** — `C:\`, `D:\`, and so on, exist only on Windows;
  POSIX systems have a single, unified root (`/`) instead.
- **UNC paths** — Windows network paths like `\\server\share\file.txt`
  have no POSIX equivalent at all.
- **Home directories** — `/home/username` (Linux), `/Users/username`
  (macOS), `C:\Users\username` (Windows) — all different, all handled
  correctly and uniformly by `Path.home()` (§4 already introduced this;
  §9 already relies on it).
- **Case sensitivity** — Linux filesystems are typically
  case-*sensitive* (`Report.csv` and `report.csv` are different files);
  Windows and (by default) macOS filesystems are typically
  case-*insensitive* (or case-preserving but insensitive for lookup) —
  code that works by accident on one platform can silently break, or
  silently "work" for the wrong reason, on another.
- **Reserved names** — Windows reserves certain filenames (`CON`,
  `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`) regardless of
  extension — a filename that is perfectly valid on Linux/macOS can
  fail to be created on Windows if it collides with one of these.

### 24.3 Why `Path("data") / "file.txt"` is the right default

Constructed this way, `pathlib` automatically renders the correct
separator for whichever platform your code actually runs on — you
never hardcode `/` or `\` yourself, and the resulting `Path` object
behaves correctly regardless of platform.

### 24.4 What `pathlib` cannot magically solve

`pathlib` solves separator and composition problems — it does **not**
make case-sensitivity differences disappear (a path that works because
your Linux filesystem happens to be case-sensitive can still fail on a
case-insensitive one, or vice versa), does **not** make every filename
valid everywhere (the Windows reserved-name list still applies
regardless of how you constructed the path), and does **not** make an
absolute path from one operating system meaningful on another (a
Windows `C:\...` path is simply not something Linux can interpret at
all, `pathlib` or not).

## 25. Windows/Linux/WSL2

### 25.1 Windows-specific concepts

```python
from pathlib import PureWindowsPath

p = PureWindowsPath(r"C:\Users\User\data\file.txt")
print(p.drive)    # 'C:'
print(p.parts)      # ('C:\\', 'Users', 'User', 'data', 'file.txt')
```

Windows paths can begin with a **drive letter** (`C:`), or, for network
locations, a **UNC path** (`\\server\share\...`, which `pathlib`
represents with its own drive-like anchor). `WindowsPath` is the
concrete, filesystem-touching class you get automatically from
`Path(...)` when running on Windows; `PureWindowsPath` (shown above) is
useful for inspecting Windows-style paths from *any* platform, without
touching a real filesystem (§5.5).

### 25.2 Raw strings for literal Windows paths

```python
windows_style_path = r"C:\Users\User\data"
```

A **raw string** (the `r` prefix) tells Python not to interpret
backslashes as escape-sequence introducers (so `\U` is not mistaken for
part of a Unicode escape, for example) — genuinely useful when a
literal Windows-style path string must be written out by hand.
**Emphasis, restated:** constructing paths with `Path(...)` and `/`
composition (§6) remains the generally preferable approach even on
Windows — raw strings matter mainly when you are handed, or must
literally reproduce, a pre-existing Windows-style string.

### 25.3 Linux filesystem paths

Linux has a single, unified directory tree rooted at `/` — there is no
drive-letter concept; every storage device, once mounted, appears as
some subdirectory within that one tree. A typical user's home directory
is `/home/<username>`.

### 25.4 WSL2 — how it actually works

You are running Ubuntu through **WSL2** (Windows Subsystem for Linux,
version 2) — a genuine Linux environment, running inside a lightweight
virtual machine, on top of Windows. Because of this, **your Python
program, running inside WSL2, sees a completely ordinary Linux
filesystem** — Linux-style paths (`/home/...`), Linux permission
semantics, Linux case-sensitivity — with no `pathlib`-visible
difference from running on a "real," standalone Linux machine.

### 25.5 `/mnt/c/...` — where your Windows files actually are

WSL2 makes your Windows drives available *inside* the Linux
environment, mounted under `/mnt/` — your Windows `C:\Users\You\Documents`
appears, from inside WSL2, as `/mnt/c/Users/You/Documents`. **A path
visible in Windows Explorer is not represented identically inside
WSL2** — `C:\Users\You\data\file.txt` (Windows-visible) corresponds to
`/mnt/c/Users/You/data/file.txt` (WSL2-visible) — an entirely different
string, requiring an entirely different `Path` construction, even
though both describe, physically, the same underlying file.

### 25.6 Performance considerations across the WSL2/Windows boundary

Reading or writing files that live on the Windows-mounted side
(anything under `/mnt/c/...` and similar) from inside WSL2 is
meaningfully slower than working with files that live natively inside
the Linux filesystem (anything under `/home/...`) — because every such
operation must cross the boundary between the Linux virtual machine and
the Windows host. For real data-processing or AI-engineering work
involving many files or large files, **prefer keeping your project and
its data inside the native Linux filesystem (`/home/...`) rather than
under `/mnt/c/...`**, when you have the choice.

### 25.7 Why portability still matters, even working only in WSL2 today

Code you write today may later run in a plain Docker container, on a
teammate's native Linux server, on a colleague's macOS laptop, or in a
cloud CI pipeline — none of which have any `/mnt/c/` concept at all,
and some of which (a fresh Linux server, for instance) will behave
identically to your WSL2 environment for `pathlib` purposes. Writing
portable, `pathlib`-based paths now (§24) is what makes that eventual
move require zero path-related code changes.

## 26. Permissions and Errors

### 26.1 The core permission concepts

- **Read permission** — can this file's content be read, or this
  directory's contents be listed?
- **Write permission** — can this file's content be changed, or can
  something be created/removed inside this directory?
- **Execute/search permission on a directory** — can you actually enter
  (or "traverse through") this directory at all? (For a directory
  specifically, "execute" permission means something closer to
  "search/enter," not "run as a program.")
- **Ownership** — every file/directory on a POSIX system belongs to a
  specific owning user and group, which affects which permission set
  (owner/group/other) applies to a given process.

This chapter does not attempt a full Linux-permissions course — only
enough to make the following behavior understandable.

### 26.2 `PermissionError` in practice

```python
Path("/root/secret.txt").read_text(encoding="utf-8")
```

```text
Traceback (most recent call last):
  ...
PermissionError: [Errno 13] Permission denied: '/root/secret.txt'
```

Raised whenever the operating system's real access controls genuinely
forbid the attempted operation — not a `pathlib`-specific concept, but
the exact same `PermissionError` already introduced for plain `open()`
in
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§18.1.

### 26.3 Platform differences in permission semantics

POSIX systems (Linux/macOS) use the classic owner/group/other
read/write/execute model. Windows uses a meaningfully different,
richer access-control model (ACLs) under the hood — `pathlib` exposes a
simplified, cross-platform-ish view through `.stat().st_mode`, but the
*exact* meaning and granularity of "permission" genuinely differs by
platform; do not assume permission-checking code written and tested
purely on Linux will behave identically, byte-for-byte, on Windows.

## 27. Validation

### 27.1 The six-step boundary discipline

Directly extending
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§3 "validate at the boundary" principle, specifically for paths:

1. **Receive input** — a string, from a CLI argument, environment
   variable, config file, or direct user entry.
2. **Convert to `Path`** — `Path(raw_input)`, immediately, so every
   following step gets `pathlib`'s full toolset.
3. **Normalize/resolve when appropriate** — `.resolve()` (§10), so
   later comparisons and checks operate on a single, unambiguous,
   symlink-followed form.
4. **Validate expected location/type** — does it exist? Is it the right
   kind of thing (file vs. directory)? Is it inside an allowed area
   (§26)?
5. **Perform the operation** — the actual read, write, or filesystem
   action your program needed to do in the first place.
6. **Handle failure explicitly** — a specific, anticipated exception
   (§29's principle), not a silent catch-all.

### 27.2 A reusable validation function

```python
from pathlib import Path


def validate_input_file(path: Path) -> Path:
    resolved = path.resolve()

    if not resolved.exists():
        raise FileNotFoundError(f"No such file: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"Expected a file, got something else: {resolved}")

    return resolved
```

**Why this belongs near the boundary:** once `validate_input_file` has
returned successfully, every piece of code *downstream* of it can
safely assume "this really is an existing, real file" — exactly the
"transform into a reliable internal representation" idea from the
previous chapter's §3, now applied specifically to paths rather than
file content.

## 28. Path Traversal Security

### 28.1 The `../` problem

```python
user_input = "../../etc/passwd"
```

If a program blindly does `(uploads_directory / user_input)` and then
performs a read or write, a maliciously (or even just carelessly)
crafted `user_input` containing `..` components can walk the resulting
path entirely **outside** the directory the program intended to
restrict access to — this class of vulnerability is called **path
traversal** (or **directory traversal**).

### 28.2 A safe pattern

```python
from pathlib import Path


def safe_path_within(base_dir: Path, user_supplied: str) -> Path:
    base_dir = base_dir.resolve()
    candidate = (base_dir / user_supplied).resolve()

    if not candidate.is_relative_to(base_dir):
        raise ValueError(f"Path traversal attempt detected: {user_supplied!r}")

    return candidate
```

```python
uploads_dir = Path("/app/uploads")
safe_path_within(uploads_dir, "report.csv")          # fine
safe_path_within(uploads_dir, "../../etc/passwd")      # raises ValueError
```

### 28.3 Why resolving *before* checking matters

**The check must happen on the fully `.resolve()`d candidate, not on
the raw, unresolved joined path.** `(base_dir / "../../etc/passwd")`,
left unresolved, would not *textually* look like it escapes
`base_dir` in every naive string-based check — only after `.resolve()`
actually walks the `..` components (and follows any symlinks along the
way, §18) does the *true* final destination become visible for
comparison. `.is_relative_to()` (§10.5; Python 3.9+) then gives a
direct, reliable yes/no answer.

### 28.4 Symlink attacks, briefly

Even a `candidate` that resolves to a location genuinely inside
`base_dir` textually can, in principle, be — or pass through — a
symlink whose *target* leads somewhere else entirely; `.resolve()`
already accounts for this by following symlinks to their real
destination before the containment check runs (§28.2's pattern is
correct specifically because it resolves first). Genuinely
security-critical systems (accepting paths from untrusted, potentially
adversarial users) often need additional hardening beyond this
chapter's introductory scope — the principle taught here (resolve,
then verify containment, never trust the raw string) is the correct
foundation to build on.

### 28.5 Where this matters

Safe extraction of uploaded archive contents, restricting a file-serving
tool to one designated directory, restricting a download tool from
writing outside its intended output folder, and validating any
configuration- or environment-provided path that ultimately comes,
even indirectly, from something outside your own program's control.

## 29. TOCTOU and Race Conditions

### 29.1 The concept: time-of-check to time-of-use

```python
# RISKY pattern
if path.exists():
    content = path.read_text(encoding="utf-8")
```

**TOCTOU** ("time-of-check to time-of-use") names the gap between
*checking* a condition and *acting* on it — however small that gap is
in wall-clock time, the filesystem can genuinely change in between.
Between the `if path.exists():` check succeeding and the
`path.read_text(...)` call actually running, another process (or even
another part of your own program) could delete the file, replace it,
or change its permissions — the check's result is already stale by the
time the action runs.

### 29.2 The engineering principle: prefer attempting and handling, over pre-checking

```python
# PREFERRED -- attempt the real operation directly, and handle the specific failure
try:
    content = path.read_text(encoding="utf-8")
except FileNotFoundError:
    content = ""
```

This is not merely "shorter code" — it is **structurally immune** to
the TOCTOU gap, because there is no separate check-then-act window at
all: the single operation either succeeds or raises, atomically, as far
as your program's own logic is concerned. This directly reuses
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§18.3/§28's "catch the specific, anticipated exception" principle — here
applied specifically as a defense against a real class of filesystem
race condition, not merely a style preference.

### 29.3 Where a pre-check is still reasonable

A pre-check like `.exists()` remains genuinely useful for **early,
user-facing feedback** ("that file doesn't look right — did you mean
...?") *before* attempting a potentially expensive or consequential
operation — as long as the code that actually performs the real
operation afterward **still** handles the relevant exception properly,
rather than assuming the earlier check makes the later operation safe.

## 30. Safe and Atomic Operations

### 30.1 The core production pattern: write elsewhere, then replace

```python
from pathlib import Path
import os


def write_safely(target: Path, content: str) -> None:
    temporary_file = target.with_name(target.name + ".tmp")
    temporary_file.write_text(content, encoding="utf-8")
    temporary_file.replace(target)
```

The idea: write the *entire* new content to a separate, temporary
location first; only once that write has fully succeeded, use
`.replace()` (§17.2) to swap it into the real target location in one
step.

### 30.2 Why this can be safer than overwriting directly

If writing the temporary file fails partway through (a crash, a
full disk, an interrupted process), the **original target file is
completely untouched** — only the incomplete temporary file is
affected, and it can simply be discarded. Compare this against writing
directly to `target` with `"w"` mode
([01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§9.4/§29.2): a failure partway through leaves the *real* file
truncated and corrupted, with no original version left to recover.

### 30.3 An honest limitation: do not overstate the guarantee

`.replace()` is typically atomic **at the filesystem level**, on the
same filesystem/volume (§17.3) — but "the rename step itself is atomic"
is not the same claim as "the data is now permanently, physically safe
against every possible hardware failure." As
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§33.3 already noted for `flush()`, true durability guarantees against
power loss involve lower-level operations (`os.fsync()`) outside this
chapter's scope. What this pattern *does* reliably guarantee: **your
target file is never left in a half-written, corrupted intermediate
state as a direct result of your own write logic failing partway
through** — a meaningfully strong, genuinely useful guarantee on its
own, even without claiming more than that.

## 31. Performance

### 31.1 Lazy iteration

`.iterdir()`, `.glob()`, and `.rglob()` are all **lazy** — they are
generators, producing one result at a time as you iterate, rather than
building a complete list up front. `for entry in path.iterdir():`
never holds more than one entry's worth of overhead at a time;
`list(path.iterdir())`, by contrast, forces every entry to be
collected into memory at once before continuing — a choice worth
making deliberately, not automatically, exactly mirroring
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§8 lesson about `for line in f:` versus `readlines()`, applied here to
directories instead of files.

### 31.2 Recursive traversal cost

`.rglob()`'s cost scales directly with the total number of files and
directories visited across the *entire* tree beneath the starting
point — a directory tree with a million files means a million
individual filesystem lookups, regardless of how few of them actually
match your pattern. For very large trees, consider whether a narrower
`.glob()` at a known, shallower level can avoid visiting parts of the
tree you already know are irrelevant.

### 31.3 Metadata calls and repeated filesystem access

```python
# WASTEFUL -- calls stat() (indirectly, via is_file()) twice for the same path
for entry in Path("data").iterdir():
    if entry.is_file():
        size = entry.stat().st_size
```

```python
# BETTER -- captures the stat() result once, reuses it
for entry in Path("data").iterdir():
    info = entry.stat()
    if not (info.st_mode & 0o170000 == 0o100000):   # illustrative only -- prefer entry.is_file() in real code
        continue
    size = info.st_size
```

Each call to `.exists()`, `.is_file()`, `.is_dir()`, or `.stat()` is,
in general, its own separate round trip to the operating system —
exactly the kind of I/O cost
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§4.7 already established as meaningfully slower than in-memory work.
For code inspecting many files, minimizing *redundant* metadata calls
on the same path is a genuine, worthwhile optimization — though, as
with all optimization, only after a real, measured cost justifies the
extra complexity.

### 31.4 Network filesystems

Paths that resolve onto a network-mounted filesystem (a shared drive, a
cloud-synced folder, or, relevantly, files accessed across the WSL2/
Windows boundary, §25.6) carry meaningfully higher per-operation
latency than a purely local disk — every `.exists()`, `.stat()`, or
`.iterdir()` call pays that network round trip. Code performing many
small filesystem operations against such a location will be
measurably slower than the exact same code against a local path.

## 32. Application Architecture

### 32.1 Bad design: everything tangled together

```python
# BAD -- path construction, validation, I/O, logic, and output all mixed together
def process_file(filename):
    path = Path.cwd() / filename
    if not path.exists():
        print(f"Missing: {filename}")
        return
    content = path.read_text(encoding="utf-8")
    result = content.upper()
    output_path = Path.cwd() / (filename + ".out")
    output_path.write_text(result, encoding="utf-8")
    print("Done")
```

This single function decides *where* the file lives (tied to `cwd`,
§8.3's exact fragility), validates it, reads it, transforms it, writes
it, and reports to the user — six responsibilities, none of which can
be tested or reused independently of the rest.

### 32.2 A better separation of concerns

```python
from pathlib import Path
from typing import Iterable


# -- Path/configuration layer --------------------------------------
def build_output_path(input_path: Path) -> Path:
    return input_path.with_suffix(input_path.suffix + ".out")


# -- Filesystem adapter ---------------------------------------------
def read_input(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_output(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


# -- Domain logic (pure, no filesystem involved) ---------------------
def transform(content: str) -> str:
    return content.upper()


# -- Orchestration / CLI layer ---------------------------------------
def process_file(input_path: Path) -> Path:
    output_path = build_output_path(input_path)
    content = read_input(input_path)
    result = transform(content)
    write_output(output_path, result)
    return output_path
```

### 32.3 Why this matters

- **Testing** — `transform()` and `build_output_path()` can be tested
  with plain strings/`Path` objects and no real filesystem at all
  (§31's testing chapter equivalent, §38, relies on exactly this).
- **Maintainability** — changing *where* output files go touches only
  `build_output_path`; changing the transformation touches only
  `transform`.
- **Portability** — no function here assumes anything about `cwd`
  (§8.3) or a specific operating system.
- **Debugging** — a wrong result narrows immediately to one of four
  small, individually-reasoned-about functions.
- **Production systems** — this is the same layered shape
  [01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
  §27 already established for file *content* processing, now extended
  to include an explicit path-construction layer as well.

### 32.4 Reusable path functions

```python
def find_config_file(config_dir: Path) -> Path:
    candidate = config_dir / "config.json"
    if not candidate.is_file():
        raise FileNotFoundError(f"No config.json found in {config_dir}")
    return candidate
```

A well-designed path-handling function has a clear parameter list
(usually one or more `Path` objects, §32.5), a clear, predictable
return value or exception, and — critically — **never secretly depends
on the current working directory** (§8.3) unless that dependency is the
function's entire, explicit purpose. Prefer functions that *receive* a
base directory as a parameter over functions that silently reach for
`Path.cwd()` internally.

### 32.5 Type hinting with paths

```python
from pathlib import Path


def load_data(path: Path) -> str:
    return path.read_text(encoding="utf-8")
```

`path: Path` documents the API contract precisely: this function
expects an already-constructed `Path`, not a raw string, and callers
should treat that as the expected interface. Occasionally, a function
is deliberately written to accept either:

```python
def load_data(path: Path | str) -> str:
    return Path(path).read_text(encoding="utf-8")
```

`Path | str` communicates "callers may pass either; this function
normalizes internally" — a legitimate, deliberate choice for a
public-facing convenience function, but not a default to reach for
everywhere; internal, application-specific functions are generally
clearer accepting `Path` alone and trusting their callers to have
already converted (§23.3's habit).

## 33. Testing

### 33.1 Why `tmp_path`, not your real filesystem

Exactly as
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§39 established for file content, tests exercising `pathlib` code
should never read or write inside your actual project directory —
`pytest`'s built-in `tmp_path` fixture hands each test function a
fresh, isolated, automatically-cleaned-up temporary directory, as a
`Path` object, ready to use directly.

### 33.2 Testing existence and type

```python
def test_creates_file(tmp_path):
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")

    assert path.exists()
    assert path.is_file()


def test_missing_file_is_detected(tmp_path):
    path = tmp_path / "does_not_exist.txt"

    assert not path.exists()
```

### 33.3 Testing directory creation, including nested

```python
def test_mkdir_creates_nested_directories(tmp_path):
    nested = tmp_path / "raw" / "2024" / "january"
    nested.mkdir(parents=True)

    assert nested.is_dir()
```

### 33.4 Testing path construction and renaming

```python
def test_with_suffix_builds_expected_path(tmp_path):
    original = tmp_path / "report.csv"
    expected = tmp_path / "report.json"

    assert original.with_suffix(".json") == expected


def test_rename_moves_file(tmp_path):
    source = tmp_path / "old.txt"
    source.write_text("data", encoding="utf-8")
    destination = tmp_path / "new.txt"

    source.rename(destination)

    assert not source.exists()
    assert destination.read_text(encoding="utf-8") == "data"
```

### 33.5 Testing invalid input and path-traversal validation

```python
import pytest


def test_validate_input_file_raises_for_missing_file(tmp_path):
    missing = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        validate_input_file(missing)


def test_safe_path_within_rejects_traversal(tmp_path):
    base_dir = tmp_path / "uploads"
    base_dir.mkdir()

    with pytest.raises(ValueError):
        safe_path_within(base_dir, "../outside.txt")
```

### 33.6 A note on permission-related tests

Genuinely testing `PermissionError` behavior portably is difficult —
permission semantics differ meaningfully by platform (§26.3), and
CI/test environments often run as a user with unusually broad
permissions. In practice, most projects test the *code path* that
handles `PermissionError` using a small helper that simulates the
exception being raised, rather than attempting to create genuinely
unreadable files on disk within an automated test.

## 34. Debugging

### 34.1 A systematic thirteen-step workflow

1. **Print/inspect the `Path`** — confirm it holds the value you
   actually expect.
2. **Inspect `repr(path)`** — reveals the exact class (`PosixPath` vs.
   `WindowsPath`, §5.5) and exact stored text, catching subtle
   surprises `print()` alone can hide.
3. **Inspect `Path.cwd()`** — confirm the current working directory
   matches your assumption (§8.3).
4. **Inspect `path.absolute()`** — see the syntactic, non-filesystem-
   touching absolute form.
5. **Inspect `path.resolve()`** — see the fully normalized,
   symlink-followed form (§10.2).
6. **Check `.exists()`.**
7. **Check `.is_file()`.**
8. **Check `.is_dir()`.**
9. **Inspect parent directories** — does `path.parent` exist? Does
   *its* parent?
10. **Inspect permissions** — can this location genuinely be read or
    written, independent of Python (§26)?
11. **Inspect the platform** — `import platform; platform.system()` —
    confirm you are reasoning about the correct OS's path semantics.
12. **Inspect symlinks** — is any component along the way secretly a
    symlink (§18), possibly pointing somewhere unexpected?
13. **Reproduce with the smallest possible example** — a fresh, tiny
    `tmp_path`-style directory with one or two known files, confirming
    your logic in isolation before trusting it against real data.

### 34.2 Common bugs and their signature

| Symptom | Likely cause |
|---|---|
| `FileNotFoundError` for a path that "should" exist | Wrong working directory (§8.3) |
| `FileNotFoundError` on `.mkdir()` for a nested path | Missing `parents=True` (§13.2) |
| A file appears at the wrong location entirely | Typo in the filename, or an accidental absolute-path override during `/` composition (§6.5) |
| Extension-based logic silently fails on one file | `.suffix` capitalization mismatch (`.CSV` vs `.csv`) or a multi-suffix file (`.suffix` vs `.suffixes`, §7.1) |
| Code works on Linux, fails on Windows (or vice versa) | Hardcoded separator, drive assumption, or case-sensitivity assumption (§24) |
| A path that looks right in Windows Explorer can't be found | WSL2 path-translation confusion — `C:\...` vs. `/mnt/c/...` (§25.5) |
| `.exists()` is `True` for a link you thought was broken, or vice versa | Confusing a symlink's own existence with its target's existence (§18.4) |
| `PermissionError` on an operation that "should" be allowed | Real OS-level permission restriction — verify outside Python first (§26.2) |
| A relative path resolves somewhere unexpected | `Path.cwd()` differs from what you assumed — verify explicitly (step 3, §8.4) |

## 35. Common Mistakes

**1. Hard-coding absolute paths.**
```python
# BAD
config_path = Path("/home/alice/project/config.json")
```
→ Only works for one specific user, on one specific machine. **Better:**
build from `Path(__file__).resolve().parent` (§9) or an environment
variable/config value.

**2. Manually concatenating path strings.**
```python
# BAD
file_path = "data/" + filename
```
→ **Better:** `Path("data") / filename` (§5.1, §6.4).

**3. Using `/` incorrectly inside plain strings.**
```python
# BAD -- forgot the trailing separator, or hardcoded the wrong one
file_path = "data" + filename   # "datacustomers.csv"
```
→ **Better:** `Path("data") / filename` — impossible to make this
specific mistake, since `pathlib` inserts the separator itself.

**4. Assuming the current working directory.**
Directly §8.3's worked example. **Better:** anchor to
`Path(__file__).resolve().parent` (§9) when the intent is
project-relative, not cwd-relative.

**5. Confusing a file name with a full path.**
```python
# BAD -- "customers.csv" alone, when a specific directory was intended
Path("customers.csv").read_text(encoding="utf-8")
```
→ Silently reads/writes wherever the cwd happens to be, not the
intended `data/` directory. **Better:** always build the full,
intended path explicitly: `Path("data") / "customers.csv"`.

**6. Confusing a `Path` object with a file's contents.**
```python
# BAD
path = Path("notes.txt")
print(path)          # prints the PATH, "notes.txt" -- not the file's content!
```
→ **Better:** `print(path.read_text(encoding="utf-8"))` — a `Path` is a
location (§4.3), never the data stored there.

**7. Forgetting `parents=True` on `.mkdir()`.**
Directly §13.1's worked `FileNotFoundError` example.

**8. Using `.rmdir()` on a non-empty directory.**
Directly §17.4's worked `OSError` example. **Better:** use
`shutil.rmtree()` (§19) when recursive deletion is genuinely intended
— and confirm that intent very deliberately, since it is irreversible.

**9. Assuming `.with_suffix()` renames a file.**
Directly §20.4's worked example — it returns a new `Path` *value*; it
never touches the filesystem.

**10. Assuming `.resolve()` changes the filesystem.**
`.resolve()` only computes a normalized path string — it does not
create, move, or otherwise affect anything on disk, exactly like
`.with_suffix()` (mistake 9) is a pure computation, not an action.

**11. Assuming `.exists()` guarantees the next operation will succeed.**
Directly §29.1's TOCTOU example. **Better:** attempt the operation and
handle the specific exception (§29.2).

**12. Ignoring permissions.**
Writing code that assumes every read/write will succeed, with no
`PermissionError` handling anywhere (§26.2, §29's specific exceptions
list).

**13. Blindly catching all exceptions.**
```python
# BAD
try:
    path.unlink()
except Exception:
    pass
```
→ Hides `PermissionError`, a genuine bug elsewhere, everything —
identically to
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§27.3. **Better:** catch the specific exception(s) you anticipated.

**14. Using `str` everywhere instead of `Path`.**
Directly §23.3's worked example — discards `pathlib`'s benefits at
every conversion boundary.

**15. Relying on platform-specific path syntax.**
Directly §24.1's `"C:\\Users\\..."` example, or its POSIX mirror
(hardcoding `/home/...` in code meant to also run on Windows).

**16. Testing against real user directories.**
```python
# BAD -- a test that writes into the real project or home directory
def test_creates_file():
    path = Path("output.txt")
    path.write_text("test")
```
→ Pollutes real state, is not isolated, and can silently overwrite real
data. **Better:** use `tmp_path` (§33) for every filesystem-touching
test.

### 35.1 Wrong vs. correct, gathered as quick contrasts

```python
# WRONG
file_path = "data/" + filename

# RIGHT
file_path = Path("data") / filename
```

```python
# WRONG (not actually wrong -- just worth knowing the alternative)
if os.path.exists(some_path):
    ...

# ALSO RIGHT -- pathlib's equivalent
if Path(some_path).exists():
    ...
```

`os.path.exists()` is not incorrect — §34 discusses exactly when
`os.path` remains a perfectly appropriate, common choice. The two are
equivalent in outcome here; the difference is purely about which
overall style (function-on-a-string vs. method-on-an-object) the rest
of your code has committed to.

```python
# SOMETIMES WRONG -- when project-relative behavior was actually required
data_dir = Path.cwd() / "data"

# SOMETIMES RIGHT INSTEAD
project_root = Path(__file__).resolve().parent
data_dir = project_root / "data"
```

**Neither pattern is universally correct** — `Path.cwd()`-based paths
are exactly right for a tool whose entire purpose is "operate on
wherever the user currently is" (like a CLI utility meant to be run
from inside varying project folders); `Path(__file__)`-based paths are
exactly right when the intent is "find files that are part of my own
project, regardless of where the user launched me from" (§9.3–§9.4).
Correctness depends on which of those two intents your specific code
actually has.

## 36. pathlib vs. os.path vs. shutil

### 36.1 The mental model

```
pathlib  →  represents and manipulates paths; provides direct filesystem operations tied to a single path
os       →  general operating-system interfaces (including os.path, the older string-based path toolkit)
shutil   →  higher-level, multi-file/directory operations (copying trees, moving, recursive deletion)
```

### 36.2 `pathlib` vs. `os.path`

| | `os.path` | `pathlib` |
|---|---|---|
| Represents a path as | A plain `str` | A dedicated `Path` object |
| Joining | `os.path.join(a, b)` | `a / b` |
| Extension | `os.path.splitext(p)` | `p.suffix` / `p.stem` |
| Existence check | `os.path.exists(p)` | `p.exists()` |
| Style | Free functions taking strings | Methods/properties on an object |

`os.path` is **not obsolete** — it remains fully valid, widely used, and
you will encounter it constantly in existing codebases, standard-library
internals, and some third-party libraries that predate `pathlib`'s
widespread adoption. **Modern Python application code commonly favors
`pathlib` for new code**, specifically because of the composition and
readability advantages this entire chapter has demonstrated — but
knowing `os.path` remains genuinely useful for reading and maintaining
existing code, and the two interoperate freely (a `Path` can always be
converted to a string for an `os.path` function via `str()`, and vice
versa via `Path(os_path_string)`).

### 36.3 `pathlib` vs. `shutil`

Already covered in full in §19: `pathlib` represents and manipulates
*individual* paths, including simple single-path filesystem operations
(§13–§14, §17–§18); `shutil` handles operations that inherently involve
*more* than a single path's worth of work — copying an entire file's
bytes, copying an entire directory tree, or recursively deleting one.
They are designed to work *together*, not as competing alternatives —
`shutil` functions accept `Path` objects directly (§22.3), and real code
routinely uses both side by side, exactly as §19.2 demonstrated.

## 37. Advanced API Reference

A compact reference to every `pathlib` API this chapter has covered.
No invented APIs — every entry below is a genuine, documented `pathlib`
member.

### 37.1 Constructors / classes

| API | Category | What it does | Example | Caveat |
|---|---|---|---|---|
| `Path(...)` | Constructor | Builds a path, auto-selecting `PosixPath`/`WindowsPath` for the current platform | `Path("data", "file.txt")` | The practical default for nearly all application code |
| `PurePath(...)` | Constructor | Pure, non-I/O path representation | Rare — mostly a shared base | No filesystem access at all |
| `PurePosixPath(...)` | Constructor | POSIX-style path, no I/O | `PurePosixPath("/etc/hosts")` | Useful for cross-platform path *analysis* only |
| `PureWindowsPath(...)` | Constructor | Windows-style path, no I/O | `PureWindowsPath(r"C:\data")` | Useful for cross-platform path *analysis* only |
| `PosixPath` / `WindowsPath` | Concrete classes | What `Path(...)` becomes automatically | — | Rarely instantiated by name directly |

### 37.2 Path properties (no filesystem access)

| API | What it does | Example |
|---|---|---|
| `.name` | Final component | `Path("a/b.txt").name` → `'b.txt'` |
| `.stem` | Name without last suffix | `'b'` |
| `.suffix` | Last extension | `'.txt'` |
| `.suffixes` | All extensions, as a list | `['.tar', '.gz']` for `archive.tar.gz` |
| `.parent` | Immediate containing directory | `Path("a/b.txt").parent` → `PosixPath('a')` |
| `.parents` | Sequence of all ancestor directories | `p.parents[0]`, iterable |
| `.parts` | Tuple of every component | `('a', 'b.txt')` |
| `.anchor` | Drive + root combined | `'/'` on POSIX |
| `.root` | Root marker alone | `'/'` on POSIX |
| `.drive` | Drive/UNC share (Windows only) | `''` on POSIX |

### 37.3 Path inspection (touches the filesystem)

| API | What it does | Caveat |
|---|---|---|
| `.exists()` | Does anything exist here? | Follows symlinks |
| `.is_file()` | Is it a regular file? | Follows symlinks |
| `.is_dir()` | Is it a directory? | Follows symlinks |
| `.is_symlink()` | Is the path itself a symlink? | Does **not** follow the link |
| `.is_mount()` | Is it a mount point? | Windows support added in 3.12 |
| `.is_block_device()` / `.is_char_device()` / `.is_fifo()` / `.is_socket()` | Specialized POSIX filesystem object checks | Rarely needed in application code |
| `.stat()` | Full metadata (size, timestamps, mode) | Follows symlinks |
| `.lstat()` | Metadata of the link itself | Does **not** follow symlinks |

### 37.4 Path resolution

| API | What it does | Caveat |
|---|---|---|
| `.absolute()` | Prepends cwd — purely syntactic | Does not resolve `..` or symlinks |
| `.resolve(strict=False)` | Fully normalizes, follows symlinks, touches the filesystem | `strict=True` raises if not real |
| `.expanduser()` | Expands a leading `~` | `~` is never auto-expanded otherwise |
| `.relative_to(other)` | Computes a relative path | Raises `ValueError` if not a subpath (unless `walk_up=True`, 3.12+) |
| `.is_relative_to(other)` | Yes/no version of the above | Added in Python 3.9 |
| `Path.cwd()` | Current working directory, absolute | Depends entirely on how the process was launched |
| `Path.home()` | Current user's home directory | Cross-platform |

### 37.5 Directory traversal

| API | What it does | Caveat |
|---|---|---|
| `.iterdir()` | Direct children only | Order is not guaranteed |
| `.glob(pattern)` | Pattern-matched children | `**` needs explicit use for recursion |
| `.rglob(pattern)` | Recursive pattern match | Equivalent to `glob("**/" + pattern)` |

### 37.6 Directory creation

| API | What it does | Caveat |
|---|---|---|
| `.mkdir(mode=0o777, parents=False, exist_ok=False)` | Creates a directory | `parents=True` for missing intermediates; `exist_ok=True` to allow "already there" |

### 37.7 File operations

| API | What it does | Caveat |
|---|---|---|
| `.touch(mode=0o666, exist_ok=True)` | Creates an empty file, or updates its timestamp | Not a "create-only-if-missing" guarantee unless `exist_ok=False` |
| `.read_text(encoding=None, errors=None)` | Reads full text content | Convenience wrapper around `.open()` |
| `.write_text(data, encoding=None, errors=None, newline=None)` | Writes full text content | `newline=` added in Python 3.10 |
| `.read_bytes()` / `.write_bytes(data)` | Binary equivalents | Outside this chapter's text-focused scope |
| `.open(mode='r', ...)` | Returns an ordinary file object | Identical parameters to the built-in `open()` |

### 37.8 Renaming/replacement/deletion

| API | What it does | Caveat |
|---|---|---|
| `.rename(target)` | Renames/moves | Overwrite behavior differs by platform |
| `.replace(target)` | Renames/moves, always overwrites | Preferred for portable overwrite behavior |
| `.unlink(missing_ok=False)` | Deletes a file | `missing_ok=True` added in Python 3.8 |
| `.rmdir()` | Deletes an **empty** directory only | Raises `OSError` if not empty |

### 37.9 Symlinks

| API | What it does | Caveat |
|---|---|---|
| `.symlink_to(target)` | Creates a symlink | Argument order: `link.symlink_to(target)` |
| `.readlink()` | Reads the raw symlink target | Added in Python 3.9 |
| `.hardlink_to(target)` | Creates a hard link (distinct from a symlink) | Added in Python 3.10; not covered in depth in this chapter |

### 37.10 Matching

| API | What it does | Caveat |
|---|---|---|
| `.match(pattern)` | Tests one path against a glob pattern | `**` recursive support only from Python 3.13 |

### 37.11 Path transformations (no filesystem access)

| API | What it does | Caveat |
|---|---|---|
| `.with_name(name)` | New path, final component replaced | Returns a new `Path`; changes nothing on disk |
| `.with_stem(stem)` | New path, stem replaced | Added in Python 3.9 |
| `.with_suffix(suffix)` | New path, suffix replaced | Include the leading dot: `".json"` |
| `.with_segments(...)` | Low-level path rebuild, mainly for subclassing | Added in Python 3.12; rarely used directly |

### 37.12 Pure-path-only operations

Every property in §37.2, plus `.match()`, `.relative_to()`,
`.is_relative_to()`, and the `.with_*()` methods, are available on
`PurePath`/`PurePosixPath`/`PureWindowsPath` as well — none of them
touch the filesystem, which is exactly why they work identically
whether or not the path they describe actually exists, or even belongs
to the operating system currently running the code.

### 37.13 Interoperability

| API | What it does | Caveat |
|---|---|---|
| `os.PathLike` | Abstract interface `Path` implements | Lets standard-library functions accept `Path` directly |
| `os.fspath(path)` | Converts a `PathLike` to `str` | Rarely needed explicitly, since most APIs accept `Path` already |
| `str(path)` | Same practical effect as `os.fspath()` for this purpose | Prefer keeping values as `Path` internally (§23.3) |

## 38. Internal Mental Model

### 38.1 What actually happens for three lines of code

```python
path = Path("data/file.txt")
path.exists()
path.read_text(encoding="utf-8")
```

**Line 1, `Path("data/file.txt")`:** no filesystem access happens at
all. Python parses the given string(s) into path components (§7.1) and
constructs a `PosixPath`/`WindowsPath` object (§5.5) purely in memory —
this succeeds identically whether or not `data/file.txt` exists
anywhere.

**Line 2, `path.exists()`:** *now* Python's `pathlib` layer asks the
operating system, via a system call, whether something currently
exists at that location — this is the exact moment the "path
representation" (line 1) and the "real filesystem resource" (whatever
may or may not physically be there) actually make contact.

**Line 3, `path.read_text(encoding="utf-8")`:** another, separate
system-level request — open the file, read its bytes, decode them per
`encoding="utf-8"`
([01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§25), close the file — all bundled into this one convenience call
(§15.1).

### 38.2 The layered picture

```
Path object (in-memory representation only)
    ↓
    .exists() / .read_text() / .stat() / ... -- each one, its own request
    ↓
Python's I/O and pathlib layer
    ↓
operating-system / filesystem operation
```

### 38.3 The distinction, stated once more, directly

**A `Path` is not the file.** It is a value — comparable, hashable,
copyable, cheap to create, cheap to pass around — that merely
*describes a location*. Nothing about creating, storing, or even
printing a `Path` object ever touches disk. Only calling one of its
filesystem-facing methods (`.exists()`, `.read_text()`, `.mkdir()`,
`.unlink()`, and the rest of §37.3–§37.9) does. This is exactly why
§20.4 could say "`.with_suffix()` doesn't rename anything" and §10.1
could say "`.absolute()` doesn't touch the filesystem" — both are pure
computations on the *representation*, never actions on the *resource*.

## 39. Real-World AI Engineering Examples

**1. Loading a model configuration file.**
```python
config_path = Path(__file__).resolve().parent / "config" / "model.json"
config_text = config_path.read_text(encoding="utf-8")
```

**2. Finding a dataset directory.**
```python
dataset_dir = Path(__file__).resolve().parent / "datasets" / "train"
if not dataset_dir.is_dir():
    raise FileNotFoundError(f"Expected dataset directory at {dataset_dir}")
```

**3. Creating an output directory.**
```python
output_dir = Path("experiments") / "run_001"
output_dir.mkdir(parents=True, exist_ok=True)
```

**4. Processing a folder of CSV files.**
```python
for csv_path in sorted(Path("data/raw").glob("*.csv")):
    print(f"Processing {csv_path.name}")
```

**5. Finding JSON configuration files recursively.**
```python
config_files = sorted(Path("configs").rglob("*.json"))
```

**6. Building an experiment output directory.**
```python
from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
experiment_dir = Path("experiments") / f"run_{timestamp}"
experiment_dir.mkdir(parents=True)
```

**7. Saving logs/artifacts.**
```python
artifacts_dir = experiment_dir / "artifacts"
artifacts_dir.mkdir(exist_ok=True)
(artifacts_dir / "metrics.json").write_text(metrics_json, encoding="utf-8")
```

**8. Handling a user-provided input path.**
```python
user_path = Path(user_input).expanduser().resolve()
if not user_path.is_file():
    raise ValueError(f"Not a valid input file: {user_path}")
```

**9. A CLI tool built around filesystem paths.**
```python
def main(input_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(input_dir.glob("*.txt")):
        process_one(path, output_dir / path.name)
```
(Full command-line argument handling is
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
own subject — this shows only how `pathlib` fits into such a tool.)

**10. Building portable project paths.**
```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
```

**11. A temporary processing directory.**
```python
import tempfile

with tempfile.TemporaryDirectory() as tmp:
    work_dir = Path(tmp)
    intermediate = work_dir / "intermediate.jsonl"
    ...
```

**12. Dataset validation before use.**
```python
def validate_dataset_dir(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_dir():
        raise ValueError(f"Dataset directory not found: {resolved}")
    if not any(resolved.glob("*.csv")):
        raise ValueError(f"No CSV files found in dataset directory: {resolved}")
    return resolved
```

## 40. Mini-Projects

### Mini Project 1 — Filesystem Explorer

**Problem statement:** build a small tool that accepts a directory path
and reports what's inside it.

**Requirements:** accept a directory path; validate it (§27); list its
direct children; identify which are files vs. directories; show basic
metadata (size for files, §16) for each; handle errors gracefully
(missing path, path is actually a file, permission problems).

**Expected behavior:** running against a real directory prints a
readable listing; running against a missing or invalid path reports a
clear, specific error rather than a raw traceback.

**Suggested design:** a `validate_directory(path: Path) -> Path`
function (§27.2's pattern), a separate `describe_entry(entry: Path) ->
str` function, and a small orchestration function tying them together
— directly §32.2's layered shape.

**Constraints:** use `pathlib` exclusively for path work — no manual
string path-building.

**Edge cases:** an empty directory; a directory containing a broken
symlink (§18.4); a directory you lack permission to read (§26).

**Testing requirements:** use `tmp_path` (§33) to build a small,
known directory structure and assert on the reported output.

**Extension challenge:** sort entries deterministically (§12.4) and add
an option to show only files, or only directories.

### Mini Project 2 — Data Directory Inspector

**Problem statement:** given a dataset directory, report what data
files it contains, recursively.

**Requirements:** accept a dataset directory path; recursively find all
`.csv` and `.json` files (§12.3); report the count of each; report the
total combined file size (§16.1); identify any files that are exactly
zero bytes; produce deterministic, sorted output (§12.4).

**Expected behavior:** two runs against the same unchanged directory
produce byte-for-byte identical output.

**Suggested design:** separate "find matching files" (pure filesystem
traversal) from "summarize results" (pure computation on the list of
paths and sizes found) — §32's separation-of-concerns principle,
applied here directly.

**Constraints:** avoid redundant `.stat()` calls (§31.3) on the same
path.

**Edge cases:** a dataset directory with no matching files at all; a
very deeply nested subdirectory structure; a file with an uppercase
extension (`.CSV`) — decide, deliberately, whether that should count.

**Testing requirements:** build a small `tmp_path` tree with a known
mix of `.csv`, `.json`, and irrelevant files, including at least one
empty file, and assert the exact expected counts and total size.

**Extension challenge:** write the report itself to an output file
using `.write_text()` (§15.1), and add a `--recursive` vs. `--top-level-only`
style toggle conceptually (full argument parsing belongs to
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)).

### Mini Project 3 — Safe Project Artifact Manager

**Problem statement:** build a small utility that manages a project's
output artifacts safely, defending against path traversal and unsafe
overwrites.

**Requirements:** define a fixed project root and a set of standard
subdirectories (e.g. `outputs/`, `logs/`) created safely with
`.mkdir(parents=True, exist_ok=True)` (§13.2); accept an
artifact name from a caller and construct its full output path *within*
the allowed directory, validated against path traversal (§28.2); write
artifact content using the safe write-then-replace pattern (§30.1);
rename/replace existing outputs safely (§17.2); raise clear, specific
exceptions (not silent failures) for every anticipated failure mode;
include a `pytest` suite using `tmp_path` (§33) covering at least
successful writes, a rejected traversal attempt, and a safe overwrite.

**Expected behavior:** a well-formed artifact name is written correctly
inside the intended directory; a maliciously crafted name (containing
`..`) is rejected with a clear `ValueError`, and nothing is written
anywhere.

**Suggested design:** exactly §32's layered shape — a path/config
layer defining the project root and subdirectories, a validation layer
(§27.2 + §28.2 combined), a write layer (§30.1's safe pattern), and a
thin orchestration layer tying them together.

**Constraints:** every path-accepting function must have a clear type
hint (§32.5); no function should silently trust an unvalidated,
caller-supplied artifact name.

**Edge cases:** an artifact name that is just `".."`; an artifact name
containing a leading `/` (making it look absolute, §6.5); overwriting
an artifact that already exists; the target directory not yet existing
on first run.

**Testing requirements:** the full set from §33's examples, adapted —
successful write, traversal rejection, safe overwrite, and a missing
parent directory being created automatically.

**Extension challenge:** add a rolling limit (keep only the N most
recent artifacts, deleting older ones with `.unlink()`, §17.4) and
handle the case where deletion itself fails partway through.

## 41. Coding Exercises

### Level 1 — Foundation

1. Create a `Path` object representing `"reports/summary.txt"` and
   print its `.name`. *Expected behavior:* prints `summary.txt`.
2. Print the `.parent` of the path from exercise 1.
3. Print the `.suffix` and `.stem` of `Path("archive.tar.gz")`. *Edge
   case:* explain, in your own words, why `.suffix` alone is not
   `.tar.gz`.
4. Check whether a path you construct actually exists on disk, using
   `.exists()`.
5. Create a new, empty directory using `.mkdir()`. *Edge case:* what
   happens if you run your code twice in a row, unmodified?
6. Create a new, empty file using `.touch()` inside the directory from
   exercise 5.

### Level 2 — Practical

7. Recursively find every `.py` file under a directory of your choosing,
   using `.rglob()`, and print them in sorted order.
8. Create a nested directory structure (at least three levels deep) in
   a single `.mkdir()` call. *Constraint:* it must work whether or not
   any of the intermediate directories already exist.
9. Rename a file, and confirm (by checking `.exists()` on both the old
   and new paths) that the rename actually happened.
10. Write a function `validate_input_path(path: Path) -> Path` that
    raises a clear exception if the path does not exist, and a
    different clear exception if it exists but is not a file. *Edge
    case:* a path that points at a directory.
11. Write a function that computes the total size, in bytes, of every
    file directly inside a given directory (not recursively). *Edge
    case:* an empty directory.

### Level 3 — Engineering

12. Build a reusable path-validation function combining existence,
    type, and (optionally) extension checks, with clear, specific
    exceptions for each failure mode (§27.2's pattern, extended).
13. Build a small `project_paths.py`-style set of constants
    (`PROJECT_ROOT`, `DATA_DIR`, `OUTPUT_DIR`) using
    `Path(__file__).resolve()` (§9.1), and write one test confirming
    each resolves to the expected location relative to your test file.
14. Write `pytest` tests, using `tmp_path`, for at least three
    functions you built in Level 2.
15. Implement a "safe output path" function: given a base output
    directory and a desired filename, return the full path only if it
    would land inside that directory, otherwise raise `ValueError`
    (§28.2).
16. Implement path-traversal protection as a standalone, reusable
    function (distinct from exercise 15, if you built that one
    inline), and write at least three tests: an allowed path, a `..`-based
    traversal attempt, and an absolute-path-injection attempt (§6.5).

### Level 4 — Advanced

17. Write a function that checks whether a given path is a symlink,
    and if so, reports both its own existence and its target's
    existence separately (§18.4). *Edge case:* a broken symlink.
18. Write a function demonstrating the TOCTOU-safe pattern (§29.2) for
    reading an optional config file, with a test that specifically
    confirms the *exception-handling* path, not just the successful
    path.
19. Write a function that lists files in a directory in a fully
    deterministic order, regardless of the underlying filesystem's
    natural ordering (§12.4), and prove it with a test.
20. Implement the safe write-then-replace pattern (§30.1) as a
    reusable function, and write a test confirming that if the write
    step is simulated to fail, the original target file (if any) is
    left completely untouched.
21. Design a small, portable filesystem utility module bringing
    together several functions from this chapter (validation, safe
    output paths, directory creation, metadata inspection), each with
    type hints, each independently tested with `tmp_path`.

## 42. Debugging Exercises

Each snippet below is broken. Diagnose it using §34's workflow before
reading the corrected version.

**1. Wrong cwd.**
```python
# Run from anywhere other than the project's root directory:
data = Path("data/customers.csv").read_text(encoding="utf-8")
```
*Diagnose:* what does §34 step 3 (`Path.cwd()`) reveal here? *Corrected:*
anchor with `Path(__file__).resolve().parent` (§9) instead of a bare
relative path.

**2. Incorrect path concatenation.**
```python
folder = "data"
filename = "report.csv"
path = Path(folder + filename)
```
*Diagnose:* what does `print(repr(path))` (§34 step 2) reveal is
actually inside the resulting `Path`? *Corrected:*
`Path(folder) / filename`.

**3. Missing parent directory.**
```python
Path("output/2024/results.json").write_text("{}", encoding="utf-8")
```
*Diagnose:* which exception is raised, and why (§13.1)? *Corrected:*
`Path("output/2024").mkdir(parents=True, exist_ok=True)` before
writing.

**4. Wrong file/directory assumption.**
```python
config = Path("config").read_text(encoding="utf-8")   # "config" is actually a directory!
```
*Diagnose:* which exception, and what does `.is_dir()` (§34 steps 7–8)
reveal? *Corrected:* check `.is_file()` before reading, or fix the
intended path to `Path("config") / "settings.json"`.

**5. A platform-specific path.**
```python
path = Path("C:\\Users\\User\\data.txt")   # run on Linux/WSL2
```
*Diagnose:* what does `type(path)` and `path.exists()` reveal? *Corrected:*
build the path portably with `Path(...) / ...` composition instead of a
hardcoded Windows-style string (§24).

**6. A symlink issue.**
```python
link = Path("latest")
link.symlink_to("release-1.0")
# release-1.0 is later deleted
content = link.read_text(encoding="utf-8")
```
*Diagnose:* what does `.is_symlink()` vs. `.exists()` (§18.4) reveal
about `link`? *Corrected:* check `.exists()` (which correctly reports
`False` for a broken link) before attempting to read, or handle
`FileNotFoundError` directly.

**7. A path-traversal bug.**
```python
def save_upload(base_dir: Path, filename: str, content: str) -> None:
    (base_dir / filename).write_text(content, encoding="utf-8")
```
*Diagnose:* what happens if `filename` is `"../../etc/cron.d/evil"`?
*Corrected:* apply §28.2's `safe_path_within`-style containment check
before writing.

**8. An incorrect `.resolve()` assumption.**
```python
path = Path("does/not/exist.txt")
resolved = path.resolve()
print(resolved.exists())   # assumed True because "it was resolved"
```
*Diagnose:* does `.resolve()` (§10.3, default `strict=False`) require
the path to exist? *Corrected:* `.resolve()` succeeding says nothing
about existence — check `.exists()` separately, or pass
`strict=True` if non-existence should itself raise immediately.

**9. Incorrect `.relative_to()` usage.**
```python
a = Path("/home/user/project")
b = Path("/home/user/other")
print(a.relative_to(b))
```
*Diagnose:* is `a` actually inside `b`? What exception results (§10.5)?
*Corrected:* use `.is_relative_to()` first to check safely, or (Python
3.12+) pass `walk_up=True` if an upward-walking relative path is
genuinely intended.

## 43. Interview Questions

Beginner:
1. What is `pathlib`, and why does it exist? (§5.1–§5.3)
2. Why use `Path` instead of plain strings for filesystem paths? (§23.1)
3. What is the difference between an absolute and a relative path?
   (§4.7)
4. What is the current working directory (cwd)? (§8.1)
5. What does `Path.cwd()` return? (§8.1)
6. What does `Path.home()` return, and why is hardcoding `/home/...`
   a bad idea instead? (§4.7, §10)

Intermediate:
7. What is the difference between `.resolve()` and `.absolute()`?
   (§10.1–§10.2)
8. What is the difference between `.relative_to()` and
   `.is_relative_to()`? (§10.5)
9. What does `Path("data") / "file.txt"` actually do, mechanically?
   (§5.4)
10. What is `os.PathLike`, and why does it matter? (§22.1)
11. How does `pathlib` support cross-platform portability, and what
    are its limits? (§24.3–§24.4)
12. What is the difference between `Path.glob()` and `Path.rglob()`?
    (§12.2–§12.3)
13. What does `Path.match()` do, and how is it different from
    `.glob()`? (§21.1–§21.2)
14. What is the difference between `.stat()` and `.lstat()`? (§16.3)
15. What is a symbolic link, and how can you tell if one is broken?
    (§18.1, §18.4)
16. What is the difference between `.rename()` and `.replace()`?
    (§17.1–§17.2)

Production-oriented:
17. How do you prevent path traversal in a Python program accepting
    user-supplied filenames? (§28.2–§28.3)
18. What is TOCTOU, and why should you generally prefer "attempt and
    handle" over "check then act"? (§29)
19. Why can `.exists()` alone be insufficient before performing a real
    operation? (§29.1)
20. Why use `tmp_path` in `pytest` for filesystem tests? (§33.1)
21. How does `pathlib` compare to `os.path`? (§36.2)
22. How does `pathlib` compare to `shutil`, and why do they coexist?
    (§36.3)

Scenario-based:
23. A teammate's script works perfectly for them, but fails with
    `FileNotFoundError` the moment you run it. What would you check
    first, and why? (§8.3, §34.1)
24. You need to build an output path from a filename a user typed into
    a web form. Walk through exactly what you would do before writing
    anything to disk. (§27.1, §28.2)
25. Your program runs correctly on your WSL2 environment but a
    colleague reports it can't find a file they insist exists, on
    their native Windows Python install. What's the most likely
    explanation? (§25.5)

## 44. Knowledge Check

**A. Conceptual**
1. In your own words, explain why a `Path` object is not the same
   thing as the file it describes.
2. Explain why relative paths are meaningless without knowing what
   they are relative to.

**B. Code-reading**
3. What does the following construct, exactly (as text)?
```python
Path("a") / "b" / "/c" / "d"
```

**C. Predict-the-output**
4. What does this print?
```python
p = Path("/home/user/report.tar.gz")
print(p.stem)
print(p.suffix)
print(p.suffixes)
```

**D. Debugging**
5. A call to `.mkdir()` raises `FileExistsError` even though the code
   uses `exist_ok=True`. List at least two possible explanations.

**E. API-selection**
6. You need every `.log` file anywhere under a directory tree, no
   matter how deeply nested. Which method should you reach for, and
   why?
7. You need to know whether one specific, already-known `Path` matches
   the pattern `*.csv`. Which method should you reach for, and why?

**F. Portability**
8. Why is `Path("data") / "file.txt"` preferable to
   `Path("data/file.txt")` when the components themselves might one day
   need to be built dynamically, piece by piece?
9. What is the difference between how a path visible in Windows
   Explorer is represented inside WSL2?

**G. Security**
10. Why is checking `str(candidate).startswith(str(base_dir))` a weaker
    defense against path traversal than `candidate.is_relative_to(base_dir)`
    after both have been `.resolve()`d?

**H. Production-design**
11. Describe, in your own words, why a function that internally calls
    `Path.cwd()` is harder to test reliably than one that receives its
    base directory as a parameter.

---

**Answer key**

1. A `Path` is a location descriptor — it can be created, compared, and
   manipulated entirely in memory with zero filesystem access; the file
   it describes may or may not currently exist, and nothing about the
   `Path` object itself changes based on that (§4.3, §38.3).
2. A relative path is only meaningful once paired with a starting
   point — typically the current working directory — which is not
   fixed and can differ between runs, machines, and launch methods
   (§4.7, §8.2).
3. `PosixPath('/c/d')` — because `/c` is itself absolute, everything
   before it in the composition (`"a"`, `"b"`) is discarded (§6.5).
4. `'report.tar'`, `'.gz'`, `['.tar', '.gz']` — `.stem` removes only the
   *last* suffix, and `.suffixes` lists every one (§7.1–§7.2).
5. Possible causes: a race condition where something recreated the
   directory with different permissions between check and creation
   attempt (§13.4); or the path already exists but as a *file*, not a
   directory — `exist_ok=True` tolerates an existing directory, not an
   existing file at that same path, which still raises `FileExistsError`.
6. `.rglob("*.log")` — it searches recursively at any depth, which
   `.iterdir()` and non-recursive `.glob()` do not (§12.3).
7. `.match("*.csv")` — it tests one already-known path against a
   pattern directly, without searching a directory (§21.1–§21.2).
8. Building components dynamically (e.g. from variables, in a loop, or
   conditionally) is naturally expressed as repeated `/` joins; a single
   pre-formatted string requires manual, error-prone string
   interpolation to achieve the same flexibility (§5.4, §6.3).
9. They are different strings describing the same physical file —
   `C:\Users\You\...` (Windows-visible) vs. `/mnt/c/Users/You/...`
   (WSL2-visible); neither can be used directly in the other's context
   without translation (§25.5).
10. A raw string-prefix check can be fooled by a path that merely
    *looks* like it starts with the right prefix textually (e.g. a
    sibling directory with a similar name, or an unresolved `..` that
    hasn't actually been walked yet) — `.is_relative_to()` on
    `.resolve()`d paths compares the *true, final, symlink-followed*
    locations, not surface text (§28.3).
11. A function depending on `Path.cwd()` behaves differently depending
    on how and from where the test itself is run, making its behavior
    non-deterministic across environments; a function receiving its
    base directory as a parameter can be pointed at a `tmp_path` in
    every test, deterministically, regardless of the test runner's own
    cwd (§8.4, §32.4, §33.1).

## 45. Production Checklist

**Path design**
- [ ] No unnecessary hard-coded absolute paths (§35 mistake 1).
- [ ] Paths are constructed portably, via `Path(...)` and `/`
      composition, not raw string concatenation (§6.4).
- [ ] Each path has a clear "owner" — one function/module responsible
      for deciding where it points, not scattered assumptions across
      the codebase (§32).

**Validation**
- [ ] External paths (CLI, config, environment, user input) are
      validated at the boundary (§27.1).
- [ ] Expected file vs. directory type is checked explicitly, not
      assumed (§27.2).
- [ ] Errors are handled with specific, anticipated exceptions, not a
      blanket catch-all (§29's principle, extending
      [01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
      §27.3–§28).

**Security**
- [ ] User-influenced paths are resolved and checked for containment
      before use (§28.2).
- [ ] Symlink risk is considered for any path derived from untrusted
      input (§18.6, §28.4).
- [ ] No path from an untrusted source is trusted without validation,
      regardless of how "clean" it looks as a string (§28.1).

**Portability**
- [ ] No hardcoded `/` or `\` separators anywhere (§24.3).
- [ ] Case-sensitivity and reserved-name differences across platforms
      have been considered where relevant (§24.2).
- [ ] WSL2/Windows path-translation confusion has been accounted for,
      if the code may run in both contexts (§25.5–§25.7).

**Reliability**
- [ ] Check-then-act patterns have been replaced with attempt-and-handle
      where a TOCTOU gap would matter (§29.2).
- [ ] Important writes use a safe write-then-replace pattern, not a
      direct in-place overwrite (§30.1).
- [ ] Exceptions from filesystem operations are handled explicitly, not
      silently ignored (§29, §35 mistake 13).

**Testing**
- [ ] Filesystem-touching tests use `tmp_path`, never the real project
      or home directory (§33.1, §35 mistake 16).
- [ ] Missing-path, wrong-type, and invalid-path cases are each
      explicitly tested (§33.5).
- [ ] Path-traversal validation itself has a dedicated test proving it
      actually rejects an attack attempt (§33.5).

**Maintainability**
- [ ] `Path` objects are used internally throughout, converting to
      `str` only at genuine external boundaries (§23.3).
- [ ] Functions accepting paths have clear type hints (§32.5).
- [ ] Filesystem/path logic is separated from business/domain logic
      (§32.1–§32.3).
- [ ] Reusable, focused path-handling functions exist instead of
      logic duplicated inline everywhere it's needed (§32.4).

## 46. Mastery Checklist

You should be able to confidently say:

- [ ] I understand what a filesystem path is, and how it differs from
      the file or directory it describes.
- [ ] I understand absolute and relative paths, and why a relative
      path's meaning depends on the current working directory.
- [ ] I understand the current working directory (cwd), and why code
      should not blindly assume it.
- [ ] I can construct `Path` objects using every common form
      (`Path()`, `Path("a", "b")`, `Path("a/b")`).
- [ ] I can combine paths safely using `/`, and I understand what
      happens when an absolute path appears mid-composition.
- [ ] I understand every core path component (`.name`, `.stem`,
      `.suffix`, `.suffixes`, `.parent`, `.parents`, `.parts`,
      `.anchor`, `.root`, `.drive`).
- [ ] I can navigate directories with `.iterdir()`, `.glob()`, and
      `.rglob()`, and I know their ordering is not guaranteed.
- [ ] I can create directories safely with `.mkdir(parents=True,
      exist_ok=True)`.
- [ ] I can inspect files and directories with `.exists()`,
      `.is_file()`, `.is_dir()`, `.is_symlink()`, and `.stat()`.
- [ ] I can read and write text through `pathlib`
      (`.read_text()`/`.write_text()`/`.open()`), and I know when each
      is the right choice.
- [ ] I understand file/directory metadata, including the platform
      difference in `st_ctime`.
- [ ] I can rename, replace, and delete filesystem objects correctly,
      and I know `.rmdir()` only removes empty directories.
- [ ] I understand symbolic links, including broken symlinks and the
      `.exists()`/`.is_symlink()` distinction.
- [ ] I understand path resolution — the difference between
      `.absolute()` and `.resolve()`, and strict vs. non-strict
      resolution.
- [ ] I can write portable paths that work correctly on Linux, macOS,
      and Windows.
- [ ] I understand the WSL2/Windows path-translation distinction and
      its performance implications.
- [ ] I can validate user-provided paths at the application boundary.
- [ ] I understand path traversal and can defend against it using
      `.resolve()` plus `.is_relative_to()`.
- [ ] I understand TOCTOU at a conceptual level, and prefer
      attempt-and-handle over check-then-act where it matters.
- [ ] I can test filesystem code using `pytest`'s `tmp_path` fixture.
- [ ] I can debug path problems systematically, using a repeatable
      checklist rather than guessing.
- [ ] I can use `pathlib` in production-oriented Python code —
      separating path/filesystem concerns from business logic, using
      clear type hints, and applying safe write patterns where they
      matter.

With this foundation in place, you are ready for
[03-csv-files.md](03-csv-files.md), where the paths this chapter taught
you to build and validate start pointing at genuinely structured data.
