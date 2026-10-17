# Base64, zlib, gzip, and Stream Compression

**Stage 1 · Module 14 — Bytes, Binary Data and Advanced Text Processing**  
**Target:** Python 3.12+; Python 3.13/3.14 differences and optional third-party codecs are labelled explicitly.

## Learning outcomes

By the end of this lesson, you should be able to:

- Encode bytes as Base64, URL-safe Base64, Base32, Base16, and Ascii85; explain bytes-versus-text conversion, padding, expansion, and why encoding is not encryption.
- Select and use `zlib`, `gzip`, `bz2`, and `lzma` for whole-buffer and streaming compression.
- Process compressed files in chunks, line by line, or through a bounded pipeline without accumulating the full output in memory.
- Enforce absolute decompressed-byte limits and expansion-ratio limits on untrusted streams; distinguish a complete stream from a truncated one.
- Explain gzip concatenated members, HTTP `Content-Encoding`, checksums versus cryptographic hashes, codec trade-offs, splitability, and compression side channels.
- Benchmark realistic data, inspect error cases, and choose a format based on compatibility, latency, CPU, memory, and downstream processing requirements.

## Prerequisites

You should understand `str` versus `bytes`, explicit text encodings, binary file modes (`rb`/`wb`), context managers, exceptions, generators, and basic file I/O. Earlier lessons in this module cover byte buffers and checksums. You do **not** need `mmap` or `struct` to complete this lesson; they are adjacent topics rather than the focus here.

---

## 1. Encoding is not compression, and neither is encryption

These solve different problems:

- **Encoding** maps data into a representation accepted by a channel or format. Base64 maps arbitrary bytes to ASCII characters; it normally makes data larger.
- **Compression** represents redundancy more compactly. It may shrink repetitive text substantially and may slightly expand already-compressed or random data.
- **Encryption** uses a cryptographic key to provide confidentiality. Base64 and compression provide no confidentiality.

A typical pipeline may encode a compressed binary payload for a JSON field, but both transformations are reversible without a secret. Anyone who obtains Base64 text can decode it.

## 2. Base encodings

The functions in `base64` accept bytes-like input and return **`bytes`**. JSON, HTTP headers, and most text protocols need `str`, so decode the result with ASCII. Do not decode arbitrary binary content as UTF-8; encode it first.

```python
import base64

raw = b"data engineering"
encoded = base64.b64encode(raw)
print(encoded)                         # b'ZGF0YSBlbmdpbmVlcmluZw=='
print(encoded.decode("ascii"))        # ZGF0YSBlbmdpbmVlcmluZw==
print(base64.b64decode(encoded))       # b'data engineering'
print(len(encoded), len(raw))          # 24 16
```

### Common APIs

| API | Purpose | Important detail |
| --- | --- | --- |
| `base64.b64encode(data)` / `b64decode(data)` | Standard Base64 | Output is bytes; encoded length is usually `4 * ceil(n / 3)` bytes, including `=` padding. |
| `urlsafe_b64encode(data)` / `urlsafe_b64decode(data)` | URL/file-name-friendly alphabet | Replaces `+` and `/` with `-` and `_`; padding may still be present. |
| `b32encode` / `b32decode` | Base32 | Larger than Base64; useful where a restricted alphabet matters. |
| `b16encode` / `b16decode` | Hex-like Base16 | Two output characters per input byte; `b16decode` is strict by default. |
| `a85encode` / `a85decode` | Ascii85 | Usually denser than Base64, but variant/framing options and interoperability need care. |
| `b85encode` / `b85decode` | Base85 variant | Distinct from Ascii85; do not assume the variants are interchangeable. |

```python
import base64

sample = b"\x00\xffA"
print(base64.b16encode(sample))        # b'00FF41'
print(base64.b32encode(b"cat"))       # b'MNQXI==='
print(base64.urlsafe_b64encode(b"?/?"))  # b'Py8_'
print(base64.a85encode(b"hello"))       # b'BOu!rDZ'
```

Exact Ascii85/Base85 text depends on the chosen function and options; for protocols, document the alphabet, padding, framing, and whitespace rules rather than treating the labels as synonyms.

### Padding, validation, and URL-safe tokens

Base64 encodes groups of 3 input bytes as 4 output characters. One or two leftover input bytes are padded with `=` characters. Some token formats omit padding, but that is a protocol convention—not a universal property of URL-safe Base64. Restore the expected padding only when the protocol specifies that behavior.

```python
import base64

def decode_unpadded_urlsafe(token: str, *, max_chars: int = 4096) -> bytes:
    # Example policy for a protocol that explicitly omits '=' padding.
    # The caller should set max_chars to the protocol's actual token limit.
    if max_chars < 0:
        raise ValueError("max_chars must be non-negative")
    if len(token) > max_chars:
        raise ValueError("encoded token is too long")
    if not token.isascii():
        raise ValueError("token must be ASCII")
    if len(token) % 4 == 1:
        raise ValueError("invalid unpadded Base64 length")
    token_bytes = token.encode("ascii")
    token_bytes += b"=" * (-len(token_bytes) % 4)
    return base64.b64decode(token_bytes, altchars=b"-_", validate=True)

assert decode_unpadded_urlsafe("Y2F0") == b"cat"
```

