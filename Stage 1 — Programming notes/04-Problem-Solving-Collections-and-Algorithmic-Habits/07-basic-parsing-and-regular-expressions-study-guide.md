# 07 — Basic Parsing and Regular Expressions
## Complete Study Guide, Exercise Solutions, and Log Parsing Mini-Project

**Source:** `07-basic-parsing-and-regular-expressions.md`  
**Roadmap:** Stage 1 → Module 04 — Problem-Solving, Collections, and Algorithmic Habits  
**Learning approach:** Beginner-friendly explanations, practical examples, and solutions restricted to the concepts already introduced in the project tree.

---

# Part A — Complete chapter summary (under 5,000 words)

## 1. Parsing: turning text into usable data

**Parsing** means converting raw or semi-structured text into structured Python data such as lists and dictionaries.

```python
raw = "John,25,India"
record = {"name": "John", "age": 25, "country": "India"}
```

The first value is one string. The second has named fields that code can look up, filter, group, and aggregate. Parsing is therefore the bridge between external text and the collection-processing techniques from earlier lessons.

Parsing is used for server logs, CSV exports, API responses, configuration, user commands, data cleaning, and AI/ML document preprocessing. If parsing is wrong, later filtering and aggregation can produce incorrect results even if those later steps are written correctly.

### Raw, semi-structured, and structured data

- **Raw text:** a string with no parsed fields, e.g. `"John,25,India"`.
- **Semi-structured text:** contains recognizable separators or patterns but has not yet been converted to records, e.g. a CSV row or log line.
- **Structured data:** Python dictionaries, lists, and records that can be navigated directly.

### Parsing vs string manipulation vs validation

```python
text = "  JOHN@EXAMPLE.COM  "
cleaned = text.strip().lower()       # manipulation: normalize text
is_valid = "@" in cleaned            # validation: yes/no check
username, domain = cleaned.split("@")  # parsing: extract two fields
```

- **String manipulation** changes or inspects text (`strip`, `lower`, `replace`).
- **Validation** checks whether data follows a rule.
- **Parsing** extracts fields or structure.

A real workflow may clean first, validate second, and parse third.

## 2. Choose the right parsing strategy

| Input structure | Appropriate tool |
|---|---|
| Fixed delimiter such as comma, pipe, or tab | `split()` |
| One separator, with everything after it kept together | `partition()` |
| Known prefix or suffix | `startswith()` / `endswith()` |
| Special character-by-character rules | Manual parsing with state |
| Standard CSV or JSON | `csv` or `json` library |
| Variable pattern embedded in text | Regular expressions (`re`) |

Use the simplest tool that correctly handles the format. Regex is excessive for a fixed comma; `.split(",")` is unsafe for genuine CSV when quoted fields can contain commas.

A **delimiter/separator** is the character or sequence marking field boundaries, such as `,`, `-`, or `\t`.

## 3. Essential string parsing methods

### `split()`

```python
"John,25,India".split(",")          # ['John', '25', 'India']
"hello   world\tfoo".split()        # ['hello', 'world', 'foo']
"a,,b".split(",")                   # ['a', '', 'b']
"key=value=with=equals".split("=", maxsplit=1)
# ['key', 'value=with=equals']
```

`split(separator)` returns a list, splitting at each separator. With no separator, it splits on runs of whitespace and does not produce empty fields for repeated spaces. With an explicit separator, adjacent delimiters produce empty strings. `maxsplit=1` limits splitting to one occurrence.

### `partition()`

```python
"key=value".partition("=")          # ('key', '=', 'value')
"no-equals".partition("=")          # ('no-equals', '', '')
timestamp, separator, message = "2026-01-15: server: started".partition(": ")
```

`partition()` always returns a three-item tuple: before the first separator, the separator itself, and everything after it. It is useful when the rest of the text may contain the same separator. Unlike unrestricted `split()`, it does not accidentally split the message again.

### `splitlines()` and `join()`

```python
"line one\nline two\r\nline three".splitlines()
# ['line one', 'line two', 'line three']

fields = ["John", "25", "India"]
",".join(fields)                    # 'John,25,India'
```

`splitlines()` handles common newline conventions. `join()` combines strings using the separator on which it is called. A common cleanup pipeline:

```python
line = "  John , 25 , India  "
cleaned = ",".join(field.strip() for field in line.split(","))
# 'John,25,India'
```

This combines splitting, trimming, and joining; the generator expression avoids creating an extra intermediate list.

### `strip()`, `lstrip()`, and `rstrip()`

```python
"  hello  ".strip()       # 'hello'
"  hello  ".lstrip()      # 'hello  '
"  hello  ".rstrip()      # '  hello'
"***important***".strip("*")  # 'important'
```

They remove whitespace from both ends, left end, or right end. An argument specifies characters to remove from the ends (any of those characters), not an exact substring. Strip parsed fields before comparing them; `" John"` is not equal to `"John"`.

### `find()`, `index()`, `count()`, and `in`

```python
text = "error: connection refused"
text.find("error")       # 0
text.find("missing")     # -1 (does not raise)
text.index("error")      # 0
text.count("r")          # 3
"error" in text          # True
```

