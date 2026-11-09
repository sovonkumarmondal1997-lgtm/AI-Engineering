# 03 — CSV Files: Complete Study Guide and Exercise Solutions

**Roadmap:** Stage 1 — Programming & Computational Thinking  
**Module 05:** Text Files, Structured Data, and CLI Programs  
**Lesson 03:** CSV Files  
**Scope:** Python standard library only; builds on text-file I/O, `pathlib`, functions, collections, loops, exceptions, and basic testing.

---

# Part A — Complete lesson summary

## 1. What CSV is and why it matters

CSV means *comma-separated values*. It is a plain-text format for representing tabular data. It is widely used because spreadsheets, databases, APIs, programming languages, and data tools can easily exchange it. It is human-readable and requires no special editor.

Example:

```text
name,age,city
Alice,30,London
Bob,25,Delhi
```

- **File:** the complete text.
- **Row/record:** one logical data entry, such as `Alice,30,London`.
- **Field:** one value in a row, such as `Alice`.
- **Column:** values occupying the same position across rows, such as `age`.
- **Header:** optional first row naming the columns.
- **Headerless CSV:** every row, including the first, is data. The format itself does not declare whether a header exists.

CSV represents **structured/tabular data**: predictable rows and columns. It is more accurately a family of *delimited text* formats than strictly comma-only files. Delimiters can be comma, semicolon, tab, or pipe. Some European spreadsheet settings use semicolons because commas are decimal separators (for example, `3,14`).

## 2. CSV is text, not typed data

A CSV file is physically a sequence of text characters. Rows and fields are reconstructed by applying delimiter and quoting rules. CSV itself does not encode Python types.

```python
import csv

with open("people.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # consume header
    for row in reader:
        print(row, type(row[1]))
```

Default output values are strings, e.g. `"30"` is `str`, not `int`. `"true"`, `"2026-09-21"` and `"30.5"` are also strings. Your application decides and performs conversion. One exception is a special reader configuration such as `csv.QUOTE_NONNUMERIC`, which converts unquoted values to `float`; that is parser behavior, not a type system built into CSV.

Never use `bool(value)` to interpret text booleans: `bool("false")` is `True` because every non-empty string is truthy. Use explicit accepted-value mappings.

## 3. Delimiters, quoting, escaping and multiline fields

A delimiter separates fields. Configure it using `delimiter=";"` or `delimiter="\t"` when the source is not comma-delimited.

Quoting protects delimiters that belong inside a field:

```text
name,city
Alice,"New York, NY"
```

The city is one field, not two. A quoted field may contain commas, spaces, quotes, or newlines:

```text
name,comment
Alice,"She said ""hello"""
Bob,"Lives at
123 Main St"
```

With the default `doublequote=True`, two consecutive quote characters `""` represent one literal quote inside a quoted field. Some sources instead use an escape character such as backslash (`escapechar="\\"`, commonly with `doublequote=False`); reader and writer settings must match the source convention.

A logical CSV row is **not necessarily one physical text line**: a newline inside an open quoted field belongs to that field. Therefore this is unsafe:

```python
fields = line.split(",")  # WRONG for real CSV
```

For `Alice,"New York, NY",30`, `.split(",")` produces four pieces rather than three. It also cannot parse escaped quotes or multiline fields. A real parser tracks whether it is inside quotes, whether a quote is escaped, and whether a newline ends a row. Always use `csv.reader` or `csv.DictReader`.

## 4. The `csv` module and the four core tools

```python
import csv
```

The standard library module implements quote-aware parsing and writing. Its main tools:

- `csv.reader`: each parsed row is a `list[str]`, accessed by position.
- `csv.writer`: writes lists/iterables of fields.
- `csv.DictReader`: yields dictionaries keyed by header names.
- `csv.DictWriter`: writes dictionaries according to an explicit column order.

### `csv.reader`

```python
with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

The file is opened first; `csv.reader` receives the already-open iterable text stream, not a path. Each iteration yields one parsed row. The header is returned as an ordinary row; `reader` does not automatically skip it. The reader is lazy: it parses one row when requested rather than loading the whole file.

Important parameters:

| Parameter | Purpose |
|---|---|
| `iterable` | Already-open iterable text stream, not filename |
| `dialect` | Named bundle of CSV rules; default `"excel"` |
| `delimiter` | Field separator; default comma |
| `doublequote` | Whether `""` means one literal quote |
| `escapechar` | Alternative escape character, often `\` |
| `quotechar` | Quote character; default `"` |
| `quoting` | Quoting mode |
| `skipinitialspace` | Skip spaces immediately after delimiters |
| `strict` | Raise `csv.Error` for certain malformed syntax when `True` |

`skipinitialspace=True` does not trim all whitespace from every field; call `.strip()` when general trimming is part of your data rules. `strict=True` validates parser syntax only; it does not validate headers, field counts, types, missing values, or business rules.

### `csv.writer`

```python
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])
    writer.writerow(["Alice", 30])
    writer.writerows([["Bob", 25], ["Carol", 31]])
```

`writerow()` writes one row; `writerows()` writes an iterable of rows. Non-string values are converted to text. The writer inserts delimiters and quoting as needed. Its return value reflects the underlying stream's write result; normal application code generally ignores it.

`lineterminator` controls the row ending; default is `"\r\n"` even on other operating systems. `newline=""` is required so Python's text newline translation does not translate the writer's line endings a second time, potentially creating `\r\r\n`.

### `csv.DictReader`

```python
with open("customers.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"])
```

By default, the first row becomes the header and is consumed. Later rows are dictionaries; named access is clearer and survives column reordering. Modern Python dictionaries preserve insertion order.

