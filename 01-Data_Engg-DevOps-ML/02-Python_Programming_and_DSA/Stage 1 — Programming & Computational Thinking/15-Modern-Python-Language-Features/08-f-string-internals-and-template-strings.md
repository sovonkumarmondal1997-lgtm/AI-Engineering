# Lesson 08 — F-String Internals and Template Strings

> **Version policy:** Examples target Python 3.12+. PEP 701 changes are available in Python 3.12. Template string literals (`t"..."`, or *t-strings*) require Python 3.14+. The current validation runtime for this lesson is Python 3.13, so t-string syntax is explained and shown in clearly marked Python 3.14-only blocks; those blocks were not executed here.

## Learning objectives

By the end of this lesson, you should be able to:

- Format values precisely and read the format-spec mini-language.
- Explain PEP 701 and evaluate f-string expressions without assuming they are inert text.
- Use `__format__`, `format`, `str.format`, `format_map`, percent formatting, and logging's lazy formatting appropriately.
- Inspect f-string bytecode while treating bytecode as implementation detail.
- Explain Python 3.14 t-strings and write consumers that deliberately process interpolation values.
- Distinguish interpolation from safe use in SQL, HTML, shells, logs, and LLM prompts.
- Preserve translatable message templates and test output contracts.

## 1. Mental model: formatting is not escaping

A formatting operation converts values into text according to a presentation rule. It does **not** automatically make that text safe for SQL, HTML, shell syntax, a log format, or an LLM prompt. Those are different destination languages with different grammars and trust boundaries.

```python
user = "Ada"
message = f"Hello, {user}!"
print(message)
```

Output:

```text
Hello, Ada!
```

The f-string evaluates its expressions and produces one ordinary `str`. Afterward, the string no longer records which parts were literal text and which parts came from `user`.

### Version guide

| Feature | Version | What matters |
|---|---:|---|
| F-strings (PEP 498) | 3.6 | Runtime expression interpolation into `str`. |
| Debug `=` syntax | 3.8 | `f"{value=}"` includes expression text and representation by default. |
| PEP 701 formal f-string grammar | 3.12 | Same-quote reuse, comments, backslashes and multiline expressions become valid where the embedded Python grammar permits them. |
| `FORMAT_SIMPLE` and `FORMAT_WITH_SPEC` opcodes | 3.13 | CPython implementation details visible through `dis`; not a language-level API. |
| T-strings (PEP 750) | 3.14 | `t"..."` returns a `string.templatelib.Template`, not a `str`. |

## 2. Beginner: f-string fundamentals

### 2.1 Expressions, conversions, and debug syntax

A replacement field has the general shape `{expression[!conversion][:format_spec]}`. The expression is evaluated at runtime. Common conversions are `!s` (`str()`), `!r` (`repr()`), and `!a` (`ascii()`).

```python
name = "Ana"
items = ["tea", "cake"]
print(f"Hello {name}!")
print(f"items={items!r}")
print(f"{name=}")
print(f"{name=!s:>8}")
```

Output:

```text
Hello Ana!
items=['tea', 'cake']
name='Ana'
name=     Ana
```

`!r` is useful when debugging strings containing whitespace, newlines, or escape characters. The debug form `f"{name=}"` preserves the expression text and uses `repr()` by default; an explicit conversion or format spec changes that behavior.

```python
raw = "line 1\nline 2"
print(f"{raw}")
print(f"{raw!r}")
```

Output:

```text
line 1
line 2
'line 1\nline 2'
```

### 2.2 Format-spec mini-language

The general format-spec shape for many built-in numeric types is:

```text
[[fill]align][sign][z][#][0][width][grouping_option][.precision][type]
```

Not every option applies to every type. Consult the type's `__format__` contract rather than assuming every object supports numeric flags.

| Element | Meaning | Example | Output |
|---|---|---|---|
| Fill and alignment | Pad left, right, or center | `f"{'cat':*^7}"` | `**cat**` |
| Sign | `+`, `-`, or space for positive values | `f"{7:+d}"` | `+7` |
| Alternate form `#` | Prefix for bases; retain decimal point for some formats | `f"{42:#x}"` | `0x2a` |
| Zero padding | Pad numeric field with zeroes | `f"{42:06d}"` | `000042` |
| Width | Minimum field width | `f"{42:6d}"` | `    42` |
| Grouping | `,` or `_` thousands separators | `f"{1234567:,}"` | `1,234,567` |
| Precision | Fractional digits for `f`, significant digits for `g`, max chars for `s` | `f"{3.14159:.2f}"` | `3.14` |
| Type | Presentation such as `d`, `f`, `e`, `g`, `%`, `x`, `b`, `o`, `s` | `f"{255:#x}"` | `0xff` |

