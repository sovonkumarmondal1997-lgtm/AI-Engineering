# 02 — pathlib and Portable Paths: Complete Study Guide

**Roadmap:** Stage 1 → Module 05 — Text Files, Structured Data, and CLI Programs  
**Lesson:** 02 — pathlib and Portable Paths  
**Python baseline:** 3.10+ unless a version note says otherwise

---

# Part A — Complete lesson summary and teaching notes

## 1. Why paths matter

A **filesystem** is the operating system's way of organizing stored data. A **file** stores named data; a **directory** (folder) contains files and other directories. A **path** describes where a file or directory is located. The path is not the file and does not prove that the location exists.

Example project:

```text
project/
├── data/
│   ├── customers.csv
│   └── transactions.csv
├── src/
│   └── main.py
└── README.md
```

`data/customers.csv` has directory component `data`, filename `customers.csv`, stem `customers`, and suffix `.csv`. A directory's **parent** is the directory directly containing it. The **root** is the top of the filesystem (`/` on Linux/macOS; a drive root such as `C:\\` on Windows).

- **Absolute path:** begins from the filesystem root and identifies a location independently of the current directory, e.g. `/home/user/project/data/customers.csv`.
- **Relative path:** is interpreted from a starting directory, usually the process's current working directory (cwd), e.g. `data/customers.csv`.
- `.` means the current directory; `..` means the parent. `data/../data/customers.csv` and `data/customers.csv` identify the same normalized location.

Programs need paths because every filesystem operation needs a specific location.

## 2. Why `pathlib` is preferred to manual strings

String concatenation is fragile:

```python
folder = "data"
filename = "customers.csv"
file_path = folder + filename  # "datacustomers.csv" — wrong
```

`os.path.join("data", "customers.csv")` solves separator joining and remains valid. However, it returns strings and uses separate functions such as `basename`, `dirname`, and `splitext`.

`pathlib` represents paths as objects:

```python
from pathlib import Path

base = Path("data")
file_path = base / "customers.csv"
print(file_path)  # data/customers.csv
```

The `/` operator is deliberately overloaded by `Path` to join components using the correct platform convention. It prevents missing-separator mistakes and gives access to path-aware properties and methods. Important edge case: an absolute right-hand operand replaces the left side:

```python
Path("data") / "/etc/passwd"  # PosixPath('/etc/passwd')
```

Never assume a user-supplied component will remain inside the left-hand directory.

### Path class family

- `Path`: normal application choice; supports filesystem operations and automatically selects the platform's concrete class.
- `PosixPath` / `WindowsPath`: concrete filesystem paths for the current operating system; usually created through `Path()`.
- `PurePath`: path computation without filesystem access.
- `PurePosixPath` / `PureWindowsPath`: reason about a POSIX or Windows path on any operating system without touching that filesystem.

Use `Path(...)` in ordinary application code. Pure paths are useful when analyzing a path belonging to another OS.

## 3. Constructing paths

```python
Path()                         # current directory, "."
Path("data")
Path("data", "customers.csv")
Path("data/customers.csv")
Path.cwd()                     # cwd as an absolute Path
Path.home()                    # current user's home directory
```

All of the following are valid:

```python
base = Path("data")
raw_dir = base / "raw"
customers_file = raw_dir / "customers.csv"
```

Build paths from components rather than hardcoding separators or concatenating strings.

## 4. Path components and properties

For:

```python
p = Path("/home/user/project/data/report.csv")
```

- `.name` → `report.csv` (last component).
- `.stem` → `report` (filename without its final suffix).
- `.suffix` → `.csv` (last extension, including dot; empty if none).
- `.suffixes` → `['.csv']`; for `archive.tar.gz`, it is `['.tar', '.gz']`.
- `.parent` → `/home/user/project/data`.
- `.parents` → iterable/indexable ancestors, nearest first; `p.parents[0]` equals `p.parent`.
- `.parts` → tuple of path components.
- `.anchor` → drive plus root, such as `/` or `C:\\`.
- `.root` → root marker.
- `.drive` → Windows drive/UNC share; empty on POSIX.

`.stem` removes only the final suffix: `archive.tar.gz` has stem `archive.tar`, suffix `.gz`, suffixes `['.tar', '.gz']`. `.parents` slicing is available from Python 3.10.

## 5. Current working directory and project-relative paths

A relative path is resolved against the process's cwd. The cwd is set by the launcher, not automatically by the script's physical location. Terminals, IDEs, pytest, and notebooks can each start programs from different directories.

For example, `Path("data/customers.csv")` may work when launched from `project/`, but fail when launched from `project/src/`, even though the code is unchanged.

```python
Path.cwd()                         # launch directory
Path(__file__).resolve().parent    # directory containing this .py file
```

