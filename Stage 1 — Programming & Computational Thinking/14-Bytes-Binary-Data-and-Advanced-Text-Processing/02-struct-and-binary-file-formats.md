# 02 — `struct` and Binary File Formats

> **Target:** Python 3.12+  
> **Stage:** 1 — Programming & Computational Thinking  
> **Module:** 14 — Bytes, Binary Data and Advanced Text Processing  
> **Prerequisite:** `01-bytes-bytearray-and-memoryview.md`

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain why a binary format specifies field widths, byte order, and layout.
- Use `struct.pack`, `unpack`, `calcsize`, `Struct`, `unpack_from`, `pack_into`, and `iter_unpack` correctly.
- Choose portable format prefixes and explain the difference between standard layouts and native alignment.
- Encode and decode fixed-width byte fields without confusing padding, truncation, or text encoding.
- Parse a small real file header and a custom record format with explicit bounds checks.
- Handle short reads, malformed input, hostile length fields, checksums, version fields, and flags.
- Implement and test a bounded unsigned LEB128-style integer and a simple TLV record.
- Recognize when a mature format library is safer than a new custom format.

## Prerequisites and context

You should already understand binary digits, bytes and hexadecimal; integer ranges; Python functions, exceptions, and file I/O; and the distinction between `str` and `bytes`. Lesson 01 introduces `bytes`, `bytearray`, and `memoryview`; this lesson uses those concepts but does not repeat the full buffer-protocol lesson.

A Python `str` is text. A `bytes` object is a sequence of octets (integers from 0 through 255). A binary file stores octets, not Python objects or human-readable numbers. For example, the integer `258` has no unique byte representation until a width and byte order are chosen:

```python
print((258).to_bytes(2, "big").hex())
print((258).to_bytes(2, "little").hex())
```

Expected output:

```text
0102
0201
```

A binary **format** defines how to interpret those octets: field order, widths, signedness, byte order, padding, and sometimes versions and checksums. `struct` maps a specified fixed layout to Python values. It does not discover a format for you, validate every semantic rule, or make untrusted input safe automatically.

## 1. Why fixed-width binary fields exist

Fixed-width fields make offsets and record sizes predictable. A network packet might contain a 2-byte message type, a 4-byte payload length, and a fixed-size identifier. A file header might start with a signature and version, followed by dimensions or offsets. Sensor logs often store many same-shaped records back-to-back.

The format specification must answer at least these questions:

1. Which field comes first, and how many bytes does it occupy?
2. Is an integer signed or unsigned?
3. Which byte is most significant: big-endian or little-endian?
4. Are there padding bytes? If so, are they part of the format or merely native compiler alignment?
5. How are text bytes encoded, terminated, or padded?
6. How can a reader distinguish a supported version from an unknown one?
7. What lengths and values are valid, and how are corrupt records detected?

A field's width is not the same thing as its meaning. Four bytes might represent an unsigned integer, a signed integer, a 32-bit float, or four literal bytes. The format defines which.

## 2. The `struct` essentials

```python
import struct

packed = struct.pack("<IHf", 42, 7, 3.5)
print(packed.hex())
print(struct.calcsize("<IHf"))
print(struct.unpack("<IHf", packed))
```

Expected output:

```text
2a000000070000006040
10
(42, 7, 3.5)
```

`<IHf` is **little-endian**, with standard field sizes and no alignment padding:

- `<` — little-endian byte order, standard sizes, no alignment padding.
- `I` — unsigned 4-byte integer (`42`).
- `H` — unsigned 2-byte integer (`7`).
- `f` — 4-byte IEEE 754 binary floating-point value (`3.5`).

The size is `4 + 2 + 4 = 10` bytes. The hexadecimal output is eight bytes for the integer, two for the short integer, and four for the float: `2a000000 0700 00006040`. (Whitespace is added here only for readability.)

`struct.pack(fmt, ...)` returns a new `bytes` object. It raises `struct.error` if the format is invalid, the number of values does not match, or a value cannot fit its field. `struct.unpack(fmt, buffer)` requires a buffer of exactly `struct.calcsize(fmt)` bytes and returns a tuple. Too few or too many bytes raise `struct.error`; do not rely on unpacking to validate the rest of a file.

`struct.calcsize(fmt)` returns the byte size of the format under its selected prefix. Calculate sizes from the format instead of duplicating a magic number in code.

## 3. Format prefixes: byte order, sizes, and alignment

The optional first character controls the layout. For portable file and network formats, choose the byte order explicitly.

| Prefix | Byte order | Field sizes | Alignment | Typical use |
|---|---|---|---|---|
| `<` | Little-endian | Standard | None | Portable formats defined as little-endian |
| `>` | Big-endian | Standard | None | Portable formats defined as big-endian |
| `!` | Network (big-endian) | Standard | None | Network protocol fields |
| `=` | Native byte order | Standard | None | Native-endian data with a standard layout, usually not ideal for interchange |
| `@` | Native byte order | Native | Native alignment between fields | Interfacing with a matching C ABI on the same platform/build |

If no prefix is supplied, `@` is the default. This is a common portability bug: an omitted prefix can make a layout depend on the machine and C compiler ABI. Even when `@` fields have familiar sizes, the offsets and total size can differ due to alignment. For example, on many common platforms `@BI` includes padding between the one-byte `B` and four-byte `I`, whereas `<BI` is exactly five bytes. Native sizes and alignment are platform-dependent; verify with `calcsize` on the target platform instead of assuming a particular result.

`>` and `!` have the same byte order and standard layout. `=` is **not** the same as `<`: it uses the host's native byte order, but standard sizes and no alignment. `sys.byteorder` reports the interpreter's native byte order (`"little"` or `"big"`); portable file formats should not need to guess it.

```python
import struct
import sys

print(sys.byteorder in {"little", "big"})
print(struct.calcsize("<BI"))  # 5 everywhere supported by struct
print(struct.calcsize("!I"))   # 4
print(struct.calcsize("=I"))   # 4
print("native @I size:", struct.calcsize("@I"))
```

