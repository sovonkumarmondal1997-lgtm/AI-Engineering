# 08 — `mmap` and Large Binary Files

> **Target:** Python 3.12+  
> **Scope:** Stage 1 — Programming & Computational Thinking, Module 14: Bytes, Binary Data and Advanced Text Processing.  
> **Platform note:** Examples use the standard library unless explicitly marked. `mmap`, file-locking, allocation, and memory-accounting behavior depends on the operating system, filesystem, Python build, and container runtime.

## Learning outcomes

By the end of this lesson, you should be able to:

- Map a non-empty file using `mmap.mmap(file.fileno(), length=0, access=mmap.ACCESS_READ)` and use slicing, `find`, `rfind`, `read`, `seek`, and `readline`.
- Close maps and release exported views in the right order; handle empty files without trying to map them.
- Explain demand paging, page cache, page faults, virtual address space, and resident memory without claiming that `mmap` eliminates I/O or memory use.
- Choose among buffered reads, `readinto`, and `mmap` based on access pattern and measured behavior.
- Explain `ACCESS_READ`, `ACCESS_WRITE`, `ACCESS_COPY`, `flush()`, resizing, and platform caveats.
- Parse bounded fixed-size records with `struct`, and understand the lifetime risks of `memoryview` and `numpy.frombuffer` views.
- Recognize operational risks from external truncation, concurrent mutation, network filesystems, sparse files, and container memory limits.
- Design a safer append-only binary log or indexed file with checksums and recovery from an incomplete tail.

## Prerequisites

You should already understand binary `bytes`, slicing, file modes (`rb`/`r+b`), basic `struct.pack`/`unpack`, context managers, exceptions, and temporary files. NumPy is introduced only as an optional consumer of memory-mapped arrays; this lesson does not teach NumPy or `struct` from scratch.

---

## 1. What memory mapping does

A memory map associates a file region with a process's virtual address space. Python can access the mapped region through a byte-sequence/file-like object. The operating system normally brings pages into physical memory when they are accessed and may retain file-backed pages in the page cache.

```python
from pathlib import Path
import mmap
import tempfile

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "events.log"
    path.write_bytes(b"INFO started\nERROR disk full\nINFO stopped\n")

    with path.open("rb") as f:
        if path.stat().st_size == 0:
            print("empty file: nothing to map")
        else:
            with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
                pos = mm.find(b"ERROR")
                print(pos, mm[pos:mm.find(b"\n", pos)])
                mm.seek(0)
                print(mm.readline().rstrip())
```

Expected output:

```text
13 b'ERROR disk full'
b'INFO started'
```

### Important constructor details

- `f.fileno()` supplies the operating-system file descriptor/handle for an already-open file.
- `length=0` means map the current file size. It does **not** mean “map an empty file successfully.” A zero-length mapping is not portable and normally fails; check size first.
- `access=mmap.ACCESS_READ` requests a read-only map. The file should be opened in binary read mode (`"rb"`).
- A mapping can be indexed and sliced, and supports methods such as `find`, `rfind`, `read`, `seek`, and `readline`. Slicing usually creates a new `bytes` object; it is not automatically zero-copy.
- The file object must remain valid while creating the map. Keep the file and map lifetimes explicit, even though a successful map may outlive the Python file object on some systems.
- Use nested context managers so the map closes before the file object exits.

### `mmap` does not mean “no memory” or “no I/O”

`mmap` can avoid allocating a second, full-file Python `bytes` object merely to read a file. It does not eliminate physical I/O, page faults, page-cache use, virtual-address-space use, or memory pressure. Accessing a page not resident in memory can trigger storage I/O. A warm cache can make a second scan much faster than a cold scan. Some workloads can perform worse with `mmap`, especially if access is random, page faults are expensive, or the file is small enough that ordinary buffered I/O is simpler.

- **Virtual size:** address-space range associated with the mapping.
- **Resident set:** pages currently resident in physical memory for the process; accounting for shared/file-backed pages differs by OS and tooling.
- **Page fault:** a virtual-memory access that needs OS handling; it may be minor (no disk read) or major (storage I/O), depending on platform and state.
- **Page cache:** OS-managed cache of file data. It is distinct from a Python-level `read()` buffer.

