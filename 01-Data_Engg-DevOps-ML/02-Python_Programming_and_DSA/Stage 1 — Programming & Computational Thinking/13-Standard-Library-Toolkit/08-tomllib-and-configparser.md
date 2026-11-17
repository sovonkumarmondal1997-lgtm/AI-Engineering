# Lesson 08 — `tomllib` and `configparser`: Reliable Python Configuration

**Target runtime:** Python 3.12+ (version-sensitive behavior is called out).  
**Module:** Stage 1 — Programming & Computational Thinking → Module 13 — Standard Library Toolkit → Phase D — Config, Network and Runtime Utilities.

## Learning objectives

By the end of this lesson, you should be able to:

- Explain why configuration is separate from application logic and how defaults, files, environment variables, and CLI arguments interact.
- Parse TOML with `tomllib.load()` and `tomllib.loads()` and understand TOML's data model and read-only scope.
- Read legacy INI files with `configparser`, including defaults, interpolation, typed getters, and multiple files.
- Validate required and unknown keys, types, ranges, and nested configuration paths before a pipeline starts.
- Resolve precedence deterministically, deep-merge nested mappings, and convert the effective configuration into typed immutable settings.
- Handle secrets and configuration files without leaking sensitive values into logs.
- Test parsing, precedence, validation, and failure modes using isolated temporary files and controlled environment variables.

## Prerequisites and roadmap boundaries

The Module 13 roadmap lists environment variables and configuration in Module 1.5 (09) and Module 1.10 (01); CLI arguments in the earlier text/CLI module; validation and useful errors in the control-flow module; `pathlib`, encodings, dictionaries, mutability, and pytest fixtures in earlier lessons. Review those skills first if file paths, mappings, environment variables, or exceptions are unfamiliar.

This lesson comes after the standard-library lessons on files/processes/local data (`shutil`, `tempfile`, archives, `subprocess`, `sqlite3`) and security/numbers (`hashlib`, `hmac`, `secrets`, `uuid`, `random`, `statistics`). It precedes `urllib`, sockets, and runtime utilities. It teaches configuration parsing and composition—not a general secrets-management product, deployment platform, or third-party schema framework. Pydantic is a later-stage preview, not a requirement here.

## 1. Foundations: configuration is input

Configuration describes how a program should operate without changing its code: endpoints, paths, batch sizes, retry limits, enabled features, and logging levels. Separating it from logic makes deployments easier to adapt and tests easier to isolate. But a config file is still input: successfully parsing it does **not** mean values are valid, safe, authorized, or operationally sensible.

Common sources include:

1. **Code defaults** for safe non-secret behavior.
2. **A configuration file** for stable deployment-specific settings.
3. **Environment variables** for process/container deployment overrides and secret references.
4. **CLI arguments** for explicit, run-specific choices.
5. **Secret managers** for retrieving actual credentials under an identity/authorization policy.

This lesson uses the precedence rule **defaults < file < environment < CLI**: each later source overrides earlier sources. Pick one policy, document it, and apply it consistently. Some systems intentionally use another order; what matters is explicitness and testability.

A useful configuration lifecycle is:

```text
read source → parse → merge layers → validate schema and values → build typed settings → run application
```

Do not let individual business functions repeatedly read environment variables or config files. Load once at the application boundary and pass validated settings to components. Cache the validated immutable settings snapshot for the lifetime of a run rather than repeatedly reparsing files or sharing a mutable raw dictionary. If hot reload is needed, make it a deliberate feature: parse and validate a complete replacement, then atomically publish the new snapshot; never expose a half-merged configuration.

## 2. TOML with `tomllib`

### What TOML is

TOML is a human-readable configuration format with explicit types and tables. Python's `tomllib` is a standard-library **reader** introduced in Python 3.11. It does not serialize or write TOML. If a program must edit TOML while preserving comments and formatting, use a suitable writer such as the third-party `tomlkit`; a writer such as `tomli-w` can serialize values but should not be assumed to preserve comments.

### `load()` versus `loads()`

- `tomllib.load(file_object)` reads a **binary** file object. Open a TOML file with `Path.open("rb")` or `open(path, "rb")`.
- `tomllib.loads(text)` parses a Python `str` containing TOML text.
- Successful parsing returns Python dictionaries, lists, strings, integers, floats, booleans, and `datetime`/`date`/`time` values for TOML temporal types.
- Invalid TOML raises `tomllib.TOMLDecodeError`. Error attributes vary by Python version; Python 3.14 added more structured details. Do not rely on a particular message format or newer attributes when targeting Python 3.12.