Expected output begins with `True`, `5`, and `4`. The `=I` and `@I` sizes are printed as `4` on most modern systems; the native `@I` result is deliberately shown as a runtime value because it follows the platform's C ABI rather than a portable file-format promise.

**Rule:** write a format specification with `<`, `>`, or `!` unless the data is explicitly defined in native ABI terms. Never use `@` for a portable file format merely because it works on your computer.

## 4. Format characters and field widths

The following are the characters in the roadmap's required set. Except for `s` and `x`, a repeat count means repeated values/fields; for `Ns`, the count is the size of one fixed-width byte-string field.

| Character | Meaning | Standard size | Value returned / expected |
|---|---|---:|---|
| `b` | signed integer | 1 byte | `-128` through `127` |
| `B` | unsigned integer | 1 byte | `0` through `255` |
| `h` | signed short integer | 2 bytes | `-32768` through `32767` |
| `H` | unsigned short integer | 2 bytes | `0` through `65535` |
| `i` | signed integer | 4 bytes | signed 32-bit range in standard layouts |
| `I` | unsigned integer | 4 bytes | `0` through `2**32 - 1` |
| `q` | signed long long integer | 8 bytes | signed 64-bit range |
| `Q` | unsigned long long integer | 8 bytes | `0` through `2**64 - 1` |
| `f` | IEEE 754 binary32 float | 4 bytes | Python `float` on unpack; rounded to binary32 precision |
| `d` | IEEE 754 binary64 float | 8 bytes | Python `float` on unpack |
| `?` | Boolean | 1 byte in standard layouts | `bool`; nonzero values unpack as `True` |
| `Ns` | exactly `N` bytes | `N` bytes | one `bytes` object |
| `x` | pad byte | 1 byte each | consumes/produces a zero pad byte; no tuple value |

For standard prefixes (`<`, `>`, `!`, `=`), `b/B` are 1 byte, `h/H` 2, `i/I/f` 4, and `q/Q/d` 8. Native `@` follows native C sizes/alignment; the common widths shown above are not a substitute for checking the platform's ABI. The `q` and `Q` formats are available on standard Python platforms.

```python
import struct

print(struct.unpack(">bBhH", struct.pack(">bBhH", -2, 250, -300, 60000)))
print(struct.unpack("<2s2xH", struct.pack("<2s2xH", b"OK", 513)))
print(struct.unpack("< ? 3s", struct.pack("<?3s", True, b"cat")))
```

Expected output:

```text
(-2, 250, -300, 60000)
(b'OK', 513)
(True, b'cat')
```

The second format, `<2s2xH`, consists of a two-byte string, two pad bytes, and a little-endian unsigned two-byte integer. The `2x` bytes do not appear in the returned tuple. Whitespace in format strings is ignored, but avoid unusual spacing when it makes a format harder to review.

### Range errors are useful

`struct.pack` does not silently wrap out-of-range integer values:

```python
import struct

for value in (-1, 256):
    try:
        struct.pack("<B", value)
    except struct.error as exc:
        print(type(exc).__name__)
```

Expected output:

```text
error
error
```

The exception class is `struct.error` (whose displayed class name is `error`). Validate domain-specific ranges explicitly if you want clearer error messages; do not mask a range error by silently clipping values unless clipping is part of the format's specification.

## 5. Fixed-width byte strings, padding, and text

`4s` means one field containing exactly four bytes. It does **not** mean four Unicode characters. `struct.pack` pads a short `s` field with zero bytes and truncates a longer value to the specified width. Truncation is silent, so validate input length when losing bytes would be a bug.

```python
import struct

print(struct.pack("<4s", b"A").hex())
print(struct.pack("<4s", b"ABCDE"))
print(struct.unpack("<4s", b"A\x00\x00\x00"))
```

Expected output:

```text
41000000
b'ABCD'
(b'A\x00\x00\x00',)
```

Whether trailing zero bytes are padding depends on the format. If the field is specified as a null-padded ASCII identifier, `raw.rstrip(b"\x00")` may be appropriate. If embedded or trailing zero bytes are valid data, stripping them destroys information. If the field is a null-terminated C string, the first zero byte may terminate the text; that is a different convention. Follow the file format, not a universal rule.

Decode explicitly after extracting the field:

```python
raw_name = struct.unpack("<8s", b"report\x00\x00")[0]
name = raw_name.rstrip(b"\x00").decode("ascii", errors="strict")
print(name)
```

Expected output: `report`

`struct` handles bytes and numbers, not character encodings. A fixed-width text field may be UTF-8, ASCII, a legacy code page, or opaque bytes. If a UTF-8 string is truncated to fit a fixed byte width, the cut can split a multibyte sequence; decide whether the format rejects, replaces, or otherwise handles such data. Do not assume byte count equals character count.

## 6. Reusable layouts and offsets

### `struct.Struct`

A `Struct` object compiles a format for reuse and exposes `.size`, `.pack`, `.unpack`, `.pack_into`, `.unpack_from`, and `.iter_unpack`.

```python
import struct

RECORD = struct.Struct("<Ih8s")  # uint32, int16, exactly 8 bytes
print(RECORD.size)
encoded = RECORD.pack(7, -3, b"sensor")
print(RECORD.unpack(encoded))
```

Expected output:

```text
14
(7, -3, b'sensor\x00\x00')
```

The layout is 4 + 2 + 8 = 14 bytes. `Struct` can make repeated operations clearer and avoids repeating a format literal; it does not change the validation responsibilities of the caller.

### `unpack_from` and `pack_into`

These methods work at an offset in an existing buffer. `unpack_from` requires enough bytes from the offset through the end of the requested record. `pack_into` requires a writable buffer with enough room at that offset. Both raise `struct.error` if the buffer/offset is unsuitable.

```python
import struct

ITEM = struct.Struct(">H")
buf = bytearray(6)
ITEM.pack_into(buf, 2, 513)
print(buf.hex())
print(ITEM.unpack_from(buf, 2))
```

Expected output:

```text
000002010000
(513,)
```

Here `>H` is a two-byte unsigned integer in big-endian order, so `513` is `02 01`. The other four bytes stay zero because the `bytearray` was initialized to zeros.

### `iter_unpack`

