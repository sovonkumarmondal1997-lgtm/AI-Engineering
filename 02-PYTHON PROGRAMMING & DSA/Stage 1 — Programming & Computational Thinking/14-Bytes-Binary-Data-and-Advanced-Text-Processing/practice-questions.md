# Practice Questions — Bytes, Binary Data and Advanced Text Processing

**Stage:** 1 — Programming & Computational Thinking · **Module:** 14 — Bytes, Binary Data and Advanced Text Processing  
**Target:** Python 3.12+ · **Assessment:** 35 questions · **Maximum:** 100 points

**Version-sensitive notes:** Q21 distinguishes Python 3.14 t-strings from Python 3.12; Q24 requires a PyTorch-version-aware statement; Q28/Q33 distinguish Python 3.14 `compression.zstd` from third-party `zstandard` on earlier versions.

This assessment follows the authoritative module roadmap and its Phase A/B/C ordering. Unless specified otherwise, use Python 3.12+ and the standard library. All input data needed to solve a question is included. Answers are separated from questions below. Do not execute untrusted pickle data or run dangerous ReDoS timing tests.

Six bug-identification items cover mojibake, unnormalized Unicode equality, catastrophic backtracking, untrusted pickle loading, unlimited decompression, and wrong byte order.

# Phase A — Bytes and Binary Layouts

## Q1. Byte length and indexing — 2 points
**Difficulty:** Foundational · **Lesson 01 — `bytes`, `bytearray`, `memoryview`**

Predict the output and explain it:
```python
text = "café"
data = text.encode("utf-8")
print(len(text), len(data))
print(data[3], data[:3])
print(bytes.fromhex("41 00 ff").hex())
```

## Q2. What is the bug? — mojibake — 2 points
**Difficulty:** Foundational · **Lesson 01 — encodings**
```python
raw = "café".encode("utf-8")
print(raw.decode("latin-1"))
```
Identify the bug, give the smallest correct fix, and explain why a font change is not the fix.

## Q3. Reusable-buffer chunk reader — 2 points
**Difficulty:** Intermediate · **Lesson 01 — `readinto` and `memoryview`**
Write `read_chunks(file_obj, size=4)` that allocates one `bytearray`, uses `readinto`, and yields views of only the bytes read. For `io.BytesIO(b"abcdefg")`, state the chunks yielded. Explain the lifetime rule for consumers when the buffer is reused.

## Q4. Buffer lifetime — 2 points
**Difficulty:** Foundational · **Lesson 01 — buffer protocol**
Predict the exception name and final output:
```python
buf = bytearray(b"abcd")
view = memoryview(buf)
view[1] = ord("Z")
try:
    buf.extend(b"!")
except Exception as exc:
    print(type(exc).__name__)
view.release()
buf.extend(b"!")
print(buf)
```
Explain why the resize initially fails.

## Q5. Parse a fixed header — 2 points
**Difficulty:** Foundational · **Lesson 02 — `struct`**
Header layout: `magic` (4 bytes), `version` (unsigned byte), `flags` (unsigned byte), `payload_length` (unsigned 16-bit big-endian). For `b"DATA\x02\x01\x00\x05"`, provide the `struct.Struct` format and unpacked tuple. How should a shorter-than-header file be handled?

## Q6. Byte order and alignment — 2 points
**Difficulty:** Intermediate · **Lesson 02 — portable binary formats**
Explain `<`, `>`, `!`, `=`, and `@` in `struct` formats. Calculate `struct.calcsize("<IHf")` and explain why `struct.calcsize("@IHf")` can differ across platforms. Why should portable file formats normally avoid native-aligned `@` layouts?

## Q7. Defensive length-prefixed parser — 2 points
**Difficulty:** Intermediate · **Lesson 02 — malformed input**
Records contain a 2-byte big-endian length followed by that many bytes. For example, `b"\x00\x03cat"` encodes `b"cat"`. Write a parser enforcing a 1,024-byte maximum. Explain handling of a truncated prefix, an oversized length, and a truncated payload. Give one round-trip test and one truncation test.

## Q8. What is the bug? — wrong byte order — 2 points
**Difficulty:** Foundational · **Lesson 02 — endianness**
A protocol specifies a big-endian unsigned 32-bit count:
```python
import struct
count = struct.unpack("<I", b"\x00\x00\x01\x00")[0]
```
Identify the bug, calculate the intended count, and fix the format string.

## Q9. Integer-to-bytes boundaries — 2 points
**Difficulty:** Intermediate · **Lessons 01–02 — integer conversion**
For `n = 258`, show `n.to_bytes(2, "big")` and `n.to_bytes(2, "little")`, then decode each using the matching order. What exception type is expected when encoding 258 into one unsigned byte?

## Q10. Copy or view? — 2 points
**Difficulty:** Intermediate · **Lesson 01 — zero-copy parsing**
Given `raw = b"HEADER:payload"`, compare `raw[7:]` and `memoryview(raw)[7:]`. Which makes a new bytes payload copy? Give one benefit and one limitation of `memoryview`.

# Phase B — Text in Depth

## Q11. Unicode normalization — 3 points
**Difficulty:** Foundational · **Lesson 03 — NFC/NFD**
For `composed = "é"` and `decomposed = "e\u0301"`, predict equality and lengths. Show how to compare under NFC. Why is normalization a policy choice rather than an instruction to rewrite every string indiscriminately?

