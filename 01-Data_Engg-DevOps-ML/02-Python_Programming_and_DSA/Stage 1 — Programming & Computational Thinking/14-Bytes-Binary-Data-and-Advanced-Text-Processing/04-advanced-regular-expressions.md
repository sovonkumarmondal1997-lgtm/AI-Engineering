# Advanced Regular Expressions in Python

**Target:** Python 3.12+ (examples also work on Python 3.11 unless a note says otherwise).  
**Standard library:** `re`, `datetime`, `time`, `unittest`, `collections`.  
**Optional third-party tools:** [`regex`](https://pypi.org/project/regex/) for richer Unicode and matching features; `google-re2`/`re2` for a restricted, linear-time regex engine; `pytest` for parameterized tests; `lark` or `pyparsing` for grammars.

## Learning outcomes

By the end of this lesson, you should be able to:

- Select the correct `re` API: `search`, `match`, `fullmatch`, `findall`, `finditer`, `sub`, `split`, and `compile`.
- Build readable patterns using classes, quantifiers, anchors, alternation, groups, flags, and raw string literals.
- Use named/non-capturing groups, backreferences, lookarounds, verbose mode, substitution callbacks, spans, and named-group tokenization.
- Explain Unicode behavior in `str` patterns and how `bytes` patterns differ.
- Recognize and mitigate catastrophic backtracking and ReDoS without running intentionally dangerous benchmarks.
- Test patterns with positive, negative, boundary, and adversarial cases; parse logs responsibly; and know when a parser or ordinary string method is better.

## Prerequisites and scope

You should already know strings, slicing, exceptions, basic regular expressions, and text encodings. This lesson deepens regex for production use; it is not a complete Unicode-normalization, diffing, HTML, JSON, or date/time standards lesson. Python's built-in `re` is the default. Any third-party capability is labelled explicitly.

---

## 1. Pick the right matching API

A match object contains the matched text, groups, and offsets. A failed match returns `None`.

```python
import re

text = "request id=AB-123 finished"
pattern = re.compile(r"id=(?P<id>[A-Z]{2}-\d{3})")

print(pattern.search(text).group("id"))
print(pattern.match(text))
identifier = re.compile(r"[A-Z]{2}-\d{3}")
print(identifier.fullmatch("AB-123"))
print(identifier.fullmatch("AB-123!"))
```

Expected output:

```text
AB-123
None
<re.Match object; span=(0, 6), match='AB-123'>
None
```

The exact representation of a match object is shown for illustration; rely on its groups/spans, not the repr formatting.

| API | Meaning | Typical use |
|---|---|---|
| `re.search(p, s)` | First match anywhere | Find a field in a larger message |
| `re.match(p, s)` | Match at the start of `s` | Parse a prefix |
| `re.fullmatch(p, s)` | Entire string must match | Validate one complete field |
| `re.findall(p, s)` | Return all matches as a list | Small result sets; return shape depends on capturing groups |
| `re.finditer(p, s)` | Iterator of match objects | Large scans, offsets, named fields |
| `re.sub(p, repl, s)` | Replace matches | Redaction and transformations |
| `re.split(p, s)` | Split at matches | Structured delimiters; capturing groups are included in output |
| `re.compile(p, flags=0)` | Build reusable pattern object | Repeated use or a named, documented pattern |

**Validation rule:** use `fullmatch()` for a complete input field unless a deliberately anchored prefix grammar is required. `^...$` is not always a substitute: `$` can match before a final newline, and `MULTILINE` changes anchor behavior.

## 2. Pattern fundamentals

Use raw string literals (`r"..."`) for most regex patterns so Python string escapes do not consume backslashes before the regex engine sees them.

| Construct | Meaning | Example |
|---|---|---|
| `.` | Any character except newline by default | `a.c` |
| `\d`, `\w`, `\s` | Digit, word character, whitespace (Unicode-aware for `str` by default) | `\d+` |
| `[...]` | One character from a set/range | `[A-F0-9]` |
| `[^...]` | One character not in the set | `[^,]+` |
| `*`, `+`, `?` | Zero-or-more, one-or-more, optional | `ab?` |
| `{m}`, `{m,n}` | Exact or bounded repetitions | `\d{4}` |
| `*?`, `+?`, `??`, `{m,n}?` | Lazy versions; prefer the shortest match that allows the whole pattern to succeed | `<.*?>` |
| `^`, `$` | Start/end anchors; `MULTILINE` changes them | `^ERROR:` |
| `\A`, `\Z` | Absolute start/end of string in Python `re` | `\A[A-Z]+\Z` |
| `(abc)` | Capturing group | `(ha)+` |
| `(?:abc)` | Non-capturing group | `(?:ha)+` |
| `a|b` | Alternation | `cat|dog` |
| `\b` | Word boundary under the engine's definition of `\w` | `\bcat\b` |

Alternation is tried left-to-right. Put longer or more specific alternatives first when prefix overlap matters: `(?:==|=)` rather than `(?:=|==)` if you intend `==` to be one token. Quantifiers are greedy by default, but “greedy” means they try a longer match first, not that they always consume everything.

```python
import re

s = "<name>one</name><name>two</name>"
print(re.findall(r"<name>.*</name>", s))
print(re.findall(r"<name>.*?</name>", s))
```

Expected output:

```text
['<name>one</name><name>two</name>']
['<name>one</name>', '<name>two</name>']
```

This illustrates greediness only. Regex is not a robust HTML/XML parser: nesting, entities, malformed markup, and quoting make parsing substantially more complex.

### Escaping literal text

Use `re.escape()` when user-provided text should be matched literally, not interpreted as regex syntax.

```python
import re

literal = "file[1].txt"
pattern = re.compile(re.escape(literal))
print(bool(pattern.fullmatch("file[1].txt")))
print(bool(pattern.fullmatch("file1.txt")))
```

Output:

```text
True
False
```

`re.escape()` is for building **patterns** from literals; it is not a general-purpose replacement-string escape function.

## 3. Groups, flags, and readable patterns

### Capturing, named, and non-capturing groups

```python
import re

m = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", "built 2026-10-17")
print(m.group("year"), m.group(2), m.groupdict())
print(m.span(), m.start("month"), m.end("month"))
```

Output:

```text
2026 10 {'year': '2026', 'month': '10', 'day': '17'}
(6, 16) 11 13
```

`span()` is a half-open interval `(start, end)`, so `s[start:end]` is the matched text. Named groups make extraction code resilient to group-order changes. Use `(?:...)` for grouping without adding a result field.

### Backreferences

A backreference requires the same text as a previously captured group. It can help find repeated delimiters or simple duplicated words, but avoid using it to parse arbitrary nested languages.

```python
import re

pattern = re.compile(r"(?P<quote>['\"])(?P<body>.*?)(?P=quote)")
print(pattern.findall("'alpha' and \"beta\""))
```

Output:

```text
[("'", 'alpha'), ('"', 'beta')]
```

In a pattern, `\1` refers to the first capturing group and `(?P=name)` to a named group. In Python source, `\1` can also be interpreted as an octal escape in some contexts; raw strings and named backreferences are clearer.

### Flags and inline flags

- `re.IGNORECASE` / `re.I`: case-insensitive matching; Unicode case behavior has subtleties.
- `re.MULTILINE` / `re.M`: `^` and `$` also match line boundaries.
- `re.DOTALL` / `re.S`: `.` also matches newline.
- `re.ASCII` / `re.A`: makes shorthand classes such as `\w`, `\d`, `\s`, and word-boundary behavior ASCII-oriented for `str` patterns.
- `re.VERBOSE` / `re.X`: ignores unescaped pattern whitespace and allows comments outside character classes.

```python
import re

pattern = re.compile(r"""
    (?P<key> [A-Za-z_][A-Za-z0-9_]* )  # identifier-like key
    \s* = \s*
    (?P<value> [^;\n]* )              # value until semicolon/newline
""", re.VERBOSE)
print(pattern.search(" mode = fast; rest").groupdict())
print(bool(re.search(r"^warn", "info\nwarn: disk", re.MULTILINE)))
```

Output:

```text
{'key': 'mode', 'value': 'fast'}
True
```

Inline flags include `(?i)` for case-insensitive matching and scoped forms such as `(?i:abc)` for a region. In verbose mode, literal spaces and `#` inside patterns need escaping or placement in a character class when they should be matched literally. `re.VERBOSE` does not ignore whitespace inside character classes.

## 4. Lookarounds

Lookarounds assert context without consuming it:

- `(?=...)`: positive lookahead — the next text must match.
- `(?!...)`: negative lookahead — the next text must not match.
- `(?<=...)`: positive lookbehind — the preceding text must match.
- `(?<!...)`: negative lookbehind — the preceding text must not match.

```python
import re

text = "item=12 item=0 item=45x"
positive = re.findall(r"item=\d+(?=\s|$)", text)
nonzero = re.findall(r"(?<!\d)0*[1-9]\d*(?!\d)", "0 7 42 007")
print(positive)
print(nonzero)
```

Output:

```text
['item=12', 'item=0']
['7', '42', '007']
```

The second pattern identifies positive digit runs that are not adjacent to another digit; it does **not** reject leading zeros or parse numbers semantically. Use numeric conversion and explicit rules for that.

**Built-in `re` constraint:** lookbehind must have a fixed width. `(?<=ab)c` works; `(?<=a|bc)c` fails because alternatives have different widths; `(?<=\w+)x` fails because `\w+` is variable-width. If variable-length lookbehind is truly needed, consider the third-party `regex` package, or restructure the pattern to capture the preceding context. Do not add a dependency merely to avoid a simple, clearer parser.

## 5. Substitution, splitting, and token spans

### Replacement strings and callbacks

```python
import re

text = "user=alice; user=bob"
print(re.sub(r"user=(\w+)", r"user=<\1>", text))
# Named replacement references make the intent explicit.
print(re.sub(r"user=(?P<name>\w+)", r"user=<\g<name>>", text))

# A callback can make a decision for each match.
def redact(match):
    return f"token=[redacted:{len(match.group('secret'))} chars]"

print(re.sub(r"token=(?P<secret>[A-Za-z0-9_-]+)", redact, "token=abc123"))
```

Output:

```text
user=<alice>; user=<bob>
user=<alice>; user=<bob>
token=[redacted:6 chars]
```

For replacement strings, `\g<name>` and `\g<1>` avoid ambiguity, e.g. `r"\g<1>0"` means group 1 followed by `0`. Function replacements are preferable for conditional or computed output. Never log secrets just because a callback can inspect them.

### `split()` and capturing groups

```python
import re

print(re.split(r"[,;]\s*", "red, green;blue"))
print(re.split(r"([,;])\s*", "red, green;blue"))
```

Output:

```text
['red', 'green', 'blue']
['red', ',', 'green', ';', 'blue']
```

Capturing groups in a split pattern are included in the output. Prefer non-capturing groups if delimiters should not be returned.

### Named-group tokenization

A `finditer()` tokenizer must not silently skip invalid characters. The pattern below is useful for simple arithmetic-like input, but a production tokenizer should ensure each next match begins exactly where the previous one ended.

```python
import re

TOKEN = re.compile(r"""
    (?P<NUM>  \d+(?:\.\d+)? )
  | (?P<ID>   [A-Za-z_][A-Za-z0-9_]* )
  | (?P<OP>   [=+*/()\-] )
  | (?P<WS>   \s+ )
""", re.VERBOSE | re.ASCII)

def tokenize(source):
    pos = 0
    while pos < len(source):
        match = TOKEN.match(source, pos)
        if match is None:
            raise ValueError(f"unexpected character at offset {pos}: {source[pos]!r}")
        pos = match.end()
        if match.lastgroup != "WS":
            yield match.lastgroup, match.group()

print(list(tokenize("total = 3.5 + count")))
try:
    list(tokenize("total @ 3"))
except ValueError as exc:
    print(type(exc).__name__, str(exc))
```

Output:

```text
[('ID', 'total'), ('OP', '='), ('NUM', '3.5'), ('OP', '+'), ('ID', 'count')]
ValueError unexpected character at offset 6: '@'
```

The pattern uses an ASCII identifier policy and explicitly recognizes `=`, arithmetic operators, and parentheses. A tokenizer is not an expression parser: precedence, parentheses, and grammar validity are separate steps.

## 6. Unicode and bytes patterns

For a `str` pattern, `\w`, `\d`, and `\s` are Unicode-aware by default:

```python
import re

print(bool(re.fullmatch(r"\d+", "١٢٣")))  # Arabic-Indic decimal digits
print(bool(re.fullmatch(r"\w+", "café")))
print(bool(re.fullmatch(r"\s", "\u00A0")))  # no-break space
print(bool(re.fullmatch(r"\d+", "١٢٣", re.ASCII)))
```

Output:

```text
True
True
True
False
```

These shorthand classes are not a universal definition of “valid identifier”, “numeric”, or “whitespace” for every application. Specify the intended alphabet explicitly when the input grammar is protocol-defined. Unicode normalization is a separate operation; regex matching does not normalize text automatically.

`str` patterns match `str`; `bytes` patterns match `bytes`. They cannot be mixed in one match call. Bytes patterns are useful for ASCII delimiters in binary/log streams without decoding the whole input:

```python
import re

line = b"status=200 bytes=123\xff"
m = re.search(rb"status=(\d+)", line)
print(m.group(1), int(m.group(1)))
```

Output:

```text
b'200' 200
```

In bytes patterns, shorthand classes are ASCII-oriented; bytes are not Unicode text. Decode with a known encoding if language-aware text processing is required.

## 7. A bounded ISO-8601-like timestamp exercise

“ISO 8601” describes a broad family of date/time representations. The following is a deliberately narrow, documented subset, not a full ISO 8601 validator:

- Exactly `YYYY-MM-DD[T or space]HH:MM:SS`.
- Optional fractional seconds with 1–6 decimal digits.
- Optional timezone suffix `Z` or numeric offset `±HH:MM`.
- No reduced-precision dates, week dates, leap seconds, `24:00`, or timezone names.
- Regex validates shape and basic ranges; `datetime` validates calendar dates and clock fields.

```python
import re
from datetime import datetime

TIMESTAMP = re.compile(r"""
    (?P<date> \d{4}-\d{2}-\d{2} )
    [T ]
    (?P<time>
        (?:[01]\d|2[0-3]) : [0-5]\d : [0-5]\d
        (?: \.\d{1,6} )?
    )
    (?P<tz> Z | [+-](?:[01]\d|2[0-3]):[0-5]\d )?
""", re.VERBOSE | re.ASCII)

def valid_timestamp(value):
    m = TIMESTAMP.fullmatch(value)
    if not m:
        return False
    try:
        datetime.strptime(m.group("date") + " " + m.group("time").split(".")[0], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False
    # Validate fractional digits by the regex; validate offset shape/range by the regex.
    # This subset intentionally does not construct a timezone-aware datetime.
    return True

cases = [
    "2026-10-17T12:30:45Z",
    "2024-02-29 23:59:59.123456+05:30",
    "2025-01-01T00:00:00",
    "2023-02-29T12:00:00Z",
    "2026-10-17T24:00:00Z",
    "2026-10-17T12:30:60Z",
    "2026-10-17T12:30:45.1234567Z",
    "2026-10-17T12:30Z",
    "17-10-2026T12:30:45Z",
    "2026-10-17T12:30:45+05:30:00",
]
print([valid_timestamp(x) for x in cases])
```

Expected output:

```text
[True, True, True, False, False, False, False, False, False, False]
```

The offset range check here permits offsets through `23:59`, which is syntactically broad and not the range of real-world civil time zones. For a real application, enforce the narrower range your protocol allows and construct/validate a timezone-aware `datetime` explicitly. Python's `datetime` does not support leap seconds. Avoid naming a narrow custom pattern “ISO validator”.

## 8. Catastrophic backtracking and ReDoS

Backtracking engines explore alternatives when a later part of a pattern fails. Some patterns can cause a huge number of explored paths for a carefully chosen near-match. This is called catastrophic backtracking; when exposed to untrusted input it can become Regular Expression Denial of Service (ReDoS).

A classic risky shape is `(a+)+$`: repeated groups and overlapping quantifiers can partition the same run of `a` characters in many ways. A string of many `a` characters followed by a non-matching character forces the engine to reconsider those partitions. Runtime can grow exponentially. **Do not benchmark this pattern with long attacker-controlled strings.** Even a demonstration can hang a process.

Safer alternative when the intended grammar is “one or more lowercase a characters, then end”:

```python
import re

SAFE = re.compile(r"a+\Z")
print(bool(SAFE.fullmatch("aaaa")))
print(bool(SAFE.fullmatch("aaaa!")))
```

Output:

```text
True
False
```

This simpler pattern has no nested ambiguous repetition. If the real grammar needs more structure, redesign it rather than blindly swapping quantifiers.

### Mitigations

1. **Simplify and constrain the grammar.** Avoid overlapping alternatives and nested unbounded quantifiers where possible. Prefer explicit character classes and bounded repetitions.
2. **Bound input length** before matching untrusted data. A length cap is defense in depth, not a proof that a pattern is safe.
3. **Anchor or use `fullmatch()` appropriately.** This prevents accidental substring matches but does not automatically remove catastrophic backtracking.
4. **Use atomic groups or possessive quantifiers when semantically correct.** Python 3.11+ supports atomic groups `(?>...)` and possessive quantifiers such as `a++`; they prevent some backtracking, but can change which strings match. They are not a universal repair.
5. **Consider a restricted engine** such as Google's RE2 (`google-re2` Python package). RE2-family engines are designed to avoid backtracking blowups, but do not support every Python `re` feature (notably some backreferences/lookarounds). Check the exact package/API and pattern compatibility.
6. **Test safely.** Use bounded input sizes, an external process timeout for performance experiments, and production observability. Do not rely on a timeout that cannot interrupt a blocked in-process `re` call.

Python 3.11+ feature examples:

```python
import re

# Atomic group: once this group has matched, the engine will not backtrack into it.
atomic = re.compile(r"(?>a+)a")
# Possessive quantifier: a++ will not give back matched 'a' characters.
possessive = re.compile(r"a++a")
print(bool(atomic.fullmatch("aaa")))
print(bool(possessive.fullmatch("aaa")))
```

Output:

```text
False
False
```

Both fail because the first part consumes all `a` characters and cannot backtrack to leave one for the final `a`. On Python 3.10 and earlier these constructs raise `re.error` at compile time. Use them only when this stricter behavior matches the grammar you mean to express.

## 9. Performance and memory

- Compile once when a pattern is reused, especially when flags or naming make it part of the program's interface. The `re` module also has an internal cache, but explicit compiled patterns document intent.
- Use `fullmatch()` for whole-field validation and anchors when you need prefix/line semantics; anchoring can reduce needless searching but does not fix every complexity problem.
- Avoid needless `.*` prefixes such as `.*ERROR`; use `search(r"ERROR", line)` or `"ERROR" in line` if that is all you need.
- Prefer string methods (`startswith`, `endswith`, `partition`, `split`, `in`) for simple fixed delimiters.
- Use `finditer()` for large scans when you need one result at a time; `findall()` materializes a list and may consume substantial memory.
- A compiled pattern does not guarantee a fast pattern. Complexity is mostly about the pattern, engine, and input.

### Responsible benchmarking plan

For a real log-processing benchmark, do not start with a 1 GB file or adversarial pattern. First:

1. Create representative, sanitized sample lines and a known expected match count.
2. Compare a compiled `finditer()` pattern with a string-method or parser baseline.
3. Use `time.perf_counter()` and repeat each bounded run; report throughput, input size, Python version, CPU, and match count.
4. Scale input gradually and test malformed but bounded lines. Do not use the risky `(a+)+$` pattern on large inputs.
5. For very large files, stream line-by-line rather than loading the whole file. `mmap` may be appropriate for some workloads but is outside this lesson's scope; measure before adopting it.

## 10. Log parsing example

This example parses a common **shape** of Apache/Nginx combined access-log line. Real deployments vary; use a parser or a more carefully specified grammar if your log format differs. It intentionally places bounds on line length and checks the entire line.

```python
import re

COMBINED = re.compile(r'''
    (?P<host>\S+)\s+                         # remote host/address
    \S+\s+                                   # ident (often '-')
    \S+\s+                                   # authenticated user (often '-')
    \[(?P<time>[^\]\r\n]{1,64})\]\s+       # bracketed timestamp
    "(?P<request>[^"\r\n]{1,2048})"\s+     # quoted request
    (?P<status>[1-5][0-9]{2})\s+              # HTTP status, 100..599
    (?P<size>-|[0-9]{1,12})                    # bytes sent or '-'
''', re.VERBOSE | re.ASCII)

def parse_access_line(line):
    # The caller should pass one decoded line, not an arbitrary multi-line blob.
    if len(line) > 8192:
        raise ValueError("log line exceeds configured length limit")
    if "\n" in line or "\r" in line:
        # Remove at most one conventional line terminator, then reject embedded ones.
        if line.endswith("\r\n"):
            line = line[:-2]
        elif line.endswith("\n") or line.endswith("\r"):
            line = line[:-1]
        if "\n" in line or "\r" in line:
            return None
    m = COMBINED.fullmatch(line)
    if m is None:
        return None
    fields = m.groupdict()
    fields["status"] = int(fields["status"])
    fields["size"] = None if fields["size"] == "-" else int(fields["size"])
    return fields

sample = '203.0.113.7 - - [17/Oct/2026:03:15:00 +0000] "GET /health HTTP/1.1" 200 12'
parsed = parse_access_line(sample)
print(parsed["host"], parsed["status"], parsed["size"], parsed["request"])
print(parse_access_line('not a valid access log line'))
print(parse_access_line(sample + "\nforged second line"))
```

Output:

```text
203.0.113.7 200 12 GET /health HTTP/1.1
None
None
```

The regular expression limits selected field sizes and checks the entire record. The parser accepts at most one final LF, CRLF, or CR line terminator and rejects embedded line breaks; it does not fully validate HTTP request syntax or the timestamp's calendar semantics. Never assume a regex match means every field is semantically valid. If the source is adversarial, also enforce upstream line/frame limits and define behavior for malformed records.

### Bytes log fragments

When only ASCII delimiters/fields are needed, bytes regexes can avoid decoding the whole stream. Decode extracted text fields only after choosing a known encoding and error policy. A `bytes` regex is not a way to interpret arbitrary UTF-8 characters as Unicode categories.

## 11. Third-party `regex` package and engine trade-offs

The third-party package named `regex` is **not** Python's standard-library `re`. Install separately, for example `python -m pip install regex`, and pin/test its version in an application.

Common capabilities include:

- Unicode properties such as `\p{L}` (letters) and `\p{Script=Greek}`.
- `\X` for an extended grapheme cluster according to the package's Unicode implementation.
- Fuzzy matching with edit constraints.
- Recursive patterns for some nested structures.
- Variable-length lookbehind, unlike standard `re`.

These features can be useful, but add dependency, behavior/version, and performance considerations. Fuzzy matching is not the same as safe validation. Recursive patterns are not automatically a good parser. `\X` grapheme behavior depends on Unicode-version support. Benchmark and test the actual workload.

RE2-family engines make different trade-offs: predictable matching-time guarantees for a restricted feature set. If a pattern requires backreferences or lookaround unsupported by the selected engine, redesign the pattern or choose a different parsing approach; do not assume drop-in compatibility.

## 12. When regex is the wrong tool

| Problem | Better starting point | Why |
|---|---|---|
| HTML/XML | HTML/XML parser | Nesting, entities, malformed markup, quoting |
| JSON | `json` module | Escaping, nested objects/arrays, grammar |
| CSV | `csv` module | Quoted fields can contain delimiters/newlines |
| Nested expressions/DSL | Hand-written scanner or grammar library such as `lark` / `pyparsing` | Recursive grammar and precedence |
| Dates/times | `datetime` plus explicit accepted grammar; sometimes `dateutil` | Calendar and timezone semantics exceed shape matching |
| Email/URL validation | Purpose-built validator plus application policy | “Looks like” syntax is not complete validation or deliverability/reachability |
| Shell-like command strings | `shlex` for its documented shell-like syntax | Quoting/escaping rules are not just token separators |
| Fixed prefix/delimiter | `startswith`, `partition`, `split` | Simpler and often clearer |

`str.partition(separator)` splits once into `(before, separator, after)` and is often easier to reason about than a regex for a fixed delimiter. A scanner that advances one character/token at a time is a good next step when regexes become unreadable.

## 13. Table-driven tests

Test intended behavior, not merely a few successful matches. Include positive, negative, boundary, and adversarial-shaped inputs. Adversarial tests should remain bounded and should not deliberately trigger an expensive catastrophic case.

```python
import re
import unittest

IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,31}", re.ASCII)

class IdentifierTests(unittest.TestCase):
    def test_table(self):
        cases = [
            ("name", True),
            ("_private", True),
            ("A9", True),
            ("", False),
            ("9name", False),
            ("has-dash", False),
            ("a" * 32, True),
            ("a" * 33, False),
            ("name\n", False),
            ("é", False),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(IDENTIFIER.fullmatch(value) is not None, expected)

    def test_adversarial_shape_is_bounded(self):
        # The pattern has bounded repetition and the input length is deliberately modest.
        value = "a" * 100 + "!"
        self.assertIsNone(IDENTIFIER.fullmatch(value))

if __name__ == "__main__":
    unittest.main()
```

Run it with `python lesson_tests.py` after saving the code as `lesson_tests.py`. The expected test result is two passing tests. This is a teaching example, not proof against every possible attack; tests should reflect actual production limits and threat models.

## 14. Guided exercises

### Exercise 1 — `match`, `search`, and `fullmatch`

For `text = "ID: ABC-123 done"`, find the identifier anywhere, determine whether the whole string is an identifier, and validate a standalone identifier `ABC-123`.

**Solution:**

```python
import re
p = re.compile(r"[A-Z]{3}-\d{3}")
text = "ID: ABC-123 done"
print(p.search(text).group())
print(p.fullmatch(text))
print(p.fullmatch("ABC-123").group())
```

Output:

```text
ABC-123
None
ABC-123
```

### Exercise 2 — redact a secret

Replace `api_key=...` with `api_key=[REDACTED]`, using a callback that reports the length but never returns the secret.

**Solution:**

```python
import re

def redact_key(m):
    return f"api_key=[REDACTED:{len(m.group('key'))} chars]"

line = "service started api_key=abc_DEF-123"
print(re.sub(r"api_key=(?P<key>[A-Za-z0-9_-]+)", redact_key, line))
```

Output:

```text
service started api_key=[REDACTED:11 chars]
```

### Exercise 3 — tokenization must not skip errors

Extend the tokenizer so `,` is a delimiter token. Keep the scanner's position check, and reject `@` with its offset rather than silently ignoring it.

**Solution:** add `| (?P<COMMA> , )` to the alternation before the whitespace group; the `TOKEN.match(source, pos)` loop already raises on an unknown character.

## 15. Independent exercises

1. Write a named-group pattern for `level=INFO code=204` and return a dictionary. Reject missing fields.
2. Write a `re.VERBOSE` pattern for a bounded key-value pair with optional spaces around `=`. Document every group.
3. Parse 10 timestamp inputs using the subset in section 7; add cases for invalid leap day, too many fractional digits, and malformed timezone.
4. Review a pattern with nested quantifiers and explain the ambiguous partitions that cause backtracking. Rewrite it with a simpler grammar and a length limit; do not benchmark the risky original on long input.
5. Parse a log file line-by-line with a compiled pattern, counting valid and invalid lines without storing all match objects.
6. Decide whether regex, `partition`, `csv`, `json`, `shlex`, or a grammar library best fits a quoted, nested input format. Explain the grammar feature driving your choice.

## 16. Common mistakes and fixes

| Mistake | Why it fails | Better approach |
|---|---|---|
| Use `match()` to find text in the middle | It only tries at position zero | Use `search()` or scan explicitly |
| Use `search()` to validate an entire field | Valid substring may hide trailing junk | Use `fullmatch()` |
| Assume `.` includes newlines | It does not unless `DOTALL` is enabled | Use `re.S` only when appropriate, or a specific class |
| Use `.*` to parse nested markup | Regex lacks general nested-grammar handling | Use a parser |
| Capture every grouping expression | Group tuple/list shape changes | Use `(?:...)` for structural groups |
| Put `finditer()` over a pattern and assume no gaps | `finditer()` skips unmatched text | Use a scanner with `match(text, pos)` when every character must be consumed |
| Use nested unbounded quantifiers on untrusted text | Can cause catastrophic backtracking | Simplify, bound input, test safely, or use a suitable restricted engine |
| Compile in every loop iteration | Adds noise/work and hides pattern intent | Compile once for reuse |
| Treat `\w` as a universal identifier rule | Unicode and application policy differ | Define the accepted alphabet explicitly |
| Use `re.escape()` on a replacement string | It escapes for patterns, not replacement syntax | Use a callback or proper replacement references |
| Use regex alone to validate dates | Shape is not calendar validity | Parse fields with `datetime` and enforce the supported subset |
| Trust a match as semantic validation | Regex may only validate lexical shape | Validate ranges, cross-field rules, and application policy separately |

## 17. Roadmap self-check — answers

### 1. Show an input that makes `(a+)+$` take exponential time and fix the pattern.

The dangerous shape is a long run of `a` characters followed by a character that prevents the final `$` from succeeding, for example conceptually `"a" * n + "!"`. The nested repetitions allow many ways to partition the run among inner and outer repetitions; the final failure forces the backtracking engine to explore those alternatives. Do not run a long benchmark of this expression in-process. If the intended language is simply one or more `a` characters to the end, use `a+\Z` or `fullmatch(r"a+", value)`. For more complex input, simplify the grammar, cap length, and consider a restricted engine if its feature set fits.

### 2. Write a verbose regex for ISO-8601 timestamps with an optional timezone and test 10 cases.

Section 7 provides a verbose, named-group pattern and 10 table cases. It deliberately accepts only `YYYY-MM-DD[T or space]HH:MM:SS`, optional 1–6 fractional digits, and optional `Z` or `±HH:MM`. Regex validates shape/ranges; `datetime` checks the calendar date. It is not a full ISO 8601 validator and does not cover leap seconds, every legal representation, or full timezone semantics.

### 3. Explain `match`, `search`, and `fullmatch`.

`match()` only tries at the beginning; `search()` scans for the first occurrence anywhere; `fullmatch()` requires the entire input to match. Use `fullmatch()` for complete-field validation, `search()` for finding an occurrence in larger text, and `match()` for a prefix parser that advances from a known offset.

## 18. Glossary

- **Anchor:** Assertion about a position, such as start/end of string or line.
- **Backreference:** Reuse of text captured by an earlier group.
- **Catastrophic backtracking:** Exponential-like exploration of alternatives for certain patterns and inputs.
- **Character class:** Set/range describing one character, e.g. `[A-Z]`.
- **Compiled pattern:** Reusable object returned by `re.compile()`.
- **Greedy/lazy quantifier:** Quantifier that tries longer/shorter matches first.
- **Lookaround:** Zero-width assertion about preceding/following text.
- **Match span:** Half-open character or byte interval `(start, end)`.
- **Named group:** Capturing group identified by a name.
- **ReDoS:** Denial of service caused by expensive regular-expression matching.
- **Scanner/tokenizer:** Code that advances through input while classifying each token and rejecting unexpected gaps.
- **Unicode-aware shorthand:** `\w`, `\d`, and `\s` behavior on `str` patterns unless ASCII mode is enabled.

## 19. Completion checklist

- [ ] I can explain the difference among `search`, `match`, and `fullmatch`.
- [ ] I can read/write character classes, quantifiers, anchors, alternation, and groups.
- [ ] I can use named groups, `groupdict`, non-capturing groups, backreferences, flags, verbose mode, and lookarounds.
- [ ] I know that standard-library `re` requires fixed-width lookbehind.
- [ ] I can use `sub` callbacks, `\g<name>`, `split`, `re.escape`, and match spans correctly.
- [ ] My tokenizer detects unexpected gaps instead of silently skipping characters.
- [ ] I understand Unicode shorthand classes and the distinction between `str` and `bytes` patterns.
- [ ] I can identify ReDoS risk and avoid unsafe adversarial benchmarks.
- [ ] I know Python 3.11+ atomic/possessive syntax and its semantic trade-offs.
- [ ] I can explain when `regex`, RE2, string methods, or a parser is appropriate.
- [ ] I can test positive, negative, boundary, and bounded adversarial cases.
- [ ] I can parse log lines incrementally with explicit size limits and malformed-line behavior.

**Lesson complete when:** you can explain why each pattern is safe for its intended input, show tests for edge cases, and justify why regex is the right tool for the grammar.
