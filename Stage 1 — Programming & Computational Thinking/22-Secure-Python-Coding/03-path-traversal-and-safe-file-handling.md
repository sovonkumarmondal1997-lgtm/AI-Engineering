# Path Traversal and Safe File Handling

**Module:** Stage 1 — Programming & Computational Thinking / 22 — Secure Python Coding  
**Lesson:** 03 — `03-path-traversal-and-safe-file-handling.md`  
**Level:** Beginner → intermediate → advanced  
**Primary concern:** Prevent untrusted input from selecting, reading, overwriting, or exhausting filesystem resources outside an explicitly authorized storage boundary.

## Learning outcomes

By the end, you should be able to:

- Explain how path parsing differs from filesystem resolution and why a filename is not an authorization decision.
- Recognize traversal through `..`, absolute paths, drive/UNC paths, URL encodings, null bytes, mixed separators, Unicode variants, symlinks, junctions, and hard links.
- Contain paths with `pathlib`, `resolve()`, and `is_relative_to()` without relying on string prefixes.
- Design storage APIs around server-generated IDs, least-privilege permissions, secure temporary files, and atomic replacement.
- Explain TOCTOU races and choose descriptor-relative operations or OS-level isolation where appropriate.
- Apply explicit member, link, type, count, expanded-size, and compression-ratio policies to archives.
- Secure upload/download flows, object-store keys, tenant boundaries, and document-processing workers.
- Build and test the `safe_storage` exercise, including malicious inputs, legitimate use, resource limits, and documented residual risks.

## Prerequisites and setup

You should already know `pathlib`, exceptions, file modes, `tempfile`, `os`, basic ZIP/TAR handling, unit tests, and the trust-boundary idea from the earlier lessons. The module roadmap also connects this lesson to subprocesses and archives in Module 1.13, pickle/decompression risks in Module 1.14, testing/fuzzing in Module 1.16, and packaging/supply-chain practices in Module 1.18.

Use Python 3.11+ for the main lab. The portable examples generally work on Python 3.9+, except where a version is called out. Python 3.12 introduced `tarfile` extraction filters; Python 3.14 makes the `data` filter the default for common extraction APIs. Do not infer that a Python version alone makes an extraction routine safe. Test on every supported OS and Python version.

Create a clean lab directory and virtual environment:

```console
python -m venv .venv
# POSIX
. .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip pytest
mkdir -p lab
```

The `mkdir -p` line is for POSIX shells; on Windows, create `lab` with `mkdir lab` or File Explorer. The lesson's main `safe_storage` implementation uses only the standard library. Optional Hypothesis tests are shown later and require `python -m pip install hypothesis`.

## 1. Terminology and mental model

- **Path traversal:** untrusted path syntax is used to escape an intended directory or select a different resource.
- **Containment:** the resolved target is within an approved root. This is a path property, not by itself a complete authorization policy.
- **Canonicalization / resolution:** interpreting path components and resolving filesystem links. `Path.resolve()` is not merely string cleanup.
- **TOCTOU:** time-of-check/time-of-use; the filesystem can change between a check and a later operation.
- **Symlink:** a filesystem object that redirects path resolution. Windows reparse points and junctions have related but platform-specific behavior.
- **Hard link:** another directory entry for the same underlying file on filesystems that support it. A hard link is not detected by `is_symlink()`.
- **Capability-style API:** give code an already-authorized handle (such as an open directory descriptor) and allow only operations relative to that handle, rather than asking it to interpret arbitrary global paths.
- **Archive bomb:** an archive whose expanded output or processing cost is much larger than its compressed input suggests.
- **Object-store key:** an opaque object identifier in an API, not necessarily a local filesystem path. Some tools impose their own prefix/path interpretation, so semantics must be understood end to end.

The key rule is: **authorization should select a server-controlled resource identifier, not trust a user-supplied path.** Path validation is a defense-in-depth layer, not a substitute for access control.

## 2. Filesystem paths and attack surface

A path string is interpreted by the host OS, filesystem, runtime, and sometimes an upstream protocol. A web server may URL-decode a request before Python sees it; a reverse proxy may decode once while the application decodes again. A ZIP member name is usually specified with POSIX-style `/` separators, even when extraction happens on Windows. Treat each boundary explicitly.

Common attack surfaces include upload names, download IDs, archive member names, report destinations, user-selected export paths, tenant/job partition names, cache keys, notebook outputs, model artifacts, temporary directories, and object-store keys.

### 2.1 Traversal forms to recognize

| Form | Example | Why it matters |
|---|---|---|
| Parent traversal | `../secret.txt` | Moves to a parent directory during path resolution. |
| Absolute POSIX path | `/etc/passwd` | Can replace the intended base when joined. |
| Windows drive path | `C:\Windows\win.ini` | Drive-qualified paths can escape a root on Windows. |
| Windows drive-relative path | `C:secret.txt` | Meaning depends on the current directory for that drive. |
| UNC path | `\\server\share\file` | Names a network share on Windows. |
| URL-encoded traversal | `%2e%2e%2fsecret` | Becomes traversal if decoded before path validation. |
| Double encoding | `%252e%252e%252fsecret` | Can become traversal if decoded repeatedly. |
| Mixed separators | `..\../secret` | Different components may normalize separators differently. |
| Null byte | `report.txt\x00.exe` | Historically confused APIs/libraries; modern Python rejects embedded NUL in OS paths, but reject it at the input boundary. |
| Symlink | `uploads/link -> /private` | A syntactically contained path can resolve outside the root. |
| Hard link | `uploads/alias` linked to another file | Link-count and ownership assumptions can fail; symlink checks do not catch it. |
| Windows alternate data stream | `report.txt:metadata` | Colon has special meanings on Windows/NTFS. |
| Unicode lookalike/normalization | visually similar dots or separators | Different layers may normalize or compare strings differently. |

Do not decode URL-encoded strings arbitrarily inside a filesystem helper. Define exactly which layer performs URL decoding, decode once according to the protocol, then validate the decoded value. Reject malformed encodings and null bytes. If an application accepts only an opaque ID, do not decode or interpret a supplied filename as a path at all.

### 2.2 Why joining a base is not enough

**VULNERABLE / LAB ONLY** — absolute paths can discard the base, and `..` can escape it:

```python
# VULNERABLE / LAB ONLY
from pathlib import Path

BASE = Path("/srv/app/uploads")
user_name = "../../etc/passwd"
target = BASE / user_name
# Do not open target: it may point outside BASE.
```

**Safe alternative:** use server-generated IDs for real storage. If a legitimate application must accept a relative path, resolve and check it, while understanding the remaining race described below:

```python
from pathlib import Path, PureWindowsPath

BASE = Path("/srv/app/uploads").resolve(strict=True)

def contained_path(relative_name: str) -> Path:
    if not relative_name or "\x00" in relative_name or "\\" in relative_name:
        raise ValueError("invalid or non-portable path")
    candidate = Path(relative_name)
    windows_candidate = PureWindowsPath(relative_name)
    if (candidate.is_absolute() or candidate.drive or candidate.root
            or windows_candidate.is_absolute() or windows_candidate.drive
            or windows_candidate.root):
        raise ValueError("absolute or drive-qualified paths are not allowed")
    resolved = (BASE / candidate).resolve(strict=False)
    if not resolved.is_relative_to(BASE):  # Python 3.9+
        raise PermissionError("path escapes storage root")
    return resolved
```

