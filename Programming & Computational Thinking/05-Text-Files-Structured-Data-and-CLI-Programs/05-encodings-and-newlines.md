# Encodings and Newlines

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain, precisely, the difference between a character, Unicode text,
  and bytes — and why "use UTF-8" alone is not a sufficient mental
  model.
- Explain Unicode, code points, and why Unicode itself is not a byte
  encoding.
- Explain and use Python's `str` and `bytes` types correctly, including
  `bytearray`.
- Explain ASCII, UTF-8 (including its internal byte-pattern mechanics),
  UTF-16, UTF-32, and common legacy encodings (Latin-1, Windows-1252),
  and choose correctly among them.
- Use `str.encode()` and `bytes.decode()` correctly, including every
  standard error-handling mode (`strict`, `ignore`, `replace`,
  `backslashreplace`, `namereplace`, `surrogateescape`, `surrogatepass`).
- Diagnose and explain `UnicodeEncodeError`, `UnicodeDecodeError`, and
  mojibake.
- Explain BOMs and use `utf-8-sig` correctly.
- Use `open()`'s `encoding=`, `errors=`, and `newline=` parameters
  correctly, and explain Python's universal-newline behavior precisely.
- Explain `\n`, `\r`, and `\r\n`, and platform newline conventions,
  including WSL2-specific considerations.
- Distinguish text mode from binary mode, and explain why `encoding=`
  is a text-mode-only concept.
- Use `str.splitlines()` correctly, including `keepends=True`.
- Explain filesystem encoding vs. file-content encoding, standard
  stream encoding, and Python's UTF-8 mode.
- Integrate correct encoding/newline handling with CSV, JSON, and
  `pathlib`.
- Explain Unicode normalization (NFC/NFD/NFKC/NFKD) and grapheme-
  cluster limitations.
- Recognize Unicode-related security and data-quality risks
  (confusables, invisible characters, malformed input).
- Debug encoding and newline problems systematically.
- Test encoding/newline behavior with `pytest`.
- Design a production-safe, portable text-ingestion pipeline.

## 2. Why Encodings and Newlines Matter

Every file this module has taught you to work with —
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
plain text files, [03-csv-files.md](03-csv-files.md)'s CSV files, and
[04-json-and-serialization.md](04-json-and-serialization.md)'s JSON —
has quietly depended on the exact same two settings, repeated in nearly
every `open()` call across all three: `encoding="utf-8"` and, for CSV,
`newline=""`. This chapter is where those two settings — deferred,
deliberately, in every earlier file — finally get their complete,
first-principles treatment.

This matters more than it might first appear. **"Just use UTF-8"** is
genuinely good, correct, practical advice for nearly all new code you
write — but it is not, by itself, a sufficient *understanding*. It does
not explain what happens when you receive a file someone *else* wrote,
possibly years ago, possibly with a different encoding entirely. It
does not explain why a file that looks perfectly normal on one machine
prints as corrupted garbage on another. It does not explain why a CSV
file needs `newline=""` specifically, while a JSON file does not. This
chapter builds the actual mental model — character → code point →
encoding → bytes, and back — that makes all of that reasoning possible,
rather than leaving "just use UTF-8" as an instruction to follow
without knowing why.

This chapter continues the same boundary-validation discipline this
entire module has built:
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§3 established that external files are untrusted input — encoding
mismatches are one of the most common, and most silent, ways that
untrusted assumption goes wrong in practice, because a wrong encoding
does not always announce itself with an exception (§21 makes this
concrete): it can simply produce corrupted-looking, or subtly wrong,
text, with no error raised at all.

## 3. Text and Bytes Fundamentals

### 3.1 What a character is, and why this is harder than it sounds

A **character** is, informally, one unit of written language — a
letter, a digit, a punctuation mark, an emoji. Humans think in
characters. Computers, at the hardware level, only ever store and move
around **bytes** — small, fixed-size numeric units, with no inherent
meaning as "text" at all. Everything in this chapter exists to bridge
that gap.

### 3.2 A string is not automatically a universal thing

```
Hello
বাংলা
こんにちは
🙂
```

Each of these looks, to a human reader, like "some text." But **each
one has a different underlying byte representation**, depending on
which encoding is used to store it — and the visual similarity between
"text that displays correctly" hides a real, important question this
entire chapter answers: *which specific bytes represent this specific
text, under which specific rule?*

### 3.3 Why computers ultimately store and process bytes

A byte is the smallest addressable unit of computer memory and storage
— every file on disk, every message sent over a network, is,
physically, nothing but a sequence of bytes. There is no separate
"character storage" mechanism in computer hardware — text is always,
ultimately, bytes, interpreted according to some agreed-upon rule.
§9–§10 name that rule precisely: **encoding**.

### 3.4 The two-layer model this entire chapter is built on

```
CHARACTER
    ↓
UNICODE CODE POINT
    ↓
ENCODING
    ↓
BYTES
    ↓
FILE / NETWORK / STORAGE
```

and, in reverse:

```
BYTES
    ↓
DECODING
    ↓
UNICODE CODE POINT
    ↓
CHARACTER
    ↓
PYTHON str
```

Every section from here through §31 exists to make each individual
arrow in this diagram completely precise — what a character actually
*is*, computationally (§4–§5); what a code point is (§5); what encoding
and decoding actually do, mechanically (§9–§18); and what happens when
the two ends of this pipeline disagree (§20–§22).

## 4. Unicode

### 4.1 Why ASCII was insufficient

Early computing used **ASCII** (§9), a scheme covering only 128
characters — enough for unaccented English text, digits, and basic
punctuation, but nothing for accented letters (`é`), non-Latin scripts
(`বাংলা`, `中`, `こんにちは`), or symbols like emoji (`🙂`). As computing
became genuinely global, this was a real, practical limitation — many
incompatible, *ad hoc* encodings sprang up, each covering a different
region's characters, with **no shared way to represent a document
containing more than one language's characters at once**, and no
guarantee that a byte meaning one character under one such scheme meant
the same character under another.

### 4.2 Unicode as a universal character repertoire

**Unicode** was created to solve exactly this: a single, universal
standard assigning every character used in essentially every written
language — plus symbols, emoji, and more — its own unique, permanent
identity, called a **code point** (§5). Unicode's job is answering
"what is this character?", uniquely and unambiguously, for any
character from any of the world's writing systems, in one shared
system.

### 4.3 The critical distinction: Unicode is not itself a byte encoding

**This is the single most important conceptual distinction in this
entire chapter, and it is worth stating as plainly as possible:
Unicode defines *what characters exist and what number identifies
each one* — it does not, by itself, define how those numbers are
stored as bytes.** That second, separate question — "given this
character's Unicode identity, which actual bytes represent it on
disk?" — is answered by an **encoding** (§9), and there is more than
one valid answer (§11–§15 cover several). Confusing "Unicode" with "a
specific encoding" (most often, informally, with UTF-8) is an extremely
common source of imprecise thinking — this chapter deliberately keeps
the two concepts separate throughout.

## 5. Code Points

### 5.1 What a code point is

A **Unicode code point** is the unique number Unicode assigns to a
specific character (or, more precisely, a specific *identity* — some
code points represent combining marks, formatting instructions, or
other non-visible entities, not only what a human would call a
"letter"). Code points are conventionally written as `U+` followed by a
hexadecimal number, e.g. `U+0041` for the capital letter `A`. Unicode
code points range from `U+0000` to `U+10FFFF`.

### 5.2 `ord()` and `chr()`

```python
print(ord("A"))     # 65
print(hex(ord("A")))  # '0x41'  -- matching U+0041
print(chr(65))          # 'A'
print(chr(0x0041))       # 'A'  -- the same value, written in hex
```

`ord(character)` returns a single character's code point, as a plain
Python `int`. `chr(code_point)` does the reverse — given an integer
code point, it returns the one-character string it identifies.

### 5.3 Applying this to non-ASCII characters

```python
for character in "Aébà":
    print(character, hex(ord(character)))
```

```text
A 0x41
é 0xe9
b 0x62
à 0xe0
```

Every character, from every script, has a well-defined code point this
same way — `é` is `U+00E9`, exactly as precisely and unambiguously as
`A` is `U+0041`.

### 5.4 Three genuinely different concepts, named precisely

- **Character** — the informal, human-facing concept of "a letter, a
  digit, a symbol."
- **Code point** — Unicode's own precise, numeric identity for that
  character (`U+0041` for `A`).
- **Encoded bytes** — the actual bytes stored on disk or sent over a
  network, produced by applying a *specific encoding* (§9) to a code
  point — the same code point can produce *different* bytes under
  different encodings (§11 and §13 make this concrete for `é`
  specifically).

**Holding these three as distinct concepts — not synonyms for each
other — is the single most important habit this chapter builds.**

## 6. Python `str`

### 6.1 `str` represents Unicode text — not bytes

```python
text = "বাংলা"
print(type(text))
```

```text
<class 'str'>
```

In Python 3, **`str` is a sequence of Unicode characters** (more
precisely, of Unicode code points — §5) — it is fundamentally **not** a
raw sequence of bytes, and holds no inherent encoding of its own.
Indexing, slicing, and iterating a `str` operate on characters
(code points), not on the bytes any particular encoding might produce
from it.

### 6.2 Why this makes Unicode programming genuinely easier

Because a Python `str` is not tied to any particular byte encoding,
you can build, manipulate, compare, and reason about text — in any
mixture of scripts — entirely without thinking about bytes at all,
until the specific moment you need to write that text somewhere
external (a file, a network connection) — exactly the moment §9's
"encoding" step applies. Many older languages and systems conflated
"string" with "a specific byte encoding" directly, which made correctly
handling multiple languages' text in a single program genuinely
error-prone; Python 3's clean separation is a deliberate, meaningful
design improvement over that older approach.

### 6.3 A caveat: "one code point" is not always "one user-perceived character"

Python's `str` model is precise about code points — it is **not**
always precise about what a human would casually call "one character."
A single code point is not always what a person visually perceives as
one character; some visually-single characters are actually built from
*multiple* code points (an accented letter formed by combining a base
letter with a separate combining accent mark, for example, or certain
emoji). **§40 develops this "grapheme cluster" caveat fully** — it is
introduced here only so you do not walk away from this section assuming
Python's `str` model is a perfectly simple "one code point equals one
visible character" system in every case.

## 7. Python `bytes`

### 7.1 What `bytes` is

```python
data = b"hello"
print(type(data))
```

```text
<class 'bytes'>
```

`bytes` is an **immutable sequence of byte values** — each element is
an integer from `0` to `255` (inclusive), representing exactly one
byte. A `bytes` literal is written with a leading `b` before the
quotes, as shown.

### 7.2 Indexing and slicing

```python
data = b"hello"
print(data[0])        # 104
print(data[0:2])        # b'he'
```

```text
104
b'he'
```

**Indexing a single element of `bytes` returns a plain Python `int`**
— `104` is the numeric byte value corresponding to the ASCII character
`h` — **not** a one-character `bytes` object. This is a genuine,
frequently-confusing difference from indexing a `str` (where
`"hello"[0]` returns the one-character string `'h'`). **Slicing**
`bytes`, by contrast, *does* return another `bytes` object, exactly
mirroring `str` slicing behavior.

### 7.3 `str` and `bytes` are genuinely different, incompatible types

```python
"hello" + b"world"
```

```text
Traceback (most recent call last):
  ...
TypeError: can only concatenate str (not "bytes") to str
```

Python 3 deliberately **refuses** to silently mix `str` and `bytes`
together — attempting to concatenate, compare (beyond `==`, which
simply returns `False` rather than raising), or otherwise combine them
directly raises `TypeError`. This is a deliberate safety feature, not
an inconvenience: in earlier Python 2, `str` and byte data were far
more casually interchangeable, which made it easy to silently mix
encoded and unencoded data without noticing — a common source of subtle
bugs that Python 3's strict separation specifically prevents. **The
correct fix is never to work around this error by force — it is to
explicitly convert, deliberately, using `.encode()` or `.decode()`
(§18), choosing the specific encoding that conversion should use.**

## 8. `bytearray`

### 8.1 What it is, and how it differs from `bytes`

```python
data = bytearray(b"hello")
data[0] = 72   # ASCII for 'H'
print(data)
```

```text
bytearray(b'Hello')
```

`bytearray` is `bytes`' **mutable** counterpart — an ordinary,
in-place-modifiable sequence of byte values, otherwise behaving very
similarly (indexing returns an `int`, slicing returns another
`bytearray`, and it supports `.decode()` exactly like `bytes` does).

### 8.2 When it is useful

`bytearray` is genuinely useful specifically when you need to **build
up or modify raw byte data incrementally**, in place — for example,
assembling a byte buffer piece by piece before a single final
`.decode()`, or accumulating incoming binary data in a networking or
streaming context. For most everyday text-processing code in this
chapter's scope, plain, immutable `bytes` (produced by `.encode()`,
§18) is entirely sufficient — `bytearray` is included here for
completeness and recognition, at the encoding/decoding boundary
specifically, rather than as a technique this chapter builds deep
fluency in.

## 9. ASCII

### 9.1 What ASCII is, historically

**ASCII** (American Standard Code for Information Interchange) is a
7-bit character encoding, defined decades before Unicode, covering
exactly 128 characters (code points `0`–`127`): unaccented uppercase
and lowercase English letters, digits, common punctuation, and a
handful of control characters (§29 covers two of these — CR and LF —
specifically).

### 9.2 ASCII's limitations

128 characters is nowhere near enough to represent the world's writing
systems — no accented letters, no non-Latin scripts, no emoji, nothing
outside a narrow slice of English-language text. This limitation is
precisely §4.1's motivation for Unicode's creation.

### 9.3 ASCII's continued relevance: compatibility with UTF-8

```python
print("A".encode("ascii"))
```

```text
b'A'
```

```python
print("é".encode("ascii"))
```

```text
Traceback (most recent call last):
  ...
UnicodeEncodeError: 'ascii' codec can't encode character '\xe9' in position 0: ordinal not in range(128)
```

Every character encodable in ASCII produces the **exact same single
byte** under UTF-8 (§11) as it does under plain ASCII — this
intentional compatibility is a large part of why UTF-8 became so
widely adopted: existing ASCII text and tooling continues to work
correctly, unmodified, when reinterpreted as UTF-8. `"é"`, however, is
entirely outside ASCII's 128-character range, and attempting to encode
it as ASCII raises `UnicodeEncodeError` (§20) immediately.

## 10. Encoding and Decoding

### 10.1 Encoding, defined precisely

**Encoding** is the process of converting Unicode text (a Python `str`,
made of code points, §5) into a specific sequence of bytes, according
to a defined, named rule (an "encoding," in the sense of "which specific
scheme" — the same word is used for both the *process* and the *named
scheme*, which is worth noticing explicitly to avoid confusion).

```python
text = "Hello"
data = text.encode("utf-8")

print(text)
print(data)
```

```text
Hello
b'Hello'
```

### 10.2 Decoding, defined precisely

**Decoding** is the reverse: converting a specific sequence of bytes
back into Unicode text, using a specified encoding.

```python
data = b"Hello"
text = data.decode("utf-8")

print(text)
```

```text
Hello
```

### 10.3 The full round trip

```
text → encode → bytes → (file / network / storage) → bytes → decode → text
```

```python
original = "বাংলা"
encoded = original.encode("utf-8")
decoded = encoded.decode("utf-8")

print(original == decoded)
```

```text
True
```

### 10.4 The critical requirement: decoding must match encoding