`__file__` is generally available in scripts, but not necessarily in an interactive REPL or notebook.

For files belonging to the project, anchor paths to the source file:

```python
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
```

If `main.py` is inside `project/src/` but data is a sibling directory at `project/data/`, go up one additional parent:

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
```

Choose the path source according to intent:
1. Project-relative paths for bundled project files.
2. Configuration paths when operators should configure locations.
3. Environment-variable paths for deployment-specific locations.
4. User-provided paths for interactive tools; validate them before use.

`Path.cwd()` is appropriate when the tool is deliberately meant to operate relative to the user's current directory. It is not a universal replacement for project-relative paths.

## 6. Path resolution

- `.absolute()` prepends cwd to a relative path. It is syntactic: it does not normalize `.`/`..`, follow symlinks, or inspect the filesystem.
- `.resolve()` produces a normalized absolute path, removes `.`/`..`, follows symlinks, and consults the filesystem.
- `.resolve()` defaults to non-strict behavior: it can return a normalized path even if the final path does not exist. `.resolve(strict=True)` raises `FileNotFoundError` if the path cannot be resolved because a component is missing.
- `.expanduser()` explicitly expands `~`; `Path("~/notes.txt")` does not expand it automatically.
- `.relative_to(base)` returns a path relative to `base`, but raises `ValueError` if the path is not a descendant. `.is_relative_to(base)` is the Boolean check (Python 3.9+). `walk_up=True` for `.relative_to()` was added in Python 3.12.

Do not confuse a successfully resolved path with an existing file.

## 7. Inspecting paths and filesystem objects

```python
p.exists()       # does something exist here?
p.is_file()      # regular file?
p.is_dir()       # directory?
p.is_symlink()   # is this path itself a symlink?
```

`.exists()` follows a symlink and checks its target. `.is_symlink()` checks the link itself. Therefore a broken symlink can have `is_symlink() == True` and `exists() == False`.

Other specialized checks include `.is_mount()`, `.is_block_device()`, `.is_char_device()`, `.is_fifo()`, and `.is_socket()`. These are mainly for lower-level/platform-specific work.

## 8. Directory traversal and glob patterns

- `.iterdir()` yields direct children only.
- `.glob(pattern)` finds matching children at the depth described by the pattern.
- `.rglob(pattern)` searches recursively; it is equivalent to `.glob("**/" + pattern)`.

Glob wildcards: `*` means any number of characters within one path component; `?` means one character; `[abc]` means one of the listed characters; `**` means recursive directory depth when used in a glob pattern.

```python
for item in Path("data").iterdir():
    print(item)

csv_files = sorted(Path("data").glob("*.csv"))
json_files = sorted(Path("data").rglob("*.json"))
```

Traversal methods are lazy and do not guarantee order. Sort results whenever deterministic reports, tests, or logs are required. Hidden dotfiles are included; filter them yourself if needed. Recursive globbing does not follow directory symlinks by default; `recurse_symlinks=True` is a Python 3.13 addition. Large recursive trees cost time proportional to entries visited.

## 9. Creating directories and files

```python
Path("data").mkdir()  # one directory; parent must exist; fails if already exists
Path("data/raw/2024").mkdir(parents=True, exist_ok=True)
```

- `parents=True` creates missing parent directories.
- `exist_ok=True` tolerates an already-existing directory, but not a file at that path.
- `mode=0o755` requests POSIX permissions; the OS umask may further restrict them.
- Concurrent creation can still encounter rare race conditions.

`.touch()` creates an empty file if missing. By default `exist_ok=True`, it leaves existing content intact but updates its modification timestamp. Use `touch(exist_ok=False)` when the final path must not already exist. This exclusive creation is safer than `if not path.exists(): path.touch()`, which has a race between the check and creation.

## 10. Reading and writing through `pathlib`

```python
text = Path("notes.txt").read_text(encoding="utf-8")
Path("notes.txt").write_text("Hello", encoding="utf-8")

with Path("notes.txt").open("r", encoding="utf-8") as handle:
    for line in handle:
        print(line)