Examples:

```python
x, width = 1234567.891, 14
print(f"{x:>{width},.2f}|{x=:.1f}|{42:#06x}|{0.256:.1%}")
print(f"{255:b} {255:o} {255:x} {255:#X}")
print(f"{'left':<8}|{'center':^8}|{'right':>8}")
```

Output:

```text
  1,234,567.89|x=1234567.9|0x002a|25.6%
11111111 377 ff 0XFF
left    | center |   right
```

**Frequent mistakes:** width is a minimum, not truncation; `.2f` rounds for display but does not change the stored number; `,` is not universally valid for every type; and `%` presentation multiplies a numeric value by 100 for display.

### 2.3 Dynamic format specifications

A format specification may contain nested replacement fields, which are evaluated to build the specification itself.

```python
value = 12.34567
width, precision = 10, 3
print(f"{value:{width}.{precision}f}")
```

Output:

```text
    12.346
```

### 2.4 Dates and times

Datetime objects implement formatting with `strftime`-style directives in the format specification.

```python
from datetime import datetime, timezone

stamp = datetime(2026, 10, 17, 9, 5, tzinfo=timezone.utc)
print(f"{stamp:%Y-%m-%d %H:%M %Z}")
```

Output:

```text
2026-10-17 09:05 UTC
```

For machine interchange, use an explicit timezone policy and ISO 8601 where appropriate (`stamp.isoformat()`). A display format should not silently discard timezone information when that information matters.

## 3. Intermediate: PEP 701, runtime semantics, and APIs

### 3.1 PEP 701 in Python 3.12

Before Python 3.12, f-string parsing used special restrictions that made some otherwise-valid Python expressions awkward or invalid. PEP 701 integrated f-strings into the formal grammar. Among other things, embedded expressions can now use the same quote type as the surrounding f-string, contain comments and backslashes where Python grammar allows them, and span multiple lines.

**Python 3.12+ example:**

```python
names = {"first": "Ada", "last": "Lovelace"}
print(f"{names["first"]} {names["last"]}")
print(f"{ '\n'.join(["alpha", "beta"]) }")
```

Output:

```text
Ada Lovelace
alpha
beta
```

The code is legal because the embedded expression is parsed as Python syntax. It still needs to be readable. PEP 701 did not make every arbitrary sequence valid: the expression must remain a valid expression, and comments generally require a multiline expression context so the closing brace is not swallowed by the comment.

### 3.2 Evaluation order and side effects

Replacement expressions are evaluated at runtime from left to right. Calls, property access, indexing, and other expression operations can have side effects or raise exceptions. Do not hide important work inside a formatting expression.

```python
calls = []
def mark(label):
    calls.append(label)
    return label.upper()

result = f"{mark('first')} / {mark('second')}"
print(result)
print(calls)
```

Output:

```text
FIRST / SECOND
['first', 'second']
```

For clearer exception handling, reuse, and testability, compute expensive or side-effecting values before formatting:

```python
def load_customer_name(customer_id):
    return "Ada"  # stand-in for an application/service call

customer_id = 17
customer_name = load_customer_name(customer_id)
summary = f"Customer: {customer_name}"
```

### 3.3 `__format__`, `format()`, `str.format()`, and `format_map()`

The built-in `format(value, spec)` dispatches to `type(value).__format__(value, spec)`. F-strings use the same formatting protocol for fields with format specifications. Custom classes can implement `__format__`, but should document supported specifications and reject invalid ones predictably.

```python
class Celsius:
    def __init__(self, value):
        self.value = value

    def __format__(self, spec):
        if spec in ("", "f"):
            return f"{self.value:.1f} °C"
        if spec == "whole":
            return f"{self.value:.0f} °C"
        raise ValueError(f"unsupported Celsius format: {spec!r}")

c = Celsius(21.56)
print(f"{c}")
print(format(c, "whole"))
print("Reading: {}".format(c))
print("Reading: {temp}".format_map({"temp": c}))
```

Output:

