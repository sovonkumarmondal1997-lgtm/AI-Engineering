# Untrusted Input and Injection Risks

**Stage 1 — Programming & Computational Thinking**  
**Module 22 — Secure Python Coding**  
**Lesson 01 of 08** · Basic foundations, intermediate injection families, advanced review and testing

> **Lesson boundary:** This lesson establishes the shared mindset for injection risks. It gives only orientation-level coverage of command injection and path traversal; study their full mitigations in Lesson 04, `04-shell-and-subprocess-injection.md`, and Lesson 03, `03-path-traversal-and-safe-file-handling.md`, respectively. LLM prompt injection is a preview of the later AI security stage, not a complete treatment.

## 1. Learning outcomes

By the end, you should be able to:

1. Identify trust boundaries and explain how data becomes instructions at an injection sink.
2. Trace an input through source, parsing, validation, transformation and sink to its potential impact.
3. Use parameterized SQL for values and a strict allow-list for dynamic SQL identifiers.
4. Recognize the major injection families and select the sink-specific safe API or control.
5. Parse inputs into exact types, enforce ranges and resource limits, normalize consistently, and reject ambiguous data.
6. Design safe errors, structured logs, context-aware output handling and least-privilege database access.
7. Test defensive behavior with malicious-payload tables, regression tests and fuzzing.
8. Review data-pipeline entry points—files, CSV headers, JSON keys, partition values, object-store keys and derived table names—with a threat-model mindset.

## 2. Prerequisites and recall

This lesson assumes basic Python strings, collections, functions and exceptions; reading and writing text/CSV/JSON; logging; parameter passing; and basic testing. The roadmap also connects this lesson to:

- Module 1.3: exceptions, validation and useful errors.
- Module 1.5 and 1.10: environment configuration, logging and safe writes.
- Module 1.7 and 1.16: tests, regression tests and fuzzing.
- Module 1.12: dynamic execution (`eval`/`exec`) and AST allow-lists.
- Module 1.13: subprocesses, temporary files, hashing and HTTP basics.
- Module 1.14: Unicode, regular-expression denial of service (ReDoS), decompression and serialization risks.
- Module 1.18: dependency and supply-chain awareness.
- Stage 0: operating-system permissions, processes and networking.

### Prerequisite recall

- **Parsing** turns raw representation into a meaningful value, such as `"42"` into integer `42`.
- **Validation** decides whether that parsed value satisfies the application's contract.
- **Encoding** represents data safely for a particular output context. HTML encoding is not SQL parameterization, and neither is shell argument separation.
- **Exception handling** lets a program reject invalid input without exposing implementation details.
- **Regression test**: a test added to ensure a previously discovered defect does not return.
- **Least privilege**: a component receives only the permissions it needs.
- **Fuzzing**: supplying many generated or mutated inputs to find crashes, invariant violations or unexpected behavior.

If any term is unfamiliar, review the related earlier module before treating a security check as a mechanical recipe.

## 3. Beginner foundation: trust boundaries and injection mechanics

### 3.1 What is a trust boundary?

A **trust boundary** is a point where data crosses from one security domain into another. A web request entering an API, a CSV arriving in object storage, a database row written by another service, or a model response passed to a tool are all examples.

Treat these as untrusted until the application has established a reason to trust a specific property:

- User-controlled form fields, query parameters, headers and uploaded files.
- HTTP response bodies from third-party APIs.
- Environment variables and configuration files writable by other users or deployment systems.
- Database values originally supplied by users or other services.
- Filenames, CSV headers, JSON keys, object-store keys and partition values.
- Error messages or output from external processes.
- Model-generated text and tool output.

“Internal” does not automatically mean “trusted.” A shared drive, internal API, staging database or company-produced CSV can contain attacker-controlled data, stale data or mistakes.

Trust is **property-specific**. A validated integer may be safe as a row limit but still be inappropriate as a database identifier or log field. A string that is safe to display as HTML text may be unsafe inside JavaScript or a URL.

### 3.2 Data versus instructions

An injection flaw occurs when an interpreter or parser treats attacker-controlled **data** as part of its **instruction language**.

For example, a SQL query has a program-like structure:

```sql
SELECT id FROM users WHERE name = ?
```

The placeholder marks a value position. The database driver sends the value separately, so quote characters in the value remain data. By contrast, constructing SQL by joining strings allows the value to alter the query's syntax.

The same principle applies to shell commands, templates, HTML, LDAP filters, regular expressions and other languages. Each has its own grammar and safe interface.

### 3.3 A useful mental model

Remember three rules:

1. **Validate early:** at the boundary, parse raw input into a narrow type and enforce the application's contract.
2. **Keep data separate from instructions:** use parameter binding, argument arrays, fixed templates and structured APIs.
3. **Encode at the sink:** when data must be embedded in an output language, use the encoder designed for that exact context.

“Validate early, encode late” is not a license to skip validation. Validation answers “is this value allowed here?”; output encoding or parameterization answers “can this value change the meaning of the output program?” They solve different problems.

A deny-list such as “remove apostrophes” cannot enumerate every syntax feature, encoding, parser behavior or future change. Prefer a positive contract: accept only values that fit the intended type, range, length and allowed choices.

## 4. Injection lifecycle: source → parsing/validation → transformation → sink → impact

| Stage | Meaning | Review question |
|---|---|---|
| **Source** | Where input originates | Who can influence it, directly or indirectly? |
| **Parsing** | Convert representation into a typed value | Is parsing strict, bounded and unambiguous? |
| **Validation** | Enforce allowed values and business rules | Is the accepted set explicit? |
| **Transformation** | Normalize, format, concatenate or derive values | Does transformation change what the validator checked? |
| **Sink** | The interpreter or system receiving the value | Is there a parameterized or structured API? |
| **Impact** | What happens if the value changes meaning | Could it disclose data, modify state, execute code, forge records or exhaust resources? |

Consider a report API that receives `limit="100"`:

1. Source: query string controlled by a caller.
2. Parsing: parse to an integer.
3. Validation: require `1 <= limit <= 500`.
4. Transformation: pass the integer to a database driver as a bound value.
5. Sink: SQL query.
6. Impact if mishandled: an attacker might change query structure or request excessive work.

A common advanced defect is **validate one representation, use another**. For example, validate a raw path, then URL-decode it and use the decoded path. Another is to validate a value at ingestion, store it, and later interpolate it into a query. The later use is a new sink and needs the same discipline.

## 5. Main injection families

The examples below are deliberately tiny and local. Every vulnerable example is labelled **VULNERABLE / LAB ONLY** and immediately paired with a safer pattern. Never point these examples at systems you do not own or have permission to test.

### 5.1 SQL injection