## Q12. NFC, NFKC, and slug keys — 3 points
**Difficulty:** Intermediate · **Lesson 03 — normalization and text cleaning**
A catalog needs a caseless lookup key while retaining the original display name. Explain NFC versus NFKC and sketch a `slugify(text)` approach covering case, whitespace, accents, symbols, emoji, and CJK. Give two tests and explain why the display text should be preserved.

## Q13. What is the bug? — unnormalized Unicode equality — 3 points
**Difficulty:** Foundational · **Lesson 03 — equality**
```python
def same_label(a, b):
    return a == b
print(same_label("é", "e\u0301"))
```
The specification says canonically equivalent labels must compare equal. Identify and fix the bug. Why might blindly using NFKC be inappropriate for some identifiers?

## Q14. Case folding — 3 points
**Difficulty:** Intermediate · **Lesson 03 — `casefold`**
Predict:
```python
print("Straße".casefold() == "STRASSE".casefold())
print("Straße".lower() == "STRASSE".lower())
```
Which operation is designed for caseless matching, and what language/collation limitations remain?

## Q15. Code points versus user-perceived characters — 3 points
**Difficulty:** Intermediate · **Lesson 03 — grapheme clusters**
A UI truncates with `label[:5]`. Explain why this may split a displayed character or fail to fit five terminal columns. State a better requirement and name a relevant tool/library for grapheme-cluster handling.

## Q16. Named-group timestamp regex — 3 points
**Difficulty:** Intermediate · **Lesson 04 — regex groups and validation**
Write a compiled standard-library `re.VERBOSE` pattern for exactly `YYYY-MM-DDTHH:MM:SS` with an optional final `Z`. It must reject trailing text. Give ten positive/negative test cases. Explain why shape validation does not establish calendar validity.

## Q17. `match`, `search`, `fullmatch` — 3 points
**Difficulty:** Foundational · **Lesson 04 — regex API**
For `re.compile(r"\d+")` and `text = "id=42x"`, which of `match`, `search`, and `fullmatch` succeed? What does `search` capture? Which is usually appropriate to validate a complete field?

## Q18. What is the bug? — catastrophic backtracking — 3 points
**Difficulty:** Advanced · **Lesson 04 — ReDoS defense**
A validator applies `re.compile(r"(a+)+$")` to attacker-controlled input. A conceptual near-match is a long run of `a` characters followed by `!`; explain the risk without running or timing that input. Give a safer pattern for “one or more lowercase `a` characters and nothing else” and two additional mitigations.

## Q19. Parse a log line — 3 points
**Difficulty:** Intermediate · **Lesson 04 — named groups**
Parse `level=INFO user=alice action=login`, where level contains uppercase letters and values contain no spaces. Write a readable named-group regex and use `fullmatch`. How should malformed lines be handled? Why not parse nested JSON with a single giant regex?

## Q20. “Did you mean?” — 3 points
**Difficulty:** Intermediate · **Lesson 05 — `difflib`**
Write a function suggesting up to three commands from `{"deploy", "describe", "delete", "doctor", "diff"}` for an unknown command using `difflib.get_close_matches`. Choose a cutoff and explain how to calibrate it. Why is `difflib` not a brute-force solution for millions of names against millions of queries?

## Q21. Unified diff, formatting, and template safety — 3 points
**Difficulty:** Intermediate · **Lesson 05 — `difflib`, `textwrap`**
Given old lines `['host=old', 'port=5432']` and new lines `['host=new', 'port=5432']`, write code producing a unified diff labelled `before` and `after`, then wrap a summary to width 32. Also format `costs = [("ingest", 12500), ("storage", 8400)]` as a right-aligned currency table with thousands separators and a total row. Explain how `unified_diff` differs from `ndiff`, and why a readable diff is not a substitute for structured validation. Briefly explain when `string.Template` may be useful, why it is not a SQL/shell/HTML security boundary, and label Python 3.14 t-strings as version-specific rather than assuming they exist in Python 3.12.

# Phase C — Serialization and Compression

## Q22. Pickle threat model — 3 points
**Difficulty:** Intermediate · **Lesson 06 — pickle security**
Explain how pickle loading can execute code and how `__reduce__` relates to reconstruction. Why is “it came from our cache” not sufficient proof of trust? Compare an allow-listing `Unpickler.find_class` with `pickletools.dis`: what does each do, and why is neither a universal guarantee? Mention one protocol/version or picklability limitation relevant to compatibility.

## Q23. What is the bug? — unpickling untrusted bytes — 3 points
**Difficulty:** Advanced · **Lesson 06 — unsafe deserialization**
```python
import pickle
obj = pickle.loads(request_body)
```
The body comes from an external client. Identify the bug and propose a safer API payload design. Explain why HMAC signing does not help against a sender who can generate valid signatures, and why scanners are not universal guarantees.

## Q24. Select a serialization format — 3 points
**Difficulty:** Intermediate · **Lesson 06 — alternatives**
Choose and justify formats for (a) an ordinary API request, (b) a cache shared by services, and (c) a trained scikit-learn model. Consider schema validation, compatibility, JSON/Parquet/Arrow where suitable, and model-specific formats. Briefly explain what PyTorch’s `torch.load(weights_only=True)` aims to restrict and why version compatibility and artifact provenance still matter. **Version-sensitive:** if you discuss `torch.load` defaults, name the PyTorch version rather than assuming every release has the same default. Do not assume one format is universally suitable for every model.

