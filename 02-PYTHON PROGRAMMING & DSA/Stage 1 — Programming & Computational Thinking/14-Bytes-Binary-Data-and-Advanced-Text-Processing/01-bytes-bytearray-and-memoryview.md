# Bytes, `bytearray` and `memoryview`

**Stage 1 — Programming & Computational Thinking**  
**Module 14 — Bytes, Binary Data and Advanced Text Processing**  
**Lesson 01 of 08**  
**Target: Python 3.12+**

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain the difference between Unicode text (`str`) and binary data (`bytes`), and distinguish immutable, mutable, and view-based objects.
- Construct, inspect, compare, slice, encode, decode, and convert byte sequences safely.
- Convert integers to and from byte sequences with explicit width, byte order, and signedness.
- Read binary streams using bounded chunks, `readinto()`, and reusable buffers.
- Recognize byte-order marks (BOMs), use `surrogateescape` when preserving undecodable bytes, and avoid pretending an encoding can always be inferred.
- Use the buffer protocol and `memoryview` to inspect data without copying it, while respecting buffer ownership and resizing rules.
- Explain typed buffers with `array.array`, the limited relationship to NumPy, and when a zero-copy view is useful.
- Measure copy-versus-view trade-offs fairly, avoid unsafe byte truncation, and validate untrusted lengths before allocating memory.

## Prerequisites

You should already understand basic variables, strings, indexing and slicing, loops, exceptions, file handling, and the idea that a byte contains eight bits. Familiarity with UTF-8 and hexadecimal notation will help. You do not need to know `struct`, NumPy, or binary file formats yet.

## Why this matters in real systems

Text files, network sockets, compressed streams, image and audio payloads, database BLOBs, tokenizer inputs, checksums, and model weights all move through programs as bytes at some boundary. Confusing text with bytes can corrupt data, break signatures, truncate multibyte characters, or create security bugs. `memoryview` can reduce copying when processing large buffers, but it introduces lifetime and mutability constraints that must be understood.

---

## 1. Foundations: text is not bytes

### 1.1 `str`: Unicode text

A Python `str` is a sequence of Unicode code points. A code point is a number assigned to a Unicode character. A `str` represents text, not a particular on-disk encoding.

```python
text = "café"
print(text)
print(len(text))
print([hex(ord(char)) for char in text])
```

Expected output:

```text
café
4
['0x63', '0x61', '0x66', '0xe9']
```

`len(text)` counts code points, not bytes, grapheme clusters, or terminal columns. Some visible characters are composed from multiple code points; that topic is explored further in the later Unicode lesson.

### 1.2 `bytes`: immutable byte values

A `bytes` object is an immutable sequence of integers in the inclusive range 0–255. It is suitable for raw data and encoded text.

```python
payload = b"ABC"
print(payload)
print(list(payload))
print(payload[0])
print(payload[:2])
```

Expected output:

```text
b'ABC'
[65, 66, 67]
65
b'AB'
```

**Important:** indexing `bytes` returns an `int`, not a one-byte `bytes` object. Slicing returns a new `bytes` object containing the selected bytes.

### 1.3 `bytearray`: mutable bytes

`bytearray` is a mutable sequence of byte values. It is useful when a buffer must be assembled or edited incrementally.

```python
buf = bytearray(b"ABC")
buf[0] = 97
buf.append(33)
print(buf)
print(bytes(buf))
```

Expected output:

```text
bytearray(b'aBC!')
b'aBC!'
```

A single-byte assignment must be an integer from 0 to 255. Unlike `bytes`, a `bytearray` can change in place; resizing it may be prohibited while an exported view is active.

### 1.4 `memoryview`: a view onto existing storage

A `memoryview` exposes the buffer of another object without first copying the selected data into a new bytes object. It is a view, not an independent data container. A view can keep its exporter alive and can prevent a resizable exporter such as `bytearray` from resizing while the view is active.

```python
source = bytearray(b"abcdef")
view = memoryview(source)
part = view[1:4]
part[0] = ord("Z")
print(source)
print(bytes(part))
view.release()
part.release()
```

Expected output:

```text
bytearray(b'aZcdef')
b'Zcd'
```

The `bytes(part)` call deliberately makes a copy for display/conversion. The slice `view[1:4]` itself is a view and does not copy the payload.

### 1.5 Comparison table

| Type | Represents | Mutable? | Index returns | Slice normally returns | Typical use |
|---|---|---:|---|---|---|
| `str` | Unicode text | No | one-character `str` | `str` (an immutable result; implementations may reuse objects) | Text processing |
| `bytes` | Byte values 0–255 | No | `int` | `bytes`; ordinary partial slices copy selected data, though some slices may reuse immutable objects | Immutable payloads, hashes, protocols |
| `bytearray` | Byte values 0–255 | Yes | `int` | new `bytearray` | Incremental construction and editing |
| `memoryview` | View of buffer-protocol storage | Depends on exporter and view permissions | usually scalar value | another view | Zero-copy inspection/parsing |

Use `str` when the value is text; use `bytes` when the value is binary or encoded data; use `bytearray` when you need to mutate a byte sequence; use `memoryview` when you need to inspect or parse existing buffer storage without copying it.

---

## 2. Constructing and inspecting bytes

### 2.1 Byte literals and constructors

```python
literal = b"abc"
from_values = bytes([65, 66, 67])
zeros = bytes(4)
raw = b"\x00\xff"
print(literal)
print(from_values)
print(zeros)
print(raw.hex())
```

Expected output:

```text
b'abc'
b'ABC'
b'\x00\x00\x00\x00'
00ff
```

Key details:

- `b"abc"` is a bytes literal. ASCII characters in a bytes literal map directly to their ASCII byte values.
- `\xNN` expresses one byte using two hexadecimal digits. `b"\x00\xff"` contains values 0 and 255.
- `bytes(iterable)` consumes integers in the range 0–255. An out-of-range value raises `ValueError`.
- `bytes(n)` creates `n` zero bytes. Do not pass an untrusted `n` without validating and capping it first.
- `bytes(existing_bytes)` may return the same immutable object rather than allocate a distinct copy; do not rely on object identity for program logic.

### 2.2 Hexadecimal conversion

Hex is a readable representation of byte values, not a different kind of data.

```python
packet = bytes.fromhex("de ad be ef")
print(packet)
print(packet.hex())
print(packet.hex(" "))
```

Expected output:

```text
b'\xde\xad\xbe\xef'
deadbeef
de ad be ef
```

`bytes.fromhex()` accepts ASCII whitespace between byte pairs. Each pair must describe a complete byte. Use `.hex()` for diagnostics and reproducible test fixtures; do not treat a hex string as the original binary object.

### 2.3 Indexing, slicing, and mutation

```python
data = b"ABCDE"
print(data[0], data[-1], data[1:4])
try:
    data[0] = 90
except TypeError as exc:
    print(type(exc).__name__)

mutable = bytearray(data)
mutable[1:3] = b"xy"
del mutable[-1]
print(mutable)
```

Expected output:

```text
65 69 b'BCD'
TypeError
bytearray(b'AxyD')
```

A `bytearray` slice creates a new `bytearray`; an ordinary partial `bytes` slice copies the selected data, although implementations may reuse immutable objects for cases such as a full slice. Repeatedly slicing large byte ranges can copy substantial data. Prefer indexing for single values, chunked processing for streams, or `memoryview` when a view is appropriate.

### 2.4 Byte-oriented methods

Many familiar methods exist on `bytes` and `bytearray`, including `split`, `rsplit`, `strip`, `lstrip`, `rstrip`, `startswith`, `endswith`, `find`, `index`, `count`, `replace`, `partition`, and `join`. Their arguments and results are bytes-like values, not text strings.

```python
line = b"  id=42;status=ok  \r\n"
clean = line.strip()
key, sep, value = clean.partition(b";")
print(clean)
print(key, sep, value)
print(b",".join([b"a", b"b", b"c"]))
```

Expected output:

```text
b'id=42;status=ok'
b'id=42' b';' b'status=ok'
b'a,b,c'
```

`bytes` has no text formatting method equivalent to `str.format()`. For human-readable formatted text, format a `str` and then encode it explicitly if the protocol requires bytes:

```python
record = f"id={42:04d},status=ok".encode("ascii")
print(record)
```

Expected output: `b'id=0042,status=ok'`.

Avoid mixing `str` and `bytes` implicitly. For example, `b"id=" + str(42)` raises `TypeError`; decide which representation the boundary requires.

---

## 3. Explicit text encoding and decoding

### 3.1 Encoding converts text to bytes

An **encoding** defines how text is represented as bytes. UTF-8 is a common encoding for Unicode text. Encoding must be explicit at a text/binary boundary.

```python
text = "café"
data = text.encode("utf-8")
print(data)
print(data.hex())
print(len(text), len(data))
print(data.decode("utf-8"))
```

Expected output:

```text
b'caf\xc3\xa9'
636166c3a9
4 5
café
```

The character `é` is one code point here but takes two bytes in UTF-8. UTF-8 uses one to four bytes per Unicode code point. Therefore `len(text)` and `len(text.encode("utf-8"))` measure different things.

### 3.2 Decoding converts bytes to text

Decoding requires knowing the encoding, or having a trustworthy external declaration that specifies it.

```python
encoded = b"caf\xc3\xa9"
print(encoded.decode("utf-8"))
```

Expected output: `café`.

Decoding bytes using the wrong codec may fail or produce mojibake (text that decodes successfully but displays as corrupted characters). A successful decode is not proof that the chosen encoding was correct.

### 3.3 Error policies

For `bytes.decode()` and `str.encode()`, the default is `errors="strict"`. The policy determines what happens when a sequence cannot be decoded or encoded.

```python
bad = b"valid:\xff:end"

for policy in ("replace", "ignore", "backslashreplace"):
    print(policy, bad.decode("utf-8", errors=policy))
```

Expected output (the replacement glyph may vary by display environment):

```text
replace valid:�:end
ignore valid::end
backslashreplace valid:\xff:end
```

- `strict`: raises `UnicodeDecodeError` or `UnicodeEncodeError`; usually best when invalid data means the input is malformed.
- `replace`: inserts a replacement character when decoding fails; preserves readability but loses the original byte sequence.
- `ignore`: drops invalid data; lossy and often dangerous for identifiers, logs, signatures, and forensic evidence.
- `backslashreplace`: represents problematic bytes/code points with backslash escapes; useful for diagnostics, not a reversible general-purpose interchange format.

For encoding, `backslashreplace` escapes characters that the target encoding cannot represent. Error-handler behavior is defined by Python; test the exact boundary behavior you need.

### 3.4 Round-trip behavior

With a compatible codec and strict handling, valid text can round-trip:

```python
original = "Hello, café — 世界"
assert original.encode("utf-8").decode("utf-8") == original
print("UTF-8 round trip passed")
```

Expected output: `UTF-8 round trip passed`.

The reverse invariant, `data.decode(codec).encode(codec) == data`, holds only when the byte input is valid under that codec and the decode/encode process preserves the original representation. Lossy error handlers invalidate that guarantee.

### 3.5 BOM awareness and encoding detection

A **byte-order mark (BOM)** is a leading byte sequence that can signal a Unicode encoding or byte order. For example, UTF-8 may begin with `EF BB BF`. Python's `utf-8-sig` codec removes a leading UTF-8 BOM when decoding and writes one when encoding.

```python
with_bom = b"\xef\xbb\xbfname,value"
print(with_bom.decode("utf-8"))
print(with_bom.decode("utf-8-sig"))
```

Expected output:

```text
﻿name,value
name,value
```

A BOM is evidence, not a universal encoding detector. If no reliable metadata or BOM exists, encoding detection is uncertain. Libraries such as `charset-normalizer` can estimate likely encodings, but heuristics can be wrong. Prefer documented source encodings, protocol metadata, or an explicit contract.

### 3.6 `surrogateescape` for lossless handling of dirty bytes

For certain legacy filesystem and system interfaces, `errors="surrogateescape"` allows undecodable bytes to be represented using special surrogate code points and then recovered when re-encoded with the same codec and error policy.

```python
raw = b"name-\xff.txt"
text = raw.decode("utf-8", errors="surrogateescape")
recovered = text.encode("utf-8", errors="surrogateescape")
print(recovered == raw)
print(repr(text))
```

Expected first line: `True`. The `repr` contains a surrogate escape representation for the invalid byte (typically `'\udcff'`).

Use this for round-trip preservation, not for normal user-facing text. It is not a repair or detection method, and the surrogate-containing string may be unsuitable for systems that require valid Unicode scalar values.

---

## 4. Mutable buffers and integer conversion

