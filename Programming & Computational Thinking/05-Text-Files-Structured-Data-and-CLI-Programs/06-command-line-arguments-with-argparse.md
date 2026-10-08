# Command-Line Arguments with argparse

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what a command-line interface is, and why command-line
  programs remain essential even in a world of GUIs and web apps.
- Explain precisely how the shell, the Python process, `sys.argv`, and
  `argparse` divide responsibility for turning what a user types into
  data your program can use.
- Read and reason about `sys.argv` directly, and explain why manual
  parsing of it does not scale.
- Build CLI programs using `argparse.ArgumentParser`, from the smallest
  possible script to a multi-command production tool.
- Distinguish positional arguments from optional arguments, and choose
  correctly between them.
- Use every major `add_argument()` parameter: `action`, `nargs`,
  `const`, `default`, `type`, `choices`, `required`, `help`, `metavar`,
  `dest`.
- Use every standard-library action (`store`, `store_const`,
  `store_true`, `store_false`, `append`, `append_const`, `count`,
  `extend`, `help`, `version`), and know when a custom `Action` is
  actually warranted.
- Write custom type-conversion and validation functions using
  `argparse.ArgumentTypeError`, and know where syntactic validation
  ends and business validation begins.
- Design help output deliberately: descriptions, epilogs, formatter
  classes, and metavars that make a tool self-documenting.
- Use `parse_args()`, `parse_known_args()`, and `parse_intermixed_args()`
  correctly, and explain the tradeoffs and limitations of each.
- Work with `Namespace` objects, including converting them to
  dictionaries and to typed configuration objects.
- Build mutually exclusive groups and argument groups, and explain the
  difference between validation and documentation grouping.
- Reuse arguments across parsers with `parents=`.
- Build multi-command CLIs with `add_subparsers()`, including aliases,
  required subcommands, and `set_defaults()`-based dispatch.
- Validate paths and cross-argument dependencies after parsing, and
  raise clean errors with `parser.error()`.
- Explain `parser.exit()`, `print_help()`, and `print_usage()`, and
  when application code should use each.
- Implement `--version` correctly with `action="version"`.
- Explain `allow_abbrev`, `fromfile_prefix_chars`,
  `convert_arg_line_to_args()`, `argument_default`, `conflict_handler`,
  and `exit_on_error`, including their Python-version support.
- Write a minimal, well-scoped custom `argparse.Action` when the
  standard actions genuinely cannot express what you need.
- Use `argparse.FileType` and explain why parsing a `Path` and opening
  it yourself is usually the better production choice.
- Separate argument parsing from business logic using a
  `main(argv) -> int` architecture, and test CLI programs with pytest
  by calling `parse_args()` and `main()` with explicit argument lists.
- Recognize and avoid the classic argparse mistakes, especially the
  `type=bool` trap.
- Reason about CLI security: untrusted input, path validation, and why
  secrets do not belong in command-line arguments.
- Design a production-grade, multi-command CLI application from
  scratch, with a thin CLI layer, a validated configuration object, and
  testable domain logic underneath it.

## 2. Why CLI Programs Matter

A command-line program is a program controlled entirely through text:
you type a command, the program reads it, does something, and reports
back — usually as text, usually without any window, button, or mouse
click involved. It is easy, coming from a GUI-first world, to think of
this as a primitive fallback. In practice it is the opposite: the
command line is the interface every other layer of computing is built
on top of.

CLI programs matter because of what they make possible:

- **Automation.** A GUI requires a human to click things. A CLI program
  can be invoked by another program — a script, a scheduler, another
  CLI tool — with no human present at all.
- **Scripting and composition.** Small CLI tools can be chained
  together (`grep ... | sort | uniq -c`), each doing one job well. A
  GUI application cannot be piped into another GUI application.
- **CI/CD pipelines.** Every build server, test runner, linter, and
  deployment tool your future work will depend on is invoked as a CLI
  command, because pipelines are themselves just sequences of shell
  commands.
- **Cron jobs and scheduled tasks.** A scheduled job runs unattended,
  at 3 a.m., with no one available to click "OK" on a dialog. It must
  be drivable from a command line.
- **Data pipelines and batch processing.** Data engineering tools —
  ingestion jobs, transformation scripts, validators — are almost
  always CLI programs, often running on remote servers with no display
  at all.
- **ML and AI workflows.** Training scripts, dataset preparation
  tools, evaluation harnesses, and increasingly, agent and LLM tooling
  itself, are driven by command-line arguments so they can be
  parameterized, scripted, and run unattended or in parallel.
- **Developer tools.** `git`, `python`, `pip`, `docker`, `ruff`, `pytest`
  — the tools you use every day to build software are themselves CLI
  programs, and most of them use exactly the kind of design this
  chapter teaches.
- **Server and operational tooling.** Debugging a remote server almost
  always means SSHing in and running commands — there usually is no
  GUI available at all.

GUIs and web applications did not make the CLI obsolete; they solved a
different problem (interactive use by a human, in real time). The CLI
solves the problem of **programmable, scriptable, unattended,
composable control** — a problem that never goes away, and that every
tool you will build in this course, from data processors to agent
tooling, will eventually need to solve.

## 3. CLI Fundamentals

Before touching any code, fix the vocabulary. Every term below will be
used precisely for the rest of this chapter.

- **Terminal** — the application that displays text and accepts
  keyboard input. In WSL2 this might be Windows Terminal, VS Code's
  integrated terminal, or a standalone terminal emulator.
- **Shell** — the program that *reads what you type in the terminal,
  interprets it, and starts other programs*. On Ubuntu/WSL2 this is
  almost always `bash` (or `zsh`). The shell is not Python — it has its
  own syntax, its own quoting rules, its own variables.
- **Command** — the name of the program the shell should run, e.g.
  `python`, `git`, `ls`.
- **Command-line argument** — any piece of text after the command name
  that the shell passes along to the program being started. In
  `python app.py data.csv --verbose`, the arguments are `app.py`,
  `data.csv`, and `--verbose`.
- **Command-line option** (or **flag**) — an argument that begins with
  a prefix character (conventionally `-` or `--`) and names a specific
  setting, e.g. `--verbose`, `-v`, `--output result.json`.
- **Positional argument** — an argument identified purely by its
  *position* in the command, not by a name. In `cp source.txt dest.txt`,
  both `source.txt` and `dest.txt` are positional.
- **Optional argument** — an argument the user may or may not supply,
  usually (but not always — see §16) introduced by an option string
  like `--format`.

A few concrete commands, annotated:

```
python app.py
```
No arguments beyond the program name. The program must work with
nothing supplied, or explain that it can't.

```
python app.py data.csv
```
One positional argument: `data.csv`. Position tells argparse what it
means (§9).

```
python app.py data.csv --verbose
```
One positional argument (`data.csv`) plus one flag (`--verbose`) — a
boolean option that is either present or absent (§11).

```
python app.py --input data.csv --output result.json
```
Two optional arguments, each carrying a value, identified by name
rather than position. Order between `--input` and `--output` does not
matter here — that is one of the main advantages of named options over
positional ones.

## 4. Shell vs Python vs argparse

This is the single most important mental model in this chapter, and
skipping it is the single most common reason beginners get confused
about what argparse can and cannot do.

```
USER TYPES A COMMAND
        ↓
     SHELL           (bash) — parses quoting, expands globs/variables,
        ↓                     handles pipes/redirects, splits into tokens
   COMMAND-LINE TOKENS
        ↓
  PYTHON PROCESS      (a new OS process starts; Python receives the
        ↓              already-split token list from the OS)
     sys.argv          (raw list of strings — Python's only view
        ↓               into what was typed)
     argparse           (interprets the token list according to the
        ↓                parser you defined)
  PARSED Namespace
        ↓
     VALIDATION        (your code — argparse can't know your business rules)
        ↓
  APPLICATION LOGIC
        ↓
   OUTPUT / ERROR
```

The **shell** and **argparse** are two entirely separate parsers, with
entirely separate responsibilities, and they run at entirely separate
times.

- The **shell** parses *before your Python program even starts*. It
  decides how to split what you typed into a list of tokens. It handles
  quoting (`"hello world"` becomes one token, not two), wildcard
  expansion (`*.csv` becomes a list of matching filenames), variable
  expansion (`$HOME` becomes your home directory), pipes (`|`),
  redirection (`>`, `<`), and command substitution (`` `cmd` `` or
  `$(cmd)`). By the time your program starts, all of that has already
  happened — irreversibly. Your Python code never sees the quotes, the
  `*`, or the `$HOME` — it only ever sees the *result*.
- **argparse** starts working only *after* the OS hands your process a
  finished list of string tokens (`sys.argv`, §5). It has no concept of
  quoting, globbing, or pipes at all — those concepts have already been
  resolved by the shell before argparse ever runs. argparse's job is
  narrower and different: interpreting *which token means what* —
  which ones are flags, which are their values, which are positional,
  what type each should become, and what to do if something required
  is missing.

Concretely:

```bash
python app.py "hello world"
```

The shell sees the quotes and produces exactly one token, `hello world`
(no quotes, one string, one space). Python's `sys.argv` will contain
`["app.py", "hello world"]` — two entries, not three. argparse never
"sees" a quote character; the quoting problem was already solved before
argparse existed for this run.

```bash
python app.py *.csv
```

The shell expands `*.csv` into every matching filename in the current
directory *before* Python starts. If there are three matching files,
`sys.argv` will contain three separate tokens. If there are none, most
shells pass the literal string `*.csv` through unchanged — a common
source of confusion (§59).

The rule to internalize: **argparse never parses shell syntax.**
Quoting, globbing, variable expansion, pipes, and redirection are the
shell's job and are finished long before your program starts running.
argparse's entire job begins with a plain Python list of strings.

## 5. `sys.argv`

`sys.argv` is the raw, unprocessed list of command-line tokens Python's
interpreter received at startup. The underlying process-creation
mechanism differs by platform, but Python exposes the command-line
arguments to the program as strings through `sys.argv`. It is the one and only
channel through which command-line input reaches your program, and
argparse is built entirely on top of it.

```python
import sys

print(sys.argv)
```

Running:

```bash
python app.py one two three
```

prints:

```
['app.py', 'one', 'two', 'three']
```

Key facts about `sys.argv`:

- **`sys.argv[0]`** is the name (or path) the program was invoked with
  — `app.py` here. It is *not* one of "your" arguments; treat it as
  metadata about the invocation, not input.
- **`sys.argv[1:]`** is the actual argument list your program needs to
  interpret. This is exactly the slice argparse consumes by default.
- **Order is preserved** exactly as typed (after shell processing).
  argparse relies on this to figure out which value follows which flag.
- **Every element is a `str`.** There is no automatic type conversion.
  `python app.py 42` gives you `sys.argv[1] == "42"`, a string, not the
  integer `42`. Every numeric or boolean interpretation you want has to
  be done deliberately (this is exactly what `type=` in argparse
  automates — §13).
- If no arguments are given beyond the program name, `sys.argv[1:]` is
  an empty list, `[]` — not `None`, not an error.

Why not just parse `sys.argv` by hand? Handling a couple of positional
arguments manually is tempting:

```python
import sys

if len(sys.argv) < 2:
    print("Usage: app.py <name>")
    sys.exit(1)

name = sys.argv[1]
print(f"Hello, {name}")
```

This works — for exactly this one case. §6 shows why it stops working
the moment your CLI needs more than the absolute simplest shape.

## 6. Why argparse Exists

Manual `sys.argv` parsing degrades fast as requirements grow. Consider
a slightly more realistic program that wants a required filename, an
optional `--verbose` flag, and an optional `--output` value:

```python
import sys

args = sys.argv[1:]
verbose = False
output = None
filename = None

i = 0
while i < len(args):
    if args[i] == "--verbose":
        verbose = True
        i += 1
    elif args[i] == "--output":
        if i + 1 >= len(args):
            print("Error: --output requires a value", file=sys.stderr)
            sys.exit(2)
        output = args[i + 1]
        i += 2
    elif not args[i].startswith("-"):
        filename = args[i]
        i += 1
    else:
        print(f"Error: unknown argument {args[i]!r}", file=sys.stderr)
        sys.exit(2)
    i += 1  # bug: double-increments after the elif branches above

if filename is None:
    print("Error: filename is required", file=sys.stderr)
    sys.exit(2)
```

Even before running it, notice everything this snippet has to get
right on its own, with no help from the language or standard library:
missing-value detection for `--output`, a required-positional check,
an "unknown argument" error path, sensible exit codes, and — as flagged
in the comment — it is easy to introduce subtle bugs like double-
incrementing the index. And this handles only three arguments. It has
no `--help`, no usage message, no type conversion, no support for
short options (`-v`), no way to say "one of these three choices only,"
and no way to combine flags. Every one of those would be more
hand-rolled state-machine logic, and every one is a place for bugs to
hide.

`argparse` is the standard-library answer: a declarative way to
*describe* what arguments your program accepts, after which argparse
handles the parsing, validation, type conversion, defaults, error
messages, and `--help`/`--usage` generation for you — consistently,
and without you writing a hand-rolled parser for every script.

## 7. First argparse Program

The smallest useful argparse program:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("name")

args = parser.parse_args()
print(f"Hello, {args.name}")
```

```bash
python app.py Alice
# Hello, Alice
```

Line by line:

- `import argparse` — the standard-library module; no installation
  needed.
- `parser = argparse.ArgumentParser()` — creates a parser object. This
  is the thing you configure by calling `add_argument()` on it,
  repeatedly, once per argument you want to accept.
- `parser.add_argument("name")` — declares one **positional** argument
  named `name` (no leading `-`, so argparse treats it as positional —
  see §9). It is required by default.
- `args = parser.parse_args()` — reads `sys.argv[1:]` (implicitly),
  matches it against everything you declared, converts types, applies
  defaults, and returns a `Namespace` object (§29) holding the result.
  If something is missing or invalid, this call prints an error and
  usage message and terminates the process — you never reach the next
  line.
- `args.name` — attribute access on the `Namespace`. Because the
  argument was declared as `name`, argparse exposes it as `args.name`.

Already, for free, you get:

```bash
python app.py
# usage: app.py [-h] name
# app.py: error: the following arguments are required: name
```

```bash
python app.py --help
# usage: app.py [-h] name
#
# positional arguments:
#   name
#
# options:
#   -h, --help  show this help message and exit
```

None of that — the usage line, the error message, the `--help` flag —
was written by hand. This is the value argparse provides even before
any of its more advanced features are used.

## 8. `ArgumentParser`

`argparse.ArgumentParser` is the object every argparse program is built
around. Its constructor accepts several keyword parameters that shape
the whole parser's behavior and help output.

```python
parser = argparse.ArgumentParser(
    prog="csv-tool",
    description="Inspect and summarize CSV files.",
    epilog="Example: csv-tool data.csv --format json",
)
```

| Parameter | What it does | Notes |
|---|---|---|
| `prog` | Name shown in usage/help (historically `sys.argv[0]`'s basename; since Python 3.14, a program started with `python -m module` shows `python -m module`) | Set explicitly for consistent help output regardless of how the script is invoked |
| `usage` | Overrides the auto-generated usage line entirely | Rarely needed; auto-generation is usually better and stays in sync as you add arguments |
| `description` | Text shown above the argument list in `--help` | Explains what the tool *does* |
| `epilog` | Text shown *below* the argument list in `--help` | Good place for usage examples (§24) |
| `parents` | A list of other `ArgumentParser` objects whose arguments are copied in | Used to share common arguments across parsers (§33) |
| `formatter_class` | Controls how help text is wrapped/rendered | See §25 |
| `prefix_chars` | Characters that introduce optional arguments | Default `"-"`; changing it is unusual (§49) |
| `add_help` | Whether to auto-add `-h`/`--help` | Default `True`; set `False` only if you want to define help yourself |
| `allow_abbrev` | Whether unambiguous long-option prefixes are accepted | Default `True`; see §49 for why production CLIs often disable it |
| `exit_on_error` | Whether parse errors call `sys.exit()` or raise `ArgumentError` | Added in Python 3.9; default `True`; see §55 |
| `suggest_on_error` | Whether to suggest close matches for mistyped choices/subcommands | Added in Python 3.14; default `True` starting with Python 3.15 |
| `color` | Whether help/error output is colorized | Added in Python 3.14; output can vary by terminal/environment |
| `argument_default` | A global default applied to every argument that doesn't set its own | Default `None`; see §53 |
| `conflict_handler` | How to handle option-string collisions | Default `"error"`; `"resolve"` is the alternative (§54) |
| `fromfile_prefix_chars` | Enables `@file` style argument-file expansion | Default `None` (disabled); see §51 |

Each parameter is explored in depth in its own section below (cross-
referenced in the table); this section exists so you know, up front,
that all of them live on the constructor and can be combined freely.

A caveat worth stating early: **`ArgumentParser` objects are mutable
and stateful.** Calling `add_argument()` mutates the parser in place
and returns an `Action` object (mostly ignored in simple scripts, but
occasionally useful — §38 uses the subparser equivalent). Build the
parser once, typically inside a `build_parser()` function (§39), rather
than constructing it inline in `main()` — this makes it independently
testable and reusable.

## 9. `add_argument()`

`add_argument()` is how you declare a single argument — positional or
optional — that the parser should recognize. Its general shape:

```python
parser.add_argument(
    "name_or_flags",          # one name (positional) or one/more flags (optional)
    action=...,                # what to do when this argument is seen (§12)
    nargs=...,                 # how many values to consume (§18)
    const=...,                 # a fixed value for certain actions/nargs (§19)
    default=...,                # value used when argument is absent (§15)
    type=...,                   # conversion function applied to the raw string (§13)
    choices=...,                 # restrict to a fixed set of values (§17)
    required=...,                # for optionals only — force presence (§16)
    help=...,                    # help text shown in --help (§22)
    metavar=...,                  # name shown for the value in help/usage (§20)
    dest=...,                     # Namespace attribute name (§21)
)
```

Two shapes distinguish positional from optional:

```python
parser.add_argument("filename", help="Input file")
# positional: no leading '-', identified by position

parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
# optional: leading '--', identified by name
```

Every `add_argument()` call ultimately does three things: it tells
argparse **how to recognize** this argument on the command line (by
position, or by a flag string), **how to convert and validate** the
raw string(s) it captures, and **what attribute name** to store the
result under in the returned `Namespace`. The sections that follow
work through each of those three responsibilities in turn.

## 10. Positional Arguments

A positional argument is declared by giving `add_argument()` a name
with no leading `-`:

```python
parser.add_argument("input_file")
```

Key properties:

- **Required by default.** Unless `nargs="?"` or `nargs="*"` is used
  (§18), omitting a positional argument is a parse error.
- **Order matters.** Positional arguments are matched to values in the
  order they were declared, matching the order values appear on the
  command line.
- **Multiple positionals** are declared with multiple `add_argument()`
  calls:

```python
parser.add_argument("input_file")
parser.add_argument("output_file")
```

```bash
python app.py data.csv result.json
# args.input_file == "data.csv"
# args.output_file == "result.json"
```

- **Type conversion and choices apply the same way** as for optionals:

```python
parser.add_argument("count", type=int, choices=range(1, 11))
```

Use positional arguments for values that are *always* required and
whose meaning is obvious from position and count — typically one or
two central inputs (a filename, a URL, a name). Once a program needs
three or more required values, or the meaning of "the second argument"
stops being obvious, prefer named optional arguments instead (§11) —
positional arguments do not self-document at the call site the way
`--input` and `--output` do.

## 11. Optional Arguments

An optional argument is declared with one or more strings that begin
with a prefix character (`-` by default):

```python
parser.add_argument("--input")       # long option
parser.add_argument("-i", "--input") # short + long alias, same destination
```

```bash
python app.py --input data.csv
python app.py -i data.csv
```

Both forms populate `args.input`. Conventions worth following:

- **Long options** (`--input`) are self-documenting and should exist
  for every optional argument.
- **Short options** (`-i`) are single-dash, single-character
  conveniences for frequently-typed flags; not every option needs one.
- When both are given, argparse infers the destination attribute from
  the **first long option** (or the short one, if no long option is
  given) — see §21 for the exact rule and how to override it.
- Optional arguments can appear **in any order** relative to each
  other and (with caveats — §28) relative to positional arguments.
  This is their main usability advantage over positional arguments
  once a program has more than a couple of required inputs.

By default, an optional argument is — despite the name "optional
argument" referring to the *argparse category* — not required to be
present (§16 covers making one mandatory anyway, and explains why that
should be the exception, not the rule).

## 12. Flags

A **flag** is a boolean optional argument: its mere presence or
absence *is* the value, with no accompanying data.

```python
parser.add_argument("--verbose", action="store_true")
```

```bash
python app.py --verbose   # args.verbose == True
python app.py             # args.verbose == False (default)
```

`store_true` sets the destination to `True` if the flag is present,
and implicitly defaults it to `False` if declared with no other
`default=`. The mirror image is `store_false`:

```python
parser.add_argument("--no-color", action="store_false", dest="use_color")
```

```bash
python app.py --no-color   # args.use_color == False
python app.py              # args.use_color == True (default)
```

Use `store_false` when the *feature is on by default* and the flag is
how a user turns it *off* — name the flag for what it disables
(`--no-color`, not `--color` bound to `store_false`, which would be
deeply confusing to read). Since Python 3.9, `argparse.BooleanOptionalAction`
offers a third option that some tools prefer: a single argument
declaration that automatically creates both a positive and a `--no-`
prefixed negative form:

```python
parser.add_argument("--color", action=argparse.BooleanOptionalAction, default=True)
```

```bash
python app.py --color     # args.color == True
python app.py --no-color  # args.color == False
```

This gives explicit on/off control from one declaration, at the cost
of only being available on Python 3.9+.

## 13. Common Actions

`action=` tells argparse *what to do* with the value(s) it captures for
an argument. `"store"` is the (implicit) default; the rest change that
behavior for specific purposes.

| Action | Behavior | Typical use |
|---|---|---|
| `"store"` | Store the (possibly type-converted) value as-is | The default for any argument that takes a value |
| `"store_const"` | Store a fixed `const=` value when the flag is present | A flag that sets one specific value, not a boolean |
| `"store_true"` | Shortcut for `store_const` with `const=True`, `default=False` | Boolean on-flags (§12) |
| `"store_false"` | Shortcut for `store_const` with `const=False`, `default=True` | Boolean off-flags (§12) |
| `"append"` | Append each occurrence's value to a list | An argument repeatable on the command line |
| `"append_const"` | Append `const=` to a list each time the flag appears | Building a list from repeated fixed-value flags |
| `"count"` | Count how many times the flag appears | `-vvv` for increasing verbosity |
| `"extend"` | Like `append`, but extends the list with each value (works naturally with `nargs`) | Collecting values across multiple repeated multi-value flags — added in Python 3.8 |
| `"help"` | Print help and exit (this is what `-h`/`--help` uses internally) | You will rarely add this yourself |
| `"version"` | Print a version string and exit | `--version` (§47) |

Examples, each showing the resulting `Namespace`:

```python
parser.add_argument("--mode", action="store_const", const="fast", dest="mode", default="normal")
# --mode present  -> Namespace(mode="fast")
# --mode absent   -> Namespace(mode="normal")

parser.add_argument("--tag", action="append")
# --tag a --tag b -> Namespace(tag=["a", "b"])
# (absent)        -> Namespace(tag=None)

parser.add_argument("--verbose", "-v", action="count", default=0)
# (absent)  -> Namespace(verbose=0)
# -v        -> Namespace(verbose=1)
# -vvv      -> Namespace(verbose=3)

parser.add_argument("--tag", action="extend", nargs="+", type=str)
# --tag a b --tag c -> Namespace(tag=["a", "b", "c"])
```

Caveats:

- `append`'s default, if you don't set `default=[]` yourself, is
  `None` — not an empty list. Checking `if args.tag:` handles both
  cases safely; assuming `args.tag` is always a list will crash on the
  "never supplied" path.
- `count`'s default should be set explicitly (`default=0`); otherwise
  it is `None`, and `None` cannot be compared numerically the way a
  verbosity level usually needs to be.
- Custom actions (writing your own `Action` subclass) exist for cases
  none of the above cover — but they are rarely needed. See §56 before
  reaching for one.

## 14. `type=`

`type=` is a callable applied to each raw (string) value argparse
captures, before storing it in the `Namespace`. It handles both
**conversion** and, incidentally, basic **validation** (a conversion
that fails is treated as an invalid argument).

```python
parser.add_argument("--count", type=int)
```

```bash
python app.py --count 5      # args.count == 5   (an int, not "5")
python app.py --count five   # error: argument --count: invalid int value: 'five'
```

Mechanically, argparse calls `type(raw_string)` and catches
`ValueError` and `TypeError`, turning either into a clean
"invalid X value" error with usage output — you do not need to
`try`/`except` this yourself.

Common built-in types used this way: `int`, `float`, and
`pathlib.Path` (§41):

```python
parser.add_argument("--threshold", type=float)
parser.add_argument("--input", type=Path)
```

`type=` runs **once per raw string value**, before `choices` is
checked (§17) and before the value is stored — so by the time your
code sees `args.count`, it is already the right Python type, not a
string you have to convert yourself.

## 15. Custom Type Functions

When a built-in type isn't enough — when a value needs conversion
*and* a validation rule beyond "did it parse" — write your own
function and pass it as `type=`.

```python
import argparse

def positive_int(value: str) -> int:
    number = int(value)  # ValueError propagates as an argparse error automatically
    if number <= 0:
        raise argparse.ArgumentTypeError(f"must be a positive integer, got {value!r}")
    return number

parser.add_argument("--workers", type=positive_int, default=1)
```

```bash
python app.py --workers 4    # args.workers == 4
python app.py --workers 0    # error: argument --workers: must be a positive integer, got '0'
python app.py --workers abc  # error: argument --workers: invalid positive_int value: 'abc'
```

Why this matters:

- `argparse.ArgumentTypeError` is the *deliberate* way to signal "this
  parsed, but it's invalid" — argparse catches it the same way it
  catches a bare `ValueError`, and produces a clean, usage-attached
  error message instead of a Python traceback.
- Writing the validation as a **plain function of one string argument**
  keeps it trivially reusable and independently testable — you can
  call `positive_int("4")` directly in a unit test, with no
  `ArgumentParser` involved at all.
- Keep custom type functions narrow: syntactic conversion and simple,
  self-contained validation only ("is this a positive integer",
  "does this path exist"). Business rules that depend on *other*
  arguments (§42) belong after parsing, not inside a `type=` function,
  because `type=` functions only ever see one raw string in isolation.

## 16. `default=`

`default=` is the value stored in the `Namespace` when an optional
argument is not supplied on the command line.

```python
parser.add_argument("--format", default="json")
```

```bash
python app.py               # args.format == "json"
python app.py --format csv  # args.format == "csv"
```

Notes:

- Positional arguments with `nargs` other than the default (§18) can
  also have defaults; a plain required positional (`nargs` unset)
  cannot meaningfully have one, since it must always be supplied.
- If the default value is a **string**, argparse applies the `type=`
  converter to that default (`type=int, default="5"` gives the int `5`
  when the flag is omitted). If the default is **not a string**, it is
  used as supplied, without conversion. Setting defaults to the
  *already-converted* Python value (`default=5`) remains the clearest
  habit.
- `default=argparse.SUPPRESS` is a special sentinel: if the argument is
  not supplied, no attribute is set on the `Namespace` at all (instead
  of being set to `None` or some other default). This is useful when
  you want to distinguish "user didn't mention this" from "user
  explicitly set this to some falsy value," typically so a later
  configuration-merging step (§58) can tell the two apart.
- Think of `default=` as the last, lowest-priority layer in a broader
  configuration precedence — command line, then environment variables,
  then a config file, then hardcoded defaults (§58) — rather than the
  only place defaults can come from.

## 17. `required=`

By default, **positional** arguments are required and **optional**
arguments are not. `required=True` overrides that for an optional
argument, forcing the user to supply it despite its flag-like syntax:

```python
parser.add_argument("--environment", required=True)
```

```bash
python app.py                       # error: the following arguments are required: --environment
python app.py --environment prod    # args.environment == "prod"
```

When is this appropriate? When a value has no sensible default and the
program genuinely cannot proceed without it — a target
environment name, a destination that must be explicit for safety.

When it is *not* appropriate: turning every argument required "just in
case." A CLI with five `required=True` flags is barely more ergonomic
than five positional arguments, and loses the self-documenting
flag-name advantage optional arguments are supposed to provide. Prefer
sensible defaults over required flags wherever a reasonable default
exists; reserve `required=True` for values that are genuinely
mandatory and have no safe default.

Note the asymmetry with positional arguments: a positional argument is
inherently required *unless* you loosen it with `nargs="?"` (optional,
single value) or `nargs="*"` (optional, zero-or-more values) — see §18.

## 18. `choices=`

`choices=` restricts a value to a fixed, known set, validated after
`type=` conversion:

```python
parser.add_argument("--format", choices=["json", "csv", "yaml"])
```

```bash
python app.py --format json   # OK
python app.py --format xml    # error: argument --format: invalid choice: 'xml'
#                                (choose from 'json', 'csv', 'yaml')
```

- `choices` can be any container supporting `in` — a list, tuple,
  `range` (useful with `type=int`, e.g. `choices=range(1, 11)`), or
  even an enum's value list.
- The generated error message and the `--help` output both list the
  valid choices automatically — one more thing you don't hand-write.
- `choices` is checked *after* `type=` runs, so compare against the
  *converted* Python values, not raw strings — `choices=range(1, 11)`
  paired with `type=int` compares integers, not `"1"` against `range`.

## 19. `nargs`

`nargs` controls **how many command-line values** a single argument
declaration consumes.

| `nargs` value | Meaning | Resulting type |
|---|---|---|
| *(omitted)* | Exactly one value | The single converted value |
| `"?"` | Zero or one value | The value, or `default` (or `const` if the flag is bare) |
| `"*"` | Zero or more values | A list (possibly empty) |
| `"+"` | One or more values (at least one required) | A non-empty list |
| an integer `N` | Exactly `N` values | A list of length `N` |

Examples:

```python
parser.add_argument("--files", nargs="*")
```
```bash
python app.py --files a.txt b.txt c.txt
# args.files == ["a.txt", "b.txt", "c.txt"]

python app.py --files
# args.files == []