`find()` returns the first position or `-1`; `index()` returns the position but raises `ValueError` if absent. Use `in` for a simple yes/no membership question; use `find`/`index` when the position matters.

### `startswith()` and `endswith()`

```python
line = "ERROR: disk full"
line.startswith("ERROR")                 # True
line.startswith(("ERROR", "WARNING"))    # True
"report.csv".endswith(".csv")            # True
```

Use these for fixed prefixes/suffixes, such as log severity routing or file-extension checks. They are clearer than regex for literal checks.

### `replace()` and normalization

```python
"2026-01-15".replace("-", "/")  # '2026/01/15'

number = "(555) 123-4567"
clean = number.replace("(", "").replace(")", "").replace(" ", "").replace(".", "").replace("-", "")
# '5551234567'
```

`replace(old, new)` replaces every occurrence of a fixed substring. Chaining works for a small number of known characters, but becomes difficult to read when many variants must be removed. Later, `re.sub()` can express a character set in one operation.

## 4. Manual parsing and state

For a simple key-value format, combine existing string tools:

```python
def parse_simple_key_values(text):
    result = {}
    for pair in text.split(";"):
        pair = pair.strip()
        if not pair:
            continue
        key, separator, value = pair.partition("=")
        result[key.strip()] = value.strip()
    return result

parse_simple_key_values("name = John; age = 25 ; country=India")
# {'name': 'John', 'age': '25', 'country': 'India'}
```

The loop processes each pair; empty pairs are skipped; `partition()` separates key and value; `strip()` removes surrounding whitespace.

**Stateful parsing** means remembering information from earlier characters because it changes how later characters should be interpreted. Example: a comma inside quotation marks is data, not a field separator.

```python
def split_respecting_quotes(text, delimiter=","):
    fields, current = [], []
    inside_quotes = False
    index = 0

    while index < len(text):
        char = text[index]
        if char == '"':
            if inside_quotes and text[index + 1:index + 2] == '"':
                current.append('"')
                index += 1
            else:
                inside_quotes = not inside_quotes
        elif char == delimiter and not inside_quotes:
            fields.append("".join(current))
            current = []
        else:
            current.append(char)
        index += 1

    if inside_quotes:
        raise ValueError("Unmatched quote in input")

    fields.append("".join(current))
    return fields

split_respecting_quotes('a,"b,c",d')          # ['a', 'b,c', 'd']
split_respecting_quotes('a,"say ""hi""",d')    # ['a', 'say "hi"', 'd']
```

`inside_quotes` is the state. A delimiter is a separator only outside quotes; doubled quotes inside quoted content represent one literal quote. This is a teaching sketch with limited rules, not a replacement for CSV parsing. Real CSV has more dialect and edge-case rules, so use the standard library.

### Parsing key-value records and converting types

A parser can split records and convert numeric text:

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
records = parse_records(raw_lines)
# [{'name': 'John', 'age': 25, 'country': 'India'},
#  {'name': 'Ada', 'age': 30, 'country': 'UK'}]

average_age = sum(record["age"] for record in records) / len(records)
# 27.5
```

The input age begins as a string. `int()` converts it to a number so numeric comparison and aggregation work correctly. Production parsing must handle invalid rows and failed conversions rather than assuming every row is valid.

### Nested or semi-structured text

```python
line = "T1|John|apple:2,banana:3|completed"
transaction_id, customer, items_raw, status = line.split("|")

items = {}
for item in items_raw.split(","):
    name, separator, quantity = item.partition(":")
    items[name] = int(quantity)

# T1 John {'apple': 2, 'banana': 3} completed
```

Split the outer record by `|`, then parse the item field separately by comma and colon. This is useful for simple known formats, but repeated manual splitting becomes fragile as nesting and escaping rules grow.

## 5. Use dedicated parsers for CSV and JSON

### CSV: why `.split(",")` can corrupt data

```python
line = 'John,"Smith, Jr.",25'
line.split(",")
# ['John', '"Smith', ' Jr."', '25']  -- incorrect
```

The comma inside the quoted surname is part of the field. `.split(",")` does not understand CSV quoting.

```python
import csv
import io

raw_csv = 'name,role\nJohn,"Senior Engineer, Backend"\nAda,Manager'
rows = list(csv.reader(io.StringIO(raw_csv)))
# [['name', 'role'],
#  ['John', 'Senior Engineer, Backend'],
#  ['Ada', 'Manager']]

records = list(csv.DictReader(io.StringIO(raw_csv)))
# [{'name': 'John', 'role': 'Senior Engineer, Backend'},
#  {'name': 'Ada', 'role': 'Manager'}]
```

`csv.reader()` returns rows as lists. `csv.DictReader()` uses the header row as dictionary keys. Use `csv` for genuine CSV, including quoted commas and escaping.

### JSON

```python
import json

raw_json = '{"name": "John", "age": 25, "tags": ["admin", "active"]}'
data = json.loads(raw_json)
# {'name': 'John', 'age': 25, 'tags': ['admin', 'active']}
type(data["age"])  # int