**Definition.** SQL injection occurs when data changes the structure or meaning of a SQL statement.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — do not use in application code.
query = f"SELECT id FROM users WHERE name = '{name}'"
cursor.execute(query)
```

If `name` contains SQL syntax, the query text itself changes. The problem is not the particular payload; it is that the value is being used to construct SQL grammar.

**Safe alternative:**

```python
cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
```

The `?` placeholder is for SQLite's DB-API parameter style. Other drivers may use `%s`, `%(name)s` or another documented style; follow the driver, never interpolate the value yourself.

Dynamic identifiers such as a column or table name usually cannot be represented by a value placeholder because SQL parses identifiers as part of statement structure. Map external choices to fixed identifiers:

```python
ALLOWED_SORT_COLUMNS = {
    "name": "name",
    "created": "created_at",
}

def list_users(cursor, sort: str) -> list[tuple]:
    try:
        column = ALLOWED_SORT_COLUMNS[sort]
    except KeyError:
        raise ValueError("Unsupported sort field") from None
    cursor.execute(f"SELECT id, name FROM users ORDER BY {column}")
    return cursor.fetchall()
```

The f-string is acceptable here only because `column` comes from a closed, application-owned mapping. Do not substitute a user-supplied identifier directly.

**Limits and checklist**

- Parameterization protects values, not arbitrary query structure or business authorization.
- Avoid building `WHERE`, `ORDER BY`, table names or fragments from raw input.
- ORM use is not automatically safe if raw SQL or unsafe expression construction is used.
- SQLAlchemy `text()` can be safe with bind parameters: `text("SELECT ... WHERE id=:id")` plus a separate parameter mapping.
- Stored procedures are not automatically safe; a procedure that concatenates SQL can still be injectable.
- Use a database account with the minimum required permissions, separate migration credentials from application credentials, and use row-level controls where appropriate.
- Ask: “Which bytes become SQL syntax, and which remain bound values?”

### 5.2 Log injection and log forging

**Definition.** Log forging occurs when untrusted input makes log records appear to contain extra or misleading entries, commonly through newline characters or control characters.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — attacker-controlled newline can forge a line.
logger.warning("Login failed for %s", username)
```

The logging call uses formatting rather than string concatenation, but if the output is a plain text formatter and `username` contains line breaks, the rendered output may still be misleading. Parameterized logging prevents eager formatting; it does not automatically neutralize every control character in every formatter or downstream log viewer.

**Safer pattern:** serialize the event as JSON and configure a dedicated handler to emit only the serialized message, without a plain-text prefix:

```python
import json
import logging

logger = logging.getLogger("security_events")
logger.setLevel(logging.WARNING)
logger.propagate = False
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)

def log_login_failure(username: str, request_id: str) -> None:
    record = json.dumps(
        {"event": "login_failed", "username": username, "request_id": request_id},
        ensure_ascii=True,
    )
    logger.warning("%s", record)
```

JSON escapes embedded CR/LF as data, and the message-only formatter emits the JSON object as one physical record. In production, prefer a structured logging formatter that serializes fields at the handler boundary; verify that the configured formatter emits one record and that downstream collectors/viewers preserve JSON semantics. `extra=` alone does not guarantee structured output. Configure the handler once during application startup rather than repeatedly. Do not place secrets, access tokens, passwords, session cookies or unnecessary personal data in logs. For plain-text sinks, encode or visibly replace CR/LF/control characters in untrusted fields.

**Safe errors.** Return a generic message such as `Invalid report request` to the caller. Log diagnostic details on the server with a correlation ID and appropriate access controls. Do not return stack traces, SQL errors, internal paths, credentials or raw exception messages to untrusted clients. Preserve useful details for authorized operators without leaking them to the caller.

**Checklist:** Can one input create multiple visual records? Are fields escaped/serialized by the actual formatter? Are logs searchable without trusting attacker-controlled text? Are secrets and sensitive values redacted?

### 5.3 Command injection — orientation only

**Definition.** Command injection occurs when untrusted data changes a command interpreted by a shell or another command language.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY.
import os
os.system(f"echo {user_value}")
```

**Safer direction:**

```python
import subprocess
subprocess.run(["echo", user_value], check=True, timeout=5, shell=False)
```

An argument list with `shell=False` removes shell parsing, but it does not prevent **argument injection**: a value beginning with `-` may be interpreted as an option by the target program. Validate arguments, use `--` where the executable supports it, map choices to fixed command templates, set timeouts and least privilege, and prefer a library over a subprocess where practical. See Lesson 04 for complete treatment, including environment hardening, platform differences and sandboxing.

**Checklist:** Is a shell involved? Can a value become an option or a second interpreter's code? Are executable, arguments, environment, working directory, time and privileges constrained?

### 5.4 Template injection / server-side template injection (SSTI)

**Definition.** SSTI occurs when attacker-controlled text is interpreted as template source rather than as a value inserted into a trusted template.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — do not render user-controlled template source.
from jinja2 import Template
rendered = Template("Hello " + user_text).render()
```

The string is assembled into the template language before rendering. Template expressions inside `user_text` can therefore be evaluated.

**Safe alternative:**

```python
from jinja2 import Environment, select_autoescape

env = Environment(autoescape=select_autoescape(["html", "htm", "xml"]))
template = env.from_string("Hello {{ name }}")
rendered = template.render(name=user_text)
```

The template source is trusted and the user value is passed as data. Autoescaping is important for HTML output, but it does not make arbitrary template source safe. Jinja's `SandboxedEnvironment` is defence-in-depth, not a guarantee that attacker-controlled templates are safe: resource exhaustion, exposed objects, custom filters and sandbox gaps still require consideration.

**Checklist:** Who controls the template source? Are values passed as variables? Is autoescape enabled for the output type? Are custom filters and objects minimal? Are render time and output size bounded?

### 5.5 HTML injection and cross-site scripting (XSS)

**Definition.** HTML injection changes document markup; XSS is the execution of attacker-controlled script in a victim's browser under the application's origin.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — unsafe when inserted into an HTML response.
html = f"<p>Hello {display_name}</p>"
```

**Safe alternative for a small HTML-text example:**

```python
from markupsafe import escape

