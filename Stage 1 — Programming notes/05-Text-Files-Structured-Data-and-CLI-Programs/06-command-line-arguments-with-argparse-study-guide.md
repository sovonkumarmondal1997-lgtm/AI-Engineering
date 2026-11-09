# 06 — Command-Line Arguments with `argparse`
## Complete Lesson Summary, Roadmap Review, Coding Exercise Solutions, and Revision

**Roadmap:** Stage 1 — Programming & Computational Thinking  
**Module:** 05 — Text Files, Structured Data, and CLI Programs  
**Lesson:** 06 — Command-Line Arguments with `argparse`

---

# Part A — Complete lesson summary

## 1. What a command-line interface (CLI) is and why it matters

A CLI lets a user control a program by typing commands and arguments instead of clicking GUI controls. CLIs remain important because they are scriptable, automatable, composable, and usable on remote machines without a graphical desktop.

Typical uses include:
- **Automation and scheduled jobs:** scripts can run unattended, including cron jobs and batch processing.
- **CI/CD:** build, test, lint, and deployment systems invoke command-line programs.
- **Data engineering:** ingestion, validation, transformation, and export jobs are commonly CLI applications.
- **AI/ML:** dataset preparation, training, evaluation, and model tooling need repeatable parameters.
- **Composition:** tools can be chained with pipes and redirected input/output.
- **Remote operations:** engineers often work on servers through SSH and a terminal.

A terminal displays text and accepts input. A **shell** (such as Bash or Zsh) interprets what is typed and starts programs. A **command** is the program name. A **command-line argument** is a token passed to that program. An **option/flag** usually starts with `-` or `--`. A **positional argument** is interpreted by its position. An **optional argument** is normally named by a flag and may be omitted.

Examples:

```bash
python app.py
python app.py data.csv
python app.py data.csv --verbose
python app.py --input data.csv --output result.json
```

## 2. Shell, Python, `sys.argv`, and `argparse` are separate stages

The order is:

```text
What user types → shell parses → OS starts Python with tokens
→ sys.argv contains strings → argparse interprets tokens
→ application validation → business logic → output/status
```

The shell handles quoting, wildcard expansion, environment variables, pipes, redirection, and command substitution **before Python starts**. For example:

```bash
python app.py "hello world"
```

The shell passes one argument `"hello world"` (without quote characters). Python and argparse never see the original quotes. Likewise, `*.csv` may be expanded by the shell into several filenames before Python starts.

`sys.argv` is the raw list of strings Python receives:

```python
import sys
print(sys.argv)
```

For `python app.py one two`, it resembles `["app.py", "one", "two"]`. `sys.argv[0]` is the program name/path; `sys.argv[1:]` are the user's arguments. Every element is a string, so `"42"` is not integer `42` until converted. No extra arguments means `sys.argv[1:] == []`.

Manual parsing may work for one tiny script, but grows fragile when you add optional values, defaults, unknown-argument errors, type conversion, help, choices, and exit codes. A manual example in the lesson also demonstrates a double-increment bug in its index. `argparse` replaces this custom parsing state machine with a declarative parser.

## 3. First `argparse` program

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("name")
args = parser.parse_args()
print(f"Hello, {args.name}")
```

- `import argparse` loads Python's standard-library parser.
- `ArgumentParser()` creates the parser.
- `add_argument("name")` declares a required positional argument.
- `parse_args()` reads `sys.argv[1:]` by default, validates and converts values, then returns a `Namespace`.
- `args.name` reads the value from that namespace.

Argparse automatically creates `-h`/`--help` and useful usage/error output. Omitting the required `name` causes a usage error and exit status 2.

## 4. `ArgumentParser` constructor

```python
parser = argparse.ArgumentParser(
    prog="csv-tool",
    description="Inspect and summarize CSV files.",
    epilog="Example: csv-tool data.csv --format json",
)
```

| Parameter | Purpose |
|---|---|
| `prog` | Program name shown in help/usage; explicit setting stabilizes output. |
| `usage` | Replaces the generated usage line; rarely needed. |
| `description` | Explanation above the arguments in help. |
| `epilog` | Text after the arguments, useful for command examples. |
| `parents` | Copies argument definitions from parent parsers. |
| `formatter_class` | Controls help wrapping and whitespace. |
| `prefix_chars` | Characters introducing options; default `-`. |
| `add_help` | Automatically add `-h`/`--help`; default `True`. |
| `allow_abbrev` | Accept unambiguous long-option prefixes; default `True`. |
| `exit_on_error` | With `False`, most parse errors raise `ArgumentError`; Python 3.9+. |
| `suggest_on_error` | Suggest close matches for choices/subcommands; added in 3.14, default becomes `True` in 3.15. |
| `color` | Controls colored help/errors; added in 3.14. |
| `argument_default` | Global fallback for arguments without their own default. |
| `conflict_handler` | Option collision behavior: normally `"error"`, alternatively `"resolve"`. |
| `fromfile_prefix_chars` | Enables `@filename` argument expansion; default disabled. |

Parser objects are mutable: `add_argument()` changes the parser and returns an `Action` object. Usually construct the parser once inside `build_parser()`.

## 5. Positional arguments, optional arguments, and flags

**Positional:** no leading dash; order matters and it is required by default.

```python
parser.add_argument("input_file")
parser.add_argument("output_file")
```

**Optional:** starts with `-` or `--`; order among options generally does not matter.

```python
parser.add_argument("-i", "--input")
```

Both `-i data.csv` and `--input data.csv` populate `args.input`. Long options are self-documenting; add short aliases only when they are useful. For one or two central required values, positional arguments are natural. For multiple settings, named options are clearer.

**Boolean flags** use presence/absence as the value:

```python
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--no-color", action="store_false", dest="use_color")
```

`store_true` defaults to `False`; `store_false` defaults to `True`. Python 3.9+ also provides:

```python
parser.add_argument("--color", action=argparse.BooleanOptionalAction, default=True)
```

This creates both `--color` and `--no-color`.

## 6. `action=` and all standard actions

| Action | Meaning |
|---|---|
| `store` | Store the value; default action. |
| `store_const` | Store the fixed `const=` value when the option appears. |
| `store_true` | Store `True` when present, otherwise `False`. |
| `store_false` | Store `False` when present, otherwise `True`. |
| `append` | Append each occurrence's value to a list. |
| `append_const` | Append a fixed `const=` value for each occurrence. |
| `count` | Count occurrences, e.g. `-vvv` gives 3. |
| `extend` | Extend a list with values from each occurrence; Python 3.8+. |
| `help` | Print help and exit; used by built-in help. |
| `version` | Print version text and exit. |

Examples:

```python
parser.add_argument("--mode", action="store_const",
                    const="fast", default="normal")