`validate=True` rejects non-alphabet characters for standard Base64 decoding instead of silently discarding them. URL-safe alphabets require appropriate handling of `-` and `_`; validate according to the exact wire protocol. Do not mistake syntactic validity for authenticity, authorization, or safe content. Always impose a maximum encoded-input length before decoding, because decoding allocates output.

### Size overhead and practical limits

- Base64: about **33⅓%** overhead for large inputs, plus up to two `=` characters and surrounding JSON syntax.
- Base32: about 60% overhead for large inputs.
- Hex/Base16: 100% overhead (two characters per byte).
- Base85/Ascii85: roughly 25% overhead for large inputs, with variant-specific details.

The exact encoded size includes padding and depends on input length. For example, 1 MiB of binary data becomes approximately 1.33 MiB of Base64 text. That can exceed API request-body limits, database column limits, URL length limits, proxy limits, or logging budgets. Prefer binary uploads or object storage for large blobs instead of embedding them in JSON or URLs. Never put sensitive payloads into URLs or logs merely because they are encoded.

---

## 3. Standard-library compression tools

Compression is not guaranteed to shrink every input. Random bytes, JPEG/PNG, ZIP, many media files, and already-compressed payloads may grow slightly due to framing and metadata.

| Module/API | Typical use | Strengths | Trade-offs and cautions |
| --- | --- | --- | --- |
| `zlib` | zlib-wrapped streams; DEFLATE primitives | Fast, widely supported; exposes streaming objects | Wrapper format matters (`zlib`, raw DEFLATE, and gzip are not interchangeable without the right `wbits`). |
| `gzip` | `.gz`, HTTP gzip bodies | Very interoperable; file-like API; concatenated gzip members supported by `gzip` readers | DEFLATE-based; not generally independently splittable at arbitrary byte offsets. |
| `bz2` | `.bz2` archives and files | Often good ratio on text | Usually slower and more CPU-intensive than gzip. |
| `lzma` / XZ | `.xz` and LZMA streams | Often high compression ratio | Can be CPU- and memory-intensive; untrusted inputs need strict resource limits. |
| `compression.zstd` | Zstandard in the standard library | Modern codec with good speed/ratio options | **Python 3.14+** standard library only; check exact API and interoperability needs. |
| `zstandard` | Zstandard before Python 3.14 or for richer features | Mature third-party implementation; dictionaries/advanced options | Third-party dependency; pin and test versions. |
| `lz4` | Very fast compression/decompression | Low latency and high throughput | Third-party package; ratio may be lower. |
| `snappy` | Fast data-engineering pipelines | Low overhead, widely used in data formats | Third-party bindings; availability depends on platform/package. |

**Version and dependency notes**

- **Python 3.12 and 3.13:** no standard-library `compression.zstd`; use a pinned third-party `zstandard` package if Zstandard is required.
- **Python 3.14+:** `compression.zstd` was added to the standard library. It provides file, one-shot, and incremental APIs, but the module can be absent from some distributor builds; verify availability in the deployed interpreter. Its API is not identical to the third-party `zstandard` package.
- `lz4` and `python-snappy` are third-party packages (the latter is commonly imported as `snappy`). Install and pin them explicitly; binary wheels and platform support vary.
- Parquet, Arrow, and other data systems may support codecs through their own libraries; availability is not implied by Python itself.

### Whole-buffer APIs (small, trusted data only)

```python
import gzip
import zlib
import bz2
import lzma

raw = b"status=ok\n" * 100

z = zlib.compress(raw, level=6)
g = gzip.compress(raw, compresslevel=6, mtime=0)
b = bz2.compress(raw, compresslevel=9)
x = lzma.compress(raw, preset=6)

assert zlib.decompress(z) == raw
assert gzip.decompress(g) == raw
assert bz2.decompress(b) == raw
assert lzma.decompress(x) == raw
print(len(raw), len(z), len(g), len(b), len(x))
```

`zlib.compress` supports levels 0–9; level 0 stores without meaningful compression, 1 favors speed, and 9 favors ratio at additional CPU cost. `gzip.compress` exposes `compresslevel` 0–9. `bz2` levels are 1–9. `lzma` presets are 0–9 (higher usually means more work/memory). Use defaults or benchmark representative inputs before hard-coding a level. Compression level is not a universal “quality” scale across codecs.

Whole-buffer functions hold the input and output in memory. Do not use `gzip.decompress`, `zlib.decompress`, `bz2.decompress`, or `lzma.decompress` on untrusted data without a carefully enforced size bound. For hostile inputs, prefer bounded streaming and process-level resource limits.

### `gzip.open`: binary and text modes

```python
import gzip
import json
from pathlib import Path

path = Path("events.jsonl.gz")
with gzip.open(path, "wt", encoding="utf-8", newline="\n") as stream:
    stream.write(json.dumps({"id": 1}) + "\n")
    stream.write(json.dumps({"id": 2}) + "\n")

with gzip.open(path, "rt", encoding="utf-8") as stream:
    for line in stream:                 # line-by-line; no whole-file read
        record = json.loads(line)
        print(record["id"])

with gzip.open(path, "rb") as stream:
    prefix = stream.read(16)             # decompressed bytes
    print(prefix)
```

`"wt"`/`"rt"` add text encoding and newline handling; `"wb"`/`"rb"` expose decompressed bytes. Use explicit encodings for text. The context manager closes/finalizes the gzip stream. In production, keep compressed and uncompressed byte counts and limits separate.

### Streaming compression with `compressobj`