```

`read_text()` and `write_text()` open, perform one whole-file operation, and close automatically. They are convenient for small files. `.open()` behaves like built-in `open()` and is preferable for streaming, line-by-line processing, or multiple operations on one open file. Specify UTF-8 explicitly for predictable text handling. `write_text(newline=...)` is available from Python 3.10. Binary counterparts are `.read_bytes()` and `.write_bytes()`.

## 11. Metadata

`.stat()` asks the OS for metadata:

```python
info = Path("data/customers.csv").stat()
info.st_size   # bytes
info.st_mtime  # modification time, Unix timestamp
info.st_ctime  # platform-dependent meaning
info.st_mode   # packed file type and permission bits
```

`st_ctime` means metadata-change time on Linux, but creation time on Windows; do not treat it as a portable creation timestamp. Convert `st_mtime` with `datetime.fromtimestamp(...)` when a readable date is needed. `.stat()` follows symlinks; `.lstat()` reports metadata about the link itself.

## 12. Rename, replace, delete

- `.rename(destination)` renames/moves. If destination exists, POSIX generally overwrites while Windows raises `FileExistsError`.
- `.replace(destination)` consistently requests overwrite behavior across platforms; use it when overwrite is intended.
- Rename/replace is typically atomic on the same filesystem. Cross-filesystem rename may fail with `OSError`; it does not automatically copy.
- `shutil.move()` can fall back to copy-and-delete across filesystems, but that is not atomic and can leave partial results.
- `.unlink()` deletes a file; `missing_ok=True` (Python 3.8+) treats a missing file as acceptable.
- `.rmdir()` removes only an empty directory. Recursive deletion belongs to `shutil.rmtree()` and must be deliberate.

Anticipate `FileNotFoundError`, `PermissionError`, `IsADirectoryError`, `NotADirectoryError`, and `OSError` for non-empty directories. Check expected object types and never delete an unvalidated user path.

## 13. Symbolic links

A symlink is a filesystem entry pointing to another path. Reading/writing through it acts on its target.

```python
link = Path("latest")
link.symlink_to("release-2.3")
link.is_symlink()  # True
link.readlink()    # raw target path (Python 3.9+)
```

A relative symlink target is interpreted relative to the link's directory, not the program's cwd; it is often portable when the whole directory tree moves. An absolute target can break when its location changes. Broken links still exist as links, but their target does not: `.is_symlink()` can be true while `.exists()` is false. `.stat()` follows the link, `.lstat()` does not, and `.resolve()` follows it to its final target. Symlinks can be used in attacks to redirect operations; untrusted paths need validation and, in high-security settings, stronger protections.

## 14. Copy and move with `shutil`

`pathlib` represents paths and provides simple operations tied to one path. `shutil` handles multi-file operations:

```python
from shutil import copy, copy2, copytree, move

