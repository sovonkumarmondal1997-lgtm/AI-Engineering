# File Operations, Temporary Storage, ZIP and TAR Archives

> **Target:** Python 3.12+ · **Module:** Stage 1, Module 13 — Standard Library Toolkit · **Lesson:** 03
>
> This lesson builds on the roadmap's earlier lessons on file I/O, `pathlib`, encodings, pytest, idempotency, and safe file writes. It focuses on local filesystem operations and archive handling—not cloud storage or third-party storage platforms.

## Learning objectives

By the end, you should be able to:

- Choose the right `shutil` copy/move/archive API and explain which metadata it preserves.
- Create temporary resources with safe lifetime management.
- Write a file by atomic replacement and distinguish atomic visibility from crash durability.
- Read large ZIP/TAR members without materializing the whole member in memory.
- Extract archives defensively with path, type, member-count, and byte limits.
- Test success and failure paths using `pytest` and `tmp_path`.
- Design repeatable file-processing jobs with explicit recovery and integrity checks.

## 1. Prerequisites and roadmap boundaries

The roadmap places this lesson in **Phase B — Files, Processes and Local Data**, after the `itertools` and `operator` lessons and before `subprocess` and `sqlite3`.

Relevant prior knowledge:

| Prerequisite | Earlier roadmap location | Used here for |
|---|---|---|
| Text/binary file I/O, paths, encodings | Module 1.5, lessons 01–05 | Correct path handling and byte/text modes |
| `pathlib` | Module 1.5, lesson 02 | Portable paths and path composition |
| pytest and boundary testing | Module 1.7 | Isolated filesystem tests with `tmp_path` |
| Idempotency and safe writes | Module 1.10, lessons 04–05 | Atomic replacement and repeatable processing |
| Context managers and generators | Module 1.9 | Resource lifetime and streaming |
| Copying/mutability | Modules 1.2 and 1.11 | Understand that filesystem copies differ from object copies |

**Scope boundaries:** use `itertools` only when an iterator is useful; this is not another iteration-recipes lesson. `functools` and functional composition are not retaught. Hashing is used for integrity verification, while deeper `hashlib`/HMAC material belongs to Lesson 06. External commands belong to Lesson 04. This lesson's central concern is local file lifecycle, copying, temporary storage, archive I/O, and safe extraction.

## 2. Foundations: filesystem operations are not transactions

A path names a filesystem object; it does not guarantee that the object exists, is writable, is on a particular filesystem, or remains unchanged between checks. Filesystem operations can fail because of permissions, disk exhaustion, path-length rules, concurrent writers, antivirus/indexer locks, or device errors.

Three guarantees are distinct:

- **Atomic visibility:** observers see either the old name binding or the new one, rather than a partially written destination. `os.replace()` typically provides this for a same-filesystem rename.
- **Durability:** data survives a sudden power loss. This may require flushing file contents and syncing the containing directory, and behavior depends on the OS/filesystem/storage stack.
- **Idempotency:** repeating a job has a defined safe result. Atomic replacement helps, but does not by itself prevent duplicate downstream side effects.

Treat filesystem operations as fallible. Validate inputs, use context managers, clean up temporary artifacts, and test both success and exceptions.

## 3. Beginner: copying, moving, and deleting with `shutil`

`shutil` provides high-level file operations. Prefer it over hand-written byte loops unless you need specialized progress, throttling, hashing, or policy logic.

### 3.1 Copy APIs and metadata

| API | Main behavior | Typical use |
|---|---|---|
| `shutil.copyfile(src, dst)` | Copies file contents; destination must not be a directory; does not copy permission bits | Content-only copy |
| `shutil.copy(src, dst)` | Copies contents and permission mode | Ordinary copy when mode matters |
| `shutil.copy2(src, dst)` | Like `copy`, attempts to preserve metadata such as timestamps | Backups and staging where metadata is useful |
| `shutil.copytree(src, dst)` | Recursively copies a directory tree; destination normally must not exist | Snapshot a directory tree |
| `shutil.move(src, dst)` | Renames when possible; may copy then delete across filesystems | Move with cross-device fallback understood |
| `shutil.rmtree(path)` | Removes a directory tree recursively | Cleanup only after validating the target path |

Metadata preservation is best-effort and platform-dependent. `copy2()` does not promise to preserve every ACL, owner, alternate data stream, extended attribute, or platform-specific metadata field. A filesystem copy is also not the same as `copy.copy()`/`copy.deepcopy()` on Python objects.

```python
from pathlib import Path
import shutil
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    source = root / "input.txt"
    source.write_text("batch-42\n", encoding="utf-8")

    shutil.copyfile(source, root / "contents.txt")
    shutil.copy(source, root / "mode-copy.txt")
    shutil.copy2(source, root / "metadata-copy.txt")
    print(sorted(path.name for path in root.iterdir()))
```

Output (the temporary directory itself is not listed):

```text
['contents.txt', 'input.txt', 'metadata-copy.txt', 'mode-copy.txt']
```

Use `copy2()` when timestamps and mode are helpful, not as a forensic-grade metadata clone. `copyfile()` raises `SameFileError` when source and destination refer to the same file. Copy functions can overwrite an existing destination file; establish overwrite policy explicitly.

### 3.2 `copytree`, ignore patterns, `move`, and `rmtree`

```python
from pathlib import Path
import shutil
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    source = root / "incoming"
    source.mkdir()
    (source / "data.csv").write_text("id\n1\n", encoding="utf-8")
    (source / "debug.log").write_text("verbose\n", encoding="utf-8")

    snapshot = root / "snapshot"
    shutil.copytree(source, snapshot, ignore=shutil.ignore_patterns("*.log"))
    # Merge into an existing tree (Python 3.8+).
    shutil.copytree(source, snapshot, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("*.log"))
    print(sorted(p.name for p in snapshot.iterdir()))
```

Output:

```text
['data.csv']
```

`dirs_exist_ok=True` allows the destination tree to exist; files with colliding names may be overwritten. It is not a transactional directory merge. If a copy fails halfway, the destination may be partially updated.

A same-filesystem `move()` is commonly implemented as a rename. Across filesystems, it may become copy-and-delete and can fail after copying only part of the data; it is **not necessarily atomic**. For a robust cross-filesystem move, copy into a destination-side temporary name, verify size/hash, atomically replace the final destination, and only then remove the source according to an explicit recovery policy.

`rmtree()` is destructive. Do not call it on a user-provided or derived path without checking that it is the intended child of a trusted work directory. Avoid string-prefix checks such as `str(target).startswith(str(root))`; path components and symlinks make those checks unreliable. Resolve/validate paths and keep cleanup targets narrowly scoped. `shutil.rmtree.avoids_symlink_attacks` reports whether this Python/platform uses the fd-based symlink-attack-resistant implementation; check it when the threat model requires that property. In adversarial directories, path-based checks alone cannot eliminate races; use private directories and OS-level APIs where available.

