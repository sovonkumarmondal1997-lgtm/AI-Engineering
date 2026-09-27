# Configuration and Environment Files

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain what configuration is and why it should be separated from application behavior;
- explain what an environment variable is and how a process receives it;
- read configuration safely with `os.environ`, `os.getenv()`, and `os.environ.get()`;
- convert string configuration values into Python types;
- parse Boolean configuration correctly;
- distinguish required settings from optional settings;
- validate configuration at application startup;
- understand `.env` files and their role in local development;
- design a safe `.env.example`;
- use `.gitignore` correctly for local secret-containing files;
- distinguish configuration from secrets;
- design configuration for development, testing, staging, and production;
- define and document configuration precedence;
- centralize configuration in a typed object;
- use `dataclass` and `frozen=True` for stable configuration;
- test configuration without depending on the developer's machine;
- debug configuration failures without exposing secrets;
- design configuration for an Applied AI application;
- recognize common configuration anti-patterns;
- reason about startup behavior, validation, and operational safety.

### Learning progression

This chapter intentionally moves through:

```text
Beginner
  ↓
What is configuration?
  ↓
Environment variables
  ↓
Python environment access
  ↓
Types and validation
  ↓
.env and .env.example
  ↓
Configuration precedence
  ↓
Central configuration object
  ↓
Testing and debugging
  ↓
Production architecture
  ↓
Applied AI Engineering
```

---

## 2. Why Configuration Exists

A program usually contains two different kinds of decisions:

1. **Behavior** — what the code does.
2. **Configuration** — how that behavior is selected for a particular environment.

Consider:

```python
API_URL = "https://api.example.com"
TIMEOUT = 30
MODEL_NAME = "some-model"


def call_service(url: str) -> str:
    return f"calling {url}"


print(call_service(API_URL))
```

The function contains application behavior. `API_URL`, `TIMEOUT`, and `MODEL_NAME` are configuration values.

### Why hard-coding becomes a problem

Imagine the same application runs in:

```text
Development
Testing
Staging
Production
```

Each environment may need different:

```text
API endpoint
timeout
log level
model name
feature flag
batch size
worker count
```

If those values are hard-coded, changing environments can require changing source code.

That creates several problems:

- developers can accidentally commit environment-specific values;
- production values may leak into development;
- configuration changes require code changes;
- deployments become harder to reproduce;
- secrets may be placed in source code;
- reviewing configuration changes becomes harder.

The production habit is:

```text
stable application code
+
environment-specific configuration
```

---

## 3. Hard-Coded Configuration

Hard-coded configuration is not always wrong.

For example, a constant such as:

```python
DEFAULT_PAGE_SIZE = 100
```

can be a legitimate application default.

The problem begins when values that vary by environment or deployment are embedded directly into code.

### Example of a poor design

```python
MODEL_NAME = "production-model"
MODEL_ENDPOINT = "https://prod.example.internal"
API_KEY = "fake-secret-for-demo-only"
TIMEOUT_SECONDS = 30
```

The most serious problem is the secret, but even non-secret values can become difficult to maintain.

### Better separation

```python
def call_model(endpoint: str, timeout: float) -> str:
    return f"calling {endpoint} with timeout={timeout}"
```

Now the function describes behavior while configuration is supplied separately.

### Important rule

Do not confuse:

```text
constant
```

with:

```text
environment-specific configuration
```

A value can be fixed by the application design and still be a normal constant. A value that must change between environments is a strong candidate for external configuration.

---

## 4. What Configuration Means

Configuration is a set of values that controls application behavior without changing the application's core source code.

Typical configuration includes:

```text
PORT
HOST
LOG_LEVEL
REQUEST_TIMEOUT
MAX_RETRIES
MODEL_NAME
BATCH_SIZE
FEATURE_ENABLED
```

Configuration usually answers questions such as:

- Which endpoint should I call?
- How long should I wait?
- Which model should I use?
- Which feature should be enabled?
- How many items should I process in one batch?

### Configuration is not always a secret

For example:

```text
LOG_LEVEL=INFO
PORT=8000
MODEL_NAME=my-model
```

are generally configuration.

By contrast:

```text
API_KEY=real-credential
DATABASE_PASSWORD=real-password
```

are sensitive.

The distinction matters because the handling rules are different.

---

## 5. Configuration vs Code vs Data vs Secrets

### Application code

Code defines behavior.

```python
def normalize_name(name: str) -> str:
    return name.strip().lower()
```

### Configuration

Configuration controls how the application behaves.

```text
MAX_RETRIES=3
```

### Data

Data is what the application processes.

```text
customer records
documents
events
model inputs
```

### Secrets

Secrets are sensitive values used for authentication or authorization.

```text
API keys
passwords
tokens
signing secrets
```

### A practical classification

| Category | Example | Typical handling |
|---|---|---|
| Code | `def process(...):` | Source control |
| Configuration | `TIMEOUT=30` | Environment/config |
| Data | document text | Data store/pipeline |
| Secret | `API_KEY=...` | Secret-capable production mechanism |

The important engineering question is not:

> "Can this value be stored in a file?"

The better question is:

> "What is the correct ownership and exposure model for this value?"

---

## 6. Environment Variables

An environment variable is a named value made available to a process through its execution environment.

A shell might define:

```bash
export APP_ENV=development
export PORT=8000
export LOG_LEVEL=DEBUG
```

A Python process can read those values.

The conceptual flow is:

```text
Shell / process launcher
        ↓
Process environment
        ↓
Python process
        ↓
os.environ / os.getenv()
        ↓
Configuration loader
```

### Why environment variables are useful

They allow the same source code to run with different settings.

For example:

```text
Development:
APP_ENV=development

Production:
APP_ENV=production
```

The Python source can remain unchanged.

### Important property

Environment variables are normally represented as strings.

So:

```text
PORT=8000
```

is read by Python as:

```python
"8000"
```

not:

```python
8000
```

That leads to one of the most important configuration habits:

> Parse and validate configuration values before using them.

---

## 7. The Operating-System Environment

A process does not magically see configuration.

A process is started with an environment.

Conceptually:

```text
Parent process
    ↓
starts child process
    ↓
child receives environment
    ↓
Python exposes environment through os
```

Different launch mechanisms can provide different environment variables.

For example:

```text
terminal shell
IDE
test runner
process manager
container runtime
```

may start the same Python program with different environments.

This explains a common beginner confusion:

> "It worked in my terminal, but the application did not see the variable."

The application may have been launched by a different process with a different environment.

### Important boundary

A value in one terminal session is not automatically a universal system configuration.

The relevant question is:

> What environment did the process actually receive?

---

## 8. Reading Environment Variables in Python

The most common tools are:

```python
import os

value = os.getenv("APP_ENV")
```

and:

```python
import os

value = os.environ.get("APP_ENV")
```

and:

```python
import os

value = os.environ["APP_ENV"]
```

These are similar but have important differences.

### Basic example

```python
import os

os.environ["APP_ENV"] = "development"

environment = os.getenv("APP_ENV")

print(environment)
```

Expected output:

```text
development
```

### Setting a value in the current process

```python
import os

os.environ["MODE"] = "test"

print(os.environ["MODE"])
```

This changes the Python process's environment mapping.

It does not mean that some permanent machine-wide configuration file has been changed.