html = f"<p>Hello {escape(display_name)}</p>"
```

Prefer framework templates with autoescaping and keep values in the correct context. HTML text, HTML attributes, JavaScript, CSS and URL contexts differ; HTML escaping is not a universal encoder. Avoid constructing JavaScript or CSS with untrusted strings. Use safe DOM APIs such as `textContent` in browser code rather than `innerHTML` for plain text. A Content-Security-Policy (CSP) can reduce impact but is defence-in-depth, not a replacement for safe output handling.

**Checklist:** Is the output context known? Is autoescape active? Are values ever marked “safe” or inserted as raw HTML? Is CSP configured as an additional layer?

### 5.6 LDAP, NoSQL and GraphQL injection

**Definition.** These occur when data changes a directory filter, document-database query operator, or GraphQL document/selection rather than occupying a safe value position.

**VULNERABLE / LAB ONLY (NoSQL-shaped pseudocode):**

```python
# VULNERABLE / LAB ONLY — do not pass a client-controlled object as a query.
query = {"username": request_json}
collection.find_one(query)
```

If the application expects a username string but accepts an arbitrary JSON object, a caller may supply query operators instead of a username.

**Safe alternative:**

```python
def parse_username(value: object) -> str:
    if type(value) is not str:
        raise ValueError("username must be a string")
    if not 1 <= len(value) <= 64:
        raise ValueError("invalid username length")
    return value

username = parse_username(request_json)
collection.find_one({"username": username})
```

Use driver-supported escaping/parameterization for LDAP filters and avoid constructing filter strings manually. For GraphQL, use variables instead of string-building documents, constrain query depth/complexity and enforce authorization at resolvers. Validation alone does not authorize access to an object.

**Checklist:** Does the API accept an arbitrary object where a scalar is expected? Are query operators controlled by the server? Are variables used? Are depth, complexity and authorization bounded?

### 5.7 Header and CRLF injection

**Definition.** CRLF injection uses carriage-return/newline characters to alter line-oriented protocols or headers, potentially creating extra headers or response splitting.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — conceptual raw header construction.
response_header = "Location: " + user_supplied_location + "\r\n"
```

**Safe alternative:** use a framework's response/header API, validate URLs against an explicit scheme/host policy, and reject CR/LF in header values. Never construct raw HTTP messages by concatenating untrusted text. A framework may reject newlines already, but verify the behavior of the specific server and proxy chain.

**Checklist:** Is a header value accepted by a safe API? Are CR/LF rejected? Is redirect destination policy separate from syntax validation?

### 5.8 Format-string injection

**Definition.** Format-string injection happens when untrusted input controls the formatting template itself, potentially allowing unexpected attribute access or disclosure.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY.
message = user_format.format(secret_object)
```

**Safe alternative:**

```python
message = "{}".format(user_value)  # trusted format string; user_value is data
# Or simply:
message = str(user_value)
```

Do not let callers provide arbitrary `str.format` templates when the template can access objects. Python f-strings are evaluated by the Python parser and should not be generated/evaluated from untrusted text.

**Checklist:** Is the format string fixed and trusted? Can it reference objects or attributes? Is arbitrary format syntax a real product requirement, and if so, is a constrained formatter used?

### 5.9 Regular expressions and ReDoS

**Definition.** Regular-expression denial of service (ReDoS) occurs when a pattern/input combination triggers excessive backtracking or other expensive matching.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — a caller-controlled regex is not a safe validator.
import re
matched = re.search(user_pattern, text)
```

**Safer alternative:** if validating a simple identifier, use a fixed pattern and `fullmatch()`:

```python
import re

IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}")

def validate_identifier(value: object) -> str:
    # Bound length and type before regex work; annotations alone do not validate.
    if type(value) is not str or len(value) > 32:
        raise ValueError("invalid identifier")
    if IDENTIFIER.fullmatch(value) is None:
        raise ValueError("invalid identifier")
    return value
```

`fullmatch()` requires the entire input to match, unlike `search()`, which can accept a substring. Avoid ambiguous nested quantifiers and bound input length. If arbitrary patterns are a requirement, consider a regex engine with time/resource controls or isolate matching in a process with a deadline. Python's standard `re` API does not provide a general per-match timeout.

**Checklist:** Is the pattern fixed? Is the input bounded? Does the pattern have catastrophic-backtracking risk? Is matching work bounded?

### 5.10 XML external entities (XXE) and entity expansion

**Definition.** XXE occurs when an XML parser resolves attacker-controlled external entities. Entity expansion can also consume excessive memory or CPU.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — avoid permissive parsing of untrusted XML.
from xml.etree import ElementTree
root = ElementTree.fromstring(untrusted_xml)  # parser behavior depends on parser/version/features
```

**Safer alternative for untrusted XML:**

```python
from defusedxml import ElementTree as SafeET

root = SafeET.fromstring(untrusted_xml)
```

Use a hardened parser such as `defusedxml`, keep it updated, and impose document size and processing limits. “XML parsed successfully” does not mean the resulting structure is trustworthy.

**Checklist:** Is XML actually required? Is the parser hardened against external entities and expansion? Are document size, depth and element counts bounded?

### 5.11 CSV/Excel formula injection

**Definition.** Spreadsheet formula injection occurs when a cell containing untrusted text is interpreted as a formula by a spreadsheet application. Common leading characters include `=`, `+`, `-`, `@`, and in some import paths tabs or carriage returns.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — writing arbitrary untrusted cells to a spreadsheet.
import csv
with open("report.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow([user_supplied_cell])
```

CSV quoting protects delimiters and quotes; it does **not** guarantee that spreadsheet software treats a cell as plain text.

**Context-dependent mitigation:**

```python
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")

def spreadsheet_text_cell(value: str) -> str:
    # Example policy only. Verify behavior with the actual spreadsheet consumer.
    if value.startswith(FORMULA_PREFIXES):
        return "'" + value
    return value
```

Write with the `csv` module, but recognize that prefixing an apostrophe is consumer-dependent: spreadsheet products, import settings, encodings and later transformations can behave differently. Test with the actual Excel/LibreOffice/import workflow. For high-assurance reporting, prefer a format/API that explicitly sets cells to text, or avoid opening untrusted CSVs as spreadsheets. Do not claim this helper is universally reliable.

**Checklist:** Who will open/import the file? Are formula-leading and control-character cases tested? Is the mitigation verified in the target consumer? Are raw data exports separated from analyst-facing spreadsheet exports?

### 5.12 Path traversal — orientation only

**Definition.** Path traversal attempts to escape an intended directory using relative segments, absolute paths, encoded forms, mixed separators or symlinks.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — user input can escape or replace the base.
from pathlib import Path
path = Path("/srv/app/reports") / user_filename
```

**Safer direction:** prefer server-generated IDs over user-controlled path names, resolve and check containment, account for symlinks and time-of-check/time-of-use races, and use restrictive permissions. String-prefix checks are not containment checks. See Lesson 03 for the full file-handling design and platform-specific details.

**Checklist:** Is the identifier a path or an opaque ID? Can absolute paths or symlinks escape the base? Is the check race-free for the actual filesystem operations?

### 5.13 LLM prompt injection — preview only

**Definition.** Prompt injection occurs when instructions embedded in user content, retrieved documents, tool output or other model-visible data influence a model to ignore intended instructions or misuse tools.

Treat retrieved text and model output as untrusted data. Do not treat a model's assertion that an action is safe as authorization. Enforce permissions, tool schemas, approval gates and data-access policy outside the model. This lesson only previews the topic; the later AI security stage covers prompt injection, agent sandboxing, model supply chain and privacy in depth.

**Checklist:** Can the model invoke a tool or access a secret? Is authorization enforced by deterministic code? Are tool outputs and retrieved documents treated as data rather than policy?

## 6. Validation and canonicalization

### 6.1 Parse to types, then enforce the contract

A type annotation alone does not validate runtime input. `def f(limit: int)` does not stop a JSON caller from sending a string, boolean or huge number. Parse external representations and reject values outside the contract.

```python
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
from uuid import UUID
import ipaddress
import re

class ReportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

def parse_limit(raw: object) -> int:
    # API contract expects a decimal string, not bool/float/list.
    if type(raw) is not str or not re.fullmatch(r"[0-9]{1,3}", raw):
        raise ValueError("limit must be a decimal integer")
    value = int(raw)
    if not 1 <= value <= 500:
        raise ValueError("limit out of range")
    return value

def parse_report_date(raw: object) -> date:
    if type(raw) is not str or len(raw) != 10:
        raise ValueError("date must use YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(raw)
    except ValueError:
        raise ValueError("invalid date") from None
    if parsed.isoformat() != raw:
        raise ValueError("date must use canonical YYYY-MM-DD")
    return parsed

def parse_amount(raw: object) -> Decimal:
    if type(raw) is not str or len(raw) > 32:
        raise ValueError("invalid amount")
    try:
        value = Decimal(raw)
    except InvalidOperation:
        raise ValueError("invalid amount") from None
    if not value.is_finite() or value < 0 or value > Decimal("1000000"):
        raise ValueError("amount out of range")
    return value
```

Other useful parsers include `uuid.UUID`, `ipaddress.ip_address`, and `datetime.fromisoformat`. Parsing is not the end: enforce timezone expectations, valid ranges, enum membership, authorization and domain invariants.

Python has a subtle type trap: `True == 1` is `True`, and `isinstance(True, int)` is also true. If the contract requires an actual integer and booleans are invalid, use `type(value) is int` (or explicitly reject `bool`). Also decide how to handle NaN and Infinity for numeric inputs; many numeric comparisons with NaN behave unexpectedly. Bound integer digit count before converting huge decimal strings, and bound payload sizes before parsing.

### 6.2 Allow-list versus deny-list

An **allow-list** defines the complete set or shape of accepted input. A **deny-list** tries to enumerate forbidden input. Deny-lists are fragile because syntax, encodings and parser features are extensive.

```python
SORT_COLUMNS = {"name": "name", "created": "created_at"}

def sort_column(raw: object) -> str:
    if type(raw) is not str or raw not in SORT_COLUMNS:
        raise ValueError("unsupported sort")
    return SORT_COLUMNS[raw]
```

This rejects everything except the two supported choices. A blacklist such as `if "'" not in value` does not establish that a value is safe for SQL, HTML, a shell or any other context.

### 6.3 Canonicalize, validate, then use the canonical value

**Canonicalization** converts multiple representations into the form the application intends to use. Examples include Unicode normalization, URL decoding and path resolution. The order matters:

1. Define which encodings and transformations are accepted.
2. Decode/normalize exactly once according to that contract.
3. Reject ambiguous or malformed representations.
4. Validate the normalized representation.
5. Use that same normalized value downstream.

Do not validate the raw string and later decode, case-fold or normalize it without revalidation. Avoid double-decoding. Specific edge cases to consider in the contract include:

- **Double URL encoding:** a value such as `%252e%252e` becomes `%2e%2e` after one decode and `..` after another. Decode only according to the documented protocol layer; reject unexpected residual encodings rather than letting downstream components decode again.
- **Overlong or malformed UTF-8:** strict decoders should reject invalid encodings. Do not add custom decoding that accepts multiple byte representations of a character.
- **Null bytes (`\x00`):** reject them where the downstream API, native library or storage layer could truncate or interpret the value differently.
- **Mixed separators and case folding:** path and identifier semantics differ by platform and filesystem. Validate the canonical representation that the actual sink will use; do not assume `/` and `\` or case-sensitive and case-insensitive comparisons are interchangeable.
- **Unicode normalization and homoglyphs:** NFC can make canonically equivalent sequences consistent, but it does not make visually confusable characters equivalent. Use a narrow ASCII allow-list for machine identifiers where feasible, or define and test an explicit Unicode policy.

Security-sensitive identifiers may need an ASCII allow-list or a documented Unicode policy. Canonicalization is context-specific: do not URL-decode a value that is not URL-encoded, and do not treat normalization as authorization.

```python
import unicodedata
import re

def parse_account_key(raw: object) -> str:
    if type(raw) is not str or len(raw) > 80:
        raise ValueError("invalid account key")
    normalized = unicodedata.normalize("NFC", raw)
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", normalized) is None:
        raise ValueError("invalid account key")
    return normalized
```

This example intentionally accepts a narrow ASCII identifier set after normalization. It does not claim to make arbitrary Unicode safe.

### 6.4 Schema validation and exact shapes

At an API boundary, use a schema/model validator such as Pydantic or `jsonschema` when appropriate. Configure strictness deliberately: coercion may be useful for human forms but surprising in machine APIs. A schema can validate shape, types, ranges and lengths; it does not automatically enforce authorization, business rules, safe output encoding or resource limits.

Example with Pydantic v2 (optional dependency; install with `python -m pip install "pydantic>=2,<3"` in the lesson environment):

```python
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ReportRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    name: str = Field(min_length=1, max_length=64)
    limit: int = Field(ge=1, le=500)

    @field_validator("name")
    @classmethod
    def name_uses_allowed_grammar(cls, value: str) -> str:
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value) is None:
            raise ValueError("invalid report name")
        return value