### 3.3 Utility functions

```python
import shutil

usage = shutil.disk_usage(".")
print(usage.total >= usage.used + usage.free)  # Usually True; accounting may vary.
print(shutil.which("python") is not None)     # Depends on PATH and environment.
```

- `disk_usage(path)` returns total, used, and free bytes. Do not assume all quotas or remote filesystem constraints are reflected.
- `which(command)` searches the current `PATH`. It is useful for discovery, not a guarantee the executable will remain present or trustworthy when later invoked.
- `make_archive(base_name, format, root_dir=...)` creates a supported archive such as ZIP or TAR. Ensure the source tree is trusted and that the output naming/overwrite policy is intentional.
- `unpack_archive(filename, extract_dir=...)` is convenient for trusted archives. For untrusted archives, prefer explicit format-specific validation and extraction limits; convenience APIs are not a complete resource-abuse policy.

```python
from pathlib import Path
import shutil
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    source = root / "bundle"
    source.mkdir()
    (source / "readme.txt").write_text("trusted input\n", encoding="utf-8")
    archive_base = root / "bundle-backup"
    archive_name = shutil.make_archive(str(archive_base), "zip", root_dir=source)
    extracted = root / "unpacked"
    shutil.unpack_archive(archive_name, extracted)
    print((extracted / "readme.txt").read_text(encoding="utf-8").strip())
```

Output:

```text
trusted input
```

The example uses a trusted archive created by the same process. Do not treat `unpack_archive()` as the secure extraction function for untrusted input.

## 4. Beginner: temporary files and directories

Temporary resources are useful for downloads, decompression, intermediate datasets, test fixtures, and atomic replacement. Use a context manager when possible so cleanup occurs even when an exception propagates.

| API | Returns | Notes |
|---|---|---|
| `TemporaryDirectory()` | Context manager/path-like object | Creates a directory and recursively cleans it on exit |
| `NamedTemporaryFile()` | Open file object with a name | Cross-platform reopening behavior differs; Windows may prevent reopening/deleting while open depending on options/handles |
| `mkstemp()` | `(fd, path)` | Low-level; caller must close descriptor and remove file |
| `mkdtemp()` | Directory path | Low-level; caller must remove directory |

Never use `tempfile.mktemp()`: it returns a name without creating the file, leaving a race in which another process can claim the name. Use APIs that create the resource atomically. The default temporary directory is selected by Python/OS configuration (environment and platform rules can matter); choose an explicit trusted parent when security or filesystem placement matters.

```python
from pathlib import Path
import tempfile

with tempfile.TemporaryDirectory(prefix="ingest-") as temp_dir:
    work = Path(temp_dir)
    staged = work / "part.csv"
    staged.write_text("id,value\n1,7\n", encoding="utf-8")
    print(staged.read_text(encoding="utf-8").strip())
# Directory and contents are removed here.
```

For low-level APIs, resource ownership is explicit:

```python
import os
import tempfile

fd, name = tempfile.mkstemp(prefix="chunk-")
try:
    with os.fdopen(fd, "wb") as stream:
        stream.write(b"payload")
    fd = -1  # Ownership transferred to fdopen; its context has closed it.
finally:
    if fd != -1:
        os.close(fd)
    try:
        os.unlink(name)
    except FileNotFoundError:
        pass
```

`mkstemp()` typically creates a file accessible only to the creating user (commonly mode `0o600` on POSIX); exact semantics are platform-dependent. A private temporary directory reduces exposure to other local users, but do not put secrets in a location with untrusted parent-directory permissions or assume secure deletion: unlinking a file does not reliably erase data from storage media or snapshots.

```python
from pathlib import Path
import shutil
import tempfile

# NamedTemporaryFile owns and cleans up its file by default.
with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".txt") as stream:
    stream.write("temporary report")
    stream.seek(0)
    print(stream.read())

# mkdtemp is lower-level: explicitly remove the directory when finished.
work_dir = Path(tempfile.mkdtemp(prefix="work-"))
try:
    (work_dir / "part.bin").write_bytes(b"chunk")
finally:
    shutil.rmtree(work_dir)
```

Output:

```text
temporary report
```

When another process or library must reopen a named temporary file, close it first where necessary. On Windows, an open handle may prevent reopening or deleting the file depending on sharing flags; do not assume POSIX unlink/reopen behavior is portable.

## 5. Beginner: ZIP and TAR basics

### 5.1 ZIP: create, list, read, and extract trusted data

```python
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    source = root / "events.csv"
    source.write_text("id\n1\n2\n", encoding="utf-8")
    archive = root / "events.zip"

    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=6) as zf:
        zf.write(source, arcname="events.csv")

    with ZipFile(archive) as zf:
        print(zf.namelist())
        print(zf.read("events.csv").decode("utf-8").strip().splitlines())
```

Output:

```text
['events.csv']
['id', '1', '2']
```

`ZipFile.read()` returns the entire member as bytes, so use it only when the member comfortably fits in memory. `ZipFile.open(member)` returns a file-like object and is preferable for large members.

### 5.2 TAR: create, list, and read

```python
from pathlib import Path
import tarfile
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    source = root / "record.txt"
    source.write_text("record-7\n", encoding="utf-8")
    archive = root / "records.tar.gz"

    with tarfile.open(archive, "w:gz") as tf:
        tf.add(source, arcname="record.txt")
    with tarfile.open(archive, "r:gz") as tf:
        print(tf.getnames())
        member = tf.extractfile("record.txt")
        assert member is not None
        with member:
            print(member.read().decode("utf-8").strip())
```

Output:

```text
['record.txt']
record-7
```

TAR preserves filesystem metadata such as member type, mode, ownership fields, and links in the archive format. That makes extraction policy especially important. For large TAR members, stream from `extractfile()` in chunks rather than calling `.read()` without a size.

### 5.3 Read a ZIP member without extracting it

```python
from zipfile import ZipFile

with ZipFile("dataset.zip") as archive:
    with archive.open("large/part-000.csv", "r") as member:
        for line in member:
            # Binary lines; decode explicitly if text processing is needed.
            process_line = line.decode("utf-8").rstrip("\r\n")
            print(process_line)
```

This example assumes `dataset.zip` contains the named member and that `process_line` is a placeholder for downstream processing. Iteration keeps memory bounded by line/member buffering rather than loading the entire member. For a binary format or a single enormous line, use bounded `.read(size)` chunks instead. Reading a member verifies its CRC when the stream reaches the end, but CRC is not a cryptographic authenticity check.