```python
from pathlib import Path
import tomllib

CONFIG_TEXT = '''
[database]
host = "localhost"
port = 5432
enabled = true
connect_timeout = 3.5
labels = ["raw", "daily"]
created_at = 2026-01-15T12:30:00Z

[[jobs]]
name = "daily"
source = "events"

[[jobs]]
name = "hourly"
source = "metrics"
'''

parsed = tomllib.loads(CONFIG_TEXT)
assert parsed["database"]["port"] == 5432
assert parsed["database"]["enabled"] is True
assert parsed["jobs"][0]["name"] == "daily"

# File form: TOML must be opened in binary mode.
def load_toml(path: Path) -> dict:
    try:
        with path.open("rb") as file:
            return tomllib.load(file)
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        # Invalid UTF-8 may raise UnicodeDecodeError; syntax errors raise TOMLDecodeError.
        # Avoid depending on version-specific TOMLDecodeError attributes.
        raise ValueError(f"Invalid TOML or UTF-8 encoding in {path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Cannot read configuration file {path}: {exc}") from exc
```

**Why binary mode?** The `tomllib.load()` API expects a binary file object and decodes TOML according to the format's UTF-8 rules. Passing a text-mode file object violates its documented contract and raises a type-related error.

### TOML data model

| TOML construct | Example | Python result / note |
|---|---|---|
| String | `name = "worker"` | `str` |
| Integer | `port = 5432` | `int` |
| Float | `ratio = 0.25` | `float` |
| Boolean | `enabled = true` | `bool` |
| Date/time | `at = 2026-01-15T12:30:00Z` | `datetime.datetime` with timezone information for offset-aware values |
| Array | `regions = ["eu", "us"]` | `list` |
| Table | `[database]` | nested `dict` |
| Array of tables | `[[jobs]]` | list of dictionaries |

TOML distinguishes booleans from integers in the source grammar, although Python's `bool` is a subclass of `int`; validation should check `type(value) is bool` where an actual boolean is required, and `type(value) is int` if booleans must not count as integers.

### Parsing `pyproject.toml`

`pyproject.toml` uses TOML, but its tables have defined conventions. `[project]` is standardized by the Python packaging specification; `[tool.<name>]` is a tool-specific namespace. Do not assume every project's dependencies or settings appear under the same table.

```python
from pathlib import Path
import tomllib


def read_pyproject(path: Path = Path("pyproject.toml")) -> dict:
    """Read project metadata without performing I/O at import time."""
    try:
        with path.open("rb") as file:
            return tomllib.load(file)
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Invalid TOML or UTF-8 encoding in {path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc


if __name__ == "__main__":
    project = read_pyproject()
    metadata = project.get("project", {})
    print("project name:", metadata.get("name", "(not declared)"))
    print("project version:", metadata.get("version", "(not declared)"))
    ruff_config = project.get("tool", {}).get("ruff", {})
```

Use this for inspection and tooling, not as a replacement for a packaging tool's complete metadata validation.

## 3. INI with `configparser`

INI is common in older applications and simple tools. `configparser.ConfigParser` parses sections and key/value options, with string values converted using getters.

```python
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

parser = ConfigParser(interpolation=ExtendedInterpolation())
parser.read_string("""
[DEFAULT]
root = /srv/pipeline
log_level = INFO

[paths]
input = ${root}/input
output = ${root}/output

[batch]
size = 500
enabled = yes
""")

input_path = parser.get("paths", "input")
batch_size = parser.getint("batch", "size")
enabled = parser.getboolean("batch", "enabled")
log_level = parser.get("batch", "log_level", fallback="WARNING")
assert input_path == "/srv/pipeline/input"
assert batch_size == 500 and enabled is True
```

Important semantics:

- Section names are case-sensitive by default; **option names are case-insensitive by default** because `optionxform` lowercases them. A key such as `BatchSize` is normally accessed as `batchsize`.
- `DEFAULT` values are inherited by sections unless overridden. They can make a key appear available even when it is not explicitly present in that section.
- `get()`, `getint()`, `getfloat()`, and `getboolean()` return converted values or raise parsing/conversion exceptions. The `fallback=` argument returns a default when the option is absent; use it only when absence is truly acceptable.
- Standard boolean spellings include `1/0`, `yes/no`, `true/false`, and `on/off` (case-insensitive).
- Basic `%(name)s` interpolation is enabled by default. `ExtendedInterpolation` uses `${section:option}` and `${option}` references and is useful for composing paths. Interpolation cycles and missing references raise errors.
- `allow_no_value=True` allows options without values; avoid it for settings that must have values.
- `read([file1, file2])` reads multiple files in order. Later files override earlier values for duplicate options. Missing files are silently skipped by `read()`; use `read_file()` when a required file must exist and failures should be explicit.

```python
from configparser import ConfigParser

parser = ConfigParser(allow_no_value=True)
parser.read_string("""
[features]
experimental
safe_mode = true
""")
assert parser.has_option("features", "experimental")
assert parser.get("features", "experimental") is None
```

For most application settings, prefer strict requirements: explicit values, a documented interpolation policy, and no silent acceptance of missing required files.

## 4. Composition and precedence

### Deep merge policy

