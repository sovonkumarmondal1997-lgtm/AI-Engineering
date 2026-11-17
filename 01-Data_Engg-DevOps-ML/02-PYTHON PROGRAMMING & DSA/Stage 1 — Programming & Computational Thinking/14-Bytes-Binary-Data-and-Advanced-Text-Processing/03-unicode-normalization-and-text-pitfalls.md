# Unicode Normalization and Text Pitfalls

> **Target:** Python 3.12+  
> **Scope:** Unicode representation, normalization, matching, inspection, safe text processing, and practical text-pipeline pitfalls.  
> **Third-party notes:** `regex`, `PyICU`, and `ftfy` are optional packages; examples label them explicitly. Unicode property data comes from the Unicode database bundled with the running Python, so exact property results can evolve across Python releases even when the source code is unchanged.

## Learning outcomes

By the end of this lesson, you should be able to:

- Distinguish Unicode code points, encoded bytes, glyphs, and grapheme clusters, and explain what `len(str)` counts.
- Diagnose visually similar strings that compare unequal and choose an appropriate normalization and matching policy.
- Explain and demonstrate `lower()` versus `casefold()`, Unicode character predicates, and the four Unicode normalization forms.
- Inspect categories, names, combining classes, whitespace, invisible characters, and suspicious bidirectional controls.
- Handle encoding errors, surrogate escapes, mojibake, language-sensitive sorting, filenames, and LLM preprocessing without assuming one universal text-cleaning rule.
- Write tests for normalization and matching behavior, including CJK text and emoji.

## Prerequisites

You should already know Python strings, indexing and slicing, basic encodings (`str.encode()` and `bytes.decode()`), exceptions, functions, and basic tests. Module 1.5 introduced encodings; this lesson focuses on Unicode text pitfalls rather than repeating a full encoding lesson. Basic regular-expression knowledge is enough for the small `re.split()` example.

## 1. Text, code points, encodings, and what “a character” means

Python `str` is a sequence of Unicode code points. A code point is written `U+` followed by hexadecimal digits. A Unicode encoding maps code points to bytes. UTF-8 uses one to four bytes per Unicode scalar value; UTF-16 uses one or two 16-bit code units (a supplementary code point uses a surrogate pair); UTF-32 uses 32-bit code units. The exact bytes depend on the encoding and, for UTF-16/32, the byte order and BOM convention where applicable.

A **glyph** is a visual shape drawn by a font. A **grapheme cluster** is an approximation of a user-perceived character: it may consist of multiple code points, such as a base letter plus combining accent, or an emoji joined with zero-width joiners. Rendering depends on font, shaping engine, platform, and context; code points alone do not fully specify appearance.

```python
text = "Aé🙂"
print(len(text))
print([f"U+{ord(ch):04X}" for ch in text])
print(text.encode("utf-8").hex(" "))
```

Expected output:

```text
3
['U+0041', 'U+00E9', 'U+1F642']
41 c3 a9 f0 9f 99 82
```

`len(text)` returns **3 code points**, not bytes, grapheme clusters, terminal columns, or visible glyphs. In UTF-8, `len(text.encode("utf-8"))` is 7 for this example. Do not use byte length as a proxy for character count, nor `len(str)` as a proxy for how many characters a user sees.

### `ord`, `chr`, and named escapes

```python
print(ord("A"))
print(chr(0x1F642))
print("\\N{LATIN SMALL LETTER E WITH ACUTE}")
print("\N{LATIN SMALL LETTER E WITH ACUTE}")
print("\u00E9", "\U0001F642")
```

Expected output:

```text
65
🙂
\N{LATIN SMALL LETTER E WITH ACUTE}
é
é 🙂
```

The third line deliberately prints a literal backslash escape because it is written as `"\\N{...}"`; the fourth line demonstrates the named escape interpreted by Python as `é`. `ord()` accepts a one-character string; `chr()` accepts an integer in `0..0x10FFFF` and raises `ValueError` outside that range. Not every code point is an assigned character, and surrogate code points are a special case discussed later.

## 2. Visually identical strings and equality

The word “café” can use U+00E9 (`é`) or U+0065 followed by U+0301 (`e` plus COMBINING ACUTE ACCENT). They can render identically while comparing unequal because Python compares code-point sequences.

```python
composed = "café"
decomposed = "cafe\u0301"
print(composed == decomposed, len(composed), len(decomposed))
print([f"U+{ord(ch):04X}" for ch in composed[-1:]])
print([f"U+{ord(ch):04X}" for ch in decomposed[-2:]])
```