json.dumps({"name": "John", "age": 25})
# '{"name": "John", "age": 25}'
```

`json.loads()` converts JSON text into native Python dictionaries, lists, strings, numbers, booleans, and `None`. `json.dumps()` converts Python data back to JSON text. Do not hand-parse CSV or JSON with splitting or regex: their formats have quoting, escaping, and nesting rules already handled by standard-library parsers.

## 6. Regular expressions (regex): recognizing patterns

A **regular expression** is a small language for describing a text pattern, not just one exact string. For example, `r"\d{3}-\d{4}"` describes three digits, a hyphen, and four digits. It can match many values such as `555-1234` and `000-0000`.

Use regex when the target has variable shape (email-like text, phone formats, log fields), not when a simple fixed string method already solves the task. Regex is powerful but can be hard to maintain, is not a parser for nested formats, and can have performance/security risks.

Python's module:

```python
import re
re.search(pattern, text)
```

The engine interprets literal characters as themselves and metacharacters as pattern instructions. Build patterns incrementally and test each addition.

### Literals and metacharacters

```python
re.search("cat", "concatenate")  # match
re.search("dog", "concatenate")  # None
re.search("c.t", "cat")          # match
re.search("c.t", "cot")          # match
re.search("c.t", "ct")           # None
```

`.` matches any one character except newline. Common metacharacters include:

```text
. ^ $ * + ? { } [ ] \ | ( )
```

### Character classes

```python
re.search("[aeiou]", "sky")      # None
re.search("[aeiou]", "cat")      # finds 'a'
re.search("[0-9]", "abc123")     # finds '1'
re.search("[a-z]", "ABC")        # None
re.search("[^0-9]", "123abc")    # finds 'a'
```

`[...]` matches one character from the set/range; `^` at the beginning inside the brackets negates the set.

| Shorthand | Meaning |
|---|---|
| `\d` / `\D` | digit / non-digit |
| `\w` / `\W` | word character (Unicode letters, digits, underscore) / non-word |
| `\s` / `\S` | whitespace / non-whitespace |

For Python string patterns, `\d` and `\w` are Unicode-aware by default. Use `[0-9]` or `re.ASCII` when ASCII-only matching is required.

### Quantifiers

| Syntax | Meaning |
|---|---|
| `*` | zero or more |
| `+` | one or more |
| `?` | zero or one |
| `{n}` | exactly n |
| `{n,}` | at least n |
| `{n,m}` | n through m inclusive |

```python
re.search(r"\d*", "abc")          # matches empty text: zero digits allowed
re.search(r"\d+", "abc")          # None: at least one digit required
re.search(r"colou?r", "color")    # match: u is optional
re.search(r"\d{3}", "12")         # None
re.search(r"\d{3}", "1234")       # matches '123'
re.search(r"\d{3,4}", "12345")    # matches '1234'
```

Be deliberate: `*` permits zero occurrences; `+` requires at least one.

### Anchors and word boundaries

```python
re.search(r"^Hello", "Hello world")  # start
re.search(r"^Hello", "Say Hello")    # None
re.search(r"world$", "Hello world")  # end
re.search(r"\bcat\b", "concatenate") # None
re.search(r"\bcat\b", "the cat sat") # match
```

`^` and `$` match positions at the start and end. In Python, `$` can also match before a final newline; use `re.fullmatch()` when the entire input must match. `\b` matches a boundary between a word and non-word character (or string edge).

### Groups, captures, alternation, and escaping

```python
re.search(r"(ab)+", "ababab")  # '+' applies to the whole 'ab' group
re.search(r"ab+", "abbb")      # '+' applies only to 'b'
```

Parentheses group several pattern elements. A **capturing group** stores matched text:

```python
match = re.search(r"(\d{4})-(\d{2})-(\d{2})", "Date: 2026-01-15")
match.group(0)  # '2026-01-15' entire match
match.group(1)  # '2026'
match.group(2)  # '01'
match.group(3)  # '15'
match.groups()  # ('2026', '01', '15')
```

`(?:...)` is a non-capturing group: it groups for quantifiers/alternation without adding a captured value.

```python
match = re.search(r"(?:https?://)?(\w+\.com)", "Visit https://example.com")
match.group(1)  # 'example.com'
```

`|` means OR; parentheses control its scope:

```python
re.search(r"cat|dog", "I have a dog")  # match 'dog'
re.search(r"gr(a|e)y", "grey")         # match 'grey'
```

Escape a metacharacter to match it literally:

```python
re.search(r"3.14", "3x14")   # matches: '.' is a wildcard
re.search(r"3\.14", "3x14")  # None: literal period required
```

Other literal metacharacters can be escaped similarly (`\*`, `\+`, `\?`, `\(`, `\)`, `\[`, `\]`, `\{`, `\}`, `\|`, `\\`).

### Raw strings

Python itself interprets backslashes in normal strings (`"\n"` becomes a newline), while regex also uses backslashes (`\d`, `\s`). Raw strings pass the backslashes through as typed:

```python
re.search(r"\d+", text)     # recommended
re.search("\\d+", text)     # equivalent but requires doubled slashes
```

Write regex patterns as raw strings (`r"..."`) consistently to avoid Python string-escape confusion.

## 7. Main functions in Python's `re` module

```python
re.search(r"\d+", "Order 12345")  # first match anywhere; returns Match or None
re.match(r"\d+", "12345 order")   # match only at position zero
re.fullmatch(r"\d+", "12345")     # entire input must be digits
re.findall(r"\w+@\w+\.\w+", text) # list of all non-overlapping matches
```

Always check for `None` before calling `.group()` on a possible match.

If `findall()` has no capturing groups, it returns full matched strings. With one group it returns that group's text; with multiple groups it returns tuples of captured text.

```python
for match in re.finditer(r"\w+@\w+\.\w+", text):
    print(match.group(), match.start(), match.end())