---

## 9. The `os` Module

The `os` module exposes operating-system related functionality.

For configuration, the relevant pieces are:

```python
import os

print(os.environ)
print(os.getenv("APP_ENV"))
print(os.environ.get("APP_ENV"))
```

### `os.environ`

`os.environ` behaves like a mutable mapping of environment variables.

Example:

```python
import os

os.environ["APP_MODE"] = "testing"

print(os.environ["APP_MODE"])
```

### `os.getenv()`

`os.getenv()` reads a named environment variable and returns its value or a supplied default.

```python
import os

mode = os.getenv("APP_MODE", "development")

print(mode)
```

### `os.environ.get()`

This behaves like mapping-style `.get()`:

```python
import os

mode = os.environ.get("APP_MODE", "development")
```

For most application code, `os.getenv()` is convenient when the intent is clearly environment-variable access, while `os.environ[...]` is useful when the variable is required.

---

## 10. `os.environ`

`os.environ` is a mapping-like interface to the process environment.

### Read an existing variable

```python
import os

os.environ["APP_ENV"] = "development"

print(os.environ["APP_ENV"])
```

### Check for existence

```python
import os

if "APP_ENV" in os.environ:
    print("APP_ENV is configured")
```

### Set a value

```python
import os

os.environ["APP_ENV"] = "testing"
```

### Delete a value

```python
import os

os.environ["APP_ENV"] = "testing"
del os.environ["APP_ENV"]

print("APP_ENV" in os.environ)
```

### `[]` is strict

This:

```python
value = os.environ["MISSING_VALUE"]
```

raises `KeyError` when the variable does not exist.

That is often useful when the configuration is required.

### Important production consideration

Do not casually mutate environment variables deep inside application logic.

A cleaner design is:

```text
process environment
        ↓
configuration loader
        ↓
typed AppConfig
        ↓
application
```

---

## 11. `os.getenv()`

`os.getenv()` is convenient when a variable is optional or a default is appropriate.

```python
import os

timeout = os.getenv("TIMEOUT", "30")

print(timeout)
```

Notice:

```python
timeout
```

is still a string.

This is the difference between:

```python
timeout = os.getenv("TIMEOUT", "30")
```

and:

```python
timeout = int(os.getenv("TIMEOUT", "30"))
```

The second converts the string to an integer.

### Required value

You can deliberately avoid a default:

```python
import os

api_key = os.getenv("API_KEY")

if api_key is None:
    raise RuntimeError("API_KEY is required")
```

This can be clearer than allowing a missing secret to fail much later.

### When not to use `getenv()`

Avoid scattered calls like:

```python
def feature_a():
    timeout = int(os.getenv("TIMEOUT", "30"))
    ...


def feature_b():
    timeout = int(os.getenv("TIMEOUT", "30"))
    ...


def feature_c():
    timeout = int(os.getenv("TIMEOUT", "30"))
    ...
```

The code may work, but configuration logic is now distributed across the application.

A centralized configuration object is easier to reason about.

---

## 12. Missing Environment Variables

There are three common patterns.

### Pattern A — strict indexing

```python
import os

api_key = os.environ["API_KEY"]
```

Missing variable:

```text
KeyError
```

### Pattern B — nullable lookup

```python
import os

api_key = os.getenv("API_KEY")

if api_key is None:
    raise RuntimeError("API_KEY is required")
```

### Pattern C — safe default

```python
import os

log_level = os.getenv("LOG_LEVEL", "INFO")
```

The correct pattern depends on whether the setting is required.

### Production rule

Do not use a fake default for a setting that is truly required.

For example, this is dangerous:

```python
api_key = os.getenv("API_KEY", "temporary-key")
```

A missing credential becomes hidden configuration failure.

---

## 13. Default Values

Defaults are useful when the application has a safe, documented fallback.

Example:

```python
import os

timeout = int(os.getenv("TIMEOUT", "30"))
```

Here:

```text
TIMEOUT provided → use supplied value
TIMEOUT missing  → use 30
```

### Good defaults

A default is usually appropriate when:

- the application can operate safely without explicit configuration;
- the default is documented;
- the default is reasonable for the environment.

Examples:

```text
LOG_LEVEL=INFO
TIMEOUT=30
MAX_RETRIES=3
```

### Dangerous defaults

Be cautious when the absence of a value should be treated as an error.

Examples:

```text
API_KEY
SECRET_KEY
required endpoint
required storage location
```

### Mental model

```text
Required?
  ├── yes → validate presence
  └── no  → safe documented default may be used
```

---

## 14. Environment Variable Types

Environment variables are normally strings.

Consider:

```bash
PORT=8000
DEBUG=false
TIMEOUT=2.5
MODEL=my-model
```

Python sees values such as:

```python
"8000"
"false"
"2.5"
"my-model"
```

Therefore, type conversion is an application responsibility.

Common conversions include:

```python
int(...)
float(...)
```

For Booleans, use explicit parsing.

For lists, define a format and parse it.

For structured configuration, define an explicit representation and validation rule.

---

## 15. Converting Strings to Python Types

### Integer

```python
import os

port = int(os.getenv("PORT", "8000"))
print(type(port))
```

### Float

```python
import os

timeout = float(os.getenv("TIMEOUT", "30.0"))
print(type(timeout))
```

### What can go wrong?

```python
import os

os.environ["PORT"] = "abc"

port = int(os.environ["PORT"])
```

This raises:

```text
ValueError
```

That is a configuration error, not a business-logic error.

### Better design

```python
import os


def read_port() -> int:
    raw = os.getenv("PORT", "8000")

    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError("PORT must be an integer") from exc

    if not 1 <= value <= 65535:
        raise ValueError("PORT must be between 1 and 65535")

    return value
```

Now conversion and validation happen together.

---

## 16. Boolean Configuration

Boolean environment variables require special care.

This is a common bug:

```python
import os

debug = bool(os.getenv("DEBUG", "false"))

print(debug)
```

Why is this wrong?

Because:

```python
bool("false")
```

is:

```python
True
```

Any non-empty string is truthy.

### Safe Boolean parser

```python
def parse_bool(raw: str) -> bool:
    value = raw.strip().lower()

    if value in {"1", "true", "yes", "on"}:
        return True

    if value in {"0", "false", "no", "off"}:
        return False

    raise ValueError(
        "Boolean configuration must be one of: "
        "1, 0, true, false, yes, no, on, off"
    )
```

Usage:

```python
import os

debug_raw = os.getenv("DEBUG", "false")
debug = parse_bool(debug_raw)

print(debug)
```

### Production rule

Define one accepted Boolean format and use it consistently.

Do not let different parts of the application interpret Boolean strings differently.

---

## 17. Integer and Numeric Configuration

Numeric configuration should be parsed and range-checked.

```python
def parse_positive_int(raw: str, name: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc

    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")

    return value
```

Usage:

```python
import os

workers = parse_positive_int(
    os.getenv("WORKER_COUNT", "2"),
    "WORKER_COUNT",
)
```

### Why range checks matter

This is syntactically valid:

```python
workers = int("-100")
```

but it is not a sensible worker count.

Validation should enforce semantic correctness, not only syntactic correctness.

### Example with timeout