A shallow dictionary update replaces a whole nested mapping. A deep merge recursively merges mapping-to-mapping pairs, while scalars and lists from a higher-precedence layer replace lower-precedence values. Lists are **replaced**, not concatenated, in the implementation below. This avoids surprising duplication and is a policy choice, not a universal rule.

```python
from collections.abc import Mapping
from copy import deepcopy


def deep_merge(base: Mapping, override: Mapping) -> dict:
    """Return a new mapping; nested mappings merge, all other values replace."""
    result = deepcopy(dict(base))
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result

base = {"database": {"host": "localhost", "port": 5432}, "tags": ["raw"]}
layer = {"database": {"port": 6432}, "tags": ["daily"]}
assert deep_merge(base, layer) == {
    "database": {"host": "localhost", "port": 6432}, "tags": ["daily"]
}
```

### Environment and CLI overlays

Environment variables are strings; CLI values are strings unless `argparse` is configured to convert them (for example, `type=int`). Treat both as untrusted inputs and validate them even after conversion. Do not blindly merge strings and assume the resulting types are correct. The overlay functions should only map recognized variables/arguments, then the final configuration must be validated.

```python
import os
from collections.abc import Mapping


def apply_env(raw: dict, environ: Mapping[str, str]) -> dict:
    """Apply supported environment overrides, converting known value types."""
    result = deep_merge({}, raw)
    if "PIPELINE_BATCH_SIZE" in environ:
        try:
            result.setdefault("pipeline", {})["batch_size"] = int(environ["PIPELINE_BATCH_SIZE"])
        except (TypeError, ValueError) as exc:
            raise ValueError("PIPELINE_BATCH_SIZE must be an integer") from exc
    if "PIPELINE_LOG_LEVEL" in environ:
        result.setdefault("logging", {})["level"] = environ["PIPELINE_LOG_LEVEL"]
    return result


def apply_cli(raw: dict, *, batch_size: int | None = None,
              log_level: str | None = None) -> dict:
    result = deep_merge({}, raw)
    if batch_size is not None:
        result.setdefault("pipeline", {})["batch_size"] = batch_size
    if log_level is not None:
        result.setdefault("logging", {})["level"] = log_level
    return result
```

The `os` module is only needed if using `os.environ`; accepting a mapping makes these functions straightforward to test without mutating the process environment.

## 5. Typed settings and validation

Parsing establishes syntax. Validation establishes the application's contract. A robust loader should detect:

- Missing required keys.
- Unknown keys and likely misspellings.
- Wrong types (including booleans accidentally accepted as integers).
- Invalid values and ranges.
- Invalid configuration version.
- Contradictory settings, such as an output path equal to a protected input path when that is forbidden.

Error messages should identify the configuration path, for example `pipeline.batch_size must be a positive integer`; avoid printing secret values in error messages.

```python
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PipelineSettings:
    batch_size: int
    log_level: str
    input_path: str
    output_path: str


def require_mapping(value: Any, path: str) -> dict:
    if value is None:
        raise ValueError(f"{path} is required and must be a table/object")
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a table/object")
    return value


def reject_unknown_keys(mapping: dict, allowed: set[str], path: str) -> None:
    unknown = set(mapping) - allowed
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"Unknown key(s) at {path}: {names}")


def parse_settings(raw: dict) -> PipelineSettings:
    root = require_mapping(raw, "config")
    reject_unknown_keys(root, {"config_version", "pipeline", "logging", "paths"}, "config")

    version = root.get("config_version")
    if type(version) is not int or version != 1:
        raise ValueError("config.config_version must be integer 1")

    pipeline = require_mapping(root.get("pipeline"), "config.pipeline")
    reject_unknown_keys(pipeline, {"batch_size"}, "config.pipeline")
    batch_size = pipeline.get("batch_size")
    if type(batch_size) is not int:
        raise ValueError("config.pipeline.batch_size must be an integer")
    if not 1 <= batch_size <= 100_000:
        raise ValueError("config.pipeline.batch_size must be between 1 and 100000")

    logging = require_mapping(root.get("logging"), "config.logging")
    reject_unknown_keys(logging, {"level"}, "config.logging")
    log_level = logging.get("level")
    if not isinstance(log_level, str) or log_level.upper() not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("config.logging.level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")

    paths = require_mapping(root.get("paths"), "config.paths")
    reject_unknown_keys(paths, {"input", "output"}, "config.paths")
    input_path = paths.get("input")
    output_path = paths.get("output")
    if not isinstance(input_path, str) or not input_path.strip():
        raise ValueError("config.paths.input must be a non-empty string")
    if not isinstance(output_path, str) or not output_path.strip():
        raise ValueError("config.paths.output must be a non-empty string")
    if input_path == output_path:
        raise ValueError("config.paths.input and config.paths.output must differ")

    return PipelineSettings(batch_size, log_level.upper(), input_path, output_path)
```

For larger schemas, avoid hand-writing hundreds of checks: use a well-tested schema library where project constraints permit. Even then, enforce application-specific invariants and security policy explicitly.