## 2. Search and scan mapped data

`mmap` search methods operate on bytes. Use bytes regex patterns (`rb"..."`) with `re`; do not decode arbitrary binary data as UTF-8 unless the file format guarantees that encoding.

```python
import mmap
import re
import tempfile
from pathlib import Path

pattern = re.compile(rb"\bERROR\b.*")
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "service.log"
    p.write_bytes(b"INFO boot\nERROR timeout after 5s\nWARN retry\nERROR disk\n")
    with p.open("rb") as f:
        if p.stat().st_size:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                print("first ERROR:", mm.find(b"ERROR"))
                print("last ERROR:", mm.rfind(b"ERROR"))
                mm.seek(0)
                for line in iter(mm.readline, b""):
                    match = pattern.search(line)
                    if match:
                        print(match.group().decode("ascii"))
```

Expected output:

```text
first ERROR: 10
last ERROR: 44
ERROR timeout after 5s
ERROR disk
```

For line iteration, `readline()` advances the map's shared cursor. If multiple consumers need independent positions, use explicit offsets or separate maps rather than sharing one cursor casually. For very long lines, line-by-line processing still may allocate a large `bytes` object for that line; impose a line-size policy when input is untrusted.

### Empty, missing, and changing files

- **Missing file:** opening it raises `FileNotFoundError`; do not silently interpret this as an empty file unless the application contract says so.
- **Empty file:** check size and skip mapping. `mmap` generally cannot create a useful zero-length map.
- **Truncated or modified after mapping:** a map reflects a file-backed region whose size and contents may change externally. If another process truncates the underlying file while a map is being accessed, behavior can be severe: Unix-like systems may deliver `SIGBUS` on access to pages beyond the new end; Windows can raise an access violation or other OS-level failure. Do not use a try/except block as a reliable shield against all such faults.
- **Concurrent writers:** changing bytes while a reader scans can produce inconsistent records even if the file is not truncated. Prefer immutable snapshots, a lock/protocol, or versioned files when consistency matters.

For untrusted or concurrently managed files, verify size and format bounds before mapping, then ensure a writer cannot truncate or rewrite the file during the read. A pre-check alone is not enough if the file can change immediately afterward.

---

## 3. Access modes, flushing, and resizing

| Mode/API | Semantics | Appropriate use | Caveats |
|---|---|---|---|
| `mmap.ACCESS_READ` | Read-only mapping | Search and read stable files | Writes through the map are prohibited. Underlying file changes can still affect the view. |
| `mmap.ACCESS_WRITE` | Writes update the mapped file | Controlled in-place edits | Requires a writable file/region; coordinate writers and define crash-recovery behavior. |
| `mmap.ACCESS_COPY` | Copy-on-write private mapping | Temporary modifications that must not update the file | Changes are private to the mapping and are not persisted to the source file. |
| `mm.flush()` | Requests mapped changes be flushed to storage | Persisting changes to a writable mapping | Does not by itself guarantee application-level transactionality or all crash-durability guarantees. Platform semantics differ. |
| `mm.resize(new_size)` | Attempts to change mapping/file size | Controlled file-format maintenance | Requires writable mapping and OS support; may fail with exported buffer views or platform restrictions. Do not resize while views/arrays refer to the map. |

For writable mappings, `flush()` is not a transaction and does not make a multi-record update crash-consistent. On POSIX systems, an application needing stronger durability may also need `os.fsync()` on the file descriptor and directory metadata after rename, with an explicit ordering policy. Windows uses different APIs and guarantees. The exact durability contract must be designed and tested for the target OS/filesystem.

```python
import mmap
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "mutable.bin"
    p.write_bytes(b"ABCDE")
    with p.open("r+b") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE) as mm:
            mm[1:3] = b"xy"
            mm.flush()
    print(p.read_bytes())
```

Expected output:

```text
b'AxyDE'
```

Do not assume `ACCESS_COPY` changes are written back; do not assume `flush()` alone makes a multi-step update atomic.

### Resizing rules of thumb

