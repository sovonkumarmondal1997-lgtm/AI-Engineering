# Environment Configuration and Input Validation

## Learning Objectives

By the end of this chapter you will be able to:

- Explain what configuration is, how it differs from code and from
  ordinary data, and why production applications must not hard-code
  environment-specific values.
- Read environment variables safely with `os.environ` and
  `os.getenv()`, understand that every value is a string, and convert
  values to `int`, `float`, and `bool` correctly and safely.
- Design configuration defaults deliberately: when to use one, when to
  require a value, and when to fail fast instead of guessing.
- Explain why secrets are commonly passed through environment
  variables, how `.env` files fit into local development, and why
  environment variables are not automatically a complete secret-
  management solution.
- Design and defend an explicit configuration precedence (defaults →
  config file → environment → CLI arguments), and explain why an
  implicit or undocumented precedence causes real bugs.
- Distinguish parsing from validation, and validation from
  normalization and from sanitization — three related but genuinely
  different operations.
- Apply the boundary-validation principle: validate untrusted input
  once, at the edge of the system, and let the rest of the program
  operate on a trusted, normalized internal representation.
- Apply the standard validation types (presence, type, range, length,
  format, enum, cross-field, path/file, encoding) using Python's
  standard library.
- Write correct string, numeric, boolean, and path/file validators,
  including a safe, reusable boolean-environment-variable parser.
- Validate JSON and CSV input for shape, required fields, and field
  types — extending
  [03-csv-files.md](03-csv-files.md) and
  [04-json-and-serialization.md](04-json-and-serialization.md).
- Choose between fail-fast and error-collection validation strategies
  depending on the situation, and write clear, actionable validation
  error messages.
- Use the standard exceptions relevant to validation (`ValueError`,
  `TypeError`, `FileNotFoundError`, `PermissionError`, `KeyError`,
  `json.JSONDecodeError`, `argparse.ArgumentError`) correctly —
  knowing when to raise, when to catch, and when not to catch.
- Write small, reusable, testable validator functions with predictable
  return types and predictable exceptions.
- Design a centralized, validated, immutable configuration object using
  `dataclasses`, and explain why passing it explicitly beats reading
  `os.environ` throughout an application.
- Recognize defensive-engineering concerns around untrusted input:
  secrets, path traversal, unsafe command/query construction, and log
  injection — at a conceptual, non-offensive level.
- Log configuration and validation state safely, without ever exposing
  secrets, connecting directly to
  [08-logging-versus-print.md](08-logging-versus-print.md).
- Test configuration and validation logic systematically with pytest,
  including parameterized tests for valid, missing, malformed, and
  boundary input.
- Design a complete, production-style CLI that turns untrusted external
  input — CLI arguments, environment variables, and file data — into a
  validated configuration object and validated records, before any
  business logic runs.

## Prerequisites

This chapter is the capstone of Module 1.5, and draws directly on
every prior file in this folder:
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)
(path validation),
[03-csv-files.md](03-csv-files.md) and
[04-json-and-serialization.md](04-json-and-serialization.md) (record
validation),
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)
(CLI parsing and the `main(argv) -> int` pattern),
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)
(exit codes and stdout/stderr separation), and
[08-logging-versus-print.md](08-logging-versus-print.md) (safe,
structured diagnostics). No new external tools are required; this
chapter is standard-library only, with `python-dotenv` mentioned once,
by name, purely as background context (§6).

## 1. What Is Configuration?

**Configuration** is the set of values that control *how* a program
behaves, kept separate from the code that defines *what* the program
does. The distinction matters because code and configuration change
for different reasons, at different times, by different people: code
changes when the program's logic changes; configuration changes when
the program needs to behave differently in a different situation — a
different environment, a different deployment, a different user —
with the logic itself staying exactly the same.

**Configuration vs. code:**
```python
# Code: the logic — how a connection is made. This should rarely change.
def connect(host: str, port: int):
    ...

# Configuration: the specific values — where to connect. This changes constantly.
host = "db.production.example.com"
port = 5432
```

**Configuration vs. data:** configuration controls program *behavior*
(a port number, a feature flag, a log level); data is the *content* a
program processes (a CSV file's rows, a user's uploaded document).
The line is not always perfectly sharp — a config file can technically
be read the same way a data file is — but the *purpose* is different:
data is what the program is *for*; configuration is *how* it does that
job in this particular run, on this particular machine.

Why applications need configuration at all: the exact same program
logic commonly needs to run differently in different situations — a
development laptop talking to a local test database versus the same
code, unchanged, talking to a production database in a data center;
a CLI tool run with verbose logging while debugging versus quietly in
an automated pipeline. Configuration is what makes one codebase
usable across all of these situations without editing the code itself
for each one.

**Hard-coded configuration** — the value is written directly into the
source code:
```python
DATABASE_HOST = "db.production.example.com"   # hard-coded
```
This is the simplest possible approach, and it is a real, common
mistake once a program needs to run in more than one place: changing
the value now requires editing and redeploying code, and — worse — it
becomes tempting to hard-code secrets the same way (§5 covers exactly
why that's dangerous).

The alternatives this chapter builds up, in order of increasing
flexibility:

- **Environment-based configuration** (§2) — values read from the
  process's environment at startup.
- **CLI configuration** (§8) — values supplied as command-line
  arguments for this specific invocation.
- **Configuration files** — values stored in a file (JSON, TOML, YAML,
  `.env`) read at startup; briefly touched on here since Module 1.5's
  earlier chapters already cover reading structured files.
- **Defaults** — a value the program falls back to when nothing else
  supplies one, chosen deliberately (§4).

**Required vs. optional configuration** is a decision each individual
setting needs, explicitly: a **required** value (e.g. a database
connection string with no sensible universal default) should cause the
program to refuse to start if it's missing, rather than silently
guessing; an **optional** value (e.g. a log level) can reasonably fall
back to a sensible default. §4 develops this distinction fully.

The rule this whole chapter enforces: **production applications should
not hard-code environment-specific values.** A value that's different
between your laptop and a production server — hostnames, ports,
credentials, feature flags — belongs in configuration, not in the
source code itself.

## 2. Environment Variables

An **environment variable** is a named string value that lives outside
your program, attached to the **process** that runs it, rather than
to the program's own source code. Every running process on Linux
(including inside WSL2), macOS, and Windows has its own **environment**
— a simple key/value collection of strings — available to it from the
moment it starts.

**The key/value model:** every environment variable is a name (a
string, conventionally uppercase with underscores, e.g. `DATABASE_URL`)
paired with a value (also always a string — §3 covers exactly why this
matters). A process's environment is essentially a flat dictionary of
these pairs.

**Inheritance:** when a process starts another process (for example,
your shell starting Python, exactly as
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)'s
§54 described for stdin/stdout/stderr), the new (**child**) process, by
default, **inherits a copy of its parent's environment**. This is
precisely how setting a variable in your shell makes it visible to a
Python program you then run from that same shell — the shell is the
parent process, and Python is the child.

**Setting environment variables in the shell** (bash, the default on
Ubuntu/WSL2):
```bash
export APP_ENV=development
export PORT=8000
```

`export` makes the variable part of the shell's own environment (not
just a shell-local variable), so any process the shell subsequently
starts inherits it. Once exported, running `python app.py` from that
same shell session gives the Python process access to both variables.

**Reading environment variables in Python:**
```python
import os

print(os.environ["APP_ENV"])   # raises KeyError if APP_ENV is not set
print(os.getenv("PORT"))       # returns None if PORT is not set, instead of raising
```

`os.environ` is a mapping (dictionary-like object) representing the
current process's entire environment. Accessing it with `[...]`
(square brackets) behaves like a regular dictionary — a missing key
raises `KeyError`. `os.getenv(name, default=None)` is the safer,
more forgiving alternative: it returns `None` (or your chosen
`default`) instead of raising, when the variable isn't set.

```python
import os

# raises KeyError if PORT is missing — appropriate when the value is REQUIRED
port_str = os.environ["PORT"]

# returns "8000" if PORT is missing — appropriate when a DEFAULT is acceptable
port_str = os.getenv("PORT", "8000")

# returns None if PORT is missing — appropriate when you need to check for absence explicitly
port_str = os.getenv("PORT")
if port_str is None:
    raise RuntimeError("PORT is required")
```

**When to use which:** use `os.environ["NAME"]` (or `os.environ.get`
with your own explicit `None`-check, as shown above) when a variable
is **required** and its absence should be treated as a startup error;
use `os.getenv("NAME", default)` when a **sensible default** genuinely
exists. Reaching for `os.getenv()` everywhere, with a default supplied
"just in case," is a common way required configuration silently
becomes optional (§4, §27) — this choice should be made deliberately,
per variable, not out of habit.

## 3. Environment Variable Types

**Every environment variable value is a string — always, with no
exception.** The operating system's environment mechanism has no
concept of integers, booleans, or lists; it only ever stores and
retrieves text.

```bash
export PORT=8000
```

```python
import os

value = os.getenv("PORT")
print(type(value), repr(value))   # <class 'str'> '8000'
```

`"8000"` is a string of four characters, not the integer `8000` — this
is exactly the same "everything arrives as a string" principle
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
§5 established for `sys.argv`, now applying to environment variables
for the identical underlying reason (the OS only ever deals in text
for both).

**Safe conversion to `int`:**
```python
port = int(os.getenv("PORT", "8000"))
```

This works — but blindly converting can fail in a very specific way:
if `PORT` is set to something that isn't a valid integer (a typo, an
empty string, accidentally quoted text), `int(...)` raises
`ValueError`, and if that's never anticipated, the program crashes
with an unhelpful traceback instead of a clear, actionable error.

```python
import os


def get_port(default: int = 8000) -> int:
    raw = os.getenv("PORT")
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"PORT must be an integer, got {raw!r}") from None
```

**Safe conversion to `float`:**
```python
def get_threshold(default: float = 0.5) -> float:
    raw = os.getenv("THRESHOLD")
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        raise ValueError(f"THRESHOLD must be a number, got {raw!r}") from None
```

**Lists**, where an environment variable represents multiple values,
are conventionally represented as a delimited string (commonly comma-
separated), split manually:
```python
def get_allowed_hosts() -> list[str]:
    raw = os.getenv("ALLOWED_HOSTS", "")
    return [item.strip() for item in raw.split(",") if item.strip()]
```

**Booleans** are dangerous enough to get their own numeric type *and*
their own full section — §14 covers exactly why `bool("false")` is a
trap here too, for the same underlying reason
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
§65 diagnosed for `argparse`'s `type=bool`.

The single rule underlying this entire section: **never assume an
environment variable already has the type your program needs.**
Convert explicitly, and handle the conversion failing explicitly — the
same discipline this whole chapter applies to every source of external
input, not just environment variables.

## 4. Configuration Defaults

A **default** is the value a program uses when a specific
configuration setting was not explicitly supplied. Choosing whether a
setting *should* have a default — and if so, what it should be — is a
real design decision with real consequences, not a formality.

- **Required configuration** — no default exists that would be safe or
  meaningful; the program cannot reasonably proceed without an
  explicit value (a database connection string; the input file a data-
  processing CLI is meant to process).
- **Optional configuration** — a sensible default genuinely exists,
  and using it is a reasonable, unsurprising choice if nothing else is
  specified (a log level defaulting to `INFO`; a `--workers` count
  defaulting to `1`).