```

`finditer()` returns an iterator of Match objects, preserving positions and groups; prefer it when positions or full match details matter.

```python
re.split(r"\s*,\s*", "John,  25,India")
# ['John', '25', 'India']

re.sub(r"\d", "#", "Card: 1234-5678")
# 'Card: ####-####'

re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\2/\3/\1", "2026-01-15")
# '01/15/2026'

result, count = re.subn(r"\d", "#", "Card: 1234-5678")
# result='Card: ####-####', count=8
```

`re.split()` splits on a variable pattern; `re.sub()` returns text with all matches replaced; replacement backreferences such as `\1` reuse captured groups; `re.subn()` also returns the number of replacements.

### Compiled patterns

```python
pattern = re.compile(r"\d{3}-\d{4}")
pattern.search("Call 555-1234")
pattern.findall("555-1234 or 555-5678")
```

Compile once when repeatedly reusing a pattern or when a named pattern object improves clarity. Python also caches recently used module-level patterns, so explicit compilation is not guaranteed to create a dramatic speedup. It does not change the fundamental complexity of matching.

### Flags

- `re.IGNORECASE` / `re.I`: ignore letter case.
- `re.MULTILINE` / `re.M`: `^` and `$` apply to each line.
- `re.DOTALL` / `re.S`: `.` also matches newlines.
- `re.VERBOSE` / `re.X`: ignore formatting whitespace and allow comments in a pattern.

```python
re.search(r"hello", "HELLO", re.IGNORECASE)

text = "Line one\nLine two\nLine three"
re.findall(r"^Line \w+$", text, re.MULTILINE)
# ['Line one', 'Line two', 'Line three']

pattern = re.compile(r"""
    (\d{4})   # year
    -
    (\d{2})   # month
    -
    (\d{2})   # day
""", re.VERBOSE)
```

Flags can be combined with `|`, e.g. `re.IGNORECASE | re.MULTILINE`.

### Named groups and backreferences

```python
match = re.search(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})",
    "2026-01-15",
)
match.group("year")  # '2026'
match.groupdict()    # {'year': '2026', 'month': '01', 'day': '15'}
```

Named groups make patterns with multiple fields easier to read and directly produce dictionaries. Prefer them over numbered groups once there are several fields.

A **backreference** requires the exact text captured earlier to appear again:

```python
re.search(r"(\w+) \1", "hello hello world")  # matches 'hello hello'
re.search(r"\b(\w+)\s+\1\b", "the the cat sat")  # duplicate word
```

### Lookarounds

Lookarounds test nearby context without consuming it as part of the match:

```python
re.findall(r"\d+(?=px)", "width: 100px, height: 50em")  # ['100']
re.findall(r"(?<=\$)\d+", "Price: $100, Quantity: 50")  # ['100']
re.findall(r"(?<!\$)\b\d+", "Price: $100, Quantity: 50") # ['50']
```

- `(?=...)`: positive lookahead; `(?!...)`: negative lookahead.
- `(?<=...)`: positive lookbehind; `(?<!...)`: negative lookbehind.

Lookbehind in Python's standard `re` engine requires fixed-length patterns. A negative lookahead without a complete boundary can match only part of a number; always test boundaries. These are advanced tools; understand their purpose before using them heavily.

## 8. Validation, extraction, and transformation

### Validation

```python
def is_valid_simple_email(text):
    return re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", text) is not None
```

`fullmatch()` checks the entire input. This is a simple shape check, not a complete implementation of every valid email rule and not proof that an address exists or can receive mail. Real deliverability is verified by sending a confirmation message.

### Extraction into a record

```python
log_line = "2026-01-15 10:30:00 ERROR: connection refused"
pattern = (
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+): (?P<message>.+)"
)
match = re.search(pattern, log_line)
record = match.groupdict()
# {'date': '2026-01-15', 'time': '10:30:00',
#  'level': 'ERROR', 'message': 'connection refused'}
```

Named groups extract fields from one semi-structured line into a dictionary.

### Transformation

```python
def redact_card_numbers(text):
    return re.sub(
        r"\b\d{4}-\d{4}-\d{4}-\d{4}\b",
        "****-****-****-****",
        text,
    )