```text
21.6 °C
22 °C
Reading: 21.6 °C
Reading: 21.6 °C
```

`str.format()` resolves named or positional fields from supplied arguments; `format_map(mapping)` resolves named fields from a mapping without first copying it to keyword arguments. Both can access attributes and indexes in field expressions, so **do not apply them to untrusted template strings**. For example, `{0.__class__}` can traverse attributes; format strings are not a safe sandbox.

### 3.4 Percent formatting, bytes, and logging

Percent formatting remains relevant in existing code, bytes interpolation, and Python's logging API. The logging API uses `%`-style placeholders because it can defer interpolation until a record is emitted.

```python
user_id = 42
print("user=%05d" % user_id)
print(b"id=%04d" % 7)
```

Output:

```text
user=00042
b'id=0007'
```

For normal application strings, prefer f-strings when the value should be formatted immediately. For logging, use deferred arguments:

```python
import logging
logger = logging.getLogger("example")
customer_id, count = "cust_42", 3
logger.debug("processed customer_id=%s count=%d", customer_id, count)
```

Avoid:

```python
import logging
logger = logging.getLogger("example")
customer_id, count = "cust_42", 3
logger.debug(f"processed customer_id={customer_id} count={count}")
```

The second form formats eagerly even when DEBUG logging is disabled. Logging's `%` placeholders are not the same as using the `%` operator yourself: the logger can skip interpolation when the record will not be emitted.

### 3.5 Multiline templates and maintainability

Keep templates readable, keep data preparation separate, and avoid large expressions that mix business logic with presentation. `textwrap.dedent()` is useful when a triple-quoted template is indented to match source code.

```python
from textwrap import dedent

name = "Ada"
report = dedent(f"""\
    Report
    ======
    Owner: {name}
    Status: ready
""")
print(report, end="")
```

Output:

```text
Report
======
Owner: Ada
Status: ready
```

For templates that are edited by non-developers or translated, use a dedicated template or localization system rather than scattering complex f-strings through business logic.

### 3.6 Floating-point, `Decimal`, and locale

Binary floats cannot exactly represent many decimal fractions. Formatting controls presentation, not the underlying arithmetic. For monetary calculations, use `Decimal` with a deliberate rounding policy and quantize at the domain boundary when needed.

```python
from decimal import Decimal, ROUND_HALF_UP

amount = Decimal("12.345")
rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
print(f"{amount:.3f}")
print(f"{rounded:.2f}")
print(f"{0.1 + 0.2:.20f}")
```

Output:

```text
12.345
12.35
0.30000000000000004441
```

`locale` can affect locale-aware formatting, but locale is process-global in common Python usage and may be unsafe to switch per request in a concurrent server. For web applications that need multiple locales in one process, consider a library such as Babel and pass the requested locale explicitly. Never assume a decimal comma or grouping symbol based on the server's environment.

With Babel installed, pass the locale explicitly rather than changing process-global locale state:

```python
from decimal import Decimal
from babel.numbers import format_currency

amount = Decimal("1234.50")
print(format_currency(amount, "EUR", locale="de_DE"))
print(format_currency(amount, "EUR", locale="en_US"))
```

Expected output with Babel 2.18.0:

```text
1.234,50 €
€1,234.50
```

The first line contains a non-breaking space before the euro symbol. Currency placement and separators are locale data, so pin and test the localization library/data version when output is a strict external contract.

### 3.7 Prompt templates: f-strings, `string.Template`, and Jinja2

F-strings are convenient for developer-owned templates. `string.Template` provides a simpler `$name` substitution syntax, which can be easier when braces are meaningful in the content. Jinja2 provides richer template logic and escaping controls, but its autoescaping must be configured for the destination format (for example, HTML) and does not make arbitrary prompt content trustworthy.

| Tool | Best fit | Important boundary |
|---|---|---|
| f-string | Small, code-owned, immediate formatting | Produces plain text; no automatic escaping or provenance. |
| `string.Template` | Simple placeholder substitution, often user-editable text | Substitution is not sandboxing or destination-language escaping. |
| Jinja2 | Larger templates, inheritance, filters, HTML templates | Configure autoescape correctly; avoid unsafe filters and untrusted template execution. |
| Python 3.14 t-string | Structured static text plus evaluated interpolation values for a consumer | Safe only if the consumer validates and encodes values correctly for the target language. |