copy(source, destination)       # content + permission bits
copy2(source, destination)      # additionally attempts to preserve metadata
copytree(source_dir, target_dir)
move(source, destination)
```

These functions accept `Path` objects directly. `copy2()` is generally preferred for a more faithful duplicate. Ensure destination-parent assumptions are satisfied.

## 15. Path transformations and matching

These return new path values; they do not change the filesystem:

```python
p.with_name("summary.csv")   # replace final component
p.with_stem("summary")       # replace stem; Python 3.9+
p.with_suffix(".json")       # replace suffix
```

To actually rename, call `p.rename(new_path)` or `p.replace(new_path)`. `.with_segments()` is a Python 3.12 feature mainly for custom path subclasses.

`.match(pattern)` checks one known path against a glob pattern; it does not search a directory. `.glob()` and `.rglob()` search the filesystem. `.match()` does not provide recursive `**` matching; Python 3.13 adds `.full_match()` for full glob matching. Use `.rglob()` for recursive searching on older supported versions.

## 16. `os.PathLike`, strings, and interoperability

`os.PathLike` is an interface for objects implementing `__fspath__`. `Path` implements it, so built-in `open()`, `shutil`, and many standard-library functions accept a `Path` without converting it to a string.

```python
import os
path = Path("data/file.txt")
isinstance(path, os.PathLike)  # True
os.fspath(path)                 # "data/file.txt"
str(path)                       # string representation
```

Keep paths as `Path` internally. Convert to `str` only at a genuine boundary where an external API requires it. `os.path` is still valid and common in legacy code; new Python application code often favors `pathlib`. `shutil` remains the tool for copying/moving trees and recursive deletion.

## 17. Cross-platform paths, Windows, Linux, and WSL2

Use `Path("data") / "file.txt"` rather than hardcoded `/` or `\\` separators or machine-specific absolute paths. `pathlib` handles separator composition, but cannot erase all OS differences: case sensitivity, reserved filenames, drive letters, permissions, and filesystem behavior can differ.

A raw string (`r"C:\\Users\\You\\data.txt"`) prevents backslashes from being interpreted as escape sequences when a literal Windows path is unavoidable. It is not the preferred way to build paths.

Linux has one root `/`; Windows commonly has drive roots such as `C:\\`. WSL2 runs a genuine Linux environment. Its native Linux files (for example `/home/...`) behave like Linux. Windows files appear under `/mnt/c/...`; `C:\\Users\\You\\...` and `/mnt/c/Users/You/...` are different path representations for the same physical files. Access across the WSL2/Windows boundary can be slower, especially for workloads with many filesystem operations. Prefer native Linux storage for intensive work when practical. Portable code also runs more easily in Docker, Linux servers, macOS, and CI.

## 18. Permissions and path validation

Read permission controls reading file content/listing directories; write permission controls modifying or creating/removing entries; directory execute/search permission controls traversing it; ownership affects which permissions apply. POSIX uses owner/group/other bits; Windows uses ACLs, so permission semantics are not identical. An OS may raise `PermissionError`.

Validate paths at the boundary in six steps:
1. Receive external input.
2. Convert it to `Path`.
3. Resolve/normalize when appropriate.
4. Validate existence, expected type, and allowed location.
5. Perform the requested operation.
6. Handle specific expected exceptions.

```python
def validate_input_file(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"No such file: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"Expected a file: {resolved}")
    return resolved
```

Validation describes the state at that moment; the filesystem may change immediately afterward, so the actual operation must still handle errors.

## 19. Path traversal and TOCTOU

Path traversal occurs when untrusted input such as `../../etc/passwd` escapes an intended directory. Resolve both base and candidate before checking containment:

```python
def safe_path_within(base_dir: Path, user_supplied: str) -> Path:
    base = base_dir.resolve()
    candidate = (base / user_supplied).resolve()
    if not candidate.is_relative_to(base):
        raise ValueError(f"Path traversal: {user_supplied!r}")
    return candidate
```

This also follows symlinks before comparison. A string-prefix test is weaker because similar textual prefixes and unresolved `..` can fool it. This introductory defense is not a complete guarantee against an attacker changing symlinks between validation and use; security-critical systems need stronger handle-based/directory-relative operations.

**TOCTOU** means time-of-check to time-of-use. This is risky:

```python
if path.exists():
    content = path.read_text(encoding="utf-8")
```

The file may disappear or change between the check and read. Prefer attempting the operation and handling the specific failure:

```python
try:
    content = path.read_text(encoding="utf-8")
except FileNotFoundError:
    content = ""
```

A pre-check can still provide early user feedback, but never treat it as a guarantee that the later operation will succeed.

## 20. Safe writes and performance

A production-oriented write pattern creates a unique temporary file in the target's own directory, writes all content, closes it, and then replaces the target. Same-directory placement keeps the replace on one filesystem. If writing/replacing fails, attempt to remove the temporary file and re-raise the original failure. This protects the original target from a partial write. Atomic visibility is not the same as durability: no `fsync()` means the pattern does not guarantee survival through power loss; cleanup can also fail.

Directory traversal (`iterdir`, `glob`, `rglob`) is lazy; wrapping in `list()` collects all results in memory. `rglob()` cost depends on all entries visited, not only matches. Each metadata method may trigger a separate OS call, so avoid redundant `.stat()`/`.is_file()` checks when measured performance justifies it. Network filesystems and WSL2 Windows-mounted paths add latency.

## 21. Application architecture, testing, debugging

Separate responsibilities:
1. Path/configuration layer decides locations.
2. Filesystem adapter reads/writes.
3. Domain logic transforms values without filesystem access.
4. Orchestration/CLI coordinates the steps.

Prefer small reusable functions with clear `Path` type hints and explicit parameters. `Path | str` is reasonable for a public convenience function, but internal functions are often clearer accepting `Path`.

Use pytest's `tmp_path` fixture for filesystem tests. It gives each test an isolated temporary directory as a `Path`, cleaned up automatically. Test successful and failure paths: missing files, wrong types, nested directory creation, rename, traversal rejection. Permission tests are difficult to make portable; simulate the exception path with a helper rather than relying on OS permissions.

Debug systematically: inspect the path and `repr(path)`, cwd, `.absolute()`, `.resolve()`, `.exists()`, `.is_file()`, `.is_dir()`, parent directories, permissions, platform, symlinks, then reproduce in a small temporary directory.

Common mistakes include hardcoded absolute paths, string concatenation, assuming cwd, passing only a filename when a directory was intended, confusing a `Path` with file contents, omitting `parents=True`, using `rmdir()` on non-empty directories, assuming `.with_suffix()` renames, assuming `.resolve()` creates something, trusting `.exists()` before a later operation, ignoring permissions, blanket exception catches, converting everything to strings, hardcoded OS syntax, and tests that write into real user directories.

## 22. AI/data engineering examples and mini-projects

Typical uses include locating model configuration files relative to source code, validating dataset directories, creating experiment output directories, finding CSV/JSON files recursively, creating timestamped experiment folders, saving logs and metrics, validating user-provided input files, and passing input/output `Path` objects into CLI functions.

The lesson proposes three mini-projects:
- **Filesystem Explorer:** validate a directory, list direct children, identify file/directory types, show file sizes, handle missing/wrong-type/permission errors, sort deterministically, and test with `tmp_path`.
- **Data Directory Inspector:** recursively find CSV/JSON, count each type, total sizes, detect zero-byte files, sort output, avoid duplicate metadata calls, and test a known temporary tree.
- **Safe Project Artifact Manager:** define project output directories, validate artifact names against traversal, write with write-then-replace, handle overwrites and errors, and test successful writes, traversal rejection, safe overwrite, and directory creation.

---

# Part B — Project-tree review and learning-level assessment

Your roadmap places this lesson in **Stage 1 → Module 05: Text Files, Structured Data, and CLI Programs**. The previous lesson, *Reading and Writing Text Files*, introduced `open()`, modes, context managers, file exceptions, text encoding, streaming, and basic `tmp_path`/pytest usage. This lesson is the second step: it adds portable path construction and filesystem operations before the later CSV, JSON, encoding/newline, argparse, streams, logging, and environment-configuration lessons.

Your recorded progress includes Python fundamentals, conditions, loops, functions, arguments/defaults/docstrings, scope, pure functions/side effects, collections, comprehensions, algorithms, recursion, parsing/regex, and exceptions/validation. The overall assessment remains **beginner progressing toward intermediate**.

For this lesson, use the following boundaries:
- In scope: Python functions, loops, collections, exceptions, type hints, `Path`, `shutil`, `tempfile` examples from this lesson, and the basic pytest `tmp_path`/`pytest.raises` patterns shown here.
- Do not assume later Module 05 lessons such as CSV, JSON, argparse, logging, or environment configuration have been completed.
- Do not introduce unrelated pandas, NumPy, Spark, databases, decorators, or advanced OOP.
- The lesson itself introduces advanced filesystem/security concepts. The solutions below explain them at the level presented here; production hardening beyond the chapter is explicitly identified as out of scope.

---

# Part C — All coding exercises solved

The examples use `Path` and temporary test directories. Run filesystem examples in a safe practice folder, not over valuable real data.

## Level 1 — Foundation

### 1. Create a path and print its name

```python
from pathlib import Path

report_path = Path("reports/summary.txt")
print(report_path.name)
```

- Import `Path` to work with filesystem paths.
- Construct the path; this does not create a file.
- `.name` returns the final component: `summary.txt`.

### 2. Print its parent

```python
from pathlib import Path

report_path = Path("reports/summary.txt")
print(report_path.parent)
```

`.parent` returns the containing directory: `reports`.

### 3. Inspect multi-suffix filename

```python
from pathlib import Path

archive = Path("archive.tar.gz")
print(archive.suffix)   # .gz
print(archive.stem)     # archive.tar
print(archive.suffixes) # ['.tar', '.gz']
```

`.suffix` and `.stem` concern the final suffix only. `.suffixes` returns all suffixes; therefore `.suffix` alone is not `.tar.gz`.

### 4. Check existence

```python
from pathlib import Path

candidate = Path("data/customers.csv")
print(candidate.exists())
```

The result is `True` if something exists at that path and `False` otherwise. It does not prove that the object is a regular file.

### 5. Create a directory

```python
from pathlib import Path

reports_dir = Path("reports")
reports_dir.mkdir()
```

This creates one directory. Running it a second time raises `FileExistsError`. For repeatable setup, use `reports_dir.mkdir(parents=True, exist_ok=True)`.

### 6. Create an empty file inside it

```python
from pathlib import Path

reports_dir = Path("reports")
reports_dir.mkdir(parents=True, exist_ok=True)

summary_file = reports_dir / "summary.txt"
summary_file.touch(exist_ok=False)
```

First ensure the parent exists. `/` builds the child path. `touch(exist_ok=False)` creates the file only if it is absent; it raises `FileExistsError` if already present.

## Level 2 — Practical

### 7. Find Python files recursively in sorted order

```python
from pathlib import Path

source_dir = Path("src")
for python_file in sorted(source_dir.rglob("*.py")):
    print(python_file)
```

`rglob("*.py")` searches all nested levels. `sorted()` makes output deterministic; the loop prints each matching path.

### 8. Create a three-level nested directory in one call

```python
from pathlib import Path

nested_dir = Path("data") / "raw" / "2026"
nested_dir.mkdir(parents=True, exist_ok=True)
```

Each `/` adds a component. `parents=True` creates missing ancestors; `exist_ok=True` makes an already-existing directory acceptable.

### 9. Rename and verify both paths

```python
from pathlib import Path

old_path = Path("reports/old.txt")
new_path = Path("reports/new.txt")

old_path.rename(new_path)

print(old_path.exists())  # False
print(new_path.exists())  # True
```

`rename()` performs the filesystem operation. The two checks confirm the expected state. This assumes the source exists and the destination behavior is acceptable on the current platform.

### 10. Validate that an input exists and is a file

```python
from pathlib import Path

def validate_input_path(path: Path) -> Path:
    resolved = path.resolve()

    if not resolved.exists():
        raise FileNotFoundError(f"Input does not exist: {resolved}")
    if not resolved.is_file():
        raise IsADirectoryError(f"Expected a file, got: {resolved}")

    return resolved
```

- The function accepts a `Path` and returns a validated, resolved `Path`.
- Missing input raises `FileNotFoundError`.
- An existing directory or other non-file raises a different exception.
- Returning the path lets callers use the validated value.

### 11. Total bytes of direct files only

```python
from pathlib import Path

def total_direct_file_size(directory: Path) -> int:
    if not directory.is_dir():
        raise NotADirectoryError(directory)

    total = 0
    for entry in directory.iterdir():
        if entry.is_file():
            total += entry.stat().st_size
    return total
```

Validate the directory first. `iterdir()` visits direct children only, so nested files are excluded. Add each regular file's byte size. An empty directory returns `0`.

## Level 3 — Engineering

### 12. Reusable validator with optional suffix

```python
from pathlib import Path

def validate_path(path: Path, expected_suffix: str | None = None) -> Path:
    resolved = path.resolve()

    if not resolved.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"Expected a regular file: {resolved}")
    if expected_suffix is not None and resolved.suffix != expected_suffix:
        raise ValueError(f"Expected {expected_suffix}, got {resolved.suffix}")

    return resolved