`iter_unpack` iterates over consecutive fixed-size records. The buffer length must be an exact multiple of the format size; otherwise it raises `struct.error`. Check the input length or deliberately separate a trailing partial record before calling it.

```python
import struct

PAIR = struct.Struct("<HH")
data = PAIR.pack(1, 10) + PAIR.pack(2, 20)
print(list(PAIR.iter_unpack(data)))
```

Expected output:

```text
[(1, 10), (2, 20)]
```

The iterator avoids building an intermediate list of tuples until you ask for one; `list(...)` here materializes all records. It still returns a tuple per record. For large files, read bounded chunks and preserve any incomplete trailing record between reads rather than loading the whole file without a size limit.

## 7. Read exact amounts; never assume one read is enough

A file object's `read(n)` may return fewer than `n` bytes before EOF. This is especially important for sockets and other streams, and a robust file parser should not interpret a short result as a complete field. Use a helper that loops until it has all requested bytes or encounters EOF:

```python
def read_exact(stream, size: int) -> bytes:
    """Read exactly size bytes or raise EOFError; size must be non-negative."""
    if size < 0:
        raise ValueError("size must be non-negative")
    chunks = []
    remaining = size
    while remaining:
        chunk = stream.read(remaining)
        if not chunk:
            received = size - remaining
            raise EOFError(f"needed {size} bytes, received {received}")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)
```

The helper is bounded by `size`, but the caller must still cap `size` before calling it if the value came from an untrusted header. For an ordinary local regular file, a short read often indicates EOF; for generic streams, the loop also handles a stream that returns small pieces. This helper assumes a blocking binary stream whose `read(n)` returns bytes or an empty bytes-like value at EOF; non-blocking sockets need readiness handling and may raise `BlockingIOError` instead.

## 8. Worked real-format parser: PNG signature and IHDR

PNG is a useful example because the format explicitly defines big-endian lengths and a CRC32 per chunk. A PNG begins with an 8-byte signature. Each chunk has:

- a 4-byte big-endian unsigned length `L`;
- a 4-byte chunk type;
- `L` bytes of chunk data;
- a 4-byte big-endian CRC32 over **chunk type + chunk data** (not over the length field).

The first chunk is `IHDR`, whose data length must be 13 bytes. Its data contains width (4), height (4), bit depth (1), color type (1), compression method (1), filter method (1), and interlace method (1). The following parser reads and validates this header and first chunk. It does **not** decode image pixels or validate the entire PNG file.

```python
import struct
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHUNK_PREFIX = struct.Struct(">I4s")  # uint32 length, 4-byte chunk type
IHDR_DATA = struct.Struct(">IIBBBBB") # uint32 width/height, five uint8 fields
U32 = struct.Struct(">I")
MAX_PNG_CHUNK = 64 * 1024 * 1024      # local parser policy: 64 MiB cap


def read_exact(stream, size: int) -> bytes:
    if size < 0:
        raise ValueError("size must be non-negative")
    parts = []
    remaining = size
    while remaining:
        part = stream.read(remaining)
        if not part:
            raise EOFError(f"truncated input: wanted {size} bytes")
        parts.append(part)
        remaining -= len(part)
    return b"".join(parts)


def parse_png_ihdr(stream):
    signature = read_exact(stream, len(PNG_SIGNATURE))
    if signature != PNG_SIGNATURE:
        raise ValueError("invalid PNG signature")

    length, chunk_type = CHUNK_PREFIX.unpack(read_exact(stream, CHUNK_PREFIX.size))
    if length > MAX_PNG_CHUNK:
        raise ValueError("PNG chunk exceeds configured size limit")
    if chunk_type != b"IHDR":
        raise ValueError("first PNG chunk must be IHDR")
    if length != IHDR_DATA.size:
        raise ValueError("IHDR data length must be 13 bytes")

    data = read_exact(stream, length)
    stored_crc = U32.unpack(read_exact(stream, U32.size))[0]
    calculated_crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    if stored_crc != calculated_crc:
        raise ValueError("IHDR CRC32 mismatch")

    width, height, bit_depth, color_type, compression, filtering, interlace = IHDR_DATA.unpack(data)
    # PNG stores each dimension in a uint32 field, but the format's valid
    # range is 1..2**31-1 (not the entire unsigned 32-bit range).
    if not (1 <= width <= 0x7FFFFFFF and 1 <= height <= 0x7FFFFFFF):
        raise ValueError("PNG width and height must be in 1..2**31-1")
    if compression != 0 or filtering != 0 or interlace not in (0, 1):
        raise ValueError("unsupported or invalid IHDR method field")

    # Legal bit-depth/color-type combinations are format-specific; check them too.
    valid_depths = {
        0: {1, 2, 4, 8, 16},
        2: {8, 16},
        3: {1, 2, 4, 8},
        4: {8, 16},
        6: {8, 16},
    }
    if color_type not in valid_depths or bit_depth not in valid_depths[color_type]:
        raise ValueError("invalid PNG bit-depth/color-type combination")

    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "interlace": interlace,
    }
```

### Build a tiny valid test chunk

This fixture is only a valid signature plus an IHDR chunk; it is not a complete PNG image because it has no image-data or IEND chunks.

```python
import io
import struct
import zlib

sig = b"\x89PNG\r\n\x1a\n"
kind = b"IHDR"
data = struct.pack(">IIBBBBB", 640, 480, 8, 2, 0, 0, 0)
chunk = struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
fixture = sig + chunk
print(parse_png_ihdr(io.BytesIO(fixture)))
```

Expected output:

```text
{'width': 640, 'height': 480, 'bit_depth': 8, 'color_type': 2, 'interlace': 0}
```

### Negative tests

```python
import io

bad_dimensions = (
    PNG_SIGNATURE
    + struct.pack(">I4s", 13, b"IHDR")
    + struct.pack(">IIBBBBB", 0x80000000, 1, 8, 2, 0, 0, 0)
    + struct.pack(">I", zlib.crc32(b"IHDR" + struct.pack(">IIBBBBB", 0x80000000, 1, 8, 2, 0, 0, 0)) & 0xFFFFFFFF)
)
for label, content in (
    ("bad signature", b"NOTPNG!!"),
    ("truncated", PNG_SIGNATURE + b"\x00\x00"),
    ("bad CRC", fixture[:-1] + bytes([fixture[-1] ^ 1])),
    ("invalid dimensions", bad_dimensions),
):
    try:
        parse_png_ihdr(io.BytesIO(content))
    except (ValueError, EOFError) as exc:
        print(label, type(exc).__name__)
```