For LLM prompts, separate system instructions, user-provided data, and tool outputs structurally where the API supports it. Delimiters in a single string may improve clarity but are not a security boundary; prompt injection is not solved by f-strings, `Template`, or t-strings alone.

Literal braces in f-strings are escaped by doubling them: `f"{{name}}"` produces `{name}`. Do not confuse a literal brace with an interpolation field.

## 4. Advanced: bytecode and runtime inspection

Use `dis` to explore what the current interpreter emits:

```python
import dis

def render(name, amount):
    return f"{name}: {amount:,.2f}"

dis.dis(render)
```

Do not hard-code expected bytecode in application logic or tests. Opcode names, stack effects, and instruction sequences are CPython implementation details that can change between minor versions and even differ by interpreter implementation.

| Runtime | Useful orientation | Caveat |
|---|---|---|
| Python 3.11 and earlier | F-strings commonly disassemble with `FORMAT_VALUE` and `BUILD_STRING`. | Exact sequence varies with expression and version. |
| Python 3.12 | PEP 701 changes parsing/tokenization; common f-string bytecode still includes `FORMAT_VALUE`/`BUILD_STRING`. | Grammar changes do not imply a stable bytecode contract. |
| Python 3.13 | CPython added `CONVERT_VALUE`, `FORMAT_SIMPLE`, and `FORMAT_WITH_SPEC` for f-string conversion/formatting paths. | These are implementation details, not Python language APIs; the emitted sequence depends on the expression and conversion. |
| Python 3.14 | Inspect the actual target interpreter's `dis` output. | Do not infer opcode behavior from another release or rely on an opcode list as a compatibility promise. |

If bytecode matters for a performance investigation, record `sys.version`, `sys.implementation`, the exact benchmark, and the complete disassembly. Measure end-to-end behavior rather than optimizing from opcode names alone. For broader profiling, see the roadmap's profiling/performance modules.

## 5. Python 3.14 t-strings (PEP 750)

> **Python 3.14 only:** the following syntax is not valid on Python 3.13 or earlier.

```python
# Python 3.14 only
from string.templatelib import Template, Interpolation

name = "World"
template = t"Hello {name}!"
print(isinstance(template, Template))
print(isinstance(template, str))
print(template.strings)
print(template.interpolations[0].value)
print(template.interpolations[0].expression)
```

Expected output on Python 3.14:

```text
True
False
('Hello ', '!')
World
name
```

A t-string is not a `str`. It produces a `string.templatelib.Template` containing:

- `strings`: a tuple of static string segments; for N interpolations, there are N+1 segments.
- `interpolations`: a tuple of `Interpolation` objects.
- Each interpolation exposes `value` (already evaluated), `expression` (source expression text), `conversion` (`None`, `"s"`, `"r"`, or `"a"`), and `format_spec` (a string, already evaluated if it contains nested expressions).
- `values`: the tuple of interpolation values.

Expressions are still evaluated eagerly and left to right. T-strings do **not** defer arbitrary Python expression execution. They preserve the separation between static text and interpolation objects *after* evaluating the expressions. The debug `=` form is handled during parsing: for example, `t"{name=}"` contributes `"name="` to the static text and records the interpolation with `conversion == "r"`; a consumer cannot recover a distinct “debug marker” from the interpolation metadata.

```python
# Python 3.14 only
from string.templatelib import Interpolation

who = "Ada"
t = t"Hi {who!r:>8}."
part = t.interpolations[0]
assert t.strings == ("Hi ", ".")
assert part.value == "Ada"
assert part.expression == "who"
assert part.conversion == "r"
assert part.format_spec == ">8"
```

A consumer chooses how to handle each interpolation. It may escape the value, bind it as a parameter, validate its type, or build a non-string structured object. There is no universal automatic conversion that makes every t-string safe.

### 5.1 Example: a deliberately narrow HTML text consumer

> **Python 3.14 only.** This demonstration escapes interpolation values for **HTML text-node content only**. It assumes that the literal template fragments are trusted developer-authored HTML and that interpolations do not occur inside attributes, scripts, styles, URLs, or other contexts. A production HTML renderer should use a mature context-aware template engine.

```python
# Python 3.14 only
from html import escape
from string.templatelib import Template, Interpolation

def html_text(template: Template) -> str:
    parts = []
    for part in template:
        if isinstance(part, Interpolation):
            if part.conversion is not None or part.format_spec:
                raise ValueError("this renderer accepts plain text interpolations only")
            parts.append(escape(str(part.value)))
        else:
            parts.append(part)
    return "".join(parts)

untrusted = "<script>alert('x')</script>"
print(html_text(t"<p>{untrusted}</p>"))
```