## 6. Intermediate: compression and archive streaming

### 6.1 ZIP compression

- `ZIP_STORED`: no compression; fast and useful for already-compressed data.
- `ZIP_DEFLATED`: widely supported general-purpose compression.
- `ZIP_BZIP2` and `ZIP_LZMA`: supported by Python's `zipfile`, but compatibility with other tools may be lower.
- `compresslevel` controls the codec's compression effort where supported. Higher compression can cost CPU and time and may not materially reduce already-compressed CSV/Parquet/media data.

Python 3.14 adds `ZIP_ZSTANDARD` support. Do not use it if archives must be readable by older Python versions or external tools that lack Zstandard support. Choose codec based on the consumer compatibility contract, not only local size.

### 6.2 TAR modes and version notes

Common modes include `w` (uncompressed write), `w:gz`, `w:bz2`, `w:xz`, and corresponding read modes such as `r:gz`. `r|gz` is a streaming mode for sequential reading; random access and member lookup behavior differ from seekable modes.

Python 3.14 adds Zstandard TAR support (`w:zst`, `r:zst`) using the standard library's Zstandard support. This is **not available in Python 3.12**. For a Python 3.12+ lesson, keep `w:gz` and `w:xz` as baseline examples and feature-gate 3.14-only behavior. Archive format support and compression-library availability can affect portability.

### 6.3 Stream copy and checksums

`shutil.copyfileobj(src, dst, length=...)` copies file-like objects. A positive `length` is a buffer size for each copy operation; it does not impose a total byte limit. Choose a moderate buffer (for example, 1 MiB) for large sequential copies and benchmark on the real storage medium.

```python
import hashlib
import shutil
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def copy_and_verify(source: Path, destination: Path) -> str:
    with source.open("rb") as src, destination.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
        dst.flush()
    source_hash = sha256_file(source)
    destination_hash = sha256_file(destination)
    if source_hash != destination_hash:
        raise OSError("checksum mismatch after copy")
    return destination_hash
```

This function overwrites/truncates `destination` before the checksum is known; it is not atomic. Production code should copy to a destination-side temporary file, verify it, then `os.replace()` the final path. Hash equality detects accidental corruption relative to the source observed during hashing; it does not prove authenticity if an attacker controls both files or the expected hash.

For progress reporting, count bytes copied and report periodically. Do not print per chunk for very large files; logging every chunk can dominate runtime. `shutil` may use platform fast-copy syscalls internally, so a Python loop is not automatically faster. `os.sendfile()` is platform- and descriptor-specific and is not a universal replacement for `shutil.copyfile()`.

## 7. Intermediate: atomic file replacement

An atomic write generally means: create a temporary file beside the destination, write all bytes, flush Python buffers, `fsync()` the file, close it, and `os.replace()` it over the destination. Keeping the temporary file in the same directory normally keeps the rename on the same filesystem. If the temp file is on another filesystem, `os.replace()` can fail with a cross-device error.

```python
from pathlib import Path
import os
import tempfile


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Atomically replace path with data on a trusted local filesystem."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temp_path = Path(temp_name)
    fd_owned = True
    try:
        with os.fdopen(fd, "wb") as stream:
            fd_owned = False  # fdopen owns and closes the descriptor now.
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
        # On POSIX, syncing the directory can improve rename durability.
        # This is platform-specific and is not attempted here.
    except BaseException as original_error:
        if fd_owned:
            try:
                os.close(fd)
            except OSError as cleanup_error:
                original_error.add_note(f"Could not close temporary descriptor: {cleanup_error!r}")
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass
        except OSError as cleanup_error:
            # Preserve the write/replace exception as the primary failure.
            original_error.add_note(f"Could not remove temporary file {temp_path}: {cleanup_error!r}")
        raise
```

**Guarantees and limits:** on filesystems where replacement is atomic, readers see the old or new file name binding, not a partially written destination. The temporary file is created in the target directory, and the descriptor is closed on both success and failure. If the write, flush, sync, or replace fails, the function re-raises and attempts to remove the temp file. A process crash or power loss can still leave a temp file, and durable rename semantics vary by OS/filesystem. A stronger POSIX durability protocol may open and `fsync()` the parent directory after replacement; portable directory syncing is not guaranteed.

`os.replace()` replaces an existing destination where permitted and may fail due to Windows file locks, permissions, or sharing modes. The new file inherits the temporary file's mode (often restrictive), not necessarily the previous destination's permissions, ACLs, or owner. If permissions/metadata are part of the contract, set them deliberately and test on target platforms. The function assumes the parent directory is trusted; it is not hardened against an attacker who can replace path components concurrently.

### Failure cleanup test

A useful unit test injects failure at the write/replace boundary or patches `os.replace`; it should assert the previous destination remains intact and temporary artifacts are cleaned. Do not test atomicity by racing many processes on a developer laptop and treating one successful run as proof.

## 8. Intermediate: `ExitStack` and multi-resource lifetimes

`contextlib.ExitStack` is useful when the number of resources is dynamic or resources are acquired in a loop. It unwinds successfully entered context managers in reverse order when an exception occurs.

```python
from contextlib import ExitStack
from pathlib import Path
from zipfile import ZipFile


def list_archive_members(paths: list[Path]) -> list[list[str]]:
    with ExitStack() as stack:
        archives = [stack.enter_context(ZipFile(path)) for path in paths]
        # Build plain data while handles are open; handles close on scope exit.
        return [archive.namelist() for archive in archives]
```

The intentionally empty return illustrates a common boundary: resources opened inside the stack are closed when the `with` block exits. In real code, process them inside the block or transfer ownership explicitly; do not return closed handles. A clearer reusable pattern is to pass a callback into a function that owns the stack, or have the caller provide the stack.

## 9. Advanced security: archive extraction threat model

An archive can be malicious even when its file extension looks ordinary. Assume an untrusted archive may contain:

- **Path traversal / ZIP Slip:** names like `../../outside.txt`, absolute paths, drive-qualified paths, or platform-specific separators.
- **Links and special entries:** TAR can represent symlinks, hard links, devices, FIFOs, and other member types. A link can redirect later writes outside the intended tree.
- **Duplicate/colliding names:** repeated names, case-folding collisions on some filesystems, or file/directory conflicts.
- **Resource exhaustion:** many tiny members, huge declared sizes, high compression ratios, or a member whose decompressed stream is much larger than expected.
- **Malformed or truncated streams:** parse errors, CRC failures, unsupported compression, or I/O errors.

The destination should be a new, private directory under a trusted parent. Validate archive metadata **before** writing and enforce actual byte limits while streaming. Never trust declared sizes alone. Avoid extracting directly into a live application directory.