```

A strict model may reject JSON strings for integer fields rather than coercing them; this is often desirable for service-to-service contracts. Confirm behavior for the installed Pydantic version and the transport layer.

### 6.5 Resource limits are security controls

Valid syntax can still be expensive. Apply limits before or during processing:

- Maximum HTTP body and file size.
- Maximum list items, object keys, nesting depth and string length.
- Maximum regex input length and query complexity.
- Request deadlines, database timeouts, rate limits and concurrency limits.
- Maximum rows, partitions, archive members and decompressed bytes in data jobs.

A limit must be enforced before the expensive operation when possible. Checking a 20 GB body after loading it into memory is too late. Rate limiting belongs at the appropriate service/gateway layer; application-level checks may need shared state in distributed deployments.

### 6.6 Parser differentials and ambiguous inputs

A **parser differential** occurs when two components interpret the same bytes differently. Examples include a proxy and application disagreeing about URL boundaries, JSON parsers disagreeing on duplicate keys, or inconsistent handling of multipart boundaries and encodings. This can lead to policy bypasses or request-smuggling classes of bugs.

Prefer one authoritative parse, strict parsers, explicit encoding, rejection of duplicate or ambiguous fields where relevant, and consistent canonical values across proxy, application and downstream systems. Do not rely on a web application firewall as the only validation layer.

## 7. Beginner-to-advanced code walkthroughs

The following examples use Python 3.11+ unless a dependency is explicitly stated. The standard-library examples need no third-party package. Run snippets in a clean local virtual environment.

### 7.1 SQLite: separate SQL values from query structure

```python
import sqlite3

connection = sqlite3.connect(":memory:")
connection.execute("CREATE TABLE users (id INTEGER, name TEXT)")
connection.executemany(
    "INSERT INTO users VALUES (?, ?)",
    [(1, "Asha"), (2, "Bo")],
)

name = "Asha' OR '1'='1"
rows = connection.execute(
    "SELECT id, name FROM users WHERE name = ?",
    (name,),
).fetchall()

print(rows)
```

Expected output:

```text
[]
```

The payload-like text is treated as a literal name, not as SQL syntax. This is the key security property of parameter binding.

For a safe sort choice, map a public option to a fixed identifier and reject unknown values:

```python
sort_map = {"name": "name", "id": "id"}
requested_sort = "name"
column = sort_map.get(requested_sort)
if column is None:
    raise ValueError("unsupported sort")
rows = connection.execute(f"SELECT id, name FROM users ORDER BY {column}").fetchall()
print(rows)
```

Expected output:

```text
[(1, 'Asha'), (2, 'Bo')]
```

This f-string is safe only because `column` is selected from a fixed mapping, not because f-strings are inherently safe.

### 7.2 Validate a report route

The roadmap self-check asks for a validator for `/reports/<name>?from=<date>&limit=<n>`. Here is a small parser for the individual fields; a real HTTP framework should parse the route and query string, and the application should reject duplicate/ambiguous parameters according to its contract.

```python
from datetime import date
import re

REPORT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}")

def validate_report_request(name: object, from_date: object, limit: object) -> tuple[str, date, int]:
    if type(name) is not str or REPORT_NAME.fullmatch(name) is None:
        raise ValueError("invalid report name")
    if type(from_date) is not str or len(from_date) != 10:
        raise ValueError("invalid date")
    try:
        parsed_date = date.fromisoformat(from_date)
    except ValueError:
        raise ValueError("invalid date") from None
    if parsed_date.isoformat() != from_date:
        raise ValueError("date must be YYYY-MM-DD")
    parsed_limit = parse_limit(limit)
    return name, parsed_date, parsed_limit

print(validate_report_request("daily-report", "2026-10-18", "50"))
```

Expected output:

```text
('daily-report', datetime.date(2026, 10, 18), 50)
```

A real handler should also enforce authorization, query parameter multiplicity, request size and business date rules. Never turn `name` into a filesystem path or SQL identifier without the specific controls required by that sink.

### 7.3 Safe errors and correlation IDs

```python
import logging
import uuid

logger = logging.getLogger(__name__)

def handle_request(raw_limit: object) -> tuple[int, dict[str, str]]:
    request_id = str(uuid.uuid4())
    try:
        limit = parse_limit(raw_limit)
    except ValueError:
        logger.info("request_rejected", extra={"request_id": request_id, "reason": "invalid_limit"})
        return 400, {"error": "Invalid request", "request_id": request_id}
    return 200, {"limit": str(limit), "request_id": request_id}
