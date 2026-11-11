# 05 — `difflib`, `textwrap`, and String Utilities

> **Baseline:** Python 3.12+. The standard-library examples run without third-party packages. Optional tools (`rapidfuzz`, `rich`, `tabulate`, `wcwidth`, Jinja2, and MinHash libraries) are identified as dependencies. Python 3.14 template strings are a preview only, not baseline syntax.

## Learning outcomes

By the end of this lesson, you should be able to:

- Produce readable unified, context, and inline diffs; explain similarity scores and their limits.
- Use `SequenceMatcher` opcodes and matching blocks, and recognize `autojunk` and scaling pitfalls.
- Wrap and format prose, logs, and fixed-width reports with `textwrap`, `string`, and `str` methods.
- Use f-string format specifications deliberately, including alignment, fill, signs, separators, precision, `!r`, and debug `=`.
- Build a tested CLI typo-suggestion feature with a cutoff calibrated to the application.
- Select an appropriate matching metric or library, and keep templates separate from SQL, shell, and HTML safety.

## Prerequisites

You should know basic Python strings, lists, loops, functions, exceptions, f-strings, file reading, and simple tests. Familiarity with unit tests helps when using diffs in assertion messages. Unicode normalization and regular expressions are background topics here, not the subject of this lesson.

---

## 1. Start with the right tool

| Need | Good starting point | Important boundary |
|---|---|---|
| Explain line changes | `difflib.unified_diff` | It compares sequences; it does not understand program semantics. |
| Show inline hints | `difflib.ndiff` | Its `?` guide lines are heuristic visual hints. |
| Show context around edits | `difflib.context_diff` | Output is a textual diff format, not a patch guarantee. |
| Generate an HTML comparison | `difflib.HtmlDiff` | Escape or sanitize untrusted labels/content for the output context. |
| Compare sequences heuristically | `SequenceMatcher` | `ratio()` is not Levenshtein distance or a calibrated probability. |
| Suggest nearby words | `get_close_matches` | Useful for small candidate lists, not large-scale entity resolution. |
| Wrap paragraphs | `textwrap` | Width counts characters, not terminal display cells. |
| Format small reports | f-strings and `str` methods | ANSI escapes, wide CJK glyphs, and combining marks affect display width. |
| Match millions of names | blocking + a purpose-built matcher | Do not compare every query with every candidate using Python loops. |

## 2. `difflib`: compare text and sequences

### 2.1 Unified diff, context diff, and `ndiff`

A diff describes changes between sequences. Pass lines (usually from `splitlines(keepends=True)` or `readlines()`) so newline behavior remains explicit.

```python
import difflib

old = "name=service\nretries=2\n".splitlines(keepends=True)
new = "name=service\nretries=3\n".splitlines(keepends=True)
print("".join(difflib.unified_diff(
    old, new, fromfile="before.conf", tofile="after.conf"
)), end="")
```

Expected output:

```text
--- before.conf
+++ after.conf
@@ -1,2 +1,2 @@
 name=service
-retries=2
+retries=3
```

`unified_diff()` yields lines with `---`/`+++` headers and `@@` hunk headers. Its default `lineterm="\n"` is convenient when input lines retain line endings. If inputs do not include newline characters, choose `lineterm` deliberately and join results consistently.

```python
import difflib

print("".join(difflib.context_diff(
    ["mode=dev\n"], ["mode=prod\n"], "old", "new"
)), end="")
print(list(difflib.ndiff(["colour\n"], ["color\n"])))
```

Output (the context diff ends with a newline; `repr` is omitted here):

```text
*** old
--- new
***************
*** 1 ****
! mode=dev
--- 1 ----
! mode=prod
['- colour\n', '?     -\n', '+ color\n']
```

`context_diff()` shows surrounding context using `***`/`---` headers and `!`, `-`, `+` markers. `ndiff()` produces an inline-oriented sequence: `- ` lines are removed, `+ ` lines added, `  ` lines unchanged, and `? ` lines indicate character-level hints. Exact guide-line content depends on the comparison; do not parse `ndiff()` as a stable machine protocol.

`HtmlDiff` produces a complete HTML comparison table:

```python
from difflib import HtmlDiff
from html import escape

untrusted_label = "<img src=x>"
html = HtmlDiff().make_file(
    ["status: old"], ["status: new"],
    fromdesc=escape(untrusted_label), todesc="After", context=True,
)
assert "<table" in html
assert "&lt;img src=x&gt;" in html
```