### 9.1 Defensive ZIP extraction with bounded resources

This implementation is intentionally conservative:

- The destination must not already exist.
- The staging directory is created beside the destination so final rename stays on the same filesystem.
- Absolute paths, `..`, backslashes, NULs, drive-qualified names, duplicate normalized paths, symlinks, and non-regular/non-directory entries are rejected.
- Member count, per-member uncompressed size, total uncompressed bytes, and compression ratio are bounded.
- Actual bytes written are counted; declared-size mismatch and CRC/stream errors fail the operation.
- The destination becomes visible only after successful extraction and a directory rename.

```python
from __future__ import annotations

from pathlib import Path, PurePosixPath
import math
import os
import shutil
import stat
import tempfile
import unicodedata
import re
from zipfile import ZipFile, ZipInfo


class UnsafeArchiveError(ValueError):
    """The archive violates the extraction policy."""


_WINDOWS_RESERVED = re.compile(
    r"(?i)^(?:CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|CLOCK\$|"
    r"COM[1-9¹²³]|LPT[1-9¹²³])(?:\..*)?$"
)
_WINDOWS_FORBIDDEN = set('<>:"|?*')


def _safe_zip_member_path(name: str) -> PurePosixPath:
    """Validate a ZIP name conservatively for common Windows/POSIX targets."""
    if not name or "\x00" in name or "\\" in name:
        raise UnsafeArchiveError(f"invalid ZIP member name: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute():
        raise UnsafeArchiveError(f"absolute member path: {name!r}")

    # Inspect raw components before PurePosixPath normalizes repeated slashes
    # or dot segments. A single final empty component represents a directory.
    components = name.split("/")
    if name.endswith("/"):
        components.pop()
    if not components or any(part in ("", ".", "..") for part in components):
        raise UnsafeArchiveError(f"invalid or traversing path component: {name!r}")
    for part in components:
        if any(ord(char) < 32 or ord(char) == 127 for char in part):
            raise UnsafeArchiveError(f"control character in member path: {name!r}")
        if any(char in _WINDOWS_FORBIDDEN for char in part):
            raise UnsafeArchiveError(f"non-portable character in member path: {name!r}")
        # Win32 commonly strips trailing dots/spaces and reserves device names,
        # even when followed by an extension. Reject them to avoid aliases.
        if part.endswith((".", " ")) or _WINDOWS_RESERVED.fullmatch(part):
            raise UnsafeArchiveError(f"non-portable/reserved path component: {name!r}")
    return path


def safe_extract_zip(
    archive_path: Path,
    destination: Path,
    *,
    max_members: int = 10_000,
    max_member_bytes: int = 256 * 1024 * 1024,
    max_total_bytes: int = 1024 * 1024 * 1024,
    max_compression_ratio: float = 200.0,
    chunk_size: int = 1024 * 1024,
) -> None:
    """Extract a restricted ZIP into a new destination directory.

    Assumes destination.parent is trusted and not writable by an attacker.
    This is a conservative application policy, not a sandbox against all OS
    races or parser vulnerabilities.
    """
    archive_path = Path(archive_path)
    destination = Path(destination)
    integer_limits = (max_members, max_member_bytes, max_total_bytes, chunk_size)
    if any(type(value) is not int or value <= 0 for value in integer_limits):
        raise ValueError("count, byte, and chunk limits must be positive integers")
    if not math.isfinite(max_compression_ratio) or max_compression_ratio <= 0:
        raise ValueError("max_compression_ratio must be a finite positive number")
    if not destination.parent.is_dir():
        raise FileNotFoundError(destination.parent)
    if destination.exists() or destination.is_symlink():
        # is_symlink() also catches a dangling destination symlink.
        raise FileExistsError(destination)

    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.extract-",
                                    dir=destination.parent))
    published = False
    try:
        with ZipFile(archive_path, "r") as archive:
            infos = archive.infolist()
            if len(infos) > max_members:
                raise UnsafeArchiveError("too many archive members")

            seen: dict[str, bool] = {}  # case-folded path -> is directory
            planned: list[tuple[ZipInfo, PurePosixPath, bool]] = []
            declared_total = 0
            for info in infos:
                relative = _safe_zip_member_path(info.filename)
                normalized = relative.as_posix().rstrip("/")
                # Normalize Unicode before case-folding so canonically
                # equivalent names collide under common filesystem rules.
                collision_key = "/".join(
                    unicodedata.normalize("NFC", part).casefold()
                    for part in relative.parts
                )

                mode = (info.external_attr >> 16) & 0xFFFF
                file_type = stat.S_IFMT(mode)
                is_dir = info.is_dir()
                if file_type == stat.S_IFDIR and not is_dir:
                    raise UnsafeArchiveError("directory metadata without directory name")
                if is_dir and file_type == stat.S_IFREG:
                    raise UnsafeArchiveError("member type/name conflict")
                if is_dir and info.file_size != 0:
                    raise UnsafeArchiveError("directory member contains data")
                if collision_key in seen:
                    raise UnsafeArchiveError(f"duplicate/colliding member: {info.filename!r}")
                components = collision_key.split("/")
                for end in range(1, len(components)):
                    ancestor = "/".join(components[:end])
                    if ancestor in seen and not seen[ancestor]:
                        raise UnsafeArchiveError(f"file/directory path conflict: {info.filename!r}")
                if not is_dir and any(existing.startswith(collision_key + "/") for existing in seen):
                    raise UnsafeArchiveError(f"file/directory path conflict: {info.filename!r}")
                seen[collision_key] = is_dir
                if file_type == stat.S_IFLNK:
                    raise UnsafeArchiveError(f"symlink member not allowed: {info.filename!r}")
                if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise UnsafeArchiveError(f"special file not allowed: {info.filename!r}")
                if info.file_size < 0 or info.file_size > max_member_bytes:
                    raise UnsafeArchiveError(f"member too large: {info.filename!r}")
                declared_total += info.file_size
                if declared_total > max_total_bytes:
                    raise UnsafeArchiveError("declared total size exceeds limit")
                if info.file_size and info.compress_size == 0:
                    raise UnsafeArchiveError("non-empty member has zero compressed size")
                if info.compress_size > 0:
                    ratio = info.file_size / info.compress_size
                    if ratio > max_compression_ratio:
                        raise UnsafeArchiveError(f"compression ratio too high: {info.filename!r}")
                planned.append((info, relative, is_dir))

            actual_total = 0
            for info, relative, is_dir in planned:
                target = staging.joinpath(*relative.parts)
                # All parent paths are under a newly created private staging tree.
                if is_dir:
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                written = 0
                with archive.open(info, "r") as src, target.open("xb") as dst:
                    while chunk := src.read(chunk_size):
                        written += len(chunk)
                        actual_total += len(chunk)
                        if written > max_member_bytes or actual_total > max_total_bytes:
                            raise UnsafeArchiveError("actual decompressed bytes exceed limit")
                        dst.write(chunk)
                if written != info.file_size:
                    raise UnsafeArchiveError(f"declared/actual size mismatch: {info.filename!r}")

        # destination must not exist; staging is a sibling on the same filesystem.
        os.replace(staging, destination)
        published = True
    except BaseException as original_error:
        if not published:
            try:
                shutil.rmtree(staging)
            except FileNotFoundError:
                pass
            except OSError as cleanup_error:
                # Do not hide the archive/write failure with a cleanup failure.
                original_error.add_note(
                    f"Could not remove staging directory {staging}: {cleanup_error!r}"
                )
        raise
```