Expected output:

```text
bad signature ValueError
truncated EOFError
bad CRC ValueError
invalid dimensions ValueError
```

A CRC is an error-detection mechanism, not a cryptographic signature or proof of authenticity. An attacker who can change data can generally recompute a CRC. If authenticity or tamper resistance is required, use a cryptographic MAC or digital signature designed for the threat model; do not substitute CRC32.

**Bounds-checking order matters:** validate the length against both the format's rules and your application limit before reading or allocating that many bytes. A field being representable as a 32-bit unsigned integer does not mean allocating that many bytes is safe.

## 9. A tiny custom record format

Custom formats are excellent exercises, but production formats require a written specification, compatibility policy, and adversarial tests. Here is a deliberately small educational format:

- Header: `>4sBBH` — magic `b"DLOG"` (4 bytes), version (1 byte), flags (1 byte), record count (2-byte unsigned integer).
- Each record: `>Ih8s` — identifier (4-byte unsigned integer), temperature in tenths of a degree (2-byte signed integer), label (8 bytes, zero-padded UTF-8/ASCII for this example).
- Footer: `>I` — CRC32 over every preceding file byte.
- Version 1 permits only flag bit 0; unknown flag bits are rejected. Record count is capped by the parser policy below.
- Labels in this example must be 1–8 ASCII bytes and cannot contain NUL; this avoids ambiguous null-padding semantics.

The format's fixed sizes are computed once:

```python
import struct

LOG_HEADER = struct.Struct(">4sBBH")
LOG_RECORD = struct.Struct(">Ih8s")
LOG_CRC = struct.Struct(">I")
MAX_RECORDS = 10_000
MAGIC = b"DLOG"
VERSION = 1
KNOWN_FLAGS = 0b0000_0001
print(LOG_HEADER.size, LOG_RECORD.size, LOG_CRC.size)
```

Expected output: `8 14 4`

### Encoder and parser

```python
import struct
import zlib

LOG_HEADER = struct.Struct(">4sBBH")
LOG_RECORD = struct.Struct(">Ih8s")
LOG_CRC = struct.Struct(">I")
MAGIC = b"DLOG"
VERSION = 1
KNOWN_FLAGS = 0b0000_0001
MAX_RECORDS = 10_000


def encode_log(records, flags=0):
    # Bound materialization too: do not consume an arbitrarily long iterable
    # before discovering that the file format's record limit was exceeded.
    bounded_records = []
    for record in records:
        if len(bounded_records) >= MAX_RECORDS:
            raise ValueError("too many records")
        bounded_records.append(record)
    records = bounded_records
    if not 0 <= flags <= 0xFF or flags & ~KNOWN_FLAGS:
        raise ValueError("unsupported flags")

    output = bytearray(LOG_HEADER.pack(MAGIC, VERSION, flags, len(records)))
    for identifier, temperature_tenths, label in records:
        if not 0 <= identifier <= 0xFFFFFFFF:
            raise ValueError("identifier out of range")
        if not -32768 <= temperature_tenths <= 32767:
            raise ValueError("temperature out of range")
        if not isinstance(label, str):
            raise TypeError("label must be str")
        label_bytes = label.encode("ascii", errors="strict")
        if not 1 <= len(label_bytes) <= 8 or b"\x00" in label_bytes:
            raise ValueError("label must be 1–8 non-NUL ASCII bytes")
        output.extend(LOG_RECORD.pack(identifier, temperature_tenths, label_bytes))

    checksum = zlib.crc32(output) & 0xFFFFFFFF
    output.extend(LOG_CRC.pack(checksum))
    return bytes(output)


def decode_log(data):
    # This parser receives bytes already in memory. For file streams, read the
    # fixed header first, validate count, then read only the bounded body.
    view = memoryview(data)
    try:
        minimum = LOG_HEADER.size + LOG_CRC.size
        if view.nbytes < minimum:
            raise ValueError("truncated log header or footer")

        magic, version, flags, count = LOG_HEADER.unpack_from(view, 0)
        if magic != MAGIC:
            raise ValueError("bad log magic")
        if version != VERSION:
            raise ValueError(f"unsupported log version: {version}")
        if flags & ~KNOWN_FLAGS:
            raise ValueError("unknown flag bits")
        if count > MAX_RECORDS:
            raise ValueError("record count exceeds limit")

        expected_size = LOG_HEADER.size + count * LOG_RECORD.size + LOG_CRC.size
        if view.nbytes != expected_size:
            raise ValueError("wrong file length or truncated/trailing data")

        stored_crc = LOG_CRC.unpack_from(view, expected_size - LOG_CRC.size)[0]
        actual_crc = zlib.crc32(view[:expected_size - LOG_CRC.size]) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise ValueError("log CRC32 mismatch")

        records = []
        offset = LOG_HEADER.size
        for _ in range(count):
            identifier, temperature_tenths, raw_label = LOG_RECORD.unpack_from(view, offset)
            offset += LOG_RECORD.size
            # The encoder's contract says ASCII and zero-padding. Reject bytes
            # after the first NUL instead of silently discarding hidden content.
            label_raw, separator, tail = raw_label.partition(b"\x00")
            if separator and any(tail):
                raise ValueError("nonzero bytes after label terminator")
            try:
                label = label_raw.decode("ascii", errors="strict")
            except UnicodeDecodeError as exc:
                raise ValueError("label is not ASCII") from exc
            if not label:
                raise ValueError("empty label")
            records.append((identifier, temperature_tenths, label))
        return {"version": version, "flags": flags, "records": records}
    finally:
        view.release()
```

The parser checks the minimum size before reading fields, validates the magic/version/flags/count, computes the exact expected size using a capped count, rejects both truncation and trailing bytes, and checks the checksum before returning records. In a streaming parser, do not read a count-controlled body until the count has been capped and the total byte size calculated safely. The `memoryview` is released in `finally`; the code does not return a view into the input.