Expected output:

```text
False 4 5
['U+00E9']
['U+0065', 'U+0301']
```

This matters for deduplication, joins, database keys, search, cache keys, and indexes. Do not “fix” this by assuming visual appearance defines identity. Instead, define a documented normalization and matching policy for the particular field and apply it consistently at ingestion and comparison boundaries.

## 3. Case conversion and character predicates

### `lower()` versus `casefold()`

`lower()` converts text to lowercase. `casefold()` is designed for caseless matching and can make more transformations; it can change length. For example, German sharp s (`ß`) case-folds to `ss`.

```python
print("Straße".lower())
print("Straße".casefold())
print("Straße".casefold() == "STRASSE".casefold())
```

Expected output:

```text
straße
strasse
True
```

**Use:** `casefold()` is usually a better building block for language-independent caseless matching than `lower()`. **Limit:** it is not a universal language-specific search algorithm and does not resolve all linguistic equivalences. The Turkish dotted capital `İ` case-folds to `i` plus COMBINING DOT ABOVE; dotless `ı` is distinct. Do not blindly strip combining marks afterward: that may merge distinctions important in a language. If product requirements specify locale-specific matching, implement and test that policy explicitly.

### `isalpha()`, `isdigit()`, `isdecimal()`, and `isnumeric()`

These methods classify Unicode characters, not just ASCII digits and letters. Their definitions differ:

```python
samples = ["7", "²", "四", "⅕", "A", "é"]
for ch in samples:
    print(ch, ch.isalpha(), ch.isdecimal(), ch.isdigit(), ch.isnumeric())
```

Expected output:

```text
7 False True True True
² False False True True
四 True False False True
⅕ False False False True
A True False False False
é True False False False
```

- `isdecimal()` is the narrowest of these numeric tests; it accepts Unicode decimal digits suitable for base-10 digit strings.
- `isdigit()` includes decimal digits and additional digit characters such as superscript two.
- `isnumeric()` is broader still and includes numeric characters such as vulgar fractions.
- `isalpha()` is based on Unicode alphabetic properties; it is not a test for “ASCII letters” or for a valid username policy.

An empty string returns `False` for these predicates. For ASCII-only identifiers or protocol fields, use an explicit allow-list or a clearly specified grammar instead of relying on broad Unicode predicates.

## 4. The four normalization forms

Python's standard library `unicodedata.normalize(form, text)` implements Unicode normalization. Canonical normalization makes canonically equivalent sequences comparable. Compatibility normalization additionally folds distinctions that Unicode treats as compatibility-equivalent.

| Form | Operation | Typical uses | Main caveat |
|---|---|---|---|
| **NFC** | Canonical decomposition, then composition where possible | Common default for stored human text and consistent equality | Does not fold all compatibility characters or perform case-insensitive matching |
| **NFD** | Canonical decomposition | Analysis of combining marks; some processing pipelines | Often expands one code point into several; not necessarily how text should be stored |
| **NFKC** | Compatibility decomposition, then composition | Search keys and constrained identifiers when policy explicitly permits compatibility folding | Can erase meaningful distinctions, e.g. ligatures, width, superscript formatting |
| **NFKD** | Compatibility decomposition | Search/analysis pipelines that need compatibility decomposition | Most aggressive here; output may be visually and semantically different |

```python
import unicodedata as ud

samples = ["é", "e\u0301", "ﬁ", "Ｆ", "²"]
for value in samples:
    print(repr(value), "NFC=", repr(ud.normalize("NFC", value)),
          "NFD=", repr(ud.normalize("NFD", value)),
          "NFKC=", repr(ud.normalize("NFKC", value)),
          "NFKD=", repr(ud.normalize("NFKD", value)))
```

The exact output is deterministic for a given Unicode database version. Important transformations include:

- `"é"` and `"e\u0301"` become equal after NFC or NFD.
- The ligature `ﬁ` becomes `fi` under NFKC/NFKD, but not under NFC/NFD.
- Full-width `Ｆ` becomes ordinary `F` under NFKC/NFKD.
- Superscript `²` becomes `2` under NFKC/NFKD.

### Choosing a normalization policy

For general human text storage, NFC is often a reasonable interoperability default. For a search key, a deliberately lossy pipeline such as NFKC + casefold + whitespace canonicalization may be useful. Keep the original text when fidelity matters, and treat the search key as a derived value.