**Important limitations and production notes:**

1. `max_compression_ratio` is a heuristic, not a complete ZIP-bomb defense. Limits should reflect workload expectations; decompression CPU/time limits may also be needed. A strict wall-clock timeout is not safely implemented by a simple loop.
2. This implementation rejects case-insensitive name collisions even on case-sensitive filesystems to improve portability. It pre-validates duplicate paths and file-versus-directory ancestor conflicts. It does not pre-validate every platform-specific reserved filename or Unicode-normalization collision; test and tighten policy for the target platform.
3. The name policy rejects Windows-reserved device names, trailing dots/spaces, control characters, and common Windows-forbidden characters, and it checks normalized/case-folded collisions. This is deliberately conservative, but it still does not model every filesystem's normalization, reserved-name, or path-length rules.
4. A malicious actor with write access to `destination.parent` could race directory operations. A private trusted parent and private staging directory are assumptions, not optional details. Path checks alone do not defeat all symlink/TOCTOU attacks on hostile filesystems.
5. ZIP metadata and decompressor implementations can themselves have bugs. Keep Python patched and run extraction with OS/container resource limits for high-risk workloads. `ZipFile` must parse the central directory before this function can count entries, so `max_members` does not cap all parser/metadata memory use.
6. The code deliberately does not preserve archive permissions or links; it writes regular files and directories with local default permissions.

### 9.2 TAR extraction filters and version differences

TAR requires special care because it represents links and special files. Python 3.12 introduced extraction filters. Use `filter="data"` when extracting untrusted-but-allowed TAR content on Python 3.12+, and still apply your own resource/member policy. Python 3.14 changes the default filter to `data`; **do not rely on the default when supporting Python 3.12 and 3.13**. Pass it explicitly.

```python
from pathlib import Path
import tarfile


def extract_tar_with_data_filter(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            archive.extractall(path=destination, filter="data")  # Python 3.12+
    except BaseException as original_error:
        # destination was created exclusively for this extraction
        import shutil
        try:
            shutil.rmtree(destination)
        except FileNotFoundError:
            pass
        except OSError as cleanup_error:
            original_error.add_note(
                f"Could not remove partial extraction {destination}: {cleanup_error!r}"
            )
        raise
```

The `data` filter is an important safety boundary: it rejects or modifies dangerous members such as paths escaping the destination and unsafe links/special entries. It is not a total denial-of-service limit; it does not replace limits on member count, total extracted bytes, CPU, or disk usage. For untrusted TAR archives, preflight `getmembers()` against a member-count and declared-size policy, then stream/extract under actual byte limits. Note that `getmembers()` materializes metadata for all members, so cap archive size/member count and consider streaming modes for very large archives. TAR extraction filters are not a substitute for a trusted destination parent or patched Python.

Python 3.14 adds Zstandard TAR modes such as `w:zst` and `r:zst`. These are not baseline Python 3.12 features. Check the exact interpreter version and consumer compatibility before producing them.

## 10. ZIP bombs and resource limits

A ZIP bomb exploits a small compressed archive that expands to huge output. Check:

- Member count and path count.
- Declared `file_size` per member and declared total.
- Compression ratio (`file_size / compress_size`, guarding zero compressed size).
- Actual bytes emitted during decompression.
- Disk capacity and process-level time/CPU/memory limits.

Do not rely solely on declared metadata; it can be malicious or inconsistent. Do not assume compression ratio alone identifies every bomb. Extraction into a staging directory prevents partially extracted output from being published, but it still consumes temporary disk space while work proceeds. Reserve capacity and reject input before extraction if declared sizes already exceed policy.

## 11. Common failures and cross-platform behavior

| Failure | Why it happens | Defensive response |
|---|---|---|
| `os.replace()` cross-device error | Temp file is on another filesystem | Create temp file in target parent |
| Temp file left after failure | Cleanup path missed or process killed | `try/finally`; reconcile stale temp files at startup |
| `PermissionError` during cleanup | Open handles, ACLs, read-only files, Windows locks | Close all handles; retry only with bounded, observable policy |
| ZIP/TAR extraction partially writes | Corrupt archive or disk full | Extract to private staging; publish only on success |
| Windows cannot reopen temp file | Sharing/locking semantics differ | Close first or use suitable `NamedTemporaryFile` options |
| Path collision on Windows/macOS | Case-folding or reserved names | Reject collisions; test on target filesystems |
| Long path failures | Platform/API configuration | Test real deployment path depth; avoid assuming all APIs support arbitrary length |
| Copy succeeds but data differs | I/O failure or source changed during copy | Compare size/hash against a stable source snapshot |
| Cleanup deletes wrong tree | Bad path derivation or symlink race | Private temp roots; validate exact target; never use broad string-prefix checks |

If a source file can change while copying, hashing the source only after the copy may compare two different source versions. Use an immutable snapshot, file lock where appropriate, or hash while copying and then validate the source consistency contract.

## 12. Idempotent file-processing workflow

A repeatable ingestion job should define:

1. **Input identity:** path plus expected size/hash or upstream batch identifier.
2. **Staging:** write/copy into a unique temporary location on the destination filesystem.
3. **Validation:** schema, expected record count, size, hash, archive policy, and output checks.
4. **Publish:** atomic replacement or rename of the completed artifact.
5. **Checkpoint:** persist the processed input identity only after publication succeeds.
6. **Recovery:** on restart, remove or quarantine stale staging artifacts and reconcile output/checkpoint mismatches.

Atomic replacement avoids exposing partial files, but it does not make a multi-file update atomic. If a job publishes multiple outputs, use a manifest/commit marker, versioned directory plus atomic pointer/rename, or a transactional store for the commit decision. Define whether reprocessing an identical input is a no-op, a verified replacement, or an error.

## 13. Testing with pytest and `tmp_path`