```

The optional argument defaults to `None`, meaning no extension restriction. Each failure has a clear exception/message. The caller can request, for example, `validate_path(path, ".csv")`.

### 13. Project path constants

Example `src/project_paths.py`:

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
```

`__file__` points to this module. `.parent` is `src/`; `.parent.parent` is the project root. The other paths are built from that anchor, not from cwd. A test can assert the expected relationships:

```python
def test_project_paths():
    assert DATA_DIR == PROJECT_ROOT / "data"
    assert OUTPUT_DIR == PROJECT_ROOT / "output"
    assert PROJECT_ROOT == Path(__file__).resolve().parents[1]
```

The final assertion assumes the test file is one directory below the project root; adjust the parent index to match the actual tree.

### 14. Test three Level 2 functions with `tmp_path`

```python
def test_nested_directory(tmp_path):
    target = tmp_path / "one" / "two" / "three"
    target.mkdir(parents=True, exist_ok=True)
    assert target.is_dir()

def test_validate_file(tmp_path):
    file_path = tmp_path / "input.txt"
    file_path.write_text("hello", encoding="utf-8")
    assert validate_input_path(file_path) == file_path.resolve()

def test_total_size(tmp_path):
    (tmp_path / "a.txt").write_text("abc", encoding="utf-8")
    (tmp_path / "b.txt").write_text("12345", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "ignored.txt").write_text("longer", encoding="utf-8")
    assert total_direct_file_size(tmp_path) == 8
```