**The encoding used to decode bytes back into text must match the
encoding originally used to produce those bytes** — unless the bytes
are otherwise, reliably identifiable as using a different one (a BOM,
§23–§24, is one, limited, mechanism for exactly this; explicit metadata
from the data's source, §22, is the more general and reliable one).
Decoding with the *wrong* encoding does not always raise an error —
sometimes it silently produces different, wrong text instead (§21
develops this precisely — this specific danger is exactly **mojibake**,
§21's own subject).

### 10.5 Why the same text can produce different bytes under different encodings

```python
text = "é"
print(text.encode("utf-8"))
print(text.encode("utf-16"))
print(text.encode("latin-1"))
```

```text
b'\xc3\xa9'
b'\xff\xfe\xe9\x00'
b'\xe9'
```

The **same** character, the **same** underlying Unicode code point
(`U+00E9`), produces **three genuinely different byte sequences**,
depending purely on which encoding is applied — exactly §4.3's
distinction, made fully concrete: Unicode identity is one thing;
encoded bytes are a separate, encoding-dependent thing.

## 11. UTF-8

### 11.1 What UTF-8 is, in plain terms

**UTF-8** is a **variable-width** encoding — each Unicode code point is
represented using **between 1 and 4 bytes**, depending on the code
point's numeric value. It is, by a wide margin, the dominant encoding
across the modern web, most operating systems, and most modern file
formats and protocols.

### 11.2 Why UTF-8 is so widely used

**ASCII compatibility** — every ASCII character encodes to exactly the
same single byte under UTF-8 (§9.3), meaning enormous amounts of
existing ASCII-only text and tooling work correctly, unmodified, under
UTF-8. **Full Unicode support** — unlike ASCII, UTF-8 can represent
*every* Unicode code point, without exception. **Space efficiency for
common text** — text that is mostly or entirely ASCII stays compact
(one byte per character), while still allowing any other script or
symbol to appear when actually needed, using more bytes only where
genuinely necessary. **Self-synchronizing byte structure** — §12
explains exactly how a UTF-8 parser can always tell where a character
boundary is, even starting from an arbitrary byte offset, a property
some other encodings lack.

### 11.3 Byte-length examples

```python
examples = ["A", "é", "বাংলা", "🙂"]

for text in examples:
    encoded = text.encode("utf-8")
    print(f"{text!r}: {len(text)} character(s), {len(encoded)} byte(s)")
```

```text
'A': 1 character(s), 1 byte(s)
'é': 1 character(s), 2 byte(s)
'বাংলা': 4 character(s), 12 byte(s)
'🙂': 1 character(s), 4 byte(s)
```

### 11.4 `len(text)` vs. `len(text.encode("utf-8"))` — why they differ

`len(text)` counts **Python `str` characters (code points, §5)**.
`len(text.encode("utf-8"))` counts **bytes**. For pure ASCII text,
these are always equal — but the moment any non-ASCII character
appears, they diverge, since UTF-8 uses *more than one byte* for those
characters (§11.3's table shows this directly). **This distinction
matters practically** whenever a system genuinely limits data by *byte*
size (a network payload limit, a database column's byte-length limit,
[03-csv-files.md](03-csv-files.md)'s §25 `field_size_limit`) — assuming
`len(text)` measures the same thing as the eventual byte size is a
concrete, common bug for any text containing non-ASCII characters.

## 12. UTF-8 Internal Mechanics

### 12.1 The four byte-pattern shapes

| Code point range | Byte pattern | Bytes used |
|---|---|---|
| `U+0000`–`U+007F` | `0xxxxxxx` | 1 |
| `U+0080`–`U+07FF` | `110xxxxx 10xxxxxx` | 2 |
| `U+0800`–`U+FFFF` | `1110xxxx 10xxxxxx 10xxxxxx` | 3 |
| `U+10000`–`U+10FFFF` | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` | 4 |

Each `x` represents one bit of the code point's actual numeric value,
spread across the available bit positions in the pattern.

### 12.2 What the leading bits actually communicate

The **first byte** of any UTF-8 character encodes, in its own leading
bits, exactly how many bytes the whole character occupies: a leading
`0` bit means "this is a complete, 1-byte character" (matching plain
ASCII exactly); a leading `110` means "2 bytes total"; `1110` means "3
bytes total"; `11110` means "4 bytes total." Every **continuation
byte** — every byte *after* the first, within a multi-byte character —
always begins with the fixed bit pattern `10`.

### 12.3 Why this specific design matters: self-synchronization

Because continuation bytes are always unambiguously marked (`10......`),
and the first byte of any character is always marked differently (never
starting with `10`), **a UTF-8 parser can always correctly identify a
character boundary, even if it starts reading from an arbitrary point
in the middle of a byte stream** — it simply looks backward or forward
until it finds a byte that is *not* a continuation byte. This
"self-synchronizing" property is a genuinely important, deliberate
design choice — it is part of why UTF-8 handles partial reads, byte-
stream corruption detection (§21), and random access into the *middle*
of a large text stream far more gracefully than some fixed-width or
less self-describing encodings.

### 12.4 A worked example: `é`, byte by byte

```python
data = "é".encode("utf-8")
print(" ".join(f"{byte:08b}" for byte in data))
```

```text
11000011 10101001
```

`é` is `U+00E9`, which falls in the `U+0080`–`U+07FF` range — a 2-byte
character. The first byte, `11000011`, begins with `110` (2-byte
marker); the second, `10101001`, begins with `10` (continuation byte)
— exactly matching §12.1's table.

## 13. UTF-16

### 13.1 What UTF-16 is

**UTF-16** represents each Unicode code point using one or two **16-bit
code units** — it is *not* simply "always two bytes per character," a
genuinely common oversimplification worth correcting directly. Code
points within the **Basic Multilingual Plane** (`U+0000`–`U+FFFF`,
excluding a reserved surrogate range) fit in exactly one 16-bit unit.
Code points *beyond* that range (`U+10000`–`U+10FFFF` — including many
emoji) require **two** 16-bit units together, called a **surrogate
pair**: a "high surrogate" followed by a "low surrogate," each drawn
from a specific, reserved code-point range set aside exclusively for
this purpose.

### 13.2 A Python example

```python
text = "A🙂"
print(text.encode("utf-16"))
print(text.encode("utf-16-le"))
```

```text
b'\xff\xfeA\x00\x00\x3d\x08\xde'
b'A\x00=\xd8\x08\xde'
```

(Exact byte values for the emoji's surrogate pair may render
differently depending on your terminal; the structural point —
`utf-16` including a BOM prefix that `utf-16-le` omits — is the one to
focus on.)

### 13.3 Why the plain `"utf-16"` output includes a BOM

`text.encode("utf-16")` (with no explicit byte-order suffix) picks the
**native byte order of the encoding machine** (§24 explains "byte
order" precisely) and **prepends a BOM** (§23) specifically so that
whatever later reads these bytes can determine which byte order was
actually used. `"utf-16-le"` and `"utf-16-be"` instead commit to a
*specific*, explicit byte order and, correspondingly, do **not**
include a BOM at all — the receiving system is expected to already
know the byte order out of band.

### 13.4 Common uses, and how it differs from UTF-8

UTF-16 remains genuinely significant internally within certain systems
and APIs (notably, it is the internal text representation many Windows
APIs and some programming environments, like Java and JavaScript, use)
— but it is **not** the dominant choice for files and network
interchange the way UTF-8 is: it is *not* ASCII-compatible at the byte
level (even plain English text is at least 2 bytes per character
under UTF-16, unlike UTF-8's 1), and its variable-length surrogate-pair
mechanism differs meaningfully from UTF-8's own variable-length scheme.

## 14. UTF-32

### 14.1 What UTF-32 is

**UTF-32** represents **every** Unicode code point using a **fixed** 4
bytes, with no exceptions and no surrogate-pair mechanism needed at
all — the simplest possible encoding scheme to reason about, at the
direct cost of using considerably more space for ordinary text.

```python
text = "A🙂"
print(text.encode("utf-32"))
print(len(text.encode("utf-32-le")))
```

```text
b'\xff\xfe\x00\x00A\x00\x00\x00=\xf6\x01\x00'
8
```

### 14.2 The trade-off

**Advantage:** because every code point occupies exactly the same
fixed size, certain operations (like jumping directly to the *N*th
character in a UTF-32 byte stream, by simple arithmetic) are trivially
simple compared to variable-width encodings. **Disadvantage:** for
ordinary text — especially ASCII-heavy text — UTF-32 uses roughly four
times the storage of UTF-8, a genuinely significant, wasteful cost at
scale. This trade-off is exactly why UTF-32 is **not** a common default
storage or interchange encoding for real files or network data — it
remains occasionally useful for specific internal processing needs
(where fixed-width indexing genuinely matters, and memory is not a
tight constraint) rather than as a general-purpose choice.

## 15. Legacy Encodings

### 15.1 What "legacy" means here

Before Unicode (and UTF-8's later dominance) became universal, many
regional, single-purpose encodings existed, each covering only a
limited character set, and generally **incompatible** with each other
at the byte level. Older datasets, older systems, and files exported
from older software can still use these — recognizing and correctly
handling them remains a genuinely practical, real-world skill.

### 15.2 Latin-1 / ISO-8859-1

```python
text = "é"
data = text.encode("latin-1")
print(data)
print(data.decode("latin-1"))
```

```text
b'\xe9'
é
```

**Latin-1** is a single-byte encoding covering Western European
characters — code points `U+0000`–`U+00FF` map directly, one-to-one, to
byte values `0`–`255`. This direct mapping has a notable, sometimes
misused practical consequence: `bytes.decode("latin-1")` **never
raises** `UnicodeDecodeError`, for *any* input bytes at all, because
every possible byte value `0`–`255` is a valid Latin-1 code point —
worth knowing precisely because it means "decoding with `latin-1`
succeeded" is **not** meaningful evidence that `latin-1` was actually
the *correct* encoding (§22's practical identification section returns
to this directly).

### 15.3 Windows-1252

**Windows-1252** closely resembles Latin-1 for most of its range, but
repurposes a specific block of byte values (`0x80`–`0x9F`, which
Latin-1 reserves for rarely-used control characters) for additional
printable characters — curly quotation marks, an em dash, and a few
others commonly produced by Windows word-processing software. This
near-but-not-quite similarity to Latin-1 is a genuine, common,
practical source of confusion — text is sometimes mislabeled
"Latin-1" when it was actually produced as Windows-1252, and the two
only visibly disagree in that specific byte range.

### 15.4 Why old datasets may still use these

A file exported years ago by older software, or by a system configured
for a specific regional locale, may have been written in Latin-1,
Windows-1252, or another regional legacy encoding, rather than UTF-8 —
simply because UTF-8 was not yet universally the default at the time it
was created. **Assuming every historical file is UTF-8 is a real,
common, and avoidable mistake** (§57 mistake 1) — §22 covers how to
approach an unknown or suspected-legacy encoding responsibly.

## 16. Encoding Comparison

| | ASCII | UTF-8 | UTF-16 | UTF-32 | Latin-1 | Windows-1252 |
|---|---|---|---|---|---|---|
| **Unicode support** | None (128 chars only) | Full | Full | Full | None (256 chars only) | None (256 chars only) |
| **Byte width** | Fixed, 1 byte | Variable, 1–4 bytes | Variable, 2 or 4 bytes | Fixed, 4 bytes | Fixed, 1 byte | Fixed, 1 byte |
| **ASCII-compatible?** | — (is ASCII) | Yes | No | No | Yes, for the ASCII range | Yes, for the ASCII range |
| **Common use today** | Legacy, protocol-level tokens | The dominant default for files, web, APIs | Some internal system/language representations | Rare; specific internal-processing needs | Legacy Western European files | Legacy Windows-originated text |
| **Advantage** | Simple, universal for its limited range | Compact, universal, ASCII-compatible | Fixed-ish width for common characters | Simplest possible fixed-width reasoning | Simple, never raises on decode | Adds useful Windows-era typography |
| **Limitation** | No non-English support at all | Slightly more complex byte rules (§12) | Not ASCII-byte-compatible; surrogate pairs | Large storage cost | No non-Western-European support | Same as Latin-1, plus its own quirks |

**Not every encoding here is equally appropriate today.** For any new
file, API, or system you design, **UTF-8 is the correct default choice
in the overwhelming majority of cases** — this table exists to help you
*recognize and correctly handle* the others when you encounter them
from external, legacy, or platform-specific sources, not to present
them as equally good options for new work.

## 17. Character Sets vs. Encodings

### 17.1 The precise distinction

A **character repertoire** (or **character set**) is simply the *set
of characters* a scheme knows about — Unicode itself, in this sense,
is a character repertoire: it defines which characters exist and what
number identifies each one (§4.2), but says nothing about bytes. An
**encoding** is the separate rule for turning those abstract characters
(via their code points) into actual bytes (§10.1).

### 17.2 Why "UTF-8 is a character set" is technically inaccurate

You will sometimes encounter loose language calling UTF-8 "a character
set" — this blurs exactly the distinction §17.1 just drew. **UTF-8 does
not define which characters exist** — Unicode does that. **UTF-8
defines how Unicode's already-existing code points get turned into
bytes.** Multiple different encodings (UTF-8, UTF-16, UTF-32) can all
correctly represent the *exact same* underlying Unicode character
repertoire, while producing entirely different bytes for it (§10.5) —
which is only a coherent idea once "the set of characters" and "how
they become bytes" are understood as genuinely separate concepts.

## 18. `encode()` and `decode()`

### 18.1 `str.encode()`, systematically

```python
str.encode(encoding="utf-8", errors="strict")
```

```python
"Hello".encode()                        # defaults: encoding="utf-8", errors="strict"
"Hello".encode("ascii")                    # explicit encoding
"é".encode("utf-8", errors="ignore")         # explicit error-handling policy (§19)
```

**`encoding`** — which named encoding scheme to apply; defaults to
`"utf-8"` in modern Python (a version-relevant default worth knowing
explicitly rather than assuming, §34). **`errors`** — what to do when a
character cannot be represented under the chosen encoding at all
(§19–§20 develop this fully).

### 18.2 `bytes.decode()`, systematically

```python
bytes.decode(encoding="utf-8", errors="strict")
```

```python
b"Hello".decode()                          # defaults: encoding="utf-8", errors="strict"
b"Hello".decode("ascii")                     # explicit encoding
some_bytes.decode("utf-8", errors="replace")   # explicit error-handling policy
```

**`encoding`** and **`errors`** mean exactly the same thing here, in
the reverse direction — which encoding to *interpret the bytes as*, and
what to do if a byte sequence cannot be validly interpreted under that
encoding at all.

### 18.3 Valid and invalid conversions, side by side

```python
"café".encode("utf-8")          # b'caf\xc3\xa9'  -- succeeds
"café".encode("ascii")            # UnicodeEncodeError -- 'é' is outside ASCII's range

b"caf\xc3\xa9".decode("utf-8")      # 'café'  -- succeeds
b"caf\xc3\xa9".decode("ascii")        # UnicodeDecodeError -- 0xc3 is not valid ASCII
```

## 19. Error Handling

### 19.1 Why an error-handling policy is necessary at all

Not every character can be represented under every encoding (§9.3's
`é`/ASCII example), and not every byte sequence is valid under every
encoding (§18.3's reverse example). Something must decide what happens
when this occurs — Python's `errors=` parameter is exactly that
decision point, and it applies identically to `str.encode()`,
`bytes.decode()`, and `open()`'s own `errors=` (§26).

### 19.2 The standard error handlers

| Handler | Encode behavior | Decode behavior | Danger level |
|---|---|---|---|
| **`strict`** (default) | Raises `UnicodeEncodeError` | Raises `UnicodeDecodeError` | Safest — surfaces the problem immediately |
| **`ignore`** | Silently drops the unencodable character | Silently drops the invalid byte(s) | **High — silent data loss** |
| **`replace`** | Substitutes `?` for the unencodable character | Substitutes `U+FFFD` (the replacement character) | Moderate — visibly marks the problem, but still loses the original data |
| **`backslashreplace`** | Substitutes a `\xNN`/`\uNNNN`-style escape | Substitutes a `\xNN`-style escape (decode support added in Python 3.5) | Low — preserves a recoverable, if unusual, textual trace |
| **`namereplace`** | Substitutes a `\N{...}`-style named escape | *(encode-only)* | Low — human-readable diagnostic trace |
| **`surrogateescape`** | Encodes previously-surrogate-escaped bytes back to their original form | Maps invalid bytes to a reserved surrogate code-point range (`U+DC80`–`U+DCFF`), enabling lossless round-tripping | Specialized — used internally for filesystem paths (§35) |
| **`surrogatepass`** | Allows encoding lone surrogate code points directly (normally forbidden) | Allows decoding lone surrogate byte sequences directly | Specialized — narrow, low-level use cases |

### 19.3 Worked examples

```python
"café".encode("ascii", errors="ignore")           # b'caf'          -- 'é' silently vanished!
"café".encode("ascii", errors="replace")            # b'caf?'         -- visibly marked, still lossy
"café".encode("ascii", errors="backslashreplace")     # b'caf\\xe9'      -- recoverable trace
"café".encode("ascii", errors="namereplace")           # b'caf\\N{LATIN SMALL LETTER E WITH ACUTE}'
```

### 19.4 Why `ignore` is especially dangerous

```python
data = b"caf\xc3\xa9 latte"
print(data.decode("ascii", errors="ignore"))
```

```text
caf latte
```

`errors="ignore"` produced perfectly plausible-*looking* output — `caf
latte` reads as valid English text, with **absolutely no indication**
that the `é` character (and, in fact, the boundary information around
it) was silently discarded entirely. **This is precisely why
`errors="ignore"` should be treated with real caution in production
code**: unlike a raised exception, silently dropped data gives you no
signal at all that anything went wrong — the output simply looks
"fine," while being subtly, silently incorrect. §58 makes this contrast
directly, with a corrected alternative.

### 19.5 `strict` as the correct default

**`strict` (Python's own default for both `.encode()` and `.decode()`)
is the correct default for data integrity, unless a different, specific
policy is a deliberate, documented decision for a specific, known
reason.** An exception surfaced immediately, at the exact point of
failure, is a far better outcome than silently corrupted or
data-losing output discovered — if ever — much later, far from its
actual root cause.

## 20. Unicode Errors

### 20.1 `UnicodeEncodeError`

```python
"café".encode("ascii")
```

```text
Traceback (most recent call last):
  ...
UnicodeEncodeError: 'ascii' codec can't encode character '\xe9' in position 3: ordinal not in range(128)
```

**What failed:** converting a Python `str` to `bytes` under a specific
encoding, because at least one character has no representation under
that encoding at all. **Why it failed:** `'\xe9'` (`é`, `U+00E9`) is
outside ASCII's 128-character range (§9.2). **Inspecting the error:**
the message names the exact codec (`'ascii'`), the exact problem
character, and its exact `position` within the string — directly
actionable diagnostic information (§42's debugging workflow relies on
exactly this). **Selecting an appropriate encoding:** the fix is
almost always choosing an encoding that *can* represent the character
in question — most often, `"utf-8"` — rather than reaching for
`errors="ignore"`/`"replace"` as a reflex (§19.5).

### 20.2 `UnicodeDecodeError`

```python
data = "café".encode("utf-8")   # b'caf\xc3\xa9'
data.decode("ascii")
```

```text
Traceback (most recent call last):
  ...
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 3: ordinal not in range(128)
```

**What failed:** converting `bytes` to a Python `str`, because at
least one byte (or byte sequence) is not valid under the specified
encoding. **Why it failed:** `0xc3` is the first byte of `é`'s
*two-byte* UTF-8 sequence (§12.4) — entirely meaningless as a standalone
byte under plain ASCII, which only ever expects single bytes in the
`0`–`127` range. **The byte position** the error reports (`position 3`
here) points precisely at where the invalid byte sequence begins —
again, directly actionable (§42). **The debugging process:** confirm
what encoding the bytes were *actually* produced with (§22), rather
than guessing at alternative encodings one at a time.

## 21. Mojibake

### 21.1 What mojibake is

**Mojibake** (a borrowed Japanese term, literally "character
transformation/corruption") is the name for text that has been
**decoded with the wrong encoding**, producing output that *looks*
like corrupted, garbled characters — even though, technically, no
exception was necessarily raised at all.

### 21.2 A worked, conceptual example

```python
original = "café"
utf8_bytes = original.encode("utf-8")   # b'caf\xc3\xa9'

corrupted = utf8_bytes.decode("latin-1")
print(corrupted)
```

```text
café
```

`é`'s two UTF-8 bytes (`\xc3\xa9`) were each **individually,
"successfully"** reinterpreted as two *separate*, single-byte Latin-1
characters (`Ã` and `©`) — Latin-1 never raises on decode (§15.2), so
this produces **no exception at all**, only visibly wrong text. This is
mojibake's defining, dangerous characteristic: **it frequently fails
silently, not loudly** — exactly why §22's practical identification
guidance, and §55's dedicated mojibake-debugging section, both matter.

### 21.3 The general pattern

```
correct bytes  →  wrong decoder  →  corrupted-looking text
```

Mojibake can occur in either direction between any two mismatched
encodings — UTF-8 bytes decoded as Windows-1252 produces one
characteristic pattern of corruption; Windows-1252 (or Latin-1) bytes
decoded as UTF-8 produces a *different* characteristic pattern (often
raising `UnicodeDecodeError` outright, since not every byte sequence a
single-byte encoding can produce is valid UTF-8) — §55 works through
both directions concretely.

### 21.4 How to diagnose and avoid it

**Diagnosing:** recognizable, characteristic corruption patterns
(certain repeating symbol clusters in place of accented letters) are a
strong hint of a specific encoding mismatch, though not a certainty —
§22's evidence-based approach is the reliable path, not pattern-matching
alone. **Avoiding it in the first place:** always know, explicitly,
which encoding a given file or byte stream actually uses (§22), rather
than assuming — the single most effective defense against mojibake is
never guessing the decoding encoding in the first place.

## 22. Unknown Encoding Problems

### 22.1 The practical reality: you generally cannot reliably guess an encoding from bytes alone

**There is no universal, foolproof way to look at an arbitrary
sequence of bytes and determine, with certainty, which encoding
produced them.** Some encodings (Latin-1, §15.2) accept *any* byte
sequence at all, giving no signal whatsoever about correctness; other
encodings will "successfully" decode bytes that were never actually
written under them, simply producing wrong (but not obviously invalid)
text, exactly as §21's mojibake example demonstrated.

### 22.2 Real sources of evidence, instead of guessing

**File documentation** — does the file's source, format specification,
or accompanying README state its encoding explicitly? **The producer
system** — what software or system generated this file, and what
encoding does *it* default to, or document using? **Metadata** — does
the file, protocol, or surrounding context carry explicit encoding
information (an HTTP `Content-Type` header's `charset=` parameter,
§45; a JSON file's own convention of always being UTF-8, per
[04-json-and-serialization.md](04-json-and-serialization.md)'s §25.3)?
**Protocol specification** — does the format itself mandate a specific
encoding (JSON, notably, is specified to always be Unicode, almost
always UTF-8 in practice)? **A known, specific application** — if you
know precisely which program exported this file, and that program's
own documented default, that is real, usable evidence. **BOM** (§23) —
present, and unambiguous, when it exists — but far from universal.
**Successful validation** — decoding successfully, *and* the resulting
text passing further application-specific sanity checks (expected
field names, expected value shapes), is meaningfully stronger evidence
than a bare decode succeeding alone (recall Latin-1 "succeeds" on
almost anything, §15.2, §22.1). **Controlled sampling and domain
knowledge** — inspecting a representative sample of the actual content,
combined with genuine, specific knowledge of where this particular data
came from.

### 22.3 Why "try random encodings until it looks okay" is unreliable

Trial-and-error decoding can produce output that *looks* plausible
while still being wrong — exactly §21.2's mojibake example, which
produced entirely readable (if wrong) text with zero exception raised.
"It looks fine to me" is not the same claim as "this is correct," and
relying on visual inspection alone, absent any of §22.2's real
evidence, is not a reliable engineering practice.

### 22.4 Detection libraries, mentioned only conceptually

Third-party libraries exist that attempt **statistical, heuristic
encoding detection** from raw bytes alone — genuinely useful tools in
practice, when no better evidence (§22.2) is available at all. This
chapter deliberately does not make such a library its primary teaching
path (consistent with this entire module's standard-library-first
approach) — the important conceptual takeaway is that even the best
such tools are performing **statistical inference**, not certain
determination, and their output should still be treated as a
*candidate*, validated (§22.2's "successful validation" point) before
being trusted, exactly like `csv.Sniffer`'s own guessed dialect
([03-csv-files.md](03-csv-files.md)'s §27.4).

## 23. Byte Order Mark (BOM)

### 23.1 What a BOM is, and why it exists

A **BOM** (Byte Order Mark) is a small, specific sequence of bytes,
sometimes placed at the very start of a text file, whose purpose is to
signal **which encoding, and (where relevant) which byte order**, the
rest of the file uses.

### 23.2 Byte order, briefly

Multi-byte code units (like UTF-16's 16-bit units, §13, or UTF-32's
32-bit units, §14) can be stored with their bytes in either of two
orders — "big-endian" (most significant byte first) or "little-endian"
(least significant byte first) — a genuine, real hardware-level
difference between systems. A BOM at the start of such a file lets a
reader determine, unambiguously, which byte order was used to write
it, without needing that information from anywhere else.

### 23.3 BOMs for each encoding

| Encoding | BOM bytes (hex) |
|---|---|
| UTF-8 | `EF BB BF` |
| UTF-16, big-endian | `FE FF` |
| UTF-16, little-endian | `FF FE` |
| UTF-32, big-endian | `00 00 FE FF` |
| UTF-32, little-endian | `FF FE 00 00` |

### 23.4 A BOM is not simply "an encoding"

**A BOM is a specific marker, at the start of a file, indicating byte
order and/or encoding — it is not itself a distinct encoding.**
`"utf-8-sig"` (§25) is Python's name for "UTF-8, plus recognize and
correctly strip a leading BOM if present" — a *behavior*, built on top
of the UTF-8 encoding, not a fundamentally different way of encoding
text. UTF-16 and UTF-32 use their BOM specifically to resolve byte
order (§23.2) — a genuine ambiguity those encodings have that UTF-8, as
a byte-oriented (not code-unit-oriented) encoding, does not.

## 24. UTF-8-SIG

### 24.1 Why a UTF-8 BOM exists at all, despite UTF-8 having no byte-order ambiguity

UTF-8 operates at the level of individual *bytes*, not multi-byte code
units — it has **no byte-order ambiguity to resolve** (§23.2 does not
apply to it the way it does to UTF-16/UTF-32). Some tools (notably
certain Windows applications, and Excel specifically, for CSV export —
directly recalling
[03-csv-files.md](03-csv-files.md)'s §26.4) nonetheless prepend a UTF-8
BOM anyway, purely as an explicit **signal**: "this file is UTF-8,"
even though UTF-8 itself does not strictly require one.

### 24.2 Reading UTF-8 files that may have a BOM

```python
with open("exported_from_excel.csv", "r", encoding="utf-8-sig") as f:
    text = f.read()
```

`encoding="utf-8-sig"` decodes as ordinary UTF-8, but **additionally
recognizes and correctly strips a leading BOM if one is present** —
without it, plain `encoding="utf-8"` would leave that BOM's three bytes
decoded as one stray, invisible `﻿` character glued onto the very
start of the file's content (silently corrupting, for example, a CSV
file's very first header name, exactly as
[03-csv-files.md](03-csv-files.md)'s §26.4 already demonstrated).

### 24.3 Writing UTF-8 with a BOM

```python
with open("output.csv", "w", encoding="utf-8-sig") as f:
    f.write("name,age\n")
```

Writing with `encoding="utf-8-sig"` **prepends** the UTF-8 BOM bytes at
the start of the output — useful specifically for compatibility with
tools (again, notably certain versions of Excel) that expect this
marker to correctly recognize a file as UTF-8, rather than falling back
to a locale-dependent default guess.

### 24.4 Why plain UTF-8 and UTF-8-SIG are not identical

**`"utf-8"` and `"utf-8-sig"` produce genuinely different bytes on
write** (the latter includes three extra leading bytes), and behave
genuinely differently on read (the latter strips a leading BOM if
present; the former does not, leaving it as a stray character). Using
the wrong one of the pair — reading a BOM-prefixed file as plain
`"utf-8"`, or writing a BOM-prefixed file when downstream tooling does
not expect one — is a real, common, and easily avoidable source of
subtle bugs (§57 mistake, and §54's debugging workflow, both return to
this).

## 25. `open()` and Encoding

### 25.1 Explicit `encoding=` — restated, precisely, one final time

```python
with open("data.txt", "r", encoding="utf-8") as f:
    text = f.read()
```

Every prior chapter in this module has already established the
practice; this chapter now gives it its full justification: **always
specify `encoding=` explicitly.** Omitting it does not mean "no
encoding is used" — it means Python silently falls back to a
**platform- and configuration-dependent default** (§34 develops exactly
what that default is, and why it can genuinely differ between
machines) — the exact same code can behave correctly on your machine
and incorrectly on a colleague's, or a deployment server's, purely
because of this omission.

### 25.2 What happens if `encoding=` is omitted, concretely

```python
with open("data.txt", "r") as f:   # no encoding= specified
    text = f.read()
```

On one machine, this might quietly use UTF-8, and behave identically
to specifying it explicitly. On another — a machine with a different
locale configuration (§34) — it might use a different default entirely,
producing mojibake (§21) or a `UnicodeDecodeError` (§20.2) on the
*exact same file*, with the *exact same code*. **This unpredictability,
not any specific wrong behavior, is the actual danger of omitting
`encoding=`.**

### 25.3 `errors=` on `open()`

```python
with open("legacy_data.txt", "r", encoding="utf-8", errors="replace") as f:
    text = f.read()
```

`open()`'s own `errors=` parameter behaves identically to
`bytes.decode()`'s (§19.2, §19.3) — it is passed straight through to
the same underlying decoding machinery, applied automatically every
time the file object reads text. The exact same caution applies:
`strict` (the default) is the correct choice for data integrity unless
a specific, documented reason calls for something else; `errors="ignore"`
risks exactly the same silent data loss described in §19.4, now
happening transparently, line after line, throughout an entire file's
worth of reading, rather than in one isolated `.decode()` call.

## 26. `newline=`

### 26.1 A first look at the parameter

```python
open("file.txt", "r", encoding="utf-8", newline=None)   # the default
open("file.txt", "r", encoding="utf-8", newline="")        # disables newline translation
open("file.txt", "r", encoding="utf-8", newline="\n")         # only recognizes "\n" as a line ending
open("file.txt", "r", encoding="utf-8", newline="\r")           # only recognizes "\r" as a line ending
open("file.txt", "r", encoding="utf-8", newline="\r\n")           # only recognizes "\r\n" as a line ending
```

`newline=` controls **how line-ending characters are recognized and
translated** as text is read or written — a genuinely separate concern
from `encoding=` (§67 makes this separation explicit, as its own
mental-model layer). §27–§29 build the vocabulary this parameter needs
(what a newline actually is, and how it differs across platforms)
before §31 explains precisely what each `newline=` value does.

### 26.2 Why this section is deliberately brief, for now

This parameter genuinely deserves full, careful treatment — §31
("Universal Newlines") gives it exactly that, once §27–§30 have built
the necessary background. Introducing it here only establishes that it
exists, and that it is a parameter of `open()` distinct from
`encoding=`/`errors=`.

## 27. Newline Fundamentals

### 27.1 What a newline is

A **newline** (also called a **line terminator** or **line ending**) is
a special character, or short sequence of characters, embedded directly
within text data, marking the boundary between one line and the next —
already introduced conceptually in
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§17; this chapter now gives it its complete, precise treatment.

### 27.2 LF, CR, and CRLF, named precisely

- **LF** ("line feed") — the character `\n`. Originally, on
  physical teleprinters, this instructed the print head to advance to
  the *next line* (vertically), without necessarily returning to the
  start of the current one.
- **CR** ("carriage return") — the character `\r`. Originally, this
  instructed the print head to return to the *start* of the current
  line (horizontally), without advancing to a new one.
- **CRLF** — the two-character sequence `\r\n` — CR immediately
  followed by LF: "return to the start, *then* advance to a new line"
  — together producing what a modern reader would recognize as a
  complete, ordinary line break.

### 27.3 The historical reason both exist

On old mechanical teleprinters and typewriters, "move to the next line"
and "return to the start of the line" were genuinely two **separate**
physical actions — some early computing systems adopted both
characters together (CRLF) to precisely mirror that two-step physical
mechanism. Other systems later simplified this to just one character
(LF alone, meaning both "advance" and, implicitly, "return") — this
historical divergence is the direct root of §28's Windows-vs-Linux
difference.

## 28. CR/LF/CRLF

### 28.1 Which systems use which convention today

- **Linux and macOS** use a single `\n` (LF) as their standard line
  ending.
- **Windows** conventionally uses `\r\n` (CRLF) as its standard line
  ending.
- **Classic, pre-OS-X Macintosh** systems (a now largely historical
  case, worth knowing exists, rarely encountered directly today) used a
  bare `\r` (CR) alone.

### 28.2 Why files can behave differently across systems

A text file written on Windows, using `\r\n` line endings, opened
naively on a Linux system that expects `\n`, can produce visible,
unwanted artifacts — commonly, a stray `\r` character appearing at the
*end* of every line (often rendered, depending on the viewing tool, as
nothing visible at all, or occasionally as a visible `^M` symbol in
certain terminal tools) — because the reading system did not
automatically translate the unfamiliar convention. §31's universal-
newline handling is Python's own, deliberate defense against exactly
this class of cross-platform annoyance.

### 28.3 WSL2 considerations

Because you are running Ubuntu through **WSL2** — a genuine Linux
environment (already established in
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§25.4) — files created *natively within* WSL2's own Linux filesystem
follow ordinary Linux (`\n`) conventions. Files that originated on the
**Windows side** (anything accessed via `/mnt/c/...`, per that same
chapter's §25.5), or that were edited by a Windows-native text editor
before being brought into WSL2, may well still carry `\r\n` line
endings — worth checking explicitly (§56's debugging techniques), never
assumed, when a file's true origin crosses that boundary.

## 29. Universal Newlines

### 29.1 The problem universal newlines solves

Without any special handling, a program would need to know, in
advance, exactly which of `\n`, `\r`, or `\r\n` a given file actually
uses, and handle each differently — genuinely inconvenient, and a real
source of cross-platform bugs. Python's **universal newline** mode
exists specifically to make this mostly automatic and invisible, for
the overwhelmingly common case.

### 29.2 `newline=None` — the default, on reading

With `newline=None` (`open()`'s default), **on read**: any of `\n`,
`\r`, or `\r\n` encountered in the file is recognized as a line
boundary, and **all of them are translated to a single `\n`** in the
`str` your program actually receives — regardless of which convention
the file on disk originally used. Your program's own logic, working
with the resulting `str`, therefore never needs to think about `\r\n`
vs. `\n` at all, for reading.

### 29.3 `newline=None` — the default, on writing

With `newline=None`, **on write**: every `\n` character your program
writes is translated to the **current operating system's own native
line-ending convention** (`\n` on Linux/macOS, `\r\n` on Windows) before
being physically written to disk — `os.linesep` names this
platform-specific value directly, though you rarely need to reference
it explicitly, since `newline=None` applies it automatically.

### 29.4 `newline=""` — disabling translation entirely

With `newline=""`, **on read**: line boundaries are still recognized
(any of `\n`/`\r`/`\r\n`), but they are returned to your program
**exactly as they appeared in the file, untranslated** — no
normalization to `\n` happens at all. **On write**: `\n` characters you
write are passed through to disk **completely unmodified** — no
platform-native translation happens either. **This is precisely why
CSV files are opened with `newline=""`** (§32 develops the connection
fully): the `csv` module needs to perform its *own*, precise line-ending
handling (including recognizing embedded newlines within quoted fields,
[03-csv-files.md](03-csv-files.md)'s §8), and Python's own separate
translation layer, left enabled, can interfere with that.

### 29.5 A specific `newline=` value — full manual control

With `newline` set to one specific string (`"\n"`, `"\r"`, or `"\r\n"`),
**on read**: only *that exact* string is treated as a line boundary at
all — no translation to `\n` happens, and no other convention is even
recognized as a line ending. **On write**: every `\n` character you
write is translated to that specific string. This gives complete,
explicit, manual control — genuinely useful when you know, precisely,
which single convention a file must use, and want no automatic
guessing or platform-based defaulting to occur at all.

### 29.6 This behavior is not oversimplified — a summary table

| `newline=` value | On read | On write |
|---|---|---|
| `None` (default) | Recognizes `\n`/`\r`/`\r\n`; all translated to `\n` | Every `\n` translated to the platform's native line ending |
| `""` | Recognizes `\n`/`\r`/`\r\n`; returned untranslated, exactly as found | No translation at all — `\n` written as-is |
| `"\n"` / `"\r"` / `"\r\n"` | Only that exact string is a line boundary; no translation | Every `\n` translated to that specific string |

## 30. Text Mode vs. Binary Mode

### 30.1 The two fundamentally different modes

```python
with open("file.txt", "r") as f:      # text mode
    text = f.read()                     # returns str

with open("data.bin", "rb") as f:     # binary mode
    data = f.read()                     # returns bytes
```

**Text mode** (`"r"`, `"w"`, and the rest of
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§9 modes, with no `"b"`) automatically **decodes** bytes into `str` on
read, and **encodes** `str` into bytes on write — using the file
object's configured `encoding` (§25) and `errors` (§25.3), and applying
newline translation (§29) — all invisibly, on every call. **Binary
mode** (`"rb"`, `"wb"`, and their variants) does **none of this** — it
reads and writes raw `bytes` directly, exactly as they exist on disk,
with **no** encoding/decoding and **no** newline translation applied at
all.

### 30.2 When binary mode is required

Binary mode is required for genuinely non-text data — images, audio,
compiled programs, compressed archives — anything where interpreting
the bytes *as characters* would be meaningless or actively harmful
(directly extending
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§1.4 text-vs-binary distinction). It is also occasionally the correct
choice for text data specifically when you need to perform §18's
encoding/decoding operations **entirely manually and deliberately** —
for example, when the encoding is not yet known and must be determined
*before* any automatic decoding is allowed to happen at all (§22).

## 31. Binary Mode and Encoding

### 31.1 `encoding=` and `errors=` are text-mode-only concepts

```python
open("data.bin", "rb", encoding="utf-8")
```

```text
Traceback (most recent call last):
  ...
ValueError: binary mode doesn't take an encoding argument
```

Python **refuses**, outright, to combine binary mode with `encoding=`
(or `errors=`, or `newline=`) — these parameters are meaningless in
binary mode, since binary mode performs no text interpretation at all;
passing them raises `ValueError` immediately, rather than silently
ignoring them.

### 31.2 Explicit decoding is required, deliberately, for binary data

```python
with open("data.bin", "rb") as f:
    raw = f.read()

text = raw.decode("utf-8")
```

When binary-mode bytes genuinely *do* represent text (perhaps read
this way specifically because the encoding needed to be confirmed
first, per §22, before any automatic decoding was allowed), converting
them to a usable `str` is an **explicit, separate, deliberate step** —
`.decode()` (§18.2), called by your own code, at the exact point you
have decided the correct encoding to use.

## 32. `str.splitlines()`

### 32.1 `splitlines()` vs. `split("\n")`

```python
text = "line one\r\nline two\rline three\n"

print(text.split("\n"))
print(text.splitlines())
```

```text
['line one\r', 'line two\rline three', '']
['line one', 'line two', 'line three']
```

`.split("\n")` splits **only** on the literal `\n` character —
anywhere `\r` or `\r\n` appears instead, it is left embedded, unsplit,
inside a resulting piece; a trailing `\n` also produces a spurious
final empty string. `.splitlines()` is **newline-aware**: it correctly
recognizes `\n`, `\r`, and `\r\n` (and, worth knowing, several
additional Unicode line-boundary characters, §32.3) as line boundaries,
and does **not** produce a spurious trailing empty entry for a
final trailing newline.

### 32.2 `splitlines(keepends=True)`

```python
text = "line one\nline two\n"
print(text.splitlines())
print(text.splitlines(keepends=True))
```

```text
['line one', 'line two']
['line one\n', 'line two\n']
```

`keepends=True` retains each line's original terminator character(s)
in the returned pieces, rather than stripping them — §35 develops
exactly why this matters.

### 32.3 `splitlines()`'s broader-than-expected line-boundary set

Worth knowing precisely, rather than assuming `.splitlines()` is simply
"CR/LF/CRLF-aware": it *additionally* recognizes several other Unicode
line/paragraph-boundary characters (including `\v`, `\f`, `\x1c`–`\x1e`,
`\x85` "next line," ` ` "line separator," and ` ` "paragraph
separator") as line boundaries too — a genuinely broader definition of
"line boundary" than `\n`/`\r`/`\r\n` alone. For the overwhelming
majority of everyday text processing this broader behavior is exactly
what you want; it is worth being aware of specifically if your code
needs to reason precisely about *which exact characters* counted as
boundaries in a given piece of text.

## 33. Keeping Newline Characters

### 33.1 Why retaining line endings can matter

For simply **reading and printing lines**, stripping line endings (or
letting `.splitlines()`'s default strip them automatically) is usually
exactly right. For **file transformations**, **patching** (applying a
small, precise change to specific lines of an existing file),
**source-code or configuration processing**, or **protocol parsing**
where the exact original line-ending bytes are themselves meaningful
data (not merely a formatting artifact to discard), **exact text
preservation** matters — and `keepends=True` (§32.2) is exactly the
tool that preserves it.

### 33.2 A concrete example: reconstructing a file exactly

```python
with open("source.txt", "r", encoding="utf-8", newline="") as f:
    text = f.read()

lines = text.splitlines(keepends=True)
reconstructed = "".join(lines)

assert reconstructed == text
```

Because `keepends=True` preserves each line's *original* terminator
exactly, `"".join(lines)` reproduces the *exact* original text —
something `.splitlines()`'s default (ends stripped) or `.split("\n")`
(loses distinction between `\r\n` and bare `\n`, per §32.1) cannot
reliably guarantee.

## 34. CSV/JSON Integration

### 34.1 CSV — `newline=""`, restated with full understanding

```python
with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
```

Now that §26–§29 have built the full picture, this pattern — already
used throughout
[03-csv-files.md](03-csv-files.md)'s §26.2 without full explanation —
is precisely explained: `csv.writer`'s own default `lineterminator`
(`\r\n`, unconditionally, regardless of platform,
[03-csv-files.md](03-csv-files.md)'s §15.2) can, if Python's *own*
separate `newline=None` translation layer is also active, be
double-translated on some platforms (the `\n` half of `csv.writer`'s
own `\r\n` getting additionally converted by the file object's own
layer) — producing malformed, doubled line endings. `newline=""` (§29.4)
disables that separate translation layer entirely, leaving the `csv`
module in full, sole control of exactly how line endings are written
and read — including correctly recognizing genuine embedded newlines
*inside* quoted CSV fields
([03-csv-files.md](03-csv-files.md)'s §8.1), which requires exactly the
untranslated, "as written" byte-level view `newline=""` provides.

### 34.2 CSV encoding assumptions and legacy CSV

Because CSV has no built-in encoding declaration of its own
([03-csv-files.md](03-csv-files.md)'s §4.1 established CSV as
fundamentally just text), a CSV file's actual encoding is entirely a
matter of external knowledge (§22) — a CSV file exported by older,
legacy software may well use Windows-1252 or another regional legacy
encoding rather than UTF-8 (§15.4), and a CSV file exported by Excel
specifically may include a UTF-8 BOM, requiring `encoding="utf-8-sig"`
(§24.2, directly matching
[03-csv-files.md](03-csv-files.md)'s own §26.4).

### 34.3 Multilingual CSV, in practice

```python
with open("customers.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"])   # correctly handles names in any script, under UTF-8
```

With correct `encoding="utf-8"` (or `"utf-8-sig"` where a BOM is
present) and `newline=""` both in place, CSV data containing any mix
of scripts and languages is handled entirely correctly, with no
special-casing needed beyond getting these two parameters right.

### 34.4 JSON — why `newline=""` is *not* needed

```python
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
```

Unlike CSV, **JSON text files do not need `newline=""`**
([04-json-and-serialization.md](04-json-and-serialization.md)'s §13.2
already stated this without full justification; here is the full
reasoning): JSON has no equivalent of CSV's raw, embedded-in-a-field
newline character requiring precise, untranslated byte-level handling
— a JSON string value's own internal newline is represented as the
*escape sequence* `\n` (two characters, backslash and `n`) within the
JSON text itself, never as a genuine, literal newline byte
(RFC-8259-compliant JSON does not permit a raw control character inside
a string literal at all) — so Python's ordinary universal-newline
translation (§29.2–§29.3) never has anything meaningful to interfere
with.

### 34.5 JSON pretty-printing and cross-platform portability

```python
json.dumps(data, indent=2)
```

`json.dumps(..., indent=2)`'s own multi-line, pretty-printed output
uses plain `\n` characters between lines, internally, as ordinary Python
string content — when subsequently written to a file via
`f.write(...)` or `json.dump(...)` under ordinary text mode (`newline=
None`, the default, appropriate here per §34.4), those `\n` characters
are correctly translated to the current platform's native line ending
on write, and correctly translated back to `\n` on read on any
platform — exactly the "just works across platforms" behavior universal
newlines (§29) is designed to provide, and precisely why JSON files
require no special `newline=` handling the way CSV does.

## 35. Standard Stream Encoding

### 35.1 `stdin`, `stdout`, and `stderr` are text streams too

```python
import sys

print(sys.stdout.encoding)
```

```text
utf-8
```

Python's standard input, output, and error streams (`sys.stdin`,
`sys.stdout`, `sys.stderr` — fully developed later in
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md))
are, like any text-mode file object, associated with a specific
**encoding** — `sys.stdin.encoding`, `sys.stdout.encoding`, and
`sys.stderr.encoding` each report it. This encoding governs how text
your program `print()`s is converted to bytes before being sent to the
terminal (or wherever the stream is redirected to), and how bytes
typed at a terminal are converted to text your program receives via
`input()`.

### 35.2 Why terminal encoding can differ from file encoding

The encoding `sys.stdout` uses is determined by the **surrounding
environment** — the terminal emulator's own configuration, the
operating system's locale settings (§36), or, increasingly commonly,
Python's own UTF-8 mode (§37) — **not** by anything your program
explicitly requests the way `open(..., encoding="utf-8")` does for a
file. This is precisely why a program correctly reading a UTF-8 file
can still occasionally fail, or produce corrupted output, specifically
when *printing* certain characters to a terminal whose own configured
encoding cannot represent them — a genuinely different failure point
from file-reading encoding mismatches, worth recognizing as its own,
separate category.

## 36. Default Encoding and UTF-8 Mode

### 36.1 Explicit vs. default encoding

An **explicit** encoding is one you name directly, in code —
`encoding="utf-8"` in an `open()` call. A **default** encoding is
whatever Python falls back to using when no explicit encoding is
given — and, critically, **this default is not a single, fixed,
universal value** — it depends on the platform and its configuration.

### 36.2 Locale encoding

```python
import locale

print(locale.getpreferredencoding(False))
```

`locale.getpreferredencoding()` returns the text encoding associated
with the current process's **locale** settings — a system-level
configuration describing language, region, and related formatting
conventions. Historically, on many systems, this locale-derived value
was exactly what `open()` silently fell back to when `encoding=` was
omitted — and because locale configuration genuinely differs between
machines, deployment environments, and even user accounts on the *same*
machine, this made file-encoding behavior genuinely unpredictable
without explicit `encoding=` (exactly §25.2's concrete warning).

### 36.3 Filesystem encoding, previewed

```python
import sys

print(sys.getfilesystemencoding())
```

`sys.getfilesystemencoding()` reports the encoding used specifically
for **filenames and paths** — a genuinely different concern from a
file's own *content* encoding, developed fully, and deliberately kept
separate, in §38.

### 36.4 UTF-8 mode, conceptually

Because locale-dependent default encoding behavior (§36.2) proved to be
a genuine, ongoing source of cross-platform bugs in real Python
programs, Python introduced **UTF-8 mode** — a global setting that, when
active, makes Python consistently default to UTF-8 for text
operations, **regardless** of the surrounding locale configuration.
`sys.flags.utf8_mode` reports whether it is currently active
(`1`) or not (`0`).

```python
import sys

print(sys.flags.utf8_mode)
```

### 36.5 Why explicit `encoding=` remains valuable even with UTF-8 mode available

**Even where UTF-8 mode is active, and even on a version of Python
where UTF-8 is the overall default, explicit `encoding="utf-8"` in
every `open()` call remains the better practice** — it makes your
code's **data contract** (§69) self-evident directly in the code
itself, immune to *any* environment-level configuration, present or
future, correct today and correct if that code is later run under a
different Python version, a different operating system, or a different
deployment environment whose defaults you do not control. §37 develops
exactly why relying on any default — even a generally-good one — is
weaker engineering than stating the requirement explicitly.

## 37. Python UTF-8 Mode

### 37.1 Why it exists

UTF-8 mode exists specifically to reduce the real-world harm caused by
locale-dependent default encoding behavior (§36.2) — by making Python's
own defaults consistently UTF-8-based, regardless of the surrounding
system's locale configuration, a large class of "works on my machine,
fails on the server" encoding bugs simply stops occurring by default.

### 37.2 How it can be enabled

```
PYTHONUTF8=1 python your_script.py
```

```
python -X utf8 your_script.py
```

UTF-8 mode can be enabled via the `PYTHONUTF8` environment variable, or
the `-X utf8` command-line flag — and, on POSIX systems, is also
enabled automatically under certain "locale coercion" conditions (most
notably, when the system's own configured locale is the minimal `"C"`
or `"POSIX"` locale, which itself typically implies no meaningful,
specific text-encoding preference was ever actually configured).

### 37.3 A genuinely important, version-specific caveat

**Per PEP 686, UTF-8 mode is planned to become Python's *default*
behavior, beginning with Python 3.15** — a meaningful, deliberate shift
away from locale-dependent defaulting altogether, for every Python
installation, not merely ones where UTF-8 mode has been explicitly
enabled. As of this chapter's writing, this is a genuinely significant,
forward-looking version distinction worth knowing explicitly: **do not
assume every Python installation you will encounter already defaults
to UTF-8 without explicit configuration** — verify your actual Python
version's behavior (`sys.flags.utf8_mode`, §36.4) rather than assuming,
and, regardless of which default your specific Python version happens
to use, **continue writing `encoding="utf-8"` explicitly in your own
code** (§36.5) — the safest, most portable habit, unaffected by which
Python version, or which system's locale configuration, your code
happens to run under.

## 38. Filesystem Encoding

### 38.1 The critical distinction

**Filesystem encoding** governs how **filenames and paths themselves**
are represented as bytes at the operating-system level. **File content
encoding** (everything §9–§24 of this chapter has covered) governs how
the **bytes stored *inside* a file** are interpreted as text. **These
are two entirely separate concerns, answered by entirely separate
mechanisms — confusing them is a genuine, if subtle, mistake.**

### 38.2 `sys.getfilesystemencoding()` does not tell you a file's content encoding

```python
import sys

print(sys.getfilesystemencoding())   # e.g. 'utf-8' -- this describes FILENAMES, not file CONTENT
```

A file named `café.txt` (a filename containing a non-ASCII character)
has that *filename itself* encoded according to
`sys.getfilesystemencoding()`'s value — but the actual **text stored
inside** `café.txt` could be UTF-8, Latin-1, Windows-1252, or anything
else entirely, completely independent of, and unrelated to, whatever
encoding the filesystem happens to use for filenames. **Checking
`sys.getfilesystemencoding()` tells you absolutely nothing about what
encoding to pass to `open(..., encoding=...)` for that file's
*content*.**

### 38.3 A brief, practical note: `surrogateescape`

Directly connecting to §19.2's table: `surrogateescape` is specifically
the error handler Python's own filesystem-path handling relies on
internally, precisely because filenames occasionally contain byte
sequences that are not, strictly, valid text under the filesystem's
nominal encoding — `surrogateescape` allows such filenames to be
represented losslessly in Python anyway (as special surrogate code
points), round-tripping correctly back to their original bytes when
needed, rather than raising an error merely for *existing as a
filename* on disk.

## 39. pathlib Integration

### 39.1 Encoding remains a file-*content* concern with `pathlib`, too

```python
from pathlib import Path

text = Path("notes.txt").read_text(encoding="utf-8")
Path("notes.txt").write_text("Hello", encoding="utf-8")

with Path("notes.txt").open("r", encoding="utf-8") as f:
    text = f.read()
```

[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§15 already introduced `.read_text()`/`.write_text()`/`.open()` as
`pathlib`'s bridge to ordinary file I/O — this chapter's contribution
is simply making explicit that **every one of §38.1's distinctions
still applies unchanged**: `Path`'s own filesystem-facing operations
(§38 of that chapter — `.exists()`, `.iterdir()`, and the rest) concern
themselves with *paths*, not file *content*; the moment you call
`.read_text()`, `.write_text()`, or `.open()` specifically, you are back
in this chapter's territory — `encoding=` remains every bit as
necessary, and every bit as much your own explicit responsibility, as
it is with the plain built-in `open()`.

## 40. Network/Data Engineering Integration

### 40.1 The general boundary

```
network bytes  →  decode according to protocol/metadata  →  text
```

Exactly the same encode/decode boundary this entire chapter has taught
for files applies, conceptually unchanged, to data arriving over a
network — bytes arrive first, and must be decoded, using whatever
encoding the specific protocol or accompanying metadata specifies,
before your program can treat them as text at all.

### 40.2 HTTP content types, conceptually

An HTTP response commonly carries a `Content-Type` header including a
`charset=` parameter — e.g. `Content-Type: text/plain; charset=utf-8`
— telling the receiving program exactly which encoding to use when
decoding the response body's raw bytes. This is precisely §22.2's
"metadata" evidence source, made concrete for a specific, extremely
common real protocol. **This chapter does not attempt a full
HTTP/networking tutorial** — the point here is only that the same
decode-according-to-known-encoding discipline this chapter has built
for files applies identically the moment your programs begin
communicating over a network, a topic this roadmap develops fully much
later.

### 40.3 Databases, briefly

Database systems and their Python drivers commonly perform their own
internal encoding/decoding of text data, according to the database's
own configured character set — the **same underlying principle**
applies regardless of the specific system involved: **always understand
where, exactly, raw bytes become interpreted text**, in *any* system
your data passes through, rather than assuming it "just works" without
knowing why. This chapter does not duplicate a full database lesson —
a separate, later part of the roadmap's own subject.

### 40.4 Encoding in data engineering: a realistic pipeline

```
SOURCE
    ↓
BYTES
    ↓
DECODE  (using a known, or carefully determined, encoding -- §22)
    ↓
VALIDATE  (does the resulting text look correct? §22.2's "successful validation")
    ↓
TRANSFORM  (your actual business logic)
    ↓
ENCODE  (typically to UTF-8, on the way out)
    ↓
OUTPUT
```

Realistic scenarios where this pipeline matters directly: **ingesting a
legacy CSV** export that turns out to use Windows-1252, not UTF-8
(§15.3, §34.2); **multilingual customer data**, correctly requiring
UTF-8's full Unicode range (§11.2); **exported spreadsheet data**,
frequently carrying a UTF-8 BOM (§24); **log files**, sometimes
containing a mix of encodings across entries written by different
systems over time; **ETL pipelines** and **object-storage files**,
where the encoding is a property of the *specific source system*, not
a universal constant; **batch processing**, where a single malformed or
mis-encoded record should be handled deliberately (quarantined,
reported), never silently discarded, exactly mirroring
[03-csv-files.md](03-csv-files.md)'s §24.3 principle, now applied
specifically to an encoding-level failure rather than a structural CSV
one.

## 41. AI/ML Integration

### 41.1 Where encoding matters throughout AI/ML systems

**Training data** — text corpora, especially multilingual ones, depend
entirely on correct, consistent encoding to avoid silently corrupting
what a model actually learns from. **Prompts** — text sent to a
language model must be correctly encoded for the API or system
receiving it. **Documents** — source documents ingested into a
retrieval or processing pipeline may arrive in any of §15–§16's
encodings, especially if sourced from older archives. **Metadata and
annotations** — labels, tags, and human-review notes, frequently
containing free-text in multiple languages. **Multilingual datasets**
— directly depend on correct, consistent UTF-8 handling throughout, to
avoid silently mixing correctly- and incorrectly-decoded text within
the same dataset. **Text embeddings and model input pipelines** — text
must be correctly decoded *before* being tokenized or embedded;
mojibake (§21) fed into a model is learned, or reasoned over, as if it
were genuine, meaningful content. **Evaluation datasets** — an encoding
bug silently corrupting even a small fraction of evaluation examples
can quietly bias measured results. **Generated text** — output from a
model must itself be correctly encoded on the way out, to any
downstream file, API, or display. **JSON/CSV metadata** — exactly this
module's own §34's integration guidance, applied specifically to the
metadata files that accompany real ML/AI artifacts.

### 41.2 Why encoding problems can silently corrupt training data

**This is a genuinely serious, and easy to overlook, risk specific to
AI/ML work: an encoding mismatch does not always raise an exception
(§21's mojibake) — it can silently produce corrupted-but-plausible-
looking text, which a training pipeline may simply ingest and learn
from without any error ever being raised at all.** Unlike a program
that crashes on bad input (immediately, visibly, forcing a fix), a
model trained partly on silently mojibake-corrupted text degrades
*quietly* — the resulting problem (subtly worse quality on some subset
of inputs, particularly for the specific languages or scripts most
affected) can be genuinely difficult to trace back to its actual root
cause, long after the corrupted data has already been baked into a
trained model. This is precisely why this chapter's emphasis on
**explicit encoding, deliberate error handling, and validation at
ingestion** (§40.4, §69) matters especially, not merely academically,
for AI/ML data pipelines specifically.

## 42. Unicode Normalization

### 42.1 Why visually identical strings may not compare equal

```python
a = "é"                      # a single, precomposed code point: U+00E9
b = "é"                  # 'e' (U+0065) followed by a COMBINING ACUTE ACCENT (U+0301)

print(a)
print(b)
print(a == b)
```

```text
é
é
False
```

Both `a` and `b` **display identically** — but they are made of
**genuinely different sequences of code points**: `a` uses one single,
"precomposed" code point representing `é` directly; `b` uses **two**
code points — a plain `e`, followed by a separate "combining" accent
mark applied to it. Unicode explicitly permits *both* representations
of the same visual character, and Python's `==` compares code-point
sequences exactly, with no automatic awareness that these two
sequences are meant to represent "the same" character visually.

### 42.2 `unicodedata.normalize()`

```python
import unicodedata

a = "é"
b = "é"

normalized_a = unicodedata.normalize("NFC", a)
normalized_b = unicodedata.normalize("NFC", b)

print(normalized_a == normalized_b)
```

```text
True
```

`unicodedata.normalize(form, text)` converts text into one of several
standard, canonical representations, making genuinely equivalent text
comparable directly with `==` afterward.

### 42.3 The four normalization forms

- **NFC** ("Normalization Form Canonical Composition") — combines
  decomposed sequences into their precomposed form wherever one exists
  (`e` + combining accent → `é`, the single code point). The most
  commonly recommended default for general-purpose text storage and
  comparison.
- **NFD** ("Canonical Decomposition") — the reverse: splits precomposed
  characters into their base character plus separate combining marks.
- **NFKC** ("Compatibility Composition") — like NFC, but *additionally*
  normalizes certain "compatibility" variants (for example, certain
  stylistic or formatting-only character variants) toward a single,
  simpler canonical form — a stronger, sometimes *lossy* (in the sense
  of discarding a real stylistic distinction) normalization.
- **NFKD** — the compatibility-aware decomposed counterpart to NFKC.

### 42.4 When normalization is useful — and when it is not something to apply unconditionally

Normalization is genuinely valuable before comparing, searching,
deduplicating (§43), or using text as an identifier or lookup key,
where two differently-encoded-but-visually-identical strings should be
treated as "the same." **It should not be applied unconditionally,
without consideration, to every piece of text your program handles** —
NFKC/NFKD's compatibility normalization specifically can discard real,
sometimes meaningful, distinctions (§43.2 returns to this trade-off
directly) — normalization is a deliberate choice, made for a specific,
understood reason, not a reflexive "always apply this" habit.

## 43. Grapheme Clusters

### 43.1 What a user perceives as "one character" can be several code points

```python
text = "👨‍👩‍👧‍👦"   # a "family" emoji, visually one glyph
print(len(text))
```

```text
7
```

This single, visually-one-glyph emoji is actually composed of
**multiple** separate code points — several individual emoji joined
together using invisible "zero width joiner" characters — a
**grapheme cluster**: what a human reader perceives as one single,
indivisible visual unit, even though it is technically several distinct
Unicode code points combined. §42.1's combining-accent-mark example
(`e` + combining acute accent) is, likewise, a two-code-point grapheme
cluster that visually displays as one character.

### 43.2 Why `len(text)` does not always equal "the number of characters a user sees"

`len(text)` on a Python `str` counts **code points** (§5) — not
grapheme clusters, and not bytes (§11.4's separate distinction).
**None of these three counts — code points, bytes, and user-perceived
characters — are guaranteed to agree**, for text containing combining
marks or multi-code-point emoji sequences specifically. This has real,
practical consequences: a naive "truncate this text to the first *N*
characters" operation, implemented with plain slicing (`text[:N]`),
can split a combining-mark sequence or a multi-part emoji *in the
middle*, producing genuinely broken, malformed-looking output — a
correctness risk worth knowing exists, even though fully solving it
(true grapheme-cluster-aware text segmentation) generally requires
dedicated, specialized tooling beyond this chapter's introductory
scope.

## 44. Unicode Security

### 44.1 Why this is a genuine, defensive engineering concern

Unicode's flexibility — the same visual character often having more
than one valid representation (§42), and Unicode containing characters
specifically designed to be invisible or visually near-identical to
others — creates real opportunities for confusion, whether accidental
or deliberately adversarial. This section teaches the defensive
awareness needed to recognize and guard against these risks — not
techniques for exploiting them.

### 44.2 Malformed byte sequences, oversized input, and decoding failures

Treat malformed byte sequences (§20.2) and unexpectedly oversized text
input as genuine data-validation concerns, not mere inconveniences —
exactly [04-json-and-serialization.md](04-json-and-serialization.md)'s
§39.2 resource-exhaustion warning, restated here specifically for raw
text/bytes: validate expected size and structure explicitly at any
boundary accepting text from an untrusted or external source, rather
than assuming it will always be well-formed and reasonably sized.

### 44.3 Normalization is not a substitute for validation

**Do not blindly normalize or silently discard invalid characters as
a general-purpose "cleaning" step, assuming this automatically makes
text safe.** Normalization (§42) changes *representation*; it does not
inherently validate *content* — text can be perfectly well-formed,
fully normalized Unicode, and still be entirely inappropriate,
malicious, or invalid for your specific application's purposes.
Similarly, silently discarding characters your code does not expect
(via `errors="ignore"`, §19.4) hides information from you exactly when
you most need to see it — a defensive posture requires surfacing
unexpected input explicitly, not quietly erasing it.

## 45. Confusables and Invisible Characters

### 45.1 Unicode confusables

Unicode **confusables** are distinct code points that render as
**visually identical, or nearly identical**, characters — a Latin
letter `a` (`U+0061`) and a visually near-identical Cyrillic letter
(`U+0430`), for example, look the same to a human reader, but are
genuinely different code points, and compare as unequal with `==`.
**Risk:** a username, domain-like identifier, or any other
human-verified text field can be spoofed by substituting a confusable
character an attacker controls for a visually indistinguishable
"real" one — a genuine, documented security concern in systems that
display such identifiers to humans for visual verification.

### 45.2 Zero-width and invisible characters

Certain Unicode code points render as **entirely invisible** — a
zero-width space, a zero-width joiner used outside its intended emoji-
combination context, or various formatting-control characters. **Risk:**
two strings that *look* completely identical to a human reader can
differ by the presence of one of these invisible characters, causing
`==` comparisons, search matches, or "duplicate" detection (§46) to
behave in genuinely surprising, hard-to-diagnose ways.

### 45.3 Non-breaking spaces and control characters

A **non-breaking space** (`U+00A0`) looks, visually, exactly like an
ordinary space, but is a *different* code point — text containing one
in place of a genuine space will not match a search or comparison
expecting an ordinary ASCII space. **Unicode control characters**
(non-printing characters carrying formatting or protocol-level
meaning, rather than visible content) embedded unexpectedly within
otherwise-ordinary text can likewise cause confusing, hard-to-spot
behavior in display, comparison, or downstream processing.

### 45.4 The practical, defensive takeaway

For any system accepting free-text identifiers from untrusted sources
— usernames, search queries, display names — being aware that
**"looks the same" is not the same claim as "is the same string"** is
a genuine, practical engineering concern (§46 develops the
data-quality angle of this directly), worth explicit validation and
testing, not an obscure theoretical curiosity.

## 46. Debugging Encoding Problems

### 46.1 A systematic ten-step workflow

1. **Inspect the raw bytes directly**, before assuming anything about
   the intended encoding.
2. **Use `repr()`**, not plain `print()`, on both bytes and decoded
   text, to reveal exactly what characters (and, for bytes, exactly
   which byte values) are actually present.
3. **Determine the source encoding** using §22's real evidence sources
   — never by guessing.
4. **Test decoding explicitly**, with your best-evidence candidate
   encoding, before trusting the result.
5. **Inspect the first failing byte's position**, from a
   `UnicodeDecodeError`'s own message (§20.2), if one is raised.
6. **Inspect for a BOM** (§23) — the first few bytes of the file,
   compared against §23.3's known BOM byte sequences.
7. **Inspect newline style** (§56 develops this specifically) — a
   separate, but frequently co-occurring, concern.
8. **Compare platform behavior**, if the same file behaves differently
   on two different machines — a strong signal of a default-encoding
   (§36) or newline-convention (§28) difference between them, not a
   problem with the file itself.
9. **Inspect file metadata or documentation** — anything the file's
   source system, or accompanying documentation, states about its
   encoding.
10. **Reproduce with a minimal file** — a tiny, deliberately crafted
    file containing exactly the suspicious byte pattern, isolated from
    the rest of a larger, more complex dataset.

### 46.2 A worked example

```python
from pathlib import Path

data = Path("mystery.txt").read_bytes()
print(repr(data[:100]))
```

```text
b'caf\xc3\xa9 latte\r\nwith cream\r\n'
```

Reading raw bytes and printing their `repr()` immediately reveals two
separate, useful pieces of evidence at once: `\xc3\xa9` is exactly
`é`'s UTF-8 byte pattern (§12.4), and `\r\n` throughout suggests
Windows-originated (or Windows-edited) line endings (§28.1) — both
determined *before* attempting any decoding at all, directly following
step 1 and step 2 of §46.1's workflow.

```python
text = data.decode("utf-8")
print(text)
```

```text
café latte
with cream
```

## 47. Debugging Newline Problems

### 47.1 Common symptoms and their likely causes

| Symptom | Likely cause |
|---|---|
| Unexpected **blank lines** appearing between every real line | Mixed line-ending conventions, or writing `\r\n` explicitly *in addition to* text-mode's own automatic `\n`→native translation (§29.3), doubling the effective line break |
| **Doubled newlines** in output | Exactly the CSV `lineterminator`/`newline=` interaction §34.1 already explained, now generalized: writing an already-complete line ending while translation is also active |
| **Missing** line endings entirely | A file genuinely written with no line-ending characters at all, or `newline=""` used on write when native translation was actually needed |
| **Mixed** line endings within one file | The file was edited or concatenated using more than one tool/platform over its history |
| Behavior differing between **Windows and Linux** | Exactly §28.2 and §28.3's platform-convention differences, most often surfacing specifically where universal-newline handling (§29) was bypassed (`newline=""` or a specific fixed value) without a deliberate reason |

### 47.2 Inspecting with `repr()`

```python
with open("suspicious.txt", "r", encoding="utf-8", newline="") as f:
    text = f.read()

print(repr(text))
```

```text
'line one\r\nline two\nline three\r\n'
```

Reading with `newline=""` (§29.4) specifically **preserves** the file's
original, untranslated line endings — exactly what you need visible to
diagnose a genuine newline-convention problem; reading with the default
`newline=None` would have already silently normalized everything to
`\n`, hiding the very evidence you are trying to inspect.

### 47.3 `splitlines(keepends=True)` as a diagnostic tool

```python
for line in text.splitlines(keepends=True):
    print(repr(line))
```

```text
'line one\r\n'
'line two\n'
'line three\r\n'
```

Directly reveals that this specific file mixes `\r\n` and bare `\n`
line endings within itself — precisely the "mixed line endings" symptom
from §47.1's table, now confirmed with concrete evidence rather than
suspicion.

## 48. Common Mistakes

**1. Assuming all files are UTF-8.**
Directly §15.4/§22's warning — a real, historical file may use a
legacy encoding; confirm, using real evidence (§22.2), rather than
assuming.

**2. Omitting `encoding=` without understanding the default.**
Directly §25.2/§36's warning — the resulting behavior is
platform-/configuration-dependent, not a fixed, safe fallback.

**3. Decoding bytes with the wrong encoding.**
Directly §21's mojibake, and §22.3's "trial and error is unreliable"
warning.

**4. Encoding text that is already encoded (double-encoding).**
```python
# BAD -- text is already a str; encoding it, then treating the result as text again, is wrong
text = "café"
once = text.encode("utf-8")
twice = once.decode("utf-8").encode("utf-8").decode("latin-1")   # nonsensical chain
```
→ **Lesson:** keep clear, explicit track of whether a given value is
currently `str` or `bytes` at every point in your code (§7.3) — never
"just try encoding/decoding again" hoping it fixes something.

**5. Decoding text that is already decoded.**
```python
text = "café"
text.decode("utf-8")   # AttributeError -- str has no .decode() method at all
```
→ `str` objects do not have a `.decode()` method; only `bytes`/
`bytearray` do — this error itself is a direct, useful signal you have
confused the two.

**6. Mixing `str` and `bytes` carelessly.**
Directly §7.3's `TypeError` example.

**7. Using `errors="ignore"` casually.**
Directly §19.4's silent-data-loss warning.

**8. Ignoring `UnicodeDecodeError`/`UnicodeEncodeError` with a bare
`except:`.**
```python
# BAD
try:
    text = data.decode("utf-8")
except Exception:
    text = ""
```
→ Exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§27.3 principle — catch the specific exception, and handle it
deliberately, never blanket-swallow it.

**9. Stripping characters without understanding why they appeared.**
Removing a stray `\r`, a BOM's `﻿`, or an unexpected control
character with an ad hoc `.replace(...)` call, without first
diagnosing *why* it is there (§46, §47) — the fix is treating the root
cause (wrong `newline=`, missing `utf-8-sig`, wrong encoding), not
scrubbing its symptom after the fact.

**10. Confusing UTF-8 with Unicode.**
Directly §4.3/§17.2's core distinction — Unicode defines characters;
UTF-8 is one specific way of encoding them as bytes.

**11. Confusing code points with bytes.**
Directly §5.4's distinction — a code point is a number; bytes are its
*encoded* representation, and the two are not interchangeable
concepts, nor always the same count (§11.4).

**12. Assuming `len(str)` equals byte length.**
Directly §11.4's worked example.

**13. Assuming `len(str)` equals user-visible character count.**
Directly §43.2's grapheme-cluster caveat.

**14. Ignoring BOM.**
Reading a BOM-prefixed file with plain `"utf-8"` instead of
`"utf-8-sig"` (§24.2), leaving a stray `﻿` character glued to the
start of the content.

**15. Ignoring normalization where it genuinely matters.**
Comparing, deduplicating, or using as a lookup key, text that may
exist in more than one valid Unicode representation, without
normalizing first (§42) — resulting in "duplicate" entries that
`==` fails to recognize as such.

**16. Assuming newline is always `\n`.**
Directly §28's Windows/Linux/WSL2-convention warning.

**17. Manually replacing all `\r\n` without understanding context.**
```python
# RISKY -- can corrupt data that genuinely, deliberately contains \r\n as content, not as a line ending
text = raw_bytes.decode("utf-8").replace("\r\n", "\n")
```
→ **Better:** let Python's own universal-newline handling (§29,
`newline=None`, the default) perform this translation correctly and
consistently during reading, rather than reimplementing it by hand
with a blunt, context-blind string replacement.

## 49. Bad vs. Good Code

```python
# BAD -- relies on a platform-dependent default
with open("data.txt") as f:
    text = f.read()

# GOOD -- explicit, portable, correct everywhere
with open("data.txt", encoding="utf-8") as f:
    text = f.read()
```
**When explicit encoding is appropriate:** essentially always, for any
file whose content your program cares about — the only real exception
is binary-mode reads (§30–§31), where `encoding=` does not apply at
all.

```python
# BAD -- silently discards data, with no trace of what was lost
text = data.decode("utf-8", errors="ignore")

# GOOD -- surfaces the problem explicitly, and lets you decide deliberately
try:
    text = data.decode("utf-8")
except UnicodeDecodeError as error:
    # log, quarantine, or handle explicitly -- never silently proceed
    raise
```
**Why silent data loss is dangerous:** exactly §19.4/§41.2's warning —
an `errors="ignore"` failure produces plausible-looking, wrong output,
with no signal anything went wrong at all.

```python
# BAD -- not newline-aware; breaks on \r\n or bare \r
lines = text.split("\n")

# GOOD -- correctly recognizes every standard line-ending convention
lines = text.splitlines()
```
**Newline awareness:** directly §32.1's worked comparison.

## 50. End-to-End Examples

### 50.1 Example 1 — Multilingual Text File Inspector

```python
from pathlib import Path
import unicodedata

KNOWN_BOMS = {
    b"\xef\xbb\xbf": "utf-8-sig",
    b"\xff\xfe\x00\x00": "utf-32-le",
    b"\x00\x00\xfe\xff": "utf-32-be",
    b"\xff\xfe": "utf-16-le",
    b"\xfe\xff": "utf-16-be",
}


def detect_bom(data: bytes) -> str | None:
    for bom_bytes, name in KNOWN_BOMS.items():
        if data.startswith(bom_bytes):
            return name
    return None


def detect_newline_style(text: str) -> str:
    has_crlf = "\r\n" in text
    has_lone_cr = "\r" in text.replace("\r\n", "")
    has_lf = "\n" in text.replace("\r\n", "")
    styles = []
    if has_crlf:
        styles.append("CRLF")
    if has_lone_cr:
        styles.append("CR")
    if has_lf:
        styles.append("LF")
    return ", ".join(styles) if styles else "none detected"


def inspect_file(path: Path, encoding: str = "utf-8") -> None:
    # 1-2. Inspect raw bytes and report size.
    data = path.read_bytes()
    print(f"File: {path}")
    print(f"Size: {len(data)} bytes")

    # 3. Inspect for a BOM.
    bom = detect_bom(data)
    print(f"BOM detected: {bom or 'none'}")
    decode_encoding = bom if bom else encoding

    # 4-5. Attempt decoding, reporting any error precisely.
    try:
        text = data.decode(decode_encoding)
    except UnicodeDecodeError as error:
        print(f"Decode failed with {decode_encoding!r}: {error}")
        return

    # 6. Detect newline style.
    print(f"Newline style: {detect_newline_style(text)}")

    # 7. Report line count.
    print(f"Lines: {len(text.splitlines())}")

    # 8. Show code-point info for the first few non-ASCII characters.
    non_ascii = [c for c in text if ord(c) > 127][:5]
    for character in non_ascii:
        print(f"  {character!r}: U+{ord(character):04X} ({unicodedata.name(character, 'UNKNOWN')})")

    # 9. Optionally write a normalized, UTF-8 output file.
    normalized = unicodedata.normalize("NFC", text)
    path.with_suffix(".normalized.txt").write_text(normalized, encoding="utf-8")
```

**Every stage explained:** raw bytes are inspected first, before any
decoding is attempted (§46.1 steps 1–2); BOM detection (§23.3's known
byte patterns) runs before choosing a decode encoding, since a
confirmed BOM is strong, direct evidence (§22.2); decoding failure is
reported with full diagnostic detail rather than silently guessed
around (§20.2); newline style is detected using the raw, undecoded-
translation-free text (mirroring §47.2's diagnostic pattern);
non-ASCII characters are reported with their precise code points and
Unicode names (§5.2–§5.3, using `unicodedata.name()`, §66); and the
output is explicitly normalized (§42.2) and written as plain UTF-8
(§24.1's correct default), regardless of whatever encoding the input
file actually used.

### 50.2 Example 2 — Advanced: Robust Text Ingestion Pipeline

```python
from pathlib import Path
from dataclasses import dataclass
import unicodedata


@dataclass
class IngestResult:
    source_path: Path
    encoding_used: str
    lines_processed: int
    normalized: bool


class EncodingDecisionError(Exception):
    pass


def decide_encoding(data: bytes, declared_encoding: str | None) -> str:
    # Prefer explicit, known evidence over guessing (§22.2).
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if declared_encoding:
        return declared_encoding
    raise EncodingDecisionError(
        "No BOM present and no declared encoding provided; refusing to guess."
    )


def ingest_text_file(
    path: Path,
    output_path: Path,
    *,
    declared_encoding: str | None = "utf-8",
    normalize: bool = True,
) -> IngestResult:
    # READ BYTES
    data = path.read_bytes()

    # ENCODING DECISION
    encoding = decide_encoding(data, declared_encoding)

    # DECODE (explicit, strict -- surfaces problems immediately)
    try:
        text = data.decode(encoding, errors="strict")
    except UnicodeDecodeError as error:
        raise EncodingDecisionError(
            f"{path} could not be decoded as {encoding!r}: {error}"
        ) from error

    # VALIDATE TEXT (a minimal, deliberate sanity check)
    if not text.strip():
        raise EncodingDecisionError(f"{path} decoded to empty content")

    # NORMALIZE IF REQUIRED
    if normalize:
        text = unicodedata.normalize("NFC", text)

    # PROCESS (kept intentionally simple -- a real pipeline's own logic goes here)
    lines = text.splitlines()

    # WRITE UTF-8 OUTPUT
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # VALIDATE OUTPUT
    written_back = output_path.read_text(encoding="utf-8")
    if written_back.splitlines() != lines:
        raise EncodingDecisionError(f"Output verification failed for {output_path}")

    return IngestResult(
        source_path=path,
        encoding_used=encoding,
        lines_processed=len(lines),
        normalized=normalize,
    )
```

**Architecture:** the pipeline follows exactly the diagram §40.4 already
laid out, stage by stage, with each stage's exact responsibility
visible directly in the code's own comments and function boundaries.
**Explicit encoding and error policy:** `decide_encoding` refuses to
silently guess (§22.3) when no real evidence is available, raising a
clear, specific exception instead; decoding uses `errors="strict"`
explicitly (§19.5), never `"ignore"`. **Newline policy:** the pipeline
deliberately normalizes to a single, consistent `\n`-based output
(`"\n".join(lines) + "\n"`), regardless of the input's original
convention — a deliberate, explicit choice, not an accident of
whichever `newline=` happened to be in effect. **Unicode normalization**
is applied, but only as a documented, optional (`normalize=True`)
parameter — never unconditionally forced (§42.4's caution). **Output
validation** — reading the just-written output back and confirming it
matches what was intended — is a direct, concrete instance of the
"verify output" habit already established in
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§19.3.

## 51. Testing

### 51.1 Testing ASCII, UTF-8, and general Unicode content

```python
def test_reads_ascii_content(tmp_path):
    path = tmp_path / "ascii.txt"
    path.write_text("Hello", encoding="utf-8")
    assert path.read_text(encoding="utf-8") == "Hello"


def test_reads_multilingual_utf8_content(tmp_path):
    path = tmp_path / "multilingual.txt"
    text = "Hello বাংলা こんにちは 🙂"
    path.write_text(text, encoding="utf-8")
    assert path.read_text(encoding="utf-8") == text
```

### 51.2 Testing UTF-8 BOM handling

```python
def test_utf8_sig_strips_bom(tmp_path):
    path = tmp_path / "bom.txt"
    path.write_bytes(b"\xef\xbb\xbfhello")

    assert path.read_text(encoding="utf-8-sig") == "hello"
    assert path.read_text(encoding="utf-8").startswith("﻿")
```

### 51.3 Testing invalid UTF-8 and Latin-1

```python
import pytest


def test_invalid_utf8_raises(tmp_path):
    path = tmp_path / "invalid.txt"
    path.write_bytes(b"caf\xc3 latte")   # a truncated, invalid UTF-8 sequence

    with pytest.raises(UnicodeDecodeError):
        path.read_text(encoding="utf-8")


def test_latin1_decodes_without_raising(tmp_path):
    path = tmp_path / "latin1.txt"
    path.write_bytes(bytes(range(0, 256)))   # every possible byte value

    text = path.read_text(encoding="latin-1")   # never raises, per §15.2
    assert len(text) == 256
```

### 51.4 Testing newline variations

```python
def test_universal_newlines_normalize_to_lf(tmp_path):
    path = tmp_path / "mixed.txt"
    path.write_bytes(b"line one\r\nline two\rline three\n")

    text = path.read_text(encoding="utf-8")   # newline=None default via read_text
    assert text == "line one\nline two\nline three\n"


def test_newline_empty_string_preserves_original_endings(tmp_path):
    path = tmp_path / "mixed.txt"
    path.write_bytes(b"line one\r\nline two\n")

    with path.open("r", encoding="utf-8", newline="") as f:
        text = f.read()

    assert text == "line one\r\nline two\n"
```

### 51.5 Testing Unicode normalization

```python
import unicodedata


def test_nfc_normalization_makes_equivalent_forms_equal():
    precomposed = "é"
    decomposed = "é"

    assert precomposed != decomposed
    assert unicodedata.normalize("NFC", precomposed) == unicodedata.normalize("NFC", decomposed)
```

## 52. Round-Trip Testing

### 52.1 The pattern

```
text → encode → bytes → decode → text
```

```python
def test_round_trip_preserves_multilingual_text():
    original = "Hello বাংলা こんにちは 🙂"
    encoded = original.encode("utf-8")
    decoded = encoded.decode("utf-8")

    assert decoded == original
```

### 52.2 When exact equality can, correctly, change

**Lossy error handlers break round-tripping, by design.**
`text.encode("ascii", errors="ignore").decode("ascii")` does **not**
round-trip back to the original — characters were deliberately
discarded (§19.4); this is expected, correct behavior for that
specific handler, not a test failure to chase. **Normalization changes
representation, deliberately.** `unicodedata.normalize("NFC", text)`
applied to already-NFC text is a no-op, but applied to NFD text
produces genuinely different code points than the NFD original — a
round-trip test comparing *normalized* output against a
*non-normalized* original should expect this difference, not treat it
as a bug (§42.4). **`errors="replace"`/`"backslashreplace"` are also
inherently lossy**, by their own documented design (§19.2) — a correct
round-trip test of these handlers checks that the *expected*,
documented substitution occurred, not that the original text was
exactly recovered.

## 53. Property-Style Thinking

### 53.1 A simple, useful invariant

**For valid text and a fully compatible encoding:**

```
decode(encode(text)) == text
```

```python
def test_utf8_round_trip_invariant_holds_for_arbitrary_text():
    samples = ["Hello", "café", "বাংলা", "🙂", "", "a" * 1000]

    for text in samples:
        assert text.encode("utf-8").decode("utf-8") == text
```

### 53.2 Why this is a useful mental model, without needing a dedicated framework

Thinking in terms of **invariants** — properties that should hold true
across a *range* of inputs, not merely one hand-picked example — is a
genuinely valuable testing habit, and this chapter's round-trip
invariant is a simple, concrete instance of it: **for any text, and
any encoding capable of representing every character in that text**,
encoding followed by decoding with the *same* encoding should always
recover the original exactly. This chapter does not require a
dedicated third-party property-based testing framework to benefit from
this mental model — simply testing the invariant against a
**deliberately varied set of representative examples** (ASCII, accented
characters, non-Latin scripts, emoji, empty string, a long string), as
§53.1 does, already captures most of the practical value.

## 54. Performance

### 54.1 Where the real costs are

**Encoding/decoding cost** scales with the amount of text/bytes being
converted — genuinely large volumes of text incur proportionally more
work. **Memory** — reading an entire large file's content as one string
(`f.read()`) requires holding that entire decoded text in memory at
once, exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§20 warning, restated here specifically at the decoding layer.
**Repeated conversions** — encoding and then decoding (or vice versa)
the same data more than once, when the result could simply be reused,
is pure, avoidable waste.

### 54.2 `for line in file:` vs. `file.read()`, specifically for encoding cost

```python
# Reads and decodes the ENTIRE file's bytes into one string, all at once
with open("huge.txt", "r", encoding="utf-8") as f:
    text = f.read()
```

```python
# Decodes incrementally, one line/chunk at a time, as iteration proceeds
with open("huge.txt", "r", encoding="utf-8") as f:
    for line in f:
        process(line)
```

Exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§8/§20 lesson, viewed specifically through this chapter's lens: decoding
work happens incrementally either way (the file object performs it
internally as bytes are consumed), but `f.read()` forces the **entire**
resulting decoded string to be held in memory simultaneously, while
`for line in f:` never holds more than roughly one line's worth of
decoded text at a time — `for line in file:` is preferable whenever the
file may be large, exactly as it already was for the purely
memory-focused reasons that earlier chapter established.

### 54.3 Buffered I/O, briefly

Python's file objects perform their own internal buffering (already
covered conceptually in
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§32) beneath the text-decoding layer this chapter has focused on — the
two layers (buffering, and encoding/decoding) are genuinely separate
concerns, working together: buffering governs *how often* the
underlying bytes are actually fetched from disk; encoding/decoding
governs *how* those fetched bytes are turned into (or from) `str`.

## 55. Streaming Text Processing

### 55.1 The pattern, restated in this chapter's terms

```python
with open("access.log", "r", encoding="utf-8") as f:
    for line in f:
        process(line)
```

**Memory efficiency:** exactly §54.2's point, restated as this
chapter's own direct application — only a small, roughly constant
amount of memory is used, regardless of the file's total size, because
decoding happens incrementally, one line at a time. **Newline
behavior:** with the default `newline=None`, each yielded line is
already correctly, uniformly `\n`-terminated, regardless of the
original file's actual line-ending convention (§29.2) — one fewer
concern for `process(line)` to worry about. **Large log files and data
pipelines:** this is precisely the shape real log-processing and
streaming data-ingestion code takes — one line, fully decoded and
newline-normalized, at a time, exactly matching
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§20.5's own "streaming" example, now understood with the full
encoding/newline mechanics behind *why* it works correctly across
files of any origin and any platform's line-ending convention.

## 56. API Reference

No invented APIs — every entry below is a genuine, documented member of
Python's standard library.

### 56.1 String/bytes conversion

| API | What it does | Key parameters | Returns | Caveat |
|---|---|---|---|---|
| `str.encode()` | Converts text to bytes | `encoding` (default `"utf-8"`), `errors` (default `"strict"`) | `bytes` | May raise `UnicodeEncodeError` (§20.1) |
| `bytes.decode()` | Converts bytes to text | `encoding` (default `"utf-8"`), `errors` (default `"strict"`) | `str` | May raise `UnicodeDecodeError` (§20.2) |
| `bytes` | An immutable byte sequence | — | — | Indexing returns `int`, not a one-byte `bytes` (§7.2) |
| `bytearray` | A mutable byte sequence | — | — | Otherwise behaves like `bytes` (§8) |
| `ord()` | Character → code point | A single-character `str` | `int` | Raises `TypeError` for a multi-character string |
| `chr()` | Code point → character | An `int` in range `0`–`0x10FFFF` | A one-character `str` | Raises `ValueError` outside the valid range |

### 56.2 File/text I/O

| API | What it does | Key parameters | Caveat |
|---|---|---|---|
| `open()` | Opens a file, text or binary | `mode`, `encoding`, `errors`, `newline` (§25–§29) | `encoding`/`errors`/`newline` are text-mode-only (§31.1) |
| `TextIOWrapper` | The concrete type returned by `open()` in text mode | — | Rarely instantiated directly; `open()` is the normal entry point |
| `.read()` / `.readline()` / `.readlines()` / iteration | Reading methods | — | Fully covered in [01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s §6, §8 |
| `.write()` / `.writelines()` | Writing methods | — | Fully covered in that same chapter's §17–§18 |

### 56.3 Newline/string helpers

| API | What it does | Key parameters | Caveat |
|---|---|---|---|
| `str.splitlines()` | Newline-aware line splitting | `keepends` (default `False`) | Recognizes more boundary characters than just `\n`/`\r`/`\r\n` (§32.3) |

### 56.4 Unicode database (`unicodedata`)

| API | What it does | Key parameters | Returns | Caveat |
|---|---|---|---|
| `unicodedata.normalize()` | Converts text to a canonical form | `form` (`"NFC"`/`"NFD"`/`"NFKC"`/`"NFKD"`), `text` | `str` | NFKC/NFKD can discard meaningful stylistic distinctions (§42.3–§42.4) |
| `unicodedata.name()` | The official Unicode name of a character | A one-character `str`, optional `default` | `str` | Raises `ValueError` for unnamed characters unless `default` is given |
| `unicodedata.category()` | The character's general Unicode category (letter, punctuation, etc.) | A one-character `str` | `str` (a two-letter code) | Specialized, rarely needed in everyday code |
| `unicodedata.bidirectional()` | The character's bidirectional class (relevant to right-to-left scripts) | A one-character `str` | `str` | Specialized; relevant mainly for text layout/rendering concerns |
| `unicodedata.combining()` | The character's canonical combining class | A one-character `str` | `int` | Specialized; relevant mainly to normalization internals |

### 56.5 Encoding/environment

| API | What it does | Returns | Caveat |
|---|---|---|---|
| `locale.getpreferredencoding()` | The encoding associated with the current locale | `str` | Historically what `open()` fell back to without explicit `encoding=` (§36.2) |
| `sys.getfilesystemencoding()` | The encoding used for filenames/paths | `str` | Does **not** describe file *content* encoding (§38.2) |
| `sys.stdin.encoding` / `sys.stdout.encoding` / `sys.stderr.encoding` | The encoding of each standard stream | `str` | Determined by the surrounding environment, not your code (§35.2) |
| `sys.flags.utf8_mode` | Whether Python's UTF-8 mode is currently active | `int` (`1` or `0`) | Planned to become the default starting with Python 3.15, per PEP 686 (§37.3) |

## 57. Internal Mental Model

### 57.1 The full pipeline

```
USER TEXT
    ↓
Python str  (Unicode code points, §5-§6)
    ↓  ENCODE  (str.encode() / open()'s own internal encoding, §18, §25)
BYTES
    ↓
FILE / NETWORK / STORAGE
    ↓
BYTES
    ↓  DECODE  (bytes.decode() / open()'s own internal decoding, §18, §25)
Python str
    ↓
APPLICATION
```

### 57.2 Newline handling as a genuinely separate layer

```
bytes
    ↓  decode
text stream  (already-decoded Unicode text)
    ↓  newline translation  (§29 -- governed by newline=, entirely separate from encoding=)
Python str  (as your program actually receives it)
```

### 57.3 Why encoding and newline translation are related but different problems

**Encoding** answers "how do these bytes map to characters?" —
entirely a question about *which byte values mean which Unicode code
points* (§9–§18). **Newline translation** answers a completely separate
question — "which specific character sequence, *within already-decoded
text*, counts as a line boundary, and should it be normalized?" (§26–
§29). A file can have its encoding configured perfectly correctly while
its newline handling is configured wrong (or vice versa) — the two
`open()` parameters (`encoding=` and `newline=`) are independent knobs,
addressing independent concerns, and this chapter's own two-diagram
structure (§57.1 and §57.2) exists specifically to keep that
independence clear in your mental model, rather than treating "text
file handling" as one single, undifferentiated concern.

## 58. Cross-Platform Portability

### 58.1 A practical guide, by platform

| | Linux | Windows | macOS | WSL2 |
|---|---|---|---|---|
| **Default line ending** | `\n` | `\r\n` | `\n` | `\n` (native Linux filesystem) |
| **Filesystem encoding** | Typically UTF-8 | Typically UTF-16-based internally, exposed as configurable | Typically UTF-8 | Typically UTF-8 (genuine Linux environment) |
| **Terminal encoding** | Typically UTF-8 | Historically variable; increasingly UTF-8-capable | Typically UTF-8 | Typically UTF-8 |
| **A special consideration** | — | Legacy code pages/locale-dependent defaults still occasionally encountered | — | Files from `/mnt/c/...` (Windows side) may carry `\r\n`; native `/home/...` files follow Linux convention (§28.3) |

### 58.2 CSV and JSON behavior across platforms

CSV: `csv.writer`'s own `lineterminator` default (`\r\n`) is
**platform-independent by design** — it is the same regardless of which
OS your code runs on, precisely why `newline=""` (§34.1) matters
identically everywhere, not merely on one specific platform. JSON: as
§34.4–§34.5 already established, plain text-mode `open()` (with
`newline=None`, the default) correctly, automatically handles
cross-platform line-ending differences for JSON's own pretty-printed
output, with no special handling required.

### 58.3 The central portability principle

**Portable software should make important text-format assumptions
explicit — never implicit, and never dependent on whichever platform
happened to be used to write or test the code.** Explicit
`encoding="utf-8"` (§25.1, §36.5), a deliberate, documented `newline=`
choice where one is genuinely needed (§34.1's CSV case being the clear
example, rather than the default elsewhere), and awareness of exactly
which platform's conventions a given piece of data actually originated
from (§22.2, §46.1) — together, these are what make code correct
*regardless* of which platform someone eventually runs it on, rather
than merely correct on the platform it happened to be written and
tested on.

## 59. Production Engineering Principles

1. **Know the data contract.** Understand, explicitly and in advance,
   what encoding and newline convention a given file or data source is
   expected to use — never assume.
2. **Prefer explicit encodings at file boundaries.** Every `open()`
   call handling text should name `encoding=` explicitly (§25.1),
   regardless of what any environment or Python-version default
   happens to be (§36.5).
3. **Do not silently discard invalid data.** `errors="ignore"` should
   be a rare, deliberate, documented exception — not a default (§19.4–
   §19.5).
4. **Validate external text.** Successful decoding alone is not
   sufficient evidence of correctness (§22.2's "successful validation"
   point) — apply further, application-specific sanity checks where it
   matters.
5. **Preserve source data when needed.** Where the original, unmodified
   bytes or text may need to be recovered later, keep them — exactly
   [03-csv-files.md](03-csv-files.md)'s §39.2 "landing zone" principle,
   applied here to raw text data specifically.
6. **Separate raw bytes from decoded text, deliberately, in your own
   code.** Know, at every point, whether a given value is currently
   `bytes` or `str` (§7.3, §48 mistakes 4–6).
7. **Make newline policy explicit where it matters.** Default
   (`newline=None`) is correct for most text; CSV specifically needs
   `newline=""` (§34.1) — know which situation you are in, and why.
8. **Test multilingual data.** Include genuinely non-ASCII, multi-script
   text in your test data (§51.1), not only ASCII examples.
9. **Test cross-platform behavior**, or at minimum understand and
   document the platform-specific behaviors your code depends on
   (§58).
10. **Document encoding assumptions.** A file format, API contract, or
    data pipeline's expected encoding should be written down, not left
    implicit in whoever happened to write the ingestion code first.
11. **Monitor ingestion failures.** A production pipeline encountering
    `UnicodeDecodeError` or unexpected encoding mismatches should
    surface this clearly (logging, metrics, a rejected-records report —
    exactly [03-csv-files.md](03-csv-files.md)'s §24.3 principle) rather
    than failing silently or crashing without useful context.
12. **Avoid unnecessary text/byte conversions.** Every extra
    encode/decode round trip is both a real, if usually small,
    performance cost (§54.1) and a real, avoidable opportunity to
    introduce a subtle bug.

## 60. Mini-Projects

### Mini Project 1 — Text Encoding Inspector

**Problem statement:** build a tool reporting encoding-relevant facts
about an unfamiliar text file.

**Requirements:** inspect the file's raw bytes; report its size; attempt
decoding with a specified (or BOM-detected) encoding; identify a BOM if
present (§23); report the detected newline style (§47.3); report
Unicode information (code point, name) for a sample of non-ASCII
characters.

**Expected behavior:** matches, in spirit, §50.1's worked example —
built by you, with your own reporting format.

**Suggested architecture:** separate, independently testable functions
for BOM detection, newline-style detection, and character-info
reporting — each takes already-loaded data/text, no file I/O needed to
test any one of them directly.

**Constraints:** must not assume the encoding in advance — must
genuinely attempt BOM-based detection first, falling back to an
explicit, caller-provided encoding only when no BOM is present.

**Edge cases:** an empty file; a file that is valid ASCII only (no
non-ASCII characters to report on); a file that fails to decode
entirely under the assumed encoding.

**Testing requirements:** `tmp_path`-based tests (§51) for each edge
case, plus at least one genuinely multilingual sample file.

**Extension challenge:** report the file's apparent "encoding
confidence" — whether decoding succeeded cleanly, versus only via a
lossy `errors=` fallback.

### Mini Project 2 — Multilingual Text Converter

**Problem statement:** convert a text file from a specified source
encoding into clean, UTF-8 output.

**Requirements:** read the source file using a caller-specified
encoding (§18.2, §26); validate that decoding actually succeeded,
raising clearly if not; optionally apply Unicode normalization
(§42.2), controlled by an explicit parameter, never forced
unconditionally; write UTF-8 output (§24.1); preserve the original
line structure faithfully (§33's `keepends=True` technique, if exact
preservation is the goal, or deliberate, documented normalization to
`\n` if that is instead the goal — choose, and document, one).

**Expected behavior:** correctly converts a genuinely non-UTF-8 source
file (Latin-1 or Windows-1252, §15) into valid, readable UTF-8 output.

**Suggested architecture:** a pure conversion function (bytes + source
encoding → normalized `str`), separated from the file-reading/writing
I/O around it — directly this module's now-familiar separation-of-
concerns pattern.

**Constraints:** decoding must use `errors="strict"` by default —
never a silent, lossy fallback, unless explicitly and deliberately
requested by the caller.

**Edge cases:** a source file that is already UTF-8 (should convert
losslessly, effectively unchanged in content); a source file containing
a BOM; a source file that genuinely fails to decode under the specified
encoding.

**Testing requirements:** at least one round-trip test (§52) per
supported source encoding.

**Extension challenge:** auto-detect a UTF-8 BOM and use `utf-8-sig`
automatically, while still requiring an explicit source encoding for
non-BOM-marked input (directly mirroring §50.2's `decide_encoding`
pattern).

### Mini Project 3 — Cross-Platform Text Normalizer

**Problem statement:** process a file with mixed or unknown newline
conventions into deterministic, single-convention output.

**Requirements:** correctly detect and report the input's actual
newline style(s) (§47.3, potentially mixed within a single file);
normalize to a single, explicitly chosen convention on output
(`\n`, matching Linux/WSL2 convention, is a reasonable default choice);
explicitly choose and document the output encoding; produce byte-
for-byte deterministic output for the same logical input, run
repeatedly.

**Expected behavior:** a file with mixed `\r\n`/`\n`/`\r` line endings
becomes a file with exactly one consistent convention throughout.

**Suggested architecture:** read with `newline=""` (to see, and be able
to report on, the original convention, §47.2) and reconstruct the
output deliberately, rather than relying solely on `newline=None`'s
automatic translation, which would not let you *report* on the mixture
that was originally present.

**Constraints:** must correctly handle a file where more than one line-
ending convention is present simultaneously (§47.1's "mixed" symptom).

**Edge cases:** a completely empty file; a file with no line endings at
all (one single unterminated line); a file already fully consistent in
its original convention.

**Testing requirements:** test each individual convention (`\n` only,
`\r\n` only, `\r` only) and at least one genuinely mixed-convention
input file.

**Extension challenge:** run the tool, unmodified, against a file
brought in from the Windows side of WSL2 (`/mnt/c/...`,
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§25.5) versus a file created natively within WSL2's own filesystem, and
confirm your tool correctly normalizes both.

### Mini Project 4 — Robust Text Ingestion Pipeline

**Problem statement:** build a complete, production-oriented ingestion
pipeline, extending §50.2's advanced example.

**Requirements:** configurable source-encoding policy (explicit
default, with BOM-based override, §50.2's `decide_encoding` pattern);
explicit, `strict`-based decoding error policy (§19.5); explicit
newline policy (§29, §58.3); an optional, explicitly-controlled Unicode
normalization step (§42.4); streaming processing for large files
(§55), not `f.read()` on the whole file; clear error reporting,
distinguishing decode failures from downstream validation failures;
clean UTF-8 output (§24.1); a `pytest` suite (§51) covering at least
ASCII, multilingual UTF-8, a legacy-encoded source, a BOM-prefixed
source, mixed newlines, and a deliberately invalid/undecodable input;
brief, honest documentation of the pipeline's exact encoding and
newline assumptions/guarantees (§59 principle 10).

**Expected behavior:** matches and extends §50.2's `ingest_text_file`
example — you are encouraged to add genuine line-by-line streaming
(rather than that example's simpler, whole-file `read_bytes()`
approach) as a deliberate improvement.

**Suggested architecture:** §50.2's three-part shape (an encoding-
decision function, a decode-and-validate step, and a thin orchestration
function), extended with a genuinely streaming read/write loop.

**Constraints:** the entire input file must never be required to fit
in memory at once, for the streaming variant specifically.

**Edge cases:** a source file too large to comfortably load whole (to
genuinely exercise the streaming requirement); a source file that
decodes successfully but fails a downstream content-validation check;
a source file with a BOM that does *not* match the caller's declared
encoding (which should win, and why — decide, and document, the
answer).

**Testing requirements:** the full set described in "Requirements"
above, plus at least one test confirming the pipeline never calls
anything equivalent to `f.read()` on the full input (verifiable, for
example, by testing against a file large enough that a full in-memory
read would be a clearly observable, deliberate design choice, not an
accident).

**Extension challenge:** support reading from a genuinely unknown
source encoding by requiring explicit configuration at the call site
(never guessing internally, §22.3), while providing a clear, actionable
error message when that configuration is missing and no BOM is
present to fall back on.

## 61. Coding Exercises

### Level 1 — Foundation

1. Print `type()` for a `str` value and a `bytes` value, side by side,
   and explain the difference in your own words.
2. Encode a plain ASCII string with `.encode("ascii")`, and print the
   result.
3. Encode a string containing at least one non-ASCII character with
   `.encode("utf-8")`, and print the result.
4. Decode a `bytes` value back to a `str` with `.decode("utf-8")`.
5. Use `ord()` and `chr()` together to confirm they are exact inverses
   for at least three different characters, including one non-ASCII
   character.
6. Compare `len(text)` and `len(text.encode("utf-8"))` for a string
   containing at least one non-ASCII character, and explain the
   difference.

### Level 2 — Practical

7. Write a function that detects whether a given `bytes` value begins
   with a UTF-8 BOM (§23.3).
8. Read a genuinely UTF-8-encoded file and print its contents.
9. Read a genuinely Latin-1-encoded file (one you construct yourself)
   and print its contents.
10. Deliberately trigger a `UnicodeDecodeError` by decoding UTF-8 bytes
    as ASCII, and inspect the exception's `.start`, `.end`, and
    `.reason` attributes.
11. Write a function that normalizes a file's line endings to `\n`,
    regardless of its original convention (without simply relying on
    the default `newline=None` translation alone — do it explicitly,
    using `newline=""` and your own logic, as practice).
12. Use `str.splitlines()` on text containing a mix of `\n`, `\r`, and
    `\r\n`, and confirm it produces the expected, uniform result.

### Level 3 — Engineering

13. Build a function that validates whether a given `bytes` value is
    valid UTF-8, without raising an exception — returning `True`/`False`
    instead (hint: `try`/`except` around a decode attempt, returning a
    boolean, is a legitimate, common pattern here).
14. Build a function that inspects a file's raw bytes and reports its
    detected newline style(s), exactly as §47.3 demonstrated, as a
    standalone, independently testable function.
15. Build a small multilingual file processor: read a file (encoding
    provided explicitly), report its character count and byte count
    separately, and explain, in a comment, why they can differ.
16. Write UTF-8, normalized (NFC) output from text that originally
    contained a mix of precomposed and decomposed character sequences,
    and write a test confirming the output is fully NFC-normalized.
17. Write `pytest` tests specifically confirming that
    `errors="strict"` (the default) correctly raises on invalid input,
    for both `.encode()` and `.decode()`.

### Level 4 — Advanced

18. Implement a small text-ingestion pipeline supporting at least two
    different possible input encodings, selected explicitly by the
    caller (never auto-detected via trial and error, §22.3).
19. Add Unicode normalization as an explicit, optional step to your
    Level 4 exercise 18 pipeline, and write a test proving it is
    genuinely optional (i.e., the pipeline behaves correctly with it
    both enabled and disabled).
20. Extend your pipeline to preserve the *original*, unmodified source
    text (or bytes) alongside its processed output — implementing
    [03-csv-files.md](03-csv-files.md)'s §39.2 "landing zone" principle
    concretely, for text data.
21. Implement genuinely streaming (line-by-line) processing for your
    pipeline, rather than reading the whole file at once, and write a
    test confirming correct behavior on a large, generated input file.
22. Implement a robust error policy distinguishing at least three
    different failure categories (decode failure, empty/malformed
    content, downstream validation failure) with a distinct, specific
    exception or error code for each.
23. Write at least one test in your pipeline's suite that is explicitly
    a cross-platform-behavior test — confirming your pipeline produces
    identical, correct output regardless of which newline convention
    the *input* file happened to use.

## 62. Debugging Exercises

Each snippet below is broken. Diagnose using §46's workflow before
reading the corrected version.

**1. UTF-8 decoded as ASCII.**
```python
data = "café".encode("utf-8")
text = data.decode("ascii")
```
*Diagnose:* what does the resulting `UnicodeDecodeError`'s byte
position point at (§20.2)? *Corrected:* `data.decode("utf-8")`.

**2. UTF-8 decoded as Windows-1252.**
```python
data = "café".encode("utf-8")
text = data.decode("windows-1252")
```
*Diagnose:* does this raise an exception, or silently produce wrong
text (§21.2's mojibake pattern)? *Corrected:* `data.decode("utf-8")`.

**3. Latin-1 decoded as UTF-8.**
```python
data = "café".encode("latin-1")
text = data.decode("utf-8")
```
*Diagnose:* is `\xe9` (Latin-1's single byte for `é`) a valid start of
a UTF-8 sequence on its own (§12.1's table)? *Corrected:*
`data.decode("latin-1")`.

**4. Mixed newline styles, unaddressed.**
```python
with open("mixed.txt", "r", encoding="utf-8") as f:
    lines = f.read().split("\n")
```
*Diagnose:* what happens to lines originally ending in `\r\n` or bare
`\r` under a plain `.split("\n")` (§32.1)? *Corrected:* use
`.splitlines()` instead, or rely on the default `newline=None`
translation and then split on the now-guaranteed `\n`.

**5. Missing `encoding=`.**
```python
with open("multilingual.txt") as f:
    text = f.read()
```
*Diagnose:* what does this rely on that isn't visible in the code
itself (§25.2, §36)? *Corrected:* add `encoding="utf-8"` explicitly.

**6. `errors="ignore"` used casually, hiding a real problem.**
```python
with open("data.txt", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()
```
*Diagnose:* what happens to any genuinely invalid bytes in the file,
and would you ever know they were there (§19.4)? *Corrected:* use the
default `errors="strict"`, and handle `UnicodeDecodeError` explicitly
and deliberately if it occurs.

**7. `str`/`bytes` mixing.**
```python
header = b"Content: "
message = "café"
combined = header + message
```
*Diagnose:* what does the resulting `TypeError` tell you about mixing
these two types directly (§7.3)? *Corrected:*
`header + message.encode("utf-8")`, or `header.decode("utf-8") + message`
— pick one representation and stay consistent.

**8. Incorrect BOM handling.**
```python
with open("exported_from_excel.txt", "r", encoding="utf-8") as f:
    text = f.read()
print(text.startswith("header"))
```
*Diagnose:* if the file has a BOM, what invisible character is
actually at the very start of `text` (§24.2)? *Corrected:*
`encoding="utf-8-sig"`.

**9. Incorrect `UTF-8-SIG` usage — the reverse mistake.**
```python
with open("plain_utf8_no_bom.txt", "w", encoding="utf-8-sig") as f:
    f.write("hello")
```
*Diagnose:* was a BOM actually wanted in this output file, or was this
simply copied from another example without considering the specific
downstream consumer (§24.3–§24.4)? *Corrected:* use plain
`encoding="utf-8"` unless a BOM is genuinely, specifically required by
whatever will read this file next.

**10. Incorrect normalization assumptions.**
```python
seen_names = set()

def is_duplicate(name: str) -> bool:
    is_dup = name in seen_names
    seen_names.add(name)
    return is_dup
```
*Diagnose:* what happens if the same visual name arrives twice, once
as precomposed and once as decomposed Unicode (§42.1)? *Corrected:*
normalize before comparing/storing:
`normalized = unicodedata.normalize("NFC", name)`.

## 63. Interview Questions

Beginner:
1. What is Unicode? (§4.2)
2. What is a code point? (§5.1)
3. What is encoding? What is decoding? (§10.1–§10.2)
4. Unicode vs. UTF-8 — what's the difference? (§4.3, §17.2)
5. ASCII vs. UTF-8 — what's the relationship between them? (§9.3)
6. Why is UTF-8 described as "variable width"? (§11.1, §12.1)

Intermediate:
7. What is a BOM? (§23.1)
8. What is `utf-8-sig`, and why does it exist? (§24.1–§24.2)
9. What is `UnicodeDecodeError`? What information does it give you?
   (§20.2)
10. What is `UnicodeEncodeError`? (§20.1)
11. What is mojibake, and why can it occur without raising any
    exception at all? (§21.1–§21.2)
12. What is newline translation, and why does Python perform it by
    default? (§29.1–§29.3)
13. What are `\n`, `\r`, and `\r\n`, and where does each convention
    come from historically? (§27.2–§27.3)
14. Why does `newline=""` matter specifically for CSV files? (§34.1)
15. `str` vs. `bytes` — what's the fundamental difference? (§6.1, §7.1)
16. `bytes` vs. `bytearray` — what's the difference? (§8.1)
17. What does `errors="ignore"` do, and why can it be dangerous?
    (§19.2, §19.4)

Advanced/production-oriented:
18. What is Python's UTF-8 mode, and why was it introduced? (§37.1–§37.2)
19. What's the difference between filesystem encoding and
    file-content encoding? (§38.1–§38.2)
20. What is Unicode normalization, and why can two visually identical
    strings fail an `==` comparison? (§42.1–§42.2)
21. How would you debug an unknown text encoding, systematically?
    (§22.2, §46.1)
22. How would you design a multilingual text-ingestion pipeline, at a
    high level? (§40.4, §50.2)

Scenario-based:
23. A file that displays correctly on a teammate's Windows machine
    shows corrupted characters on your Linux machine. What are the two
    most likely categories of root cause, and how would you
    distinguish between them? (§21–§22, §28.2, §46.1)
24. A CSV export from an older internal system fails to decode as
    UTF-8. What evidence would you gather before choosing an
    alternative encoding to try? (§22.2, §15.4)
25. A colleague suggests using `errors="ignore"` everywhere to "make
    the encoding errors go away" in a data pipeline. How would you
    respond, and what would you propose instead? (§19.4–§19.5)

## 64. Knowledge Check

**A. Conceptual**
1. In your own words, explain why "Unicode" and "UTF-8" are not
   synonyms.
2. Explain why decoding bytes with the wrong encoding does not always
   raise an exception.

**B. Code-reading**
3. What does the following print, and why?
```python
print(len("café"))
print(len("café".encode("utf-8")))
```

**C. Predict-the-output**
4. What is printed by:
```python
data = b"caf\xc3\xa9"
print(data.decode("utf-8", errors="replace"))
print(data.decode("ascii", errors="replace"))
```

**D. Byte/character questions**
5. Why does `b"hello"[0]` return an `int`, not a one-character
   `bytes` object?

**E. Encoding questions**
6. Why does `"é".encode("latin-1")` succeed while
   `"é".encode("ascii")` raises `UnicodeEncodeError`?

**F. Newline questions**
7. What is the difference between `newline=None` and `newline=""` on
   *reading* a file?

**G. Debugging**
8. You inspect a suspicious file's raw bytes and see it begins with
   `b'\xef\xbb\xbf'`. What does this tell you, and what should you do
   differently when opening the file?

**H. Unicode questions**
9. Why might `unicodedata.normalize("NFC", a) ==
   unicodedata.normalize("NFC", b)` be `True` even when `a == b` is
   `False`?

**I. Portability questions**
10. Why does a CSV file written by `csv.writer` use `\r\n` line
    endings even when the program runs on Linux?

**J. Production-design**
11. Why is `errors="strict"` (the default) generally the better choice
    for a production data-ingestion pipeline than `errors="ignore"`,
    even though `"ignore"` lets the program keep running without
    crashing?

---

**Answer key**

1. Unicode defines *which characters exist and what number identifies
   each one* (code points, §5); UTF-8 is one specific, particular rule
   for turning those numbers into bytes (§10.1) — other valid encodings
   (UTF-16, UTF-32) exist for the exact same Unicode character
   repertoire, producing entirely different bytes (§4.3, §17.2).
2. Some encodings (notably Latin-1, §15.2) accept *any* byte value at
   all as valid — decoding with the wrong such encoding "succeeds," in
   the sense of not raising, while silently producing incorrect text
   (mojibake, §21.2) instead of an error.
3. `4` then `5` — `len("café")` counts 4 Unicode characters/code
   points; `len("café".encode("utf-8"))` counts bytes, and `é` alone
   takes 2 UTF-8 bytes (§11.3–§11.4).
4. `café` then `caf�` — the UTF-8 decode succeeds cleanly with no
   replacement needed; the ASCII decode encounters `0xc3` and `0xa9`
   (both outside ASCII's range), each replaced with the Unicode
   replacement character `U+FFFD` (§19.2–§19.3).
5. Indexing a single position of `bytes` returns the raw numeric byte
   value at that position, as a plain Python `int` — this is `bytes`'
   own documented indexing behavior, genuinely different from `str`
   indexing, which returns a one-character string (§7.2).
6. `é` (`U+00E9`) falls within Latin-1's directly-representable
   `U+0000`–`U+00FF` range (§15.2), but is entirely outside ASCII's
   much smaller `0`–`127` range (§9.2) — encoding requires the target
   encoding to actually be able to represent every character present.
7. With `newline=None` (the default), any of `\n`/`\r`/`\r\n` found in
   the file are recognized as line boundaries and all translated to a
   single `\n` in the returned text. With `newline=""`, the same
   boundaries are recognized, but returned completely untranslated,
   exactly as they appeared in the file (§29.2, §29.4).
8. Those bytes are the UTF-8 BOM (§23.3) — the file should be opened
   with `encoding="utf-8-sig"` instead of plain `"utf-8"`, so the BOM
   is correctly recognized and stripped rather than left as a stray
   `﻿` character at the start of the decoded content (§24.2).
9. `a` and `b` can be two different, but Unicode-equivalent, code-point
   sequences representing the visually identical character — a
   precomposed form and a base-character-plus-combining-mark form,
   respectively (§42.1) — `==` compares code points exactly, with no
   awareness of this equivalence, while `normalize("NFC", ...)`
   converts both to the same canonical form first, making them
   genuinely equal afterward (§42.2).
10. `csv.writer`'s `lineterminator` default is `\r\n` by design,
    unconditionally, regardless of the operating system the code
    happens to run on — it is a property of the CSV dialect
    ([03-csv-files.md](03-csv-files.md)'s §15.2), not of the
    platform's own native line-ending convention (§28.1) — exactly why
    `newline=""` (§34.1) is needed, so Python's own separate,
    platform-based translation layer does not additionally interfere
    with it.
11. `errors="strict"` surfaces a genuine data problem immediately, at
    the precise point of failure, with full diagnostic information
    (§20.1–§20.2) — allowing it to be caught, logged, and handled
    deliberately (quarantined, reported, investigated). `errors="ignore"`
    instead silently discards the problematic data with **no** signal
    that anything went wrong at all (§19.4) — the pipeline "succeeds"
    while quietly producing corrupted or incomplete output, a
    significantly worse outcome for a production system than a clearly
    surfaced, immediately actionable failure.

## 65. Production Checklist

**Encoding**
- [ ] Encoding assumptions for every file/data source are documented,
      not left implicit (§59 principle 10).
- [ ] Explicit `encoding=` is used at every file-content I/O boundary
      (§25.1, §36.5).
- [ ] Multilingual data has been genuinely tested, not only ASCII
      examples (§59 principle 8).
- [ ] Legacy encodings, where they genuinely occur in real source
      data, have been identified explicitly, not assumed away (§15.4,
      §22).

**Decoding**
- [ ] Invalid bytes are handled with an intentional, documented
      `errors=` policy — `strict` by default (§19.5).
- [ ] No silent data loss occurs from an unconsidered `errors="ignore"`
      (§19.4).
- [ ] Useful diagnostic context (exact byte position, source file) is
      preserved and surfaced when a decode error occurs (§20.2, §46).

**Newlines**
- [ ] A deliberate newline policy is defined for each file type/format
      in use (default translation for most text; `newline=""` for
      CSV, §34.1).
- [ ] Cross-platform newline behavior has been tested, or at minimum
      explicitly understood and documented (§58).
- [ ] CSV newline handling is confirmed correct
      (`newline=""` + `csv`'s own line-ending logic, §34.1).

**Unicode**
- [ ] A normalization policy is defined wherever text comparison,
      deduplication, or use as a lookup key is genuinely needed
      (§42.4, §51.5).
- [ ] Confusable characters are considered wherever user-facing
      identifiers are compared or displayed for human verification
      (§45.1, §45.4).
- [ ] Invisible/control characters are considered as a genuine
      data-quality and security concern, not assumed impossible
      (§45.2–§45.4).

**Performance**
- [ ] Large files are streamed (`for line in file:`), not loaded whole
      with `.read()`, where size genuinely warrants it (§54.2).
- [ ] Unnecessary repeated encode/decode conversions are avoided
      (§54.1).
- [ ] Memory usage from decoding is considered explicitly for
      genuinely large text volumes (§54.1).

**Testing**
- [ ] UTF-8 and non-ASCII/multilingual content are both tested (§51.1).
- [ ] BOM-prefixed input is tested (§51.2).
- [ ] Invalid byte sequences are tested, confirming the expected
      exception is raised (§51.3).
- [ ] Multiple newline-convention variants, including mixed, are
      tested (§51.4).
- [ ] Unicode normalization behavior is tested where it is used
      (§51.5).
- [ ] Cross-platform behavior is tested or explicitly, deliberately
      reasoned about (§58).

**Observability**
- [ ] Encoding failures are identifiable — distinct from other kinds
      of failure, not lumped into one generic error category (§59
      principle 11).
- [ ] The specific source file/data involved in a failure is captured
      and reported.
- [ ] Byte position or line location is captured where practical, to
      speed diagnosis (§20's exception attributes, §46.1).

## 66. Final Mastery Checklist

You should be able to confidently say:

- [ ] I understand characters, distinctly from code points and bytes.
- [ ] I understand bytes, and why computers ultimately store and move
      only bytes.
- [ ] I understand Unicode, as a character repertoire distinct from
      any particular encoding.
- [ ] I understand code points, and can use `ord()`/`chr()` correctly.
- [ ] I understand ASCII, its limitations, and its relationship to
      UTF-8.
- [ ] I understand encoding and decoding as precise, distinct, named
      operations.
- [ ] I understand `str` vs. `bytes`, and why Python 3 refuses to mix
      them silently.
- [ ] I understand `bytearray` and when it is useful.
- [ ] I understand UTF-8 deeply, including its variable-width,
      self-synchronizing internal byte mechanics.
- [ ] I understand UTF-16, including surrogate pairs, and that it is
      not simply "two bytes per character."
- [ ] I understand UTF-32 and its fixed-width trade-off.
- [ ] I understand legacy encodings (Latin-1, Windows-1252) and why
      they still appear in real data.
- [ ] I can use `str.encode()` and `bytes.decode()` correctly,
      including their parameters.
- [ ] I understand every standard `errors=` handling mode, and know
      `strict` is the correct default for data integrity.
- [ ] I understand `UnicodeEncodeError` and `UnicodeDecodeError`, and
      can read their diagnostic attributes.
- [ ] I understand mojibake, including why it can occur without any
      exception being raised at all.
- [ ] I understand BOMs, and `utf-8-sig`, precisely.
- [ ] I understand `open(encoding=...)`, and why explicit encoding is
      always the correct default habit.
- [ ] I understand `newline=`, including every value's precise
      read/write behavior.
- [ ] I understand `\n`, `\r`, and `\r\n`, and where each convention
      comes from.
- [ ] I understand text mode vs. binary mode, and why `encoding=`
      is a text-mode-only concept.
- [ ] I understand Python's universal newline handling precisely, not
      as an oversimplified "it just normalizes everything."
- [ ] I can debug encoding problems and newline problems
      systematically.
- [ ] I understand filesystem encoding vs. file-content encoding as
      genuinely separate concerns.
- [ ] I understand Python's UTF-8 mode, including the PEP 686
      Python-3.15 default-behavior change.
- [ ] I understand Unicode normalization (NFC/NFD/NFKC/NFKD) and when
      it is, and is not, appropriate to apply.
- [ ] I understand grapheme-cluster limitations, and why `len(str)`
      does not always match user-perceived character count.
- [ ] I understand Unicode security and data-quality issues
      (confusables, invisible characters, malformed input).
- [ ] I can process multilingual data safely and correctly.
- [ ] I can write portable text-processing programs, robust to
      platform and encoding differences.
- [ ] I can test encoding and newline behavior with `pytest`.
- [ ] I can design a production-safe, well-documented text-ingestion
      pipeline.

With this foundation in place, you are ready for
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md),
where this module turns from file-format concerns toward building
programs that communicate clearly through the command line.