parser.add_argument("--tag", action="append")
parser.add_argument("-v", "--verbose", action="count", default=0)
parser.add_argument("--items", action="extend", nargs="+")
```

Caveats: `append` defaults to `None` unless you set a default; `count` should normally use `default=0`. Use `if args.tag:` if the option may never be supplied. A custom `Action` is a last resort.

## 7. `type=`, custom validators, and `choices=`

`type=` is a callable that converts each captured string before storing it:

```python
parser.add_argument("--count", type=int)
parser.add_argument("--threshold", type=float)
parser.add_argument("--input", type=Path)
```

Invalid conversion becomes a clean argparse error. A custom function can perform a small, single-value validation:

```python
def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number
```

Keep type functions limited to conversion and self-contained validation. A rule depending on multiple arguments belongs after parsing.

`choices=` restricts the converted value to a known set:

```python
parser.add_argument("--format", choices=["json", "csv", "yaml"])
parser.add_argument("--count", type=int, choices=range(1, 11))
```

Argparse applies `type=` before `choices=`. Choices are normally case-sensitive.

## 8. `default=`, `required=`, `nargs`, and `const=`

`default=` is used when an optional argument is absent:

```python
parser.add_argument("--format", default="json")
```

If a default is a string and `type=` exists, argparse converts that default too (`type=int, default="5"` becomes integer 5). A non-string default is used as supplied. `default=argparse.SUPPRESS` omits the attribute entirely when absent, useful when merging configuration sources.

`required=True` can make an optional flag mandatory, but should be reserved for values without a safe default. Plain positional arguments are required unless their `nargs` makes them optional.

`nargs` controls the number of values:

| Value | Meaning | Result |
|---|---|---|
| omitted | exactly one | single value |
| `"?"` | zero or one | value or default/const |
| `"*"` | zero or more | list, possibly empty |
| `"+"` | one or more | non-empty list |
| integer `N` | exactly N | list of N values |

A variable-length positional can be ambiguous beside another variable-length positional; avoid that design.

`const=` is used when an option is present without an explicit value, or with `store_const`:

```python
parser.add_argument("--log-level", nargs="?",
                    const="INFO", default="WARNING")
```

Absent → `"WARNING"`; bare `--log-level` → `"INFO"`; `--log-level DEBUG` → `"DEBUG"`.

## 9. `metavar=`, `dest=`, and `help=`

- `metavar` changes the placeholder shown in help, not parsing. `--input FILE` is more useful than `--input INPUT`.
- `dest` sets the `Namespace` attribute. `--input-file` automatically becomes `args.input_file`; explicit `dest="input"` changes it to `args.input`.
- `help` describes what the value is and what the flag does. Mention defaults once, either manually or with `ArgumentDefaultsHelpFormatter`.

Help output is generated from the parser declaration. `description` appears above arguments; `epilog` appears below. The default formatter wraps whitespace. Formatter classes:
- `HelpFormatter`: normal wrapping.
- `RawDescriptionHelpFormatter`: preserves description/epilog line breaks.
- `RawTextHelpFormatter`: preserves most whitespace in all help text.
- `ArgumentDefaultsHelpFormatter`: appends defaults.
- `MetavarTypeHelpFormatter`: displays type names as metavars.

Only one formatter class can be passed. Combine behaviors with a small multiple-inheritance subclass if needed.

## 10. Parsing methods and `Namespace`

`parse_args()` returns a `Namespace`; on invalid input it prints usage/error to stderr and exits with status 2 (`SystemExit`). Help/version normally exit with status 0. You can pass explicit argument lists:

```python
args = parser.parse_args(["--verbose", "data.csv"])
```

This makes parsing easy to test without invoking a real process.

`parse_known_args()` returns `(namespace, unknown_tokens)` instead of rejecting unknown tokens. Use it for wrappers/forwarding or plugin parsing; ordinary CLIs should generally reject misspelled options. Known-option abbreviation may still be consumed.

`parse_intermixed_args()` (Python 3.7+) allows positional and optional arguments to interleave in certain cases. It does not support subparsers or mutually exclusive groups mixing positional and optional arguments. Use only when the CLI genuinely needs it. `parse_known_intermixed_args()` is the companion.

`Namespace` stores parsed values as attributes. `vars(args)` creates a dictionary. Namespace equality works for tests. Avoid passing a raw Namespace deep into business logic.

## 11. Groups and parent parsers

A **mutually exclusive group** allows at most one option; `required=True` means exactly one must be supplied:

```python
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--json", action="store_true")
group.add_argument("--csv", action="store_true")
```

An **argument group** only organizes help output; it does not validate or enforce anything.

A **parent parser** shares arguments across parsers:

```python
common = argparse.ArgumentParser(add_help=False)
common.add_argument("--verbose", action="store_true")
parser = argparse.ArgumentParser(parents=[common])
```

`add_help=False` is important because otherwise parent and child both define `-h`/`--help`, causing a conflict. Parent parsers copy argument definitions; option collisions normally raise errors.

## 12. Subcommands and dispatch

Subparsers create multi-command tools such as `tool ingest`, `tool validate`, and `tool export`:

```python
subparsers = parser.add_subparsers(dest="command", required=True)
ingest = subparsers.add_parser("ingest", aliases=["in"])
ingest.add_argument("source")
ingest.set_defaults(func=handle_ingest)
```

`dest` records the chosen command. `required=True` requires a subcommand (Python 3.7+). `aliases` provide alternate command names; `args.command` reflects the alias actually typed. `set_defaults(func=...)` attaches a handler to that subparser, allowing dispatch without a growing `if/elif` chain.

A maintainable flow is:

```text
main(argv) → build_parser() → parse_args(argv)
→ cross-argument validation → handler dispatch
→ domain/service logic → return status
```

The parser builder should only construct the parser. `main(argv: Sequence[str] | None = None) -> int` is testable because callers can supply explicit tokens. The script boundary alone turns the returned status into process exit:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

## 13. Validation and error/exit/help methods

Argparse handles syntax (types, choices, required values). Application code handles semantic rules:
- Is a path actually an existing file?
- Is a numeric range valid?
- Does one option become required only when another is selected?
- Is an output path allowed to overwrite an existing file?

Use `type=Path` for conversion only; it does not resolve or check existence. A custom type function can check a single path, while cross-argument rules belong after parsing:

```python
args = parser.parse_args(argv)
if args.format == "csv" and args.output is None:
    parser.error("--output is required when --format=csv")