def to_snake_case(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
```

The redaction replaces every card-shaped string. The snake-case lookaround inserts `_` immediately before each capital letter except the first, then lowercases the result. Redaction patterns must be treated as format filters, not proof that all real card formats have been covered.

### Practical text processing

```python
text = "The Quick Brown Fox Jumps Over The Lazy Dog"
capitalized_words = re.findall(r"\b[A-Z]\w*\b", text)
word_count = len(re.findall(r"\b\w+\b", text))
```

Regex can identify word-shaped patterns, count matches, and extract capitalized words. These are pattern-based versions of earlier search/count techniques.

### Combining string methods and regex

```python
def parse_log_file(text, log_pattern):
    records = []
    for line in text.splitlines():       # fixed line boundary: string method
        line = line.strip()              # whitespace cleanup: string method
        if not line:
            continue
        match = log_pattern.search(line) # variable fields: regex
        if match:
            records.append(match.groupdict())
    return records
```

Use simple methods for lines and whitespace; use regex only for the variable pattern within a line. This division of responsibilities is the intended parsing style.

## 9. Greedy matching, complexity, security, and production practice

Quantifiers are **greedy** by default: they try to consume as much text as possible while still allowing a match. Add `?` after a quantifier to make it non-greedy:

```python
re.search(r"<.*>", "<b>bold</b> and <i>italic</i>").group()
# '<b>bold</b> and <i>italic</i>' -- too much

re.search(r"<.*?>", "<b>bold</b> and <i>italic</i>").group()
# '<b>'
```

### Common mistakes

1. Not escaping a literal `.` (`r"3.14"` also matches `3x14`; use `r"3\.14"`).
2. Using `*` when at least one character is required (use `+`).
3. Forgetting raw-string prefix (use `r"..."`).
4. Misunderstanding alternation scope (`r"gr(a|e)y"`).
5. Using `search()` for whole-input validation (use `fullmatch()`).
6. Forgetting `findall()` returns captured groups when groups exist.
7. Greedy `.*` captures too much (consider `.*?`).
8. Using regex for a fixed prefix when `startswith()` is enough.
9. Parsing CSV/JSON with regex instead of their parser.
10. Writing complex unreadable patterns without comments or `re.VERBOSE`.

### Debugging regex systematically

1. Build the pattern one piece at a time.
2. Test both strings that should match and strings that should fail.
3. Print the Match object and inspect its span.
4. Inspect `.groups()` or `.groupdict()` one field at a time.
5. Use a regex visualizer if a pattern is difficult to trace.
6. If still hard to reason about, simplify, split into smaller steps, or use a string method/dedicated parser.

### Complexity and catastrophic backtracking

A simple regex often scans text in roughly O(n), but this is not guaranteed for every pattern. Certain nested/overlapping quantifiers can cause exponentially many alternative match paths. Compiling a pattern avoids repeated pattern preparation but does not change the algorithmic matching complexity.

```python
dangerous_pattern = r"(a+)+b"
```

On a long run of `a` characters followed by a character that cannot satisfy `b`, the engine may explore many possible ways to partition the `a`s before failing. This is **catastrophic backtracking**.

**ReDoS (Regular Expression Denial of Service)** occurs when an attacker supplies input that makes a vulnerable regex consume excessive CPU, potentially blocking a service.

Production safeguards:
- Avoid nested quantifiers over overlapping character sets, e.g. `(a+)+` and `(a*)*`.
- Prefer simpler and more specific patterns.
- Bound the size of untrusted input and test adversarial examples.
- Python's standard `re` functions do not provide a timeout parameter; if a hard timeout is required, use an engine that supports it or isolate matching in a time-limited process.
- Do not avoid regex entirely; use it with awareness of pattern shape and input trust.

### Production guidelines

- Select the simplest correct tool.
- Always use raw strings for regex patterns.
- Consider compiling patterns reused in loops; do not assume a guaranteed speedup.
- Prefer named groups for multi-field patterns.
- Use `re.VERBOSE` and comments for complex patterns.
- Use `csv`/`json` for those formats and a real parser for nested structures.
- Test positive and negative examples.
- Document why the pattern exists and what it is intended to match.

## 10. Data Engineering and Applied AI applications

- **Log processing:** parse timestamps, severity, and messages, then filter/group/count errors.
- **Data cleaning:** normalize inconsistent numeric, date, and categorical values before analytics or model training.
- **NLP/retrieval:** extract dates, entities, and section headers from semi-structured documents; use recursion too when the document is nested.
- **API/configuration ingestion:** use JSON and simple key-value parsing for appropriate formats.
- **Data quality:** validate batches with `fullmatch()` and route invalid records separately.
- **Know when not to use regex:** parse genuine CSV/JSON with standard libraries and nested structures with a real parser.

### Refactoring workshop — all ten decisions

1. `re.search(r"^ERROR", line)` → `line.startswith("ERROR")`: fixed prefix.
2. `re.split(r",", line)` → `line.split(",")`: fixed delimiter.
3. `line.split(" ")` for variable spaces → `re.split(r"\s+", line.strip())` (or no-argument `.split()` if only whitespace tokenization is needed).
4. CSV `.split(",")` → `next(csv.reader([line]))`: respect quoting.
5. Regex to extract JSON field → `json.loads(json_text)["name"]`: respect escaping and nesting.
6. Greedy `r"\[.*\]"` → `re.findall(r"\[.*?\]", text)`: stop at each nearest closing bracket for this simple example.
7. `re.search(r"\d{5}", text)` for ZIP validation → `re.fullmatch(r"\d{5}", text)`: reject extra text.
8. Keep a legitimate complex timestamp regex but reformat it with `re.VERBOSE` and comments.
9. Compile a repeatedly used regex outside a large loop.
10. Replace dangerous `(a+)+b` with equivalent intended pattern `a+b`, avoiding nested quantifiers.

---

# Part B — Your current level and project-tree fit

The supplied project tree places this file at **Stage 1 → Module 04 → Lesson 07**, immediately after the recursion lesson. The relevant prior learning includes computational thinking, Python variables and types, strings/lists/tuples/dictionaries/sets, conditionals, loops, functions, defaults, errors, collection processing, grouping, Big-O, data-structure selection, comprehensions, and recursion.

**Current level: beginner progressing toward intermediate.** You have already encountered the key building blocks used here: strings, slicing, loops, functions, dictionaries, lists, `enumerate`, comprehensions, `Counter`, `defaultdict`, recursion, and Big-O. This lesson adds parsing strategy, standard-library CSV/JSON parsing, and regex. The project tree shows later modules for file I/O, testing, packages, OOP, and advanced Python; those are not prerequisites for these exercises.

The supplied tree also contains practical projects such as a data-quality pipeline and a rule-based risk-review engine. The current lesson directly supports their future needs: turning raw text into records, validating formats, preserving malformed inputs, and summarizing logs.

**Scope discipline:** solutions below use the current lesson and earlier concepts. They do not require pandas, SQL, Spark, classes, or later testing frameworks. Standard-library `csv`, `json`, `re`, and `collections` are used because they are explicitly taught in this lesson.

---

# Part C — All 20 progressive exercises (under 2,000 words)

Each solution includes the tool choice and the important line-by-line logic.

## Level 1 — Beginner

### 1. Split the fruit list

```python
fruits = "apple,banana,cherry".split(",")
print(fruits)
```

`split(",")` is correct because the delimiter is one fixed comma. It returns `['apple', 'banana', 'cherry']`.

### 2. Trim whitespace

```python
cleaned = "  hello world  ".strip()
print(cleaned)
```

`strip()` removes whitespace from both ends; it does not remove the space between the words.

### 3. Parse `key=value`

```python
key, separator, value = "key=value".partition("=")
print(key, value)
```

`partition()` returns three values. The middle variable receives `"="`; the key is `"key"` and the value is `"value"`.

### 4. Check a file suffix

```python
print("report.csv".endswith(".csv"))
```

`endswith()` is the direct fixed-suffix check. Regex is unnecessary. Output: `True`.

### 5. Validate date shape

```python
import re
print(re.fullmatch(r"\d{4}-\d{2}-\d{2}", "2026-01-15") is not None)
```

`\d{4}` means four digits; hyphen is literal; `\d{2}` means two digits. `fullmatch()` requires the entire string to follow the pattern. This checks shape, not calendar validity (e.g. it does not prove the month/day exists).

## Level 2 — Intermediate

### 6. Parse comma-separated records

```python
def parse_records(lines):
    records = []
    for line in lines:
        name, age, country = line.split(",")
        records.append({"name": name, "age": int(age), "country": country})
    return records
```

Create an output list. Split each line into three fields. Convert age from string to integer. Build a dictionary and append it. Return all records. Assumes each line has exactly three valid fields.

### 7. Extract all email-shaped strings

```python
import re
text = "Contact: john@example.com or ada@example.org"
emails = re.findall(r"\w+@\w+\.\w+", text)
print(emails)
```

`findall()` returns every non-overlapping match. `\w+` matches word characters, `@` and escaped `\.` are literal separators. This is a simple illustrative email pattern, not a complete email-spec validator.

### 8. Extract price as a float

```python
match = re.search(r"\$(\d+\.\d+)", "price: $45.00")
amount = float(match.group(1))
print(amount)
```

`\$` matches a literal dollar sign. Parentheses capture the numeric part. `group(1)` retrieves it; `float()` converts `"45.00"` into `45.0`. Assumes a match exists.

### 9. Split commas with inconsistent spaces

```python
fields = re.split(r"\s*,\s*", "John,  25 ,India")
print(fields)
```

The pattern means optional whitespace around a comma. `re.split()` is appropriate because the delimiter varies by surrounding spaces. Output: `['John', '25', 'India']`.

### 10. Convert camelCase to snake_case

```python
def to_snake_case(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

print(to_snake_case("myVariableNameHere"))
```

The lookbehind excludes the start of the string; the lookahead finds a position before each capital letter. `re.sub()` inserts underscores at those positions; `lower()` converts the result. Output: `my_variable_name_here`.

## Level 3 — Advanced

### 11. Parse a log line with named groups

```python
pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+): (?P<message>.+)"
)
match = pattern.fullmatch("2026-01-15 10:00:00 ERROR: disk full")
record = match.groupdict()
print(record)
```

Compile the pattern once. Each `(?P<name>...)` captures a named field. `fullmatch()` checks the whole line; `groupdict()` returns a dictionary.

### 12. Parse quoted CSV correctly

```python
import csv
import io