## Q25. `marshal`, `pickle`, and `shelve` — 3 points
**Difficulty:** Intermediate · **Lesson 06 — persistence risks**
Compare intended use, version/portability expectations, and trust assumptions for `marshal`, `pickle`, and `shelve`. Why can reading a shelve entry carry pickle risk, and why is shelve not a transactional database replacement?

## Q26. Base64 and padding — 3 points
**Difficulty:** Foundational · **Lesson 07 — encoding**
Encode `b"cat"` in Base64 and show its ASCII text form. Explain `=` padding, roughly 33% overhead, URL-safe Base64, why it is not encryption, and why `b64encode` initially returns bytes. Briefly compare Base16/hex, Base32, and Ascii85/Base85 with Base64 for alphabet safety and expansion; mention why a protocol-specific padding rule must be followed.

## Q27. Codec choice and integrity — 3 points
**Difficulty:** Intermediate · **Lesson 07 — compression and checksums**
Choose among gzip, bz2, and lzma for (a) broad interchange compatibility, (b) prioritizing compactness over speed, and (c) simple standard-library gzip streaming. Explain why rankings are workload-dependent. Distinguish CRC32, a cryptographic hash, and message authentication.

## Q28. Streaming JSONL pipeline — 3 points
**Difficulty:** Advanced · **Lesson 07 — streaming**
Design a pipeline reading gzip-compressed JSON Lines, filtering records where `status == "failed"`, and writing matches to a new gzip file. Cover line-by-line processing, malformed lines, bounded memory, closing output, and backpressure. Explain what changes if the output must be zstd instead: label the Python 3.14 standard-library option versus the third-party dependency on earlier Python versions, and retain explicit input/output limits.

## Q29. What is the bug? — unlimited decompression — 3 points
**Difficulty:** Advanced · **Lesson 07 — decompression bombs**
```python
import zlib
plain = zlib.decompress(untrusted_compressed_bytes)
```
Identify the resource risk. Why is limiting compressed input length insufficient? Outline a safe `decompressobj().decompress(..., max_length=...)` approach with absolute output and incomplete-stream policies. Do not construct a bomb payload.

## Q30. Bounded decompression algorithm — 3 points
**Difficulty:** Advanced · **Lesson 07 — `decompressobj`**
Write a function or precise pseudocode that decompresses one zlib-wrapped stream with a 1 MiB output cap. Handle `unconsumed_tail`, avoid unbounded `flush()`, and reject input that has not reached `eof`. Explain how to add an expansion-ratio policy and name one reason a production implementation needs further review.

## Q31. Corrupt or truncated compression stream — 4 points
**Difficulty:** Advanced · **Lesson 07 — error handling**
A service receives gzip bodies that may be corrupt or truncated. Explain how to verify completion and handle `gzip.BadGzipFile`, `EOFError`, and `zlib.error`. Why does receiving some output not prove success? Name useful size, ratio, and failure metrics.

## Q32. Compression benchmark plan — 4 points
**Difficulty:** Advanced · **Lesson 07 — performance measurement**
Design a fair benchmark for gzip and one other codec over text, JSON, CSV, and already-compressed/incompressible input. Define ratio and throughput, describe repetitions and cold/warm cache controls, and list environment details. Label third-party dependencies and avoid universal performance claims.

## Q33. Compression side channels and splitting — 4 points
**Difficulty:** Advanced · **Lessons 06–07 — production security**
A service compresses attacker-influenced text and a secret token into the same response. Explain when CRIME/BREACH-style side channels may leak information and propose layered mitigations. Compare gzip with bgzip or independently framed/block formats for parallel processing, and explain that HTTP `Content-Encoding: gzip` describes compressed representation bytes that the client must decode. Mention gzip multi-member behavior. **Version-specific: Python 3.14** — state the standard-library `compression.zstd` availability and distinguish third-party packages.

## Q34. Safe `mmap` search — 4 points
**Difficulty:** Advanced · **Lesson 08 — large files**
Write a binary/log search function using `mmap` and `find` or a bytes regex. Handle missing and empty files, close the map reliably, and avoid reading the entire file into Python bytes. Explain `ACCESS_READ`, `ACCESS_WRITE`, and `ACCESS_COPY`, and why `flush()` is not by itself a universal durability/crash-consistency guarantee. Mention one NumPy-backed option (`numpy.memmap`, an external dependency) or supported random-read alternative such as `os.pread`, and explain why mmap still incurs page faults/physical I/O. Explain the risk of concurrent external truncation and one case where buffered I/O is preferable. Briefly design a fair comparison against buffered line reading and `readinto`, including cold/warm cache conditions and identical search work.

## Q35. Integrated binary-log design — 4 points
**Difficulty:** Advanced · **Lessons 01, 02, 03, 06, 07, 08 — integrated**
Design a versioned append-only binary log with a file header (magic and version), records containing timestamp, severity, a length-prefixed UTF-8 message and CRC32, and a footer record count. Explain explicit `struct` byte order, length caps, text-normalization policy, append/fsync trade-offs, partial-tail recovery, bounded compressed export, and safe `mmap` scanning. State what CRC32 does and does not protect against.