- **Sensible defaults** are ones a reasonable user would expect and
  that cause no harm if silently applied — `format=json` for an
  output-format setting, `timeout=30` seconds for a network call.
- **Invalid or dangerous defaults** are the failure mode to avoid —
  silently defaulting a required security setting (`DEBUG = True`,
  `verify_ssl = False`) "just so the program runs" can turn a missing-
  configuration bug into a serious, silent production incident (§23).

**Fail-fast configuration** means: when a required setting is missing
or invalid, the program should refuse to start (or refuse to proceed
past its configuration step) **immediately, with a clear error** —
rather than limping along with a guessed value and failing
confusingly, much later, somewhere unrelated in the code.

```python
import os
import sys


def get_database_url() -> str:
    value = os.getenv("DATABASE_URL")
    if not value:
        print("error: DATABASE_URL environment variable is required", file=sys.stderr)
        raise SystemExit(4)   # matches the "configuration problem" convention from §07's chapter
    return value
```

When should a program **use a default**, **reject startup**, **warn**,
or **raise an error**?

| Situation | Response |
|---|---|
| A setting has a genuinely safe, unsurprising default | Use the default silently |
| A setting has a default, but using it is unusual enough to be worth knowing about | Use the default, and log a `WARNING` (§25) that it's in effect |
| A setting is required and missing | Fail fast — refuse to start, with a clear message and a meaningful exit code |
| A setting is present but invalid (wrong type, out of range) | Fail fast — never silently substitute a default for a value that *was* provided but is wrong |

That last row matters: a value that was **provided but invalid** is a
different situation from a value that was **never provided at all** —
silently falling back to a default when the user *did* set something
(just set it incorrectly) hides a real mistake instead of surfacing
it.

## 5. Secrets and Environment Variables

Environment variables are the most common way real applications
receive **secrets** — API keys, database credentials, authentication
tokens, and passwords — because they keep sensitive values **out of
source code** (which is typically version-controlled, shared, and
long-lived) and **out of command-line arguments** (which, per
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
§73, can be visible to other users on the same system while the
process runs).

```python
import os

api_key = os.environ["API_KEY"]
```

The rules that follow directly from this:

- **Never hard-code secrets** in source code — not even "temporarily,"
  since temporary code has a well-earned reputation for outliving its
  intended lifespan, and version control remembers every value ever
  committed, even after it's later removed.
- **Never commit secrets** to version control. A `.gitignore` entry for
  any file that might contain real secret values (most commonly
  `.env`, §6) is a baseline precaution, not a guarantee — a secret
  committed once, even briefly, should generally be considered
  compromised and rotated, since a single push can be enough for it to
  reach a remote history.
- **`.env` files** are a common local-development convenience,
  covered fully in §6.
- **Secret managers** — dedicated external systems (cloud-provider
  secret stores, dedicated secrets-management services) — exist for
  production environments needing stronger guarantees than plain
  environment variables provide: access auditing, rotation, and
  fine-grained permissions. This chapter introduces the *concept* only;
  it is not a tutorial for any specific service.
- **Environment variables are not automatically a perfect secret-
  management system.** They are a meaningful improvement over hard-
  coding, but they have real limitations worth knowing: they can be
  visible to other processes with sufficient privilege on the same
  machine (via `/proc/<pid>/environ` on Linux, for a process you have
  permission to inspect); they are commonly captured, by accident, in
  crash reports, debugging dumps, or — directly connecting to
  [08-logging-versus-print.md](08-logging-versus-print.md)'s §18 — in
  logs, if a program is careless about what it logs.

**Safe handling and logging**, extending §08's security section
directly:
```python
import logging

logger = logging.getLogger(__name__)

# UNSAFE — never do this
logger.info("Connecting with API key %s", api_key)

# SAFE — confirm presence and identity without exposing the value
logger.info("API key configured: %s", "yes" if api_key else "no")
```

## 6. `.env` Files

A **`.env` file** is a plain text file, conventionally named `.env`,
placed in a project's root directory, containing `KEY=value` pairs —
a simple, local convention for keeping a development environment's
configuration (often including secrets meant only for local, non-
production use) in one place, without needing to `export` a long list
of variables manually in every new terminal session.

```
# .env (example contents — never commit real secrets like this)
APP_ENV=development
PORT=8000
DATABASE_URL=postgresql://localhost:5432/dev_db
API_KEY=dev-only-fake-key
```

**The crucial distinction: a `.env` file is not, by itself, the same
thing as the OS environment.** Python's standard library has **no
built-in support for reading `.env` files** — nothing in `os` or
elsewhere in the standard library will automatically notice a `.env`
file's existence or load its contents into `os.environ`. A `.env` file
is just a text file; something has to actually read it and set the
corresponding environment variables (or otherwise make those values
available to your program) for it to have any effect at all.

**`python-dotenv`** is a small, widely used **third-party** package
that fills exactly this gap — it reads a `.env` file and loads its
key/value pairs into `os.environ` (or returns them as a dictionary),
so the rest of your code can keep using the same `os.getenv()` calls
regardless of whether a value came from a real exported environment
variable or from a local `.env` file:

```python
# conceptual usage of the third-party python-dotenv package — NOT part of the standard library
from dotenv import load_dotenv
load_dotenv()   # reads .env in the current directory and loads it into os.environ

import os
print(os.getenv("PORT"))
```

This chapter deliberately keeps this section conceptual rather than a
tutorial for that specific package — the important standard-library-
independent ideas are: (1) a `.env` file is a *local development
convenience*, not a production configuration mechanism (production
deployments typically set real environment variables directly, through
whatever platform they run on); (2) **a `.env` file containing real
secrets should generally not be committed to version control** — a
`.gitignore` entry for `.env` is standard practice; and (3) a
**`.env.example`** file (committed, with placeholder or dummy values
only) is the standard way to document *which* variables a project
expects, without exposing any actual secret:

```
# .env.example (safe to commit)
APP_ENV=development
PORT=8000
DATABASE_URL=postgresql://localhost:5432/dev_db
API_KEY=
```

## 7. Configuration Sources and Precedence

Real applications commonly accept configuration from **more than one
source at once** — and when they do, they need an explicit,
documented rule for what happens when two sources disagree. This is
**precedence**.

A realistic, common hierarchy, from lowest to highest priority (each
layer can override everything below it):

```
built-in defaults        (lowest priority — hardcoded in the program itself)
        ↓ overridden by
configuration file         (project- or environment-specific settings)
        ↓ overridden by
environment variables        (deployment-specific settings)
        ↓ overridden by
CLI arguments                  (highest priority — specific to THIS invocation)
```

```python
import argparse
import os


def resolve_port(cli_value: int | None) -> int:
    if cli_value is not None:
        return cli_value                                  # CLI wins if given
    env_value = os.getenv("PORT")
    if env_value is not None:
        return int(env_value)                              # then environment
    return 8000                                              # otherwise, the built-in default
```

This is exactly the precedence
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
§59 introduced conceptually, worked out here as actual, runnable
code. The specific order above (CLI highest, defaults lowest) is a
*common, sensible* choice — not a law: it reflects "the more specific
to this one run, the higher the priority," since a CLI flag typed for
this exact invocation is a stronger, more deliberate signal than a
general environment-wide setting.

**Precedence must be explicit and documented**, because the
alternative — an undocumented, ad hoc mix of `os.getenv()` calls
scattered through the codebase, each with its own inconsistent
fallback logic — is a direct, common source of real bugs: a value set
correctly in the environment appears to have no effect because some
unrelated piece of code happens to read a CLI default first; two
different parts of a program disagree about which source should win,
and nobody designed that disagreement on purpose. §27 and §31 return
to this exact failure mode as both a common mistake and a debugging
scenario.

## 8. CLI Input Validation

Connecting directly to
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md):
**parsing is not the same operation as validation**, even though
`argparse` performs a useful amount of both at once.

- **Syntax validation** — did the user provide something argparse can
  even make sense of as an argument? (a required flag present; a value
  where one was expected). This is what `parse_args()` itself checks.
- **Semantic validation** — is the value, once parsed, actually
  *meaningful and acceptable* for what the program needs? (is this
  path an existing, readable file; is this integer within a sensible
  range; does this string match one of a small set of valid modes?)
  argparse can express some of this directly, and needs help
  (custom `type=` functions, or post-parse checks) for the rest.

argparse features that perform real validation, not just parsing,
directly reusing
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
own vocabulary:

```python
import argparse
from pathlib import Path


def existing_file(value: str) -> Path:
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"not a file: {path}")
    return path


parser = argparse.ArgumentParser()
parser.add_argument("input", type=existing_file, help="Path to an existing input file")
parser.add_argument("--port", type=int, choices=range(1, 65536), metavar="PORT", default=8000)
parser.add_argument("--format", choices=["json", "csv"], required=True, default=argparse.SUPPRESS)
```

- **`type=`** — converts *and* can validate (§08's chapter's §14–§15),
  raising `argparse.ArgumentTypeError` for a value that parses but is
  unacceptable.
- **`choices=`** — restricts to a known, closed set of valid values.
- **`required=`** — forces an optional argument's presence.
- **`default=`** — the fallback when an optional argument is omitted.
- **`nargs=`** — how many values an argument consumes.
- **`metavar=`, `help=`** — documentation, not validation, but part of
  making validation failures easy for a user to actually fix.

argparse **cannot**, by itself, express validation that depends on
**more than one argument at once** (`--output` required only if
`--format=csv`) — that's exactly the cross-argument, post-parse
validation
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
§43–§44 covered, using `parser.error()`. This chapter's job is to
generalize that same idea — parse, then validate, then normalize —
beyond just CLI arguments, to environment variables, files, and
structured data as well.

## 9. Validation vs. Sanitization vs. Normalization

Three genuinely different operations, routinely and dangerously
conflated:

- **Validation** — *"Is this input acceptable?"* A yes/no (or
  accept/reject) decision. Validation never changes the input; it only
  decides whether to accept it.
  ```python
  def is_valid_port(value: int) -> bool:
      return 1 <= value <= 65535
  ```
- **Normalization** — *"Can we convert equivalent representations into
  one consistent representation?"* Takes an already-acceptable input
  and reshapes it into the program's preferred canonical form, with no
  change in *meaning*.
  ```python
  def normalize_environment_name(value: str) -> str:
      return value.strip().lower()   # "Production", " PRODUCTION ", "production" all become "production"
  ```
- **Sanitization** — *"Can we safely remove or transform unwanted
  content?"* Takes input that may contain something unsafe or
  unwanted and strips or alters it — a fundamentally different goal
  from validation: sanitization doesn't ask "is this acceptable
  as-is," it actively **changes** the input to make it acceptable (or
  safer), sometimes silently discarding part of it.
  ```python
  def sanitize_filename(name: str) -> str:
      return "".join(ch for ch in name if ch.isalnum() or ch in "-_.")
  ```

Why confusing these matters in practice: **sanitizing when you should
validate** can silently accept and "fix" input that should have been
rejected outright, hiding a real problem from whoever supplied it (a
config value with a typo gets silently mangled into something
technically valid but not what was intended); **validating when you
need to normalize** leaves your program handling multiple equivalent
representations of the same value inconsistently throughout its logic,
instead of converting to one form once, at the boundary; **skipping
sanitization when it's genuinely needed** (§23–§24) can leave a real
security gap where "this value happens to be well-formed" was
mistaken for "this value is safe to use in a specific dangerous
context" (a filename, a shell command, a query).