```

`parser.error(message)` prints usage and an error to stderr, then exits with status 2. `parser.exit(status, message)` is a lower-level stop mechanism; avoid scattering exits through business logic. Prefer returning a status from `main()`.

`print_help()` prints full help without exiting. `print_usage()` prints only the usage line. `action="version"` provides `--version` and exits 0.

## 14. Advanced parser configuration

- `prefix_chars`: changes option prefix characters; usually leave `-`.
- `allow_abbrev=True`: accepts unambiguous prefixes such as `--verb`; can break scripts when a new option makes an old prefix ambiguous. Production CLIs should generally use `allow_abbrev=False`.
- `fromfile_prefix_chars="@"`: lets users pass many tokens through an argument file. By default, each line becomes one token.
- `convert_arg_line_to_args()`: override this method to split each argument-file line differently (e.g. whitespace-separated tokens).
- `argument_default`: global fallback default; per-argument default wins. `argparse.SUPPRESS` omits unset attributes.
- `conflict_handler="error"`: default; duplicate option strings fail at parser construction. `"resolve"` lets a later declaration take over a collision, but is a niche escape hatch.
- `exit_on_error=False`: Python 3.9+; most parse errors raise `ArgumentError` rather than exiting. Help/version still exit intentionally.
- `suggest_on_error`: Python 3.14+; newer Python defaults to suggestions.
- `color`: Python 3.14+ help/error color control.
- `prog` behavior for `python -m module` was improved in Python 3.14.

## 15. Custom `Action` and `FileType`

A custom `argparse.Action` subclasses `argparse.Action` and implements `__call__(parser, namespace, values, option_string=None)`. It can inspect which alias was used and store a transformed value. It is rarely needed: prefer a `type=` function for one-value conversion or post-parse validation for rules needing multiple arguments.

`argparse.FileType` opens a file during parsing and returns an open file object. `"-"` maps to stdin/stdout. It is deprecated since Python 3.14. It can simplify small scripts, but makes resource ownership and closing less clear. Prefer parsing `Path`, then opening it in a `with` block where it is actually used.

## 16. CLI architecture, configuration, and tests

A CLI should have a thin interface layer and separate domain logic:

```text
cli.py: build_parser(), main(argv)
config.py: typed Config dataclass and build_config()
commands/: handler functions
domain/: business logic, no argparse dependency
services/: I/O and external systems
```

Convert the parsed and validated Namespace to a typed configuration object, often a frozen dataclass. Domain logic then receives stable, typed inputs and can be called from tests, notebooks, scheduled jobs, or another interface.

Configuration often follows precedence: CLI arguments override environment variables, which override config files, which override hardcoded defaults. Argparse only parses the CLI layer; your application merges other sources.

Testing patterns:
- `parser.parse_args([...])` tests parsing without a subprocess.
- `pytest.raises(SystemExit)` tests invalid input and exit codes.
- Test defaults, types, choices, flags, mutually exclusive combinations, subcommands, validators, cross-argument rules, help/version exits.
- Test `main([...])` and capture output with `capsys`.
- `tmp_path` creates isolated test files.

## 17. UX, shell behavior, security, and performance

Good CLIs are predictable, discoverable, explicit, safe by default, scriptable, composable, stable, and backward-compatible. Provide useful help/version, sensible defaults, actionable errors, distinct exit codes, machine-readable output where useful, and diagnostics on stderr.

Shell quoting matters:

```bash
python app.py "hello world"  # one token
python app.py hello world    # two tokens
```

Double quotes permit environment-variable expansion in Bash; single quotes suppress it. Wildcards may expand before Python starts. Pipes/redirection are shell features, not argparse features.

Treat every CLI value as untrusted:
- Validate paths and prevent path traversal when writes must stay under a root.
- Never send untrusted input to `subprocess.run(..., shell=True)` or construct shell command strings; pass an argument list with no shell.
- Do not pass passwords/API keys as plain CLI arguments; process listings may expose them. Prefer a secrets manager or a suitably protected configuration mechanism.
- Validate at point of use, not just at parse time.

Argparse is almost never the performance bottleneck. Parser construction and parsing are cheap; parsing cost scales with token count. Avoid rebuilding the parser repeatedly in a loop, but optimize the actual data work first.

## 18. End-to-end examples in the lesson

### Beginner: CSV Summary CLI

The lesson's example:
- Builds a parser with positional `input_file: Path`, optional `--output: Path`, and `--verbose`.
- `summarize(path, verbose)` opens CSV with `newline=""` and UTF-8, uses `csv.reader`, obtains the header with `next(reader, [])`, counts data rows with `sum(1 for _ in reader)`, and returns a formatted string.
- `main(argv)` validates `input_file.is_file()`, writes summary to output or prints it, and returns 0.
- The `if __name__ == "__main__"` block raises `SystemExit(main())`.

### Intermediate: Data Converter CLI

The example uses required subcommand `convert`, a custom `existing_file()` type validator, required `--input`, `--output`, and `--format {json,csv}`, and `set_defaults(func=handle_convert)`. It reads CSV with `DictReader`, materializes rows, retains field names, writes JSON or `DictWriter` CSV, and reports rows written. A header-only CSV is valid with zero rows; a completely empty CSV has no header and is rejected as an application content error (exit 1), not a CLI syntax error (exit 2).

### Advanced: Data Pipeline CLI architecture sketch

A shared parent parser defines `--verbose` and `--dry-run`. Four subcommands (`ingest`, `validate`, `transform`, `export`) use aliases, Path validators, mutually exclusive `--rule`/`--script`, format choices, required output, and `set_defaults(func=...)`. Shared parent arguments are attached at top level and subcommand level so they work before or after the command. The lesson intentionally leaves the handlers for the mini-project.

## 19. API reference coverage

The lesson's reference covers:
- `ArgumentParser`, `add_argument`, `parse_args`, `parse_known_args`, `parse_intermixed_args`, `error`, `exit`, `print_help`, `print_usage`.
- Argument groups, mutually exclusive groups, parent parsers.
- `add_subparsers`, `add_parser`, aliases, `set_defaults`.
- All constructor settings and `add_argument()` parameters.
- All standard actions and `BooleanOptionalAction`.
- `Namespace`, `Action`, `ArgumentError`, `ArgumentTypeError`, `FileType`, and `SUPPRESS`.

## 20. Common mistakes and systematic debugging

Common mistakes: manual `sys.argv` parsing, forgetting values are strings, using `type=bool`, assuming optional arguments are required, confusing positional and optional declarations, too many required flags, poor help, no sensible defaults, ambiguous short options, relying on abbreviations, mixing parsing with business logic, passing Namespace deep into domain logic, overloading argparse with business validation, unnecessary custom Actions, not testing explicit argv, ignoring shell quoting, missing cross-argument validation, and a monolithic `main()`.

The `type=bool` trap:

```python
parser.add_argument("--enabled", type=bool)
```

`bool("false")` is `True` because every non-empty string is truthy. Use `store_true`/`store_false` for presence flags, `BooleanOptionalAction` for `--flag`/`--no-flag`, or a real `parse_bool()` converter for explicit textual booleans.

Debugging sequence:
1. Record the exact command.
2. Check shell quoting.
3. Print `repr(sys.argv)`.
4. Inspect each parser declaration.
5. Print the Namespace immediately after parsing.
6. Check defaults and types.
7. Check choices and case.
8. Verify the intended subparser owns the argument.
9. Inspect cross-argument validation.
10. Reproduce with explicit `argv` to remove shell behavior from the test.

---

# Part B — Roadmap and current learning-level review

## 1. Stage 1 project tree

The roadmap defines Stage 1 — **Programming & Computational Thinking** — as 24 modules, 212 numbered lessons, and 282 files. The module structure is:

1. Computational Thinking and Program Design.
2. Python Core Language and Data Types.
3. Control Flow, Functions, Scope, and Errors.
4. Problem-Solving, Collections, and Algorithmic Habits.
5. Text Files, Structured Data, and CLI Programs.
6. Modules, Packages, Dependencies, and Code Quality.
7. Testing and Systematic Debugging.
8. Object-Oriented Design, Data Modelling, and Functional Style.
9. Advanced Production-Oriented Python Foundations.
10. Production Habits for Python Programs.
11. Advanced Python Data Model and Object Design.
12. Metaprogramming and Dynamic Python.
13. Standard Library Toolkit.
14. Bytes, Binary Data, and Advanced Text Processing.
15. Modern Python Language Features.
16. Advanced Testing and Test Architecture.
17. Profiling, Memory, and Runtime Performance.
18. Packaging, Distribution, and Publishing.
19. CPython Internals and Runtime Behaviour.
20. Design Patterns and Library API Design.
21. Data Visualization and Notebook Workflows.
22. Secure Python Coding.
23. Code Reading, Refactoring, and Code Review.
24. Functions and OOP Gap Lessons.

The relevant Module 05 lesson sequence is:
1. Reading and Writing Text Files — completed.
2. `pathlib` and Portable Paths — completed.
3. CSV Files — completed.
4. JSON and Serialization — completed.
5. Encodings and Newlines — completed.
6. **Command-Line Arguments with `argparse` — current lesson.**
7. Standard Streams and Exit Codes.
8. Logging versus Print.
9. Environment Configuration and Input Validation.
10. Module README and practice questions.

The four Stage 1 projects are:
- **Personal Expense Ledger CLI** — a command-line expense application.
- **Log Investigation and Reliability CLI** — operational log analysis and reliability reporting.
- **Data Quality and Transformation Pipeline** — `orders.csv`, a `dqpipe` package (`cli.py`, `config.py`, `pipeline.py`, `rules.py`), tests, configuration, and a data contract.
- **Rule-Based Risk Review Engine** — `transactions.csv`, `rules.toml`, a `riskreview` package (`cli.py`, `engine.py`, `io.py`, `models.py`, `rules.py`), tests, and golden decision data.

## 2. Current level and scope discipline

Your recorded level is **beginner progressing toward intermediate**. You have completed/covered Python fundamentals, collections, functions, argument design, scope, pure functions and side effects, exceptions and validation, algorithms, text-file I/O, `pathlib`, CSV, JSON, and encoding/newline handling.

This is an appropriate point to learn `argparse`: the lesson builds directly on functions, `Path`, CSV/JSON, exceptions, return values, and basic pytest patterns. The exercises below stay within the current module and concepts already taught. They use the standard library (`argparse`, `pathlib`, `dataclasses`, `csv`, `json`, `sys`, `collections.abc`) and the previously introduced pytest patterns. Advanced package layout is explained as a design exercise, not treated as already mastered.

Why this lesson matters to the projects:
- The Expense Ledger needs reliable arguments such as input file, date range, and output.
- The Log Investigation CLI needs file/directory inputs, filters, verbosity, and clean errors.
- The Data Quality Pipeline needs subcommands such as `inspect`, `validate`, and `transform`, shared configuration, and typed paths.
- The Risk Review Engine needs explicit rule/config inputs and safe output behavior.

The later Module 05 lessons will deepen standard streams/exit codes, logging, and environment configuration. Do not jump ahead to those implementations yet.

---

# Part C — All 27 coding exercises solved

The code is intentionally compact so every exercise remains within the requested word limit. The explanations describe each meaningful line and the command/edge case to test.

## Level 1 — Foundation

### 1. Inspect `sys.argv`

```python
import sys
print(sys.argv)
```

Run `python app.py one two`. Python prints a list similar to `['app.py', 'one', 'two']`. Run with no extra tokens to see only the script name. All entries are strings; `sys.argv[1:]` excludes the script name.

### 2. Required positional `name`

```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("name")
args = parser.parse_args(["Sovon"])
print(args.name)
```

The declaration has no dash, so it is positional and required. The explicit argv list makes the example testable. Expected value: `"Sovon"`. Edge case: `parse_args([])` raises `SystemExit` because the name is missing.

### 3. Optional greeting with default

```python
parser.add_argument("--greeting", default="Hello")
args = parser.parse_args(["Sovon"])
print(args.greeting)
```

The option is optional; when omitted, the default is `"Hello"`. Try `["Sovon", "--greeting", "Welcome"]` to override it. Expected Namespace includes `greeting='Hello'` in the first case.

### 4. `--shout` flag

```python
parser.add_argument("--shout", action="store_true")
greeting = args.greeting.upper() if args.shout else args.greeting
print(f"{greeting}, {args.name}")
```

Presence sets `shout=True`; absence gives `False`. With `--shout`, `"Hello"` becomes `"HELLO"`. Without it, greeting casing is preserved.

### 5. Verify a default

```python
parser.add_argument("--format", default="json")
args = parser.parse_args([])
assert args.format == "json"
```

The omitted option receives the default. Try `["--format", "csv"]` to confirm explicit input wins.

### 6. Integer conversion

```python
parser.add_argument("--count", type=int)
print(parser.parse_args(["--count", "5"]).count)
```

Argparse converts `"5"` to integer `5`. Try `["--count", "five"]`; argparse prints a clean invalid-integer error and raises `SystemExit`.

## Level 2 — Practical

### 7. Restrict choices

```python
parser.add_argument("--size", choices=["small", "medium", "large"])
print(parser.parse_args(["--size", "medium"]).size)
```

The valid command succeeds. `["--size", "huge"]` fails and lists valid choices. Matching is case-sensitive.

### 8. Collect one or more values

```python
parser.add_argument("--files", nargs="+")
args = parser.parse_args(["--files", "a.csv", "b.csv"])
print(args.files)
```

`nargs="+"` returns a non-empty list. `["--files"]` fails because at least one value is required; omitting the option entirely gives `None` unless a default is set.

### 9. Percentage validator

```python
def percentage(value: str) -> float:
    try:
        number = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be numeric") from error
    if not 0 <= number <= 100:
        raise argparse.ArgumentTypeError("must be between 0 and 100")
    return number