```python
import zlib

parts = [b"alpha\n", b"beta\n", b"gamma\n"]
compressor = zlib.compressobj(level=6)
encoded_parts = []
for part in parts:
    encoded_parts.append(compressor.compress(part))
encoded_parts.append(compressor.flush())  # finish the stream exactly once
blob = b"".join(encoded_parts)
assert zlib.decompress(blob) == b"".join(parts)
print(len(blob) < sum(map(len, parts)))  # False: tiny inputs can grow
```

`compress()` may return `b""` until enough data accumulates. Always finish a stream with `flush()` when you own the compression stream; do not call `compress()` again after finalization. The example joins outputs only because it demonstrates a tiny in-memory value. A real file pipeline writes each returned chunk immediately.

### `gzip.GzipFile` and `shutil.copyfileobj`

```python
import gzip
import shutil

with open("input.bin", "rb") as source:
    with open("output.bin.gz", "wb") as raw_destination:
        with gzip.GzipFile(fileobj=raw_destination, mode="wb", compresslevel=6, mtime=0) as compressor:
            shutil.copyfileobj(source, compressor, length=1024 * 1024)
```

`shutil.copyfileobj` copies in chunks; its `length` argument is the buffer size used for copying, **not** a total-byte limit. It does not enforce a decompressed-size cap. For deterministic gzip metadata, `mtime=0` avoids embedding the current timestamp; reproducibility can still depend on Python/zlib versions and gzip header details.

### Incremental decompression: basic trusted-input pattern

```python
import zlib

obj = zlib.decompressobj()
with open("payload.zlib", "rb") as source, open("payload.out", "wb") as target:
    for chunk in iter(lambda: source.read(64 * 1024), b""):
        target.write(obj.decompress(chunk))
    if not obj.eof:
        raise EOFError("compressed stream ended before its end marker")
    if obj.unused_data:
        raise ValueError("unexpected trailing bytes after the zlib stream")
```

This is incremental, but **not bounded against decompression bombs**: one `decompress(chunk)` call can return a very large object. Use the next section for untrusted inputs. Do not append every output chunk to one ever-growing `bytearray` or list if the goal is constant-memory processing.

---

## 4. Bounded decompression for untrusted streams

A compressed-size limit alone is not enough: a small input can expand enormously. A robust pipeline needs at least:

1. A maximum compressed-input size (enforced by the caller/transport).
2. An **absolute output limit** in bytes.
3. An optional expansion-ratio limit, with a clearly defined denominator.
4. Chunked reads and writes; no unbounded output accumulation.
5. Explicit stream-completion checks (`eof`) and a policy for trailing bytes / concatenated members.
6. CPU/time limits at the service or process boundary when inputs are hostile.

The code below demonstrates a single **zlib-wrapped** stream, not gzip, raw DEFLATE, or a multi-member gzip file. It accepts an already-open source and destination, so the caller must also limit incoming compressed bytes. It writes output incrementally and never accumulates all decompressed bytes in RAM.

```python
from __future__ import annotations

import zlib
from typing import BinaryIO


def copy_zlib_bounded(
    source: BinaryIO,
    destination: BinaryIO,
    *,
    max_input_bytes: int,
    max_output_bytes: int,
    max_ratio: float | None = 100.0,
    chunk_size: int = 64 * 1024,
) -> tuple[int, int]:
    """Copy exactly one zlib-wrapped stream with cumulative byte limits.

    The source and destination must be blocking binary streams. On any error,
    destination may contain a valid prefix; publish through a temporary file
    if the caller requires all-or-nothing output.
    """
    import math

    for name, value in (
        ("max_input_bytes", max_input_bytes),
        ("max_output_bytes", max_output_bytes),
        ("chunk_size", chunk_size),
    ):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
    if max_input_bytes < 0 or max_output_bytes < 0:
        raise ValueError("limits must be non-negative")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if max_ratio is not None:
        if isinstance(max_ratio, bool) or not isinstance(max_ratio, (int, float)):
            raise TypeError("max_ratio must be a finite positive number or None")
        if not math.isfinite(max_ratio) or max_ratio <= 0:
            raise ValueError("max_ratio must be finite and positive, or None")

    decoder = zlib.decompressobj()  # zlib wrapper, not gzip/raw DEFLATE
    input_count = 0
    output_count = 0

    def write_all(block: bytes) -> None:
        view = memoryview(block)
        while view:
            written = destination.write(view)
            if written is None:
                raise BlockingIOError("destination would block during write")
            if written <= 0:
                raise OSError("destination made no progress while writing")
            view = view[written:]

    while True:
        # Read at most one byte beyond the remaining budget so overflow is
        # detected without an unbounded source read.
        chunk = source.read(min(chunk_size, max_input_bytes - input_count + 1))
        if not chunk:
            break
        input_count += len(chunk)
        if input_count > max_input_bytes:
            raise ValueError("compressed input limit exceeded")
        if decoder.eof:
            raise ValueError("trailing data after the single zlib stream")

        pending = chunk
        drain_buffered_output = False
        while pending or drain_buffered_output:
            # +1 detects the first byte over the policy cap. max_length=0
            # means unlimited output, so this allowance is always positive.
            allowance = min(chunk_size, max_output_bytes - output_count + 1)
            produced = decoder.decompress(pending, max_length=allowance)
            pending = decoder.unconsumed_tail
            # If a call filled its output allowance but consumed all supplied
            # input, ask the decoder for buffered output using bounded empty
            # input calls as well. Stop when a call returns fewer bytes.
            drain_buffered_output = (
                not pending and not decoder.eof and len(produced) == allowance
            )

            if produced:
                output_count += len(produced)
                if output_count > max_output_bytes:
                    raise ValueError("decompressed output limit exceeded")
                # This ratio uses bytes read so far, not exact bytes consumed;
                # it is a policy heuristic, never the hard output boundary.
                if max_ratio is not None and output_count > max_ratio * max(input_count, 1):
                    raise ValueError("decompression ratio limit exceeded")
                write_all(produced)

            if decoder.eof:
                if decoder.unused_data or pending:
                    raise ValueError("trailing data after the single zlib stream")
                drain_buffered_output = False
                break
            if pending:
                drain_buffered_output = False

        if decoder.eof:
            # Detect data following the stream even if it was not in the last
            # source chunk. Any such byte is rejected, not silently ignored.
            if source.read(1):
                raise ValueError("trailing data after the single zlib stream")
            break

    if not decoder.eof:
        # Do not use an unbounded flush() to turn partial output into an
        # apparent success. eof is the completion signal for this zlib stream.
        raise EOFError("truncated zlib stream: end marker not reached")
    return input_count, output_count
```

