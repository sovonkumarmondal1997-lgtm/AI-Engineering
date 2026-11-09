# 05 — Encodings and Newlines
## Complete Lesson Summary, Roadmap Review, Exercises, Debugging, and Revision

**Roadmap:** Stage 1 — Programming & Computational Thinking  
**Module:** 05 — Text Files, Structured Data, and CLI Programs  
**Lesson:** 05 — Encodings and Newlines

---

# Part A — Complete lesson summary

## 1. Why encoding and newline handling matter

Every text file is ultimately stored as bytes. Python must decode those bytes into text before your program can process them, and encode text into bytes when writing. The encoding determines how bytes map to characters. Newline handling determines how line-ending characters are recognized and translated.

This matters for ordinary text files, CSV, JSON, multilingual customer data, logs, API payloads, data lakes, ETL pipelines, training corpora, prompts, and model outputs. A wrong encoding can raise an exception, but it can also silently produce plausible-looking corrupted text (mojibake). A wrong newline policy can create extra blank lines, stray `\r` characters, or malformed CSV output.

The core pipeline is:

```text
Character → Unicode code point → encoding → bytes → file/network
file/network → bytes → decoding → Unicode code point → Python str
```

Encoding and newline translation are separate layers. Encoding answers, “How do bytes represent text?” Newline handling answers, “Which characters mark a line boundary, and should they be normalized?”

## 2. Characters, Unicode, and code points

A character is the human-facing idea of a letter, digit, punctuation mark, or symbol. Computers store bytes, not human concepts. Unicode provides a shared character repertoire and assigns each character identity a **code point**, conventionally written as `U+` plus hexadecimal digits. The range is `U+0000` through `U+10FFFF`.

Unicode is **not** itself a byte encoding. It defines which characters exist and their numeric identities; UTF-8, UTF-16, and UTF-32 define how those identities become bytes.

```python
print(ord("A"))        # 65
print(hex(ord("A")))   # 0x41
print(chr(65))         # A
print(chr(0x0041))     # A

for character in "Aébà":
    print(character, hex(ord(character)))
```

`ord()` maps one-character `str` to an integer code point. `chr()` maps a valid code point integer back to a one-character `str`. The examples show that accented characters also have precise code points.

## 3. Python `str`, `bytes`, and `bytearray`

Python 3 `str` represents Unicode text. It is not a byte sequence and has no inherent encoding. Indexing and slicing a string work on code points:

```python
text = "বাংলা"
print(type(text))      # <class 'str'>
```

`bytes` is an immutable sequence of values from 0 to 255. It represents raw bytes:

```python
data = b"hello"
print(type(data))      # <class 'bytes'>
print(data[0])         # 104: an int
print(data[0:2])       # b'he': another bytes object
```

A key difference: indexing `str` returns a one-character string, but indexing `bytes` returns an integer byte value. Python deliberately prevents careless mixing:

```python
"hello" + b"world"     # TypeError
```

Do not work around this by guessing. Convert explicitly with `.encode()` or `.decode()` using the correct encoding.

`bytearray` is the mutable counterpart of `bytes`:

```python
data = bytearray(b"hello")
data[0] = 72
print(data)            # bytearray(b'Hello')
```

Use it when building or modifying raw byte buffers in place. Ordinary text processing usually needs `str` and `bytes`; `bytearray` is useful at lower-level binary boundaries.

A further distinction: one Python code point is not always one user-perceived character. Combining accents and joined emoji can contain multiple code points but render as one glyph; this is explained under grapheme clusters below.

## 4. ASCII and why Unicode was needed

ASCII (American Standard Code for Information Interchange) is a 7-bit encoding covering 128 values: basic English letters, digits, punctuation, and control characters. It cannot represent accented characters, Bengali, Chinese, Japanese, or emoji.

UTF-8 deliberately preserves ASCII compatibility: every ASCII character has the same single-byte representation in ASCII and UTF-8.

```python
print("A".encode("ascii"))  # b'A'
"é".encode("ascii")         # UnicodeEncodeError
```

ASCII encoding fails for `é` because its code point is outside the ASCII range.

## 5. Encoding and decoding

**Encoding** converts a Python Unicode `str` into bytes using a named encoding. **Decoding** converts bytes back into a Python `str` using the matching encoding.

```python
text = "বাংলা"
encoded = text.encode("utf-8")
decoded = encoded.decode("utf-8")
print(text == decoded)      # True
```

The encoding used for decoding must match the one used to create the bytes. If it does not, decoding may raise `UnicodeDecodeError`, or may succeed but return wrong text. The same code point can produce different bytes under different encodings:

```python
text = "é"
print(text.encode("utf-8"))    # b'\xc3\xa9'
print(text.encode("utf-16"))   # includes BOM and UTF-16 code unit
print(text.encode("latin-1"))  # b'\xe9'
```

`len(text)` counts Python code points; `len(text.encode("utf-8"))` counts bytes. For `"café"`, the first is 4 and the UTF-8 byte length is 5. This matters when systems impose byte limits.

## 6. UTF-8 internal mechanics

UTF-8 is variable-width: a Unicode scalar value uses one to four bytes.