```python
import unicodedata as ud

def search_key(text: str) -> str:
    """Example policy for broad search, not a universal identity function."""
    normalized = ud.normalize("NFKC", text).casefold()
    return " ".join(normalized.split())

assert search_key("  ﬁne\u00A0Art ") == search_key("FINE art")
```

The policy intentionally equates some forms that may be distinct in other contexts. Never assume that one normalization form is correct for every language, identifier, legal name, password, source-code token, or database key. Normalization does not detect malicious lookalikes, transliterate languages, remove all invisibles, or guarantee human-perceived equality.

### Normalize consistently before equality, hashing, joins, and indexing

Python strings are immutable and their hashes reflect their exact code-point sequence. If a system normalizes only at lookup but not at insertion, records can be missed or duplicated. Choose one policy for a field, apply it at every boundary, and use the same canonical key for deduplication, joins, and indexes. Preserve the original input if auditability or exact reproduction matters. Do not normalize passwords or opaque tokens unless the relevant specification explicitly requires it.

## 5. Inspecting Unicode properties

`unicodedata` exposes Unicode database properties useful for diagnosis and limited validation.

```python
import unicodedata as ud

for ch in ["A", "é", "\u0301", "\u200B", "\u202E"]:
    print(repr(ch), ud.name(ch, "<unnamed>"), ud.category(ch), ud.combining(ch))
```

Interpretation:

- `name()` returns the Unicode character name, or the supplied fallback for unnamed code points.
- `category()` returns a two-letter general category such as `Lu` (uppercase letter), `Mn` (nonspacing mark), `Zs` (space separator), or `Cf` (format character).
- `combining()` returns the canonical combining class as an integer; zero does not mean “not visible” or “safe.”

Unicode properties are useful signals, not a complete security validator. Legitimate scripts use combining marks and format controls. A category allow-list must reflect the application's supported languages and field semantics.

### Accent stripping: useful, lossy, and language-dependent

A common search transformation decomposes text with NFD and removes combining marks:

```python
import unicodedata as ud

def strip_combining_marks(text: str) -> str:
    decomposed = ud.normalize("NFD", text)
    without_marks = "".join(ch for ch in decomposed
                             if not ud.category(ch).startswith("M"))
    return ud.normalize("NFC", without_marks)

print(strip_combining_marks("café"))
print(strip_combining_marks("São Tomé"))
```

Expected output:

```text
cafe
Sao Tome
```

This is a search convenience, not faithful transliteration. Some marks carry meaning; not every accented letter decomposes into a base letter plus a mark; and removing marks can collapse distinctions in many languages. It does not convert every non-Latin script to Latin. Keep original text and test the policy against the languages your product supports.

## 6. Whitespace, invisible characters, and safe inspection

Some characters look like spaces or are not visibly rendered:

- **U+200B ZERO WIDTH SPACE** (`\u200b`) is a format character and is not the same as ordinary whitespace.
- **U+FEFF BOM / ZERO WIDTH NO-BREAK SPACE**: at the start of some encoded streams it serves as a byte-order mark; inside decoded text it may appear as U+FEFF. Do not indiscriminately delete every occurrence.
- **U+00A0 NO-BREAK SPACE** looks space-like but has different line-breaking behavior.
- **U+200E/U+200F** are left-to-right/right-to-left marks; other bidi controls can affect display order.
- Smart quotes (`“ ” ‘ ’`) differ from ASCII quote characters.

Use `repr()`, code-point dumps, and Unicode names before cleaning. Avoid printing untrusted text raw into terminals, logs, or code review interfaces if it may contain terminal controls or bidi formatting.

```python
import unicodedata as ud

def describe(text: str) -> list[str]:
    return [f"{ch!r} U+{ord(ch):04X} {ud.name(ch, '<unnamed>')} "
            f"category={ud.category(ch)}" for ch in text]

for item in describe("A\u00A0B\u200BC\uFEFFD"):
    print(item)
```

A cleaning function must be field-specific. For example, an ingestion system might reject zero-width spaces in an ASCII account ID, but preserve them in quoted source text or natural-language content. If you remove a character, log a safe representation and retain the original when traceability is needed.

### `str.split()` versus regex splitting

With no separator, `str.split()` collapses runs of Unicode whitespace and omits leading/trailing empty fields. A regular expression `\s` matches Unicode whitespace by default for Python `str` patterns, but splitting has different edge behavior and can preserve empty fields depending on the pattern and input.

