# Roadmap — Module 1.14: Bytes, Binary Data and Advanced Text Processing

This is the learning roadmap for the fourteenth module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about bytes, binary formats and advanced text handling, **in what order**,
**how** to practise each topic, and **how to prove to yourself** that you
have learned it.

Text and bytes are different things, and almost every data-engineering and
AI bug involving "weird characters", corrupted files, wrong checksums,
truncated downloads or unreadable binaries comes from mixing them up.
Tokenizers operate on bytes (byte-level BPE), Parquet/Avro/Arrow are binary
formats, network protocols are byte streams, model weights are binary blobs,
and embeddings are packed floats. This module gives you the tools to read,
write, inspect and reason about all of them.

Module 1.5 taught encodings and newlines for text files. Module 1.4 taught
basic regular expressions. This module goes **deeper**: raw bytes,
`memoryview`, `struct`, Unicode normalisation, advanced regex, diffs,
pickle risks, compression and memory-mapped files.

> Target version: **Python 3.12+**; 3.13/3.14 notes are flagged inline.

---

## 1. Module outcome

By the end of this module you will be able to:

- Distinguish `str`, `bytes`, `bytearray` and `memoryview`, and convert
  between them with explicit encodings.
- Read and write fixed binary layouts with `struct`, handling endianness and
  alignment, and parse a real file header.
- Explain Unicode code points, normalisation forms (NFC/NFD/NFKC/NFKD),
  case folding, grapheme clusters and their effect on equality, length,
  sorting and search.
- Write maintainable, safe, fast regular expressions using named groups,
  lookarounds, verbose mode, and know how to avoid catastrophic backtracking.
- Compare text with `difflib`, wrap and format with `textwrap`, and use
  `string` utilities and `str` methods fluently.
- Explain pickle/marshal/shelve risks and choose safer serialisation.
- Compress, encode and stream data with `base64`, `zlib`, `gzip`, `bz2`, `lzma`.
- Memory-map large files with `mmap` and process them without loading them fully.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Binary, bits, bytes, hexadecimal | Stage 0 — Module 0.1 (04, 05) | Reading hex dumps and byte layouts |
| Strings, indexing, slicing | Module 1.2 (04) | `bytes` mirrors many `str` operations |
| Encodings, newlines | Module 1.5 (05) | UTF-8 details build on this |
| Regular expression basics | Module 1.4 (07) | Advanced regex extends it |
| Safe file writes | Module 1.10 (05) | Binary writes and checksums |
| Standard library toolkit (`hashlib`, `tempfile`) | Module 1.13 | Used in exercises |
| Memory, object model | Module 1.9 (10), Module 1.11 (07) | `memoryview` and buffers |

**Tools:** Python 3.12+, `uv`, `pytest`, `hexdump`/`xxd`/`od` (CLI),
`file`, and a hex editor extension in VS Code (Stage 0 developer environment).

---

## 3. How the module is organised

```text
Phase A — Bytes and Binary Layouts            (Basics)
  01 bytes, bytearray and memoryview
  02 struct and binary file formats
Phase B — Text in Depth                       (Intermediate)
  03 Unicode normalisation and text pitfalls
  04 advanced regular expressions
  05 difflib, textwrap and string utilities
Phase C — Serialisation and Compression       (Advanced)
  06 pickle, marshal and shelve risks
  07 base64, zlib, gzip and stream compression
  08 mmap and large binary files
```

Pace: about 2–3 weeks part-time. Each lesson ends with a tested script and
a hex-dump exercise.

---

## Lesson 01 — `01-bytes-bytearray-and-memoryview.md`

**Why it matters.** Network I/O, files opened in `"rb"`, hashes, images,
audio, tokenizer output, protobuf messages and database BLOBs are bytes.
`memoryview` lets you slice big buffers **without copying**.

### Basic — what to learn

- `str` = sequence of Unicode code points; `bytes` = immutable sequence of
  integers 0–255; `bytearray` = mutable version.
- Literals: `b"abc"`, `bytes([65, 66])`, `bytes(4)` (zeros), `b"\x00\xff"`.
- `.encode("utf-8")` / `.decode("utf-8")`; `errors="strict" | "replace" | "ignore" | "backslashreplace"`.
- Indexing returns an **int** (`b"A"[0] == 65`); slicing returns `bytes`.
- Hex helpers: `bytes.hex()`, `bytes.fromhex("ff00")`.