### 4.1 Building a `bytearray` incrementally

Repeated concatenation of immutable `bytes` can allocate a new object each time. For incremental assembly, a `bytearray` is often clearer and can reduce repeated copying.

```python
out = bytearray()
out.extend(b"header:")
out.append(0x31)
out.extend(b",payload")
out[0:6] = b"HEADER"
print(out)
```

Expected output:

```text
bytearray(b'HEADER:1,payload')
```

Common operations include:

- `append(value)`: add one integer byte.
- `extend(iterable)`: add multiple byte values.
- Slice assignment: replace a range; the replacement may change the total length.
- `del buffer[start:end]`: remove a range.
- `clear()`: remove all bytes.

A `bytearray` may over-allocate internally to make repeated appends efficient, but its exact capacity strategy is an implementation detail. Avoid assuming a particular allocation size.

### 4.2 Integers to bytes

A byte sequence does not intrinsically say whether it is an integer, text, a color, or part of a file format. When interpreting bytes as an integer, specify the width, byte order, and signedness.

```python
n = 258
print(n.to_bytes(2, "big"))
print(n.to_bytes(2, "little"))
print(int.from_bytes(b"\x01\x02", "big"))
print(int.from_bytes(b"\xfe", "big", signed=True))
```

Expected output:

```text
b'\x01\x02'
b'\x02\x01'
258
-2
```

- **Big-endian** stores the most significant byte first.
- **Little-endian** stores the least significant byte first.
- `signed=False` (the default) interprets the sequence as an unsigned integer.
- `signed=True` uses two's-complement representation for signed integers.

For a fixed number of bytes, unsigned values range from \(0\) through \(2^{8n}-1\). Signed values range from \(-2^{8n-1}\) through \(2^{8n-1}-1\), where \(n\) is the number of bytes.

```python
print((127).to_bytes(1, "big", signed=True))
print((-128).to_bytes(1, "big", signed=True))

try:
    print((256).to_bytes(1, "big"))
except OverflowError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
b'\x7f'
b'\x80'
OverflowError
```

A value that cannot fit in the requested width raises `OverflowError`. Invalid lengths or byte-order values raise `ValueError`. Negative unsigned values cannot be represented. Do not silently increase the width unless the surrounding protocol permits it; width is often part of the data format.

### 4.3 Bytes to integers

```python
raw = b"\xff\xfe"
print(int.from_bytes(raw, "big"))
print(int.from_bytes(raw, "little"))
print(int.from_bytes(raw, "big", signed=True))
```

Expected output:

```text
65534
65279
-2
```

The same bytes can mean different numbers depending on byte order and signedness. These choices must come from the file or protocol specification, not from guesswork.

---

## 5. Binary file I/O and bounded buffers

### 5.1 Open files in binary mode

Use `"rb"` to read raw bytes and `"wb"` to write bytes. Text mode decodes/encodes data and may translate newlines; binary mode does not.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = Path(directory) / "payload.bin"
    path.write_bytes(b"\x00A\xffB")

    with path.open("rb") as file:
        print(file.read(2))
        print(file.read())

    print(path.read_bytes().hex())
```

Expected output:

```text
b'\x00A'
b'\xffB'
0041ff42
```

This example uses temporary data and does not depend on a pre-existing file.

### 5.2 Chunked reads

For large files, avoid loading the whole file into memory when you only need to process it sequentially. The examples below assume a blocking binary file or stream; non-blocking sources need explicit readiness and retry handling.

```python
def read_chunks(file, size=64 * 1024):
    if size <= 0:
        raise ValueError("size must be positive")
    while True:
        chunk = file.read(size)
        if not chunk:
            break
        yield chunk
```

Example use:

```python
from io import BytesIO

stream = BytesIO(b"abcdefgh")
print(list(read_chunks(stream, 3)))
```

Expected output: `[b'abc', b'def', b'gh']`.

The final chunk may be shorter than the requested size. An empty bytes object signals end-of-file for a normal blocking file read. A network stream or non-blocking source may have different partial-read semantics; do not generalize file behavior to every I/O API.

A concise alternative for ordinary blocking files is:

```python
from io import BytesIO

stream = BytesIO(b"abcdefgh")
print(list(iter(lambda: stream.read(3), b"")))
```

Expected output: `[b'abc', b'def', b'gh']`.

### 5.3 `readinto()` and a preallocated buffer

`readinto(writable_buffer)` reads into caller-provided writable storage and returns the number of bytes read. It can avoid allocating a new `bytes` object for each chunk.

```python
from io import BytesIO

stream = BytesIO(b"abcdefgh")
buffer = bytearray(3)
while True:
    count = stream.readinto(buffer)
    if count == 0:
        break
    # Only the first `count` bytes belong to this read.
    chunk_view = memoryview(buffer)[:count]
    try:
        print(bytes(chunk_view))
    finally:
        chunk_view.release()
```

Expected output:

```text
b'abc'
b'def'
b'gh'
```

**Partial-read rule:** only the first `count` bytes are valid for that iteration. The unused tail retains old bytes from the previous read. Never process the entire buffer after a short read.

For APIs that may return partial data before a logical record is complete, implement a loop that accumulates data until the required length is reached, EOF occurs, or an error occurs. Do not assume one call fills the requested buffer.

### 5.4 Yielding views from a reusable buffer: lifetime matters

A reusable buffer can be used with views, but yielding a view into that same buffer is subtle: the next read overwrites bytes visible through previously yielded views. Consumers must finish with each view before the producer reuses the storage, or the API must copy the chunk.

The following generator expects a blocking binary stream and is safe only under a **borrowed-view contract**: each view is valid for immediate use and must not be retained while iteration continues. Non-blocking streams need an explicit readiness/retry policy rather than treating temporary unavailability as EOF.

```python
def read_chunk_views(file, size=64 * 1024):
    """Yield borrowed views; consume each view before requesting the next."""
    if size <= 0:
        raise ValueError("size must be positive")
    buffer = bytearray(size)
    view = memoryview(buffer)
    try:
        while True:
            count = file.readinto(buffer)
            if count is None:
                raise BlockingIOError("readinto would block; this generator expects a blocking stream")
            if count == 0:
                break
            yield view[:count]
    finally:
        view.release()
```

Usage:

```python
from io import BytesIO

for chunk_view in read_chunk_views(BytesIO(b"abcdef"), 2):
    print(bytes(chunk_view))
    chunk_view.release()