## Phase A answers

### Answer 1 (Q1)

`len(text)` is `4` code points and `len(data)` is `5` UTF-8 bytes. `data[3]` is `195` (the first byte of the two-byte UTF-8 encoding for `é`), `data[:3]` is `b'caf'`, and the final line prints `4100ff`. Byte indexing returns an integer from 0 to 255.

### Answer 2 (Q2) — Bug analysis

The output is mojibake (`cafÃ©`) because UTF-8 bytes were decoded with Latin-1. Use `raw.decode("utf-8")` when the bytes are known to be UTF-8. A font affects rendering; it cannot repair incorrectly decoded characters.

### Answer 3 (Q3)

```python
def read_chunks(file_obj, size=4):
    if size <= 0:
        raise ValueError("size must be positive")
    buffer = bytearray(size)
    view = memoryview(buffer)
    try:
        while True:
            count = file_obj.readinto(buffer)
            if not count:
                break
            yield view[:count]
    finally:
        view.release()
```

For `b"abcdefg"`, chunks observed immediately as bytes are `b"abcd"`, `b"efg"`. Each yielded view aliases the same reusable buffer and can change after the next iteration; consumers that need to retain a chunk should copy it (for example, `bytes(chunk)`) before requesting the next one. Do not retain views as immutable snapshots.

### Answer 4 (Q4)

The first print is `BufferError`. An exported memoryview prevents resizing the underlying `bytearray`. After `view.release()`, extension succeeds and the final output is `bytearray(b'aZcd!')`.

### Answer 5 (Q5)

```python
import struct
HEADER = struct.Struct(">4sBBH")
magic, version, flags, payload_length = HEADER.unpack(b"DATA\x02\x01\x00\x05")
```

The tuple is `(b'DATA', 2, 1, 5)`. Before unpacking, require at least `HEADER.size` bytes; a truncated header should raise or be reported as a malformed/incomplete record, not be padded with invented bytes.

### Answer 6 (Q6)

`<` is little-endian with standard sizes/no alignment; `>` is big-endian with standard sizes/no alignment; `!` is network byte order (big-endian); `=` uses native byte order but standard sizes/no alignment; `@` uses native byte order, native sizes, and native alignment. `struct.calcsize("<IHf")` is 10 bytes (4 + 2 + 4); `@IHf` may differ because native alignment can insert padding. Portable on-disk formats should specify byte order and field sizes explicitly.

### Answer 7 (Q7)

```python
class MalformedRecord(ValueError):
    pass

def parse_record(data: bytes, max_size: int = 1024) -> bytes:
    if len(data) < 2:
        raise MalformedRecord("truncated length prefix")
    size = int.from_bytes(data[:2], "big")
    if size > max_size:
        raise MalformedRecord("record exceeds configured maximum")
    if len(data) != 2 + size:
        raise MalformedRecord("truncated payload or trailing bytes")
    return data[2:]

encoded = len(b"cat").to_bytes(2, "big") + b"cat"
assert parse_record(encoded) == b"cat"
try:
    parse_record(encoded[:-1])
except MalformedRecord:
    pass
else:
    raise AssertionError("truncation was not rejected")
```

For a stream parser, read exactly the two-byte prefix and then exactly the announced payload; a short read is an error. Reject oversized lengths before allocating or reading the payload. The byte-string parser above also rejects trailing bytes because its contract is exactly one record.

### Answer 8 (Q8) — Bug analysis

The intended count is `256`, because `00 00 01 00` is 256 in big-endian order. Use `struct.unpack(">I", b"\x00\x00\x01\x00")[0]`. The existing `<I` reads the same bytes as little-endian and yields 65,536.

### Answer 9 (Q9)

Big-endian bytes: `b"\x01\x02"`; little-endian bytes: `b"\x02\x01"`. Decoding with the corresponding order returns `258` in both cases. Encoding 258 into one unsigned byte raises `OverflowError`.

### Answer 10 (Q10)

`raw[7:]` creates a new `bytes` object; `memoryview(raw)[7:]` creates a view without copying the payload. Views can reduce copies for large buffers, but they retain access to the exporter and have lifetime/release constraints; they are not a universal speed win for small data.

## Phase B answers

### Answer 11 (Q11)

`composed == decomposed` is `False`; lengths are `1` and `2` code points. Compare with `unicodedata.normalize("NFC", composed) == unicodedata.normalize("NFC", decomposed)`, which is `True`. Normalize according to the field's documented comparison policy; preserve original input where display, legal identity, or byte-for-byte fidelity matters.

### Answer 12 (Q12)

NFC makes canonically equivalent sequences comparable while generally preserving compatibility distinctions. NFKC additionally folds compatibility characters and is useful for some search/identifier policies, but can erase distinctions that a domain needs. One explicit slug policy is NFKD + case-folding, remove combining marks, convert whitespace to a single hyphen, retain alphanumeric characters plus non-ASCII symbols (so CJK and emoji survive), and strip edge hyphens. Under that policy, tests can assert `slugify("Café Menu") == "cafe-menu"` and `slugify("東京 🍵") == "東京-🍵"`. Other policies are valid, but must be specified and tested. Keep the original label separately.

### Answer 13 (Q13) — Bug analysis