| Code point range | Pattern | Bytes |
|---|---|---:|
| `U+0000`–`U+007F` | `0xxxxxxx` | 1 |
| `U+0080`–`U+07FF` | `110xxxxx 10xxxxxx` | 2 |
| `U+0800`–`U+FFFF` excluding surrogates | `1110xxxx 10xxxxxx 10xxxxxx` | 3 |
| `U+10000`–`U+10FFFF` | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` | 4 |

The leading bits identify the sequence length. Continuation bytes always begin with `10`. This makes UTF-8 **self-synchronizing**: a decoder can identify character boundaries even when reading partway through a byte stream. It also detects many malformed sequences, but it is not a general corruption-detection system; corrupted bytes can sometimes form another valid sequence.

```python
data = "é".encode("utf-8")
print(" ".join(f"{byte:08b}" for byte in data))
# 11000011 10101001
```

`é` is U+00E9 and uses two bytes. UTF-8 supports all Unicode scalar values (excluding the surrogate range U+D800–U+DFFF).

## 7. UTF-16, UTF-32, and legacy encodings

**UTF-16** uses one or two 16-bit code units. Code points in the Basic Multilingual Plane generally fit in one unit; code points above it (such as many emoji) use a surrogate pair. It is not simply “two bytes per character.”

```python
text = "A🙂"
print(text.encode("utf-16"))     # normally includes a BOM
print(text.encode("utf-16-le"))  # explicit little-endian; no BOM
```

Plain `utf-16` uses native byte order and writes a BOM so the reader can identify byte order. `utf-16-le` and `utf-16-be` explicitly select an order and do not add a BOM.

**UTF-32** uses four bytes per Unicode scalar value. It is simple to reason about and fixed-width, but uses much more storage, so it is uncommon for general file and network interchange.

**Latin-1 / ISO-8859-1** maps U+0000–U+00FF directly to bytes 0–255. Every possible byte sequence decodes under Latin-1, so a successful decode does not prove Latin-1 was the correct encoding.

**Windows-1252** resembles Latin-1 but assigns printable characters such as curly quotes and em dashes to positions 0x80–0x9F. Older exports may use either. Do not assume historical files are UTF-8.

| Encoding | Width | Main point |
|---|---|---|
| ASCII | 1 byte, limited | 128 basic values |
| UTF-8 | 1–4 bytes | Best default for new text interchange |
| UTF-16 | 2 or 4 bytes | Code units and surrogate pairs; BOM/byte order |
| UTF-32 | 4 bytes | Fixed width, larger storage |
| Latin-1 | 1 byte | Legacy Western European; every byte decodes |
| Windows-1252 | 1 byte | Legacy Windows typography |

A **character repertoire/character set** is the set of characters a system knows about. An **encoding** is the rule for converting those characters into bytes. Calling UTF-8 a character set is technically imprecise: Unicode defines the repertoire; UTF-8 encodes it.

## 8. `encode()` and `decode()` error policies

The common signatures are:

```python
str.encode(encoding="utf-8", errors="strict")
bytes.decode(encoding="utf-8", errors="strict")
```

`encoding` selects the codec. `errors` selects what happens when a character cannot be encoded or bytes cannot be decoded.

| Handler | Behavior | Main risk/use |
|---|---|---|
| `strict` | Raises an error (default) | Best data-integrity default |
| `ignore` | Silently drops invalid/unrepresentable data | Dangerous silent data loss |
| `replace` | Uses `?` on encode or U+FFFD on decode | Visible but lossy |
| `backslashreplace` | Emits escaped representation | Useful diagnostic trace |
| `namereplace` | Emits `\N{UNICODE NAME}` on encode | Human-readable diagnostic trace; encode-only |
| `surrogateescape` | Maps undecodable bytes into U+DC80–U+DCFF so they can round-trip | Specialized filesystem handling |
| `surrogatepass` | Allows surrogate code points through certain Unicode codecs | Specialized low-level use |

Examples:

```python
"café".encode("ascii", errors="ignore")          # b'caf'
"café".encode("ascii", errors="replace")         # b'caf?'
"café".encode("ascii", errors="backslashreplace")# b'caf\\xe9'
"café".encode("ascii", errors="namereplace")     # named escape
```

`ignore` is dangerous because output can look plausible while characters have disappeared. Prefer `strict`; catch and handle failures explicitly, quarantine bad data, or document a deliberate lossy policy.

`UnicodeEncodeError` means a `str` contains a character the selected codec cannot represent. `UnicodeDecodeError` means bytes are not a valid sequence under the selected codec. Their messages expose the codec, problematic character/bytes, and position; decode errors also expose `.start`, `.end`, and `.reason`.

## 9. Mojibake and unknown encodings

**Mojibake** is corrupted-looking text caused by decoding bytes using the wrong encoding. It often happens without an exception:

```python
original = "café"
utf8_bytes = original.encode("utf-8")
wrong = utf8_bytes.decode("latin-1")
print(wrong)             # cafÃ©
```

Latin-1 accepts every byte, so the wrong decode succeeds but produces incorrect text.

There is no universal, foolproof way to identify an arbitrary encoding from bytes alone. Use evidence:
- File documentation or format specification.
- Producer software and its documented defaults.
- Metadata such as an HTTP `charset`.
- Protocol requirements (JSON exchanged between independent systems is UTF-8).
- A BOM when present.
- Successful decode plus domain-specific validation of expected content.
- Representative samples and knowledge of the source system.

Do not try random encodings until the output “looks right.” Statistical detector libraries can provide candidates, not certainty. Validate the result.

## 10. BOM and `utf-8-sig`

A **Byte Order Mark (BOM)** is a byte sequence at the start of a file that can indicate encoding and, for UTF-16/UTF-32, byte order.

| Encoding | BOM bytes |
|---|---|
| UTF-8 | `EF BB BF` |
| UTF-16 BE | `FE FF` |
| UTF-16 LE | `FF FE` |
| UTF-32 BE | `00 00 FE FF` |
| UTF-32 LE | `FF FE 00 00` |

UTF-8 has no byte-order ambiguity, but some Windows applications (including some Excel workflows) add a BOM as a signal.

```python
with open("excel_export.csv", "r", encoding="utf-8-sig") as f:
    text = f.read()
```

`utf-8-sig` reads ordinary UTF-8 and strips a leading UTF-8 BOM if present. Plain `utf-8` leaves it as U+FEFF at the start, potentially contaminating the first CSV header. Writing with `utf-8-sig` adds the BOM. Use it only when the downstream consumer specifically benefits from it.

## 11. `open()` encoding and errors

Always specify `encoding=` explicitly for text files:

```python
with open("data.txt", "r", encoding="utf-8") as f:
    text = f.read()