```

Expected output:

```text
b'ab'
b'cd'
b'ef'
```

This example explicitly releases each yielded child view. If the consumer stores a view, asks for the next chunk, or needs independent ownership, this contract is not appropriate. Use a copying generator that yields `bytes`, or design a pool/lease API with explicit ownership and lifetime rules. A generator closing while a consumer still holds a view can also encounter exported-buffer lifetime constraints; treat view lifetime as part of the API contract.

---

## 6. Buffer protocol and `memoryview`

### 6.1 What is the buffer protocol?

The buffer protocol is a Python interface through which an object exposes memory to another object. `bytes`, `bytearray`, `array.array`, and many third-party array types can export buffers. `memoryview` provides a standard Python-level way to access that storage.

The key benefit is avoiding an intermediate copy when the consumer can work with the existing representation. The trade-off is that the view's shape, format, mutability, and lifetime are constrained by the exporter.

### 6.2 Zero-copy slices and `.nbytes`

```python
data = bytearray(b"0123456789")
view = memoryview(data)
window = view[2:6]
print(window.tobytes())
print(window.nbytes)
window[0] = ord("X")
print(data)
window.release()
view.release()
```

Expected output:

```text
b'2345'
4
bytearray(b'01X3456789')
```

The slice is a view over the original storage; modifying the writable view modifies the exporter. `.nbytes` reports the number of bytes represented by the view, which is not always the same as `len(view)` for multi-byte formats or multidimensional views. `len(view)` reports the length of its first dimension.

### 6.3 `.cast()` and `.tolist()`

`memoryview.cast()` reinterprets the same bytes using a different native format and shape, when the cast is permitted. It does not perform numeric conversion or byte swapping.

```python
raw = bytearray([1, 0, 2, 0])
view = memoryview(raw)
words = view.cast("H")
print(words.tolist())
print(words.nbytes)
words.release()
view.release()
```

The values depend on the machine's native byte order. On a little-endian machine, expected output is:

```text
[1, 2]
4
```

On a big-endian machine, the list would be `[256, 512]`. This platform dependence is intentional: `"H"` is a native unsigned-short format, not a portable file-format declaration. Use a later lesson's `struct` tools or explicit integer conversion for portable binary layouts.

`.tolist()` creates Python objects (and nested lists for multidimensional views), so it is not zero-copy. It is useful for inspection and small examples, not for converting a huge buffer without memory cost.

### 6.4 `.release()` and resizing constraints

```python
buf = bytearray(b"abc")
view = memoryview(buf)
try:
    buf.extend(b"d")
except BufferError:
    print("resize blocked while view is active")
view.release()
buf.extend(b"d")
print(buf)
```

Expected output:

```text
resize blocked while view is active
bytearray(b'abcd')
```

A live exported view prevents resizing the `bytearray`, because resizing could invalidate the exported memory region. In-place element updates of the existing size are allowed through a writable view. `memoryview.release()` explicitly releases the view's access; after release, most operations on that view raise `ValueError`. Release child views as well when they are no longer needed.

Do not resize or replace the exporter while a view is being used. Avoid holding views longer than necessary, especially across asynchronous tasks, callbacks, or generator yields.

### 6.5 `array.array` and typed buffers

`array.array` stores a sequence of values using a compact C-compatible type code rather than one Python object per value. It exports the buffer protocol, so a `memoryview` can inspect its storage.

```python
from array import array

values = array("I", [10, 20, 30])
view = memoryview(values)
print(view.format)
print(view.tolist())
print(view.nbytes)
view.release()
```

The format code and element size for `"I"` are platform-dependent within the guarantees of `array`; do not assume a universal on-disk layout. Typed arrays are useful for compact numeric sequences and interoperability with APIs accepting buffers.

**Scoped NumPy bridge:** NumPy `ndarray` also exposes the buffer protocol in many cases. `numpy.frombuffer()` can create an array view over an existing buffer, often without copying, but dtype, byte order, alignment, contiguity, mutability, and source lifetime still matter. This is a connection to the later NumPy/data-engineering lessons, not a replacement for learning NumPy here.

---

## 7. Zero-copy parsing and memory trade-offs

Suppose a message has a fixed prefix, a payload, and a suffix. If the message is already in memory, slicing a `bytes` object copies the selected bytes. A `memoryview` can expose each region without copying the underlying data.

```python
message = b"HEAD" + b"x" * 1_000_000 + b"TAIL"
view = memoryview(message)

header = view[:4]
payload = view[4:-4]
trailer = view[-4:]

print(header.tobytes())
print(payload.nbytes)
print(trailer.tobytes())

header.release()
payload.release()
trailer.release()
view.release()
```

Expected output:

```text
b'HEAD'
1000000
b'TAIL'
```

For large buffers, views can reduce allocations and copying. However:

- A view does not make the original buffer smaller; it can keep a large exporter alive.
- Views over mutable data observe later mutations.
- Converting a view to `bytes`, calling `.tobytes()`, or `.tolist()` creates data and can remove much of the benefit.
- Some consumers require a contiguous buffer or a specific format and may copy internally.
- A zero-copy design can be harder to reason about because storage ownership and lifetime are shared.

### 7.1 `sys.getsizeof()` is not total memory accounting

```python
import sys

data = b"x" * 100_000
view = memoryview(data)
print(sys.getsizeof(data) > 0)
print(view.nbytes)
view.release()
```

Expected output:

```text
True
100000
```

`sys.getsizeof(obj)` reports the object's shallow size as reported by the implementation. It does not recursively include all referenced objects, and a `memoryview`'s own shallow size does not include the exporter’s storage. Use it for limited comparisons, not as a complete memory profiler.

### 7.2 A fair copy-versus-view benchmark

Run this benchmark locally; timing depends on Python build, CPU, operating system, allocator, and workload. It reports measurements rather than asserting that one approach is always faster.

```python
from timeit import timeit

data = b"x" * 1_000_000
start, stop = 100_000, 900_000
view = memoryview(data)

def copied_slice():
    return data[start:stop]

def viewed_slice():
    return view[start:stop]

# Both functions return an object covering the same logical byte range.
# The bytes version copies the selected payload; the view version does not.
# 1,000 iterations copy about 800 MB in total; lower the count for slower machines.
copy_seconds = timeit(copied_slice, number=1_000)
view_seconds = timeit(viewed_slice, number=1_000)