The direct comparison returns `False`, although the stated specification defines these forms as equivalent. Correct it with `normalize("NFC", a) == normalize("NFC", b)` (and apply a specified case-folding policy if needed). NFKC is more aggressive and may merge compatibility characters that the identifier scheme needs to distinguish.

### Answer 14 (Q14)

Output is `True` then `False`. `casefold()` is intended for caseless matching and maps `ß` to `ss`; `lower()` does not. Locale-aware collation, accent-insensitive comparison, and language-specific sorting require separate policy/library support.

### Answer 15 (Q15)

Python `str` indexing addresses code points, not grapheme clusters (a base plus combining marks or joined emoji sequence) and not terminal columns. Specify whether the UI needs grapheme-safe truncation, a maximum display width, or both. The third-party `regex` package supports `\X`; `wcwidth` helps estimate terminal display columns. Test the exact UI requirements.

### Answer 16 (Q16)

Example:
```python
import re
STAMP = re.compile(r"""
    (?P<year>\d{4}) - (?P<month>\d{2}) - (?P<day>\d{2}) T
    (?P<hour>\d{2}) : (?P<minute>\d{2}) : (?P<second>\d{2})
    (?P<z>Z)?
""", re.VERBOSE)

cases = [
    ("2024-02-29T23:59:59Z", True),
    ("2026-10-17T04:15:00", True),
    ("2026-10-17T04:15:00Z", True),
    ("2000-01-01T00:00:00", True),
    ("1999-12-31T23:59:59Z", True),
    ("x2026-10-17T04:15:00Z", False),
    ("2026-10-17T04:15:00Z trailing", False),
    ("2026-1-17T04:15:00", False),
    ("2026-10-17T04:15Z", False),
    ("2026-10-17T04:15:00+00:00", False),
]
for value, expected in cases:
    assert bool(STAMP.fullmatch(value)) is expected, value
assert STAMP.fullmatch("2026-19-99T29:88:77")  # shape matches, values are invalid
```
Use `datetime` parsing or explicit range checks after shape validation. The pattern alone verifies formatting, not calendar/time validity.

### Answer 17 (Q17)

`match` fails because the string does not begin with digits. `search` succeeds and matches `"42"`. `fullmatch` fails because the entire string is not digits. Use `fullmatch` when the complete field must conform to the pattern.

### Answer 18 (Q18) — Bug analysis

Nested unbounded quantifiers can cause catastrophic backtracking on near-matching attacker-controlled strings, such as a long run of `a` characters followed by `!`; do not run a timing test against the risky pattern. For the stated requirement, use `re.fullmatch(r"a+", value)` (still enforce a reasonable input-length limit). Additional controls include simpler regexes, strict input length caps, time/resource isolation where appropriate, or a linear-time engine such as RE2 via a third-party package.

### Answer 19 (Q19)

```python
import re
LINE = re.compile(
    r"level=(?P<level>[A-Z]+) "
    r"user=(?P<user>\S+) action=(?P<action>\S+)"
)
m = LINE.fullmatch("level=INFO user=alice action=login")
assert m and m.groupdict() == {
    "level": "INFO", "user": "alice", "action": "login"
}
```
Reject or quarantine malformed lines with a counted, observable parse error; do not silently reinterpret them. JSON has escaping and nested structure, so use `json.loads` and schema validation rather than a giant regex.

### Answer 20 (Q20)

```python
import difflib
COMMANDS = ["deploy", "describe", "delete", "doctor", "diff"]
def suggestions(word):
    return difflib.get_close_matches(word, COMMANDS, n=3, cutoff=0.6)
```
The cutoff is a product choice; calibrate it against representative misspellings and unrelated inputs to balance useful suggestions against false positives. `difflib`'s matching can be expensive at large scale; use blocking/indexing and a purpose-built tool such as third-party `rapidfuzz` if profiling and requirements justify it.

### Answer 21 (Q21)

```python
import difflib
import textwrap

old = ["host=old", "port=5432"]
new = ["host=new", "port=5432"]
diff = "\n".join(difflib.unified_diff(
    old, new, fromfile="before", tofile="after", lineterm=""
))
print(diff)
print(textwrap.fill("Host changed; port is unchanged.", width=32))

costs = [("ingest", 12_500), ("storage", 8_400)]
for name, amount in costs:
    print(f"{name:<12} ${amount:>10,}")
print(f"{'TOTAL':<12} ${sum(v for _, v in costs):>10,}")
```
Expected diff:
```text
--- before
+++ after
@@ -1,2 +1,2 @@
-host=old
+host=new
 port=5432
Host changed; port is unchanged.
ingest       $    12,500
storage      $     8,400
TOTAL        $    20,900
```
`unified_diff` gives a compact patch-style view with context; `ndiff` marks line-level additions/deletions and may add `?` hint lines to show intraline differences. `string.Template` is useful for simple `$name` substitutions when template text should have a limited grammar, but it does not escape values for SQL, shell, or HTML: use parameterized SQL, argument arrays for subprocesses, and context-aware HTML escaping/autoescaping. Python 3.14 t-strings are a separate version-specific structured-interpolation feature; do not assume they exist in Python 3.12. The diff is human-readable, but machine validation should compare parsed fields against constraints. Similarity thresholds need calibration because data distributions and desired false-positive rates differ.

## Phase C answers

### Answer 22 (Q22)