**Why the `max_length` loop matters:** `decompress(data, max_length)` limits bytes returned by that call. When the cap prevents consuming all input, the remaining compressed bytes appear in `unconsumed_tail`; the caller must feed that tail back in bounded iterations. Passing `max_length=0` means unlimited output. The `+1` pattern makes it possible to detect the first byte beyond the policy limit instead of accidentally accepting exactly the limit while additional output remains. The per-call allowance is also capped by `chunk_size`, so a large configured total limit does not turn one decoder call into a correspondingly large allocation.

**Important ratio nuance:** the example computes the ratio against compressed bytes read so far, not a precise accounting of bytes consumed by the decoder. Because a read can include bytes the decoder has not consumed yet, this estimate can understate the instantaneous expansion ratio and varies with chunk size. It is a policy heuristic, not a hard security boundary. The absolute output limit is the hard output-exposure guardrail; the compressed input is also capped, and output is streamed rather than accumulated. Choose a ratio threshold from representative valid data and threat requirements; a threshold that is too low can reject legitimate highly compressible content. A ratio limit alone is insufficient, especially with a tiny denominator.

**Failure handling:** `zlib.error` can indicate malformed data or checksum failure; `EOFError` is raised here when EOF arrives before `decoder.eof`; `ValueError` signals policy violations. Since the destination may contain a prefix on failure, use a temporary destination and delete it on error. This example intentionally rejects trailing data and therefore is not a multi-stream container reader.

### Safe demonstration of output limits

This test uses a small, predictable payload and a low cap. It does not construct an explosive payload.

```python
import io
import zlib

small = b"hello world\n" * 20
compressed = zlib.compress(small)
out = io.BytesIO()
read_n, written_n = copy_zlib_bounded(
    io.BytesIO(compressed), out,
    max_input_bytes=10_000,
    max_output_bytes=1_000,
    max_ratio=None,
)
assert out.getvalue() == small
assert read_n == len(compressed)
assert written_n == len(small)

try:
    copy_zlib_bounded(
        io.BytesIO(compressed), io.BytesIO(),
        max_input_bytes=10_000,
        max_output_bytes=10,
        max_ratio=None, chunk_size=3,
    )
except ValueError as exc:
    print(type(exc).__name__, str(exc))
else:
    raise AssertionError("expected output-limit rejection")
```

### gzip, bz2, and lzma limits

`gzip.GzipFile`, `bz2.BZ2File`, and `lzma.LZMAFile` are convenient file-like interfaces, but a simple loop that calls `read(64 * 1024)` and stops after a fixed number of output bytes is the easiest way to enforce an absolute output cap. Do not assume that their convenience APIs expose the same `max_length` contract as `zlib.Decompress.decompress`. Check completion and concatenated-member semantics for the chosen format. For an untrusted gzip body, use a counting reader and stop after `limit + 1` decompressed bytes; also cap compressed bytes, CPU time, and request duration. If a single member must be required, validate that policy explicitly rather than assuming the high-level reader rejected all trailing data.

A practical high-level bounded copy pattern (for gzip or another file-like decompressor) is:

```python
def copy_limited(source, destination, *, max_output_bytes: int,
                 chunk_size: int = 64 * 1024) -> int:
    """Copy from an already-decompressing binary stream; output cap only."""
    if max_output_bytes < 0 or chunk_size <= 0:
        raise ValueError("invalid limit or chunk size")
    total = 0
    while True:
        # Request one extra byte to detect overflow.
        block = source.read(min(chunk_size, max_output_bytes - total + 1))
        if not block:
            return total
        total += len(block)
        if total > max_output_bytes:
            raise ValueError("decompressed output limit exceeded")
        destination.write(block)
```

Use it with a decompressor that has already been opened, for example `with gzip.open(path, "rb") as src: copy_limited(src, dst, max_output_bytes=...)`. It enforces an output limit, but **does not by itself** cap compressed input bytes, expansion ratio, CPU time, or validate an application-specific member/trailing-data policy. The `read(n)` API limits returned bytes per call, not all internal decoder buffering. For adversarial environments, combine this with transport/input caps and process-level resource controls.

---