```

If omitted, Python uses a platform/configuration-dependent default. The same program may behave differently on a developer machine and a server. Python versions before 3.15 generally use the locale encoding unless UTF-8 mode is active; Python 3.15+ defaults to UTF-8 mode unless disabled (PEP 686). Even with UTF-8 mode, explicit `encoding="utf-8"` documents the data contract and is the portable habit.

`open(..., errors=...)` applies the same error policy as `.decode()` during text reads. `strict` is the default. `ignore` can silently discard invalid bytes throughout the file.

## 12. Newline fundamentals: LF, CR, CRLF

A newline/line terminator marks a boundary between lines:
- **LF** is `\n` (line feed).
- **CR** is `\r` (carriage return).
- **CRLF** is `\r\n` (CR followed by LF).

Historically, CR returned a teleprinter carriage to the start of the line, and LF advanced to the next line. Some systems adopted both; others use LF alone.

Today Linux and modern macOS conventionally use LF; Windows conventionally uses CRLF; classic pre-OS-X Macintosh used CR. WSL2's native Linux filesystem uses LF, but files under `/mnt/c/...` or edited with Windows tools may use CRLF.

## 13. `open(newline=...)` and universal newlines

`newline=` controls line-ending recognition and translation; it is separate from `encoding=`.

| `newline=` | Reading | Writing |
|---|---|---|
| `None` (default) | Recognizes LF, CR, CRLF and translates all to `\n` | Translates written `\n` to platform-native ending |
| `""` | Recognizes all three but returns original endings unchanged | Writes `\n` unchanged |
| `"\n"`, `"\r"`, or `"\r\n"` | Recognizes only that exact ending; no translation | Translates written `\n` to that chosen ending |

`newline=None` is universal-newline mode. It makes normal text processing portable by normalizing line endings on read and writing platform-native endings on output.

`newline=""` disables translation but still recognizes line boundaries. It is essential for CSV because the `csv` module must manage its own line endings, including embedded newlines inside quoted fields. `csv.writer` defaults to CRLF regardless of platform; if Python's text layer also translates newlines, doubled endings can result. Therefore CSV files use `newline=""`.

JSON does not need `newline=""`: literal control characters inside JSON strings are escaped as `\n` in the JSON text, and normal text-mode universal-newline handling is appropriate. Pretty-printed JSON's `\n` text is translated to the platform convention on write and normalized on read.

## 14. Text mode vs. binary mode

Text mode reads/writes `str` and applies decoding/encoding and newline handling. Binary mode reads/writes `bytes` and does not decode, encode, or translate newlines. `encoding=`, `errors=`, and `newline=` are text-mode concepts and must not be used with binary mode.

Use binary mode when inspecting raw bytes, detecting BOMs, copying exact content, handling images or other binary formats, or preserving exact original newline bytes. Use text mode when you want decoded text.

## 15. `splitlines()` and preserving exact line endings

```python
text = "one\r\ntwo\nthree\rfour"
print(text.splitlines())
# ['one', 'two', 'three', 'four']
```

`splitlines()` recognizes LF, CR, CRLF and additional Unicode line/paragraph separators. It is more newline-aware than `text.split("\n")`.

```python
text.splitlines(keepends=True)
```

`keepends=True` retains each original line terminator. To reconstruct exact text read without newline translation:

```python
with open("source.txt", "r", encoding="utf-8", newline="") as f:
    text = f.read()
lines = text.splitlines(keepends=True)
assert "".join(lines) == text
```

This matters for exact file transformations, patching, source code, configuration, and protocols.

## 16. Standard streams, locale, UTF-8 mode, filesystem encoding

`sys.stdin`, `sys.stdout`, and `sys.stderr` are text streams with their own `.encoding`. Terminal encoding comes from the environment/terminal/locale or Python UTF-8 mode, not from the encoding you specify for a separate file. A UTF-8 file can be read correctly but fail when printed to a terminal that cannot represent a character.

`locale.getpreferredencoding(False)` reports the locale-associated preferred encoding. `locale.getencoding()` (Python 3.11+) reports the current locale encoding itself. `sys.flags.utf8_mode` reports whether UTF-8 mode is active; `PYTHONUTF8=1` or `python -X utf8` can enable it.

**Filesystem encoding** is for filenames and paths. **File-content encoding** is for bytes inside a file. `sys.getfilesystemencoding()` tells you about filenames, not the content encoding to pass to `open()`. Python uses `surrogateescape` internally to preserve filenames containing bytes that do not decode normally under the filesystem encoding.

With `pathlib`, content encoding remains explicit:

```python
from pathlib import Path

text = Path("notes.txt").read_text(encoding="utf-8")
Path("notes.txt").write_text("Hello", encoding="utf-8")
with Path("notes.txt").open("r", encoding="utf-8") as f:
    text = f.read()