Pickle opcodes can request global callables and reconstruction behavior; a class's `__reduce__`/`__reduce_ex__` can define how it is rebuilt. Loading a malicious pickle can execute code. A cache may be writable by another user/process or poisoned through a compromised producer. Controls include replacing pickle with schema-validated formats, restricting access and provenance, signatures/HMAC for authenticated origin, restricted unpicklers, scanning, and sandboxing. `Unpickler.find_class` can block selected global lookups but is not a universal safe-pickle proof; `pickletools.dis` inspects opcodes without executing the pickle but does not prove that loading is safe. Protocol 5 / PEP 574 supports out-of-band buffers for large data transfer, not a trust guarantee. Signatures only establish a trusted signer and integrity, scanners can miss behavior, and sandboxes reduce impact rather than prove safety.

### Answer 23 (Q23) — Bug analysis

Never `pickle.loads` a client-controlled request body. Use a documented schema in JSON or another suitable data format, validate types/lengths/ranges, and reject unknown or malformed fields. HMAC authenticates a message only for parties holding the key; if the sender is allowed to sign arbitrary payloads, signing does not make the payload safe. Static analysis is useful defense-in-depth, not a universal proof of safety.

### Answer 24 (Q24)

(a) JSON with schema/type/range validation is a reasonable API default. (b) A shared service cache should use a versioned schema format such as JSON/MessagePack/Protobuf or a data-oriented format where suitable; ensure cache permissions and compatibility. Parquet/Arrow are more natural for tabular or columnar data interchange than for a small ordinary JSON-style API request. (c) For scikit-learn, the right choice depends on model/estimator support and trust requirements: consider a documented export/interchange route such as ONNX when supported, or a trusted, integrity-checked artifact with a clear environment/version policy. PyTorch `torch.load(weights_only=True)` aims to restrict loading to a safer subset for weights, but it is not a universal guarantee and behavior/support depends on version and artifact. `safetensors` suits supported tensor weights, not arbitrary scikit-learn estimator objects. Never load untrusted pickle merely because it is a model file.

### Answer 25 (Q25)

`marshal` is an implementation-oriented format used for Python internals such as code objects/`.pyc`; its format is version-dependent and not a general interchange format. `pickle` serializes Python object graphs but is Python-specific and unsafe to load from untrusted sources. `shelve` provides key/value access backed by `dbm` and pickle serialization; reading entries can invoke pickle reconstruction. Lambdas, open files, locks, and generators are common examples of objects that are not generally picklable. Protocol 5 / PEP 574 allows out-of-band buffers for large data, but does not make pickle portable or safe for untrusted data. Backend semantics, concurrent access, and `writeback=True` memory caching make shelve unsuitable as a transactional multi-writer database.

### Answer 26 (Q26)

`base64.b64encode(b"cat")` returns `b'Y2F0'`; decoding those bytes as ASCII gives `'Y2F0'`. Base64 encodes each 3-byte group into 4 characters, so large payloads grow by about one third, with `=` padding for incomplete final groups. URL-safe Base64 substitutes `-` and `_` for `+` and `/`; padding policy must match the receiving protocol. It is reversible encoding, not secrecy. The function returns bytes because its input/output contract is byte-oriented; decode ASCII only when a text protocol needs a `str`. Base16/hex uses two characters per byte and is easy to inspect but expands more; Base32 uses a more restricted alphabet with greater overhead than Base64; Ascii85/Base85 is denser than Base64 but has alphabet/escaping considerations. Use the alphabet and padding rules required by the receiving protocol.

### Answer 27 (Q27)

Gzip is the common default for broad compatibility and streaming. `bz2` or `lzma` may yield smaller output on some data at a cost in CPU/latency; measure on the actual corpus. `zlib.crc32` detects accidental corruption but is not collision-resistant authentication. A cryptographic hash such as SHA-256 gives a stronger content fingerprint but alone does not authenticate the sender. A MAC or digital signature authenticates origin/integrity under its key model.

### Answer 28 (Q28)

Open source with `gzip.open(..., "rt", encoding="utf-8")` and destination with `gzip.open(..., "wt", encoding="utf-8")`; iterate source lines, parse each with `json.loads`, validate the expected shape, and write only failed records. Catch `JSONDecodeError` according to a documented reject/quarantine policy, with counters. Avoid accumulating all rows. Synchronous read-filter-write naturally provides backpressure; if queues are introduced, bound their size. Close both contexts to finish gzip trailers and surface errors. For zstd output, Python 3.14 provides `compression.zstd`; earlier versions generally need the third-party `zstandard` package. Pin/test the chosen codec and preserve absolute decompressed-output and record-size limits.

### Answer 29 (Q29) — Bug analysis

`zlib.decompress` may allocate arbitrarily large output from small input. Input size alone does not bound expansion. Use a `decompressobj`, pass a positive `max_length`, process `unconsumed_tail` in bounded iterations, stop/reject as soon as an absolute cap is exceeded, and require `eof` before treating output as complete. Reject unexpected trailing data when the protocol requires exactly one stream. Apply a ratio limit as an additional policy, not a replacement for an absolute cap.

### Answer 30 (Q30)