rows = list(csv.reader(io.StringIO('John,"Smith, Jr.",25')))
print(rows)
```

`StringIO` presents the string as a file-like object. `csv.reader()` understands that the comma inside quotes belongs to the surname. `.split(",")` would incorrectly create four pieces.

### 13. Parse JSON and recursively flatten nested dictionaries

```python
import json

def flatten(data, path=""):
    result = {}
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            result.update(flatten(value, new_path))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            result.update(flatten(value, f"{path}[{index}]"))
    else:
        result[path] = data
    return result

config = json.loads('{"service":{"limits":{"retries":3}}}')
print(flatten(config))
```

`json.loads()` creates Python structures. For dictionaries, recurse into each value with a dotted path. For lists, recurse with an indexed path. A leaf is stored in the result. Output: `{'service.limits.retries': 3}`.

### 14. Redact card-shaped numbers

```python
def redact(text):
    return re.sub(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b", "[REDACTED]", text)
```

The pattern recognizes four groups of four digits separated by hyphens. `sub()` replaces every match. This is only the specified shape, not every possible card-number format.

### 15. Explain and fix catastrophic backtracking

`(a+)+b` has nested quantifiers. The engine can divide a long run of `a` characters into many possible groups; when the final `b` is missing, it may retry many combinations before failing. The intended meaning is simply one or more `a` characters followed by `b`.

```python
safe_pattern = r"a+b"
```

Removing the redundant outer group avoids the dangerous nested-quantifier structure.

## Level 4 — Production-oriented

### 16. Count ERROR messages using a compiled named-group pattern

```python
from collections import Counter
import re

pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+): (?P<message>.+)"
)