A version number is useful only when its behavior is explicit. This small migration helper accepts the current version 1 shape and migrates a deliberately simple version 0 shape (`batch_size` at the root) into `pipeline.batch_size`. Unsupported future versions are rejected. Real migrations should validate the old shape before transforming it and validate the migrated result afterward.

```python
def migrate_config(raw: dict) -> dict:
    version = raw.get("config_version")
    if type(version) is not int:
        raise ValueError("config.config_version must be an integer")
    if version == 0:
        if type(raw.get("batch_size")) is not int:
            raise ValueError("version 0 config requires integer batch_size")
        if "pipeline" in raw:
            raise ValueError("version 0 config must not contain a pipeline table")
        migrated = deep_merge({}, raw)
        migrated["pipeline"] = {"batch_size": migrated.pop("batch_size")}
        migrated["config_version"] = 1
        return migrated
    if version == 1:
        return deep_merge({}, raw)
    raise ValueError("Unsupported config_version; update the application or migrate the config")
```

## 6. Complete pipeline configuration loader

This implementation combines TOML defaults, a required or optional TOML file, an injected environment mapping, and explicit CLI overrides. It deliberately contains no credentials. Environment overrides are converted to the correct primitive types before final validation. Errors are contextual but do not echo secret values.

Example `pipeline.toml`:

```toml
config_version = 1

[pipeline]
batch_size = 1000

[logging]
level = "INFO"

[paths]
input = "./data/incoming"
output = "./data/processed"
```

Implementation:

```python
from pathlib import Path
import tomllib

DEFAULTS = {
    "config_version": 1,
    "pipeline": {"batch_size": 1000},
    "logging": {"level": "INFO"},
    "paths": {"input": "./data/incoming", "output": "./data/processed"},
}


def load_pipeline_settings(path: Path | None, *, environ=None,
                           cli_batch_size: int | None = None,
                           cli_log_level: str | None = None) -> PipelineSettings:
    """Load and validate settings; `environ` is injectable for deterministic tests."""
    if environ is None:
        import os
        environ = os.environ

    raw = deep_merge({}, DEFAULTS)
    if path is not None:
        try:
            with path.open("rb") as file:
                file_config = tomllib.load(file)
        except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"Invalid TOML or UTF-8 encoding in {path}: {exc}") from exc
        except OSError as exc:
            raise ValueError(f"Cannot read configuration file {path}: {exc}") from exc
        if "config_version" not in file_config:
            raise ValueError(f"Configuration file {path} must declare config_version")
        file_config = migrate_config(file_config)
        raw = deep_merge(raw, file_config)

    # Only recognized environment variables are mapped; parse numeric text explicitly.
    env_layer = {}
    if "PIPELINE_BATCH_SIZE" in environ:
        try:
            env_layer.setdefault("pipeline", {})["batch_size"] = int(environ["PIPELINE_BATCH_SIZE"])
        except (TypeError, ValueError) as exc:
            raise ValueError("PIPELINE_BATCH_SIZE must be an integer") from exc
    if "PIPELINE_LOG_LEVEL" in environ:
        env_layer.setdefault("logging", {})["level"] = environ["PIPELINE_LOG_LEVEL"]
    raw = deep_merge(raw, env_layer)

    cli_layer = {}
    if cli_batch_size is not None:
        cli_layer.setdefault("pipeline", {})["batch_size"] = cli_batch_size
    if cli_log_level is not None:
        cli_layer.setdefault("logging", {})["level"] = cli_log_level
    raw = deep_merge(raw, cli_layer)
    return parse_settings(raw)
```

**Operational notes:**