python app.py
# args.files == None   (default, unless default= was set)
```

```python
parser.add_argument("--files", nargs="+")
```
```bash
python app.py --files
# error: argument --files: expected at least one argument
```

```python
parser.add_argument("input", nargs="?", default="stdin")
```
```bash
python app.py            # args.input == "stdin"
python app.py data.csv   # args.input == "data.csv"
```

```python
parser.add_argument("--point", nargs=2, type=float, metavar=("X", "Y"))
```
```bash
python app.py --point 1.5 2.5
# args.point == [1.5, 2.5]
```

Mixing multiple `nargs="*"`/`"+"` positional arguments in one parser is
ambiguous and generally avoided — argparse cannot know where one
variable-length positional ends and the next begins. Keep at most one
variable-length positional argument per parser, and prefer named
optional arguments (with their own `nargs`) once you need more than
one collection-like input.

## 20. `const=`

`const=` supplies a **fixed value** used by certain actions/`nargs`
combinations, distinct from `default=` (used when the argument is
*absent*) and from the parsed value (used when the argument is
present with an explicit value).

Two places `const=` shows up:

```python
parser.add_argument("--mode", action="store_const", const="debug", default="normal")
```
```bash
python app.py --mode   # args.mode == "debug"  (const, since store_const takes no value)
python app.py          # args.mode == "normal" (default)
```

```python
parser.add_argument("--log-level", nargs="?", const="INFO", default="WARNING")
```
```bash
python app.py                       # args.log_level == "WARNING" (absent -> default)
python app.py --log-level           # args.log_level == "INFO"    (present, no value -> const)
python app.py --log-level DEBUG     # args.log_level == "DEBUG"   (present, with value)
```

This second pattern — `nargs="?"` plus `const=` — is the standard way
to build a flag that means one thing bare, another thing with an
explicit value, and a third thing when omitted entirely.

## 21. `metavar=`

`metavar=` controls the placeholder name shown for an argument's
*value* in usage and help text — it has no effect on parsing itself.

Without a metavar:

```python
parser.add_argument("--input")
```
```
usage: app.py [--input INPUT]
```

argparse's default is the (upper-cased) destination name — reasonable,
but not always the clearest thing to show a user. With an explicit
metavar:

```python
parser.add_argument("--input", metavar="FILE")
```
```
usage: app.py [--input FILE]
```

For `nargs=N`, a tuple of names documents each position:

```python
parser.add_argument("--point", nargs=2, type=float, metavar=("X", "Y"))
```
```
usage: app.py [--point X Y]
```

A good metavar names *what kind of value* is expected (`FILE`, `PATH`,
`N`, `URL`) rather than restating the option name — `--input INPUT` is
redundant; `--input FILE` tells the user something new.

## 22. `dest=`

`dest=` names the attribute argparse stores the parsed value under in
the `Namespace`. Usually you never need to set it — argparse derives a
sensible default automatically:

- For a **positional** argument, `dest` is the name you gave it
  directly: `add_argument("filename")` → `args.filename`.
- For an **optional** argument, `dest` is derived from the first
  **long** option string (falling back to the first short one if no
  long form exists), with leading dashes stripped and internal dashes
  converted to underscores: `add_argument("--input-file")` →
  `args.input_file`.

Set `dest=` explicitly when you want the attribute name to differ from
what that derivation would produce — most often when two related flags
should populate the *same* attribute:

```python
parser.add_argument("--verbose", dest="loglevel", action="store_const", const="DEBUG")
parser.add_argument("--quiet", dest="loglevel", action="store_const", const="ERROR")
parser.set_defaults(loglevel="INFO")
```

Here, `--verbose` and `--quiet` are two different flags on the command
line, but both write to the single `args.loglevel` attribute your
application logic reads — the CLI surface and the internal data model
are decoupled deliberately.

## 23. `help=`

`help=` is the text shown for this argument in `--help` output. It
seems minor, but it is the single biggest lever you have over whether
your CLI is usable by someone who is not you.

Bad:
```python
parser.add_argument("--input", help="file")
```

Good:
```python
parser.add_argument("--input", help="Path to the input CSV file to process")
```

Guidelines:

- State **what the value is** and, if not obvious, **what it affects**
  — not just a restatement of the flag name.
- Keep it to one line where possible; argparse wraps long help text
  automatically, but a wall of text per argument makes `--help` output
  hard to scan.
- Mention defaults explicitly in the text (`"(default: json)"`) *or*
  use `ArgumentDefaultsHelpFormatter` (§25) to have argparse append
  them automatically — don't do both, or defaults will be printed
  twice.
- For flags, describe the *effect* of setting them: `"Enable verbose
  logging output"`, not `"Verbose flag"`.

## 24. Help Output

Every `ArgumentParser` gets a `-h`/`--help` option automatically
(unless `add_help=False`), which prints usage, positional arguments,
optional arguments, and exits. Given:

```python
parser = argparse.ArgumentParser(
    prog="csv-tool",
    description="Inspect and summarize CSV files.",
)
parser.add_argument("input", help="Path to the input CSV file")
parser.add_argument("-o", "--output", metavar="FILE", help="Write summary to FILE instead of stdout")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
```

`python csv-tool.py --help` produces:

```
usage: csv-tool [-h] [-o FILE] [--verbose] input

Inspect and summarize CSV files.

positional arguments:
  input                 Path to the input CSV file

options:
  -h, --help            show this help message and exit
  -o FILE, --output FILE
                        Write summary to FILE instead of stdout
  --verbose             Enable verbose output
```

(The exact formatting of argparse help/error output can vary by Python
version and terminal/environment settings; examples here show the
logical content and representative formatting.)

(On Python versions before 3.10, the `options:` heading reads
`optional arguments:` instead — a cosmetic, version-dependent
difference, not something your code needs to handle.)

Every part of this — the usage line's bracket/ordering conventions,
the two labeled sections, the description at the top — is generated
from what you declared. There is no separate "write the help text"
step; the help *is* the parser definition, rendered.

## 25. Description and Epilog

`description=` appears **above** the argument listing; `epilog=`
appears **below** it. Together they turn `--help` from a bare argument
reference into actual documentation.

```python
parser = argparse.ArgumentParser(
    description="Convert data files between JSON and CSV formats.",
    epilog=(
        "Examples:\n"
        "  data_tool.py convert --input data.csv --output data.json --format json\n"
        "  data_tool.py convert --input data.json --output data.csv --format csv\n"
    ),
)
```

By default argparse **re-wraps and collapses whitespace** in both
`description` and `epilog` — so a multi-line epilog like the one above
will lose its line breaks and look wrong unless you also switch
formatter classes (§25 next section covers exactly this fix, with
`RawDescriptionHelpFormatter`).

Use `description` to say what the tool *does*, in a sentence or two.
Use `epilog` for concrete example invocations — the single most useful
thing you can put in `--help` output for a real user, and something a
bare argument list can never convey on its own.

## 26. Formatter Classes

`formatter_class=` controls how `ArgumentParser` renders help text.
Passed as a class (not an instance) to the constructor:

```python
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
```

| Formatter | Effect |
|---|---|
| `HelpFormatter` | The default: wraps and re-flows `description`, `epilog`, and each `help=` string |
| `RawDescriptionHelpFormatter` | Leaves `description` and `epilog` exactly as written (preserves line breaks); still wraps individual `help=` strings |
| `RawTextHelpFormatter` | Leaves *everything* — description, epilog, and every `help=` string — exactly as written |
| `ArgumentDefaultsHelpFormatter` | Automatically appends `(default: ...)` to each argument's help text |
| `MetavarTypeHelpFormatter` | Shows each argument's `type.__name__` (e.g. `int`, `str`) as its metavar instead of the destination name |

Using `RawDescriptionHelpFormatter` to fix the multi-line epilog from
§24:

```python
parser = argparse.ArgumentParser(
    epilog=(
        "Examples:\n"
        "  data_tool.py convert --input data.csv --output data.json\n"
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
```

Using `ArgumentDefaultsHelpFormatter` to auto-document defaults instead
of writing `"(default: ...)"` into every `help=` string by hand:

```python
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--format", default="json", help="Output format")
# --help now shows: --format FORMAT  Output format (default: json)
```

You can only pass **one** formatter class per parser — if you want raw
text *and* auto-documented defaults, subclass both:

```python
class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(formatter_class=HelpFormatter)
```

## 27. `parse_args()`

`parse_args()` is the method that actually runs the parser against a
list of arguments and returns a `Namespace` (§29).

```python
args = parser.parse_args()          # reads sys.argv[1:] implicitly
args = parser.parse_args(["--verbose", "data.csv"])  # explicit list
```

Behavior:

- With no argument, it parses `sys.argv[1:]` — the normal, real-world
  invocation path.
- Given an explicit list of strings, it parses *that* instead, ignoring
  `sys.argv` entirely. This is the basis of all CLI testing (§60): a
  test can call `parser.parse_args(["--input", "data.csv"])` directly,
  with no subprocess, no real command line, and no dependency on how
  the test runner itself was invoked.
- On success, returns a `Namespace`.
- On failure (missing required argument, invalid type, unknown
  argument, invalid choice, etc.), it prints a usage message and an
  error to stderr and calls `sys.exit(2)` — by default, this **raises
  `SystemExit`**, which will propagate up and terminate the process
  (or the test, if not caught — §60 shows how to assert on this
  deliberately with `pytest.raises(SystemExit)`).
- `-h`/`--help` and `--version` (if defined) also exit the process,
  with status `0`, after printing their respective output.

## 28. `parse_known_args()`

`parse_known_args()` behaves like `parse_args()`, except it does not
error out on unrecognized arguments — instead it returns them
separately.

```python
args, unknown = parser.parse_known_args()
```

- `args` — a `Namespace` of everything the parser *did* recognize.
- `unknown` — a plain `list[str]` of leftover tokens the parser didn't
  understand.

Use cases:

- **Argument forwarding.** A wrapper CLI that handles a few of its own
  flags and passes the rest through to another tool or subprocess
  unmodified.
- **Incremental/plugin-style parsers**, where different parts of a
  larger application each claim a subset of arguments and later merge
  results.
- **Tolerant tooling** where truly rejecting unknown flags would be
  worse than ignoring them (used sparingly — most CLIs *should* reject
  unknown arguments, since silently ignoring a typo'd flag is a poor
  user experience).

```python
parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")

args, unknown = parser.parse_known_args(["--verbose", "--extra", "value"])
# args == Namespace(verbose=True)
# unknown == ["--extra", "value"]
```

Prefix matching (§49) still applies with `parse_known_args()`: an
abbreviated form of a known option (such as `--verb` for `--verbose`)
is consumed by the parser rather than appearing in the `unknown` list.

## 29. `parse_intermixed_args()`

Ordinarily, argparse expects positional arguments to be contiguous
relative to a variable-length (`nargs="*"`/`"+"`) positional — once
argparse starts consuming positionals, interleaved optional arguments
in the middle can behave unexpectedly. `parse_intermixed_args()`
(added in Python 3.7) relaxes this, allowing positional and optional
arguments to be freely interleaved on the command line.

```python
parser = argparse.ArgumentParser()
parser.add_argument("--flag", action="store_true")
parser.add_argument("files", nargs="*")

args = parser.parse_intermixed_args(["a.txt", "--flag", "b.txt"])
# args.files == ["a.txt", "b.txt"], args.flag == True
```

With plain `parse_args()`, the same input can fail to group `files` as
expected, because `--flag` appearing in the middle of the positional
run confuses the single-pass matching algorithm.

Limitations, stated plainly:

- Officially, `parse_intermixed_args()` **does not support subparsers**
  in the same parser, nor **mutually exclusive groups that contain both
  optional and positional arguments**.
- Separately from those documented restrictions, it is good design to
  avoid more than one variable-length (`nargs="*"`, `"+"`) positional
  argument: where one ends and the next begins can be ambiguous. That
  is a design recommendation, not an official unsupported feature.
- There is a companion `parse_known_intermixed_args()`, mirroring
  `parse_known_args()`.
- Reach for this only when you have a genuine, demonstrated need for
  interleaved positional/optional syntax (tools like `find` do this);
  for the vast majority of CLIs, plain `parse_args()` combined with
  disciplined argument ordering in documentation and examples (§57) is
  simpler and has no such restrictions.

## 30. `Namespace`

`Namespace` is the simple object `parse_args()` returns — parsed values
stored as attributes, one per argument.

```python
args = parser.parse_args(["--verbose", "data.csv"])
print(args)
# Namespace(verbose=True, input_file='data.csv')

print(args.verbose)     # True
print(args.input_file)  # 'data.csv'
```

Useful operations:

```python
vars(args)
# {'verbose': True, 'input_file': 'data.csv'}
```

`vars()` converts a `Namespace` into a plain `dict` — handy for
logging the full set of parsed arguments, or for `**args_dict`-style
unpacking into a function call.

`Namespace` objects support `==` comparison by attribute value (useful
in tests — `assert args == argparse.Namespace(verbose=True, input_file="data.csv")`),
and attributes can be set on them manually before or after parsing
(`args.extra = "value"`) — though doing so outside of `set_defaults()`
(§38) is unusual and generally a sign the value belongs somewhere else
in your design.

Do not treat a `Namespace` as a long-lived data structure to pass deep
into application code — §59 covers why converting it into an explicit,
typed configuration object at the boundary is the better production
pattern.

## 31. Explicit `argv` Lists

Every example above that calls `parser.parse_args([...])` with an
explicit list, rather than relying on the implicit `sys.argv[1:]`, is
demonstrating the single most important testability feature in
argparse.

```python
argv = ["--input", "data.csv", "--verbose"]
args = parser.parse_args(argv)
```

Why this matters, concretely:

- **Testing.** A pytest test can construct exactly the argument list it
  wants to exercise, with no subprocess, no monkey-patching of
  `sys.argv`, and no dependency on how pytest itself was invoked (§60).
- **Embedding.** A library that wants to offer CLI-style configuration
  internally (e.g., parsing a config string split into tokens) can
  reuse the same parser without a real command line ever existing.
- **Programmatic invocation.** Other Python code — a notebook, a
  wrapper script, another tool — can drive your CLI's argument-parsing
  logic directly and predictably.

This is also the reasoning behind the `main(argv=None)` pattern
(§39, §63): accepting an optional `argv` parameter that defaults to
`None` (meaning "use real `sys.argv`") makes the *entire program*, not
just the parser, testable the same way.

## 32. Mutually Exclusive Groups

`add_mutually_exclusive_group()` declares a set of arguments where **at
most one** may be supplied — supplying two from the same group is a
parse error.

```python
group = parser.add_mutually_exclusive_group()
group.add_argument("--verbose", action="store_true")
group.add_argument("--quiet", action="store_true")
```

```bash
python app.py --verbose            # OK
python app.py --quiet              # OK
python app.py --verbose --quiet    # error: argument --quiet: not allowed with argument --verbose
python app.py                      # OK — neither is required
```

Pass `required=True` to the group itself to require that **exactly
one** (not zero) of the group's arguments be given:

```python
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--json", action="store_true")
group.add_argument("--csv", action="store_true")
```

```bash
python app.py               # error: one of the arguments --json --csv is required
```

Mutually exclusive groups can hold positional arguments too, though in
practice they are used almost exclusively with optional flags — mixing
in a required positional alongside a mutually-exclusive optional group
gets confusing fast and is best avoided.

## 33. Argument Groups

`add_argument_group()` is purely organizational — it changes how
arguments are displayed in `--help`, grouped under a custom heading,
with **no effect on parsing or validation**.

```python
parser = argparse.ArgumentParser()

input_group = parser.add_argument_group("Input Options")
input_group.add_argument("--input", required=True)
input_group.add_argument("--format", choices=["csv", "json"])

output_group = parser.add_argument_group("Output Options")
output_group.add_argument("--output")
output_group.add_argument("--overwrite", action="store_true")
```

`--help` now shows two labeled sections instead of one flat list:

```
Input Options:
  --input INPUT
  --format {csv,json}

Output Options:
  --output OUTPUT
  --overwrite
```

This matters more than it looks: a CLI with fifteen flags in one flat
list is much harder to scan than the same fifteen flags organized into
three or four labeled groups. It costs nothing beyond calling
`add_argument_group()` and using the returned object instead of
`parser` directly for those specific `add_argument()` calls. Do not
confuse this with `add_mutually_exclusive_group()` (§32) — the two
solve unrelated problems (documentation grouping vs. validation), and
an argument group by itself enforces nothing.

## 34. Parent Parsers

`parents=` lets you define a set of common arguments once, in a
standalone `ArgumentParser`, and reuse them across multiple other
parsers — most commonly, across every subcommand in a subparser-based
CLI (§35–§37).

```python
common = argparse.ArgumentParser(add_help=False)
common.add_argument("--verbose", action="store_true", help="Enable verbose output")
common.add_argument("--config", type=Path, help="Path to a config file")

parser = argparse.ArgumentParser(parents=[common])
parser.add_argument("input_file")
```

`parser` now has `--verbose`, `--config`, *and* `input_file` — the
parent's arguments are copied in.

Two details that matter in practice:

- **`add_help=False` on the parent is mandatory.** Every
  `ArgumentParser` auto-adds `-h`/`--help` by default; if both the
  parent and the child try to add it, you get a conflicting-option
  error (§54). A parent parser meant only to be reused via `parents=`
  should always disable its own help.
- **Conflicting option strings across parents raise an error** by
  default (`conflict_handler="error"`, §54) — reuse `parents=` to
  *add* shared arguments, not to combine parsers that redefine the
  same flag differently.

This pays off most clearly in multi-command tools: instead of
repeating `--verbose`, `--config`, and `--dry-run` in every subcommand
definition (and risking them drifting out of sync), define them once
and pass `parents=[common]` to every `subparsers.add_parser(...)` call
(§37).

## 35. Subcommands

Many real CLIs are not "one command with flags" but a **family of
commands** under one program name — `git commit`, `git push`,
`docker run`, `docker build`. argparse supports this directly through
`add_subparsers()`.

```python
parser = argparse.ArgumentParser(prog="tool")
subparsers = parser.add_subparsers(dest="command")

ingest = subparsers.add_parser("ingest")
validate = subparsers.add_parser("validate")
export = subparsers.add_parser("export")
```