```python
data = "café".encode("utf-8")
print(data, len("café"), len(data))          # b'caf\xc3\xa9' 4 5
print(data.hex(), data.decode())
print(b"abc"[0], b"abc"[:2])                  # 97 b'ab'
```

### Intermediate — what to learn

- `bytearray` mutation: `append`, `extend`, slice assignment, `del`; use for
  building packets or buffers incrementally.
- `bytes` methods that mirror `str`: `split`, `strip`, `startswith`,
  `find`, `replace`, `join`; and ones that don't (`format` is absent; use
  `%` formatting or f-strings then encode).
- Integer ↔ bytes: `int.to_bytes(length, "big"|"little", signed=...)` and
  `int.from_bytes`.
- File I/O: `open(path, "rb")`, `read(n)`, `readinto(buf)`, chunked reading
  with `iter(lambda: f.read(65536), b"")`.
- Detecting encodings (BOM, `charset-normalizer` awareness) and handling
  undecodable input with `surrogateescape` for round-trip safety.
- Comparison and hashing of `bytes`; constant-time comparisons for secrets.

```python
n = 258
print(n.to_bytes(2, "big"), n.to_bytes(2, "little"))   # b'\x01\x02' b'\x02\x01'
print(int.from_bytes(b"\x01\x02", "big"))              # 258

buf = bytearray(b"hello")
buf[0:1] = b"J"; buf.extend(b"!")
print(buf)                                             # bytearray(b'Jello!')
```

### Advanced — what to learn

- The **buffer protocol** and `memoryview`: zero-copy slices of
  `bytes`/`bytearray`/`array`/NumPy arrays; `.cast("I")`, `.tolist()`, `.nbytes`, `.release()`.
- `readinto` + preallocated `bytearray` for allocation-free loops.
- `array.array` and typed buffers; relationship to NumPy `ndarray` (Stage 2).
- Zero-copy parsing: slicing a `memoryview` of a large message and decoding
  only the fields you need.
- Byte-level views of text: how UTF-8 encodes 1–4 bytes per code point;
  why `len(s)` ≠ `len(s.encode())`; truncating bytes can split a character
  (use `errors="ignore"` carefully or decode incrementally with `codecs.getincrementaldecoder`).
- Byte-level tokenizers (GPT-style byte-level BPE) as a motivating example.
- Memory: `sys.getsizeof` for bytes; copy cost of slicing `bytes` vs `memoryview`; benchmark.
- Security: untrusted lengths and sizes in binary input → cap allocations.

### Common mistakes

- Indexing `bytes` and expecting a 1-length `bytes`.
- Decoding with the wrong codec or without `errors=` handling for dirty data.
- Slicing large `bytes` in a loop (O(n²) copying).

### Self-check

1. What do `len("é")` and `len("é".encode())` return and why?
2. How does `memoryview` avoid copying and what is the risk when the underlying object resizes?
3. Write `read_chunks(path, size)` yielding `memoryview`s from a reusable buffer.

---

## Lesson 02 — `02-struct-and-binary-file-formats.md`

**Why it matters.** Many formats are just packed fixed-width fields:
file headers (PNG, WAV, ELF, Parquet footers), network packets, sensor
records, custom logs. `struct` converts between Python values and those bytes.

### Basic — what to learn

- `struct.pack(fmt, *values)` / `struct.unpack(fmt, buffer)`; `calcsize`.
- Format characters: `b B h H i I q Q f d ? s x`.
- Byte-order prefixes: `<` little-endian, `>` big-endian/network (`!`),
  `=` native with standard sizes, `@` native with alignment.

```python
import struct
packed = struct.pack("<IHf", 42, 7, 3.5)       # u32, u16, float32
print(packed.hex(), struct.calcsize("<IHf"))   # 10 bytes
print(struct.unpack("<IHf", packed))           # (42, 7, 3.5)
```

### Intermediate — what to learn

- Strings in structs: `4s` yields `bytes` of exactly length 4 (pad/truncate);
  decode explicitly; null-padding conventions.
- `struct.Struct(fmt)` compiled objects, `unpack_from(buf, offset)`,
  `pack_into`, `iter_unpack` for arrays of records.