The right order, generally: **validate first** (reject clearly
unacceptable input outright); **normalize** what's accepted (put it in
one consistent internal form); **sanitize** only the specific, narrow
cases where a value's *content* — not its overall validity — poses a
risk in how it will subsequently be used.

## 10. Boundary Validation

The **boundary-validation principle**, stated as the load-bearing rule
of this entire chapter:

> **Validate untrusted input once, at the boundary where it enters
> your system. Everywhere else, the rest of the program operates on
> already-validated, already-normalized, trusted values.**

"The boundary" includes every place external, untrusted data enters
your program: CLI arguments, environment variables, file contents,
JSON documents, CSV rows, API request bodies, and direct user input
(typed at a prompt). None of these should be trusted just because they
arrived — every one of them could be missing, malformed, unexpected in
type or shape, or (§23–§24) actively adversarial.

**Bad — raw, unvalidated input flows everywhere:**
```python
def process(raw_config: dict):
    port = raw_config["port"]              # could be a string, could be missing, could be negative
    connect(host=raw_config["host"], port=port)   # validation, if any, happens deep inside connect()
    # ... twenty more places in the codebase, each trusting raw_config blindly ...
```

**Better — a clear pipeline, validated once, near the entry point:**
```
raw input (CLI / environment / file / JSON / CSV / user input)
        ↓
     PARSE            (turn raw text into candidate Python values)
        ↓
    VALIDATE           (accept or reject — is this acceptable at all?)
        ↓
   NORMALIZE            (one consistent internal representation)
        ↓
TRUSTED INTERNAL REPRESENTATION   (e.g. a validated AppConfig, §21)
        ↓
   BUSINESS LOGIC          (operates on trusted values — no re-validation needed)
```

```python
@dataclass(frozen=True)
class AppConfig:
    host: str
    port: int

def build_config(raw: dict) -> AppConfig:
    host = raw.get("host", "localhost")
    port_raw = raw.get("port", "8000")
    try:
        port = int(port_raw)
    except (TypeError, ValueError):
        raise ValueError(f"port must be an integer, got {port_raw!r}") from None
    if not (1 <= port <= 65535):
        raise ValueError(f"port must be between 1 and 65535, got {port}")
    return AppConfig(host=host, port=port)

def connect(config: AppConfig):
    ...   # config.port is GUARANTEED to already be a valid int in range — no re-checking needed here
```

The payoff, concretely: `connect()` (and every other function deeper
in the program) never needs to re-check whether `port` is an integer,
or in range — that work happened exactly once, at `build_config()`,
and every caller downstream can simply trust `AppConfig`'s fields.
This is what §21–§22 build into a full, reusable pattern.

## 11. Common Validation Types

A working vocabulary of the standard kinds of validation, each
returning to specific sections below for full treatment:

| Type | Question it answers | Example |
|---|---|---|
| **Type validation** | Is this the right kind of value? | Is `port` actually an `int`, not a `str`? |
| **Presence validation** | Is this required value actually here? | Is `DATABASE_URL` set at all? |
| **Range validation** | Is this numeric value within acceptable bounds? | Is `1 <= port <= 65535`? |
| **Length validation** | Is this collection/string an acceptable size? | Is a username between 3 and 30 characters? |
| **Format validation** | Does this value match an expected shape? | Does this look like a valid email address? |
| **Enum/choice validation** | Is this one of a known, fixed set of values? | Is `format` one of `"json"`/`"csv"`? |
| **Cross-field validation** | Is this combination of values consistent? | Is `end_date` after `start_date`? |
| **Uniqueness validation** | Does this value collide with something that must be unique? | Is this record's `id` already used? |
| **Path validation** | Does this filesystem path make sense for its intended use? | Is `input_path` an existing, readable file? |
| **File existence validation** | Does the named file actually exist (or, for output, *not* already exist)? | `Path(x).is_file()` |
| **Extension validation** | Does this file have an expected extension? | Does `output_path` end in `.json`? |
| **Encoding considerations** | Can this data actually be decoded/read as expected? | Does this file decode cleanly as UTF-8 (§05)? |

Sections 12–16 work through Python implementations of the most common
of these — string, numeric, boolean, path/file, and structured-data
(JSON/CSV) validation — in depth.

## 12. String Validation

The recurring gotchas, and how to handle each correctly:

**Empty strings and whitespace:**
```python
def validate_name(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("name must not be empty or whitespace-only")
    return stripped
```
`.strip()` removes leading/trailing whitespace; checking `if not
stripped:` catches both a genuinely empty string (`""`) and a
whitespace-only one (`"   "`) in one check, since both become falsy
once stripped.

**Length checks:**
```python
def validate_username(value: str) -> str:
    value = value.strip()
    if not (3 <= len(value) <= 30):
        raise ValueError(f"username must be 3-30 characters, got {len(value)}")
    return value
```

**Allowed characters:**
```python
def validate_identifier(value: str) -> str:
    if not all(ch.isalnum() or ch == "_" for ch in value):
        raise ValueError(f"identifier may only contain letters, digits, and underscores: {value!r}")
    return value
```

**Case normalization**, distinguishing this from validation (§9):
```python
def normalize_environment_name(value: str) -> str:
    return value.strip().lower()

VALID_ENVIRONMENTS = {"development", "staging", "production"}

def validate_environment(value: str) -> str:
    normalized = normalize_environment_name(value)
    if normalized not in VALID_ENVIRONMENTS:
        raise ValueError(f"unknown environment {value!r}; expected one of {sorted(VALID_ENVIRONMENTS)}")
    return normalized
```

**When regular expressions are appropriate, and when they're not:**
the `re` module is the right tool when a value's *shape* genuinely
needs pattern matching — a version string (`"1.2.3"`), a simple format
check (does this look roughly like an email address). It is
**unnecessary, and often the wrong tool**, for checks that a plain
method call already expresses more clearly and efficiently:
`value.isdigit()` beats `re.match(r"^\d+$", value)`; `value in
{"json", "csv"}` beats a regex alternation. Reach for `re` when the
pattern is genuinely about *shape* (repeated structure, optional
parts, alternation across meaningfully different forms), not as a
default first tool for every string check.

```python
import re

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

def validate_version(value: str) -> str:
    if not VERSION_PATTERN.match(value):
        raise ValueError(f"version must look like X.Y.Z, got {value!r}")
    return value
```

## 13. Numeric Validation

**Conversion, with a clear failure path:**
```python
def parse_int(value: str, field_name: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{field_name} must be an integer, got {value!r}") from None
```

**Minimum/maximum, inclusive vs. exclusive boundaries** — be explicit
about which you mean, since off-by-one errors here are common and
consequential:
```python
def validate_port(value: int) -> int:
    if not (1 <= value <= 65535):   # inclusive on both ends
        raise ValueError(f"port must be between 1 and 65535 (inclusive), got {value}")
    return value

def validate_probability(value: float) -> float:
    if not (0.0 <= value < 1.0):    # inclusive lower bound, EXCLUSIVE upper bound
        raise ValueError(f"probability must be in [0.0, 1.0), got {value}")
    return value
```

**Invalid numeric input** — `int("abc")` and `float("abc")` both raise
`ValueError`; `int("3.5")` also raises `ValueError` (an int conversion
does not silently truncate a decimal string) — worth knowing
explicitly, since it's a common source of confusion (`int(float("3.5"))`
works; `int("3.5")` directly does not).

**`NaN` and infinity**, at the level this chapter needs: `float("nan")`
and `float("inf")` are both **valid float conversions** in Python —
they will not raise `ValueError` — but they are very likely *not*
acceptable values for most real configuration or business fields (a
port number, a price, a percentage). If a numeric field must exclude
these, check explicitly:
```python
import math

def validate_finite(value: float, field_name: str) -> float:
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{field_name} must be a finite number, got {value}")
    return value
```

## 14. Boolean Configuration

Exactly the same trap
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
§65 diagnosed for `argparse`'s `type=bool` applies here, for the
identical underlying reason:

```python
bool("false")   # True  — any non-empty string is truthy in Python
```

An environment variable set to `"false"`, `"no"`, or `"0"`, if passed
through Python's built-in `bool()`, is silently treated as **truthy**
— a dangerous, easy-to-miss bug for exactly the settings (feature
flags, `DEBUG` toggles) where getting this wrong matters most.

**Correct parsing**, accepting the common conventional spellings:

```python
def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"expected a boolean value (true/false), got {value!r}")


def get_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return parse_bool(raw)
```

```bash
export DEBUG=false
```
```python
debug = get_bool_env("DEBUG", default=False)   # correctly False
```

This reusable `parse_bool()` function is worth keeping as a small,
independent, well-tested utility (§20, §26) — every boolean
configuration value in a real application should go through it (or an
equivalent), never through Python's raw `bool(some_string)`.

## 15. Path and File Validation

Connecting directly to
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md):
`pathlib.Path` objects, once obtained from CLI arguments or
environment variables (both arrive as strings first — wrap with
`Path(...)`), support exactly the checks this section needs.

```python
from pathlib import Path

path = Path("data.csv")
path.exists()      # does anything exist at this path at all?
path.is_file()      # does it exist AND is it a regular file (not a directory)?
path.is_dir()        # does it exist AND is it a directory?
path.suffix           # ".csv" — the file extension, including the leading dot
```

**Input path validation** — the file must already exist and be usable:
```python
def validate_input_file(path: Path) -> Path:
    if not path.exists():
        raise ValueError(f"input file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"input path is not a file: {path}")
    return path
```

**Output path validation** — often the *opposite* concern: avoiding an
accidental overwrite, or ensuring the destination directory actually
exists:
```python
def validate_output_path(path: Path, *, allow_overwrite: bool = False) -> Path:
    if path.exists() and not allow_overwrite:
        raise ValueError(f"output file already exists (use --force to overwrite): {path}")
    if not path.parent.exists():
        raise ValueError(f"output directory does not exist: {path.parent}")
    return path
```

**Extension validation:**
```python
def validate_csv_path(path: Path) -> Path:
    if path.suffix.lower() != ".csv":
        raise ValueError(f"expected a .csv file, got {path.suffix or '(no extension)'}: {path}")
    return path
```

**Directory creation**, when a program should create a missing output
directory rather than reject it — a deliberate choice, not a default:
```python
def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
```

**Permissions**, at a conceptual level: even a path that exists and has
the right type (`is_file()`, `is_dir()`) might still not be **readable**
or **writable** by the current process — a permission problem
Python typically surfaces as `PermissionError` only when you actually
attempt to open the file (§19), not from `exists()`/`is_file()` alone.
Validating "this path looks right" and "this path is actually usable"
are related but distinct checks; the second is often only fully
confirmed at the point of actual use.

**Path-related errors worth anticipating**, connecting to §19:
`FileNotFoundError` (the path doesn't exist when you try to open it —
even if you checked `exists()` moments earlier, since the filesystem
can change between the check and the actual open, a real if uncommon
race condition worth being aware of), `PermissionError` (exists, but
not accessible), `IsADirectoryError` (expected a file, got a
directory).

## 16. JSON/CSV Input Validation

Extending
[03-csv-files.md](03-csv-files.md) and
[04-json-and-serialization.md](04-json-and-serialization.md) directly
with the validation vocabulary from §9–§11.