```python
def parse_timeout(raw: str) -> float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError("TIMEOUT must be a number") from exc

    if value <= 0:
        raise ValueError("TIMEOUT must be greater than zero")

    return value
```

---

## 18. Lists and Structured Configuration

Environment variables are strings, so a list needs a defined representation.

For a simple comma-separated list:

```text
ALLOWED_REGIONS=us-east-1,eu-west-1,ap-south-1
```

Parse it explicitly:

```python
import os

raw = os.getenv("ALLOWED_REGIONS", "")

regions = [
    item.strip()
    for item in raw.split(",")
    if item.strip()
]

print(regions)
```

### Common mistake

Do not assume a string that looks like a list is already a Python list.

```python
raw = "[1, 2, 3]"
```

is still a string.

### Structured configuration

For complex values, define a representation deliberately.

For example, JSON can represent nested configuration:

```text
MODEL_OPTIONS={"temperature":0.2,"max_tokens":1000}
```

If you choose such a format, parse it with an appropriate parser and validate the resulting structure.

```python
import json
import os

raw = os.getenv("MODEL_OPTIONS", "{}")
options = json.loads(raw)

if not isinstance(options, dict):
    raise ValueError("MODEL_OPTIONS must contain a JSON object")
```

Keep structured environment variables limited to cases where their complexity is justified. A giant environment variable can become harder to inspect and validate than several simple settings.

---

## 19. Required vs Optional Configuration

Configuration should be categorized intentionally.

### Required

The application cannot safely operate without it.

```text
API_KEY
REQUIRED_MODEL_ENDPOINT
SECRET_KEY
```

### Optional

The application has a documented safe default.

```text
LOG_LEVEL
TIMEOUT
MAX_RETRIES
```

### Example

```python
import os


def required(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(f"{name} is required")

    return value
```

Usage:

```python
api_key = required("API_KEY")
```

### Why empty strings matter

This:

```text
API_KEY=
```

is technically present but often not useful.

A required-secret validator should decide whether empty values are acceptable. In most application configurations, they should not be.

---

## 20. Configuration Validation

Configuration validation should happen before the application performs meaningful work.

A useful validation stack is:

```text
Presence
  ↓
Type
  ↓
Format
  ↓
Range
  ↓
Cross-field rules
  ↓
Application startup
```

### Example

```python
def validate_environment_name(value: str) -> str:
    allowed = {"development", "test", "staging", "production"}

    if value not in allowed:
        raise ValueError(
            f"APP_ENV must be one of {sorted(allowed)}"
        )

    return value
```

### Cross-field validation

Some settings are individually valid but invalid together.

Example:

```python
def validate_config(app_env: str, debug: bool) -> None:
    if app_env == "production" and debug:
        raise ValueError("DEBUG must be disabled in production")
```

This is important because validation is about a valid **configuration state**, not just valid individual fields.

---

## 21. `.env` Files

A `.env` file is a local file commonly used to store environment-style key-value pairs for development.

Example:

```dotenv
APP_ENV=development
PORT=8000
LOG_LEVEL=DEBUG
MODEL_NAME=local-model
API_KEY=local-development-secret
```

### Important distinction

A `.env` file is not the same thing as the operating-system process environment.

A Python application may need a tool or library to load a `.env` file into the process environment.

Python's standard `os` module does not automatically parse `.env` files.

### Safe mental model

```text
.env file
   ↓
loader/tool
   ↓
process environment
   ↓
Python configuration loader
```

### Why `.env` is useful

It is convenient for local development because developers can keep environment-specific local values outside the main source file.

### What `.env` is not

Do not assume:

```text
.env = production secret manager
```

A local file is not automatically a durable, centralized, audited, access-controlled production secret system.

---

## 22. Why `.env` Files Exist

Developers often need different local settings without changing source code.

A `.env` file provides a convenient developer-local representation.

For example:

```text
Project source code
        +
local .env
        ↓
development configuration
```

This can help with:

- local setup;
- developer onboarding;
- repeatable local runs;
- testing different local settings.

### Trade-off

A `.env` file is convenient but sensitive if it contains secrets.

Therefore:

```text
convenient
≠
safe to commit blindly
```

The production habit is to make the boundary explicit.

---

## 23. `.env` vs Operating-System Environment Variables

| Characteristic | `.env` file | Process environment |
|---|---|---|
| Form | Text file | Process key/value mapping |
| Location | Filesystem | Process context |
| Python stdlib access | Not automatic | `os.environ` / `os.getenv()` |
| Convenient for local development | Yes | Yes |
| Automatically a production secret store | No | No |
| May contain secrets | Yes, but should be protected | Yes |

The important design question is:

> Which source is authoritative for each environment?

For local development, a `.env` file may be convenient.

For production, values are commonly injected by the deployment/runtime environment or an appropriate configuration/secret mechanism.

This chapter does not attempt to teach a specific cloud or deployment platform.

---

## 24. `.env.example`

`.env.example` documents expected variables without containing real credentials.

Example:

```dotenv
APP_ENV=development
PORT=8000
LOG_LEVEL=INFO
MODEL_NAME=your-local-model
MODEL_TIMEOUT=30
MAX_RETRIES=3
API_KEY=
```

### Why commit `.env.example`?

It acts as an onboarding contract.

A new developer can see:

```text
Which variables exist?
Which are optional?
Which have examples?
Which require a secret?
```

### What should not be committed

Do not put:

```dotenv
API_KEY=real-secret
```

in `.env.example`.

Use a placeholder:

```dotenv
API_KEY=
```

or:

```dotenv
API_KEY=replace-me
```

The placeholder must never look like a real credential that could accidentally be interpreted as one.

---

## 25. Secrets and Sensitive Configuration

A secret is a value whose disclosure could allow unauthorized access or impersonation.

Examples:

```text
API keys
passwords
access tokens
private signing material
```

### Treat secrets differently

A secret should generally:

- not be hard-coded;
- not be committed to source control;
- not be printed in logs;
- not be placed in example files as a real value;
- be supplied through an appropriate protected mechanism in production.

### Important distinction

Not all configuration is sensitive.

```text
LOG_LEVEL=INFO
```

is generally not a secret.

```text
API_KEY=<credential>
```

is sensitive.

This distinction helps avoid both under-protection and unnecessary complexity.

---

## 26. Why Secrets Must Not Be Committed

Consider:

```python
API_KEY = "real-looking-secret"
```

Even if the repository is private today, this creates avoidable risk.

Source repositories can be:

```text
cloned
backed up
forked
shared
logged
indexed
copied
```

### Important incident principle

If a real credential is accidentally committed, changing the file later is not enough.

The credential may already exist in repository history or other copies.

The safe production response is conceptually:

```text
Secret exposed
    ↓
Treat as compromised
    ↓
Revoke/rotate credential
    ↓
Remove it from active configuration
    ↓
Audit how it was exposed
```

Do not rely on `.gitignore` as a magic erase button.

---

## 27. `.gitignore`

A local `.env` file containing secrets is commonly excluded with:

```gitignore
.env
```

A project may also choose patterns such as:

```gitignore
.env.*
!.env.example
```

The exact pattern should match the project's file naming convention.

### Important warning

`.gitignore` prevents untracked files from being added accidentally.

It does **not** remove an already tracked file.

That means:

```text
already committed secret
```

and:

```text
.gitignore added later
```