### Round-trip and malformed-input tests

```python
records = [(17, 235, "TEMP"), (18, -12, "HUMID")]
encoded = encode_log(records, flags=1)
decoded = decode_log(encoded)
assert decoded == {"version": 1, "flags": 1, "records": records}
print(decoded["records"])

for bad in (encoded[:-1], encoded + b"x", b"NOPE" + encoded[4:]):
    try:
        decode_log(bad)
    except ValueError as exc:
        print(type(exc).__name__)
```

Expected output:

```text
[(17, 235, 'TEMP'), (18, -12, 'HUMID')]
ValueError
ValueError
ValueError
```

These tests cover a round trip, truncation, trailing data, and invalid magic. The following focused tests demonstrate the hostile-count and invalid-label paths; the label test recomputes CRC so it reaches label validation rather than failing earlier on the checksum.

```python
import zlib

hostile_header = LOG_HEADER.pack(MAGIC, VERSION, 0, MAX_RECORDS + 1)
hostile_count = hostile_header + LOG_CRC.pack(zlib.crc32(hostile_header) & 0xFFFFFFFF)
try:
    decode_log(hostile_count)
except ValueError as exc:
    print(str(exc))

header = LOG_HEADER.pack(MAGIC, VERSION, 0, 1)
invalid_record = LOG_RECORD.pack(1, 0, b"\xff" + b"\x00" * 7)
body = header + invalid_record
invalid_label = body + LOG_CRC.pack(zlib.crc32(body) & 0xFFFFFFFF)
try:
    decode_log(invalid_label)
except ValueError as exc:
    print(str(exc))
```

Expected output:

```text
record count exceeds limit
label is not ASCII
```

A checksum failure and a format failure are different diagnostics, even if both reject the input.

## 10. Length-prefixed strings, TLV, and variable-length integers

### Length-prefixed fields

A length-prefixed field stores a length followed by that many bytes. The reader must validate the length before consuming it, and decode text only after the bytes are read. A fixed-width integer length is easy to parse, but can be wasteful for small values; variable-length integers trade compactness for a more involved decoder.

```python
import struct

text = "hello"
payload = text.encode("utf-8")
wire = struct.pack(">H", len(payload)) + payload  # uint16 byte length
length = struct.unpack_from(">H", wire)[0]
if length > 4096:
    raise ValueError("string exceeds application limit")
if len(wire) != 2 + length:
    raise ValueError("truncated or trailing bytes")
print(wire[2:].decode("utf-8", errors="strict"))
```

Expected output: `hello`

The length counts encoded bytes, not Python characters. The example uses `>H`, so its encoded payload length must fit in an unsigned 16-bit field, and the additional 4096-byte cap is an application policy.

### Unsigned LEB128-style varints

Unsigned LEB128 encodes seven data bits per byte; the high bit (`0x80`) means another byte follows. This teaching implementation accepts unsigned values up to 64 bits and rejects truncation, excessive encodings, overflow, and non-canonical encodings (for example, encoding zero as `80 00`). Protobuf varints use the same basic seven-bit continuation pattern for unsigned values, but a full Protobuf implementation also has field tags and type-specific rules; use its library for actual Protobuf messages.

```python
MAX_U64 = (1 << 64) - 1


def encode_uvarint(value: int) -> bytes:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("value must be an integer")
    if not 0 <= value <= MAX_U64:
        raise ValueError("value must fit unsigned 64 bits")
    out = bytearray()
    while value >= 0x80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)


def decode_uvarint(data: bytes, offset: int = 0) -> tuple[int, int]:
    if not 0 <= offset <= len(data):
        raise ValueError("offset out of range")
    value = 0
    shift = 0
    pos = offset
    while pos < len(data) and pos - offset < 10:
        byte = data[pos]
        pos += 1
        # At byte 10, only the low bit can be used for a 64-bit value.
        if shift == 63 and (byte & 0x7E):
            raise ValueError("unsigned varint overflow")
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            encoded = data[offset:pos]
            if encode_uvarint(value) != encoded:
                raise ValueError("non-canonical varint")
            return value, pos
        shift += 7
    if pos >= len(data):
        raise ValueError("truncated varint")
    raise ValueError("varint exceeds 10 bytes")
```

```python
for n in (0, 1, 127, 128, 300, (1 << 64) - 1):
    raw = encode_uvarint(n)
    recovered, end = decode_uvarint(raw)
    assert recovered == n and end == len(raw)
    print(n, raw.hex())
```

Expected output:

```text
0 00
1 01
127 7f
128 8001
300 ac02
18446744073709551615 ffffffffffffffffff01
```

The decoder returns both the integer and the next offset so multiple fields can share one byte sequence. A caller parsing a stream must also enforce a maximum total message length; a bounded varint alone does not bound the whole message.

### TLV: type-length-value

TLV is a pattern rather than one universal standard: each field has a type, a length, and a value. This example uses a one-byte type and a two-byte big-endian length, followed by the raw value. It limits each value to 4096 bytes and rejects truncated headers and values.

```python
import struct

TLV_HEADER = struct.Struct(">BH")  # uint8 type, uint16 value length
MAX_TLV_VALUE = 4096


def encode_tlv(kind: int, value: bytes) -> bytes:
    if not 0 <= kind <= 255:
        raise ValueError("type out of range")
    if len(value) > MAX_TLV_VALUE:
        raise ValueError("value too long")
    return TLV_HEADER.pack(kind, len(value)) + value


def decode_tlvs(data: bytes):
    offset = 0
    result = []
    while offset < len(data):
        if len(data) - offset < TLV_HEADER.size:
            raise ValueError("truncated TLV header")
        kind, length = TLV_HEADER.unpack_from(data, offset)
        offset += TLV_HEADER.size
        if length > MAX_TLV_VALUE:
            raise ValueError("TLV value exceeds limit")
        end = offset + length
        if end > len(data):
            raise ValueError("truncated TLV value")
        result.append((kind, data[offset:end]))
        offset = end
    return result


wire = encode_tlv(3, b"abc") + encode_tlv(7, b"\x00\xff")
assert decode_tlvs(wire) == [(3, b"abc"), (7, b"\x00\xff")]
print(decode_tlvs(wire))
```