print(f"bytes slices: {copy_seconds:.6f}s")
print(f"view slices:  {view_seconds:.6f}s")
view.release()
```

For this large selected region, the view generally avoids copying 800,000 bytes per iteration. But a view object still has overhead; for tiny slices, short-lived views may not improve end-to-end performance. This benchmark measures creation time, not downstream processing, retained memory, cache behavior, or the cost of eventually copying. Benchmark your actual workload, and do not present one microbenchmark as a universal rule.

---

## 8. UTF-8 lengths, truncation, incremental decoding, and tokenization

### 8.1 Never truncate encoded text at an arbitrary byte boundary

A byte limit and a character limit are different requirements.

```python
text = "A€B"
encoded = text.encode("utf-8")
print(len(text), len(encoded))
print(encoded)
print(encoded[:2])
try:
    print(encoded[:2].decode("utf-8"))
except UnicodeDecodeError:
    print("truncation split a UTF-8 sequence")
```

Expected output:

```text
3 5
b'A\xe2\x82\xacB'
b'A\xe2'
truncation split a UTF-8 sequence
```

The euro sign uses three UTF-8 bytes. Cutting the encoded sequence after its first byte creates invalid UTF-8. If you need a byte-limited text field, choose a truncation policy deliberately. Decoding with `errors="ignore"` may avoid an exception but silently discards data; it should not be the default fix.

One simple safe approach is to shorten the text until its encoded representation fits:

```python
def truncate_utf8(text: str, max_bytes: int) -> str:
    if max_bytes < 0:
        raise ValueError("max_bytes must be non-negative")
    result = []
    used = 0
    for char in text:
        size = len(char.encode("utf-8"))
        if used + size > max_bytes:
            break
        result.append(char)
        used += size
    return "".join(result)

print(truncate_utf8("A€B", 4))
print(len(truncate_utf8("A€B", 4).encode("utf-8")))
```

Expected output:

```text
A€
4
```

This preserves code points but does not guarantee a user-perceived grapheme cluster will remain intact; combining marks and joined emoji are a separate Unicode concern.

### 8.2 Incremental decoding across chunks

A UTF-8 character can be split between two reads. Decoding each chunk independently can fail even if the overall stream is valid. `codecs.getincrementaldecoder()` retains incomplete sequences between calls.

```python
import codecs

raw = "A€B".encode("utf-8")
chunks = [raw[:2], raw[2:4], raw[4:]]
decoder = codecs.getincrementaldecoder("utf-8")()
parts = [decoder.decode(chunk) for chunk in chunks]
parts.append(decoder.decode(b"", final=True))
print("".join(parts))
```

Expected output: `A€B`.

The final call with `final=True` is important: it makes the decoder report an incomplete trailing sequence instead of silently treating the stream as complete. For valid UTF-8 the output is correct; malformed data still follows the configured error policy.

### 8.3 Byte-level tokenization as a motivating example

Some tokenizers, including byte-level BPE designs, operate over bytes or a reversible mapping from bytes to visible symbols. This helps represent arbitrary text and unusual characters without requiring a separate vocabulary entry for every Unicode character. Actual tokenizer implementations have their own pre-tokenization, byte-to-symbol mapping, merges, and special-token rules; this simplified example is only a byte-level illustration.

```python
text = "Hi €"
raw = text.encode("utf-8")
print(list(raw))
print(raw.hex())
```

Expected output:

```text
[72, 105, 32, 226, 130, 172]
486920e282ac
```

The euro sign becomes three bytes. A byte-level tokenizer may begin from these byte values before applying its vocabulary/merge rules. Do not assume the byte list above equals the token IDs emitted by a specific model tokenizer; use that tokenizer's official implementation when token counts or model inputs matter.

---

## 9. Comparing, hashing, and secret values

### 9.1 Equality and hashing

`bytes` objects support equality, lexicographic ordering, and hashing. Since `bytes` is immutable, it can be used as a dictionary key or set member.

```python
a = b"abc"
b = bytes.fromhex("616263")
print(a == b)
print(a < b"abd")
print({a: "payload"}[b])
```

Expected output:

```text
True
True
payload
```

`bytearray` is mutable and unhashable, so it cannot be used as a dictionary key. Do not confuse a byte sequence's lexicographic ordering with the numeric value of a multi-byte integer.

### 9.2 Constant-time comparison for secrets

Ordinary equality may stop at the first differing byte. When comparing secret-derived values such as authentication tags, use `hmac.compare_digest()` to reduce timing leakage from content-dependent comparison behavior.

```python
import hmac

expected = b"example-auth-tag"
provided = b"example-auth-tag"
print(hmac.compare_digest(expected, provided))
```

Expected output: `True`.

`compare_digest()` does not make an entire authentication system constant-time, protect secret storage, or replace correct cryptographic protocol design. Validate types and lengths according to the protocol, avoid leaking detailed authentication errors, and use established cryptographic libraries.

---

## 10. Security and production rules

Binary inputs are untrusted until validated. A length prefix may be malformed, maliciously large, truncated, or inconsistent with the remaining data.

### 10.1 Cap allocations before allocating

```python
MAX_PAYLOAD = 8 * 1024 * 1024  # 8 MiB application policy

def validate_payload_length(length: int) -> int:
    if not isinstance(length, int) or isinstance(length, bool):
        raise TypeError("length must be an integer")
    if length < 0:
        raise ValueError("length must be non-negative")
    if length > MAX_PAYLOAD:
        raise ValueError("payload exceeds configured limit")
    return length

print(validate_payload_length(1024))
```

Expected output: `1024`.

Only after validation should code allocate a buffer or request that many bytes. A safe cap is application-specific: derive it from the protocol, memory budget, concurrency, and expected workload. Also validate that the declared length is plausible relative to the remaining input and enforce timeouts/limits when reading from network sources.

### 10.2 Bounded exact reads

```python
def read_exact(file, length: int, *, max_length: int = 8 * 1024 * 1024) -> bytes:
    if not isinstance(length, int) or isinstance(length, bool):
        raise TypeError("length must be an integer")
    if not isinstance(max_length, int) or isinstance(max_length, bool):
        raise TypeError("max_length must be an integer")
    if max_length < 0:
        raise ValueError("max_length must be non-negative")
    if length < 0 or length > max_length:
        raise ValueError("invalid or excessive length")

    result = bytearray(length)
    view = memoryview(result)
    offset = 0
    try:
        while offset < length:
            remaining = view[offset:]
            try:
                count = file.readinto(remaining)
            finally:
                remaining.release()
            if count is None:
                raise BlockingIOError("readinto would block; read_exact expects a blocking stream")
            if count == 0:
                raise EOFError("input ended before requested length")
            offset += count
    finally:
        view.release()
    return bytes(result)