## 5. gzip details, multi-member streams, and HTTP

### Concatenated gzip members

A gzip file can contain multiple gzip members concatenated one after another. This is useful for append-oriented workflows: appending with gzip append mode generally creates another member rather than rewriting the previous member. Python's `gzip` readers support concatenated members and expose their decompressed content as one stream. Do not assume every gzip-compatible tool or random-access reader has identical member behavior. Test the target ecosystem.

```python
import gzip
from pathlib import Path

p = Path("members.gz")
with gzip.open(p, "wb") as f:
    f.write(b"first\n")
with gzip.open(p, "ab") as f:
    f.write(b"second\n")
with gzip.open(p, "rb") as f:
    print(f.read())                    # b'first\nsecond\n'
```

For bounded untrusted decompression, multiple members complicate limits and integrity policy. Track total output across all members; do not reset the budget for each member. If the application expects exactly one member, use an API/parser that can reliably enforce that requirement.

### HTTP `Content-Encoding: gzip`

`Content-Encoding: gzip` means the HTTP representation body is gzip-compressed. The HTTP client or framework may transparently decompress it; check the library's contract to avoid double decompression. This is different from `Content-Type`, which describes the media type (for example `application/json`). If you implement decompression yourself, enforce limits on compressed bytes, decompressed bytes, elapsed time, and accepted content type/encoding. A server must not trust `Content-Length` as a substitute for a post-decompression output cap: it may describe the compressed representation, may be absent, or may not be reliable for all transport paths.

### Compression and encryption order; CRIME/BREACH

Compression can leak information through output lengths when secret-dependent data and attacker-controlled data are compressed together and an attacker can observe ciphertext or response lengths while making repeated chosen inputs. CRIME and BREACH are classes of attacks that exploit specific protocol and oracle conditions; they are not a claim that every compressed encrypted file is vulnerable.

For ordinary file storage, the common pattern is to compress the plaintext and then encrypt the compressed bytes with a modern authenticated-encryption scheme. **That ordering alone does not solve length side channels.** For interactive protocols, avoid compressing secrets together with attacker-controlled content, isolate secret-bearing responses, disable vulnerable compression where appropriate, and use protocol-specific mitigations. Do not rely on padding or a generic “compress first” rule without a threat model. Never compress attacker-controlled data together with secrets in a context where length feedback can be observed unless the protocol is designed to prevent the leak.

---

## 6. Checksums, hashes, and authenticity

`zlib.crc32(data, value=0)` and `zlib.adler32(data, value=1)` return rolling 32-bit checksums. Pass the previous return value as `value` to update incrementally. These are useful for accidental-corruption detection and format compatibility, **not** cryptographic integrity or authenticity: an attacker can deliberately alter data and recompute them.

```python
import hashlib
import zlib

payload = b"record-1\nrecord-2\n"
crc = zlib.crc32(payload)
adler = zlib.adler32(payload)
digest = hashlib.sha256(payload).hexdigest()
print(f"{crc:08x}", f"{adler:08x}", len(digest))  # 98043870 3c9f05d0 64
```

- **CRC32/Adler-32:** fast checks against accidental corruption; not resistant to intentional tampering.
- **Cryptographic hash (e.g. SHA-256):** detects changes if the expected digest is trusted; a digest sent alongside the payload by the same attacker does not authenticate it.
- **MAC/signature:** can authenticate data when keys and verification policy are managed correctly. Use a vetted cryptographic protocol/library; do not invent one.
- **Authenticated encryption:** protects confidentiality and detects tampering when used correctly; it does not remove all side channels or resource-exhaustion risks.

A gzip stream includes CRC32 and uncompressed-size information, but that is not a security boundary. Treat checksum verification as a corruption check, not proof of who created the data.

---

## 7. Benchmarking codecs responsibly

Compression ratio and throughput depend on the content, chunk size, codec, level, implementation, CPU, and I/O. Benchmark at least:

- repeated natural-language text;
- JSON Lines and CSV with realistic schemas and repeated values;
- already-compressed data (for example generated random bytes, or actual media/archive samples).

Use the same input bytes for every codec, warm up if relevant, repeat runs, and report medians. Separate compression and decompression throughput. Include CPU time or environment details for reproducibility. Never benchmark only a tiny string and infer production behavior.

```python
import gzip
import json
import os
import statistics
import time
import zlib


def benchmark_one(name: str, payload: bytes, compress, decompress, repeats: int = 5) -> dict:
    compressed = compress(payload)
    assert decompress(compressed) == payload
    compress_elapsed = []
    decompress_elapsed = []
    for _ in range(repeats):
        start = time.perf_counter()
        compress(payload)
        compress_elapsed.append(time.perf_counter() - start)
        start = time.perf_counter()
        restored = decompress(compressed)
        decompress_elapsed.append(time.perf_counter() - start)
        assert restored == payload
    compress_seconds = statistics.median(compress_elapsed)
    decompress_seconds = statistics.median(decompress_elapsed)
    return {
        "dataset": name,
        "input_bytes": len(payload),
        "compressed_bytes": len(compressed),
        "ratio_compressed_over_input": len(compressed) / max(len(payload), 1),
        "compression_mib_s": len(payload) / max(compress_seconds, 1e-12) / (1024 * 1024),
        "decompression_mib_s": len(payload) / max(decompress_seconds, 1e-12) / (1024 * 1024),
    }

text_data = ("A data pipeline emits stable records and repeated field names.\n" * 20_000).encode()
json_data = b"".join(
    (json.dumps({"id": i, "status": "ok", "region": "west"}) + "\n").encode()
    for i in range(20_000)
)
csv_data = ("id,status,region\n" + "1,ok,west\n" * 20_000).encode()
random_data = os.urandom(256 * 1024)  # random bytes approximate incompressible input

for name, data in [("text", text_data), ("jsonl", json_data), ("csv", csv_data), ("random", random_data)]:
    print(benchmark_one(name, data, zlib.compress, zlib.decompress))
```