- Ensure the map is writable and the file is open with appropriate permissions.
- Release every exported `memoryview`, NumPy view, or other buffer export before closing or resizing the map. Python can raise `BufferError` when the buffer is still exported.
- A mapping resize can alter the file size. Validate the intended new size and update any header/index consistently.
- Mapping and resizing constraints vary between Windows and Unix-like platforms. Treat `resize()` as an operation to test on the deployment platform, not as a portable transaction primitive.

---

## 4. Buffer views: `memoryview`, `struct`, and NumPy

The buffer protocol lets consumers view bytes without copying. That is useful for fixed-width records, but it introduces a lifetime dependency: a view cannot outlive the storage it refers to. Release views before closing a map.

```python
import mmap
import struct
import tempfile
from pathlib import Path

RECORD = struct.Struct("<Ih")  # little-endian uint32 + int16; 6 bytes
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "records.bin"
    p.write_bytes(RECORD.pack(100, -2) + RECORD.pack(200, 7))
    with p.open("rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            view = memoryview(mm)
            try:
                first = RECORD.unpack_from(view, 0)
                second = RECORD.unpack_from(view, RECORD.size)
                print(first, second)
            finally:
                view.release()
```

Expected output:

```text
(100, -2) (200, 7)
```

`struct.unpack_from()` reads at an offset without requiring a sliced temporary `bytes` object. Always validate `offset >= 0` and `offset + RECORD.size <= len(mm)` before parsing data from an untrusted file. The sample's offsets are known because the file was generated by the same code.

### `numpy.frombuffer` and view lifetime

`numpy.frombuffer` is also third-party NumPy functionality. It can interpret a buffer as an array without copying the entire buffer, but the resulting array keeps a dependency on the exported buffer. Release the array and any derived views before closing the mapping. This example is optional and requires NumPy:

```python
# Requires: python -m pip install numpy
import mmap
import tempfile
from pathlib import Path
import numpy as np

with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "samples.u16"
    p.write_bytes(b"\x01\x00\x02\x00\x03\x00")
    with p.open("rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            values = np.frombuffer(mm, dtype="<u2")
            try:
                print(values.tolist())
            finally:
                del values  # no derived arrays/views may remain here
```

Expected output:

```text
[1, 2, 3]
```

If another array or view still references the mapping, closing `mm` can raise `BufferError`. Avoid forcibly closing a mapping behind live NumPy views; keep ownership and cleanup order explicit.

### NumPy is optional third-party software

`numpy.memmap` is provided by **NumPy**, not the Python standard library. It is useful for large, regular arrays with known dtype, shape, and byte order. The file size must be compatible with the declared shape and dtype; a wrong dtype, shape, offset, or endianness silently produces wrong values or indexing errors.

```python
# Requires: python -m pip install numpy
import tempfile
from pathlib import Path
import numpy as np

with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "values.f32"
    np.asarray([1.25, 2.5, 5.0], dtype="<f4").tofile(p)
    arr = np.memmap(p, dtype="<f4", mode="r", shape=(3,))
    try:
        print(arr[1], arr.sum())
    finally:
        # NumPy memmap lifetime/close details depend on views and NumPy version.
        # Drop derived views before releasing arr; do not rely on private _mmap APIs
        # in portable application code.
        del arr
```

Expected output (floating-point formatting may vary slightly):

```text
2.5 8.75
```

For a large production array, keep the owning memmap alive for the whole period of use and do not forcibly close its underlying mapping while derived arrays still exist. Use the documented NumPy API for your version and test cleanup behavior. Avoid depending on private attributes such as `arr._mmap` as a cross-version contract.

### `os.pread` alternative

On systems that support it (commonly Unix-like systems), `os.pread(fd, n, offset)` reads bytes at an explicit offset without changing the file object's shared cursor. It is useful for independent random reads without mapping a large address range. It is not available on every platform (notably it is not a portable Windows API); check `hasattr(os, "pread")` or the target platform. On Windows, use an appropriate platform-specific API or independent file handles/seek-read logic with coordination.

---

## 5. Fixed records, offset indexes, and sparse files

