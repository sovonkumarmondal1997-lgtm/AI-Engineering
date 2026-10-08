# JSON and Serialization

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what JSON is, why it exists, and why it became the dominant
  data-interchange format.
- Explain JSON's data model — objects, arrays, strings, numbers,
  booleans, and null — and JSON's syntax rules precisely.
- Explain, precisely, the difference between a JSON *text* and a Python
  *object*, and why a Python dictionary is not the same thing as JSON.
- Explain serialization and deserialization, and use `json.dumps()`,
  `json.loads()`, `json.dump()`, and `json.load()` correctly, including
  their important parameters.
- Map every JSON value type to its corresponding Python type, and
  explain which Python types JSON cannot directly represent.
- Serialize custom Python types (`datetime`, `Decimal`, `Path`, `Enum`,
  dataclasses) deliberately, using `default=` and a custom
  `JSONEncoder`.
- Use `object_hook`, `object_pairs_hook`, `parse_int`, `parse_float`,
  and `parse_constant` to control deserialization.
- Control formatting and determinism with `indent`, `separators`, and
  `sort_keys`.
- Handle `json.JSONDecodeError` deliberately, and distinguish syntax
  validity from application-level schema validity.
- Recognize JSON-specific security considerations, including why
  `eval()` must never be used to parse JSON.
- Process JSON data too large to comfortably load at once, including
  JSON Lines (NDJSON).
- Write reusable, type-hinted JSON utility functions, and test them
  with `pytest`.
- Debug JSON failures systematically.
- Recognize JSON's central role in APIs, configuration, and modern
  AI/ML and LLM-application engineering — including why AI-generated
  JSON still requires validation.
- Design a production-oriented JSON ingestion/serialization workflow.

## 2. Why JSON Matters

This chapter follows
[03-csv-files.md](03-csv-files.md), which taught you how to work with
*flat*, tabular text data. JSON is where this module's data-interchange
skills extend to **nested, typed structured data** — the format
underneath nearly every API request and response, most modern
configuration files, and an enormous share of the metadata, artifacts,
and messages exchanged inside real backend, data, and AI/ML systems.

Where CSV's central lesson was "this looks simple, but hides real
parsing complexity," JSON's central lesson is different: **JSON looks
almost exactly like a Python dictionary, and that resemblance is
exactly what makes it easy to get subtly wrong.** `True` is not `true`;
`None` is not `null`; a Python `dict` is not, itself, JSON — it merely
*converts to* JSON. This chapter spends real, deliberate effort making
that distinction precise, because every other concept in this chapter —
type mapping, custom serialization, validation, security — depends on
holding it clearly in mind.

Exactly as with every other file in this module, this chapter continues
the same boundary-validation discipline:
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§3 established that files, CLI arguments, environment variables, and
JSON are all **untrusted input** — this chapter is where that principle
gets its fullest treatment, because JSON's flexibility (arbitrary
nesting, arbitrary structure) makes "syntactically valid but
semantically wrong" a genuinely common, genuinely dangerous failure
mode — one that matters especially once JSON is something an AI model,
not just a human or another well-behaved system, is producing (§35,
§46).

This chapter assumes the file-I/O foundations from
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)
and the path-handling foundations from
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md) —
it builds on both without repeating them.

## 3. JSON Fundamentals

### 3.1 Data, structured data, and interchange formats

**Data** is simply information a program works with. **Structured
data** is data organized according to a consistent, predictable shape
— [03-csv-files.md](03-csv-files.md)'s §3.1 already introduced this for
*flat*, tabular data; JSON extends the same idea to data that can be
**nested** — values containing other values, to arbitrary depth. A
**data interchange format** is a format specifically designed so that
*different* programs, often written in different languages, running on
different machines, can reliably exchange structured data with each
other.

### 3.2 What JSON is, and what it stands for

**JSON** stands for **JavaScript Object Notation** — its syntax
originated from how objects are written in the JavaScript programming
language. Despite the name, JSON today is a **language-independent**
format: nearly every programming language, including Python, provides
tools to read and write it, with no dependency on JavaScript itself.

### 3.3 Why JSON was created, and why it is so widely used

JSON was created to be a **simple, lightweight, human-readable**
alternative to earlier, more verbose data-interchange formats — text
you can read directly, with a small, precisely defined set of rules
(§5), that both humans and machines can parse unambiguously. Its
continued dominance today rests on the same qualities CSV's §3.3
described for tabular data, extended to nested data: it requires no
special tooling to read or write, it maps naturally onto data
structures every mainstream language already has (§14), and it is
supported, essentially universally, by web APIs, configuration systems,
databases, and countless other tools.

### 3.4 Where JSON is used today

Web APIs (request and response bodies, §33); configuration files (§32);
application and service logs; inter-service messages in distributed
systems; machine-learning experiment metadata and evaluation results
(§34); and, increasingly, **structured output from AI models
themselves** (§35) — a program asking a large language model to return
"an answer as JSON" is relying on exactly the format this chapter
teaches.

### 3.5 A first complete example

```json
{
    "name": "Alice",
    "age": 30,
    "active": true
}
```

- `{` and `}` mark the boundaries of a JSON **object** — an unordered
  collection of key-value pairs (§4 develops this fully).
- `"name"`, `"age"`, `"active"` are **keys** — always written as
  double-quoted text in JSON (§5.1).
- `"Alice"` is a JSON **string** value.
- `30` is a JSON **number** value.
- `true` is a JSON **boolean** value — written in lowercase (§5.3);
  this is the single most common early trip-up for a Python learner,
  developed fully in §6.

## 4. JSON Data Model

### 4.1 The six fundamental value types

Every value in JSON, no matter how deeply nested, is one of exactly six
kinds:

| Type | Plain-English meaning | Example |
|---|---|---|
| **object** | An unordered collection of named values | `{"name": "Alice"}` |
| **array** | An ordered collection of values | `["Python", "SQL", "Linux"]` |
| **string** | Text, always double-quoted | `"Alice"` |
| **number** | An integer or a decimal number | `42`, `3.14` |
| **boolean** | True or false | `true`, `false` |
| **null** | The deliberate absence of a value | `null` |

### 4.2 Objects, deeply

```json
{
    "customer": {
        "id": 1001,
        "name": "Alice"
    }
}
```