Expected output on Python 3.14:

```text
<p>&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;</p>
```

This is an example of a consumer enforcing a specific rendering policy, not a built-in t-string guarantee. It intentionally rejects conversion flags and format specifications instead of silently guessing what they mean. Do not use it for HTML attributes or JavaScript/CSS contexts.

### 5.2 A minimal consumer for display-only text

```python
# Python 3.14 only
from string.templatelib import Template, Interpolation

def render_plain(template: Template) -> str:
    chunks = []
    for part in template:
        if isinstance(part, Interpolation):
            value = part.value
            if part.conversion == "r":
                value = repr(value)
            elif part.conversion == "a":
                value = ascii(value)
            elif part.conversion == "s":
                value = str(value)
            chunks.append(format(value, part.format_spec))
        else:
            chunks.append(part)
    return "".join(chunks)

name = "Ada"
print(render_plain(t"Hello {name}!"))
```

Expected output on Python 3.14:

```text
Hello Ada!
```

This illustrative renderer implements only basic formatting semantics and is intended for plain display. A production consumer must deliberately define behavior for conversion, format specifications, nested templates, types, errors, and output encoding. Do not reuse it for SQL, HTML, or shell commands.

## 6. Security boundaries: safe destination-specific processing

### 6.1 SQL: bind values, never interpolate them into SQL text

**Unsafe pattern (do not use):** building SQL by concatenating or f-string-interpolating user values can change query structure.

```python
# Do not do this:
# sql = f"SELECT * FROM users WHERE name = '{user_input}'"
```

Use the database driver's parameter-binding API instead:

```python
import sqlite3

connection = sqlite3.connect(":memory:")
connection.execute("CREATE TABLE users (name TEXT)")
connection.execute("INSERT INTO users (name) VALUES (?)", ("Ada",))
user_input = "Ada' OR 1=1 --"
rows = connection.execute(
    "SELECT name FROM users WHERE name = ?", (user_input,)
).fetchall()
print(rows)
```

Output:

```text
[]
```

Parameters bind **values**, not SQL identifiers or keywords. If a table or column name must be dynamic, use an allowlist and the database library's identifier-composition API where available; never assume value placeholders can safely substitute identifiers.

A t-string-based SQL library can be designed to convert interpolation values into bound parameters while preserving static SQL fragments. That is a library-specific contract: inspect its API and tests. The t-string itself does not automatically create a parameterized query.

### 6.2 HTML: context-aware escaping

For HTML text content, use a well-tested HTML templating system with autoescaping or an explicit encoder for the correct context. Attribute values, URLs, JavaScript, CSS, and HTML text have different rules; one generic escaping function is not universally correct.

```python
from html import escape

untrusted = "<script>alert('x')</script>"
print(escape(untrusted))
```

Output:

```text
&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;
```

`html.escape()` is appropriate for HTML text/attribute escaping in limited contexts, not a universal sanitizer for JavaScript, CSS, URLs, or arbitrary markup. Prefer context-aware template engines and safe DOM APIs. A t-string HTML consumer must apply the correct contextual escaping to each interpolation and handle any trusted markup as a distinct, explicit type.

### 6.3 Shells: pass argument arrays

Avoid constructing a shell command string from untrusted values. Prefer `subprocess.run([...], shell=False)` and pass each argument separately. Do not run a destructive command just to test formatting.

```python
import subprocess

filename = "report; not-a-shell-command.txt"
# Safe argument separation; this example does not execute a real program.
args = ["/usr/bin/printf", "%s\\n", filename]
print(args)
```

Output:

```text
['/usr/bin/printf', '%s\\n', 'report; not-a-shell-command.txt']
```

The example only displays the argument list; it does not execute it. Use an absolute executable path when appropriate, validate allowed arguments, and set `shell=False` explicitly for clarity. If a shell is genuinely required, shell escaping is platform- and shell-specific; prefer not to build shell text.

### 6.4 Logging: lazy, structured, and redacted

Use parameterized logging calls so formatting can be deferred. Use `extra` for structured fields when your configured formatter or logging pipeline consumes them. Avoid logging credentials, access tokens, secrets, or unnecessary personal data.