```

Example test:

```python
from io import BytesIO

print(read_exact(BytesIO(b"abcdef"), 4))
try:
    read_exact(BytesIO(b"ab"), 4)
except EOFError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
b'abcd'
EOFError
```

The cap limits requested allocation but is not a complete resource policy by itself. In production, choose a realistic maximum, consider aggregate memory across concurrent requests, and account for any other copies made downstream. A zero-length request returns `b""`.

### 10.3 Practical production checklist

- Keep text as `str` and binary payloads as bytes-like objects until a real boundary requires conversion.
- Specify encodings explicitly; do not rely on locale defaults for persistent data or protocols.
- Treat error handlers such as `ignore` as lossy transformations.
- Validate declared lengths before allocation and before slicing based on those lengths.
- Handle EOF and partial reads explicitly.
- Release views when finished; do not resize a `bytearray` while exported views remain active.
- Make buffer ownership and lifetime explicit in APIs that yield or retain views.
- Use established parsers for real binary formats; this lesson does not replace `struct` or format-specific validation.
- Measure end-to-end behavior before optimizing; zero-copy is a trade-off, not a goal by itself.

---

## 11. Common mistakes and fixes

| Mistake | Why it fails | Better approach |
|---|---|---|
| Treating `str` as raw bytes | Text is Unicode; encoding is a separate step | Use explicit `.encode(codec)` / `.decode(codec)` |
| Expecting `b"A"[0]` to be `b"A"` | Byte indexing returns an integer | Use `data[0]` as a numeric byte or `data[:1]` for a one-byte slice |
| Assuming `len(text)` equals encoded byte length | UTF-8 characters can occupy multiple bytes | Measure `len(text.encode("utf-8"))` for byte limits |
| Decoding each chunk independently | A multibyte character may cross a chunk boundary | Use an incremental decoder |
| Truncating arbitrary UTF-8 bytes | The cut can split a character | Truncate on a valid boundary or by encoded character sizes |
| Using `errors="ignore"` as a universal repair | It silently loses data | Prefer strict errors or a documented recovery policy |
| Assuming encoding can always be detected | Many byte sequences are valid under multiple encodings | Use metadata/BOM/protocol contracts; treat heuristics as estimates |
| Slicing large `bytes` repeatedly | Each slice copies the selected data | Consider `memoryview` or streaming |
| Calling `len(view)` for bytes in a typed view | `len` counts first-dimension elements | Use `.nbytes` for represented byte count |
| Resizing a bytearray while a view is active | Exported storage cannot be resized | Release all relevant views first |
| Assuming `.cast("H")` is portable | Native format and byte order are platform-dependent | Use explicit protocol decoding |
| Processing all of a `readinto()` buffer after a short read | The unused tail may contain stale data | Process only `buffer[:count]` |
| Trusting a file's length field | It can trigger excessive allocation or invalid slicing | Validate type, range, and available bytes first |
| Claiming `sys.getsizeof()` is total memory | It is a shallow size | Use it cautiously; profile the real workload |

---

## 12. Hands-on exercises

Work through these in order. Try each exercise before reading the answer key.

### Exercise 1 — Guided: inspect UTF-8

Given `word = "café"`:

1. Encode it as UTF-8.
2. Print the bytes and hex form.
3. Print the character count and byte count.
4. Decode it and assert that the original text is recovered.

### Exercise 2 — Guided: edit a buffer

Start with `bytearray(b"GET /v1")`. Change `GET` to `PUT`, append `b" HTTP/1.1"`, and print the final buffer.

### Exercise 3 — Intermediate: signed integer conversion

Encode `-1234` into exactly two big-endian signed bytes. Decode the bytes back and assert equality. Explain why unsigned conversion is unsuitable.

### Exercise 4 — Intermediate: safe chunking

Write `count_bytes(stream, chunk_size)` that reads a binary stream in chunks and returns the total number of bytes. Reject non-positive chunk sizes. Test it with `BytesIO`.

### Exercise 5 — Intermediate: preserve dirty input

Given `raw = b"key=\xff"`, decode with UTF-8 plus `surrogateescape`, then re-encode using the same codec and error policy. Assert byte-for-byte equality.

### Exercise 6 — Advanced: parse a framed message

A message consists of a four-byte ASCII tag, followed by a two-byte unsigned big-endian payload length, followed by the payload. Write `parse_message(data, max_payload=1024)` that:
- rejects data shorter than six bytes;
- validates the declared length against `max_payload`;
- rejects truncated payloads and trailing bytes;
- returns `(tag, payload)` without copying the payload during parsing if possible.

Hint: use a `memoryview`, `int.from_bytes`, and explicit release. Returning a view means the caller must manage its lifetime and the underlying storage remains retained.

### Exercise 7 — Advanced: benchmark responsibly

Adapt the benchmark in Section 7.2 to compare 16-byte, 4-KiB, and 1-MiB slices. Run multiple repetitions. Write down the Python version, machine/OS, and results. Explain why a microbenchmark alone does not prove end-to-end superiority.

---

## 13. Answer key and reference solutions

### Exercise 1

```python
word = "café"
encoded = word.encode("utf-8")
print(encoded)
print(encoded.hex())
print(len(word), len(encoded))
assert encoded.decode("utf-8") == word
```

Expected output:

```text
b'caf\xc3\xa9'
636166c3a9
4 5
```

The final assertion passes.

### Exercise 2

```python
request = bytearray(b"GET /v1")
request[:3] = b"PUT"
request.extend(b" HTTP/1.1")
print(request)
```

Expected output: `bytearray(b'PUT /v1 HTTP/1.1')`.

### Exercise 3

```python
encoded = (-1234).to_bytes(2, "big", signed=True)
decoded = int.from_bytes(encoded, "big", signed=True)
print(encoded.hex(), decoded)
assert decoded == -1234
```

Expected output: `fb2e -1234`. The signed representation is required to represent a negative integer in the chosen fixed width.

### Exercise 4

```python
def count_bytes(stream, chunk_size):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    total = 0
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            return total
        total += len(chunk)