- Parsing a real header: read a PNG signature + `IHDR` chunk, or a WAV
  `RIFF` header, or a BMP header; validate magic numbers and lengths.
- Checksums: `zlib.crc32` for chunk validation.
- Alignment and padding: native `@` vs standard sizes; use `<`/`>` explicitly
  for portable formats.
- `ctypes.Structure` and `array`/`dataclass` as alternatives.

```python
HEADER = struct.Struct(">8s I 4s")            # PNG sig, length, chunk type
with open("img.png", "rb") as f:
    sig, length, ctype = HEADER.unpack(f.read(HEADER.size))
    assert sig == b"\x89PNG\r\n\x1a\n", "not a PNG"
```

### Advanced — what to learn

- Variable-length encodings: varint (LEB128 / protobuf), length-prefixed
  strings, TLV (type-length-value); implement encoders/decoders and test with Hypothesis-style round-trips.
- Bit-level manipulation: masks, shifts, flags, bit fields; `int.bit_length`, `int.bit_count`.
- Endianness bugs across systems; `sys.byteorder`; network byte order.
- Robust parsing: bounds checking, truncated input, absurd length fields, versioned
  headers; fuzzing parsers (link to Module 1.16 lesson 09).
- Relationship to schema'd formats: Protobuf, Avro, MessagePack, Arrow IPC
  (Stage 2) — why you'd normally use a library, and why it helps to know the layout.
- NumPy structured dtypes and `np.frombuffer` for bulk binary arrays.
- Writing binary files atomically with a trailing checksum footer.

### Common mistakes

- Forgetting the byte-order prefix.
- Trusting length fields from untrusted files.
- Decoding fixed-width strings without stripping `\x00`.

### Self-check

1. What does `"<IHf"` mean and what is its size?
2. Why can `"@IHf"` differ in size from `"<IHf"`?
3. Write a parser for a tiny custom log format and a round-trip test plus a truncated-input test.

---

## Lesson 03 — `03-unicode-normalization-and-text-pitfalls.md`

**Why it matters.** Two strings that look identical can compare unequal
(`"é"` as one code point vs `"e"` + combining accent), emoji have variable
lengths, case-insensitive matching differs by language, and sorting names is
locale-dependent. These bugs corrupt de-duplication, joins, search and
LLM-input preprocessing.

### Basic — what to learn

- Unicode terms: **code point**, **encoding** (UTF-8/16/32), **glyph**,
  **grapheme cluster** (what users perceive as one character).
- `ord`, `chr`, `"é"`, `"\N{LATIN SMALL LETTER E WITH ACUTE}"`.
- `str.lower()` vs `str.casefold()`; `str.isalpha`, `isdigit` vs `isdecimal`, `isnumeric`.
- `len()` counts code points, not what users see.

```python
a, b = "café", "café"
print(a == b, len(a), len(b))      # False 4 5
```

### Intermediate — what to learn

- `unicodedata.normalize("NFC" | "NFD" | "NFKC" | "NFKD", s)`; when to use
  each: **NFC** for storage/comparison, **NFKC** for search keys (folds
  compatibility characters like `ﬁ`, full-width digits).
- `unicodedata.category`, `name`, `combining`; stripping accents via NFD +
  removing combining marks (and why this is lossy and language-dependent).
- `casefold()` for caseless matching (`"ß".casefold() == "ss"`); Turkish dotless-i
  caveat.
- Invisible/problem characters: zero-width space, BOM (`﻿`), non-breaking
  space, RTL marks, smart quotes; cleaning pipelines.
- Whitespace: `str.split()` vs `re.split(r"\s+")`; Unicode whitespace classes.
- Normalising before hashing, de-duplicating, joining or indexing text.

```python
import unicodedata as ud

def key(s: str) -> str:
    s = ud.normalize("NFKC", s).casefold().strip()
    return " ".join(s.split())

assert key("  ﬁne Art ") == key("FINE art")
```

### Advanced — what to learn

- Grapheme clusters: counting user-perceived characters needs the `regex`
  package (`\X`) or `grapheme`; emoji ZWJ sequences, flags, skin tones.
- Surrogates, `surrogateescape`, `UnicodeEncodeError`/`DecodeError` handling,
  and lone surrogates in JSON.