A common layout stores fixed-size records consecutively. If each record has exactly `record_size` bytes, record `i` begins at `header_size + i * record_size`; validate the index and bounds before unpacking. An offset index can provide O(1) lookup into variable-length records if each index entry stores a validated offset and length.

```python
import mmap
import struct
import tempfile
from pathlib import Path

HEADER = struct.Struct("<4sI")  # magic + record count
RECORD = struct.Struct("<I8s")  # key + fixed 8-byte value
MAX_RECORDS = 1_000_000

with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "kv.bin"
    records = [(10, b"alpha"), (20, b"beta"), (30, b"gamma")]
    body = b"".join(RECORD.pack(k, v) for k, v in records)
    p.write_bytes(HEADER.pack(b"KV01", len(records)) + body)

    with p.open("rb") as f:
        size = p.stat().st_size
        if size < HEADER.size:
            raise ValueError("truncated header")
        # Read and validate the small header before creating the mapping.
        magic, count = HEADER.unpack(f.read(HEADER.size))
        if magic != b"KV01":
            raise ValueError("bad magic")
        if count > MAX_RECORDS:
            raise ValueError("record count exceeds policy")
        expected = HEADER.size + count * RECORD.size
        if expected != size:
            raise ValueError("truncated or trailing data")

        # Assumes the file is stable during this operation; bounds checks alone
        # cannot protect against a concurrent external truncation.
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            index = 1
            if not 0 <= index < count:
                raise IndexError("record index out of range")
            offset = HEADER.size + index * RECORD.size
            if offset < HEADER.size or offset + RECORD.size > len(mm):
                raise ValueError("record outside mapped file")
            key, value = RECORD.unpack_from(mm, offset)
            print(key, value.rstrip(b"\0"))
```

Expected output:

```text
20 b'beta'
```

This is a teaching format, not a database implementation. A production format should specify versioning, byte order, maximum record count/size, checksum coverage, and recovery semantics. Validate arithmetic and limits before trusting a count from a file; a malicious count must not cause huge allocations or unchecked offsets.

### Sparse files and preallocation

- `os.truncate(path, size)` changes a file's length and may create a sparse region on filesystems that support sparse files. Newly read regions commonly appear as zero bytes, but physical allocation behavior is filesystem-dependent.
- `os.posix_fallocate(fd, offset, length)` is available on supported POSIX systems and requests allocation for a region; it is not portable to Windows and may fail or behave differently by filesystem.
- A sparse file's logical size can be much larger than allocated disk blocks. Do not infer physical storage usage from `stat().st_size` alone.
- Do not preallocate or truncate a file another process has mapped unless a coordinated protocol guarantees that readers are not accessing the affected range.

---

## 6. Virtual memory hints and operating-system details

On supported systems, Python exposes `mmap.madvise()` and constants such as `mmap.MADV_SEQUENTIAL` or `mmap.MADV_RANDOM`. These are advisory hints, not guarantees. The method and constants vary by platform; guard them with `hasattr` and benchmark the target workload.

```python
import mmap
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "scan.bin"
    p.write_bytes(b"x" * 4096)
    with p.open("rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            if hasattr(mm, "madvise") and hasattr(mmap, "MADV_SEQUENTIAL"):
                mm.madvise(mmap.MADV_SEQUENTIAL)
            print(len(mm))
```

`mmap.madvise` is available on supported platforms in modern Python (introduced in Python 3.8), but individual advice constants are platform-specific. Hints should never be required for correctness.

### Concurrency and locking

Read-only maps can be shared by multiple processes when the file is stable and the OS/filesystem supports the mapping. Multiple readers do not automatically make concurrent mutation safe. Writers need an explicit locking and publication protocol.

- **POSIX:** `fcntl.flock()` can provide advisory file locking on many Unix-like systems. All participating processes must follow the same protocol; advisory locks do not stop uncooperative writers.
- **Windows:** `msvcrt.locking()` provides byte-range locking for file descriptors, with different semantics and setup requirements. Windows also has file-sharing and mapping constraints that differ from POSIX.
- For portable code, define a platform-specific locking abstraction and test it on the deployment OS. Do not present either API as a universal lock.
- A robust publication pattern for read-mostly files is: write a complete new file to a temporary path, validate it, flush/fsync according to the durability contract, atomically replace the published path where supported, and have readers open the new version. On POSIX, atomic rename and directory fsync details matter; Windows replacement semantics and open-file behavior differ.