```python
import logging

logger = logging.getLogger("billing")
logger.info(
    "payment processed",
    extra={"event": "payment_processed", "payment_id": "pay_123", "amount_cents": 2500},
)
```

`extra` adds attributes to the `LogRecord`; it does not automatically emit JSON or guarantee a particular schema. Configure a JSON formatter/handler or use a structured logging library. Avoid key collisions with standard `LogRecord` attributes and do not assume that every handler serializes custom fields.

### 6.5 Untrusted templates and LLM prompts

Calling `untrusted_template.format(...)` is not safe sandboxing. Format fields may traverse attributes or indexes and invoke formatting behavior. If users can author templates, use a restricted template language with an explicit allowlist of variables and operations, or treat the template as data rather than executable formatting syntax.

For LLM prompts, never merge untrusted instructions and privileged instructions into one undifferentiated string and assume quoting protects the boundary. Prefer separate API message roles, structured input fields, tool permission checks, and validation of model outputs. T-strings can help retain interpolation provenance for a purpose-built prompt builder, but cannot by themselves prevent prompt injection.

## 7. Internationalization (i18n)

F-strings evaluate immediately, before a translation catalog can rearrange placeholders. Avoid this pattern:

```python
# Avoid: the translator receives an already formatted English sentence.
# translated = gettext(f"Hello, {name}")
```

Use a translatable template with named placeholders and interpolate after translation:

```python
from gettext import NullTranslations

translations = NullTranslations()
gettext = translations.gettext
name = "Ada"
message_template = gettext("Hello, %(name)s!")
message = message_template % {"name": name}
print(message)
```

Output with `NullTranslations`:

```text
Hello, Ada!
```

Named placeholders allow translators to reorder fields. For pluralization, use `ngettext(singular, plural, n)` and keep the count available to the translated template. A minimal standard-library example is:

```python
from gettext import NullTranslations

translations = NullTranslations()
ngettext = translations.ngettext
count = 2
unit_template = ngettext("%(count)d file", "%(count)d files", count)
print(unit_template % {"count": count})
```

Output with `NullTranslations`:

```text
2 files
```

For complex localization, use a message-format system that supports the application's plural, gender, and locale requirements. Locale-aware number/date rendering should use the user's selected locale, not a process-global assumption.

## 8. Testing formatted output and linting

Formatting is often an interface: CLI output, reports, email templates, audit logs, and generated prompts may be consumed by people or other systems. Test meaningful output contracts, not incidental implementation details.

```python
def format_total(total_cents: int) -> str:
    return f"${total_cents / 100:,.2f}"

assert format_total(123456) == "$1,234.56"
```

For larger outputs, use golden-file or snapshot tests when the full output is intentionally stable. Normalize nondeterministic fields such as timestamps, random IDs, paths, and platform-specific line endings before comparing. A snapshot test should not merely approve a changed output without reviewing what changed.

Useful Ruff rules mentioned in the roadmap:

- `UP031`: prefer modern formatting over `%` formatting where applicable.
- `UP032`: prefer f-strings over `.format` where applicable.
- `G004`: flags f-strings in logging calls (the logging call should normally use lazy arguments).
- `S608`: flags possible SQL injection through string construction.

Enable and configure rules intentionally; linters provide signals, not proof of security. A suppression should include a clear rationale and a safer design review.

## 9. Practical comparison table

| Approach | Output/result | Strength | Risk or limitation | Good use |
|---|---|---|---|---|
| F-string | `str` | Readable, fast, expressive | Eager evaluation; loses source/value boundaries; no automatic escaping | Developer-owned display text |
| `format()` / `str.format()` | `str` | Reusable format specifications and templates | Untrusted format strings can traverse attributes/indexes | Trusted templates and custom `__format__` |
| `%` operator | `str` or `bytes` depending on left operand | Legacy interoperability and bytes formatting | Older syntax; type/placeholder errors | Legacy code, bytes, narrow compatibility cases |
| Logging `%s` arguments | `LogRecord` rendered by handlers later | Lazy interpolation | Must still avoid sensitive data and unsafe log formats | Application logging |
| `string.Template` | `str` | Simple placeholder syntax | Not a sandbox; no destination escaping | Simple user-editable templates with restricted substitution |
| Jinja2 | Usually `str` or rendered output | Rich templates, filters, inheritance, autoescape support | Configuration/context mistakes; untrusted template execution risks | HTML and larger templates with reviewed configuration |
| Python 3.14 t-string | `Template` | Preserves static segments and interpolation metadata | Evaluates expressions eagerly; consumer must enforce safety | Purpose-built SQL/HTML/prompt/structured-data consumers |
| Database parameter binding | Query plus separate values | Separates SQL structure from values | Does not bind identifiers; driver-specific placeholders | SQL queries |
| Structured logging fields | Structured record/event | Queryable metadata | Needs compatible formatter/collector and redaction | Production observability |