This helper assumes `BASE` is a trusted, already-existing root. `strict=False` permits a not-yet-existing leaf while resolving existing ancestors; it does not prove that later filesystem operations are race-free. `Path.is_relative_to()` is lexical on the already-resolved paths and does not itself access the filesystem. Use `resolve()` first when filesystem links matter. On Python versions before 3.9, use `os.path.commonpath()` with care and test the target filesystem; do not replace this with a string prefix test.

### 2.3 Why string `startswith()` is wrong

**VULNERABLE / LAB ONLY** — a sibling directory can share the same textual prefix:

```python
# VULNERABLE / LAB ONLY
base = "/srv/app/uploads"
target = "/srv/app/uploads-evil/secret.txt"
if target.startswith(base):
    print("incorrectly accepted")
```

**Safe alternative:** compare path components after resolving paths:

```python
from pathlib import Path

base = Path("/srv/app/uploads").resolve(strict=True)
target = (base / "report.txt").resolve(strict=False)
if not target.is_relative_to(base):
    raise PermissionError("outside root")
```

Do not compare a resolved target with an unresolved root. Case sensitivity, mount points, network filesystems, Windows reparse points, and concurrent mutation can affect real behavior. The safest design still avoids user-selected pathnames.

## 3. IDs, filenames, permissions, temporary files, atomic writes

### 3.1 Use opaque IDs for storage names

Generate an ID on the server and keep the original name only as sanitized display metadata. Do not use the supplied filename as a directory or storage key. A UUID is a name-generation strategy, not an authorization token; every lookup still needs authentication and tenant ownership checks.

```python
from uuid import uuid4

storage_id = uuid4().hex  # 32 lowercase hexadecimal characters
original_filename_for_display = "quarterly-report.csv"
# Persist storage_id -> owner, original display name, detected type, size, checksum.
# Never turn original_filename_for_display into the on-disk path.
```

Validate IDs against a strict grammar before using them, e.g. exactly 32 lowercase hex characters. Never accept path separators, extensions, or arbitrary prefixes in the ID parameter. Keep metadata separate from the storage filename.

### 3.2 MIME types and extensions are claims, not evidence

The request's `Content-Type`, extension, and user-provided metadata can all be false. Apply an allow-list based on business need, inspect magic bytes with a maintained file-type detector where appropriate, parse with a hardened library, and enforce a size limit while streaming. Content sniffing is not a proof of safety: polyglots and parser vulnerabilities exist. Malware scanning may be appropriate for public upload services but is not a replacement for isolation.

For the lab implementation, only plain UTF-8 text and a narrow PNG signature are accepted. This deliberately small policy is a teaching example, not a general file-type detector. Expand it only with explicit format-specific validation.

### 3.3 Least privilege, modes, and `umask`

On POSIX, `0o700` means only the owner can access a directory; `0o600` means only the owner can read/write a file. The process `umask` masks requested permission bits; it is process-wide, so changing it in a threaded server can affect unrelated file creation. Explicitly set restrictive modes where supported and verify deployment ownership and ACLs. Windows uses ACLs rather than POSIX mode semantics as its primary security model; `chmod()` is not a complete ACL policy there.

Do not run a file-processing service as root/Administrator. Separate read-only application code from writable data. Secrets/config files should have least-privilege ownership and access; for POSIX, a check for group/other permission bits can detect a common misconfiguration, but it does not establish owner identity, ACL correctness, or safe path resolution.

```python
import os
import stat
from pathlib import Path

def check_posix_secret_mode(path: Path) -> None:
    if os.name != "posix":
        raise NotImplementedError("use the platform's ACL inspection policy")
    st = os.stat(path, follow_symlinks=False)
    if not stat.S_ISREG(st.st_mode):
        raise PermissionError("secret must be a regular file")
    if st.st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise PermissionError("secret file is accessible by group or others")
```

This is a diagnostic check only. It follows no symlink for the final component, but the parent path can still be redirected; use a trusted configuration directory and an appropriate descriptor-based open strategy for a hostile environment.

### 3.4 Secure temporary files

Use `tempfile.NamedTemporaryFile`, `mkstemp`, or `TemporaryDirectory`. Do not use `tempfile.mktemp()`, predictable names in shared `/tmp`, or a check-then-create pattern. Clean up in `finally` or with a context manager. Place temporary files on the same filesystem as the final target when relying on atomic rename semantics.

### 3.5 Atomic writes

An atomic replacement prevents readers from observing a partially written file under the usual local-filesystem rename semantics. It does **not** automatically prevent target symlink races, enforce ownership, make data durable after power loss, or coordinate multiple writers. Create the temporary file in a trusted parent directory, use restrictive permissions, flush and `fsync()` the file, then `os.replace()` it. If crash durability matters, also `fsync()` the containing directory on platforms that support it. Ensure untrusted users cannot modify the destination directory.

**VULNERABLE / LAB ONLY** — predictable temporary names can be pre-created or redirected:

```python
# VULNERABLE / LAB ONLY
import os

name = "/tmp/upload-123.tmp"
if not os.path.exists(name):
    with open(name, "w") as f:
        f.write("untrusted upload")
```

**Safe alternative:** use `tempfile.mkstemp()` or `NamedTemporaryFile` in a trusted directory, then write and atomically replace the intended server-generated destination. The `safe_storage` implementation below demonstrates this pattern; its residual race limitations are documented explicitly.

## 4. Intermediate defences: races, links, archives, uploads, downloads

### 4.1 TOCTOU and link attacks

A pattern such as `if not path.is_symlink(): open(path)` is racy: an attacker able to modify the directory may replace the entry after the check and before `open()`. `resolve()` followed by `open()` has the same fundamental check/use gap. A hard link is not a symlink and can refer to an inode also reachable elsewhere. Directory ownership and write permissions are therefore critical.

On POSIX systems, stronger patterns include:

- Open the trusted directory once, then use `os.open(name, flags, dir_fd=dirfd)` for a single validated basename.
- Use `O_NOFOLLOW` where available to reject a symlink at the final component; it does not necessarily protect every intermediate component in an arbitrary path.
- Use `O_CREAT | O_EXCL` for exclusive creation, not `exists()` followed by create.
- Inspect the opened descriptor with `os.fstat()` and require a regular file where appropriate.
- Use `os.replace(..., src_dir_fd=..., dst_dir_fd=...)` where supported and keep the directory non-writable by untrusted principals.

Python exposes `os.supports_dir_fd`, `os.supports_follow_symlinks`, and constants such as `os.O_NOFOLLOW` only on supported platforms. Test capability availability rather than assuming it. Windows junctions/reparse points, sharing modes, and ACLs require platform-specific handling; a POSIX flag recipe is not portable proof. For high-risk services, use OS isolation and an audited platform-specific implementation.

### 4.2 Archive extraction is a parser and filesystem boundary

Do not call `extractall()` on untrusted archives without a deliberate, version-aware policy. For each member:

1. Enforce a maximum member count before creating output.
2. Reject absolute names, drive-qualified names, `..`, NUL, backslashes if the archive format requires POSIX member names, and ambiguous normalization.
3. Reject symlinks, hard links, devices, FIFOs, and other special files. ZIP metadata can encode Unix file types; TAR has explicit link and device member types.
4. Reject duplicate normalized destinations and file/directory conflicts.
5. Enforce per-file and total expanded byte limits and a compression-ratio ceiling. Also cap archive input size, CPU time, and available disk space.
6. Extract into a newly created, empty, private directory. Do not merge untrusted archive members into an existing application tree.
7. Create regular files exclusively and stream bytes with limits rather than trusting only declared sizes.
8. Treat the extracted content as untrusted even after path validation; scan/parse in a sandbox if appropriate.

A fresh directory must itself be under a trusted parent, and attackers must not be able to replace it or modify its ancestors during extraction. The implementation below intentionally extracts ZIP archives only and rejects nested members to keep the policy auditable. If your product needs nested directories or TAR support, add and test that policy explicitly rather than silently broadening it.

#### TAR extraction filters

Python 3.12 added extraction filters; Python 3.14 changed the default for common extraction APIs to `data`. On Python 3.12+ use `filter="data"` as one layer, but still enforce application-specific count/size/ratio limits and explicitly reject links unless the product has a reviewed reason to support them. On earlier versions, do not pass a `filter` keyword that does not exist; either implement a reviewed member-by-member extractor or refuse TAR uploads. Do not treat `filter="data"` as a resource-limit mechanism. For adversarial input, prefer the explicit refusal policy until a tested TAR extractor is available.

### 4.3 Upload controls

- Authenticate and authorize the uploader and enforce per-user/tenant quotas.
- Stream into a private staging area with a hard byte limit; do not buffer unbounded request bodies in memory.
- Assign a server-generated storage ID and a server-derived extension/type policy.
- Verify file type using signature/parser checks; do not trust `Content-Type` or the filename suffix.
- Store outside the web root or in private object storage. Never expose the storage path directly.
- Scan when appropriate, but do so in an isolated worker with time, memory, process, and network limits.
- Record owner, size, detected type, checksum, and audit metadata. Do not log sensitive absolute paths or raw untrusted names without escaping.

### 4.4 Download controls

Accept an opaque ID, authenticate the caller, check tenant/owner authorization, and resolve the ID through metadata. Do not accept a client-supplied path. Stream from an already-authorized open file or object-store handle with a size limit and appropriate timeouts. Avoid returning filesystem errors or absolute paths to clients.

For browser downloads, set a server-derived `Content-Type`, `Content-Disposition: attachment` with correctly encoded display metadata, and `X-Content-Type-Options: nosniff`. Consider a restrictive content-security policy or separate download origin for active formats. Do not blindly echo user-supplied response headers. Verify checksums when reading from storage where integrity is part of the threat model.

## 5. Cross-platform notes and limitations

### POSIX / Linux

- Path comparison is usually case-sensitive but filesystem and mount behavior can differ.
- `O_NOFOLLOW`, `O_DIRECTORY`, `dir_fd`, and directory `fsync()` availability varies. Check `os.name`, `hasattr(os, ...)`, and `os.supports_dir_fd`.
- NFS and other network filesystems can have different cache/rename/durability semantics.
- `commonpath()` can raise `ValueError` for different drives and is not a universal filesystem authorization mechanism.

### Windows

- Drive-rooted (`C:\x`), drive-relative (`C:x`), rooted (`\x`), UNC (`\\host\share\x`), and extended-length paths have different semantics.
- Reserved device names (`CON`, `NUL`, `PRN`, `AUX`, `COM1`, `LPT1` and variants), trailing dots/spaces, alternate data streams (`name:stream`), case-insensitivity, reparse points, and junctions deserve explicit policy.
- Use `PureWindowsPath` to inspect Windows syntax even when tests run on POSIX; it does not emulate Windows filesystem resolution or prove safety.
- Test on Windows itself. POSIX `O_NOFOLLOW` recipes and mode bits do not translate directly into equivalent Windows guarantees.

### URL and archive paths

URL decoding and filesystem normalization are different steps. Define a single decode boundary and reject malformed/ambiguous input. Archive member names often use `/` independent of host OS; validate archive semantics before constructing native `Path` objects. Avoid relying on “sanitize by replacing `..`” or on a blacklist of a few payload strings.

## 6. Advanced design: capability APIs, OS hardening, tenants, object stores

### 6.1 Capability-oriented file access

Prefer APIs like `read_upload(upload_id, principal)` over `open_user_path(path)`. The former can authorize the principal, resolve metadata to a server-controlled object, and return a bounded stream. For a local POSIX implementation, opening a trusted directory and using relative file descriptors reduces reliance on global path resolution. A directory descriptor is a capability only if its provenance and permissions are trusted and the operations remain constrained to safe names.

Linux `openat2(2)` offers useful resolution controls such as `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, and `RESOLVE_NO_SYMLINKS`. It is a Linux syscall, not a portable Python standard-library API. Do not casually call it through `ctypes` without correct syscall numbers, structure layouts, architecture handling, and a reviewed implementation. Prefer a maintained binding or a small audited native helper. If it is unavailable, fail closed or use a deliberately weaker threat model plus strong directory permissions/isolation.

### 6.2 Container and filesystem hardening

- Run a dedicated unprivileged worker user; drop capabilities and avoid privileged containers.
- Make application code and root filesystem read-only; mount only explicit writable data and scratch volumes.
- Use `noexec,nodev,nosuid` where compatible with workload requirements; these are defense in depth, not a sandbox by themselves.
- Use quotas for bytes, inodes, CPU, memory, process count, and wall-clock time. Disk-full and inode-exhaustion handling are security requirements.
- Apply AppArmor/SELinux or equivalent policy where available. Restrict network egress for document parsers and malware scanners.
- Isolate tenants/jobs with separate directories, ownership, object prefixes/buckets, and worker identities. A UUID does not prevent cross-tenant IDOR; authorization must be checked on every read, write, delete, and share operation.
- Mount secrets read-only and expose only the credentials required by the worker. Do not place secrets in the same writable directory as user uploads.

`chroot` alone is not a complete security boundary. Containers share the host kernel; use a threat-model-appropriate sandbox and keep the kernel/runtime patched.

### 6.3 Object-store key semantics

S3-like object stores generally treat keys as opaque strings; `/` is often a naming convention rather than a true directory. But applications, sync tools, gateways, data-lake engines, and download helpers may normalize keys or map them onto local paths. Do not assume `..` is harmless across every component.

- Prefer generated opaque keys such as `tenant-id/upload-id` where both components are validated server-side.
- Authorize by tenant and object metadata, not merely by string prefix. Prefix `tenant-1` can collide with `tenant-10` if boundary checks are naive.
- Keep buckets private, use least-privilege IAM, scope pre-signed URLs to one object and short expiry, and avoid public ACLs.
- Validate partition values (`dt=...`, customer IDs) before they enter a query, key, or local export path. Escape/quote according to the downstream system's rules.
- Enable versioning/retention/immutability where audit needs justify it; verify checksum and size metadata on ingest and egress.

### 6.4 Archive bombs and hostile parsers

A compressed file can expand to huge data, contain millions of tiny entries, consume CPU through pathological structures, or exploit a bug in an image/PDF/office parser. Enforce input, expanded-size, count, per-entry, ratio, CPU, memory, process, and wall-clock limits. Stream data and abort once a limit is crossed. A ratio limit alone is insufficient: a large archive may have a modest ratio but still exceed the disk budget.

Parse documents in an isolated worker with no unnecessary network access, no application secrets, a read-only root filesystem, and a private scratch directory. Keep parser libraries patched. Consider format-specific validation and antivirus scanning, but do not interpret either as proof of harmlessness.

## 7. `safe_storage` exercise — implementation

This exercise is a compact reference implementation for a constrained lab, not a universal production storage service. It demonstrates opaque IDs, allow-listed types, bounded content, restrictive file creation, atomic replacement, ID-only reads, and conservative ZIP extraction. It assumes the storage root and its parent are provisioned by a trusted administrator and cannot be modified by an attacker running as the same OS user. If an attacker can write to the root or its ancestors, portable `Path` checks cannot provide a complete race-free guarantee.

### 7.1 Threat model

**Assets:** stored upload bytes, per-upload metadata, storage integrity, tenant isolation.  
**Attacker controls:** submitted upload bytes, declared MIME type, original filename, requested upload ID, and ZIP archive bytes.  
**Attacker does not control in this lab:** process identity, trusted storage-root parent, Python runtime, and test directory ownership.  
**Security goals:** prevent user-controlled paths; reject unsupported types and oversize content; prevent normal traversal/symlink cases; avoid partial writes; reject unsafe ZIP members and expansion; return generic access errors.  
**Out of scope:** complete same-user race resistance on every OS, malware detection, robust detection of all polyglots, multi-process metadata database, authenticated user/tenant authorization, object-store IAM, and kernel/parser vulnerabilities. Add those in a production design.

### 7.2 `safe_storage.py`

Save the following as `safe_storage.py` in your lab directory.

```python
from __future__ import annotations