### Network filesystems and containers

Network filesystem caching, consistency, locking, and error behavior vary. A map may not have the same latency or coherency properties as a local SSD. Containers may charge file-backed pages to a cgroup even when they are reclaimable; a process can be OOM-killed under memory pressure despite not holding a huge Python `bytes` object. Monitor process RSS and container/cgroup memory metrics, not just Python heap measurements.

---

## 7. Buffered I/O vs `readinto` vs `mmap`

| Technique | Strengths | Costs / risks | Often a good fit |
|---|---|---|---|
| `f.read(chunk_size)` | Simple; bounded Python buffer; clear sequential flow | Allocates a new `bytes` object per read; copying/parsing may add work | Sequential scans, streaming transforms, small/medium files |
| `f.readinto(reusable_bytearray)` | Reuses a preallocated buffer; can reduce allocation churn | Consumer must process only the returned byte count; buffer contents are overwritten on next read | High-throughput sequential pipelines with reusable buffers |
| `mmap` | Convenient random access and searching; can avoid a full-file Python copy | Page faults, virtual address use, external-truncation hazards, platform-specific behavior; slices can copy | Large stable files, random lookup, repeated scans, fixed-layout data |

There is no universal winner. Benchmark on the actual OS, filesystem, storage, file size, data shape, and access pattern. A single sequential pass may be as fast or faster with buffered I/O; repeated random access may favor a map.

### Fair benchmark plan

1. Generate a deterministic test file large enough to matter (for example, hundreds of MiB; use a smaller size in CI).
2. Compare identical work: count the same byte pattern with buffered chunk reads, a reusable `readinto` buffer, and `mmap.find`/scanning.
3. Verify every method returns the same count. Do not include file generation in timed regions.
4. Measure repeated runs and report median/dispersion, throughput, wall time, CPU time if useful, and file size. Use `time.perf_counter()`.
5. Separate **warm-cache** runs from best-effort **cold-cache** runs. Truly clearing the OS page cache often requires privileged/platform-specific operations; closing a file is not proof that the cache is cold. Label cold-cache measurements honestly.
6. Run enough iterations to reduce noise; avoid benchmarking inside a heavily loaded machine. Do not extrapolate a small in-memory file result to a 1 GB production workload.

The following benchmark harness creates its own temporary file and checks result equality. It does not try to clear the OS cache and therefore should be described as a repeatable, typically warm-cache comparison after the first pass.

```python
import mmap
import tempfile
import time
from pathlib import Path

NEEDLE = b"ERROR"
CHUNK = 1024 * 1024

def buffered_count(path: Path) -> int:
    # Counts occurrences even when a match crosses a chunk boundary.
    count = 0
    overlap = b""
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            data = overlap + chunk
            count += data.count(NEEDLE)
            overlap = data[-(len(NEEDLE) - 1):]
    return count

def readinto_count(path: Path) -> int:
    count = 0
    overlap = b""
    buf = bytearray(CHUNK)
    with path.open("rb") as f:
        while (n := f.readinto(buf)):
            data = overlap + memoryview(buf)[:n].tobytes()
            count += data.count(NEEDLE)
            overlap = data[-(len(NEEDLE) - 1):]
    return count

def mmap_count(path: Path) -> int:
    size = path.stat().st_size
    if size == 0:
        return 0
    count = 0
    with path.open("rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            pos = 0
            while True:
                pos = mm.find(NEEDLE, pos)
                if pos < 0:
                    break
                count += 1
                pos += len(NEEDLE)
    return count

with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "bench.bin"
    p.write_bytes((b"INFO data\nERROR issue\n" * 100_000))
    methods = [buffered_count, readinto_count, mmap_count]
    expected = methods[0](p)
    for fn in methods:
        result = fn(p)
        assert result == expected
        start = time.perf_counter()
        for _ in range(3):
            assert fn(p) == expected
        elapsed = (time.perf_counter() - start) / 3
        print(f"{fn.__name__}: {result} matches, {elapsed:.4f}s/run")
```