Expected output:

```text
[(3, b'abc'), (7, b'\x00\xff')]
```

Do not treat this teaching TLV layout as a standard protocol. Real TLV schemes vary in type width, length encoding, nesting, canonicalization, duplicate-field handling, and semantic validation.

## 11. Bit masks, shifts, and flags

Binary layouts often pack independent Boolean options into one integer. A bit mask selects a bit; shifting moves a bit position. Define named constants instead of sprinkling unexplained numbers throughout code.

```python
FLAG_COMPRESSED = 1 << 0  # bit 0: 0001
FLAG_ENCRYPTED  = 1 << 1  # bit 1: 0010
FLAG_FINAL      = 1 << 2  # bit 2: 0100
KNOWN_FLAGS = FLAG_COMPRESSED | FLAG_ENCRYPTED | FLAG_FINAL

flags = FLAG_COMPRESSED | FLAG_FINAL
print(bool(flags & FLAG_COMPRESSED))
print(bool(flags & FLAG_ENCRYPTED))
print(flags & ~KNOWN_FLAGS == 0)
print(flags.bit_length(), flags.bit_count())
```

Expected output:

```text
True
False
True
3 2
```

- `flags & MASK` tests whether any selected bits are set.
- `flags | MASK` sets bits; `flags & ~MASK` clears them.
- `value.bit_length()` returns the number of bits needed to represent the absolute value for nonnegative values (for zero it returns 0).
- `value.bit_count()` returns the number of one-bits in the binary representation of the absolute value.

`int.bit_length()` and `int.bit_count()` are built-in integer methods (available in modern Python, including Python 3.12). Reject unknown reserved bits unless the format explicitly says they may be ignored; that makes forward-compatibility policy deliberate.

## 12. CRC32 and integrity boundaries

`zlib.crc32(data)` computes a 32-bit CRC commonly used to detect accidental corruption. In portable file formats, mask with `& 0xFFFFFFFF` when serializing the result as an unsigned 32-bit field. Verify the exact bytes covered by the format specification: a checksum may exclude its own field and may include or exclude length/type fields.

A CRC is not cryptographically secure. It does not authenticate the sender, prevent intentional modification, or prove that data is trustworthy. For authenticity use a properly managed MAC (for example, HMAC) or digital signatures when appropriate; do not invent cryptographic constructions.

## 13. Robust parsing checklist

Before using any field from a binary input:

1. Read the fixed-size prefix completely; detect truncation.
2. Check magic/signature and supported version.
3. Check the format's valid ranges and reserved bits.
4. Validate every length against both the format and an application-level maximum **before** allocating or reading the body.
5. Calculate total sizes using bounded values; reject truncation and unexpected trailing bytes where the format requires exact length.
6. Validate field semantics after decoding: legal enums, dimensions, offsets, text constraints, and cross-field relationships.
7. Check the specified checksum over exactly the specified bytes.
8. Avoid recursion or loops driven by unbounded nested counts; cap nesting depth, record count, and total bytes.
9. Test empty, minimum, maximum, malformed, truncated, extra-trailing-byte, invalid-version, invalid-flags, and checksum-failure cases.
10. Fuzz parser inputs and assert that malformed data is rejected cleanly, without unbounded allocation or unexpected exceptions escaping your intended API.

Do not use `assert` for production input validation: Python may remove assertions when optimization is enabled. Use explicit `if ...: raise ...` checks. In tests, assertions are appropriate.

### A small fuzz-style smoke test

This is not a substitute for a coverage-guided fuzzer such as Atheris or property-based testing with Hypothesis, but it exercises many arbitrary short byte sequences and ensures the public parser rejects or accepts them through its documented result/error path.

```python
import random
import struct

rng = random.Random(2026)
for _ in range(1000):
    candidate = rng.randbytes(rng.randrange(0, 80))
    try:
        decode_log(candidate)
    except (ValueError, struct.error):
        pass
```

This test is deterministic because it uses a seeded PRNG. It does not prove the parser is secure or exhaustive; it is a smoke test for unexpected behavior on random inputs. Import `struct` in the same module for the `struct.error` handler, or simplify the test to catch only `ValueError` if the parser's public contract guarantees all malformed inputs are normalized to that exception.

## 14. Binary writing: validate, checksum, and replace atomically

A safer writing pattern is to create a temporary file in the destination directory, write the complete new content, flush it, optionally `fsync`, and atomically replace the destination with `os.replace`. The temporary file should be on the same filesystem as the destination for the usual atomic-rename guarantee. A crash after replacement may still have durability implications; atomic replacement and durable persistence are related but distinct.

The example below accepts already-encoded bytes, appends a CRC32 footer, and replaces the destination. It does not claim the CRC provides authenticity. Production code may need directory `fsync`, permissions/ownership handling, symlink policy, and platform-specific durability decisions.

```python
import os
import tempfile
import zlib
from pathlib import Path


def atomic_write_with_crc(path: str | Path, payload: bytes) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    checksum = (zlib.crc32(payload) & 0xFFFFFFFF).to_bytes(4, "big")
    content = payload + checksum
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False
        ) as stream:
            temp_name = stream.name
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, destination)
        temp_name = None
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
```

The checksum footer is four bytes, big-endian. A reader should require at least four bytes, split the payload from the footer, recompute CRC32 over the payload, and compare it with the stored value. If a writer or reader handles untrusted or concurrent paths, also consider directory permissions, symlinks, and who can modify the destination directory.

## 15. Alternatives and boundaries

`struct` is for fixed binary layouts. It is not always the best representation for application data or an evolving interchange protocol.