```

This demonstrates the boundary between a generic client error and a controlled server-side event. Configure a production JSON formatter to serialize fields as JSON; do not assume every default formatter emits structured logs. Avoid recording the raw malicious payload unless there is a documented need and a safe retention/redaction policy.

## 8. Production design patterns and trade-offs

### 8.1 Context-specific sink matrix

| Sink/context | Preferred control | Important limitation |
|---|---|---|
| SQL values | Driver parameter binding | Does not bind identifiers or enforce authorization |
| SQL identifiers | Closed allow-list / fixed query mapping | Must cover every dynamic identifier |
| Shell arguments | Argument list, `shell=False`, validated arguments; preferably a library | Argument/option injection remains possible |
| HTML text | Framework template autoescape or HTML-text encoder | Do not reuse this encoder for other contexts |
| HTML attributes | Quoted attributes plus the framework's context-aware escaping | Avoid placing untrusted values in event-handler attributes or dangerous URL schemes |
| JavaScript data | Prefer external data/JSON serialization and safe DOM APIs such as `textContent` | HTML escaping alone is not JavaScript-string encoding |
| URL components/redirects | URL builder plus a separate scheme/host/destination policy | Percent-encoding does not authorize a destination or prevent SSRF |
| CSS | Avoid dynamic CSS; use fixed classes or allow-listed tokens | HTML escaping does not make arbitrary CSS safe |
| Trusted template source | Never render attacker-controlled source | Sandbox is not a complete security boundary |
| Logs | Structured JSON serialization; CR/LF handling for text sinks | `logger.info("%s", x)` alone is not a full output policy |
| HTTP headers | Framework/client header APIs and CR/LF rejection | Proxy/server behavior must be verified |
| CSV/Excel | Consumer-tested text-cell strategy or typed spreadsheet cells | Apostrophe prefix is not universally reliable |
| LDAP filters | Library-supported escaping and fixed filter structure | Escaping must match LDAP filter context |
| NoSQL queries | Construct query objects from validated scalars | Never accept arbitrary client query objects by default |
| GraphQL | Variables, depth/complexity controls, resolver authorization | Variables do not replace authorization |
| XML | Hardened parser such as `defusedxml`; size/depth limits | Safe parsing does not validate business meaning |
| Regex | Fixed patterns, `fullmatch`, bounded input | Standard `re` has no general match timeout |
| Paths | ID-based storage and containment/symlink-safe operations | Full solution belongs in Lesson 03 |
| LLM tools | External authorization, strict tool schemas and approval gates | Model instruction-following is not a security boundary |

There is no universal `sanitize()` function. Encoding is defined by the target language and position within that language.

### 8.2 ORM, query builders and stored procedures

An ORM can help keep values separate from SQL structure, but raw SQL APIs remain a sharp edge. For SQLAlchemy, prefer expression APIs and bind parameters. If using `text()`, bind values explicitly; do not interpolate untrusted values into the SQL string. A stored procedure is safe only if its internal query construction and authorization are safe.

### 8.3 Least privilege and blast-radius reduction

Assume input validation can fail or a new bug can appear. The database identity used by a report endpoint should not be able to drop unrelated tables, read all tenants' data or alter database roles. Separate application and migration accounts; use read-only permissions for reporting; enforce row-level access where supported; scope credentials to the workload. Least privilege limits impact; it does not repair injection.

### 8.4 Safe public APIs and secure-by-default libraries

Design interfaces so callers naturally choose the safe path:

- Accept typed values rather than prebuilt query/command strings.
- Provide fixed query builders and enumerated choices for dynamic structure.
- Keep templates trusted and pass variables separately.
- Make unsafe operations explicit in names and documentation, for example `unsafe_render_template`, rather than silently using them by default.
- Do not expose a `SafeSQL` wrapper that callers can create from arbitrary strings and mistake for a proof of safety. A “safe” type is meaningful only if its constructor and invariants are controlled.
- Document accepted formats, bounds, exceptions and residual risks; include safe examples in docstrings and README files.

Python 3.14 introduces template-string (t-string) support, but a template-string object alone is not an automatic security solution. Safety depends on how a library processes the structured interpolations and whether it preserves parameterization/context-aware encoding. Use a vetted sink-specific API rather than assuming a new string feature makes SQL or HTML safe.

### 8.5 Data-engineering entry points

Threat-model data pipelines as services with trust boundaries:

- **Object-store filenames/keys:** do not assume key names are filesystem paths or safe identifiers.
- **CSV headers:** reject unexpected columns, duplicate names and names that become SQL identifiers without an allow-list.
- **JSON keys:** bound key count/length and reject duplicate or ambiguous keys if downstream parsers disagree.
- **Partition values:** validate type, length and allowed domain before constructing storage paths, SQL or table names.
- **Ingestion metadata:** treat source names, file names, content types and external job output as untrusted.
- **Generated reports:** distinguish raw-data exports from spreadsheet-facing outputs.
- **Warehouse queries:** bind values, map dynamic table/column choices to approved identifiers, and use a narrowly privileged role.
- **AI pipeline output:** treat model summaries and tool outputs as untrusted text; validate structured tool arguments and authorize actions outside the model.

## 9. Security testing and review

### 9.1 Test behavior, not just the presence of a check

A security regression test should assert a security property: invalid values are rejected, a query returns only the matching row, a report cell is not interpreted as a formula in the supported consumer, or a log event remains one structured record. Merely asserting that a helper function was called does not prove the end-to-end sink is safe.

### 9.2 Payload table

Use payloads only against your local lab and own test fixtures. A useful starting matrix:

| Area | Example input | Desired property |
|---|---|---|
| SQL value | `x' OR '1'='1` | Treated as a literal value |
| SQL identifier | `name; DROP TABLE users` | Rejected because not allow-listed |
| Log field | `alice\nWARNING forged` | One correctly serialized event/field |
| HTML text | `<script>alert(1)</script>` | Rendered as text, not executable markup |
| Template value | `{{ 7 * 7 }}` | Displayed literally when passed as data |
| Header | `ok\r\nX-Test: injected` | Rejected by header policy/API |
| Regex | Very long input against a known validator | Bounded work; no attacker-controlled pattern |
| CSV cell | `=1+1` | Consumer-specific formula mitigation verified |
| Type confusion | `true`, `["a"]`, `{}`, `NaN`, huge digit string | Rejected unless explicitly in contract |
| Unicode | Canonically equivalent forms, confusables | Normalized or rejected per policy |
| Resource abuse | Oversized body, deep JSON, huge item count | Rejected before expensive processing |

### 9.3 Unit and regression tests

The standard library's `unittest` is enough for the core examples; `pytest` is convenient but optional. Keep test fixtures local and deterministic. Do not make a regression test depend on a live external target or a particular spreadsheet UI unless that is an intentional integration test.

### 9.4 Property-based testing and fuzzing

Property-based testing generates many values and checks invariants. Hypothesis is an optional third-party library (`python -m pip install hypothesis`). For a validator, a useful invariant is: it returns only a canonical string matching the documented grammar, or raises a documented validation exception. For a storage function, the analogous invariant might be containment under a base directory (the full path lesson covers the filesystem details).

Example property test:

```python
# Optional: pip install hypothesis
import re
from hypothesis import given, strategies as st

@given(st.text(max_size=200))
def test_identifier_is_always_valid_or_rejected(value: str) -> None:
    try:
        result = validate_identifier(value)
    except ValueError:
        return
    assert IDENTIFIER.fullmatch(result) is not None