parser.add_argument("--rate", type=percentage)
```

Convert first, then check inclusive boundaries. The returned value is a float. Test `0`, `100`, `50.5`, `-1`, `101`, and `"abc"`.

### 10. Convert and validate a Path

```python
from pathlib import Path
parser.add_argument("--input", type=Path, required=True)
args = parser.parse_args(["--input", "data.csv"])
if not args.input.is_file():
    parser.error(f"not an existing file: {args.input}")
```

`type=Path` converts the string; it does not check existence. The post-parse check validates the actual file. Test a missing path and a directory path.

### 11. Mutually exclusive flags

```python
group = parser.add_mutually_exclusive_group()
group.add_argument("--verbose", action="store_true")
group.add_argument("--quiet", action="store_true")
```

Neither is allowed; either one is allowed; both together fail. Add `required=True` to the group only if exactly one must be supplied.

### 12. Improve help with `metavar`

```python
parser.add_argument("--input", metavar="CSV_FILE",
                    help="Path to the CSV file to read")
```

`metavar` changes the placeholder displayed in usage/help, not the Namespace attribute or parsing. Run `--help` and check it displays `--input CSV_FILE`.

### 13. Version option

```python
parser.add_argument("--version", action="version",
                    version="%(prog)s 1.0.0")
```

Running `--version` prints the program name and version, then exits with status 0. It works without satisfying other required arguments.

## Level 3 — Engineering

### 14. Convert to two subcommands

```python
sub = parser.add_subparsers(dest="command", required=True)
ingest = sub.add_parser("ingest")
ingest.add_argument("source")
report = sub.add_parser("report")
report.add_argument("--output", type=Path)
```

Each command has its own arguments. Run `ingest data.csv` or `report --output result.txt`. Running with no command fails because `required=True`.

### 15. Dispatch with `set_defaults`

```python
def handle_ingest(args):
    print(f"Ingesting {args.source}")
    return 0