```python
import re

text = "  alpha\u00A0beta\t\n gamma  "
print(text.split())
print(re.split(r"\s+", text.strip()))
print("a\u200bb".split())
```

Expected output:

```text
['alpha', 'beta', 'gamma']
['alpha', 'beta', 'gamma']
['a\u200bb']
```

Zero-width space is not matched by ordinary `str.split()` whitespace handling. `re` is used here only for the specific splitting comparison; see the dedicated regex lesson for broader pattern design.

### An example field-specific cleaner

```python
import unicodedata as ud

BIDI_CONTROLS = {"\u061C", "\u200E", "\u200F", "\u202A", "\u202B",
                 "\u202C", "\u202D", "\u202E", "\u2066", "\u2067",
                 "\u2068", "\u2069"}

def clean_account_label(raw: str) -> str:
    """Example policy: normalize and trim; reject controls/bidi marks."""
    value = ud.normalize("NFC", raw).strip()
    if any(ch in BIDI_CONTROLS or ud.category(ch) in {"Cc", "Cf", "Cs"}
           for ch in value):
        raise ValueError("disallowed control or surrogate in account label")
    return value
```

This is an illustrative policy, not a universal username validator. It still allows many Unicode letters and symbols. Real identity systems should define an explicit character repertoire, normalization and case policy, length limits, script policy, and confusable-handling rules.

## 7. Grapheme clusters, emoji, and user-visible length

A single visible unit may contain multiple code points:

- `e` + combining accent;
- an emoji plus a skin-tone modifier;
- a flag built from two regional-indicator code points;
- an emoji ZWJ sequence such as a family emoji.

The Python standard library does not provide a general extended grapheme-cluster iterator. The third-party `regex` package supports `\X`.

```python
# Optional dependency: python -m pip install regex
import regex

samples = ["e\u0301", "👍🏽", "🇮🇳", "👨‍👩‍👧‍👦", "中文"]
for value in samples:
    print(repr(value), "code_points=", len(value),
          "graphemes=", len(regex.findall(r"\X", value)))
```

Expected grapheme counts for current Unicode grapheme rules are commonly:

```text
'é' code_points= 2 graphemes= 1
'👍🏽' code_points= 2 graphemes= 1
'🇮🇳' code_points= 2 graphemes= 1
'👨‍👩‍👧‍👦' code_points= 7 graphemes= 1
'中文' code_points= 2 graphemes= 2
```

The exact code-point count shown for the family sequence is 7 (four people and three joiners). Grapheme segmentation rules and Unicode data evolve, so package and Unicode versions can affect edge cases. If `regex` is not installed, the optional example cannot run; do not silently replace `\X` with a hand-written emoji heuristic.

For UI truncation, define whether the limit is code points, grapheme clusters, display columns, or encoded bytes. Truncating by code points can split a grapheme cluster; truncating UTF-8 bytes can split a multibyte sequence. A grapheme-safe truncator is not automatically terminal-column-safe, because glyph widths and rendering vary.

## 8. Encodings, errors, surrogates, and JSON

Encoding and decoding are explicit operations:

```python
text = "naïve 漢字"
raw = text.encode("utf-8")
print(raw.hex())
print(raw.decode("utf-8") == text)

try:
    b"\xff".decode("utf-8")
except UnicodeDecodeError as exc:
    print(type(exc).__name__)

try:
    "🙂".encode("ascii")
except UnicodeEncodeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
6e61c3af766520e6bca2e5ad97
True
UnicodeDecodeError
UnicodeEncodeError
```

Prefer strict errors when malformed data should be rejected. `errors="replace"` preserves progress but loses information. `errors="ignore"` silently drops bytes or characters and is rarely appropriate for data pipelines where fidelity matters. `backslashreplace` is useful for readable diagnostics when encoding text to a limited encoding.

### `surrogateescape`

On supported Python codecs such as UTF-8, `surrogateescape` can preserve undecodable bytes in the range 0x80–0xFF by representing them as low surrogate code points U+DC80–U+DCFF. Re-encoding with the same encoding and error handler can round-trip those original bytes.

```python
raw = b"name-\xff.txt"
text = raw.decode("utf-8", errors="surrogateescape")
print(repr(text))
print(text.encode("utf-8", errors="surrogateescape") == raw)
```