The assertion is the expected behavior; this snippet does not print the full HTML. In particular, `fromdesc` and `todesc` are interpreted as unescaped HTML: escape untrusted descriptions with `html.escape()` before passing them. Treat the resulting document as HTML output and follow the embedding application’s context-specific policy; do not blindly escape the entire generated table, which would display markup instead of rendering it.

### 2.2 Files, preprocessing, and test failures

Read text with a deliberate encoding and compare lines. For directories, `filecmp` can identify same/different files at a basic level; use `difflib` to explain text differences. A directory-wide recursive diff needs explicit traversal, error handling, and policies for binary files and symlinks; it is not a one-call feature of `difflib`.

Whitespace- or case-insensitive comparisons must be a deliberate transformation. Preserve original lines for display, and compare normalized copies:

```python
import difflib

old = ["Host = API\n", "Retries = 2\n"]
new = ["host=api\n", "retries=3\n"]

def comparison_key(line: str) -> str:
    # This example ignores all whitespace and case for matching only.
    return "".join(line.split()).casefold()

old_keys = [comparison_key(line) for line in old]
new_keys = [comparison_key(line) for line in new]
print(old_keys == new_keys)
# Keys were preprocessed into strings without newline terminators; join the
# generated diff records explicitly so headers and changed lines stay separate.
print("\n".join(difflib.unified_diff(
    old_keys, new_keys, "old-key", "new-key", lineterm=""
)))
```

Output:

```text
False
--- old-key
+++ new-key
@@ -1,2 +1,2 @@
 host=api
-retries=2
+retries=3
```

The transformation above is only an example: removing all whitespace would be wrong if whitespace is meaningful (for example, in a programming language string literal). Other comparisons may use `line.rstrip()`, normalize only selected spaces, or case-fold values but preserve keys. A diff of transformed keys is less readable than a diff of original text, so production tools often use transformed keys for alignment and original text for display.

In tests, include a diff when an assertion fails:

```python
import difflib

expected = "alpha\nbeta\n"
actual = "alpha\nBETA\n"
if actual != expected:
    print("".join(difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile="expected", tofile="actual",
    )), end="")
```

This is useful for snapshots and generated reports. Snapshot tests should still review whether the change is correct; a diff explains a change but does not decide correctness.

### 2.3 `SequenceMatcher`: similarity and edit structure

```python
from difflib import SequenceMatcher, get_close_matches

matcher = SequenceMatcher(None, "tide", "diet")
print(round(matcher.ratio(), 3))
print(SequenceMatcher(None, "kitten", "sitting").get_opcodes())
print(SequenceMatcher(None, "abcXYZdef", "abc123def").get_matching_blocks())
print(get_close_matches("pyhton", ["python", "pytest", "pylint"]))
```

Expected output on Python 3.12+:

```text
0.25
[('replace', 0, 1, 0, 1), ('equal', 1, 4, 1, 4), ('replace', 4, 5, 4, 5), ('equal', 5, 6, 5, 6), ('insert', 6, 6, 6, 7)]
[Match(a=0, b=0, size=3), Match(a=6, b=6, size=3), Match(a=9, b=9, size=0)]
['python']
```

`ratio()` is in the range 0–1; higher means more similar according to `SequenceMatcher`'s matching-block heuristic. It is **not** a probability, and it is not a general-purpose edit-distance score. The ratio can depend on argument order for some inputs. Calibrate cutoffs against representative labeled examples rather than treating a particular score as universally meaningful.

`get_opcodes()` returns tuples `(tag, i1, i2, j1, j2)`. `tag` is one of `equal`, `replace`, `delete`, or `insert`; slices `a[i1:i2]` and `b[j1:j2]` describe the operation. `get_matching_blocks()` returns matching runs `(a_index, b_index, size)` and ends with a sentinel block of size zero. These are useful for highlighting or constructing explanations, not for recovering semantic edits.

`autojunk` and repetitive data: by default, `SequenceMatcher` uses a heuristic for sufficiently long sequences to treat very frequent elements as “popular” and avoid some expensive matching work. This can affect results for repetitive sequences (for example, long runs of the same line or character). Set `autojunk=False` only after measuring and understanding the consequences; it can substantially increase runtime on repetitive data. It is not a universal accuracy switch.

Complexity: `SequenceMatcher` can take quadratic time in the worst case; expected behavior depends on sequence structure. Comparing every one of N names to every one of M names adds N×M pair comparisons even before per-pair matching cost. `difflib` is excellent for human-readable diffs and small candidate lists, but is usually not the right engine for millions of fuzzy comparisons.