is not a complete fix.

### Safe project convention

```text
.env            → local/private
.env.example    → tracked template
```

---

## 28. Environment-Specific Configuration

The same application may run under different environments:

```text
development
test
staging
production
```

The source code should normally remain the same.

Configuration changes instead.

Example:

```text
Development:
APP_ENV=development
LOG_LEVEL=DEBUG
MODEL_NAME=development-model

Production:
APP_ENV=production
LOG_LEVEL=INFO
MODEL_NAME=production-model
```

### What should vary?

Potentially:

- endpoint;
- model selection;
- log verbosity;
- timeout;
- retry count;
- feature flags;
- batch size;
- worker count.

### What should not vary through accidental source edits?

Avoid:

```python
if production:
    model_name = "production-model"
else:
    model_name = "development-model"
```

for every environment difference.

Environment-specific behavior is often cleaner when the variation is a deliberate configuration input.

---

## 29. Development vs Test vs Staging vs Production

A useful conceptual model is:

### Development

Optimized for local feedback and debugging.

```text
LOG_LEVEL=DEBUG
```

### Test

Optimized for repeatable automated checks.

```text
APP_ENV=test
```

Configuration should be deterministic and isolated from a developer's personal environment.

### Staging

Designed to resemble production enough to catch integration/configuration problems before production.

### Production

Values are selected for real users and real operational constraints.

```text
APP_ENV=production
LOG_LEVEL=INFO
```

### Important principle

Environment names should have documented meaning.

Do not create a system where:

```text
staging
```

means one thing to one developer and another thing to another developer.

---

## 30. Configuration Precedence

A Python application may receive configuration from multiple sources.

For example:

```text
Built-in safe defaults
        ↓
Configuration file
        ↓
Local .env
        ↓
Environment variables
        ↓
Explicit runtime overrides
```

This is an example precedence design, not a Python language rule.

There is no universal Python rule saying that this exact sequence must always be used.

### Why precedence matters

Suppose:

```text
.env
PORT=8000
```

and:

```text
process environment
PORT=9000
```

Which one wins?

If the application does not define the answer, different components can make different assumptions.

### Production habit

Document precedence explicitly.

For example:

```text
1. Explicit function arguments
2. Process environment
3. Local .env for development
4. Safe application defaults
```

The exact order can differ, but it should be intentional.

---

## 31. Explicit Configuration Objects

Scattered environment-variable reads create hidden dependencies.

Instead of:

```python
def run_model():
    timeout = int(os.getenv("MODEL_TIMEOUT", "30"))
    model = os.getenv("MODEL_NAME", "default-model")
    ...
```

centralize configuration.

A simple first step is a dictionary:

```python
config = {
    "model_name": "default-model",
    "timeout": 30.0,
}
```

A stronger production-oriented design is a typed object.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    environment: str
    port: int
    timeout: float
    log_level: str
```

### Why explicit objects help

They provide:

- one place to define configuration;
- type information;
- easier validation;
- clearer dependency passing;
- easier testing;
- reduced hidden global state.

Instead of asking every function to discover its own configuration, the application can give the function what it needs.

---

## 32. Dataclasses for Configuration

`dataclasses.dataclass` can generate useful boilerplate for data-oriented classes.

Example:

```python
from dataclasses import dataclass


@dataclass
class AppConfig:
    environment: str
    port: int
    timeout: float
    log_level: str
```

Create an instance:

```python
config = AppConfig(
    environment="development",
    port=8000,
    timeout=30.0,
    log_level="DEBUG",
)

print(config)
```

### Why a dataclass fits configuration

A configuration object is usually:

```text
structured data
+
clear field names
+
known types
```

A dataclass expresses that naturally.

### Frozen configuration

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    environment: str
    port: int
    timeout: float
    log_level: str
```

Now ordinary field reassignment is blocked:

```python
config = AppConfig(
    environment="production",
    port=8000,
    timeout=30.0,
    log_level="INFO",
)

config.port = 9000
```

The assignment raises `FrozenInstanceError`.

### Important nuance

`frozen=True` does not magically make every nested object deeply immutable.

For example:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    labels: list[str]
```

The field cannot be rebound normally, but the list itself remains mutable.

Configuration design should prefer immutable nested structures when true deep immutability is important.

---

## 33. Configuration Loading Functions

A central loading function creates a clean boundary:

```python
def load_config() -> AppConfig:
    ...
```

A simplified example:

```python
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    environment: str
    port: int
    timeout: float
    log_level: str


def load_config() -> AppConfig:
    environment = os.getenv("APP_ENV", "development")
    port = int(os.getenv("PORT", "8000"))
    timeout = float(os.getenv("MODEL_TIMEOUT", "30"))
    log_level = os.getenv("LOG_LEVEL", "INFO")

    return AppConfig(
        environment=environment,
        port=port,
        timeout=timeout,
        log_level=log_level,
    )
```

### Better: validate before construction

```python
def load_config() -> AppConfig:
    environment = validate_environment_name(
        os.getenv("APP_ENV", "development")
    )

    port = parse_port(os.getenv("PORT", "8000"))
    timeout = parse_timeout(os.getenv("MODEL_TIMEOUT", "30"))
    log_level = os.getenv("LOG_LEVEL", "INFO")

    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
        raise ValueError("Invalid LOG_LEVEL")

    return AppConfig(
        environment=environment,
        port=port,
        timeout=timeout,
        log_level=log_level,
    )
```

The important design is:

```text
raw inputs
  ↓
parse
  ↓
validate
  ↓
typed AppConfig
```

---

## 34. Startup Validation

A production application should validate its configuration during startup.

Conceptually:

```text
Start
 ↓
Load configuration
 ↓
Parse configuration
 ↓
Validate configuration
 ↓
Invalid?
 ├── yes → fail startup
 └── no  → initialize application
```

### Bad behavior

```text
application starts
   ↓
30 minutes of operation
   ↓
user triggers model feature
   ↓
MODEL_NAME missing
   ↓
request fails
```

### Better behavior

```text
application starts
   ↓
configuration validation
   ↓
MODEL_NAME missing
   ↓
startup fails clearly
```

### Why fail early?

Fail-fast validation provides:

- clearer deployment feedback;
- predictable startup;
- easier debugging;
- fewer partially initialized applications;
- faster detection of configuration mistakes.

---

## 35. Fail-Fast Configuration

Fail-fast configuration means invalid required settings prevent the application from entering normal operation.

Example:

```python
import os