Parameters:
- `fieldnames=None`: first row is the header. If explicit field names are supplied, the first row is data; this is essential for headerless files.
- `restkey`: dictionary key for extra fields beyond the header. Default `None` stores them under key `None`.
- `restval`: value for missing fields in short rows. Default `None`.

A short row may quietly get `None` for missing columns; extra fields are collected rather than rejected. This permissiveness is useful for exploration but dangerous in ingestion unless you validate the row shape.

### `csv.DictWriter`

```python
fields = ["name", "age"]
with open("people.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 30})
    writer.writerows([{"name": "Bob", "age": 25}])
```

`fieldnames` is required and defines output column order. `writeheader()` explicitly writes it. `restval` (default `""`) fills a missing dictionary key. `extrasaction="raise"` is the default and raises `ValueError` if a row contains a key not in `fieldnames`; `"ignore"` silently drops it and can cause data loss. Ignore extras only when that projection is intentional and documented.

## 5. CSV dialects and quoting modes

A **dialect** bundles delimiter, quote character, escape rules, line terminator, quoting mode, `skipinitialspace`, and `strict`. Built-ins:

- `"excel"`: comma, doubled quotes, `\r\n`, `QUOTE_MINIMAL`.
- `"excel-tab"`: tab-delimited Excel-style.
- `"unix"`: comma, `\n`, `QUOTE_ALL`.

Use `csv.list_dialects()`, `csv.get_dialect(name)`, `csv.register_dialect(name, dialect=None, **fmtparams)`, and `csv.unregister_dialect(name)`. An unregistered name raises `csv.Error`.

```python
csv.register_dialect(
    "pipe_dialect", delimiter="|", quotechar="'",
    doublequote=True, lineterminator="\n"
)
reader = csv.reader(f, dialect="pipe_dialect")
csv.unregister_dialect("pipe_dialect")
```

You can also subclass `csv.Dialect` and register the class. Its attributes document the complete formatting rules.

Four core quoting constants:

- `QUOTE_MINIMAL` (default): quote only fields needing protection.
- `QUOTE_ALL`: quote every field.
- `QUOTE_NONNUMERIC`: on write, quote non-numeric values; on read, convert unquoted fields to `float` (so `30` becomes `30.0`, and nonnumeric unquoted text may raise `ValueError`).
- `QUOTE_NONE`: never quote; fields containing delimiters need an `escapechar`, otherwise writing can fail. On read, quote characters are ordinary characters.

Python 3.12 added `QUOTE_NOTNULL` and `QUOTE_STRINGS` for more specialized distinctions involving `None` and strings. Check documentation for the exact Python version before depending on them.

## 6. Errors, strict parsing, and field limits

`strict=False` (default) tolerates certain malformed syntax. With `strict=True`, malformed quoted syntax such as an unclosed quote can raise `csv.Error`. Use strict parsing when bad structure must fail loudly. Catch `csv.Error` at the parsing boundary, attach filename and useful row context, then reject the whole structurally untrustworthy file or quarantine individual bad records when the rest is usable. Never use `except Exception: pass`.

`csv.field_size_limit()` with no argument returns the current maximum size (characters) for one field. With a new integer limit, it sets the limit and returns the previous one. The default is commonly 131072 but may vary. A large field can be legitimate, but can also indicate an unclosed quote or a resource-exhaustion attempt. Raise the limit only after confirming the data is legitimate.

## 7. Correct encoding and newline handling

Use this pattern for both reading and writing:

```python
with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
```

- `newline=""` disables Python's separate universal-newline translation so the CSV parser/writer controls record boundaries and embedded newlines correctly.
- `encoding="utf-8"` avoids platform-dependent defaults.
- Excel-originated CSVs may include a UTF-8 BOM. Plain UTF-8 can leave an invisible character at the start of the first header (`"\ufeffname"`), breaking `row["name"]`. Use `encoding="utf-8-sig"` to consume the BOM.

## 8. Sniffing an unknown format

```python
with open("mystery.csv", "r", newline="", encoding="utf-8") as f:
    sample = f.read(2048)
    f.seek(0)
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(sample)
    has_header = sniffer.has_header(sample)
    reader = csv.reader(f, dialect=dialect)
```

`Sniffer.sniff()` guesses delimiter/quoting; `.has_header()` guesses whether the first row looks like a header. These are heuristics based on a sample, not guarantees. Small samples, ambiguous delimiters, inconsistent rows, numeric-only data, and misleading headers can fool them. Treat guesses as suggestions; validate expected columns and field counts before trusting them.

## 9. Streaming and transformation pipelines

Avoid `list(reader)` for large files because it parses and stores every row in memory. Stream instead:

```python
with open("huge.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # header
    total_active = 0
    for row in reader:
        if row[3] == "active":
            total_active += 1
```

Memory is roughly independent of total row count (though it depends on the current row and accumulated state). Writing can also stream: read one row, decide, write it, then continue. Materializing is reasonable for a known-small file, multiple passes, or sorting; sorting/median generally require the complete data or a more advanced external/streaming algorithm.

A reliable transformation pipeline is:

```text
read → validate → convert → transform → write
```

The weather example reads dictionaries, converts Celsius text with `float`, applies a pure `celsius_to_fahrenheit()` function, rounds, and writes with `DictWriter`. The simple example deliberately omits validation; a real pipeline adds it before transformation.

## 10. Validation, schema, missing values, types

Validate at the boundary, immediately after parsing and before business logic:

- required columns and duplicate header names;
- row length, extra/missing fields;
- required values and missing-value markers;
- numeric/date/boolean types;
- allowed values and ranges;
- unique IDs and duplicate rows;
- malformed syntax.