Use `tmp_path` so tests never write into real production paths. Test normal cases, boundaries, malformed archives, traversal names, cleanup after failure, and replacement behavior. Avoid tests that depend on exact permission bits across all platforms unless platform-gated.

```python
# test_file_ops.py
from pathlib import Path
import zipfile
import pytest

# Import these from your lesson module in a real project:
# from file_ops import atomic_write_bytes, safe_extract_zip, UnsafeArchiveError


def test_atomic_write_replaces_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "result.bin"
    target.write_bytes(b"old")
    atomic_write_bytes(target, b"new")
    assert target.read_bytes() == b"new"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["result.bin"]


def test_safe_zip_extracts_normal_member(tmp_path: Path) -> None:
    archive = tmp_path / "ok.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("nested/data.txt", b"hello")
    destination = tmp_path / "out"
    safe_extract_zip(archive, destination)
    assert (destination / "nested" / "data.txt").read_bytes() == b"hello"


def test_safe_zip_rejects_traversal_and_cleans_staging(tmp_path: Path) -> None:
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../escape.txt", b"bad")
    destination = tmp_path / "out"
    with pytest.raises(UnsafeArchiveError):
        safe_extract_zip(archive, destination)
    assert not destination.exists()
    assert not (tmp_path / "escape.txt").exists()
    assert not list(tmp_path.glob(".out.extract-*"))


def test_safe_zip_enforces_declared_size_limit(tmp_path: Path) -> None:
    archive = tmp_path / "large.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("large.bin", b"x" * 100)
    with pytest.raises(UnsafeArchiveError):
        safe_extract_zip(archive, tmp_path / "out", max_member_bytes=10)


def test_member_count_and_total_size_limits(tmp_path: Path) -> None:
    archive = tmp_path / "limits.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("one.txt", b"123")
        zf.writestr("two.txt", b"456")
    with pytest.raises(UnsafeArchiveError, match="too many"):
        safe_extract_zip(archive, tmp_path / "count-limited", max_members=1)
    with pytest.raises(UnsafeArchiveError, match="total size"):
        safe_extract_zip(archive, tmp_path / "size-limited", max_total_bytes=5)
    assert not list(tmp_path.glob(".*.extract-*"))


def test_casefold_collision_and_file_directory_conflict_are_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "collision.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("Data.txt", b"one")
        zf.writestr("data.TXT", b"two")
    with pytest.raises(UnsafeArchiveError, match="duplicate/colliding"):
        safe_extract_zip(archive, tmp_path / "collision-out")

    archive = tmp_path / "conflict.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("node", b"file")
        zf.writestr("node/child.txt", b"child")
    with pytest.raises(UnsafeArchiveError, match="conflict"):
        safe_extract_zip(archive, tmp_path / "conflict-out")
    assert not list(tmp_path.glob(".*.extract-*"))


def test_compression_ratio_limit_is_enforced(tmp_path: Path) -> None:
    archive = tmp_path / "ratio.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("repeat.txt", b"A" * 10_000)
    with pytest.raises(UnsafeArchiveError, match="compression ratio"):
        safe_extract_zip(archive, tmp_path / "out", max_compression_ratio=2.0)
    assert not (tmp_path / "out").exists()
    assert not list(tmp_path.glob(".out.extract-*"))


def test_inconsistent_directory_metadata_is_rejected(tmp_path: Path) -> None:
    import stat
    archive = tmp_path / "bad-dir.zip"
    info = zipfile.ZipInfo("directory-without-slash")
    info.create_system = 3
    info.external_attr = (stat.S_IFDIR | 0o755) << 16
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(info, b"")
    with pytest.raises(UnsafeArchiveError, match="directory metadata"):
        safe_extract_zip(archive, tmp_path / "out")
    assert not (tmp_path / "out").exists()
    assert not list(tmp_path.glob(".out.extract-*"))


def test_invalid_limits_are_rejected_before_staging(tmp_path: Path) -> None:
    archive = tmp_path / "empty.zip"
    with zipfile.ZipFile(archive, "w"):
        pass
    with pytest.raises(ValueError):
        safe_extract_zip(archive, tmp_path / "out", max_members=0)
    assert not list(tmp_path.glob(".out.extract-*"))


def test_malformed_zip_fails_without_publishing(tmp_path: Path) -> None:
    archive = tmp_path / "broken.zip"
    archive.write_bytes(b"not a zip file")
    destination = tmp_path / "out"
    with pytest.raises(zipfile.BadZipFile):
        safe_extract_zip(archive, destination)
    assert not destination.exists()
    assert not list(tmp_path.glob(".out.extract-*"))


def test_crc_failure_during_streaming_cleans_staging(tmp_path: Path) -> None:
    archive = tmp_path / "crc-broken.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("payload.bin", b"payload-marker")
    raw = archive.read_bytes()
    assert raw.count(b"payload-marker") == 1
    archive.write_bytes(raw.replace(b"payload-marker", b"PAYLOAD-marker"))
    destination = tmp_path / "out"
    with pytest.raises(zipfile.BadZipFile):
        safe_extract_zip(archive, destination)
    assert not destination.exists()
    assert not list(tmp_path.glob(".out.extract-*"))


def test_windows_alias_and_traversal_components_are_rejected(tmp_path: Path) -> None:
    for member_name in ("../escape.txt", "folder/.. /escape.txt", "CON.txt", "trailing./x.txt"):
        archive = tmp_path / "bad.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr(member_name, b"bad")
        with pytest.raises(UnsafeArchiveError):
            safe_extract_zip(archive, tmp_path / "out")
        assert not (tmp_path / "escape.txt").exists()
        assert not list(tmp_path.glob(".out.extract-*"))
        archive.unlink()


def test_zip_symlink_member_is_rejected(tmp_path: Path) -> None:
    import stat
    archive = tmp_path / "symlink.zip"
    info = zipfile.ZipInfo("link")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(info, "../../outside")
    with pytest.raises(UnsafeArchiveError, match="symlink"):
        safe_extract_zip(archive, tmp_path / "out")
    assert not (tmp_path / "outside").exists()
    assert not list(tmp_path.glob(".out.extract-*"))
```

These tests assume `atomic_write_bytes`, `safe_extract_zip`, and `UnsafeArchiveError` are in an importable module. Remove the unused `os` import if linting is strict. In a real project, test malformed streams that fail after the central directory is parsed, not only a file that is immediately rejected as a non-ZIP. A traversal test should also assert no path outside the destination is created.

### TAR extraction-filter tests (Python 3.12+)

The standard-library `data` filter blocks traversal, unsafe links, and special files, but callers still own cleanup and resource limits. These tests exercise the lesson helper's failure cleanup. In a real test module, import `extract_tar_with_data_filter` from the module where you placed it.