- Security: **homoglyph** and **confusable** attacks (Cyrillic `а` vs Latin `a`),
  bidirectional-text spoofing ("Trojan Source"), IDN/punycode; NFKC normalisation
  for identifiers (PEP 3131); defend with allow-lists and `unicodedata.category` checks.
- Collation: `locale.strxfrm`, `PyICU` / ICU collation for language-correct sorting;
  default code-point ordering is wrong for human-facing lists.
- Text for LLM pipelines: normalisation before tokenisation, token counts vs character
  counts, byte-fallback tokenisers, truncating by tokens not characters.
- File-level issues: mixed encodings, mojibake detection and repair (`ftfy`), normalising
  filenames across macOS (NFD) and Linux/Windows (NFC).
- Round-trip invariants and tests (`decode(encode(x)) == x`) and property-based tests.

### Common mistakes

- Comparing user input with `==` without normalising.
- Using `lower()` where `casefold()` is needed.
- Truncating strings by characters in the middle of a grapheme cluster.

### Self-check

1. Why are `"é"` and `"é"` unequal and how do you make them equal?
2. When is NFKC preferable to NFC?
3. Build `slugify()` that handles accents, case, whitespace and symbols, with tests including emoji and CJK input.

---

## Lesson 04 — `04-advanced-regular-expressions.md`

**Why it matters.** Log parsing, data cleaning, entity extraction,
validation and tokenisation all use regex. Module 1.4 covered the basics;
production work demands readable, tested, performant, safe patterns.

### Basic — what to learn

- Recap: `re.search`, `match`, `fullmatch`, `findall`, `finditer`, `sub`, `split`, `compile`.
- Character classes, quantifiers (greedy vs lazy), anchors, groups, alternation.
- Raw strings `r"..."` for patterns.

```python
import re
m = re.search(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})", "on 2026-10-14!")
print(m.group("y"), m.groupdict())
```

### Intermediate — what to learn

- **Named groups** and `groupdict()`; non-capturing groups `(?:...)`; backreferences `\1`, `(?P=name)`.
- **Verbose mode** `re.VERBOSE` with comments for maintainable patterns; flags
  `IGNORECASE`, `MULTILINE`, `DOTALL`, `ASCII`, inline flags `(?i)`.
- **Lookahead/lookbehind**: `(?=...)`, `(?!...)`, `(?<=...)`, `(?<!...)` (fixed-width lookbehind in `re`).
- `re.sub` with a function replacement and with `\g<name>`; `re.split` with groups; `re.escape`.
- `match.start()/end()/span()`, scanning with `finditer`, tokenisers using alternation of named groups.
- Unicode behaviour: `\w`, `\d`, `\s` match Unicode by default for `str`.

```python
TOKEN = re.compile(r"""
    (?P<NUM>   \d+(?:\.\d+)? )
  | (?P<ID>    [A-Za-z_]\w* )
  | (?P<OP>    [-+*/()] )
  | (?P<WS>    \s+ )
""", re.VERBOSE)

def tokenize(s):
    for m in TOKEN.finditer(s):
        if m.lastgroup != "WS":
            yield m.lastgroup, m.group()
```

### Advanced — what to learn

- **Catastrophic backtracking / ReDoS**: nested quantifiers like `(a+)+$`
  against `"aaaa…!"`; detect with timing tests; mitigate with atomic groups
  and possessive quantifiers (3.11+ `(?>...)`, `a++`), simpler patterns,
  input length limits, or the `re2`/`google-re2` engine.
- Performance: compile once, anchor patterns, prefer `str` methods
  (`startswith`, `in`, `partition`) when regex isn't needed, avoid `.*` prefixes.
- The third-party `regex` module: Unicode properties `\p{L}`, `\X`, fuzzy
  matching, recursive patterns, variable-length lookbehind.
- When **not** to use regex: HTML/XML (use parsers), JSON, CSV, nested
  grammars, dates (use `datetime`/`dateutil`), emails/URLs (use validators).
- Writing a parser instead: hand-rolled scanner, `str.partition`, `shlex`, or a
  grammar library (`lark`, `pyparsing`) when regex becomes unreadable.
- Testing regex: table-driven `pytest.mark.parametrize` with positive, negative
  and adversarial cases; documenting each pattern.