## 10. Common mistakes checklist

- Assuming f-strings escape HTML, SQL, shell arguments, or prompt instructions.
- Using f-strings in `logger.debug()` and paying formatting cost even when disabled.
- Calling `.format()` on user-controlled templates.
- Treating width as truncation or precision as stored-value rounding.
- Using `float` for exact monetary arithmetic without a deliberate policy.
- Using `locale.setlocale()` per request in a concurrent process.
- Treating PEP 701 as a new interpolation model rather than a grammar change.
- Assuming bytecode opcodes are stable across Python versions.
- Treating a t-string as an already-rendered string, or assuming it automatically sanitizes values.
- Assuming `extra=` automatically emits JSON.
- Formatting translatable sentences before calling `gettext`.
- Approving snapshot changes without inspecting the diff.

## 11. Exercises

### Exercise 1 — formatting mini-language

Given `price = 1234.5`, produce `$1,234.50` with a single f-string. Then show the same number with a leading sign and width 12.

### Exercise 2 — evaluation order

Write a function that appends its label to a list and returns the label. Use two calls in one f-string and explain the order in which they run.

### Exercise 3 — PEP 701

Explain why `f"{record["name"]}"` is valid in Python 3.12+ but rejected by older versions, and give one maintainability reason to keep embedded expressions short anyway.

### Exercise 4 — logging

Rewrite `logger.info(f"loaded {count} records for {tenant}")` to use lazy formatting. Name one thing that lazy formatting does not protect against.

### Exercise 5 — SQL security

Explain why SQL value placeholders cannot generally be used for table names. Describe how to handle a dynamic table name safely.

### Exercise 6 — t-strings (Python 3.14)

For `t"Hi {name!r:>8}!"`, identify the static strings, interpolation value, expression, conversion, and format specification. Explain why the consumer still must decide how to render it.

### Exercise 7 — i18n

Explain why `gettext(f"Hello, {name}")` is a poor translation pattern and rewrite it with a named placeholder.

### Exercise 8 — snapshots

List three nondeterministic elements you might normalize before comparing a generated report against a golden file.

## 12. Exercise solutions

### Solution 1

```python
price = 1234.5
print(f"${price:,.2f}")
print(f"{price:+12,.2f}")
```

Output:

```text
$1,234.50
   +1,234.50
```

### Solution 2

```python
order = []
def call(label):
    order.append(label)
    return label

text = f"{call('A')}-{call('B')}"
assert text == "A-B"
assert order == ["A", "B"]
```

The left replacement field is evaluated before the right one.

### Solution 3

PEP 701 made f-string expressions use the formal Python grammar, lifting the old quote-reuse restriction. Keep embedded expressions concise so that errors, side effects, and business logic are easy to inspect and test.

### Solution 4

```python
import logging
logger = logging.getLogger("example")
count, tenant = 3, "tenant_1"
logger.info("loaded %d records for %s", count, tenant)
```

This avoids eager interpolation when the message is filtered out. It does not redact secrets, prevent log injection through unsafe downstream rendering, or make sensitive data safe to log.

### Solution 5

Placeholders represent values, not SQL grammar tokens. For dynamic identifiers, map a user choice to a fixed allowlist of known identifiers and use the driver's identifier-quoting/composition API where available.

### Solution 6

Python 3.14 only: the static strings are `("Hi ", "!")`; the interpolation has the evaluated value of `name`, expression text `name`, conversion `"r"`, and format spec `">8"`. A consumer determines whether to honor conversion/specification and how to encode the value for its destination.

### Solution 7

The f-string is evaluated before gettext sees it, so the catalog cannot reliably identify or reorder the variable placeholder. Use `gettext("Hello, %(name)s") % {"name": name}` or a localization library with named fields.

### Solution 8