```python
from pathlib import Path
import io
import tarfile
import pytest

# from file_ops import extract_tar_with_data_filter


def test_tar_data_filter_extracts_regular_file(tmp_path: Path) -> None:
    archive = tmp_path / "regular.tar.gz"
    with tarfile.open(archive, "w:gz") as tf:
        info = tarfile.TarInfo("nested/record.txt")
        payload = b"safe data"
        info.size = len(payload)
        tf.addfile(info, io.BytesIO(payload))
    destination = tmp_path / "out"
    extract_tar_with_data_filter(archive, destination)
    assert (destination / "nested" / "record.txt").read_bytes() == b"safe data"


def test_tar_data_filter_rejects_traversal_and_cleans_up(tmp_path: Path) -> None:
    archive = tmp_path / "traversal.tar.gz"
    with tarfile.open(archive, "w:gz") as tf:
        info = tarfile.TarInfo("../escape.txt")
        info.size = 4
        tf.addfile(info, io.BytesIO(b"evil"))
    destination = tmp_path / "out"
    with pytest.raises(tarfile.FilterError):
        extract_tar_with_data_filter(archive, destination)
    assert not destination.exists()
    assert not (tmp_path / "escape.txt").exists()


def test_tar_data_filter_rejects_links_and_special_files(tmp_path: Path) -> None:
    for label, member_type, linkname in (
        ("link", tarfile.SYMTYPE, "../../outside"),
        ("fifo", tarfile.FIFOTYPE, ""),
    ):
        archive = tmp_path / f"{label}.tar.gz"
        with tarfile.open(archive, "w:gz") as tf:
            info = tarfile.TarInfo(label)
            info.type = member_type
            info.linkname = linkname
            tf.addfile(info)
        destination = tmp_path / f"{label}-out"
        with pytest.raises(tarfile.FilterError):
            extract_tar_with_data_filter(archive, destination)
        assert not destination.exists()
```

These are local-runtime tests, not a proof that TAR extraction is safe against resource exhaustion or concurrent filesystem attackers. They require a Python version with extraction filters; this lesson targets Python 3.12+ and passes `filter="data"` explicitly.

### Additional failure-cleanup test for atomic replacement

```python
from pathlib import Path
import pytest
import file_ops


def test_atomic_write_replace_failure_keeps_old_file_and_cleans_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "state.json"
    target.write_bytes(b"old")

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr(file_ops.os, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated replace failure"):
        file_ops.atomic_write_bytes(target, b"new")

    assert target.read_bytes() == b"old"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["state.json"]
```

Patching `file_ops.os.replace` changes the shared `os` module object in the process, so pytest restores it after the test. Use this style only in an isolated test. Test atomic-write failures before replacement and verify the old destination remains intact.

## 14. Practical implementation patterns

### Pattern A — copy a file with explicit metadata policy

```python
from pathlib import Path
import shutil


def copy_file(source: Path, destination: Path, *, preserve_metadata: bool = True) -> None:
    source = Path(source)
    destination = Path(destination)
    if not source.is_file():
        raise FileNotFoundError(f"not a regular source file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if preserve_metadata:
        shutil.copy2(source, destination)
    else:
        shutil.copyfile(source, destination)
```

This helper makes the metadata policy explicit but does not provide atomic destination replacement or source snapshot consistency. Use a staging file and verification for production delivery.

### Pattern B — temporary work area with deterministic cleanup

```python
from pathlib import Path
import tempfile


def build_intermediate(source: Path) -> bytes:
    with tempfile.TemporaryDirectory(prefix="transform-") as temp_dir:
        work = Path(temp_dir)
        local_copy = work / source.name
        local_copy.write_bytes(source.read_bytes())  # Fine for small files only.
        # Replace read_bytes/write_bytes with shutil.copy2 for large files.
        return local_copy.read_bytes()
```

The return value is materialized in memory; this is not suitable for a huge file. For large files, write the result to a caller-supplied destination or consume it before leaving the temporary-directory context.

### Pattern C — archive member stream with bounded chunks

```python
from zipfile import ZipFile


def copy_zip_member(archive_path: str, member_name: str, output_path: str) -> int:
    total = 0
    with ZipFile(archive_path) as archive, archive.open(member_name) as src, open(output_path, "wb") as dst:
        while chunk := src.read(1024 * 1024):
            dst.write(chunk)
            total += len(chunk)
    return total
```

This copies without loading the member in full, but it does not validate the member path or limit total output. Do not use it as an untrusted-archive extractor without adding policy checks and staging/cleanup.

## 15. Mini-project: reliable archive ingestion

**Goal:** implement a small, repeatable ingestion utility that receives a ZIP of CSV/text files, extracts only permitted regular files into a new staging directory, verifies each output's SHA-256, and publishes the directory only after all validation succeeds.

### Requirements

1. Inputs: archive path, destination path, max members, per-member size, total uncompressed size, and allowed suffixes (for example `.csv`, `.txt`).
2. Reject an existing destination rather than silently merging untrusted content.
3. Validate names and member types before writing. Reuse the defensive ZIP policy above; do not duplicate a weaker path check.
4. Stream members in bounded chunks, enforce actual bytes, and calculate SHA-256 as bytes are written.
5. Write a manifest in staging containing relative path, byte count, and digest. The manifest itself must not be sourced from an archive member with the same reserved name.
6. Publish by renaming the completed staging directory on the same filesystem.
7. On any exception, close archive handles and remove the uncommitted staging directory.
8. Re-running with the same archive and destination must follow an explicit policy: reject existing destination, verify-and-skip, or publish a versioned output. Do not quietly append duplicate data.

### Acceptance tests

- Normal ZIP with two permitted files publishes expected bytes and manifest hashes.
- Empty ZIP produces a documented result (either an empty published directory or a deliberate validation error).
- `../escape.txt`, absolute names, backslash traversal, duplicate/case-colliding names, and symlink entries are rejected.
- Member-count, per-member-size, total-size, and compression-ratio limits are enforced.
- Corrupt or truncated archives do not publish a destination and clean staging.
- Simulated disk/write/replace failures preserve any pre-existing data and clean temporary artifacts.
- A second run follows the declared idempotency policy.

**Design note:** the `safe_extract_zip()` example is a teaching baseline, not a drop-in high-assurance sandbox. For hostile multi-tenant workloads, combine a maintained Python runtime, OS-level resource isolation, restricted filesystem permissions, and a more exhaustive archive policy. Security is a system property, not a single path-validation function.

## 16. Hands-on exercises