A validator can return a list of errors instead of raising at the first issue, allowing a row to report several problems. CSV has no enforced schema: define a logical schema in your code, e.g. `customer_id: int`, `name: str`, `balance: float`, `created_at: str`. Validate headers explicitly. Duplicate header names are especially dangerous: `DictReader` lets a later duplicate key overwrite an earlier value in the row dictionary.

CSV has no universal null. Empty string, `NULL`, `null`, `NA`, `N/A`, `unknown`, and sentinel numbers may be conventions. Define a documented policy:

```python
MISSING_MARKERS = {"", "null", "na", "n/a", "unknown"}

def is_missing(value: str) -> bool:
    return value.strip().lower() in MISSING_MARKERS
```

Explicit conversions:

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
    value = value.strip().lower()
    if value in {"true", "yes", "1"}:
        return True
    if value in {"false", "no", "0"}:
        return False
    raise ValueError(f"Not a valid boolean: {value!r}")
```

These functions trim whitespace, define empty-value behavior, and raise clear errors on invalid values. A date preview uses `datetime.strptime(value.strip(), "%Y-%m-%d")`; full date/time handling is a later lesson.

## 11. Duplicates, filtering, aggregation, and joins

`DictReader` does not detect duplicate header names. Later duplicate names overwrite earlier values. Check headers before trusting dictionaries.

For duplicate IDs, keep a `seen` set and a `duplicates` set. For exact duplicate rows, build a tuple of row values (tuples are hashable) and track it in a set.

Filtering example: keep rows where `row["status"] == "active"`. Selecting a column uses `[row["name"] for row in rows]`. Aggregation can count rows, sum amounts, group by category, and compute min/max/average. `defaultdict(float)` initializes new group totals to `0.0`; it is a preview of a later standard-library lesson. For huge data, maintain running sum/count/min/max instead of storing every amount in a list.

A simple CSV join loads a small customer lookup file into a dictionary keyed by `customer_id`, then streams transactions and uses `.get()` to find the matching customer. Missing IDs are reported explicitly. Duplicate lookup IDs must be detected first; otherwise later dictionary assignment silently overwrites earlier records. This is a simple in-memory lookup, not a full relational database join.

## 12. Security

**CSV/formula injection:** spreadsheet software may interpret cells beginning with `=`, `+`, `-`, or `@` as formulas. Untrusted text exported to CSV can therefore become active when someone opens it in a spreadsheet.

```python
FORMULA_TRIGGER_CHARS = ("=", "+", "-", "@")

def sanitize_for_spreadsheet(value: str) -> str:
    if value and value[0] in FORMULA_TRIGGER_CHARS:
        return "'" + value
    return value
```

The leading apostrophe is a common mitigation, but application behavior differs and it changes exported representation. The simple function does not catch leading whitespace or control characters before a trigger; test against the target spreadsheet workflow. CSV itself does not execute formulas—the spreadsheet application does.

Also consider untrusted input validation, huge files/fields (streaming and `field_size_limit`), malformed syntax (`strict=True`), and path traversal (reuse the previous `pathlib` lesson's containment validation).

## 13. CSV vs. JSON and databases

CSV is good for flat tabular interchange, human-inspectable exports, imports, and simple batch processing. It is weak for transactions, concurrent updates, relational constraints, nested structures, random access, and complex large analytical queries.

| Format | Shape | Types | Best fit |
|---|---|---|---|
| CSV | Flat table | Text only by default | Tabular interchange |
| JSON | Nested/hierarchical | Strings, numbers, booleans, null | APIs/config/nested records |
| Database | Structured/relational | Schema-enforced | Persistent, queryable, concurrent data |

## 14. Data engineering and AI/ML applications

A common data pipeline is:

```text
source → raw CSV landing zone → validation → transformation
       → clean dataset → warehouse/database