## 3. Typo suggestions with a justified cutoff

`get_close_matches(word, possibilities, n=3, cutoff=0.6)` returns up to `n` strings whose similarity exceeds `cutoff`, ranked by similarity. The default cutoff is a library default, not a product requirement.

```python
from difflib import get_close_matches

COMMANDS = ("deploy", "describe", "delete", "doctor", "diff")

def suggest_command(word: str) -> list[str]:
    # Small fixed command vocabulary; tune cutoff from observed typos.
    return get_close_matches(word, COMMANDS, n=2, cutoff=0.65)

print(suggest_command("deply"))
print(suggest_command("unknown-command"))
```

Expected output:

```text
['deploy']
[]
```

The `0.65` cutoff is an illustrative starting value for this tiny command list, not a universal threshold. Evaluate candidate cutoffs against a labeled set of real valid commands and likely typos. Consider false suggestions, misspellings that are genuinely ambiguous, case handling, and whether normalization should be applied consistently. For security-sensitive command selection, a suggestion must never silently execute a guessed command: ask the user to choose explicitly.

Table-driven tests:

```python
from difflib import get_close_matches

COMMANDS = ("deploy", "describe", "delete", "doctor", "diff")
def suggest_command(word: str) -> list[str]:
    return get_close_matches(word, COMMANDS, n=2, cutoff=0.65)

CASES = [
    ("deply", ["deploy"]),
    ("unknown-command", []),
    ("delete", ["delete"]),
]
for query, expected in CASES:
    actual = suggest_command(query)
    assert actual == expected, (query, actual, expected)
```

The ordering is deterministic for this vocabulary and Python implementation, but when several candidates have close scores, test the behavior you require rather than assuming a score margin. If using a larger vocabulary, tests should include near-ties and valid words that resemble each other.

## 4. `textwrap`: make prose readable

`textwrap` operates on Python strings and character counts; it does not account for terminal display width, ANSI color sequences, wide CJK characters, or combining marks.

```python
import textwrap

text = "Text tools make command-line explanations easier to read."
print(textwrap.wrap(text, width=24))
print(textwrap.fill(text, width=24))
```

Output:

```text
['Text tools make command-', 'line explanations easier', 'to read.']
Text tools make command-
line explanations easier
to read.
```

- `wrap(text, width=...)` returns a list of lines.
- `fill(...)` joins wrapped lines with newline characters.
- `dedent(...)` removes common leading indentation, useful for docstrings and embedded templates.
- `indent(text, prefix, predicate=None)` adds a prefix to selected lines. Without a predicate, blank lines are not prefixed.
- `shorten(text, width, placeholder=" [...] ")` collapses whitespace and shortens to the width including the placeholder. If the placeholder is longer than the width, the result can still be longer than the requested width; validate placeholder/width if strict width is required.

```python
import textwrap

block = """
    first line
        nested line
"""
print(repr(textwrap.dedent(block)))
print(repr(textwrap.indent("one\n\ntwo", "> ")))
print(textwrap.shorten("A long description for a report", width=18, placeholder="…"))
```

Output:

```text
'\nfirst line\n    nested line\n'
'> one\n\n> two'
A long…
```

`shorten()` collapses whitespace before truncating, so it is not suitable when original spacing is significant. For fixed-width table cells, create a dedicated truncation function and decide how the ellipsis counts toward the width.

```python
def truncate(text: str, width: int, marker: str = "…") -> str:
    if width < 0:
        raise ValueError("width must be non-negative")
    if len(text) <= width:
        return text
    if width == 0:
        return ""
    if len(marker) > width:
        return marker[:width]
    return text[:width - len(marker)] + marker

assert truncate("abcdef", 4) == "abc…"
assert truncate("abc", 4) == "abc"
assert truncate("abcdef", 0) == ""
```

This function uses code-point length, not display columns. Use a display-width-aware tool when terminal cells must align.

## 5. The `string` module and useful `str` methods

### 5.1 Constants and template APIs

The `string` module exposes constants including `ascii_letters`, `ascii_lowercase`, `ascii_uppercase`, `digits`, `hexdigits`, `octdigits`, `punctuation`, and `whitespace`. These are explicit character sets, not a universal definition of every Unicode letter or digit. For example, `string.digits` contains ASCII digits.

```python
import string

print(string.ascii_lowercase[:5], string.digits, string.hexdigits[:6])
```

Output:

```text
abcde 0123456789 012345
```

`string.Template` uses `$name` or `${name}` placeholders and is useful for simple substitution with a restricted template syntax. `substitute()` raises `KeyError` for missing values; `safe_substitute()` leaves some missing/invalid placeholders unresolved and is not a security sanitizer.

```python
from string import Template, Formatter

print(Template("Hello, $name!").substitute(name="Mina"))
print(list(Formatter().parse("{user}:{count:d}")))
```

Output:

```text
Hello, Mina!
[('', 'user', '', None), (':', 'count', 'd', None)]
```

`string.Formatter` exposes parsing and formatting hooks for brace-based formatting. It is not the same as `string.Template`, and neither API should be treated as a sandbox for untrusted template authors.

### 5.2 `str` methods for parsing and display

```python
line = "key=value=tail"
print(line.partition("="))
print(line.rpartition("="))
print("a\nb\r\nc\r".splitlines())
print("prefix_data.csv".removeprefix("prefix_"))
print("report.csv".removesuffix(".csv"))
```

Output:

```text
('key', '=', 'value=tail')
('key=value', '=', 'tail')
['a', 'b', 'c']
data.csv
report
```

`partition(sep)` splits at the first occurrence; `rpartition(sep)` at the last. Both always return a 3-tuple. If the separator is missing, `partition()` returns `(original, "", "")`; `rpartition()` returns `("", "", original)`. `splitlines()` recognizes multiple line boundaries and, unlike `split("\n")`, does not normally create a final empty element just because the string ends with a newline.

`removeprefix()` and `removesuffix()` remove a literal prefix/suffix at most once. They are not general substring replacement methods.

`translate()` maps characters by code point using a translation table; `str.maketrans()` creates one:

```python
table = str.maketrans({"-": " ", "_": " ", "!": None})
print("hello-world_test!".translate(table))
```

Output: `hello world test`

`None` deletes a mapped character. `translate()` is handy for simple character-level cleanup, but deleting punctuation blindly can change meaning.

Other common methods:

```python
print("42".zfill(5))
print("cat".center(7, "-"))
print("cat".ljust(6, "."))
print("a\tb".expandtabs(4))
print("valid_name2".isidentifier())
print("not valid".isidentifier())
print("{name}={value}".format_map({"name": "mode", "value": "safe"}))
```

Output:

```text
00042
--cat--
cat...
a   b
True
False
mode=safe
```

`zfill()` handles a leading sign specially (for example, `"-7".zfill(4)` is `"-007"`). `center()` and `ljust()` measure string length in code points, not terminal columns. `expandtabs(tabsize)` expands tab characters relative to the current column. `isidentifier()` checks Python identifier syntax, not whether a name is safe, non-confusable, available, or a valid identifier in another language/runtime. `format_map()` looks up fields in a mapping; do not let untrusted users supply arbitrary format strings.

## 6. f-string format mini-language and fixed-width reports

A format specification has the general shape `[fill][align][sign][#][0][width][grouping][.precision][type]` with details varying by type. Learn the pieces you use; do not memorize this as a promise that every combination works for every value.

```python
amounts = [("alpha", 3.14159), ("beta", 1234.5)]
for name, value in amounts:
    print(f"{name:<10}{value:>12,.2f}")
```

Output:

```text
alpha           3.14
beta        1,234.50
```

Explanation:

- `<10`: left-align in a minimum width of 10.
- `>12`: right-align in a minimum width of 12.
- `,`: group thousands with commas for supported numeric types.
- `.2f`: fixed-point notation with two digits after the decimal point.
- Width is a minimum, not a truncation limit. Long values expand the field.

```python
print(f"{'item':*^9}")
print(f"{42:+d} {42:08d} {-42:08d}")
value = "a\nb"
print(f"{value!r}")
name, count = "jobs", 7
print(f"{name=} {count=}")
print(f"{0.125:.1%}")
```

Output:

```text
**item***
+42 00000042 -0000042
'a\nb'
name='jobs' count=7
12.5%
```

- `*^9`: use `*` as fill and center in width 9.
- `+d`: show a sign for positive and negative integers.
- `08d`: decimal integer padded with zeros to a minimum width of 8; sign placement is handled by formatting.
- `!r`: convert using `repr()` before formatting, making escapes/quotes visible.
- `name=` debug syntax (Python 3.8+) includes the expression text and its representation; spacing and conversion behavior can be customized.
- `.1%`: percentage formatting multiplies by 100 and displays one decimal place.