Expected output:

```text
'name-\udcff.txt'
True
```

This is a byte-preservation mechanism, not valid ordinary Unicode text for display or interchange. Do not pass surrogate-escaped strings to components that expect Unicode scalar values without understanding their behavior.

### Lone surrogates and JSON

Python strings can contain surrogate code points, but Unicode scalar-value text should not. JSON interoperability around lone surrogates is tricky: Python's `json` module may escape them when serializing with `ensure_ascii=True`, while other implementations may reject them or handle them differently. Do not use JSON as a generic lossless container for arbitrary undecodable bytes. If bytes must be transported, use a specified binary-safe representation such as base64 or a documented byte field, and test the receiving implementation.

## 9. Security: confusables, bidirectional text, identifiers, and IDNs

### Homoglyphs and confusables

Characters from different scripts can look alike: Latin `a` (U+0061) and Cyrillic `а` (U+0430) are distinct code points. NFC or NFKC does not make all visually confusable characters equal. A display name that looks like a trusted brand may therefore be a spoof.

Defenses depend on context: use explicit allow-lists for constrained identifiers, consider permitted script combinations, flag mixed-script labels, display canonical identifiers safely, and use established Unicode security guidance and confusable-detection libraries where the risk warrants it. Category checks alone cannot detect every confusable.

### Bidirectional controls and Trojan Source

Bidirectional formatting controls can change the visual ordering of text while the underlying logical order remains different. In source code, comments or string literals containing bidi controls can make code appear misleading in some editors. Inspect suspicious files with escaped code-point dumps, use editor/compiler warnings where available, and establish source-review policies. Do not strip bidi controls from all human-language text indiscriminately: some scripts legitimately use directional marks.

### Identifiers and PEP 3131

Python identifiers follow language-defined rules based on Unicode identifier properties and are normalized to NFKC during parsing (PEP 3131). That does **not** mean arbitrary application usernames should accept every Python-valid identifier. For account IDs, tenant keys, hostnames, or authorization principals, define and enforce a narrower policy and compare the canonical key consistently. Do not normalize secrets or passwords unless their protocol says to.

### IDNs and punycode

Internationalized domain names use IDNA rules to represent labels containing non-ASCII characters. Punycode is an encoding used by IDNA; it is not a general-purpose text normalizer and does not itself prove a domain is trustworthy. For domain validation, use a maintained IDNA implementation appropriate to the required standard, compare the normalized ASCII form where relevant, and consider confusable display attacks. Avoid implementing IDNA by hand.

## 10. Sorting: code-point order is not linguistic collation

Python's default string ordering is lexicographic by code points. That is deterministic, but not a human-language collation policy. Alphabetical order varies by language and locale; accents, digraphs, and case may be ordered differently.

```python
words = ["ångström", "apple", "zebra", "äther"]
print(sorted(words))  # deterministic code-point order, not universal dictionary order
```

For a simple locale-aware key, Python provides `locale.strxfrm()` after setting a suitable locale. Locale availability and behavior depend on the operating system and installed locales, so do not assume a locale name exists everywhere. The process locale is often global state; changing it inside concurrent application code can be unsafe.

```python
import locale

# Illustrative only: this locale may not be installed on your system.
# locale.setlocale(locale.LC_COLLATE, "de_DE.UTF-8")
# sorted_names = sorted(names, key=locale.strxfrm)
```

For robust internationalized sorting, ICU collation through the optional third-party `PyICU` package is often more configurable. Choose locale and collation strength explicitly, pin or document ICU/data versions if reproducibility matters, and test with real names in supported languages. Normalization alone does not implement linguistic sorting.

## 11. Text preprocessing for LLMs and tokenizers

Tokenizers do not count “characters” in the same way Python does. Depending on the tokenizer, text may be represented as subword units, bytes, or byte-fallback pieces. A tokenizer can map visually similar or normalized strings to different token sequences. Normalizing before tokenization may improve consistency for a particular pipeline, but it also changes the input and can affect model behavior.

Recommended pipeline discipline:

1. Preserve the original source when auditability or exact reproduction matters.
2. Decide whether normalization is required by the dataset, retrieval, or model contract; document the form and version assumptions.
3. Apply the same policy at indexing and query time for retrieval systems.
4. Use the tokenizer's own token-counting API for context-window limits; do not estimate token count with `len(text)`.
5. Truncate by tokens using the actual tokenizer when token budget is the constraint. If preserving human text, truncate at a safe boundary and avoid splitting grapheme clusters where possible.
6. Test multilingual input, CJK, emoji, combining marks, and whitespace under the actual tokenizer.