```

## 17. Data engineering, network, database, and AI/ML applications

Network data arrives as bytes and must be decoded according to protocol metadata. HTTP `Content-Type` may declare `charset=utf-8`. Database drivers also decode text according to the database's configured character set. The important engineering question is where bytes become text and what contract governs that boundary.

A robust ingestion flow is:

```text
source bytes → decode using known encoding → validate text
→ transform → encode (usually UTF-8) → output
```

Examples include legacy CSV exports using Windows-1252, multilingual customer records, Excel BOM-prefixed files, logs from multiple systems, object-storage data, and ETL batch jobs. Encoding failures should be reported/quarantined rather than silently discarded.

In AI/ML, encoding matters for training corpora, prompts, documents for RAG, annotations, multilingual datasets, tokenization/embeddings, evaluation datasets, generated text, and JSON/CSV metadata. Mojibake can silently corrupt training or evaluation examples and lead to degraded model quality that is difficult to trace. Correct decoding must happen before tokenization or embedding.

## 18. Unicode normalization

Two strings can look identical but have different code-point sequences:

```python
a = "é"       # one precomposed code point
b = "é"      # e + combining acute accent
print(a == b) # False
```

Normalize when comparing, searching, deduplicating, or using text as a key:

```python
import unicodedata
a_norm = unicodedata.normalize("NFC", a)
b_norm = unicodedata.normalize("NFC", b)
print(a_norm == b_norm)   # True
```

Four forms:
- **NFC:** canonical composition; combines base plus combining marks where possible. Common general-purpose choice.
- **NFD:** canonical decomposition.
- **NFKC:** compatibility composition; also folds some compatibility variants and may discard stylistic distinctions.
- **NFKD:** compatibility decomposition.

Normalization is a deliberate policy, not an unconditional cleaning step. NFKC/NFKD can remove meaningful distinctions.

## 19. Grapheme clusters, confusables, and invisible characters

A grapheme cluster is what a user perceives as one visual character, and may consist of several code points. A family emoji can contain several emoji plus zero-width joiners; `len(text)` counts code points, not visible glyphs. Thus code-point count, byte count, and user-perceived character count can all differ. Naive slicing can split a combined accent or emoji sequence; true grapheme-aware segmentation requires specialized tooling beyond this lesson.

Unicode security/data-quality risks include:
- **Confusables:** visually similar characters from different scripts (e.g. Latin `a` vs Cyrillic `а`) can spoof identifiers.
- **Invisible characters:** zero-width spaces/joiners or formatting controls can make apparently identical strings compare differently.
- **Non-breaking spaces:** visually similar to normal spaces but different code points.
- **Control characters:** can affect display, matching, and downstream processing.

Normalization is not validation. Valid, normalized text can still be malicious or invalid for an application. Do not silently erase unexpected characters.

## 20. Debugging encoding and newline problems

Encoding workflow:
1. Inspect raw bytes.
2. Use `repr()` on bytes and decoded text.
3. Establish source encoding from documentation, producer, metadata, protocol, or BOM.
4. Test decoding explicitly.
5. Inspect `.start`, `.end`, `.reason` and failing byte position.
6. Check for BOM.
7. Inspect newline style separately.
8. Compare platform behavior.
9. Inspect source metadata/docs.
10. Reproduce with a minimal file.

```python
from pathlib import Path
data = Path("mystery.txt").read_bytes()
print(repr(data[:100]))
```

`repr()` can expose UTF-8 byte sequences such as `\xc3\xa9` and CRLF markers `\r\n` before decoding. Decode only after making an evidence-based decision.

For newline debugging, read with `newline=""` to preserve original endings:

```python
with open("suspicious.txt", "r", encoding="utf-8", newline="") as f:
    text = f.read()
print(repr(text))
for line in text.splitlines(keepends=True):
    print(repr(line))