- CLI parsing itself is normally done with `argparse`; this loader accepts already-parsed arguments to keep responsibilities separate.
- Use `pathlib.Path` and resolve paths relative to a documented base (often the config file's directory) if relative paths must be portable. This example intentionally treats paths as process-working-directory-relative.
- Do not silently ignore an explicitly requested but missing config file. `path=None` means use defaults; a supplied path must exist and parse.
- Unknown environment variables are ignored because this loader supports only two named overrides. A stricter deployment may enumerate a prefix and reject unsupported names.
- For reproducibility, record the effective non-secret settings and a config version; never dump secret values.

## 7. Configuration security and operations

### Secrets

Do not commit production passwords, API keys, access tokens, private keys, or connection strings containing credentials. Prefer configuration to contain a **reference** such as `DATABASE_PASSWORD_ENV = "APP_DATABASE_PASSWORD"` or a secret-manager identifier. Retrieve the actual value at runtime through the approved identity and access-control path. Environment variables can be exposed through diagnostics, process inspection, crash dumps, or child-process inheritance; they are not a universal secrets vault.

- Never print or log the full effective configuration by default.
- Redact sensitive fields and avoid including values in validation exceptions.
- Keep config files least-privilege readable; use OS permissions appropriate to the deployment. Permissions alone do not prove integrity.
- If config integrity is a threat, protect deployment/release channels, ownership, file permissions, signatures or trusted artifact controls as appropriate. A parser cannot establish provenance.
- A malicious config can still redirect output, disable validation, or set an unsafe path. Validate values against an allow-list and the application's security model.

### Never use `eval()`

Configuration is data, not Python source. Do not call `eval()` or `exec()` on a setting. Parse a documented format, validate the resulting data structure, and map accepted values into known types. `ast.literal_eval()` is narrower than `eval()` but is not a substitute for a configuration format/schema and can still consume resources on hostile input.

### Versioned configuration

Include an explicit `config_version`. When the schema changes, choose a deliberate migration path:

1. Parse the old version.
2. Validate its known shape.
3. Migrate to the current in-memory schema with a pure function.
4. Validate the migrated configuration again.
5. Reject unsupported future versions rather than guessing.

Do not silently reinterpret an old field with new semantics. Keep migration tests and fixtures for supported historical versions.

### TOML editing and comments

`tomllib` discards comments and formatting because it returns data structures, not a concrete syntax tree. It cannot round-trip a file while preserving comments. For programmatic editing where preserving comments, whitespace, and formatting matters, use `tomlkit` (third-party) and explicitly accept that dependency. For generated configuration, a writer may be enough; test how it serializes dates and supported types.

### Configuration locations

Use explicit CLI flags or documented paths where possible. User-level config locations may follow platform conventions such as XDG Base Directory on Unix-like systems. The third-party `platformdirs` library can help discover platform-appropriate locations; it is optional, not a standard-library requirement. Avoid scattering hidden search paths that make behavior hard to explain.

### Determinism and observability

- Log which config file was loaded, its schema version, and the effective **non-secret** values needed for diagnosis.
- If multiple files are read, log the ordered list and document which layer wins.
- Freeze validated settings (for example with `@dataclass(frozen=True)`) so later code cannot mutate them accidentally.
- Avoid implicit hot reload. If enabled, parse and validate a complete new snapshot first, then atomically swap the active settings.
- Make precedence and environment inputs injectable so tests are deterministic and do not depend on a developer's shell.

## 8. INI production reader example

For a legacy `.ini` source, define expected options and convert at the boundary. Use `read_file()` when the file is required so missing input is not silently skipped.

```python
from configparser import ConfigParser, Error as ConfigParserError
from pathlib import Path


def read_legacy_ini(path: Path) -> dict:
    parser = ConfigParser(interpolation=None)
    try:
        with path.open(encoding="utf-8") as file:
            parser.read_file(file, source=str(path))
        if not parser.has_section("pipeline"):
            raise ValueError(f"INI configuration {path} is missing [pipeline]")
        if not parser.has_option("pipeline", "batch_size"):
            raise ValueError(f"INI configuration {path} is missing pipeline.batch_size")
        if not parser.has_option("pipeline", "enabled"):
            raise ValueError(f"INI configuration {path} is missing pipeline.enabled")
        try:
            batch_size = parser.getint("pipeline", "batch_size")
            enabled = parser.getboolean("pipeline", "enabled")
        except (ValueError, ConfigParserError) as exc:
            raise ValueError(
                f"Invalid pipeline.batch_size or pipeline.enabled in {path}: {exc}"
            ) from exc
        if batch_size <= 0:
            raise ValueError(f"Invalid pipeline.batch_size in {path}: must be positive")
        return {"batch_size": batch_size, "enabled": enabled}
    except (OSError, ConfigParserError) as exc:
        raise ValueError(f"Cannot parse INI configuration {path}: {exc}") from exc
```

Set `interpolation=None` when values may contain `%` characters or interpolation is not part of the file contract. If using interpolation, escape literal percent signs according to `configparser` rules and test the exact syntax.

## 9. Format selection: keep the choice proportional

The roadmap includes a brief comparison with other configuration formats. This lesson implements TOML and INI; the alternatives below are selection guidance, not additional parser tutorials.

| Format | Good fit | Main caution |
|---|---|---|
| TOML | Typed application/tool configuration with tables and arrays | `tomllib` reads only; editing needs a writer |
| INI | Existing legacy applications and simple section/key settings | Values are strings until converted; interpolation and `DEFAULT` inheritance affect lookup |
| JSON | Machine-generated configuration and interchange | No comments; configuration still needs schema and semantic validation |
| YAML | Human-authored structured configuration when the ecosystem already uses it | Requires a third-party dependency; implicit typing varies by YAML version/loader and unsafe loaders can construct objects |
| `.env` | Simple environment-variable assignments for local development/tooling | Not a full nested configuration schema or a secrets vault |

YAML's so-called **Norway problem** illustrates implicit-typing surprises: some YAML 1.1-oriented loaders interpret unquoted `NO`/`yes`-like values as booleans, while YAML 1.2 and individual loaders differ. If YAML is required, choose a maintained parser, use its safe data-only loading API for untrusted input, pin/test the loader behavior, and quote ambiguous strings. Do not add YAML merely to avoid designing a schema for TOML.

---

## 10. Common mistakes and failure modes

| Mistake | Why it fails | Better practice |
|---|---|---|
| Opening TOML in text mode for `tomllib.load()` | Violates binary-file API | Use `open(path, "rb")` |
| Treating successful parse as validation | Required keys/types/ranges may still be wrong | Validate schema and invariants after parsing |
| Using `ConfigParser.get()` for a number | Returns text | Use `getint()` or explicitly convert and validate |
| Trusting a fallback for a required key | Hides deployment mistakes | Fail early for required settings |
| Forgetting `DEFAULT` inheritance | A key may appear present indirectly | Decide whether inherited defaults are allowed |
| Relying on undocumented merge behavior | Overrides become surprising | Specify deep-merge and list semantics |
| Ignoring unknown keys | Misspellings can silently disable settings | Reject unknown keys for controlled schemas |
| Using `eval()` | Converts config input into code execution | Use TOML/INI parsing and explicit validation |
| Logging the full config | Can disclose credentials or sensitive paths | Log a redacted effective snapshot |
| Assuming environment variables are a vault | They can leak through process/runtime diagnostics | Use managed secret retrieval where warranted |
| Editing TOML with `tomllib` | It has no writer and loses comments in the parsed structure | Use a dedicated writer or `tomlkit` |
| Silently skipping missing INI files with `read()` | Missing required file may go unnoticed | Use `read_file()` for required config |
| Applying CLI values before environment values | Breaks documented precedence | Merge in one defined order and test it |

## 11. Testing configuration code

Tests should use `tmp_path` to create isolated files, and pass explicit environment mappings or use pytest's `monkeypatch`. Never depend on a real developer's home directory, shell environment, or production secrets.

To run these tests as a separate file, save the implementation snippets (not the tests) in `config_lesson.py`. The import below makes the test module's dependencies explicit. Keep demonstration code behind `if __name__ == "__main__":` so importing the module does not read a project file or perform other unexpected I/O.

```python
# test_config_lesson.py
from configparser import ConfigParser
import pytest

from config_lesson import (
    DEFAULTS,
    PipelineSettings,
    apply_env,
    deep_merge,
    load_pipeline_settings,
    load_toml,
    migrate_config,
    parse_settings,
    read_legacy_ini,
)


def test_toml_binary_loader(tmp_path):
    path = tmp_path / "pipeline.toml"
    path.write_bytes(b'config_version = 1\n')
    assert load_toml(path)["config_version"] == 1


def test_invalid_toml_has_context(tmp_path):
    path = tmp_path / "bad.toml"
    path.write_bytes(b"[pipeline\nbatch_size = 2\n")
    with pytest.raises(ValueError, match="Invalid TOML"):
        load_pipeline_settings(path)


def test_missing_toml_file_has_context(tmp_path):
    with pytest.raises(ValueError, match="Cannot read configuration file"):
        load_pipeline_settings(tmp_path / "missing.toml", environ={})


def test_invalid_utf8_toml_has_context(tmp_path):
    path = tmp_path / "bad-encoding.toml"
    path.write_bytes(b"config_version = 1\n\xff")
    with pytest.raises(ValueError, match="UTF-8 encoding"):
        load_pipeline_settings(path, environ={})
    with pytest.raises(ValueError, match="UTF-8 encoding"):
        load_toml(path)


def test_precedence_defaults_file_env_cli(tmp_path):
    path = tmp_path / "pipeline.toml"
    path.write_bytes(b'''config_version = 1
[pipeline]
batch_size = 200
[logging]
level = "WARNING"
[paths]
input = "./in"
output = "./out"
''')
    settings = load_pipeline_settings(
        path,
        environ={"PIPELINE_BATCH_SIZE": "300", "PIPELINE_LOG_LEVEL": "ERROR"},
        cli_batch_size=400,
    )
    assert settings.batch_size == 400  # CLI wins over environment and file.
    assert settings.log_level == "ERROR"  # environment wins over file.
    assert settings.input_path == "./in"  # file overrides the default path.

    env_beats_file = load_pipeline_settings(
        path,
        environ={"PIPELINE_BATCH_SIZE": "300", "PIPELINE_LOG_LEVEL": "ERROR"},
    )
    assert env_beats_file.batch_size == 300
    assert env_beats_file.log_level == "ERROR"
    assert load_pipeline_settings(None, environ={}).batch_size == 1000


def test_invalid_env_integer_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="PIPELINE_BATCH_SIZE must be an integer"):
        load_pipeline_settings(None, environ={"PIPELINE_BATCH_SIZE": "many"})


def test_invalid_range_and_unknown_key_are_rejected():
    raw = deep_merge({}, DEFAULTS)
    raw["pipeline"]["batch_size"] = 0
    with pytest.raises(ValueError, match="between 1 and 100000"):
        parse_settings(raw)

    raw = deep_merge({}, DEFAULTS)
    raw["pipline"] = {}  # common misspelling at the root
    with pytest.raises(ValueError, match="Unknown key.*config"):
        parse_settings(raw)

    raw = deep_merge({}, DEFAULTS)
    raw["pipeline"]["batch_szie"] = 1000  # typo in a nested table
    with pytest.raises(ValueError, match="Unknown key.*config.pipeline"):
        parse_settings(raw)


def test_required_sections_and_config_version(tmp_path):
    with pytest.raises(ValueError, match="config.pipeline is required"):
        parse_settings({"config_version": 1, "logging": DEFAULTS["logging"], "paths": DEFAULTS["paths"]})

    path = tmp_path / "unversioned.toml"
    path.write_bytes(b"[pipeline]\nbatch_size = 25\n")
    with pytest.raises(ValueError, match="must declare config_version"):
        load_pipeline_settings(path, environ={})


def test_old_config_version_migrates_and_future_version_fails(tmp_path):
    path = tmp_path / "v0.toml"
    path.write_text(
        'config_version = 0\nbatch_size = 250\n[logging]\nlevel = "INFO"\n[paths]\ninput = "./in"\noutput = "./out"\n',
        encoding="utf-8",
    )
    settings = load_pipeline_settings(path, environ={})
    assert settings.batch_size == 250

    future = tmp_path / "future.toml"
    future.write_text('config_version = 2\n[pipeline]\nbatch_size = 250\n', encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported config_version"):
        load_pipeline_settings(future, environ={})


def test_bool_is_not_accepted_as_integer():
    raw = deep_merge({}, DEFAULTS)
    raw["pipeline"]["batch_size"] = True
    with pytest.raises(ValueError, match="must be an integer"):
        parse_settings(raw)


def test_validation_error_does_not_echo_sensitive_value():
    raw = deep_merge({}, DEFAULTS)
    raw["logging"]["level"] = "do-not-log-this-marker"
    with pytest.raises(ValueError) as caught:
        parse_settings(raw)
    assert "do-not-log-this-marker" not in str(caught.value)


def test_deep_merge_does_not_mutate_inputs():
    base = {"a": {"b": 1}}
    override = {"a": {"c": 2}}
    result = deep_merge(base, override)
    assert result == {"a": {"b": 1, "c": 2}}
    assert base == {"a": {"b": 1}}


def test_env_overlay_converts_integer_and_rejects_invalid_value():
    assert apply_env(DEFAULTS, {"PIPELINE_BATCH_SIZE": "25"})["pipeline"]["batch_size"] == 25
    with pytest.raises(ValueError, match="PIPELINE_BATCH_SIZE must be an integer"):
        apply_env(DEFAULTS, {"PIPELINE_BATCH_SIZE": "lots"})


def test_ini_reader_validates_typed_values(tmp_path):
    path = tmp_path / "pipeline.ini"
    path.write_text("[pipeline]\nbatch_size = 25\nenabled = yes\n", encoding="utf-8")
    assert read_legacy_ini(path) == {"batch_size": 25, "enabled": True}

    path.write_text("[pipeline]\nbatch_size = many\nenabled = yes\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid pipeline.batch_size"):
        read_legacy_ini(path)

    path.write_text("[pipeline]\nbatch_size = 25\nenabled = perhaps\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid pipeline.batch_size or pipeline.enabled"):
        read_legacy_ini(path)


def test_required_ini_file_is_not_silently_skipped(tmp_path):
    with pytest.raises(ValueError, match="Cannot parse INI configuration"):
        read_legacy_ini(tmp_path / "missing.ini")

    path = tmp_path / "missing-section.ini"
    path.write_text("[other]\nvalue = 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"is missing \[pipeline\]"):
        read_legacy_ini(path)


def test_configparser_multiple_files_and_defaults(tmp_path):
    base = tmp_path / "base.ini"
    local = tmp_path / "local.ini"
    base.write_text("[DEFAULT]\nroot = /srv\n[paths]\ninput = %(root)s/input\n[batch]\nsize = 100\n", encoding="utf-8")
    local.write_text("[batch]\nsize = 250\n", encoding="utf-8")
    parser = ConfigParser()
    assert parser.read([base, local]) == [str(base), str(local)]
    assert parser.get("paths", "input") == "/srv/input"
    assert parser.getint("batch", "size") == 250


def test_pyproject_reader_does_not_need_to_run_at_import(tmp_path):
    path = tmp_path / "pyproject.toml"
    path.write_bytes(b'[project]\nname = "demo"\n[tool.demo]\nenabled = true\n')
    # read_pyproject is an optional helper; this test is intentionally local.
    from config_lesson import read_pyproject
    parsed = read_pyproject(path)
    assert parsed["project"]["name"] == "demo"
    assert parsed["tool"]["demo"]["enabled"] is True
```

The test writes bytes directly because the loader opens TOML in binary mode.

Run with:

```bash
python -m pytest -q
```

Also test missing required files, invalid INI booleans/integers, interpolation cycles, old and future config versions, nested unknown keys, secret redaction, and any path or permission restrictions your application enforces.

## 12. Mini-project: a validated local data-pipeline runner

Build a small CLI that reads `pipeline.toml`, accepts `--batch-size` and `--log-level` through `argparse`, supports `PIPELINE_BATCH_SIZE` and `PIPELINE_LOG_LEVEL`, then creates a frozen `PipelineSettings` object before processing any records.

Acceptance criteria:

1. Defaults are sufficient when no file is provided.
2. If a file is supplied, it must exist and parse successfully.
3. Precedence is defaults → file → environment → CLI.
4. Unknown keys, unsupported config versions, invalid integer conversions, and out-of-range values fail before any side effect.
5. No credentials are stored in the example config.
6. Logs show config path, config version, and non-secret effective settings only.
7. Tests prove environment and CLI overrides and verify that invalid config prevents pipeline execution.
8. A migration function exists before a second schema version is introduced; do not create speculative migration complexity for a single version.

Suggested project layout:

```text
pipeline_app/
├── config.py       # parse, merge, validate, build dataclass
├── cli.py          # argparse and application entry point
├── pipeline.py     # processing logic accepts PipelineSettings
└── tests/
    ├── test_config.py
    └── fixtures/
        ├── valid.toml
        └── invalid.toml
```

## 13. Hands-on exercises

1. Add `pipeline.max_retries` with a range of 0–10. Validate it and document its precedence.
2. Add `paths.archive` as an optional setting. Decide and test whether a missing value means `None` or a derived path.
3. Add a `config_version = 2` migration from a renamed field. Test both migration success and unsupported future versions.
4. Read two INI files using `ConfigParser.read([base.ini, local.ini])`; prove later files override earlier values.
5. Demonstrate how a `DEFAULT` key is inherited and decide whether your schema allows that behavior.
6. Add secret-reference configuration (an environment variable name, not its secret value) and redact it from effective-config logging.
7. Test interpolation-disabled INI values containing `%`.
8. Write a test proving that invalid configuration fails before the first pipeline side effect.

## 14. Explained self-check answers

1. **Why binary mode for `tomllib.load()`?** Its API requires a binary file object and performs decoding according to TOML's UTF-8 rules. Use `loads()` if you already have a Python string.
2. **Does parsing mean configuration is safe?** No. Parsing only checks syntax and builds values. The application must still validate keys, types, ranges, paths, relationships, version, permissions, and authority to use the settings.
3. **Why deep merge?** A file may override one nested setting without replacing unrelated defaults. The merge policy must specify whether arrays replace or concatenate; this lesson replaces them.
4. **Why reject unknown keys?** It catches misspellings and obsolete settings that would otherwise be silently ignored. Some extensible schemas intentionally allow extension namespaces; document that exception.
5. **Why not use `eval()`?** It treats configuration as executable Python and creates code-execution risk. Use a data format and explicit conversions.
6. **When use `tomlkit`?** When editing TOML while preserving comments, formatting, and document structure matters. `tomllib` is a parser, not a round-trip editor.
7. **Why test precedence with injected mappings?** Tests become deterministic and do not depend on ambient shell variables or developer machines.
8. **Should all effective configuration be logged?** No. Log a redacted, non-secret representation and enough provenance to reproduce behavior without exposing credentials.

## 15. Final reference checklist

| Need | Preferred approach | Caution |
|---|---|---|
| Parse TOML text | `tomllib.loads(text)` | Python 3.11+ |
| Parse TOML file | `tomllib.load(file)` with `open("rb")` | Read-only API |
| TOML syntax/encoding errors | Catch `tomllib.TOMLDecodeError` and `UnicodeDecodeError` | Structured `TOMLDecodeError` attributes vary by Python version |
| Read INI | `ConfigParser.read_file()` for required files | `read()` silently skips missing files |
| Read typed INI values | `getint()`, `getfloat()`, `getboolean()` | Conversion is not full validation |
| Optional INI value | `fallback=` | Do not hide missing required settings |
| INI interpolation | Default/basic or `ExtendedInterpolation` | Cycles/missing references fail; `%` can be special |
| Merge configuration | Explicit defaults → file → env → CLI | Define nested merge and list policy |
| Validate settings | Required/unknown key checks, exact types, ranges, invariants | Parsing alone is insufficient |
| Typed settings | Frozen dataclass | Build only after validation |
| Store credentials | Secret manager or approved runtime secret source | Do not commit secrets or log them |
| Edit TOML preserving comments | Third-party `tomlkit` | Adds dependency; test round-trip behavior |
| Locate user config | Explicit path or platform convention | `platformdirs` is third-party |
| Reproducibility | Log config version/path and redacted effective values | Never expose secret values |
| Verify behavior | `pytest`, `tmp_path`, injected environment mappings | Test invalid and precedence cases too |

**Final rule:** Parse first, compose deliberately, validate completely, freeze the result, and only then allow the application to perform side effects.