Output timings are machine-dependent. The output shape is three lines, one per method; do not copy timings from another machine as a general claim. The `readinto` example converts each used chunk to bytes for boundary overlap and counting, so it demonstrates reusable input storage rather than a perfectly zero-copy consumer. A production parser may process a `memoryview` directly.

---

## 8. Safe handling of missing, truncated, and modified inputs

The most important rule is not to induce a live external-truncation race in a unit test: on some systems that can crash the process instead of raising a Python exception. Test malformed file formats with ordinary file contents and bounds checks; test external mutation behavior only in a disposable subprocess on the target OS, with careful isolation.

```python
import mmap
import struct
import tempfile
from pathlib import Path

HEADER = struct.Struct("<4sI")

def inspect_file(path: Path) -> tuple[bytes, int]:
    size = path.stat().st_size
    if size == 0:
        raise ValueError("empty file")
    with path.open("rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            if len(mm) < HEADER.size:
                raise ValueError("truncated header")
            magic, count = HEADER.unpack_from(mm, 0)
            if magic != b"IDX1":
                raise ValueError("invalid magic")
            # A real format must check multiplication/limits before trusting count.
            if count > 1_000_000:
                raise ValueError("record count exceeds policy")
            return magic, count

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    missing = root / "missing.bin"
    try:
        missing.open("rb")
    except FileNotFoundError:
        print("missing: handled")

    empty = root / "empty.bin"
    empty.write_bytes(b"")
    try:
        inspect_file(empty)
    except ValueError as exc:
        print(type(exc).__name__, str(exc))

    short = root / "short.bin"
    short.write_bytes(b"IDX")
    try:
        inspect_file(short)
    except ValueError as exc:
        print(type(exc).__name__, str(exc))

    changed = root / "changed.bin"
    changed.write_bytes(HEADER.pack(b"BAD!", 0))
    try:
        inspect_file(changed)
    except ValueError as exc:
        print(type(exc).__name__, str(exc))
```

Expected output:

```text
missing: handled
ValueError empty file
ValueError truncated header
ValueError invalid magic
```

The bounds checks protect against the malformed files shown. They do not make it safe to map a file that an uncoordinated process can truncate during access. For concurrent environments, use immutable file publication, locks, snapshots, or an access API that gives the required consistency guarantees.

---

## 9. Checksums, append-only logs, and crash recovery

A CRC/checksum detects many accidental corruptions; it is not a cryptographic authenticity guarantee. For tamper detection, use a cryptographic hash with a trusted expected value or a MAC/signature under a correctly managed key. A checksum itself does not prove who wrote a record.

### A practical append-only record design

A production-oriented binary log can use:

- **Header:** magic, format version, declared flags.
- **Records:** fixed-size header containing bounded payload length, timestamp, level, followed by payload bytes and a CRC over explicitly specified fields.
- **Footer or sidecar index:** record count and sparse offsets, rebuilt if necessary.
- **Recovery rule:** stop at the first incomplete or invalid tail record; never treat partial data as complete. Preserve the valid prefix and report where recovery stopped.
- **Writer policy:** define whether each record is one write, whether append is atomic for the target filesystem, when `flush`/`fsync` occurs, and how to handle a crash between payload and checksum.
- **Reader policy:** validate magic/version, maximum record length, offset arithmetic, record boundary, and checksum before exposing a record.

A `mmap` reader is well suited to stable, validated files and random lookups. For a file that is actively appended or repaired, an ordinary streaming reader or a versioned snapshot may be safer. A sidecar sparse index should be treated as untrusted until its offsets and checksums are validated against the data file.

### Partial-write recovery strategy

1. Parse the header with a fixed upper bound on counts and lengths.
2. Walk records only while the complete header and complete payload/checksum fit within the known file size.
3. Validate each record checksum before yielding it.
4. If the tail is incomplete, report a recoverable truncated tail and retain the preceding valid records; do not silently claim the file is intact.
5. If corruption occurs in the middle, decide explicitly whether to stop, quarantine the file, or scan for a separately specified resynchronization marker. Guessing record boundaries is unsafe.
6. Rebuild derived indexes from validated records when possible.