This script benchmarks only `zlib` compression time for clarity. Extend it to compare `gzip`, `bz2`, `lzma`, and installed third-party codecs, and measure decompression throughput separately. Random bytes are a useful reproducible category, but actual already-compressed media/archives are also worth measuring. The ratio column is compressed bytes divided by input bytes: below 1 means smaller; above 1 means larger. Benchmark outputs are environment-specific, so this lesson does not promise fixed timings.

---

## 8. Splitability, frames, and data formats

- A conventional gzip stream is sequential. Arbitrary byte offsets are not reliable independent starting points because the DEFLATE state and member framing matter.
- **BGZF** (Blocked GNU Zip Format) divides data into independently decompressible gzip-compatible blocks and is used by tools such as genomic-data workflows. It is not identical to ordinary gzip in indexing behavior.
- **Zstandard frames** provide framing that can support independent decoding of frames; seekable/indexed access still requires appropriate frame boundaries or an index. A generic `.zst` file is not automatically splittable at arbitrary offsets.
- Columnar formats such as Parquet compress internal pages/column chunks and carry metadata/indexing around those blocks. This enables selective reads and parallel processing without treating the entire file as one opaque compressed stream. Codec support depends on the format implementation and installed libraries.
- Splittability is a format/layout property, not just a codec name. A writer must intentionally create boundaries and metadata that readers can use.

For many small, similar records, a Zstandard dictionary may improve ratio and speed. Dictionaries must be distributed and versioned consistently; selecting a dictionary is not authentication, and decoding with the wrong dictionary should be handled as an error.

---

## 9. Constant-memory pipeline design

A production data path should look like:

`bounded source read → bounded decompression → incremental parse/filter → bounded write`

Do not collect all chunks into a list or `bytearray` if the input can be large. Each stage should have a clear input/output limit and should stop reading when the downstream consumer is slow or rejects data. In async/network systems, use flow control/backpressure rather than creating unbounded queues. For uploads, stream multipart or object-storage uploads where supported, and enforce both per-chunk and total-size policies.

Example of line-by-line compressed JSONL processing:

```python
import gzip
import json

with gzip.open("incoming.jsonl.gz", "rt", encoding="utf-8") as source, \
     open("filtered.jsonl", "wt", encoding="utf-8", newline="\n") as target:
    for line_number, line in enumerate(source, start=1):
        if not line.strip():
            continue
        record = json.loads(line)  # handle JSONDecodeError per your data policy
        if record.get("status") == "ok":
            target.write(json.dumps(record, separators=(",", ":")) + "\n")
```

This demonstrates incremental parsing but not a complete hostile-input boundary. Add a decompressed-byte cap, line-length/record-size cap, record-count cap, schema validation, and error/quarantine policy. A single enormous line can still consume large memory in the text iterator/parser. Production parsers should bound record sizes before decoding/parsing where possible.

---

## 10. Error handling and truncation

Common errors include:

- `zlib.error`: malformed compressed data, checksum errors, invalid wrapper or other codec errors.
- `EOFError`: a high-level decoder or application may use it for incomplete/truncated input; the bounded helper above explicitly raises it if `eof` was not reached.
- `gzip.BadGzipFile`: invalid gzip format/header in APIs that raise it; some failures may surface as `EOFError` or `zlib.error` depending on where corruption occurs.
- `lzma.LZMAError` and `bz2`/I/O errors: format-specific decompression failures.
- `OSError`: file, disk, and I/O failures.

A clean end-of-file on the *compressed source* does not prove the compressed stream is complete. For `zlib.decompressobj`, inspect `eof`; if it is false when the input ends, the stream is truncated. Do not blindly call `flush()` and label whatever comes back a valid complete stream. `flush()` is not an authenticity check and does not replace `eof` validation. Corrupt/truncated exception types are not identical for every wrapper and Python version; catch the relevant documented exception family at the application boundary and preserve diagnostic context.

A truncated output file may have already been written before the error. Write to a temporary file, validate completion/checksums and limits, then atomically publish it if required. Log safe metadata (codec, compressed bytes, decompressed bytes, ratio, duration, outcome); do not log raw secrets or full untrusted payloads.

---

## 11. Tests: round trips, corruption, and truncation

The following test module can be saved as `test_compression_lesson.py`. It assumes the `copy_zlib_bounded` function above is saved in the same file or imported. The tests use small inputs and do not construct an explosive payload.