A JSON **object** is a set of **key-value pairs**, where each **key**
is always a string, and each **value** can be *any* of the six types —
including another object (as shown: `customer`'s value is itself a full
object) or an array. Real-world JSON documents assume, by convention,
that keys within a single object are **unique** — the JSON
specification itself does not strictly forbid duplicate keys, but a
well-formed document should never rely on them, and most parsers
(including Python's, §13) silently keep only the *last* occurrence if
duplicates do appear, exactly mirroring
[03-csv-files.md](03-csv-files.md)'s §34.1 duplicate-header lesson.
**JSON keys must always be strings** — there is no JSON equivalent of a
Python dictionary with an integer or tuple key.

### 4.3 Arrays, deeply

```json
[1, 2, 3]
```

```json
[
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]
```

A JSON **array** is an **ordered** collection of values, written inside
`[` and `]`, separated by commas. Arrays can hold any mix of the six
types, including further nested arrays or objects — the second example
above is an array of objects, a shape you will encounter constantly
(a list of records, exactly mirroring a CSV file's rows, but nested and
typed rather than flat text). Once converted into Python (§9 onward), a
JSON array becomes an ordinary Python `list`, with the exact same
zero-based indexing you already know.

### 4.4 Combining types into nested structures

```json
{
    "customer": {
        "id": 1001,
        "orders": [
            {"id": 5001, "amount": 100.5},
            {"id": 5002, "amount": 42.0}
        ]
    }
}
```

Because an object's values and an array's elements can themselves be
objects or arrays, JSON structures can nest to arbitrary depth —
exactly the property that lets JSON represent data CSV's flat,
row-and-column shape fundamentally cannot (§21's type-mapping table,
and the CSV chapter's own §38.2, both return to this).

## 5. JSON Syntax

### 5.1 The precise rules

- **Strings use double quotes only** — `"Alice"` is valid; `'Alice'` is
  **not** valid standard JSON.
- **Object keys are always double-quoted strings** — `{"name": "Alice"}`,
  never `{name: "Alice"}`.
- **A colon (`:`) separates a key from its value**, inside an object.
- **A comma (`,`) separates items** — key-value pairs within an object,
  or elements within an array.
- **No trailing commas** — `["a", "b",]` is invalid; the comma after
  the final element is not allowed in standard JSON.
- **`true`, `false`, and `null` are written in lowercase, unquoted** —
  `True`, `False`, `None`, `TRUE`, or `Null` are all invalid JSON.
- **Numbers are written without quotes**, and without leading zeros
  (except a bare `0` itself) — `42`, `3.14`, `-7`, `1.5e10` are all
  valid; `042` is not. Standard JSON numbers also do not permit a
  leading `+` (`+1`), a missing integer part (`.5`), or a trailing
  decimal point (`1.`); an exponent is `e` or `E`, an optional sign,
  and digits (`1e5`, `2.5E-3`).
- **Strings may contain only these escape forms:** `\"`, `\\`, `\/`,
  `\b`, `\f`, `\n`, `\r`, `\t`, and `\uXXXX`. Control characters
  (code points below U+0020, such as a literal newline or tab) are not
  permitted unescaped inside a JSON string.
- **Objects use `{` `}`; arrays use `[` `]`** — these are not
  interchangeable.

### 5.2 An invalid example, and precisely why

```json
{
    'name': 'Alice'
}
```

This is **invalid standard JSON** — single quotes are not permitted
anywhere in JSON syntax, for either keys or string values. It happens
to look extremely close to valid **Python dictionary literal syntax**
(where single quotes are perfectly normal) — this resemblance is
precisely why §6 exists as its own, deliberately thorough section: the
two syntaxes are close enough to be confused, and different enough that
confusing them produces real, hard-to-spot bugs.

### 5.3 A second invalid example

```json
{
    "active": True,
    "items": ["a", "b",]
}
```

Two separate problems: `True` (capitalized, Python style) is not valid
JSON — it must be lowercase `true`; and the trailing comma after
`"b"` is not permitted.

## 6. JSON vs. Python Objects

### 6.1 Side by side — the critical comparison

```python
# Python dictionary literal
data = {
    "name": "Alice",
    "active": True,
    "value": None,
}
```

```json
// The equivalent JSON text
{
    "name": "Alice",
    "active": true,
    "value": null
}
```

| | Python | JSON |
|---|---|---|
| Boolean true | `True` (capitalized) | `true` (lowercase) |
| Boolean false | `False` (capitalized) | `false` (lowercase) |
| Absent/null value | `None` | `null` |
| String quoting | Single **or** double quotes | Double quotes **only** |
| Trailing comma | Allowed | **Not** allowed |
| Comments | Not part of the syntax either way | Not part of the syntax either way |

### 6.2 What Python has that JSON does not

**Tuples** — a Python `tuple` has no JSON equivalent; when serialized,
it becomes an ordinary JSON array, and comes back from deserialization
as a `list`, **not** a `tuple` (§63.2 makes this a concrete round-trip
example). **Sets** — a Python `set` has no JSON equivalent at all, and
attempting to serialize one raises an error outright (§22.1
demonstrates this). **Arbitrary objects** — a custom class instance has
no built-in JSON representation; §18–§19 build exactly the mechanism
needed to handle this deliberately. **Dictionary keys of any hashable
type** — Python dictionaries can use integers, tuples, or other
hashable values as keys; JSON object keys must always be strings (§4.2)
— §37 covers what happens when this collides.

### 6.3 Integer vs. float

Python distinguishes `int` and `float` as genuinely different types.
JSON's single "number" type does not make this distinction
syntactically the same way — but Python's `json` module *does*
faithfully preserve the distinction on conversion: `42` (no decimal
point) becomes Python `int`; `42.0` or `4.2e1` (a decimal point or
exponent present) becomes Python `float` — §21 covers this mapping
precisely.

### 6.4 The standing rule this entire chapter is built on

**A JSON *text* (a string, or the contents of a `.json` file) and a
Python *object* (a `dict`, a `list`, and so on) are two genuinely
different things.** Converting between them is not automatic, and not
free — it is a deliberate operation, with a name: **serialization**
(Python → JSON) and **deserialization** (JSON → Python), exactly what
§7 and §8 build out fully. `json.dumps(data)` where `data` is *already*
a Python `dict`, and `json.loads(text)` where `text` is *already* a
JSON string, are the correct directions — reversing them (§64) is one
of the most common beginner mistakes this chapter addresses directly.

## 7. Serialization and Deserialization

### 7.1 The two directions, as a diagram

```
Python dict  →  json.dumps()  →  JSON string   (serialization)
JSON string  →  json.loads()  →  Python dict    (deserialization)
```

```python
import json

data = {"name": "Alice", "age": 30}
text = json.dumps(data)
print(text)
print(type(text))
```

```text
{"name": "Alice", "age": 30}
<class 'str'>
```

`json.dumps(data)` — Python `dict` **in**, JSON-formatted `str` **out**
— nothing was written to a file; `text` is simply an ordinary Python
string that happens to *contain* valid JSON syntax.

```python
recovered = json.loads(text)
print(recovered)
print(type(recovered))
```

```text
{'name': 'Alice', 'age': 30}
<class 'dict'>
```

`json.loads(text)` reverses the process — a JSON-formatted `str` in,
an ordinary Python `dict` out.

### 7.2 What "serialization" means, from first principles

An **object**, in the general sense, is some structured piece of data
your program is working with — held in memory, as Python objects, in a
shape only meaningful *within* a running Python process. A
**representation** is some other form that same information can take —
text, in JSON's case. **Serialization** is the process of converting an
in-memory object into a representation that can be **stored** (written
to a file or a database) or **transferred** (sent over a network,
between processes, between programs written in entirely different
languages) — because raw, in-memory Python objects cannot themselves be
written to disk or sent across a network; only their *representation*
can. **Deserialization** is the reverse: reconstructing a usable
in-memory object from that stored or transferred representation.

### 7.3 The full round trip, in context

```
Python object → serialize (json.dumps/json.dump) → JSON text → file / network
file / network → JSON text → deserialize (json.loads/json.load) → Python object
```

### 7.4 Where serialization appears in real systems

**APIs** — a request body sent to a server, and the response body sent
back, are both typically JSON text, serialized on one end and
deserialized on the other (§33). **Databases** — many modern databases
store and query JSON-shaped columns directly. **Caches** — a value
computed once and cached (in memory, or in a caching service) is often
serialized to JSON first, since a cache frequently stores things as
text or bytes, not live Python objects. **Configuration** — an
application's settings, read once at startup (§32). **Distributed
systems** — separate processes, potentially on separate machines,
exchanging structured messages need a shared, unambiguous
representation — JSON is an extremely common choice. **Message queues**
— messages passed between producers and consumers are frequently JSON.
**ML metadata and AI applications** — §34 and §35 develop this fully.

## 8. Python `json` Module

### 8.1 `import json`

```python
import json
```

### 8.2 The module's major public APIs, at a glance

```
json.dumps() / json.loads()    -- convert to/from a Python str
json.dump()  / json.load()      -- convert to/from an open file object
json.JSONEncoder                  -- the class doing the actual serialization work
json.JSONDecoder                   -- the class doing the actual deserialization work
json.JSONDecodeError                -- the exception raised for malformed JSON text
json.detect_encoding()                -- a low-level, rarely-used helper (§8.3)
```

### 8.3 Which of these you will use often, and which are specialized

`json.dumps()`, `json.loads()`, `json.dump()`, and `json.load()` (§9–§16)
are what the overwhelming majority of real code uses directly, every
day. `json.JSONEncoder`/`json.JSONDecoder` (§19–§20) become relevant
the moment you need custom serialization/deserialization behavior
beyond what the four top-level functions' keyword parameters already
provide. `json.JSONDecodeError` (§29.2) is relevant any time you handle
JSON coming from *outside* your program — which, per this chapter's
central "treat it as untrusted input" theme, should be essentially
always. `json.detect_encoding()` is a low-level helper, historically
used internally when decoding raw `bytes` input per the JSON
specification's own encoding-detection rules — you are very unlikely to
call it directly in application code; the recommended, explicit
practice (§16.3) is to decode bytes to `str` yourself, with a known
encoding, before ever handing text to `json`.

## 9. `json.dumps()`

### 9.1 The simplest working example

```python
import json

data = {
    "name": "Alice",
    "age": 30,
}

text = json.dumps(data)
print(text)
```

```text
{"name": "Alice", "age": 30}
```

**Input:** any JSON-serializable Python object — most commonly a
`dict` or `list`, but technically any of §21's mapped types. **Return
value:** a plain Python `str` containing valid JSON text. **No file is
created** — `dumps` (plural "s" for "string") only ever produces a
string value in memory; writing it to disk, if desired, is a separate,
explicit step (§10 shows exactly how to combine the two, and §11
introduces `json.dump()` — no `s` — which does both at once).

## 10. `json.dumps()` Parameters

### 10.1 The full signature

```text
json.dumps(
    obj,
    *,
    skipkeys=False,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=True,
    cls=None,
    indent=None,
    separators=None,
    default=None,
    sort_keys=False,
    **kw,
)
```

### 10.2 Each parameter, explained

**`obj`** — the Python object to serialize. Example:
`json.dumps({"a": 1})`.

**`skipkeys`** — what to do about a dictionary key that is not a valid
JSON key type (§21, §37). Default `False` raises `TypeError`;
`skipkeys=True` silently omits such keys instead. Production
implication: silently dropping data is dangerous — §37 develops this
fully.

**`ensure_ascii`** — whether non-ASCII characters are escaped as
`\uXXXX` sequences (`True`, the default) or written directly as their
real characters (`False`). Example: `json.dumps({"city": "Kolkata"},
ensure_ascii=False)`. §27 covers this fully.

**`check_circular`** — whether the encoder actively checks for circular
references (an object that, directly or indirectly, contains itself)
before they cause a crash. Default `True`. §38 develops this fully.

**`allow_nan`** — whether Python's non-standard `NaN`/`Infinity`/
`-Infinity` float values are permitted to be serialized at all
(`True`, the default) or raise `ValueError` instead (`False`). §26
develops this fully.

**`cls`** — a custom `JSONEncoder` subclass to use instead of the
default encoder. Example: `json.dumps(data, cls=MyEncoder)`. §19
develops this fully.

**`indent`** — how much (and whether) to pretty-print the output, with
line breaks and indentation. Default `None` (compact, single line).
§28 develops this fully.

**`separators`** — the exact item/key-value separator strings used.
Default depends on whether `indent` is set (§28.3). §28 develops this
fully.

**`default`** — a function called for any object the encoder does not
already know how to serialize, expected to return something
serializable instead. Example: `json.dumps(obj, default=str)`. §18
develops this fully, including why `default=str` specifically is a
convenient but potentially dangerous shortcut.

**`sort_keys`** — whether object keys are sorted alphabetically in the
output (`True`) or kept in their original insertion order (`False`,
the default). §28 develops this fully.

## 11. `json.loads()`

### 11.1 The simplest working example

```python
import json

text = '{"name": "Alice", "age": 30}'
data = json.loads(text)

print(data)
print(type(data))
```

```text
{'name': 'Alice', 'age': 30}
<class 'dict'>
```

**Input:** a `str` (or `bytes`/`bytearray`, though
passing already-decoded `str` explicitly is the recommended, explicit
practice, §16.3) that must contain JSON text the decoder accepts.
**Output:** the corresponding Python object — a `dict` for a JSON
object, a `list` for a JSON array, and so on down to the appropriate
Python primitive for every nested value, all the way through arbitrary
nesting depth, strings, lists, dictionaries, numbers, booleans, and
`null` (→ `None`) alike.

## 12. `json.loads()` Parameters

### 12.1 The full signature

```text
json.loads(
    s,
    *,
    cls=None,
    object_hook=None,
    parse_float=None,
    parse_int=None,
    parse_constant=None,
    object_pairs_hook=None,
    **kw,
)
```

### 12.2 Each parameter, briefly (each gets its own full section ahead)

**`s`** — the JSON text to parse.

**`cls`** — a custom `JSONDecoder` subclass to use instead of the
default decoder (§20).

**`object_hook`** — a function called with every decoded JSON *object*
(as a plain `dict`), letting you transform it into something else
during decoding (§21).

**`object_pairs_hook`** — like `object_hook`, but receives the raw
ordered list of key-value pairs, before they are collapsed into a
`dict` (§22).

**`parse_float`** — a function used to convert JSON number text
containing a decimal point or exponent, instead of the default `float`
(§24).

**`parse_int`** — a function used to convert JSON integer-looking
number text, instead of the default `int` (§23).

**`parse_constant`** — a function used to handle the special,
non-standard tokens `NaN`, `Infinity`, and `-Infinity` (§25).

### 12.3 A first small example, previewing several at once

```python
text = '{"count": 3, "ratio": 0.5}'

data = json.loads(text, parse_int=str, parse_float=str)
print(data)
```

```text
{'count': '3', 'ratio': '0.5'}
```

Both numeric values became plain strings instead of `int`/`float` —
demonstrating that these hooks genuinely intercept and override the
decoder's normal, default behavior, rather than merely validating it.

## 13. `json.dump()`

### 13.1 The simplest working example

```python
import json

data = {"name": "Alice", "age": 30}

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
```

```text
{
  "name": "Alice",
  "age": 30
}
```

`json.dump()` (no trailing `s`) writes directly to an **already-open
file object**, rather than returning a string — a combination of what
`json.dumps()` would produce, immediately written out via the file
object's own `write()` calls, without ever building the entire JSON
string as a separate, standalone Python value first. `indent=2` (§28)
makes the output human-readable — omitted, the output would be one
compact line, exactly as `json.dumps()`'s own default.

### 13.2 Encoding and newline considerations

Exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§25 lesson applies unchanged: always open a JSON file with explicit
`encoding="utf-8"`. Unlike CSV
([03-csv-files.md](03-csv-files.md)'s §26.2), **`json.dump()` does not
require `newline=""`** — it does not write embedded raw newline
characters the way a CSV field can, and does not rely on a specific
line-terminator convention the way `csv.writer` does; ordinary text-mode
opening is sufficient.

## 14. `json.dump()` Parameters

### 14.1 The same serialization options as `dumps()`, plus a file target

```text
json.dump(
    obj,
    fp,
    *,
    skipkeys=False,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=True,
    cls=None,
    indent=None,
    separators=None,
    default=None,
    sort_keys=False,
    **kw,
)
```

Every parameter from §10.2 (`skipkeys`, `ensure_ascii`,
`check_circular`, `allow_nan`, `cls`, `indent`, `separators`, `default`,
`sort_keys`) means exactly the same thing here — the only addition is
`fp`, the already-open, writable file object the output is streamed
into.

### 14.2 Stream-specific behavior

**Warning:** JSON is not a framed record format. Repeatedly calling
`json.dump()` against the same file stream to append multiple
independent JSON values does not produce one valid JSON document. Use
one enclosing JSON structure or a record-oriented format such as JSON
Lines (§41) when you need multiple independently processed records.

`json.dump()` writes incrementally to `fp` as it serializes, rather
than necessarily building the complete JSON string in memory first and
writing it all at once (the exact internal mechanics depend on the
Python version and encoder implementation) — practically, this means
`json.dump(obj, f)` and `f.write(json.dumps(obj))` produce **identical
file contents**, but `json.dump()` is the more direct, idiomatic way to
express "serialize this, straight into this file."

## 15. `json.load()`

### 15.1 The simplest working example

```python
import json

with open("config.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data)
```

```text
{'name': 'Alice', 'age': 30}
```

`json.load()` (no trailing `s`) reads and parses directly from an
already-open file object — reading the entire file's text and parsing
it, in one call, without you needing a separate `f.read()` step first.

### 15.2 File encoding and error handling, previewed

Exactly as with `json.dump()`, always open with explicit
`encoding="utf-8"`. If the file's content is not valid JSON,
`json.load()` raises `json.JSONDecodeError` (§29) — exactly the same
exception `json.loads()` raises for malformed text, since `json.load()`
is, internally, essentially "read the file's full text, then parse it
exactly as `json.loads()` would."

## 16. `load` vs. `loads` / `dump` vs. `dumps`

### 16.1 The comparison table

| | Reads from / writes to | Input/output type |
|---|---|---|
| `json.loads(s)` | A `str` already in memory | Returns a Python object |
| `json.load(fp)` | An already-open file object | Returns a Python object |
| `json.dumps(obj)` | — | Returns a `str` |
| `json.dump(obj, fp)` | An already-open file object | Writes directly; returns `None` |

### 16.2 The naming convention, made explicit

**The trailing `s` means "string."** `loads` = "load from a **s**tring";
`dumps` = "dump to a **s**tring." The versions *without* the trailing
`s` work with an already-open file object instead. This single
mnemonic resolves the single most common beginner confusion in this
entire chapter (§64 returns to it directly): reaching for `json.load()`
when you actually have a string in hand (not a file object), or
`json.loads()` when you actually have a file object in hand (not a
string), each raises a `TypeError` or otherwise fails, because the
function received a value of the wrong shape for what it expects.

### 16.3 A brief note on bytes input

`json.loads()` accepts a `str`, `bytes`, or `bytearray` containing JSON
data (for bytes input it uses `json.detect_encoding()` internally to
guess the text encoding per the JSON specification's own rules).
`json.load()` accepts an already-open file object, which may be a
binary file object. The
clearer, more explicit, and recommended practice — consistent with
every principle
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§25 already established — is to **decode bytes to `str` yourself, with
a known, explicit encoding, before handing text to `json`** (or simply
open text files with `encoding="utf-8"` in the first place, as every
example in this chapter does), rather than relying on automatic
encoding detection.

## 17. JSON Type Mapping

### 17.1 The full JSON ↔ Python conversion table

| JSON | Python (on decode) | Python (on encode) |
|---|---|---|
| object | `dict` | any `dict` |
| array | `list` | any `list` or `tuple` |
| string | `str` | any `str` |
| number (no `.`/exponent) | `int` | any `int` |
| number (with `.`/exponent) | `float` | any `float` |
| `true` | `True` | `True` |
| `false` | `False` | `False` |
| `null` | `None` | `None` |

### 17.2 Reading the table correctly

Notice the encode side accepts a **`tuple`** (converted to a JSON
array, indistinguishable on the way back out) even though the decode
side never *produces* one — this is exactly §6.2's "what Python has
that JSON does not" point, made concrete in table form.

Note also that the table describes values; JSON object **keys** are
always strings. On encode, `dict` keys that are `str` are used as-is,
`int`, `float`, `bool`, and `None` keys are converted to strings
(`"1"`, `"2.5"`, `"true"`, `"null"`), and other key types raise
`TypeError` (unless `skipkeys=True`) — so not every Python `dict` maps
directly to JSON, and keys do not round-trip back to their original
types.

### 17.3 Types with no direct mapping at all

`set`, `bytes`, `datetime`/`date`/`time`, `Decimal`, `Path`, `UUID`,
`Enum`, and any custom class instance have **no entry in this table on
the encode side** — attempting to serialize one directly raises
`TypeError`, not because of a bug, but because the `json` module
genuinely has no built-in rule for representing them. §18's entire
purpose is teaching exactly how you supply that missing rule yourself,
deliberately.

## 18. Nested JSON

### 18.1 A realistic configuration-shaped example

```json
{
    "version": 1,
    "application": {
        "name": "myapp"
    },
    "features": [
        "search",
        "logging"
    ]
}
```

Once decoded, this becomes an ordinary nested Python structure: a
`dict` with a `"version"` key mapping to an `int`, an `"application"`
key mapping to *another* `dict`, and a `"features"` key mapping to a
`list` of strings — exactly the same object model you have already
worked with throughout Modules 1.2–1.4, simply arrived at via
`json.load()`/`json.loads()` instead of being typed directly as Python
literals.

### 18.2 Deeper nesting

```json
{
    "customer": {
        "id": 1001,
        "profile": {
            "name": "Alice",
            "address": {
                "city": "Kolkata"
            }
        },
        "orders": [
            {"id": 5001, "amount": 100.5}
        ]
    }
}
```

```python
data = json.loads(text)
city = data["customer"]["profile"]["address"]["city"]
first_order_amount = data["customer"]["orders"][0]["amount"]
```

### 18.3 Why excessive nesting can make data difficult to work with

Every additional level of nesting means one more `[...]` your code
must chain through to reach a value — beyond a certain depth, this
becomes genuinely hard to read, hard to validate completely (§30–§31),
and fragile against structural change (a level being added, removed, or
renamed somewhere in the middle breaks every access chain that passes
through it). Deeply nested JSON is a real, common source of
maintenance difficulty in production systems — a fact worth
anticipating, not discovering the hard way; §31's schema-validation
habits and, in more advanced designs, converting deeply nested JSON
into flatter, purpose-built domain objects (§43) are both direct
responses to this problem.

## 19. Safe JSON Access

### 19.1 Direct key access vs. `.get()`

```python
data["name"]          # raises KeyError if "name" is missing
data.get("name")        # returns None if "name" is missing
data.get("name", "N/A")   # returns "N/A" if "name" is missing
```

This is the same `dict` access behavior you already know from
[Dictionaries and Lookups](../02-Python-Core-Language-and-Data-Types/07-dictionaries-and-lookups.md)
— JSON does not introduce anything new here; it is simply the context
in which this choice becomes especially important, because JSON data
frequently comes from *outside* your program (§30), where a missing
key is a genuinely expected possibility, not a programmer error.

### 19.2 Why blindly chaining access is risky

```python
# RISKY -- any missing level along the way raises KeyError immediately
city = data["customer"]["profile"]["address"]["city"]
```

If `"profile"`, or `"address"`, or `"city"` is missing at *any* point
in this chain — because the source system omitted it, because the data
is from an older schema version (§40), or because it is simply
malformed — this raises `KeyError`, with an error message naming only
the *specific missing key*, not which level of the chain it was, making
the failure harder to diagnose than it needs to be.

### 19.3 Safer patterns

```python
customer = data.get("customer", {})
profile = customer.get("profile", {})
address = profile.get("address", {})
city = address.get("city")
```

```python
def get_nested(data: dict, *keys: str, default=None):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


city = get_nested(data, "customer", "profile", "address", "city")
```

The chained `.get(..., {})` pattern trades a `KeyError` for a
predictable `None`/default at the end, at each step defaulting to an
*empty dict* rather than `None`, specifically so the *next* `.get()`
call in the chain does not itself raise `AttributeError` on `None`.
The small `get_nested` helper generalizes this into one reusable,
testable function — exactly the kind of small utility §42's reusable-
functions section builds further.

## 20. Encoder/Decoder Concepts

### 20.1 Why this section exists

`json.dumps()`/`json.dump()` (encoding) and `json.loads()`/`json.load()`
(decoding) are, underneath, thin convenience wrappers around two
classes: `json.JSONEncoder` and `json.JSONDecoder`. §17.3 already
established that some Python types have **no built-in JSON
representation** — the encoder/decoder classes are exactly *where*
that gap gets filled in, deliberately, by you. §18–§26 build this out
fully; this short section previews the shape of the whole picture.

### 20.2 The core idea

```
json.dumps(obj)  ≈  JSONEncoder().encode(obj)     (using the default encoder, unless cls= is given)
json.loads(text)  ≈  JSONDecoder().decode(text)     (using the default decoder, unless cls= is given)
```

Every keyword parameter §10 and §12 already introduced
(`default=`, `object_hook=`, `parse_float=`, and the rest) is,
underneath, either configuring the *default* encoder/decoder's
behavior, or being routed to a *custom* one you supply via `cls=`. §19
and §20 make this relationship concrete.

## 21. Custom Serialization

### 21.1 What happens when a type has no built-in mapping

```python
from datetime import datetime
import json

json.dumps(datetime.now())
```

```text
Traceback (most recent call last):
  ...
TypeError: Object of type datetime is not JSON serializable
```

This is not a bug — it is §17.3's gap, made concrete: the default
encoder has no built-in rule for `datetime` objects (or `Decimal`,
`Path`, `set`, `UUID`, `Enum`, or any custom class), and raises
`TypeError` rather than silently guessing at a representation.

### 21.2 `default=` — the simplest fix

```python
json.dumps({"timestamp": datetime(2026, 9, 21, 14, 3, 0, 123456)}, default=str)
```

```text
{"timestamp": "2026-09-21 14:03:00.123456"}
```

`default` is a function the encoder calls **only** for objects it does
not already know how to serialize — it receives that one object, and
must return something *else* that *is* serializable (a string, number,
list, or dict). `default=str` is a common, extremely convenient
shortcut: "for anything you don't recognize, just call `str()` on it."

### 21.3 Why `default=str` can be convenient but dangerous

`str()` applied to an arbitrary object produces *some* text — but that
text is not guaranteed to be a **structured, reconstructable**
representation of the original data; it is whatever that object's
`__str__` happens to produce, which can be lossy, inconsistent across
Python versions or library versions, or simply not the shape your
application actually needs on the way back in (§63.2 develops exactly
this as a round-trip limitation). `default=str` is a reasonable choice
for **debugging output or logging**, where a human-readable
approximation is genuinely all that's needed — it is a risky default
for **data your program (or another program) will later parse back**,
where §21.4's more deliberate approach is the better production choice.

### 21.4 A better, explicit conversion pattern

```python
def serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


json.dumps({"timestamp": datetime.now()}, default=serialize_value)
```

This is deliberately more explicit than bare `default=str`: it converts
`datetime` specifically to a well-defined, standard, **reconstructable**
format (`.isoformat()`, §60), and re-raises `TypeError` for anything
else unexpected — surfacing a genuine gap loudly, rather than silently
`str()`-ing every unanticipated type into an ambiguous, possibly
lossy string.

## 22. `json.JSONEncoder`

### 22.1 Subclassing `JSONEncoder`

```python
import json
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


data = {"created_at": datetime.now(), "amount": Decimal("19.99")}
text = json.dumps(data, cls=CustomEncoder)
```

**`default()`** is the one method meant to be overridden — it is
called *only* for objects the base encoder cannot already handle
(exactly §21.2's `default=` parameter, now expressed as a method on a
reusable class instead of a one-off function). **`super().default(obj)`**
— calling the parent class's own `default()` for anything your override
does not specifically recognize is important: the base implementation's
job is exactly to raise the correct, standard `TypeError` (§21.1) for
truly unhandled types, rather than your custom code silently returning
`None` or something else misleading.

### 22.2 `encode()` and `iterencode()`

```python
encoder = CustomEncoder()
text = encoder.encode(data)          # returns the complete JSON string at once

for chunk in encoder.iterencode(data):   # yields the JSON text in pieces
    ...
```

`.encode(obj)` is what `json.dumps(obj, cls=CustomEncoder)` calls
internally — it returns the complete serialized string in one call.
`.iterencode(obj)` produces the same output, but as a sequence of
string chunks, yielded incrementally — this is what `json.dump()`
itself uses internally to stream output directly to a file without
necessarily holding the entire serialized string in memory as one
single object first.

### 22.3 When `cls=CustomEncoder` is the right choice

Reach for a custom `JSONEncoder` subclass (rather than a bare
`default=` function, §21.2) when the same set of custom-type rules is
needed **repeatedly, across many different `dumps()`/`dump()` calls**
throughout a program — defining the rules once, as a reusable class,
avoids repeating (and risking drift between) the same `if
isinstance(...)` chain at every call site, exactly mirroring
[03-csv-files.md](03-csv-files.md)'s §20.6 argument for custom CSV
dialects.

## 23. `json.JSONDecoder`

### 23.1 What it is, and when direct use is actually useful

```python
decoder = json.JSONDecoder()
data = decoder.decode('{"name": "Alice"}')
```

`json.JSONDecoder` is the class `json.loads()` uses internally by
default. **Direct instantiation and use is genuinely rare** in typical
application code — `json.loads(text, object_hook=..., parse_float=...)`
already exposes every commonly needed customization as a simple keyword
argument (§12), without requiring you to instantiate a decoder object
yourself. Direct use becomes relevant mainly for `.raw_decode()`
(§23.3) or when passing a custom decoder class via `cls=` to
`json.loads()` for genuinely advanced, reusable customization needs.

### 23.2 `.decode()`

```python
decoder = json.JSONDecoder()
data = decoder.decode('{"name": "Alice", "age": 30}')
```

`.decode(s)` parses a string containing **exactly one** complete JSON
value, and requires the *entire* string to be consumed — trailing,
non-whitespace content after the JSON value raises an error. This is
what `json.loads()` calls internally.

### 23.3 `.raw_decode()`

```python
decoder = json.JSONDecoder()
text = '{"name": "Alice"} some trailing text here'
data, end_index = decoder.raw_decode(text)

print(data)          # {'name': 'Alice'}
print(end_index)       # 17  -- the character position where the JSON value ended
```

`.raw_decode(s, idx=0)` parses **one JSON value starting at position
`idx`**, and returns a tuple of `(parsed_object, end_index)` —
**without** requiring the rest of the string to be empty or consumed.
This is genuinely useful for a specific, advanced scenario: text that
contains a JSON value followed by *other* content you need to handle
separately — a capability `json.loads()`/`.decode()` deliberately does
not provide, since they insist on the entire input being one clean
JSON value.

## 24. `object_hook`

### 24.1 What it does

```python
def uppercase_names(obj: dict) -> dict:
    if "name" in obj:
        obj["name"] = obj["name"].upper()
    return obj


text = '{"name": "alice", "age": 30}'
data = json.loads(text, object_hook=uppercase_names)
print(data)
```

```text
{'name': 'ALICE', 'age': 30}
```

`object_hook` is called **once for every JSON object decoded**,
**innermost first** (§24.2 makes this concrete) — receiving that
object already converted to a plain `dict`, and expected to return
whatever value should actually be used in its place, in the final
result. This is transformation happening **during** decoding, not as a
separate pass afterward.

### 24.2 A practical example: converting objects into a custom class

```python
class Customer:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Customer(id={self.id}, name={self.name!r})"


def customer_hook(obj: dict):
    if "id" in obj and "name" in obj:
        return Customer(obj["id"], obj["name"])
    return obj


text = '{"id": 1, "name": "Alice"}'
customer = json.loads(text, object_hook=customer_hook)
print(customer)
```

```text
Customer(id=1, name='Alice')
```

Because `object_hook` runs on **every** decoded object, innermost
first, it is naturally well-suited to converting nested JSON objects
into a tree of custom class instances in a single decoding pass — each
inner object is already converted (or left as a plain `dict`, if it did
not match the hook's condition) by the time an *outer* object
containing it is processed.

## 25. `object_pairs_hook`

### 25.1 What it does, and why it exists

```python
def show_pairs(pairs):
    print(pairs)
    return dict(pairs)


json.loads('{"b": 2, "a": 1}', object_pairs_hook=show_pairs)
```

```text
[('b', 2), ('a', 1)]
```

`object_pairs_hook` is called with the **raw, ordered list of
key-value pairs** for a JSON object, **before** they are collapsed into
a plain `dict` — giving you access to the exact original order and,
crucially, every occurrence of a key **even if it is duplicated**,
something a plain `dict` (which can only ever hold one value per key)
cannot represent at all.

### 25.2 Detecting duplicate keys

```python
def reject_duplicate_keys(pairs):
    seen = set()
    result = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"Duplicate key detected: {key!r}")
        seen.add(key)
        result[key] = value
    return result


json.loads('{"id": 1, "id": 2}', object_pairs_hook=reject_duplicate_keys)
```

```text
Traceback (most recent call last):
  ...
ValueError: Duplicate key detected: 'id'
```

This is `object_pairs_hook`'s single most practically useful role:
**strict duplicate-key detection**, something the default decoder does
not perform on its own (it simply keeps the last occurrence silently,
exactly mirroring the general JSON-spec behavior §4.2 already noted).

### 25.3 Precedence relative to `object_hook`

**If both `object_hook` and `object_pairs_hook` are supplied,
`object_pairs_hook` takes precedence** — `object_hook` is simply
ignored in that case. Supplying only one or the other is the normal,
clear practice.

## 26. `parse_int`

### 26.1 What it does

```python
text = '{"count": 42}'

data = json.loads(text, parse_int=str)
print(data)
```

```text
{'count': '42'}
```

By default, any JSON number written without a decimal point or
exponent is converted to a Python `int`. `parse_int` lets you supply a
**different** conversion function instead — called with the raw
matched digit text (as a `str`), and expected to return whatever value
should be used in its place.

### 26.2 Practical use cases, kept simple

Validation — a `parse_int` that raises a custom, more informative
exception for out-of-range values before the rest of your program ever
sees them. Custom numeric representations — occasionally, a system
genuinely needs integers represented as something other than a plain
Python `int` (a specific wrapper type carrying extra metadata, for
example) — `parse_int` is the mechanism that makes that substitution
possible during decoding itself, rather than as a separate post-
processing pass. This chapter deliberately keeps this example simple —
`parse_int` is used far less often in everyday code than `parse_float`
(§27), whose Decimal use case (§59) is a genuinely common, important
production pattern.

## 27. `parse_float`

### 27.1 The default float-conversion concern

```python
text = '{"price": 19.99}'

data = json.loads(text)
print(data["price"])
print(type(data["price"]))
```

```text
19.99
<class 'float'>
```

By default, any JSON number written *with* a decimal point or exponent
becomes a Python `float` — and Python's `float`, exactly like every
other language's floating-point type, cannot represent every decimal
value **exactly** — a fact already familiar from earlier Python study,
and one that matters especially for **financial values**, where a tiny
representational error is unacceptable.

### 27.2 `parse_float=Decimal`

```python
from decimal import Decimal

text = '{"price": 19.99}'

data = json.loads(text, parse_float=Decimal)
print(data["price"])
print(type(data["price"]))
```

```text
19.99
<class 'decimal.Decimal'>
```

`parse_float=Decimal` tells the decoder: "for every JSON number that
would normally become a `float`, call `Decimal(raw_text)` instead" —
because `Decimal` is constructed directly from the *original digit
text*, not from an already-imprecise `float`, this avoids introducing
floating-point representation error during decoding at all. §59
develops `Decimal`'s serialization side (the reverse direction) fully.

### 27.3 Why financial systems specifically care

A system tracking money needs decimal arithmetic to behave exactly the
way currency actually works — `0.1 + 0.2` famously does not equal
`0.3` exactly, under ordinary `float` arithmetic, because of how binary
floating-point representation works; `Decimal` arithmetic avoids this
specific class of error entirely, which is precisely why real financial
and accounting systems consistently choose it over `float` for money.

## 28. `parse_constant`

### 28.1 What "special constants" means here

Strict JSON, per its own formal specification, has **no** representation
for "not a number," positive infinity, or negative infinity. Python's
`json` module, however, recognizes three specific, non-standard textual
tokens it will still parse by default: `NaN`, `Infinity`, and
`-Infinity`.

### 28.2 `parse_constant`'s role

```python
text = '{"result": NaN}'

data = json.loads(text)
print(data["result"])
```

```text
nan
```

By default, encountering one of these three tokens calls Python's
built-in `float()` equivalent (`float("nan")`, `float("inf")`,
`float("-inf")`) automatically. `parse_constant` lets you override this
— most commonly, to **reject** these non-standard tokens outright
rather than silently accepting them:

```python
def reject_special_constants(constant_name):
    raise ValueError(f"Non-standard JSON constant encountered: {constant_name}")


json.loads('{"result": NaN}', parse_constant=reject_special_constants)
```

```text
Traceback (most recent call last):
  ...
ValueError: Non-standard JSON constant encountered: NaN
```

### 28.3 Standards compatibility, and `allow_nan`

This is precisely why §29 exists as its own section: Python's *default*
behavior here is more permissive than the strict JSON specification —
useful for round-tripping Python's own `float("nan")`/`float("inf")`
values conveniently, but a genuine interoperability risk when your JSON
needs to be consumed by another, stricter system. `allow_nan` (on the
*encoding* side) and `parse_constant` (on the *decoding* side) are the
two complementary tools for controlling this behavior in each
direction.

## 29. Numeric Edge Cases: NaN and Infinity

### 29.1 What Python's `json` module does by default

```python
import json

print(json.dumps(float("nan")))
print(json.dumps(float("inf")))
print(json.dumps(float("-inf")))
```

```text
NaN
Infinity
-Infinity
```

### 29.2 Why this can cause real interoperability problems

**`NaN`, `Infinity`, and `-Infinity` are not part of the standard JSON
specification** — a strictly conforming JSON parser in another
language (or a strict validator) may reject text containing them
outright, treating it as malformed. Python's default, permissive
behavior (`allow_nan=True`) prioritizes convenient round-tripping of
Python's own float values over strict standards compliance — a choice
worth being deliberate about, not merely inheriting by default,
whenever your JSON output needs to be consumed by a system you do not
control.

### 29.3 `allow_nan=False`

```python
json.dumps(float("nan"), allow_nan=False)
```

```text
Traceback (most recent call last):
  ...
ValueError: Out of range float values are not JSON compliant: nan
```

`allow_nan=False` makes the encoder **refuse to serialize** these
non-standard values at all, raising `ValueError` immediately — the
correct choice whenever strict, standards-compliant JSON output is
genuinely required, forcing your own code to decide explicitly how to
represent (or reject) a `NaN`/infinite value *before* it ever reaches
the encoder.

## 30. Unicode and `ensure_ascii`

### 30.1 The default: `ensure_ascii=True`

```python
data = {"city": "Kolkata", "language": "বাংলা"}

print(json.dumps(data))
```

```text
{"city": "Kolkata", "language": "\u09ac\u09be\u0982\u09b2\u09be"}
```

By default, every character outside the plain ASCII range is escaped as
a `\uXXXX` sequence (a **Unicode escape**) — the output remains
entirely ASCII text, character for character, even though the
*meaning* is fully preserved and any correct JSON parser will decode it
back to the original characters exactly.

### 30.2 `ensure_ascii=False`

```python
print(json.dumps(data, ensure_ascii=False))
```

```text
{"city": "Kolkata", "language": "বাংলা"}
```

The real Unicode characters appear directly in the output — more
human-readable, and generally somewhat smaller in byte size for
text containing many non-ASCII characters (each escaped `\uXXXX`
sequence is six ASCII characters; the real character, encoded as UTF-8,
is often only one to four bytes).

### 30.3 Interoperability and file-writing considerations

`ensure_ascii=True`'s output is always safely representable in plain
ASCII — a genuine advantage for systems, protocols, or legacy tooling
that cannot reliably handle non-ASCII bytes. `ensure_ascii=False`'s
output, containing real non-ASCII characters, **requires the receiving
system, or the file it is written to, to correctly use UTF-8 (or
another Unicode-capable encoding)** — exactly the
`encoding="utf-8"` habit already established throughout this chapter
and this entire module. For files your own program writes and reads,
`ensure_ascii=False` combined with explicit `encoding="utf-8"` is a
perfectly safe, and more readable, choice; for JSON sent to external
systems whose Unicode handling is unknown or unreliable, the default
`ensure_ascii=True` remains the safer choice.

## 31. Formatting and Determinism

### 31.1 `indent` — readability vs. compactness

```python
data = {"name": "Alice", "age": 30}

print(json.dumps(data, indent=None))   # the default -- one compact line
print(json.dumps(data, indent=2))
print(json.dumps(data, indent=4))
```

```text
{"name": "Alice", "age": 30}
{
  "name": "Alice",
  "age": 30
}
{
    "name": "Alice",
    "age": 30
}
```

`indent=None` (the default) produces the smallest, single-line output
— appropriate for machine-to-machine payloads (§33) where a human is
not expected to read the raw text, and every extra byte has a real,
if small, transmission cost. `indent=2` or `indent=4` produce
genuinely human-readable, multi-line output — appropriate for
human-maintained configuration files (§32) and anywhere a person may
need to open and directly read or edit the JSON.

### 31.2 `separators`

```python
json.dumps(data, separators=(",", ":"))
```

```text
{"name":"Alice","age":30}
```

`separators` is a two-item tuple: `(item_separator, key_separator)`.
The **most compact possible JSON** — no whitespace at all — uses
`separators=(",", ":")`, which is a genuinely common, deliberate choice
for minimizing payload size on network-transmitted JSON where every
byte matters (high-volume APIs, for example).

### 31.3 The default `separators` value depends on `indent`

**A caveat worth knowing precisely:** when `indent` is `None` (compact
output), the default separators are `(", ", ": ")` — with a space after
each comma and colon, for readability even on one line. When `indent`
is *set* (pretty-printed output), the default separators become
`(",", ": ")` — **no** trailing space after the comma, since the
following newline and indentation already provide visual separation.
This default behavior is exactly why `json.dumps(data, indent=2)`
already looks clean without you needing to also specify `separators`
explicitly — but it is worth knowing this default silently changes
based on `indent`, rather than assuming one fixed default always
applies.

### 31.4 `sort_keys` — deterministic output

```python
data = {"zebra": 1, "apple": 2, "mango": 3}

print(json.dumps(data))                    # insertion order: zebra, apple, mango
print(json.dumps(data, sort_keys=True))      # alphabetical: apple, mango, zebra
```

```text
{"zebra": 1, "apple": 2, "mango": 3}
{"apple": 2, "mango": 3, "zebra": 1}
```

`sort_keys=True` produces the **same output byte-for-byte** every time,
regardless of the order keys happened to be inserted into the source
dictionary — valuable for **stable diffs** (comparing two JSON outputs
in version control, where key-order-only differences would otherwise
create meaningless noise), for **tests** asserting exact expected
output (§44), and for any workflow relying on comparing or hashing
serialized output for equality/caching purposes.

### 31.5 What `sort_keys=True` does *not* guarantee

**Sorted keys alone do not make a serialization fully "canonical" for
every purpose.** Two semantically identical Python objects can still
serialize to different text if, for example, one uses `int` values
where the other uses equal-valued `float`s (`1` vs. `1.0` — different
JSON number text, even though `1 == 1.0` in Python), or if floating-
point rounding differs subtly between the values being compared. True
canonical serialization (a single, guaranteed-unique text
representation for any given logical value, often needed for
cryptographic signing or exact hash comparison) requires considerably
more care than `sort_keys=True` alone provides — worth knowing as a
limit, not assuming `sort_keys=True` alone has fully solved
"determinism" in the strongest possible sense.

## 32. Error Handling

### 32.1 `skipkeys`

```python
data = {1: "one", "two": 2}

json.dumps(data)                       # raises TypeError: keys must be str, int, float, bool or None, not ...
```

Wait — this needs a genuinely invalid key type to demonstrate:

```python
data = {(1, 2): "tuple key"}

json.dumps(data)
```

```text
Traceback (most recent call last):
  ...
TypeError: keys must be str, int, float, bool or None, not tuple
```

```python
json.dumps(data, skipkeys=True)
```

```text
{}
```

**Default behavior (`skipkeys=False`):** a dictionary key of a type
JSON cannot represent (anything other than `str`, `int`, `float`,
`bool`, or `None` — note that non-string keys of these allowed types
are automatically converted to their string form, §37 covers this)
raises `TypeError` immediately. **`skipkeys=True`:** the offending
key-value pair is **silently omitted** from the output instead. **Why
production code should be cautious:** silently dropping data is
dangerous — exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§18.4 and
[03-csv-files.md](03-csv-files.md)'s §19.3 principle, restated here —
`skipkeys=True` should be a deliberate, documented choice for a
specific, known reason, never a reflexive fix for an inconvenient
`TypeError`.

### 32.2 `check_circular` and circular references

```python
data = {}
data["self"] = data

json.dumps(data)
```

```text
Traceback (most recent call last):
  ...
ValueError: Circular reference detected
```

A **circular reference** is exactly what it sounds like: an object
that, directly or through some chain of nested containers, ends up
referencing *itself*. **JSON cannot represent this at all** — a JSON
document is fundamentally a finite tree of values; there is no syntax
for "this value is the same as some ancestor of itself." `check_circular=True`
(the default) detects this *before* it happens and raises a clear
`ValueError`; `check_circular=False` disables that check purely for a
small performance gain, at the real risk of an unbounded recursive
crash (`RecursionError`) instead of a clean error, on data that
actually does contain a cycle — turning it off is rarely, if ever, the
right production choice.

### 32.3 `json.JSONDecodeError`

```python
import json

try:
    data = json.loads('{"name": "Alice", "age": }')
except json.JSONDecodeError as error:
    print(f"Invalid JSON: {error}")
    print(f"Line {error.lineno}, column {error.colno} (char {error.pos})")
```

```text
Invalid JSON: Expecting value: line 1 column 26 (char 25)
Line 1, column 26 (char 25)
```

`json.JSONDecodeError` (a subclass of the built-in `ValueError`) is
raised for any syntactically malformed JSON text. Its `.msg`, `.doc`
(the full original text), `.pos` (the character offset), `.lineno`, and
`.colno` attributes together give you precisely *where* the problem is
— genuinely useful diagnostic information, well worth reporting rather
than discarding (§40 builds an entire debugging workflow directly
around reading these attributes).

## 33. JSON Validation

### 33.1 Syntax validity is not the same as application validity

```python
text = '{"age": "hello"}'

data = json.loads(text)   # succeeds -- this IS syntactically valid JSON
```

`json.loads()` succeeding tells you exactly one thing: **the text was
accepted by Python's JSON decoder** — which, with its default permissive
handling (e.g. `NaN`/`Infinity`, §28–§29), does not necessarily mean the
input strictly conforms to the JSON specification. It tells you **nothing** about
whether the *resulting data* makes sense for your application —
`{"age": "hello"}` parses without error, even though `"hello"` is
obviously not a sensible age. **Never treat successful `json.loads()`
as a signal that the data is "safe" or "correct" to use** — this is
precisely
[03-csv-files.md](03-csv-files.md)'s §31.1 lesson ("CSV usually has
weak schema guarantees"), restated for JSON, whose flexibility makes
this gap, if anything, easier to overlook.

### 33.2 The two distinct kinds of validation

**Syntax validation** — does the text parse as JSON at all? Answered
entirely by whether `json.loads()`/`json.load()` raises
`json.JSONDecodeError` (§32.3). **Schema validation** — given
successfully parsed data, does its *shape and content* actually match
what your application requires (§34)? This is a separate, deliberate
step your own code must perform — `json.loads()` provides zero help
here beyond successfully returning *some* Python object.

## 34. Schema Concepts

### 34.1 What a schema means here, informally

Exactly
[03-csv-files.md](03-csv-files.md)'s §31.2 "logical schema" concept,
now applied to nested JSON: an explicit statement, made by your own
program, of what fields are **required**, what fields are **optional**,
what **type** each field should have, what **constraints** apply (an
age must be a non-negative integer, for example), how **nested
structures** should look, and how the schema itself may **version**
over time (§40).

### 34.2 A simple, explicit Python validation function

```python
def validate_config(data: object) -> None:
    if not isinstance(data, dict):
        raise ValueError("Config must be a JSON object")

    if "version" not in data:
        raise ValueError("Config missing required field: version")
    if not isinstance(data["version"], int):
        raise ValueError("Config field 'version' must be an integer")

    if "application" not in data:
        raise ValueError("Config missing required field: application")
    app = data["application"]
    if not isinstance(app, dict) or "name" not in app:
        raise ValueError("Config field 'application' must be an object with a 'name' field")
```

This is deliberately written using **plain Python control flow and
`isinstance()` checks** — no external schema library. It is explicit
about exactly what it requires, and raises a specific, actionable
`ValueError` for the first problem it finds — this chapter does not
turn into a complete JSON Schema course; a full schema-description
*language* (with its own standard, `$ref`s, and dedicated Python
libraries) is a genuinely useful, separate tool for larger systems, but
outside this chapter's introductory scope.

### 34.3 Why boundary validation matters, restated for JSON specifically

Exactly
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§27.1 six-step discipline, applied here: parse the JSON (§33.1), then
**immediately** validate its structure and types (§34.2), **before**
any business logic runs — so that everything downstream can safely
assume it is working with well-formed, schema-conformant data.

## 35. Configuration Files

### 35.1 A realistic example

```json
{
    "app": {
        "name": "processor",
        "version": 1
    },
    "features": {
        "logging": true
    }
}
```

### 35.2 Loading, defaults, and versioning, at a glance

```python
DEFAULT_CONFIG = {"features": {"logging": False}}


def load_config(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    validate_config(raw)   # §34.2's pattern, adapted to this example's "app" shape (name and version live under "app")

    config = {**DEFAULT_CONFIG, **raw}
    return config
```

**Configuration loading** means reading and parsing the file (§13–§16).
**Defaults** means deciding, deliberately, what happens when an
*optional* field is simply absent — here, a shallow dictionary merge
supplies `DEFAULT_CONFIG`'s values for anything `raw` does not itself
provide (a genuinely nested config would need a more careful, recursive
merge — left as a natural extension, not developed fully here).
**Validation** is §34.2's job, applied immediately after parsing —
for this §35.1 example, that means checking `raw["app"]["name"]` and
`raw["app"]["version"]` rather than §34.2's top-level `"version"` and
`"application"` fields (the validation pattern is identical; only the
field names differ).
**Versioning** — checking a `"version"`/`"schema_version"` field before
trusting the rest of the structure — is §40's own, fuller subject.
**Environment overrides** (letting an environment variable override a
specific config value) are mentioned here only conceptually — the full
treatment belongs to
[09-environment-configuration-and-input-validation.md](09-environment-configuration-and-input-validation.md),
not this chapter.

## 36. API Payloads

### 36.1 The conceptual flow

```
HTTP request
    ↓
JSON payload (the request body)
    ↓
parse JSON (json.loads())
    ↓
validate (§34)
    ↓
application logic
    ↓
JSON response (json.dumps())
```

### 36.2 A simple payload example

```json
{
    "customer_id": 1001,
    "items": [
        {"sku": "ABC123", "quantity": 2}
    ]
}
```

A **request body** is the JSON text a client sends to a server,
typically deserialized (§33) immediately upon receipt, then validated
(§34) before any business logic touches it. A **response body** is the
JSON text a server sends back, typically built as an ordinary Python
`dict`/`list` and serialized (§9–§10) just before being sent. **This
chapter does not attempt a full HTTP/API tutorial** — building and
running an actual web server or client is a separate, later roadmap
topic; the point here is only that whatever request/response mechanism
you eventually use, the JSON-handling core is exactly what this chapter
has already taught.

## 37. JSON in AI/ML Systems

### 37.1 Realistic, concrete uses

**Model metadata** — architecture details, training hyperparameters,
version identifiers, stored as JSON alongside a trained model.
**Inference requests and responses** — a request describing what input
to run through a model, and the structured response containing its
output. **Dataset metadata** — descriptions of a dataset's shape,
source, size, and licensing. **Experiment configuration** — the exact
settings used for one training or evaluation run, recorded for later
reproducibility. **Evaluation results** — metrics, scores, and
per-example results from evaluating a model. **Agent state** — the
current state of a multi-step agentic system's plan, memory, or
progress. **Tool arguments** — the structured arguments an AI agent
passes when invoking an external tool or function. **Structured LLM
outputs** — a language model asked to return "an answer as JSON,"
rather than free-form prose (§38's dedicated subject). **Application
configuration and pipeline metadata** — exactly §35's subject, applied
throughout ML/AI tooling specifically.

### 37.2 Why JSON is especially important in modern AI engineering

Modern AI/ML tooling is built almost entirely around passing structured
data between many separate, often independently-developed components —
a training script, an evaluation harness, a serving API, a monitoring
dashboard, an orchestration system — and JSON's combination of being
human-readable, language-independent, and universally supported makes
it the default shared language nearly all of them speak, exactly as
§3.4 already described for the broader software ecosystem, now applied
specifically to the systems you will build in this roadmap's later
stages.

## 38. JSON and Structured AI Output

### 38.1 Free-form text vs. structured output

A language model asked "describe this customer" might return several
sentences of free-flowing prose — genuinely useful for a human to read,
but **not** something a program can reliably extract specific fields
from without additional, fragile text-parsing. Asked instead to
"return the customer's name, age, and status **as JSON**," a
well-behaved model produces text your program can parse directly with
`json.loads()` (§11) — predictable, machine-readable fields, ready for
programmatic use, rather than prose requiring separate interpretation.

### 38.2 What structured output actually buys you

**Predictable fields** — your code can reach for `result["status"]`
directly, rather than trying to extract a status from a sentence.
**Machine-readable responses** — the output slots directly into the
rest of a pipeline. **Schema enforcement, conceptually** — many modern
AI tooling systems let you *describe* the expected JSON shape
up front, increasing (though never perfectly guaranteeing) the odds the
model's output actually matches it.

### 38.3 The critical caveat: valid JSON is not automatically correct JSON

**This chapter's single most important warning for this specific
topic: an AI model successfully producing syntactically valid JSON
(§33.1) does not mean the *content* of that JSON is correct,
complete, or safe to act on.** A model can produce well-formed JSON
containing a wrong value, a missing required field it hallucinated
around, or a value of the wrong type entirely — exactly the same gap
§33.1 already established for *any* JSON source, now emphasized
specifically because AI-generated JSON is, if anything, **more** likely
to contain subtly wrong content than JSON produced by a deterministic,
well-tested traditional system. **Every principle this chapter has
built — schema validation (§34), safe access (§19), explicit error
handling (§32) — applies to AI-generated JSON with, if anything, extra
insistence, never less.** Treat it exactly like any other untrusted
input: parse, then validate, before ever acting on it.

## 39. Security

### 39.1 Why `json.loads()` output is not automatically "safe data"

Parsing succeeding means the *text* was well-formed (§33.1) — it says
nothing about whether the *content* is safe to trust or act on, exactly
as §38.3 just emphasized for AI output specifically, and as this entire
chapter's boundary-validation theme has emphasized throughout.

### 39.2 Resource exhaustion risks

**Deeply nested JSON** — a document nested thousands of levels deep
can, in principle, cause excessive recursion or stack usage during
parsing or subsequent processing. **Huge strings** — a single string
value of enormous length consumes memory proportional to its size the
moment it is parsed. **Huge arrays** — an array with millions of
elements, similarly. **Huge numbers** — a number written with an
enormous number of digits can require meaningfully more processing to
parse and represent than an ordinary-sized one. **Unexpected object
structures** — an object with an enormous number of distinct keys, or
structured in a way your code's validation (§34) does not anticipate.
**The defense, in every case, is the same:** validate structure and
size expectations **before** business logic runs, and consider
explicit limits (a maximum accepted payload size, a maximum expected
nesting depth) for any endpoint or pipeline accepting JSON from a
genuinely untrusted source.

### 39.3 Never use `eval()` to parse JSON

```python
# NEVER DO THIS
data = eval(text)
```

Because JSON's syntax closely resembles a Python dictionary/list
literal (§6.1), it can be tempting to "parse" it with Python's built-in
`eval()` instead of `json.loads()`. **This is a serious security
vulnerability, not merely bad style**: `eval()` executes the given text
as **arbitrary Python code** — if `text` comes from any source you do
not fully control (a network request, a file another process could
write to, user input), an attacker can supply text that is not JSON at
all, but a malicious Python expression, and have it **execute** with
your program's own privileges. `json.loads()`, by contrast, is a
dedicated **parser** — without custom hooks, the standard decoder
produces Python representations of the JSON value types (§4.1);
custom decoder hooks (`object_hook`, `parse_float`, and so on) can
deliberately transform decoded values into other Python objects. Unlike
`eval()`, `json.loads()` does not execute arbitrary Python expressions
from the input, no matter what text it is given. **There is never a legitimate reason to use
`eval()` to parse JSON — `json.loads()` is always the correct tool,
with no exceptions.**

## 40. Large JSON

### 40.1 Why `json.load()` needs the whole structure in memory

Unlike
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§15 line-by-line text streaming, or
[03-csv-files.md](03-csv-files.md)'s §28 row-by-row CSV streaming,
**a single JSON document is one complete, nested value** — there is no
meaningful way to "read the first half of a JSON array" in isolation,
because the document's overall structure (where does this array end?
does this object close correctly?) is only fully knowable once the
*entire* text has been parsed. `json.load()`/`json.loads()` therefore
must, by the format's own nature, hold the complete parsed structure in
memory at once — for a sufficiently large document, this carries
exactly the same memory risk already established for `f.read()` on huge
text files.

### 40.2 Alternatives, conceptually

**Streaming formats** — formats specifically designed to be processed
incrementally, one piece at a time, without needing the whole document
in memory — **JSON Lines/NDJSON** (§41) is the most directly relevant
one for this chapter, and is fully standard-library-achievable.
**Incremental parsing libraries** — third-party libraries exist that
can parse a single, enormous JSON *document* (not JSON Lines)
incrementally, without loading the whole thing — genuinely useful for
specific large-document scenarios, but outside this chapter's
standard-library-first scope. **Database/object storage approaches** —
for data that is fundamentally too large or too frequently queried to
be handled as one JSON blob at all, a real database, or structured
object storage, is often the more appropriate tool entirely, rather
than forcing an ever-larger JSON file to keep working.

### 40.3 When plain `json.load()` remains entirely appropriate

For the overwhelming majority of real, practical cases — configuration
files, API payloads, metadata files, moderate-sized datasets — a JSON
document's size is nowhere near large enough for this to matter at all;
`json.load()`/`json.loads()` remain the simplest, most direct, entirely
correct choice. This section's concern becomes relevant specifically
once a *single* JSON document genuinely approaches a size where holding
it entirely in memory is itself a real constraint — a threshold worth
recognizing, not a reason to reach for more complex tooling by default.

## 41. JSON Lines / NDJSON

### 41.1 What it is

```
{"id": 1, "name": "Alice"}
{"id": 2, "name": "Bob"}
```

**JSON Lines** (also called **NDJSON**, "newline-delimited JSON") is a
convention — **not** a single JSON document — where each individual
**line** of a file is its own, independently complete, valid JSON
value (almost always an object). Crucially, **the file as a whole is
not valid JSON** — there are no enclosing `[` `]` brackets and no
commas between "records"; it is a sequence of separate JSON texts,
simply placed one per line.

### 41.2 Why this format exists

Exactly §40.1's limitation is what JSON Lines directly solves: because
each line is an **independent, complete** JSON value, a file can be
processed **one line, one record, at a time** — read a line, parse
*just that line* with `json.loads()`, process it, move on — so
memory does not need to grow with the total number of records (peak
memory still depends on the current record's size and any state you
retain while processing). This makes
JSON Lines a natural fit for **logs** (one JSON-formatted log entry per
line, appended over time, exactly mirroring
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§19 append-mode logging pattern), **data pipelines**, and **large
datasets** distributed as one record per line.

### 41.3 A simple Python implementation

```python
import json
from pathlib import Path
from typing import Iterator


def read_json_lines(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_json_lines(path: Path, records: Iterator[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record))
            f.write("\n")
```

This simple reader stops at the first malformed line, because
`json.loads()` raises `json.JSONDecodeError`. A production ingestion
reader that must continue past isolated bad records should catch
`json.JSONDecodeError` at the record (line) boundary and log or
quarantine that line.

**Nothing new is needed here** — this is exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
own `for line in f:` streaming pattern (§8, §15), combined with
`json.loads()`/`json.dumps()` applied to one line at a time, rather
than to the whole file at once. `line.strip()` and the `if line:`
check skip blank trailing lines (a common artifact of how files are
often written), rather than passing an empty string to `json.loads()`
and raising unnecessarily.

### 41.4 JSON document vs. JSON Lines — the distinction, restated precisely

| | A JSON document (`.json`) | JSON Lines (`.jsonl`/`.ndjson`) |
|---|---|---|
| **Whole file is valid JSON?** | Yes — exactly one JSON value | **No** — not one JSON value at all |
| **Structure** | Usually one large object or array | One independent JSON value per line |
| **Parsed with** | `json.load()`/`json.loads()`, once | `json.loads()`, once per line |
| **Streamable?** | No — needs the whole structure (§40.1) | **Yes** — naturally, line by line |

## 42. Atomic Updates

### 42.1 Why directly overwriting an important JSON file is risky

```python
# RISKY -- if the process crashes mid-write, config.json is left corrupted
with open("config.json", "w", encoding="utf-8") as f:
    json.dump(new_config, f, indent=2)
```

If writing is interrupted partway through — a crash, a full disk, a
killed process — `config.json` can be left as a **partial, invalid**
JSON file: truncated mid-object, unreadable by the very next
`json.load()` call, including possibly your own program's *next* run.
This is exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§29.2/§42's write-then-replace pattern, and
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§30.1 safe-write pattern, now applied specifically to JSON.

### 42.2 The safe pattern, conceptually

```
1. write the complete new content to a TEMPORARY file, fully
2. (flush/sync, conceptually -- see the caveat below)
3. REPLACE the original file with the temporary one, as one step
```

```python
from pathlib import Path


def save_json_safely(path: Path, data: object) -> None:
    temporary_path = path.with_name(path.name + ".tmp")
    temporary_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temporary_path.replace(path)
```

This is a basic single-writer pattern. A production system with
concurrent writers may need a uniquely named temporary file and
additional coordination/durability guarantees.

Directly reusing
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§30.1 pattern and its own `.replace()` method (§17.2 there): the *real*
target file is either fully, correctly updated, or left completely
untouched — never caught in a half-written, corrupted intermediate
state as a direct result of this specific write logic.

### 42.3 Do not overstate the guarantee

Exactly the same honest limitation
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§30.3 already stated: `.replace()` is typically atomic at the
filesystem level, on the same filesystem/volume — this is a real,
meaningful, and useful guarantee, but it is **not** an unconditional
guarantee of absolute physical durability against every possible
hardware or power failure. What this pattern reliably prevents is your
*own write logic* ever leaving the target file in a corrupted,
partially-written state.

## 43. Versioning

### 43.1 Why formats evolve

Real applications change over time — new fields get added, old ones
get removed or renamed, the meaning of an existing field can shift.
Data written by an *older* version of your program can still be sitting
around (a saved config file, an old experiment's metadata) long after
the program itself has moved on — **versioning** is how your program
tells the difference between "data written for the current expected
shape" and "data written for some earlier shape," so it can react
correctly to each.

### 43.2 A simple versioning pattern

```json
{
    "schema_version": 2,
    "data": {
        "name": "Alice",
        "email": "alice@example.com"
    }
}
```

```python
SUPPORTED_VERSIONS = {1, 2}


def load_versioned(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))

    version = raw.get("schema_version")
    if version not in SUPPORTED_VERSIONS:
        raise ValueError(f"Unsupported schema version: {version!r}")

    if version == 1:
        raw = migrate_v1_to_v2(raw)

    return raw["data"]
```

**Why check versions explicitly, and reject unsupported ones:**
silently trying to process data from a schema shape your current code
was never written against risks exactly the same class of silent,
hard-to-diagnose failure
[03-csv-files.md](03-csv-files.md)'s §31.3 already warned about for a
reordered CSV column — an explicit version check turns that into an
immediate, clear, actionable error instead. **Migrations** (a function
like `migrate_v1_to_v2` above) let your program keep reading genuinely
old data correctly, by explicitly transforming it into the current
expected shape, rather than either breaking on it or silently
misinterpreting it.

## 44. Performance

### 44.1 Where the real costs are

**Serialization and deserialization time** scale with the total amount
of data being converted — genuinely large, deeply nested structures
take proportionally longer. **Object allocation and memory** — every
decoded JSON value becomes a real, separate Python object (a `dict`, a
`list`, a `str`, and so on) — a large document produces a
correspondingly large number of live Python objects, each with real
memory overhead, not merely the "size" of the raw text itself.
**Indentation overhead** (`indent=`, §31.1) makes output larger and
somewhat slower to produce than compact output, purely due to the
extra whitespace characters. **Sorting overhead** (`sort_keys=True`,
§31.4) adds a real, if usually small, cost for sorting every object's
keys during serialization. **Repeated, unnecessary conversion** — the
single most common, avoidable real-world cost: serializing the same
data more than once, or deserializing the same text repeatedly, when
the result could simply be reused, computed once.

### 44.2 `json.load()` vs. JSON Lines streaming, compared directly

For genuinely large data, §41's JSON Lines approach uses dramatically
less peak memory than `json.load()` on an equivalently large single
JSON document, for exactly the reason §40.1/§41.2 already established
— because it never needs the entire structure resident in memory at
once. For data that is *not* large, `json.load()` remains simpler and
entirely appropriate (§40.3) — JSON Lines' streaming advantage is a
deliberate trade against the convenience of "the whole thing is one
easy-to-navigate Python object," a trade only worth making once size
genuinely demands it.

### 44.3 Measure before optimizing

Exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§32.4 principle, restated here: do not reach for `separators=`
micro-tuning, disabling `check_circular`, or switching to JSON Lines
purely on suspicion — confirm a real, measured performance problem
first
([Profiling and Measuring Before Optimizing](../10-Production-Habits-for-Python-Programs/06-profiling-and-measuring-before-optimizing.md),
much later in the roadmap), then apply the specific fix that measurement
actually justifies.

## 45. Reusable Serialization Utilities

### 45.1 A small, focused function set

```python
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any, *, indent: int = 2) -> None:
    path.write_text(
        json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def serialize_config(config: dict[str, Any]) -> str:
    return json.dumps(config, indent=2, sort_keys=True)
```

### 45.2 Design notes

**Separation of I/O and serialization** — `serialize_config` does
**not** touch the filesystem at all; it is pure text conversion,
independently testable with a plain dictionary and no file involved
(§44's testing chapter equivalent relies on exactly this). `load_json`/
`save_json` handle the I/O, using
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
`Path.read_text()`/`.write_text()` (already the correct integration
point, per that chapter's own §15). **Type hints** — `Any` (from
`typing`) is the honest, correct hint for "could genuinely be any
JSON-representable value" — `load_json`'s return type is not knowable
more specifically without also knowing the exact schema being loaded.
**Deterministic formatting** — `save_json` defaults to `sort_keys=True`
(§31.4), a reasonable default for files meant to be version-controlled
or diffed; a caller needing different behavior can always call
`json.dumps()` directly instead. **Error handling** — deliberately left
to propagate, exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§28.3 and
[03-csv-files.md](03-csv-files.md)'s §41.2 principle: a low-level,
reusable utility is rarely the right place to decide how a missing
file or malformed JSON should be handled — that decision belongs to
the caller, with the full context only it has.

## 46. Dataclasses and Custom Types

### 46.1 A first approach: converting to `dict` manually

```python
@dataclass
class User:
    id: int
    name: str


user = User(id=1, name="Alice")
data = {"id": user.id, "name": user.name}
text = json.dumps(data)
```

Fully explicit, and works everywhere — but repetitive, and easy to let
drift out of sync if the dataclass's fields change.

### 46.2 `dataclasses.asdict()`

```python
from dataclasses import dataclass, asdict


@dataclass
class User:
    id: int
    name: str


user = User(id=1, name="Alice")
text = json.dumps(asdict(user))
print(text)
```

```text
{"id": 1, "name": "Alice"}
```

`asdict()` (from the standard `dataclasses` module, developed fully in
[Dataclasses and Data Models](../08-Object-Oriented-Design-Data-Modelling-and-Functional-Style/03-dataclasses-and-data-models.md),
later in the roadmap — used here only as a practical bridge to JSON)
converts a dataclass instance into an ordinary Python `dict`, field by
field, **recursively** for nested dataclasses — a meaningfully less
repetitive alternative to §46.1's manual version, for straightforward
cases.

### 46.3 Why `json.dumps(asdict(obj))` is not always sufficient

`asdict()` recurses into nested **dataclasses**, but does **not** know
how to handle a dataclass field whose value is itself a type JSON
cannot represent directly (§17.3) — a `datetime` field, a `Decimal`
field, a `Path` field, an `Enum` field, or a *non-dataclass* custom
object nested inside. `json.dumps(asdict(user))` will raise exactly
the same `TypeError` (§21.1) the moment it reaches such a field —
`asdict()` solves the "nested dataclasses" problem specifically; it
does not solve §17.3's broader "unrepresentable types" problem at all,
which still needs `default=`/a custom encoder (§21, §22) layered on
top.

### 46.4 Reconstruction: JSON back into a domain object

```python
def user_from_dict(data: dict) -> User:
    if "id" not in data or "name" not in data:
        raise ValueError(f"Invalid user data: {data}")
    return User(id=data["id"], name=data["name"])


text = '{"id": 1, "name": "Alice"}'
user = user_from_dict(json.loads(text))
```

**`json.loads()` alone never produces a `User` — only a plain `dict`.**
Turning that `dict` into a real, validated domain object is a separate,
deliberate step — exactly `object_hook`'s purpose (§24.2), or, as
shown here, a simple, explicit factory function called *after*
`json.loads()` completes. The explicit function form is often clearer
for a *single*, specific target type; `object_hook` becomes more useful
when the same JSON document contains *many different* nested object
shapes that each need their own conversion, in one decoding pass.

### 46.5 Enums

```python
from enum import Enum


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


json.dumps({"status": Status.ACTIVE})
```

```text
Traceback (most recent call last):
  ...
TypeError: Object of type Status is not JSON serializable
```

```python
json.dumps({"status": Status.ACTIVE.value})
```

```text
{"status": "active"}
```

**Ordinary `Enum` members are not directly serializable by the default
JSON encoder** (§17.3; `int`- and `float`-derived Enum classes such as
`IntEnum` have special support) — you must explicitly choose what to
serialize. **Choosing between `.name` (`"ACTIVE"`) and
`.value` (`"active"`) is a deliberate data-contract decision**, not an
arbitrary one: `.value` is often more meaningful to an external system
that has no knowledge of your Python `Enum` class at all; `.name`
directly mirrors your Python code's own identifier, which can be more
convenient internally but is a less natural fit for external
consumers. Whichever you choose, the **reverse** conversion
(`Status("active")` or `Status["ACTIVE"]`) must use the matching one —
a mismatch here silently breaks round-tripping (§63).

### 46.6 `Decimal`

```python
from decimal import Decimal

json.dumps({"price": Decimal("19.99")})
```

```text
Traceback (most recent call last):
  ...
TypeError: Object of type Decimal is not JSON serializable
```

**JSON is not inherently "decimal-safe."** Directly extending §27's
`parse_float=Decimal` (the *decoding* side): on the *encoding* side,
`Decimal` has no built-in JSON representation either — an explicit
`default=` function (§21.4), converting `Decimal` to `str(value)` (the
**exact** digit text, avoiding any `float` round-trip and its
associated precision risk) is the correct, deliberate approach —
**never** convert a `Decimal` through `float()` on the way to JSON, as
that reintroduces exactly the precision loss `Decimal` exists to avoid.

### 46.7 `datetime`

```python
from datetime import datetime

now = datetime(2026, 9, 21, 14, 3, 0, 123456)
json.dumps({"created_at": now})
```

```text
Traceback (most recent call last):
  ...
TypeError: Object of type datetime is not JSON serializable
```

```python
json.dumps({"created_at": now.isoformat()})
```

```text
{"created_at": "2026-09-21T14:03:00.123456"}
```

`datetime` has no built-in JSON representation either. **`.isoformat()`**
produces the widely-standard **ISO 8601** text format — the
conventional, interoperable choice for representing a datetime as JSON
text. Reconstructing it on the way back in requires an explicit,
matching step:

```python
from datetime import datetime

recovered = datetime.fromisoformat(data["created_at"])
```

**Timezone-aware datetimes** carry their offset information directly
within the `.isoformat()` text itself (e.g. a trailing `+00:00`) —
`datetime.fromisoformat()` correctly reconstructs a timezone-aware
`datetime` from such text; full timezone handling itself belongs to
[Datetime, Timezones, and Timestamps](../09-Advanced-Production-Oriented-Python-Foundations/07-datetime-timezones-and-timestamps.md),
much later in the roadmap — this section shows only the JSON-integration
piece.

### 46.8 `Path`

```python
from pathlib import Path

json.dumps({"output": Path("data/results.json")})
```

```text
Traceback (most recent call last):
  ...
TypeError: Object of type PosixPath is not JSON serializable
```

(On POSIX systems the error names `PosixPath`; on Windows it names
`WindowsPath`.)

```python
json.dumps({"output": str(Path("data/results.json"))})
```

```text
{"output": "data/results.json"}
```

`Path` (§17.3) has no built-in JSON mapping either — `str(path)`
(exactly
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§23.2 conversion) is the explicit fix. **A genuine design decision your
application must make deliberately:** should the stored text be an
**absolute** path, a **relative** path, a full **URI**, or a purely
**logical identifier** unrelated to any real filesystem location at
all? Each has real trade-offs — an absolute path is unambiguous on the
machine that wrote it, but almost certainly wrong on a different
machine (exactly
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)'s
§35 mistake 1's hardcoded-absolute-path warning, now applied to
*stored* data, not just source code); a relative path requires the
reader to know, separately, what it is relative *to* (exactly that same
chapter's §8.2 lesson). This choice should be made explicitly, not left
to whatever `str(path)` happens to produce by accident.

## 47. Testing

### 47.1 Why `tmp_path`, restated for JSON specifically

Exactly the same principle established throughout this module: JSON
file tests should use `pytest`'s `tmp_path` fixture, never real project
files.

### 47.2 Testing valid and invalid JSON

```python
import json
import pytest


def test_load_json_reads_valid_file(tmp_path):
    path = tmp_path / "data.json"
    path.write_text('{"name": "Alice"}', encoding="utf-8")

    assert load_json(path) == {"name": "Alice"}


def test_load_json_raises_for_malformed_content(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"name": }', encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_json(path)
```

### 47.3 Testing empty structures, missing keys, and nested data

```python
def test_empty_object_and_array():
    assert json.loads("{}") == {}
    assert json.loads("[]") == []


def test_get_nested_handles_missing_key():
    data = {"customer": {"profile": {}}}
    assert get_nested(data, "customer", "profile", "address", "city") is None
```

### 47.4 Testing wrong types, null values, Unicode, and special characters

```python
def test_validate_config_rejects_wrong_type():
    with pytest.raises(ValueError):
        validate_config({"version": "not a number", "application": {"name": "x"}})


def test_null_becomes_none():
    assert json.loads('{"value": null}')["value"] is None


def test_unicode_round_trips_with_ensure_ascii_false():
    data = {"language": "বাংলা"}
    text = json.dumps(data, ensure_ascii=False)
    assert json.loads(text) == data


def test_special_characters_in_strings():
    data = {"text": 'Quote: " Backslash: \\ Newline:\n'}
    text = json.dumps(data)
    assert json.loads(text) == data
```

### 47.5 Testing deterministic and custom-type serialization

```python
def test_sort_keys_produces_deterministic_output():
    a = json.dumps({"b": 1, "a": 2}, sort_keys=True)
    b = json.dumps({"a": 2, "b": 1}, sort_keys=True)
    assert a == b


def test_datetime_is_serialized_via_isoformat():
    dt = datetime(2026, 9, 21, 14, 0, 0)
    text = json.dumps({"created_at": dt.isoformat()})
    assert json.loads(text)["created_at"] == "2026-09-21T14:00:00"
```

### 47.6 Testing large-ish JSON and version mismatches

```python
def test_processes_large_ish_json_lines(tmp_path):
    path = tmp_path / "data.jsonl"
    records = [{"id": i} for i in range(5000)]
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")

    loaded = list(read_json_lines(path))
    assert len(loaded) == 5000


def test_unsupported_schema_version_raises(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"schema_version": 99, "data": {}}', encoding="utf-8")

    with pytest.raises(ValueError):
        load_versioned(path)
```

## 48. Round-Trip Testing

### 48.1 The pattern

```
Python object  →  json.dumps()/json.dump()  →  JSON text
JSON text       →  json.loads()/json.load()    →  Python object
```

```python
def test_round_trip_preserves_data():
    original = {"name": "Alice", "age": 30, "tags": ["a", "b"]}

    text = json.dumps(original)
    decoded = json.loads(text)

    assert decoded == original
```

### 48.2 Why exact equality can sometimes fail — and why that is expected, not a bug

**Tuples become lists.** `{"point": (1, 2)}` serializes as
`{"point": [1, 2]}`, and decodes back as `{"point": [1, 2]}` — a
`list`, never a `tuple` (§6.2, §17.2) — an "equality" test comparing
against the *original* dictionary containing a tuple would fail, not
because anything is broken, but because JSON genuinely has no way to
distinguish the two. **Custom types require symmetric conversion
rules.** A round-trip test for a `datetime` or `Decimal` field (§46.6–
§46.7) must decode using the *matching* reconstruction function
(`datetime.fromisoformat()`, `Decimal(text)`) — comparing the decoded
`str` directly against the original `datetime` object will always
fail, correctly, since they are genuinely different types. **Numeric
representation** — a `Decimal("19.99")` serialized via `default=str`
and then decoded back with plain `json.loads()` (no `parse_float=`)
becomes a plain `str`, not a `Decimal` — round-tripping through
`Decimal` correctly requires *both* the encode-side and decode-side
custom handling to be present and matched. **Ordering assumptions** —
comparing two *dictionaries* for equality in Python does not care about
key order at all (`{"a": 1, "b": 2} == {"b": 2, "a": 1}` is `True`) —
but comparing the *serialized text* directly (`json.dumps(a) ==
json.dumps(b)`) very much does, unless `sort_keys=True` is used on both
(§31.4–§31.5). **A correct round-trip test compares the *reconstructed
Python objects* for logical equality, using the matching, deliberate
conversion rules on both sides — not the raw JSON text, and not a
naive assumption that "whatever went in comes back identically."**

## 49. Debugging

### 49.1 A systematic eleven-step workflow

1. **Inspect the raw JSON text directly**, before assuming anything
   about its structure.
2. **Use `repr()`**, not plain `print()`, to reveal hidden or
   unexpected characters.
3. **Check quotes** — double quotes only, consistently (§5.1).
4. **Check commas** — missing, extra, or trailing (§5.1).
5. **Check braces** — every `{` has a matching `}`.
6. **Check brackets** — every `[` has a matching `]`.
7. **Check encoding** — is `encoding="utf-8"` actually correct for
   this file's real origin (§13.2)?
8. **Inspect the error's `.lineno`/`.colno`/`.pos`** on any
   `json.JSONDecodeError` (§32.3) — it points directly at the problem.
9. **Isolate the smallest failing JSON** — hand-craft a tiny snippet
   reproducing exactly the suspicious pattern.
10. **Validate structure explicitly** — print `type(data)`, and the
    result of `.keys()` on any dict along the access chain, rather than
    assuming.
11. **Reproduce programmatically** — a minimal, standalone script
    (or test, §47) calling exactly the failing code path in isolation
    from the rest of your program.

### 49.2 Realistic debugging scenarios

**"My `json.loads()` call raises `JSONDecodeError` on data that looks
fine when I read it."** Steps 3–6 and step 8 — print
`repr(error.doc[max(0, error.pos - 20):error.pos + 20])` to see the
*exact* text surrounding the reported failure position; a single-quote,
a trailing comma, or an unescaped internal quote is very often visible
immediately.
**"A field I know exists raises `KeyError`."** Step 10 — print
`repr(list(data.keys()))` to check for an unexpected key name (extra
whitespace, different capitalization, or a BOM-related artifact,
exactly mirroring
[03-csv-files.md](03-csv-files.md)'s §26.4 lesson, now applied to a
JSON file's very first key).
**"My custom-typed data round-trips into the wrong Python type."** §48's
entire section — confirm the decode side's conversion rule (`parse_float=`,
`object_hook=`, or an explicit post-`loads()` factory function) actually
matches the encode side's rule, symmetrically.

## 50. Common Mistakes

**1. Confusing JSON with a Python `dict`.**
Directly §6's entire section — a JSON *text* and a Python *object* are
different things; converting between them is explicit (§7).

**2. Using Python `True`/`False`/`None` in raw JSON text.**
Directly §5.3's worked example — must be lowercase `true`/`false`/`null`.

**3. Using single quotes in JSON.**
Directly §5.2's worked example — JSON requires double quotes only.

**4. Trailing commas.**
Directly §5.1 — not permitted in standard JSON.

**5. Forgetting `json.loads()` and treating raw text as if it were
already parsed.**
```python
# BAD
text = '{"name": "Alice"}'
print(text["name"])   # TypeError -- text is a plain str, not a dict!
```
→ **Better:** `data = json.loads(text)` first.

**6. Passing a `dict` where a JSON string is expected.**
```python
# BAD
data = {"name": "Alice"}
json.loads(data)   # TypeError -- loads() expects str/bytes, not a dict
```
→ You already *have* the Python object — no conversion is needed at
all here.

**7. Passing a JSON string where a `dict` is expected.**
```python
# BAD
text = '{"name": "Alice"}'
print(text.get("name"))   # AttributeError -- str has no .get()
```
→ **Better:** `data = json.loads(text)` first, then `data.get("name")`.

**8. Using `load` instead of `loads` (or vice versa).**
Directly §16.2's naming-convention explanation — `load` expects a file
object; `loads` expects a string.

**9. Using `dump` instead of `dumps` (or vice versa).**
Same principle, on the writing side.

**10. Forgetting encoding.**
```python
# RISKY
with open("config.json") as f:
    data = json.load(f)
```
→ **Better:** always `encoding="utf-8"` explicitly (§13.2).

**11. Ignoring `JSONDecodeError`.**
```python
# BAD
try:
    data = json.loads(text)
except Exception:
    data = {}
```
→ Hides every kind of failure identically, exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§27.3 principle. **Better:** catch `json.JSONDecodeError` specifically
(§32.3).

**12. Assuming valid JSON means valid application data.**
Directly §33.1's entire point.

**13. Using `eval()` to parse JSON.**
Directly §39.3 — a genuine security vulnerability, never appropriate.

**14. Blindly using `default=str` for production data.**
Directly §21.3's warning — convenient for debugging, risky for data
meant to be reliably reconstructed later.

**15. Loading huge JSON files entirely into memory without
considering alternatives.**
Directly §40's entire section — consider JSON Lines (§41) once size
genuinely warrants it.

**16. Assuming all JSON values map cleanly to the Python types you
expect.**
A field declared as "always a number" in your head can still arrive as
a JSON string, or `null`, from a real, external, untrusted source —
validate explicitly (§34) rather than assuming.

**17. Ignoring versioning.**
Directly §43 — trusting data's shape has not changed, without checking,
risks exactly the silent-mismatch failure mode
[03-csv-files.md](03-csv-files.md)'s §31.3 already warned about.

**18. Trusting AI-generated JSON without validation.**
Directly §38.3 — syntactically valid is not the same as correct;
validate exactly as you would any other untrusted JSON source.

## 51. Bad vs. Good Code

```python
# BAD -- a genuine security vulnerability
data = eval(text)

# GOOD
data = json.loads(text)
```
**Why:** §39.3 — `eval()` executes arbitrary code; `json.loads()` (without custom hooks) produces only
Python representations of JSON's value types and never executes the input.

```python
# BAD -- data is already a dict; this raises TypeError
data = {"name": "Alice"}
result = json.loads(data)

# GOOD -- use the value in the representation it's actually in
data = {"name": "Alice"}
result = data
```
**Why:** §50 mistakes 6–7 — know which representation (text vs.
object) you actually have before choosing an operation.

```python
# RISKY, for production data meant to be reliably reconstructed later
json.dumps(obj, default=str)

# BETTER -- explicit, deliberate, reconstructable rules
def serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Cannot serialize {type(value).__name__}")

json.dumps(obj, default=serialize_value)
```
**Why:** §21.3–§21.4 — `str()` is convenient but not guaranteed to be a
faithful, reconstructable representation.

```python
# BAD -- relies on a platform-dependent default encoding
with open("config.json") as f:
    data = json.load(f)

# GOOD -- explicit, correct on every platform
with open("config.json", encoding="utf-8") as f:
    data = json.load(f)
```
**Why:** exactly
[01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
§25.3 principle, restated here.

## 52. End-to-End Examples

### 52.1 Example 1 — Application Configuration Loader

```python
import json
from pathlib import Path
from typing import Any


class ConfigError(Exception):
    pass


DEFAULTS = {
    "features": {"logging": False},
}


def _validate(data: Any) -> None:
    if not isinstance(data, dict):
        raise ConfigError("Config root must be a JSON object")
    if "app" not in data or not isinstance(data["app"], dict):
        raise ConfigError("Config must contain an 'app' object")
    if "name" not in data["app"] or not isinstance(data["app"]["name"], str):
        raise ConfigError("Config 'app.name' must be a string")
    if "version" not in data["app"] or not isinstance(data["app"]["version"], int):
        raise ConfigError("Config 'app.version' must be an integer")


def load_config(path: Path) -> dict:
    # 1. Load JSON, catching syntax errors explicitly.
    try:
        raw_text = path.read_text(encoding="utf-8")
        raw = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise ConfigError(f"{path} is not valid JSON: {error}") from error

    # 2. Validate structure and types before trusting the content.
    _validate(raw)

    # 3. Apply defaults for anything optional and missing.
    features = {**DEFAULTS["features"], **raw.get("features", {})}

    # 4. Convert to a clean, ready-to-use internal representation.
    return {
        "app_name": raw["app"]["name"],
        "app_version": raw["app"]["version"],
        "logging_enabled": features["logging"],
    }
```

**Stage by stage:** loading and syntax-error handling happen first,
raising a single, clear, application-specific `ConfigError` rather than
letting `json.JSONDecodeError` leak out unexplained; validation runs
immediately after, before defaults or business logic touch the data at
all (§34.3); defaults are applied explicitly, field by field, rather
than assumed; the function's final return value is a deliberately
*flattened*, already-validated internal shape — exactly
[03-csv-files.md](03-csv-files.md)'s §46.1 pattern, restated for
nested config data.

### 52.2 Example 2 — Advanced: Experiment Metadata Manager

```python
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

SCHEMA_VERSION = 1


@dataclass
class ExperimentMetadata:
    experiment_id: UUID
    created_at: datetime
    model_name: str
    dataset_path: Path


def _encode(value):
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def save_experiment(path: Path, metadata: ExperimentMetadata) -> None:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "data": asdict(metadata),
    }
    text = json.dumps(payload, default=_encode, indent=2, sort_keys=True)

    temporary_path = path.with_name(path.name + ".tmp")
    temporary_path.write_text(text, encoding="utf-8")
    temporary_path.replace(path)


def load_experiment(path: Path) -> ExperimentMetadata:
    raw = json.loads(path.read_text(encoding="utf-8"))

    if raw.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Unsupported experiment schema version: {raw.get('schema_version')!r}")

    data = raw["data"]
    return ExperimentMetadata(
        experiment_id=UUID(data["experiment_id"]),
        created_at=datetime.fromisoformat(data["created_at"]),
        model_name=data["model_name"],
        dataset_path=Path(data["dataset_path"]),
    )
```

**Architecture and trade-offs:** `_encode` centralizes every custom-type
rule this specific data shape needs (§21.4's pattern); `asdict()`
(§46.2) handles the dataclass-to-dict conversion for the *known*
fields, while `_encode` (via `default=`) handles the fields `asdict()`
alone cannot serialize (§46.3); `save_experiment` uses the safe
write-then-replace pattern (§42.2); `load_experiment` checks
`schema_version` before trusting anything else in the payload (§43.2),
and reconstructs every custom-typed field using the *matching* inverse
operation (`UUID(...)`, `datetime.fromisoformat(...)`, `Path(...)`) —
directly satisfying §48.2's round-trip-correctness requirement. This
example uses **only the standard library** — `dataclasses`, `json`,
`datetime`, `pathlib`, `uuid` — deliberately, since the goal is
mastering exactly what these already provide together.

## 53. Advanced API Reference

No invented APIs — every entry below is a genuine, documented member of
Python's `json` module.

### 53.1 Functions

| API | Purpose | Basic syntax | Key parameters | Returns | Caveat |
|---|---|---|---|---|---|
| `json.dumps` | Serialize to a `str` | `json.dumps(obj, **opts)` | `indent`, `sort_keys`, `default`, `ensure_ascii`, ... (§10) | `str` | Never writes a file |
| `json.loads` | Deserialize from a `str` | `json.loads(s, **opts)` | `object_hook`, `parse_float`, `parse_int`, ... (§12) | The corresponding Python object | Requires syntactically complete JSON text |
| `json.dump` | Serialize directly to a file object | `json.dump(obj, fp, **opts)` | Same as `dumps`, plus `fp` | `None` | `fp` must already be open, in text mode (it receives JSON text) |
| `json.load` | Deserialize directly from a file object | `json.load(fp, **opts)` | Same as `loads`, plus `fp` | The corresponding Python object | `fp` must be a readable file-like object (text or binary file objects work); for normal text-file use, specify `encoding="utf-8"` (§13.2) |
| `json.detect_encoding` | Guess text encoding from raw bytes, per the JSON spec | `json.detect_encoding(b)` | — | The detected encoding name, as `str` | Low-level; rarely called directly (§8.3) |

### 53.2 Classes

| API | Purpose | Key methods/attributes | Caveat |
|---|---|---|---|
| `json.JSONEncoder` | The default serializer, and the base class for custom ones | `.encode()`, `.iterencode()`, `.default()` (§22) | Override only `.default()`; call `super().default(obj)` for the fallback case |
| `json.JSONDecoder` | The default parser, and the base class for custom ones | `.decode()`, `.raw_decode()` (§23) | Direct use is rare — `loads()`'s own keyword parameters usually suffice |
| `json.JSONDecodeError` | The exception raised for malformed JSON text | `.msg`, `.doc`, `.pos`, `.lineno`, `.colno` (§32.3) | A subclass of the built-in `ValueError` |

### 53.3 Hooks and parameters

| Parameter | Applies to | What it does | Caveat |
|---|---|---|---|
| `object_hook` | `loads`/`load`/`JSONDecoder` | Transforms each decoded object (§24) | Runs innermost-first |
| `object_pairs_hook` | `loads`/`load`/`JSONDecoder` | Transforms the raw ordered key-value pairs before `dict` construction (§25) | Takes precedence over `object_hook` if both are given |
| `parse_int` | `loads`/`load`/`JSONDecoder` | Overrides integer conversion (§26) | Receives the raw digit text as `str` |
| `parse_float` | `loads`/`load`/`JSONDecoder` | Overrides float conversion (§27) | `Decimal` is the most common override, for precision |
| `parse_constant` | `loads`/`load`/`JSONDecoder` | Overrides `NaN`/`Infinity`/`-Infinity` handling (§28) | Python's default acceptance of these is non-standard JSON |
| `default` | `dumps`/`dump`/`JSONEncoder` | Supplies a serialization rule for otherwise-unsupported types (§21) | `default=str` is convenient but potentially lossy (§21.3) |
| `cls` | All four top-level functions | Supplies a custom `JSONEncoder`/`JSONDecoder` subclass | Use when the same custom rules are needed repeatedly (§22.3) |

### 53.4 Serialization formatting/behavior options

| Parameter | Default | What it does | Caveat |
|---|---|---|---|
| `skipkeys` | `False` | Silently drops unsupported dict keys instead of raising | Real risk of silent data loss (§32.1) |
| `ensure_ascii` | `True` | Escapes non-ASCII characters as `\uXXXX` | `False` is more readable but requires UTF-8-capable output (§30) |
| `check_circular` | `True` | Detects circular references before they crash | Disabling risks an unhandled `RecursionError` instead (§32.2) |
| `allow_nan` | `True` | Permits non-standard `NaN`/`Infinity`/`-Infinity` output | `False` enforces strict standards compliance (§29.3) |
| `indent` | `None` | Pretty-prints with the given indentation | Changes the *default* `separators` value too (§31.3) |
| `separators` | Depends on `indent` (§31.3) | Exact item/key separator strings | Most compact: `(",", ":")` |
| `sort_keys` | `False` | Sorts object keys alphabetically | Improves determinism, but is not full canonicalization (§31.5) |

## 54. Internal Mental Model

### 54.1 What actually happens for `json.dumps()`/`json.loads()`

```
Python object
    ↓  (JSONEncoder walks the object, converting each value per §17's table,
    ↓   calling default() for anything it doesn't recognize, §21-§22)
JSON text (a plain str)
```

```
JSON text
    ↓  (JSONDecoder tokenizes and parses the text, converting each token per
    ↓   §17's table, applying object_hook/parse_float/etc. as configured)
Python object
```

### 54.2 The same picture, extended to files

```python
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
```

```
Python object
    ↓  JSONEncoder (same as above)
JSON text
    ↓  written via the file object's own write() calls (01-reading-and-writing-text-files.md's §17)
    ↓  encoded to bytes per encoding="utf-8"
file on disk
```

```python
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
```

```
file on disk
    ↓  decoded from bytes per encoding="utf-8"
    ↓  read via the file object's own read() calls
JSON text
    ↓  JSONDecoder (same as above)
Python object
```

### 54.3 Where validation belongs, restated one final time

**Nothing in either diagram includes "and now the data is known to be
correct."** Both diagrams end at "a Python object was produced" —
whether that object's *content* is actually valid for your
application (§33.1, §34) is a question these diagrams do not, and
cannot, answer; it is answered only by your own explicit validation
code, run **after** deserialization and **before** anything else
touches the result. This is the single mental model this entire
chapter has been building toward: **parsing produces data; validation
earns trust.**

## 55. Mini-Projects

### Mini Project 1 — JSON Inspector

**Problem statement:** build a tool that reports basic facts about an
unfamiliar JSON file.

**Requirements:** load the file; report its top-level type (object,
array, or something else); if it's an object, list its keys; report
the overall nesting depth; handle invalid JSON gracefully, reporting
the exact line/column (§32.3).

**Expected behavior:** running against a valid, nested file reports a
useful structural summary; running against malformed JSON reports a
precise, actionable error instead of a raw traceback.

**Suggested architecture:** a small function computing nesting depth
recursively, independently testable with plain Python literals — no
file I/O needed to test *that* function in isolation.

**Constraints:** must not assume the top-level value is always an
object — a top-level JSON array or even a bare string is valid JSON.

**Edge cases:** an empty object `{}`; an empty array `[]`; a top-level
JSON value that is just a number or string.

**Testing requirements:** `tmp_path`-based tests (§47) for each edge
case, plus one deliberately malformed file.

**Extension challenge:** report, for an object, each key's value type,
without fully printing large nested values.

### Mini Project 2 — Configuration Loader

**Problem statement:** build a reusable, validated config-loading
utility.

**Requirements:** load JSON (§13–§16); validate required fields and
their types (§34); apply defaults for optional fields (§35.2); convert
the validated result into a clean, flattened internal representation
(§52.1's pattern); raise clear, specific errors naming exactly what was
wrong.

**Expected behavior:** matches §52.1's example in spirit, built by you
against a config shape of your own design.

**Suggested architecture:** separate `_validate` (pure, testable with
plain dicts) from `load_config` (I/O plus orchestration) — exactly
§52.1's shape.

**Constraints:** every validation rule must be testable independently
of file I/O.

**Edge cases:** a config missing an optional section entirely; a
config with a field of the wrong type; a syntactically malformed file.

**Testing requirements:** one test per validation rule, plus at least
one full end-to-end test using `tmp_path`.

**Extension challenge:** add `schema_version` support (§43), rejecting
an unsupported version with a clear error.

### Mini Project 3 — Experiment Metadata Store

**Problem statement:** build a small metadata store for AI/ML
experiment records, building directly on §52.2's example.

**Requirements:** save metadata including a schema version, a
timestamp, model information, and dataset information; serialize
`Path`/`UUID`/`datetime` fields explicitly, via a custom `default=`
function or `JSONEncoder` subclass (§21–§22); use deterministic
formatting (`sort_keys=True`, §31.4) for stable, diffable output; use
the safe write-then-replace update pattern (§42.2); load and validate
metadata, rejecting an unsupported schema version (§43.2); write a
round-trip test proving saved-then-loaded metadata reconstructs
correctly (§48).

**Expected behavior:** matches and extends §52.2's `ExperimentMetadata`
example — you are encouraged to add at least one additional field type
not already shown there (an `Enum` status field, §46.5, is a natural
choice).

**Suggested architecture:** §52.2's three-piece shape — a dataclass, a
custom encode function, and paired save/load functions using matching,
symmetric conversion rules.

**Constraints:** every custom-type conversion must have a clearly
matching, tested inverse.

**Edge cases:** loading a file written by an *older*, unsupported
schema version; a dataset path that doesn't currently exist on disk
(should saving metadata about it still succeed? decide deliberately).

**Testing requirements:** a full round-trip test (§48), a
version-rejection test, and a safe-update test confirming the original
file survives a simulated failure during a save.

**Extension challenge:** support loading a whole directory of
experiment metadata files at once, reporting any that fail validation
without aborting the rest — directly mirroring
[03-csv-files.md](03-csv-files.md)'s §39.2 "quarantine, don't abort"
principle.

### Mini Project 4 — JSON/NDJSON Data Pipeline

**Problem statement:** build a streaming pipeline processing a large
JSON Lines input file.

**Requirements:** read input using §41.3's streaming pattern, never
loading the whole file at once; validate each record against a schema
of your own design; transform valid records (a simple, deliberate
transformation of your choosing); write valid, transformed records to
one JSON Lines output file, and invalid records (with their specific
error reasons) to a separate one; maintain and report summary
statistics (total, valid, rejected counts) — exactly mirroring
[03-csv-files.md](03-csv-files.md)'s §46.2 transaction-ingestion
example, now for JSON Lines instead of CSV.

**Expected behavior:** processes a file with any number of records
without memory growing with the total number of records (peak memory
still depends on the current record and any retained state).

**Suggested architecture:** a streaming reader generator, a pure
validate-and-transform function (testable with plain dicts, no file
I/O), and a thin orchestration function — §52.2's, and
[03-csv-files.md](03-csv-files.md)'s §46.2's, shared three-layer shape.

**Constraints:** must not call `list(...)` on the full input stream at
any point (§40, §44.2).

**Edge cases:** a line that is not valid JSON at all (not just a
records that fails your schema, but genuinely malformed JSON text on
one line); an empty input file; every record being invalid.

**Testing requirements:** the full pattern from §47.6, adapted to your
specific schema, plus a test confirming a single malformed line does
not abort processing of the remaining, valid lines.

**Extension challenge:** support resuming — detecting, on a second run
against the same input, which records have already been processed
successfully (this can be left as a design sketch/discussion rather
than a full implementation, if genuinely out of scope for your current
skill level).

## 56. Coding Exercises

### Level 1 — Foundation

1. Convert a Python `dict` to a JSON string with `json.dumps()`, and
   print it.
2. Convert a JSON string back to a Python `dict` with `json.loads()`.
3. Write a `dict` to a JSON file using `json.dump()`.
4. Read that file back using `json.load()`.
5. Access a nested value (at least two levels deep) from JSON data
   you've loaded.

### Level 2 — Practical

6. Write a function that validates a JSON object has at least two
   specific required keys, raising a clear error if not (§34.2).
7. Handle a missing key safely using `.get()` with a sensible default
   (§19.1).
8. Write a function that catches `json.JSONDecodeError` and re-raises
   a more specific, application-level exception with additional
   context (§32.3).
9. Pretty-print a JSON structure with `indent=2`, and separately
   produce the most compact possible version with `separators=(",", ":")`
   (§31.1–§31.2).
10. Serialize a `dict` with `sort_keys=True`, and write a test proving
    two differently-ordered but logically equal dictionaries produce
    identical output (§31.4).
11. Implement a small configuration-loading function combining
    parsing, validation, and defaults (§35.2).

### Level 3 — Engineering

12. Write a `default=` function that correctly serializes `datetime`
    values via `.isoformat()`, and a matching reconstruction function
    using `datetime.fromisoformat()` (§46.7).
13. Do the same for `Decimal` (§46.6), being careful never to route the
    value through `float()`.
14. Serialize a dataclass using `asdict()` (§46.2), then extend it to
    also handle at least one field of a type `asdict()` alone cannot
    serialize (§46.3).
15. Implement `schema_version` checking (§43.2) for a config or
    metadata shape of your own design, including a deliberate rejection
    test for an unsupported version.
16. Write a round-trip test (§48) for at least one custom type,
    confirming the reconstructed object is logically equal to the
    original — not merely that no exception was raised.
17. Write a function producing fully deterministic JSON output
    (`sort_keys=True` plus fixed `indent`), and a test proving repeated
    calls on logically-equal-but-differently-ordered input produce
    identical text (§31.4–§31.5).

### Level 4 — Advanced

18. Build a custom `JSONEncoder` subclass (§22.1) handling at least
    three distinct custom types, and use it via `cls=`.
19. Implement `object_hook` (§24) converting decoded JSON objects
    matching a specific shape into instances of a custom class.
20. Implement `object_pairs_hook` (§25) that detects and raises on
    duplicate keys within a single JSON object.
21. Demonstrate `parse_int`, `parse_float`, and `parse_constant` each
    doing something meaningfully different from their defaults (§26–
    §28), in one combined example.
22. Implement JSON Lines reading and writing (§41.3) for a dataset of
    your choosing, and a streaming transformation over it that never
    materializes the full dataset in memory.
23. Implement the safe atomic JSON update pattern (§42.2), with a test
    simulating a failure partway through the write step, confirming
    the original file is left untouched.

## 57. Debugging Exercises

Each snippet below is broken. Diagnose using §49's workflow before
reading the corrected version.

**1. Invalid JSON syntax.**
```python
text = "{'name': 'Alice'}"
data = json.loads(text)
```
*Diagnose:* what does the resulting `JSONDecodeError` say, and why
(§5.2)? *Corrected:* use double quotes: `'{"name": "Alice"}'`.

**2. Wrong quote type — a variant.**
```python
text = '{"name": "Alice", "active": True}'
data = json.loads(text)
```
*Diagnose:* which specific token is invalid here (§5.3)? *Corrected:*
`true`, lowercase.

**3. A trailing comma.**
```python
text = '["a", "b", "c",]'
data = json.loads(text)
```
*Diagnose:* what does the error position point at? *Corrected:*
remove the final comma.

**4. `load` vs. `loads` confusion.**
```python
text = '{"name": "Alice"}'
data = json.load(text)
```
*Diagnose:* what does the resulting exception say about the type
`json.load()` expected (§16.2)? *Corrected:* `json.loads(text)`.

**5. `dump` vs. `dumps` confusion.**
```python
data = {"name": "Alice"}
with open("out.json", "w", encoding="utf-8") as f:
    text = json.dumps(data, f)
```
*Diagnose:* what does `json.dumps()`'s actual signature (§10.1) say
about a second positional argument? *Corrected:* `json.dump(data, f)`.

**6. Incorrect file handling.**
```python
with open("config.json") as f:
    data = json.load(f)
```
*Diagnose:* what's missing (§13.2)? *Corrected:* add
`encoding="utf-8"`.

**7. A Unicode problem.**
```python
data = {"language": "বাংলা"}
print(json.dumps(data))
```
*Diagnose:* is the output actually *wrong*, or simply not what was
expected (§30.1)? *Corrected:* not a bug at all — `ensure_ascii=False`
if the escaped form is genuinely undesired.

**8. An unsupported Python type.**
```python
json.dumps({"id": uuid4()})
```
*Diagnose:* what does the resulting `TypeError` name (§17.3, §21.1)?
*Corrected:* `json.dumps({"id": str(uuid4())})`, or a proper `default=`
function.

**9. A circular reference.**
```python
node = {"name": "root"}
node["parent"] = node
json.dumps(node)
```
*Diagnose:* what does §32.2 say about why this specifically
cannot be represented in JSON at all (§32.2)? *Corrected:* redesign
the data to avoid the cycle (e.g. store an ID reference instead of the
actual parent object).

**10. An invalid custom encoder.**
```python
class BrokenEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        # missing: no fallback for anything else!
```
*Diagnose:* what happens when this encoder encounters a type it does
not explicitly check for (§22.1)? *Corrected:* add
`return super().default(obj)` as the final line — without it, `default()`
falls off the end and returns `None`, so unsupported objects silently
become `null` instead of the standard encoder raising `TypeError`.

**11. A wrong `object_hook`.**
```python
def hook(obj):
    return obj["name"]   # assumes EVERY decoded object has a "name" key


json.loads('{"outer": {"inner": {"x": 1}}}', object_hook=hook)
```
*Diagnose:* what happens for the innermost object, `{"x": 1}`, which
has no `"name"` key at all (§24.1)? *Corrected:* check for the key's
presence first, and return `obj` unchanged otherwise.

**12. Incorrect `Decimal` handling.**
```python
from decimal import Decimal

price = Decimal("19.99")
json.dumps({"price": float(price)})
```
*Diagnose:* what did routing through `float()` before serialization
risk (§46.6)? *Corrected:* serialize via `str(price)` instead, never
`float(price)`.

**13. Incorrect `datetime` handling.**
```python
dt = datetime.fromisoformat("2026-09-21T14:00:00")
recovered = datetime.strptime(dt.isoformat(), "%Y-%m-%d")   # wrong format string!
```
*Diagnose:* does `"%Y-%m-%d"` actually match the full ISO 8601 text
`.isoformat()` produced (§46.7)? *Corrected:* use
`datetime.fromisoformat(text)` for the reverse conversion, which is
built specifically to match `.isoformat()`'s own output.

**14. A schema-validation failure, silently ignored.**
```python
def load_config(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
```
*Diagnose:* what real, specific problems does this silently hide
(§32.3, §50 mistake 11)? *Corrected:* catch `json.JSONDecodeError`
specifically, and validate the successfully-parsed result separately
(§34) rather than assuming any dict that comes back is automatically
correct.

## 58. Interview Questions

Beginner:
1. What is JSON? (§3.2)
2. What's the difference between JSON and a Python `dict`? (§6)
3. What is serialization? What is deserialization? (§7.2)
4. `dump` vs. `dumps` — what's the difference? (§16)
5. `load` vs. `loads` — what's the difference? (§16)
6. Why does JSON use lowercase `true`/`false`/`null` instead of
   Python's capitalized versions? (§5.1, §6.1)

Intermediate:
7. What is `json.JSONDecodeError`, and what information does it give
   you? (§32.3)
8. What does `ensure_ascii` control? (§30)
9. What does `sort_keys` do, and why is it useful? (§31.4)
10. What is `default=` for, and why can `default=str` be risky? (§21)
11. What is `json.JSONEncoder`? (§22)
12. What is `json.JSONDecoder`, and when would you use it directly
    instead of `json.loads()`? (§23)
13. What is `object_hook`? (§24)
14. What is `object_pairs_hook`, and how does it differ from
    `object_hook`? (§25)
15. What is `parse_float`, and why might you set it to `Decimal`?
    (§27)
16. Why might financial code prefer `Decimal` over `float` for JSON
    numbers? (§27.3)
17. What is `check_circular`? (§32.2)
18. What is `allow_nan`? (§29.3)
19. What does "schema validation" mean, and how does it differ from
    checking that JSON parses successfully? (§33)

Advanced/production-oriented:
20. How would you serialize a `datetime` to JSON, and reconstruct it
    afterward? (§46.7)
21. How would you serialize a dataclass containing fields `asdict()`
    alone cannot handle? (§46.2–§46.3)
22. How would you process a JSON file too large to comfortably load
    into memory at once? (§40)
23. What is NDJSON/JSON Lines, and why does it solve a problem plain
    JSON documents cannot? (§41)
24. How would you design a production JSON ingestion pipeline, at a
    high level? (§52.2, §55 Mini Project 4)
25. How would you safely handle JSON produced by an AI model, before
    acting on it? (§38.3)

Scenario-based:
26. A teammate's code works for most config files but crashes with
    `KeyError` on files produced by an older version of the
    application. What's the most likely cause, and what would you add
    to prevent it going forward? (§43)
27. You need to compare two JSON files for meaningful equality in a
    test, but naive string comparison keeps failing due to key
    ordering. What would you do? (§31.4–§31.5, §48.2)
28. A system you're integrating with occasionally sends numbers as
    JSON strings instead of JSON numbers (`"30"` instead of `30`).
    What does this tell you about validating external JSON, and how
    would you handle it? (§33, §34)

## 59. Knowledge Check

**A. Conceptual**
1. In your own words, explain why "JSON parsed successfully" and "this
   data is safe/correct to use" are two different claims.
2. Explain why a Python `tuple` cannot be distinguished from a `list`
   after a JSON round trip.

**B. Code-reading**
3. What does the following print, and why?
```python
print(json.dumps({"b": 1, "a": 2}))
print(json.dumps({"b": 1, "a": 2}, sort_keys=True))
```

**C. Predict-the-output**
4. What does `json.loads('{"x": 1, "y": 1.0}')` produce, in terms of
   the Python *types* of each value?

**D. API-selection**
5. You have a string already in memory containing JSON text. Which
   function do you use to parse it?
6. You need every occurrence of a duplicated JSON key, not just the
   last one. Which parameter do you reach for?

**E. Debugging**
7. `json.loads()` raises `JSONDecodeError: Expecting ',' delimiter`.
   What are the two most likely causes, syntactically?

**F. Serialization**
8. Why does `json.dumps({"price": Decimal("19.99")})` fail, and what
   are two different ways to fix it — one quick but lossy, one
   deliberate and precise?

**G. Validation**
9. Why is `{"age": "hello"}` a poor example of "invalid JSON," even
   though it clearly represents bad data?

**H. Security**
10. Why is `eval()` never an acceptable substitute for `json.loads()`,
    even for JSON you believe comes from a trusted source?

**I. Performance**
11. Why can't a single, large JSON *document* be streamed the way a
    JSON *Lines* file can?

**J. Production-design**
12. In an ingestion pipeline processing JSON Lines input, why should
    one malformed line ideally not abort processing of the rest of the
    file?

---

**Answer key**

1. Successful parsing (§33.1) only confirms the *text* was
   syntactically well-formed JSON — it says nothing about whether the
   resulting *data* is complete, correctly typed, or semantically
   sensible for your application; that requires separate, explicit
   schema validation (§34).
2. JSON has no array/tuple distinction at all — both a Python `list`
   and a Python `tuple` serialize to the identical JSON array syntax
   (§6.2, §17.2), and every JSON array always decodes back to a `list`
   — there is no information in the JSON text itself that could tell
   the decoder "this was originally a tuple."
3. `{"b": 1, "a": 2}` then `{"a": 2, "b": 1}` — the first preserves
   insertion order (the default); the second sorts keys alphabetically
   (§31.4).
4. `{'x': 1, 'y': 1.0}` — `x`'s value (`1`, no decimal point) becomes
   Python `int`; `y`'s value (`1.0`, has a decimal point) becomes
   Python `float`, even though they are mathematically equal (§6.3,
   §17.1).
5. `json.loads()` — it parses a `str` already in memory; `json.load()`
   would instead expect an open file object (§16).
6. `object_pairs_hook` — it receives every key-value pair in original
   order, including duplicates, before they are ever collapsed into a
   `dict` (§25.1–§25.2).
7. A missing comma between two items, or an extra comma left in after
   removing an item (a trailing comma, §5.1) — both surface as this
   same "expecting a delimiter" class of error.
8. It fails because `Decimal` has no built-in JSON mapping (§17.3,
   §46.6). Quick-but-lossy: `default=str` or `float(value)` (`float()`
   specifically risks reintroducing precision error, exactly what
   `Decimal` exists to avoid). Deliberate-and-precise: an explicit
   `default=` function converting `Decimal` to `str(value)` — preserving
   the exact digit text — paired with `parse_float=Decimal` on the
   decode side (§27.2) to reconstruct it correctly.
9. It is a poor example of "invalid JSON" because it is not invalid at
   all — `{"age": "hello"}` is perfectly well-formed, syntactically
   valid JSON; what's wrong with it is purely a matter of application-
   level *semantics* (an age should presumably be numeric), which is
   exactly §33.2's distinction between syntax validation and schema
   validation.
10. `eval()` executes the given text as arbitrary Python code, not as
    a restricted data format — even "trusted" input can, through a
    supply-chain compromise, a bug elsewhere, or simple human error,
    end up containing something other than what you expect; `json.loads()`
    (without custom hooks) produces only Python representations of
    JSON's value types, with no code-execution capability at all, regardless of what the input actually
    contains (§39.3).
11. A JSON document's overall structure — where a given array or
    object actually ends — is only fully determinable once the entire
    text has been parsed, because JSON's brackets/braces must all
    correctly nest and close; JSON Lines sidesteps this entirely by
    making each *line* its own complete, independent JSON value, so
    nothing about one line's structure depends on any other line
    (§40.1, §41.2).
12. A single malformed record is very often an isolated data-quality
    problem, not evidence the *entire* file is untrustworthy —
    aborting the whole run discards potentially enormous amounts of
    good, usable data over one bad line, and gives operators far less
    specific, actionable information than a report naming exactly
    which line failed and why — directly the same principle
    [03-csv-files.md](03-csv-files.md)'s §24.3 already established for
    CSV row-level failures.

## 60. Production Checklist

**Input**
- [ ] JSON syntax is validated, with `json.JSONDecodeError` handled
      explicitly, not swallowed (§32.3, §50 mistake 11).
- [ ] File encoding is known and specified explicitly (§13.2).
- [ ] All incoming JSON is treated as untrusted input, regardless of
      its apparent source (§33.1, §39.1).

**Schema**
- [ ] Required fields are validated (§34.2).
- [ ] Types are validated, not assumed (§34.2, §50 mistake 16).
- [ ] Semantic/business rules beyond bare type-correctness are
      validated where relevant.
- [ ] Schema version is validated, and unsupported versions are
      rejected explicitly (§43.2).

**Serialization**
- [ ] Every non-JSON-native type in use has an explicit, deliberate
      serialization rule — not a blanket `default=str` for data meant
      to be reliably reconstructed (§21.3–§21.4, §46).
- [ ] Deterministic formatting (`sort_keys=True`) is used where stable
      diffs, tests, or caching depend on it (§31.4).
- [ ] No accidental data loss occurs from `skipkeys=True` used without
      a specific, documented reason (§32.1).

**Error handling**
- [ ] `json.JSONDecodeError` is caught specifically, with useful
      diagnostic context preserved (`.lineno`/`.colno`/`.pos`, §32.3).
- [ ] Individually invalid records are handled deliberately (rejected
      and reported, or fixed), never silently dropped (§55 Mini
      Project 4).

**Security**
- [ ] `eval()` is never used to parse JSON, under any circumstance
      (§39.3).
- [ ] Resource limits (payload size, nesting depth) are considered for
      any endpoint or pipeline accepting JSON from an untrusted source
      (§39.2).
- [ ] Deep nesting and huge payloads/arrays/strings/numbers are
      considered explicitly, not assumed to be harmless (§39.2).
- [ ] AI-generated JSON is validated exactly like any other untrusted
      JSON source, never trusted merely because it parsed successfully
      (§38.3).

**Performance**
- [ ] Unnecessary repeated serialization/deserialization of the same
      data is avoided (§44.1).
- [ ] A deliberate strategy (plain `json.load()` vs. JSON Lines
      streaming) is chosen based on actual data size, not by default
      (§40.3, §44.2).
- [ ] NDJSON is considered specifically for genuinely large,
      streamable workloads (§41).

**Testing**
- [ ] Valid and invalid JSON are both tested (§47.2).
- [ ] Edge cases — empty objects/arrays, missing keys, `null` values —
      are tested (§47.3).
- [ ] Unicode and special characters are tested (§47.4).
- [ ] Custom-type serialization is tested via full round trips, with
      matching, symmetric conversion rules on both sides (§47.5, §48).
- [ ] Schema-version mismatches are tested explicitly (§47.6).

**Reliability**
- [ ] The safe write-then-replace update pattern is used for
      important JSON files (§42.2).
- [ ] Versioning is in place for any JSON shape expected to evolve
      over time (§43).
- [ ] A backward-compatibility/migration strategy exists for reading
      data written by older schema versions (§43.2).

## 61. Final Mastery Checklist

You should be able to confidently say:

- [ ] I understand what JSON is, and why it became widely used.
- [ ] I understand the JSON data model — objects, arrays, strings,
      numbers, booleans, and null.
- [ ] I understand objects and arrays precisely, including nesting.
- [ ] I understand JSON's primitive value types.
- [ ] I understand JSON's exact syntax rules, including what makes
      text invalid JSON.
- [ ] I understand the precise difference between JSON and Python
      dictionaries (`True`/`true`, `None`/`null`, quoting, and more).
- [ ] I understand serialization and deserialization as distinct,
      deliberate operations.
- [ ] I can use `json.dumps()`, `json.loads()`, `json.dump()`, and
      `json.load()` correctly, including their important parameters.
- [ ] I understand the full JSON ↔ Python type mapping, and which
      Python types have no direct JSON equivalent.
- [ ] I can handle nested JSON, and access it safely with `.get()`
      and defensive chaining.
- [ ] I can validate JSON structure, distinguishing syntax validity
      from schema/application validity.
- [ ] I can handle `json.JSONDecodeError` deliberately, using its
      diagnostic attributes.
- [ ] I can serialize custom Python types (`datetime`, `Decimal`,
      `Path`, `Enum`, dataclasses) explicitly and deliberately.
- [ ] I understand `JSONEncoder` and `JSONDecoder`, including when
      direct/custom use is actually warranted.
- [ ] I understand `object_hook`, `object_pairs_hook`, `parse_int`,
      `parse_float`, and `parse_constant`.
- [ ] I understand `ensure_ascii`, `indent`, `separators`, `sort_keys`,
      `skipkeys`, `check_circular`, and `allow_nan`.
- [ ] I understand Unicode handling in JSON output.
- [ ] I understand JSON Lines/NDJSON, and when it solves a problem
      plain JSON documents cannot.
- [ ] I understand the memory limitations of `json.load()` for very
      large documents.
- [ ] I can write reusable, type-hinted JSON utility functions.
- [ ] I can test JSON-processing code with `pytest`, including round-
      trip tests.
- [ ] I can debug JSON failures systematically.
- [ ] I understand JSON-specific security concerns, including why
      `eval()` must never be used.
- [ ] I can design a production-oriented JSON serialization/ingestion
      workflow.
- [ ] I understand JSON's central role in AI/ML systems, and why
      AI-generated JSON still requires the same validation as any
      other untrusted input.

With this foundation in place, you are ready for
[05-encodings-and-newlines.md](05-encodings-and-newlines.md), where the
`encoding="utf-8"` habit this chapter and every prior one in this
module has relied on gets its own full, dedicated treatment.