```

Keep the raw file unchanged for audit and reprocessing. Validate, convert, track quality metrics, quarantine rejected rows, and report counts/reasons. This is the foundation of later ETL/ELT engineering.

CSV is useful for tabular training/evaluation data, labels and annotations, experiment metrics, feature exports, and batch inference inputs/outputs. It is not suitable for embedding images, audio, or large tensors, or for high-volume distributed data. A CSV can instead contain a path/URI pointing to the actual image or other artifact.

## 15. Reusable utilities and tests

A reusable utility layer can provide `read_csv_rows(path)`, `read_csv_dicts(path)`, `write_csv_rows(path, rows)`, and `write_csv_dicts(path, fieldnames, rows)`. Reading functions can return `Iterator[...]` and use `yield from reader`, preserving lazy processing; writing functions accept `Iterable[...]`. Keep validation separate from file I/O. Low-level utilities normally let file and parser exceptions propagate so callers choose the recovery strategy.

Use pytest's `tmp_path` fixture for isolated filesystem tests. Test round-trip read/write, quoted commas, multiline fields, missing fields, malformed syntax with `pytest.raises(csv.Error)`, duplicate IDs, empty/header-only files, and a large-ish input. Do not test against real project data.

Debug in order: inspect raw text, encoding/BOM, `newline=""`, delimiter, quote character, escape rules, dialect, row lengths, header, types, a tiny reproduction, `repr()` for invisible characters, and actual reader/writer configuration.

## 16. Production design and mini-projects

The production pattern is **Input → Read → Validate → Transform → Write → Verify**. Keep responsibilities separate: path/file access, parsing, pure validation/conversion, transformation, orchestration, and reporting. Use explicit errors, streaming, deterministic output, tests, reproducible runs, and safe output practices. The chapter's safe-write discussion is conceptual: write to a temporary file, finish successfully, then replace the final output; full implementation belongs to a later production lesson.

Four mini-project specifications:
1. **CSV Inspector:** headers, data-row count, sample rows, guessed-but-validated delimiter, and clear handling of missing/empty/malformed files; stream counts; test edge cases.
2. **CSV Data Cleaner:** validate headers, normalize whitespace, convert types, apply explicit missing-value rules, and split clean/rejected rows; test every rule.
3. **CSV Data Quality Reporter:** per-column non-missing/missing/invalid counts, duplicate rows/IDs, row-length inconsistencies, deterministic report, and justified memory strategy.
4. **Transaction Ingestion Pipeline:** stream, validate schema/types/business rules, write clean and rejected outputs, return summary metrics, test full outputs, and optionally detect duplicate transaction IDs.

## 17. Advanced API reference and performance

Module functions: `reader`, `writer`, `DictReader`, `DictWriter`, `register_dialect`, `unregister_dialect`, `get_dialect`, `list_dialects`, `field_size_limit`. Classes: `Dialect`, built-in `excel`, `excel_tab`, `unix_dialect`, `Sniffer`, and `Error`. The six quoting constants and Python-version notes are covered in section 5.

`list(reader)` and direct iteration do the same total parsing work, but `list()` parses everything up front and holds every row in memory. Materialize only when data is small, multiple passes or sorting are required, or the task genuinely needs all rows. Running aggregates stream; median and sorting generally do not.

The chapter also includes 13 debugging steps, 14 common mistakes, 23 interview questions (beginner/intermediate/production), 11 knowledge checks, a production checklist, and a final mastery checklist. Key recurring mistakes: `.split(",")`, missing `newline=""`/`encoding`, assuming commas/headers/types/null conventions, loading huge files, ignoring malformed/ragged rows, trusting Sniffer, skipping schema/duplicate checks, silently ignoring extra fields, writing CSV manually, and swallowing exceptions.

---

# Part B — Project-tree review and current learning level

The roadmap file shows **Stage 1 — Programming & Computational Thinking** with 24 modules. Relevant sequence:

1. Computational Thinking and Program Design
2. Python Core Language and Data Types
3. Control Flow, Functions, Scope, and Errors
4. Problem-Solving, Collections, and Algorithmic Habits
5. Text Files, Structured Data, and CLI Programs
6. Modules, Packages, Dependencies, and Code Quality
7. Testing and Systematic Debugging
8. Object-Oriented Design, Data Modelling, and Functional Style
9. Advanced Production-Oriented Python Foundations
10. Production Habits for Python Programs
11. Advanced Python Data Model and Object Design
12. Metaprogramming and Dynamic Python
13. Standard Library Toolkit
14. Bytes, Binary Data, and Advanced Text Processing
15. Modern Python Language Features
16. Advanced Testing and Test Architecture
17. Profiling, Memory, and Runtime Performance
18. Packaging, Distribution, and Publishing
19. CPython Internals and Runtime Behaviour
20. Design Patterns and Library API Design
21. Data Visualization and Notebook Workflows
22. Secure Python Coding
23. Code Reading, Refactoring, and Code Review
24. Functions and OOP Gap Lessons.

Module 05's lesson sequence is:
1. Reading and Writing Text Files
2. `pathlib` and Portable Paths
3. **CSV Files (this lesson)**
4. JSON and Serialization
5. Encodings and Newlines
6. `argparse`
7. Standard Streams and Exit Codes
8. Logging vs. Print
9. Environment Configuration and Input Validation

Your recorded progress includes Python fundamentals, control flow, functions, arguments/defaults/docstrings, scope, pure functions/side effects, exceptions, collections, Big-O, data-structure selection, comprehensions, recursion, parsing/regex, and the first two Module 05 lessons. Your current assessed level remains **beginner progressing toward intermediate**.

### Stage 1 projects and relevance to CSV

The four stage-level projects are:
1. **Personal Expense Ledger CLI** — a small command-line expense application.
2. **Log Investigation and Reliability CLI** — a tool for inspecting operational logs and reliability signals.
3. **Data Quality and Transformation Pipeline** — includes `orders.csv`, a `dqpipe` package (`cli.py`, `config.py`, `pipeline.py`, `rules.py`), tests, config, and a data contract.
4. **Rule-Based Risk Review Engine** — includes `transactions.csv`, `rules.toml`, a `riskreview` package (`cli.py`, `engine.py`, `io.py`, `models.py`, `rules.py`), tests, and golden decision data.

CSV directly supports the data-quality pipeline and transaction risk-review project. The current lesson is therefore not an isolated syntax topic; it provides the file-ingestion and validation foundation for those projects.

### Scope decisions for the solutions

Use concepts already learned plus the current lesson: functions, loops, dictionaries, lists, sets, exceptions, type hints, `Path`, `csv`, and the basic `tmp_path`/`pytest.raises` patterns introduced in prior file lessons. Do not pull in pandas, NumPy, Spark, databases, `argparse`, logging, or advanced project packaging. The source previews `yield from`, `dataclass`, and `defaultdict`; those are not required in the exercise solutions. The advanced transaction example in the source uses `dataclass`, but the exercise solution below uses a plain dictionary summary to stay within the current level.

---

# Part C — All 24 coding exercises solved

All examples assume `import csv` and, where needed, `from pathlib import Path`. Use temporary practice files. Unless stated otherwise, each CSV open uses `newline=""` and `encoding="utf-8"`.

## Level 1 — Foundation

### 1. Read rows and print each row

```python
with open("data.csv", "r", newline="", encoding="utf-8") as f:
    for row in csv.reader(f):
        print(row)
```

Open the file; `csv.reader` parses it; the loop receives one list of strings at a time; `print` displays each parsed row.

### 2. Print only the header

```python
with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader, None)
    print(header)
```

`next(reader, None)` gets the first row safely; an empty file produces `None`, not `StopIteration`.

### 3. Count data rows, excluding header

```python
with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader, None)
    count = 0
    for row in reader:
        count += 1