`tmp_path` is a fresh isolated directory. The tests check nested creation, successful file validation, and direct-child byte totals (3 + 5; nested file excluded).

### 15. Safe output path

```python
from pathlib import Path

def safe_output_path(base_dir: Path, filename: str) -> Path:
    base = base_dir.resolve()
    candidate = (base / filename).resolve()

    if not candidate.is_relative_to(base):
        raise ValueError(f"Output path escapes its directory: {filename!r}")

    return candidate
```

Resolve both paths before checking. `.is_relative_to()` ensures the final candidate remains under the allowed base. Absolute-path injection and `..` traversal are rejected.

### 16. Standalone traversal guard and tests

```python
def safe_path_within(base_dir: Path, supplied_name: str) -> Path:
    base = base_dir.resolve()
    candidate = (base / supplied_name).resolve()
    if not candidate.is_relative_to(base):
        raise ValueError("Path is outside the allowed directory")
    return candidate

def test_safe_path_within(tmp_path):
    base = tmp_path / "uploads"
    base.mkdir()
    assert safe_path_within(base, "report.csv") == base / "report.csv"

def test_rejects_parent_traversal(tmp_path):
    base = tmp_path / "uploads"
    base.mkdir()
    with pytest.raises(ValueError):
        safe_path_within(base, "../outside.txt")

def test_rejects_absolute_path(tmp_path):
    base = tmp_path / "uploads"
    base.mkdir()
    with pytest.raises(ValueError):
        safe_path_within(base, str(tmp_path / "outside.txt"))
```