One defensible single-buffer sketch is:
```python
import zlib

def bounded_zlib(data: bytes, limit: int = 1 << 20, ratio: int = 100) -> bytes:
    if not data or limit < 0 or ratio < 1:
        raise ValueError("invalid input or limits")
    dec = zlib.decompressobj()
    out = bytearray()
    pending = data
    while pending:
        room = limit - len(out)
        piece = dec.decompress(pending, room + 1)  # one extra byte detects overflow
        if len(out) + len(piece) > limit:
            raise ValueError("decompressed output exceeds limit")
        out.extend(piece)
        pending = dec.unconsumed_tail
        if not pending:
            break
    if not dec.eof:
        raise ValueError("truncated/incomplete zlib stream")
    if dec.unused_data:
        raise ValueError("trailing data after single stream")
    if len(out) > max(1, len(data)) * ratio:
        raise ValueError("expansion ratio exceeds policy")
    return bytes(out)
```
This is an instructional sketch, not a drop-in hardened parser: production code should test supported versions and edge cases, define multi-stream policy, handle exception taxonomy, and consider CPU/time limits as well as output size. It deliberately does not call `flush()`, which could emit output outside the explicit cap. The ratio denominator is the compressed stream size; an empty input is rejected rather than treated as a valid empty stream.

### Answer 31 (Q31)

Consume the stream to completion and verify its end marker/`eof`; a gzip reader can yield data before a later CRC/trailer/truncation error appears. Catch `gzip.BadGzipFile`, `EOFError`, and `zlib.error` as relevant to the API used, classify the failure, and do not publish partial output as a successful artifact. Useful metrics include compressed bytes, decompressed bytes, expansion ratio, elapsed time, codec, completion status, and categorized failure reason. Do not log sensitive payload contents.

### Answer 32 (Q32)

Use representative fixed corpora for plain text, JSON, CSV, and already-compressed/random-like bytes. Record input/output byte counts; define ratio as `compressed_bytes / input_bytes` (lower is smaller) and throughput as bytes processed per second. Repeat runs, separate setup from timed work, report medians/spread, use the same level/settings where comparable, and test cold/warm caches separately if file I/O is involved. Record Python/codec versions, CPU, OS, storage, parameters, corpus size/composition, and cache state. A third-party option such as `zstandard` or `lz4` must be labeled and version-pinned. Do not extrapolate beyond tested conditions.

### Answer 33 (Q33)

A compression side channel can arise when attacker-controlled text and a secret share a compression context, the attacker can influence inputs, and response lengths or related observations are visible across repeated queries. Mitigations can include separating secrets from attacker-controlled content before compression, disabling compression on sensitive responses, reducing observable length leakage, limiting query rates, and using protocol-specific guidance; “compress before encrypt” alone does not solve CRIME/BREACH. Gzip streams are not naturally splittable at arbitrary offsets; Python’s `gzip` reader handles concatenated gzip members as one logical decompressed stream, though interoperability should be tested with other tools. BGZF uses independently compressed blocks with an index, and zstd can support independent frames/blocks depending on framing and implementation. HTTP `Content-Encoding: gzip` indicates that the representation body is gzip-compressed; the client must decode that representation before parsing it. Python 3.14 adds standard-library `compression.zstd`; on earlier Python versions, the third-party `zstandard` package is commonly used. `lz4` and `snappy` are also third-party codec options, not built-in modules.

### Answer 34 (Q34)

```python
import mmap, os, re

def find_matches(path, pattern=rb"ERROR"):
    rx = re.compile(pattern)
    try:
        f = open(path, "rb")
    except FileNotFoundError:
        return []
    with f:
        if os.fstat(f.fileno()).st_size == 0:
            return []
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            return [(m.start(), m.group()) for m in rx.finditer(mm)]
```
This returns matches only (so result memory can still grow with match count); a streaming consumer/callback is better for an unbounded number of matches. NumPy is third-party: `numpy.memmap` can expose large arrays backed by files; on platforms that support it, `os.pread` offers offset-based reads without changing a shared file position. mmap uses virtual memory/page cache but still incurs page faults and physical I/O. `ACCESS_READ` maps read-only; `ACCESS_WRITE` permits shared write-through changes; `ACCESS_COPY` gives copy-on-write changes that do not update the underlying file. `flush()` requests mapped changes be written back, but OS/filesystem semantics and crash consistency still matter; durable update protocols may require file synchronization and atomic record design. External truncation or mutation while mapped can cause platform-specific failures, including process-level faults on some systems; coordinate writers or use buffered reads. For a fair benchmark, use the same generated file and identical matching work for buffered line iteration, `readinto`, and mmap; repeat trials and report cold-cache and warm-cache results separately, noting that reliably clearing OS caches may require privileges or a fresh test environment. Buffered I/O may be preferable for small files, sequential one-pass reads, or portability-sensitive paths.

### Answer 35 (Q35)

One valid design is `FILE_HEADER = struct.Struct(">4sB")` for magic/version and `RECORD_HEADER = struct.Struct(">QBI")` for timestamp, severity, and message length; append the UTF-8 message and a fixed-width big-endian CRC32 (`>I`) computed over the record header plus message. Put the record count in a defined footer, or document a recoverable index/footer strategy. Validate magic/version and length caps before reading or allocating; require exact bytes, decode UTF-8 strictly or use a documented error policy, and normalize to NFC only if the schema says so. CRC32 can detect accidental corruption, not malicious tampering or authenticity. For append-only recovery, stop at the first incomplete/corrupt tail and report/truncate only under an explicit recovery policy; do not skip arbitrary bytes and pretend records are trustworthy. Choose and document append/fsync behavior: a successful write is not automatically durable, and a multi-write record can be torn by a crash. An offset index can accelerate lookups but every offset and length must be checked against the current file size. Stream exports record-by-record through bounded compression and validate decompressed limits before parsing. Scan read-only maps only after checking non-empty size, keep mapping lifetime scoped, and avoid concurrent external truncation.