```python
import gzip
import io
import zlib
import pytest


def test_zlib_round_trip():
    raw = b"row,region\n1,west\n" * 100
    assert zlib.decompress(zlib.compress(raw)) == raw
    out = io.BytesIO()
    source = io.BytesIO(zlib.compress(raw))
    copy_zlib_bounded(source, out, max_input_bytes=10_000,
                      max_output_bytes=len(raw), max_ratio=None, chunk_size=3)
    assert out.getvalue() == raw


def test_gzip_round_trip_and_members():
    first = gzip.compress(b"first\n", mtime=0)
    second = gzip.compress(b"second\n", mtime=0)
    assert gzip.decompress(first + second) == b"first\nsecond\n"


def test_corrupt_zlib_raises():
    blob = bytearray(zlib.compress(b"hello" * 10))
    blob[-1] ^= 0xFF
    with pytest.raises(zlib.error):
        zlib.decompress(bytes(blob))


def test_corrupt_zlib_is_rejected_by_bounded_copy():
    blob = bytearray(zlib.compress(b"small checksum-protected payload"))
    blob[-1] ^= 0x01  # change a checksum byte, not the decompressed content
    with pytest.raises(zlib.error):
        copy_zlib_bounded(
            io.BytesIO(bytes(blob)), io.BytesIO(), max_input_bytes=1000,
            max_output_bytes=1000, max_ratio=None, chunk_size=3,
        )


def test_truncated_zlib_is_not_accepted():
    blob = zlib.compress(b"short payload")[:-2]
    with pytest.raises(EOFError):
        copy_zlib_bounded(
            io.BytesIO(blob), io.BytesIO(), max_input_bytes=1000,
            max_output_bytes=1000, max_ratio=None, chunk_size=3,
        )


def test_ratio_policy_can_reject_high_expansion():
    blob = zlib.compress(b"A" * 100)  # small, bounded fixture; not a bomb
    with pytest.raises(ValueError, match="ratio limit"):
        copy_zlib_bounded(
            io.BytesIO(blob), io.BytesIO(), max_input_bytes=1000,
            max_output_bytes=1000, max_ratio=2, chunk_size=4,
        )


def test_trailing_data_is_rejected():
    blob = zlib.compress(b"valid") + b"extra"
    with pytest.raises(ValueError, match="trailing data"):
        copy_zlib_bounded(
            io.BytesIO(blob), io.BytesIO(), max_input_bytes=1000,
            max_output_bytes=1000, max_ratio=None, chunk_size=2,
        )


def test_absolute_output_limit():
    blob = zlib.compress(b"0123456789" * 10)
    with pytest.raises(ValueError, match="output limit"):
        copy_zlib_bounded(
            io.BytesIO(blob), io.BytesIO(), max_input_bytes=1000,
            max_output_bytes=20, max_ratio=None,
        )


def test_input_limit():
    blob = zlib.compress(b"small")
    with pytest.raises(ValueError, match="input limit"):
        copy_zlib_bounded(
            io.BytesIO(blob), io.BytesIO(), max_input_bytes=1,
            max_output_bytes=100, max_ratio=None,
        )
```

Run with `python -m pytest -q`. These are examples of test design; execution is not implied by reading the lesson. Depending on how corruption changes the stream, a corrupt payload may raise `zlib.error` or be rejected by a wrapper; choose a byte mutation that is known to violate the checksum for the tested runtime. Do not use tests that decompress an intentionally huge expansion just to prove the cap works.

---

## 12. Common mistakes

- Treating Base64 as encryption, authentication, or compression.
- Forgetting Base64 output is `bytes` and implicitly decoding binary bytes as UTF-8.
- Assuming URL-safe Base64 automatically removes `=` padding or that all Base85 variants match.
- Accepting unbounded encoded input, compressed input, decompressed output, or record length.
- Using `zlib.decompress()` or `gzip.decompress()` on untrusted content without a hard output limit.
- Passing `max_length=0` to `decompressobj.decompress()` and assuming it means zero bytes; it means no output cap.
- Ignoring `unconsumed_tail`, `eof`, `unused_data`, or truncation.
- Calling `flush()` and assuming it proves the stream was complete or safe.
- Treating CRC32/Adler-32 as cryptographic authentication.
- Assuming gzip supports arbitrary parallel splits, or that every `.zst` file is independently seekable.
- Measuring only ratio and ignoring CPU, latency, memory, and downstream splitting.
- Using `shutil.copyfileobj(..., length=N)` as if `N` were a maximum total size.
- Assuming HTTP libraries never decompress automatically or that `Content-Length` equals decompressed length.
- Believing compress-then-encrypt by itself prevents CRIME/BREACH-style length leaks.
- Failing to remove partial output or to quarantine corrupt records when a stream fails late.

---

## 13. Exercises with solutions

### Exercise 1 — Base64 size

**Question:** Why is Base64 roughly one-third larger than the original binary payload? What is the exact encoded length for `n` bytes under standard padded Base64?

**Solution:** Each 3-byte group becomes 4 Base64 characters. The encoded length is `4 * ceil(n / 3)` characters/bytes, including padding. The ratio approaches 4/3 for large inputs.

### Exercise 2 — Choose a codec

**Question:** Choose a default for (a) a web-downloadable log, (b) a latency-sensitive internal stream, (c) archival text where ratio matters more than speed, and (d) a Parquet dataset.

**Solution:** (a) gzip for compatibility; (b) benchmark zstd or lz4 depending on dependencies and ratio needs; (c) consider xz/lzma or bz2 after measuring restore cost; (d) use a codec supported by the Parquet stack and target readers, and rely on the format's page/column-chunk layout for selective access. There is no universally best codec; compatibility and measured workload decide.

### Exercise 3 — Why is this unsafe?

```python
raw = zlib.decompress(untrusted_body)
```