- Log-parsing project: Apache/NGINX combined log, syslog, application JSON-ish
  lines; measuring throughput on 1 GB with `mmap` + `bytes` regexes.
- Regexes on `bytes` patterns (`rb"..."`) for binary/log data.

### Common mistakes

- Patterns with nested unbounded quantifiers on untrusted input.
- Using `.` expecting it to match newlines.
- Compiling inside loops, or `findall` on huge inputs (use `finditer`).

### Self-check

1. Show an input that makes `(a+)+$` take exponential time and fix the pattern.
2. Write a verbose regex for ISO-8601 timestamps with an optional timezone and test 10 cases.
3. Explain the difference between `match`, `search` and `fullmatch`.

---

## Lesson 05 — `05-difflib-textwrap-and-string-utilities.md`

**Why it matters.** Comparing configs, reviewing generated text, producing
readable reports and error messages, fuzzy-matching names and formatting
CLI output are small tasks that need the right tool — not a hand-written loop.

### Basic — what to learn

- `difflib.unified_diff`, `ndiff`, `context_diff`; `HtmlDiff` for reports.
- `difflib.SequenceMatcher(None, a, b).ratio()` for similarity (0–1).
- `difflib.get_close_matches(word, possibilities, n, cutoff)` for typo suggestions ("did you mean…?").
- `textwrap.wrap`, `fill`, `dedent`, `indent`, `shorten`.

```python
import difflib, textwrap
old, new = ["a", "b", "c"], ["a", "x", "c"]
print("\n".join(difflib.unified_diff(old, new, "old", "new", lineterm="")))
print(difflib.get_close_matches("pyhton", ["python", "pytest", "pylint"]))
print(textwrap.shorten("A very long sentence for a table cell", width=20, placeholder="…"))
```

### Intermediate — what to learn

- Diffing files and directories (`filecmp`, `difflib` on lines); ignoring whitespace
  or case via preprocessing; showing diffs in test failures and snapshot tests
  (links to Module 1.16 lesson 04).
- `SequenceMatcher.get_opcodes()` / `get_matching_blocks()` to build custom
  highlighting; `autojunk` behaviour on long sequences.
- The `string` module: constants (`ascii_letters`, `digits`, `punctuation`),
  `string.Template` (safe substitution, `$name`), `string.Formatter`.
- `str` method fluency: `partition`/`rpartition`, `splitlines`, `removeprefix`/
  `removesuffix`, `translate` + `str.maketrans`, `zfill`, `center`, `ljust`,
  `expandtabs`, `isidentifier`, `format_map`.
- f-string format mini-language: width, alignment, fill, sign, thousands separators,
  precision, `!r`, `=` debugging specifier; table formatting without libraries.
- Formatting reports: fixed-width tables, truncation, ellipsis, right-aligned numbers.

```python
rows = [("alpha", 3.14159), ("beta", 1234.5)]
for name, val in rows:
    print(f"{name:<10}{val:>12,.2f}")
```

### Advanced — what to learn

- Fuzzy matching at scale: why `difflib` is O(n²) and slow for millions of
  strings → `rapidfuzz`, blocking, n-gram indexes, MinHash (preview of Stage 9 retrieval).
- Edit distance (Levenshtein), Jaro-Winkler vs `SequenceMatcher`; choosing a metric
  for names, product titles, OCR output.
- Human-friendly CLI output: width detection (`shutil.get_terminal_size`), wrapping
  with ANSI codes, `rich`/`tabulate` as next steps.
- Template safety: `string.Template` vs f-strings vs Jinja2 (autoescape); never
  format user data into SQL/shell/HTML with `%` or `.format`.
- Python 3.14 **template strings** (t-strings, PEP 750): structured interpolation
  for safe SQL/HTML builders (preview).
- Internationalised text wrapping (CJK double-width characters, combining marks) — `wcwidth`.
- Building a "did you mean" feature for a CLI using `get_close_matches` with
  unit tests and a sane cutoff.

### Common mistakes

- Using `ratio()` thresholds without calibrating on real data.
- Using `str.format` with user-controlled format strings (attribute access leaks).
- Assuming one character = one terminal column.

### Self-check

1. How does `unified_diff` differ from `ndiff`?
2. Why is `get_close_matches` unsuitable for matching 10⁶ names against 10⁶ names?
3. Format a right-aligned currency table with thousands separators and a total row.