```bash
python tool.py ingest
python tool.py validate
python tool.py export
```

`dest="command"` tells argparse to record *which* subcommand was
chosen as `args.command` — without it, you would have no way to know
which subparser matched. Each subparser (`ingest`, `validate`,
`export`) is itself a full `ArgumentParser`, capable of having its own
positional arguments, optional arguments, and even its own nested
`--help`.

The distinction to keep straight: `tool` is the **command** (the
program); `ingest`, `validate`, `export` are **subcommands** — each one
effectively its own mini-CLI, sharing only the top-level program name
and (optionally, via `parents=`) some common arguments.

## 36. Subparser Design

`subparsers.add_parser()` accepts most of the same constructor
parameters as `ArgumentParser` itself, since it *is* creating one:

```python
ingest_parser = subparsers.add_parser(
    "ingest",
    help="Load data from a source into the pipeline",
    description="Ingest data from a file or URL into the local pipeline store.",
    parents=[common],
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
ingest_parser.add_argument("source", help="File path or URL to ingest")
ingest_parser.add_argument("--batch-size", type=int, default=1000)
```

Key parameters specific to `add_parser()` itself:

- **`name`** (positional, first arg) — the subcommand string a user
  types (`ingest`).
- **`help`** — the one-line summary shown next to this subcommand in
  the *parent* parser's `--help` output (distinct from the
  subparser's *own* `description`, which appears in
  `tool.py ingest --help`).
- **`description`** — shown at the top of `tool.py ingest --help`.
- **`aliases`** — alternate names for the same subcommand (§37).
- **`parents`** — shared arguments, as in §34.
- **`formatter_class`** — per-subcommand help formatting, independent
  of the parent parser's own formatter.

Each subparser's own `--help` is fully independent and fully generated
— `python tool.py ingest --help` shows only `ingest`'s arguments, with
its own usage line, description, and epilog.

## 37. Required Subcommands

By default (on modern Python), a subparser group is **not** required —
running `tool.py` with no subcommand at all is valid, and
`args.command` will simply be `None`. Whether that is desirable depends
on the tool; usually it is not — a tool with no subcommand and nothing
to do should say so clearly rather than silently doing nothing.

```python
subparsers = parser.add_subparsers(dest="command", required=True)
```

```bash
python tool.py
# error: the following arguments are required: command
```

`required=True` on `add_subparsers()` has been supported since Python
3.7 and is the standard way to enforce "a subcommand must be chosen."
(Historically, in Python 3.3–3.6, subparsers were required by default
with no way to opt out cleanly; Python 3.7 made them optional by
default and introduced this explicit `required=` flag — worth knowing
if you ever encounter code targeting very old Python, but not a
concern for current versions.)

## 38. Subcommand Aliases

`aliases=` on `add_parser()` lets a subcommand be invoked by more than
one name — most commonly a long, descriptive name plus a short,
memorized one:

```python
checkout_parser = subparsers.add_parser("checkout", aliases=["co"])
```

```bash
python tool.py checkout branch-name
python tool.py co branch-name
# identical behavior
```

Use aliases sparingly, and only for genuinely common operations —
every alias is one more name a user (and your documentation) has to
remember exists, and `args.command` will reflect whichever name was
actually typed unless you normalize it yourself (e.g. in the dispatch
function, §39) — a detail worth testing explicitly if your dispatch
logic branches on the string value of `args.command`.

## 39. `set_defaults()` and Dispatch

`set_defaults()` sets attribute values on the resulting `Namespace`
that are not tied to any specific `add_argument()` call — most usefully,
attaching a **handler function** to each subparser, so the top-level
code doesn't need a big `if/elif` chain to figure out what to run.

```python
def handle_ingest(args: argparse.Namespace) -> int:
    print(f"Ingesting from {args.source}")
    return 0

def handle_validate(args: argparse.Namespace) -> int:
    print(f"Validating {args.path}")
    return 0

ingest_parser = subparsers.add_parser("ingest")
ingest_parser.add_argument("source")
ingest_parser.set_defaults(func=handle_ingest)

validate_parser = subparsers.add_parser("validate")
validate_parser.add_argument("path")
validate_parser.set_defaults(func=handle_validate)

args = parser.parse_args()
return args.func(args)
```

Whichever subcommand was chosen, `args.func` is *that subcommand's*
handler — parsed automatically, with no manual lookup, no dictionary of
command names to functions, and no `if args.command == "ingest": ...`
chain that grows linearly (and error-pronely) with every new
subcommand added. `set_defaults()` is not limited to functions — it can
set any attribute, and is also useful for giving a subparser a
different default value for an argument shared (via `parents=`) with
other subparsers.

## 40. CLI Dispatch Architecture

Putting §35–§39 together, a clean top-level shape looks like:

```
main(argv)
    ↓
build_parser()          # pure construction, no side effects, fully testable alone
    ↓
parser.parse_args(argv) # parsing
    ↓
validate(args)          # cross-argument checks argparse itself can't express (§42)
    ↓
args.func(args)         # dispatch to the chosen subcommand's handler
    ↓
return status code
```

```python
from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Load data")
    ingest.add_argument("source")
    ingest.set_defaults(func=handle_ingest)

    return parser


def handle_ingest(args: argparse.Namespace) -> int:
    print(f"Ingesting from {args.source}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

This shape is worth internalizing because every subsequent section —
validation, testing, production architecture — builds directly on top
of it. Notice that `build_parser()` has **no side effects** (it only
constructs and returns a parser) and `main()` accepts an *optional*
`argv`, defaulting to `None` (meaning "use the real command line" —
argparse itself treats `None` as "read `sys.argv[1:]`"). Both choices
exist purely to make this code trivially testable (§60, §63) without
subprocesses or `sys.argv` monkey-patching.

## 41. Input Validation

argparse validates **syntax**: is this a valid integer, is this one of
the allowed choices, was a required argument supplied. It cannot
validate **semantics** that depend on values outside a single
argument's own string — that is your job, after parsing.

The boundary types worth handling explicitly:

- **Numeric ranges** — `type=` alone only converts; range-checking
  needs a custom function (§15's `positive_int` pattern, generalized).
- **File/directory existence** — a `type=Path` argument is still just
  a `Path` object; whether it points to a real, readable file is a
  separate check (§43's `existing_file` example).
- **Enumerated values** — `choices=` (§17) covers the simple case;
  more complex enumerations (case-insensitive matching, aliases) need
  a custom `type=` function.
- **Required combinations** — "if `--format csv`, then `--output` must
  be given" — cannot be expressed by any single `add_argument()` call
  (§44).
- **Mutually exclusive settings** beyond what `add_mutually_exclusive_
  group()` can express (e.g., three-way exclusivity with contextual
  exceptions) — also handled after parsing.

## 42. Path Arguments

`type=pathlib.Path` converts a raw string argument directly into a
`Path` object, ready for the rest of your program to use — see
[02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)
for the full `pathlib` treatment; this section covers only the
argparse-specific integration.

```python
from pathlib import Path

parser.add_argument("--input", type=Path)
```

```bash
python app.py --input data/raw.csv
# args.input is a pathlib.Path (repr is platform-dependent, e.g. PosixPath('data/raw.csv') on POSIX)
```

Notes specific to CLI usage:

- The resulting `Path` is **not** automatically resolved to an
  absolute path, and its existence is **not** checked — `type=Path`
  only performs the string→`Path` conversion. If you need "this path
  must already exist," write a custom type function (§43).
- Relative paths supplied on the command line are relative to the
  **current working directory the process was started from** — not the
  script's own location. This is almost always what a CLI user expects
  (`python tool.py --input data.csv` from inside a project directory
  should look in that directory), but it is worth stating explicitly,
  since it surprises people coming from contexts where "relative to the
  script" is assumed instead.
- Existence/type checks (file vs. directory, readable vs. writable)
  belong in validation, layered on top of the raw `Path` — see §43.

## 43. Cross-Argument Validation

Some rules only make sense in terms of *more than one* argument at
once — argparse's per-argument model has no way to express these
directly. The standard pattern: parse first, then validate, and call
`parser.error()` (§44) on failure so the error looks and behaves like
any other argparse error.

```python
args = parser.parse_args(argv)

if args.format == "csv" and args.output is None:
    parser.error("--output is required when --format=csv")
```

```bash
python app.py --format csv
# usage: app.py [-h] --format {json,csv} [--output OUTPUT]
# app.py: error: --output is required when --format=csv
```

The principle worth remembering (from §41): **do not force every
business rule into `add_argument()`**. `choices=`, `required=`, and
mutually exclusive groups handle simple, single- or paired-argument
constraints elegantly; anything involving three-plus arguments, or
conditional logic ("required *only if* X"), reads far more clearly as
an explicit `if` statement after parsing than as increasingly clever
argparse configuration.

## 44. `parser.error()`

`parser.error(message)` is how application code raises an argparse-
style error *after* parsing has already succeeded — used for the
cross-argument validation in §43, and for custom type functions when
you already have a `parser` reference available (though
`ArgumentTypeError`, §15, is usually cleaner for type-function-level
errors).

```python
parser.error("--output is required when --format=csv")
```

Behavior: prints the parser's usage line, then
`"{prog}: error: {message}"`, to stderr, then calls
`self.exit(2, message)` — meaning it **terminates the process** with
status code 2, the same code `parse_args()` itself uses for its own
parse failures. This is exactly why `parser.error()` is preferred over
a bare `raise ValueError(...)` or `print(...); sys.exit(1)` for
argument-related failures — it produces output indistinguishable, in
shape, from argparse's own built-in errors, which is what users of a
CLI expect from *any* "you gave me a bad argument" failure.

## 45. `parser.exit()`

`parser.exit(status=0, message=None)` is the lower-level primitive
`parser.error()` and `-h`/`--version` are built on: optionally print a
message, then call `sys.exit(status)`.

```python
parser.exit(0, "Nothing to do; exiting.\n")
```

Direct use of `parser.exit()` in application code is rare — most
application-level "stop now" logic is better expressed by simply
`return`ing a status code from `main()` (§40) and letting
`if __name__ == "__main__": raise SystemExit(main())` be the *one*
place in the program that turns a status into an actual process exit.
Scattering `parser.exit()` (or bare `sys.exit()`) calls throughout
business logic makes that logic harder to test (§60) — a test calling
a function directly does not want it to unexpectedly kill the test
process — and harder to compose if it's ever called from something
other than a top-level script.

## 46. `print_help()`

`parser.print_help(file=None)` prints the same help text `-h`/`--help`
would, without exiting — useful for custom flows.

```python
if len(sys.argv) == 1:   # no arguments at all; falsey values like 0 or False can't be confused with this
    parser.print_help()
    return 1
```

A common pattern: printing help when no arguments were given at all
(rather than argparse's default of silently proceeding, if everything
happens to be optional with defaults) — genuinely useful for a
top-level tool where "just print help" is friendlier than "run with all
defaults and produce confusing output." (For a CLI with subcommands, test
the explicit state instead — `if args.command is None:` — rather than
the truthiness of parsed values.) `file=` defaults to `sys.stdout`;
pass `file=sys.stderr` if the help is being shown as part of an error
path.

## 47. `print_usage()`

`parser.print_usage(file=None)` prints only the one-line usage summary
— the same line shown at the top of full help output — without the
positional/optional argument descriptions.

```python
parser.print_usage(sys.stderr)
```

Use this when full help would be too much (e.g., inside a custom error
handler that wants a quick reminder of correct syntax) but a bare error
message alone would be too little.

## 48. Version Handling

`action="version"` is the standard way to implement `--version`:

```python
parser.add_argument(
    "--version",
    action="version",
    version="%(prog)s 1.0.0",
)
```

```bash
python app.py --version
# app.py 1.0.0
```

`%(prog)s` is replaced with the parser's `prog` value automatically —
the same substitution mechanism used in usage strings, so the version
string stays correct even if `prog` changes. Like `-h`/`--help`, this
prints and exits immediately (status 0) — it does not require any
other argument to also be satisfied, and can appear before or instead
of other required arguments on the command line.

## 49. Prefixes

`prefix_chars=` on `ArgumentParser` controls which characters introduce
an optional argument — `-` by default, and the reason `add_argument`
can tell `"--verbose"` (optional) apart from `"filename"` (positional)
by simply checking the first character.

```python
parser = argparse.ArgumentParser(prefix_chars="-+")
parser.add_argument("+f")  # a '+'-prefixed optional argument
```

Changing `prefix_chars` is rare and mostly historical (some Unix tools
use `+` for "disable" style flags, mirroring old `getopt` conventions).
For virtually all new CLI tools, leave this at its default — deviating
from `-`/`--` breaks the expectations every other tool on the system
has trained users to have.

## 50. `allow_abbrev`

By default, argparse allows a **long option** to be typed as any
unambiguous prefix of itself:

```python
parser.add_argument("--verbose", action="store_true")
```

```bash
python app.py --verb    # works — unambiguous prefix of --verbose
python app.py --v       # works too, as long as no other option starts with --v
```

This is convenient interactively, but a liability in scripts and
production tooling: adding a *new* long option later (`--version`, say)
can silently make a previously-unambiguous abbreviation (`--v`)
ambiguous, breaking any existing script that relied on it — with no
warning until that script breaks in production.

```python
parser = argparse.ArgumentParser(allow_abbrev=False)
```

With `allow_abbrev=False`, only exact, full option strings are
accepted. For any CLI whose invocations might be scripted, checked into
CI configuration, or run unattended, `allow_abbrev=False` is the safer
default — it trades a small amount of interactive typing convenience
for guaranteed forward compatibility. (Historically, a bug — bpo-26967
— meant `allow_abbrev=False` did not fully suppress abbreviation
matching for grouped short options in some Python versions before 3.8;
current Python versions do not have this issue.)

## 51. `fromfile_prefix_chars`

`fromfile_prefix_chars` lets users supply arguments from a file instead
of typing them all on the command line, using a prefix character
(conventionally `@`) in front of a filename.

```python
parser = argparse.ArgumentParser(fromfile_prefix_chars="@")
parser.add_argument("files", nargs="*")
```

Given a file `args.txt` containing:
```
--verbose
data1.csv
data2.csv
```

```bash
python app.py @args.txt
# equivalent to: python app.py --verbose data1.csv data2.csv
```

Why this exists: some commands need far more arguments than is
comfortable (or possible, on some shells) to type or paste directly —
long lists of filenames, for instance. `@file` expansion lets that list
live in a file instead.

Caveats:

- Each line of the file becomes, by default, **one argument token** —
  this is why the example file has `--verbose` and each filename on its
  own line, not space-separated on one line (that would be treated as
  a single token containing spaces).
- This behavior is customizable — see §52.
- Treat argument files the same as any other untrusted input if their
  contents come from outside your control (§71) — there is nothing
  inherently dangerous about `@file` expansion itself (it does not
  execute anything), but a file supplying unexpected flags is still a
  form of user-controlled input to your program.
- `fromfile_prefix_chars` is `None` (disabled) by default; most CLIs
  never need it, and it is worth adding only when argument lists are
  genuinely, frequently too long to type.

## 52. Custom Argument File Parsing

`ArgumentParser.convert_arg_line_to_args(arg_line)` is the method
`fromfile_prefix_chars` expansion calls **once per line** of an
`@file` — override it to change how each line is turned into argument
tokens.

The default implementation returns `[arg_line]` (the whole line, as
written, as one token) for every line — an empty line becomes `[""]`. To instead treat each
*whitespace-separated word* on a line as its own token (useful for a
file listing several filenames per line):

```python
class SpaceSeparatedArgumentParser(argparse.ArgumentParser):
    def convert_arg_line_to_args(self, arg_line: str) -> list[str]:
        return arg_line.split()