| Tool / format | Appropriate use | Important boundary |
|---|---|---|
| `dataclasses.dataclass` | Named in-memory records and validation logic | Does not define a byte layout by itself |
| `array.array` | Compact homogeneous typed numeric arrays | Type sizes and byte order need care for interchange; not a general schema format |
| `ctypes.Structure` | C-compatible memory layouts and native ABI interoperability | Native alignment/packing and platform ABI matter; not automatically a portable disk format |
| Protobuf | Schema-defined messages, evolution, generated APIs, compact wire encoding | Use the official library and `.proto` schema; do not hand-roll the full wire format |
| Avro | Schema-based data records and data pipelines, including schema evolution | Use the ecosystem's implementation and schema/registry conventions |
| MessagePack | Compact typed serialization across languages | Validate application semantics and size limits after decoding |
| Arrow IPC | Columnar interchange for analytics and data processing | Use Arrow libraries; format is more involved than a few `struct` fields |
| NumPy structured `dtype` | Homogeneous arrays of records with specified field offsets/types | Byte order, alignment, dtype definition, and input length must match the actual file layout |

### NumPy connection (optional dependency)

NumPy's `frombuffer` can interpret an existing buffer as an array without copying the underlying data at creation time, when the dtype and alignment assumptions match. It does not validate a file format, and later operations may allocate copies. Install NumPy separately; it is not part of the Python standard library.

```python
# Optional: requires NumPy (`python -m pip install numpy`).
import numpy as np

record_dtype = np.dtype([
    ("identifier", ">u4"),       # big-endian uint32
    ("temperature", ">i2"),     # big-endian int16
    ("label", "S8"),             # fixed 8-byte field
])
raw = bytes.fromhex("00000011 00eb 54454d5000000000".replace(" ", ""))
records = np.frombuffer(raw, dtype=record_dtype)
print(int(records[0]["identifier"]), int(records[0]["temperature"]))
```

Expected output: `17 235`

The dtype item size is 14 bytes, matching `>Ih8s`. The buffer length must be compatible with the dtype's item size; `frombuffer` generally rejects a buffer whose length is not a multiple of the dtype item size. A `frombuffer` array may share the original storage, so keep the backing object alive and treat mutation/lifetime deliberately. Use a mature parser first to validate headers, lengths, and constraints; then expose the verified payload to NumPy.

**Choose a mature format library instead of inventing a format** when data must interoperate across teams or languages, evolve over years, support schema changes, carry nested values, or handle untrusted messages. A custom layout can be reasonable for a narrow, documented, performance-sensitive format, but its author owns compatibility, validation, test coverage, and maintenance.

## 16. Complexity and memory notes

- `pack` allocates a new `bytes` object proportional to the packed size. `unpack` returns a tuple and Python objects for its fields.
- `pack_into` can avoid creating an intermediate packed `bytes` object when filling an existing writable buffer; the buffer still needs adequate capacity.
- `unpack_from` reads fields at an offset without requiring the entire buffer to be exactly one record, but it still creates Python result objects.
- Iterating with `iter_unpack` is linear in the number of records and avoids a separate list of all records unless you build one. Each returned record is still a tuple.
- Fixed-width records make offset calculations constant-time. Variable-length fields require length parsing and careful bounds checks.
- A whole-file `bytes` read uses memory proportional to file size. Streaming limits peak input buffering, but does not automatically make downstream accumulation bounded.
- CRC32 computation is O(n) in the bytes covered. Atomic writing may temporarily require disk space for both old and new files.

Avoid claims such as “zero-copy everywhere”: `struct.unpack` produces Python objects; `bytes` slicing copies; `memoryview` can expose an existing buffer; and NumPy operations may or may not copy depending on the operation and layout.

## 17. Common mistakes and corrections

| Mistake | Why it fails | Correction |
|---|---|---|
| Omitting the format prefix | Defaults to native `@` layout | Specify `<`, `>`, or `!` for portable formats |
| Treating `H` as signed | `H` is unsigned; `h` is signed | Use the format character matching the spec |
| Assuming `4s` means four characters | It means four bytes | Encode text first and enforce a byte limit |
| Trusting `read(n)` returned `n` bytes | Streams may return short reads | Loop until complete or EOF |
| Trusting a declared length | May trigger huge reads or allocation | Enforce limits before consuming the body |
| Using CRC32 as authentication | CRC is not cryptographic | Use a suitable MAC/signature when authenticity is needed |
| Assuming `iter_unpack` ignores trailing bytes | Input size must be a multiple of record size | Check exact length or handle remainder explicitly |
| Silently stripping all NUL bytes | May delete valid data | Follow the field's exact padding/termination convention |
| Using `assert` to reject hostile files | Assertions can be disabled | Use explicit validation and exceptions |
| Writing a custom format without a version | Future readers cannot distinguish layouts | Specify versioning and unknown-field/flag policy |
| Assuming `numpy.frombuffer` validates the format | It only interprets a buffer using a dtype | Validate the container/header before array creation |

## 18. Guided exercises

### Exercise A — Decode a packet prefix

A packet begins with a big-endian unsigned 16-bit message type and an unsigned 32-bit payload length. Define a `Struct`, print its size, and decode hex bytes `00030000000a`.

### Exercise B — Fixed-width name

Pack `b"AI"` into an 8-byte field and unpack it. Show the raw bytes and the explicitly decoded logical name. Explain why `rstrip(b"\x00")` is only correct if the field uses zero padding.

### Exercise C — Iterate fixed records

Create three records using `Struct(">Hh")` and decode them with `iter_unpack`. Add a test where one byte is appended and confirm the incomplete trailing record is rejected.

### Exercise D — Parser hardening

Extend `decode_log` tests to cover a wrong version, unknown flag bit, record count above the cap, CRC mismatch, and a label with invalid ASCII bytes. State which validation runs first and why.

## 19. Independent exercises

1. Implement a parser for a fixed header `>4sBBI`: 4-byte magic, one-byte version, one-byte flags, and a 4-byte payload length. Require a specified magic/version and cap payloads at 1 MiB. Test truncation at every header boundary.
2. Implement a length-prefixed UTF-8 string field with a 2-byte big-endian byte length. Test empty strings, non-ASCII text, malformed UTF-8, a length beyond the cap, and a truncated payload.
3. Add a bit flag named `FLAG_RETRYABLE` and reject any unknown flag bits.
4. Write property-style tests for unsigned varints at boundaries `0`, `1`, `127`, `128`, `16383`, `16384`, and `2**64 - 1`; test truncation and overflow too.
5. Compare a fixed-width record array with a schema-based format for a hypothetical cross-language event pipeline. Explain the trade-off in schema evolution, tooling, and validation burden.