from io import BytesIO
assert count_bytes(BytesIO(b"abcdefgh"), 3) == 8
```

The assertion passes. A production version may also validate the type of `chunk_size` if the function is part of a public API.

### Exercise 5

```python
raw = b"key=\xff"
text = raw.decode("utf-8", errors="surrogateescape")
assert text.encode("utf-8", errors="surrogateescape") == raw
```

The assertion passes. Do not send the surrogate-containing text to systems that require ordinary Unicode text without understanding the consequences.

### Exercise 6

```python
def parse_message(data, max_payload=1024):
    if not isinstance(max_payload, int) or isinstance(max_payload, bool):
        raise TypeError("max_payload must be an integer")
    if max_payload < 0:
        raise ValueError("max_payload must be non-negative")

    view = memoryview(data)
    try:
        # This parser treats offsets as byte offsets. Require a contiguous,
        # one-dimensional, one-byte buffer rather than silently misreading
        # a typed or strided memoryview.
        if view.ndim != 1 or view.itemsize != 1 or not view.c_contiguous:
            raise TypeError("data must expose a contiguous one-dimensional byte buffer")
        if view.nbytes < 6:
            raise ValueError("truncated header")
        tag_view = view[:4]
        try:
            tag = bytes(tag_view)
        finally:
            tag_view.release()
        length_view = view[4:6]
        try:
            declared = int.from_bytes(length_view, "big")
        finally:
            length_view.release()
        if declared > max_payload:
            raise ValueError("payload too large")
        expected = 6 + declared
        if view.nbytes < expected:
            raise ValueError("truncated payload")
        if view.nbytes > expected:
            raise ValueError("trailing bytes")
        # The returned child view retains the exporter. The caller owns it
        # and must release it when finished.
        return tag, view[6:expected]
    finally:
        view.release()

message = b"DATA" + (3).to_bytes(2, "big") + b"xyz"
tag, payload = parse_message(message)
try:
    assert tag == b"DATA"
    assert bytes(payload) == b"xyz"
finally:
    payload.release()
```

The assertions pass. The payload is returned as a view rather than a copy. The caller must release it; a production API should document this ownership contract. The parser also rejects extra trailing bytes, as specified.

### Exercise 7

There is no universal expected timing output. Record actual results from your environment. A valid conclusion should mention that `memoryview` avoids copying selected payload bytes but still creates a view object, and that downstream work, memory retention, and access patterns affect end-to-end performance.

---

## 14. Roadmap self-check — with reasoning

### 1. What do `len("é")` and `len("é".encode())` return and why?

For the precomposed string `"é"` in Python 3.12+, `len("é")` is `1`: the string contains one Unicode code point. `len("é".encode("utf-8"))` is `2`: UTF-8 represents that code point using two bytes. Character count and encoded byte count are different measurements.

### 2. How does `memoryview` avoid copying and what is the risk when the underlying object resizes?

A memoryview references storage exported by an object implementing the buffer protocol. Slicing creates another view over a region of the same storage rather than copying that region into a new bytes object. A live exported view prevents a resizable exporter such as `bytearray` from resizing; mutation may also be visible through all views. Release views when finished and document ownership/lifetime.

### 3. Write `read_chunks(path, size)` yielding `memoryview`s from a reusable buffer.

One implementation is below. Its views are **borrowed**: the caller must consume and release each view before requesting the next item because the next read reuses and overwrites the same buffer.

```python
from pathlib import Path

def read_chunks(path, size):
    if size <= 0:
        raise ValueError("size must be positive")
    with Path(path).open("rb") as file:
        buffer = bytearray(size)
        parent = memoryview(buffer)
        try:
            while True:
                count = file.readinto(buffer)
                if count == 0:
                    break
                child = parent[:count]
                try:
                    yield child
                finally:
                    child.release()
        finally:
            parent.release()
```

Usage must respect the borrowed-view contract:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = Path(directory) / "sample.bin"
    path.write_bytes(b"abcdef")
    for borrowed in read_chunks(path, 2):
        print(bytes(borrowed))
```

Expected output:

```text
b'ab'
b'cd'
b'ef'
```

The generator releases each child view when the iteration resumes or closes. Consumers should not retain a borrowed view beyond the current iteration. If independent chunks are required, yield `bytes(parent[:count])` instead; that copies each chunk but gives it independent ownership.

---

## 15. Essential glossary

- **Byte:** An eight-bit unit; Python byte values range from 0 to 255.
- **Code point:** A numbered value in the Unicode codespace.
- **Encoding:** A rule for representing text as bytes, such as UTF-8.
- **Decoding:** Interpreting bytes under a specified encoding to produce text.
- **BOM (byte-order mark):** A leading byte sequence that may identify a Unicode encoding or byte order.
- **Mojibake:** Text that appears corrupted because bytes were decoded using an incorrect encoding or were transformed incorrectly.
- **Immutable:** An object whose contents cannot be changed after creation (`str`, `bytes`).
- **Mutable:** An object whose contents can be changed (`bytearray`).
- **Buffer protocol:** An interface for exposing memory to other Python objects.
- **Exporter:** An object that provides a buffer, such as `bytearray` or `array.array`.
- **View:** An object that references existing storage instead of owning an independent copy of the selected data.
- **Zero-copy:** A design that avoids a particular data copy; it does not mean zero allocation or zero overhead everywhere.
- **Endianness:** The order in which bytes represent a multi-byte value.
- **Partial read:** A read that returns fewer bytes than requested.
- **Incremental decoder:** A decoder that retains state across chunks when a character spans chunk boundaries.
- **`surrogateescape`:** An error handler that preserves certain undecodable bytes through surrogate code points for round-trip scenarios.
- **Constant-time comparison:** A comparison designed to avoid content-dependent timing differences; use `hmac.compare_digest()` for relevant secret comparisons.

---

## 16. Version notes

- **Python 3.12+ target:** All core examples in this lesson use APIs available in Python 3.12.
- No Python 3.13- or 3.14-specific feature is required here.
- Native `memoryview.cast()` format sizes and byte order are platform-dependent; this is not a Python-version difference.
- Exact object sizes, allocation strategies, and benchmark timings are implementation- and environment-dependent. Do not encode them as correctness assumptions.

---

## 17. Completion checklist

Before moving to Lesson 02, verify that you can:

- [ ] Explain the roles and mutability of `str`, `bytes`, `bytearray`, and `memoryview`.
- [ ] Construct bytes, inspect hex, and explain byte indexing/slicing.
- [ ] Encode/decode explicitly and explain error-handler trade-offs.
- [ ] Convert integers with the correct width, endianness, and signedness.
- [ ] Read binary files in chunks and process only the valid bytes from partial reads.
- [ ] Explain BOMs, heuristic encoding detection, and `surrogateescape`.
- [ ] Use `memoryview` and release views without accidentally resizing an exported buffer.
- [ ] Explain why `memoryview` can reduce copying but can retain storage and complicate ownership.
- [ ] Truncate UTF-8 safely, use incremental decoding, and validate untrusted lengths.
- [ ] Complete the exercises and run the tests below.

### Final practical task

Build a small **binary payload inspector** that accepts a bytes payload, prints its total byte length and hexadecimal representation, reads the first four bytes as a tag, reads the next two bytes as an unsigned big-endian length, validates that the declared payload length is below a configured cap, and returns a `memoryview` of the payload without copying it. Add tests for a valid message, a truncated header, an oversized length, and a truncated payload. Document who must release the returned view.

## 18. Regression tests

Save this section as `test_bytes_buffers.py` or run it as a standalone script. It uses only the standard library and generated in-memory data.

```python
import codecs
import unittest
from io import BytesIO


def parse_message(data, max_payload=1024):
    if not isinstance(max_payload, int) or isinstance(max_payload, bool):
        raise TypeError("max_payload must be an integer")
    if max_payload < 0:
        raise ValueError("max_payload must be non-negative")

    view = memoryview(data)
    try:
        if view.ndim != 1 or view.itemsize != 1 or not view.c_contiguous:
            raise TypeError("data must expose a contiguous one-dimensional byte buffer")
        if view.nbytes < 6:
            raise ValueError("truncated header")
        tag_view = view[:4]
        try:
            tag = bytes(tag_view)
        finally:
            tag_view.release()
        length_view = view[4:6]
        try:
            declared = int.from_bytes(length_view, "big")
        finally:
            length_view.release()
        if declared > max_payload:
            raise ValueError("payload too large")
        expected = 6 + declared
        if view.nbytes < expected:
            raise ValueError("truncated payload")
        if view.nbytes > expected:
            raise ValueError("trailing bytes")
        return tag, view[6:expected]
    finally:
        view.release()


class BytesBufferTests(unittest.TestCase):
    def test_utf8_round_trip_and_lengths(self):
        text = "café"
        encoded = text.encode("utf-8")
        self.assertEqual(len(text), 4)
        self.assertEqual(len(encoded), 5)
        self.assertEqual(encoded.decode("utf-8"), text)

    def test_hex_round_trip(self):
        data = bytes.fromhex("de ad be ef")
        self.assertEqual(data.hex(), "deadbeef")

    def test_index_and_slice(self):
        data = b"ABC"
        self.assertEqual(data[0], 65)
        self.assertEqual(data[:2], b"AB")

    def test_invalid_utf8_strict(self):
        with self.assertRaises(UnicodeDecodeError):
            b"\xff".decode("utf-8")

    def test_surrogateescape_round_trip(self):
        raw = b"x\xffy"
        text = raw.decode("utf-8", "surrogateescape")
        self.assertEqual(text.encode("utf-8", "surrogateescape"), raw)

    def test_integer_width_error(self):
        with self.assertRaises(OverflowError):
            (256).to_bytes(1, "big")

    def test_incremental_decode_across_chunks(self):
        raw = "A€B".encode("utf-8")
        decoder = codecs.getincrementaldecoder("utf-8")()
        text = decoder.decode(raw[:2])
        text += decoder.decode(raw[2:], final=True)
        self.assertEqual(text, "A€B")

    def test_readinto_partial_tail_is_not_consumed(self):
        stream = BytesIO(b"abcde")
        buffer = bytearray(3)
        outputs = []
        while True:
            count = stream.readinto(buffer)
            if count == 0:
                break
            outputs.append(bytes(memoryview(buffer)[:count]))
        self.assertEqual(outputs, [b"abc", b"de"])

    def test_memoryview_mutates_exporter_and_blocks_resize(self):
        data = bytearray(b"abc")
        view = memoryview(data)
        view[0] = ord("X")
        self.assertEqual(data, bytearray(b"Xbc"))
        with self.assertRaises(BufferError):
            data.extend(b"d")
        view.release()
        data.extend(b"d")
        self.assertEqual(data, bytearray(b"Xbcd"))

    def test_parse_message_returns_owned_payload_view(self):
        message = b"DATA" + (3).to_bytes(2, "big") + b"xyz"
        tag, payload = parse_message(message)
        try:
            self.assertEqual(tag, b"DATA")
            self.assertEqual(bytes(payload), b"xyz")
        finally:
            payload.release()

    def test_parse_message_rejects_truncated_header(self):
        with self.assertRaisesRegex(ValueError, "truncated header"):
            parse_message(b"DATA\x00")

    def test_parse_message_rejects_oversized_length(self):
        message = b"DATA" + (4).to_bytes(2, "big") + b"abcd"
        with self.assertRaisesRegex(ValueError, "payload too large"):
            parse_message(message, max_payload=3)

    def test_parse_message_rejects_truncated_payload(self):
        message = b"DATA" + (4).to_bytes(2, "big") + b"abc"
        with self.assertRaisesRegex(ValueError, "truncated payload"):
            parse_message(message)

    def test_parse_message_rejects_trailing_bytes(self):
        message = b"DATA" + (1).to_bytes(2, "big") + b"xy"
        with self.assertRaisesRegex(ValueError, "trailing bytes"):
            parse_message(message)

    def test_parse_message_rejects_invalid_cap(self):
        with self.assertRaises(ValueError):
            parse_message(b"DATA\x00\x00", max_payload=-1)
        with self.assertRaises(TypeError):
            parse_message(b"DATA\x00\x00", max_payload=True)

    def test_bytearray_is_unhashable(self):
        with self.assertRaises(TypeError):
            hash(bytearray(b"x"))


if __name__ == "__main__":
    unittest.main()
```

Run with:

```bash
python -m unittest -v test_bytes_buffers.py
```

The tests are self-contained and cover valid framing plus malformed headers, oversized lengths, truncated payloads, and trailing bytes. They are included as runnable lesson content; do not interpret their presence as evidence that they were executed in your environment.