parser = SpaceSeparatedArgumentParser(fromfile_prefix_chars="@")
parser.add_argument("files", nargs="*")
```

Given a file with `data1.csv data2.csv data3.csv` on one line, this
override splits it into three separate tokens instead of one long
string. Only override this when the default one-line-per-token
behavior doesn't match the argument-file format you actually need —
for most tools that use `@file` at all, the default is fine.

## 53. `argument_default`

`argument_default=` on the `ArgumentParser` constructor sets a global
fallback default, applied to any argument that doesn't specify its own
`default=`.

```python
parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
```

With `argparse.SUPPRESS` as the global default, any argument not
explicitly given on the command line is simply **absent from the
resulting `Namespace`** — no attribute is set for it at all — rather
than defaulting to `None`. This is useful when a later configuration-
merging step (§58) needs to distinguish "the user didn't touch this"
from "the user explicitly set it," across every argument, without
repeating `default=argparse.SUPPRESS` on each `add_argument()` call.

Precedence: a **per-argument** `default=` always wins over the
parser-level `argument_default=` — the global setting only fills in
for arguments that leave `default=` unset entirely.

## 54. `conflict_handler`

By default, defining two arguments with the **same option string**
raises an error immediately:

```python
parser.add_argument("-f", "--file")
parser.add_argument("-f", "--force")
# argparse.ArgumentError: argument -f/--force: conflicting option string: -f
```

This default (`conflict_handler="error"`) is almost always what you
want — a silent collision between two flags is a real bug, and failing
loudly, at parser-construction time, is far better than the confusing
runtime behavior a silent override would produce.

```python
parser = argparse.ArgumentParser(conflict_handler="resolve")
parser.add_argument("-f", "--file")
parser.add_argument("-f", "--force")
# no error: -f now belongs to --force; --file keeps its long form only
```

`conflict_handler="resolve"` allows a later `add_argument()` call to
*take over* a conflicting option string from an earlier one, rather
than erroring. This is a niche escape hatch — mainly useful when
combining `parents=` from sources you don't fully control and need to
deliberately override one of their flags. For code you write yourself,
avoiding the conflict in the first place (choosing distinct option
strings) is almost always better than relying on `resolve` to paper
over it.

## 55. `exit_on_error`

Added in Python 3.9, `exit_on_error=False` changes what happens when
`parse_args()` encounters most parsing errors: instead of printing a
message and calling `sys.exit(2)` (raising `SystemExit`), it raises
`argparse.ArgumentError` — a regular, catchable exception.

```python
parser = argparse.ArgumentParser(exit_on_error=False)
parser.add_argument("--count", type=int)

try:
    args = parser.parse_args(["--count", "abc"])
except argparse.ArgumentError as exc:
    print(f"Bad arguments: {exc}")
```

This matters for programs that embed argument parsing as one step
inside a larger process that must not simply terminate on bad input —
a long-running service accepting command strings, for instance, where
one malformed command should produce an error response, not kill the
service.

Two things worth being precise about:

- **This parameter does not exist before Python 3.9** — code targeting
  older Python cannot rely on it, and must catch `SystemExit` around
  `parse_args()` instead if it needs to avoid terminating the process.
- Even with `exit_on_error=False`, a small number of paths (most
  notably `-h`/`--help` and `action="version"`) still call
  `parser.exit()` directly and will still raise `SystemExit` — this
  flag governs *parsing errors*, not the deliberate "print and stop"
  actions, which are expected to terminate regardless.

For a typical standalone script invoked once per process, the default
(`exit_on_error=True`) is exactly right — a bad argument *should* end
the program, with a clear message, immediately. Reach for `False` only
when your program's architecture genuinely needs parsing failures to
be recoverable exceptions rather than process termination.

## 56. Custom Actions

For the rare case where none of the standard actions (§13) can express
what an argument needs to do, argparse lets you subclass
`argparse.Action` and pass the class itself as `action=`.

```python
class UppercaseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values.upper())

parser.add_argument("--tag", action=UppercaseAction)
```

```bash
python app.py --tag hello
# args.tag == "HELLO"
```

`__call__`'s parameters:

- **`parser`** — the `ArgumentParser` instance, useful for calling
  `parser.error(...)` from inside a custom action.
- **`namespace`** — the in-progress `Namespace` being built; use
  `setattr(namespace, self.dest, ...)` to store the result.
- **`values`** — the raw (or `type`-converted, if `type=` was also
  given) value(s) captured for this argument.
- **`option_string`** — which specific option string (e.g. `"--tag"`
  vs. a short alias) triggered this call, or `None` for a positional
  argument.

This should be treated as a **last resort**. Almost everything that
looks, at first, like it needs a custom `Action` can actually be
expressed with a custom `type=` function (§15, which runs per-value,
before storage) or with post-parsing validation (§42–§43, which runs
once, after all values are gathered and can see every other argument
too). A custom `Action` is genuinely warranted only when the behavior
must happen *during* parsing and depends on argparse-internal state
(like `option_string`) that a `type=` function never sees. Prefer the
simpler tool whenever it's sufficient.

## 57. CLI UX Principles

Good CLI design borrows heavily from decades of Unix tooling
convention. The properties worth designing for, deliberately:

- **Predictable** — the same input always produces the same output;
  no hidden state, no surprising side effects from a flag whose name
  suggests something narrower.
- **Discoverable** — `--help` (and, for multi-command tools, each
  subcommand's own `--help`) should be enough to learn the tool without
  external documentation.
- **Explicit** — prefer requiring a flag to guessing intent; destructive
  operations especially should not happen by accident (consider
  requiring `--force` or `--yes` for anything irreversible).
- **Safe by default** — the default behavior, with no flags at all,
  should be the least surprising and least destructive one available.
- **Scriptable** — meaningful, distinct exit codes; no interactive
  prompts unless a `--yes`/non-interactive escape hatch also exists;
  machine-parseable output available when needed (see
  [07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)
  for exit-code conventions in depth).
- **Composable** — plays well with pipes and redirection; reads from
  stdin and writes to stdout when that makes sense, reserving stderr
  for diagnostics.
- **Stable** — option names, once shipped, are effectively a public API;
  removing or renaming one breaks every script that calls your tool.
- **Backward-compatible** — new options should be additive; avoid
  changing the meaning of an existing flag.

Concrete practices that support these: always provide `--help`; provide
`--version` for anything users will report bugs against; write error
messages that say what went wrong *and* what a valid input looks like,
not just "invalid argument"; keep defaults sensible enough that most
invocations don't need any flags at all.

## 58. Shell Quoting

Quoting is resolved entirely by the shell, **before** argparse (or even
Python itself) ever runs — this was introduced structurally in §4; this
section fills in the practical details a CLI author needs to know.

```bash
python app.py "hello world"     # one argument: "hello world"
python app.py 'hello world'     # same, single quotes: one argument
python app.py hello world       # two arguments: "hello", "world"
```

Things every CLI author should know about, even without becoming a
shell expert:

- **Whitespace** inside quotes is preserved as part of one token;
  outside quotes, it separates tokens.
- **Escaping** a space with a backslash (`hello\ world`) has the same
  effect as quoting the whole thing.
- **Environment variable expansion** (`$HOME`, `$MY_VAR`) happens
  before your program runs, inside double quotes or unquoted — inside
  single quotes, it does *not* expand (this is a common source of "why
  didn't my variable get substituted" confusion, and is a shell
  behavior, not an argparse one).
- **Wildcard/glob expansion** (`*.csv`) happens before your program
  runs, and only if at least one file matches — if nothing matches,
  most shells pass the literal, unexpanded pattern through, which is
  why "no files found" bugs sometimes manifest as your program trying
  to open a file literally named `*.csv`.
- **Pipes and redirection** (`|`, `>`, `<`) are entirely shell syntax;
  your program never sees these characters as arguments at all — the
  shell has already wired up the process's stdin/stdout/stderr by the
  time your program starts (elaborated in
  [07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)).

This chapter deliberately does not go further into shell syntax itself
— the goal here is only to make clear where the shell's job ends and
argparse's begins.

## 59. Configuration Sources

Command-line arguments are one of several common sources of
configuration for a real program — the others being environment
variables and configuration files, covered in depth in
[09-environment-configuration-and-input-validation.md](09-environment-configuration-and-input-validation.md).
This section exists only to place argparse correctly relative to those
other sources, not to duplicate that chapter.

A common, sensible precedence, from highest to lowest priority:

```
CLI arguments  (most specific to this one invocation)
    ↓ overrides
Environment variables (specific to this machine/session)
    ↓ overrides
Configuration file  (project- or user-level defaults)
    ↓ overrides
Hardcoded defaults  (argparse's own default=)
```

The exact precedence — and whether all three sources are even needed —
is an **application design decision**, not something argparse enforces
or assumes. argparse's role in this picture is narrow and specific:
parsing the CLI-arguments layer, and providing `default=` as the
lowest-priority fallback layer. Merging in environment variables or a
config file, and resolving conflicts between layers, is logic your own
code adds on top — most cleanly, as a step that runs after
`parse_args()` and before the resulting values are wrapped into a
configuration object (§60).

## 60. Configuration Objects

Passing a raw `Namespace` deep into application/domain logic works for
small scripts, but scales poorly: nothing declares what attributes are
guaranteed to exist, type checkers can't verify anything about
`args.whatever`, and domain code becomes implicitly coupled to
argparse's own object shape.

The better pattern: convert the parsed (and validated) `Namespace` into
an explicit, typed configuration object — commonly a `dataclass` — at
the boundary, and pass *that* into the rest of the program.

```python
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    input_path: Path
    output_path: Path | None
    verbose: bool


def build_config(args: argparse.Namespace) -> Config:
    return Config(
        input_path=args.input,
        output_path=args.output,
        verbose=args.verbose,
    )


def run(config: Config) -> int:
    if config.verbose:
        print(f"Reading {config.input_path}")
    # ... domain logic here, using `config`, never `args` ...
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = build_config(args)
    return run(config)
```

Why this is worth the extra step:

- **Type-checkable.** `Config`'s fields have real, static types; a type
  checker can catch a typo'd attribute name or a wrong type flowing
  into `run()` — neither is possible with a bare `Namespace`, whose
  attributes are entirely dynamic.
- **Decoupled.** `run()` (and everything it calls) has no idea argparse
  exists. It could be called from a test, a notebook, or a completely
  different entry point (an HTTP handler, a scheduled job) that builds
  a `Config` some other way, with zero changes to domain logic.
- **A single place for defaults and merging.** If §59's
  CLI/environment/config-file precedence is ever needed, `build_config()`
  is exactly where that merge belongs — one function, one
  responsibility, easy to test in isolation.

## 61. Testing

argparse's design — accepting an explicit list in `parse_args()` (§31)
— makes CLI code some of the most naturally testable code you will
write. No subprocess, no monkey-patched `sys.argv`, no I/O.

```python
import argparse
import pytest

from mytool.cli import build_parser


def test_default_format():
    parser = build_parser()
    args = parser.parse_args(["data.csv"])
    assert args.format == "json"


def test_explicit_format():
    parser = build_parser()
    args = parser.parse_args(["data.csv", "--format", "csv"])
    assert args.format == "csv"


def test_missing_required_argument_exits():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])  # missing required positional


def test_invalid_choice_exits():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["data.csv", "--format", "xml"])


def test_mutually_exclusive_flags_reject_both():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["data.csv", "--verbose", "--quiet"])


def test_subcommand_dispatch(capsys):
    parser = build_parser()
    args = parser.parse_args(["ingest", "source.csv"])
    status = args.func(args)
    assert status == 0
    captured = capsys.readouterr()
    assert "Ingesting" in captured.out
```

What to cover, systematically:

- **Valid inputs**, including every meaningfully different combination
  of positional/optional arguments and subcommands.
- **Missing required arguments** — expect `SystemExit` (or
  `argparse.ArgumentError`, if `exit_on_error=False`, §55).
- **Defaults** — call `parse_args()` with the argument omitted, assert
  the default landed correctly.
- **Flags** — both present and absent.
- **Invalid types and choices** — expect `SystemExit`.
- **Mutually exclusive combinations** — both individually valid, and
  together (should fail).
- **Subcommands**, including dispatch (`args.func(args)` actually calls
  the right handler and it behaves correctly).
- **Custom validators** — call the validator function directly for unit
  tests, *and* through the parser for integration-style tests.
- **`parser.error()` / cross-argument validation paths** — expect
  `SystemExit`.
- **Help/version behavior** is usually *not* worth asserting on in
  detail (exact wording is an implementation detail of argparse's own
  formatting), beyond confirming `-h`/`--version` exit with status 0
  and don't crash.

`SystemExit` carries a `.code` attribute if you need to assert on the
specific exit status:

```python
def test_missing_argument_exit_code():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args([])
    assert exc_info.value.code == 2
```

## 62. Testing `main(argv)`

Everything in §61 tests the *parser*. Testing the whole program means
testing `main(argv)` (§40) the same way:

```python
from mytool.cli import main


def test_main_success(tmp_path, capsys):
    input_file = tmp_path / "data.csv"
    input_file.write_text("a,b\n1,2\n")

    status = main(["ingest", str(input_file)])

    assert status == 0
    captured = capsys.readouterr()
    assert "Ingesting" in captured.out


def test_main_missing_argument():
    with pytest.raises(SystemExit):
        main([])
```

The payoff of `main(argv: Sequence[str] | None = None) -> int` as a
signature, restated concretely: `main(["--input", "data.csv"])` is a
plain function call a test can make directly, assert a return value
from, and capture output from (via pytest's `capsys`) — none of which
is true of a `main()` that reaches into `sys.argv` itself, which would
force every test to monkey-patch global process state just to exercise
one code path.

## 63. Debugging CLI Programs

When a CLI does not behave the way you expect, work through this in
order rather than guessing:

1. **Write down the exact command** you ran, character for character —
   copy it from your shell history if possible; "roughly what I typed"
   loses exactly the detail (a missing quote, an extra space) that
   often matters.
2. **Check shell quoting** — did the shell split your input the way you
   assumed? (§58)
3. **Print/repr `sys.argv`** — add a one-line `print(repr(sys.argv))`
   (or run interactively) to see exactly what Python received, with no
   argparse interpretation applied yet.
4. **Inspect the parser definition** — re-read every relevant
   `add_argument()` call; a wrong `dest`, an unexpected default, or a
   `nargs` you forgot about is often the actual cause.
5. **Inspect the resulting `Namespace`** — `print(args)` immediately
   after `parse_args()`, before any other logic runs.
6. **Check defaults** — is the value you're seeing the *default*,
   because you didn't actually supply the flag you thought you did?
7. **Check types** — is the value the type you expect, or still a raw
   string because `type=` wasn't set where you assumed it was?
8. **Check choices** — did you actually type a valid choice, exactly
   (choices are typically case-sensitive)?
9. **Check the subcommand** — for a multi-command tool, is `args.command`
   what you expect, and did you add the argument to the *right*
   subparser rather than the top-level parser (or vice versa)?
10. **Check cross-argument validation** — is a `parser.error()` call
    (§44) firing because of some *other* argument's value, not the one
    you're focused on?
11. **Reproduce with an explicit `argv` list** — `parser.parse_args([...])`
    in a scratch script or the REPL, removing the shell entirely from
    the loop, isolates whether the bug is in argument *parsing* or
    somewhere else in the program.

## 64. Common Mistakes

- **Manually parsing `sys.argv`** for anything beyond the single
  simplest case — argparse exists precisely so you don't have to (§6).
- **Forgetting everything arrives as a string** — comparing
  `args.count == 5` when `type=` was never set will always be `False`,
  silently, because `args.count` is `"5"`.
- **Using `type=bool`** — covered in full in §65; it does not do what
  it looks like it does.
- **Assuming optional arguments are automatically required** — an
  optional argument is optional by default; `required=True` (§17) must
  be set explicitly.
- **Confusing positional and optional arguments** — forgetting the
  leading `--` turns what you meant as a named flag into a positional
  argument instead (and vice versa).
- **Too many required flags** — degrades toward the same UX problems as
  a long list of positional arguments (§17).
- **Poor help text** — `help="file"` instead of a description that
  actually says what the file is for (§23).
- **Not defining sensible defaults** where a reasonable one exists,
  forcing users to type things that could have been inferred.
- **Ambiguous short options** — reusing a short flag letter for
  different meanings across subcommands, or picking one that
  collides with a very common convention (`-v` almost always means
  "verbose" or "version" — don't repurpose it).
- **Relying on abbreviation** (§50) in scripts — an unambiguous prefix
  today can become ambiguous the moment a new option is added.
- **Mixing parsing and business logic** in one function — makes both
  harder to test and harder to reuse (§40, §60).
- **Passing raw `Namespace` objects deep into application code**
  instead of converting to a typed configuration object at the
  boundary (§60).
- **Performing all validation inside argparse** rather than layering
  simple syntactic checks in argparse and genuine business rules after
  parsing (§41–§43).
- **Reaching for a custom `Action`** when a `type=` function or
  post-parsing validation would do (§56).
- **Not testing with explicit `argv` lists** — relying on manual,
  interactive testing instead of the trivial, fast tests §61–§62 make
  possible.
- **Ignoring shell quoting** when debugging — assuming a bug is in your
  Python code when it's actually in how the shell split the command
  (§58, §63).
- **Not handling cross-argument validation at all**, leaving invalid
  combinations to fail confusingly deep inside application logic
  instead of with a clear `parser.error()` (§43–§44).
- **Building one giant monolithic `main()`** that parses, validates,
  and executes everything inline, instead of the layered
  parse → validate → dispatch → domain-logic shape (§40, §66).

## 65. The `type=bool` Trap

This deserves its own section because it is one of the most common —
and most surprising — argparse mistakes, and the standard library gives
no warning about it.

```python
parser.add_argument("--enabled", type=bool)
```

```bash
python app.py --enabled false
# args.enabled == True   <-- almost certainly not what you wanted
```

Why: `type=` calls `bool("false")`, and in Python, **any non-empty
string is truthy** — `bool("false")` is `True`, exactly like
`bool("true")`, `bool("no")`, or `bool("0")`. `type=bool` does not
parse "true"/"false" text at all; it just checks "is this string
non-empty," which every non-empty command-line value trivially is.

The correct approaches:

**For a simple on/off switch**, don't use `type=bool` at all — use
`action="store_true"` or `action="store_false"` (§12):

```python
parser.add_argument("--enabled", action="store_true")
```

**When you genuinely need an explicit `--flag true` / `--flag false`
syntax** (rather than presence/absence), write a real string-to-bool
parser and use it as `type=`:

```python
import argparse