## 20. Solutions to guided exercises

### Solution A

```python
import struct

PREFIX = struct.Struct(">HI")
print(PREFIX.size)
print(PREFIX.unpack(bytes.fromhex("00030000000a")))
```

Output:

```text
6
(3, 10)
```

`>` is big-endian; `H` is a two-byte unsigned integer and `I` a four-byte unsigned integer.

### Solution B

```python
import struct

FIELD = struct.Struct("<8s")
raw = FIELD.pack(b"AI")
field = FIELD.unpack(raw)[0]
print(raw.hex())
print(field.rstrip(b"\x00").decode("ascii"))
```

Output:

```text
4149000000000000
AI
```

This trimming is valid only because the exercise defines zero-padding and the logical value contains no meaningful trailing NUL bytes.

### Solution C

```python
import struct

RECORD = struct.Struct(">Hh")
data = b"".join(RECORD.pack(i, -i) for i in (1, 2, 3))
assert list(RECORD.iter_unpack(data)) == [(1, -1), (2, -2), (3, -3)]
try:
    list(RECORD.iter_unpack(data + b"\x00"))
except struct.error:
    print("rejected incomplete trailing record")
```

Output:

```text
rejected incomplete trailing record
```

The record size is four bytes; after appending one byte, the total length is not divisible by four.

### Solution D

```python
encoded = encode_log([(17, 235, "TEMP")])
bad_cases = {
    "version": encoded[:4] + bytes([2]) + encoded[5:],
    "flags": encoded[:5] + bytes([0x80]) + encoded[6:],
    "crc": encoded[:-1] + bytes([encoded[-1] ^ 1]),
}
for label, bad in bad_cases.items():
    try:
        decode_log(bad)
    except ValueError:
        print(label, "rejected")
```

Output:

```text
version rejected
flags rejected
crc rejected
```

For a count-over-cap case, construct only the 8-byte header with the count set to `MAX_RECORDS + 1` and append a four-byte placeholder footer; the parser rejects the count before expecting a record body. For an invalid-ASCII label, build a correctly sized record with `b"\xff"` in the label and recompute the footer CRC so the test reaches label validation rather than failing early on the checksum. Keep these malformed-input tests independent so each verifies the intended validation branch.

## 21. Roadmap self-checks — answers with reasoning

### 1. What does `"<IHf"` mean and what is its size?

`<` selects little-endian byte order, standard field sizes, and no alignment padding. `I` is an unsigned 4-byte integer, `H` is an unsigned 2-byte integer, and `f` is a 4-byte IEEE 754 binary32 float. Therefore, `struct.calcsize("<IHf")` is `4 + 2 + 4 = 10` bytes on all supported platforms.

### 2. Why can `"@IHf"` differ in size from `"<IHf"`?

`@` uses native byte order, native C sizes, and native alignment. Padding may be inserted between fields to satisfy the platform's C ABI, and native field sizes can vary. `<` instead uses the format's standard field sizes and inserts no alignment padding. Use `calcsize` to inspect native layouts and avoid `@` in portable files.

### 3. How do you write a tiny custom log parser and test round-trip plus truncated input?

Specify a versioned header, field widths, byte order, record count, maximum count, and checksum coverage. Encode using `Struct.pack`; decode only after checking minimum size, magic, version, flags, count limit, exact expected total length, and checksum. A round-trip test asserts that decoding an encoded record returns the original logical values. A truncated-input test removes at least one byte and asserts rejection. The `encode_log`, `decode_log`, and malformed-input tests in Section 9 demonstrate this pattern; production parsers should add fuzz/property tests and documented compatibility rules.

## 22. Glossary

- **ABI (Application Binary Interface):** rules for native data layout and calling conventions between compiled components.
- **Alignment:** constraints on where a field can begin in memory; native layouts may add padding to satisfy them.
- **Big-endian / little-endian:** order in which a multi-byte value's most-significant / least-significant byte is stored first.
- **CRC32:** 32-bit cyclic redundancy check used to detect accidental corruption, not authenticate data.
- **Fixed-width field:** field with a specified byte count regardless of the logical value's length.
- **Magic/signature:** fixed bytes identifying a file or message type.
- **TLV:** type-length-value encoding pattern.
- **Varint / LEB128:** variable-length integer encoding using continuation bits and groups of data bits.
- **Version field:** value used to distinguish layout revisions and compatibility rules.
- **Wire format:** documented byte representation exchanged or stored by systems.

## 23. Completion checklist

- [ ] I can explain why a binary format specifies width, signedness, byte order, and padding.
- [ ] I can interpret and calculate the size of `b B h H i I q Q f d ? s x` formats.
- [ ] I can explain `<`, `>`, `!`, `=`, and `@` and choose a portable prefix.
- [ ] I can use `Struct`, `pack_into`, `unpack_from`, and `iter_unpack` with correct offsets and lengths.
- [ ] I understand fixed-width byte strings, padding, truncation, and explicit decoding.
- [ ] I can handle short reads, validate real file headers, and verify a specified CRC32.
- [ ] I never trust a length field before applying a configured limit.
- [ ] I can implement and test a tiny versioned record format, including truncated and malformed input.
- [ ] I can explain bit masks, shifts, flags, `bit_length`, and `bit_count`.
- [ ] I know the boundary between `struct` and mature schema-based formats.
- [ ] I can describe the trade-offs of streaming, buffering, and NumPy `frombuffer`.
- [ ] I can explain why CRC32 detects accidental corruption but does not establish authenticity.

**Lesson complete when:** you can write a documented fixed-layout parser, prove its expected byte sizes and offsets, reject malformed inputs predictably, and explain when a schema-based format is the better engineering choice.

---

**Version note:** This lesson targets Python 3.12+. The core `struct`, `zlib.crc32`, `int.bit_length`, `int.bit_count`, `memoryview`, and `tempfile` examples use established APIs available in Python 3.12. NumPy is optional and must be installed separately. No behavior here depends on Python 3.13 or 3.14-specific features.