```

This reveals mixed CRLF and LF endings. Common symptoms: blank lines from doubled endings, missing endings, mixed endings, stray `\r`, or different Windows/Linux behavior.

Common mistakes include assuming all files are UTF-8; omitting `encoding`; decoding with the wrong codec; double-encoding; calling `.decode()` on `str`; mixing `str` and `bytes`; casual `errors="ignore"`; blanket exception swallowing; scrubbing symptoms with `.replace()` instead of fixing root cause; confusing Unicode with UTF-8; confusing code points with bytes; assuming `len(str)` is byte length or visible-character count; ignoring BOM; assuming newline is always `\n`; and manually replacing CRLF without considering content.

## 21. End-to-end examples from the lesson

**Multilingual Text File Inspector:** read raw bytes, report size, detect BOM, choose an encoding only from BOM or caller-supplied information, decode strictly, report newline style, and list sample non-ASCII characters with code point and Unicode name (`unicodedata.name`). It inspects rather than modifies the source.

**Robust Text Ingestion Pipeline:** an `IngestResult` dataclass records source path, encoding, lines processed, and normalization status. `decide_encoding()` prefers a UTF-8 BOM, otherwise requires a caller-declared encoding and refuses to guess. `ingest_text_file()` reads bytes, decodes strictly, rejects empty content, optionally NFC-normalizes, processes lines, writes deterministic UTF-8 LF output with `newline=""`, reads output bytes back, verifies no CR remains and verifies content, then returns metrics. This worked example reads the whole file; the mini-project asks you to improve it to streaming for large files.

## 22. Testing, round trips, invariants, and performance

Use pytest's `tmp_path` for isolated tests:
- ASCII and multilingual UTF-8.
- BOM stripping (`utf-8-sig`) vs plain UTF-8 retaining U+FEFF.
- Invalid UTF-8 raises `UnicodeDecodeError`.
- Latin-1 decodes every byte.
- Universal newlines normalize CRLF/CR/LF to `\n`.
- `newline=""` preserves original endings.
- NFC makes canonical-equivalent strings equal.

Round-trip invariant:

```python
original = "Hello বাংলা こんにちは 🙂"
assert original.encode("utf-8").decode("utf-8") == original
```

Lossy error handlers and normalization intentionally change representation; tests should assert the documented substitution/normalized form rather than incorrectly expecting the original representation.

Performance: encoding/decoding cost grows with data size. `f.read()` holds the entire decoded string in memory; `for line in f:` decodes incrementally and is preferable for large files. Avoid repeated encode/decode conversions. File buffering and text decoding are separate layers.

## 23. API reference and production principles

Important APIs:
- `str.encode()` / `bytes.decode()`: convert `str` and `bytes`.
- `open()`: `mode`, `encoding`, `errors`, `newline`; text-only settings do not apply in binary mode.
- `str.splitlines(keepends=False)`.
- `ord()` / `chr()`.
- `unicodedata.normalize()`, `.name()`, `.category()`, `.bidirectional()`, `.combining()`.
- `locale.getpreferredencoding()`, `locale.getencoding()`.
- `sys.getfilesystemencoding()`, standard-stream `.encoding`, `sys.flags.utf8_mode`.

Production principles:
1. Know and document each source's encoding/newline data contract.
2. Specify `encoding=` at every text file boundary.
3. Do not silently discard invalid data.
4. Validate decoded text beyond successful decoding.
5. Preserve raw source bytes when audit/recovery matters.
6. Track whether values are `str` or `bytes`.
7. Choose newline policy deliberately; CSV uses `newline=""`.
8. Test multilingual data and platform behavior.
9. Document assumptions and monitor ingestion failures.
10. Avoid unnecessary conversions.

## 24. Four mini-project specifications

1. **Text Encoding Inspector:** inspect raw bytes and size; detect BOM; decode using BOM or explicit caller encoding; report newline style and code-point/name samples; test empty, ASCII-only, multilingual, and undecodable files.
2. **Multilingual Text Converter:** read a specified source encoding strictly; optionally normalize; write UTF-8; preserve original line endings or deliberately normalize to LF; test Latin-1/Windows-1252, UTF-8, BOM, and decode failures.
3. **Cross-Platform Text Normalizer:** detect LF/CRLF/CR including mixed files; normalize to one selected convention (e.g. LF); read with `newline=""`; produce deterministic output; test empty/no-newline/already-normalized/mixed input and WSL2 sources.
4. **Robust Text Ingestion Pipeline:** explicit source encoding policy with BOM override; strict decoding; explicit newline and optional normalization policy; streaming line processing; distinct decode/content-validation errors; UTF-8 output; tests for ASCII, multilingual, legacy, BOM, mixed endings, invalid input, large input, and caller configuration. Never guess an unknown encoding internally.

---

# Part B — Roadmap and current learning-level review

## 1. Stage 1 project tree and roadmap position

The roadmap records Stage 1 — **Programming & Computational Thinking** — as 24 modules, 212 numbered lessons, 282 files, and four stage-level projects. The 24 modules are:

1. Computational Thinking and Program Design.
2. Python Core Language and Data Types.
3. Control Flow, Functions, Scope, and Errors.
4. Problem-Solving, Collections, and Algorithmic Habits.
5. Text Files, Structured Data, and CLI Programs.
6. Modules, Packages, Dependencies, and Code Quality.
7. Testing and Systematic Debugging.
8. Object-Oriented Design, Data Modelling, and Functional Style.
9. Advanced Production-Oriented Python Foundations.
10. Production Habits for Python Programs.
11. Advanced Python Data Model and Object Design.
12. Metaprogramming and Dynamic Python.
13. Standard Library Toolkit.
14. Bytes, Binary Data, and Advanced Text Processing.
15. Modern Python Language Features.
16. Advanced Testing and Test Architecture.
17. Profiling, Memory, and Runtime Performance.
18. Packaging, Distribution, and Publishing.
19. CPython Internals and Runtime Behaviour.
20. Design Patterns and Library API Design.
21. Data Visualization and Notebook Workflows.
22. Secure Python Coding.
23. Code Reading, Refactoring, and Code Review.
24. Functions and OOP Gap Lessons.

Module 05 sequence:
1. Reading and Writing Text Files — completed.
2. `pathlib` and Portable Paths — completed.
3. CSV Files — completed.
4. JSON and Serialization — completed.
5. **Encodings and Newlines — current lesson.**
6. `argparse`.
7. Standard Streams and Exit Codes.
8. Logging vs. Print.
9. Environment Configuration and Input Validation.
10. Module README/practice questions.

The Stage 1 overview includes four projects:

- **Personal Expense Ledger CLI** — foundational command-line expense application.
- **Log Investigation and Reliability CLI** — inspect operational logs and reliability signals.
- **Data Quality and Transformation Pipeline** — `orders.csv`, `dqpipe` package (`cli.py`, `config.py`, `pipeline.py`, `rules.py`), tests, `config.toml`, and `data-contract.md`.
- **Rule-Based Risk Review Engine** — `transactions.csv`, `rules.toml`, `riskreview` package (`cli.py`, `engine.py`, `io.py`, `models.py`, `rules.py`), tests, and golden JSONL decisions.

## 2. Your current level and prerequisites

Your recorded level is **beginner progressing toward intermediate**. You have covered Python fundamentals, conditionals, loops, functions, parameters/defaults/docstrings, scope, pure functions and side effects, exceptions/validation, collections, data structures, comprehensions, Big-O, recursion, parsing/regex, text-file I/O, `pathlib`, CSV, and JSON.

That is enough foundation for this lesson. The solutions use standard-library `str`, `bytes`, `bytearray`, `Path`, `open()`, `unicodedata`, `locale`, `sys`, functions, loops, exceptions, and the basic pytest/`tmp_path` patterns used in earlier lessons.

**Scope discipline:** no pandas, NumPy, Spark, database drivers, web frameworks, third-party encoding detectors, or advanced networking. The lesson mentions these domains for context only. Solutions use standard-library techniques and keep the source encoding explicit rather than guessing.

## 3. Why this lesson matters to your projects

- The **Data Quality and Transformation Pipeline** must ingest CSVs reliably, including multilingual values, BOM-prefixed exports, legacy encodings, and line-ending variations. A wrong decode can corrupt customer/order fields before validation.
- The **Risk Review Engine** must not silently alter identifiers or transaction text; explicit encoding and normalization policy protects comparisons and auditability.
- The **Log Investigation CLI** must tolerate logs from different systems and platforms; `repr()`, newline inspection, and strict error reporting help diagnose source issues.
- The **Expense Ledger CLI** benefits from portable UTF-8 text storage and predictable line handling.

The immediate goal is to understand text/bytes boundaries and make encoding/newline assumptions explicit—not to introduce a full ETL framework yet.

---

# Part C — All 23 coding exercises solved

## Level 1 — Foundation

### 1. Print `str` and `bytes` types

```python
text = "hello"
data = b"hello"
print(type(text), type(data))
```

`text` is Unicode `str`; `data` is raw immutable `bytes`. They may display similarly but are different types.

### 2. Encode ASCII

```python
text = "Data"
encoded = text.encode("ascii")
print(encoded)
```

All characters are in ASCII's range, so encoding succeeds and returns bytes.

### 3. Encode non-ASCII with UTF-8

```python
text = "café বাংলা"
encoded = text.encode("utf-8")
print(encoded)
```

UTF-8 represents the accented and Bengali characters using multiple bytes where needed.

### 4. Decode UTF-8 bytes

```python
data = "café".encode("utf-8")
text = data.decode("utf-8")
print(text)
```

The same codec reverses the conversion, reconstructing the original string.

### 5. Confirm `ord()` and `chr()` are inverses

```python
for character in ("A", "é", "ব"):
    code_point = ord(character)
    recovered = chr(code_point)
    print(character, code_point, recovered == character)