def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1", "on"}:
        return True
    if normalized in {"false", "no", "0", "off"}:
        return False
    raise argparse.ArgumentTypeError(
        f"expected a boolean value (true/false), got {value!r}"
    )

parser.add_argument("--enabled", type=parse_bool, default=False)
```

```bash
python app.py --enabled false   # args.enabled == False  (correct, now)
python app.py --enabled true    # args.enabled == True
python app.py --enabled maybe   # error: expected a boolean value (true/false), got 'maybe'
```

As of Python 3.9, `argparse.BooleanOptionalAction` (§12) is often the
cleanest option of all for genuinely explicit boolean flags, since it
avoids string parsing entirely by generating `--flag`/`--no-flag` pairs.

## 66. Bad vs. Good Code

**Bad — manual `sys.argv` parsing everywhere:**
```python
import sys

args = sys.argv[1:]
verbose = "--verbose" in args
files = [a for a in args if not a.startswith("--")]
```

**Good — declarative, self-documenting, validated:**
```python
parser = argparse.ArgumentParser(description="Process one or more files.")
parser.add_argument("files", nargs="+", help="Files to process")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()
```

**Bad — parsing, validation, business logic, and output all mixed
together:**
```python
def process(argv):
    args = argv[1:]
    fmt = "json"
    for i, a in enumerate(args):
        if a == "--format":
            fmt = args[i + 1]
    if fmt not in ("json", "csv"):
        print("bad format")
        return
    # ... business logic directly inline here ...
    # ... printing results directly inline here too ...
```

**Good — parse, validate, convert to config, run domain logic, report:**
```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    return parser

def build_config(args: argparse.Namespace) -> Config:
    return Config(format=args.format)

def run(config: Config) -> int:
    ...  # domain logic only, no argparse in sight
    return 0

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return run(build_config(args))
```

The pattern in every "good" example: parsing declares *what* is valid;
a distinct validation/config step decides *what it means*; domain logic
never touches argparse at all. This separation is what makes the "good"
versions independently testable, reusable, and readable — the same
theme carried through §40, §42–§43, and §60.

## 67. End-to-End Examples

### 67.1 Beginner: CSV Summary CLI

```python
"""csv_summary.py — print row/column counts for a CSV file."""
from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Sequence
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print a quick summary of a CSV file's shape.",
    )
    parser.add_argument("input_file", type=Path, help="Path to the CSV file")
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Write the summary to this file instead of stdout",
    )
    parser.add_argument("--verbose", action="store_true", help="Print extra detail")
    return parser