The function is reusable and separate from the calling code. The tests prove an allowed child works and both relative traversal and absolute-path injection fail. Import `pytest` in the test module.

## Level 4 — Advanced

### 17. Report symlink and target status

```python
from pathlib import Path

def describe_symlink(link: Path) -> tuple[bool, bool, bool]:
    is_link = link.is_symlink()
    link_exists = is_link
    target_exists = link.exists() if is_link else False
    return is_link, link_exists, target_exists
```

The first Boolean identifies the link object. For a symlink, `is_symlink()` means the link exists as an entry; `exists()` checks its target. A broken link returns `(True, True, False)`. A non-link returns `(False, False, False)`. The tuple type hint describes the three Boolean results.

### 18. Read an optional config using attempt-and-handle

```python
from pathlib import Path

def read_optional_config(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def test_missing_optional_config_uses_default(tmp_path):
    missing = tmp_path / "config.txt"
    assert read_optional_config(missing) == ""
```

Do not check `.exists()` first: that creates a TOCTOU gap. Attempt the read and catch the specific expected missing-file exception. The test verifies the exception-handling path. Other errors, such as `PermissionError`, are allowed to propagate.

### 19. Deterministic directory listing

```python
from pathlib import Path

def list_files_sorted(directory: Path) -> list[Path]:
    return sorted(
        entry for entry in directory.iterdir()
        if entry.is_file()
    )
```

The function filters direct regular files and sorts their `Path` values. This gives deterministic ordering regardless of filesystem enumeration order.

```python
def test_list_files_sorted(tmp_path):
    (tmp_path / "b.txt").touch()
    (tmp_path / "a.txt").touch()
    result = list_files_sorted(tmp_path)
    assert [item.name for item in result] == ["a.txt", "b.txt"]
```

The test deliberately creates files in reverse alphabetical order, then proves the function returns sorted names.

### 20. Safe write-then-replace and failure test

```python
from pathlib import Path
import tempfile

def write_content(handle, content: str) -> None:
    handle.write(content)

def write_safely(target: Path, content: str, writer=write_content) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=target.parent,
            prefix=target.name + ".", suffix=".tmp", delete=False
        ) as handle:
            temporary = Path(handle.name)
            writer(handle, content)
        temporary.replace(target)
    except BaseException:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        raise
```

The temporary file is unique and in the target directory, so replacement stays on the same filesystem. `writer` is normally `write_content`; allowing a writer function also creates a controlled test seam. The target is replaced only after the full write succeeds. Cleanup errors do not hide the original failure; the original exception is re-raised.

```python
import pytest

def test_failed_write_preserves_original(tmp_path):
    target = tmp_path / "report.txt"
    target.write_text("original", encoding="utf-8")

    def fail_writer(handle, content):
        raise OSError("simulated write failure")

    with pytest.raises(OSError):
        write_safely(target, "replacement", writer=fail_writer)

    assert target.read_text(encoding="utf-8") == "original"
```

The test begins with known original content, injects a writer that raises before replacement, checks the expected exception, then verifies the target is unchanged. The temporary file cleanup is attempted by the function.

### 21. Portable filesystem utility module

A small reusable module can combine the already-built helpers:

```python
from pathlib import Path

def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def inspect_file(path: Path) -> tuple[int, str]:
    valid = validate_path(path)
    info = valid.stat()
    return info.st_size, valid.suffix

def build_safe_artifact_path(output_dir: Path, name: str) -> Path:
    ensure_directory(output_dir)
    return safe_path_within(output_dir, name)
```

- `ensure_directory` creates the directory tree and returns its path.
- `inspect_file` reuses the validator, calls `stat()` once, and returns size and suffix.
- `build_safe_artifact_path` ensures the output directory exists and applies traversal validation.

```python
def test_utility_module(tmp_path):
    output = tmp_path / "results"
    assert ensure_directory(output).is_dir()

    artifact = output / "metrics.csv"
    artifact.write_text("a,b", encoding="utf-8")
    assert inspect_file(artifact) == (3, ".csv")

    assert build_safe_artifact_path(output, "new.json") == output / "new.json"
    with pytest.raises(ValueError):
        build_safe_artifact_path(output, "../escape.json")
```

Each assertion tests one responsibility. Add separate missing-file and wrong-type tests for `inspect_file` by passing a missing path and a directory path. All functions have explicit type hints and receive paths rather than silently relying on cwd.

---

# Part D — All debugging exercises