---

## 10. When not to use `mmap`

Prefer buffered I/O when the file is small, you need one sequential pass, you need a simple streaming pipeline, the file may change concurrently, or portable failure handling matters more than random access. Avoid mapping untrusted files if their lifetime/size cannot be controlled. Be cautious with huge mappings in constrained 32-bit address spaces, network filesystems, containerized environments, and workloads where page-fault latency dominates.

`mmap` is a mechanism, not a database, locking protocol, transaction system, or integrity layer. It does not provide schema validation, record boundaries, atomic updates, checksums, or recovery by itself.

---

## 11. Common mistakes and fixes

| Mistake | Why it fails | Better approach |
|---|---|---|
| Mapping an empty file | Zero-length mappings generally fail | Check `stat().st_size`; handle empty input explicitly |
| Forgetting to close a map | Holds mapping resources and can keep files locked on some platforms | Use `with mmap.mmap(...) as mm:` |
| Closing map before releasing `memoryview`/NumPy views | Exported buffers can prevent close/resize (`BufferError`) or leave dependent views invalid | Release views first; keep owners alive for all dependent views |
| Assuming `length=0` handles later growth | Mapping extent is established when created | Reopen/remap or use a defined growth protocol |
| Assuming mapped bytes cannot change | Other writers may alter file content | Immutable snapshots or coordinated locking/versioning |
| Ignoring external truncation | Can cause OS-level faults, not just Python exceptions | Prevent truncation while mapped; isolate adversarial tests |
| Treating `flush()` as a transaction | Flush is not atomic multi-record commit or a full durability protocol | Specify ordering, checksums, fsync/rename policy, recovery |
| Assuming `ACCESS_COPY` persists writes | Copy-on-write changes are private | Use `ACCESS_WRITE` only for intentional controlled updates |
| Treating `mmap` as universally faster | Cache state, access pattern, and OS dominate | Benchmark the real workload against `read`/`readinto` |
| Trusting file counts and offsets | Malformed values can lead to invalid reads or excessive work | Validate limits and all offset arithmetic before use |
| Assuming `madvise` is portable or binding | Hints/constants vary and are advisory | Feature-detect and benchmark; never rely on hints for correctness |

---

## 12. Exercises with solutions

### Exercise 1 — Empty files

**Question:** Why should code check file size before calling `mmap.mmap(f.fileno(), 0, ...)`?

**Solution:** `length=0` means map the file's current size; it is not a portable way to create a zero-byte map. Empty-file mapping generally raises an exception. Handle the empty case before mapping.

### Exercise 2 — Access modes

**Question:** What is the difference between `ACCESS_WRITE` and `ACCESS_COPY`?

**Solution:** `ACCESS_WRITE` changes are reflected in the underlying file mapping. `ACCESS_COPY` uses copy-on-write semantics; changes are private to the mapping and are not written back to the file.

### Exercise 3 — Bounds-safe record access

**Question:** A file contains `count` fixed-width records after a header. What must be checked before `unpack_from(mm, header_size + i * record_size)`?

**Solution:** Validate magic/version, ensure `0 <= i < count`, bound `count` by policy, verify the declared layout fits the actual file size, and check the selected record's start and end offsets are within the mapped length. Avoid trusting file-controlled counts before limits and arithmetic checks.

### Exercise 4 — External truncation

**Question:** Why is `try: data = mm[offset] except Exception: ...` not a sufficient defence against another process truncating the mapped file?

**Solution:** Access to pages beyond a truncated file can cause an OS-level fault such as `SIGBUS` or an access violation, which may not be a normal catchable Python exception. Prevent concurrent truncation through a protocol or use a safer access pattern.

### Exercise 5 — Benchmark plan

**Question:** Design a fair `read`, `readinto`, and `mmap` comparison.

**Solution:** Generate a deterministic file; make all methods perform identical work and verify equal results; exclude generation from timing; run repeated measurements; separate warm-cache and best-effort cold-cache results; report file size, OS/filesystem, runtime, throughput, median/dispersion, and cache limitations. Do not claim universal performance superiority.

### Exercise 6 — Append-only binary log