---

## Lesson 06 — `06-pickle-marshal-and-shelve-risks.md`

**Why it matters.** `pickle` is convenient, ubiquitous in ML (sklearn
models, PyTorch `torch.save` historically) and **dangerous**: loading a
pickle executes arbitrary code. Model hubs and shared files have been used
to deliver malware. Knowing the risk and the alternatives is essential.

### Basic — what to learn

- `pickle.dumps/loads`, `dump/load`; protocols (0–5; default depends on version);
  what can be pickled (module-level functions/classes, most built-ins) and what can't (lambdas, open files, locks, generators).
- `marshal`: internal format for `.pyc`; version-specific; not for data exchange.
- `shelve`: persistent dict built on `dbm` + `pickle`; `with shelve.open(path) as db:`.

```python
import pickle
blob = pickle.dumps({"a": [1, 2, 3]}, protocol=pickle.HIGHEST_PROTOCOL)
print(pickle.loads(blob))
```

### Intermediate — what to learn

- **Why unpickling is code execution**: `__reduce__` can return any callable and
  arguments; demonstrate with a harmless `print` payload in an isolated test (never `os.system` outside a sandbox).
- Never unpickle data from untrusted or unauthenticated sources — including
  downloaded model files, cache files in shared directories, and network messages.
- Mitigations and their limits: `pickle.Unpickler.find_class` allow-listing,
  signing with HMAC (authenticity, not safety against a malicious signer),
  `fickling` for analysis, sandboxing.
- Safer alternatives by use case:
  - data: JSON, CSV, Parquet, Arrow, MessagePack, Protocol Buffers;
  - arrays/models: `numpy.save(allow_pickle=False)`, `safetensors`, ONNX;
  - config: TOML/YAML (`safe_load`).
- Versioning and compatibility problems: pickles break when classes move or
  change; they are not an archival format.
- `shelve` pitfalls: no concurrency safety, backend differences, pickle risk on read, writeback memory use.

```python
import io, pickle
ALLOWED = {("builtins", "dict"), ("builtins", "list")}

class Restricted(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) in ALLOWED:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"forbidden: {module}.{name}")

def safe_loads(b: bytes):
    return Restricted(io.BytesIO(b)).load()
```

### Advanced — what to learn

- Pickle protocol internals: opcodes (`GLOBAL`, `REDUCE`, `BUILD`); `pickletools.dis`
  to read a pickle without executing it.
- Out-of-band buffers (protocol 5, PEP 574) for zero-copy large array transfer.
- `copyreg`, `__reduce_ex__`, `__getstate__` for custom pickling (link to Module 1.11 lesson 11).
- ML supply-chain risk: malicious pickled models on public hubs; scanning tools;
  moving to `safetensors`; `torch.load(weights_only=True)`.
- Multiprocessing implicitly pickles arguments/results — why lambdas and local functions fail,
  and the cost of pickling large objects.
- Secure inter-process messaging design: schema'd formats + validation.
- Incident-style exercise: given a suspicious `.pkl`, analyse with `pickletools` and decide.
- Policy: add `pickle.loads`/`yaml.load`/`eval` to code-review and static-analysis (`bandit B301/B403`) rules.

### Common mistakes

- Using pickle as a data-interchange or long-term storage format.
- Believing "it's from my own cache" — caches in shared locations are attack surface.
- Treating `shelve` as a database.

### Self-check

1. Why can `pickle.loads(untrusted)` run arbitrary code?
2. What does the restricted `Unpickler` above protect against, and what does it not?
3. Choose a format for (a) a trained scikit-learn model, (b) a job-result cache, (c) an API payload, and justify each.

---

## Lesson 07 — `07-base64-zlib-gzip-and-stream-compression.md`

**Why it matters.** Data engineers constantly encode binary data into text
(JSON, email, URLs, tokens) and compress files and streams (`.gz`, `.zst`,
HTTP `Content-Encoding`, Parquet codecs). Streaming, bounded-memory
processing and decompression-bomb defence are the production concerns.

### Basic — what to learn

- `base64.b64encode/b64decode`, `urlsafe_b64encode`, `b32`, `b16`, `a85`;
  output is **bytes** (decode to `str` for JSON); ~33 % size overhead.