Examples include timestamps, generated IDs, temporary file paths, environment-dependent paths, random values, locale-specific output, and platform line endings. Normalize only values that are intentionally nondeterministic; do not hide real regressions.

## 13. Integrated case study: a safe billing report

This case study combines exact money, a stable display format, lazy structured logging, SQL parameter binding, and a testable report. It deliberately avoids building SQL or shell command strings from data.

```python
from decimal import Decimal, ROUND_HALF_UP
import logging
import sqlite3

logger = logging.getLogger("billing.report")


def cents(amount: Decimal) -> int:
    rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(rounded * 100)


def render_report(customer: str, amount_cents: int) -> str:
    amount = Decimal(amount_cents) / Decimal(100)
    return f"Customer: {customer}\nTotal: ${amount:,.2f}"


def find_invoice(connection: sqlite3.Connection, invoice_id: str):
    return connection.execute(
        "SELECT invoice_id, amount_cents FROM invoices WHERE invoice_id = ?",
        (invoice_id,),
    ).fetchone()


amount = Decimal("19.995")
amount_cents = cents(amount)
report = render_report("Ada", amount_cents)
logger.info("billing report rendered", extra={"event": "billing_report_rendered", "amount_cents": amount_cents})
print(report)
assert amount_cents == 2000
assert report == "Customer: Ada\nTotal: $20.00"

connection = sqlite3.connect(":memory:")
connection.execute("CREATE TABLE invoices (invoice_id TEXT, amount_cents INTEGER)")
connection.execute("INSERT INTO invoices VALUES (?, ?)", ("inv_1", amount_cents))
assert find_invoice(connection, "inv_1") == ("inv_1", 2000)
```

Output:

```text
Customer: Ada
Total: $20.00
```

**Design notes:** rounding policy is explicit; the report is a pure function with a golden assertion; SQL values are bound separately; logging uses deferred message formatting and structured fields; and no shell command is constructed. In a production service, define the currency and rounding policy as part of the domain model, configure a structured logging handler, apply authorization before querying invoices, and ensure customer data is handled according to privacy policy.

### Optional Python 3.14 extension

A t-string consumer could accept a report template and return a structured event or rendered report, but it must define a policy for each interpolation. For SQL, use a reviewed consumer that binds values through the driver. For HTML, use context-aware escaping. For logging, prefer passing structured fields to the logging API. Do not replace these established interfaces with a generic `str(template)` conversion.

## 14. Self-check

1. What does `f"{x=}"` print, and what conversion does it use by default?
2. Which grammar restrictions did PEP 701 lift in Python 3.12?
3. Why is `logger.debug(f"value={value}")` eager while `logger.debug("value=%s", value)` can defer formatting?
4. What does `__format__` control?
5. Why is `str.format()` unsafe as a sandbox for user-supplied templates?
6. What is the result type of a t-string in Python 3.14, and when are its expressions evaluated?
7. What must a t-string SQL consumer do to prevent SQL injection?
8. Why should translations use named placeholders and plural-aware APIs?

### Self-check answers

1. It includes the expression text and `repr(x)` by default, for example `x='hello'` when `x` is a string.
2. Same-quote reuse, multiline expressions, comments, and backslashes are allowed when the embedded Python grammar permits them.
3. F-strings execute immediately at the call site; logging can defer `%`-style interpolation until the record is emitted.
4. It defines how an object is converted to a string for a given format specification.
5. Format fields can access attributes and indexes and invoke formatting behavior; formatting is not a sandbox.
6. A `string.templatelib.Template`; expressions are evaluated eagerly from left to right.
7. Preserve SQL structure and bind each value using the database driver's parameter API; validate/allowlist identifiers separately.
8. Translators may need to reorder fields, and plural forms depend on count and locale.

## References

- Module roadmap, Lesson 08: required scope and common mistakes for this lesson.
- [PEP 701 — Syntactic formalization of f-strings](https://peps.python.org/pep-0701/)
- [PEP 750 — Template Strings](https://peps.python.org/pep-0750/)
- [Python `string.templatelib` documentation (3.14)](https://docs.python.org/3.14/library/string.templatelib.html)
- [Python `dis` documentation](https://docs.python.org/3/library/dis.html)
- [Python logging documentation](https://docs.python.org/3/library/logging.html)
- [Python `gettext` documentation](https://docs.python.org/3/library/gettext.html)
- [Python `sqlite3` documentation](https://docs.python.org/3/library/sqlite3.html)