def require_non_empty(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(f"{name} is required")

    return value


api_key = require_non_empty("API_KEY")
```

If `API_KEY` is missing, the application does not continue silently.

### Fail-fast does not mean

Do not catch every startup error and replace it with:

```text
"Using default."
```

That can hide real configuration problems.

The objective is:

```text
invalid configuration
→ clear failure
→ clear diagnostic
```

---

## 36. Configuration Immutability

Configuration often represents a snapshot of the intended runtime state.

That means mutating it halfway through execution can make behavior difficult to reason about.

Consider:

```python
config.timeout = 5
```

in one module, followed by another module assuming:

```python
config.timeout == 30
```

That creates hidden coupling.

### Prefer stable configuration

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    timeout: float
```

Create once:

```python
config = AppConfig(timeout=30.0)
```

Then pass it explicitly.

### Why this helps

Stable configuration improves:

- predictability;
- testability;
- reasoning;
- debugging;
- reproducibility.

### When mutation may be justified

Some systems intentionally support dynamic configuration.

That is a different design problem and should be explicit.

Do not make a mutable global configuration object "dynamic" accidentally.

---

## 37. Avoiding Global Configuration Problems

A global configuration object can be convenient:

```python
CONFIG = {
    "timeout": 30,
}
```

but it creates potential hidden dependencies.

Any module can read or modify it.

### Problems

```text
hidden dependency
accidental mutation
harder tests
unclear ownership
order-dependent behavior
```

### Better

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    timeout: float


def process_document(config: AppConfig) -> None:
    print(config.timeout)
```

The dependency is explicit.

### Important nuance

Global state is not automatically wrong.

The question is:

> Is the lifetime, ownership, mutability, and visibility of this state intentional?

For a small script, a module-level constant may be perfectly reasonable.

For a larger application, centralized immutable configuration plus explicit dependency passing is often easier to maintain.

---

## 38. Testing Configuration

Configuration code should be tested like any other code.

Important cases include:

```text
valid input
missing required input
invalid type
invalid range
default value
invalid environment name
Boolean parsing
precedence
cross-field validation
```

### Avoid accidental machine dependence

A test should not silently depend on the developer's existing:

```text
HOME
PATH
APP_ENV
PORT
API_KEY
```

### Example with environment manipulation

```python
import os


def read_required_mode() -> str:
    value = os.getenv("APP_MODE")

    if value is None:
        raise RuntimeError("APP_MODE is required")

    return value
```

A test can explicitly control the environment:

```python
def test_required_mode(monkeypatch):
    monkeypatch.setenv("APP_MODE", "test")

    assert read_required_mode() == "test"
```

The test now describes its environment rather than inheriting one accidentally.

### Important testing principle

Configuration tests should be isolated from the machine where they happen to run.

---

## 39. Testing Different Environments

You may need to test:

```text
development
test
staging
production
```

without actually running in four physical environments.

Instead, test the configuration model.

Example:

```python
def build_config(environment: str, debug: bool) -> AppConfig:
    if environment not in {
        "development",
        "test",
        "staging",
        "production",
    }:
        raise ValueError("Unknown environment")

    if environment == "production" and debug:
        raise ValueError("debug is not allowed in production")

    return AppConfig(
        environment=environment,
        port=8000,
        timeout=30.0,
        log_level="INFO",
    )
```

Tests can verify:

```text
development accepted
test accepted
staging accepted
production accepted
production + debug rejected
```

### Important idea

Environment behavior should be testable as data and rules, not only by launching the entire application.

---

## 40. Debugging Configuration Problems

Configuration failures are often simple once you inspect the right layer.

Use this workflow:

```text
1. What value does the application expect?
2. Where should the value come from?
3. Did the process receive it?
4. What raw value did it receive?
5. Was it converted correctly?
6. Was it validated?
7. Did another source override it?
8. Did startup validation run?
```

### Problem 1 — missing variable

```python
port = int(os.getenv("PORT"))
```

If `PORT` is absent:

```text
TypeError
```

because:

```python
os.getenv("PORT")
```

returns `None`, and:

```python
int(None)
```

is invalid.

### Better

```python
port = int(os.getenv("PORT", "8000"))
```

or perform explicit required-variable validation.

---

## 41. Configuration Observability

Configuration must be observable enough to diagnose startup problems, but diagnostics must not reveal secrets.

Good diagnostic information may include:

```text
Environment: production
Port: 8000
Log level: INFO
Model name: production-model
API key: <configured>
```

### Avoid

```python
print(os.environ)
```

The environment may contain secrets.

### Safer approach

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class SafeConfigSummary:
    environment: str
    port: int
    log_level: str
    api_key_configured: bool
```

Build the summary:

```python
summary = SafeConfigSummary(
    environment=config.environment,
    port=config.port,
    log_level=config.log_level,
    api_key_configured=bool(config.api_key),
)
```

### Important principle

Observability should expose:

```text
state
status
metadata
```

without exposing:

```text
credential values
```

---

## 42. Safe Configuration Logging

This is unsafe:

```python
print(config)
```

if the configuration object contains:

```python
api_key
password
token
secret
```

Instead, design a redacted representation.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    environment: str
    api_key: str
    timeout: float

    def safe_summary(self) -> dict[str, object]:
        return {
            "environment": self.environment,
            "api_key": "<configured>" if self.api_key else "<missing>",
            "timeout": self.timeout,
        }
```

Then:

```python
print(config.safe_summary())
```

Expected shape:

```text
{
    'environment': 'production',
    'api_key': '<configured>',
    'timeout': 30.0
}
```

### Do not partially expose secrets

Avoid:

```python
print(api_key[:4])
```

unless your organization's security policy explicitly allows it. Even partial identifiers can create unnecessary exposure.

A safer default is:

```text
<configured>
```

---

## 43. Configuration Anti-Patterns

### Anti-pattern 1 — hard-coded secret

```python
API_KEY = "real-secret"
```

**Why:** secret becomes source-code data.

**Better:** inject it from a protected configuration mechanism.

---

### Anti-pattern 2 — environment reads everywhere

```python
def a():
    return os.getenv("TIMEOUT")


def b():
    return os.getenv("TIMEOUT")
```

**Why:** configuration semantics become distributed.

**Better:** load once and pass an explicit configuration object.

---

### Anti-pattern 3 — no validation

```python
port = int(os.getenv("PORT", "8000"))
```

with no range check.

**Why:** syntactically valid values can still be semantically invalid.

**Better:** validate ranges and relationships.

---

### Anti-pattern 4 — Boolean bug

```python
debug = bool(os.getenv("DEBUG", "false"))
```

**Why:** `"false"` is a non-empty string and therefore truthy.

**Better:** explicit Boolean parsing.

---

### Anti-pattern 5 — printing the whole environment

```python
print(os.environ)
```

**Why:** secret leakage.

**Better:** safe summaries.

---

### Anti-pattern 6 — committing `.env`

```text
.env
```

contains credentials and is committed.

**Why:** secrets become part of repository history.

**Better:** ignore `.env`; commit `.env.example`.

---

### Anti-pattern 7 — real secrets in `.env.example`

```dotenv
API_KEY=real-key
```

**Why:** the example file becomes sensitive.

**Better:**

```dotenv
API_KEY=
```

---

### Anti-pattern 8 — mutable global config

```python
CONFIG["timeout"] = 1
```

from arbitrary modules.

**Why:** hidden state changes.

**Better:** immutable configuration and explicit ownership.

---

### Anti-pattern 9 — environment-specific code edits

```python
MODEL_NAME = "staging-model"
```

changed manually before every deployment.

**Why:** source code becomes the configuration mechanism.

**Better:** keep model selection as configuration.

---

### Anti-pattern 10 — late failure

Configuration is only validated when a specific feature is called.

**Why:** deployment can appear healthy while known invalid configuration exists.

**Better:** validate during startup.

---

## 44. Production Configuration Architecture

A practical architecture is:

```text
                Configuration Sources
                        │
          ┌─────────────┼──────────────┐
          │             │              │
      defaults        .env        environment
          │             │              │
          └─────────────┴──────────────┘
                        ↓
                 precedence rules
                        ↓
                  raw configuration
                        ↓
                    parsing
                        ↓
                   validation
                        ↓
                 AppConfig object
                        ↓
                application startup
                        ↓
         ┌──────────────┼──────────────┐
         ↓              ↓              ↓
     model client   file processor   workers
```

### Ownership

A useful rule is:

```text
Configuration loader owns:
    reading
    parsing
    validation
    normalization

Application components own:
    business/application behavior
```

### Benefits

- fewer hidden dependencies;
- easier tests;
- clear startup failures;
- explicit configuration contract;
- simpler component APIs.

---

## 45. Applied AI Engineering Examples

Configuration becomes particularly important as AI applications grow.

### LLM application

```text
MODEL_PROVIDER
MODEL_NAME
API_BASE_URL
REQUEST_TIMEOUT
MAX_RETRIES
```

These determine how the application talks to a model service.

### Embedding pipeline

```text
EMBEDDING_MODEL
BATCH_SIZE
CHUNK_SIZE
WORKER_COUNT
```

These control pipeline behavior.

### RAG application

```text
EMBEDDING_MODEL
TOP_K
CHUNK_SIZE
RETRIEVAL_TIMEOUT
```

These influence retrieval behavior.

### Agent system

```text
MODEL_NAME
MAX_STEPS
TOOL_TIMEOUT
MAX_CONCURRENT_TASKS
```

These can constrain agent behavior.

### AI data processing

```text
INPUT_PATH
OUTPUT_PATH
BATCH_SIZE
WORKER_COUNT
```

### Configuration vs secrets in AI

```text
MODEL_NAME       → configuration
TIMEOUT          → configuration
MAX_STEPS        → configuration

API_KEY          → secret
ACCESS_TOKEN     → secret
```

Do not put the distinction aside just because the application is AI-enabled.

---

## 46. Production Example

### Production AI Document Processing Service

Suppose a service processes documents:

```text
Document
   ↓
Text extraction
   ↓
Chunking
   ↓
Model/embedding processing
   ↓
Storage
```

The application needs:

```text
APP_ENV
MODEL_NAME
MODEL_TIMEOUT
MAX_RETRIES
BATCH_SIZE
LOG_LEVEL
API_KEY
```

### Step 1 — raw environment values

```python
import os

app_env = os.getenv("APP_ENV", "development")
model_name = os.getenv("MODEL_NAME", "local-model")
model_timeout_raw = os.getenv("MODEL_TIMEOUT", "30")
batch_size_raw = os.getenv("BATCH_SIZE", "16")
api_key = os.getenv("API_KEY")
```

### Step 2 — parse values

```python
model_timeout = float(model_timeout_raw)
batch_size = int(batch_size_raw)
```

### Step 3 — validate

```python
allowed_envs = {
    "development",
    "test",
    "staging",
    "production",
}

if app_env not in allowed_envs:
    raise ValueError("Invalid APP_ENV")

if model_timeout <= 0:
    raise ValueError("MODEL_TIMEOUT must be positive")

if batch_size <= 0:
    raise ValueError("BATCH_SIZE must be positive")

if app_env == "production" and not api_key:
    raise ValueError("API_KEY is required in production")
```

### Step 4 — construct configuration

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    app_env: str
    model_name: str
    model_timeout: float
    batch_size: int
    api_key: str | None
```

Then:

```python
config = AppConfig(
    app_env=app_env,
    model_name=model_name,
    model_timeout=model_timeout,
    batch_size=batch_size,
    api_key=api_key,
)
```

### Step 5 — application components use the object

```python
def process_documents(config: AppConfig) -> None:
    print(
        f"model={config.model_name}, "
        f"batch_size={config.batch_size}"
    )
```

### Design decisions

**Why centralize configuration?**

Because application components should not repeatedly inspect the process environment.

**Why parse early?**

Because runtime code should receive usable Python values.

**Why validate early?**

Because invalid deployment configuration should fail before document processing starts.

**Why keep the config immutable?**

Because runtime mutation creates hidden state changes.

**Why keep the API key separate conceptually?**

Because it is sensitive even though it is technically part of the application's runtime configuration.

---

## 47. Common Mistakes

### Mistake 1 — assuming environment variables have Python types

Wrong mental model:

```text
PORT=8000
→ Python integer
```

Correct model:

```text
PORT=8000
→ "8000"
→ int("8000")
→ 8000
```

### Mistake 2 — using truthiness for Boolean strings

Wrong:

```python
bool("false")
```

Correct approach:

```python
parse_bool("false")
```

### Mistake 3 — treating `.env` as automatically loaded

A `.env` file does not become part of `os.environ` merely because it exists on disk. A loader must explicitly bridge the two concepts.

### Mistake 4 — hiding required configuration behind defaults

Wrong:

```python
api_key = os.getenv("API_KEY", "fake")
```

This can turn a real configuration error into a hidden security or connectivity problem.

### Mistake 5 — logging sensitive configuration

Wrong:

```python
print(api_key)
```

Better:

```text
API key: <configured>
```

### Mistake 6 — changing source code for every environment

Do not manually edit source code before deployment just to replace endpoint or model settings.

### Mistake 7 — allowing unrelated modules to mutate configuration

Use a stable configuration object and explicit dependencies.

---

## 48. Exercises

These exercises are designed to reinforce the chapter progressively.

### Beginner Exercise 1 — Read an Environment Variable

**Objective**

Read `APP_ENV` with `os.getenv()` and print a safe default of `"development"`.

**Requirements**

- use `os.getenv()`;
- do not use `os.environ[...]`;
- display the resolved value.

**Expected behavior**

If the variable is absent:

```text
development
```

If present:

```text
staging
```

**Hint**

Remember that the second argument to `os.getenv()` can be the default.

---

### Beginner Exercise 2 — Parse a Port

**Objective**

Read `PORT` and convert it to an integer.

**Requirements**

- default to `8000`;
- reject values outside `1..65535`.

**Hint**

Separate parsing from range validation.

---

### Beginner Exercise 3 — Safe Boolean

Implement:

```text
parse_bool(raw: str) -> bool
```

It must accept:

```text
true
false
yes
no
1
0
```

case-insensitively.

Reject unknown values.

**Learning outcome**

Understand why `bool("false")` is not a configuration parser.

---

### Beginner Exercise 4 — Required Variable

Create:

```text
require_non_empty(name: str) -> str
```

It should reject:

```text
missing
empty string
whitespace-only string
```

**Production question**

Why should a required API credential fail at startup?

---

### Intermediate Exercise 5 — Build `AppConfig`

Create:

```python
@dataclass(frozen=True)
class AppConfig:
    ...
```

Include:

```text
environment
port
timeout
log_level
```

Then create a loader.

**Requirements**

- type conversion;
- validation;
- immutable result.

---

### Intermediate Exercise 6 — Cross-Field Validation

Design validation where:

```text
APP_ENV=production
DEBUG=true
```

is rejected.

**Question**

Why is this different from checking whether `APP_ENV` and `DEBUG` are individually valid?

---

### Intermediate Exercise 7 — Safe Diagnostics

Write:

```python
safe_summary(config)
```

It must report:

```text
environment
port
log level
whether API key is configured
```

It must never expose the API key value.

---

### Intermediate Exercise 8 — Test Isolation

Write tests where each test explicitly sets the environment variables it needs.

**Requirements**

- do not depend on a developer's personal environment;
- test both present and missing values;
- test invalid values.

---

### Advanced Exercise 9 — Configuration Precedence

Define a simple precedence system:

```text
defaults
→ .env conceptually
→ process environment
```

Write a function that merges values according to the documented order.

**Question**

Why must precedence be explicit?

---

### Advanced Exercise 10 — Environment-Specific Rules

Define configuration rules for:

```text
development
test
staging
production
```

Include at least one cross-field validation rule.

---

### Advanced Exercise 11 — AI Service Configuration

Design configuration for an AI service with:

```text
MODEL_NAME
MODEL_TIMEOUT
MAX_RETRIES
BATCH_SIZE
API_KEY
```

Classify each as:

```text
configuration
or
secret
```

Then design `AppConfig`.

---

### Production Exercise 12 — Refactor Scattered Environment Reads

Start from:

```python
def process():
    model = os.getenv("MODEL_NAME")
    timeout = float(os.getenv("MODEL_TIMEOUT", "30"))
    ...
```

Refactor so:

```text
environment
→ load_config()
→ AppConfig
→ process(config)
```

Explain why the second design is easier to test.

---

### Production Exercise 13 — Broken Deployment Configuration

Scenario:

```text
Developer says:
"The variable exists in my terminal."

Application says:
"MODEL_NAME is missing."
```

Write a diagnostic checklist to determine where the mismatch occurs.

---

### Production Exercise 14 — `.env.example`

Design a `.env.example` containing:

```text
APP_ENV
MODEL_NAME
MODEL_TIMEOUT
MAX_RETRIES
API_KEY
```

Use placeholders only.

---

### Exercise Quality Check

For each exercise, practice the full loop:

```text
Understand
    ↓
Predict
    ↓
Plan
    ↓
Implement
    ↓
Test
    ↓
Debug
    ↓
Refactor
    ↓
Explain
```

Do not read the model answer to an exercise until you have attempted your own implementation.

---

## 49. Mini-Project

# Mini-Project — Production-Ready Python Configuration System

Build a small, self-contained configuration subsystem documented entirely in this chapter.

The project should require no cloud service.

### Problem statement

Create a configuration system for a Python AI-processing application.

The application requires:

```text
APP_ENV
PORT
LOG_LEVEL
MODEL_NAME
MODEL_TIMEOUT
MAX_RETRIES
BATCH_SIZE
API_KEY
```

### Classification

```text
APP_ENV        → configuration
PORT           → configuration
LOG_LEVEL      → configuration
MODEL_NAME     → configuration
MODEL_TIMEOUT  → configuration
MAX_RETRIES    → configuration
BATCH_SIZE     → configuration
API_KEY        → secret
```

### Desired architecture

```text
Environment / local configuration
             ↓
       raw string values
             ↓
        configuration parser
             ↓
           validation
             ↓
       immutable AppConfig
             ↓
       application components
```

### Requirements

1. Read environment values.
2. Apply documented defaults.
3. Parse integers and floating-point values.
4. Parse Boolean values if you choose to add a debug flag.
5. Validate required values.
6. Validate numeric ranges.
7. Validate environment names.
8. Validate at least one cross-field rule.
9. Keep the final configuration immutable.
10. Provide safe diagnostics.
11. Keep secrets out of diagnostics.
12. Include tests.
13. Document `.env.example`.
14. Explain which source wins when multiple sources exist.

### Suggested configuration class

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    app_env: str
    port: int
    log_level: str
    model_name: str
    model_timeout: float
    max_retries: int
    batch_size: int
    api_key: str | None
```

### Suggested loader shape

```python
def load_config() -> AppConfig:
    ...
```

### Suggested helper functions

```python
def require_non_empty(name: str) -> str:
    ...


def parse_int(raw: str, name: str) -> int:
    ...


def parse_positive_float(raw: str, name: str) -> float:
    ...


def validate_environment_name(raw: str) -> str:
    ...
```

### Required test cases

Test at least:

```text
valid development configuration
valid production configuration
missing production API key
invalid port
invalid timeout
invalid retries
invalid batch size
invalid environment
default values
safe diagnostics
```

### Edge cases

Consider:

```text
APP_ENV=""
PORT="abc"
PORT="0"
PORT="70000"
MODEL_TIMEOUT="-1"
MAX_RETRIES="-5"
BATCH_SIZE="0"
API_KEY="   "
```

### Production limitations

This project is still a learning subsystem.

A real production application may use a platform-specific configuration or secret mechanism. This chapter intentionally does not prescribe one cloud provider or deployment system.

The project goal is to build strong Python-level configuration habits first.

---

## 50. Interview Questions

### Basic

**Question:** What is an environment variable?

**Model answer:** A named value provided to a process through its execution environment. Python exposes environment variables through the `os` module.

---

**Question:** Why are environment variables normally strings?

**Model answer:** The process environment is a string-based key-value interface. Applications interpret those strings as integers, floats, Booleans, paths, or other types.

---

**Question:** What is `os.getenv()`?

**Model answer:** It reads an environment variable and optionally returns a default if the variable is missing.

---

**Question:** What happens with `os.environ["X"]` when `X` is missing?

**Model answer:** A `KeyError` is raised.

---

**Question:** What is a `.env` file?

**Model answer:** A convention for storing environment-style key-value values, commonly used for local development. Python does not automatically load it into `os.environ`; a loader is needed.

### Intermediate

**Question:** Why should configuration be centralized?

**Model answer:** Centralization creates one place for parsing, validation, precedence, and documentation, reducing hidden dependencies and inconsistent behavior.

---

**Question:** Why is `.env.example` useful?

**Model answer:** It documents the configuration contract and helps onboarding without containing real secrets.

---

**Question:** Why should `.env` usually be ignored by Git?

**Model answer:** Local `.env` files often contain secrets or machine-specific values that should not be tracked.

---

**Question:** Why is `.gitignore` not enough after a secret has been committed?

**Model answer:** `.gitignore` prevents future tracking; it does not erase data that already exists in repository history or other copies.

---

**Question:** Why use `@dataclass(frozen=True)` for configuration?

**Model answer:** It gives a structured typed object and prevents ordinary field reassignment, improving predictability. It does not guarantee deep immutability.

### Advanced

**Question:** How would you design configuration for development, staging, and production?

**Model answer:** Keep application behavior in source code and supply environment-specific values through a documented configuration contract. Define precedence and validate startup configuration.

---

**Question:** How would you prevent secrets from appearing in logs?

**Model answer:** Do not serialize or print raw configuration containing secrets. Produce a safe summary with flags such as `<configured>`.

---

**Question:** Why is `bool(os.getenv("DEBUG"))` dangerous?

**Model answer:** Because a non-empty string such as `"false"` is truthy in Python.

---

**Question:** Why is centralized configuration easier to test?

**Model answer:** Configuration parsing and validation can be tested separately, and application components can receive an explicit configuration object instead of reading machine-specific environment state.

### Applied AI

**Question:** Which AI settings are usually configuration rather than secrets?

**Model answer:** Examples include model name, timeout, retry count, batch size, and feature limits. Credentials such as API keys are sensitive secrets.

---

**Question:** Why might model version be part of configuration?

**Model answer:** Changing the model can change application behavior, latency, cost, or output characteristics without requiring a source-code change.

---

## 51. Architecture Questions

### Scenario 1 — Same application, multiple environments

The same Python application runs in development, staging, and production.

**Questions**

- Where should environment-specific values live?
- How should precedence be defined?
- When should validation run?

**Expected reasoning**

Use configuration rather than source edits. Define an explicit precedence model. Validate before the application begins normal operation.

---

### Scenario 2 — Production AI service

The service needs:

```text
MODEL_NAME
MODEL_TIMEOUT
MAX_RETRIES
API_KEY
```

**Questions**

- Which are secrets?
- Which are normal configuration?
- How should the application receive them?
- How should diagnostics behave?

**Expected reasoning**

`API_KEY` is sensitive. The other values are ordinary runtime configuration. Load and validate them centrally. Never print the key.

---

### Scenario 3 — Scattered `os.getenv()`

Twenty modules each call `os.getenv()` independently.

**Risks**

```text
duplicated parsing
different defaults
different validation
hidden dependencies
difficult testing
```

**Refactoring**

Move environment interpretation to one configuration boundary.

```text
environment
   ↓
load_config()
   ↓
AppConfig
   ↓
modules
```

---

### Scenario 4 — Startup succeeds, request later fails

A production deployment starts successfully but crashes when the model feature is first used because a required variable is missing.

**Root problem**

Validation happened too late.

**Design improvement**

Move required-variable validation to startup.

---

### Scenario 5 — Secret accidentally committed

A developer commits an API credential.

**Expected defensive reasoning**

```text
Treat credential as compromised
        ↓
Rotate/revoke it
        ↓
Remove it from active use
        ↓
Replace with safe configuration
        ↓
Review how the exposure occurred
```

Do not assume that deleting the latest version from the repository is sufficient.

---

### Scenario 6 — Configuration changed unexpectedly

A developer reports:

```text
.env says PORT=8000
but Python sees PORT=9000
```

**Questions**

- Which source is authoritative?
- What is the precedence order?
- Was a process-level variable injected?
- Was the `.env` file actually loaded?

The correct answer depends on the application's documented configuration contract.

---

### Scenario 7 — Long-running AI worker

A worker should use one stable configuration snapshot during a job.

**Design reasoning**

A centralized immutable `AppConfig` passed to the worker makes the configuration state explicit and avoids accidental mid-job mutation.

---

## 52. Final Mental Model

The full configuration journey is:

```text
Configuration Source
        ↓
        Load
        ↓
        Parse
        ↓
      Validate
        ↓
      Normalize
        ↓
   Stabilize / Freeze
        ↓
     AppConfig
        ↓
    Application
        ↓
 Predictable Behavior
```

For environment variables, think:

```text
Shell / process launcher
        ↓
Process environment
        ↓
os.environ / os.getenv()
        ↓
raw strings
        ↓
type conversion
        ↓
validation
        ↓
typed configuration object
        ↓
application component
```

### The three-way separation

```text
Application Code
    = what the program does

Configuration
    = how the program is configured

Secrets
    = sensitive credentials needed by the program
```

### The most important production principle

Do not let every module discover configuration on its own.

Prefer:

```text
load once
  ↓
validate once
  ↓
represent clearly
  ↓
pass explicitly
```

### If you remember only 15 things

1. Configuration controls application behavior without requiring source-code changes.
2. Environment variables are provided to a process through its environment.
3. Python reads them through `os.environ` and `os.getenv()`.
4. Environment values are normally strings.
5. Strings must be converted into the Python types your application expects.
6. Never parse Boolean configuration with `bool(raw_string)` blindly.
7. Required configuration should fail fast.
8. Optional configuration can use safe documented defaults.
9. Validation should happen near application startup.
10. `.env` is a local-development convenience, not automatically a production secret system.
11. `.env.example` documents expected configuration without real secrets.
12. `.gitignore` helps prevent accidental tracking but does not erase previously committed secrets.
13. Centralize configuration instead of scattering environment reads across application code.
14. An immutable configuration object can make runtime behavior easier to reason about.
15. Choose configuration boundaries deliberately: source, process environment, loading, parsing, validation, and application use each have different responsibilities.

### Final engineering question

Before adding a new setting, ask:

```text
What value is changing?
Why does it vary?
Is it configuration or a secret?
Where should it come from?
What is its type?
What is its valid range?
What is the precedence?
When should it be validated?
Can it be safely logged?
How will it be tested?
```

If you can answer those questions, configuration is no longer an ad-hoc collection of environment-variable reads. It has become an explicit engineering subsystem.

---

## 53. Completion Checklist

Use this checklist only after you have worked through the chapter and exercises.

### Fundamentals

- [ ] I understand what configuration is.
- [ ] I understand why configuration should be separated from code.
- [ ] I can distinguish code, configuration, data, and secrets.
- [ ] I understand environment variables.
- [ ] I understand the process-environment boundary.

### Python access

- [ ] I can use `os.environ`.
- [ ] I can use `os.getenv()`.
- [ ] I understand `os.environ.get()`.
- [ ] I know the difference between required and optional lookups.
- [ ] I know that environment variables are strings.

### Parsing and validation

- [ ] I can parse integers.
- [ ] I can parse floating-point values.
- [ ] I can parse Booleans safely.
- [ ] I can parse simple lists.
- [ ] I can validate ranges.
- [ ] I can validate allowed values.
- [ ] I can perform cross-field validation.
- [ ] I understand fail-fast startup validation.

### `.env` workflow

- [ ] I understand what a `.env` file is.
- [ ] I understand that Python does not automatically load `.env`.
- [ ] I understand the role of a `.env` loader.
- [ ] I can design a `.env.example`.
- [ ] I understand why real secrets do not belong in `.env.example`.

### Secret hygiene

- [ ] I understand why real secrets should not be committed.
- [ ] I understand the purpose of `.gitignore`.
- [ ] I understand why `.gitignore` does not erase already committed secrets.
- [ ] I can design safe configuration diagnostics.

### Architecture

- [ ] I can centralize configuration.
- [ ] I can use a dataclass for configuration.
- [ ] I understand `frozen=True`.
- [ ] I understand that `frozen=True` is not deep immutability.
- [ ] I can define configuration precedence.
- [ ] I can test configuration without depending on my personal machine environment.
- [ ] I can reason about development, test, staging, and production differences.

### Applied AI Engineering

- [ ] I can separate model configuration from model credentials.
- [ ] I can design configuration for an LLM application.
- [ ] I can design configuration for an embedding pipeline.
- [ ] I can design configuration for an agent system.
- [ ] I can validate AI-system configuration at startup.
- [ ] I can avoid exposing AI credentials in diagnostics.

### Final capability test

You should now be able to design this pipeline:

```text
Environment / local configuration
        ↓
Configuration source
        ↓
Precedence
        ↓
Loader
        ↓
Parser
        ↓
Validator
        ↓
Immutable AppConfig
        ↓
Explicit dependency passing
        ↓
Application behavior
```

The key production habit is:

> Keep application behavior in code, keep environment-specific settings outside that code, validate configuration early, and treat secrets as sensitive data.