Byte-fallback tokenizers can represent bytes that ordinary vocabulary pieces do not cover, but this does not mean all Unicode strings have equal token cost or that arbitrary character truncation is safe. Token counts are tokenizer/model-specific; record the tokenizer name and version in reproducible data pipelines.

## 12. Mojibake, mixed encodings, and repair

**Mojibake** is garbled text produced when bytes are decoded with the wrong encoding, or text is re-encoded incorrectly. Example: UTF-8 bytes for `café` decoded as Windows-1252 may appear as `cafÃ©`. Once bytes have been lost or replaced, repair may be impossible or ambiguous.

```python
original = "café"
wrong = original.encode("utf-8").decode("cp1252")
print(wrong)
```

Expected output:

```text
cafÃ©
```

Do not blindly “repair” every suspicious string. Prefer to return to the original bytes and determine the actual encoding from source-system metadata or a documented protocol. Detection tools make guesses; they cannot reliably infer an encoding for every arbitrary byte sequence.

The third-party `ftfy` package can repair common forms of mojibake in some text. Treat it as a heuristic cleanup step, not proof of original bytes or encoding. Pin its version, retain source data, and test on representative multilingual examples before applying it to production data.

## 13. Filenames and cross-platform normalization

Filesystems differ in how they store or compare Unicode names. Some environments may expose decomposed forms, while others commonly use composed forms; behavior depends on filesystem and platform. Do not assume every macOS filesystem always stores NFD or that every Linux/Windows filesystem enforces NFC.

For a data pipeline that compares names across systems, consider maintaining a separate normalized comparison key while preserving the original path. Detect collisions before normalizing: two distinct original names may collapse to one key. Never rename files solely on a normalization guess without a collision policy and reversible logging. Path security also requires path-separator, traversal, and platform-specific checks; Unicode normalization alone is not path validation.

## 14. Tests and round-trip invariants

Tests should encode the policy, not assert that all visually similar strings must be equal. The following test functions use only the standard library and can run with `python lesson_unicode_tests.py` if saved as a `.py` file. They test composed/decomposed text, whitespace, case folding, invisible characters, emoji/CJK code-point behavior, and UTF-8 round trips.

```python
import unicodedata as ud


def search_key(text: str) -> str:
    return " ".join(ud.normalize("NFKC", text).casefold().split())


def test_composed_and_decomposed() -> None:
    a, b = "é", "e\u0301"
    assert a != b
    assert ud.normalize("NFC", a) == ud.normalize("NFC", b)


def test_whitespace_policy() -> None:
    assert " ".join(" a\u00A0\tb ".split()) == "a b"


def test_casefold() -> None:
    assert "Straße".casefold() == "STRASSE".casefold()


def test_invisible_char_is_not_silently_assumed_whitespace() -> None:
    assert "a\u200bb".split() == ["a\u200bb"]
    assert "\u200b" not in "a b"


def test_emoji_and_cjk_code_points() -> None:
    assert len("👍🏽") == 2
    assert len("🇮🇳") == 2
    assert len("中文") == 2


def test_utf8_round_trip() -> None:
    values = ["café", "中文", "🙂", "e\u0301", "" ]
    for value in values:
        assert value.encode("utf-8").decode("utf-8") == value


def test_normalization_is_idempotent() -> None:
    values = ["café", "e\u0301", "ﬁ", "中文", "👍🏽"]
    for form in ("NFC", "NFD", "NFKC", "NFKD"):
        for value in values:
            once = ud.normalize(form, value)
            assert ud.normalize(form, once) == once


def test_invisible_and_directional_characters_are_inspectable() -> None:
    sample = "a\u200bb\u200fc“d”\ufeff"
    assert "\u200b" in sample
    assert "\u200f" in sample
    assert "\ufeff" in sample
    assert ud.name("\u200b") == "ZERO WIDTH SPACE"
    assert ud.name("\u200f") == "RIGHT-TO-LEFT MARK"
    assert ud.name("\ufeff") == "ZERO WIDTH NO-BREAK SPACE"


def test_encode_and_decode_errors_are_explicit() -> None:
    try:
        b"\xff".decode("utf-8")
    except UnicodeDecodeError:
        pass
    else:
        raise AssertionError("invalid UTF-8 must fail under strict decoding")
    try:
        "🙂".encode("ascii")
    except UnicodeEncodeError:
        pass
    else:
        raise AssertionError("non-ASCII text must fail under strict ASCII encoding")


def test_search_key_policy() -> None:
    assert search_key("  ﬁne\u00A0Art ") == search_key("FINE art")


if __name__ == "__main__":
    for test in [test_composed_and_decomposed, test_whitespace_policy,
                 test_casefold, test_invisible_char_is_not_silently_assumed_whitespace,
                 test_emoji_and_cjk_code_points, test_utf8_round_trip,
                 test_normalization_is_idempotent,
                 test_invisible_and_directional_characters_are_inspectable,
                 test_encode_and_decode_errors_are_explicit,
                 test_search_key_policy]:
        test()
        print(f"PASS {test.__name__}")
```