**Solution:** It may allocate an unbounded amount of output from a small input. Use an incremental decoder with `max_length`, a hard absolute output cap, an input cap, ratio policy if useful, and completion/error handling. Do not accumulate all output in memory.

### Exercise 4 — Build a streaming gzip filter

**Question:** Sketch a `gz → filter → output` pipeline that does not read the whole file.

**Solution:** Iterate `gzip.open(source, "rt", encoding="utf-8")` line by line, parse one bounded record, validate it, and write accepted records immediately. Add a total decompressed-byte budget and maximum line/record size; use a temporary output and publish only after the stream completes successfully. If the output codec is Zstandard, use `compression.zstd` on Python 3.14+ or install and pin `zstandard` on earlier versions.

### Exercise 5 — Corruption versus authenticity

**Question:** What does a matching gzip CRC32 prove?

**Solution:** It provides a check against many accidental corruptions; it does not prove who created the stream or prevent an attacker from modifying the content and recomputing the CRC. Use a trusted cryptographic digest, MAC/signature, or authenticated encryption according to the threat model.

### Exercise 6 — Side-channel reasoning

**Question:** Why is “compress then encrypt” not a universal fix for CRIME/BREACH?

**Solution:** The leak can come from secret-dependent compressed length that remains observable through ciphertext/response lengths. If attacker-controlled input and secrets share a compression context and the attacker can make repeated chosen requests and observe lengths, encryption does not hide length. Separate secret and attacker-controlled content, disable vulnerable compression, or apply protocol-specific mitigations.

---

## 14. Glossary

- **Base encoding:** A reversible mapping from bytes to a textual alphabet.
- **Padding:** Extra characters such as `=` that complete the final encoded group.
- **Compression ratio:** State the convention. Here, `compressed_bytes / uncompressed_bytes`; below 1 means size reduction.
- **Streaming:** Processing bounded chunks without retaining the entire input or output.
- **`compressobj`:** Incremental compressor that accepts chunks and emits compressed pieces.
- **`decompressobj`:** Incremental decompressor with state, including `eof`, `unconsumed_tail`, and `unused_data`.
- **Expansion/decompression bomb:** Input that expands to an unexpectedly large output or consumes excessive CPU/memory.
- **Gzip member:** One gzip-framed compressed stream; gzip files may concatenate members.
- **Frame/block:** Independently framed portion of a compressed representation, depending on the format.
- **Backpressure:** A slow downstream stage signals upstream stages to slow or stop, preventing unbounded queues.
- **CRC32 / Adler-32:** Fast non-cryptographic checksums.
- **Cryptographic hash:** Digest designed for security properties such as collision resistance; authenticity still requires a trusted expected digest or key/signature scheme.
- **Content-Encoding:** HTTP metadata describing a transformation applied to the representation body, such as gzip.

---

## 15. Completion checklist

- [ ] I can explain encoding versus compression versus encryption.
- [ ] I can round-trip Base64, URL-safe Base64, Base32, Base16, and Ascii85/Base85, and explain padding and size overhead.
- [ ] I know that Base64 APIs return bytes and that text conversion should be explicit.
- [ ] I can choose among zlib, gzip, bz2, and lzma, and identify Python 3.14's standard-library `compression.zstd` and third-party alternatives.
- [ ] I can stream compression with `compressobj`, `gzip.GzipFile`, `shutil.copyfileobj`, and line-by-line `.gz` reads.
- [ ] I can explain gzip multi-member behavior and HTTP `Content-Encoding`.
- [ ] I can enforce compressed-input and decompressed-output caps and understand `max_length`, `unconsumed_tail`, and `eof`.
- [ ] I can distinguish truncation, corruption, trailing data, and policy-limit failures.
- [ ] I know CRC32/Adler-32 are not authenticity controls.
- [ ] I can benchmark ratio and throughput on text, JSON, CSV, and incompressible/already-compressed data.
- [ ] I can explain splittable layouts, BGZF, Zstandard frames, and internal block compression in columnar formats.
- [ ] I can design a bounded `read → decompress → parse → write` pipeline with backpressure and observability.
- [ ] I understand the conditions behind CRIME/BREACH-style compression side channels.
- [ ] I completed the exercises and tests.

## 16. Roadmap self-check — answers

1. **Why does Base64 grow data by about a third?** Three input bytes are represented by four output characters; exact padded size is `4 * ceil(n / 3)`.
2. **How do you cap output when decompressing untrusted data?** Use a streaming decompressor, call `decompress(data, max_length=positive_limit)`, repeatedly process `unconsumed_tail`, keep a hard cumulative output count and compressed-input cap, optionally apply a ratio policy, check `eof`, and reject or explicitly handle trailing data. Do not call unbounded whole-buffer decompression.
3. **How do you build a streaming `gz → filter → zstd/gz` converter?** Read the gzip stream in bounded chunks or bounded records, enforce total-output and record-size limits, validate/filter each record, write immediately to a streaming output compressor, handle backpressure, verify successful completion, and publish output only after success. Use stdlib `compression.zstd` on Python 3.14+ or a pinned third-party `zstandard` dependency on earlier versions. Test round trips, corrupt/truncated streams, and size-limit rejection with small fixtures.

**Next:** Lesson 08 — `mmap` and large binary files. Keep memory mapping and fixed-layout binary parsing as separate lessons; this lesson focuses on encodings, compression, and streaming safety.