**Question:** What should a reader do when the last record's length field is present but its payload/checksum is truncated?

**Solution:** Validate that the complete record fits in the known file size before reading. Report a truncated tail and return only the valid prefix if the format defines that recovery behavior. Never silently treat the partial record as complete. If corruption is in the middle, follow an explicit quarantine/resynchronization policy.

---

## 13. Glossary

- **Memory mapping (`mmap`):** Mapping file-backed storage into a process's virtual address space.
- **Page cache:** OS cache of file-backed pages used to avoid repeated storage reads.
- **Page fault:** OS handling required when a virtual page is accessed; may or may not require disk I/O.
- **Virtual address space:** Addresses available to a process, not a direct measurement of physical RAM consumed.
- **Resident set (RSS):** Approximate measure of pages resident for a process; shared-page accounting varies.
- **Copy-on-write:** A private mapping's modifications create private copies rather than changing the source file.
- **Exported buffer:** A `memoryview` or other consumer holding a reference to a buffer-providing object.
- **Sparse file:** A file whose logical length can exceed its allocated physical storage.
- **Offset index:** A table mapping keys/record numbers to byte offsets in a file.
- **Crash consistency:** Whether a file remains interpretable after interruption during a write/update.
- **CRC/checksum:** A corruption-detection value, not proof of authenticity.
- **`pread`:** Positional read API available on supported systems; reads from an offset without changing a shared file cursor.
- **`madvise`:** Platform-specific advisory hint to the OS about expected memory access patterns.

---

## 14. Completion checklist

- [ ] I can create a read-only map of a non-empty file and handle an empty file separately.
- [ ] I can search and scan with `find`, `rfind`, bytes regexes, and `readline`.
- [ ] I understand `ACCESS_READ`, `ACCESS_WRITE`, `ACCESS_COPY`, `flush`, and resizing caveats.
- [ ] I release `memoryview`/NumPy views before closing or resizing their backing map.
- [ ] I can bounds-check fixed records and offset indexes before parsing.
- [ ] I can explain sparse files, preallocation, `pread`, and `madvise` portability.
- [ ] I understand why external truncation and concurrent mutation are dangerous.
- [ ] I can explain the difference between virtual size, RSS, page cache, and physical I/O.
- [ ] I can design a benchmark that compares identical work and labels cache conditions honestly.
- [ ] I can describe checksummed append-only records and recovery from an incomplete tail.
- [ ] I know when buffered I/O is a better choice than `mmap`.

## 15. Roadmap self-check — answers

### 1. What is the difference between `ACCESS_WRITE` and `ACCESS_COPY`?

`ACCESS_WRITE` writes through to the mapped file. `ACCESS_COPY` is copy-on-write: changes are private and do not update the source file.

### 2. Why can a truncated file crash a process that reads from a map?

The mapping may still cover virtual pages whose backing file pages no longer exist after truncation. Access can trigger OS-level faults (for example, `SIGBUS` on some Unix-like systems or an access violation on Windows), not merely a catchable Python bounds exception. Prevent the race or use a different access strategy.

### 3. Build a binary log searcher using `mmap` and a bytes regex, and benchmark it against buffered line reading on a 1 GB file.

A suitable implementation opens the file in binary mode, checks for an empty file, maps it read-only, scans with a compiled bytes regex, and closes the map before the file. The benchmark should compare it with a buffered line reader using the same regex and same output/count semantics, verify equal results, use repeated timings, and record OS/filesystem, file size, runtime, and warm/cold cache methodology. Do not assume a cold cache just because the file was closed; a real 1 GB benchmark is environment-dependent and was not run as part of this lesson artifact.

---

## Final operational rules

1. Treat a mapped file as shared, mutable OS-backed state unless your file-publication protocol makes it immutable.
2. Validate file size, headers, counts, offsets, and record lengths before using them.
3. Keep mapping and view lifetimes explicit; release exported buffers before close/resize.
4. Use checksums for corruption detection and cryptographic authentication when adversarial tampering is in scope.
5. Define durability, concurrency, and crash recovery separately from the choice to use `mmap`.
6. Benchmark on the target OS and filesystem; never infer universal speed from one run.