Expected output:

```text
PASS test_composed_and_decomposed
PASS test_whitespace_policy
PASS test_casefold
PASS test_invisible_char_is_not_silently_assumed_whitespace
PASS test_emoji_and_cjk_code_points
PASS test_utf8_round_trip
PASS test_normalization_is_idempotent
PASS test_invisible_and_directional_characters_are_inspectable
PASS test_encode_and_decode_errors_are_explicit
PASS test_search_key_policy
```

The suite was executed successfully in the available Python 3.13.5 environment. The lesson targets Python 3.12+; Unicode property data and grapheme segmentation edge cases can vary with the runtime's Unicode database and optional package version. For more extensive coverage, use property-based testing (for example, the optional third-party `hypothesis` package) to generate Unicode strings and assert invariants such as `normalize(form, normalize(form, s)) == normalize(form, s)` for each supported normalization form. Property tests must not assert that normalization is reversible; compatibility normalization is intentionally lossy.

## 15. Guided exercise: define a `slugify()` policy

A slug is a URL-friendly identifier derived from text. There is no universally correct slugification rule. For this exercise, use a deliberately simple policy:

1. Normalize to NFKD and case-fold.
2. Remove combining marks.
3. Keep ASCII lowercase letters and digits; turn runs of other characters into a single hyphen.
4. Strip hyphens at the ends.
5. CJK characters and emoji are not transliterated; if no ASCII letters or digits remain, return an empty slug.

This is a lossy display/search convenience, not a security identity key. Real applications should decide whether to transliterate CJK, preserve non-Latin scripts, append a stable ID to avoid collisions, and handle empty results.

```python
import unicodedata as ud


def slugify(text: str) -> str:
    value = ud.normalize("NFKD", text).casefold()
    value = "".join(ch for ch in value if not ud.category(ch).startswith("M"))
    out: list[str] = []
    separator_pending = False
    for ch in value:
        if "a" <= ch <= "z" or "0" <= ch <= "9":
            if separator_pending and out:
                out.append("-")
            out.append(ch)
            separator_pending = False
        else:
            separator_pending = True
    return "".join(out).strip("-")


assert slugify("Crème brûlée") == "creme-brulee"
assert slugify("Hello, World!") == "hello-world"
assert slugify("Straße") == "strasse"
assert slugify("中文🙂") == ""
assert slugify("  A__B  ") == "a-b"
print("slugify examples passed")
```

Expected output:

```text
slugify examples passed
```

**Why this solution behaves this way:** it implements the exercise's stated ASCII-only policy. NFKD exposes many combining marks; the function removes all Unicode mark categories, then replaces any non-ASCII-alphanumeric run with one separator. That deliberately drops CJK text and emoji. It can cause collisions (`"résumé"` and `"resume"` both become `resume`), so do not use the slug as a unique database key without collision handling.

## 16. Common mistakes and corrections

| Mistake | Correction |
|---|---|
| Assuming `len(text)` counts visible characters | It counts code points; use grapheme segmentation when user-perceived length matters |
| Assuming equal appearance means equal strings | Inspect code points and apply a documented normalization policy |
| Applying NFKC everywhere | Use compatibility folding only where its lossy equivalences are acceptable |
| Using `lower()` for every caseless comparison | Consider `casefold()`, while testing language-specific behavior |
| Treating `isnumeric()` as an ASCII-digit validator | Use an explicit grammar or allow-list for constrained fields |
| Removing every format character | Inspect and handle field-by-field; some controls are meaningful in legitimate text |
| Assuming normalization prevents homoglyph spoofing | Add identifier policy, script/confusable checks, and safe display practices |
| Sorting names with `sorted()` and calling it alphabetical | Use a specified locale/ICU collation policy for human-facing sorting |
| Truncating text by bytes or arbitrary code points | Use token-aware limits and safe grapheme boundaries as appropriate |
| Repairing mojibake without preserving the source | Prefer original bytes and encoding metadata; treat repair as heuristic |
| Normalizing filenames without collision detection | Compute keys, detect collisions, preserve originals, and define a rename policy |
| Treating a successful encode/decode round trip as proof all inputs are valid | Test strict error behavior and the actual data contract |