```

For each single character, `ord()` gets its integer identity and `chr()` reconstructs it. The final value should be `True`.

### 6. Compare character count and byte count

```python
text = "café"
print(len(text))                  # 4 code points
print(len(text.encode("utf-8")))  # 5 bytes
```

`len(str)` counts code points. UTF-8 needs two bytes for `é`, so byte length is larger.

## Level 2 — Practical

### 7. Detect a UTF-8 BOM

```python
def has_utf8_bom(data: bytes) -> bool:
    return data.startswith(b"\xef\xbb\xbf")

print(has_utf8_bom(b"\xef\xbb\xbfhello"))  # True
print(has_utf8_bom(b"hello"))              # False
```

The function accepts bytes and checks their first three values against the UTF-8 BOM.

### 8. Read UTF-8 text

```python
from pathlib import Path

path = Path("utf8.txt")
text = path.read_text(encoding="utf-8")
print(text)
```

`read_text()` opens and decodes the file using the explicit encoding. The file must actually contain valid UTF-8.

### 9. Create and read a Latin-1 file

```python
from pathlib import Path

path = Path("latin1.txt")
path.write_bytes("café".encode("latin-1"))

text = path.read_text(encoding="latin-1")
print(text)
```

First create bytes using Latin-1. Then decode those same bytes using Latin-1. This is a controlled test, not an encoding-detection strategy.

### 10. Trigger and inspect `UnicodeDecodeError`

```python
data = "café".encode("utf-8")

try:
    data.decode("ascii")
except UnicodeDecodeError as error:
    print(error.start)
    print(error.end)
    print(error.reason)
```

UTF-8 bytes for `é` are invalid as ASCII. The exception attributes identify the failing byte range and reason.

### 11. Normalize file newlines explicitly

```python
from pathlib import Path