1. Copy a file with `copyfile`, `copy`, and `copy2`; inspect `stat()` timestamps/mode where supported and explain why results differ by platform.
2. Copy a tree while excluding `*.tmp` and `__pycache__`; rerun with `dirs_exist_ok=True` and document collision behavior.
3. Implement an atomic text writer that encodes UTF-8, then test a simulated `os.replace()` failure.
4. Build a ZIP containing a 100 MB generated member and process it with `ZipFile.open()` in chunks without using `read()` on the full member.
5. Add a maximum member count and actual total byte limit to the ZIP extraction function.
6. Create a TAR with a symlink member and compare explicit `filter="data"` behavior on Python 3.12+.
7. Add checksum verification to a large-file copy and test what happens if the source changes during processing.
8. Write a cleanup routine for stale staging directories that only removes artifacts matching a strict naming and age policy under a trusted work root.

## 17. Self-check questions with answers

**1. Why should an atomic-write temporary file live in the destination directory?**

Because replacement is generally atomic only within the same filesystem. A temporary file elsewhere may be on another mount, causing `os.replace()` to fail or forcing a non-atomic copy strategy.

**2. Why is `copy2()` not a complete metadata clone?**

It attempts to preserve standard metadata such as timestamps and mode, but ACLs, ownership, extended attributes, alternate streams, and other platform-specific metadata are not universally preserved.

**3. Why is `shutil.move()` not necessarily atomic?**

It may use a rename on the same filesystem, but across filesystems it can copy then delete. A failure can leave both source and partial destination or leave source removal incomplete.

**4. Why is `tempfile.mktemp()` unsafe?**

It only proposes a name. Another process can create that path before the caller opens it. `mkstemp()` and other creation APIs combine name selection with resource creation.

**5. What is ZIP Slip?**

A path traversal attack in which archive member names escape the extraction root, for example `../../outside.txt`. Reject unsafe names and extract only into a private staging directory; also consider links, collisions, and resource exhaustion.

**6. Is checking `ZipInfo.file_size` enough to stop a ZIP bomb?**

No. Metadata can be inconsistent or malicious. Enforce declared limits before extraction and actual byte limits while decompressing; consider CPU/time and disk constraints as well.

**7. What does TAR `filter="data"` protect against, and what does it not solve?**

It restricts dangerous paths, links, and special-file behavior during extraction. It does not impose complete size/time limits, eliminate every filesystem race, or replace patched runtimes and trusted destination permissions.

**8. Does `flush()` make an atomic write durable?**

No. `flush()` moves Python's buffered bytes toward the OS. `os.fsync()` requests syncing the file descriptor; directory metadata syncing may also be needed for stronger rename durability, and guarantees vary by platform and storage.

**9. Why extract into staging and publish only after validation?**

It prevents consumers from observing an incomplete output tree. Failed work can be removed without corrupting the previously published result. Staging still consumes disk and does not sandbox a malicious parser.

**10. How do you make a file job idempotent?**

Define input identity, stage and validate output, publish deterministically, and record a checkpoint only after success. Re-runs must have a documented skip/replace/version policy. Atomic file replacement alone does not make multiple outputs or external side effects transactional.

## 18. Final mastery checklist

- [ ] I can choose between `copyfile`, `copy`, and `copy2` and explain metadata limitations.
- [ ] I understand `copytree`, ignore patterns, merge behavior, `move`, and destructive `rmtree` risks.
- [ ] I use `TemporaryDirectory`/`NamedTemporaryFile` and low-level temp APIs with correct ownership and cleanup.
- [ ] I can create and inspect ZIP/TAR archives and stream members without loading them fully.
- [ ] I can explain compression compatibility and Python 3.14 Zstandard support accurately.
- [ ] I can implement atomic replacement and distinguish visibility from durability.
- [ ] I validate archive paths, member types, collisions, sizes, and actual decompressed bytes.
- [ ] I understand TAR extraction filters and Python 3.12/3.13/3.14 differences.
- [ ] I test malformed archives, traversal attempts, limits, and failure cleanup with `tmp_path`.
- [ ] I design staging, verification, publication, and recovery as an idempotent workflow.

## 19. Quick reference

| Task | Preferred starting point | Critical caveat |
|---|---|---|
| Copy contents only | `shutil.copyfile()` | Does not preserve mode metadata |
| Copy mode and contents | `shutil.copy()` | Not a full metadata clone |
| Copy with common metadata | `shutil.copy2()` | Metadata preservation is best-effort |
| Copy a directory tree | `shutil.copytree()` | Partial tree can remain after failure |
| Merge into existing tree | `copytree(..., dirs_exist_ok=True)` | Collisions can overwrite files |
| Move a path | `shutil.move()` | Cross-filesystem path may copy/delete |
| Remove tree | `shutil.rmtree()` | Destructive; validate exact target; `rmtree.avoids_symlink_attacks` reports whether this runtime/platform uses its symlink-attack-resistant implementation |
| Temporary workspace | `TemporaryDirectory()` | Cleanup is not secure erasure |
| Low-level temporary file | `mkstemp()` | Close fd and unlink on failure |
| Atomic file replacement | same-dir temp + `fsync` + `os.replace` | Durability and metadata are platform-dependent |
| ZIP member stream | `ZipFile.open()` | Add path/resource policy for untrusted archives |
| TAR extraction | `extractall(filter="data")` on 3.12+ | Add resource limits; explicit filter for 3.12/3.13 |
| Archive output | `ZipFile` / `tarfile.open()` | Codec compatibility varies by consumer |
| Large copy | `shutil.copyfileobj()` or `copyfile()` | Verify output; consider atomic staging |
| Integrity | Chunked SHA-256 | Hash proves equality to observed input, not authenticity |
| Tests | pytest `tmp_path` | Test failure paths and cleanup, not only happy paths |


## 20. Official documentation for follow-up

Use the documentation for the exact Python version deployed; security defaults can change between releases.

- [`shutil` — high-level file operations](https://docs.python.org/3.13/library/shutil.html): copy metadata, fast-copy behavior, cross-filesystem moves, and `rmtree.avoids_symlink_attacks`.
- [`tempfile` — temporary files and directories](https://docs.python.org/3.13/library/tempfile.html): secure creation, descriptor ownership, cleanup, and the `mktemp()` warning.
- [`zipfile` — ZIP archives](https://docs.python.org/3.13/library/zipfile.html): member streams, extraction behavior, and decompression pitfalls.
- [`tarfile` — TAR archives](https://docs.python.org/3.13/library/tarfile.html): extraction filters introduced in 3.12 and the `data` default in 3.14.
- [`os.replace` and filesystem operations](https://docs.python.org/3.13/library/os.html#os.replace): same-filesystem constraints and platform-dependent rename semantics.
