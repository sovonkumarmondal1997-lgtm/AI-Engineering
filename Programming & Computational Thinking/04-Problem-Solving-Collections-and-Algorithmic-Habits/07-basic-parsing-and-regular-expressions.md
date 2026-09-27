# Basic Parsing and Regular Expressions

## 1. What Parsing Means

**Parsing** means taking raw text and turning it into **structured
data** your program can actually work with — fields you can look up by
name, values you can compare, numbers you can add.

```text
"John,25,India"
```

To a computer, this is nothing more than a sequence of characters —
`J`, `o`, `h`, `n`, `,`, `2`, `5`, `,`, `I`, `n`, `d`, `i`, `a`. A human
reading it immediately recognizes *structure*: a name, an age, a
country, separated by commas. **Parsing is the process of recovering
that structure programmatically** — turning the flat string
`"John,25,India"` into something like:

```python
{"name": "John", "age": 25, "country": "India"}
```

Once the text has been parsed into this shape, every technique from
this module's earlier chapters becomes available again: you can filter
by `"country"` (search/count/filter/map/aggregate chapter), group by it
(grouping chapter), look someone up by name in O(1) average-case
(data-structures chapter) — none of that is possible while the data is
still just one undifferentiated string. **Parsing is the bridge between
raw text and everything else this module has taught.**

## 2. Why Parsing Matters

Nearly everything a real program reads from the outside world arrives
as text first: a line from a log file, a row from a CSV export, a
response from a web API, a configuration file, a command typed by a
user. None of it arrives pre-organized into Python dictionaries and
lists — **parsing is the first, unavoidable step** before any of the
search, filter, aggregate, or grouping techniques from this module can
be applied.

Concretely, parsing shows up in:

- **Log processing** — extracting a timestamp, severity level, and
  message from each line of a server log.
- **Data ingestion** — reading a CSV export from a partner system into
  usable records.
- **API integration** — reading a JSON response and pulling out the
  fields your application needs.
- **User input handling** — splitting a command like `"add milk
  2"` into an action, an item, and a quantity.
- **Data cleaning** — recognizing and fixing malformed or inconsistently
  formatted values before they corrupt downstream analysis.
- **AI/ML preprocessing** — extracting structured fields from
  semi-structured documents before they can be used as training or
  retrieval data.

Get parsing wrong, and every later stage — filtering, grouping,
aggregating (the very things Module 04 has spent five chapters
teaching) — operates on bad data without ever knowing it.

## 3. Raw Text vs Structured Data

**Raw text** is a sequence of characters with no inherent meaning to
Python beyond "this is a string." **Structured data** is text that has
already been organized into a shape a program can navigate directly —
lists, dictionaries, records — exactly the collections this whole
module has been built around.

```python
raw = "John,25,India"                              # raw text — one opaque string
structured = {"name": "John", "age": 25, "country": "India"}  # structured data — navigable by field name
```

Between these two extremes sits **semi-structured data** — text that
has *some* recognizable, consistent structure (delimiters, key-value
pairs, predictable patterns) but is not yet in a ready-to-use container
form: a CSV file, a log line, a URL query string. **Parsing is the
general name for the process of moving from raw or semi-structured
text toward fully structured data** — this chapter teaches a spectrum
of tools for doing exactly that, chosen according to how structured (or
irregular) the input already is.

## 4. Parsing vs String Manipulation vs Validation

These three are related, but distinct, and confusing them leads to
either over-engineered or under-engineered code:

- **String manipulation** — changing or inspecting a string's content
  directly (`.upper()`, `.strip()`, `.replace()`) without necessarily
  extracting new structure from it.
- **Parsing** — extracting structure from a string, producing new,
  organized data (fields, records) from it.
- **Validation** — checking whether a string (or already-parsed data)
  conforms to expected rules, *without* necessarily extracting anything
  new — a yes/no (or pass/fail-with-reason) question, closely related to
  the **search** pattern from this module's first chapter.

```python
text = "  JOHN@EXAMPLE.COM  "

cleaned = text.strip().lower()          # STRING MANIPULATION — same "kind" of value, cleaned up
is_valid = "@" in cleaned                 # VALIDATION — a yes/no question
username, domain = cleaned.split("@")     # PARSING — new structure extracted (two separate values)
```