```

Fuzzing is not a substitute for threat modelling. It can reveal edge cases but cannot prove the absence of vulnerabilities. For regexes or parsers where a hang is possible, run fuzzing with an external process timeout and resource limits.

### 9.5 Static-analysis awareness

The roadmap recommends tools such as Bandit, Ruff security (`S`) rules, Semgrep and `pip-audit`. Static analysis can flag risky APIs and known dependency vulnerabilities, but findings need context and clean scans are not proof of safety.

Optional local setup:

```bash
python -m venv .venv
# Activate the environment using the command for your shell.
python -m pip install --upgrade pip
python -m pip install pytest hypothesis jinja2 markupsafe defusedxml
python -m pip install bandit pip-audit
```

For a project using `uv`, the roadmap's optional developer-tool command is `uv add --dev bandit pip-audit detect-secrets semgrep`. Install only what your project needs and pin dependencies using the project's normal dependency-management workflow. Run `bandit -r .` and `pip-audit` from the project environment; review the reports rather than treating a zero exit status as a complete security assessment.

### 9.6 Code-review questions

1. Who controls this value, including indirectly through a file, database row or model output?
2. What exact sink receives it, and what grammar does that sink parse?
3. Are values passed separately from instructions?
4. Is validation performed on the canonical value that is actually used?
5. Are exact types, lengths, ranges, enum choices and resource limits enforced?
6. Can an ORM/raw query, template, log formatter or downstream tool reinterpret the value?
7. Could the same value be stored and used unsafely later (second-order injection)?
8. Are authorization and least privilege enforced independently of input validation?
9. Are error messages safe for callers while diagnostics remain useful to operators?
10. Is there a regression test for the defect and a test for the expected safe behavior?

## 10. Hands-on lab: local `vulnpy`

### 10.1 Safety boundary and setup

Use only a local copy of your own deliberately vulnerable training application. Do not expose it to a network, point tests at production, or use real credentials/data. If your repository already includes `vulnpy`, inspect its source and tests first. The roadmap describes it as a small sample app with a file upload, report generator, URL fetcher, config loader and admin CLI; this lesson focuses only on four defects: SQL injection, template injection, CSV formula injection and log forging.

Python 3.11+ is suitable. Create an isolated environment and install only the dependencies needed by the lab:

```bash
python -m venv .venv
# Activate .venv for your operating system.
python -m pip install jinja2 pytest
```

If your existing lab uses other frameworks, retain its pinned dependencies and adapt the same security properties rather than replacing the project with a different syllabus.

### 10.2 Lab tasks and observations

For each defect: identify the source and sink; reproduce the behavior with harmless local input; fix the code using the sink's safe API; add a regression test; then rerun the test suite.

#### A. SQL injection

- **Observe:** a query constructed with an f-string changes query structure when a name contains SQL syntax.
- **Fix:** use the database driver's parameter binding for values. If the lab has a sort/table option, map the public choice to a fixed identifier allow-list.
- **Regression:** use an in-memory SQLite database. Insert two users, query with a payload-like name, and assert that only exact matches are returned (or no rows for the payload-like name). Assert an unknown sort option is rejected.
- **Review:** ensure tests exercise the actual query function, not just a validator in isolation.

#### B. Template injection

- **Observe:** a lab function that concatenates input into Jinja template source evaluates template expressions.
- **Fix:** keep template source constant and pass user text as a variable. Enable autoescape when generating HTML. Never make arbitrary user templates safe merely by switching to a sandbox.
- **Regression:** with a trusted template `Hello {{ name }}`, pass `{{ 7 * 7 }}` as the name and assert that the rendered result contains the literal text `{{ 7 * 7 }}`, not `49`. If HTML output is expected, also assert that markup is escaped.

#### C. CSV formula injection

- **Observe:** a spreadsheet may interpret a cell beginning with `=` as a formula even when CSV quoting is correct.
- **Fix:** define the target consumer and use a tested policy: consumer-verified text-cell handling, a spreadsheet-writing API that sets cell types, or a safer report format. If using an apostrophe prefix, document that it is context-dependent.
- **Regression:** test cells beginning with `=`, `+`, `-`, `@`, tab and carriage return, then verify the actual supported spreadsheet import workflow. A unit test of the prefix helper is necessary but not sufficient to prove the consumer will treat the cell as text.

#### D. Log forging

- **Observe:** a newline in an untrusted username can create misleading lines in a naïve plain-text log.
- **Fix:** use a JSON/structured formatter that serializes field values; if plain text is required, escape CR/LF and control characters. Keep raw payloads out of logs unless necessary and controlled.
- **Regression:** capture the serialized event and assert it is one JSON object/record, with the newline represented as escaped data rather than a new physical record. Do not assume `extra=` alone guarantees this; test the configured formatter.

### 10.3 Minimal runnable regression tests

Save as `test_injection_basics.py`. These tests demonstrate the safe properties without launching a web server or contacting external systems.

```python
import csv
import io
import sqlite3

import pytest
from jinja2 import Environment, select_autoescape

def safe_user_lookup(connection: sqlite3.Connection, name: str) -> list[tuple]:
    return connection.execute(
        "SELECT id, name FROM users WHERE name = ?", (name,)
    ).fetchall()

SORT_COLUMNS = {"name": "name", "created": "created_at"}

def safe_sort_column(value: object) -> str:
    if type(value) is not str or value not in SORT_COLUMNS:
        raise ValueError("unsupported sort")
    return SORT_COLUMNS[value]

def render_greeting(user_text: str) -> str:
    env = Environment(autoescape=select_autoescape(["html", "htm", "xml"]))
    template = env.from_string("Hello {{ name }}")
    return template.render(name=user_text)

def spreadsheet_text_cell(value: str) -> str:
    # Demonstration policy only; consumer behavior must be tested separately.
    if value.startswith(("=", "+", "-", "@", "\t", "\r", "\n")):
        return "'" + value
    return value

def json_log_record(username: str) -> str:
    import json
    return json.dumps({"event": "login_failed", "username": username}, ensure_ascii=True)

@pytest.fixture
def db():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    connection.executemany("INSERT INTO users VALUES (?, ?)", [(1, "Asha"), (2, "Bo")])
    yield connection
    connection.close()

@pytest.mark.parametrize("payload", ["x' OR '1'='1", "'; DROP TABLE users; --", ""])
def test_sql_payload_is_a_value(db, payload):
    rows = safe_user_lookup(db, payload)
    assert all(row[1] == payload for row in rows)
    assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 2

def test_sort_is_allow_listed():
    assert safe_sort_column("name") == "name"
    with pytest.raises(ValueError):
        safe_sort_column("name; DROP TABLE users")

def test_template_expression_is_data():
    payload = "{{ 7 * 7 }}"
    assert render_greeting(payload) == "Hello {{ 7 * 7 }}"

def test_html_is_escaped_in_template():
    assert render_greeting("<b>x</b>") == "Hello &lt;b&gt;x&lt;/b&gt;"

@pytest.mark.parametrize("payload", ["=1+1", "+SUM(A1:A2)", "-1+2", "@SUM(A1:A2)", "\t=1+1", "\r=1+1"])
def test_spreadsheet_policy_marks_formula_prefix(payload):
    assert spreadsheet_text_cell(payload).startswith("'")

def test_log_record_keeps_newline_as_json_data():
    import json
    record = json_log_record("alice\nWARNING forged")
    assert record.count("\n") == 0
    assert json.loads(record)["username"] == "alice\nWARNING forged"

def test_csv_writer_quotes_cells_but_does_not_claim_formula_safety():
    output = io.StringIO(newline="")
    csv.writer(output).writerow(["=1+1", "ordinary"])
    assert output.getvalue().startswith("=1+1,")