- Base64 is **encoding, not encryption**.
- `zlib.compress/decompress`; `gzip.open(path, "rt" | "rb" | "wt")`, `bz2`, `lzma`.
- Compression levels trade speed vs ratio.

```python
import base64, gzip, json
payload = {"img": base64.b64encode(b"\x89PNG...").decode("ascii")}
print(json.dumps(payload))

with gzip.open("events.jsonl.gz", "wt", encoding="utf-8") as f:
    f.write(json.dumps({"id": 1}) + "\n")
```

### Intermediate — what to learn

- Streaming: `zlib.compressobj()` / `decompressobj()`, feeding chunks;
  `gzip.GzipFile`, `shutil.copyfileobj` with compression; reading `.gz` line by line.
- Appending to gzip files (multi-member), `Content-Encoding: gzip` handling.
- Choosing codecs: gzip (ubiquitous), zstd (fast, great ratio; `compression.zstd`
  in the stdlib from 3.14, `zstandard` package before), lz4/snappy (very fast), bz2/xz (slow, high ratio).
- Padding and URL-safe variants; stripping `=` padding in JWT-style tokens.
- Checksums: `zlib.crc32`, `adler32`; verifying decompressed output via hash.
- Benchmark: ratio and throughput on text, JSON, CSV, already-compressed data (incompressible).

```python
import zlib
d = zlib.decompressobj()
out = bytearray()
with open("data.z", "rb") as f:
    for chunk in iter(lambda: f.read(64 * 1024), b""):
        out += d.decompress(chunk)
out += d.flush()
```

### Advanced — what to learn

- **Decompression bombs**: tiny input expanding to GBs; cap output with
  `decompressobj().decompress(data, max_length)`; check ratio and absolute limits;
  apply to zip, gzip, HTTP bodies, images.
- Splittable vs non-splittable compression for distributed processing (gzip vs bgzip/zstd frames; why Parquet compresses *inside* the file — Stage 2).
- Base64 vs Base85 vs hex trade-offs; embedding images in HTML/JSON; size limits in APIs.
- Chunked/streaming uploads, backpressure, constant-memory pipelines
  (`read → decompress → parse → write`).
- Integrity and authenticity: compress-then-encrypt (never encrypt-then-compress with attacker-influenced data: CRIME/BREACH),
  and not mixing secrets with attacker-controlled content before compression.
- Dictionary compression (zstd dictionaries) for many small similar records.
- Error handling for truncated and corrupt streams (`zlib.error`, `EOFError`, `BadGzipFile`).
- Observability: logging compressed vs uncompressed sizes and ratios.

### Common mistakes

- Treating base64 as security.
- `read()`-ing whole compressed files into memory.
- No limits on decompressed size from untrusted sources.

### Self-check

1. Why does base64 grow data by about a third?
2. How do you cap output when decompressing untrusted data?
3. Build a streaming `gz → filter → zstd/gz` converter with constant memory and a size-limit test.

---

## Lesson 08 — `08-mmap-and-large-binary-files.md`

**Why it matters.** When a file is larger than comfortable memory but you
need random access or fast scanning (log search, index lookups, binary
datasets, embeddings matrices), memory mapping lets the OS page data on
demand. It is also how many databases and ML libraries load big files.

### Basic — what to learn

- `mmap.mmap(fileno, length=0, access=mmap.ACCESS_READ)`; behaves like a
  `bytearray`/file: slicing, `find`, `read`, `seek`.
- Context manager usage and closing; file must be non-empty to map.
- Why it's fast: the OS page cache, no `read()` copy into a Python buffer for each access.

```python
import mmap
with open("big.log", "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
    idx = mm.find(b"ERROR")
    print(idx, mm[idx: idx + 80])
```

### Intermediate — what to learn

- Searching and scanning: `mm.find`, `mm.rfind`, regexes on `mm` (bytes patterns);
  iterating lines with `mm.readline()`.
- Access modes: `ACCESS_READ`, `ACCESS_WRITE` (write-through), `ACCESS_COPY`
  (copy-on-write); `flush()`; resizing (`mm.resize`) and its platform limits.
- Combining `mmap` with `memoryview`/`struct`/`numpy.frombuffer` for zero-copy
  access to fixed-width records or float arrays.