import io
import os
import re
import shutil
import stat
import tarfile
import tempfile
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from uuid import uuid4

ID_RE = re.compile(r"^[0-9a-f]{32}$")
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_ARCHIVE_BYTES = 10 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 100
MAX_MEMBER_BYTES = 2 * 1024 * 1024
MAX_EXPANDED_BYTES = 8 * 1024 * 1024
MAX_MEMBER_RATIO = 100

# This is intentionally narrow. Add a format only with explicit validation.
ALLOWED_TYPES = {"text/plain", "image/png"}


def detect_type(data: bytes) -> str:
    """Minimal lab sniffing, not a general-purpose file-type detector."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    # Reject NUL in this simple text policy; real text validation is format-specific.
    if b"\x00" not in data:
        try:
            data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            pass
        else:
            return "text/plain"
    raise ValueError("unsupported or unrecognized content")


def validate_id(upload_id: str) -> str:
    if not isinstance(upload_id, str) or not ID_RE.fullmatch(upload_id):
        raise ValueError("invalid upload ID")
    return upload_id


def _validate_member_name(name: str) -> str:
    """Accept flat, portable ZIP file names only; return the safe basename."""
    if not name or "\x00" in name or "\\" in name:
        raise ValueError("invalid archive member name")
    if unicodedata.normalize("NFC", name) != name:
        raise ValueError("archive name must use NFC Unicode normalization")
    if name.startswith("/") or PurePosixPath(name).is_absolute():
        raise ValueError("absolute archive path")
    win = PureWindowsPath(name)
    if win.drive or win.root or ":" in name:
        raise ValueError("drive, UNC, or alternate-stream syntax")
    parts = name.split("/")
    if len(parts) != 1 or parts[0] in ("", ".", ".."):
        raise ValueError("only flat regular files are supported")
    if any(part in (".", "..") for part in parts):
        raise ValueError("dot path component")
    if name.endswith((".", " ")):
        raise ValueError("non-portable trailing dot/space")
    if any(ord(ch) < 32 for ch in name):
        raise ValueError("control character in archive name")
    if len(name.encode("utf-8")) > 180:
        raise ValueError("archive member name too long")
    # Windows reserved device names are rejected even when running on POSIX.
    stem = name.split(".", 1)[0].upper()
    reserved = {"CON", "PRN", "AUX", "NUL"} | {
        f"COM{i}" for i in range(1, 10)
    } | {f"LPT{i}" for i in range(1, 10)}
    if stem in reserved:
        raise ValueError("reserved portable filename")
    return name


def _zip_is_regular_file(info: zipfile.ZipInfo) -> bool:
    # Unix mode type is stored in the upper 16 bits of external_attr.
    mode = (info.external_attr >> 16) & 0xFFFF
    kind = stat.S_IFMT(mode)
    # Many ZIP producers leave kind=0; accept that only as an ordinary entry.
    return kind in (0, stat.S_IFREG)


class SafeStorage:
    """Small ID-based storage helper for a trusted, private root directory."""

    def __init__(self, root: str | Path, *, max_upload_bytes: int = MAX_UPLOAD_BYTES):
        root_path = Path(root)
        root_path.mkdir(mode=0o700, parents=True, exist_ok=True)
        if root_path.is_symlink():
            raise ValueError("storage root must not be a symlink")
        self.root = root_path.resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("storage root must be a directory")
        self.max_upload_bytes = max_upload_bytes
        if max_upload_bytes <= 0:
            raise ValueError("max_upload_bytes must be positive")
        if os.name == "posix":
            self.root.chmod(0o700)

    def _path_for_id(self, upload_id: str) -> Path:
        valid_id = validate_id(upload_id)
        # The filename is entirely server-generated and contains no separators.
        candidate = self.root / valid_id
        if not candidate.is_relative_to(self.root):
            raise PermissionError("storage path escapes root")
        return candidate

    def save(self, data: bytes, *, declared_type: str, original_name: str = "") -> dict[str, str | int]:
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        if len(data) > self.max_upload_bytes:
            raise ValueError("upload too large")
        actual_type = detect_type(data)
        if declared_type not in ALLOWED_TYPES or declared_type != actual_type:
            raise ValueError("declared type does not match allowed detected type")
        # Keep only display metadata here; do not use it to build the disk path.
        display_name = Path(original_name.replace("\\", "/")).name
        if "\x00" in display_name:
            raise ValueError("invalid display name")
        # Remove control characters from display metadata; it never names a file.
        display_name = "".join(
            ch for ch in display_name if unicodedata.category(ch) not in {"Cc", "Cf"}
        )[:200]

        upload_id = uuid4().hex
        target = self._path_for_id(upload_id)
        fd, temp_name = tempfile.mkstemp(prefix=".upload-", dir=self.root)
        temp_path = Path(temp_name)
        try:
            if os.name == "posix":
                os.fchmod(fd, 0o600)
            stream = os.fdopen(fd, "wb")
            fd = -1  # ownership transferred to stream; never close a reused descriptor
            with stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            # Atomic replacement is safe only under the trusted-root assumption.
            # A hostile writer with access to this directory invalidates that assumption.
            os.replace(temp_path, target)
        except Exception:
            if fd >= 0:
                try:
                    os.close(fd)
                except OSError:
                    pass
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise
        return {
            "id": upload_id,
            "original_name": display_name,
            "content_type": actual_type,
            "size": len(data),
        }

    def load(self, upload_id: str) -> bytes:
        path = self._path_for_id(upload_id)
        # Defense in depth; this check alone is not race-free in a hostile directory.
        if path.is_symlink():
            raise PermissionError("symbolic links are not accepted")
        flags = os.O_RDONLY
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(path, flags)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise PermissionError("stored object is not a regular file")
            # A generated upload object should have exactly one directory link.
            # This detects ordinary hard-link substitution where st_nlink is meaningful.
            if getattr(info, "st_nlink", 1) != 1:
                raise PermissionError("hard-linked stored objects are not accepted")
            if info.st_size > self.max_upload_bytes:
                raise ValueError("stored object exceeds size policy")
            chunks: list[bytes] = []
            total = 0
            stream = os.fdopen(fd, "rb")
            fd = -1  # stream owns the descriptor from this point onward
            with stream:
                while True:
                    chunk = stream.read(min(64 * 1024, self.max_upload_bytes - total + 1))
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > self.max_upload_bytes:
                        raise ValueError("stored object exceeds size policy")
                    chunks.append(chunk)
            return b"".join(chunks)
        finally:
            if fd >= 0:
                os.close(fd)

    def extract_zip(self, archive: bytes, *, max_archive_bytes: int = MAX_ARCHIVE_BYTES) -> Path:
        """Extract flat regular files to a fresh private directory with strict limits."""
        if max_archive_bytes <= 0 or max_archive_bytes > MAX_ARCHIVE_BYTES:
            raise ValueError("configured archive limit must be within the global policy")
        if not isinstance(archive, bytes) or len(archive) > max_archive_bytes:
            raise ValueError("archive missing or too large")
        # Fresh output directory is created beneath the trusted storage root.
        out_dir = Path(tempfile.mkdtemp(prefix="extract-", dir=self.root))
        try:
            if os.name == "posix":
                out_dir.chmod(0o700)
            seen: set[str] = set()
            total_declared = 0
            with zipfile.ZipFile(__import__("io").BytesIO(archive)) as zf:
                infos = zf.infolist()
                if len(infos) > MAX_ARCHIVE_MEMBERS:
                    raise ValueError("too many archive members")
                for info in infos:
                    if info.is_dir():
                        raise ValueError("directory entries are not supported by flat extractor")
                    name = _validate_member_name(info.filename)
                    collision_key = unicodedata.normalize("NFC", name).casefold()
                    if collision_key in seen:
                        raise ValueError("duplicate or portable-normalization-colliding archive member")
                    seen.add(collision_key)
                    if not _zip_is_regular_file(info):
                        raise ValueError("links and special files are not accepted")
                    if info.flag_bits & 0x1:
                        raise ValueError("encrypted archive entries are not accepted")
                    if info.file_size > MAX_MEMBER_BYTES:
                        raise ValueError("archive member too large")
                    total_declared += info.file_size
                    if total_declared > MAX_EXPANDED_BYTES:
                        raise ValueError("archive expands beyond total limit")
                    if info.file_size and info.compress_size == 0:
                        raise ValueError("invalid compression metadata")
                    ratio = info.file_size / max(info.compress_size, 1)
                    if ratio > MAX_MEMBER_RATIO:
                        raise ValueError("compression ratio exceeds limit")

                    destination = out_dir / name
                    # 'xb' is exclusive; no archive entry may overwrite another file.
                    written = 0
                    with zf.open(info, "r") as source, destination.open("xb") as target:
                        if os.name == "posix":
                            os.fchmod(target.fileno(), 0o600)
                        while True:
                            chunk = source.read(64 * 1024)
                            if not chunk:
                                break
                            written += len(chunk)
                            if written > MAX_MEMBER_BYTES:
                                raise ValueError("actual member data exceeds limit")
                            if written + (total_declared - info.file_size) > MAX_EXPANDED_BYTES:
                                raise ValueError("actual archive data exceeds total limit")
                            target.write(chunk)
                        target.flush()
                        os.fsync(target.fileno())
                    if written != info.file_size:
                        raise ValueError("member size differs from declared size")
            return out_dir
        except Exception:
            shutil.rmtree(out_dir, ignore_errors=True)
            raise


def extract_tar_flat(archive: bytes, trusted_parent: Path) -> Path:
    if not isinstance(archive, bytes) or not archive or len(archive) > MAX_ARCHIVE_BYTES:
        raise ValueError("TAR input missing or too large")
    if trusted_parent.is_symlink() or not trusted_parent.is_dir():
        raise ValueError("trusted parent must be an existing, non-symlink directory")
    parent = trusted_parent.resolve(strict=True)
    out_dir = Path(tempfile.mkdtemp(prefix="tar-extract-", dir=parent))
    try:
        if os.name == "posix":
            out_dir.chmod(0o700)
        seen: set[str] = set()
        count = 0
        total_declared = 0
        total_written = 0
        # Streaming mode avoids materializing an unbounded getmembers() list.
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r|*") as tf:
            for member in tf:
                count += 1
                if count > MAX_ARCHIVE_MEMBERS:
                    raise ValueError("too many TAR members")
                if not member.isfile():
                    raise ValueError("TAR links, directories, and special files are not accepted")
                name = _validate_member_name(member.name)
                key = unicodedata.normalize("NFC", name).casefold()
                if key in seen:
                    raise ValueError("duplicate or portable-normalization-colliding TAR member")
                seen.add(key)
                if member.size < 0 or member.size > MAX_MEMBER_BYTES:
                    raise ValueError("TAR member too large")
                total_declared += member.size
                if total_declared > MAX_EXPANDED_BYTES:
                    raise ValueError("TAR expands beyond total limit")
                if total_declared / max(len(archive), 1) > MAX_MEMBER_RATIO:
                    raise ValueError("TAR expansion ratio exceeds policy")
                if hasattr(tarfile, "data_filter"):
                    # Defense in depth on Python 3.12+; manual policy remains mandatory.
                    if tarfile.data_filter(member, str(out_dir)) is None:
                        raise ValueError("TAR member rejected by data filter")
                source = tf.extractfile(member)
                if source is None:
                    raise ValueError("TAR member has no regular-file payload")
                destination = out_dir / name
                written = 0
                with source, destination.open("xb") as target:
                    if os.name == "posix":
                        os.fchmod(target.fileno(), 0o600)
                    while True:
                        chunk = source.read(64 * 1024)
                        if not chunk:
                            break
                        written += len(chunk)
                        total_written += len(chunk)
                        if written > MAX_MEMBER_BYTES or total_written > MAX_EXPANDED_BYTES:
                            raise ValueError("actual TAR expansion exceeds limit")
                        target.write(chunk)
                    target.flush()
                    os.fsync(target.fileno())
                if written != member.size:
                    raise ValueError("TAR member size differs from declared size")
        return out_dir
    except Exception:
        shutil.rmtree(out_dir, ignore_errors=True)
        raise
```

**Implementation notes and boundaries:**

- The root directory must be provisioned and owned by the service account; `chmod(0o700)` does not fix malicious ownership or ACLs.
- `original_name` is display metadata only. In production, store it in a database and apply safe response-header encoding when downloading.
- The lab's `detect_type()` is deliberately minimal and should not be used as a universal detector. Add actual parsers/validators for formats you accept.
- `os.replace()` is atomic on typical local filesystems, but may replace an existing destination and is not a cross-platform guarantee against an attacker who can mutate the root. A production implementation that must defend against hostile concurrent writers should use directory descriptors and exclusive creation where supported, or an isolated storage service.
- `O_NOFOLLOW` protects the final component on platforms that implement it; the preceding `is_symlink()` is not a race-free substitute. The opened descriptor is checked with `fstat()`.
- This lab deliberately rejects nested ZIP entries, directory entries, and all link/special-file types. The strict flat policy is easier to reason about than trying to emulate every OS path rule.
- Archive expansion is limited by declared metadata and actual streamed bytes. ZIP parsing itself can consume resources before member iteration; cap archive input bytes and process it in a constrained worker for hostile production traffic.

### 7.3 `test_safe_storage.py`

Save the following as `test_safe_storage.py` beside `safe_storage.py`.

```python
import io
import os
import stat
import tarfile
import zipfile

import pytest

from safe_storage import SafeStorage, extract_tar_flat, validate_id


def zip_bytes(entries):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries:
            zf.writestr(name, data)
    return buf.getvalue()


def tar_bytes(entries):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for name, data in entries:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_save_and_load_legitimate_text(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    metadata = storage.save(
        b"hello, safe storage\n",
        declared_type="text/plain",
        original_name="../../display-only.txt",
    )
    assert storage.load(metadata["id"]) == b"hello, safe storage\n"
    assert metadata["original_name"] == "display-only.txt"
    assert (tmp_path / "private" / metadata["id"]).is_file()


def test_rejects_invalid_ids(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    for value in ("../secret", "/etc/passwd", "C:\\Windows\\win.ini", "\\\\server\\share", "%2e%2e%2fsecret", "%252e%252e%252fsecret", "a" * 31, "A" * 32, ""):
        with pytest.raises(ValueError):
            storage.load(value)


def test_display_filename_metadata_removes_control_and_format_characters(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    metadata = storage.save(
        b"text",
        declared_type="text/plain",
        original_name="report\n\u202e.txt",
    )
    assert metadata["original_name"] == "report.txt"


def test_rejects_mismatched_declared_type(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    with pytest.raises(ValueError):
        storage.save(b"plain text", declared_type="image/png", original_name="x.png")


def test_rejects_oversize_upload(tmp_path):
    storage = SafeStorage(tmp_path / "private", max_upload_bytes=4)
    with pytest.raises(ValueError, match="too large"):
        storage.save(b"12345", declared_type="text/plain")


def test_rejects_zip_traversal(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    archive = zip_bytes([("../escaped.txt", b"no")])
    with pytest.raises(ValueError):
        storage.extract_zip(archive)
    assert not (tmp_path / "escaped.txt").exists()


@pytest.mark.parametrize("name", [
    "/absolute.txt", "..\\escape.txt", "C:/Windows/win.ini",
    "\\\\server\\share\\file.txt", "folder/nested.txt", "NUL.txt",
    "stream.txt:secret", "trailing.", "trailing ",
])
def test_rejects_nonportable_or_nonflat_zip_names(tmp_path, name):
    storage = SafeStorage(tmp_path / "private")
    archive = zip_bytes([(name, b"data")])
    with pytest.raises((ValueError, OSError, zipfile.BadZipFile)):
        storage.extract_zip(archive)


def test_accepts_small_flat_zip(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    extracted = storage.extract_zip(zip_bytes([("one.txt", b"one"), ("two.txt", b"two")]))
    assert sorted(p.name for p in extracted.iterdir()) == ["one.txt", "two.txt"]
    assert (extracted / "one.txt").read_bytes() == b"one"


def test_member_validator_rejects_null_byte():
    from safe_storage import _validate_member_name
    with pytest.raises(ValueError):
        _validate_member_name("bad\x00name.txt")


def test_rejects_duplicate_member_names(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    archive = zip_bytes([("same.txt", b"a"), ("same.txt", b"b")])
    with pytest.raises(ValueError, match="duplicate"):
        storage.extract_zip(archive)


def test_rejects_member_count_limit(tmp_path, monkeypatch):
    import safe_storage
    monkeypatch.setattr(safe_storage, "MAX_ARCHIVE_MEMBERS", 1)
    storage = SafeStorage(tmp_path / "private")
    archive = zip_bytes([("one.txt", b"x"), ("two.txt", b"y")])
    with pytest.raises(ValueError, match="too many"):
        storage.extract_zip(archive)


def test_rejects_archive_input_size_limit(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    archive = zip_bytes([("one.txt", b"small")])
    with pytest.raises(ValueError, match="too large"):
        storage.extract_zip(archive, max_archive_bytes=4)


def test_rejects_per_member_expansion_limit(tmp_path, monkeypatch):
    import safe_storage
    monkeypatch.setattr(safe_storage, "MAX_MEMBER_BYTES", 3)
    storage = SafeStorage(tmp_path / "private")
    archive = zip_bytes([("one.txt", b"four")])
    with pytest.raises(ValueError, match="member too large"):
        storage.extract_zip(archive)


def test_rejects_total_expansion_limit(tmp_path, monkeypatch):
    import safe_storage
    monkeypatch.setattr(safe_storage, "MAX_EXPANDED_BYTES", 3)
    storage = SafeStorage(tmp_path / "private")
    archive = zip_bytes([("one.txt", b"ab"), ("two.txt", b"cd")])
    with pytest.raises(ValueError, match="total limit"):
        storage.extract_zip(archive)


def test_failed_extraction_cleans_partial_output(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    before = set(storage.root.iterdir())
    archive = zip_bytes([("first.txt", b"ok"), ("../escape.txt", b"no")])
    with pytest.raises(ValueError):
        storage.extract_zip(archive)
    assert set(storage.root.iterdir()) == before


def test_rejects_symlink_entry_when_unix_metadata_is_present(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        info = zipfile.ZipInfo("link.txt")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        zf.writestr(info, "../outside.txt")
    with pytest.raises(ValueError, match="links"):
        storage.extract_zip(buf.getvalue())


def test_rejects_zip_bomb_by_compression_ratio(tmp_path, monkeypatch):
    import safe_storage
    monkeypatch.setattr(safe_storage, "MAX_MEMBER_RATIO", 2)
    storage = SafeStorage(tmp_path / "private")
    # Repeated text compresses extremely well and exceeds the ratio policy.
    archive = zip_bytes([("repeated.txt", b"A" * 10_000)])
    with pytest.raises(ValueError, match="ratio"):
        storage.extract_zip(archive)


def test_rejects_symlinked_stored_object_when_supported(tmp_path):
    if not hasattr(os, "symlink"):
        pytest.skip("symlinks unavailable")
    storage = SafeStorage(tmp_path / "private")
    outside = tmp_path / "outside"
    outside.write_bytes(b"not for reading")
    fake_id = "a" * 32
    link = storage.root / fake_id
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted")
    with pytest.raises((PermissionError, OSError)):
        storage.load(fake_id)


def test_rejects_casefold_colliding_zip_names(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    archive = zip_bytes([("Report.txt", b"a"), ("report.txt", b"b")])
    with pytest.raises(ValueError, match="duplicate"):
        storage.extract_zip(archive)


def test_rejects_non_nfc_zip_member_name(tmp_path):
    storage = SafeStorage(tmp_path / "private")
    # 'é' represented as e + combining acute accent (not NFC).
    archive = zip_bytes([("e\u0301.txt", b"data")])
    with pytest.raises(ValueError, match="NFC"):
        storage.extract_zip(archive)


def test_extracts_safe_flat_tar(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    extracted = extract_tar_flat(tar_bytes([("one.txt", b"one"), ("two.txt", b"two")]), parent)
    assert sorted(p.name for p in extracted.iterdir()) == ["one.txt", "two.txt"]
    assert (extracted / "one.txt").read_bytes() == b"one"


def test_rejects_tar_traversal_and_cleans_partial_output(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    before = set(parent.iterdir())
    archive = tar_bytes([("first.txt", b"ok"), ("../escaped.txt", b"no")])
    with pytest.raises(ValueError):
        extract_tar_flat(archive, parent)
    assert set(parent.iterdir()) == before
    assert not (tmp_path / "escaped.txt").exists()


def test_rejects_tar_symlink(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        link = tarfile.TarInfo("link.txt")
        link.type = tarfile.SYMTYPE
        link.linkname = "../outside.txt"
        tf.addfile(link)
    with pytest.raises(ValueError, match="links"):
        extract_tar_flat(buf.getvalue(), parent)


def test_rejects_hardlinked_stored_object_when_supported(tmp_path):
    if not hasattr(os, "link"):
        pytest.skip("hard links unavailable")
    storage = SafeStorage(tmp_path / "private")
    outside = tmp_path / "outside-hardlink-fixture"
    outside.write_bytes(b"temporary test fixture only")
    fake_id = "b" * 32
    try:
        os.link(outside, storage.root / fake_id)
    except (OSError, NotImplementedError):
        pytest.skip("hard-link creation not permitted")
    with pytest.raises(PermissionError, match="hard-linked"):
        storage.load(fake_id)


def test_rejects_tar_member_count_limit(tmp_path, monkeypatch):
    import safe_storage
    monkeypatch.setattr(safe_storage, "MAX_ARCHIVE_MEMBERS", 1)
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    with pytest.raises(ValueError, match="too many"):
        extract_tar_flat(tar_bytes([("one.txt", b"1"), ("two.txt", b"2")]), parent)


def test_rejects_tar_member_size_limit(tmp_path, monkeypatch):
    import safe_storage
    monkeypatch.setattr(safe_storage, "MAX_MEMBER_BYTES", 3)
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    with pytest.raises(ValueError, match="member too large"):
        extract_tar_flat(tar_bytes([("large.txt", b"four")]), parent)


def test_rejects_tar_total_expansion_limit(tmp_path, monkeypatch):
    import safe_storage
    monkeypatch.setattr(safe_storage, "MAX_EXPANDED_BYTES", 3)
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    with pytest.raises(ValueError, match="total limit"):
        extract_tar_flat(tar_bytes([("one.txt", b"ab"), ("two.txt", b"cd")]), parent)


def test_rejects_tar_high_expansion_ratio(tmp_path, monkeypatch):
    import safe_storage
    monkeypatch.setattr(safe_storage, "MAX_MEMBER_RATIO", 1)
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    with pytest.raises(ValueError, match="ratio"):
        extract_tar_flat(tar_bytes([("repeated.txt", b"A" * 10_000)]), parent)


def test_posix_storage_permissions_are_restrictive(tmp_path):
    if os.name != "posix":
        pytest.skip("POSIX mode assertion")
    storage = SafeStorage(tmp_path / "private")
    meta = storage.save(b"secret", declared_type="text/plain")
    assert stat.S_IMODE(storage.root.stat().st_mode) & 0o077 == 0
    assert stat.S_IMODE((storage.root / meta["id"]).stat().st_mode) & 0o077 == 0
```

The tests assert both accepted legitimate cases and rejected malicious inputs. They do not prove resistance to every filesystem race or every archive-parser vulnerability.

### 7.4 Run the lab

```console
python -m pytest -q
```

Run on each supported operating system. Do not copy test output into documentation unless you actually ran it in that environment. Add CI jobs for supported Python versions and Windows/POSIX platforms. If Hypothesis is installed, add property-based tests below.

## 8. TAR policy example and platform-aware implementation choice

The main `SafeStorage` lab accepts ZIP only. If TAR support is not required, reject TAR uploads. If it is required, do not call `extractall()` on untrusted data and hope that `filter="data"` is enough. Python 3.12+ provides `tarfile.data_filter` / `filter="data"` as an additional path/link-safety layer, but that filter is not a count, byte, compression-ratio, CPU, or memory limit. The `extract_tar_flat()` helper included at the end of `safe_storage.py` streams **flat regular files only**, rejects links and special files, applies `data_filter` where available, bounds archive/member/total sizes and count, and cleans up partial output. It still assumes the trusted parent and its ancestors cannot be modified by an attacker, and hostile parsing must run under OS resource limits.

Example call after adding the helper to `safe_storage.py`:

```python
from pathlib import Path
from safe_storage import extract_tar_flat

# `archive_bytes` must already have been read with an input-size limit.
# The parent must be provisioned, private, and not writable by attackers.
extracted_dir = extract_tar_flat(archive_bytes, Path("/srv/private-staging"))
```

The ratio is a conservative archive-wide expanded-bytes/input-bytes ratio; tune it against legitimate corpora. It does not bound decompression CPU by itself. `tarfile.data_filter` is applied only where available (Python 3.12+), while the explicit policy rejects links/special files on every supported version. Test this helper on every supported Python/OS version and execute it in a constrained worker. Never silently fall back to unrestricted `extractall()`.

## 9. Regression matrix, property tests, fuzzing

### 9.1 Malicious path test matrix

| Input or condition | Expected policy |
|---|---|
| `../secret.txt`, `../../etc/passwd` | Reject if treated as a path; ID API rejects as invalid ID. |
| `/etc/passwd`, `\rooted`, `C:\Windows\win.ini`, `C:relative` | Reject absolute/rooted/drive-qualified paths. |
| `\\server\share\file` | Reject UNC path. |
| `%2e%2e%2fsecret`, `%252e%252e%252fsecret` | Decode only at protocol boundary; then reject traversal or reject because input is not an ID. |
| `..\..//secret`, mixed slash styles | Reject ambiguous separators in path/archive policy. |
| `name\x00.txt` | Reject before OS calls. |
| `uploads/link -> outside` | Reject symlink or use descriptor-based access; race test separately. |
| Hard link to an outside-reachable inode | Do not assume `is_symlink()` detects it; enforce trusted directory ownership and appropriate inode/ownership policy. |
| `folder/../../secret`, `/absolute`, `C:/...` in ZIP member | Reject before writing. |
| ZIP symlink/device entry, duplicate normalized names | Reject. |
| Too many entries, huge expansion, high ratio, oversized single member | Reject before or during streaming. |
| Long name, control characters, `NUL`, trailing dot/space, `name:stream` | Reject under portable filename policy. |
| Legitimate ID, small allowed content, flat safe ZIP | Accept. |

URL encodings are not inherently filesystem paths. The test must reflect the actual application boundary: if a request framework already decodes a URL, test the decoded string; if the value is an opaque storage ID, the validator should reject it regardless of encoding.

### 9.2 Property-based testing with Hypothesis

```python
from hypothesis import given, strategies as st
import pytest

from safe_storage import validate_id


@given(st.text())
def test_only_exact_lowercase_hex_ids_are_accepted(value):
    if len(value) == 32 and all(ch in "0123456789abcdef" for ch in value):
        assert validate_id(value) == value
    else:
        with pytest.raises(ValueError):
            validate_id(value)


@given(st.text())
def test_any_non_id_string_is_rejected(value):
    # This independent property catches accidental acceptance of traversal strings.
    if not (len(value) == 32 and all(ch in "0123456789abcdef" for ch in value)):
        with pytest.raises(ValueError):
            validate_id(value)
```

The two properties overlap intentionally as a simple example; in a real suite, avoid redundant tests and add generators for path separators, Unicode normalization, encoded payloads, long names, and archive member metadata. Property tests do not replace explicit regression tests for known bugs.

For archive fuzzing, generate ZIP/TAR metadata combinations, truncated archives, duplicate names, unusual encodings, link types, and inconsistent size declarations. Run fuzzers only against your own parser/helper in an isolated temporary directory. Assert invariants: no file appears outside the fresh destination; all created files are regular files; total bytes and entry count remain bounded; a rejected archive leaves no partial extraction directory. Treat crashes, timeouts, and resource-limit failures as findings.

### 9.3 Regression test expectations

At minimum, tests should prove:

- Valid uploads save and load through IDs.
- Traversal/absolute/drive/UNC IDs are rejected.
- MIME mismatch, unsupported content, and oversize uploads are rejected.
- A symlinked object is rejected where the platform can create/test symlinks.
- Safe ZIP extraction works; traversal, link, duplicate, excessive-count, excessive-size, and excessive-ratio archives are rejected.
- Failed extraction cleans up its fresh output directory.
- POSIX file and directory modes are restrictive; Windows ACL checks are tested separately.
- Cross-tenant authorization is tested at the API/service layer (the small `SafeStorage` class does not implement tenant authorization).

## 10. Local hands-on lab

1. Save `safe_storage.py` and `test_safe_storage.py` in a clean directory.
2. Install `pytest` and run the test suite.
3. Add a test for `C:relative`, `%2e%2e%2fsecret`, and a very long ID. Confirm the ID-only interface rejects them.
4. Add a valid PNG fixture beginning with the PNG signature, then add a parser-level validation requirement appropriate for your actual application. Explain why signature-only acceptance is not enough.
5. Create a ZIP with a traversal member and prove no file is created outside the extraction directory.
6. Create a ZIP with a Unix symlink entry and verify rejection. Skip only when the environment cannot construct the fixture, and record that limitation.
7. Verify file and directory modes on POSIX; design an equivalent ACL verification step for Windows rather than assuming `chmod` is equivalent.
8. Explain in a short threat-model note who can write the storage root, who owns each object, how IDs are authorized, and what happens if the process crashes mid-write.
9. Add limits for archive input bytes, member count, per-file bytes, total expanded bytes, and ratio. Demonstrate at least one rejection test for each.
10. Run tests on every supported OS/Python version. Document unsupported features and residual risks.

### Expected outcomes

- The test suite accepts legitimate, bounded inputs and rejects the explicit malicious cases.
- The storage path is generated from a strict opaque ID, not from a user filename.
- The archive extractor writes only flat regular files into a newly created private directory and removes partial output after failure.
- The learner can explain why the portable implementation still relies on a trusted root and why `resolve()` plus `open()` is not a universal race-free primitive.
- The threat model distinguishes path validation, authorization, OS permissions, resource limits, and parser isolation.

## Common mistakes to avoid

- Using `os.path.join(base, user_input)` and assuming the result stays under `base`.
- Using string `startswith()` for containment.
- Calling `resolve()` and then assuming a later `open()` cannot race.
- Trusting `is_symlink()` to detect hard links or all Windows reparse points.
- Trusting extensions, MIME headers, archive metadata, or declared uncompressed sizes alone.
- Calling `extractall()` on untrusted archives without a version-aware policy and resource limits.
- Extracting into an existing directory or the application code/web root.
- Using `mktemp()`, predictable temporary names, or check-then-create patterns.
- Treating a UUID as authorization or tenant isolation.
- Assuming `chmod(0o600)` fully configures Windows ACLs.
- Treating an object-store prefix as a local path or as an authorization boundary.
- Assuming file-type sniffing, malware scanning, or a container alone guarantees safe parsing.

## Self-check with answers

**1. Why can `Path('/base') / '/etc/passwd'` escape the base?**  
Because an absolute right-hand path replaces the earlier path. Reject absolute/rooted/drive-qualified input, or better, accept only server-generated IDs.

**2. Why does `startswith()` fail for containment?**  
It compares characters, not path components. `/srv/uploads-evil` begins with `/srv/uploads` textually but is a sibling. Resolve paths and use component-aware containment, while accounting for TOCTOU and platform behavior.

**3. Why is `resolve()` followed by `open()` not race-free?**  
A process with write access to a directory can replace a component or symlink between the check and use. Use trusted non-writable directories, directory descriptors and relative operations, supported no-follow/exclusive flags, and/or OS-level isolation.

**4. What does `O_NOFOLLOW` guarantee?**  
Where supported, it normally rejects following a symlink at the final path component. It does not make arbitrary intermediate path traversal safe, is not available everywhere, and does not replace descriptor checks or directory permissions.

**5. Why are archive member paths a separate validation problem?**  
Archive names use their own conventions and metadata, may encode links/special files, and can expand dramatically. Validate each member and type, reject dangerous links, enforce actual streamed limits, and extract into a fresh private directory.

**6. Is `tarfile`'s `filter="data"` enough?**  
No. It is a useful path/link safety layer on supported Python versions, but application-specific member/count/size/ratio/CPU limits and isolation remain necessary. Older versions need a tested alternative or should reject TAR.

**7. What is the difference between atomicity and durability?**  
Atomic replacement prevents readers from seeing a partially written name under supported filesystem semantics. Durability after a crash may require syncing the file and containing directory. Neither property alone prevents authorization mistakes or hostile directory races.

**8. Why is a UUID not an access-control check?**  
IDs can leak, be logged, or be guessed eventually; authorization must verify the requesting principal's rights and tenant ownership for every operation.

## Completion checklist

- [ ] I can explain path traversal and distinguish lexical paths from resolved filesystem objects.
- [ ] I reject absolute, drive/UNC, parent, null-byte, encoded, and mixed-separator inputs at the correct boundary.
- [ ] I do not use string-prefix containment checks.
- [ ] I use server-generated IDs and store original filenames only as metadata.
- [ ] I understand file modes, `umask`, ACL differences, secure temp files, and atomic writes.
- [ ] I can describe TOCTOU, symlink, hardlink, and platform limitations accurately.
- [ ] My archive policy rejects unsafe paths/types and enforces member and expansion limits.
- [ ] Uploads/downloads enforce authorization, quotas, content validation, safe headers, and storage isolation.
- [ ] I can explain capability-style APIs, Linux `openat2`, container hardening, and object-store key risks.
- [ ] My tests cover malicious and legitimate cases, resource limits, cleanup, and residual risks.
- [ ] I documented the threat model and did not claim guarantees the implementation cannot provide.

## References for further study

- Python `pathlib` documentation: `Path.resolve()` and `Path.is_relative_to()`.
- Python `os` documentation: `open`, `O_NOFOLLOW`, `O_EXCL`, `dir_fd`, and platform support sets.
- Python `tempfile` documentation: secure temporary file and directory creation.
- Python `zipfile` and `tarfile` documentation, including TAR extraction filters and version-specific behavior.
- Linux `openat2(2)` manual page and resolution flags.
- OWASP File Upload Cheat Sheet and path traversal testing guidance.
- Your operating system's documentation for ACLs, reparse points, filesystem quotas, and sandboxing.

Always verify documentation for the exact Python version and OS deployed. Security behavior depends on runtime version, filesystem, mount options, process privileges, and the application's actual trust boundaries.