A fixed-width report should state its policy for long fields and numbers. Right-align numbers, use thousands separators, and truncate labels deliberately rather than assuming width will clip them:

```python
def truncate(text: str, width: int, marker: str = "…") -> str:
    if width < 0:
        raise ValueError("width must be non-negative")
    if len(text) <= width:
        return text
    if width == 0:
        return ""
    if len(marker) > width:
        return marker[:width]
    return text[:width - len(marker)] + marker

rows = [("ingest", 12345), ("validation", 987), ("very-long-stage-name", 1000000)]
print(f"{'STAGE':<16} {'ROWS':>12}")
print("-" * 29)
for stage, count in rows:
    print(f"{truncate(stage, 16):<16} {count:>12,}")
print("-" * 29)
print(f"{'TOTAL':<16} {sum(count for _, count in rows):>12,}")
```

Output:

```text
STAGE                    ROWS
-----------------------------
ingest                 12,345
validation                987
very-long-stage…    1,000,000
-----------------------------
TOTAL                1,013,332
```

For real terminal alignment with CJK text, combining marks, or emoji, Python character count is insufficient. `wcwidth` (third-party) estimates display-cell widths; `rich` and `tabulate` (third-party) can build tables, but still consider terminal capabilities and untrusted content. `shutil.get_terminal_size(fallback=(80, 24))` can discover a likely terminal width; the result is a hint, not a guarantee that output is consumed by a terminal.

ANSI color sequences count as ordinary characters to `len()` and `textwrap`, so naive wrapping/alignment can break when escape sequences are present. Strip or account for ANSI sequences using a library designed for terminal output rather than applying character counts to colored strings.

## 7. Fuzzy matching: choose the metric, then scale it

Different similarity metrics answer different questions:

| Metric/tool | What it measures | Useful cases | Limitations |
|---|---|---|---|
| `SequenceMatcher.ratio()` | Matching blocks under a sequence-matching heuristic | Human-readable diff hints; small vocabularies | Not edit distance; order can matter; performance depends on input. |
| Levenshtein/edit distance | Minimum insertions, deletions, and substitutions (variant definitions may include transposition) | Typo distance; OCR edits when character edits are meaningful | Raw distance favors/penalizes length differently; normalized score needs a defined formula. |
| Jaro-Winkler | Character matches/transpositions with a prefix boost | Often considered for short names/record linkage | Prefix boost can be inappropriate; behavior differs from edit distance. |
| `rapidfuzz` (third-party) | Efficient implementations of several fuzzy metrics | Large candidate sets and high-throughput matching | Still requires normalization, candidate reduction, threshold tuning, and quality tests. |
| N-gram index / blocking | Reduces which candidate pairs are compared | Large entity resolution | Can miss true matches if the blocking rule is too restrictive. |
| MinHash (algorithm/library dependent) | Approximate Jaccard similarity of sets/shingles | Near-duplicate long text at scale | Approximate; requires token/shingle design and probabilistic error trade-offs. |

Do not use “difflib is O(n²)” as if it were a precise bound for every operation. `SequenceMatcher` has quadratic worst-case behavior, while practical runtime depends on the sequences and heuristic. Large-scale all-pairs matching is additionally expensive because candidate pair count grows multiplicatively. `rapidfuzz` can speed pair scoring, but it does not make an all-pairs search automatically scalable.

A scalable pipeline commonly does:

1. Normalize only the fields and ways that the domain permits; retain originals.
2. Block candidates using safe keys (for example, country plus a prefix or a sorted-neighborhood key).
3. Score only plausible pairs with an appropriate metric.
4. Tune thresholds on labeled matches/non-matches and review borderline cases.
5. Measure recall as well as precision; aggressive blocking may miss valid pairs.
6. Record the metric, normalization, library version, and threshold for reproducibility.

Name matching, product titles, and OCR are not interchangeable. Names may need language-aware rules; titles often benefit from token-based comparisons; OCR output may have systematic substitutions (`O`/`0`, `l`/`1`). Validate choices on representative data. Unicode normalization is a separate lesson; do not silently apply destructive cleanup here.

## 8. Safe templating and output contexts

Formatting is not escaping. Keep data and executable/query syntax separate.