def summarize(path: Path, verbose: bool) -> str:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        row_count = sum(1 for _ in reader)

    lines = [f"columns: {len(header)}", f"rows: {row_count}"]
    if verbose:
        lines.append(f"column names: {', '.join(header)}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not args.input_file.is_file():
        print(f"error: not a file: {args.input_file}", file=sys.stderr)
        return 1

    summary = summarize(args.input_file, args.verbose)

    if args.output is not None:
        args.output.write_text(summary + "\n", encoding="utf-8")
    else:
        print(summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Every part of this maps directly to earlier sections: positional input
(§10), optional `Path`-typed output (§42), a boolean flag (§12),
`main(argv) -> int` (§40), and a validation check (§41) before the
domain logic runs.

### 67.2 Intermediate: Data Converter CLI

```python
"""data_tool.py — convert between CSV and JSON.

    python data_tool.py convert --input data.csv --output result.json --format json
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections.abc import Sequence
from pathlib import Path


def existing_file(value: str) -> Path:
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"not a file: {path}")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="data_tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="Convert a file between formats")
    convert.add_argument("--input", type=existing_file, required=True)
    convert.add_argument("--output", type=Path, required=True)
    convert.add_argument("--format", choices=["json", "csv"], required=True)
    convert.set_defaults(func=handle_convert)

    return parser


def handle_convert(args: argparse.Namespace) -> int:
    with args.input.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if args.format == "json":
        args.output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    else:
        parser_error_if_empty(rows)
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


def parser_error_if_empty(rows: list[dict]) -> None:
    if not rows:
        raise SystemExit("error: input file has no rows to convert")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

This introduces subcommands (§35–§39), a custom validating type
function (§15), `choices=` (§18), and `set_defaults()`-based dispatch
(§39) — no `if/elif` chain, even with more subcommands to come.

### 67.3 Advanced: Data Pipeline CLI (architecture sketch)

A four-command pipeline tool (`ingest`, `validate`, `transform`,
`export`) puts every technique in this chapter to work together:

```python
def build_common_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    common.add_argument("--dry-run", action="store_true", help="Report actions without executing them")
    return common


def build_parser() -> argparse.ArgumentParser:
    common = build_common_parser()
    parser = argparse.ArgumentParser(
        prog="pipeline",
        parents=[common],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", parents=[common], aliases=["in"])
    ingest.add_argument("source", type=existing_file)
    ingest.set_defaults(func=handle_ingest)

    validate = subparsers.add_parser("validate", parents=[common], aliases=["val"])
    validate.add_argument("path", type=existing_file)
    validate.set_defaults(func=handle_validate)

    transform = subparsers.add_parser("transform", parents=[common])
    group = transform.add_mutually_exclusive_group(required=True)
    group.add_argument("--rule", help="Named transformation rule to apply")
    group.add_argument("--script", type=existing_file, help="Custom transform script")
    transform.set_defaults(func=handle_transform)

    export = subparsers.add_parser("export", parents=[common])
    export.add_argument("--format", choices=["json", "csv"], default="json")
    export.add_argument("--output", type=Path, required=True)
    export.set_defaults(func=handle_export)

    return parser
```

Note that `parents=[common]` is passed **both** to the top-level parser
(so `pipeline --verbose ingest ...` works) **and** to each subparser
(so `pipeline ingest --verbose ...` also works) — a deliberate design
decision about which command levels should accept shared flags, not an
argparse requirement. This sketch intentionally stops short of a full
implementation — §72's Mini-Project 4 asks you to build the rest.

## 68. Production CLI Architecture

For a CLI that will be maintained, extended, and tested over time, a
directory layout that mirrors the parse → validate → dispatch →
domain-logic pipeline (§40) pays for itself quickly:

```
src/
    app/
        cli.py            # build_parser(), main(argv) -> int
        config.py         # Config dataclass, build_config()
        commands/
            ingest.py      # handle_ingest(args) -> int
            validate.py    # handle_validate(args) -> int
            export.py      # handle_export(args) -> int
        domain/            # business logic, knows nothing about argparse
        services/          # I/O, external systems, also argparse-agnostic
```

The flow through these layers:

```
cli.py (parsing)
    ↓
config.py (validated configuration)
    ↓
commands/*.py (thin dispatch — unpack config, call domain/services)
    ↓
domain/, services/ (the actual work)
```

Why keep the CLI layer **thin**: `cli.py` and `commands/*.py` should do
almost nothing beyond parsing, validating, and calling into `domain/`
or `services/` — the actual logic (reading data, transforming it,
talking to external systems) belongs in code that has never heard of
argparse and could be called the exact same way from a test, a
different entry point, or an entirely different interface (an HTTP API,
a scheduled job) without modification. A `commands/ingest.py` handler
that is mostly `parser.add_argument()` calls and a two-line call into
`services.ingest(config)` is the goal; a handler with fifty lines of
business logic inline is a sign the separation has eroded.

## 69. API Reference

**Core parser methods**

| API | Purpose | Notes |
|---|---|---|
| `argparse.ArgumentParser(...)` | Create a parser | See §8 for constructor parameters |
| `parser.add_argument(...)` | Declare one argument | See §9 |
| `parser.parse_args(args=None, namespace=None)` | Parse and return a `Namespace`; errors exit the process | §27 |
| `parser.parse_known_args(args=None, namespace=None)` | Like `parse_args`, returns `(Namespace, list[str])`, tolerates unknown args | §28 |
| `parser.parse_intermixed_args(args=None, namespace=None)` | Allows interleaved positional/optional args; no subparser support | §29 — Python 3.7+ |
| `parser.error(message)` | Print usage + message, exit(2) | §44 |
| `parser.exit(status=0, message=None)` | Optionally print, then `sys.exit(status)` | §45 |
| `parser.print_help(file=None)` | Print full help without exiting | §46 |
| `parser.print_usage(file=None)` | Print only the usage line | §47 |

**Groups and reuse**

| API | Purpose | Notes |
|---|---|---|
| `parser.add_argument_group(title=None, description=None)` | Organize `--help` output | §33 — no validation effect |
| `parser.add_mutually_exclusive_group(required=False)` | At most (or exactly, with `required=True`) one of a set | §32 |
| `parents=[...]` (constructor param) | Copy in arguments from other parsers | §34 — parent parsers need `add_help=False` |

**Subcommands**

| API | Purpose | Notes |
|---|---|---|
| `parser.add_subparsers(dest=None, required=False, ...)` | Create a subcommand group | §35, §37 |
| `subparsers.add_parser(name, aliases=(), **kwargs)` | Define one subcommand's parser | §36, §38 |
| `parser.set_defaults(**kwargs)` | Attach fixed attributes (commonly a dispatch function) | §39 |

**Parser configuration (constructor parameters)**

| Parameter | Purpose | Section |
|---|---|---|
| `prog`, `usage`, `description`, `epilog` | Text shown in help/usage | §8, §24 |
| `formatter_class` | Help-text rendering | §26 |
| `prefix_chars` | Optional-argument prefix character(s) | §49 |
| `add_help` | Whether `-h`/`--help` is auto-added | §8 |
| `allow_abbrev` | Whether unambiguous long-option prefixes are accepted | §50 |
| `exit_on_error` | Raise `ArgumentError` instead of exiting (Python 3.9+) | §55 |
| `argument_default` | Global fallback default | §53 |
| `conflict_handler` | `"error"` (default) or `"resolve"` for option-string collisions | §54 |
| `fromfile_prefix_chars` | Enables `@file` argument expansion | §51 |

**`add_argument()` parameters**

| Parameter | Purpose | Section |
|---|---|---|
| `action` | What to do with a matched value | §13 |
| `nargs` | How many values to consume | §19 |
| `const` | Fixed value for certain action/`nargs` combos | §20 |
| `default` | Value used when absent | §16 |
| `type` | Conversion function | §14–§15 |
| `choices` | Restrict to a fixed set | §18 |
| `required` | Force an optional argument's presence | §17 |
| `help` | Help text | §23 |
| `metavar` | Value placeholder in usage/help | §21 |
| `dest` | Namespace attribute name | §22 |

**Actions**

`store`, `store_const`, `store_true`, `store_false`, `append`,
`append_const`, `count`, `extend` (Python 3.8+), `help`, `version`, and
`argparse.BooleanOptionalAction` (Python 3.9+) — all covered with
examples in §13, §12.

**Other public classes**

| Class | Purpose | Section |
|---|---|---|
| `argparse.Namespace` | The object `parse_args()` returns | §30 |
| `argparse.Action` | Base class for custom actions | §56 |
| `argparse.ArgumentError` | Raised (instead of exiting) when `exit_on_error=False` | §55 |
| `argparse.ArgumentTypeError` | Raise from a `type=` function to signal invalid input | §15 |
| `argparse.FileType` | A `type=` callable that opens a file during parsing | §70 |
| `argparse.SUPPRESS` | Sentinel: omit an attribute/help entry entirely | §16, §53 |

## 70. `argparse.FileType`

`argparse.FileType` is **deprecated since Python 3.14**; it is covered
here because you will meet it in existing code. It is a callable factory — pass an instance of it as
`type=` — that **opens a file as part of parsing**, instead of just
converting the argument to a `Path`.

```python
parser.add_argument(
    "--input",
    type=argparse.FileType("r", encoding="utf-8"),
)
```

```bash
python app.py --input data.csv
# args.input is now an already-open, readable file object
```

Parameters mirror `open()`: mode (`"r"`, `"w"`, `"rb"`, ...), `bufsize`,
`encoding`, and `errors`. The special value `"-"` is handled specially:
it maps to `sys.stdin` (in read modes) or `sys.stdout` (in write
modes) — a convenient way to support "read from stdin if no file is
given."

The tradeoff worth understanding, not just the mechanism:

- **Letting argparse open the file** means one line handles both
  parsing and file-opening, and `FileType` raises a clean argparse
  error if the file can't be opened — including for the "does not
  exist" case, at parse time.
- The cost is **resource ownership** becomes unclear: the file is
  opened during `parse_args()`, potentially long before your program
  actually needs it, and *your* code becomes responsible for closing
  it (`args.input.close()`) — easy to forget, especially if the
  program exits early via some other path. It also makes the argument
  harder to reuse for anything except "open exactly this file, exactly
  this way" (you can't easily check existence without opening, decide
  the mode dynamically, or pass the same value to two different
  functions that need it opened differently).
- **Parsing a `Path` (§42) and opening it later**, inside domain logic,
  right where it's used (ideally with a `with` block), keeps resource
  lifetime explicit and colocated with its use — the pattern this
  chapter recommends by default. Reach for `FileType` only for small
  scripts where the convenience clearly outweighs the looser resource
  ownership.

## 71. Internal Mental Model

The complete pipeline, worked through on one concrete example:

```
COMMAND
python tool.py --input data.csv --verbose

    ↓ SHELL (splits on whitespace; no quotes here to resolve)

argv (as the OS delivers it to the new process)
["tool.py", "--input", "data.csv", "--verbose"]

    ↓ ARGPARSE (matches tokens against declared arguments,
                 converts types, applies defaults)

Namespace(input="data.csv", verbose=True)

    ↓ VALIDATION (your code — existence checks, cross-argument rules)

    ↓ CONFIGURATION (typed Config object, §60)

Config(input_path=Path("data.csv"), verbose=True)

    ↓ APPLICATION LOGIC (domain/services code, argparse-agnostic)
```

Every earlier section in this chapter is, in effect, a detailed
explanation of exactly one arrow in this diagram. When something goes
wrong, §63's debugging workflow is really just "figure out which arrow
broke" — is the shell producing the tokens you expect? Is argparse
matching them the way you declared? Is the `Namespace` correct? Is
your validation logic firing when it shouldn't (or not firing when it
should)?

## 72. Performance

CLI argument parsing is, for the overwhelming majority of programs, not
a performance concern worth optimizing. A few honest notes on where
cost actually lives:

- **Parser construction** (all the `add_argument()` calls) is cheap, even
  for a parser with dozens of arguments and several subcommands. It
  happens once per process invocation.
- **Parsing itself** is proportional to the number of command-line
  tokens, which is always small (tens, not millions) — never a
  bottleneck.
- **Large argument lists** via `nargs="*"`/`"+"` (thousands of
  filenames, say) are still parsed in effectively linear time; if this
  ever becomes large enough to matter, the actual bottleneck is almost
  always what your program *does* with those thousands of values
  afterward, not the parsing step.
- **Repeated parsing** — constructing a fresh parser and calling
  `parse_args()` many times in a tight loop (e.g., inside a long-running
  service processing many command strings) is the one scenario worth a
  second thought: building the parser *once* outside the loop and
  reusing it (parsing is stateless with respect to the parser object;
  it does not need to be rebuilt per call) avoids repeated
  `add_argument()` overhead.
- **Subparser complexity** scales with the number of subcommands and
  shared arguments, but for normal CLI programs, argparse parsing is not generally a
  meaningful performance bottleneck.

The takeaway: design for clarity and correctness first (§57); do not
pre-optimize argument parsing, and treat any reported CLI slowness as
almost certainly coming from the program's actual work, not from
argparse.

## 73. CLI Security

argparse itself does not execute anything — it only turns strings into
Python values. But CLI programs are, by nature, one of the most direct
places untrusted input enters a program, and a few defensive habits
matter:

- **Treat every command-line argument as untrusted input**, exactly
  like [01-reading-and-writing-text-files.md](01-reading-and-writing-text-files.md)'s
  §3 treats file contents — even when the "user" is a trusted colleague,
  the value could still be wrong, malformed, or (in a scripted/CI
  context) generated by something else entirely.
- **Path traversal** — a `--output ../../etc/passwd`-style value is
  syntactically a perfectly valid path. If a tool must not write
  outside a specific directory, validate that explicitly (e.g. resolve
  the path and check it's relative to an expected root) rather than
  trusting any path a user supplies — see
  [02-pathlib-and-portable-paths.md](02-pathlib-and-portable-paths.md)
  for path-resolution details.
- **argparse does not execute shell commands** — parsing a string does
  not run it. The risk of shell/command injection arises entirely from
  what your program *does* with a parsed value afterward — most
  commonly, passing a CLI-supplied string into `subprocess.run(...,
  shell=True)` or building a shell command via string concatenation.
  Never do that with untrusted input; pass arguments as a list to
  `subprocess.run([...])` (no `shell=True`) so the shell is never
  involved in interpreting the value at all.
- **Command-line arguments can be visible to other users on the same
  system** — on Linux, a process's full argument list is generally
  readable by other users via `/proc/<pid>/cmdline` or tools like `ps`,
  for as long as the process runs. **Do not pass secrets — passwords,
  API keys, tokens — as plain command-line arguments** when a safer
  mechanism exists: an environment variable (still visible via
  `/proc/<pid>/environ` to sufficiently privileged users, but not to
  `ps` output by default), a file with restricted permissions, or a
  secrets manager. See
  [09-environment-configuration-and-input-validation.md](09-environment-configuration-and-input-validation.md)
  for handling secrets properly.
- **Validate before use, not just before storage** — a value that
  passed `type=` and `choices=` is syntactically fine; whether it's
  *safe* to use where it's about to be used (a file path, a database
  identifier, a URL) is a separate, deliberate check.

This section is deliberately defensive in scope — building exploits is
out of scope here; the goal is knowing what to validate and what never
to do with unvalidated CLI input.

## 74. Mini-Projects

### Mini-Project 1 — File Inspector CLI

**Problem statement:** Build `file-inspect PATH` that reports basic
information about a file or directory.

**Requirements:**
- Positional `path` argument.
- `--recursive` — if `path` is a directory, descend into subdirectories.
- `--json` — emit machine-readable JSON instead of human-readable text.
- `--verbose` — include extra detail (permissions, size in bytes).

**Expected behavior:** With no flags, print a short human-readable
summary. `--recursive` only affects directories (decide, and document,
what it does for a plain file — most sensibly, nothing extra). `--json`
and normal output should carry the same information, just formatted
differently.

**Suggested architecture:** `build_parser()` → `parse_args()` →
`inspect_path(path, recursive) -> dict` (pure, testable) →
`render(result, as_json) -> str` (also pure) → print.

**Constraints:** Standard library only (`pathlib`, `json`).

**Edge cases:** `path` does not exist; `path` is a broken symlink;
`path` is a directory with no read permission; empty directory with
`--recursive`.

**Test requirements:** cover a plain file, a directory, `--recursive`
on a nested directory, `--json` output is valid JSON, nonexistent path
produces a clean error (not a traceback).

**Extension challenge:** add `--exclude PATTERN` (repeatable, using
`action="append"`) to skip matching paths during a recursive scan.

### Mini-Project 2 — CSV Processing CLI

**Problem statement:** Build `csv-tool` with three subcommands:
`inspect`, `validate`, `transform`.

**Requirements:**
- `csv-tool inspect FILE` — print row/column counts and column names.
- `csv-tool validate FILE --schema SCHEMA_FILE` — check that every row
  matches an expected column set.
- `csv-tool transform FILE --output OUT --format {json,csv}` — convert.
- Shared `--verbose` flag across all three subcommands, via `parents=`.

**Expected behavior:** Each subcommand fails clearly (via
`parser.error()` or a validated custom type, §15/§43) on a missing or
malformed input file, without a raw traceback reaching the user.

**Suggested architecture:** One `handle_*` function per subcommand,
dispatched via `set_defaults(func=...)` (§39); a shared `existing_file`
validator (§15).

**Constraints:** Standard library only.

**Edge cases:** empty CSV (header only, zero data rows); CSV with
inconsistent column counts across rows; `--format csv` requested for
data containing a column with a comma in a value (verify your writer
quotes correctly — see
[03-csv-files.md](03-csv-files.md)).

**Test requirements:** one test per subcommand's success path, one per
subcommand's primary failure path, plus at least one cross-argument
validation test.

**Extension challenge:** add a `--dry-run` shared flag that reports
what `transform` *would* write without writing it.

### Mini-Project 3 — Data Quality CLI

**Problem statement:** Build `dq` with subcommands `check`, `report`,
`fix`, operating on a directory of CSV files.

**Requirements:**
- Shared arguments across subcommands via a parent parser: `--verbose`,
  `--config PATH`.
- A mutually exclusive group on `fix`: `--in-place` vs. `--output-dir
  DIR` (exactly one required).
- At least one custom validator beyond a basic existence check (e.g., a
  `type=` function validating a "quality threshold" is a float between
  0 and 1).
- A `Config` dataclass (§60) built from parsed args, passed into all
  domain logic — no subcommand handler should read from `args`
  directly beyond building this object.
- `main(argv: Sequence[str] | None = None) -> int`, fully testable.

**Expected behavior:** `check` reports pass/fail per file without
modifying anything; `report` aggregates results across all files in a
directory; `fix` requires exactly one of `--in-place`/`--output-dir`
and refuses to run with neither or both.

**Constraints:** Standard library only; no third-party validation
libraries — this is an argparse and design exercise, not a schema-
validation-library exercise.

**Edge cases:** directory with zero CSV files; a quality threshold of
exactly `0` or exactly `1` (boundary-valid); `fix --in-place` on a
read-only file.

**Test requirements:** full coverage of the mutually exclusive group
(neither, one, both, each individually); the custom threshold
validator tested directly *and* through the parser; at least one
`main(argv)`-level integration test per subcommand.

**Extension challenge:** add `--fail-fast` to `check`, stopping at the
first failing file instead of scanning the whole directory.

### Mini-Project 4 — Production-Style Data Pipeline CLI

**Problem statement:** Fully implement the `pipeline` sketch from
§67.3: `ingest`, `validate`, `transform`, `export`, each a real,
working subcommand.

**Requirements:**
- A parent parser shared by every subcommand (`--verbose`, `--dry-run`).
- Subcommand aliases (`in` for `ingest`, `val` for `validate`).
- Typed `Path` arguments with existence validation where inputs are
  read, and non-existence-required validation where outputs must not
  silently overwrite something (unless `--force` is passed).
- At least one custom validator with real business logic, not just an
  existence check.
- A `PipelineConfig` dataclass per subcommand, or one shared config
  with subcommand-specific optional fields.
- `set_defaults(func=...)` dispatch for every subcommand.
- Clear, non-tracebacked errors for every invalid input you can think
  of.
- A pytest suite covering every subcommand's success and failure paths,
  plus the shared parent-parser flags.
- `--help` output at both the top level and for each subcommand that
  would make sense to someone who has never seen the tool before.

**Suggested architecture:** the `src/app/...` layout from §68, with
`cli.py`, `config.py`, and one file per subcommand under `commands/`.

**Constraints:** standard library only for parsing/validation; you may
use any library you like for the actual ingest/transform/export I/O.

**Edge cases:** `transform` invoked with neither `--rule` nor
`--script` (should fail via the mutually exclusive group's
`required=True`); `export --format csv` on data with a column
structure unsuitable for flat CSV; running two subcommands' worth of
flags on one invocation (should fail — this is exactly what
subparsers, not `parse_intermixed_args()`, are for).

**Test requirements:** as described above; additionally, at least one
test asserting that `pipeline --help` and every
`pipeline <subcommand> --help` exit with status 0.

**Extension challenge:** add a fifth subcommand, `pipeline run`, that
executes `ingest`, `validate`, `transform`, and `export` in sequence by
calling their existing handler functions directly — demonstrating that
the thin-CLI-layer design (§68) makes this almost free.

## 75. Coding Exercises

**Level 1 — Foundation**

1. Print `sys.argv` from a script and run it with several different
   argument combinations; predict the output before running each one.
2. Create a parser with one required positional argument, `name`.
3. Add an optional `--greeting` argument with a default of `"Hello"`.
4. Add a `--shout` flag (`action="store_true"`) that upper-cases the
   greeting when present.
5. Add `default=` to an argument that currently has none, and verify
   the `Namespace` value when the argument is omitted.
6. Add `type=int` to a numeric argument and verify both a valid and an
   invalid input.

For each: state the example command, the expected `Namespace`, and one
edge case to check (e.g., what happens with no arguments at all).

**Level 2 — Practical**

1. Add `choices=["small", "medium", "large"]` to an existing argument;
   verify the error message for an invalid choice.
2. Add an argument with `nargs="+"` that collects one-or-more values;
   verify the "at least one required" error.
3. Write a custom validator function (using `ArgumentTypeError`) for a
   percentage value that must be between 0 and 100.
4. Add a `type=Path` argument and a follow-up check (after parsing)
   that the path exists.
5. Build a mutually exclusive group with two boolean flags; verify all
   three cases (neither, either, both).
6. Adjust `--help` output using `metavar=` so a value's purpose is
   clearer than the auto-derived name.
7. Add `action="version"` with a version string that uses `%(prog)s`.

**Level 3 — Engineering**

1. Convert a single-command parser into a two-subcommand parser using
   `add_subparsers()`, moving existing arguments into the appropriate
   subparser.
2. Add `set_defaults(func=...)` dispatch so `main()` no longer branches
   on `args.command` directly.
3. Extract shared arguments into a parent parser and reuse it across
   both subcommands.
4. Add an argument group purely for `--help` organization (no
   validation change) and confirm the help output changes as expected.
5. Add a cross-argument validation rule (§43) and a test asserting it
   raises `SystemExit`.
6. Refactor `main()` to accept `argv: Sequence[str] | None = None`, and
   write a test calling it with an explicit list.
7. Write a pytest test file covering at least five distinct scenarios
   for one of your subcommands.

**Level 4 — Advanced**

1. Use `parse_known_args()` to build a wrapper CLI that recognizes one
   flag of its own and forwards everything else (print the leftover
   list rather than acting on it).
2. Demonstrate a case where `parse_intermixed_args()` succeeds and
   plain `parse_args()` fails (or produces a different grouping) for
   the same input.
3. Add `fromfile_prefix_chars="@"` support to a parser that accepts
   many repeated `nargs="*"` values, and demonstrate `@file` expansion.
4. Write a minimal custom `argparse.Action` that records which option
   alias was used (for example `--verbose` versus `-v`, via
   `option_string`) while storing the normalized value, and explain, in
   a comment, why a `type=` function cannot do this (it never receives
   `option_string`).
5. Override `convert_arg_line_to_args()` to support multiple
   space-separated values per line in an `@file`.
6. Build a full `src/app/...`-style layout (§68) for one of the
   mini-projects, with `cli.py`, `config.py`, and `commands/`.
7. Write a `Config` dataclass and a `build_config()` function that
   converts a `Namespace` into it, with a test verifying the
   conversion for at least three different argument combinations.

For every exercise: state the exact example command you'd run, the
expected behavior, any constraints, at least one edge case, and which
concept from this chapter it exercises. Solutions are intentionally not
provided here — work through them, then check your understanding
against the relevant section.

## 76. Debugging Exercises

For each, the broken code and a description of the observed (wrong)
behavior are given; diagnose the bug using §63's workflow before
reading the corrected version.

**1. Missing required argument, unclear error**
```python
parser.add_argument("--input")
args = parser.parse_args()
print(args.input.read_text())  # AttributeError: 'NoneType' object has no attribute 'read_text'
```
*Diagnose:* `--input` was never marked `required=True`, and has no
`default=` — omitting it entirely produces `None`, not an error, and
the crash happens much later, far from the real cause.
*Fix:* add `required=True` (prevents omission) **and** `type=Path`
(converts the CLI string to a `Path`, so `.read_text()` exists on the
value): `parser.add_argument("--input", type=Path, required=True)` with
`from pathlib import Path`. `required=True` alone would still leave a
plain `str`. Alternatively, check `if args.input is None:` before use.

**2. The `type=bool` trap**
```python
parser.add_argument("--enabled", type=bool, default=False)
```
Run with `--enabled false` — `args.enabled` is `True`. *Diagnose and
fix:* see §65 in full; replace with `action="store_true"` or a real
`parse_bool` function.

**3. Wrong `nargs`**
```python
parser.add_argument("--tags", nargs="?")
args = parser.parse_args(["--tags", "a", "b"])
```
Fails unexpectedly — `nargs="?"` only accepts zero or *one* value, but
two were given. *Diagnose:* the author wanted "one or more," which is
`nargs="+"`, not `"?"`.

**4. Incorrect default type**
```python
parser.add_argument("--count", type=int, default="5")
args = parser.parse_args([])
print(args.count)
print(type(args.count))
```
```text
5
<class 'int'>
```
*Diagnose:* not a bug — the default (`"5"`) is a string, so argparse
applies `type=int` to it (§16), and the result is the int `5`; no
`TypeError` occurs. (A non-string default, e.g. `default=5`, is used
as supplied.) `default=5` is still the clearer way to write it.

**5. Invalid choices, confusing error location**
```python
parser.add_argument("--env", choices=["dev", "staging", "prod"])
args = parser.parse_args(["--env", "Prod"])
```
Fails with "invalid choice: 'Prod'" — the user assumed case
insensitivity. *Diagnose:* `choices` compares exactly, case-sensitively.
*Fix:* normalize with a `type=` function (`value.lower()`) before the
`choices` check runs, or document the exact required case.

**6. Conflicting mutually exclusive group and default**
```python
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--json", action="store_true")
group.add_argument("--csv", action="store_true", default=True)
```
The required group checks *explicit* option presence, and the truthy
default does not satisfy that requirement — so running with neither
flag still errors. However, the default creates a misleading `Namespace`
state: `--json` alone gives `json=True, csv=True`. *Diagnose:* don't
set a truthy default inside a `required=True` mutually exclusive group;
let absence-of-both correctly trigger the group's own error.

**7. Subparser dispatch failure**
```python
subparsers = parser.add_subparsers(dest="command")
ingest = subparsers.add_parser("ingest")
args = parser.parse_args(["ingest"])
args.func(args)  # AttributeError: 'Namespace' object has no attribute 'func'
```
*Diagnose:* `set_defaults(func=handle_ingest)` was never called on the
`ingest` subparser. *Fix:* add it — and note `required=True` on
`add_subparsers()` would at least guarantee a subcommand was chosen,
though it wouldn't by itself guarantee `func` was set.

**8. Wrong `dest`**
```python
parser.add_argument("--input-file")
args = parser.parse_args(["--input-file", "data.csv"])
print(args.input_file)  # this one is actually fine —
```
A variant that *is* broken:
```python
parser.add_argument("--input-file", dest="input")
print(args.input_file)  # AttributeError — dest was overridden to "input"
```
*Diagnose:* an explicit `dest=` overrides argparse's automatic
derivation; code reading the `Namespace` must match whichever name won.

**9. Broken custom validator (swallows the real error)**
```python
def positive_int(value):
    try:
        return int(value)
    except Exception:
        return 0  # silently wrong — invalid input becomes a valid-looking 0
```
*Diagnose:* catching and hiding the error defeats the entire purpose of
a validating `type=` function — invalid input should raise
`argparse.ArgumentTypeError`, not silently produce a fallback value.

**10. Path validation checked too early**
```python
parser.add_argument("--output", type=lambda v: _fail_if_exists(v))
```
where `_fail_if_exists` raises if the *output* path already exists —
but this runs during parsing, before a `--force` flag (declared later
in the same parser) has been checked. *Diagnose:* validation depending
on another argument's value cannot live inside a single argument's
`type=` function (§41) — move this check to after `parse_args()`
returns, where all values are available together (§43).

**11. Shell-quoting confusion mistaken for a parsing bug**
```bash
python app.py --name John Smith
```
`args.name` is `"John"`, and `"Smith"` ends up an unexpected extra
positional (or an error, if none was declared). *Diagnose:* this is not
an argparse bug — the shell split `John` and `Smith` into two separate
tokens because they weren't quoted. *Fix:* `--name "John Smith"`.

**12. Cross-argument validation never runs**
```python
def main(argv=None):
    args = parser.parse_args(argv)
    return 0  # validate_args(args) was written but never called
```
*Diagnose:* a validation function existing in the codebase does not
help if nothing calls it — verify, by reading `main()` line by line,
that every validation step you believe is happening is actually wired
into the execution path.

## 77. Interview Questions

**Conceptual**
- What is a CLI, and why do CLI programs remain important alongside
  GUIs and web apps?
- What is `sys.argv`, and what type are its elements?
- Why use `argparse` instead of parsing `sys.argv` by hand?
- What is the difference between a positional and an optional argument?
- What is a flag, and how does it differ from an option that takes a
  value?
- What is a `Namespace`, and how do you access a parsed value from it?
- What does `parse_args()` do, and what happens on invalid input?
- What is `type=` used for, and when does argparse call it?
- Why is `type=bool` dangerous? What should be used instead?
- What is `nargs`, and what do `"?"`, `"*"`, `"+"`, and an integer value
  each mean?
- What is `action`, and name at least four built-in actions.
- What is `choices=`, and when does argparse check it relative to
  `type=`?
- What is `required=`, and why doesn't it apply to plain positional
  arguments the same way?
- What is `default=`, and what happens if it's set to a string when
  `type=int` is also set?
- What is `metavar=` for?
- What is `dest=`, and how is it derived automatically?
- What are mutually exclusive groups, and what does `required=True`
  mean on one?
- What are subparsers, and what problem do they solve?
- What is `set_defaults()` used for in a multi-command CLI?
- What is the difference between `parse_args()` and
  `parse_known_args()`?
- What is `parse_intermixed_args()`, and what is one thing it cannot
  handle?
- What is an argument group, and how is it different from a mutually
  exclusive group?
- What is a parent parser, and why must it be created with
  `add_help=False`?
- What is `argparse.FileType`, and what's the tradeoff versus parsing a
  `Path` and opening it yourself?
- When would you write a custom `argparse.Action`, and why should it be
  rare?
- How do you validate that a path argument actually exists?
- How do you validate a rule that depends on two different arguments at
  once?
- How do you test a CLI program without running it as a real
  subprocess?
- Why design `main()` to accept an `argv` parameter?
- How would you design a production-grade multi-command CLI from
  scratch?
- How should secrets be passed to a CLI program, and why not as a plain
  argument?
- What is the difference between what the shell parses and what
  argparse parses?

**Scenario-based**
- "A user reports that `--count 5` works but `--count=5` doesn't." What
  would you check? (Both forms are supported by argparse by default;
  investigate whether a custom `type=` or `Action` is interfering, or
  whether the issue is actually shell-related.)
- "Our script worked fine for years, then broke when we added a new
  `--verify` flag — old invocations using `--verb` as shorthand for
  `--verbose` now fail." What happened, and how would you prevent this
  going forward? (§50 — `allow_abbrev` ambiguity; fix with
  `allow_abbrev=False`.)
- "We need `--output` to be required only when `--format=csv`, but
  optional otherwise." How would you implement this? (§43 —
  cross-argument validation after `parse_args()`, via `parser.error()`.)
- "A colleague wants to pass a password via `--password` on the command
  line." What would you tell them, and why? (§73 — process-list
  visibility; recommend an environment variable or secrets manager
  instead.)
- "Our subcommand dispatch is a 200-line `if/elif` chain on
  `args.command` and every new subcommand makes it worse." How would
  you refactor it? (§39 — `set_defaults(func=...)`.)

## 78. Knowledge Check

**Conceptual**
1. In your own words, explain the difference between what the shell
   does and what argparse does.
2. Why does every element of `sys.argv` start out as a string, even
   `sys.argv` entries that look numeric?

**Command interpretation**
3. Given `parser.add_argument("--tag", action="append")`, what is
   `args.tag` after `python app.py --tag a --tag b --tag c`?
4. Given `parser.add_argument("-v", action="count", default=0)`, what
   is `args.v` after `python app.py -vvv`?

**Code-reading**
5. What is wrong with
   `parser.add_argument("--enabled", type=bool, default=False)` as a
   way to accept `--enabled true`/`--enabled false` on the command
   line?
6. Given a parent parser created without `add_help=False`, what error
   occurs when it's passed via `parents=` to another parser, and why?

**Predict-the-output**
7. `parser.add_argument("--point", nargs=2, type=float)` — what is
   `args.point` after `python app.py --point 1 2`?
8. `parser.add_argument("count", nargs="?", default=10)` — what is
   `args.count` after `python app.py` with no arguments?

**Parser design**
9. You need a CLI where the user must supply exactly one of
   `--from-file` or `--from-url`. Which argparse feature expresses
   this directly?
10. You need three related subcommands sharing a `--verbose` flag.
    Name the two features you'd combine to avoid repeating that flag's
    definition three times.

**Debugging**
11. A user reports `args.tag` is `None` even though they expect a list.
    What's the likely cause, and what default would fix it?
12. `python app.py --input data.csv` produces
    `args.input == "data.csv"` even though `type=Path` was set — what
    would you check first?

**Validation**
13. Where should a rule like "`--retries` must be between 0 and 10" be
    implemented — as `choices=range(0, 11)`, a custom `type=` function,
    or post-parse validation? Justify your choice.
14. Where should a rule like "`--output` is required if `--dry-run` is
    *not* set" be implemented, and why can't `required=` alone express
    it?

**Architecture**
15. Why is passing a raw `Namespace` deep into business logic
    considered a design smell for anything beyond a small script?
16. What does `main(argv: Sequence[str] | None = None) -> int` buy you
    that a `main()` reading `sys.argv` directly does not?

**Security**
17. Why shouldn't a password be passed as a plain CLI argument, even on
    a single-user machine?
18. Does argparse itself perform any shell command execution? Where
    does actual injection risk come from instead?

**Production CLI design**
19. In a layered CLI architecture (parsing → config → domain logic),
    which layer should contain argparse-specific code, and which
    should not?
20. Name three properties of a good CLI's exit-code and output design
    that make it scriptable.

---

**Answer Key**

1. The shell splits raw typed input into tokens — handling quoting,
   globbing, variables, pipes, redirection — *before* your program
   starts; argparse then interprets that already-finished list of
   string tokens, deciding which are flags, which are positional, and
   what type/shape each should have. They never see each other's
   input.
2. Because the OS only ever passes a process a list of strings for its
   arguments — there is no separate "typed argument" channel at the
   process-creation level; any type beyond string is something Python
   (via `type=` or manual conversion) must apply afterward.
3. `["a", "b", "c"]`.
4. `3`.
5. `bool("false")` is `True` — any non-empty string is truthy in
   Python, so `type=bool` never actually parses "true"/"false" text; it
   only checks non-emptiness. Use `action="store_true"`/`"store_false"`,
   or a custom `parse_bool` function.
6. A `conflicting option string` error for `-h`/`--help`, because both
   the parent parser (which auto-adds `-h`/`--help` by default) and the
   child parser try to define the same option string.
7. `[1.0, 2.0]` (a list of two floats).
8. `10` (the default, since the positional was omitted and `nargs="?"`
   permits that).
9. `add_mutually_exclusive_group(required=True)`.
10. A parent parser (`parents=[common]`) combined with
    `add_subparsers()`/`add_parser(..., parents=[common])`.
11. The `append` action's default, if unset, is `None`, not `[]`;
    setting `default=[]` explicitly (or checking `if args.tag:` rather
    than assuming a list) fixes it.
12. Check whether `type=Path` was actually applied to *this*
    `add_argument()` call and not a different one — a `Path`-typed
    argument is a `pathlib.Path` object (its repr is platform-dependent,
    e.g. `PosixPath('data.csv')` on POSIX), not the bare string
    `'data.csv'`; if it prints as a plain string, `type=Path` isn't
    actually wired up where you think it is.
13. `choices=range(0, 11)` — it's a simple, closed, small set of valid
    integers, exactly what `choices=` is for; a custom function would
    be unnecessary complexity, and post-parse validation is
    unnecessary since the rule involves only this one argument.
14. Post-parse validation using `parser.error()` — `required=` can only
    express "always required" or "always optional," not a condition
    depending on another argument's value; that inherently needs code
    that runs after both values are known.
15. It couples business logic to argparse's dynamic, unchecked
    attribute access (no static type checking, no guaranteed
    attributes), and makes that logic harder to reuse or test from any
    entry point other than the CLI itself.
16. It lets tests call `main([...])` directly with an explicit argument
    list, asserting on the return value and captured output, with no
    subprocess and no monkey-patching of global `sys.argv` state.
17. Command-line arguments are visible to other users on the same
    system (e.g. via `/proc/<pid>/cmdline` or `ps`) for as long as the
    process runs — a password passed this way can leak to anyone who
    can inspect running processes.
18. No — argparse only converts strings to Python values; it never
    executes shell commands. Injection risk comes from what your
    program *does* afterward, most commonly passing a parsed value into
    `subprocess.run(..., shell=True)` or into a hand-built shell
    command string.
19. The parsing layer (`cli.py`, subcommand handlers built around
    `add_argument()`/`parse_args()`) should contain argparse-specific
    code; the domain/services layer should contain none of it at all,
    operating only on the validated configuration object.
20. Any three of: predictable, distinct exit codes (see
    [07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md));
    no unavoidable interactive prompts (a non-interactive escape hatch
    exists); output on stdout is stable and parseable when a
    machine-readable mode is offered, with diagnostics kept on stderr.

## 79. Production Checklist

**CLI Design**
- [ ] Commands and subcommands are predictable and consistently named.
- [ ] `--help` is informative at every level (top-level and per
      subcommand).
- [ ] `--version` is implemented via `action="version"`.
- [ ] Option names are stable — treated as a public API, not renamed
      casually.
- [ ] Defaults are sensible enough that most invocations need few or no
      flags.

**Parsing**
- [ ] Positional vs. optional arguments are chosen deliberately, not by
      habit.
- [ ] `type=` is set for every non-string argument.
- [ ] `choices=` is used for closed, small sets of valid values.
- [ ] `nargs` matches the actual cardinality the argument needs.
- [ ] No custom `Action` exists that a `type=` function or post-parse
      validation could have expressed instead.

**Validation**
- [ ] Boundary validation (ranges, existence, format) happens close to
      parsing, via `type=` functions where it's per-argument.
- [ ] Cross-argument validation happens after `parse_args()`, via
      `parser.error()`.
- [ ] Error messages state what was wrong *and* what a valid value
      looks like.
- [ ] Paths are validated (existence, and traversal/scope where
      relevant) before use.

**Architecture**
- [ ] The CLI layer is thin — parsing and dispatch only.
- [ ] Parsed arguments are converted into a typed configuration object
      before reaching domain logic.
- [ ] Domain logic has no dependency on `argparse`.
- [ ] `main(argv: Sequence[str] | None = None) -> int` is the program's
      single, testable entry point.

**Testing**
- [ ] Valid inputs are tested for every argument and subcommand.
- [ ] Invalid inputs (bad type, bad choice, missing required argument)
      are tested and assert `SystemExit`.
- [ ] Defaults are tested explicitly (argument omitted, value checked).
- [ ] Mutually exclusive groups are tested in every combination.
- [ ] Subcommand dispatch is tested, not just parsing.
- [ ] `main(argv)` has at least one end-to-end test per subcommand.

**Security**
- [ ] No secrets are ever passed as plain CLI arguments.
- [ ] Untrusted paths are validated before being read from or written
      to.
- [ ] No CLI-supplied value ever reaches `subprocess` with
      `shell=True` or hand-built shell strings.

**UX**
- [ ] `--help` output reads clearly to someone who has never seen the
      tool.
- [ ] `epilog` includes at least one realistic example invocation.
- [ ] Metavars name what kind of value is expected, not just a
      restatement of the flag.
- [ ] Errors are clear enough that a user can fix their command without
      reading source code.

## 80. Final Mastery Checklist

- [ ] I understand what a CLI is and why CLI programs remain essential.
- [ ] I understand command-line arguments, options, and flags.
- [ ] I understand `sys.argv`, including that every element is a
      string.
- [ ] I understand exactly where the shell's job ends and argparse's
      job begins.
- [ ] I can create an `ArgumentParser` and configure its constructor
      parameters deliberately.
- [ ] I can add positional arguments and explain when to prefer them.
- [ ] I can add optional arguments, with both short and long forms.
- [ ] I can create boolean flags with `store_true`/`store_false`, and
      know about `BooleanOptionalAction`.
- [ ] I understand every standard `action` and when each applies.
- [ ] I understand `type=`, including writing custom validating type
      functions with `ArgumentTypeError`.
- [ ] I understand `default=`, including its interaction with `type=`
      and `argparse.SUPPRESS`.
- [ ] I understand `required=` and why to use it sparingly.
- [ ] I understand `choices=` and when it's the right tool versus a
      custom validator.
- [ ] I understand every `nargs` value and its resulting type.
- [ ] I understand `const=` and its two main use patterns.
- [ ] I understand `metavar=` and how to choose a good one.
- [ ] I understand `dest=` and how it's derived automatically.
- [ ] I understand `help=` and what makes help text actually useful.
- [ ] I understand the formatter classes and when to use each.
- [ ] I understand `parse_args()`, including its error/exit behavior.
- [ ] I understand `parse_known_args()` and its use cases.
- [ ] I understand `parse_intermixed_args()` and its limitations.
- [ ] I understand `Namespace`, including `vars()` conversion.
- [ ] I understand mutually exclusive groups, including `required=True`.
- [ ] I understand argument groups and that they affect display only.
- [ ] I understand parent parsers and why they need `add_help=False`.
- [ ] I understand subcommands, `add_subparsers()`, and required
      subcommands.
- [ ] I understand subcommand aliases.
- [ ] I understand `set_defaults()` and dispatch-based CLI architecture.
- [ ] I can validate paths and write custom cross-argument validation.
- [ ] I understand `parser.error()`, `parser.exit()`, `print_help()`,
      and `print_usage()`.
- [ ] I can implement `--version` correctly.
- [ ] I understand `allow_abbrev` and why production CLIs often disable
      it.
- [ ] I understand `fromfile_prefix_chars` and
      `convert_arg_line_to_args()`.
- [ ] I understand `argument_default` and `conflict_handler`.
- [ ] I understand `exit_on_error` and its Python-version support.
- [ ] I know when a custom `argparse.Action` is (rarely) warranted.
- [ ] I understand `argparse.FileType` and its tradeoffs versus `Path`.
- [ ] I can test CLI programs with pytest using explicit `argv` lists.
- [ ] I can design and test a `main(argv) -> int` entry point.
- [ ] I can debug a misbehaving CLI systematically.
- [ ] I can design a production-grade, multi-command CLI with a thin
      CLI layer, a typed configuration object, and testable domain
      logic underneath it.