ingest.set_defaults(func=handle_ingest)
args = parser.parse_args(["ingest", "data.csv"])
status = args.func(args)
```

The subparser attaches its handler. After parsing, `args.func` points to the chosen function; this avoids a growing `if/elif` dispatch chain. Test the report handler similarly.

### 16. Share flags with a parent parser

```python
common = argparse.ArgumentParser(add_help=False)
common.add_argument("--verbose", action="store_true")
ingest = sub.add_parser("ingest", parents=[common])
report = sub.add_parser("report", parents=[common])
```

The parent defines shared arguments once. `add_help=False` avoids duplicate `-h`/`--help` options. Test `ingest --verbose ...` and `report --verbose ...`.

### 17. Organize help into groups

```python
inputs = parser.add_argument_group("Input options")
inputs.add_argument("--input", type=Path)
outputs = parser.add_argument_group("Output options")
outputs.add_argument("--output", type=Path)
```

The groups create headings in `--help`; they do not change validation or requiredness. Confirm parsing still works as before.

### 18. Cross-argument validation

```python
args = parser.parse_args(["--format", "csv"])
if args.format == "csv" and args.output is None:
    parser.error("--output is required for CSV")
```

The rule depends on two values, so it runs after parsing. In pytest, assert the invalid case raises `SystemExit` with code 2. Test JSON without output as a valid case if your rule permits it.

### 19. `main(argv)` and a test

```python
from collections.abc import Sequence