---

# Scoring rubric

| Questions | Count | Points each | Subtotal |
|---|---:|---:|---:|
| Q1–Q10 | 10 | 2 | 20 |
| Q11–Q30 | 20 | 3 | 60 |
| Q31–Q35 | 5 | 4 | 20 |
| **Total** | **35** | — | **100** |

Award full credit for correct reasoning and safe, syllabus-consistent solutions. Award partial credit for correct core concepts with a minor omission. For malformed-input/security questions, do not award full credit to answers that omit validation, trust boundaries, or explicit resource limits. For code-writing questions, equivalent correct solutions are acceptable; exact formatting need not match the answer key.

# Coverage map

| Question(s) | Lesson(s) | Main skills / roadmap self-checks covered |
|---|---|---|
| Q1–Q4, Q9–Q10 | 01 | `str` vs `bytes`, UTF-8 length, indexing, byte conversion, `memoryview`, reusable-buffer `readinto`, exported-buffer lifetime |
| Q5–Q8, Q9 | 02 | `struct` formats/size, endianness/alignment, fixed header parsing, bounds checks, truncated input and round-trip tests |
| Q11–Q15 | 03 | NFC/NFD equality, NFC vs NFKC, slug policy, case folding, grapheme clusters and text pitfalls |
| Q16–Q19 | 04 | named groups, fullmatch/search/match, test cases, calendar validation, catastrophic backtracking and defensive mitigation |
| Q20–Q21 | 05 | `get_close_matches`, cutoff calibration, scale trade-offs, `unified_diff` vs `ndiff`, `textwrap`, `string.Template`, f-string currency formatting, and template-injection safety boundaries |
| Q22–Q25 | 06 | why pickle executes code, restricted mitigation limits, safer format choice for model/cache/API, `marshal` and `shelve` caveats |
| Q26–Q33 | 07 | Base64 overhead/padding, codecs/checksums, streaming JSONL, bounded decompression, truncation/corruption, benchmarking, gzip multi-member and HTTP content encoding, splitting, CRIME/BREACH, Python 3.14 zstd note |
| Q34–Q35 | 08 | `mmap` empty/missing-file handling, lifetime, external truncation risk, binary log format, partial-tail recovery, CRC32 and integrated pipeline design |
| Q35 | 01, 02, 03, 06, 07, 08 | Integrated `binlog`-style design, explicit format policy, defensive parsing, serialization trust, bounded export, large-file scanning |

# Final self-check map

The roadmap's three self-checks per lesson are represented as follows:

1. **Lesson 01:** Q1 (text/byte lengths), Q3 (reusable buffer and memoryview lifetime), Q4/Q10 (view behavior and copying).
2. **Lesson 02:** Q5/Q6 (header parsing, `<IHf` size, native alignment), Q7 (parser, round-trip, and truncated input).
3. **Lesson 03:** Q11 (canonical equivalence), Q12 (NFKC and slugification policy/tests), Q15 (grapheme/display issues).
4. **Lesson 04:** Q18 (a conceptual near-match, ReDoS risk, and fix without running the risky pattern), Q16 (timestamp regex and cases), Q17 (matching API differences).
5. **Lesson 05:** Q21 (`unified_diff` versus `ndiff`, wrapped report, right-aligned currency table and total), Q20 (scale limit of fuzzy suggestions and calibrated cutoff).
6. **Lesson 06:** Q22 (untrusted pickle execution), Q22/Q23 (restricted controls and their limits), Q24 (model/cache/API format choices).
7. **Lesson 07:** Q26 (Base64 overhead), Q29/Q30 (bounded output), Q28 (gzip filter and gzip/zstd output choice), Q31/Q32 (truncation errors and benchmark methodology).
8. **Lesson 08:** Q34 (mmap search, access modes, external truncation, and mmap-versus-buffered/readinto benchmark design), Q35 (record recovery and durable append design).

# Completion checklist

- [ ] I can distinguish text, bytes, mutable buffers, and views, including lifetime constraints.
- [ ] I can parse portable binary headers with explicit byte order, bounds checks, and truncation tests.
- [ ] I can normalize and compare Unicode according to a documented field policy.
- [ ] I can write maintainable regexes and avoid catastrophic backtracking on untrusted input.
- [ ] I can use `difflib`, `textwrap`, and close-match suggestions with calibrated expectations.
- [ ] I can explain why pickle is unsafe for untrusted input and choose alternatives by use case.
- [ ] I can encode Base64 data, stream compression, enforce decompression limits, and detect incomplete streams.
- [ ] I can use `mmap` for large files while understanding empty-file, lifetime, and external-mutation risks.
- [ ] I can explain checksums versus cryptographic integrity/authenticity and design defensive recovery behavior.
- [ ] I can complete the roadmap's `binlog` mini-project with round-trip, corruption, truncation, and resource-limit tests.