## 17. Roadmap self-check answers

### 1. Why are `"é"` and `"é"` unequal, and how do you make them equal?

The first commonly contains U+00E9; the second contains U+0065 and U+0301. Python compares the underlying code-point sequences, so they are unequal without normalization. Applying the same canonical normalization form (commonly NFC) makes these canonically equivalent representations compare equal: `unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b)`. This should be a field-level policy applied consistently, not an assumption that all visually similar strings are equivalent.

### 2. When is NFKC preferable to NFC?

NFKC is useful when a search or constrained-identifier policy intentionally treats compatibility forms as equivalent, such as the `ﬁ` ligature and `fi`, full-width letters and ordinary-width letters, or superscript digits and ordinary digits. NFC preserves these compatibility distinctions. NFKC is lossy and can collapse distinctions users or a domain may care about, so it should not be applied indiscriminately to passwords, exact source text, legal names, or arbitrary natural-language content.

### 3. Build `slugify()` that handles accents, case, whitespace and symbols, with tests including emoji and CJK input.

See Section 15 for a complete function and assertions. It normalizes with NFKD, case-folds, removes combining marks, maps runs of non-ASCII-alphanumeric characters to hyphens, and strips edge hyphens. Tests cover accents, mixed case, whitespace, symbols, German sharp s, emoji, and CJK. The policy explicitly returns an empty slug for CJK-only or emoji-only input because transliteration is outside its scope; a production slug system must define collision handling and whether non-Latin scripts should be preserved or transliterated.

## Glossary

- **Code point:** A numbered value in the Unicode code space, written `U+....`.
- **Encoding:** A mapping between Unicode text and bytes, such as UTF-8.
- **Glyph:** A rendered visual shape for text.
- **Grapheme cluster:** A sequence of code points treated as one user-perceived character under Unicode segmentation rules.
- **Canonical equivalence:** Different code-point sequences representing the same abstract text under Unicode canonical equivalence.
- **Compatibility equivalence:** A broader equivalence that folds formatting or presentation distinctions, used by NFKC/NFKD.
- **Case folding:** A Unicode transformation for caseless matching, available as `str.casefold()`.
- **Combining mark:** A character that may modify a preceding base character; category names include `Mn`, `Mc`, and `Me`.
- **Mojibake:** Garbled text caused by incorrect decoding or re-encoding.
- **Confusable/homoglyph:** A character or sequence that looks similar to another but has a different identity.
- **IDN / punycode:** Internationalized domain name handling and an encoding used by IDNA for non-ASCII labels.
- **Collation:** Rules for ordering strings for a language or locale.
- **Surrogate escape:** An error handler that preserves certain undecodable bytes using surrogate code points for later round-tripping.

## Completion checklist

- [ ] I can distinguish code points, bytes, glyphs, and grapheme clusters and explain `len(str)`.
- [ ] I can diagnose composed/decomposed text and choose a consistent normalization policy.
- [ ] I can explain NFC/NFD/NFKC/NFKD and the trade-offs of compatibility folding.
- [ ] I understand `lower()`, `casefold()`, and the Turkish dotted/dotless-I caveat.
- [ ] I can distinguish `isdecimal()`, `isdigit()`, `isnumeric()`, and `isalpha()`.
- [ ] I can inspect Unicode names, categories, combining classes, whitespace, and invisible controls.
- [ ] I know why normalization does not solve confusables, bidi spoofing, IDNs, or identifier security by itself.
- [ ] I can select grapheme-aware counting when appropriate and account for third-party dependency/version behavior.
- [ ] I can reason about encoding errors, `surrogateescape`, mojibake, and JSON interoperability.
- [ ] I can explain collation, tokenizer token counts, filename normalization, and round-trip tests.
- [ ] I completed the slug exercise and understand why its output is lossy and may collide.