def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)

def test_main():
    assert main(["--format", "json"]) == 0
```

The optional argv parameter lets tests pass tokens directly instead of changing global `sys.argv`. The function returns a status instead of exiting. Keep `SystemExit(main())` only at the script entry point.

### 20. Test five scenarios for one subcommand

```python
def test_validate_parser():
    parser = build_parser()
    assert parser.parse_args(["validate", "a.csv"]).command == "validate"
    assert parser.parse_args(["validate", "b.csv", "--verbose"]).verbose
    with pytest.raises(SystemExit):
        parser.parse_args([])
    with pytest.raises(SystemExit):
        parser.parse_args(["validate"])
    with pytest.raises(SystemExit):
        parser.parse_args(["unknown"])
```

These tests cover valid parsing, a flag, missing command, missing positional, and unknown command. Add success/failure tests for the handler's actual file-validation behavior as the project grows.

## Level 4 — Advanced

### 21. Forward unknown arguments

```python
parser.add_argument("--verbose", action="store_true")
args, unknown = parser.parse_known_args(
    ["--verbose", "--engine", "fast", "data.csv"]
)
print(args.verbose, unknown)
```

Argparse consumes `--verbose` and returns the remaining tokens unchanged: `["--engine", "fast", "data.csv"]`. This is useful for wrappers. Do not use it in ordinary CLIs just to hide misspelled options.

### 22. Intermixed arguments

```python
parser.add_argument("--verbose", action="store_true")
parser.add_argument("files", nargs="*")
args = parser.parse_intermixed_args(
    ["a.csv", "--verbose", "b.csv"]
)
print(args.files, args.verbose)
```

The result groups both filenames and sets verbose true. This demonstrates positional/optional interleaving. It is not supported with subparsers; use it only when genuinely required.

### 23. Expand an `@file`

```python
parser = argparse.ArgumentParser(fromfile_prefix_chars="@")
parser.add_argument("--verbose", action="store_true")
parser.add_argument("files", nargs="*")
args = parser.parse_args(["@args.txt"])
```

If `args.txt` has `--verbose`, `a.csv`, and `b.csv` on separate lines, those become tokens. Default behavior treats each line as one token. Test a missing argument file and an empty file.

### 24. Custom Action records alias

```python
class RecordAlias(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values.upper())
        setattr(namespace, "used_alias", option_string)

parser.add_argument("-v", "--verbose-tag", action=RecordAlias)
```

`option_string` identifies whether `-v` or `--verbose-tag` was used. A `type=` function cannot do this because it receives the value, not the option name. Test both aliases and verify normalized value plus alias.

### 25. Customize argument-file tokenization

```python
class SplitLinesParser(argparse.ArgumentParser):
    def convert_arg_line_to_args(self, arg_line: str) -> list[str]:
        return arg_line.split()

parser = SplitLinesParser(fromfile_prefix_chars="@")
parser.add_argument("files", nargs="*")
```

The override splits each line into whitespace-separated tokens. Without it, one line is one token. Test a line containing three filenames and note that this simple split does not implement shell quoting.

### 26. Package-style layout

```text
src/app/
    __init__.py
    cli.py
    config.py
    commands/
        __init__.py
        inspect.py
        transform.py