print(count)
```

Consume the header once; increment for every remaining parsed row. Empty/header-only files produce zero.

### 4. Print a column by index

```python
with open("data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader, None)
    for row in reader:
        if len(row) > 1:
            print(row[1])
```

Skip the header; `row[1]` is the second field; the length guard prevents `IndexError` on short rows.

### 5. Write a CSV with header and two records

```python
with open("people.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])
    writer.writerows([["Alice", 30], ["Bob", 25]])
```

Open output in write mode; create writer; write header; write both records. `writer` handles quoting and separators.

### 6. Read it back with `DictReader`

```python
with open("people.csv", "r", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["name"])
```

`DictReader` consumes the header and maps each data row by column name. Print the `name` value.

### 7. Write with `DictWriter`

```python
fields = ["name", "age"]
with open("people_dict.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 30})
    writer.writerow({"name": "Bob", "age": 25})
```

The field list defines the output schema/order; `writeheader()` emits it; each dictionary becomes one row.

## Level 2 — Practical

### 8. Filter active rows

```python
with open("customers.csv", "r", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row.get("status", "").strip().lower() == "active":
            print(row)
```

Read by header; get `status` safely; normalize whitespace/case; print only active records.

### 9. Convert amount to float and total it

```python
def parse_float(value: str) -> float:
    try:
        return float(value.strip())
    except ValueError:
        raise ValueError(f"Invalid amount: {value!r}") from None

total = 0.0
with open("transactions.csv", "r", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        total += parse_float(row["amount"])
print(total)
```

The helper converts a string and replaces the generic error with a useful message. The loop adds each converted amount. A production caller should add row context to the error.

### 10. Count rows by category

```python
counts = {}
with open("sales.csv", "r", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        category = row["category"]
        counts[category] = counts.get(category, 0) + 1
print(counts)
```

Use a dictionary as a counter; `.get(category, 0)` starts a new category at zero; increment once per row.

### 11. Find duplicate IDs

```python
def find_duplicates(rows, key):
    seen = set()
    duplicates = set()
    for row in rows:
        value = row[key]
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates

with open("customers.csv", "r", newline="", encoding="utf-8") as f:
    duplicates = find_duplicates(csv.DictReader(f), "customer_id")
print(duplicates)
```

`seen` tracks first appearances; repeated values enter `duplicates`; sets ensure each duplicate ID is reported once. The helper accepts any iterable of dictionaries, so it can process the reader without loading all rows.

### 12. Validate required headers

```python
def validate_headers(actual, required):
    missing = set(required) - set(actual or [])
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

with open("customers.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    validate_headers(reader.fieldnames, ["customer_id", "name", "age"])
```

Convert required and actual names to sets; subtract to find missing columns; raise a clear error before reading data. `actual or []` handles an empty file.

## Level 3 — Engineering

### 13. Stream a large file and calculate running total

```python
total = 0.0
with open("large_sales.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += float(row["amount"])
print(total)
```

No `list(reader)` is used. One row is processed and released before the next. Memory does not grow with total row count.

### 14. Validate schema, types, and report all violations

```python
SCHEMA = {"customer_id": int, "name": str, "balance": float}

def validate_record(row):
    errors = []
    for column, expected_type in SCHEMA.items():
        value = row.get(column, "")
        if value is None or not value.strip():
            errors.append(f"{column}: missing")
        elif expected_type is int:
            try:
                int(value)
            except ValueError:
                errors.append(f"{column}: expected integer, got {value!r}")
        elif expected_type is float:
            try:
                float(value)
            except ValueError:
                errors.append(f"{column}: expected float, got {value!r}")
    return errors

with open("customers.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    validate_headers(reader.fieldnames, SCHEMA)
    for row_number, row in enumerate(reader, start=2):
        errors = validate_record(row)
        if errors:
            print(row_number, errors)
```

The schema lists required columns and intended types. Each row is checked for missing values and conversion failures; the function returns all errors instead of stopping at the first. Header validation happens before row processing. `str` fields are required but need no conversion.

### 15. Split clean and rejected rows

```python
fields = ["id", "name", "amount"]
with open("input.csv", "r", newline="", encoding="utf-8") as source, \
     open("clean.csv", "w", newline="", encoding="utf-8") as good_file, \
     open("rejected.csv", "w", newline="", encoding="utf-8") as bad_file:

    reader = csv.DictReader(source)
    good = csv.DictWriter(good_file, fieldnames=fields)
    bad = csv.DictWriter(bad_file, fieldnames=fields + ["errors"])
    good.writeheader()
    bad.writeheader()

    for row in reader:
        errors = []
        if not (row.get("id") or "").strip():
            errors.append("missing id")
        try:
            amount = float(row.get("amount") or "")
            if amount < 0:
                errors.append("negative amount")
        except ValueError:
            errors.append("invalid amount")

        if errors:
            bad.writerow({**row, "errors": "; ".join(errors)})
        else:
            good.writerow({**row, "amount": amount})
```

Open input and both outputs; define separate schemas; validate each record; route invalid rows with reasons; write valid rows with converted numeric amount. This streams input and output. For a real production pipeline, also validate headers and decide whether zero is allowed.

### 16. Build two reusable CSV functions with type hints

```python
from pathlib import Path
from typing import Iterable, Iterator

def read_rows(path: Path) -> Iterator[list[str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        yield from csv.reader(f)

def write_rows(path: Path, rows: Iterable[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
```

The reader returns a lazy iterator of string lists; `yield from` passes through rows as requested. The writer accepts any iterable and writes each row. Both isolate file handling.

### 17. Test three functions with `tmp_path`

```python
def test_header_validation():
    with pytest.raises(ValueError):
        validate_headers(["name"], ["name", "age"])

def test_duplicate_ids():
    assert find_duplicates([{"id": "1"}, {"id": "1"}], "id") == {"1"}

def test_csv_round_trip(tmp_path):
    path = tmp_path / "rows.csv"
    write_rows(path, [["name", "age"], ["Alice", "30"]])
    assert list(read_rows(path)) == [["name", "age"], ["Alice", "30"]]
```

First test verifies the expected exception; second checks duplicate detection; third writes and reads an isolated temporary CSV. `tmp_path` is supplied by pytest; import `pytest`.

## Level 4 — Advanced

### 18. Register and use a pipe dialect

```python
csv.register_dialect("pipe", delimiter="|", quotechar='"',
                     quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
with open("data.psv", "r", newline="", encoding="utf-8") as f:
    for row in csv.reader(f, dialect="pipe"):
        print(row)
csv.unregister_dialect("pipe")
```

Register one named bundle of rules; use it in the reader; unregister after use. A pipe-delimited row such as `1|Alice|London` becomes three fields.

### 19. Sniff and validate the dialect

```python
with open("unknown.csv", "r", newline="", encoding="utf-8") as f:
    sample = f.read(2048)
    f.seek(0)
    dialect = csv.Sniffer().sniff(sample, delimiters=",;|\t")
    reader = csv.reader(f, dialect)
    header = next(reader, [])
    if len(header) != 3 or "customer_id" not in header:
        raise ValueError("Detected CSV format does not match expected schema")
    for row in reader:
        if len(row) != 3:
            raise ValueError(f"Unexpected row shape: {row!r}")
```

Read a sample and rewind; restrict candidate delimiters; infer dialect; check the expected header and row width. Sniffer is a guess, not a guarantee.

### 20. Streaming transformation pipeline

```python
def normalize_name(value):
    return value.strip().title()

with open("people.csv", "r", newline="", encoding="utf-8") as source, \
     open("people_clean.csv", "w", newline="", encoding="utf-8") as target:
    reader = csv.DictReader(source)
    required = ["name", "age"]
    validate_headers(reader.fieldnames, required)
    writer = csv.DictWriter(target, fieldnames=required)
    writer.writeheader()

    for row in reader:
        name = normalize_name(row["name"])
        age = parse_int(row["age"])
        if age is None or age < 0:
            continue
        writer.writerow({"name": name, "age": age})
```

Read dictionaries; validate the header; normalize and convert; apply a business rule; write each accepted row immediately. For production, replace `continue` with an explicit rejected-row output so no bad row disappears silently.

### 21. Join two CSV files and handle missing keys

```python
customers = {}
with open("customers.csv", "r", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        key = row["customer_id"]
        if key in customers:
            raise ValueError(f"Duplicate customer_id: {key}")
        customers[key] = row

with open("transactions.csv", "r", newline="", encoding="utf-8") as f:
    for transaction in csv.DictReader(f):
        customer = customers.get(transaction["customer_id"])
        if customer is None:
            print("Unknown customer:", transaction["customer_id"])
            continue
        print(customer["name"], transaction["amount"])
```

Load the smaller lookup file once; reject duplicate keys rather than silently overwriting; stream transactions; use `.get()` to handle unmatched IDs.

### 22. Classify at least three error kinds

```python
def check_transaction(row):
    errors = []
    if not (row.get("id") or "").strip():
        errors.append("missing_field:id")
    try:
        amount = float(row.get("amount") or "")
    except ValueError:
        errors.append("invalid_type:amount")
    else:
        if amount <= 0:
            errors.append("business_rule:amount_must_be_positive")
    return errors
```

The three categories are missing required field, invalid numeric type, and a valid number that violates the business rule. The `else` runs only when conversion succeeds.

### 23. Mitigate formula injection and test it

```python
def sanitize_for_spreadsheet(value: str) -> str:
    if value and value[0] in ("=", "+", "-", "@"):
        return "'" + value
    return value

def test_formula_value_is_neutralized():
    assert sanitize_for_spreadsheet("=1+1") == "'=1+1"
```

Prefix a leading formula trigger with an apostrophe; leave ordinary text unchanged. This is a baseline that must be tested against the actual spreadsheet application; it does not handle leading whitespace/control characters.

### 24. Production-oriented ingestion module

A compact solution using a streaming reader, schema validation, pure row conversion, clean/reject files, summary metrics, and duplicate detection:

```python
import csv
import math
from pathlib import Path

FIELDS = ["transaction_id", "customer_id", "amount", "currency"]

def validate_and_convert(row):
    errors = []
    transaction_id = (row.get("transaction_id") or "").strip()
    customer_id = (row.get("customer_id") or "").strip()
    currency = (row.get("currency") or "").strip().upper()

    if not transaction_id:
        errors.append("missing transaction_id")
    if not customer_id:
        errors.append("missing customer_id")

    try:
        amount = float(row.get("amount") or "")
    except ValueError:
        amount = None
        errors.append("invalid amount")
    else:
        if not math.isfinite(amount):
            errors.append("amount must be finite")
        elif amount <= 0:
            errors.append("amount must be positive")

    if currency not in {"USD", "EUR", "GBP"}:
        errors.append("unsupported currency")

    if errors:
        return None, errors
    return {"transaction_id": transaction_id, "customer_id": customer_id,
            "amount": amount, "currency": currency}, []

def ingest(input_path: Path, clean_path: Path, reject_path: Path):
    counts = {"total": 0, "valid": 0, "rejected": 0, "duplicate_id": 0}
    seen_ids = set()

    with input_path.open("r", newline="", encoding="utf-8") as source, \
         clean_path.open("w", newline="", encoding="utf-8") as clean_file, \
         reject_path.open("w", newline="", encoding="utf-8") as reject_file:

        reader = csv.DictReader(source)
        validate_headers(reader.fieldnames, FIELDS)
        clean = csv.DictWriter(clean_file, fieldnames=FIELDS)
        reject = csv.DictWriter(reject_file, fieldnames=FIELDS + ["errors"])
        clean.writeheader()
        reject.writeheader()

        for row in reader:
            counts["total"] += 1
            converted, errors = validate_and_convert(row)
            transaction_id = (row.get("transaction_id") or "").strip()
            if transaction_id and transaction_id in seen_ids:
                errors.append("duplicate transaction_id")
                counts["duplicate_id"] += 1
            if transaction_id:
                seen_ids.add(transaction_id)

            if errors:
                counts["rejected"] += 1
                reject.writerow({**row, "errors": "; ".join(errors)})
            else:
                counts["valid"] += 1
                clean.writerow(converted)

    return counts
```

A compact pytest suite for this module:

```python
def test_validate_and_convert_accepts_valid_row():
    clean, errors = validate_and_convert({
        "transaction_id": "t1", "customer_id": "c1",
        "amount": "12.5", "currency": "usd"
    })
    assert errors == []
    assert clean == {
        "transaction_id": "t1", "customer_id": "c1",
        "amount": 12.5, "currency": "USD"
    }

def test_validate_and_convert_rejects_bad_amounts():
    for value in ("abc", "0", "-2", "nan", "inf"):
        clean, errors = validate_and_convert({
            "transaction_id": "t1", "customer_id": "c1",
            "amount": value, "currency": "USD"
        })
        assert clean is None
        assert errors

def test_ingest_writes_clean_and_rejected_rows(tmp_path):
    source = tmp_path / "input.csv"
    clean = tmp_path / "clean.csv"
    rejected = tmp_path / "rejected.csv"
    source.write_text(
        "transaction_id,customer_id,amount,currency\\n"
        "t1,c1,12.5,usd\\n"
        "t2,c2,0,USD\\n"
        "t1,c3,8,EUR\\n",
        encoding="utf-8"
    )

    counts = ingest(source, clean, rejected)

    assert counts == {"total": 3, "valid": 1, "rejected": 2, "duplicate_id": 1}
    with clean.open("r", newline="", encoding="utf-8") as f:
        assert list(csv.DictReader(f)) == [{
            "transaction_id": "t1", "customer_id": "c1",
            "amount": "12.5", "currency": "USD"
        }]
    with rejected.open("r", newline="", encoding="utf-8") as f:
        bad_rows = list(csv.DictReader(f))
    assert len(bad_rows) == 2
    assert "amount must be positive" in bad_rows[0]["errors"]
    assert "duplicate transaction_id" in bad_rows[1]["errors"]
```

The first test checks the pure conversion function without disk access. The second checks invalid, zero, negative, and non-finite values. The integration test creates an isolated CSV, runs the pipeline, checks exact summary counts, and reads both outputs to confirm clean/rejected routing and duplicate detection. Add separate tests for missing headers and empty/header-only input; `validate_headers` should reject absent required columns before row processing.

Line-by-line design:
- `FIELDS` is the expected schema and output order.
- `validate_and_convert` performs no file I/O; it normalizes text, converts amount, checks required fields and business rules, and returns either a clean dictionary or error list.
- `ingest` initializes counts and a set for transaction IDs.
- Three context-managed files keep the input streaming and outputs open for the run.
- `DictReader` parses rows; `validate_headers` rejects a structurally wrong file before processing.
- Writers emit headers once.
- Each row increments `total`, is converted, and is checked for duplicate ID.
- Bad rows go to the reject file with reasons; valid rows go to clean output.
- The returned dictionary provides reproducible metrics to the caller.

For the full test suite, use `tmp_path` to test: pure conversion (valid amount, missing ID, invalid amount, zero/negative amount, currency case); missing required headers; duplicate IDs; exact clean/reject file contents; empty/header-only files; quoted and multiline fields; malformed syntax with `strict=True`; and all-invalid input. The exercise asks for one extra capability beyond Mini Project 4; duplicate transaction-ID detection is that capability.

---

# Part D — All 12 debugging exercises

1. **`.split(",")` bug:** quoted city commas become false extra fields. Replace manual splitting with `csv.reader(f)` and the correct dialect.
2. **Missing `newline`:** open the output with `newline=""` so CSV controls line endings.
3. **Wrong delimiter:** inspect `len(row)`; a semicolon file parsed with comma delimiter often produces one field. Use `delimiter=";"`.
4. **Wrong quote character:** `repr(row)` reveals quote characters left in the field or incorrect splits. Match the source's quote character (default `"` here).
5. **Headerless input:** default `DictReader` consumes the first real data row as header. Supply explicit `fieldnames=[...]`.
6. **Wrong numeric conversion:** `int("12.50")` raises `ValueError`. Use `float()` or `parse_float()`.
7. **Malformed syntax not rejected:** default `strict=False` is permissive. Use `strict=True` when malformed syntax must raise `csv.Error`.
8. **Wrong `DictWriter` fieldnames:** `"age"` is an extra key and default `extrasaction="raise"` raises `ValueError`; missing `"email"` is written as `restval` (default empty string). Align the schema with the row dictionaries.
9. **Extra field ignored:** `"city"` is silently dropped by `extrasaction="ignore"`. Add it to `fieldnames` or document why dropping it is intended.
10. **Huge file materialized:** `list(reader)` stores every row. Stream with `for row in reader:` unless multiple passes/random access genuinely require materialization.
11. **Blind Sniffer:** small/ambiguous samples can yield the wrong dialect. Validate header names and expected field counts before processing.
12. **Duplicate IDs overwritten:** dictionary comprehension keeps only the last row for a repeated key. Detect duplicates with a `seen` set before building the lookup dictionary.

---

# Part E — All 11 knowledge-check answers

1. **Why no built-in types?** CSV is a text interchange format; type meaning belongs to the consuming application, which converts values according to its schema.
2. **Why row differs from physical line?** A quoted field can contain a newline, so the logical record continues until the closing quote.
3. **`QUOTE_ALL` output?** `"Alice","30"` — every field is quoted, including the integer after conversion to text.
4. **Short row with `restval="?"`?** `{'name': 'Bob', 'age': '25', 'city': '?'}`.
5. **Reader for known column names but unknown order?** `csv.DictReader`, because access is by header name rather than position.
6. **DictWriter missing-key setting?** `restval`, which supplies the value for omitted fields.
7. **Invisible first-header character?** Usually a UTF-8 BOM. Inspect `repr(reader.fieldnames)` and use `encoding="utf-8-sig"`.
8. **Why not check only `value == ""`?** Missing values may be encoded as `NULL`, `NA`, `N/A`, `unknown`, or column-specific sentinels. Define a policy.
9. **Why is `=SUM(...)` risky?** Spreadsheet software may execute a leading `=` value as a formula when the CSV is opened; sanitize untrusted exports and test the target workflow.
10. **What changes with `list(reader)`?** Total parsing work is similar; `list` does it all up front and increases peak memory by retaining every row.
11. **Why quarantine bad rows?** A few invalid rows should not necessarily discard thousands of good rows; quarantine preserves usable data and records exactly what failed and why. Structural file-level corruption may still justify rejecting the whole file.

---

# Part F — Interview revision answers

1. **CSV:** a plain-text, delimited representation of tabular records.
2. **CSV as text:** rows/fields are interpreted by parser conventions; values are not typed by the format.
3. **No `split(",")`:** it fails on quoting, embedded delimiters, escaped quotes, and multiline fields.
4. **Quoting:** marks a field so delimiters/newlines inside it remain part of that field.
5. **Dialect:** reusable bundle of delimiter, quote, escape, line-ending, and related parsing/writing rules.
6. **`reader`:** lazy iterator yielding one list of string fields per parsed row.
7. **`writer`:** object that serializes row iterables with delimiter and quoting rules.
8. **DictReader vs reader:** dictionary access by header is more readable and resilient to column reordering; positional reader is useful when positions are deliberately defined.
9. **DictWriter vs writer:** dictionary output maps named values to explicit field order; row writer writes positional sequences.
10. **`newline=""`:** prevents Python newline translation from interfering with CSV's own record and embedded-newline handling.
11. **Explicit encoding:** avoids platform-dependent defaults and decoding surprises.
12. **Sniffer:** heuristic sample-based dialect/header guess; validate before trusting.
13. **`csv.Error`:** parser/module-specific failures such as malformed strict syntax, bad dialect names, or field-limit overflow.
14. **`strict=True`:** raises on certain malformed CSV syntax; it is not schema validation.
15. **`field_size_limit`:** gets/sets the maximum size of one field to limit excessive buffering.
16. **10 GB CSV:** stream row-by-row, validate and transform incrementally, write outputs incrementally, and retain only bounded aggregates/lookup state.
17. **Schema validation:** verify required headers, duplicates, row shape, missing fields, types, ranges, allowed values, and uniqueness.
18. **Malformed rows:** distinguish file-structure errors from row-level errors; fail fast on an unusable file, quarantine/report individual invalid records.
19. **Missing values:** define per-column accepted markers and normalize explicitly.
20. **CSV injection:** neutralize untrusted spreadsheet formula prefixes and test against the actual spreadsheet consumer.
21. **CSV vs JSON:** CSV for flat tables; JSON for nested structured records and APIs.
22. **CSV vs database:** CSV lacks transactions, concurrency control, constraints, indexing, and efficient complex queries.
23. **Production pipeline:** preserve raw input, parse, validate schema, validate/convert rows, apply business rules, route clean/rejected data, report metrics, and test.
24. **Intermittent KeyError:** inspect `repr(reader.fieldnames)` for BOM/whitespace, validate headers and duplicates, verify encoding (`utf-8-sig` if needed).
25. **Non-unique join ID:** detect duplicates and decide whether to reject, quarantine, or support one-to-many before building lookup.
26. **Excel external-link popups:** likely formula injection from untrusted cells beginning with formula trigger characters; sanitize and test the export.

---

# Part G — Final production and mastery checklist

- [ ] Use `csv.reader`/`DictReader`, never `.split(",")`.
- [ ] Know the delimiter, quote character, escape convention, and header policy.
- [ ] Open CSV with `newline=""` and explicit `encoding=`.
- [ ] Use `utf-8-sig` when a UTF-8 BOM is expected.
- [ ] Know the difference between positional and dictionary readers/writers.
- [ ] Validate headers, duplicate names, row lengths, missing values, types, and business rules.
- [ ] Define missing-value markers per data contract.
- [ ] Detect duplicate identifiers before building lookup dictionaries.
- [ ] Stream large inputs and outputs; materialize only for a reason.
- [ ] Treat Sniffer output as a guess and verify it.
- [ ] Handle `csv.Error` deliberately and never silently discard exceptions.
- [ ] Consider field-size limits, untrusted paths, and formula injection.
- [ ] Keep raw input, clean output, rejected output, and summary metrics distinct.
- [ ] Test with `tmp_path`, including empty, malformed, quoted, multiline, and duplicate cases.
- [ ] Separate file I/O from pure validation/conversion and transformation logic.

**Next roadmap lesson:** `04-json-and-serialization.md`. The next lesson moves from flat tabular text to nested structured data. Do not advance until you can parse CSV correctly, convert and validate fields, and stream a file without materializing all rows.