def error_message_counts(text):
    errors = []
    for line in text.splitlines():
        match = pattern.fullmatch(line)
        if match:
            record = match.groupdict()
            if record["level"] == "ERROR":
                errors.append(record)
    return Counter(record["message"] for record in errors)
```

Compile once outside the loop. Split the text into lines, parse only full matches, convert matches into dictionaries, retain only `ERROR`, then count messages with `Counter`.

### 17. Normalize phone numbers

```python
def normalize_phone(number):
    return re.sub(r"[^0-9]", "", number)
```

`[^0-9]` matches every character that is not an ASCII digit; `sub()` removes them. A single regex is clearer than many `.replace()` calls when several punctuation/spacing variants are possible. This normalizes characters only; it does not validate country code or phone-number length.

### 18. Validate email format and state the limitation

```python
def is_valid_email_format(email):
    return re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", email) is not None

# This checks a simplified format only; it does not prove the mailbox exists
# or can receive messages. Use a confirmation email to verify deliverability.
```

`fullmatch()` rejects extra text before or after the address. The pattern is intentionally approximate; real email syntax is more complex.

### 19. Separate valid and invalid CSV rows with line numbers

```python
import csv
import io

def separate_rows(text, expected_fields=3):
    valid, invalid = [], []
    for line_number, row in enumerate(csv.reader(io.StringIO(text)), start=1):
        if len(row) == expected_fields:
            valid.append(row)
        else:
            invalid.append((line_number, row))
    return valid, invalid
```

`csv.reader()` respects quoted commas. `enumerate(..., start=1)` attaches a one-based record number. The field-count rule separates rows. This simple solution assumes one physical input line per CSV record; CSV fields that contain embedded newlines require tracking reader line numbers more carefully.

### 20. Design and implement support-ticket parsing

Assumption: each non-empty line follows `TICKET-<digits> [<priority>] <description>`.

```python
import re

TICKET_PATTERN = re.compile(
    r"TICKET-(?P<ticket_id>\d+) "
    r"\[(?P<priority>\w+)\] "
    r"(?P<description>.+)"
)

def parse_tickets(text):
    tickets, invalid = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = TICKET_PATTERN.fullmatch(line)
        if match:
            tickets.append(match.groupdict())
        else:
            invalid.append(line)
    return tickets, invalid
```

Split lines using a simple string method because line boundaries are fixed. Use a compiled named-group regex for the variable ticket ID, priority, and free-text description. `fullmatch()` validates the complete line. Keep unmatched lines separately rather than silently losing them.

---

# Part D — Mini-project: Log Parsing and Alerting Pipeline

## 1. Problem definition

Convert raw multi-line server logs into structured records and an actionable report. The pipeline must preserve malformed lines, identify serious events, extract transaction IDs, group events, and count severities.

**Input:** one multi-line string.  
**Output:** unparseable lines, severity counts, serious records, records grouped by transaction ID, and total serious records.

**Assumptions and edge cases**
- Expected format: `YYYY-MM-DD HH:MM:SS LEVEL: message`.
- Some lines may be malformed; collect them instead of crashing.
- A serious message may not contain a transaction ID; use `"none"`.
- If multiple transaction IDs occur, use the first match.
- Matching is case-sensitive: lowercase `error` is parsed as a level but is not treated as `ERROR`.
- Empty lines are skipped; empty input returns empty collections and zero counts.

## 2. Complete implementation

```python
import re
from collections import defaultdict, Counter

LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+): (?P<message>.+)"
)
TRANSACTION_PATTERN = re.compile(r"(?P<transaction_id>T\d+)")


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
    serious = [
        record for record in parsed
        if record["level"] in ("ERROR", "CRITICAL")
    ]

    errors_by_transaction = defaultdict(list)
    for record in serious:
        match = TRANSACTION_PATTERN.search(record["message"])
        key = match.group("transaction_id") if match else "none"
        errors_by_transaction[key].append(record)

    return {
        "unparseable_lines": unparseable,
        "severity_counts": dict(severity_counts),
        "serious_records": serious,
        "errors_by_transaction": dict(errors_by_transaction),
        "total_serious": len(serious),
    }


log_text = """
2026-01-15 10:00:00 INFO: server started
2026-01-15 10:05:23 ERROR: payment failed for T12345
2026-01-15 10:05:24 ERROR: retry failed for T12345
this line does not match the expected format at all
2026-01-15 10:06:01 CRITICAL: database unreachable
"""

report = build_report(log_text)
print(report["severity_counts"])
print(report["errors_by_transaction"].keys())
print(report["unparseable_lines"])
```

Expected key results:

```text
{'INFO': 1, 'ERROR': 2, 'CRITICAL': 1}
dict_keys(['T12345', 'none'])
['this line does not match the expected format at all']
```

## 3. Code walkthrough

1. Import `re` for pattern matching, `Counter` for frequency counts, and `defaultdict` for automatic list groups.
2. `LOG_PATTERN` is compiled once. Named groups capture date, time, level, and message.
3. `TRANSACTION_PATTERN` captures a transaction ID beginning with `T` followed by digits.
4. `parse_log_text()` creates two lists: successful records and malformed lines.
5. `splitlines()` separates input. `strip()` cleans each line; empty lines are skipped.
6. `fullmatch()` requires the entire line to follow the log structure. Successful matches become dictionaries through `groupdict()`; failures are preserved.
7. `build_report()` counts every parsed severity with `Counter`.
8. A list comprehension keeps only exact `ERROR` and `CRITICAL` levels.
9. For each serious record, `search()` finds the first transaction ID in its message.
10. The key is the captured ID or `"none"`. `defaultdict(list)` groups records under that key.
11. The final dictionary combines malformed lines, counts, serious records, groups, and total serious count.

## 4. Complexity

Let `N` be total input characters and `r` the number of parsed records. Splitting and matching with these simple, non-nested patterns takes O(N) under the intended input assumptions. Counting, filtering, and grouping take O(r). Since `r` is bounded by the number of input lines, the overall pipeline is O(N) in this model. The implementation makes several linear passes; the regexes are compiled once and reused.

---

# Part E — Review checklist and interview revision

## Review checklist

- [ ] Explain raw, semi-structured, and structured data.
- [ ] Distinguish manipulation, parsing, and validation.
- [ ] Choose correctly among `split`, `partition`, `splitlines`, `join`, `strip`, `find`, `startswith`, and `replace`.
- [ ] Explain why `csv` and `json` should parse their own formats.
- [ ] Read and construct basic regex patterns incrementally.
- [ ] Distinguish `search`, `match`, and `fullmatch`.
- [ ] Use character classes, quantifiers, anchors, groups, alternation, and escaping.
- [ ] Use raw strings and named groups.
- [ ] Explain `findall` versus `finditer`, `sub` versus `subn`, and compiled patterns.
- [ ] Explain greedy matching, lookarounds, flags, and `re.VERBOSE`.
- [ ] Recognize catastrophic backtracking and ReDoS risk.
- [ ] Combine parsing with filtering, grouping, and counting.

## Interview questions to practise

**Foundational:** What is parsing? How does it differ from string manipulation? `split()` versus `partition()`? Why use `csv` and `json` modules? What is regex?

**Intermediate:** `search()` versus `match()` versus `fullmatch()`? Capturing versus non-capturing groups? `*` versus `+`? Why raw strings? How does `findall()` change when captures exist? Greedy versus non-greedy matching?

**Advanced:** What is catastrophic backtracking/ReDoS? Why can regex not parse arbitrary nested JSON? Lookahead versus capturing group? When compile a pattern, and what does that optimize? How do you choose between string methods, standard parsers, and regex?

**Scenarios:** How would you parse large logs? Why does regex-based CSV parsing corrupt fields? How would you validate one of several phone formats? What might make regex validation suddenly take seconds on unusual inputs?

---

## Final engineering principle

**Choose the simplest tool that correctly matches the input's structure:**

- Fixed structure → string methods.
- Standard CSV/JSON → `csv` / `json`.
- Variable pattern inside otherwise simple text → regex.
- Deeply nested or recursively structured content → a real parser or recursive traversal.

Regex is a pattern-matching tool, not a replacement for parsers, and not something to apply to untrusted input without considering performance and security.