1. **Wrong cwd:** `Path("data/customers.csv")` is cwd-relative. Inspect `Path.cwd()` and anchor to `Path(__file__).resolve().parent` (or the correct number of parents) when the data belongs to the project.
2. **Incorrect concatenation:** `"data" + "report.csv"` becomes `"datareport.csv"`. Use `Path("data") / "report.csv"`.
3. **Missing parent:** writing `output/2024/results.json` fails if parents are absent. First call `Path("output/2024").mkdir(parents=True, exist_ok=True)`.
4. **Directory mistaken for file:** reading a directory raises `IsADirectoryError`. Check `.is_file()` or use `Path("config") / "settings.json"` if that was intended.
5. **Windows path on Linux/WSL2:** `Path("C:\\Users\\User\\data.txt")` is not a native Linux path. Inspect `type(path)` and `.exists()`; construct paths for the OS/context where the program runs.
6. **Broken symlink:** after the target is deleted, `link.is_symlink()` is true but `link.exists()` is false. Handle `FileNotFoundError` when reading, or check target status for clear feedback.
7. **Traversal:** `"../../etc/cron.d/evil"` can escape the base directory. Resolve candidate and base, then reject unless `candidate.is_relative_to(base)` is true.
8. **Resolved but missing:** `.resolve()` with default `strict=False` does not require existence. Check `.exists()` or use `.resolve(strict=True)` when missing paths must raise.
9. **Invalid `.relative_to()`:** `/home/user/project` is not inside `/home/user/other`, so `.relative_to()` raises `ValueError`. Use `.is_relative_to()` for a Boolean check; Python 3.12+ `walk_up=True` is only for intentionally computing an upward path.

---

# Part E — Knowledge-check answers

1. A `Path` is an in-memory location description, not the file; it can describe something that does not exist.
2. A relative path needs a starting directory, usually cwd, and cwd can change between launches.
3. On POSIX, `Path("a") / "b" / "/c" / "d"` becomes `/c/d`; the absolute component discards earlier components.
4. For `report.tar.gz`: stem is `report.tar`, suffix is `.gz`, suffixes are `['.tar', '.gz']`.
5. `exist_ok=True` only tolerates an existing directory; a file at that name can still raise `FileExistsError`. Permissions or concurrent races can also cause errors.
6. Use `.rglob("*.log")` for all depths.
7. Use `.match("*.csv")` to test one known path without searching.
8. Repeated `/` joins make dynamically selected components clear and safe; a preformatted string requires manual separators/interpolation.
9. A Windows path such as `C:\\Users\\You\\...` appears inside WSL2 as `/mnt/c/Users/You/...`.
10. A string-prefix check compares text and can be fooled by similar prefixes or unresolved `..`; resolved paths plus `.is_relative_to()` compare actual normalized locations.
11. A function that calls `Path.cwd()` depends on the test runner's launch directory. Passing a base `Path` makes tests deterministic and lets them use `tmp_path`.

---

# Part F — Interview revision prompts

Be prepared to explain:
- Why `pathlib` is preferred over string concatenation, and how it differs from `os.path`.
- Absolute vs relative paths; cwd vs `__file__`-anchored paths.
- `.absolute()` vs `.resolve()`, `.relative_to()` vs `.is_relative_to()`.
- `.iterdir()`, `.glob()`, `.rglob()`, and `.match()`.
- `.stat()` vs `.lstat()`, and how broken symlinks behave.
- `.rename()` vs `.replace()`, and same-filesystem atomicity.
- `os.PathLike`, WSL2 path translation, and platform limitations.
- Path validation, traversal, TOCTOU, safe write-then-replace, and `tmp_path`.

---

# Part G — Final revision checklist

- [ ] A `Path` describes a location; it is not the file.
- [ ] Build paths with `Path(...)` and `/`, not string concatenation.
- [ ] Know the cwd and choose project-relative vs user-relative paths intentionally.
- [ ] Understand path properties, parents, suffixes, and absolute/relative paths.
- [ ] Distinguish `.absolute()` from `.resolve()`.
- [ ] Distinguish `.exists()` from `.is_file()`, `.is_dir()`, and `.is_symlink()`.
- [ ] Sort traversal results when deterministic output matters.
- [ ] Use `mkdir(parents=True, exist_ok=True)` for repeatable directory setup.
- [ ] Use `read_text`/`write_text` for small files and `.open()` for streaming.
- [ ] Understand metadata, rename/replace, deletion, symlinks, and `shutil`.
- [ ] Validate external paths and defend against traversal.
- [ ] Prefer attempt-and-handle over check-then-act where races matter.
- [ ] Use `tmp_path` for filesystem tests.
- [ ] Separate path construction, filesystem I/O, domain logic, and orchestration.

**Next roadmap lesson:** `03-csv-files.md`. Do not move forward until you can construct and validate paths, explain cwd behavior, and complete the exercises without relying on hardcoded machine-specific locations.