- **f-strings and `.format()` are not sanitizers.** F-strings are Python code expressions and must not be built/evaluated from untrusted input. For `.format()`/`string.Formatter` templates, do not accept arbitrary user-controlled format strings: replacement fields can access attributes or indexes.
- **`string.Template`**: simpler placeholder syntax and useful for basic substitution. It does not HTML-escape, SQL-escape, or shell-escape values.
- **Jinja2** (third-party): autoescaping can help for HTML templates when configured for the correct output context. It does not make JavaScript, CSS, URL, SQL, or shell interpolation automatically safe. Keep autoescape enabled for HTML and follow the framework's context-specific guidance.
- **SQL**: use parameterized queries from the database driver, not f-strings or `.format()` to splice values into SQL.
- **Shell**: prefer APIs such as `subprocess.run([...], shell=False)` with separate arguments; quoting a shell command string is not a substitute for argument separation.
- **HTML**: use a context-aware template engine or appropriate escaping. HTML escaping is not a universal sanitizer for all contexts.

Python 3.14 preview: template strings (“t-strings”, PEP 750) produce structured template/interpolation objects rather than immediately behaving exactly like ordinary f-strings. They may enable libraries to inspect values and literal pieces before rendering. They are not Python 3.12 syntax or a security guarantee; use only with a supported Python 3.14+ runtime and a library explicitly designed for them. Do not invent a t-string API on the 3.12 baseline.

## 9. Practical log-diff exercise

This example compares two short log excerpts, keeps newline handling explicit, and emits a unified diff. It is intentionally small and line-oriented; it does not attempt to parse arbitrary log formats or compare entire production archives in memory.

```python
import difflib

before = [
    "2025-03-01T10:00:00Z INFO started\n",
    "2025-03-01T10:00:01Z INFO processed=10\n",
]
after = [
    "2025-03-01T10:00:00Z INFO started\n",
    "2025-03-01T10:00:01Z INFO processed=12\n",
    "2025-03-01T10:00:02Z WARN retrying\n",
]
print("".join(difflib.unified_diff(before, after, "before.log", "after.log")), end="")
```

Expected output:

```text
--- before.log
+++ after.log
@@ -1,2 +1,3 @@
 2025-03-01T10:00:00Z INFO started
-2025-03-01T10:00:01Z INFO processed=10
+2025-03-01T10:00:01Z INFO processed=12
+2025-03-01T10:00:02Z WARN retrying
```

For very large logs, stream and filter lines before comparison where possible; cap retained context and report size; compare files in chunks or use specialized tools if global alignment is not required. Do not read unbounded attacker-controlled logs into memory. If ignoring timestamps, strip only the known timestamp field after parsing/validating it; broad text replacement can hide meaningful differences.

### Responsible benchmark plan

Do not benchmark only one convenient pair. Build a reproducible dataset containing short/long strings, repetitive inputs, near-matches, non-matches, Unicode text, and skewed candidate distributions. Measure candidate generation separately from scoring; report dataset size, Python/library versions, hardware, warm-up, median and tail latency, throughput, and memory. Include correctness checks and false-positive/false-negative review. Use bounded inputs and time-limited experiments; avoid deliberately constructing enormous pathological inputs against an unbounded matcher in production. Benchmark `difflib` and alternatives on representative, safe samples, not on arbitrary user-provided worst cases.

## 10. Alternatives: choose the simplest correct parser

- `partition()` is often clearer than a regex for splitting once at a known delimiter.
- `shlex` can tokenize shell-like command strings; it is not a shell executor and is not a universal parser for every shell dialect.
- CSV should use `csv`, JSON should use `json`, and HTML/XML should use an appropriate parser. Regex can be useful for constrained validation or extraction, but nested syntax, quoting, escapes, and malformed inputs quickly make ad hoc patterns fragile.
- A scanner or state machine is useful when the grammar is simple but context-dependent. A grammar/parser library is appropriate for nested or formally specified syntax.
- `filecmp` can compare files/directories at a basic level; `difflib` explains text differences. Decide how to handle binary files, encoding errors, permissions, and large inputs.

## 11. Test suite: behavior, boundaries, and regression

A compact test set should exercise both expected results and edge cases. Example with `pytest`:

```python
# test_text_utilities.py
import difflib
import textwrap

import pytest

from text_utilities import suggest_command, truncate

@pytest.mark.parametrize(
    ("text", "width", "expected"),
    [
        ("abc", 4, "abc"),
        ("abcdef", 4, "abc…"),
        ("abcdef", 1, "…"),
        ("abcdef", 0, ""),
    ],
)
def test_truncate(text, width, expected):
    assert truncate(text, width) == expected

@pytest.mark.parametrize("width", [-1, -10])
def test_truncate_rejects_negative_width(width):
    with pytest.raises(ValueError):
        truncate("abc", width)

@pytest.mark.parametrize(
    ("query", "expected"),
    [("deply", ["deploy"]), ("unknown-command", []), ("delete", ["delete"])],
)
def test_suggest_command(query, expected):
    assert suggest_command(query) == expected

def test_unified_diff_has_expected_change():
    diff = list(difflib.unified_diff(["x=1\n"], ["x=2\n"]))
    assert any(line.startswith("-x=1") for line in diff)
    assert any(line.startswith("+x=2") for line in diff)

def test_textwrap_fill():
    assert textwrap.fill("one two three", width=7) == "one two\nthree"
```

The import assumes you saved `truncate` and `suggest_command` in `text_utilities.py` as defined above. The test file requires third-party `pytest` (`python -m pip install pytest` or the project's package manager). The tests are examples of test design; they are not evidence that a test suite has been executed.

Additional cases worth adding:

- Empty input, missing delimiters, trailing newlines, long fields, and negative widths.
- Unicode and wide terminal text; confirm display layout with `wcwidth` or a terminal-aware library if required.
- A candidate vocabulary with near-ties, capitalization differences, and ambiguous suggestions.
- Large but bounded input, repetitive sequences, and memory limits for file-diff workflows.
- HTML reports containing quotes and markup-like strings; verify output is escaped in the actual embedding context.

## 12. Common mistakes and corrections

| Mistake | Correction |
|---|---|
| Treating `ratio()` as a probability or edit-distance score | Name the metric, test it against labeled data, and calibrate thresholds. |
| Assuming `get_close_matches()` scales to millions of candidates | Reduce candidates with blocking/indexing and consider `rapidfuzz`. |
| Setting `autojunk=False` everywhere for “better” results | Understand repetitive-sequence behavior and benchmark representative data. |
| Using `textwrap.shorten()` to preserve exact spacing | It collapses whitespace; use explicit truncation if layout semantics require it. |
| Assuming f-string width truncates long values | Width is a minimum; truncate explicitly and define an ellipsis policy. |
| Aligning CJK/emoji or colored text with `len()` | Use terminal-cell-aware tooling and account for ANSI escape sequences. |
| Using `Template.safe_substitute()` as a sanitizer | It only softens missing-placeholder handling; it does not escape output. |
| Building SQL/shell/HTML by formatting strings | Use parameterized SQL, argument-list subprocess APIs, and context-aware HTML templating. |
| Normalizing text destructively without preserving originals | Define field-specific normalization, retain raw data, and test impact. |
| Printing a full diff of huge or untrusted input | Apply size limits, stream/filter first, and bound report output. |

## 13. Guided exercises

### Exercise A — explain a configuration diff

Given `timeout=10` and `timeout=15`, produce a unified diff with filenames `old.ini` and `new.ini`. Keep line endings consistent.

**Answer:**

```python
import difflib
old = ["timeout=10\n"]
new = ["timeout=15\n"]
print("".join(difflib.unified_diff(old, new, "old.ini", "new.ini")), end="")
```

Output:

```text
--- old.ini
+++ new.ini
@@ -1 +1 @@
-timeout=10
+timeout=15
```

### Exercise B — format a report

Print a `NAME` column left-aligned to width 12 and a `COUNT` column right-aligned with comma separators.

**Answer:**

```python
print(f"{'NAME':<12}{'COUNT':>12}")
print(f"{'events':<12}{1234567:>12,}")
```

Output:

```text
NAME               COUNT
events          1,234,567
```

### Exercise C — choose a matching strategy

You need to compare 500 command names, then later reconcile millions of customer records. Which approach changes?

**Answer:** `get_close_matches()` is a reasonable baseline for a few hundred commands after validating its cutoff. At millions of records, define normalization and match semantics, block candidate pairs, select an appropriate metric, consider `rapidfuzz` for efficient scoring, and evaluate recall/precision. Do not assume faster pair scoring alone solves the all-pairs problem.

## 14. Independent exercises

1. Use `SequenceMatcher.get_opcodes()` to print each operation and the corresponding slices from two short strings.
2. Use `textwrap.dedent()` and `indent()` to turn a multiline help string into a quoted block.
3. Build a table formatter that truncates a label to 14 code points and right-aligns an integer with thousands separators.
4. Write a test for `partition()` when the separator is absent.
5. Propose a small labeled evaluation set for typo suggestions. Explain false positives, false negatives, and how you would choose a cutoff.
6. Explain why a `difflib` score should not decide a security-sensitive authorization or identity match by itself.

### Answer key

1. `get_opcodes()` yields `(tag, i1, i2, j1, j2)`; print `a[i1:i2]` and `b[j1:j2]` for each tuple. Include a case with an insertion and one with a deletion.
2. Dedent the common indentation first, then call `indent(text, "> ")`; remember blank lines are not prefixed by default.
3. Reuse `truncate(label, 14)` and format as `f"{label:<14}{count:>12,}"`. This aligns code points, not terminal display cells.
4. `assert "abc".partition(":") == ("abc", "", "")`.
5. Label valid typo→intended command examples and unrelated queries; evaluate several cutoffs and measure precision/recall. Prefer an explicit user choice when suggestions are ambiguous.
6. Similarity is heuristic and can be manipulated by near-matches; authorization requires exact, policy-defined identifiers and independent checks.

## 15. Roadmap self-check — answers with reasoning

### 1. How does `unified_diff` differ from `ndiff`?

`unified_diff` emits a compact, patch-style line diff with file headers and hunk ranges, making it suitable for reviews and test failure output. `ndiff` emits line-level markers and optional `?` guide lines that hint at intraline differences. Use unified diffs for compact change review and `ndiff` when its explanatory hints help a person; do not parse either as a semantic representation of the source.

### 2. Why is `get_close_matches` unsuitable for matching 10⁶ names against 10⁶ names?

The naive cross-product has 10¹² candidate pairs. `get_close_matches()` is intended for small candidate collections and uses sequence-matching heuristics whose cost varies with string length and structure. The number of pairs dominates at this scale. Use blocking or an index to reduce candidate pairs, then a purpose-built scorer such as `rapidfuzz` if suitable; evaluate recall because blocking can discard true matches.

### 3. Format a right-aligned currency table with thousands separators and a total row.

```python
rows = [("Compute", 1234.5), ("Storage", 98765.43)]
print(f"{'SERVICE':<14}{'COST':>14}")
print("-" * 28)
for service, cost in rows:
    print(f"{service:<14}{cost:>14,.2f}")
total = sum(cost for _, cost in rows)
print("-" * 28)
print(f"{'TOTAL':<14}{total:>14,.2f}")
```

Output:

```text
SERVICE                 COST
----------------------------
Compute             1,234.50
Storage            98,765.43
----------------------------
TOTAL              99,999.93
```

The format `>14,.2f` right-aligns a numeric value in a minimum width of 14, adds comma grouping, and displays two decimal places. For financial systems, use an appropriate decimal representation and rounding policy rather than assuming binary floating point is exact for currency.

## 16. Glossary

- **Diff:** A representation of differences between two sequences.
- **Unified diff:** Compact line-oriented diff with file headers and hunks.
- **Similarity ratio:** A heuristic score from `SequenceMatcher`, not a probability.
- **Opcode:** A `SequenceMatcher` edit operation and the slices it relates.
- **`autojunk`:** A heuristic that treats popular elements specially in long sequences.
- **Cutoff:** Minimum similarity score accepted by a matching operation.
- **Blocking:** Candidate-reduction step before expensive pairwise matching.
- **N-gram:** Contiguous sequence of N units, often characters or tokens.
- **MinHash:** A sketching technique for approximate set-similarity estimation.
- **Autoescaping:** Context-sensitive output escaping performed by a template engine.
- **Display width:** Terminal cells occupied by text, which may differ from Python string length.

## 17. Completion checklist

- [ ] I can choose among `unified_diff`, `context_diff`, `ndiff`, and `HtmlDiff` and explain their output forms.
- [ ] I understand `SequenceMatcher.ratio()`, opcodes, matching blocks, `autojunk`, and performance limits.
- [ ] I can implement and test typo suggestions with a cutoff justified by data.
- [ ] I can use `textwrap` for wrapping, indentation, dedenting, and shortening.
- [ ] I can use `string` constants, `Template`, `Formatter`, and the listed `str` utilities.
- [ ] I can format fixed-width reports and explain why terminal display width can differ from `len()`.
- [ ] I choose matching metrics based on the task and use blocking/indexing at scale.
- [ ] I keep formatting separate from SQL, shell, and context-sensitive HTML safety.
- [ ] I can explain why the Python 3.14 t-string preview is not Python 3.12 baseline behavior.
- [ ] I have completed the exercises and tested boundary cases.

**Next lesson:** `06-pickle-marshal-and-shelve-risks.md`.