A single real task often needs all three, in sequence — clean, then
validate, then parse — and recognizing which one a given line of code
is actually doing helps keep each step focused and testable, exactly
as the previous chapter on readable code (comprehensions chapter's §28)
recommended naming and separating distinct concerns.

## 5. Basic Parsing Strategies

Before reaching for any specific tool, it helps to recognize which
*strategy* a piece of text calls for:

| Text shape | Strategy |
|---|---|
| Fields separated by a consistent character (`,`, `\|`, `\t`) | **split on a delimiter** (§7–§9) |
| A single separator dividing text into exactly two parts (`key=value`) | **partition** (§8) |
| Text with a known prefix/suffix to check or strip | **`startswith()`/`endswith()`** (§13) |
| Text requiring position-by-position scanning with changing rules | **manual parsing with state** (§15) |
| A well-known, standard format (CSV, JSON) | **a dedicated library** — `csv`, `json` (§19–§20) |
| Irregular or highly variable text where you must recognize a *pattern*, not a fixed position | **regular expressions** (§21 onward) |

**The strategy should match the text's actual structure** — reaching
for a regular expression to split a simple comma-separated line is
solving an easy problem with a needlessly complex tool (developed fully
in §55); reaching for `.split(",")` on a CSV file that might contain
commas *inside* quoted fields is solving a subtly wrong problem with a
tool too simple for the job (developed fully in §19). This chapter
builds up the full toolbox, strategy by strategy, precisely so that
choice can be made deliberately rather than by habit.

## 6. Delimiters and Separators

A **delimiter** (or **separator**) is a character or sequence of
characters that marks the boundary between one piece of data and the
next. `"John,25,India"` uses `,` as its delimiter; `"2026-01-15"` uses
`-`; a tab-separated log line uses `\t`. Recognizing the delimiter is
almost always the very first step in parsing simple, regularly
formatted text — every tool in §7–§10 exists specifically to work with
delimiters once identified.

## 7. `split()`

```python
line = "John,25,India"
fields = line.split(",")
print(fields)   # ['John', '25', 'India']
```

`str.split(separator)` breaks a string into a **list** everywhere the
separator occurs. Called with no argument at all, `split()` splits on
**any whitespace** (spaces, tabs, newlines), automatically collapsing
multiple consecutive whitespace characters into one boundary — a
distinct, commonly useful behavior from splitting on an explicit
character:

```python
"hello   world\tfoo".split()          # ['hello', 'world', 'foo'] — whitespace-aware
"a,,b".split(",")                      # ['a', '', 'b']            — empty string, NOT collapsed
```

**`maxsplit`** limits how many splits occur, useful when only the first
piece matters and the rest should stay intact:

```python
"key=value=with=equals".split("=", maxsplit=1)
# ['key', 'value=with=equals']
```

**Common mistake:** assuming `split()` always drops empty strings
between consecutive delimiters — it does not, unless splitting on
plain whitespace with no argument (§57 covers this and related
mistakes in full).

## 8. `partition()`

```python
"key=value".partition("=")
# ('key', '=', 'value')
```

`str.partition(separator)` splits a string into **exactly three
parts** — everything before the *first* occurrence of the separator,
the separator itself, and everything after — always returning a
3-tuple, even if the separator is absent:

```python
"no-equals-here".partition("=")
# ('no-equals-here', '', '')
```

**When `partition()` beats `split()`:** whenever the text is guaranteed
(or expected) to have exactly one meaningful separator and everything
after it should stay together, even if it contains more of the same
character — a URL query string's `key=value`, or a log line's
`"timestamp: rest of the message"`:

```python
timestamp, _, message = "2026-01-15: server started: ok".partition(": ")
print(timestamp, message)
# 2026-01-15 server started: ok
```

Compare against `split(": ")`, which would have produced **three**
pieces here, silently splitting the message itself at its own colon —
exactly the kind of subtle bug `partition()`'s "split only once, keep
the rest together" behavior avoids by design.

## 9. `splitlines()`

```python
text = "line one\nline two\nline three"
lines = text.splitlines()
print(lines)   # ['line one', 'line two', 'line three']
```

`str.splitlines()` splits a multi-line string into a list of individual
lines, correctly handling different line-ending conventions (`\n`,
`\r\n`) without needing to know in advance which one a given file uses
— a common, subtle source of bugs when reading files created on
different operating systems. This is the natural first step whenever
parsing a multi-line log file or text document: split into lines first
(§9), then parse each line individually using the other techniques in
this chapter.

## 10. `join()`

```python
fields = ["John", "25", "India"]
print(",".join(fields))   # "John,25,India"
```

`join()` is `split()`'s inverse — it combines a list of strings back
into one string, inserting the given separator between each item. It
is called *on* the separator, not the list — a detail beginners
frequently get backward (`",".join(fields)`, not `fields.join(",")`).
`join()` matters for parsing specifically because many parsing
pipelines are round-trips: split text apart, transform or filter the
pieces (directly reusing the comprehension patterns from
[Comprehensions and Readable Code](05-comprehensions-and-readable-code.md)),
and rejoin them into a new, cleaned string:

```python
line = "  John , 25 , India  "
cleaned = ",".join(field.strip() for field in line.split(","))
print(cleaned)   # "John,25,India"
```

## 11. `strip()`, `lstrip()`, and `rstrip()`

```python
"  hello  ".strip()    # "hello"   — removes whitespace from both ends
"  hello  ".lstrip()    # "hello  " — removes only from the left
"  hello  ".rstrip()    # "  hello" — removes only from the right
```

By default these remove whitespace; passed an argument, they remove any
of the given characters from that end:

```python
"***important***".strip("*")   # "important"
```

**Why this matters for parsing specifically:** raw text pulled from
files, user input, or split-apart fields very often carries stray
leading/trailing whitespace (as seen already in §10's example) —
`.strip()` is almost always the correct first cleanup step immediately
after splitting a line into fields, before any comparison or validation
is attempted; comparing an un-stripped `" John"` against `"John"` will
silently fail, a common and easy-to-miss bug (§57).

## 12. `find()`, `index()`, `count()`, and Membership

```python
text = "error: connection refused"

text.find("error")     # 0   — the starting index of the first match
text.find("missing")    # -1  — returns -1 if not found, never raises
text.index("error")     # 0   — same as find(), but raises ValueError if not found
text.count("r")          # 3   — how many times "r" appears
"error" in text           # True — the membership check from the search chapter's §4.7
```

**`find()` vs. `index()` — when to use which**, directly mirroring the
`dict[key]` vs. `dict.get(key)` distinction from the data-structures
chapter's §10: use `index()` when the substring's presence is
guaranteed and its absence should be a loud, immediate error; use
`find()` when absence is a normal, expected possibility that should be
handled gracefully (checking for `-1`) rather than caught as an
exception.

**When to reach for these vs. `in`:** plain `in` (search chapter's
§4.7) is the right tool for a simple yes/no "does this substring
exist" question; `find()`/`index()` are needed specifically when the
*position* of the match matters — for example, to split the string
around it manually.

## 13. `startswith()` and `endswith()`

```python
line = "ERROR: disk full"

line.startswith("ERROR")    # True
line.startswith(("ERROR", "WARNING"))   # True — accepts a tuple of options
line.endswith(".log")        # False
```

These are the correct, direct tools whenever parsing logic depends on
*where in the string* a pattern occurs — specifically at the beginning
or end — rather than merely whether it occurs at all. A very common
real use: routing log lines by their severity prefix, or filtering
files by extension, without needing a full pattern-matching tool.

```python
log_lines = ["INFO: ok", "ERROR: fail", "INFO: ok"]
errors = [line for line in log_lines if line.startswith("ERROR")]
```

This directly reuses the filter pattern from the search/count/filter/
map/aggregate chapter's §6, with `startswith()` as the condition —
exactly the kind of simple, readable parsing this chapter recommends
reaching for before any more powerful tool.

## 14. `replace()` and Text Normalization

```python
"2026-01-15".replace("-", "/")   # "2026/01/15"
```

`str.replace(old, new)` substitutes every occurrence of `old` with
`new`. This is the simplest possible tool for **normalization** —
making text consistent before further processing:

```python
messy_phone_numbers = ["(555) 123-4567", "555.123.4567", "555-123-4567"]

normalized = [
    number.replace("(", "").replace(")", "").replace(" ", "").replace(".", "").replace("-", "")
    for number in messy_phone_numbers
]
print(normalized)   # ['5551234567', '5551234567', '5551234567']
```

This chained-`.replace()` approach works, but is already starting to
strain readability (five chained calls) — this is a deliberately chosen
example, revisited directly in §52 and §55, where a single regular
expression will be shown to express the same normalization far more
concisely, once regex has been properly introduced. For now, the
lesson is: `.replace()` is the right tool for **simple, fixed**
substitutions; once many different characters must all be treated the
same way, that is an early signal a different tool may fit better.

## 15. Manual Parsing with State

Some text cannot be parsed with a single `split()` or `partition()`
call because the rules for what to do next **depend on what has already
been seen** — this requires tracking **state** as you scan through the
text character by character or token by token.

```python
def parse_simple_key_values(text):
    """Parses "key1=val1;key2=val2" into a dict, handling extra whitespace."""
    result = {}
    for pair in text.split(";"):
        pair = pair.strip()
        if not pair:
            continue
        key, _, value = pair.partition("=")
        result[key.strip()] = value.strip()
    return result


print(parse_simple_key_values("name = John; age = 25 ; country=India"))
# {'name': 'John', 'age': '25', 'country': 'India'}
```

This example is not yet "stateful" in the deepest sense — it is shown
first because it directly combines §7 (`split(";")`), §8
(`partition("=")`), and §11 (`.strip()`) into one small, realistic
parser, which is itself the point: **most everyday parsing tasks are
solved by combining these simple string tools, not by writing something
exotic.**

A genuinely stateful example — tracking whether the current position is
*inside* a quoted section, which changes how a delimiter should be
treated:

```python
def split_respecting_quotes(text, delimiter=","):
    fields = []
    current = []
    inside_quotes = False   # STATE: tracked across the whole scan

    for char in text:
        if char == '"':
            inside_quotes = not inside_quotes
        elif char == delimiter and not inside_quotes:
            fields.append("".join(current))
            current = []
            continue
        else:
            current.append(char)
        if char == '"':
            continue
        current.append(char) if False else None  # placeholder removed below

    fields.append("".join(current))
    return fields
```

The example above is intentionally left slightly rough to make a point
directly: **manually tracking state character by character is
genuinely tricky to get exactly right** (quoted commas, escaped quotes,
edge cases at the string's start and end) — this is precisely why §19
exists: the standard library's `csv` module already solves this exact
problem, correctly and thoroughly, and should be preferred over hand-
rolled quote-aware splitting in real production code. Manual,
stateful parsing remains an important *skill* to understand — it is how
parsers like `csv` and `json` work internally, and it is still the
right approach for genuinely custom, non-standard formats that no
library covers — but it is not the first tool to reach for once a
standard format is involved.

## 16. Parsing Key-Value Data

Building directly on §15's `parse_simple_key_values`, key-value parsing
(`key=value` pairs, separated by some delimiter) is one of the most
common real-world parsing tasks — configuration lines, URL query
strings, HTTP headers, and simple log metadata all share this shape:

```python
def parse_key_values(text, pair_delimiter=";", kv_delimiter="="):
    result = {}
    for pair in text.split(pair_delimiter):
        pair = pair.strip()
        if not pair:
            continue
        key, _, value = pair.partition(kv_delimiter)
        result[key.strip()] = value.strip()
    return result
```

This generalizes the earlier example into a small, reusable, named
function — directly applying the readable-code lesson from
[Comprehensions and Readable Code](05-comprehensions-and-readable-code.md)
§20 (complex or repeated logic deserves its own named function) and
§28 ("complexity should be named").

## 17. Parsing Records

A **record** is one complete "row" of related fields — a transaction, a
log entry, a user profile — exactly the dictionaries this whole module
has used throughout (search/count/filter/map/aggregate chapter's §2
onward). Parsing a batch of raw lines into records combines
line-splitting (§9) with field-splitting (§7) and key assignment:

```python
def parse_records(lines):
    records = []
    for line in lines:
        name, age, country = line.split(",")
        records.append({
            "name": name.strip(),
            "age": int(age.strip()),
            "country": country.strip(),
        })
    return records


raw_lines = ["John,25,India", "Ada,30,UK"]
print(parse_records(raw_lines))
# [{'name': 'John', 'age': 25, 'country': 'India'}, {'name': 'Ada', 'age': 30, 'country': 'UK'}]
```

Notice `int(age.strip())` — parsing frequently involves **type
conversion** alongside structural extraction: the raw text `"25"` is a
string until explicitly converted; forgetting this conversion is a
common mistake (§57) that causes numeric comparisons and aggregations
from earlier chapters (search/count/filter/map/aggregate chapter's §8)
to silently fail or behave unexpectedly on what looks like numeric
data.

Once parsed, every earlier-chapter technique becomes available again
immediately:

```python
records = parse_records(raw_lines)
average_age = sum(r["age"] for r in records) / len(records)   # aggregate chapter's §8.5
```

## 18. Parsing Nested or Semi-Structured Text

Some text has structure at more than one level — for example, a single
line containing a delimited list of sub-items:

```python
line = "T1|John|apple:2,banana:3|completed"

transaction_id, customer, items_raw, status = line.split("|")

items = {}
for item in items_raw.split(","):
    name, _, quantity = item.partition(":")
    items[name] = int(quantity)

print(transaction_id, customer, items, status)
# T1 John {'apple': 2, 'banana': 3} completed
```

This is a direct application of §15's "combine simple tools" philosophy
at two levels: split the whole line by `|` first, then further split
and partition just the `items_raw` piece. **This nested-splitting
approach becomes fragile quickly** as more levels of nesting or more
irregular formatting appear — this is the natural limit of manual
string-splitting techniques, and is precisely the boundary where §19's
`csv` module (for tabular data) or a genuinely custom, well-tested
parser becomes the right next step, rather than continuing to add more
`.split()`/`.partition()` levels by hand.

## 19. Parsing CSV Correctly

### 19.1 Why `line.split(",")` is often wrong for real CSV

```python
line = 'John,"Smith, Jr.",25'
line.split(",")
# ['John', '"Smith', ' Jr."', '25']   — WRONG! The quoted field was split apart.
```

Real-world CSV data frequently contains commas **inside** quoted
fields — a name, an address, a free-text description — and the CSV
format has well-defined rules for quoting and escaping such fields.
`.split(",")` knows nothing about quoting; it splits on every comma,
unconditionally, silently corrupting exactly this kind of field.

### 19.2 The standard library's `csv` module

```python
import csv
import io

raw_csv = 'name,role\nJohn,"Senior Engineer, Backend"\nAda,Manager'

reader = csv.reader(io.StringIO(raw_csv))
rows = list(reader)
print(rows)
# [['name', 'role'], ['John', 'Senior Engineer, Backend'], ['Ada', 'Manager']]
```

`csv.reader` correctly handles quoted fields containing commas,
respecting the actual CSV specification — exactly the quote-aware
scanning that §15's rough manual attempt was trying (and struggling)
to implement by hand.

```python
reader = csv.DictReader(io.StringIO(raw_csv))
records = list(reader)
print(records)
# [{'name': 'John', 'role': 'Senior Engineer, Backend'}, {'name': 'Ada', 'role': 'Manager'}]
```

`csv.DictReader` goes one step further, using the first row as field
names and producing dictionaries directly — skipping the manual
`{"name": ..., "role": ...}` construction from §17 entirely, for files
that are genuinely in CSV format.

### 19.3 The rule to take away

**For any text that is genuinely CSV (or CSV-like, with quoting and
escaping rules), use the `csv` module, not manual `.split(",")`.**
`.split(",")` is only safe when you can *guarantee* the delimiter never
appears inside a field's actual content — a guarantee real-world CSV
data frequently does not honor.

## 20. Parsing JSON Correctly

### 20.1 Why hand-parsing JSON is a mistake

```python
raw_json = '{"name": "John", "age": 25, "tags": ["admin", "active"]}'
```

JSON supports nested objects, nested arrays, strings with escaped
quotes, numbers, booleans, and `null` — attempting to hand-parse this
with `.split()`/`.partition()` reproduces, in full, every difficulty
already flagged for nested/semi-structured text (§18) and CSV quoting
(§19), compounded by JSON's own additional nesting and escaping rules.
**JSON has an exact, standardized grammar — always use a real parser
for it.**

### 20.2 The standard library's `json` module

```python
import json

data = json.loads(raw_json)
print(data)
# {'name': 'John', 'age': 25, 'tags': ['admin', 'active']}
print(type(data["age"]))   # <class 'int'> — already correctly typed, no manual int() conversion needed!
```

`json.loads()` parses a JSON string directly into native Python
objects — dictionaries, lists, strings, numbers, booleans, `None` —
with correct types already applied, unlike §17's manual CSV-style
parsing, which required an explicit `int()` conversion. The result
plugs directly into the nested-data recursion pattern from the previous
chapter (recursion chapter's §33) when the JSON is itself deeply
nested.

```python
json.dumps({"name": "John", "age": 25})
# '{"name": "John", "age": 25}'
```

`json.dumps()` performs the reverse operation — Python data back into a
JSON string — directly analogous to `join()` (§10) undoing `split()`.

### 20.3 The rule to take away

**Never write a custom parser for CSV or JSON.** Both have mature,
correct, thoroughly tested standard-library implementations
(`csv`, `json`) — reaching for manual string splitting or (as will be
tempting once regex is introduced) a regular expression to parse either
format is a well-known, well-documented anti-pattern, restated directly
in §56.

## 21. What Regular Expressions Are

A **regular expression** (**regex**, for short) is a compact,
specialized *language* for describing **patterns** in text — not a
specific string to search for, but a *shape* many different strings
might match. `"cat"` matches only the literal text `"cat"`; the regex
pattern `\d{3}-\d{4}` matches *any* string shaped like three digits, a
hyphen, then four digits — `"555-1234"`, `"000-0000"`, and countless
other specific strings all match that one pattern.

Everything from §7 through §20 worked because the text had a
**known, fixed structure** — a specific delimiter, a known field order.
Regular expressions exist for the next tier of problem: **recognizing
and extracting text that follows a *pattern*, even when the exact
characters vary** — an email address, a phone number in one of several
formats, every word starting with a capital letter, any line matching
`ERROR: <anything>`.

## 22. Why Regular Expressions Exist

### 22.1 Where simple string tools stop being enough

```python
text = "Contact us at support@example.com or sales@example.com"
```

Extracting every email address here with `.split()`/`.find()` alone is
awkward at best — there is no single, fixed delimiter marking where an
email address starts and ends; the pattern to recognize is "some
non-space characters, an `@`, some more non-space characters, a dot,
some more non-space characters" — a *shape*, not a fixed position or
delimiter. This is exactly the kind of problem regex was built for.

### 22.2 The trade-offs, stated as directly as this module states every trade-off

Regex is genuinely powerful — but, mirroring the honesty this module
has applied to every technique so far (recursion chapter's §2.2 on
recursion's own honest trade-offs is a direct model for this section):

- Regex **can express patterns simple string operations cannot express
  at all** (validating an email's general shape, extracting all
  matches of a variable pattern from free text).
- Regex **can become difficult to read and maintain** — a sufficiently
  complex pattern can become nearly write-only, understood by no one,
  including its own author, a month later (§57–§58 address this
  directly).
- **Regex is not a replacement for a real parser.** It has no built-in
  concept of nesting, quoting, or balanced structure — attempting to
  use regex for CSV or JSON (§56) reproduces every problem already
  flagged in §19–§20, often worse.
- **Simple string operations are often better than regex** when the
  text's structure is already fixed and known (§55 makes this
  comparison rigorous, operation by operation).
- Regex has real **performance and security implications** for
  production systems (§59–§60) that a beginner-friendly introduction
  must not skip.

This chapter introduces regex as **one tool in a larger toolbox**,
specifically for the class of problems where simple string operations
genuinely fall short — not as the default, first-reach tool for every
text-processing task.

## 23. Regex Mental Model

Before any specific syntax, build the correct mental model: a regex
**engine** scans through a piece of text, attempting to match your
pattern **starting at each position**, moving left to right, until it
finds a position where the pattern matches (or exhausts the text
without a match). A pattern is built from two kinds of building
blocks:

- **Literal characters** — match themselves exactly (`cat` matches the
  three characters `c`, `a`, `t`, in that order).
- **Metacharacters** — special symbols with their own meaning (`.` means
  "any character," `*` means "zero or more of the previous thing," and
  so on — introduced piece by piece from §25 onward).

**The single most important habit for learning regex**: build a
pattern up piece by piece, testing each addition against real example
text as you go, rather than trying to write a complete, complex pattern
in one attempt. Every section from §25 onward follows exactly this
incremental approach.

## 24. Python's `re` Module

```python
import re
```

Python's built-in `re` module provides every regex-related function
this chapter covers: `re.search()`, `re.match()`, `re.findall()`,
`re.sub()`, and more (each is given its own full section, §35–§42). All
of them take a **pattern** (a string, following regex syntax) and a
**text** to search, in that order:

```python
re.search(pattern, text)
```

## 25. Regex Literals and Metacharacters

```python
import re

re.search("cat", "concatenate")   # a match object — "cat" literally appears inside "concatenate"
re.search("dog", "concatenate")    # None — no match
```

Plain letters and digits in a pattern are **literal** — they match
themselves exactly, with no special meaning, exactly like the
substring search from §12. Certain characters, however, are
**metacharacters** — they mean something *other* than their literal
selves:

```
.  ^  $  *  +  ?  {  }  [  ]  \  |  (  )
```

Each of these is introduced individually, with its own dedicated
section, starting with `.` here and continuing through §26–§32:

```python
re.search("c.t", "cat")    # matches — "." matches ANY single character
re.search("c.t", "cot")    # matches
re.search("c.t", "ct")      # None — "." still requires exactly one character to be present
```

`.` (a period) matches **any single character except a newline** — a
placeholder for "something is here, but I don't care what."

## 26. Character Classes

A **character class** — written inside square brackets `[...]` —
matches **any one** of the characters listed inside it:

```python
re.search("[aeiou]", "sky")    # None — no vowels in "sky"
re.search("[aeiou]", "cat")     # matches "a"
```

A **range** inside a character class is a compact way to list many
characters:

```python
re.search("[0-9]", "abc123")    # matches "1"
re.search("[a-z]", "ABC")        # None — no lowercase letters
```

A **negated character class**, starting with `^` inside the brackets,
matches any character **not** in the list:

```python
re.search("[^0-9]", "123abc")    # matches "a" — the first non-digit
```

**Shorthand classes** exist for the most common character categories,
saving you from writing `[0-9]` by hand every time:

| Shorthand | Meaning | Equivalent to |
|---|---|---|
| `\d` | any digit | `[0-9]` |
| `\D` | any non-digit | `[^0-9]` |
| `\w` | any "word" character (letters, digits, underscore) | `[a-zA-Z0-9_]` |
| `\W` | any non-word character | `[^a-zA-Z0-9_]` |
| `\s` | any whitespace character (space, tab, newline) | roughly `[ \t\n\r\f\v]` |
| `\S` | any non-whitespace character | the negation of `\s` |

```python
re.search(r"\d", "abc123")   # matches "1"
```

(The `r` prefix before the pattern string is a **raw string** — this is
explained fully and carefully in §34; every regex example from this
point forward uses it, as is standard, correct practice.)

## 27. Quantifiers

A **quantifier** controls **how many times** the preceding element must
appear for a match:

| Quantifier | Meaning |
|---|---|
| `*` | zero or more |
| `+` | one or more |
| `?` | zero or one (optional) |
| `{n}` | exactly `n` |
| `{n,}` | `n` or more |
| `{n,m}` | between `n` and `m`, inclusive |

```python
re.search(r"\d*", "abc")        # matches "" — zero digits is still a match for *
re.search(r"\d+", "abc")         # None — + requires AT LEAST one digit
re.search(r"colou?r", "color")    # matches — "u" is optional
re.search(r"colou?r", "colour")   # matches
re.search(r"\d{3}", "12")          # None — needs exactly 3 digits
re.search(r"\d{3}", "1234")         # matches "123" — the first 3 digits
re.search(r"\d{3,4}", "12345")       # matches "1234" — takes as many as allowed, up to 4
```

**The `*` vs. `+` distinction is worth internalizing precisely,**
because it is a common source of subtle bugs: `*` will happily match
*zero* occurrences, meaning a pattern built entirely from `*`
quantifiers can match an empty string — often not what was intended
when the goal was "one or more."

## 28. Anchors

**Anchors** do not match any character at all — they match a
**position** in the text.

```python
re.search(r"^Hello", "Hello world")   # matches — ^ anchors to the START of the string
re.search(r"^Hello", "Say Hello")      # None — "Hello" is not at the start
re.search(r"world$", "Hello world")    # matches — $ anchors to the END of the string
re.search(r"^Hello world$", "Hello world")   # matches the ENTIRE string, start to end
```

`^` anchors to the beginning; `$` anchors to the end. Combined, `^...$`
requires the *entire* string to match the pattern — this distinction
(matching *somewhere within* the text, versus matching the *entire*
text) becomes directly important when choosing between `re.search()`
and `re.fullmatch()` in §35 and §37.

`\b` is a related anchor, matching a **word boundary** — the position
between a word character (`\w`) and a non-word character (or the
start/end of the string):

```python
re.search(r"\bcat\b", "concatenate")   # None — "cat" here is not a whole word
re.search(r"\bcat\b", "the cat sat")    # matches — "cat" is a whole word here
```

## 29. Groups

**Grouping** with parentheses `(...)` serves two related purposes:
applying a quantifier to more than one character at once, and (as §30
develops) capturing part of a match for later use.

```python
re.search(r"(ab)+", "ababab")   # matches "ababab" — + applies to the WHOLE group "ab"
re.search(r"ab+", "ababab")      # matches "abbbb"-style patterns differently — + applies ONLY to "b"
```

The distinction matters precisely: without parentheses, a quantifier
applies only to the single character or class immediately before it;
with parentheses, it applies to everything inside the group.

## 30. Capturing Groups

A **capturing group** does everything a plain group does, *plus* it
remembers exactly what text it matched, so that text can be retrieved
afterward:

```python
import re

match = re.search(r"(\d{4})-(\d{2})-(\d{2})", "Date: 2026-01-15")
print(match.group(0))   # "2026-01-15" — the ENTIRE match
print(match.group(1))   # "2026"        — the FIRST capturing group
print(match.group(2))   # "01"          — the SECOND capturing group
print(match.group(3))   # "15"          — the THIRD capturing group
print(match.groups())    # ("2026", "01", "15") — all groups, as a tuple
```

`match.group(0)` (or simply `match.group()`) is always the entire
matched text; `match.group(1)`, `match.group(2)`, and so on refer to
each parenthesized group, numbered left to right by their **opening**
parenthesis. Capturing groups are the primary mechanism for
**extraction** (§49) — recognizing a pattern is often only half the
job; pulling out the specific *pieces* of it is what groups are for.

## 31. Non-Capturing Groups

Sometimes parentheses are needed purely to apply a quantifier (§29),
with no intention of ever retrieving that group's matched text
separately — a **non-capturing group**, written `(?:...)`, does exactly
this:

```python
match = re.search(r"(?:https?://)?(\w+\.com)", "Visit https://example.com")
print(match.group(1))   # "example.com" — only the ONE real capturing group counts
```

Here, `(?:https?://)?` groups `"https?://"` together so the trailing
`?` correctly makes the *entire* protocol prefix optional, without
that group cluttering `.groups()`'s output with a piece of text nobody
needs to retrieve separately. **Use non-capturing groups whenever
grouping is needed only for structure (quantifiers, alternation), not
for extraction** — this keeps `.groups()`'s output limited to
genuinely meaningful, intentional captures.

## 32. Alternation

`|` inside a pattern means **"or"** — matching whichever alternative
succeeds:

```python
re.search(r"cat|dog", "I have a dog")    # matches "dog"
re.search(r"cat|dog", "I have a bird")    # None — neither alternative matches
```

Combined with grouping (§29), alternation can apply to just part of a
pattern:

```python
re.search(r"gr(a|e)y", "gray")   # matches "gray"
re.search(r"gr(a|e)y", "grey")    # matches "grey"
```

Without the parentheses, `r"gra|ey"` would mean "the whole pattern
`gra`, OR the whole pattern `ey`" — an entirely different, likely
unintended pattern. **Alternation's scope is exactly the group it sits
inside** — always double-check what `|` is actually alternating between
in a larger pattern, since this is a common, easy mistake (§57).

## 33. Escaping

Because metacharacters (§25) have special meaning, matching them
**literally** requires **escaping** them with a backslash:

```python
re.search(r"3.14", "pi is 3.14")    # matches — but "." here ALSO matches any character, e.g. "3x14"!
re.search(r"3\.14", "pi is 3.14")    # matches — "\." means a LITERAL period, and ONLY a period
re.search(r"3\.14", "pi is 3x14")     # None — correctly rejects the non-period case
```

Every metacharacter from §25's list can be escaped the same way:
`\.`, `\*`, `\+`, `\?`, `\(`, `\)`, `\[`, `\]`, `\{`, `\}`, `\|`, `\\`.
**Forgetting to escape a literal special character** (most often `.`,
when matching a real period, as in a decimal number or a domain name)
is one of the most common regex mistakes beginners make (§57) —
always ask explicitly, for every metacharacter in a pattern, "do I mean
this literally, or as its special regex meaning?"

## 34. Raw Strings in Python

### 34.1 The problem raw strings solve

Python strings already treat backslash specially, for their *own*
escape sequences (`\n` for newline, `\t` for tab). This collides
directly with regex's own use of backslash (§26, §33):

```python
"\d"     # Python sees this as... just "\d" (Python has no \d escape, so it's kept as-is — but this is fragile)
"\n"      # Python interprets this as an ACTUAL newline character, not the two characters \ and n!
```

If a regex pattern needs a literal `\n` (backslash-n, meaning "newline"
*in regex's own vocabulary*, which happens to coincide here, but many
other sequences do not), writing it as a plain Python string risks
Python's own escape-sequence processing silently altering what the
regex engine actually receives.

### 34.2 The fix: the `r` prefix

```python
re.search(r"\d+", text)    # RAW STRING — backslash is passed through EXACTLY as typed
re.search("\\d+", text)     # equivalent, but requires doubling every backslash manually — error-prone
```

A **raw string**, written with an `r` immediately before the opening
quote, tells Python: *"do not process backslash escape sequences in
this string at all — pass every character through exactly as typed."*
This means the regex engine receives the pattern exactly as written,
with no risk of Python's own string-escaping rules interfering.

**The rule, stated as firmly as this module states any rule: always
write regex patterns as raw strings (`r"..."`) in Python**, even for
patterns that do not currently contain a backslash — this avoids an
entire, easy-to-miss category of bugs the moment a backslash is later
added to the pattern during routine maintenance.

## 35. `re.search()`

```python
import re

match = re.search(r"\d+", "Order number: 12345")
print(match)          # <re.Match object; span=(14, 19), match='12345'>
print(match.group())   # "12345"
```

`re.search(pattern, text)` scans through `text` looking for the
**first** position where `pattern` matches, **anywhere** in the string
— it does not require the match to start at the beginning. It returns a
**match object** if found, or `None` if not — directly mirroring the
`find()`/`-1` versus "returns `None`" distinction from §12, so always
check for `None` before calling `.group()` on the result:

```python
match = re.search(r"\d+", "no numbers here")
if match:
    print(match.group())
else:
    print("no match found")
```

## 36. `re.match()`

```python
re.match(r"\d+", "12345 is the order")    # matches — "12345" is at the very START
re.match(r"\d+", "Order: 12345")            # None — digits do NOT start the string
```

`re.match()` behaves exactly like `re.search()`, **except it only ever
checks for a match starting at position 0** — the very beginning of the
string. This is functionally similar to combining `re.search()` with a
`^` anchor (§28), though `^` also interacts with certain flags (§44)
in ways `match()` alone does not — for straightforward "does this
string *begin with* this pattern" checks, `re.match()` is the more
direct, commonly used tool.

## 37. `re.fullmatch()`

```python
re.fullmatch(r"\d+", "12345")        # matches — the ENTIRE string is exactly one or more digits
re.fullmatch(r"\d+", "12345 items")   # None — extra text after the digits means no full match
```

`re.fullmatch()` requires the pattern to match the **entire** string,
start to end — equivalent to wrapping the pattern in `^...$` (§28) and
using `re.match()`. **This is the correct tool for validation** (§48):
checking whether an *entire* piece of input conforms to an expected
shape (a valid phone number, a valid ID format), rather than merely
containing a matching substring somewhere within a larger, possibly
messier string.

## 38. `re.findall()`

```python
text = "Contact us at support@example.com or sales@example.com"
emails = re.findall(r"\w+@\w+\.\w+", text)
print(emails)   # ['support@example.com', 'sales@example.com']
```

`re.findall()` returns a **list of every non-overlapping match** in the
text — not just the first one, unlike `re.search()`. This is the direct
answer to §22.1's original motivating problem: extracting *every*
occurrence of a pattern from a larger body of text.

**A subtlety worth knowing:** if the pattern contains capturing groups
(§30), `findall()`'s behavior changes — it returns the captured
group(s), not the full match, for each occurrence:

```python
re.findall(r"(\w+)@(\w+\.\w+)", text)
# [('support', 'example.com'), ('sales', 'example.com')]
```

With one capturing group, each result is that group's text; with
multiple groups, each result is a tuple of all the groups — this is a
common, easy-to-be-surprised-by behavior change (§57), worth checking
deliberately whenever a pattern with groups is passed to `findall()`.

## 39. `re.finditer()`

```python
for match in re.finditer(r"\w+@\w+\.\w+", text):
    print(match.group(), match.start(), match.end())
```

```text
support@example.com 14 34
sales@example.com 38 56
```

`re.finditer()` returns an **iterator** of match objects, rather than a
plain list of strings — directly analogous to the lazy, one-at-a-time
behavior of `map()`/`filter()` (comprehensions chapter's §13) versus a
fully materialized list. Each match object retains its full
information (`.group()`, `.start()`, `.end()`, and — if present —
`.group(1)`, `.group(2)`, etc.), unlike `findall()`'s simplified
string/tuple output. **Prefer `finditer()` over `findall()`** whenever
you need each match's *position* in the original text, or whenever the
full match object's information — not just the captured substrings —
is required.

## 40. `re.split()`

```python
re.split(r"\s*,\s*", "John,  25,India")
# ['John', '25', 'India']
```

`re.split()` generalizes `str.split()` (§7) to split on a **pattern**
rather than a fixed, literal string — here, `\s*,\s*` means "a comma,
with any amount of optional whitespace on either side," correctly
handling inconsistent spacing around delimiters that plain `.split(",")`
would leave as stray whitespace requiring a separate `.strip()` pass.
**Use `re.split()` specifically when the delimiter itself is variable**
(inconsistent whitespace, one of several possible separator characters)
— for a single, fixed, literal delimiter, plain `str.split()` remains
simpler and clearer (§55 develops this comparison fully).

## 41. `re.sub()`

```python
re.sub(r"\d", "#", "Card: 1234-5678")
# "Card: ####-####"
```

`re.sub(pattern, replacement, text)` returns a **new string** with
every match of `pattern` replaced by `replacement` — directly
generalizing `str.replace()` (§14) from a fixed literal substring to an
arbitrary pattern. Revisiting §14's phone-number normalization example,
now with a single regex substitution instead of five chained
`.replace()` calls:

```python
messy = "(555) 123-4567"
normalized = re.sub(r"[()\-\s.]", "", messy)
print(normalized)   # "5551234567"
```

`[()\-\s.]` is a character class (§26) listing every character to
strip: `(`, `)`, an escaped `-` (escaping is not strictly required for
`-` here since it is not positioned to form a range, but is a common,
safe habit), whitespace (`\s`), and a literal `.`. This is exactly the
promised, more concise replacement for §14's chained `.replace()`
calls — one pattern instead of five separate calls, and one that
automatically also handles a `.` separator style that the original
chain did not even cover.

**Replacement strings can reference captured groups**, using `\1`,
`\2`, and so on:

```python
re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\2/\3/\1", "2026-01-15")
# "01/15/2026"
```

This reorders a date from `YYYY-MM-DD` to `MM/DD/YYYY` by referencing
each capturing group from §30 directly inside the replacement pattern
— a genuinely powerful transformation technique, developed further in
§50.

## 42. `re.subn()`

```python
result, count = re.subn(r"\d", "#", "Card: 1234-5678")
print(result)   # "Card: ####-####"
print(count)     # 8 — the number of substitutions actually made
```

`re.subn()` behaves identically to `re.sub()`, but returns a **tuple**
of `(new_string, number_of_substitutions)` instead of just the new
string. This is useful specifically when the *count* of changes made
matters — for example, logging how many sensitive values were redacted,
or verifying that at least one substitution occurred as an implicit
validation step.

## 43. Compiled Regex Patterns

```python
import re

pattern = re.compile(r"\d{3}-\d{4}")

pattern.search("Call 555-1234")     # same as re.search(r"\d{3}-\d{4}", "Call 555-1234")
pattern.findall("555-1234 or 555-5678")   # ['555-1234', '555-5678']
```

`re.compile(pattern)` pre-processes a pattern into a reusable **compiled
pattern object**, which exposes the same methods (`.search()`,
`.match()`, `.findall()`, `.sub()`, and so on) directly, without needing
to pass the pattern string again each time. **When to compile:**
whenever the *same* pattern will be used **repeatedly** — for example,
checking every line of a large log file against the same pattern — this
avoids Python re-parsing the pattern string on every single call, a
direct application of the "preprocess once, reuse many times" trade-off
already established in the Big-O chapter's §24 for dictionary indexes.
For a pattern used only once or twice, compiling adds no meaningful
benefit and is purely optional style.

## 44. Regex Flags

**Flags** modify how a pattern is interpreted, passed as an optional
extra argument:

```python
re.search(r"hello", "HELLO world", re.IGNORECASE)   # matches — case is ignored
re.search(r"hello", "HELLO world")                     # None — case-sensitive by default
```

| Flag | Effect |
|---|---|
| `re.IGNORECASE` (or `re.I`) | case-insensitive matching |
| `re.MULTILINE` (or `re.M`) | `^` and `$` match at the start/end of **each line**, not just the whole string |
| `re.DOTALL` (or `re.S`) | `.` matches newlines too (by default, it does not, per §25) |
| `re.VERBOSE` (or `re.X`) | allows whitespace and comments inside the pattern itself, for readability on complex patterns |

```python
text = "Line one\nLine two\nLine three"
re.findall(r"^Line \w+$", text, re.MULTILINE)
# ['Line one', 'Line two', 'Line three'] — without MULTILINE, only the first line would match ^...$
```

Multiple flags can be combined with `|`: `re.IGNORECASE | re.MULTILINE`.
`re.VERBOSE` deserves a direct mention as a readability tool in its own
right — it is worth previewing here and connecting forward to §61:

```python
pattern = re.compile(r"""
    (\d{4})   # year
    -
    (\d{2})   # month
    -
    (\d{2})   # day
""", re.VERBOSE)
```

With `re.VERBOSE`, whitespace and `#`-comments inside the pattern are
ignored by the engine, letting a genuinely complex pattern be laid out
and documented almost like ordinary, commented code — directly applying
this module's own readability principles (comprehensions chapter's
§39) to regex patterns specifically.

## 45. Named Groups

Referring to capturing groups by number (`match.group(1)`, `match.group(2)`,
§30) works, but becomes hard to read and easy to get wrong once a
pattern has several groups. **Named groups** solve this directly:

```python
match = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", "2026-01-15")
print(match.group("year"))    # "2026"
print(match.group("month"))    # "01"
print(match.groupdict())        # {'year': '2026', 'month': '01', 'day': '15'}
```

`(?P<name>...)` defines a named group; `match.group("name")` retrieves
it by name instead of position; `match.groupdict()` returns **every**
named group as a dictionary in one call — directly producing the kind
of structured record (search/count/filter/map/aggregate chapter's §2)
this entire chapter has been building toward. **Prefer named groups
over numbered ones** the moment a pattern has more than two or three
capturing groups, purely for the same readability reason meaningful
variable names were recommended over `x`/`y` throughout this module
(comprehensions chapter's §24).

## 46. Backreferences

A **backreference** lets a pattern refer back to *what an earlier group
already matched*, within the same pattern — not merely reusing the
group's *pattern*, but requiring the exact same *text* to repeat:

```python
re.search(r"(\w+) \1", "hello hello world")    # matches "hello hello" — the SAME word repeated
re.search(r"(\w+) \1", "hello world")            # None — the words differ
```

`\1` inside the pattern means "whatever text group 1 actually matched,
literally, right here again." A genuinely useful, concrete application:
detecting accidentally duplicated words in text (a common typo,
"the the cat sat"):

```python
re.search(r"\b(\w+)\s+\1\b", "the the cat sat")
# matches "the the"
```

Backreferences are a genuinely advanced feature — used comparatively
rarely in everyday text processing — introduced here mainly so it is
recognized when encountered in other code, rather than as a technique
to reach for by default.

## 47. Lookahead and Lookbehind

**Lookahead** and **lookbehind** check that a pattern exists
immediately before or after a position, **without including that
matched text in the overall result** — they assert a condition about
surrounding context, then discard it.

```python
# Positive lookahead — match a number only if followed by "px":
re.findall(r"\d+(?=px)", "width: 100px, height: 50em")
# ['100'] — "50" is not followed by "px", so it's excluded

# Negative lookahead — match a number only if NOT followed by "px":
re.findall(r"\d+(?!px)", "width: 100px, height: 50em")
# ['10', '50'] — note: "100" partially matches as "10" before hitting "0px"; a stricter
# pattern (e.g., adding a word boundary) would be needed for fully correct results here
```

```python
# Positive lookbehind — match a number only if preceded by "$":
re.findall(r"(?<=\$)\d+", "Price: $100, Quantity: 50")
# ['100']

# Negative lookbehind — match a number only if NOT preceded by "$":
re.findall(r"(?<!\$)\b\d+", "Price: $100, Quantity: 50")
# ['50']
```

`(?=...)` is a positive lookahead; `(?!...)` is negative. `(?<=...)`
is a positive lookbehind; `(?<!...)` is negative (note: Python requires
lookbehind patterns to have a fixed length — this is a real,
implementation-specific constraint worth knowing if a lookbehind
pattern unexpectedly raises an error). These are genuinely advanced
tools, useful specifically when a match's validity depends on nearby
context that should not itself be captured or consumed — introduced
here at a conceptual, "know it exists and roughly how it works" level,
consistent with this chapter's approach to every advanced feature past
§43.

## 48. Regex Validation

**Validation** (§4) asks a yes/no question: does this text conform to
an expected shape? `re.fullmatch()` (§37) is the correct tool, since
validation requires the *entire* input to match, not merely contain a
matching substring somewhere:

```python
def is_valid_simple_email(text):
    return re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", text) is not None


print(is_valid_simple_email("john@example.com"))   # True
print(is_valid_simple_email("not-an-email"))          # False
```

**An important, honest caveat, stated directly:** a genuinely fully
correct email-validating regex is notoriously long and complex — the
official email specification allows far more variety than most people
expect. The pattern above is a **reasonable, simple approximation**,
suitable for basic sanity-checking of user input, not a guarantee of
strict specification compliance. **Production systems needing to
truly *verify* an email address almost always send a confirmation
email** rather than relying on regex validation alone — a direct,
concrete illustration of §22.2's warning that regex is genuinely
powerful but should not be over-trusted for complex, real-world
formats.

## 49. Regex Extraction

**Extraction** pulls the meaningful pieces out of matched text, using
capturing groups (§30) or named groups (§45):

```python
log_line = "2026-01-15 10:30:00 ERROR: connection refused"

match = re.search(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>\w+): (?P<message>.+)",
    log_line,
)

print(match.groupdict())
# {'date': '2026-01-15', 'time': '10:30:00', 'level': 'ERROR', 'message': 'connection refused'}
```

This single call produces a ready-to-use dictionary directly — exactly
the "raw text → structured data" transformation this chapter opened
with in §1, now achieved for a log line whose structure would have
required significantly more manual `.split()`/`.partition()` chaining
(§15–§18) to extract by hand, precisely because the *number of spaces*
and the message's own free-form content make simple, fixed-position
splitting fragile.

## 50. Regex Transformation

**Transformation** changes text according to a pattern, using
`re.sub()` (§41) — often the same capturing groups used for extraction
(§49), but now feeding into a replacement rather than a dictionary:

```python
def redact_card_numbers(text):
    return re.sub(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b", "****-****-****-****", text)


print(redact_card_numbers("Card: 1234-5678-9012-3456 was charged"))
# "Card: ****-****-****-**** was charged"
```

```python
def to_snake_case(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


print(to_snake_case("myVariableName"))   # "my_variable_name"
```

The second example uses a **lookahead** (§47) with an **empty
replacement position** — `(?<!^)(?=[A-Z])` matches the *position*
immediately before every capital letter that is not at the very start
of the string, and inserts an underscore there — a genuinely elegant,
if advanced, use of zero-width assertions for text transformation,
included here specifically to connect §47's conceptual introduction to
a real, practical payoff.

## 51. Regex for Logs

```python
log_lines = [
    "2026-01-15 10:00:00 INFO: server started",
    "2026-01-15 10:05:23 ERROR: disk full",
    "2026-01-15 10:06:01 ERROR: connection refused",
]

log_pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>\w+): (?P<message>.+)"
)

parsed_logs = [log_pattern.search(line).groupdict() for line in log_lines]

errors = [log for log in parsed_logs if log["level"] == "ERROR"]
print(len(errors))   # 2
```

This directly combines §43's compiled pattern (reused across every
line — the exact "preprocess once, apply many times" case that
justifies compiling), §49's extraction, and the filter pattern from the
search/count/filter/map/aggregate chapter's §6 — a complete,
realistic, small log-processing pipeline built from tools this module
has now fully introduced.

## 52. Regex for Data Cleaning

```python
messy_values = ["  100.50  ", "$200.00", "150", "  $75.25"]

def clean_amount(value):
    cleaned = re.sub(r"[^\d.]", "", value)
    return float(cleaned)


print([clean_amount(v) for v in messy_values])
# [100.5, 200.0, 150.0, 75.25]
```

`[^\d.]` (a negated character class, §26) matches **any character that
is not a digit or a period**, and `re.sub()` removes every one of them
— a single, compact expression that strips currency symbols and
whitespace regardless of exactly which ones appear, generalizing
§14/§41's earlier phone-number normalization to a case where an
explicit list of characters to remove would be harder to fully specify
in advance.

## 53. Regex for Practical Text Processing

```python
text = "The Quick Brown Fox Jumps Over The Lazy Dog"

capitalized_words = re.findall(r"\b[A-Z]\w*\b", text)
print(capitalized_words)
# ['The', 'Quick', 'Brown', 'Fox', 'Jumps', 'Over', 'The', 'Lazy', 'Dog']

word_count = len(re.findall(r"\b\w+\b", text))
print(word_count)   # 9
```

These examples deliberately reuse the "counting" and "extraction"
framing from the search/count/filter/map/aggregate chapter's §5, now
applied to a genuinely pattern-based (rather than delimiter-based)
question — "how many words," and "which words are capitalized" — that
plain `.split()` alone answers less precisely (`.split()` alone cannot
distinguish "capitalized" without an additional check per word, whereas
the regex expresses that condition directly inside the pattern itself).

## 54. Parsing and Regex Together

Real pipelines frequently combine both simple string tools *and* regex,
each doing the part it is best suited for:

```python
def parse_log_file(text):
    records = []
    for line in text.splitlines():          # simple string tool — split into lines (§9)
        line = line.strip()                   # simple string tool — clean whitespace (§11)
        if not line:
            continue
        match = log_pattern.search(line)       # regex — extract the pattern-based structure (§51)
        if match:
            records.append(match.groupdict())
    return records
```

**This is the intended, idiomatic shape of most real parsing code**:
use simple string operations for the parts of the text that are simply
and reliably structured (line boundaries, whitespace), and reserve
regex specifically for the parts that genuinely require
pattern-matching (variable-length fields, optional components,
recognizing a *shape* rather than a fixed position). Neither tool
should try to do the other's job.

## 55. Regex vs Simple String Operations

| Task | Simple string tool | When regex is actually needed instead |
|---|---|---|
| Split on one fixed character | `str.split(",")` | Only if the delimiter itself varies (extra spaces, multiple possible separator characters) — §40 |
| Check a fixed prefix/suffix | `str.startswith()`/`endswith()` | Only if the prefix/suffix itself has variable parts (a digit, any of several words) |
| Replace one fixed substring | `str.replace()` | Only if many different substrings must all be replaced the same way, or the substring to match has a variable shape — §41 |
| Check for one literal substring | `in` | Only if what counts as "present" is a *pattern* (any digit sequence, any of several spellings), not one exact string |
| Extract text between two exact delimiters | `str.partition()` (twice, if needed) | Only if the delimiters themselves vary, or extraction from multiple positions in a longer, less predictable string is needed |

**The decision rule, stated directly:** if the text's structure is
**fixed and known** (a specific delimiter character, a specific
prefix), use the simple string operation — it is faster to write,
faster to read, and (per §59) typically faster to run. **Reach for
regex only once the structure itself is variable** — different possible
formats, optional pieces, a pattern rather than a specific known
string. Reaching for regex when a simple string method would do is a
named, common mistake (§57) — this table exists specifically to make
that judgment call concrete rather than a vague feeling.

## 56. Regex vs Dedicated Parsers

Directly restating and reinforcing §19.3 and §20.3, now that regex's
apparent power might otherwise tempt a return to those exact mistakes:
**regex has no built-in concept of nesting, quoting, or balanced
structure.** Attempting to parse CSV with regex reproduces every
quoting problem from §19.1; attempting to parse JSON with regex is
significantly worse, because JSON's nesting can be arbitrarily deep
(directly connecting to the recursion chapter's own treatment of
arbitrarily nested structures, §15–§16, §33 there) — no single regular
expression can correctly match arbitrarily deep, balanced nested
brackets in the general case, a well-known, provable limitation of
regular expressions as a formal language tool, not merely a matter of
writing a sufficiently clever pattern.

**The rule, restated as firmly as §19.3 and §20.3 stated it: for CSV,
use `csv`; for JSON, use `json`; for genuinely nested or recursively
structured formats, use a real parser (or, if writing one from
scratch, the recursive techniques from the previous chapter) — never
regex.** Regex remains the correct tool specifically for *flat*
pattern recognition within otherwise simply structured text — log
lines, single-line records, extracting patterns from free text — not
for formats with real, non-trivial grammatical structure.

## 57. Common Regex Mistakes

1. **Forgetting to escape a literal special character.**
```python
re.search(r"3.14", text)    # "." matches ANY character, not just a literal period!
```
→ **Correct:** `re.search(r"3\.14", text)`. **Lesson:** always ask, for
every metacharacter, whether it is meant literally (§33).

2. **Using `*` when `+` was actually meant.**
```python
re.fullmatch(r"\d*", "")    # matches the EMPTY string — is that really intended?
```
→ **Lesson:** `*` allows zero occurrences; if at least one is required,
use `+` (§27).

3. **Forgetting the raw-string prefix.**
```python
re.search("\d+", text)    # works today by coincidence, but fragile — see §34
```
→ **Correct:** `re.search(r"\d+", text)`. **Lesson:** always use `r"..."`
for regex patterns, without exception (§34).

4. **Misjudging alternation's scope.**
```python
re.search(r"gra|ey", text)    # means "gra" OR "ey" — probably not intended!
```
→ **Correct:** `re.search(r"gr(a|e)y", text)`. **Lesson:** `|`
alternates across the *entire* enclosing group/pattern, not just the
adjacent characters (§32).

5. **Using `re.search()` when validation (`re.fullmatch()`) was
actually needed.**
```python
def is_valid_id(text):
    return re.search(r"\d{5}", text) is not None

is_valid_id("12345-extra-junk")   # True — but should this really be considered valid?
```
→ **Correct:** use `re.fullmatch()` if the *entire* string must conform
(§37, §48). **Lesson:** `search()` finds a match *anywhere*; only
`fullmatch()` requires the whole string to match.

6. **Being surprised by `findall()`'s behavior with capturing groups.**
Directly §38's flagged subtlety — expecting full matches back, but
receiving only captured groups (or tuples of groups) instead, once
parentheses are added to a pattern that previously had none.

7. **Overly greedy or overly broad character classes/quantifiers.**
```python
re.search(r"<.*>", "<b>bold</b> and <i>italic</i>")
# matches "<b>bold</b> and <i>italic</i>" — the ENTIRE span, not just "<b>"!
```
→ **Why wrong:** `.*` is **greedy** by default — it matches as *much*
text as possible while still allowing the overall pattern to succeed,
here stretching all the way to the *last* `>` in the string rather than
stopping at the first one. **Correct:** use a non-greedy quantifier,
`.*?`, which matches as *little* as possible: `re.search(r"<.*?>", text)`
correctly matches just `"<b>"`. **Lesson:** always consider whether
greedy or non-greedy matching is actually wanted, especially with `.*`
or `.+` — this is one of the single most common sources of "my regex
matched way more than I expected" bugs.

8. **Reaching for regex when a simple string operation would do.**
Directly §55's central point, restated as a named mistake: using
`re.search(r"^ERROR", line)` when `line.startswith("ERROR")` (§13) is
simpler, clearer, and (per §59) typically faster.

9. **Trying to parse CSV or JSON with regex.**
Directly §56's central point — a named, common, well-documented
anti-pattern.

10. **Writing an unreadable, uncommented, deeply nested pattern** with
no `re.VERBOSE` (§44) formatting and no supporting comments, making the
pattern effectively unmaintainable by anyone other than its original
author, and often not even by them, a month later.

## 58. Debugging Regex

A systematic approach, directly mirroring the debugging methods already
established for comprehensions (comprehensions chapter's §34) and
recursion (recursion chapter's §28):

1. **Build the pattern incrementally.** Start with the simplest
   possible piece, confirm it matches expected text, then add one more
   piece at a time (§23's core habit), re-testing after every addition.
2. **Test against multiple example strings deliberately** — both
   strings that *should* match and strings that *should not* — not just
   one "happy path" example (directly mirroring the edge-case testing
   habit from every earlier chapter in this module, e.g., search chapter's
   §16, grouping chapter's §33).
3. **Print the match object itself**, not just `.group()`, when
   behavior is unclear — `print(match)` shows the exact matched span
   and text, which often immediately reveals whether the match is
   longer or shorter than expected (frequently a greedy-quantifier issue,
   mistake #7 in §57).
4. **Isolate capturing groups one at a time** with `.groups()` or
   `.groupdict()` (§30, §45) to confirm each piece is capturing exactly
   the intended substring, rather than assuming the whole pattern is
   correct just because *a* match was found.
5. **Use an online regex visualizer/tester during development** (a
   general, widely available category of tool, not tied to Python
   specifically) to see, step by step, how the engine processes a
   pattern against sample text — genuinely useful while learning, and
   for debugging any pattern complex enough that mental tracing becomes
   unreliable.
6. **If the pattern remains hard to reason about even after these
   steps, that is itself a signal** — per §22.2 and §57 mistake #10,
   consider whether the pattern should be simplified, broken into
   several smaller patterns applied in sequence, or replaced with a
   combination of simple string operations (§55) or a dedicated parser
   (§56).

## 59. Regex Complexity and Performance

Connecting directly to
[Big-O, Time, and Space Complexity](03-big-o-time-and-space-complexity.md):
a **simple** regex pattern applied to a string of length `n` typically
runs in time roughly proportional to `n` — comparable to a single pass
over the text, similar in spirit to the O(n) string-scanning operations
already covered in that chapter's §19 (`in`, `.count()`).

**This is not a universal guarantee, and the caveat matters
significantly** (§60 develops the worst case in full): certain pattern
shapes — particularly ones combining **nested or overlapping
quantifiers** — can cause the regex engine to explore an enormous,
exponentially growing number of possible ways to match, dramatically
increasing runtime for specific, otherwise ordinary-looking inputs.
**Do not assume every regex operation is automatically fast just
because the pattern looks short** — pattern *shape*, not pattern
*length*, is what determines worst-case performance, directly
echoing the Big-O chapter's own repeated warning (§18 there) against
judging cost by superficial appearance alone.

**Compiling a pattern once and reusing it (§43)** avoids repeated
parsing overhead, but does **not** change a pattern's fundamental
matching complexity — it is a constant-factor optimization, not an
algorithmic one, in the same sense the Big-O chapter distinguished
implementation speed from asymptotic complexity (§31–§32 there).

## 60. Catastrophic Backtracking and ReDoS Awareness

### 60.1 What catastrophic backtracking is

Some patterns, given the right (or rather, wrong) input, can cause the
regex engine to take an extraordinarily long time — potentially many
seconds, minutes, or effectively forever — to determine that *no* match
exists. This happens specifically with patterns containing **nested
quantifiers over overlapping character sets**:

```python
import re

# DANGEROUS pattern — do not run this against untrusted, adversarial input:
dangerous_pattern = r"(a+)+b"
```

Against a string like `"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"`
(many `a`s, followed by a character that can never satisfy the pattern),
this pattern can take an amount of time that roughly **doubles** with
every additional `a` in the input — precisely the O(2ⁿ) exponential
growth already derived in the recursion chapter's §23.2 and §30.1, here
arising from the regex engine's own internal backtracking search rather
than from a recursive function you wrote yourself.

### 60.2 Why this is a genuine security concern: ReDoS

This is significant enough, in real production systems, to have its
own name: **ReDoS — Regular Expression Denial of Service.** If a
regex pattern with this vulnerable shape is applied to **user-supplied,
untrusted input** — a search box, a form field, an uploaded file — an
attacker can deliberately craft a short, seemingly innocuous input
string that causes the pattern-matching call to hang for an extremely
long time, potentially tying up server resources and denying service to
other legitimate users. This is a documented, real-world category of
vulnerability, not a theoretical curiosity.

### 60.3 Practical guidance

- **Avoid nested quantifiers over overlapping patterns** — `(a+)+`,
  `(a*)*`, and similar shapes are the classic warning sign; if a
  pattern contains a quantified group that is *itself* quantified again,
  examine it carefully.
- **Be especially cautious with regex patterns applied to untrusted,
  externally supplied input** — treat this exactly as any other
  external-input security boundary (a direct application of this
  project's general security posture: validate and bound input, never
  trust it by default).
- **Prefer simpler, more specific patterns** over broad, deeply nested
  ones — often the safer pattern is also the more readable one, a
  genuinely convenient alignment between this chapter's readability
  guidance (§57, §61) and its security guidance.
- **Consider setting an explicit timeout or input-length limit** when
  applying regex to untrusted input in a production system, as a
  defensive measure independent of the pattern's own design.
- **This is not a reason to avoid regex entirely** — it is a reason to
  understand pattern shape well enough (§27–§29) to recognize the
  specific, well-documented danger shape, and to treat regex applied to
  untrusted input with the same engineering care given to any other
  external-input-handling code.

## 61. Production Engineering Guidelines

- **Choose the simplest tool that correctly solves the problem** —
  §5's strategy table and §55's comparison table exist precisely to
  make this choice deliberate, every time, rather than reflexive.
- **Always use raw strings for regex patterns** (§34), without
  exception, even for patterns that do not currently contain a
  backslash.
- **Compile patterns used repeatedly** (§43), especially inside loops
  processing many lines or records, following the same "preprocess
  once, apply many times" principle already established for dictionary
  indexes (Big-O chapter's §24).
- **Prefer named groups over numbered ones** (§45) once a pattern has
  more than a couple of capturing groups.
- **Use `re.VERBOSE` with comments** (§44) for any pattern complex
  enough that its purpose is not immediately obvious from a glance —
  this is the regex-specific application of this module's standing
  comment guidance (comprehensions chapter's §28: name and explain
  genuinely non-obvious complexity).
- **Never use regex for CSV or JSON, or for any format with real
  nested/recursive structure** (§56) — use the standard library's `csv`
  and `json` modules, or a real parser, instead.
- **Treat regex applied to untrusted input with real security
  awareness** (§60) — check for dangerous nested-quantifier shapes, and
  consider input-length limits or timeouts for genuinely
  externally-supplied patterns or text.
- **Test regex against both matching and non-matching examples
  explicitly** (§58) — a pattern that "works" on the one example you
  first tried is not the same as a pattern that is actually correct.
- **Document why a regex pattern exists and what it is meant to match**
  — a regex pattern with no surrounding context is one of the hardest
  things for a future engineer (including future you) to safely modify.

## 62. Applied AI / Data Engineering Connections

- **Log processing at scale** — the log-parsing pattern from §51
  (compiled pattern + named groups + filtering) is the direct,
  practical shape of real log-analysis pipelines, feeding parsed
  records into the grouping, counting, and aggregation techniques from
  this module's earlier chapters (grouping chapter's §31, §36).
- **Data cleaning before analysis or model training** — §52's amount-
  cleaning pattern generalizes directly to cleaning any inconsistently
  formatted numeric, date, or categorical field ingested from external,
  imperfectly formatted sources, a near-universal first step in any
  real data pipeline.
- **Text preprocessing for NLP and retrieval** — extracting structured
  fields (dates, entity-like patterns, section headers) from
  semi-structured documents before further processing, directly
  connecting to the recursion chapter's own nested-document-processing
  examples (recursion chapter's §42) for documents whose structure is
  *both* nested *and* pattern-based.
- **API and configuration parsing** — §16's key-value parsing and
  §20's `json` handling are the direct, everyday tools for reading
  configuration and API responses, exactly the kind of "raw text
  arriving from outside the program" scenario motivating this entire
  chapter (§2).
- **Data validation pipelines** — §48's validation pattern, applied at
  scale across an ingested batch of records (combining `re.fullmatch()`
  with the filter pattern from the search chapter's §6), is a standard
  first-line data-quality check before records are trusted for further
  processing.
- **Where regex is deliberately avoided in applied AI work** — genuinely
  structured formats (JSON API responses, CSV exports, well-formed
  configuration files) should always go through `json`/`csv` (§56), and
  deeply nested or recursively structured text should use the recursive
  techniques from the previous chapter rather than an attempted regex
  workaround — regex's real, ongoing value in this domain is
  specifically pattern recognition within otherwise simple, flat, or
  semi-structured text.

## 63. Refactoring Workshop

For each: **Original code → Decision → Reason → Improved version** —
directly following the format established in the comprehensions
chapter's own refactoring workshop (§41 there).

**1. Simple prefix check done with regex.**
```python
if re.search(r"^ERROR", line):
    ...
```
Decision: **REWRITE**, using `.startswith()`.
```python
if line.startswith("ERROR"):
    ...
```
Reason: no pattern variability exists here at all — this is exactly
§55's central case, and §57 mistake #8.

**2. Fixed-delimiter split done with regex.**
```python
fields = re.split(r",", line)
```
Decision: **REWRITE**, using `str.split()`.
```python
fields = line.split(",")
```
Reason: the delimiter is a single, fixed, literal character — no
pattern is needed at all (§55).

**3. Variable-whitespace split.**
```python
fields = line.split(" ")   # breaks if there are multiple consecutive spaces!
```
Decision: **REWRITE**, using `re.split()` (or plain `.split()` with no
argument, per §7, if only whitespace-splitting on the whole string is
needed).
```python
fields = re.split(r"\s+", line.strip())
```
Reason: the delimiter itself is variable (inconsistent whitespace) —
this is exactly the case where `re.split()` earns its place over plain
`str.split()` (§40).

**4. CSV parsed with a hand-rolled split.**
```python
fields = line.split(",")   # breaks on any comma inside a quoted field!
```
Decision: **REWRITE**, using the `csv` module.
```python
import csv
fields = next(csv.reader([line]))
```
Reason: directly §19's central warning — quoting rules require a real
CSV parser.

**5. JSON parsed with regex.**
```python
name = re.search(r'"name":\s*"([^"]*)"', json_text).group(1)
```
Decision: **REWRITE**, using the `json` module.
```python
import json
name = json.loads(json_text)["name"]
```
Reason: directly §20 and §56 — even though this particular regex might
happen to work on simple, well-behaved JSON, it will silently break on
escaped quotes, nested objects, or any structural variation the
original author did not anticipate.

**6. Greedy quantifier capturing too much.**
```python
re.search(r"\[.*\]", "[1, 2] and [3, 4]")   # matches "[1, 2] and [3, 4]" — too much!
```
Decision: **REWRITE**, using a non-greedy quantifier.
```python
re.findall(r"\[.*?\]", "[1, 2] and [3, 4]")   # ['[1, 2]', '[3, 4]']
```
Reason: directly §57 mistake #7 — greedy `.* ` matched across both
bracket pairs; `.*?` correctly stops at the first closing bracket.

**7. Validation done with `search()` instead of `fullmatch()`.**
```python
def is_valid_zip(text):
    return re.search(r"\d{5}", text) is not None
```
Decision: **REWRITE**, using `re.fullmatch()`.
```python
def is_valid_zip(text):
    return re.fullmatch(r"\d{5}", text) is not None
```
Reason: directly §57 mistake #5 — `search()` would accept
`"12345-extra"` as valid, which is very unlikely to be the intended
behavior for a validation function.

**8. Unreadable, uncommented complex pattern.**
```python
p = re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})T(?P<h>\d{2}):(?P<mi>\d{2}):(?P<s>\d{2})Z")
```
Decision: **KEEP, but reformat with `re.VERBOSE` and comments.**
```python
p = re.compile(r"""
    (?P<year>\d{4}) - (?P<month>\d{2}) - (?P<day>\d{2})   # date
    T
    (?P<hour>\d{2}) : (?P<minute>\d{2}) : (?P<second>\d{2})   # time
    Z
""", re.VERBOSE)
```
Reason: the pattern is genuinely appropriate for the task (a real
ISO-8601 timestamp shape) — the fix is readability (§44, §57 mistake
#10), not replacement.

**9. Repeated pattern used inside a large loop, uncompiled.**
```python
for line in millions_of_lines:
    if re.search(r"\bERROR\b", line):
        ...
```
Decision: **REWRITE**, compiling the pattern once outside the loop.
```python
error_pattern = re.compile(r"\bERROR\b")
for line in millions_of_lines:
    if error_pattern.search(line):
        ...
```
Reason: directly §43 and §61 — the same pattern is used repeatedly, so
compiling once avoids redundant re-parsing on every iteration.

**10. Nested-quantifier pattern applied to untrusted input.**
```python
def is_valid(text):
    return re.fullmatch(r"(a+)+b", text) is not None   # applied to user-supplied input!
```
Decision: **REWRITE**, simplifying the pattern's structure.
```python
def is_valid(text):
    return re.fullmatch(r"a+b", text) is not None
```
Reason: directly §60 — `(a+)+` is a classic catastrophic-backtracking
shape; `a+` alone expresses the same intended match ("one or more `a`s,
then `b`") without the dangerous nested quantifier, and should always
be preferred once recognized as equivalent for the actual matching
intent.

## 64. Progressive Exercises

Work through each using the decision frameworks from §5 and §55 —
explicitly justify your choice of tool for every exercise, not just
your final pattern or code.

### Level 1 — Beginner

**1.** Given `"apple,banana,cherry"`, split it into a list of three
fruit names.

**2.** Given `"  hello world  "`, produce a cleaned string with no
leading or trailing whitespace.

**3.** Given `"key=value"`, extract the key and the value separately
using `partition()`.

**4.** Given `"report.csv"`, check whether it ends with `.csv` without
using regex.

**5.** Given `"2026-01-15"`, use a regex pattern to confirm it consists
of exactly 4 digits, a hyphen, 2 digits, a hyphen, and 2 digits.

### Level 2 — Intermediate

**6.** Given a list of raw lines `["John,25,India", "Ada,30,UK"]`,
parse them into a list of dictionaries with keys `"name"`, `"age"`
(as an integer), and `"country"`.

**7.** Given `"Contact: john@example.com or ada@example.org"`, extract
every email address using `re.findall()`.

**8.** Given `"price: $45.00"`, extract just the numeric amount as a
`float`, without the dollar sign.

**9.** Given a string with inconsistent spacing around commas
(`"John,  25 ,India"`), split it into clean fields using `re.split()`.

**10.** Given `"myVariableNameHere"`, convert it to `"my_variable_name_here"`
using regex (see §50 for the underlying technique).

### Level 3 — Advanced

**11.** Given a log line `"2026-01-15 10:00:00 ERROR: disk full"`,
extract the date, time, severity level, and message into a dictionary
using named groups.

**12.** Given a raw CSV string containing a quoted field with an
embedded comma, correctly parse it into rows using the `csv` module,
and explain why `str.split(",")` would have failed.

**13.** Given a JSON string representing a small nested configuration,
parse it with `json.loads()` and then use the recursive flattening
template from the previous chapter (recursion chapter's §33) to produce
a flat dictionary of dotted paths.

**14.** Write a function that redacts every credit-card-shaped number
(`\d{4}-\d{4}-\d{4}-\d{4}`) in a block of text, replacing each with
`"[REDACTED]"`.

**15.** Given a pattern `r"(a+)+b"`, explain, in your own words, why
this pattern is dangerous, and rewrite it to express the same intended
match safely.

### Level 4 — Production-Oriented

**16.** Given a large list of raw log lines, write a pipeline that:
splits into lines, extracts structured fields using a **compiled**,
**named-group** pattern, filters to only `ERROR`-level entries, and
counts how many errors occurred per distinct message.

**17.** Given a batch of raw, inconsistently formatted phone numbers,
write a function that normalizes every one to a single consistent
digits-only format, and explain your choice of `.replace()` chains vs.
a single `re.sub()` call.

**18.** Given a batch of user-submitted email addresses, write a
validation function using `re.fullmatch()`, and write a short comment
explaining why this validation alone is not sufficient to guarantee the
email address is real and deliverable (§48).

**19.** Given a mixed batch of raw records where some are valid CSV
rows and some are malformed (wrong number of fields), write a pipeline
that separates valid from invalid records and reports the invalid ones
with their original line number.

**20.** Design (in words, then in code) a small pipeline for
ingesting semi-structured support-ticket text, extracting a ticket ID,
a priority level, and a free-text description, and explain, for each
step, whether you chose a simple string operation, `csv`/`json`, or
regex, and why.

## 65. Mini Project

**"Log Parsing and Alerting Pipeline"**

### Requirements

Given a block of raw, multi-line server log text, build a pipeline that:

1. Splits the raw text into individual lines.
2. Parses each line into a structured record (timestamp, severity
   level, message), using a compiled, named-group regex pattern.
3. Filters out any line that does not match the expected log format,
   collecting these separately as "unparseable" lines rather than
   silently discarding or crashing on them.
4. Filters the successfully parsed records to only `ERROR` and
   `CRITICAL` severity levels.
5. Extracts, from each error message, any embedded transaction ID
   matching the pattern `T\d+` (e.g., `T12345`), using a named group.
6. Groups the filtered error records by their extracted transaction ID
   (records with no transaction ID go into a `"none"` group), reusing
   the grouping chapter's `defaultdict(list)` pattern (grouping
   chapter's §6).
7. Counts how many errors occurred at each severity level, reusing the
   counting chapter's `Counter` pattern (grouping chapter's §5.6).
8. Produces a final summary report combining all of the above.

### Before implementing, document:

- **Problem** — turn a raw block of unstructured log text into an
  actionable summary, robust to some lines not matching the expected
  format at all.
- **Inputs** — a single multi-line string of raw log text.
- **Outputs** — a list of unparseable lines; a list of parsed error/
  critical records; a dictionary grouping error records by transaction
  ID; a count of records per severity level; one combined summary
  dictionary.
- **Assumptions** — most lines follow the format `YYYY-MM-DD HH:MM:SS
  LEVEL: message`; some lines may be malformed (e.g., from a different
  subsystem with its own log format) and must not crash the pipeline;
  not every error message contains a transaction ID.
- **Edge cases** — an entirely empty input; a block where every line is
  malformed; an error message containing more than one `T\d+`-shaped
  substring (decide explicitly: this project takes the *first* match
  per line); a log level in unexpected casing.
- **Pseudocode:**
  ```
  lines = split raw text into lines
  parsed, unparseable = [], []
  for each line:
      strip whitespace; skip if empty
      match against the compiled log pattern
      if match: parsed.append(match.groupdict())
      else: unparseable.append(line)

  severity_counts = Counter of every parsed record's level
  serious = filter parsed records where level in {"ERROR", "CRITICAL"}

  errors_by_transaction = defaultdict(list)
  for each serious record:
      find first T\d+ match in its message, or use "none"
      append record to errors_by_transaction[that key]

  summary = combine unparseable, severity_counts, errors_by_transaction
  ```
- **Complexity** — every stage is a single O(n) pass over the lines
  (Big-O chapter's §27), where `n` is the number of lines; the regex
  pattern is compiled once and reused, per §43 and §61's guidance for
  code applying the same pattern repeatedly.

### Reference Implementation

```python
import re
from collections import defaultdict, Counter


LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+): (?P<message>.+)"
)
TRANSACTION_PATTERN = re.compile(r"T\d+")


def parse_log_text(text):
    parsed, unparseable = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = LOG_PATTERN.fullmatch(line)
        if match:
            parsed.append(match.groupdict())
        else:
            unparseable.append(line)
    return parsed, unparseable


def build_report(text):
    parsed, unparseable = parse_log_text(text)

    severity_counts = Counter(record["level"] for record in parsed)

    serious = [r for r in parsed if r["level"] in ("ERROR", "CRITICAL")]

    errors_by_transaction = defaultdict(list)
    for record in serious:
        match = TRANSACTION_PATTERN.search(record["message"])
        key = match.group() if match else "none"
        errors_by_transaction[key].append(record)

    return {
        "unparseable_lines": unparseable,
        "severity_counts": dict(severity_counts),
        "errors_by_transaction": dict(errors_by_transaction),
        "total_serious": len(serious),
    }
```

```python
log_text = """
2026-01-15 10:00:00 INFO: server started
2026-01-15 10:05:23 ERROR: payment failed for T12345
2026-01-15 10:05:24 ERROR: retry failed for T12345
this line does not match the expected format at all
2026-01-15 10:06:01 CRITICAL: database unreachable
"""

report = build_report(log_text)
print(report["severity_counts"])
# {'INFO': 1, 'ERROR': 2, 'CRITICAL': 1}
print(report["errors_by_transaction"].keys())
# dict_keys(['T12345', 'none'])
print(report["unparseable_lines"])
# ['this line does not match the expected format at all']
```

**The lesson this project demonstrates concretely:** the parsing
techniques from this chapter (compiled patterns, named groups,
fullmatch-based structural validation, extraction of an embedded
sub-pattern) combine directly and naturally with this module's earlier
chapters' own techniques (filtering, grouping with `defaultdict`,
counting with `Counter`) — parsing is not a separate discipline from
everything else this module has taught; it is the first step that
makes all of that other work possible on real, raw text.

## 66. Review Checklist

- [ ] I can explain the difference between raw text, semi-structured
      text, and fully structured data.
- [ ] I can explain the difference between parsing, string
      manipulation, and validation.
- [ ] I can choose correctly between `split()`, `partition()`,
      `startswith()`/`endswith()`, and `replace()` for a fixed-structure
      parsing task, and justify the choice.
- [ ] I know when to reach for the `csv` or `json` modules instead of
      manual string splitting, and can explain why hand-parsing either
      format is a mistake.
- [ ] I can read an unfamiliar, moderately complex regex pattern and
      explain what it matches, piece by piece.
- [ ] I can write a regex pattern incrementally, testing each addition,
      rather than attempting a complete complex pattern in one attempt.
- [ ] I understand the difference between `re.search()`, `re.match()`,
      and `re.fullmatch()`, and can choose correctly among them for a
      given task.
- [ ] I can extract structured data from text using capturing groups
      and named groups.
- [ ] I can perform pattern-based text transformation using `re.sub()`,
      including group backreferences in the replacement.
- [ ] I understand why greedy quantifiers can match more than intended,
      and how to fix this with a non-greedy quantifier.
- [ ] I can explain catastrophic backtracking and ReDoS at a conceptual
      level, and recognize the nested-quantifier pattern shape that
      causes it.
- [ ] I can judge, for a new text-processing problem, whether a simple
      string operation, a standard-library parser, or regex is the
      right tool — and can articulate why.
- [ ] I understand that regex is not a substitute for a real parser for
      nested or recursively structured formats.

## 67. Interview Questions

**Foundational**

- What is parsing? How does it differ from simple string manipulation?
- What is the difference between `split()` and `partition()`? When
  would you use one over the other?
- Why should you use the `csv` module instead of manually splitting on
  commas?
- Why should you use the `json` module instead of writing a custom
  JSON parser?
- What is a regular expression, conceptually?

**Intermediate**

- What is the difference between `re.search()`, `re.match()`, and
  `re.fullmatch()`?
- What is a capturing group? What is a non-capturing group, and when
  would you use one instead of a capturing group?
- What is the difference between `*` and `+` as quantifiers?
- Why should regex patterns in Python always be written as raw strings?
- What does `re.findall()` return when the pattern contains capturing
  groups, versus when it does not?
- What is the difference between a greedy and a non-greedy quantifier?
  Give an example where the difference changes the result.

**Advanced**

- What is catastrophic backtracking, and why can it be a security
  concern (ReDoS)? What pattern shape should you watch for?
- Why can't a single regular expression correctly parse arbitrarily
  nested JSON in the general case?
- What is the difference between a lookahead and a capturing group?
  Why might you prefer one over the other in a specific case?
- When should you compile a regex pattern with `re.compile()`, and what
  performance characteristic does compiling actually improve (and not
  improve)?
- How would you decide, for a new text-processing task, whether to use
  a simple string method, a standard-library parser, or a regular
  expression?

**Scenario-based**

- "You're processing a large log file and need to extract every error
  message along with its timestamp. Walk through your approach, tool by
  tool."
- "A teammate wrote a regex to parse CSV data and it occasionally
  produces corrupted fields. What is the likely cause, and what would
  you recommend instead?"
- "You need to validate that user-submitted phone numbers match one of
  three acceptable formats. How would you approach this, and would you
  use `re.search()` or `re.fullmatch()`? Why?"
- "A regex-based validation function in production started taking
  several seconds to respond to certain unusual inputs. What would you
  investigate, and what might explain it?"

## 68. Answer Key and Reference Solutions

### Level 1

**1.** A fixed, single-character delimiter — `str.split()` is the
correct, simplest tool (§7, §55).
```python
print("apple,banana,cherry".split(","))   # ['apple', 'banana', 'cherry']
```

**2.** `.strip()` (§11) removes whitespace from both ends directly.
```python
print("  hello world  ".strip())   # "hello world"
```

**3.** `.partition("=")` (§8) splits into exactly the key, the
separator, and the value.
```python
key, _, value = "key=value".partition("=")
print(key, value)   # key value
```

**4.** `.endswith()` (§13) is the direct, correct tool — no regex
needed for a fixed literal suffix.
```python
print("report.csv".endswith(".csv"))   # True
```

**5.** A structural validation — `re.fullmatch()` (§37, §48) is
appropriate since the *entire* string must conform.
```python
import re
print(re.fullmatch(r"\d{4}-\d{2}-\d{2}", "2026-01-15") is not None)   # True
```

### Level 2

**6.** Directly §17's pattern.
```python
def parse_records(lines):
    records = []
    for line in lines:
        name, age, country = line.split(",")
        records.append({"name": name, "age": int(age), "country": country})
    return records

print(parse_records(["John,25,India", "Ada,30,UK"]))
```

**7.** `re.findall()` (§38) with an email-shaped pattern.
```python
import re
print(re.findall(r"\w+@\w+\.\w+", "Contact: john@example.com or ada@example.org"))
# ['john@example.com', 'ada@example.org']
```

**8.** Combining a capturing group (§30) with `float()` conversion —
mirroring the type-conversion lesson from §17.
```python
import re
match = re.search(r"\$(\d+\.\d+)", "price: $45.00")
print(float(match.group(1)))   # 45.0
```

**9.** `re.split()` (§40) is correct here specifically because the
delimiter itself (comma plus variable surrounding whitespace) is not a
single fixed string.
```python
import re
print(re.split(r"\s*,\s*", "John,  25 ,India"))   # ['John', '25', 'India']
```

**10.** Directly §50's `to_snake_case` example.
```python
import re
def to_snake_case(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

print(to_snake_case("myVariableNameHere"))   # "my_variable_name_here"
```

### Level 3

**11.** Directly §49's named-group extraction pattern.
```python
import re
match = re.search(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>\w+): (?P<message>.+)",
    "2026-01-15 10:00:00 ERROR: disk full",
)
print(match.groupdict())
```

**12.** Directly §19's worked example and its reasoning: `str.split(",")`
splits on every comma unconditionally, incorrectly breaking apart a
quoted field's own internal comma; `csv.reader` correctly respects
quoting rules.
```python
import csv, io
rows = list(csv.reader(io.StringIO('John,"Smith, Jr.",25')))
print(rows)   # [['John', 'Smith, Jr.', '25']]
```

**13.** Combining `json.loads()` (§20) with the previous chapter's
recursive flattening template (recursion chapter's §33, §46).
```python
import json

def flatten(data, path=""):
    result = {}
    if isinstance(data, dict):
        for key, value in data.items():
            result.update(flatten(value, f"{path}.{key}" if path else key))
    else:
        result[path] = data
    return result

config = json.loads('{"a": {"b": {"c": 1}}}')
print(flatten(config))   # {'a.b.c': 1}
```

**14.** Directly §50's redaction pattern.
```python
import re
def redact(text):
    return re.sub(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b", "[REDACTED]", text)

print(redact("Card: 1234-5678-9012-3456"))   # "Card: [REDACTED]"
```

**15.** Directly §60's central lesson.
`(a+)+b` is dangerous because the outer `+` can repeat the inner `a+`
group in many different, overlapping ways to match the same run of
`a`s — when the input ultimately fails to match (no trailing `b`), the
engine must try an exponentially growing number of these equivalent
groupings before giving up. The safe equivalent, `a+b`, expresses
"one or more `a`s, then `b`" directly, without any nested quantifier,
and matches exactly the same intended strings without the
backtracking explosion.

### Level 4

**16.** Directly combining §51's log-parsing pattern with the grouping
chapter's `Counter` (grouping chapter's §5.6) and the search chapter's
filter pattern (search chapter's §6).
```python
import re
from collections import Counter

log_pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>\w+): (?P<message>.+)"
)

def error_message_counts(log_text):
    records = [
        log_pattern.search(line).groupdict()
        for line in log_text.splitlines()
        if log_pattern.search(line)
    ]
    errors = [r for r in records if r["level"] == "ERROR"]
    return Counter(r["message"] for r in errors)
```

**17.** A single `re.sub()` call (§41, §52) is preferred here over a
chain of `.replace()` calls: it expresses "remove every character from
this set" as one declarative pattern, rather than one `.replace()` call
per specific character, and automatically covers any additional
punctuation variant without needing a new `.replace()` call added for
each one.
```python
import re
def normalize_phone(number):
    return re.sub(r"[^\d]", "", number)

print(normalize_phone("(555) 123-4567"))   # "5551234567"
```

**18.** Directly §48's validation pattern and its explicit caveat.
```python
import re
def is_valid_email_format(email):
    return re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", email) is not None

# This only checks the SHAPE of the address, not whether it actually
# exists or can receive mail — a confirmation email is the only reliable
# way to verify true deliverability (§48).
```

**19.** Uses `csv.reader` (§19) with explicit line-number tracking and a
simple field-count check, separating valid from malformed rows without
crashing on the malformed ones — directly mirroring the mini project's
own "collect unparseable lines separately" approach (§65).
```python
import csv, io

def separate_valid_invalid(csv_text, expected_fields=3):
    valid, invalid = [], []
    for line_number, row in enumerate(csv.reader(io.StringIO(csv_text)), start=1):
        if len(row) == expected_fields:
            valid.append(row)
        else:
            invalid.append((line_number, row))
    return valid, invalid
```

**20.** A reasonable design: split on lines first (§9, simple);
extract the ticket ID and priority with a compiled, named-group regex
(§43, §45, since these are pattern-shaped, variable-length fields
embedded in otherwise free-form text); keep the remaining free-text
description as-is (no further parsing needed — it is meant to stay
unstructured). Each tool choice is justified by matching §5's strategy
table: fixed line boundaries → simple split; a recognizable but
variable-shaped embedded pattern → regex; genuinely free text → no
further parsing at all.

## 69. Final Mental Model

**PARSING = "turning raw or semi-structured text into structured data
your program can actually work with."**

```
FIXED, KNOWN STRUCTURE?
    → simple string operations: split(), partition(), startswith(),
      endswith(), replace(), strip(), join()

A STANDARD, WELL-DEFINED FORMAT?
    → a dedicated library: csv, json — never hand-rolled parsing

A VARIABLE PATTERN OR SHAPE, WITHIN OTHERWISE SIMPLE TEXT?
    → regular expressions (re) — built incrementally, tested
      deliberately, used with raw strings

DEEPLY NESTED OR RECURSIVELY STRUCTURED?
    → a real parser, or the recursive techniques from the
      previous chapter — never regex alone
```

And the chapter's two standing reminders, each restated one final
time because each was emphasized throughout:

**"Use the simplest tool that correctly matches the text's actual
structure — reach for regex only once a pattern, not a fixed
structure, is genuinely what needs to be recognized."**

**"Regex is a powerful, general pattern-matching tool — not a
parser, not a replacement for `csv`/`json`, and not something to
apply to untrusted input without understanding its performance and
security implications."**