**Syntactic validity** is the first, narrowest check — can this even
be parsed at all:
```python
import json

def parse_json_line(line: str) -> dict:
    try:
        return json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
```

**Shape/schema validation** comes next — assuming it parsed, is its
*structure* what the program actually expects:
```python
def validate_record_shape(record: object) -> dict:
    if not isinstance(record, dict):
        raise ValueError(f"expected a JSON object, got {type(record).__name__}")
    return record
```

**Required fields, field types, missing fields:**
```python
REQUIRED_FIELDS = {"id": int, "name": str, "value": float}

def validate_record_fields(record: dict) -> dict:
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in record:
            raise ValueError(f"missing required field: {field!r}")
        if not isinstance(record[field], expected_type):
            actual = type(record[field]).__name__
            raise ValueError(f"field {field!r} must be {expected_type.__name__}, got {actual}")
    return record
```

**Unexpected fields** — sometimes worth rejecting (a strict schema),
sometimes worth simply ignoring (a lenient, forward-compatible schema)
— a deliberate design choice, not a default:
```python
ALLOWED_FIELDS = {"id", "name", "value"}

def reject_unknown_fields(record: dict) -> dict:
    unknown = set(record) - ALLOWED_FIELDS
    if unknown:
        raise ValueError(f"unexpected field(s): {sorted(unknown)}")
    return record
```

**CSV field validation**, combining `csv.DictReader` with per-row
checks:
```python
import csv
from pathlib import Path


def validate_csv_row(row: dict, line_number: int) -> dict:
    if not row.get("id"):
        raise ValueError(f"line {line_number}: missing 'id'")
    try:
        row["value"] = float(row["value"])
    except (KeyError, ValueError):
        raise ValueError(f"line {line_number}: invalid or missing 'value'") from None
    return row


def read_valid_rows(path: Path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):  # header occupies line 1
            yield validate_csv_row(row, line_number)
```

This chapter deliberately does not introduce a heavy schema-validation
framework — the standard-library patterns above (a small dictionary of
expected field types, a loop, and a clear `ValueError`) are sufficient
for the great majority of CLI and data-processing validation needs,
and keep the validation logic itself transparent and easy to test
(§26) without an added dependency.

## 17. Fail-Fast vs. Error Collection

Two genuinely different validation *strategies*, appropriate in
different situations:

**Fail-fast** — stop immediately at the first invalid, critical input:
```python
def load_config(raw: dict) -> AppConfig:
    if "database_url" not in raw:
        raise ValueError("database_url is required")   # stop immediately — nothing else matters yet
    ...
```
Appropriate for **configuration** and for any input where proceeding
with a known-bad critical value would be actively harmful or
meaningless — there is no reasonable way to "partially" start a
program with a missing database connection string.

**Error collection** — process everything possible, gathering every
problem found along the way, before deciding what to do:
```python
def validate_all_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    valid_rows = []
    errors = []
    for line_number, row in enumerate(rows, start=2):
        try:
            valid_rows.append(validate_csv_row(row, line_number))
        except ValueError as exc:
            errors.append(str(exc))
    return valid_rows, errors
```
Appropriate for **batch data processing** — a CSV with ten thousand
rows, three of which are malformed, is far more useful to a user as
"9,997 valid, 3 rejected, here's exactly what was wrong with each"
than as an immediate crash on the very first bad row, forcing a
frustrating fix-one-error-at-a-time cycle. This is exactly the pattern
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)'s
§61 mini-project and
[08-logging-versus-print.md](08-logging-versus-print.md)'s §25 mini-
project both applied, without naming it explicitly until now.

The deciding question: **is this input a small number of critical,
all-or-nothing settings** (fail-fast is right), **or a large batch of
independent, individually-skippable records** (error collection is
right)? A production system frequently uses *both*, in different
places — fail-fast for its own configuration at startup, error
collection while processing the data that configuration points it at.

## 18. Error Messages

The quality of a validation error message is, in practice, the
difference between a user who fixes their mistake in ten seconds and
one who has to read your source code to understand what happened.

**Bad:**
```
Invalid input
```

**Better:**
```
PORT must be an integer between 1 and 65535, got 'eight-thousand'
```

A good validation error message names: **which field/input** was
wrong (`PORT`); **what was expected** (an integer between 1 and
65535); and, where safe, **what was actually received** (`'eight-
thousand'`) — enough for the person reading it to fix the problem
without guessing.

```python
def validate_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise ValueError(f"PORT must be an integer, got {value!r}") from None
    if not (1 <= port <= 65535):
        raise ValueError(f"PORT must be between 1 and 65535, got {port}")
    return port
```

**Avoiding secret leakage** — the one important exception to "show
what was received": never echo a secret value back in an error
message, even when it's invalid.
```python
# UNSAFE — echoes the actual (invalid) secret value into an error message
raise ValueError(f"API_KEY is invalid: {api_key!r}")

# SAFE — confirms the problem without exposing the value
raise ValueError("API_KEY is set but does not match the expected format")
```

**User-friendly CLI errors vs. developer diagnostics** — a distinction
directly connecting to
[08-logging-versus-print.md](08-logging-versus-print.md): the message
a user sees on stderr (or via `parser.error()`) should be clear and
actionable; full diagnostic detail (a stack trace, internal state)
belongs in a log file at `DEBUG`/`ERROR` level (via
`logger.exception()`), not necessarily in the user-facing message
itself. Connecting to
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md):
a validation failure should produce both a clear stderr message *and*
a specific, meaningful exit code (§25's own example convention:
`3 = input/data problem`, `4 = configuration problem`).

## 19. Exceptions and Validation

The standard exceptions most relevant to validation, and what each
signals:

| Exception | Raised when |
|---|---|
| `ValueError` | A value has the right *type* but an unacceptable *value* (an out-of-range int, an unparseable string) |
| `TypeError` | A value is fundamentally the wrong *type* for an operation |
| `FileNotFoundError` | A path was expected to exist (for reading) but doesn't |
| `PermissionError` | The process lacks permission to access a path it otherwise correctly identified |
| `KeyError` | A required dictionary key (e.g. a JSON field) is missing |
| `json.JSONDecodeError` | Text that was expected to be valid JSON could not be parsed |
| `argparse.ArgumentError` | Raised internally by argparse itself for a parsing failure (rare to catch directly — usually surfaces as `SystemExit` instead, per §06's chapter) |

**When to raise:** whenever your own validation function determines
input is unacceptable — raise a specific, well-chosen exception
(usually `ValueError` for "wrong value," occasionally a custom
exception type for a large application) with a clear message (§18).

**When to catch:** at the **boundary** — the specific point where you
have enough context to produce a clear, useful error and decide what
to do next (report and exit; skip and continue; retry). Catching a
`ValueError` deep inside a validator itself, only to immediately
re-raise a *different*, clearer `ValueError`, is the standard pattern
for converting a low-level error into a boundary-appropriate one
(exactly what §3's `get_port()` example did with `int(...)`'s raw
`ValueError`).

**When *not* to catch:** avoid `except Exception:` (or a bare
`except:`) as a default reflex — it catches genuinely unexpected bugs
right alongside the specific failure modes you actually anticipated,
exactly the mistake
[08-logging-versus-print.md](08-logging-versus-print.md)'s §15 and
§23 warned against. Catch the *specific* exception types you expect
and know how to handle; let anything else propagate (or catch it once,
at a true top-level boundary, log it with `logger.exception()`, and
fail cleanly — never silently).

```python
# GOOD — converts a low-level error into a clear, boundary-appropriate one
def load_port_from_env() -> int:
    raw = os.environ["PORT"]              # KeyError if missing — let it propagate; that's a real bug in setup
    try:
        return int(raw)                    # ValueError if malformed
    except ValueError:
        raise ValueError(f"PORT must be an integer, got {raw!r}") from None
```

## 20. Custom Validation Functions

The pattern this entire chapter has been building toward, made
explicit: small, focused, reusable **validator functions**, each doing
exactly one job.

```python
def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise ValueError(f"port must be an integer, got {value!r}") from None
    if not (1 <= port <= 65535):
        raise ValueError(f"port must be between 1 and 65535, got {port}")
    return port


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"expected a boolean value, got {value!r}")


def validate_input_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"input file does not exist: {path}")
    return path
```

What makes each of these worth writing this way, deliberately:

- **Single responsibility** — each function validates exactly one
  thing; combining checks happens by *calling several validators*, not
  by writing one large function that does everything.
- **Clear return types** — every validator returns the *converted,
  validated* value (an `int`, a `bool`, a `Path`), never the raw input
  unchanged — the caller receives something already trustworthy.
- **Predictable exceptions** — every validator raises the same,
  well-understood exception type (`ValueError`, by convention
  throughout this chapter) with a clear message, so callers can catch
  consistently regardless of which specific validator failed.
- **Testability** — each validator is a plain function of simple
  inputs to simple outputs, trivially unit-testable in isolation with
  no CLI, no environment, no file I/O involved at all (§26).
- **Reuse** — the exact same `parse_port()` can validate a CLI
  argument (as a `type=` function, per
  [06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)'s
  §15), an environment variable (§3), or a value loaded from a config
  file — one implementation, three call sites, no duplicated logic to
  keep in sync.

## 21. Configuration Objects

Passing many independent configuration values around individually —
`connect(host, port, timeout, use_ssl, retries, ...)` — scales badly:
every function that needs *any* configuration ends up needing a long,
fragile, easily-misordered parameter list, and adding one new setting
means touching every function signature in between.

The fix: a single, centralized **configuration object**, most commonly
a `dataclass`.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    environment: str
    port: int
    debug: bool
```

- **`@dataclass`** generates `__init__`, `__repr__`, and `__eq__`
  automatically from the declared fields — no boilerplate needed.
- **`frozen=True`** makes instances **immutable** — once created, a
  `Config`'s fields cannot be reassigned (`config.port = 9000` raises
  `dataclasses.FrozenInstanceError`). This is a deliberate design
  choice: configuration, once validated and built, should not be
  quietly mutated somewhere deep in the program — a bug that changes
  `config.port` at runtime should fail loudly, not silently succeed.

**Centralized configuration**: every part of the program that needs
configuration receives (or is passed) the *same* `AppConfig` instance,
rather than each independently reading `os.environ` or parsing
arguments itself. **Validated configuration**: by the time an
`AppConfig` exists at all, every one of its fields has already passed
through the parse → validate → normalize pipeline (§10, §22) — nothing
downstream needs to re-check `config.port`'s type or range. **Clean
dependency passing**: functions declare exactly what they need
(`def connect(config: AppConfig)`, or even more narrowly, `def
connect(host: str, port: int)` pulled from the config at the call
site) — explicit, typed, and easy for both a human reader and a type
checker to follow.

## 22. Configuration Validation

The complete flow this chapter has been assembling piece by piece,
now shown end to end:

```
environment / CLI / config file
        ↓
      PARSE              (os.getenv, argparse, or a config-file reader — raw strings/values)
        ↓
    VALIDATE               (parse_port, parse_bool, validate_input_file, ... — §12–§20)
        ↓
   NORMALIZE                 (consistent casing, stripped whitespace, canonical form — §9)
        ↓
     AppConfig                  (one immutable, trusted object — §21)
        ↓
     application

```

```python
import argparse
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    environment: str
    port: int
    debug: bool
    input_file: Path


def build_config(argv: list[str] | None = None) -> AppConfig:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args(argv)

    environment = normalize_environment_name(os.getenv("APP_ENV", "development"))
    validate_environment(environment)

    port = args.port if args.port is not None else parse_port(os.getenv("PORT", "8000"))
    debug = parse_bool(os.getenv("DEBUG", "false"))
    input_file = validate_input_file(args.input_file)

    return AppConfig(environment=environment, port=port, debug=debug, input_file=input_file)
```

The reason **the application should receive validated configuration,
rather than repeatedly reading `os.environ` throughout its own code**,
follows directly from everything above: every additional place that
calls `os.getenv("PORT")` directly is another place that has to
remember to convert, validate, and handle a missing/invalid value
correctly — and another place that can quietly get it wrong, or
disagree with how some *other* part of the code handles the exact same
variable. Reading configuration in **exactly one place**
(`build_config()`), producing **one validated, immutable object**, and
passing *that* explicitly to everything else, closes off this entire
category of bug at the source.

## 23. Security Considerations

Extending
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)'s
§73 and
[08-logging-versus-print.md](08-logging-versus-print.md)'s §18
directly into the configuration/validation layer, defensively:

- **Secrets** — never hard-coded, never logged, never echoed back in
  error messages (§5, §18).
- **Command injection**, conceptually: if a program ever builds a
  shell command by concatenating untrusted input directly into a
  string, an attacker-controlled value could inject additional shell
  syntax. §24 covers this concretely.
- **Path traversal**, conceptually: an input path like
  `"../../etc/passwd"` or an absolute path where only a relative one
  inside a specific directory was intended can let untrusted input
  read or write files well outside where the program was meant to
  operate.
  ```python
  def validate_within_directory(path: Path, allowed_root: Path) -> Path:
      resolved = path.resolve()
      if not resolved.is_relative_to(allowed_root.resolve()):
          raise ValueError(f"path escapes the allowed directory: {path}")
      return resolved
  ```
  (`Path.is_relative_to()` is available from Python 3.9 onward.)
- **Unsafe file paths** more generally — accepting an arbitrary,
  unchecked path from untrusted input and immediately opening it for
  writing is dangerous if that path could point somewhere sensitive;
  validate against an expected location or pattern when the path
  itself comes from an untrusted source.
- **Untrusted input, in general** — every boundary this chapter has
  discussed (CLI, environment, files, JSON, CSV) should be treated as
  potentially wrong, malformed, or adversarial, never assumed benign
  just because it "usually" comes from a trusted colleague or system.
- **Maliciously large input** — a CSV or JSON "record" of unreasonable
  size (a single field containing gigabytes of text) can be used to
  exhaust memory; where input size isn't already bounded by context,
  consider an explicit sanity limit before fully loading a value into
  memory.
- **Log injection**, conceptually: a log message built by directly
  embedding untrusted text (a value from a config file, a CSV field)
  can, in some structured logging pipelines, be crafted to look like a
  *different* log entry, or to break structured (e.g. JSON) log
  parsing downstream — one more reason to prefer `%`-style lazy
  formatting with the untrusted value passed as a distinct argument
  (§08's chapter's §19), rather than blindly interpolating it into the
  message template itself.
- **Unsafe deserialization** — a brief warning, not a full topic:
  Python's `pickle` module (and similarly powerful deserialization
  mechanisms in other libraries) can execute arbitrary code while
  loading data, and must never be used to load data from an untrusted
  source. JSON (§04's chapter) does not have this problem — `json.loads()`
  only ever produces plain Python data structures (dicts, lists,
  strings, numbers, booleans, `None`), never arbitrary code execution
  — which is one of several reasons JSON is the safer default choice
  for untrusted structured input.
- **Never trust external input** is the one-sentence summary of this
  entire chapter, restated once more as this section's closing
  principle.

This section is deliberately **defensive**, not offensive — the goal
is knowing what to guard against and how, not how to construct an
actual attack.

## 24. Input Validation and Injection Risks

A slightly deeper, still foundational, look at the specific risk
patterns §23 named:

**Shell injection** — never build a shell command by concatenating
untrusted input directly into a string passed with `shell=True`:
```python
import subprocess

# UNSAFE — if filename contains e.g. "; rm -rf ~", that's now part of the actual shell command
subprocess.run(f"cat {filename}", shell=True)

# SAFE — arguments passed as a list; no shell parsing of the value occurs at all
subprocess.run(["cat", filename])
```
This directly matches
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)'s
§73 guidance: pass arguments as a list to `subprocess.run()`, never a
single hand-built string with `shell=True`, whenever any part of that
string comes from outside your own program's fixed, trusted code.

**SQL injection**, conceptually (this module does not use a database
directly, but the principle generalizes and is worth knowing by name):
never build a query by concatenating untrusted input directly into SQL
text.
```python
# UNSAFE — conceptual illustration; do not build queries this way
query = f"SELECT * FROM users WHERE name = '{name}'"

# SAFE — parameterized query; the database driver handles the value safely
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```
The general principle behind both examples: **use the safe, structured
API a tool provides for combining a fixed template with untrusted
values (parameterized queries, argument lists) instead of building the
final command/query as one hand-assembled string.** The safe API
exists specifically so the untrusted value is always treated as *data*,
never as additional *syntax*.

**Path traversal** was covered concretely in §23; the same principle —
never assume a path is confined to where you expect just because it
"looks like" a relative path — applies.

**Unsafe command construction**, generalized: any time untrusted text
is about to become part of something that will later be
*interpreted* (a shell command, a query, a template, a regular
expression pattern built from user input), stop and ask whether a
safer, structured alternative exists — in almost every real case,
Python's standard library or a well-established library already
provides one.

## 25. Configuration + Logging

Directly extending
[08-logging-versus-print.md](08-logging-versus-print.md)'s §18 and §25
into this chapter's specific concern — logging the *outcome* of
configuration loading and validation, safely:

```python
import logging

logger = logging.getLogger(__name__)


def build_config(argv=None) -> AppConfig:
    config = _build_config_unlogged(argv)
    logger.info(
        "Configuration loaded: environment=%s port=%d debug=%s",
        config.environment, config.port, config.debug,
    )
    logger.debug("Input file: %s", config.input_file)
    return config
```

**Never log secrets** — restated once more here because configuration
loading is *exactly* the code path most likely to have a secret value
sitting right there in scope, one careless `logger.info(f"config:
{config}")` away from ending up in a log file indefinitely (§5, §18).

```python
# UNSAFE — if AppConfig ever grows an api_key field, this logs it directly
logger.info("Configuration: %s", config)

# SAFE — log only the specific, known-non-sensitive fields
logger.info("Configuration: environment=%s port=%d", config.environment, config.port)
```

**Log the environment name and non-sensitive configuration** — this is
genuinely useful, routine `INFO`-level operational information (which
environment is this process running as; what port did it bind to);
**distinguish configuration errors from runtime errors** — a
configuration error (missing/invalid `PORT`) is a startup-time failure,
appropriately logged (if at all, since the program may not even have
working logging configured yet — §12 of the previous chapter) and
exited from immediately with a specific exit code (§4, §18); a runtime
error (a network call failing mid-run) is a different kind of event,
happening after the program is already up and configured, appropriately
logged through the application's already-established logging setup.

## 26. Testing Configuration and Validation

Every validator and configuration-building function in this chapter is
a plain function of simple inputs to simple outputs (or a raised
exception) — directly testable with pytest, no CLI, no real
environment variables, and no real files required for the validator
tests themselves.

```python
import pytest

from myapp.config import parse_port, parse_bool, validate_input_file


def test_parse_port_valid():
    assert parse_port("8000") == 8000


def test_parse_port_out_of_range():
    with pytest.raises(ValueError, match="between 1 and 65535"):
        parse_port("70000")


def test_parse_port_not_a_number():
    with pytest.raises(ValueError, match="must be an integer"):
        parse_port("eight-thousand")


@pytest.mark.parametrize("raw,expected", [
    ("true", True), ("True", True), ("1", True), ("yes", True), ("on", True),
    ("false", False), ("False", False), ("0", False), ("no", False), ("off", False),
])
def test_parse_bool_valid(raw, expected):
    assert parse_bool(raw) is expected


def test_parse_bool_invalid():
    with pytest.raises(ValueError):
        parse_bool("maybe")


def test_validate_input_file_missing(tmp_path):
    missing = tmp_path / "does-not-exist.csv"
    with pytest.raises(ValueError, match="does not exist"):
        validate_input_file(missing)


def test_validate_input_file_exists(tmp_path):
    real_file = tmp_path / "data.csv"
    real_file.write_text("id,value\n1,2\n", encoding="utf-8")
    assert validate_input_file(real_file) == real_file
```

**Testing environment-variable-dependent code** uses pytest's built-in
`monkeypatch` fixture, which safely sets (and automatically restores)
environment variables for the duration of one test:

```python
def test_get_port_reads_env(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    assert get_port() == 9000


def test_get_port_uses_default_when_unset(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    assert get_port(default=8000) == 8000
```

**Testing configuration precedence** — verifying CLI overrides
environment, which overrides the built-in default:
```python
def test_precedence_cli_wins_over_env(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    assert resolve_port(cli_value=7000) == 7000


def test_precedence_env_wins_over_default(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    assert resolve_port(cli_value=None) == 9000


def test_precedence_default_when_nothing_set(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    assert resolve_port(cli_value=None) == 8000
```

What to cover, systematically, per validator/config function: **valid
input**; **missing input** (and whether a default applies or an error
is expected); **malformed input**; **boundary values** (exactly at the
edge of a range — both just inside and just outside); **invalid
types**; **invalid paths**; **default behavior**; and, for anything
combining multiple sources, **precedence** itself, explicitly.

## 27. Common Mistakes

1. **Trusting environment variables.** *Why:* they can be missing,
   empty, or set to something unexpected by a typo or a misconfigured
   deployment. *Fix:* always validate, exactly as any other untrusted
   input (§2, §10).
2. **Assuming env values have the correct type.** *Why:* every
   environment variable is a string, always (§3). *Fix:* convert
   explicitly, and handle conversion failure explicitly.
3. **`bool("false")`.** *Why:* any non-empty string is truthy in
   Python (§14). *Fix:* use a real `parse_bool()` function.
4. **Hard-coded secrets.** *Why:* committed to version control, shared
   with everyone who can read the source, effectively permanent (§5).
   *Fix:* environment variables (or a secret manager), never literals
   in code.
5. **Committing `.env`.** *Why:* a `.env` file frequently contains
   real local secrets (§6). *Fix:* `.gitignore` it; commit a
   `.env.example` with placeholders instead.
6. **Validating too late.** *Why:* invalid data that's traveled deep
   into business logic before failing produces confusing errors far
   from the actual root cause (§10). *Fix:* validate at the boundary,
   before the value is used for anything.
7. **Validating inconsistently.** *Why:* the same logical value
   (a port, a boolean flag) validated differently in different parts
   of the codebase produces subtly different, hard-to-predict
   behavior. *Fix:* one reusable validator function per value type
   (§20), called everywhere that value enters the system.
8. **Mixing parsing and business logic.** *Why:* makes both harder to
   test and reuse, and hides what's actually validated versus assumed
   (§10, §21–§22 — the same architectural lesson
   [06](06-command-line-arguments-with-argparse.md)'s §40 and
   [07](07-standard-streams-and-exit-codes.md)'s §45 applied to CLI
   dispatch). *Fix:* separate `build_config()`/validators from the
   functions that actually do the program's work.
9. **Overly broad exception handling.** *Why:* `except Exception:` (or
   bare `except:`) hides genuinely unexpected bugs alongside
   anticipated validation failures (§19). *Fix:* catch specific
   exception types.
10. **Vague error messages.** *Why:* `"Invalid input"` gives the user
    nothing to act on (§18). *Fix:* name the field, the expectation,
    and (when safe) the actual value received.
11. **Silently using dangerous defaults.** *Why:* a required security-
    relevant setting quietly defaulting to something permissive
    (`DEBUG=True`, `verify_ssl=False`) can turn a missing-configuration
    mistake into a serious, silent production problem (§4). *Fix:*
    require explicit values for anything security-relevant; fail fast
    rather than guessing.
12. **Reading environment variables throughout the application.**
    *Why:* scatters validation logic, makes precedence and defaults
    inconsistent, and makes testing harder (§21–§22). *Fix:* read and
    validate configuration once, centrally, into an `AppConfig`.
13. **Ignoring configuration precedence.** *Why:* undocumented,
    inconsistent precedence produces "it works on my machine but not in
    CI" -style bugs that are genuinely hard to trace (§7). *Fix:*
    define and document precedence explicitly, and implement it in one
    place.
14. **Accepting arbitrary paths.** *Why:* untrusted path input can
    enable path traversal or accidental overwrites (§15, §23). *Fix:*
    validate paths against expected locations/patterns when they come
    from untrusted input.
15. **Confusing validation with sanitization.** *Why:* silently
    "fixing" invalid input (sanitizing) when the input should have been
    rejected outright (validating) hides real mistakes from whoever
    made them (§9). *Fix:* decide, deliberately, which operation a
    given check actually needs to be.

## 28. Progressive Coding Examples

**1. Reading one environment variable**
```python
import os
print(os.getenv("APP_ENV"))
```

**2. Using a default**
```python
environment = os.getenv("APP_ENV", "development")
```

**3. Converting an environment value**
```python
port = int(os.getenv("PORT", "8000"))
```

**4. Boolean parsing**
```python
def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"expected a boolean, got {value!r}")

debug = parse_bool(os.getenv("DEBUG", "false"))
```

**5. Required configuration, fail-fast**
```python
import sys

database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("error: DATABASE_URL is required", file=sys.stderr)
    raise SystemExit(4)
```

**6. CLI argument validation with argparse**
```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, choices=range(1, 65536), default=8000)
args = parser.parse_args()
```

**7. Path validation**
```python
from pathlib import Path

def validate_input_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"input file does not exist: {path}")
    return path
```

**8. JSON/CSV record validation**
```python
def validate_record(record: dict) -> dict:
    if "id" not in record:
        raise ValueError("missing 'id'")
    return record
```

**9. A reusable validator module (conceptual layout)**
```python
# validators.py
def parse_port(value: str) -> int: ...
def parse_bool(value: str) -> bool: ...
def validate_input_file(path) -> "Path": ...
```

**10. A centralized `AppConfig`**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    environment: str
    port: int
    debug: bool
```

**11. Configuration precedence**
```python
def resolve_port(cli_value: int | None) -> int:
    if cli_value is not None:
        return cli_value
    return int(os.getenv("PORT", "8000"))
```

**12. A complete CLI configuration/validation flow**
```python
def build_config(argv=None) -> AppConfig:
    args = build_parser().parse_args(argv)
    return AppConfig(
        environment=validate_environment(os.getenv("APP_ENV", "development")),
        port=resolve_port(args.port),
        debug=parse_bool(os.getenv("DEBUG", "false")),
    )
```

Each step above builds directly on the one before it — §29's mini
project assembles all twelve into one complete, working program.

## 29. Mini Project — Production-Style Configurable Data Processing CLI

**Requirements:** a CLI, `process_data.py`, that reads its input file
path and processing options from CLI arguments, reads its environment
name and log level from environment variables (with CLI taking
precedence where both apply), validates every external input,
normalizes values into a single `AppConfig`, processes a CSV file
record by record, collects (rather than fails fast on) per-record
validation errors, logs safely (no secrets, appropriate levels), and
exits with a meaningful, documented status code.

**Architecture:**
```
Raw Inputs (CLI argv, os.environ, the CSV file itself)
        ↓
   Parsing            (argparse; os.getenv)
        ↓
  Validation            (parse_port, parse_bool, validate_input_file, validate_csv_row)
        ↓
 Normalization            (lowercased environment name, stripped strings)
        ↓
   AppConfig                 (one immutable, trusted object)
        ↓
 Business Logic               (process_file — operates only on trusted values)
        ↓
    Output                       (a JSON summary on stdout; diagnostics via logging)
```

**Configuration flow:** `APP_ENV` and `LOG_LEVEL` come from the
environment, with sensible defaults (`"development"`, `"INFO"`);
`--port` (used here only to demonstrate precedence, not because this
CLI opens a network port) can be set via `PORT` in the environment or
overridden by `--port` on the command line, CLI taking precedence, per
§7's convention.

**Validation flow:** the input file path is validated once
(`validate_input_file`, fail-fast — there is nothing to process
without it); each CSV row is validated independently (error
collection — a handful of bad rows should not stop the whole file
from being processed).

**Implementation:**
```python
"""process_data.py — a production-style, validated, configurable CSV processor."""
from __future__ import annotations

import argparse
import csv
import json
import logging
import logging.config
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


# ---- Validators (§20) ----

def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise ValueError(f"port must be an integer, got {value!r}") from None
    if not (1 <= port <= 65535):
        raise ValueError(f"port must be between 1 and 65535, got {port}")
    return port


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"expected a boolean value, got {value!r}")


VALID_ENVIRONMENTS = {"development", "staging", "production"}


def validate_environment(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in VALID_ENVIRONMENTS:
        raise ValueError(f"unknown environment {value!r}; expected one of {sorted(VALID_ENVIRONMENTS)}")
    return normalized


def validate_input_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"input file does not exist: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"expected a .csv file, got {path.suffix or '(no extension)'}")
    return path


def validate_row(row: dict, line_number: int) -> dict:
    if not row.get("id"):
        raise ValueError(f"line {line_number}: missing 'id'")
    try:
        row["value"] = float(row["value"])
    except (KeyError, ValueError):
        raise ValueError(f"line {line_number}: invalid or missing 'value'") from None
    return row


# ---- Configuration object (§21) ----

@dataclass(frozen=True)
class AppConfig:
    environment: str
    port: int
    log_level: str
    input_file: Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and summarize a CSV file.")
    parser.add_argument("input_file", type=Path, help="Path to the input CSV file")
    parser.add_argument("--port", type=int, default=None, help="Overrides the PORT environment variable")
    return parser


def build_config(argv: Sequence[str] | None = None) -> AppConfig:
    args = build_parser().parse_args(argv)

    environment = validate_environment(os.getenv("APP_ENV", "development"))

    port = args.port if args.port is not None else parse_port(os.getenv("PORT", "8000"))

    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(f"LOG_LEVEL must be a valid logging level, got {log_level!r}")

    input_file = validate_input_file(args.input_file)

    return AppConfig(environment=environment, port=port, log_level=log_level, input_file=input_file)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


# ---- Business logic (never touches os.environ or argparse directly) ----

def process_file(path: Path) -> dict:
    valid = 0
    errors: list[str] = []

    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            try:
                validate_row(row, line_number)
            except ValueError as exc:
                errors.append(str(exc))
                logger.warning(str(exc))
                continue
            valid += 1
            logger.debug("Line %d valid: id=%s value=%s", line_number, row["id"], row["value"])

    logger.info("Processed %s: %d valid, %d invalid", path, valid, len(errors))
    return {"valid": valid, "invalid": len(errors), "errors": errors}


def main(argv: Sequence[str] | None = None) -> int:
    try:
        config = build_config(argv)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4   # configuration problem, per this module's exit-code convention

    configure_logging(config.log_level)
    logger.info("Starting: environment=%s port=%d", config.environment, config.port)

    summary = process_file(config.input_file)
    print(json.dumps(summary))   # the actual result — stdout, clean, machine-readable

    return 0 if summary["invalid"] == 0 else 3   # input/data problem


if __name__ == "__main__":
    raise SystemExit(main())
```

**Testing strategy:**
```python
import json

from process_data import main, parse_port, parse_bool, validate_environment


def test_parse_port_valid():
    assert parse_port("9000") == 9000


def test_parse_bool_variants():
    assert parse_bool("YES") is True
    assert parse_bool("off") is False


def test_validate_environment_normalizes_case():
    assert validate_environment(" Production ") == "production"


def test_main_missing_input_file(monkeypatch, tmp_path):
    missing = tmp_path / "nope.csv"
    status = main([str(missing)])
    assert status == 4


def test_main_all_valid_records(tmp_path, capsys):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("id,value\n1,2.5\n2,3.5\n", encoding="utf-8")

    status = main([str(csv_file)])
    captured = capsys.readouterr()

    assert status == 0
    assert json.loads(captured.out.strip())["valid"] == 2


def test_main_some_invalid_records(tmp_path, capsys):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("id,value\n1,2.5\n,bad\n", encoding="utf-8")

    status = main([str(csv_file)])
    summary = json.loads(capsys.readouterr().out.strip())

    assert status == 3
    assert summary["valid"] == 1
    assert summary["invalid"] == 1


def test_cli_port_overrides_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("PORT", "9999")
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("id,value\n1,2\n", encoding="utf-8")

    from process_data import build_config
    config = build_config([str(csv_file), "--port", "1234"])
    assert config.port == 1234
```

**Debugging scenarios:** if `PORT` set in the environment appears to
have no effect, check whether `--port` was also passed on the command
line — CLI intentionally wins (§7); if `LOG_LEVEL=debug` (lowercase)
is rejected, remember `build_config()` upper-cases it before checking
— confirm the exact validation logic being applied, rather than
assuming; if a record with a boundary value (e.g. `value=0`) is
unexpectedly rejected, re-check `validate_row()`'s actual conditions
against the intended rule (§31 covers exactly this class of bug).

**Production improvements worth naming:** structured (JSON) logging
output (§08's chapter's §21); a `--max-error-rate` threshold above
which the whole run is treated as failed outright rather than merely
reporting invalid rows; moving `VALID_ENVIRONMENTS` and other constants
into an external, documented configuration schema.

## 30. Exercises + Answer Key

**Beginner**

1. Read an environment variable with `os.getenv()`, supplying a
   default, and print its value and type.
2. Write and test a function that reads a required environment
   variable, raising a clear error if it's missing.
3. Write `parse_int(value: str) -> int` with a clear error message on
   invalid input.
4. Convert `"42"` to an `int` and explain, in a comment, why
   `int("42.0")` fails.

**Intermediate**

5. Add an argparse argument using a custom `type=` validator that
   rejects negative numbers.
6. Write `validate_output_path(path, allow_overwrite=False)` and test
   both branches.
7. Write three custom validators of your choice (beyond this chapter's
   examples) and write at least two tests per validator (valid and
   invalid).
8. Implement configuration precedence (CLI > environment > default)
   for one setting of your choice, and test all three cases.
9. Validate a small JSON record against a required-fields schema,
   collecting (not failing fast on) every missing field at once.

**Advanced**

10. Build a complete `AppConfig` dataclass with at least four fields,
    each independently validated, assembled by one `build_config()`
    function.
11. Implement both fail-fast and error-collection validation for the
    same kind of input (e.g. a list of numbers), and write a short
    comment explaining which situation each would actually be used in.
12. Write a validator that checks a path does not escape an allowed
    root directory (§23), and test it against both a safe and an
    unsafe path.
13. Design (and briefly implement) a complete configuration pipeline
    for a small CLI of your choosing, including at least one secret
    handled safely (never logged, never in an error message).

**Answer key**

1. `os.getenv("SOME_VAR", "default")` always returns a `str` (or
   exactly the `default` you passed, whatever type that is) — printing
   `type(...)` confirms the value is a string when the variable is set
   (§2–§3).
2. The function should raise (commonly `RuntimeError` or `ValueError`)
   with a message naming the missing variable specifically, rather
   than allowing a bare `KeyError` (from `os.environ[...]`) to
   propagate unexplained (§4, §18).
3. `int("abc")` raises `ValueError`; the wrapping function should catch
   that and re-raise with the field name and the actual value included
   (§13, §20).
4. `int("42.0")` raises `ValueError` because `int()`'s string
   conversion does not accept a decimal point at all — it expects a
   string that looks like a plain integer; converting `"42.0"` requires
   going through `float` first: `int(float("42.0"))` (§13).
5. The custom `type=` function should raise
   `argparse.ArgumentTypeError` (not a bare `ValueError`) for negative
   input, matching
   [06](06-command-line-arguments-with-argparse.md)'s §15 pattern.
6. `validate_output_path` should raise when the path exists and
   `allow_overwrite=False`, and succeed (returning the path) both when
   the path doesn't exist and when it exists but `allow_overwrite=True`
   (§15).
7. Each validator should have at least one test confirming it accepts
   valid input and returns the expected (possibly converted) value,
   and at least one confirming it raises on invalid input with a clear
   message (§20, §26).
8. All three tests should use `monkeypatch.setenv`/`delenv` to control
   the environment independently per test, confirming CLI wins when
   both are set, environment wins when only it is set, and the default
   applies when neither is set (§7, §26).
9. The validator should return a list of missing-field error strings
   (potentially empty) rather than raising on the first missing field,
   consistent with the error-collection strategy (§16–§17).
10. `AppConfig` should be a frozen dataclass; `build_config()` should
    call one validator per field and only construct the `AppConfig`
    once every field has passed (§21–§22).
11. Fail-fast is appropriate when any single invalid value makes
    continuing meaningless or unsafe (e.g., a required configuration
    setting); error collection is appropriate when the input is a
    batch of independent items where partial success is still useful
    (e.g., validating many numbers, most of which might be fine) (§17).
12. The safe path (inside the allowed root) should pass through
    unchanged (resolved); the unsafe path (e.g. containing `../`
    escaping the root) should raise `ValueError` — testing
    `Path.is_relative_to()`'s actual behavior directly (§23).
13. A complete answer should show: at least one required, fail-fast
    setting; at least one optional setting with a sensible default; a
    secret read from the environment and never appearing in any log
    call or error message; and one `build_config()` function that
    assembles everything into a single validated object (§5, §18,
    §21–§22, §25).

## 31. Debugging Lab

**1. Environment variable missing**
```python
port = int(os.environ["PORT"])
```
*Observed:* `KeyError: 'PORT'`. *Diagnosis:* `PORT` was never exported
in the current shell session, or the process was started from a
different shell/context than expected. *Fix:* decide whether `PORT` is
genuinely required (fail fast with a clear message, per §4) or should
have a default (`os.getenv("PORT", "8000")`).

**2. Incorrect environment variable type**
```python
timeout = os.getenv("TIMEOUT", 30)   # BUG: default is an int, but a set env var is always a str
response = wait(timeout=timeout * 2)
```
*Observed:* works fine when `TIMEOUT` is unset (default `30`, an int),
but crashes with a `TypeError` (or produces `"3030"` via string
repetition) the moment `TIMEOUT` is actually set in the environment.
*Diagnosis:* the default is the wrong type (`int`) for what
`os.getenv()` returns when the variable *is* set (always `str`) —
inconsistent types depending on whether the variable was set at all
(§3). *Fix:* convert explicitly, with the default also passed as a
string: `int(os.getenv("TIMEOUT", "30"))`.

**3. `bool("false")` bug**
```python
debug = bool(os.getenv("DEBUG", "false"))
```
*Observed:* `debug` is always `True`, even when `DEBUG=false` is set.
*Diagnosis:* §14 — any non-empty string is truthy. *Fix:* use a real
`parse_bool()` function.

**4. CLI argument accepted but semantically invalid**
```python
parser.add_argument("--port", type=int)
```
```bash
python app.py --port -5
```
*Observed:* argparse accepts `-5` without complaint (it's a valid
`int`), but the program later fails confusingly when trying to bind to
a negative port. *Diagnosis:* `type=int` performs syntax validation
(is this an int) but not semantic validation (is this int a valid
port) — exactly §8's distinction. *Fix:* a custom `type=` function
(`parse_port`) that also checks the range, or `choices=range(1, 65536)`.

**5. Wrong configuration precedence**
A value set correctly via `--port 9000` on the command line appears to
have no effect; the program keeps using the environment's `PORT`
value instead. *Diagnosis:* check the actual precedence logic —
likely, the code checks `os.getenv("PORT")` *before* checking whether
`args.port` was explicitly provided, silently reversing the intended
order (§7). *Fix:* check the higher-priority source first, and only
fall through to lower-priority sources when the higher one is
genuinely absent (`if args.port is not None: ...`, not
`if args.port: ...` — the latter would also incorrectly skip an
explicitly-provided `--port 0`).

**6. Invalid file path**
```python
path = Path(os.getenv("INPUT_FILE"))
```
*Observed:* `TypeError: argument should be a str or an os.PathLike
object, not 'NoneType'`. *Diagnosis:* `INPUT_FILE` was never set, so
`os.getenv()` returned `None`, and `Path(None)` fails. *Fix:* check for
`None` explicitly (or supply a string default) before constructing the
`Path`.

**7. Vague validation errors**
```python
raise ValueError("bad config")
```
*Observed:* a user has no idea which setting was wrong or why.
*Diagnosis:* the message names neither the field nor the expectation
nor the actual value (§18). *Fix:*
`raise ValueError(f"PORT must be between 1 and 65535, got {port}")`.

**8. Configuration read from multiple places**
Two different modules each independently call `os.getenv("LOG_LEVEL")`
with two different (and inconsistent) default values, causing
different parts of the program to behave as if they were configured
differently. *Diagnosis:* configuration is being read ad hoc,
throughout the codebase, instead of once, centrally (§21–§22, §27).
*Fix:* read `LOG_LEVEL` exactly once, in `build_config()`, and pass the
resulting `AppConfig.log_level` value to everything that needs it.

**9. Secret accidentally logged**
```python
logger.debug("Loaded config: %s", config)
```
where `AppConfig` includes an `api_key` field, and `Formatter` renders
the full dataclass repr, secret included. *Diagnosis:* logging the
entire configuration object at once, rather than its specific,
known-safe fields (§5, §18, §25). *Fix:* log only explicitly-chosen,
non-sensitive fields, or implement a custom `__repr__` on `AppConfig`
that masks sensitive fields.

**10. Validator catches too much**
```python
def validate_port(value):
    try:
        return int(value)
    except Exception:      # too broad
        return 8000          # silently substitutes a default for genuinely invalid input
```
*Observed:* an obviously wrong `PORT` value (e.g. `"not-a-port"`)
silently becomes `8000` instead of producing an error anyone notices.
*Diagnosis:* catching `Exception` broadly, and silently falling back
to a default rather than raising, hides a real configuration mistake
(§4, §19, §27). *Fix:* catch only `ValueError` specifically, and raise
a clear error rather than silently substituting a default for input
that *was* provided but was wrong.

**11. Valid boundary value rejected**
```python
def validate_probability(value: float) -> float:
    if not (0.0 < value < 1.0):   # BUG: excludes both 0.0 and 1.0
        raise ValueError(...)
```
*Observed:* a legitimately valid input of exactly `0.0` (or `1.0`, if
the field is meant to be inclusive) is rejected. *Diagnosis:* the
comparison operators (`<` vs. `<=`) don't match the field's actual,
intended inclusive/exclusive boundaries (§13). *Fix:* re-check the
specification for this field and use the matching operators — e.g.
`0.0 <= value <= 1.0` for a fully inclusive range.

## 32. Interview + Architecture Questions

1. What is configuration, and how does it differ from code?
2. What is an environment variable, and how does a child process come
   to have access to one?
3. What is the difference between `os.environ["NAME"]` and
   `os.getenv("NAME")`?
4. Why are all environment variable values strings, and why does that
   matter?
5. Why is hard-coding secrets in source code dangerous, even if the
   repository is private?
6. What is a `.env` file, and how does it differ from an actual OS
   environment variable?
7. Why should `.env` files containing real secrets not be committed to
   version control?
8. Design a configuration precedence order for a CLI that reads from
   defaults, a config file, environment variables, and CLI arguments.
   Justify the order.
9. What is the difference between parsing and validation?
10. What is the difference between validation, normalization, and
    sanitization?
11. What is boundary validation, and why should the rest of an
    application avoid re-validating already-validated data?
12. Name at least five distinct kinds of validation and give an
    example of each.
13. How does `argparse`'s `type=` support both parsing and validation
    at once?
14. What is the specific danger in `bool(some_env_string)`?
15. How would you validate that an input file path both exists and has
    the expected extension?
16. What is the difference between fail-fast and error-collection
    validation, and when would you choose each?
17. Why does a good validation error message name the field, the
    expectation, and (usually) the actual value received?
18. Why should a secret never be echoed back in an error message, even
    when it's the thing that's invalid?
19. Name three standard exceptions relevant to input validation and
    what each signals.
20. Why is `except Exception:` generally a poor choice for handling
    validation failures specifically?
21. Design a small, reusable validator function for a "positive
    integer" field. What should it return, and what should it raise?
22. Why should a configuration object (e.g. a frozen dataclass) be
    preferred over passing many individual configuration values
    around?
23. Why should `frozen=True` be used for a configuration dataclass?
24. What security risk does path traversal pose, and how would you
    guard against it?
25. Why should command/query strings never be built by concatenating
    untrusted input directly?
26. How should configuration state be logged safely?
27. How would you test that configuration precedence works correctly
    with pytest?
28. Design the full configuration architecture for a production CLI
    that needs a required database URL, an optional log level, and a
    required-but-sensitive API key.

**Answer key**

1. Configuration is the set of values controlling how a program
   behaves, kept separate from the logic (code) that defines what it
   does — they change for different reasons and at different rates
   (§1).
2. An environment variable is a named string value attached to a
   process; a child process inherits a copy of its parent's
   environment by default when it's started (§2).
3. `os.environ["NAME"]` raises `KeyError` if the variable is missing;
   `os.getenv("NAME")` returns `None` (or a supplied default) instead
   — use the former when the variable is required, the latter when a
   default is acceptable (§2).
4. Because the OS environment mechanism has no concept of types beyond
   text — every value must be explicitly converted (and that
   conversion explicitly validated) before use (§3).
5. Because version-controlled repositories retain history — a secret
   committed once can remain recoverable from history even after being
   removed later, and anyone with read access to the repo (private or
   not) can see it (§5).
6. A `.env` file is a plain text file of `KEY=value` pairs used as a
   local development convenience; unlike a real environment variable,
   nothing loads it automatically — a tool (e.g. `python-dotenv`) or
   your own code must read it and set the corresponding environment
   variables explicitly (§6).
7. Because `.env` files commonly contain real secret values meant only
   for local development, and committing them exposes those secrets
   the same way hard-coding them would (§5–§6).
8. A reasonable order, highest to lowest priority: CLI arguments >
   environment variables > config file > built-in defaults —
   justified by "the more specific to this one invocation, the higher
   the priority" (§7).
9. Parsing turns raw text into a candidate value (a type conversion);
   validation decides whether that value is actually acceptable — the
   two are related but distinct, and `argparse`'s `type=` often
   performs both at once (§8).
10. Validation asks "is this acceptable?" (no change to the value);
    normalization converts an acceptable value into one consistent
    representation; sanitization actively removes/transforms unwanted
    content from a value (§9).
11. Boundary validation means validating untrusted input once, at the
    point it enters the system; the rest of the program can then trust
    it and avoid redundant, inconsistent re-validation scattered
    throughout the codebase (§10).
12. Any five of: type, presence, range, length, format, enum/choice,
    cross-field, uniqueness, path, file existence, extension, encoding
    (§11), each with an example from that section's table.
13. `type=` is a callable applied to the raw string; it can both
    convert (e.g. `int(...)`) and raise `argparse.ArgumentTypeError`
    for a value that converts successfully but fails some additional
    check, combining conversion and validation in one function (§8,
    citing [06](06-command-line-arguments-with-argparse.md)'s §15).
14. Any non-empty string, including `"false"`, `"0"`, and `"no"`, is
    truthy in Python — `bool(some_string)` never actually parses
    boolean-like text, it only checks whether the string is empty
    (§14).
15. Check `path.is_file()` for existence and type, and
    `path.suffix.lower() == ".csv"` (or the relevant extension) for the
    expected extension, raising a clear `ValueError` if either check
    fails (§15).
16. Fail-fast stops immediately on the first critical invalid value —
    appropriate for configuration, where partial success is
    meaningless; error collection processes everything and reports all
    problems found — appropriate for batches of independent records,
    where partial success is genuinely useful (§17).
17. Because a message with all three pieces of information lets the
    person reading it fix the problem without guessing or reading
    source code — exactly the difference between `"Invalid input"` and
    a specific, actionable message (§18).
18. Because doing so would leak the very secret the validation was
    trying to guard, defeating the purpose of treating it as sensitive
    in the first place (§18).
19. Any three of: `ValueError` (right type, wrong value),
    `TypeError` (wrong type entirely), `FileNotFoundError` (expected
    path doesn't exist), `PermissionError` (path exists but
    inaccessible), `KeyError` (missing required field/key),
    `json.JSONDecodeError` (malformed JSON text) (§19).
20. Because it catches genuinely unexpected bugs alongside the
    specific, anticipated validation failures you actually meant to
    handle, hiding real problems and making debugging much harder
    (§19, referencing [08](08-logging-versus-print.md)'s §15/§23).
21. It should return the converted `int` on success, and raise
    `ValueError` (with a message naming the field and what was
    expected) on failure — matching every validator pattern in §20.
22. Because passing many individual values around scales badly (long,
    fragile, easily-misordered parameter lists) and makes it easy for
    different call sites to validate or default the same logical
    setting inconsistently; one validated object avoids both problems
    (§21).
23. Because configuration should not be silently mutated somewhere deep
    in a running program — `frozen=True` makes any attempted mutation
    fail loudly and immediately, rather than succeeding silently and
    causing confusing behavior elsewhere (§21).
24. Path traversal lets untrusted input escape an intended directory
    (e.g. via `"../"` segments), potentially reading or writing files
    outside where the program was meant to operate; guard against it by
    resolving the path and checking `Path.is_relative_to()` against
    the intended allowed root (§23).
25. Because untrusted input concatenated directly into a command or
    query string can be crafted to inject additional syntax the program
    never intended to execute — the fix is to use parameterized queries
    or list-based subprocess arguments, which treat the untrusted value
    strictly as data, never as syntax (§24).
26. By logging only specific, known-non-sensitive fields (or a
    deliberately redacted representation) — never the whole
    configuration object indiscriminately, and never any field known or
    suspected to hold a secret (§25).
27. By using `monkeypatch.setenv`/`delenv` to independently control the
    environment per test case, combined with passing an explicit
    `argv` list, and asserting the resulting value matches whichever
    source is expected to win in each specific combination (§26).
28. `DATABASE_URL` — required, read once via `os.environ[...]`
    (fail-fast if missing, no default); `LOG_LEVEL` — optional, read via
    `os.getenv("LOG_LEVEL", "INFO")`, validated against the known set of
    levels; `API_KEY` — required, read via `os.environ[...]`, never
    logged, never included in any error message, and (if the
    `AppConfig` object itself is ever logged or printed as a whole)
    masked via a custom `__repr__` or excluded entirely from any
    logging call — all three assembled once, in a single
    `build_config()` function, into one frozen `AppConfig` (§5, §18,
    §21–§22, §25).

## 33. Knowledge Check

**Conceptual**
1. In your own words, why must every environment variable value be
   treated as a string, regardless of what it "looks like"?
2. Why is "validate once, at the boundary" better than validating the
   same value repeatedly throughout a codebase?

**Code-reading**
3. What's wrong with this function, specifically?
```python
def get_timeout():
    return os.getenv("TIMEOUT", 30)
```
4. What will this print if `DEBUG` is not set in the environment at
   all?
```python
print(bool(os.getenv("DEBUG", "false")))
```

**Debugging**
5. A CLI's `--output` argument is accepted with any string, including
   one pointing at a directory the program has no write permission to.
   What kind of validation is missing, and where should it be added?
6. A config value provided via an environment variable is being
   silently overridden by a hardcoded default deep inside a helper
   function, even though the environment variable is set correctly.
   What's the most likely cause?

**Scenario-based**
7. A CSV import tool currently stops at the first invalid row. Users
   want to see *all* problems in one pass instead. What validation
   strategy should it switch to, and why?
8. A teammate suggests logging the entire parsed configuration object
   at `DEBUG` level "to help with debugging." What's the risk, and
   what would you suggest instead?

**Design**
9. Design (briefly) the validators and the `AppConfig` fields needed
   for a CLI that uploads a file to a specific directory, where the
   destination directory must be confined to one known-safe root.

---

**Answer key**

1. Because the OS environment mechanism itself has no type system
   beyond text — Python receives exactly what the OS provides, a
   string, with no automatic conversion, regardless of what the value
   was intended to represent (§2–§3).
2. Because validating once, at the boundary, produces one trusted
   representation the rest of the program can rely on without
   redundant checks — validating repeatedly throughout the codebase
   risks inconsistency (different checks in different places) and
   wastes effort (§10).
3. The default (`30`, an `int`) has a different type than what
   `os.getenv()` returns when `TIMEOUT` *is* set (always a `str`) —
   the function's return type is inconsistent depending on whether the
   variable was set at all (§3, §31 debugging scenario 2).
4. `True` — `os.getenv("DEBUG", "false")` returns the string
   `"false"` (since `DEBUG` is unset, the default is used, and the
   default itself is the *string* `"false"`, not the boolean `False`),
   and `bool("false")` is `True` because the string is non-empty
   (§14).
5. Permission/writability validation, and directory-existence
   validation, are both missing — these belong at the point
   `--output` is validated (ideally in a custom `type=` function or an
   immediately-following check in `build_config()`), before the value
   is trusted anywhere else in the program (§15).
6. The helper function is very likely reading its own hardcoded
   default (or reading from a different source entirely) instead of
   receiving the already-resolved value from a centralized
   `build_config()`/`AppConfig` — a direct instance of "configuration
   read from multiple places" (§27, §31 debugging scenario 8).
7. Error collection — process every row, collect every validation
   failure, and report them all together, since users clearly need to
   see the full picture of what's wrong across the whole file rather
   than fixing one row at a time (§17).
8. The risk is that the configuration object may contain (now, or in
   the future) a secret field, which would then be logged in full;
   the safer approach is logging only specific, deliberately chosen,
   known-non-sensitive fields (§18, §25).
9. Validators: `validate_input_file` (exists, readable); a path-
   traversal guard confirming the resolved destination path is
   `is_relative_to()` the known-safe root (§23); `AppConfig` fields:
   `input_file: Path`, `destination_root: Path`, `destination_file:
   Path` (already validated and resolved) — assembled once in
   `build_config()`, with the upload logic itself trusting these
   fields without re-checking them.

## 34. Production Checklist

**Untrusted input**
- [ ] Every external input (CLI, environment, file, JSON, CSV, user
      input) is treated as untrusted, regardless of its usual source.
- [ ] Validation happens once, at the boundary, not scattered
      inconsistently throughout the codebase (§10, §27).

**Configuration precedence**
- [ ] Precedence across defaults, config file, environment, and CLI is
      explicit, documented, and implemented in exactly one place (§7).

**Defaults**
- [ ] Every default is a deliberate, safe choice — never a permissive
      or dangerous fallback for a security-relevant setting (§4).
- [ ] Required settings fail fast, with a clear message, rather than
      silently substituting a default.

**Secrets**
- [ ] No secret ever appears hard-coded, committed in `.env`, logged,
      or echoed in an error message (§5, §18, §25).
- [ ] `.env` (if used) is `.gitignore`d; `.env.example` documents
      expected variables with placeholder values only (§6).

**Environment values parsed correctly**
- [ ] Every environment/CLI value is explicitly converted to its
      intended type, with conversion failure handled explicitly
      (§3, §13).
- [ ] Boolean values go through a real `parse_bool()`-style function,
      never Python's raw `bool(some_string)` (§14).

**Centralized configuration**
- [ ] Configuration is read and validated once, into a single
      immutable object (e.g. a frozen dataclass), rather than read
      repeatedly via `os.getenv()` throughout the application (§21–
      §22).
- [ ] The application receives and depends on that validated object,
      not raw `os.environ`/`argparse.Namespace` values, deep in its
      logic.

**Validation errors**
- [ ] Every validation failure produces a clear, actionable message
      naming the field, the expectation, and (when safe) the value
      received (§18).
- [ ] Exceptions are handled specifically (`ValueError`, `KeyError`,
      etc.), never with a broad `except Exception:` reflex (§19).

**Safe paths**
- [ ] Input paths are validated for existence/type before use; output
      paths are validated for overwrite-safety and a valid parent
      directory (§15).
- [ ] Paths derived from untrusted input are checked against an
      expected root when path traversal is a genuine risk (§23).

**Safe logging**
- [ ] Configuration state is logged only through specific,
      known-non-sensitive fields, never as a whole object that might
      contain a secret (§25).
- [ ] Untrusted values passed into log messages use lazy `%`-style
      formatting, not direct string interpolation (§23–§24, citing
      [08](08-logging-versus-print.md)'s §19).

**Testing**
- [ ] Every validator is tested for valid input, missing input,
      malformed input, and boundary values (§26).
- [ ] Configuration precedence is tested explicitly for every
      combination of sources that matters.

**Exit codes**
- [ ] Configuration errors and input/data errors produce distinct,
      documented, non-zero exit codes, consistent with
      [07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)'s
      conventions (§4, §18, §29).