- `numpy.memmap` for big arrays on disk (Stage 2); `os.pread` as an alternative for random reads.
- Fixed-record file index: build an on-disk index of offsets and do O(1) lookups.
- Sparse files, preallocation (`os.truncate`, `posix_fallocate`).

```python
import numpy as np
arr = np.memmap("embeddings.f32", dtype="float32", mode="r", shape=(1_000_000, 384))
print(arr[123_456][:4])        # reads only the needed pages
```

### Advanced — what to learn

- Virtual memory, page faults, resident vs virtual size, `madvise` hints
  (`mm.madvise(mmap.MADV_SEQUENTIAL)` 3.8+) — links to Stage 0 OS fundamentals.
- Concurrency: multiple processes sharing a read-only map; writers need locking
  (`fcntl.flock`, `msvcrt.locking`); crash consistency and `msync` semantics.
- Pitfalls: file truncated by another process → `SIGBUS`/access violation; 32-bit address limits;
  network filesystems; Windows file-lock behaviour; memory accounting in containers.
- Throughput measurements: `read(1 MiB)` loops vs `mmap` scanning vs `readinto`; cold vs warm page cache.
- Designing append-only log files + sparse index; checksummed records; recovery after partial writes.
- When not to use mmap: tiny files, sequential-once reads (plain buffered I/O is as fast),
  hostile files, portability constraints.
- Use cases: grep-like log search tool, vector-file loader, binary lookup table.
- Building a mini key-value store file format (header + records + footer checksum) with `struct` + `mmap`.

### Common mistakes

- Mapping an empty file (`ValueError`).
- Forgetting to close maps (file handles/virtual memory leak).
- Assuming `mmap` writes are durable without `flush`.

### Self-check

1. What is the difference between `ACCESS_WRITE` and `ACCESS_COPY`?
2. Why can a truncated file crash a process that reads from a map?
3. Build a binary log searcher using `mmap` and a bytes regex, and benchmark it against buffered line reading on a 1 GB file.

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**:

| Phase | Question types |
| --- | --- |
| A | Predict `len`/index results; parse a header with `struct`; fix endianness bugs; zero-copy slicing |
| B | Normalise and compare tricky strings; ReDoS fix; fuzzy "did you mean"; diff formatter |
| C | Spot the pickle exploit; choose safe formats; bounded decompression; mmap search |

Include 6 **"what is the bug?"** items (mojibake, `==` on unnormalised text, `(a+)+`, unpickling untrusted bytes, unlimited `decompress`, wrong byte order).

---

## 5. Module mini-project

**Build `binlog`**, a compact binary log format and toolchain:

1. Define a format: magic bytes, version, record = length-prefixed UTF-8 message
   + timestamp (u64) + level (u8) + CRC32, file footer with record count.
2. `writer.py`: append records atomically (temp file → replace) or in append mode with fsync policy.
3. `reader.py`: `mmap`-based iterator with bounds checks, CRC verification, and
   resilient recovery from a truncated tail.
4. `search.py`: regex search (bytes patterns) over messages with level and time filters.
5. `convert.py`: stream to/from JSON Lines and gzip/zstd with decompression limits.
6. Normalise messages with NFC on write; test with accents, emoji, CJK.
7. Property-style round-trip tests and a corrupted-file test suite; benchmark vs JSON Lines.

Acceptance: ≥ 90 % coverage, fuzz-style tests for the reader (random truncation/bit flips never crash or over-allocate), documented format spec in `FORMAT.md`.

---

## 6. Completion checklist

- [ ] I can explain `str` vs `bytes` and convert with explicit encodings and error policies.
- [ ] I can parse and build binary layouts with `struct`, including endianness.
- [ ] I use `memoryview` for zero-copy slicing and know its limits.
- [ ] I normalise and case-fold text correctly and explain grapheme clusters.
- [ ] I write maintainable regexes and avoid catastrophic backtracking.
- [ ] I use `difflib`/`textwrap`/`str` utilities for diffs, suggestions and reports.
- [ ] I can explain why unpickling untrusted data is code execution and choose safer formats.
- [ ] I stream compress/decompress with limits against decompression bombs.
- [ ] I use `mmap` for large-file access and understand its failure modes.
- [ ] I completed the `binlog` mini-project.

**Next:** Module 1.15 — Modern Python Language Features.