```

`cli.py` builds the parser and `main(argv)`. `config.py` defines typed configuration. `commands/` contains thin handlers. Business logic belongs in domain/service modules, not in argparse declarations. Test parser, config construction, and handlers separately.

### 27. Typed Config and conversion test

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Config:
    input_path: Path
    output_path: Path | None
    verbose: bool

def build_config(args):
    return Config(args.input, args.output, args.verbose)

def test_config():
    args = argparse.Namespace(
        input=Path("in.csv"), output=None, verbose=False
    )
    assert build_config(args) == Config(Path("in.csv"), None, False)
```

The dataclass declares the shape and types expected by the application. `build_config()` translates argparse's Namespace at the boundary. Test at least three combinations: no optional output, explicit output, and verbose enabled.

---

# Part D — All 12 debugging exercises

1. **Missing required input:** `--input` defaults to `None`, so later `.read_text()` fails. Declare `required=True` and `type=Path`, or check for `None` before use.
2. **`type=bool`:** `"false"` is non-empty, so `bool("false")` is `True`. Use `store_true`, `store_false`, `BooleanOptionalAction`, or a real parser function.
3. **Wrong `nargs`:** `"?"` accepts zero or one value; use `"+"` for one or more.
4. **String default with `type=int`:** the example is not broken; argparse converts string default `"5"` to integer `5`. Prefer `default=5` for clarity.
5. **Case-sensitive choices:** `"Prod"` does not equal `"prod"`. Normalize with a custom `type=` function before choices or require documented casing.
6. **Mutually exclusive group default:** a truthy default does not satisfy required group presence and can produce both booleans true. Do not set a truthy default inside a required mutually exclusive group.
7. **Missing dispatch function:** `args.func` is absent because `set_defaults(func=...)` was not attached to the subparser. Add it to that parser.
8. **Wrong `dest`:** explicit `dest="input"` means the value is `args.input`, not `args.input_file`. Make the code use the actual destination.
9. **Validator hides error:** returning 0 on any exception turns invalid input into plausible data. Raise `ArgumentTypeError`; catch only the expected conversion exception.
10. **Cross-argument check too early:** a `type=` function cannot see `--force`. Parse all arguments first, then check output existence against the force flag.
11. **Shell quoting:** `John Smith` becomes two tokens. Use `--name "John Smith"`; this is shell tokenization, not argparse malfunction.
12. **Validation never called:** defining `validate_args()` is not enough. Trace `main()` and ensure it invokes validation after parsing and before dispatch.

---

# Part E — Interview questions and answers

## 37 interview questions

1. **What is a CLI and why important?** A programmable text interface that supports automation, scripting, CI/CD, batch jobs, remote operations, and tool composition.
2. **What is `sys.argv`?** The list of process arguments; all elements are strings.
3. **Why argparse?** It provides declarative parsing, type conversion, defaults, choices, help, and consistent errors.
4. **Positional vs optional?** Positionals are identified by order; optionals by named flags.
5. **Flag vs value option?** A flag's presence is its boolean value; a value option consumes a following value.
6. **What is Namespace?** The object holding parsed values as attributes.
7. **What does parse_args do?** Parses tokens and returns Namespace; invalid input normally exits 2.
8. **What is type=?** A callable converting each raw string before storing it.
9. **Why is type=bool wrong?** `bool("false")` is true; use boolean actions or a real string parser.
10. **What is nargs?** Controls number of values: `?`, `*`, `+`, or exact integer count.
11. **What is action?** How argparse stores/processes values; examples: store, append, count, store_true.
12. **What is choices?** Restricts converted values to an allowed set; checked after type conversion.
13. **What is required?** Forces an optional argument to appear; positionals are required by default.
14. **What is default?** Value used when omitted; a string default is converted by `type=`.
15. **What is metavar?** Help placeholder for the expected value.
16. **What is dest?** Namespace attribute name, normally derived from argument name.
17. **Mutually exclusive group?** At most one option; required group means exactly one.
18. **Subparsers?** Separate command-specific parsers under one CLI.
19. **set_defaults()?** Attaches metadata, commonly a handler function, to a subparser.
20. **parse_args vs parse_known_args?** The latter returns unknown tokens rather than rejecting them.
21. **parse_intermixed_args?** Allows some positional/optional interleaving; does not support subparsers.
22. **Argument group vs mutually exclusive?** Argument group organizes help only; mutually exclusive group validates combinations.
23. **Parent parser?** Reusable argument definitions; use `add_help=False` to avoid duplicate help flags.
24. **FileType?** Opens files during parsing; less explicit resource ownership than parsing Path and opening with `with`.
25. **When custom Action?** Rarely, when behavior needs parser state such as which alias was used.
26. **How validate path existence?** Convert with `type=Path`, then check `.is_file()`/`.is_dir()` or use a narrow validator.
27. **How validate cross-argument rules?** After parsing, inspect all values and call `parser.error()` for invalid CLI combinations.
28. **How test without subprocess?** Pass explicit lists to `parse_args()` or `main(argv)`.
29. **Why main(argv)?** Makes the program directly callable and testable without changing global `sys.argv`.
30. **Production multi-command design?** Thin CLI, shared parser arguments, subparsers, typed Config, handlers, and argparse-independent domain logic.
31. **How handle secrets?** Use a secrets manager or protected configuration; command-line args may be visible in process listings.
32. **Shell vs argparse?** Shell tokenizes and expands before process start; argparse interprets the resulting string tokens.
33. **Why might `--count=5` fail while `--count 5` works?** Both are normally supported; inspect custom type/Action, shell behavior, and exact parser definition.
34. **Why did `--verb` stop working after adding `--verify`?** Prefix abbreviation became ambiguous; set `allow_abbrev=False`.
35. **Output required only for CSV?** Validate after parsing and call `parser.error()` when format is CSV and output is absent.
36. **Why not pass password via CLI?** Process arguments may be visible to other users or monitoring tools.
37. **How replace a large dispatch chain?** Attach each handler with `set_defaults(func=...)` and invoke `args.func(args)`.