def normalize_newlines(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as f:
        original = f.read()
    return original.replace("\r\n", "\n").replace("\r", "\n")
```

`newline=""` preserves original endings. Replace CRLF first so it becomes one LF, then replace any remaining bare CR. Return normalized text; this function does not overwrite the source file.

### 12. Split mixed newline text

```python
text = "one\n two\rthree\r\nfour"
lines = text.splitlines()
print(lines)
```

`splitlines()` recognizes LF, CR, and CRLF. The result contains the four logical lines without terminators.

## Level 3 — Engineering

### 13. Validate UTF-8 bytes without raising to the caller

```python
def is_valid_utf8(data: bytes) -> bool:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True
```

Attempt strict decoding. Return `False` only for invalid UTF-8; return `True` if decoding succeeds. Other programming errors are not hidden.

### 14. Inspect newline styles in raw bytes

```python
from pathlib import Path

def detect_newline_styles(path: Path) -> set[str]:
    data = path.read_bytes()
    styles = set()

    if b"\r\n" in data:
        styles.add("CRLF")
    without_crlf = data.replace(b"\r\n", b"")
    if b"\n" in without_crlf:
        styles.add("LF")
    if b"\r" in without_crlf:
        styles.add("CR")

    return styles
```

Read bytes to avoid newline translation. Detect CRLF first, remove those pairs from a temporary copy, then identify remaining LF and CR. A set can report mixed styles.

### 15. Report character and byte counts

```python
from pathlib import Path

def report_text_sizes(path: Path, encoding: str) -> tuple[int, int]:
    text = path.read_text(encoding=encoding)
    character_count = len(text)
    byte_count = len(text.encode(encoding))
    return character_count, byte_count
```

Read using the caller's declared encoding. Count code points and re-encoded bytes separately; multilingual characters may need multiple bytes.

### 16. Write NFC-normalized UTF-8 and test

```python
import unicodedata
from pathlib import Path

def write_nfc(path: Path, text: str) -> None:
    normalized = unicodedata.normalize("NFC", text)
    path.write_text(normalized, encoding="utf-8")

def test_write_nfc(tmp_path):
    path = tmp_path / "normalized.txt"
    write_nfc(path, "e\u0301")
    result = path.read_text(encoding="utf-8")
    assert result == unicodedata.normalize("NFC", result)
```

Normalize before writing. The test supplies decomposed `e` plus combining accent and confirms the stored output is NFC.

### 17. Test strict encoding and decoding errors

```python
import pytest

def test_ascii_encode_is_strict():
    with pytest.raises(UnicodeEncodeError):
        "é".encode("ascii")

def test_utf8_decode_is_strict():
    with pytest.raises(UnicodeDecodeError):
        b"\xff".decode("utf-8")
```

Both operations use `strict` by default. `pytest.raises` proves the expected, specific exception occurs.

## Level 4 — Advanced

### 18. Explicitly selected source encodings

```python
def decode_source(data: bytes, encoding: str) -> str:
    if encoding not in {"utf-8", "latin-1"}:
        raise ValueError("Supported encodings: utf-8, latin-1")
    return data.decode(encoding, errors="strict")
```

The caller chooses the encoding. The function refuses unsupported names and decodes strictly. It does not guess based on trial and error.

### 19. Make normalization optional

```python
import unicodedata

def process_text(data: bytes, encoding: str, *, normalize: bool = False) -> str:
    text = decode_source(data, encoding)
    if normalize:
        text = unicodedata.normalize("NFC", text)
    return text

def test_normalization_is_optional():
    decomposed = "e\u0301".encode("utf-8")
    unchanged = process_text(decomposed, "utf-8")
    normalized = process_text(decomposed, "utf-8", normalize=True)
    assert unchanged != normalized
    assert normalized == unicodedata.normalize("NFC", unchanged)
```

The default preserves original code points. Passing `normalize=True` applies NFC. The test proves both modes work and differ intentionally.

### 20. Preserve original bytes alongside processed output

```python
from pathlib import Path

def preserve_and_convert(source: Path, landing: Path, output: Path,
                          encoding: str) -> str:
    raw = source.read_bytes()
    landing.write_bytes(raw)                 # exact original bytes
    text = raw.decode(encoding, errors="strict")
    output.write_text(text, encoding="utf-8")
    return text
```

Copy the original bytes to a landing-zone file before decoding. Then decode strictly and write UTF-8 output. If decoding fails, the original is still preserved.

### 21. Stream line-by-line and test a large file

```python
from pathlib import Path

def stream_copy(source: Path, target: Path, encoding: str) -> int:
    count = 0
    with source.open("r", encoding=encoding, newline=None) as src, \
         target.open("w", encoding="utf-8", newline="") as dst:
        for line in src:
            dst.write(line)
            count += 1
    return count

def test_stream_copy_large_file(tmp_path):
    source = tmp_path / "large.txt"
    target = tmp_path / "copy.txt"
    source.write_text("বাংলা line\n" * 10000, encoding="utf-8")
    assert stream_copy(source, target, "utf-8") == 10000
    assert target.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")
```

Iterate the input file rather than calling `.read()`. The source is decoded incrementally. Output is explicitly UTF-8 with LF characters passed through unchanged because `newline=""`.

### 22. Distinguish three failure categories

```python
class DecodeFailure(Exception):
    pass

class EmptyContentError(Exception):
    pass

class ContentValidationError(Exception):
    pass

def ingest_bytes(data: bytes, encoding: str) -> str:
    try:
        text = data.decode(encoding, errors="strict")
    except UnicodeDecodeError as error:
        raise DecodeFailure("Could not decode source bytes") from error

    if not text.strip():
        raise EmptyContentError("Input contains no non-whitespace text")

    if "REQUIRED" not in text:
        raise ContentValidationError("Required marker is missing")

    return text
```

First classify codec failure. Then reject empty/whitespace-only content. Finally apply a downstream content rule. Each failure has a distinct exception and preserved cause where relevant.

### 23. Cross-platform newline test

```python
def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")

def test_newline_inputs_produce_same_output():
    expected = "one\ntwo\nthree"
    assert normalize_text("one\ntwo\nthree") == expected
    assert normalize_text("one\r\ntwo\r\nthree") == expected
    assert normalize_text("one\rtwo\rthree") == expected
    assert normalize_text("one\r\ntwo\rthree\n") == expected + "\n"
```

The pure function normalizes all standard conventions. The test checks LF, CRLF, CR, and mixed endings. In a file-level test, read with `newline=""` so the original line endings remain available to the function.

---

# Part D — All 10 debugging exercises

1. **UTF-8 decoded as ASCII:** `é` begins at byte position 3 in `b"caf\xc3\xa9"`; ASCII cannot decode `0xC3`. Use `.decode("utf-8")`.
2. **UTF-8 decoded as Windows-1252:** it may not raise; it produces mojibake such as `cafÃ©`. Decode with UTF-8 because that is how the bytes were encoded.
3. **Latin-1 decoded as UTF-8:** byte `0xE9` alone is not a complete valid UTF-8 sequence. Decode with Latin-1, matching the producer.
4. **Mixed endings with `.split("\n")`:** CRLF leaves `\r` attached, and bare CR is not split. Use `.splitlines()` or universal newline reading.
5. **Missing `encoding=`:** code relies on environment-dependent defaults. Specify the source's known encoding explicitly.
6. **`errors="ignore"`:** invalid bytes disappear silently. Use strict decoding and handle `UnicodeDecodeError` deliberately.
7. **Mixing `str` and `bytes`:** direct concatenation raises `TypeError`. Convert one side explicitly, e.g. `header + message.encode("utf-8")`.
8. **BOM not handled:** decoded text begins with invisible U+FEFF, so `startswith("header")` is false. Read with `encoding="utf-8-sig"`.
9. **Unwanted BOM on output:** `utf-8-sig` writes a BOM. Use plain UTF-8 unless the downstream consumer specifically needs one.
10. **Unicode normalization ignored:** visually identical precomposed/decomposed names compare unequal. Normalize both with NFC before storing/comparing, if that is the documented identifier policy.

---

# Part E — All 25 interview questions

## Beginner

1. **Unicode:** a universal character repertoire assigning code points to characters.
2. **Code point:** the numeric Unicode identity of a character, written like U+0041.
3. **Encoding/decoding:** converting Unicode text to bytes and bytes back to text.
4. **Unicode vs UTF-8:** Unicode defines characters/code points; UTF-8 encodes code points as bytes.
5. **ASCII vs UTF-8:** UTF-8 preserves every ASCII character's exact one-byte representation.
6. **Variable-width UTF-8:** a code point uses one to four bytes depending on its range.

## Intermediate

7. **BOM:** a byte marker at the beginning of a file indicating encoding and/or byte order.
8. **`utf-8-sig`:** UTF-8 codec that strips a leading BOM on read and writes one on output.
9. **`UnicodeDecodeError`:** invalid byte sequence for the chosen codec; exposes position and reason.
10. **`UnicodeEncodeError`:** text contains a character the selected codec cannot represent.
11. **Mojibake:** wrong decoding produces corrupted text, sometimes without an exception.
12. **Newline translation:** recognizing line terminators and normalizing them for portable text processing.
13. **LF/CR/CRLF:** line feed, carriage return, and the combined sequence; inherited from historical terminal mechanics.
14. **CSV `newline=""`:** prevents Python's separate newline translation from interfering with CSV's own reader/writer handling.
15. **`str` vs `bytes`:** Unicode text vs immutable raw byte sequence.
16. **`bytes` vs `bytearray`:** immutable vs mutable byte sequence.
17. **`errors="ignore"`:** silently drops invalid/unrepresentable data; dangerous because it hides data loss.

## Advanced / production

18. **UTF-8 mode:** Python mode making defaults UTF-8 to reduce locale-dependent behavior; can be enabled with environment/CLI options.
19. **Filesystem vs content encoding:** filename/path bytes vs bytes stored inside a file; separate mechanisms.
20. **Unicode normalization:** canonical/compatibility transformation so equivalent code-point sequences can compare consistently.
21. **Unknown encoding debugging:** gather source metadata, producer docs, BOM, protocol rules, raw-byte samples, and validate decoded content; do not guess.
22. **Multilingual ingestion:** inspect bytes, decide encoding from evidence, decode strictly, validate, process/normalize under policy, write UTF-8, test and report failures.

## Scenario-based

23. **Windows teammate sees good text, Linux sees corruption:** likely encoding mismatch/default or newline convention difference. Inspect raw bytes and `repr()`, identify BOM/producer metadata, compare explicit decoding and newline-preserving reads.
24. **Legacy CSV fails UTF-8:** investigate producer application/version, export settings, documentation, metadata, sample byte patterns, BOM, and expected field content before selecting Windows-1252/Latin-1 or another codec.
25. **“Use ignore everywhere”:** reject this as a default because it silently destroys data. Use strict decoding, capture diagnostics, quarantine failures, and add an explicitly documented fallback only when the business contract permits it.

---

# Part F — All 11 knowledge-check answers

1. Unicode assigns character identities/code points; UTF-8 is one encoding that maps those code points to bytes.
2. Some codecs (especially Latin-1) accept every byte; wrong decoding can succeed while producing mojibake.
3. `len("café")` prints `4`; UTF-8 byte length prints `5` because `é` uses two bytes.
4. UTF-8 with `replace` prints `café`; ASCII with `replace` prints `caf��` because the two non-ASCII bytes are replaced.
5. `bytes` indexing returns the numeric value of one byte as an integer; slicing returns `bytes`.
6. Latin-1 represents U+00E9, while ASCII only represents U+0000–U+007F.
7. `newline=None` recognizes CR/LF/CRLF and translates all to `\n`; `newline=""` recognizes them but preserves the original characters.
8. `EF BB BF` is a UTF-8 BOM; use `encoding="utf-8-sig"` to strip it.
9. The strings can contain canonically equivalent but different code-point sequences; NFC maps them to the same canonical representation.
10. `csv.writer` uses its own CRLF line terminator independent of platform; `newline=""` prevents Python's text layer from double-translating it.
11. `strict` exposes the error and lets the pipeline log/quarantine/investigate it. `ignore` silently deletes bytes and can produce incomplete, plausible-looking output.

---

# Part G — Four mini-project implementation plans

1. **Text Encoding Inspector:** independent BOM detection, raw-byte size, caller/BOM-based decode, newline-style report, Unicode code-point/name report, and tests for empty, ASCII, multilingual, and invalid files.
2. **Multilingual Text Converter:** caller-specified strict source decode, optional normalization, UTF-8 output, and explicit decision to preserve exact line endings or normalize to LF.
3. **Cross-Platform Text Normalizer:** read with `newline=""`, detect mixed endings, normalize to a chosen convention, and verify deterministic output on LF/CRLF/CR/WSL2 files.
4. **Robust Text Ingestion Pipeline:** explicit encoding policy, BOM override, strict decode, optional normalization, streaming processing, separate decode/content errors, UTF-8 output, and tests for legacy/BOM/multilingual/mixed/invalid/large files.

---

# Part H — Production and mastery checklist

- [ ] Distinguish characters, Unicode code points, encoded bytes, `str`, and `bytes`.
- [ ] Explain ASCII, UTF-8, UTF-16, UTF-32, Latin-1, and Windows-1252.
- [ ] Use `ord()`, `chr()`, `.encode()`, and `.decode()`.
- [ ] Understand UTF-8's 1–4 byte patterns and self-synchronization.
- [ ] Read `UnicodeEncodeError` and `UnicodeDecodeError` diagnostics.
- [ ] Keep `errors="strict"` unless a documented policy says otherwise.
- [ ] Recognize mojibake and do not guess encodings from appearance alone.
- [ ] Detect/handle BOMs with `utf-8-sig` where appropriate.
- [ ] Specify `encoding=` for every text-file boundary.
- [ ] Explain LF, CR, CRLF and each `newline=` mode.
- [ ] Use `newline=""` for CSV; do not add it to JSON without a reason.
- [ ] Use binary mode for exact raw-byte inspection/copying.
- [ ] Use `splitlines()` and `keepends=True` correctly.
- [ ] Separate filesystem encoding from file-content encoding.
- [ ] Understand terminal encoding and Python UTF-8 mode.
- [ ] Normalize Unicode only under an explicit application policy.
- [ ] Recognize grapheme-cluster and Unicode confusable/invisible-character risks.
- [ ] Stream large text files instead of loading everything into memory.
- [ ] Preserve original bytes when audit/recovery requires it.
- [ ] Test multilingual content, BOMs, invalid bytes, mixed newlines, and cross-platform behavior.
- [ ] Monitor and report encoding failures; never silently discard source data.

**Next roadmap lesson:** `06-command-line-arguments-with-argparse.md`. Complete the exercises and be comfortable inspecting raw bytes, decoding with an evidence-based encoding, normalizing newlines, and testing the behavior before moving on.