```

Run:

```bash
python -m pytest -q
```

The expected result is that the tests pass; no test execution is claimed by this lesson. The last test intentionally demonstrates that CSV quoting alone does not mitigate formula interpretation. The spreadsheet-policy tests validate the helper's behavior, not every spreadsheet consumer.

### 10.4 Lab completion criteria

- You can point to each source, transformation and sink in the vulnerable code.
- Each fix separates data from instructions rather than deleting suspicious characters.
- Tests cover both benign and malicious-looking values and preserve legitimate behavior.
- The CSV strategy is verified against the actual consumer, not just unit-tested.
- Logs remain useful to operators without exposing secrets or allowing forged records.
- The code has no production credentials, no external targets and no exposed lab service.

## 11. Common mistakes and why they are wrong

1. **Removing apostrophes or blacklisting suspicious characters.** SQL and other languages have many syntax features and encodings. Use parameterization or the sink's safe API.
2. **Validating raw input, then transforming it.** Decoding, normalization or concatenation may change the meaning. Validate and use the same canonical form.
3. **Using an f-string for a SQL table name without an allow-list.** Value placeholders do not generally bind identifiers; use a fixed mapping for the identifier.
4. **Assuming an ORM or stored procedure is automatically safe.** Raw SQL and dynamic query construction can reintroduce injection.
5. **Assuming `logger.info("%s", value)` prevents log forging.** It defers formatting, but the output formatter and downstream log viewer still matter.
6. **Treating client-side validation as a security control.** Clients can be modified or bypassed. Validate again at the trusted server boundary.
7. **Using one encoder for every output context.** HTML text, attributes, JavaScript, URLs, CSS, SQL and shell syntax differ.
8. **Treating a sandbox or CSP as the primary fix.** These are defence-in-depth; do not execute untrusted templates or emit unsafe markup in the first place.
9. **Checking only value equality or `isinstance` for numbers.** `True == 1`; reject booleans explicitly when the contract requires an integer. Handle NaN/Infinity and extreme sizes deliberately.
10. **Ignoring resource exhaustion because input is syntactically valid.** Bound size, depth, item count, CPU time, query complexity and rate.
11. **Assuming internal databases, files or model outputs are trusted.** Trust depends on provenance, write permissions and the current boundary, not the network label.
12. **Assuming an apostrophe prefix universally neutralizes CSV formulas.** Spreadsheet consumers differ; verify the target workflow and prefer explicit text-cell types when available.
13. **Assuming a clean static-analysis scan proves security.** Static tools have blind spots; combine them with tests, review, least privilege and threat modelling.
14. **Treating a model's instructions or output as authorization.** LLM output is untrusted data; deterministic policy code must authorize actions.

## 12. Self-check questions and answer key

Try answering before reading the explanations.

### Questions

1. Why can't table names usually be parameterized, and what is the safe approach?
2. Name five injection sinks and the safe API/control for each.
3. What is the difference between validation and output encoding?
4. Why is removing `'` from input not a robust SQL defence?
5. Why does `logger.info("%s", username)` not necessarily prevent log forging?
6. Explain second-order injection and blind injection.
7. Why is `True == 1` relevant to validation? How should a numeric API handle NaN, Infinity and huge integers?
8. What does “canonicalize → validate → use” mean? Give one example of validating the wrong representation.
9. Why are ORM use and stored procedures not sufficient guarantees against SQL injection?
10. What are the residual risks of CSV apostrophe-prefix mitigation, CSP and template sandboxing?
11. Design a validator for `/reports/<name>?from=<date>&limit=<n>`: specify the accepted name grammar, date format, limit range and at least four rejection tests.
12. In a data pipeline, name four entry points that must be treated as untrusted and identify their likely sinks.

### Answer key

1. SQL parses identifiers as statement structure, while placeholders normally represent values. Map public choices to a closed set of application-owned table/column identifiers and reject unknown choices.
2. Examples: SQL values → parameter binding; HTML text → framework autoescape/context-aware encoding; shell → argv list with `shell=False` plus argument validation; logs → structured serialization/CRLF-safe formatter; XML → hardened parser such as `defusedxml`; templates → trusted template source and variables; CSV → consumer-tested spreadsheet text handling.
3. Validation determines whether the value satisfies the application contract. Encoding/parameterization prevents the value from changing the syntax of a particular sink. Both may be needed.
4. SQL syntax is broader than apostrophes, and encoding/driver behavior varies. Parameter binding preserves the separation between query structure and value.
5. Deferred logging formatting does not guarantee that the final formatter or downstream viewer treats newline/control characters as data. Use and test structured serialization.
6. Second-order injection stores a value and later uses it unsafely at another sink. Blind injection is inferred from indirect behavior (for example, differences in response, timing or side effects) rather than a direct query result. Test only systems you own or are authorized to assess.
7. `bool` is a subclass of `int` and `True == 1`; exact type checks or explicit boolean rejection may be required. Reject non-finite decimals/floats if unsupported, and cap digits/size before expensive conversion.
8. Normalize/decode according to a defined policy, validate the resulting canonical representation, and use that same value. Validating `%2e%2e` before URL-decoding and then using `../` is a classic wrong-representation pattern.
9. An ORM may expose raw SQL; a stored procedure may concatenate dynamic SQL internally. Inspect the actual construction path and use parameters/allow-lists.
10. Spreadsheet behavior differs by consumer; CSP only limits some browser execution paths; template sandboxes may expose dangerous objects or allow resource exhaustion. These are not substitutes for safe source/data separation.
11. Example contract: name `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`, date exactly canonical `YYYY-MM-DD`, limit decimal string `1..500`. Reject `../secret`, empty name, 65-character name, invalid date `2026-02-30`, noncanonical date, `limit=0`, `limit=501`, boolean/array input and oversized numeric strings.
12. Examples: object-store filename → storage path; CSV header → column/table identifier; JSON key → schema/dispatch logic; partition value → SQL/path; model output → tool argument; external process output → log or downstream command. Each sink needs its own control.

## 13. Completion checklist and what to learn next

### Completion checklist

- [ ] I can identify trust boundaries and name likely attackers, assets and entry points.
- [ ] I can trace an input through parsing, validation, transformation, sink and impact.
- [ ] I use SQL parameters for values and allow-lists for identifiers.
- [ ] I distinguish trusted template source from untrusted template variables.
- [ ] I know why log formatting, HTML encoding and CSV quoting are not universal defences.
- [ ] I can explain the main command, path, LDAP/NoSQL/GraphQL, header, format-string, regex, XML and LLM prompt-injection risks at the level required here.
- [ ] I validate exact types, lengths, ranges, enums and canonical forms.
- [ ] I set size, depth, time and rate limits for untrusted inputs.
- [ ] I use generic client errors, controlled server diagnostics and least-privilege database access.
- [ ] I can write payload-based regression tests and explain what they do—and do not—prove.
- [ ] I have completed the four local `vulnpy` lab tasks and verified the relevant consumer behavior for CSV output.

### What to learn next

Proceed to **Lesson 02 — `02-unsafe-deserialization.md`** in the roadmap's sequence. It builds on the same trust-boundary discipline and applies it to formats and loaders that may instantiate objects or trigger behavior during deserialization. Do not skip ahead: Lessons 03 and 04 provide the full treatments of path traversal and subprocess/command injection introduced here.

---

## Version and scope notes

- The standard-library code examples target Python 3.11+ unless noted. The optional Pydantic example targets Pydantic v2; Jinja2, MarkupSafe, `defusedxml`, pytest and Hypothesis are third-party dependencies.
- The roadmap is the source of the lesson's required scope, sequence, named tools, lab defects, common mistakes and self-check topics. Explanations, example code and test scaffolding here are instructional elaborations of that scope.
- No external system is targeted. This document does not claim that its snippets or tests were executed; run them in the isolated environment and review the behavior of your actual framework, database driver, logger and spreadsheet consumer.