---

# Part F — All 20 knowledge-check answers

1. The shell handles quoting, globbing, variable expansion, pipes, and redirection before Python starts; argparse interprets the resulting tokens.
2. The OS process interface supplies arguments as strings; Python performs later type conversion.
3. `action="append"` produces `["a", "b", "c"]`.
4. `-vvv` with `action="count", default=0` produces `3`.
5. `type=bool` maps any non-empty string, including `"false"`, to `True`; use boolean actions or a real parser.
6. Parent and child both define `-h`/`--help`, causing a conflicting option-string error; set `add_help=False` on the parent.
7. `nargs=2, type=float` yields `[1.0, 2.0]`.
8. The optional positional gets its default `10`.
9. `add_mutually_exclusive_group(required=True)`.
10. Use a parent parser with `add_help=False` and pass it through `parents=` to each subparser.
11. `append` defaults to `None`; use `default=[]` or handle the absent case.
12. Verify `type=Path` is on the exact argument declaration being parsed; otherwise the value remains a string.
13. `choices=range(0, 11)` is simplest for a small closed integer range; use a custom type for more complex validation.
14. Post-parse validation: requiredness depends on another option's value.
15. Namespace has dynamic attributes and no stable typed contract; it couples domain code to argparse.
16. `main(argv)` can be tested with explicit lists and returns a status without mutating process-global arguments.
17. Command-line values can be visible in process listings such as `/proc/<pid>/cmdline`.
18. Argparse never runs shell commands; injection risk occurs later if program code builds shell strings or uses `shell=True`.
19. Parsing code belongs in the CLI layer; domain/services should receive validated configuration and know nothing about argparse.
20. Good scriptability includes distinct exit codes, no unavoidable prompts, stable machine-readable stdout, and diagnostics on stderr.

---

# Part G — Four mini-project specifications

## 1. File Inspector CLI

Build `file-inspect PATH` with positional path, `--recursive`, `--json`, and `--verbose`. Use `pathlib` and `json`. Separate `inspect_path()` (returns data) and `render()` (formats output) from parsing. Handle missing paths, broken symlinks, unreadable directories, and empty directories. Test files, directories, recursion, valid JSON, and clean errors. Extension: repeatable `--exclude PATTERN` using `action="append"`.

## 2. CSV Processing CLI

Build `csv-tool` with `inspect`, `validate`, and `transform` subcommands. Share `--verbose` via a parent parser. Inspect row/column counts, validate rows against a schema, and transform CSV to JSON/CSV. Use one handler per subcommand and `set_defaults()`. Test empty/header-only files, inconsistent rows, quoted commas, success and failure for each command, and cross-argument validation. Extension: shared `--dry-run`.

## 3. Data Quality CLI

Build `dq check`, `dq report`, and `dq fix` for a directory of CSV files. Share `--verbose` and `--config`. `fix` must require exactly one of `--in-place` or `--output-dir`. Add a custom quality-threshold validator (0–1), typed Config, and `main(argv)`. Test zero CSV files, boundary values 0 and 1, read-only files, all mutually exclusive combinations, validators, and each subcommand. Extension: `--fail-fast`.

## 4. Production-Style Data Pipeline CLI

Implement `pipeline ingest`, `validate`, `transform`, and `export`. Share `--verbose` and `--dry-run`; provide aliases; validate input/output paths and avoid accidental overwrite unless `--force`; use a typed `PipelineConfig`, custom business validator, `set_defaults()` dispatch, clean errors, and full pytest coverage. Test help at every level, missing mutually exclusive transform choice, unsuitable CSV structure, and mixing subcommand flags. Extension: `pipeline run` calls existing handlers in sequence.

---

# Part H — Production and mastery checklist

- [ ] Know the terminal/shell/process/`sys.argv`/argparse boundary.
- [ ] Distinguish positional, optional, and boolean flag arguments.
- [ ] Use all relevant `add_argument()` parameters deliberately.
- [ ] Understand every standard action and `BooleanOptionalAction`.
- [ ] Avoid `type=bool`.
- [ ] Use `type=` for conversion and narrow validation; use `choices=` for small closed sets.
- [ ] Understand `default`, `required`, `nargs`, and `const`.
- [ ] Write useful `help`, `description`, `epilog`, and `metavar` text.
- [ ] Understand Namespace and `vars()`.
- [ ] Choose among `parse_args`, `parse_known_args`, and `parse_intermixed_args`.
- [ ] Use mutually exclusive groups for actual validation and argument groups for help organization.
- [ ] Reuse shared options with parent parsers that disable help.
- [ ] Build subcommands and dispatch with `set_defaults(func=...)`.
- [ ] Validate paths and cross-argument dependencies before work begins.
- [ ] Understand error/help/version/exit methods and exit status behavior.
- [ ] Know advanced settings and their Python-version constraints.
- [ ] Prefer Path plus context-managed opening over deprecated FileType.
- [ ] Convert Namespace to a typed configuration object.
- [ ] Keep domain logic independent of argparse.
- [ ] Test explicit argv lists and `main(argv)`.
- [ ] Treat CLI values as untrusted; protect paths and secrets.
- [ ] Make help, output, and exit codes stable and scriptable.

**Next roadmap lesson:** `07-standard-streams-and-exit-codes.md`. Do not advance until you can build a small parser, validate inputs, test explicit argv, and explain the CLI-to-domain boundary.
