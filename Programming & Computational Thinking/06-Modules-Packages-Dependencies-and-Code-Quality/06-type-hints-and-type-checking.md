# Type Hints and Type Checking

## Learning Objectives

By the end of this chapter you will be able to:

- Explain what a type is, why Python cares about types even though it
  never requires you to declare them, and why untyped code becomes
  harder to maintain as a codebase grows.
- Explain Python's actual type model precisely: dynamically typed at
  runtime, with a rich type system and optional static type checking
  layered on top — never "Python has no types."
- Write variable, function-parameter, and return-type annotations
  correctly, and explain precisely what they do and do not do at
  runtime.
- Distinguish type hints (a static, optional layer) from runtime
  validation (actual, enforced checks) — the single most important
  distinction in this entire chapter.
- Annotate collections (`list[str]`, `dict[str, int]`, `tuple[str,
  int]`, `tuple[str, ...]`, `set[str]`), and know when to prefer an
  abstract type (`Sequence`, `Mapping`, `Iterable`, `Iterator`) over a
  concrete container.
- Use `Optional`/`str | None`, `Union`/`int | str`, type aliases,
  `Literal`, `Any`, and `object` correctly, and explain the tradeoffs
  of each.
- Write generic functions and classes with `TypeVar`/`Generic` and
  modern (Python 3.12+) type-parameter syntax, including bounded and
  constrained type variables.
- Use type narrowing (`isinstance`, `is None`, `assert`, control flow)
  and explain how a static checker follows it — including
  `TypeGuard`/`TypeIs` for custom narrowing functions.
- Explain structural typing via `Protocol`, and when it's preferable
  to inheritance or an abstract base class.
- Use `TypedDict`, `dataclass`, `ClassVar`, and `Self` for typed data
  modeling.
- Explain forward references, runtime introspection of annotations
  (`__annotations__`, `inspect.get_annotations()`), and how they
  differ from static checking.
- Explain what a static type checker (mypy, Pyright/basedpyright) does,
  how it fits into a development workflow, and how it differs from
  Ruff and from testing.
- Recognize and fix the common categories of type-checking errors, with
  special attention to `None`-safety at real system boundaries (JSON,
  CLI input, environment variables, the filesystem).
- Use advanced typing features (`overload`, `cast`, `NewType`, `Final`,
  `Annotated`, `ParamSpec`, `Concatenate`) appropriately and know their
  limitations.
- Design typed module/package boundaries, and use `Protocol` for
  dependency injection and provider abstraction — including in
  AI/agentic-system contexts.
- Adopt typing gradually in a legacy codebase, and integrate type
  checking into CI alongside Ruff and tests.

## 1. Why Types Matter

Look at four ordinary assignments:

```python
age = 25
name = "Rahul"
price = 99.50
active = True
```

Each value has a **type** — a category describing what kind of data it
is and what you can do with it. `age` is an `int` (a whole number);
`name` is a `str` (text); `price` is a `float` (a decimal number);
`active` is a `bool` (`True`/`False`). **Why does data have different
types at all?** Because different kinds of data need different
operations and different storage — you can do arithmetic on `age`, you
can concatenate `name` with another string, you can't sensibly add
`True` and `"Rahul"` together and expect a meaningful result.

**Why does Python care about types**, even though — as §2 makes
precise — it never requires you to declare one? Every value in Python
*has* a type at all times, checked the moment an operation is actually
attempted:

```python
>>> "5" + 3
TypeError: can only concatenate str (not "int") to str
```

Python didn't stop you from *writing* `"5" + 3` — it only complained
the instant it actually tried to *execute* that line, at runtime.
**This is exactly the problem this whole chapter exists to address**:
Python's willingness to accept almost any code, and only fail once a
specific, incompatible operation is actually attempted, is enormously
flexible — and also means a type mismatch can hide, undetected, in a
rarely-executed branch of your code for a long time before anyone
notices.

Now look at a function with no type information at all:

```python
def add(a, b):
    return a + b
```

Reading only this signature, several real questions have no answer:
**What is `a`?** A number? A string? **What is `b`?** **What should
the function return?** **Can strings be passed?** (`add("a", "b")`
returns `"ab"` — technically "works," but is that intended?) **Can
lists be passed?** (`add([1, 2], [3, 4])` returns `[1, 2, 3, 4]` —
also "works," via list concatenation, but almost certainly not what
the function's name suggests it's for.)

**Why dynamically typed code becomes difficult to maintain**: every
one of these ambiguities is invisible in the source code itself — a
reader has to either trust a docstring (if one exists and is
accurate), trace every call site to infer intended usage, or simply
guess. **Why a large codebase needs better communication between
developers**: as a project grows past what one person can hold in
their head, a function's *signature* becomes the primary way its
intent is communicated to everyone else who calls it — and an
unannotated signature like `def add(a, b):` communicates almost
nothing. This is precisely the gap **type hints** exist to close —
not by changing what Python does at runtime, but by making a
function's *intent* explicit, checkable, and visible directly at the
call site, which §3 onward builds out in full.

## 2. Static vs. Dynamic Typing

Two genuinely different ideas, easy to conflate, that this section
keeps carefully separate.

**Dynamically typed** means a variable's type is determined by
whatever value it currently holds, checked at the moment an operation
is performed — not declared or fixed in advance. Python is
dynamically typed:

```python
x = 10          # x currently refers to an int
x = "hello"       # now x refers to a str — Python allows this without complaint
```

Nothing about this is an error. `x` never had a *declared* type
locking it to `int` forever — it's simply a name, currently bound to
whichever object it was last assigned. This is **runtime type
checking** in the sense that matters here: Python checks whether an
*operation* is valid for a value's *actual, current* type only at the
moment that operation runs (`"5" + 3` fails only when executed, not
when merely written).

**A statically typed language**, by contrast (Java, C, Go, and many
others), requires a variable's type to be declared and checked
*before* the program ever runs — an incompatible assignment is
rejected by the compiler, before execution even begins.

**The statement this section exists specifically to correct**:
**"Python has no type system" is wrong**, and this chapter will not
say it. Python has a genuinely rich **type system** — every value has
a well-defined type, and that type governs what operations are valid.
What Python does *not* have, by default, is **enforced static type
checking** — nothing built into the language itself refuses to run
code because a type mismatch exists somewhere. What Python *does*
support is **optional static type checking**, layered on top via type
hints (§3) and a separate tool (§39, a **static type checker** like
mypy or Pyright) that reads your code *without running it* and reports
type inconsistencies *before* execution.

```python
def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")
```

Run this exact code, and Python **executes it without error** —
`"hello" + "world"` is a perfectly valid string concatenation at
runtime; the annotations `a: int, b: int` change nothing about what
Python itself will accept and execute. A static type checker,
however, examining this same file **without running it**, would
report that `add("hello", "world")` doesn't match the declared
parameter types. This is the entire shape of Python's typing model,
summarized precisely, and the exact distinction §3–§4 build out next.

## 3. What Are Type Hints?

A **type hint** (also called a **type annotation**) is a piece of
syntax attached to a variable, parameter, or return value, stating
what type of value is expected there.

```python
name: str = "Alice"
age: int = 30
price: float = 10.5
active: bool = True
```

Reading `name: str = "Alice"` piece by piece: **`name`** is the
variable being defined; **`:`** introduces the annotation; **`str`**
is the annotation itself — the declared, expected type; **`=
"Alice"`** is the ordinary assignment, exactly as it would be without
any annotation at all. The annotation and the assignment are two
independent pieces of syntax that happen to sit next to each other —
you can even annotate a variable with no value yet assigned
(`name: str`, a **declaration** with no binding), though this is less
common for simple local variables than for class attributes (§35).

**What a type hint fundamentally communicates**: "the author of this
code intends this name to hold a value of this type." It is a
statement of **intent**, written directly into the source, visible to
every future reader (and, critically, to a type checker, §39) without
needing a separate comment or docstring to convey the same
information less precisely.

**Type hints generally do not, by themselves, enforce anything at
runtime** — this is stated here as a first, brief preview of §4's
entire, dedicated treatment of exactly this point, because it is
important enough to flag the moment annotations are introduced, not
only afterward.

## 4. Type Hints vs. Runtime Enforcement

This is the single most important distinction in this entire chapter,
and it deserves to be stated with complete precision before anything
else is built on top of it.

```python
age: int = "twenty"
```

**What Python itself does with this line**: nothing. It runs
successfully. `age` is now bound to the string `"twenty"`. Python does
not look at the `: int` annotation and reject the assignment, convert
`"twenty"` into a number, or raise any warning at all — **the
annotation has zero effect on what actually happens when this line
executes.**

**What a static type checker (§39) does with this same line**: it
reports an error — something like "Incompatible types in assignment
(expression has type `str`, variable has type `int`)" — **without
ever running the code at all**. The checker's entire analysis happens
by reading the source text and reasoning about it; it never executes
`age = "twenty"` to discover the mismatch.

**Four terms, precisely distinguished, since they are frequently
conflated:**

- **Type hints** — the annotation syntax itself (`age: int`); pure
  documentation-as-code, with no inherent behavior.
- **Static checking** — a separate tool (§39) reading your annotated
  code *without executing it*, reporting inconsistencies between
  declared types and actual usage.
- **Runtime validation** — actual code that runs *while your program
  executes*, checking a value and raising an exception (or converting
  it) if it doesn't meet expectations — this is ordinary Python logic,
  not related to annotations at all unless you deliberately build it
  to read them (§38 touches on this narrow exception).
- **Runtime enforcement** — the (largely absent, by default) idea that
  Python itself would refuse to run code based on a type annotation —
  **Python does not do this**, ever, on its own.

**Annotations do not automatically convert values.** `age: int =
"10"` does **not** turn `"10"` into the integer `10` — `age` is still,
at runtime, the string `"10"`, annotation notwithstanding. **Annotations
do not automatically reject invalid runtime values.** A function
annotated `def set_age(age: int) -> None:` will happily accept
`set_age("banana")` at runtime, execute its body, and only fail (if at
all) wherever `age` is later used in a way that specifically requires
integer behavior.

**Where runtime validation is appropriate**: exactly the boundary
this course's Module 1.5 already established in depth —
[09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
entire chapter on validating untrusted input (CLI arguments,
environment variables, file contents) is precisely the *runtime*
mechanism that type hints alone cannot provide. §48 returns to this
connection in full, once more typing vocabulary is in place — the
short version, worth internalizing now: **type hints describe what
your own code *assumes* is already true; runtime validation is what
actually *makes* it true at the boundary where untrusted data enters
your program.**

## 5. Basic Variable Annotations

The foundational built-in types, each annotated directly:

```python
username: str = "arjun"
retry_count: int = 3
timeout_seconds: float = 30.0
is_enabled: bool = True
payload: bytes = b"raw data"
result: None = None
```

- **`str`** — text.
- **`int`** — whole numbers.
- **`float`** — decimal numbers.
- **`bool`** — `True`/`False` (technically a subtype of `int` in
  Python, but annotated and reasoned about as its own distinct type).
- **`bytes`** — raw binary data, directly connecting to
  [05-encodings-and-newlines.md](../05-Text-Files-Structured-Data-and-CLI-Programs/05-encodings-and-newlines.md)'s
  `str`/`bytes` distinction from Module 1.5.
- **`None`** — the singleton "no value" object; as an annotation, it
  specifically means "this must be exactly `None`" (most commonly seen
  combined with another type via `| None`, §12, rather than alone).

**When annotations are useful, and when they may be unnecessary**: for
a **local variable** whose value and type are obvious from the very
next line (`count = 0`), an explicit annotation often adds little —
both a human reader and a type checker can trivially infer `int` from
the literal `0` itself (§43 covers this **type inference** directly).
Annotations earn their keep most clearly at **boundaries**: function
parameters and return values (§6–§7, where there is no adjacent
literal to infer from), **module-level variables** and **constants**
whose value might not make their intended type obvious at a glance,
and **configuration values** (directly connecting to
[09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
own configuration chapter) where stating the expected type explicitly
guards against a subtle mismatch.

```python
MAX_RETRIES: int = 5
DEFAULT_TIMEOUT: float = 30.0
```

**Constants are conventionally named in uppercase** — a naming
convention, not a typing feature — and are frequently annotated
explicitly precisely because they often appear at module level, far
from any obvious call site that would make their type self-evident.

## 6. Function Parameter Types

```python
def greet(name: str) -> str:
    return f"Hello, {name}"
```

- **`name: str`** — a **parameter annotation**, declaring that `name`
  is expected to be a `str`.
- **`-> str`** — a **return annotation**, declaring that this function
  is expected to return a `str`.
- **The `->` syntax** sits between the closing parenthesis of the
  parameter list and the function's own `:` — it is Python's dedicated
  syntax specifically for return-type annotations, used nowhere else
  in the language.

**Multiple parameters, each annotated independently:**
```python
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity
```

**An incorrect call, shown conceptually:**
```python
calculate_total("9.99", 3)
```
Python **still executes this** — `"9.99" * 3` is valid Python
(string repetition), producing `"9.999.999.99"`, a nonsensical but
non-erroring result. This is exactly §4's principle made concrete once
more, now at a function-call boundary rather than a bare assignment:
the annotation communicated intent (`price` should be a `float`); it
did not, and does not, stop this specific misuse from executing and
silently producing a wrong result — only a static checker (§39, §45)
examining this call site *before* runtime would flag the mismatch.

## 7. Return Types

```python
def log_message(message: str) -> None:
    print(message)
```

`-> None` states that this function does not meaningfully return a
value — any caller relying on its return value is, per the
annotation's own claim, doing something the function was never
designed to support.

**Why `-> None` is written as `None`, and not `-> NoneType`**: `None`
is the singleton value every "no return" function actually produces
at runtime; **`NoneType`** is the *name of the type* `None` belongs
to (`type(None)` is `NoneType`) — but Python's typing convention
specifically permits (and expects) writing the bare value `None`
directly in annotation position to mean "the type of `None`," as a
deliberate, well-established special case, rather than requiring the
more verbose, and far less commonly seen, `NoneType` spelling.

| Annotation | Meaning |
|---|---|
| `-> str` | Returns a string |
| `-> int` | Returns an integer |
| `-> float` | Returns a float |
| `-> bool` | Returns `True`/`False` |
| `-> None` | Returns no meaningful value |

**A common mistake**: omitting the return annotation entirely on a
function that *does* return a meaningful value, leaving both human
readers and a type checker to infer it from the function body alone
(§43) — usually fine for a trivial one-line function, but a real gap
in documentation and static-checking value for anything more
substantial, especially a function meant to be called from other
modules (§53–§54).

## 8. Collection Types

Modern Python (3.9+) lets you annotate built-in collections directly,
using their own names with square brackets — no separate import
needed for the container type itself:

```python
names: list[str] = ["Alice", "Bob"]
scores: dict[str, float] = {"Alice": 92.5, "Bob": 88.0}
unique_tags: set[str] = {"python", "typing"}
```

- **`list[str]`** — a list whose elements are all `str`.
- **`list[int]`** — a list whose elements are all `int`.
- **`dict[str, int]`** — a dictionary mapping `str` keys to `int`
  values.
- **`set[str]`** — a set of `str` elements.
- **`frozenset[str]`** — an immutable set of `str` elements.

**What the inner type means**: the annotation inside the brackets
describes every element (or, for `dict`, every key and every value)
the collection is expected to hold — this is what makes the
collection **homogeneous** from the type checker's point of view: a
`list[str]` is understood to contain *only* strings, and a static
checker will flag `names.append(42)` as an error against that
declared contract, even though Python itself would happily execute it
at runtime (§4's principle, once more, now applied to mutation of a
typed collection).

**Tuples and abstract sequence/mapping types** (`Sequence`, `Mapping`,
`Iterable`, `Iterator`) each deserve, and receive, their own dedicated
treatment next, in §9–§11.

## 9. Tuples

Tuple annotations have a genuinely different shape from `list`/`dict`,
because a tuple's *length* is frequently meaningful and fixed:

```python
point: tuple[float, float] = (1.5, 2.5)
record: tuple[str, int, bool] = ("Alice", 30, True)
```

**`tuple[str, int]`** describes a **fixed-length, two-element** tuple
— position 0 must be `str`, position 1 must be `int`, and nothing
else is valid. This is a **heterogeneous, fixed-shape** container
annotation, genuinely different from `list[str]`'s "any number of
elements, all the same type."

```python
scores: tuple[int, ...] = (85, 90, 78, 92)
```

**`tuple[str, ...]`** (the literal ellipsis, `...`, used here as
syntax, not as a value) means "a tuple of **any length**, where every
element is a `str`" — this is the tuple equivalent of `list[str]`'s
homogeneous-collection meaning, distinct from the fixed-length form
above.

**Fixed-length vs. variable-length, side by side:**
```python
def get_coordinates() -> tuple[float, float]:
    return (10.0, 20.0)             # exactly two floats — x and y

def get_all_scores() -> tuple[int, ...]:
    return (85, 90, 78)                # any number of ints
```
Choosing between them is a genuine modeling decision: use the
fixed-length form when a tuple's positions each have distinct,
individual meaning (a coordinate pair, a `(name, age)` record); use
the `...` form when a tuple is simply an immutable sequence of
same-typed items, with no positional meaning attached to any specific
index.

## 10. Dictionaries

```python
user_ages: dict[str, int] = {"alice": 30, "bob": 25}
user_scores: dict[str, list[int]] = {"alice": [85, 90], "bob": [78]}
```

**Nested types** compose exactly as you'd expect: `dict[str,
list[int]]` is a dictionary whose keys are strings and whose values
are each, themselves, a `list[int]` — the type checker follows this
nesting fully, understanding that `user_scores["alice"]` is a
`list[int]`, and `user_scores["alice"][0]` is an `int`.

**Why overly broad types reduce type-checking usefulness:**
```python
config: dict[str, object] = {"port": 8000, "debug": True, "name": "svc"}
```
`dict[str, object]` is technically accurate — every one of those
values genuinely *is* an `object` (everything in Python is) — but it
tells a type checker almost nothing useful: accessing
`config["port"] + 1` would still need to be treated as potentially
invalid, since `object` supports no arithmetic at all, forcing you to
narrow (§26) or cast (§73) before doing anything meaningful with the
value. A more precise type — a `TypedDict` (§33), a `dataclass` (§34),
or several individually-typed variables — almost always serves a
project's real needs better than a single, maximally-permissive `dict`
whose values could be anything.

## 11. Sequences and Abstract Types

`list[str]`, `dict[str, int]`, and similar are **concrete** container
types — specific, particular kinds of collections. Python's
`collections.abc` module (imported as, e.g., `from collections.abc
import Sequence, Mapping, Iterable, Iterator`) provides **abstract**
types describing *behavior* rather than a specific implementation.

```python
from collections.abc import Sequence

def total(values: Sequence[float]) -> float:
    return sum(values)
```

**Why a function should sometimes accept an abstraction instead of a
concrete container**: `total()` doesn't actually need a `list`
specifically — it only needs something that supports iteration and
indexing (what `Sequence` promises). Declaring the parameter as
`Sequence[float]` instead of `list[float]` means callers can pass a
`list`, a `tuple`, or any other object that genuinely behaves like a
sequence — the function's contract is exactly as permissive as its
actual implementation needs, no more and no less.

| Abstract type | What it promises |
|---|---|
| `Iterable[T]` | Can be iterated over with `for` — nothing more (no length, no indexing) |
| `Iterator[T]` | An `Iterable` that also supports `next()` — a single-pass, stateful cursor |
| `Sequence[T]` | An ordered, indexable, sized collection (supports `len()`, `[index]`, iteration) — `list` and `tuple` both satisfy this |
| `Mapping[K, V]` | A read-only key-to-value lookup (supports `[key]`, `.get()`, iteration over keys) — `dict` satisfies this |

**The engineering benefit**, stated as this section's core principle:
a function parameter's type should be **as general as the function's
actual implementation allows**, and a function's *return* type should
be **as specific as what it actually guarantees** — accepting
`Sequence[float]` but returning `list[float]` (when that's genuinely
what's produced) gives callers maximum flexibility on the way in and
maximum certainty on the way out.

## 12. Optional and `None`

A huge number of real values are **sometimes absent** — a database
lookup that might find nothing, a configuration setting with no
default, an API response field that's optional.

```python
def find_user(user_id: int) -> str | None:
    ...
```

**`str | None`** — the **modern syntax** (Python 3.10+) — means "either
a `str`, or exactly `None`." This directly uses the union operator
`|` (§13) applied specifically to `None`, and is the **preferred,
current** way to express an optional value in a codebase whose
`target-version` (per
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §20) supports it.

**The older, equivalent syntax**, worth recognizing when reading
existing code (and still entirely valid on any supported Python
version):
```python
from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    ...
```
`Optional[str]` is **exactly equivalent** to `str | None` — both mean
precisely the same thing. This chapter's own convention, and the
modern preferred choice for any project targeting Python 3.10+, is
`str | None`; `Optional[str]` is shown here specifically so you
recognize it immediately in code written before the `|` syntax
existed, or in a codebase still supporting an older Python version.

**A realistic example, worked through fully:**
```python
def find_user(user_id: int) -> str | None:
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)


user_name = find_user(3)
print(user_name.upper())   # a type checker flags this: user_name could be None
```

**How the caller must handle `None`:**
```python
user_name = find_user(3)
if user_name is not None:
    print(user_name.upper())
else:
    print("User not found")
```

This exact pattern — a function whose return type honestly admits
"or `None`," and a caller that must therefore check before using the
value — recurs constantly in real systems: **configuration** (a
setting that might not be set), **database lookups** (a record that
might not exist), and **API responses** (a field that might be
absent) all share this exact shape. §26 and §46 return to this pattern
in much greater depth, once type narrowing itself has been fully
introduced.

## 13. Union Types

A **union type** describes a value that could be *one of several*
specific types — a generalization of `Optional`'s "this, or `None`"
to "this, or that, or ... ".

```python
def normalize(value: int | str) -> str:
    return str(value)
```

**`int | str`** — the modern syntax (3.10+) — means "either an `int`
or a `str`." The older, equivalent form:
```python
from typing import Union

def normalize(value: Union[int, str]) -> str:
    return str(value)
```

**Why union types exist**: some functions genuinely, legitimately
accept more than one kind of input by design — `normalize()` above is
meant to work whether it's handed a number or already-text value, and
declaring `int | str` communicates that intentional flexibility
precisely, rather than either overclaiming a single type (which would
be inaccurate) or falling back to `Any` (§17, which would discard the
type checker's ability to verify anything about the parameter at
all).

**The problem of unions becoming too broad:**
```python
def process(value: int | str | float | bool | list | dict) -> object:
    ...
```
A union with many members, especially combined with a vague return
type like `object`, starts to communicate almost as little useful
information as `Any` would — every additional member widens what a
caller can pass and narrows what the function body (and any caller of
its result) can safely assume without further narrowing (§26). A
union that has grown this large is often a signal that a function is
trying to do too many genuinely different things at once, and might
be better split into several more narrowly-typed functions instead.

## 14. Type Aliases

A **type alias** gives an existing type a new, more meaningful name —
purely for readability; it does not create a genuinely new type.

```python
UserId = int
Coordinates = tuple[float, float]

def get_distance(a: Coordinates, b: Coordinates) -> float:
    ...
```

This simple-assignment form (`UserId = int`) is the long-standing,
universally-supported way to write a type alias — Python (and every
type checker) treats `UserId` as **exactly** the same type as `int`
from this point on; nothing distinguishes a "real" `int` from a value
merely labeled `UserId` (§74's `NewType` covers the stronger,
genuinely-distinct alternative, when that extra distinction is worth
having).

**The modern, explicit alias syntax** (Python 3.12+, via PEP 695):
```python
type UserId = int
type Coordinates = tuple[float, float]
```
The `type` statement makes the alias **explicit** in the source
itself — clearly distinguishing "this is a type alias declaration"
from an ordinary variable assignment that merely happens to hold a
type object, at a glance, without needing to infer intent from
context. On Python versions before 3.12, the plain-assignment form
(`UserId = int`) remains the correct, portable choice; a
`TypeAlias`-annotated form (`UserId: TypeAlias = int`, using
`typing.TypeAlias`, available from 3.10) is also available as an
explicit-but-portable middle ground for projects that need to support
3.10 or 3.11.

**Readability, reuse, and domain modeling**: `Coordinates` communicates
intent far more clearly than a bare `tuple[float, float]` repeated at
every call site — a reader immediately understands "this represents a
coordinate pair," and if the underlying representation ever needs to
change (say, to a three-element tuple for a `z` coordinate), the alias
provides exactly one place to update, rather than every individual
annotation across the codebase. §32 develops this domain-modeling use
case further, once `NewType` (§74) provides the stronger companion
tool for when a plain alias isn't quite enough.

## 15. Literal Types

`Literal` (from `typing`) restricts a value to one of a **specific,
finite set of exact values** — not just a type, but the *particular*
values allowed.

```python
from typing import Literal

Mode = Literal["development", "production"]

def configure(mode: Mode) -> None:
    ...
```

`Mode` is not "any string" — it is **exactly** `"development"` or
**exactly** `"production"`, and nothing else. A static checker will
flag `configure("prod")` as invalid, since `"prod"` isn't one of the
two specific, literal strings declared.

**Why `Literal` is useful, with realistic examples:**
```python
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]
Status = Literal["pending", "active", "completed", "failed"]
```
**Configuration** (a settings value with a known, small set of valid
options — directly extending
[09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
own `validate_environment()` example, now expressible as a static
type rather than only a runtime check), **status values**, **API
parameters** (an HTTP method that's genuinely restricted to a known
set), and any other **finite set of options** all benefit from
`Literal` precisely because it lets a type checker catch an invalid
value *before* runtime, in cases where `str` alone would accept
literally anything.

**Limitations**: `Literal` only works well for a genuinely **small,
stable** set of values known at the time the code is written — it
doesn't scale to values determined dynamically, and (unlike an `Enum`,
§16) it provides no runtime object to iterate over, compare by
identity, or attach behavior to; it is purely a *type-level*
restriction on plain values (commonly strings, but also numbers and
booleans).

## 16. Enum vs. Literal

Three ways to model "a value from a small, known set," compared
directly rather than ranked:

```python
# Literal
Mode = Literal["development", "production"]

# Enum
from enum import Enum

class Mode(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

# plain string constants
DEVELOPMENT = "development"
PRODUCTION = "production"
```

**`Literal`** restricts a plain `str` (or other primitive) to specific
values, purely at the type-check level — at runtime, a `Mode` value
is still just an ordinary string, with no special object, no
namespace, and no protection against a typo like `"developement"`
being caught anywhere *except* by a type checker that happens to be
run.

**`Enum`** creates a genuine runtime type — `Mode.DEVELOPMENT` is a
real object, distinct from the bare string `"development"`, providing
namespacing (`Mode.DEVELOPMENT`, not a bare, collision-prone
constant), iteration (`for m in Mode:`), and — critically — a runtime
guarantee: it is *impossible* to construct an invalid `Mode` value at
all (`Mode("staging")` raises `ValueError` immediately), independent
of whether a type checker was ever run.

**Plain string constants** offer the least structure of the three —
easy to write, but providing neither `Literal`'s static-only
restriction nor `Enum`'s runtime guarantee; a typo in a bare string
constant's *value* is caught by nothing at all.

**When each is appropriate, without one universal answer**: `Literal`
is a lightweight, zero-runtime-cost choice when a value is genuinely
"just a string, but restricted" (an API's own on-the-wire format,
where you specifically want it to remain a plain string, not an
`Enum` instance, for compatibility with something like JSON
serialization). `Enum` is the stronger choice when the value has real
runtime significance — needs comparison, iteration, or behavior of
its own, or when you want the *impossible-to-construct-a-bad-value*
guarantee independent of static checking. Plain constants are
reasonable only for the simplest, lowest-stakes cases where neither
of the above provides meaningfully more value than the added
structure costs. A production system frequently uses `Enum` for
internal domain concepts and `Literal` at the specific boundary where
values are serialized to/from an external format like JSON.

## 17. `Any`

```python
from typing import Any

value: Any = fetch_from_somewhere()
```

**What `Any` means**: "this could be anything — turn off type
checking for this value entirely." A static checker allows *any*
operation on an `Any`-typed value, and allows an `Any`-typed value to
be assigned to (or passed as) *any* other type, with no complaint at
all — `Any` is deliberately, completely permissive.

**Why it exists**: sometimes a value's type genuinely cannot be known
or expressed precisely — data from a source with no available type
information (§55, §58 cover exactly this for untyped third-party
libraries), or a deliberately dynamic, generic piece of code (a
logging helper that accepts literally anything to print). `Any` is
the escape hatch that lets typed and untyped code coexist, rather than
requiring every single value in a codebase to have a precise,
provable type before any of it can be type-checked at all — this
coexistence is called **gradual typing**, and is one of Python's
typing system's central design principles (§80 develops this in
full).

**Why excessive `Any` is dangerous**: every `Any` is a place where the
type checker's guarantees simply stop — and `Any` is **contagious**:
```python
def parse(data: Any) -> Any:
    return data["result"]["items"][0]

items = parse(raw_response)
items.nonexistent_method()   # NOT flagged — items is Any, so anything goes
```
Once a value is `Any`, everything derived from it (`data["result"]`,
`items[0]`, and so on) is *also* `Any`, silently, propagating the loss
of static guarantees outward through however much code touches that
value — a single careless `Any` at one boundary can quietly disable
type checking across a much larger portion of a codebase than it
first appears to.

**The engineering principle**: **use precise types where possible; use
`Any` deliberately, narrowly, and only when genuinely necessary** —
never as a default reflex to silence a type checker you don't want to
listen to right now (§73's `cast()` section, and §86's mistakes
section, both return to this exact temptation directly).

## 18. `object` vs. `Any`

```python
def log_anything(value: object) -> None:
    print(str(value))

def log_anything_unsafe(value: Any) -> None:
    print(value.nonexistent_attribute)   # Any: not flagged. object: WOULD be flagged.
```

**`object`** is the actual **base type** every single Python value
genuinely is an instance of — `object` is a real, specific type, at
the very top of Python's class hierarchy. **`Any`** is not a type in
this sense at all — it's a special marker telling the type checker
"stop checking this."

**How they differ, concretely**: with a value typed `object`, a
static checker knows *only* what `object` itself actually guarantees
(very little — essentially just that it exists, can be printed,
compared for identity, and so on) — and will flag `value.
nonexistent_attribute` as an error, since `object` genuinely has no
such attribute. With a value typed `Any`, the checker enforces
*nothing at all* — `value.nonexistent_attribute` passes silently, no
matter how obviously wrong it is, because `Any` opts the value fully
out of checking.

**Why `object` is often safer when the exact type is unknown**:
`object` still gives you the type checker's full protection — you
simply cannot do anything type-*specific* with the value until you
narrow it (§26) to something more concrete (via `isinstance`, for
instance). This forces exactly the right discipline: "I don't yet know
what this is specifically, so let me check before I use it" — whereas
`Any` invites skipping that check entirely, with no complaint from the
tooling that's supposed to catch exactly this kind of mistake.

```python
def describe(value: object) -> str:
    if isinstance(value, int):
        return f"an integer: {value}"
    if isinstance(value, str):
        return f"a string: {value}"
    return f"something else: {value!r}"
```
This function accepts genuinely anything (`object` is as permissive an
*input* type as `Any` would be) — but inside the function, every
narrowed branch is fully, precisely type-checked, unlike the
equivalent `Any`-typed version would be.

## 19. `Never`

```python
from typing import Never

def fail(message: str) -> Never:
    raise RuntimeError(message)
```

**`Never`** (Python 3.11+; the older, still-valid equivalent is
`typing.NoReturn`, available since 3.6.2/3.5.3) annotates a function
that **never returns normally at all** — every possible execution path
either raises an exception or loops forever; there is no value it
ever hands back to its caller.

**Functions that always raise**: `fail()` above is the clearest case —
calling it always ends in an exception, never a return.
**Exhaustive checks**, a more advanced but genuinely useful pattern:
```python
def handle_mode(mode: Mode) -> str:
    match mode:
        case Mode.DEVELOPMENT:
            return "dev config"
        case Mode.PRODUCTION:
            return "prod config"
        case _:
            assert_never(mode)   # conceptually: if Mode ever gains a new member, this becomes a type error
```
Here, a helper (`typing.assert_never`, or a hand-written equivalent
typed to accept `Never`) documents "every possible case has already
been handled above — if this line is ever actually reached, something
is wrong" — and, more usefully, if `Mode` later gains a new member
that isn't handled by any `case` above, a static checker will flag the
now-reachable `assert_never(mode)` call, since `mode`'s narrowed type
at that point would no longer actually be `Never`. This is a
genuinely useful way to get compile-time-style protection against
forgetting to update a branch when an enum or literal set grows —
introduced here only at the conceptual level this chapter needs,
without further elaboration.

## 20. `Callable`

Functions themselves are ordinary values in Python — they can be
passed as arguments, stored in variables, and returned from other
functions — and `Callable` (from `collections.abc`, or `typing`) is
how you annotate exactly that.

```python
from collections.abc import Callable

def apply_operation(
    operation: Callable[[int, int], int],
    a: int,
    b: int,
) -> int:
    return operation(a, b)


def add(x: int, y: int) -> int:
    return x + y


result = apply_operation(add, 3, 4)   # 7
```

**Reading `Callable[[int, int], int]`**: the first part,
`[int, int]`, is the list of **parameter types** the callable must
accept, in order; the second part, `int`, is the **return type** it
must produce. `Callable[[int, int], int]` therefore means "a function
(or anything else callable) that takes two `int`s and returns an
`int`" — exactly matching `add`'s own actual signature above, which is
why passing `add` type-checks cleanly.

**Connecting this to real patterns**: **callbacks** (a function passed
in to be invoked later, at some specific point — an event handler, a
completion hook); **dependency injection** (passing in *which*
implementation of some behavior to use, typed by its call signature
rather than by a specific class — closely related to `Protocol`, §29,
which frequently supersedes a bare `Callable` when more than one
method needs to be described together); and **higher-order functions**
(functions that accept or return other functions, exactly as
`apply_operation` does above) all rely on `Callable` to make a
function-shaped parameter's expected signature explicit and
checkable, rather than left entirely to a docstring or convention.

## 21. Type Variables

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]
```

**The problem `TypeVar` solves**: `first()` needs to work for a
`list[int]` *and* return an `int`, and for a `list[str]` *and* return
a `str` — one single function, whose return type genuinely *depends*
on which specific list it was called with. Annotating the return type
as `int` would be wrong for `first(["a", "b"])`; annotating it `Any`
(§17) would technically "work" but would discard exactly the
information a caller most wants: "whatever type went in, the same type
comes back out."

```python
numbers: list[int] = [1, 2, 3]
first_number = first(numbers)      # inferred as int

words: list[str] = ["a", "b"]
first_word = first(words)            # inferred as str
```

`T` is a **type variable** — a placeholder standing for "whatever
specific type is actually used at this particular call." A static
checker resolves `T` independently for each call site: when `first()`
is called with a `list[int]`, `T` is understood to be `int` for that
call, and the return type is inferred as `int` accordingly; called
with a `list[str]`, `T` becomes `str` for that call instead.

**Why this is better than `Any`**: `def first(items: list[Any]) ->
Any:` would accept the exact same calls, but would tell a type
checker *nothing* about the relationship between the input and the
output — `first_number` would be typed `Any`, discarding the fact
that it's specifically an `int`, and losing every downstream benefit
(autocomplete, further checking) that specific type would have
provided. `TypeVar` preserves the actual, meaningful relationship —
"the return type is exactly whatever the list's element type was" —
precisely, for every individual call.

## 22. Generics

A **generic** function or class is one written to work with *any*
type, parameterized by a type variable, exactly as `first()` in §21
already demonstrated for a function.

**Generic classes** extend the same idea to a whole class, not just
one function:
```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:
        return self.item


int_box: Box[int] = Box(42)
str_box: Box[str] = Box("hello")
```

`Box(Generic[T])` declares that `Box` is parameterized by a type `T`
— `Box[int]` is "a `Box` specifically holding an `int`"; `Box[str]`
is "a `Box` specifically holding a `str`." Every method that mentions
`T` (here, `get()`'s return type) is understood, for any *specific*
instantiation like `Box[int]`, to use that specific type consistently
— `int_box.get()` is known to return `int`, and `str_box.get()` is
known to return `str`, from the exact same class definition.

**Generic containers**, the most common real-world use, are exactly
what `list[T]`, `dict[K, V]`, and every other built-in collection
annotation (§8–§10) already are, under the hood — `list` is itself a
generic class, parameterized by its element type, which is precisely
why `list[str]` and `list[int]` are both valid, distinct
specializations of the same one underlying `list` implementation.

**Start with simple examples before advanced ones**: a single-type-
parameter generic function (`first()`, §21) or a single-type-parameter
generic class (`Box`, above) covers the overwhelming majority of real,
everyday generic code — multi-parameter generics (`dict[K, V]`'s own
two-parameter shape, or a custom class needing more than one type
variable) follow the exact same principles, simply with more than one
`TypeVar` declared and used consistently throughout the class.

## 23. Modern Type Parameter Syntax

Python 3.12 (via PEP 695) introduced a more concise, built-in syntax
for declaring type parameters directly, without a separate `TypeVar`
assignment:

```python
def first[T](items: list[T]) -> T:
    return items[0]


class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:
        return self.item
```

**`def first[T](...)`** declares `T` as a type parameter directly in
the function's own signature — `[T]` immediately after the function
name — rather than requiring a module-level `T = TypeVar("T")`
declared separately beforehand. **`class Box[T]:`** does the same for
a class, directly replacing the `Generic[T]` base-class pattern from
§22 with equivalent, more concise syntax.

**This syntax requires Python 3.12 or newer.** For a project whose
`target-version` (per
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §20) is 3.12+, this modern form is the preferred, current choice
— consistent with this module's own established `py312` baseline. For
a project that must support an **older** Python version, the
`TypeVar`/`Generic[T]` form from §21–§22 remains the correct, portable
choice, and is not obsolete — it is simply the form required on
versions before 3.12, and continues to work correctly on 3.12+ as
well. **If your project's own `requires-python` supports a Python
version older than 3.12, do not use the `[T]` bracket syntax** — it
will fail with a syntax error on those older interpreters; always
match your typing syntax choice to your project's actual, declared
minimum supported version, exactly the same discipline
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
§20–§21 already established for Ruff's own modernization rules.

## 24. Bounded Type Variables

```python
from typing import TypeVar

class Comparable:
    def __lt__(self, other: object) -> bool: ...

TComparable = TypeVar("TComparable", bound=Comparable)

def smallest(items: list[TComparable]) -> TComparable:
    return min(items)
```
Or, using modern syntax (3.12+):
```python
def smallest[T: Comparable](items: list[T]) -> T:
    return min(items)
```

**A bound** restricts a type variable to "any type, *as long as it's a
subtype of* this specific type" — `T: Comparable` (or, in the older
form, `bound=Comparable`) means `T` can be `Comparable` itself, or any
class that inherits from it, but nothing unrelated.

**When a bound is useful**: exactly here — `smallest()`'s
implementation genuinely needs to call `<` on the items it's given
(via `min()`), so it needs *some* guarantee that whatever type `T`
ends up being actually supports that operation. An unbounded `T` (as
in §21's `first()`) makes no such assumption at all, since `first()`
never actually operates *on* the elements beyond returning one — a
bounded `T` is the right tool specifically when the generic function's
own body genuinely depends on the type parameter supporting some
particular capability.

## 25. Constrained Type Variables

```python
from typing import TypeVar

TNumber = TypeVar("TNumber", int, float)

def double(value: TNumber) -> TNumber:
    return value * 2
```

**A constraint** restricts a type variable to one of an **explicit,
closed list** of specific types — `int` or `float`, in this example,
and *nothing else at all*, not even a subclass of either.

**Bound vs. constraint, the difference stated precisely**: a
**bound** (§24) says "this type, or anything that inherits from it" —
open-ended, permitting any subtype. A **constraint** says "exactly one
of these specific types, from this closed list" — no subtyping
relationship is implied or accepted; a type must be *literally one of*
the listed alternatives (`int` or `float` here) to satisfy it, not
merely compatible with one of them in some looser sense.

```python
double(5)        # OK — int is one of the constrained alternatives
double(5.0)         # OK — float is one of the constrained alternatives
double("hello")        # error — str is not int and not float
```

**When each is appropriate**: reach for a **bound** when you need "any
type sharing this one specific capability" (§24's `Comparable`
example) — genuinely open-ended, extensible to any future subtype.
Reach for a **constraint** when you have a small, specific, *closed*
set of acceptable types that don't share a convenient common base
class to bound against (`int`/`float` here have no shared,
specifically-arithmetic base class worth bounding against) — this is
a narrower, less common need than a bound, and worth reaching for only
when the "closed list of exact alternatives" shape genuinely matches
your situation.

## 26. Type Narrowing

```python
def describe(value: str | int) -> str:
    if isinstance(value, str):
        return value.upper()      # here, the checker KNOWS value is str
    return str(value * 2)           # here, the checker KNOWS value is int
```

**Type narrowing** is a static type checker's ability to follow your
code's own control flow and progressively refine what it believes a
value's type is, at each specific point in the program — starting from
a broader declared type (`str | int`) and narrowing it, branch by
branch, based on runtime checks your code actually performs.

**Common narrowing mechanisms:**
- **`isinstance(value, str)`** — the most common and most reliable
  narrowing check; inside the `if` branch, the checker treats `value`
  as `str`.
- **`is None` / `is not None`** — narrows a `T | None` value to `T`
  (or confirms it's specifically `None`) within the corresponding
  branch — exactly the mechanism §12's `find_user()` example already
  relied on.
- **Truthiness**, where appropriate — `if value:` can, in some cases,
  narrow away `None` or an empty container, though this is a weaker,
  less universally-recognized signal than an explicit `is None` check,
  and worth using narrowing-for-truthiness deliberately, not by
  accident.
- **`assert`** — `assert isinstance(value, str)` narrows exactly like
  the equivalent `if` branch would, for the remainder of the code
  after the assertion.
- **General control flow** — a checker follows `if`/`elif`/`else`,
  early `return`s, and `raise` statements, understanding that code
  *after* an early return in one branch cannot still be operating
  under that branch's narrowed (or excluded) type.

**The difference between runtime behavior and static inference, stated
precisely**: `isinstance(value, str)` is an ordinary **runtime**
check — Python actually evaluates it, every time, to decide which
branch executes. The type checker's narrowing is a **separate,
static** inference process, running entirely at analysis time, that
happens to *track* the same logical structure your runtime check
creates — the checker isn't "running" your `isinstance` call; it's
reasoning, from the source code's structure alone, about what must be
true inside each branch *if* that runtime check succeeds or fails.
Both perspectives — the actual runtime check, and the checker's
static understanding of it — describe the same underlying logic, from
two genuinely different vantage points (§41 develops this dual
perspective in full).

## 27. `TypeGuard`

```python
from typing import TypeGuard

def is_str_list(items: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in items)


def process(items: list[object]) -> None:
    if is_str_list(items):
        for item in items:
            print(item.upper())   # checker now treats items as list[str]
```

**Why custom type-checking helper functions sometimes need to
communicate information to a static checker**: `isinstance()` works
directly for simple cases (§26), but it cannot express something like
"every element of this list is a `str`" in one call — that requires a
loop, which an ordinary function's return type (`bool`) gives a static
checker no special way to connect back to narrowing the *input*
parameter's type. `TypeGuard` exists precisely to bridge this gap.

**The runtime predicate vs. static narrowing, distinguished
precisely**: `is_str_list()`'s actual **runtime behavior** is an
ordinary boolean check — it really does iterate and check every
element, and returns an honest `True`/`False`. Its **return
annotation**, `TypeGuard[list[str]]`, is a *separate*, additional
promise made specifically *to the type checker*: "if this function
returns `True`, you (the checker) may narrow the argument you passed
in to `list[str]`." The checker trusts this promise — it does not
re-derive it from the function's own implementation; the burden is on
the function's author to make sure the runtime check and the
`TypeGuard` claim genuinely agree with each other.

This chapter does not go further into type-theoretic detail than this
— the practical takeaway is: when `isinstance` alone can't express a
narrowing check you need, a small helper function annotated with
`TypeGuard` lets you write that check once, reusably, while still
getting real narrowing benefit at every call site.

## 28. `TypeIs`

```python
from typing import TypeIs

def is_str(value: object) -> TypeIs[str]:
    return isinstance(value, str)
```

**`TypeIs`** (Python 3.13+) is a newer, closely related alternative to
`TypeGuard`, solving almost the same problem with one meaningful
behavioral difference: a `TypeGuard`-annotated function's `True`
result narrows the *positive* branch only, and Python's static
checkers make **no particular promise** about what happens in the
`else` branch (the argument's type is typically left unchanged, not
narrowed at all, in the `else` case). A `TypeIs`-annotated function,
by contrast, is specifically designed to narrow **both** branches
correctly — if `is_str(value)` returns `False`, a `TypeIs`-aware
checker can correctly narrow `value` to exclude `str` in the `else`
branch too, which `TypeGuard` does not guarantee.

**When it's useful**: any time you're writing a reusable, `isinstance`-
style narrowing helper (much like `is_str` above) where you want both
branches — the "yes, it's this type" branch *and* the "no, it's
excluded" branch — to narrow correctly, mirroring how a direct
`isinstance()` check already behaves.

**Clearly identifying version compatibility**: `TypeIs` requires
Python 3.13 or newer. For a project targeting an earlier Python
version — including this module's own established `py312`
baseline — `TypeGuard` (§27, available since 3.10) remains the correct,
portable choice; do not use `TypeIs` unless your project's actual,
declared minimum Python version genuinely supports it, following the
exact same version-discipline this chapter has applied consistently
since §23.

## 29. Protocols

Start from the underlying idea Python has always embraced, long
before `Protocol` existed as typing syntax: **duck typing** —
"if it walks like a duck and quacks like a duck, treat it as a duck."

```python
def read_contents(source) -> str:
    return source.read()
```

This function doesn't care whether `source` is a real file object, an
in-memory `io.StringIO`, a network socket wrapper, or anything else —
it only cares that **whatever is passed has a `.read()` method**. This
is **structural typing**: compatibility is determined by *what an
object can do* (its structure — which methods/attributes it has),
not by *what it's declared to be* (its class, or what it inherits
from).

`Protocol` (from `typing`) gives this long-standing duck-typing idea a
precise, checkable type annotation:

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...


def read_contents(source: Readable) -> str:
    return source.read()
```

`Readable` declares "anything with a `read() -> str` method" — **any**
class satisfies this protocol automatically, simply by having a
matching method, **with no inheritance from `Readable` required at
all**. A real file object, an `io.StringIO`, or a completely unrelated
custom class you write yourself all satisfy `Readable` as long as each
defines a compatible `read()` method — the type checker verifies
structural compatibility, not a declared class relationship.

**Why `Protocol` is powerful for decoupling**: it lets you write a
function's type signature in terms of *only the behavior it actually
needs*, with zero coupling to any specific class hierarchy — directly
extending §11's `Sequence`/`Mapping` abstraction principle (itself
built on exactly this same structural idea, since `collections.abc`'s
abstract types are conceptually protocols too) to your *own*,
custom-defined behaviors. §69–§70 build this into a concrete,
production-relevant pattern for swapping implementations (AI model
providers, storage backends) without the caller ever needing to know
or care about the concrete class actually being used.

## 30. Protocol vs. Inheritance

Three related but genuinely different tools for expressing "this
class provides that behavior," compared directly:

```python
# inheritance
class Animal:
    def make_sound(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def make_sound(self) -> str:
        return "Woof"


# Protocol — structural, no inheritance needed
class SoundMaker(Protocol):
    def make_sound(self) -> str: ...

class Cat:                              # note: does NOT inherit from SoundMaker at all
    def make_sound(self) -> str:
        return "Meow"

def announce(entity: SoundMaker) -> None:
    print(entity.make_sound())

announce(Dog())    # OK — Dog happens to have a compatible make_sound()
announce(Cat())      # ALSO OK — Cat satisfies SoundMaker structurally, despite no inheritance at all
```

**Nominal relationships vs. structural compatibility, precisely**:
**inheritance** creates a **nominal** relationship — `Dog` is
explicitly, by name, declared to be an `Animal`, and that declared
relationship is what a type checker (and Python's own `isinstance`)
recognizes. **`Protocol`** instead checks **structural**
compatibility — does this object *actually have* the required
methods, with compatible signatures, regardless of what it's declared
to inherit from (or not inherit from) at all. `Cat` above satisfies
`SoundMaker` purely because it happens to define a matching
`make_sound()` method — no explicit relationship to `SoundMaker` was
ever declared.

**Coupling, the central practical difference**: inheriting from a
specific base class **couples** a subclass to that base class's own
module, its own inheritance chain, and any implementation details it
carries — changing the base class can ripple outward to every
subclass. A `Protocol` couples a function only to a **behavioral
contract** — any class satisfying that contract works, including
classes that were never written with the protocol in mind at all
(e.g., a class from a third-party library you don't control, which
could never have been made to inherit from your own protocol class,
but can still satisfy it structurally).

**A realistic example**: a function needing "something that can send a
message" doesn't need to know or care whether it's handed an email
client, a Slack client, or an SMS gateway — each can independently
satisfy a `MessageSender` protocol (`def send(self, text: str) ->
None: ...`) without any of them sharing a common base class at all,
letting each be developed, tested, and swapped completely
independently.

## 31. Abstract Base Classes

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, key: str, value: str) -> None: ...

    @abstractmethod
    def load(self, key: str) -> str: ...


class InMemoryStorage(Storage):
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def save(self, key: str, value: str) -> None:
        self._data[key] = value

    def load(self, key: str) -> str:
        return self._data[key]
```

**`ABC`** (Abstract Base Class) and **`@abstractmethod`** together
define a class that **cannot be instantiated directly**, and that
*requires* any concrete subclass to actually implement every method
marked `@abstractmethod` — attempting to instantiate `Storage()`
directly, or a subclass that forgot to implement `load()`, raises a
`TypeError` **at runtime**, not just a static-checking complaint.

**When ABCs are appropriate**: when you want a **nominal**,
runtime-enforced contract — subclasses must explicitly `class
InMemoryStorage(Storage):`, and Python itself refuses to let an
incomplete implementation be instantiated at all, independent of
whether a type checker is ever run. This is a genuinely different,
stronger guarantee than `Protocol` provides.

**Compared with `Protocol`**: an ABC requires explicit inheritance
(nominal, per §30) and enforces completeness **at runtime**; a
`Protocol` requires no inheritance at all (structural) and provides
**no runtime enforcement whatsoever** by default — protocol
compatibility is checked only by a static type checker, unless you
explicitly opt a specific `Protocol` into `isinstance()`-style runtime
checking via `@runtime_checkable` (a narrower, less common need this
chapter does not develop further). Choose an ABC when you want a
real, enforced base class relationship with guaranteed
implementation-completeness; choose `Protocol` when you want maximal
decoupling and don't need (or don't want) to force an explicit
inheritance relationship at all. This chapter keeps this comparison
narrowly focused on the *typing* implications — the fuller treatment
of object-oriented design and ABCs belongs to this course's dedicated
OOP material elsewhere.

## 32. Type Aliases for Domain Models

Extending §14's type-alias introduction specifically toward making a
codebase's *domain concepts* explicit in its types:

```python
UserId = int
OrderId = int
Money = float
Coordinates = tuple[float, float]
Timestamp = float
FilePath = str
```

Each of these gives a plain, generic type (`int`, `float`, `str`,
`tuple[float, float]`) a name that communicates *what it actually
represents* in this specific domain — a function signature reading
`def get_order(order_id: OrderId, user_id: UserId) -> Order:` is far
more self-explanatory than the equivalent `def get_order(order_id:
int, user_id: int) -> Order:`, even though both are, to a type
checker, exactly identical.

**The limitation of simple aliases, stated directly**: because a
plain alias (§14) creates **no genuinely new type**, `UserId` and
`OrderId` are, to a static checker, both *exactly* `int` — nothing
prevents `get_order(order_id=some_user_id, user_id=some_order_id)`
from type-checking perfectly cleanly, despite the two arguments
almost certainly being swapped by mistake. A plain alias documents
intent for a human reader; it provides **zero** additional static
protection against this exact class of mix-up.

**When a stronger domain model is needed**: precisely when this class
of mistake (swapping two same-underlying-type-but-different-meaning
values) is a real, costly risk worth actively guarding against —
`NewType` (§74) is the next tool this chapter introduces specifically
for that stronger guarantee, once enough context exists to explain it
properly; a full custom class (or a `dataclass`, §34) is the strongest
option of all, appropriate when a domain concept genuinely needs its
own behavior, not just a distinguishable type.

## 33. TypedDict

```python
from typing import TypedDict

class User(TypedDict):
    id: int
    name: str
    email: str


def greet_user(user: User) -> str:
    return f"Hello, {user['name']}!"


alice: User = {"id": 1, "name": "Alice", "email": "alice@example.com"}
```

**The problem `TypedDict` solves**: a plain `dict[str, object]` (§10)
tells a type checker only "keys are strings, values could be
anything" — it says nothing about *which specific keys* are expected,
or what type *each individual key's* value should be. `TypedDict`
fixes exactly this: `User` declares a dictionary with **exactly**
these three keys, each with its own specific, individually-checked
type — `user["name"]` is statically known to be `str`; `user["id"]` is
statically known to be `int`.

**Required and optional keys:**
```python
class User(TypedDict):
    id: int
    name: str
    email: str

class PartialUser(TypedDict, total=False):
    id: int
    name: str
    email: str
```

By default, **every key in a `TypedDict` is required** — a value
missing any declared key is flagged by a static checker as incomplete.
**`total=False`** flips this — every key becomes **optional**, useful
when modeling a dictionary where any subset of fields might
legitimately be present (a partial update payload, for instance).

**Mixing required and optional keys precisely** (Python 3.11+, via
`Required`/`NotRequired`):
```python
from typing import NotRequired, Required

class User(TypedDict):
    id: Required[int]
    name: Required[str]
    email: NotRequired[str]
```
This states, field by field, exactly which keys are mandatory and
which are optional — finer-grained than an all-or-nothing `total=`
setting on the whole class.

**Nested `TypedDict`s:**
```python
class Address(TypedDict):
    city: str
    country: str

class UserWithAddress(TypedDict):
    id: int
    name: str
    address: Address
```

**Realistic use — API/data-processing examples**: `TypedDict` is
particularly well-suited to representing the **shape of external
data** — a JSON API response, a parsed configuration file, a database
row fetched as a dictionary — where the underlying value really is a
plain `dict` at runtime (unlike a `dataclass`, §34, which creates an
actual, different kind of object), but you still want the type
checker's full, field-by-field guarantees about its structure. §49
returns to `TypedDict`'s specific role in modeling JSON in depth.

## 34. Dataclasses and Typing

```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str


alice = User(id=1, name="Alice", email="alice@example.com")
```

Directly extending
[09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
own `AppConfig` frozen-`dataclass` pattern from Module 1.5:
**`@dataclass` provides real runtime behavior** — it automatically
generates `__init__`, `__repr__`, and `__eq__` based on the annotated
fields — **while the type annotations themselves provide the static
type information** a checker uses to verify every field's usage
throughout the rest of the codebase. This is a genuinely different
relationship between annotation and runtime than `TypedDict`'s: a
`dataclass` instance is a real, distinct **object** (`isinstance(alice,
User)` is `True`, and `alice.name` is attribute access), where a
`TypedDict`-typed value is, at runtime, just an ordinary `dict`
(`isinstance` against a `TypedDict` doesn't behave the way it does for
a real class, and access is via `user["name"]`, not `user.name`).

**Connecting this to data modeling**: a `dataclass` is generally the
better choice when you're modeling data that's created and used
**within your own Python code** (an internal domain object, exactly
like `AppConfig`) — you get real attribute access, equality
comparison, and a readable `repr` for free. `TypedDict` is generally
the better choice when you're modeling the **shape of external data**
that genuinely arrives (or must be serialized back out) as a plain
dictionary — JSON, in particular (§49) — where converting to a full
class instance may be unnecessary overhead, or where the data is
consumed directly as a `dict` by some other library or interface.

## 35. Class Attribute Types

```python
from typing import ClassVar

class User:
    role: ClassVar[str] = "user"      # shared across ALL instances
    name: str                            # per-instance — each User has its own

    def __init__(self, name: str) -> None:
        self.name = name
```

**Instance attributes** (`self.name`, declared via `name: str` at
class level and assigned in `__init__`) belong to each individual
object — every `User` instance has its own, independent `name`.
**Class attributes** — a value defined directly on the class body,
shared by every instance unless a specific instance overrides it — are
what `role: ClassVar[str] = "user"` declares.

**Why `ClassVar` exists**: without it, `role: str = "user"` written at
class level is *ambiguous* to a type checker — is this meant as a
shared class-level default, or as (incorrectly) an attempt to give
every instance its own `role`, initialized identically? `ClassVar`
removes the ambiguity explicitly: it tells the checker "this is a
class-level attribute, not a per-instance one," and (as a further,
useful consequence) the checker will flag an attempt to assign to it
*through an instance* (`some_user.role = "admin"` would be flagged,
since `role` is documented as shared, class-level state, not something
an individual instance is meant to reassign).

## 36. `Self`

```python
from typing import Self

class Builder:
    def __init__(self) -> None:
        self.name: str = ""
        self.age: int = 0

    def set_name(self, name: str) -> Self:
        self.name = name
        return self

    def set_age(self, age: int) -> Self:
        self.age = age
        return self


builder = Builder().set_name("Alice").set_age(30)
```

**`Self`** (Python 3.11+) annotates a return value as "an instance of
whatever class this method is actually being called on" — precisely
the type needed for **fluent APIs** (methods that return `self` to
allow chained calls, exactly as `set_name`/`set_age` do above).

**Why not just annotate the return type as `Builder` directly?**
Because that breaks for **subclasses**:
```python
class AdminBuilder(Builder):
    def set_permissions(self, permissions: list[str]) -> Self:
        self.permissions = permissions
        return self


admin = AdminBuilder().set_name("Alice").set_permissions(["admin"])
```
If `set_name()` were annotated `-> Builder` (instead of `-> Self`),
`AdminBuilder().set_name("Alice")` would be statically typed as a
plain `Builder`, "losing" the more specific `AdminBuilder` type — and
the subsequent `.set_permissions(...)` call (which only exists on
`AdminBuilder`, not the base `Builder`) would be incorrectly flagged
as an error, even though it's perfectly valid at runtime. `-> Self`
correctly preserves "whatever the actual, specific calling class is"
through the entire chain, subclass and all — exactly the guarantee a
fluent, chainable API needs.

## 37. Forward References

```python
class Node:
    def __init__(self, value: int, next_node: "Node | None" = None) -> None:
        self.value = value
        self.next_node = next_node
```

**The problem**: inside `Node`'s own `__init__` method, the name
`Node` doesn't fully exist yet — the class is still in the process of
being *defined* when its own method bodies are being parsed. Writing
`next_node: Node | None` directly, unquoted, would fail, since `Node`
isn't yet a resolvable name at that exact point in the file's
execution.

**The quoted-string solution** shown above — `"Node | None"` — is a
**forward reference**: a string containing what will *become* a valid
type expression once the whole module has finished being defined.
Type checkers understand this convention specifically and parse the
string as if it were ordinary annotation syntax, once the full module
context is available.

**`from __future__ import annotations`**, an alternative, module-wide
approach:
```python
from __future__ import annotations

class Node:
    def __init__(self, value: int, next_node: Node | None = None) -> None:
        self.value = value
        self.next_node = next_node
```
This import, placed at the very top of a module, makes **every**
annotation in that file automatically treated as a string at runtime
(evaluated lazily, only if something actually inspects it) — meaning
`Node | None` can be written directly, unquoted, everywhere in the
file, with no forward-reference quoting needed anywhere, including for
self-referential or otherwise not-yet-defined names.

**A note on the state of this feature, stated honestly rather than
overclaimed**: `from __future__ import annotations` has been
available since Python 3.7 and remains an explicit, opt-in import you
must add yourself — it is **not** default behavior in current Python,
despite having been proposed, at one point, as a possible future
default; do not assume it's automatically in effect. For a project
targeting Python 3.12+ (this module's own baseline), both the quoted-
string approach and the `from __future__ import annotations` approach
remain fully valid, supported options — choose whichever your project
adopts consistently, rather than mixing the two styles within one
codebase.

## 38. Annotations at Runtime

```python
def greet(name: str, age: int = 0) -> str:
    return f"Hello, {name}"

print(greet.__annotations__)
# {'name': <class 'str'>, 'age': <class 'int'>, 'return': <class 'str'>}
```

**`__annotations__`** is a real, ordinary dictionary attribute every
annotated function (and class, and module) carries at runtime, mapping
each annotated name to its annotation. This is what makes annotations
**inspectable** — not just documentation for a human or a static
checker, but a genuine, runtime-accessible piece of data about the
function's own signature.

```python
import inspect

print(inspect.get_annotations(greet))
```
`inspect.get_annotations()` is the modern, recommended way to read
annotations, handling the string-vs-object distinction that `from
__future__ import annotations` (§37) can introduce more robustly than
accessing `__annotations__` directly.

**Frameworks, validation libraries, serialization, and dependency
injection**: this runtime-inspection capability is exactly what powers
a wide category of modern Python tooling — a validation library can
read a class's annotations and automatically generate runtime checks
from them; a serialization library can read a `dataclass`'s
annotations to know how to convert it to/from JSON; a dependency-
injection framework can read a function's parameter annotations to
figure out what to automatically supply. **This is a genuinely
separate, third thing from static type checking** — worth stating
explicitly, since it's easy to conflate: a static checker (§39) never
runs your code and never touches `__annotations__` at all — it works
purely by reading source text; a framework using
`inspect.get_annotations()` operates entirely at **runtime**, on the
same annotation *information*, but through a completely different
mechanism, for a completely different purpose (building actual runtime
behavior, not analyzing code before it runs).

## 39. Type Checkers

A **static type checker** is a separate program that reads your
Python source code — **without ever executing it** — and verifies that
your type annotations are used consistently throughout: that every
function call's arguments match the declared parameter types, every
assignment matches the declared variable type, every returned value
matches the declared return type, and so on, across the entire
analyzed codebase at once.

**What it analyzes**: your source files' text and structure — parsing
them into the same kind of structural representation (an AST,
directly connecting to
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §3 explanation of how a formatter reads code) and then reasoning
about types across that structure, following assignments, function
calls, and control flow (§26's narrowing) as it goes.

**When does it run?** Entirely separately from your program's own
execution — typically invoked as its own command, on demand, or in CI
(§83) — never as part of running `python app.py` itself. **Does it
execute the program?** No — this bears repeating as plainly as
possible, since it is the single most important fact about static
type checking: a type checker **never runs your code**. It can, and
often does, report an error about a code path that would never
actually execute at runtime (an unreachable branch, or one that's
logically impossible given the actual data your program will ever see)
— its analysis is purely structural and type-based, not behavioral.

**What does it report?** **Diagnostics** — directly parallel to
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §4 definition of the term for linting — each one naming a specific
type inconsistency, its location, and an explanation.

**Common Python type-checking tools, introduced as context, not as a
tutorial for any one of them specifically**: **mypy** — the original,
long-established reference implementation of Python static type
checking, closely tied to the evolution of the typing standard
itself; **Pyright** — a fast, widely-used type checker (also powering
much of the type-checking experience inside VS Code's Python tooling,
connecting directly to
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §23 editor-integration discussion); **basedpyright** — a
community-maintained fork/distribution of Pyright with some
additional defaults and options. This chapter does not attempt to
teach the specific configuration or command-line usage of any one of
these in full — the focus throughout remains on the underlying
*concepts* of type checking, which apply regardless of which specific
tool a project chooses.

## 40. Type Checking Workflow

```
Python source code
      ↓
Type annotations                (§3–§38 — the vocabulary this chapter has built)
      ↓
Static type checker              (§39 — reads the code, never runs it)
      ↓
Type analysis                      (following assignments, calls, narrowing, §26)
      ↓
Diagnostics                          (a list of type inconsistencies found)
      ↓
Developer fixes code                   (adjusts either the code or the annotations)
      ↓
Tests / runtime verification              (§60 — a separate, complementary check)
```

Each stage feeds the next in a genuinely linear pipeline: annotations
are meaningless without a checker to read them; a checker's analysis
is meaningless without diagnostics reported back to a human; those
diagnostics are only useful if a developer actually acts on them; and
— critically, closing the loop back to §31's testing distinction from
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)
— fixing every type diagnostic still leaves **tests** (§60) as the
separate, necessary final check that the code's actual *behavior*, not
just its type consistency, is correct.

## 41. Static Checking vs. Runtime Execution

A concrete example demonstrating both perspectives on the exact same
code, side by side:

```python
def get_discount(user_type: str) -> float:
    if user_type == "premium":
        return 0.2
    elif user_type == "standard":
        return 0.1
    # no else — falls through, implicitly returning None


discount = get_discount("premium")
total_price = 100 * (1 - discount)
```

**What Python executes**: called with `"premium"`, this runs fine —
`discount` becomes `0.2`, `total_price` computes correctly. Called
with anything else (`"guest"`, a typo, an unexpected value), the
function falls through with no explicit `return`, implicitly
returning `None` — and `100 * (1 - None)` then raises `TypeError` **at
that later point**, potentially far from `get_discount()`'s own
definition, and only for the specific inputs that actually trigger it.

**What a type checker reports**, examining the same source, without
ever running it: `get_discount()` is declared `-> float`, but one
code path (falling through with no explicit `return`) actually
returns `None` — a direct, statically-detectable mismatch between the
declared return type and one of the function's own actual behaviors,
flagged **regardless of whether that specific path was ever exercised
by any test or any real call**.

**Why both perspectives matter, stated as this section's core
principle**: **static checking catches classes of problems before
execution** — including problems on code paths that might not be
exercised by *any* specific runtime call you happen to test, exactly
like the missing-`else` branch above. **Runtime tests verify actual
behavior** — confirming that, for specific, chosen inputs, the code
produces the specific, expected output; a test suite that only ever
calls `get_discount("premium")` and `get_discount("standard")` would
never actually trigger the bug above at all, even though it's real and
would eventually surface in production. Neither perspective alone is
sufficient — this is the same "layered quality assurance" principle
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
§5 and §31 already established for formatting/linting/testing, now
extended to include static type checking as its own distinct layer.

## 42. Type Checking Modes

**Permissive type checking** — a checker's default, more forgiving
mode — typically tolerates **missing annotations** (an unannotated
function or variable is simply not checked, or is treated as
implicitly `Any`, rather than flagged as an error in itself),
**implicit `Any`** (a value whose type couldn't be determined is
quietly treated as `Any`, §17, rather than raising a complaint about
the missing information itself), and generally reports only the
clearest, most confident type errors.

**Strict type checking** — a more demanding mode most checkers
support as an explicit, opt-in configuration — typically requires
every function to be annotated, flags implicit `Any` usage explicitly
(rather than silently tolerating it), and generally surfaces a much
larger set of potential issues.

**Unchecked functions and type inference**: an entirely unannotated
function is, in permissive mode, frequently left essentially unchecked
— the checker has no declared types to verify calls against, and (in
permissive mode) doesn't necessarily *require* it to have any. §43
covers **type inference** — what a checker can still figure out
*without* an explicit annotation — in full detail next.

**Why strictness may increase gradually, rather than being maximized
from day one**: directly paralleling
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §34 gradual-rule-adoption strategy for linting — a codebase with
little or no prior type-checking history will typically surface an
overwhelming number of diagnostics the moment strict mode is turned on
everywhere at once; a staged, deliberate increase in strictness (§80's
own dedicated "gradual typing" section develops this in full) is
almost always the more practical, sustainable path for a real,
existing project.

**This chapter deliberately does not present one specific checker's
exact strictness configuration as universally correct** — the right
level of strictness for any given project is a genuine, situational
engineering decision (§82 returns to this as a team-policy question),
not a single settled answer this chapter can hand you.

## 43. Type Inference

```python
count = 10
```

Even with **no explicit annotation at all**, a type checker can often
**infer** `count`'s type directly from the assigned value — here,
`int`, simply from the literal `10` on the right-hand side. This is
**type inference**: a checker deriving a type from context, rather
than requiring it to be stated explicitly every single time.

```python
name = "Alice"           # inferred: str
prices = [9.99, 19.99]      # inferred: list[float]
config = {"debug": True}       # inferred: dict[str, bool]
```

**Inferred vs. explicitly annotated types, and when explicit
annotation improves clarity**: for a simple local variable assigned
directly from an obvious literal, inference already gives a checker
everything it needs — an explicit `count: int = 10` adds little
beyond what's already self-evident. Explicit annotation earns its
value specifically where inference **cannot** reach a useful
conclusion on its own: a function's own **parameters** (there is no
"assigned value" for a parameter to infer from — only the caller
supplies one, at a completely different point in the code, §6);
**return types** (particularly for anything beyond a single trivial
expression, where stating the intended contract explicitly is more
reliable than trusting whatever the checker happens to infer from a
potentially complex function body); and any variable whose declared,
*intended* type is deliberately **broader** than what its initial
value alone would suggest:
```python
tags: list[str] = []
```
Without the explicit `list[str]` annotation, an empty list literal
(`[]`) alone gives a checker nothing to infer an element type from at
all — the explicit annotation states the *intended* future contents
directly, rather than leaving the element type effectively unresolved
or overly permissive.

## 44. `reveal_type`

```python
def get_user_id() -> int:
    return 42

user_id = get_user_id()
reveal_type(user_id)
```

**`reveal_type(...)`** is a special, checker-recognized debugging
construct — when a static checker (mypy, Pyright) analyzes a file
containing a `reveal_type(...)` call, it prints out exactly what type
it has inferred for that expression, directly in its diagnostic
output (something like `Revealed type is "builtins.int"`), *without*
that call representing a real error.

**Why developers use it**: to directly, empirically confirm what a
checker actually believes a value's type is, at a specific point in
the code — especially useful when a complex chain of inference,
narrowing (§26), or a generic function's type-variable resolution
(§21) makes the "obviously correct" answer genuinely unclear without
asking the tool directly, rather than guessing.

**An important, easy-to-miss accuracy point**: `reveal_type` is
**not** an ordinary Python builtin function you can call and expect to
work when your program actually *runs* — if `reveal_type(...)` is left
in code that's executed normally (not just statically checked),
Python itself will raise `NameError: name 'reveal_type' is not
defined`, since no such name genuinely exists at runtime; it is purely
a convention specific checkers recognize and special-case while
performing **static** analysis of your source text. Use it as a
temporary debugging aid while working with a type checker, and remove
it before running the code for real (or, in mypy specifically, an
equivalent `--reveal-type`-style workflow may exist depending on the
tool and version — verify your specific checker's own current
documentation rather than assuming identical behavior across tools).

## 45. Common Type-Checking Errors

**1. Incompatible assignment:**
```python
age: int = "twenty"
```
*Diagnostic (conceptually):* "Incompatible types in assignment
(expression has type `str`, variable has type `int`)." *Why it
matters:* the declared type and the actual assigned value disagree —
exactly §4's foundational example. *Fix:* `age: int = 20`, or
`age: str = "twenty"`, whichever actually matches intent.

**2. Wrong argument type:**
```python
def greet(name: str) -> str:
    return f"Hello, {name}"

greet(42)
```
*Diagnostic:* "Argument 1 to `greet` has incompatible type `int`;
expected `str`." *Fix:* `greet("42")` or `greet(str(42))`, depending
on what's actually intended.

**3. Wrong return type:**
```python
def get_count() -> int:
    return "5"
```
*Diagnostic:* "Incompatible return value type (got `str`, expected
`int`)." *Fix:* `return 5` (or `return int("5")` if genuinely
converting from a string source).

**4. Missing attribute:**
```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name

user = User("Alice")
print(user.email)
```
*Diagnostic:* "`User` has no attribute `email`." *Why it matters:*
this class genuinely never defined `email` — a checker catches this
statically, without needing to actually run the code and hit an
`AttributeError`. *Fix:* add the missing attribute to the class, or
correct the typo if `email` was meant to be a different, existing
attribute name.

**5. Possible `None`:**
```python
def find_user(user_id: int) -> str | None:
    ...

user = find_user(1)
print(user.upper())
```
*Diagnostic:* "Item `None` of `str | None` has no attribute `upper`."
*Fix:* narrow first — `if user is not None: print(user.upper())` —
exactly §12's and §26's established pattern (§46 is dedicated
entirely to this exact category).

**6. Incompatible container types:**
```python
def process(names: list[str]) -> None:
    ...

process([1, 2, 3])
```
*Diagnostic:* "Argument 1 to `process` has incompatible type
`list[int]`; expected `list[str]`." *Fix:* pass a genuine `list[str]`,
or correct `process`'s own signature if it was meant to accept
integers.

**7. Incorrect callable signature:**
```python
def apply(operation: Callable[[int, int], int], a: int, b: int) -> int:
    return operation(a, b)

def concatenate(x: str, y: str) -> str:
    return x + y

apply(concatenate, 1, 2)
```
*Diagnostic:* "Argument 1 to `apply` has incompatible type
`Callable[[str, str], str]`; expected `Callable[[int, int], int]`."
*Fix:* pass a callable whose own parameter and return types genuinely
match what `apply` declared it needs.

**8. Invalid dictionary access:**
```python
config: dict[str, int] = {"port": 8000}
print(config["port"].upper())
```
*Diagnostic:* "`int` has no attribute `upper`." *Fix:* the declared
value type (`int`) doesn't support `.upper()` at all — either the
dictionary's declared type is wrong, or the code calling `.upper()`
was written against a mistaken assumption about what `config["port"]`
actually holds.

**9. Unreachable branches, where appropriate:**
```python
def check(value: int) -> str:
    if isinstance(value, int):
        return "is an int"
    return "unreachable"   # a checker may flag this as unreachable, given value is already narrowed to int
```
*Why it matters:* given `value`'s declared type is already `int`, the
`isinstance(value, int)` check is always `True`, making the second
`return` provably unreachable — a signal the check itself may be
redundant, or that the function's actual intended parameter type is
broader than currently declared.

## 46. None Safety

A dedicated, practical treatment of exactly the category of error §45
item 5 introduced — arguably the single most common, and most
consequential, category of type-checking diagnostic in real Python
code.

```python
user = find_user(user_id)
```
```python
user: User | None
```

**Why this matters, across every realistic system boundary:**

- **Databases** — a lookup by ID might find no matching row at all;
  the honest return type admits `None` rather than pretending a
  result is always guaranteed.
- **APIs** — a response field might be genuinely optional or absent,
  and deserializing it should be typed to reflect that honestly.
- **Configuration** — a setting with no default might legitimately be
  unset (directly connecting to
  [09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
  own `os.getenv()` discussion, which returns `None` when a variable
  is unset).
- **Caching** — a cache lookup might miss, returning `None` rather
  than a cached value.
- **File operations** — a search through file contents might not find
  a matching line or record at all.

**Safe handling, shown for each shape this pattern commonly takes:**
```python
user = find_user(user_id)
if user is not None:
    print(user.name)
else:
    print("User not found")
```
```python
user = find_user(user_id)
if user is None:
    raise ValueError(f"No user found for id {user_id}")
print(user.name)   # checker knows user is User here — None was already excluded above
```
```python
user = find_user(user_id)
name = user.name if user is not None else "Unknown"
```

Every one of these patterns does the same fundamental thing: **check
before use**, in a form a static checker can actually follow and
narrow through (§26) — the discipline this entire section reinforces
is treating an honestly-typed `T | None` return value as a genuine
prompt to handle the absent case explicitly, every time, rather than
assuming (often incorrectly, and often only discovered in production)
that a value will "probably" be present.

## 47. Type Narrowing in Real Applications

Extending §26's mechanics into the realistic, messy shapes uncertain
input actually takes in production systems.

**API responses:**
```python
def parse_response(data: dict[str, object]) -> str:
    status = data.get("status")
    if isinstance(status, str):
        return status
    raise ValueError("Missing or invalid 'status' field")
```

**Configuration:**
```python
def get_port(raw: str | None) -> int:
    if raw is None:
        return 8000
    return int(raw)
```

**Command-line input**, connecting directly to
[06-command-line-arguments-with-argparse.md](../05-Text-Files-Structured-Data-and-CLI-Programs/06-command-line-arguments-with-argparse.md)'s
own Module 1.5 territory:
```python
def resolve_limit(cli_value: int | None) -> int:
    if cli_value is not None:
        return cli_value
    return 100
```

**JSON data:**
```python
def get_items(payload: dict[str, object]) -> list[str]:
    raw_items = payload.get("items")
    if isinstance(raw_items, list) and all(isinstance(item, str) for item in raw_items):
        return raw_items
    raise ValueError("'items' must be a list of strings")
```

**Database results:**
```python
def get_email(row: dict[str, object] | None) -> str | None:
    if row is None:
        return None
    email = row.get("email")
    return email if isinstance(email, str) else None
```

**The shared shape across every one of these examples**: each starts
from a value whose type is **genuinely uncertain** (`object`, `T |
None`, a raw external value with no inherent guarantee) and uses
narrowing (an `isinstance` check, an `is None` check, a validated
`.get()`) to **transform that uncertainty into a reliable, precisely-
typed internal value**, at the exact point where the uncertainty
actually needs to be resolved — never later, never assumed away. §48
generalizes this shared shape into this chapter's own explicit,
named pipeline.

## 48. Untrusted Data and Type Hints

**Type hints do not validate external data.** This is worth stating
with the same bluntness as §4's original, foundational warning,
because it's the single most consequential place that warning
actually matters in a real system.

```python
def process_order(data: dict[str, int]) -> int:
    return data["quantity"] * data["unit_price"]
```

Annotating `data: dict[str, int]` does **not** verify, at runtime,
that whatever is actually passed in genuinely matches that shape —
**JSON** parsed from an untrusted request, a row read from a **CSV**,
an **environment variable**, raw **user input**, or a **database
record** can all, in practice, hand your code something that doesn't
match its declared type at all — a missing key, a string where an
`int` was expected, an unexpected `None`. The annotation is a
*promise your own code makes to itself* about what it expects to
receive **once validation has already happened** — it is not, and
cannot be, the validation itself.

```
untrusted input           (JSON / CSV / env vars / user input / DB records)
        ↓
runtime validation           (§09's chapter — actual, executed checks)
        ↓
typed internal representation    (a dataclass, TypedDict, or validated primitive — NOW trustworthy)
        ↓
business logic                     (operates on the validated, typed representation, safely)
```

This is **exactly** the boundary-validation pipeline
[09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
§10 already established as this whole course's central engineering
principle — parse → validate → normalize → trusted representation →
business logic — with type hints now added as the layer that
**documents and statically enforces** the *shape of the trusted
representation*, once runtime validation has actually produced it.
Type hints and runtime validation are **complementary, not
competing**: validation makes the data trustworthy; type hints let
every subsequent line of code that touches that now-trustworthy data
be statically checked for consistency, with a checker able to assume
(correctly, because validation already ran) that the declared shape
genuinely holds.

## 49. Type Hints and JSON

```python
def get_user_email(data: dict[str, object]) -> str | None:
    ...
```

**Why `dict[str, object]` may not be enough** for complex JSON data:
real JSON documents frequently have **known, specific structure** —
particular keys, each with its own particular type, potentially
nested several levels deep — and `dict[str, object]` discards all of
that specific structure, forcing every single access to be manually
narrowed (§47) before it's useful for anything at all.

**Approaches, introduced conceptually, without a third-party-library
tutorial:**

- **`TypedDict`** (§33) — models the JSON document's *shape* directly
  as a typed dictionary, matching JSON's own natural "it's just a
  dict" runtime representation closely:
  ```python
  class UserPayload(TypedDict):
      id: int
      name: str
      email: NotRequired[str]
  ```
- **`dataclass`** (§34) — converts the raw JSON `dict` into a real,
  distinct Python object, typically via an explicit parsing function
  that reads the raw dict and constructs the dataclass field by field
  — trading a small amount of explicit conversion code for real
  attribute access and stronger guarantees afterward.
- **Validation models** — a broader category of tooling (this chapter
  does not teach any specific third-party validation library in
  depth) that combines runtime validation *and* typed output in one
  step, directly automating exactly the "validate, then produce a
  typed representation" pipeline §48 laid out manually.
- **Explicit parsing** — writing your own small, explicit function
  (following
  [09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
  §16 field-by-field JSON validation pattern) that reads a raw `dict`,
  validates each expected field, and returns a fully-typed
  `dataclass` or `TypedDict` — the most transparent, dependency-free
  option, and the one this course's own Module 1.5 material already
  demonstrated in full.

Whichever approach a project chooses, the underlying principle is
identical: **the raw, just-parsed JSON `dict` is untrusted (§48); a
deliberate step converts it into a precisely-typed, validated
representation before business logic ever touches it.**

## 50. Type Hints and CLI Programs

Directly extending
[06-command-line-arguments-with-argparse.md](../05-Text-Files-Structured-Data-and-CLI-Programs/06-command-line-arguments-with-argparse.md)'s
own Module 1.5 material with the typing layer now available:

```python
from pathlib import Path

def process_file(path: Path, limit: int | None) -> int:
    ...
```

**How CLI input begins as strings and eventually becomes typed
internal data**, restating this exact pipeline in typing-specific
terms:

```
CLI input              (sys.argv — every value is a raw str, per Module 1.5's own argparse chapter)
    ↓
parse                    (argparse's type= conversion — str → int, str → Path, etc.)
    ↓
validate                   (custom validators, §09's chapter — range checks, existence checks)
    ↓
typed representation          (an AppConfig dataclass, or individually-typed local variables)
    ↓
business logic                   (functions like process_file above, operating on trusted, typed values)
```

`process_file`'s own signature — `path: Path`, `limit: int | None` —
is only meaningful, and only trustworthy, **once** argparse's own
`type=Path` conversion and any additional validation
(`06-command-line-arguments-with-argparse.md`'s §41–§43) have already
run; the function itself never touches `sys.argv` or a raw string
directly. This is precisely why this course's own established
`build_parser()` → `parse_args()` → validate → `main()`/business-logic
architecture (from Module 1.5's argparse and configuration chapters)
already produces exactly the shape type hints document and verify —
typing adds a formal, checkable layer on top of an architecture this
course had already been teaching for entirely independent reasons.

## 51. Type Hints and Environment Variables

```python
import os

port_raw: str | None = os.getenv("PORT")
```

Directly restating
[09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
own §3 in typing terms: **every environment variable value is a
string** — `os.getenv("PORT")` is typed, correctly and precisely, as
`str | None` (a `str` if set, `None` if not) — **never** `int`, no
matter what the variable's value "looks like."

```python
def get_port(default: int = 8000) -> int:
    raw = os.getenv("PORT")
    if raw is None:
        return default
    return int(raw)
```

**Runtime conversion is required, and type hints alone cannot perform
it**: `int(raw)` is ordinary, executed Python code — it's what
actually turns the string `"8000"` into the integer `8000`; no
annotation anywhere causes this conversion to happen automatically.
If `int(raw)` fails (because `raw` holds something that isn't a valid
integer string), it raises `ValueError` **at runtime**, exactly the
failure mode
[09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
own `parse_port()` was built specifically to handle cleanly.

**The relationship between runtime validation, type hints, and static
checking, stated as this section's summary**: `get_port()`'s **type
hints** (`default: int = 8000`, `-> int`) document and statically
verify that its *interface* — what it promises to return — is always
an `int`, for any caller. Its **body** performs the actual **runtime
validation/conversion** that makes that promise true. A **static
checker** verifies the two are consistent (that every `return`
statement inside the function genuinely produces an `int`) — but it is
the runtime `int(raw)` call, not any annotation, that does the actual
work of turning an environment variable's raw string into a usable
integer.

## 52. Type Hints and File System Code

```python
from pathlib import Path

def load_config(path: Path) -> str:
    return path.read_text(encoding="utf-8")
```

**`path: Path` vs. `path: str`** — a genuinely consequential typing
decision, not merely a stylistic one: annotating a parameter as `Path`
(rather than `str`) tells both a human reader and a static checker
that this value is expected to already be a proper `pathlib.Path`
object — with all of `Path`'s own methods (`.read_text()`, `.exists()`,
`.parent`, and every other `pathlib` capability Module 1.5's
[02-pathlib-and-portable-paths.md](../05-Text-Files-Structured-Data-and-CLI-Programs/02-pathlib-and-portable-paths.md)
covered in full) available and statically verified, directly at the
call site — a bare `path: str` parameter would need to be wrapped in
`Path(path)` before any of that functionality becomes available or
checkable at all.

**Why `Path` is often the better internal representation**: it
matches exactly the "typed internal representation" stage of §48's
own untrusted-data pipeline — a raw CLI argument or config value
starts as a `str` (per §50), gets converted to a `Path` **once**, at
the boundary, and every function *deeper* in the application can then
declare `path: Path` directly, relying on that conversion having
already happened, rather than each individual function needing to
re-wrap a bare string in `Path(...)` defensively, every time, on its
own.

## 53. Type Hints and Modules

```python
# users.py
def get_user(user_id: int) -> User | None:
    ...
```
```python
# service.py
from users import get_user

user = get_user(user_id)
if user is not None:
    send_welcome_email(user)
```

**How type information communicates a contract between modules**:
`users.py`'s own `get_user()` signature is a promise, visible to
**every other module that imports it**, stating precisely what input
it needs (an `int`) and precisely what it might give back (a `User`,
or `None`) — `service.py`, reading only this signature (not
`get_user()`'s internal implementation at all), already knows it must
handle the `None` case, exactly as shown. This is annotations
functioning as **inter-module communication** — directly extending
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
own emphasis on clean, well-defined module boundaries: an import
statement declares *that* one module depends on another (per that
chapter's §26); a well-typed function signature declares *precisely
what, in terms of data*, that dependency actually consists of.

## 54. Type Hints and Packages

Directly extending
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
own §22 public-package-API discussion with typing specifically:

```python
# mypackage/__init__.py
from .processing import process_data   # process_data: (RawRecord) -> ProcessedRecord
```

**Public APIs, internal functions, package boundaries, interfaces,
contracts**: exactly as
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
§8 and §22 established naming conventions (a leading underscore) and
`__init__.py` re-exports as the mechanisms for distinguishing a
package's **public** interface from its **internal** implementation —
typing adds a *formal, checkable* dimension to that same distinction.
**Why public functions should have clearer types than internal
helpers**: a public function's signature is, in effect, a promise made
to *every consumer of the package*, potentially including code you'll
never personally read or review — an internal helper's signature is a
promise made only to the small number of other functions within the
same package that call it directly, and can be adjusted far more
freely as the package's own internals evolve, precisely because
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
own §22 principle ("internal implementation is free to change; the
public interface is not") already established that internal helpers
carry no external compatibility obligation at all.

## 55. Type Hints and Dependencies

```python
import requests   # third-party — does it ship its own type information?
```

**How third-party packages affect typing, conceptually**: when your
own code calls into a dependency (directly extending
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
§26 standard-library/local/third-party distinction), a static checker
can only verify that call *as precisely as the dependency's own
available type information allows*. A dependency's type information
can be: **fully typed** (the library ships accurate annotations
throughout, either inline or via bundled stub files, §56–§57);
**partially typed** (some functions/classes are annotated, others are
not, typically because the annotation effort is still in progress);
or **untyped** (no type information available at all) — in which case
calls into it are, from a checker's perspective, effectively `Any`
(§17), regardless of how precisely *your own* code is annotated.

**Type stubs and `py.typed`**, introduced briefly here and developed
fully in §56–§57: a dependency's type information doesn't have to live
directly in its own `.py` source files — it can instead live in
separate `.pyi` **stub files** shipped alongside the library, or the
library can simply declare (via a `py.typed` marker file) that its own
inline annotations should be trusted by checkers at all. **Third-party
stub packages** — separately published packages (conventionally named
`types-<library>`) providing type stubs for a library that doesn't
ship its own — are a further, community-maintained option worth
knowing exists, without this chapter teaching any specific one in
depth.

**What happens when a dependency has incomplete type information**:
every call into its untyped portions effectively becomes an `Any`
"hole" in your own codebase's static guarantees, precisely per §17's
"`Any` is contagious" warning — a genuinely important, practical limit
on how much static safety any one project can actually achieve,
however carefully its *own* code is typed (§58 continues this thread
directly).

## 56. Type Stubs

A **stub file** — a `.pyi` file — contains **only type information**,
no actual runtime implementation at all:

```python
# requests_client.pyi  (a stub file — conceptual illustration)
def get(url: str, timeout: float | None = None) -> Response: ...
```

**What a stub file is**: a separate file, alongside (or instead of) a
module's real `.py` implementation, containing function/class
signatures with full type annotations but **no bodies** (the `...`
ellipsis stands in for "implementation omitted — this file exists
purely to describe types"). **Why it exists**: it lets a library
provide precise, complete type information for a static checker to
consume, **without** requiring that information to be baked directly
into the library's actual source code — useful when a library's
implementation is written in a way that's hard to annotate directly
(compiled/C-extension code, for instance, which has no Python source
at all for annotations to live in), or when type information is
maintained *separately* from the implementation (as in a third-party
stub package, per §55's closing point).

**How it represents types without implementation**: a checker reading
a `.pyi` file learns everything it needs about a function's or class's
*signature* — exactly enough to verify how your own code calls it —
without ever needing (or being able) to see what that function
actually *does* internally; stub files are purely a static-analysis
artifact, never executed by Python at runtime at all.

## 57. `py.typed`

```
mypackage/
├── __init__.py
├── py.typed          ← an empty marker file
└── processing.py
```

**The purpose of `py.typed`**: a small, typically **empty** marker
file placed directly inside a package's own directory, whose sole
purpose is to declare "this package's own inline type annotations are
complete and accurate enough to be trusted by a static type checker."

**Why library authors include it**: without a `py.typed` marker,
static checkers conventionally assume a third-party package's own type
information (even if the source code *does* have annotations sprinkled
throughout) is **not** reliable enough to be checked against by
default, and treat imports from it as effectively `Any` (§17) unless
explicitly told otherwise. Adding `py.typed` is a library author's
explicit, deliberate promise: "you can trust my annotations — check
your calls into my library against them."

**Connecting this to distributing typed Python packages**: directly
extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
own packaging-configuration coverage — a package meant to be
consumed by other, type-checked projects should both write accurate
annotations throughout its own code, **and** include a `py.typed`
marker (correctly configured to actually be included in the built
package, a packaging-configuration detail this chapter does not
develop further) — omitting the marker, even with perfectly accurate
annotations underneath, still leaves consumers unable to actually rely
on them by default.

## 58. Type Checking Third-Party Libraries

Practical challenges, gathered together as this section's own honest
summary of a real, common limitation:

- **Untyped dependencies** — a library with no type information at
  all; every call into it is effectively `Any` (§17), regardless of
  how carefully your own code around it is annotated.
- **Partially typed dependencies** — some functions/classes annotated,
  others not; the "boundary" between checked and unchecked code inside
  a single dependency can be inconsistent and non-obvious.
- **Inaccurate stubs** — a stub file (§56), whether shipped by the
  library itself or by a separate third-party stub package, can
  simply be *wrong* (out of sync with the library's actual current
  behavior) — a static checker has no way to detect this on its own;
  it trusts the stub exactly as written, even if the stub itself is
  mistaken.
- **`Any` leakage** — per §17's "contagious" warning, restated here at
  the dependency-boundary level specifically: a single untyped
  dependency call, deep inside an otherwise carefully-typed function,
  can silently degrade everything derived from its result back to
  `Any`, without any obvious signal that this has happened unless you
  specifically go looking for it.

**How this can affect application type safety, honestly stated**: no
matter how rigorously your *own* code is typed, your application's
overall static-safety guarantee is only as strong as its **weakest,
least-typed dependency boundary** — this is a genuine, practical
limitation of Python's gradual typing model (§80), not a flaw specific
to any one project's own discipline, and worth factoring into how much
confidence you place in "the type checker passed" for code that leans
heavily on an untyped or partially-typed dependency.

## 59. Type Hints and Ruff

Directly connecting to
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §5 formatter/linter/type-checker/tests comparison, now made
completely explicit for this specific pair of tools:

| | **Ruff (linting)** | **Static type checker** |
|---|---|---|
| **What it analyzes** | Syntax structure, simple patterns, per-file logic | Type consistency across the whole analyzed codebase, following data flow |
| **Detects unused imports?** | Yes (`F401`) | No — not its concern at all |
| **Detects an undefined name?** | Yes (`F821`) | Yes, differently — as a type/name-resolution error |
| **Detects a wrong-type argument?** | No — not what linting checks for | Yes — precisely its central purpose |
| **Detects `None`-safety issues (§46)?** | No | Yes |
| **Detects a missing return statement's type mismatch (§41)?** | No | Yes |
| **Enforces formatting?** | Yes | No — not its concern at all |

**Ruff linting and type checking are genuinely different layers**,
restated once more with full precision: Ruff's rule families (`F`,
`E`, `UP`, `B`, and the rest, per
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
§9) are fundamentally **pattern-based** — recognizing specific,
nameable code shapes, without performing deep, whole-program type
inference. A dedicated type checker performs exactly that deep
inference — following how a value's type flows from where it's created
through every function it's passed to, across the entire analyzed
project, which is a categorically different (and more expensive)
analysis than any individual Ruff rule performs. A production project
runs **both**, as independent, complementary CI stages (§83 shows this
concretely) — neither substitutes for the other.

## 60. Type Hints and Testing

```python
def average(numbers: list[float]) -> float:
    return sum(numbers) / len(numbers) - 1   # bug: the "- 1" should not be here
```

Directly restating
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §31 example, now specifically through the typing lens: this
function **satisfies a static type checker completely** — every
parameter and return type is precisely declared, and every internal
operation (`sum(numbers)`, division, subtraction) is fully consistent
with those declarations. It still **returns the wrong answer**, for
every single input:
```python
>>> average([2.0, 4.0, 6.0])
3.0   # WRONG — the correct average is 4.0
```
A type checker has **no concept at all** of "is this arithmetic
formula actually correct" — that is a question about *behavior*, not
*type consistency*, and only a **test** — actually running `average()`
against a known input and comparing the result to the *expected*
correct value — can catch it:
```python
def test_average():
    assert average([2.0, 4.0, 6.0]) == 4.0   # correctly FAILS, exposing the bug
```

**Conversely**: tests, by their nature, only cover the *specific
input/output pairs someone actually wrote a test for* — a test suite
with excellent coverage of `average()`'s *normal* behavior might still
never happen to call it with an argument of the *wrong type*
(`average("not a list")`), a case a static checker would catch
instantly and universally, across every call site in the codebase at
once, with no test needed at all.

**Layered quality assurance, restated one final time with static type
checking now included as its own explicit layer**:
```
formatting        — layout only
linting             — pattern-based structural/correctness checks
type checking          — type consistency, across the whole codebase, following data flow
unit testing               — verifies specific, known input/output pairs
integration testing            — verifies multiple real components together
system testing                    — verifies the whole system end to end
```
Each layer catches a category of problem none of the others
structurally can — precisely the same principle
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §5, §31, and §52 built up in full, now with type checking given
its own explicit, permanent place in that stack.

## 61. Type Hints and Documentation

**Without type hints:**
```python
def calculate(a, b):
    ...
```
**With type hints:**
```python
def calculate(price: float, quantity: int) -> float:
    ...
```

**How type hints act as executable documentation**: the annotated
version tells a reader — instantly, without needing a separate
docstring, and without any risk of that documentation silently going
stale as the code evolves — exactly what kind of values `price` and
`quantity` are expected to be, and exactly what kind of value the
function produces. A traditional prose docstring *can* convey the same
information, but nothing keeps a docstring's claims in sync with the
actual code the way a type checker keeps annotations in sync with
actual usage (§45's whole category of diagnostics exists precisely to
catch exactly this kind of drift, which a plain-text docstring has no
mechanism to catch at all).

**Readability and IDE support, previewed here and developed fully in
§62**: `calculate(price: float, quantity: int) -> float` is
immediately, unambiguously readable at the call site — and, because
it's *structured, machine-readable* information rather than free-text
prose, an editor can actively *use* it (autocomplete, inline parameter
hints, real-time error highlighting) in ways it fundamentally cannot
for a docstring's own prose description, however well-written.

## 62. IDE Support

Directly extending
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §23 editor-integration discussion with typing specifically.

Type hints improve:

- **Autocomplete** — an editor knowing a value's precise type can
  suggest exactly the attributes/methods that type actually has,
  rather than guessing or offering nothing at all.
- **Navigation** — "go to definition" and "find all usages" become far
  more reliable when the editor can trace a value's *actual* type
  through a codebase, rather than relying on textual name-matching
  alone.
- **Refactoring** — §63 covers this specifically and in full.
- **Diagnostics** — the exact same type-checking errors §45 catalogued
  can surface directly inline in the editor, as you type, rather than
  only when a separate command is run.
- **Documentation** (§61) — hovering over a function call can show its
  full, precise signature directly, without needing to navigate away
  to find a docstring.
- **Signature help** — as you type a function call's arguments, an
  editor can show the expected parameter types and names directly,
  live, guiding correct usage as you write it.

**Connecting this to VS Code and Python development specifically**:
exactly as
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
§23 already established for Ruff's own editor integration, Python
editor tooling (in VS Code, and elsewhere) commonly relies on a
**language server** built on top of the same static-analysis
technology a standalone type checker (§39) uses — meaning much of an
editor's "smart" Python assistance is, under the hood, running
essentially the same kind of type-aware analysis this entire chapter
has been teaching, just surfaced live, inline, rather than as a
separate command-line report.

**A note worth restating from
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §23 closing point, now applied to type checking specifically**:
IDE-surfaced type diagnostics are genuinely useful for immediate,
in-the-moment feedback — but, exactly like Ruff's own editor
integration, they depend entirely on every contributor's local setup
being correctly configured, which is precisely why CI-enforced type
checking (§83) remains the independent, un-bypassable layer a real
team's workflow should never rely on IDE feedback alone to replace.

## 63. Type Hints and Refactoring

```python
def send_notification(user_id: int, message: str) -> bool:
    ...
```

Suppose this function's signature needs to change — say, `user_id:
int` becomes `user: User` (passing the whole object instead of just
an ID), because the function now needs more than just the ID.

**How static types make refactoring safer**: the moment you change
`send_notification`'s own declared parameter type, a static checker
immediately identifies **every single call site** across the entire
codebase that still passes an `int` — each one becomes a concrete,
listed type error, rather than a silent, undetected mismatch waiting
to surface later as a runtime `AttributeError` deep inside the
function body (since the old callers are now passing something the
new body doesn't expect at all). Without type hints, finding every
affected call site relies entirely on either a text-based search
(unreliable — it can miss call sites that don't literally match a
search pattern, or falsely flag unrelated ones) or exhaustive manual
review of the whole codebase.

**Renaming a domain object** carries the exact same benefit: renaming
a class (`User` → `Account`, say) and updating its own definition
immediately surfaces every annotation, every variable, and every
function signature across the codebase still referencing the old name
as a checker error — turning what would otherwise be an error-prone,
manual, codebase-wide search-and-replace into a precise, complete,
tool-verified list of exactly what needs to change.

## 64. Type Hints and API Design

```python
from collections.abc import Sequence

def create_order(
    user_id: int,
    items: Sequence[OrderItem],
) -> Order:
    ...
```

**How types communicate an API's contract, field by field**:
**inputs** — `user_id: int` and `items: Sequence[OrderItem]` state
precisely what this function needs, and (per §11) `Sequence` rather
than `list` signals that any ordered, indexable collection of
`OrderItem`s is acceptable, not specifically a `list`. **Outputs** —
`-> Order` states precisely what's guaranteed back, as a real,
specific domain type (§34), not a vague `dict` or `object`.
**Optional values** — if some parameter were genuinely optional
(`discount_code: str | None = None`), that's stated explicitly, per
§12, rather than left to a docstring or convention. **Domain models**
— `OrderItem` and `Order` (rather than raw `dict`s or primitive types)
communicate that this function operates on the application's own
well-defined domain concepts, not arbitrary loosely-structured data.

This signature, read on its own, with **zero** access to
`create_order`'s actual implementation, already tells a caller
everything needed to use it correctly — precisely the same
"communicate intent, checkably" principle §1 and §61 established,
now shown at the scale of a full, realistic API boundary rather than
a two-line toy example.

## 65. Type Hints and Backend Services

```
API layer            (typed request/response models — e.g., TypedDict or dataclass)
    ↓
service layer           (typed business-logic functions — domain models in, domain models out)
    ↓
repository layer            (typed data-access functions — e.g., def get_user(id: int) -> User | None)
    ↓
database
```

**How types communicate between layers**, working through the chain
concretely: the **API layer** receives raw, untyped external input
(§48) and, after validation, produces a typed request object; the
**service layer** receives that typed request and coordinates
business logic, calling into the **repository layer** with precisely
typed parameters and receiving precisely typed results back (including
the honest `User | None` shape, §46, for anything that might not be
found); the **repository layer** is the one place that actually
touches the database, converting raw rows into the application's own
typed domain models before handing them back upward. At every single
boundary in this chain, the function signature involved is a
checkable, enforced contract — a change at any one layer that breaks
its promised contract with an adjacent layer is caught statically
(§63), before it ever reaches a running system at all.

## 66. Type Hints and Data Engineering

```python
RawRecord = dict[str, str]              # every CSV field arrives as a string — per Module 1.5's CSV chapter

class ParsedRecord(TypedDict):
    id: int
    amount: float
    timestamp: str

class ValidatedRecord(TypedDict):
    id: int
    amount: float                 # guaranteed non-negative, per validation
    timestamp: str

@dataclass
class ProcessedRecord:
    id: int
    amount: float
    category: str                   # derived during processing — not present in the raw input at all
```

```
RawRecord           (untrusted, every field a plain str — directly from Module 1.5's csv.DictReader)
    ↓  parse (str → int, str → float — per-field conversion, exactly like §51's environment-variable pattern)
ParsedRecord
    ↓  validate (range checks, required-field checks — per 09's chapter)
ValidatedRecord
    ↓  transform (business logic — deriving new fields, computing new values)
ProcessedRecord
```

**How types document a pipeline's own transformations**: each named
stage's type is **genuinely different** from the one before it — not
merely a cosmetic rename, but a real, progressively stronger guarantee
about what the data is known to satisfy at that specific point. A
function's signature (`def validate(record: ParsedRecord) ->
ValidatedRecord:`) makes the pipeline's *own architecture* directly
visible and statically checkable — it becomes a type error to
accidentally call the `transform` stage with a merely-`ParsedRecord`
(skipping validation entirely), exactly the kind of pipeline-ordering
mistake that could otherwise slip through silently in an
untyped codebase.

## 67. Type Hints and Machine Learning

```python
from collections.abc import Sequence
from dataclasses import dataclass

@dataclass
class TrainingExample:
    features: Sequence[float]
    label: int

@dataclass
class ModelConfig:
    learning_rate: float
    epochs: int
    batch_size: int

@dataclass
class Prediction:
    label: int
    confidence: float

@dataclass
class EvaluationResult:
    accuracy: float
    precision: float
    recall: float


def load_dataset(path: Path) -> list[TrainingExample]:
    ...

def train(examples: Sequence[TrainingExample], config: ModelConfig) -> Model:
    ...

def predict(model: Model, features: Sequence[float]) -> Prediction:
    ...

def evaluate(model: Model, examples: Sequence[TrainingExample]) -> EvaluationResult:
    ...
```

**Realistic use cases, each given a precise, checkable type**:
**dataset loaders** (`load_dataset`, returning a precisely-typed list
of examples, not an ambiguous `list[Any]` or `list[dict]`); **feature
pipelines** (`Sequence[float]` for a feature vector, rather than a
bare, untyped list); **model configuration** (`ModelConfig`, giving
every hyperparameter its own name and type, directly connecting to
this course's own established configuration-object pattern from
[09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
§21); **prediction objects** and **evaluation results** (each a real,
named type, rather than a generic tuple or dict whose meaning depends
entirely on remembering positional order). Every one of these types
turns what would otherwise be implicit, undocumented conventions
("the third element of the tuple is the confidence score, I think")
into explicit, checkable, self-documenting structure — genuinely
valuable in ML code specifically, where pipelines are often long,
multi-stage, and easy to misconnect.

## 68. Type Hints and Applied AI / Agent Systems

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class Message:
    role: Literal["user", "assistant", "system", "tool"]
    content: str

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, object]

@dataclass
class ToolResult:
    tool_name: str
    output: str
    success: bool

@dataclass
class ModelResponse:
    content: str
    tool_calls: list[ToolDefinition]

@dataclass
class AgentState:
    messages: list[Message]
    available_tools: list[ToolDefinition]
    turn_count: int
```

**Connecting typing directly to this course's own long-term
direction**: every one of these types names a concept an agentic AI
system genuinely, constantly deals with — a chat **`Message`** with a
constrained `role` (`Literal`, §15, precisely capturing that a
message's role is one of a small, known set); a **`ToolDefinition`**
an agent can choose to invoke; a **`ToolResult`** reporting what
happened; a **`ModelResponse`** representing what the underlying model
actually produced; and an **`AgentState`** tracking the whole
conversation's evolving context.

```
user input
    ↓  parse + validate
typed request                    (a validated Message)
    ↓
agent orchestration                 (operates on AgentState, calling the model)
    ↓
typed tool call                        (a ToolDefinition the model chose to invoke)
    ↓
typed tool result                         (a ToolResult, after the tool actually runs)
    ↓
typed model response                         (a ModelResponse, incorporating the tool result)
```

**How typed interfaces make agentic systems easier to maintain**:
agent systems are, by nature, built from many cooperating pieces
(a model client, a tool registry, an orchestration loop, a
conversation-state store) passing structured data back and forth
constantly — exactly the kind of system where an untyped `dict`
passed between every stage becomes genuinely hard to reason about,
and where a well-typed `Message`/`ToolResult`/`AgentState` boundary
(directly applying §65's layered-services pattern to this specific
domain) lets each piece be developed, tested, and refactored (§63)
independently, with a static checker actively verifying every
handoff between them stays consistent as the system inevitably grows
in complexity over time.

## 69. Protocols in AI Systems

```python
from typing import Protocol

class ModelClient(Protocol):
    def generate(self, prompt: str) -> str: ...


class OpenAIClient:
    def generate(self, prompt: str) -> str:
        ...  # calls a specific provider's API


class AnthropicClient:
    def generate(self, prompt: str) -> str:
        ...  # calls a different provider's API


class FakeModelClient:
    def generate(self, prompt: str) -> str:
        return "This is a fake response for testing."


def run_agent(client: ModelClient, prompt: str) -> str:
    return client.generate(prompt)
```

Directly applying §29's structural-typing foundation to exactly the
kind of system §68 just introduced: `run_agent()` never needs to know
or care **which** specific model provider it's actually talking to —
`OpenAIClient`, `AnthropicClient`, and `FakeModelClient` each satisfy
`ModelClient` purely by having a compatible `generate()` method, with
**no shared base class, no inheritance relationship, and no
coordination between their authors required at all** (exactly §30's
`Cat`/`SoundMaker` structural-compatibility example, now applied to a
genuinely production-relevant scenario).

**Why this is useful, concretely, for four distinct reasons:**

- **Testing** — `run_agent(FakeModelClient(), "hello")` lets you test
  an agent's own orchestration logic completely independently of any
  real model API, real network call, or real cost — the fake client is
  statically just as valid a `ModelClient` as a real one.
- **Dependency injection** — `run_agent()`'s own signature (`client:
  ModelClient`) declares exactly what it needs, in purely behavioral
  terms, letting the caller decide *which specific implementation* to
  supply.
- **Model swapping** — switching from one provider to another (or
  supporting several at once, chosen at runtime) requires no change at
  all to `run_agent()`'s own code — only a different object, satisfying
  the same protocol, being passed in.
- **Provider abstraction** — the rest of the codebase depends on the
  *behavior* (`ModelClient`'s `generate()` contract), never on any one
  specific provider's actual SDK or API details — directly protecting
  against §55's "third-party dependency" concerns leaking deep into
  your own application's core logic.

## 70. Dependency Injection and Typing

Generalizing §69's model-client example into the broader pattern it
represents:

```python
class Repository(Protocol):
    def get_user(self, user_id: int) -> User | None: ...
    def save_user(self, user: User) -> None: ...


class PostgresRepository:
    def get_user(self, user_id: int) -> User | None: ...
    def save_user(self, user: User) -> None: ...


class InMemoryRepository:
    def __init__(self) -> None:
        self._users: dict[int, User] = {}

    def get_user(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def save_user(self, user: User) -> None:
        self._users[user.id] = user


def register_user(repo: Repository, user: User) -> None:
    repo.save_user(user)
```

**How typing improves dependency injection, across the same recurring
categories**: **repositories** (a database-backed implementation for
production, an in-memory one for fast, isolated tests — exactly as
shown above); **model clients** (§69's own worked example);
**API clients** (an HTTP-backed implementation versus a
recorded/mocked one for testing); **storage providers** (a real cloud
storage backend versus a local-filesystem one for development).

**How `Protocol` reduces coupling, stated as this section's — and this
whole sequence's — closing principle**: `register_user()`'s own
signature depends on nothing but the `Repository` protocol's two
method signatures — it has no idea `PostgresRepository` or
`InMemoryRepository` even exist, and neither of those classes needs to
know about the other, or about `Repository` itself beyond structurally
matching its shape. This is the *typed*, *statically checkable*
realization of a design principle real production systems depend on
constantly: business logic depends on **behavior**, never on
**concrete implementation** — `Protocol` is what lets Python express
that dependency precisely, with full static verification, while
keeping every implementation completely free to vary, be swapped, or
be tested in isolation.

## 71. Advanced Type System Concepts

Every feature this chapter has covered so far (§3–§70) forms the
foundation the following sections build on. This section is a brief
orientation before diving into each remaining advanced feature in its
own dedicated section (§72–§79) — `overload`, `cast`, `NewType`,
`Final`, `Annotated`, `ParamSpec`, `Concatenate`, and (where relevant)
`TypeAliasType`. Each of the following sections follows the same
pattern this whole chapter has used throughout: the problem the
feature solves, a simple example, production use, real limitations,
and — just as importantly — when *not* to reach for it. These are
genuinely advanced tools, each solving a real but relatively narrow
problem; none of them is something a typical function or class needs
routinely, and reaching for one where a simpler tool (already covered
in §1–§70) would do is itself worth actively avoiding.

## 72. `overload`

```python
from typing import overload

@overload
def parse(value: str) -> int: ...
@overload
def parse(value: bytes) -> bytes: ...
def parse(value: str | bytes) -> int | bytes:
    if isinstance(value, str):
        return int(value)
    return value
```

**Why overloads exist**: a single function whose **return type
genuinely depends on which specific input type it was called with** —
`parse("42")` should be statically known to return `int`;
`parse(b"42")` should be statically known to return `bytes` — cannot
be expressed by one plain signature alone; a single `def parse(value:
str | bytes) -> int | bytes:` would force *every* call site to handle
*both* possible return types, even when the actual call makes the
correct one perfectly obvious.

**How overloads work**: each `@overload`-decorated signature declares
one specific input-type-to-output-type pairing, purely for the
**static checker's** benefit — a checker reading a call to `parse()`
picks whichever `@overload` signature matches the argument's actual
type, and reports the corresponding, more specific return type for
that call site.

**Overload declarations primarily help static analysis and require an
implementation**: none of the `@overload`-decorated signatures above
have real bodies (each is just `...`) — they exist purely as
type-level declarations. The **final**, undecorated `def parse(value:
str | bytes) -> int | bytes:` is the actual, real, runtime
implementation that genuinely executes — every overloaded function
needs exactly one such real implementation beneath its overload
declarations, and that implementation's own signature must be broad
enough (typically a union) to accept every case any of the overloads
promises to handle.

## 73. `cast`

```python
from typing import cast

def get_config_value(data: dict[str, object], key: str) -> str:
    value = data[key]
    return cast(str, value)
```

**What `cast()` does**: it tells the **static checker**, explicitly,
"trust me — treat this value as this specific type from here on,"
overriding whatever the checker would otherwise have inferred.

**What `cast()` does *not* do — stated with the same bluntness as
§4's original warning, because this is exactly the same category of
misunderstanding**: `cast(str, value)` performs **no runtime
conversion and no runtime validation whatsoever**. If `value` is
actually an `int` at runtime, `cast(str, value)` does not convert it,
does not check it, and does not raise anything — it simply returns
`value`, completely unchanged, while telling the *type checker* to
now treat it as `str`. If that claim is wrong, the mistake surfaces
later, at runtime, wherever the (actually-still-an-`int`) value is
used as if it were genuinely a string — `cast()` has actively **hidden**
the mismatch from the one tool (the type checker) that could otherwise
have caught it.

**Why excessive `cast()` usage can hide type problems**: every `cast()`
call is a point where you've told the checker to stop verifying
something and simply trust your own claim instead — reaching for it
routinely, rather than as a narrow, deliberate escape hatch (much like
`Any`, §17, and for exactly the same underlying reason), quietly
erodes the very guarantees the rest of your typed code is relying on.
Reach for `cast()` only when you have genuinely verified, through some
means the checker itself cannot see (a runtime check performed
elsewhere, a documented invariant about the data's actual source),
that the cast claim is really true — and prefer an actual `isinstance`
narrowing check (§26) wherever one is possible instead, since that
provides the checker's own, genuine verification rather than merely
asking it to stop checking at all.

## 74. `NewType`

```python
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)


def get_order(order_id: OrderId, user_id: UserId) -> Order:
    ...


get_order(order_id=OrderId(42), user_id=UserId(7))    # OK
get_order(order_id=UserId(7), user_id=OrderId(42))       # error — even though both are "really" int
```

**Why `NewType` provides a stronger semantic distinction than a plain
alias**: directly resolving §32's own stated limitation — a plain
alias (`UserId = int`, §14) creates **no new type at all**; `UserId`
and `OrderId` remain, to a checker, both simply `int`, and nothing
stops them from being silently swapped. `NewType("UserId", int)`
instead creates a genuinely **distinct type**, as far as the static
checker is concerned — `UserId` values and plain `int` values (and
`OrderId` values) are **not** interchangeable without an explicit
`UserId(...)` call, and the swapped-argument mistake above is now a
real, caught, static type error.

**Comparing the three tools directly**:

| | **Plain alias** | **`NewType`** | **Subclass** |
|---|---|---|---|
| Creates a genuinely distinct static type? | No — identical to the underlying type | Yes | Yes |
| Runtime cost | None | Minimal (a thin callable wrapper) | A real class, with its own `__init__`, potential overhead |
| Can add its own methods/behavior? | No | No | Yes |
| Best for | Pure readability, no risk of mix-up | Preventing mix-ups between same-underlying-type values | A domain concept that genuinely needs its own behavior |

**Trade-offs**: `NewType` sits deliberately between a plain alias
(cheap, but no protection) and a full subclass (real protection and
real behavior, but real runtime cost and design overhead) — reach for
it specifically when the *mix-up risk* (exactly `UserId`/`OrderId`
above) is real and worth guarding against, but a full custom class
would be more machinery than the concept actually needs.

## 75. `Final`

```python
from typing import Final

MAX_RETRIES: Final = 5
DEFAULT_TIMEOUT: Final[float] = 30.0
```

**How `Final` communicates that a value should not be reassigned**: it
tells a static checker "this name, once assigned, must never be
assigned again" — `MAX_RETRIES = 10` anywhere later in the same scope
becomes a flagged error. `Final[float]` combines this with an explicit
type, exactly like any other annotation; the bare `Final` form (with
no bracketed type) lets the checker infer the type from the assigned
value directly, per §43's inference discussion.

**Configuration/constants examples**: `Final` is a natural fit for
exactly the module-level constants §5 already introduced by
convention (uppercase naming) — `Final` adds a real, checked guarantee
on top of that naming convention alone, catching an accidental
reassignment statically rather than relying purely on a human noticing
a constant's name looks like it shouldn't be reassigned. Like every
other feature in this chapter, `Final`'s protection is **static
only** — Python itself does not prevent reassigning a `Final`-annotated
name at runtime; only a type checker, reading the annotation, refuses
to consider such a reassignment valid.

## 76. `Annotated`

```python
from typing import Annotated

Age = Annotated[int, "must be between 0 and 150"]

def set_age(age: Annotated[int, "must be non-negative"]) -> None:
    ...
```

**The concept of attaching metadata to a type**: `Annotated[int, ...]`
is still, fundamentally, `int` as far as ordinary type checking is
concerned — every operation valid on `int` remains valid — but the
second (and any further) argument to `Annotated` attaches arbitrary
extra **metadata** alongside that base type, which a checker itself
generally ignores for its own core type-consistency checks, but which
some other tool or framework can specifically read and act on.

**What that metadata is actually used for**: this varies entirely by
which tool is reading it — a validation framework might read
`Annotated`'s metadata to generate an actual runtime check (e.g., "this
int must be non-negative," enforced for real, at runtime, by that
framework — not by Python or by the type checker themselves); a
documentation generator might read it to produce richer, more
descriptive API documentation than the bare type alone would provide.

**Do not overstate what Python itself enforces**, restating this
chapter's now-familiar core caution one more time, specifically for
this feature: `Annotated`'s metadata is, by itself, **inert** — plain
data attached to a type, doing nothing on its own. Writing `Annotated[
int, "must be non-negative"]` does **not**, by itself, cause Python
(or even a static type checker) to actually verify that constraint
anywhere — only a specific tool deliberately built to read and act on
that metadata does anything with it at all; without such a tool in the
picture, `Annotated[int, "must be non-negative"]` behaves, for every
practical purpose, exactly like bare `int`.

## 77. `ParamSpec`

```python
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@log_calls
def add(x: int, y: int) -> int:
    return x + y
```

**The problem `ParamSpec` solves**: **preserving a wrapped function's
own, exact parameter signature** through a decorator. Without
`ParamSpec`, a decorator like `log_calls` would typically need to
annotate `wrapper`'s own parameters generically (`*args: Any, **kwargs:
Any`), which — per §17's "contagious `Any`" warning — would silently
discard `add`'s own precise `(x: int, y: int) -> int` signature the
moment it's wrapped, meaning a static checker could no longer verify
calls to the *decorated* `add` against its real, original signature at
all.

**How the example works**: `P = ParamSpec("P")` captures "whatever
parameter signature the wrapped function actually has" as its own type
variable, distinct from an ordinary `TypeVar` (which captures a single
*value* type, not a whole *parameter list* shape); `Callable[P, R]`
appears **twice** — once for `func` (the original function being
wrapped) and once as `log_calls`'s own return type — telling the
checker "whatever signature `func` has, the returned, wrapped function
has that exact same signature too." `*args: P.args, **kwargs:
P.kwargs` inside `wrapper` lets the wrapper itself forward arbitrary
arguments through while still being tied, precisely, to `P`.

**Keep the first example simple**: `ParamSpec` is genuinely one of the
more advanced tools this chapter covers — its value is almost entirely
concentrated in exactly this one recurring pattern (a decorator that
needs to preserve the wrapped function's own signature); reach for it
specifically when writing this kind of decorator, and not as a general-
purpose tool for other situations.

## 78. `Concatenate`

```python
from typing import Concatenate

def with_logger(
    func: Callable[Concatenate[Logger, P], R]
) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger = get_current_logger()
        return func(logger, *args, **kwargs)
    return wrapper


@with_logger
def process(logger: Logger, data: str) -> None:
    logger.info(f"Processing {data}")
```

**Why `Concatenate` exists**, building directly on §77's `ParamSpec`:
`with_logger`'s decorated function needs a **modified** signature — the
*wrapped* version (`process` as seen from the outside, after
decoration) should **not** require a caller to pass `logger` at all
(the decorator supplies it automatically), even though the *original*
function genuinely does take `logger` as its first parameter.
`Concatenate[Logger, P]` expresses exactly this: "the original
function's parameters are `Logger`, followed by whatever `P`
represents" — letting the decorator's own return type
(`Callable[P, R]`, **without** `Logger` prepended) correctly reflect
that the *caller* of the decorated function no longer needs to supply
it.

**A simple dependency-injection/decorator example, stated plainly**:
this is precisely the shape of a decorator that automatically injects
one specific, extra argument (a logger, a request context, a database
connection) that the *decorated* function needs internally, but that
callers of the *already-decorated* version should never need to
provide themselves — `Concatenate` is what lets that transformation
be expressed with full, static precision, rather than falling back to
an unchecked `*args: Any` shape that discards the caller-facing
signature's accuracy entirely. Avoid unnecessary type-theory
complexity beyond this one concrete pattern — like `ParamSpec` itself,
`Concatenate`'s value is concentrated almost entirely in exactly this
recurring decorator shape.

## 79. `TypeAliasType`

```python
type UserId = int
```

Revisiting §14's modern `type` statement (Python 3.12+, via PEP 695)
specifically from the runtime-object angle: evaluating a `type`
statement actually creates a real, distinct runtime object — an
instance of `typing.TypeAliasType` — bound to the name `UserId`,
**distinct from** simply assigning `UserId = int` directly (the plain-
assignment form, which binds `UserId` to the exact same object `int`
itself is).

**Clearly distinguishing the three related things this section (and
§14) has now fully covered**: a **plain (implicit) type alias**
(`UserId = int`) is an ordinary variable assignment, binding a name
directly to an existing type object, with no new object created at
all. An **explicit alias** written using `TypeAlias` (`UserId:
TypeAlias = int`, available from Python 3.10) adds a static-only
annotation marking the assignment as intentionally an alias, without
changing what actually happens at runtime. The **`type` statement**
(3.12+) is different again at the runtime level — it creates a real
**`TypeAliasType`** instance, which behaves like `int` for type-
checking purposes but is, at runtime, its own distinct kind of object
(useful, in particular, for supporting **lazy evaluation** of forward
references inside the alias itself, and for carrying its own
`__name__`/`__value__` introspection attributes) — a genuinely
different mechanism underneath a very similar-looking surface syntax.

**Do not introduce this distinction unless it's useful for your
project's actual Python version**: this level of detail matters
primarily for library authors or advanced tooling that specifically
needs to *introspect* alias objects at runtime; for a project simply
targeting Python 3.12+ and wanting the clearest, most modern alias
syntax (this module's own established baseline), the plain `type
UserId = int` statement from §14 is the right choice, with this
section's finer runtime distinction being background knowledge rather
than something to actively design around in ordinary application
code.

## 80. Gradual Typing

**Gradual typing** is the design principle underlying everything this
chapter has taught: **typed and untyped code can coexist in the same
codebase, and a project can move incrementally from no annotations at
all toward comprehensive, strictly-checked typing**, rather than
requiring an all-or-nothing commitment.

```
no annotations at all
        ↓
basic annotations             (a few key functions, added opportunistically)
        ↓
public API annotations           (every function other code/modules actually call gets typed)
        ↓
internal annotations                (helper functions, internal-only code, typed too)
        ↓
static checking                        (a type checker is actually run, in permissive mode, §42)
        ↓
stricter checking                         (strict mode, §42, progressively enabled)
```

**Why incremental adoption is the right default, not a compromise**:
`Any` (§17) is precisely the mechanism that makes every one of these
intermediate stages *valid* — an untyped function, called from a typed
one, is effectively `Any` at that boundary, which the checker accepts
without complaint (in permissive mode, §42) rather than refusing to
process the file at all. This is a deliberate design choice built into
Python's typing system from the ground up, not a workaround this
chapter is suggesting around some stricter, unintended default — it
is *exactly* what lets a team begin gaining real value from typing on
day one, on the specific functions that matter most, without first
needing to annotate an entire, possibly large, pre-existing codebase.

## 81. Legacy Code Migration

A practical, step-by-step plan for adding type hints to an existing,
previously-unannotated project — directly mirroring
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §35 legacy-migration structure, now applied to typing specifically.

1. **Identify critical modules.** Start with the code where a type
   error would be most costly, or where confusion about a function's
   contract has caused real problems before — not necessarily the
   largest file, but the most *consequential* one.
2. **Annotate public functions first.** Per §54's own principle,
   public functions carry the widest "blast radius" if their contract
   is unclear — annotating them first delivers the most value per
   annotation written.
3. **Annotate boundaries.** Exactly §48's untrusted-data boundaries —
   where external data enters the system (CLI parsing, JSON parsing,
   environment-variable reads) — benefit enormously from precise types
   on the *validated* side of that boundary, even before the rest of
   the codebase is touched at all.
4. **Reduce `Any`.** Wherever an early annotation pass leaves a
   parameter or return type at `Any` (because the real type wasn't
   immediately obvious, or gradual typing left it implicit), come back
   and tighten it once the surrounding code is better understood.
5. **Introduce type checking.** Run a static checker (§39) in
   **permissive mode** (§42) first, against whatever's been annotated
   so far — don't wait until the whole project is fully typed before
   running a checker even once.
6. **Fix errors incrementally.** Address the diagnostics a checker
   surfaces in manageable batches, exactly like
   [05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
   own §35 recommended for lint violations — not necessarily all at
   once.
7. **Increase strictness gradually.** Once the low-hanging, high-value
   annotations are in place and their diagnostics resolved, progressively
   enable stricter checking (§42, §82) for the portions of the codebase
   that are ready for it.

**Why trying to type an entire legacy project at once may be
impractical**: for any codebase of meaningful size, a single,
all-at-once annotation effort competes directly against real feature
work, risks introducing bugs through hasty, poorly-considered
annotations added purely to satisfy a checker, and — much like
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §34–§35 warned for an overly broad, all-at-once Ruff rule
rollout — can produce an overwhelming, demoralizing wall of initial
diagnostics with no clear, prioritized path through them. §80's
gradual-typing principle is precisely what makes staged, incremental
migration not just tolerable but the genuinely correct, intended way
to adopt typing on an existing project.

## 82. Strict Typing Strategy

How a real engineering team defines its own **typing policy** — a
deliberate set of team-wide decisions, not a single, universally
correct configuration:

- **Required annotations** — which parts of the codebase (all public
  functions? every function, no exceptions? only new code going
  forward?) are required to be annotated, and by when.
- **Strictness level** — whether (and how far) strict mode (§42) is
  enabled, and for which parts of the codebase.
- **`Any` policy** — under what specific circumstances `Any` is an
  acceptable choice (an untyped third-party dependency boundary, §58)
  versus something that should be actively minimized or explicitly
  justified with a comment.
- **Public API requirements** — a stricter bar for anything exposed as
  part of a package's own public interface (§54), reflecting that its
  contract is a promise to a wider set of consumers.
- **CI enforcement** — whether, and how strictly, type-checking
  failures actually block a merge (§83), versus being reported as a
  non-blocking, advisory signal during an initial adoption period.

**Why this chapter deliberately does not prescribe one universal
policy**: exactly the same honest position
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §22 and §39 took for Ruff's own rule-selection policy — the right
level of typing strictness genuinely depends on a project's size,
maturity, risk profile (§39's library-vs-application-style tradeoffs
apply here too), and how much of its existing codebase is already
annotated. A brand-new project can reasonably start at full strictness
from day one; a large, long-lived legacy codebase reasonably adopts
strictness gradually (§80–§81), and the "correct" policy for each is
genuinely different, not a matter of one being objectively more
rigorous than the other in some universal sense.

## 83. CI Type Checking

```
formatting          (ruff format --check)
    ↓
linting                (ruff check)
    ↓
type checking              (mypy / pyright / basedpyright)
    ↓
tests                          (pytest)
    ↓
build
```

Directly extending
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §26–§29 CI-integration chapter with static type checking now
inserted as its own explicit, independent stage — positioned *after*
formatting/linting (since both are cheap, fast, and worth failing on
immediately, before spending time on a typically-more-expensive type-
checking pass) and *before* tests (since a codebase with real type
errors is often not worth spending test-suite time on until those are
resolved, though a team's own policy may reasonably order this
differently).

**Local checks vs. CI checks**: exactly
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §26 principle, restated for type checking specifically — a
developer can (and should) run a type checker locally, or rely on
editor integration (§62), during active development; **CI
independently re-verifies** the exact same check, in a clean,
reproducible environment (directly connecting to
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
own reproducibility guarantees — the type checker's own version,
pinned via `uv.lock`, is exactly as important to keep reproducible as
any other dependency), regardless of whether any individual developer
actually ran it themselves before pushing.

**Exit codes and pull requests**: directly reusing
[07-standard-streams-and-exit-codes.md](../05-Text-Files-Structured-Data-and-CLI-Programs/07-standard-streams-and-exit-codes.md)'s
own established vocabulary — a type checker run as a CI step exits
non-zero when it finds any type error, failing that pipeline stage and
(via the repository's own branch-protection configuration, exactly
per
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
§26) blocking the pull request from merging until resolved — the same
CI-gating mechanism this course has now applied consistently to
formatting, linting, and, here, static type checking as well.

## 84. Pre-Commit and Type Checking

**Should type checking run in `pre-commit`** (per
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
own §25 introduction of the tool)? The honest answer is: **it
depends, and not every team should run full type checking on every
single commit.**

**The trade-offs, stated directly:**
- **Speed** — a full, whole-project static type-checking pass can
  genuinely take longer than Ruff's own formatting/linting checks
  (which are specifically engineered for extreme speed, per
  [05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
  §37) — running it on *every single commit*, especially for a large
  codebase, risks becoming a real, repeated interruption to a
  developer's local workflow, exactly the concern that same chapter's
  §37 raised about slow tooling generally.
- **Developer feedback** — faster, more immediate feedback (via editor
  integration, §62, or a fast, incremental check) is often more
  valuable day-to-day than a slower, more exhaustive pre-commit pass.
- **Repository size** — a small project's full type-check might run in
  a fraction of a second, making pre-commit inclusion essentially
  free; a large monorepo's full check might take much longer, making
  the same choice far more costly.
- **CI enforcement** — because CI (§83) already independently, and
  authoritatively, verifies type correctness on every push, pre-commit
  type checking is not the *only* safety net — it's an optional,
  earlier one, whose value has to be weighed against its own local
  cost.

**A reasonable middle ground many teams adopt**: run type checking in
pre-commit only on the **specific files actually being committed**
(many type checkers, and pre-commit's own framework, support this kind
of scoped, incremental checking), rather than the whole project every
time — keeping the pre-commit hook fast while still catching type
errors before they're even committed, with the *full*, whole-project
check reserved for CI. This chapter does not claim one universal
answer is correct for every team — exactly §82's own honest position,
applied here specifically to the pre-commit-vs-CI placement question.

## 85. Type Checking and Performance

**The distinction this section exists specifically to make precise**:
**static analysis time** — how long a type checker takes to *analyze*
your source code, before your program ever runs — is a completely
separate concern from **application runtime performance** — how fast
your program actually executes, once it's running.

```python
def add(a: int, b: int) -> int:
    return a + b
```

**Type hints generally do not make normal Python execution faster
simply because they exist.** This needs to be stated with the same
directness as every other "does not automatically do X" warning this
chapter has issued (§4, §17, §73, §76): by default, **CPython does not
use annotations to optimize execution at all** — `add(3, 4)` runs at
essentially the same speed whether `a`/`b`/the return value are
annotated or not; the interpreter, in its default, standard mode of
execution, does not read `__annotations__` (§38) during ordinary
function calls, does not use them to skip runtime type checks it
wouldn't otherwise perform, and gains no inherent speed benefit from
their mere presence.

**Discussing exceptions honestly, without overclaiming**: certain
**runtime frameworks** genuinely do inspect annotations (§38's own
closing discussion) and use that information to change their own
behavior — a validation library might use annotations to decide what
runtime checks to perform (which itself typically adds runtime
overhead, for the *validation work*, not a speed-up); a serialization
library might use them to decide how to convert data — but any such
effect is a property of that *specific third-party framework's own
implementation*, deliberately built to read and act on annotations at
runtime, not an inherent property of type hints themselves, and not
something you should assume applies to your own annotated code by
default, absent such a framework specifically using it that way.

## 86. Common Beginner Mistakes

1. **Thinking annotations enforce types.** *Why it happens:* the
   syntax looks declarative and authoritative, much like a statically
   typed language's own variable declarations. *Why problematic:*
   leads to code that assumes invalid data was already rejected, when
   nothing actually rejected it (§4). *Better approach:* treat
   annotations as documentation-plus-static-checking only; validate
   explicitly at real boundaries (§48).
2. **Using `Any` everywhere.** *Why it happens:* it's the fastest way
   to silence a checker's complaints. *Why problematic:* `Any` is
   contagious (§17) and silently disables checking for everything
   derived from it. *Better approach:* use precise types by default;
   reach for `Any` narrowly and deliberately.
3. **Using `cast` to silence errors.** *Why it happens:* it makes a
   checker's complaint disappear immediately, with no further code
   changes. *Why problematic:* performs no runtime verification at all
   (§73) — the underlying mismatch, if real, still exists, just hidden
   from the one tool that could have caught it. *Better approach:*
   prefer an actual `isinstance` narrowing check; reserve `cast` for
   cases genuinely verified some other way.
4. **Overusing unions.** *Why it happens:* it feels safer to accept
   "anything that might come up." *Why problematic:* a union with many
   members communicates little more than `Any` would, and often
   signals a function trying to do too much (§13). *Better approach:*
   keep unions narrow and intentional; split an overly broad function
   if needed.
5. **Overengineering types.** *Why it happens:* enthusiasm after
   learning advanced features (`TypeVar`, `Protocol`, `ParamSpec`).
   *Why problematic:* adds real cognitive overhead without
   proportional benefit for code that doesn't actually need that level
   of generality. *Better approach:* start simple (§1–§20's basics);
   reach for advanced features (§71–§79) only when the specific
   problem they solve is genuinely present.
6. **Annotating everything without understanding the domain.** *Why it
   happens:* treating annotation as a mechanical, box-checking
   exercise. *Why problematic:* produces technically-present but
   low-value types (`dict[str, object]` everywhere, per §10's own
   warning) that don't actually communicate anything useful. *Better
   approach:* annotate with the actual domain in mind — precise types,
   domain aliases (§32), `TypedDict`/`dataclass` (§33–§34) where the
   structure genuinely matters.
7. **Ignoring `None`.** *Why it happens:* it's easy to forget a
   function *can* return `None` when a "happy path" value is the
   common case. *Why problematic:* exactly §46's central concern —
   the single most common source of real production `AttributeError`s
   from code that "passed" a checker only because `None` was never
   actually excluded before use. *Better approach:* always narrow a
   `T | None` value before using it as `T`.
8. **Using `object` when a precise type is already known.** *Why it
   happens:* a reflexive habit of "being safe" by staying vague. *Why
   problematic:* discards real, available static-checking value for no
   benefit — if you already know a parameter is always an `int`,
   `object` only adds friction (forcing unnecessary narrowing) with no
   corresponding safety gain. *Better approach:* use `object` (§18)
   specifically when a type is genuinely unknown/heterogeneous, not by
   default.
9. **Using overly broad `dict` types.** *Why it happens:* `dict[str,
   object]` (or worse, an unannotated `dict`) feels like the "safe,
   flexible" default. *Why problematic:* per §10, tells a checker
   almost nothing useful about a structure that likely has real, known
   shape. *Better approach:* reach for `TypedDict` (§33) or a
   `dataclass` (§34) once a dictionary's actual keys and value types
   are known.
10. **Confusing `TypedDict` with `dict` runtime behavior.** *Why it
    happens:* `TypedDict` syntax visually resembles a class definition.
    *Why problematic:* a `TypedDict`-typed value is, at runtime,
    literally just a plain `dict` — `isinstance(user, User)` does not
    behave the way it would for a real class, and there's no runtime
    enforcement of its declared keys/types at all (exactly §4's
    warning, applied specifically here). *Better approach:* remember
    `TypedDict` provides *static* structure only; pair it with actual
    validation (§48–§49) at the boundary where the dictionary is first
    constructed from untrusted data.
11. **Confusing `Protocol` with inheritance.** *Why it happens:* both
    involve defining methods a class must "have." *Why problematic:*
    leads to unnecessary, forced inheritance relationships where
    structural compatibility (§29–§30) would have been simpler and
    less coupled. *Better approach:* default to `Protocol` for
    behavioral contracts unless you specifically need an ABC's runtime-
    enforced completeness (§31).
12. **Assuming tests replace type checking.** *Why it happens:* a
    thorough test suite feels like it should "cover everything." *Why
    problematic:* per §60, tests only exercise the specific cases
    someone wrote a test for — a type checker catches classes of
    mismatch across the *whole* codebase, including paths no test
    happens to exercise. *Better approach:* run both, as complementary
    layers.
13. **Assuming type checking replaces tests.** *Why it happens:* the
    opposite, equally common misunderstanding — a "fully typed, checker-
    clean" codebase feels thoroughly verified. *Why problematic:*
    §60's `average()` example — a type checker has no concept of
    whether your logic is actually *correct*, only whether it's type-
    *consistent*. *Better approach:* the same answer as mistake 12 —
    run both.
14. **Blindly enabling strict mode.** *Why it happens:* "strict" sounds
    like the more rigorous, responsible choice. *Why problematic:* on
    an existing, previously-unannotated codebase, this can produce an
    overwhelming wall of diagnostics with no clear starting point,
    mirroring
    [05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
    own §34 warning about enabling too many lint rules at once.
    *Better approach:* adopt strictness gradually (§80–§82), matched to
    the codebase's actual current state.
15. **Ignoring third-party typing limitations.** *Why it happens:*
    assuming every installed package is fully, accurately typed by
    default. *Why problematic:* per §55/§58, an untyped or partially-
    typed dependency silently weakens your own application's static
    guarantees at exactly the boundary where it's used, regardless of
    how carefully your own code is annotated. *Better approach:*
    understand which of your dependencies are (and aren't) reliably
    typed, and treat calls into untyped ones with the same caution
    you'd give any other `Any`-typed boundary.

## 87. Debugging Lab

The following (fictional) module, `inventory.py`, has several
type-related problems. Diagnose each before reading the answer key.

```python
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class Item:
    name: str
    quantity: int


class Storage(Protocol):
    def save(item: Item) -> None: ...


def find_item(items: list[Item], name: str) -> Item:
    for item in items:
        if item.name == name:
            return item


def total_quantity(items: list) -> int:
    return sum(item.quantity for item in items)


def get_metadata(item: Item) -> Any:
    return {"name": item.name, "quantity": item.quantity}


def restock(item: Item, amount) -> Item:
    item.quantity = item.quantity + amount
    return item


class FileStorage:
    def save(self, item: Item, path) -> None:
        ...


def process(storage: Storage, item: Item) -> None:
    storage.save(item)
```

**Diagnose the following, before reading further:**
1. A missing return path against a declared return type.
2. An overly broad, unparameterized collection type.
3. Unnecessary/misused `Any`.
4. A missing parameter type annotation.
5. A `Protocol` method missing `self`.
6. A class that doesn't actually satisfy the `Protocol` it's meant to
   implement.

**Answer key:**

1. **Missing return path (§45 item 3-adjacent, and §46's `None`-safety
   territory):** `find_item()` is declared `-> Item`, but if no
   matching item is found, the function falls through with no explicit
   `return` at all — implicitly returning `None`, which doesn't match
   the declared `-> Item` return type. *Fix:*
   ```python
   def find_item(items: list[Item], name: str) -> Item | None:
       for item in items:
           if item.name == name:
               return item
       return None
   ```
2. **Overly broad collection type (§8, §10, §86 mistake 9):**
   `total_quantity(items: list)` uses a bare, unparameterized `list` —
   a checker has no idea what's inside it, so `item.quantity` inside
   the function body can't be verified at all. *Fix:*
   `def total_quantity(items: list[Item]) -> int:`.
3. **Unnecessary `Any` (§17, §86 mistake 2):** `get_metadata()`
   returns `Any`, discarding real, available structure — the return
   value is actually always a two-key dictionary with known types.
   *Fix:*
   ```python
   def get_metadata(item: Item) -> dict[str, str | int]:
       return {"name": item.name, "quantity": item.quantity}
   ```
   (or, better still, a small `TypedDict`, §33, if this shape recurs
   elsewhere).
4. **Missing parameter type annotations (§6, §86 mistake 6):**
   `restock(item: Item, amount)` leaves `amount` completely
   unannotated, and `FileStorage.save(self, item: Item, path)` leaves
   `path` unannotated too. *Fix:* `def restock(item: Item, amount:
   int) -> Item:`; `def save(self, item: Item, path: Path) -> None:`.
5. **`Protocol` method missing `self` (§29):** `Storage.save(item:
   Item) -> None:` is missing its own `self` parameter — as written,
   this declares a *static*-style method taking only `item`, which
   does not correctly describe an ordinary instance method any real
   implementing class would define. *Fix:*
   `def save(self, item: Item) -> None: ...`.
6. **A class that doesn't actually satisfy its intended `Protocol`
   (§29–§30):** even after fixing mistake 5, `FileStorage.save(self,
   item: Item, path)` takes an *extra* required parameter (`path`)
   that `Storage.save`'s own protocol signature doesn't have at all —
   meaning `FileStorage` does **not** actually structurally satisfy
   `Storage`, and `process(FileStorage(), item)` in the last function
   would be flagged as a type error, correctly, the moment `Storage`
   itself is fixed and `path` isn't given a default. *Fix:* either
   remove `path` from `FileStorage.save()` if it's genuinely
   unnecessary, or give it a default value (`path: Path = DEFAULT_PATH`)
   so the method remains callable with just `item`, matching
   `Storage`'s own declared contract.

## 88. Complete Example Project — Typed Production-Style Python Service

A realistic project structure, shown here purely as Markdown (no
files are created), demonstrating this chapter's major features
working together:

```
typed-service/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── models.py
│       ├── repository.py
│       ├── service.py
│       ├── client.py
│       └── main.py
├── tests/
└── pyproject.toml
```

**`models.py` — domain models, `TypedDict`, and a type alias:**
```python
from dataclasses import dataclass
from typing import TypedDict

UserId = int


@dataclass
class User:
    id: UserId
    name: str
    email: str


class UserPayload(TypedDict):
    id: int
    name: str
    email: str
```

**`repository.py` — `Protocol` for a swappable data-access layer:**
```python
from typing import Protocol

from .models import User, UserId


class UserRepository(Protocol):
    def get(self, user_id: UserId) -> User | None: ...
    def save(self, user: User) -> None: ...


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[UserId, User] = {}

    def get(self, user_id: UserId) -> User | None:
        return self._users.get(user_id)

    def save(self, user: User) -> None:
        self._users[user.id] = user
```

**`service.py` — business logic, `Optional`/`None` handled explicitly,
generics for a small reusable helper:**
```python
from collections.abc import Sequence
from typing import TypeVar

from .models import User, UserId, UserPayload
from .repository import UserRepository

T = TypeVar("T")


def first_or_none(items: Sequence[T]) -> T | None:
    return items[0] if items else None


def parse_user_payload(payload: dict[str, object]) -> UserPayload:
    user_id = payload.get("id")
    name = payload.get("name")
    email = payload.get("email")
    if not isinstance(user_id, int) or not isinstance(name, str) or not isinstance(email, str):
        raise ValueError("invalid user payload")
    return {"id": user_id, "name": name, "email": email}


def register_user(repo: UserRepository, payload: dict[str, object]) -> User:
    validated = parse_user_payload(payload)
    user = User(id=validated["id"], name=validated["name"], email=validated["email"])
    repo.save(user)
    return user


def get_user_or_raise(repo: UserRepository, user_id: UserId) -> User:
    user = repo.get(user_id)
    if user is None:
        raise ValueError(f"no user found for id {user_id}")
    return user
```

**`client.py` — `Callable`/`Protocol` for an external dependency:**
```python
from typing import Protocol


class NotificationClient(Protocol):
    def send(self, to: str, message: str) -> bool: ...


class ConsoleNotificationClient:
    def send(self, to: str, message: str) -> bool:
        print(f"[to {to}] {message}")
        return True
```

**`main.py` — the thin entry point, tying it all together:**
```python
from .client import ConsoleNotificationClient
from .repository import InMemoryUserRepository
from .service import get_user_or_raise, register_user


def main() -> int:
    repo = InMemoryUserRepository()
    notifier = ConsoleNotificationClient()

    user = register_user(repo, {"id": 1, "name": "Alice", "email": "alice@example.com"})
    notifier.send(user.email, "Welcome!")

    found = get_user_or_raise(repo, 1)
    print(found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**What this demonstrates, tied back to specific sections**: `UserId`
as a domain-meaningful type alias (§14, §32); `User` as a typed
`dataclass` (§34); `UserPayload` as a `TypedDict` describing raw,
externally-sourced data (§33, §49); `UserRepository` and
`NotificationClient` as `Protocol`s enabling dependency injection and
easy testing with a fake implementation (§29, §69–§70); `T`/generics
for a small, genuinely reusable helper (§21–§22); explicit `None`
handling at the repository boundary (§46); and runtime validation
(`parse_user_payload`) converting untrusted `dict[str, object]` input
into a precisely-typed representation before any business logic
touches it (§48–§49) — exactly this chapter's own, central "untyped →
validated → typed → business logic" pipeline, worked through in full,
in one small, coherent, realistic codebase. Ruff (per
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md))
and a static type checker (§39) would both run cleanly against this
project's `pyproject.toml`-configured CI (§83), as two independent,
complementary verification layers.

## 89. Coding Exercises

**Level 1 — Basic**

1. Annotate three local variables of different types, and explain in
   a comment why an explicit annotation is (or isn't) genuinely useful
   for each.
2. Add parameter and return type annotations to an unannotated
   two-parameter function of your choice.
3. Add a return type of `-> None` to a function that only prints, and
   explain why that's different from omitting the return annotation
   entirely.
4. Annotate a `list[str]`, a `dict[str, int]`, and a `tuple[str, int,
   bool]` variable, each with an appropriate literal value.
5. Given a function call that passes a value of the wrong type against
   an already-annotated function, identify the mismatch by reading the
   signature alone, without running any tool.

**Level 2 — Intermediate**

6. Write a function returning `str | None`, and write the correct
   caller-side narrowing code to safely use its result.
7. Rewrite an `Optional[int]`-annotated function signature into modern
   `int | None` syntax.
8. Define a `TypedDict` for a three-field record of your choosing, and
   write one function that accepts it and one that returns it.
9. Define a type alias for a domain concept in a project you're
   familiar with, and explain what readability benefit it provides.
10. Write a generic function using a `TypeVar` (or modern `[T]`
    syntax) that returns the last element of a `Sequence[T]`.
11. Write an `isinstance`-based narrowing example for a `str | int`
    parameter, handling both branches distinctly.

**Level 3 — Advanced**

12. Define a `Protocol` with two methods, and write two unrelated
    classes (no shared base class) that each satisfy it.
13. Write a bounded `TypeVar` (or `[T: SomeBase]` syntax) for a
    function that needs to call a specific method on its generic
    parameter.
14. Write a small `TypeGuard`-annotated helper function narrowing
    `list[object]` to `list[int]`.
15. Write a two-overload `@overload` declaration (plus its single real
    implementation) for a function whose return type depends on its
    input type.
16. Add `Self` to a fluent-style class with at least two chainable
    methods, and explain why `-> Self` is preferable to the class's own
    concrete name for a class that might later be subclassed.

**Level 4 — Production**

17. Take a small, previously-untyped mini-project (or a snippet of
    real, unannotated code you've written before) and annotate its
    public functions first, following §81's migration order.
18. Design typed module boundaries (following §53's pattern) for a
    two-module mini-project: one module owning data access, one owning
    business logic.
19. Type an API/service-layer function (following §64's pattern),
    including its inputs, its output, and at least one optional field.
20. Describe (in words, plus a short config snippet) how you'd
    introduce CI type checking (§83) into a project that currently has
    none.
21. Describe a plan (following §81) for migrating a partially-typed
    codebase — some modules fully annotated, others not at all — toward
    consistent, checked typing.

**Answer key**

1. A reasonable answer explains that a variable assigned directly from
   an obvious literal (`count = 0`) benefits little from an explicit
   annotation (§43's inference), while one assigned from a less
   obvious source, or meant to communicate an intended broader type
   (e.g. `tags: list[str] = []`), benefits genuinely (§5, §43).
2. The answer should show both a parameter annotation and a `->`
   return annotation, correctly matching the function's actual
   behavior (§6).
3. `-> None` states an explicit, verified promise that the function
   returns no meaningful value; omitting the annotation entirely
   leaves that unstated, relying purely on inference or a reader's own
   assumption (§7).
4. E.g. `names: list[str] = ["a", "b"]`, `ages: dict[str, int] =
   {"a": 1}`, `record: tuple[str, int, bool] = ("x", 1, True)` (§8–§9).
5. The answer should name the specific parameter and its declared
   type, and state precisely what type was actually passed instead
   (§45 item 2).
6. E.g.:
   ```python
   def find_name(user_id: int) -> str | None:
       ...

   name = find_name(1)
   if name is not None:
       print(name.upper())
   ```
   (§12, §26, §46).
7. `Optional[int]` → `int | None` — semantically identical; the
   modern form is preferred for a 3.10+ target (§12).
8. A reasonable `TypedDict` declares three named, typed fields; one
   function should accept it as a parameter, another should build and
   return one (§33).
9. Answers will vary; a strong answer names the specific readability
   or mix-up-prevention benefit (§14, §32).
10. E.g.:
    ```python
    def last[T](items: Sequence[T]) -> T:
        return items[-1]
    ```
    (§21–§23).
11. A reasonable answer branches on `isinstance(value, str)` /
    `isinstance(value, int)` (or an `else`), performing a distinct,
    type-appropriate operation in each branch (§26).
12. Two classes with no shared base class, each independently defining
    methods matching the `Protocol`'s own signatures exactly, both
    passed successfully to a function typed against the `Protocol`
    (§29–§30).
13. E.g. a bound requiring a `.total()` method, used inside the
    generic function's own body to call that method on the parameter
    (§24).
14. E.g.:
    ```python
    def is_int_list(items: list[object]) -> TypeGuard[list[int]]:
        return all(isinstance(item, int) for item in items)
    ```
    (§27).
15. Two `@overload`-decorated signatures (each with a `...` body),
    followed by one real, implementing function whose own signature is
    broad enough to cover both cases (§72).
16. `-> Self` correctly preserves the actual, possibly-subclassed
    calling type through a chained call, whereas the class's own
    concrete name would incorrectly "downcast" a subclass instance
    back to the base class in the type checker's eyes (§36).
17. The answer should demonstrate annotating the project's own public,
    externally-called functions before its private helpers, following
    §81's own stated order and reasoning.
18. A reasonable design shows one module's function signatures (data
    access) being consumed by another module's function signatures
    (business logic), with the contract between them expressed
    entirely through the annotated interface (§53).
19. A reasonable function signature includes a required input, a
    domain-typed output, and at least one `T | None`-typed optional
    field, explained per §64's own field-by-field breakdown.
20. A reasonable answer names running the checker locally first (in
    permissive mode, §42), then adding it as its own CI stage
    (§83), positioned after formatting/linting and before (or
    alongside) tests, gated on a non-zero exit code exactly like every
    other CI check in this course.
21. A reasonable plan explicitly sequences work using §81's own seven
    steps, prioritizing the currently-untyped modules with the
    clearest public boundaries first, and explains how gradual typing
    (§80) makes the *interim*, partially-typed state entirely valid to
    run a checker against, not an error condition in itself.

## 90. Mini Project — Production-Ready Typed Data Processing Service

**Requirements**: a typed data-processing pipeline, shown as code
inside this document (no files created), demonstrating domain models,
input validation, a `Protocol` for one external dependency, and static
type checking, following the exact pipeline shape this chapter has
used repeatedly:

```
raw input
    ↓  parse
    ↓  validate
typed representation
    ↓  transform
    ↓
output
```

**`models.py`-equivalent — domain types:**
```python
from dataclasses import dataclass
from typing import TypedDict


class RawRecord(TypedDict):
    id: str
    amount: str
    category: str


@dataclass
class ValidatedRecord:
    id: int
    amount: float
    category: str


@dataclass
class ProcessedRecord:
    id: int
    amount: float
    category: str
    amount_with_tax: float
```

**Validation — untrusted `RawRecord` to trusted `ValidatedRecord`,
following §48's own pipeline exactly:**
```python
def parse_record(raw: RawRecord) -> ValidatedRecord:
    try:
        record_id = int(raw["id"])
        amount = float(raw["amount"])
    except ValueError as exc:
        raise ValueError(f"invalid record {raw!r}: {exc}") from None

    if amount < 0:
        raise ValueError(f"amount must be non-negative, got {amount}")

    return ValidatedRecord(id=record_id, amount=amount, category=raw["category"])
```

**Transformation — pure, fully-typed business logic:**
```python
TAX_RATE = 0.08


def apply_tax(record: ValidatedRecord) -> ProcessedRecord:
    return ProcessedRecord(
        id=record.id,
        amount=record.amount,
        category=record.category,
        amount_with_tax=round(record.amount * (1 + TAX_RATE), 2),
    )
```

**A `Protocol` for one external dependency — a pluggable output
sink:**
```python
from typing import Protocol


class RecordSink(Protocol):
    def write(self, record: ProcessedRecord) -> None: ...


class ConsoleSink:
    def write(self, record: ProcessedRecord) -> None:
        print(record)


class InMemorySink:
    def __init__(self) -> None:
        self.records: list[ProcessedRecord] = []

    def write(self, record: ProcessedRecord) -> None:
        self.records.append(record)
```

**The pipeline, tying every stage together:**
```python
from collections.abc import Iterable


def run_pipeline(raw_records: Iterable[RawRecord], sink: RecordSink) -> int:
    processed_count = 0
    for raw in raw_records:
        try:
            validated = parse_record(raw)
        except ValueError as exc:
            print(f"skipping invalid record: {exc}")
            continue
        processed = apply_tax(validated)
        sink.write(processed)
        processed_count += 1
    return processed_count
```

**A test, using `InMemorySink` — exactly §69–§70's testing benefit,
realized concretely:**
```python
def test_run_pipeline_applies_tax() -> None:
    raw_records: list[RawRecord] = [{"id": "1", "amount": "100.0", "category": "books"}]
    sink = InMemorySink()

    count = run_pipeline(raw_records, sink)

    assert count == 1
    assert sink.records[0].amount_with_tax == 108.0
```

**Why type hints improve each boundary, stage by stage**: `RawRecord`
(a `TypedDict`) precisely documents the untrusted input's expected
shape, without pretending it's already trustworthy (§33, §49);
`parse_record`'s signature (`RawRecord -> ValidatedRecord`) makes the
validation boundary itself a checkable, unambiguous contract (§48);
`ValidatedRecord` and `ProcessedRecord` being genuinely distinct types
(not the same class reused) means it's a *type error*, not just a
convention, to accidentally call `apply_tax` on data that skipped
validation (directly realizing §66's own pipeline-stage-typing
principle); and `RecordSink` as a `Protocol` means `run_pipeline`
never needs to know or care whether it's writing to a console, memory
(for testing, as shown), a file, or a database — exactly §69–§70's
dependency-injection benefit, now demonstrated end to end in one
complete, working pipeline. Running Ruff (per
[05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md))
and a static type checker (§39, §83) against this exact code, as two
independent CI stages, alongside the test shown above, completes the
full quality-assurance stack this chapter's §60 and §95 (final mental
model) both describe.

## 91. Interview Questions

**Beginner**
1. What are type hints?
2. What is dynamic typing?
3. What is static type checking?
4. Do type hints enforce runtime types?
5. What does `-> str` mean?

**Intermediate**
6. `Optional` vs. `Union`?
7. `list[str]` vs. `list[Any]`?
8. `Any` vs. `object`?
9. `TypedDict` vs. `dataclass`?
10. Type alias vs. `NewType`?

**Advanced**
11. What is `TypeVar`?
12. What is `Generic`?
13. What is `Protocol`?
14. What is structural typing?
15. What is `TypeGuard`?
16. What is `overload`?
17. What is `ParamSpec`?

**Production**
18. How would you introduce typing into a legacy Python project?
19. How would you design a typing strategy for a large repository?
20. How would you combine Ruff, type checking, and tests?
21. How would you type external API boundaries?
22. How would you use `Protocol` to decouple services?

**Answer key**

1. Annotations stating the intended type of a variable, parameter, or
   return value — documentation-as-code that a static checker can
   verify, with no inherent runtime effect of its own (§3).
2. A variable's type is determined by whatever value it currently
   holds, checked at the moment an operation runs, rather than fixed
   by a prior declaration — Python's own model (§2).
3. A separate tool reading annotated source code, without executing
   it, to verify type consistency before the program ever runs (§2,
   §39).
4. No — Python itself executes annotated code exactly as it would
   unannotated code; only a static checker reads and verifies
   annotations, entirely separately from execution (§4).
5. This function's declared return type is `str` — a promise, checked
   statically, about what the function is expected to produce (§7).
6. `Optional[str]` is exactly equivalent to `str | None` — "this, or
   `None`"; `Union[int, str]` (or `int | str`) is the general form for
   "one of several specific types," of which `Optional` is a special,
   `None`-specific case (§12–§13).
7. `list[str]` is a precisely homogeneous list a checker can verify
   element usage against; `list[Any]` disables that verification
   entirely for every element, functioning close to an unannotated
   list (§8, §17).
8. `object` is a real type every value genuinely is; a checker still
   verifies operations against it (very little is valid without
   narrowing). `Any` is a marker that disables checking entirely for
   that value (§17–§18).
9. `TypedDict` describes the shape of a plain `dict` at the type
   level, with no runtime enforcement and no real object created;
   `dataclass` generates a genuine class with real attribute access,
   equality, and `repr`, at real runtime cost (§33–§34).
10. A plain type alias creates no new type at all (identical to the
    underlying type); `NewType` creates a genuinely distinct static
    type, preventing accidental mix-ups between two same-underlying-
    type values, at minimal runtime cost (§14, §74).
11. A placeholder representing "whatever specific type is used at a
    given call site," letting a function's return type (or other
    parameters) be expressed as depending on its input type, rather
    than fixed or `Any` (§21).
12. A class (or function) parameterized by one or more type variables,
    letting the same implementation work precisely, and be separately
    verified, for many different concrete types (§22).
13. A way of declaring a structural, behavioral contract ("anything
    with these methods") without requiring inheritance — satisfied by
    any class whose methods structurally match, regardless of its
    declared class hierarchy (§29).
14. Type compatibility determined by what an object can actually do
    (its methods/attributes), rather than by what it's explicitly
    declared to inherit from — Python's own long-standing duck-typing
    principle, made checkable via `Protocol` (§29–§30).
15. A specially-annotated function whose `bool` return value, when
    `True`, tells a static checker it may narrow its argument to a more
    specific type — used when `isinstance` alone can't express the
    needed check (§27).
16. A way to declare multiple type-level signatures for one function,
    each pairing a specific input type with a specific, more precise
    return type, backed by exactly one real runtime implementation
    (§72).
17. A type variable capturing an entire callable's parameter
    signature (not just one value's type), primarily used to preserve
    a wrapped function's exact signature through a decorator (§77).
18. Following §81's staged plan: identify critical modules, annotate
    public functions and boundaries first, reduce `Any` over time,
    introduce a checker in permissive mode, fix diagnostics
    incrementally, and increase strictness gradually.
19. Define an explicit team policy (§82) covering required
    annotations, strictness level, an `Any` policy, stricter public-
    API requirements, and CI enforcement — calibrated to the
    repository's actual size and maturity, not a single universal
    answer.
20. Run all three as independent, gated CI stages (§59, §60, §83) —
    Ruff for formatting/linting, a static checker for type
    consistency, and tests for actual behavior — with none
    substituting for either of the others.
21. Model the raw, untrusted external data precisely (a `TypedDict` or
    equivalent), validate it explicitly at the boundary, and convert
    it into a trusted, typed internal representation before any
    business logic touches it (§48–§49, §64–§65).
22. Define a `Protocol` describing exactly the behavior a dependency
    (a model client, a repository, a notification sender) needs to
    provide, and depend on that protocol everywhere instead of a
    concrete implementation — letting implementations be swapped or
    faked for testing with zero coupling (§69–§70).

## 92. Architecture Questions

1. **Where should type checking occur in CI?** As its own, independent
   stage — after formatting/linting (cheap, fast, worth failing on
   first) and before or alongside tests — gated on a non-zero exit
   code exactly like every other CI check this course has established
   (§83).
2. **Which module boundaries should be strongly typed?** Every
   boundary where one module's data becomes another module's input —
   public package APIs (§54) and the specific points where untrusted
   external data (JSON, CLI input, environment variables, database
   rows) crosses into the application's own trusted, validated domain
   (§48).
3. **How should an AI platform type model providers?** Via a shared
   `Protocol` (e.g. `ModelClient`, §69) describing exactly the
   behavior every provider must support — letting the platform's own
   orchestration code depend on that behavioral contract, never on
   any one specific provider's SDK, and letting new providers (or
   fakes, for testing) be added with zero change to existing code.
4. **How can `Protocol` support model-provider abstraction
   specifically?** By expressing "anything that can `generate(prompt)
   -> str`" (or an equivalent contract) structurally — every concrete
   provider client satisfies it independently, with no shared
   inheritance and no coordination between provider implementations
   required (§69).
5. **How should a data pipeline represent raw vs. validated data?**
   With genuinely distinct types for each pipeline stage (§66) — a
   `TypedDict` or similar for untrusted raw input, and a separate
   `dataclass` (or equivalent) for validated data — so that skipping
   validation and passing raw data directly into a stage expecting
   validated data becomes an actual, caught type error, not merely an
   undocumented convention.
6. **How should a large monorepo gradually adopt strict typing?**
   Module by module, prioritizing modules with the clearest, most
   consequential public boundaries first (§81), using permissive mode
   initially (§42) and increasing strictness only for the portions
   already annotated and stabilized, exactly mirroring
   [05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)'s
   own §38 monorepo-adoption guidance for linting.
7. **How should typed interfaces be designed between services?**
   Each service's own request/response shapes modeled explicitly
   (`TypedDict`/`dataclass`, §64–§65), with `None`/optional fields
   stated honestly (§46) rather than assumed present, and any service-
   to-service dependency expressed as a `Protocol` (§70) wherever the
   concrete implementation might reasonably vary or need to be faked
   for isolated testing.

## 93. Knowledge Check

1. What is a type, and why does Python care about types even without
   requiring declarations?
2. What is the difference between dynamic typing and static type
   checking?
3. What does a type hint do, precisely, and what does it not do?
4. What is the difference between an annotation and runtime
   validation?
5. Predict the output/behavior: `age: int = "5"; print(type(age))`.
6. What does `list[str]` communicate that a bare `list` does not?
7. What is the difference between `tuple[str, int]` and `tuple[str,
   ...]`?
8. What is `Optional[str]`'s modern equivalent?
9. Why can a union type become "too broad"?
10. What is a type alias, and what does it *not* create?
11. What does `Any` disable, and why is it described as "contagious"?
12. Why is `object` often a safer choice than `Any` for an unknown
    value?
13. What does `Never` (or `NoReturn`) communicate about a function?
14. What is `Callable[[int, int], int]`?
15. What problem does `TypeVar` solve that `Any` does not?
16. What is the difference between a bounded and a constrained
    `TypeVar`?
17. What must be true for a static checker to narrow a value's type
    inside an `if` branch?
18. What does `TypeGuard` let a custom function communicate to a
    checker?
19. What is structural typing, and how does `Protocol` implement it?
20. How does an ABC's guarantee differ from a `Protocol`'s?
21. What does `TypedDict` model, and is it a real runtime type?
22. What does `@dataclass` provide that a `TypedDict` does not?
23. What is `ClassVar` for?
24. Why is `-> Self` sometimes preferable to a class's own concrete
    name as a return type?
25. What is a forward reference, and why is it sometimes necessary?
26. What is `__annotations__`, and how does it differ from static
    checking?
27. Does a static type checker execute your program?
28. What is type inference, and when does explicit annotation still
    add value despite it?
29. What does `reveal_type(...)` do, and can it be called at runtime
    in production code?
30. Name three categories of common type-checking error.
31. Why is `None`-safety specifically important at system boundaries?
32. Why don't type hints validate JSON, CLI input, or environment
    variables by themselves?
33. What is `py.typed`, and what does it signal?
34. What is the practical effect of an untyped third-party dependency
    on your own application's type safety?
35. How does Ruff differ from a static type checker?
36. Why can a function pass a type checker completely and still
    contain a real bug?
37. How do type hints function as documentation, beyond a plain
    docstring?
38. What does `overload` require in addition to its `@overload`-
    decorated signatures?
39. What does `cast()` actually do, and what does it not do?
40. Why should CI independently run type checking, rather than trusting
    local developer checks alone?

**Answer key**

1. A type is a category of data determining what operations are
   valid; Python cares because every value has one, checked at the
   moment an operation is actually attempted (§1–§2).
2. Dynamic typing is Python's own runtime behavior — types checked as
   code executes, with no declared, fixed type required in advance;
   static type checking is a separate, optional process reading code
   *before* it runs, verifying declared/inferred types for consistency
   (§2).
3. It documents intended type information, checkable by a static
   checker; it does not itself convert values, validate them at
   runtime, or change what Python actually executes (§3–§4).
4. An annotation is static, unenforced documentation; runtime
   validation is actual, executed code that checks (and can reject) a
   value while the program runs (§4, §48).
5. `age` is bound to the string `"5"` at runtime, unaffected by the
   `int` annotation; `type(age)` prints `<class 'str'>` (§4).
6. `list[str]` communicates that every element is specifically a
   `str`, letting a checker verify element usage; a bare `list` gives
   no such guarantee (§8).
7. `tuple[str, int]` is a fixed-length, two-element, heterogeneous
   tuple; `tuple[str, ...]` is a variable-length tuple of any size,
   every element a `str` (§9).
8. `str | None` (§12).
9. Because each additional member widens what's accepted and narrows
   what can be assumed without further narrowing — a union with many
   members starts communicating little more than `Any` (§13).
10. It gives an existing type a new, more readable name; it does not
    create a genuinely new or distinct type (§14).
11. It disables static checking for that value entirely; it's
    "contagious" because everything derived from an `Any`-typed value
    (attribute access, indexing, further calls) also becomes `Any`
    (§17).
12. `object` still lets a checker enforce that you narrow the value
    before doing anything type-specific with it; `Any` allows any
    operation, silently, with no such requirement (§18).
13. That the function never returns normally — every path either
    raises or loops forever (§19).
14. A type for a callable taking two `int` parameters and returning an
    `int` (§20).
15. `TypeVar` preserves the actual relationship between an input's
    type and an output's type across a call; `Any` discards that
    relationship entirely, providing no type information at all (§21).
16. A bound (`T: SomeBase`) accepts any subtype of a given type; a
    constraint (`TypeVar("T", int, float)`) accepts only one of an
    explicit, closed list of exact types, with no subtyping implied
    (§24–§25).
17. The checker must be able to follow the code's actual control flow
    and see a recognized narrowing check (`isinstance`, `is None`,
    `assert`, or similar) governing that specific branch (§26).
18. That, when the function returns `True`, its argument may be safely
    narrowed to the more specific type declared in `TypeGuard[...]`
    (§27).
19. Compatibility determined by an object's actual methods/attributes
    rather than its declared class; `Protocol` implements it by
    checking any class's methods against a protocol's declared
    signatures, with no inheritance required (§29).
20. An ABC enforces completeness (every `@abstractmethod` implemented)
    at runtime, via required, explicit inheritance; a `Protocol`
    provides no runtime enforcement by default and requires no
    inheritance at all (§30–§31).
21. It models the shape of a plain dictionary — specific keys, each
    with its own type; at runtime, a `TypedDict`-typed value is just an
    ordinary `dict`, with no distinct runtime type or enforcement of
    its own (§33).
22. Real attribute access, an auto-generated `__init__`/`__repr__`/
    `__eq__`, and a genuinely distinct runtime object type — none of
    which `TypedDict` provides (§34).
23. Declaring a class-level attribute (shared across all instances)
    explicitly, distinguishing it from an ambiguous, possibly-intended-
    as-per-instance annotation (§35).
24. Because it correctly preserves the actual, possibly-subclassed
    calling type through a chained method call, whereas the base
    class's own concrete name would incorrectly narrow a subclass
    instance back to the base class (§36).
25. A string-quoted (or `from __future__ import annotations`-enabled)
    reference to a type not yet fully defined at the point it's
    written — necessary for self-referential classes or types defined
    later in the same module (§37).
26. `__annotations__` is a real, runtime-inspectable dictionary
    attribute holding a function's/class's own annotations; static
    checking is a separate process that never touches this attribute
    at all, working purely from source text analysis (§38–§39).
27. No — never. It reads and analyzes source code without executing
    any of it (§39, §41).
28. Type inference is a checker's ability to determine a type from
    context (e.g. a literal value) without an explicit annotation;
    explicit annotation still adds value at boundaries with no
    adjacent literal to infer from — function parameters, return
    types, and variables whose intended type is broader than an
    initial value alone suggests (§43).
29. It reports what a checker has inferred a value's type to be,
    directly in the checker's own diagnostic output; it is not a real
    runtime function and raises `NameError` if actually executed
    (§44).
30. Any three of: incompatible assignment, wrong argument type, wrong
    return type, missing attribute, possible `None`, incompatible
    container types, incorrect callable signature, invalid dictionary
    access, unreachable branches (§45).
31. Because a value that might legitimately be absent (a database
    lookup, an API field, a config setting, a cache miss) is one of
    the most common real sources of production runtime errors when
    used without first checking for `None` (§46).
32. Because type hints are purely static, unenforced documentation
    (§4); actual validation of untrusted, external data requires real,
    executed runtime code, exactly as
    [09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)
    established (§48).
33. A marker file signaling that a package's own inline annotations
    are complete and accurate enough for a static checker to trust and
    verify calls against (§57).
34. Every call into the untyped portion effectively becomes `Any`,
    silently weakening your own application's static guarantees at
    that specific boundary, regardless of how carefully your own code
    is typed (§55, §58).
35. Ruff performs fast, pattern-based structural/style checks with no
    deep type inference; a static type checker performs deep,
    whole-codebase type-consistency analysis, following how values
    flow through the program — genuinely different, complementary
    layers (§59).
36. Because a checker only verifies type *consistency*, never
    *correctness* of the actual logic/arithmetic/business rules — a
    function can be perfectly type-consistent while still computing
    the wrong result (§60).
37. Type hints are structured, machine-readable information a tool can
    actively use (autocomplete, inline diagnostics, signature help,
    §62), and are automatically checked for consistency with actual
    usage — properties a free-text docstring alone does not have
    (§61–§62).
38. Exactly one real, non-decorated implementation whose own signature
    is broad enough to cover every declared `@overload` case (§72).
39. It tells the static checker to treat a value as a specific type,
    purely for checking purposes; it performs no runtime conversion
    and no runtime validation at all (§73).
40. Because local checks depend entirely on each individual
    developer's setup and diligence; CI independently re-verifies the
    exact same check, in a clean, reproducible environment, regardless
    of what happened (or didn't) on any one developer's own machine
    (§83).

## 94. Glossary

- **Type** — a category of data determining what operations are valid
  on a value (§1).
- **Type system** — the overall set of rules governing how types
  behave and interact in a language; Python has a rich one, layered
  with optional static checking (§2).
- **Dynamic typing** — a variable's type determined by its current
  value, checked at the moment an operation runs (§2).
- **Static typing** — types declared and checked before a program
  runs; not Python's default runtime behavior, but supported as an
  optional, separate analysis layer (§2, §39).
- **Type hint / type annotation** — syntax stating a variable's,
  parameter's, or return value's intended type; pure documentation-as-
  code by default (§3).
- **Type checker** — a separate tool that statically analyzes
  annotated source code for type consistency, without executing it
  (§39).
- **Static analysis** — examining source code's text/structure without
  running it (§39).
- **Type inference** — a checker deriving a type from context (e.g. a
  literal) without an explicit annotation (§43).
- **Type narrowing** — a checker refining a value's believed type
  based on runtime checks your code performs (`isinstance`, `is None`,
  and similar) (§26).
- **Generic** — a function or class parameterized by one or more type
  variables, working precisely for many different concrete types
  (§22).
- **`TypeVar`** — a placeholder representing "whatever specific type
  is used at a given call site" (§21).
- **`Protocol`** — a structural, behavioral type contract, satisfied by
  any class with matching methods, with no inheritance required (§29).
- **Structural typing** — type compatibility determined by an object's
  actual behavior/shape, not its declared class (§29).
- **Nominal typing** — type compatibility determined by an explicit,
  named class relationship (inheritance) (§30).
- **`TypedDict`** — a type describing the shape of a plain `dict`,
  with no runtime enforcement (§33).
- **`Callable`** — a type describing a function's (or other callable's)
  parameter and return types (§20).
- **`Any`** — a marker disabling static type checking for a value
  entirely (§17).
- **`object`** — the real base type every Python value is an instance
  of; still fully type-checked, unlike `Any` (§18).
- **`Optional`** — `Optional[T]`, equivalent to `T | None` — "this, or
  `None`" (§12).
- **`Union`** — `Union[A, B]`, equivalent to `A | B` — "one of these
  specific types" (§13).
- **`TypeGuard`** — a return-type annotation letting a custom function
  narrow its argument's type in the caller, on a `True` result (§27).
- **`TypeIs`** — a newer (3.13+) alternative to `TypeGuard`, correctly
  narrowing both the positive and negative branches (§28).
- **`overload`** — a decorator declaring multiple input-to-output type
  pairings for one function, backed by a single real implementation
  (§72).
- **`ParamSpec`** — a type variable capturing an entire callable's
  parameter signature, primarily used to preserve a wrapped function's
  signature through a decorator (§77).
- **`cast`** — tells a static checker to treat a value as a specific
  type; performs no runtime conversion or validation (§73).
- **`NewType`** — creates a genuinely distinct static type from an
  existing one, preventing accidental value mix-ups, at minimal
  runtime cost (§74).
- **`Literal`** — restricts a value to one of a specific, finite set of
  exact values, not just a type (§15).
- **`Final`** — communicates (statically) that a name should never be
  reassigned after its initial assignment (§75).
- **`ClassVar`** — declares a class-level (shared) attribute, distinct
  from a per-instance one (§35).
- **`Self`** — a return-type annotation preserving the actual,
  possibly-subclassed calling type through a method (§36).
- **`Annotated`** — attaches extra, tool-specific metadata to a type,
  inert by default unless a specific framework reads and acts on it
  (§76).
- **Stub (`.pyi`)** — a file containing only type information, no
  implementation, describing a module's types separately from its
  actual code (§56).
- **`py.typed`** — a marker file signaling that a package's inline
  annotations are trustworthy for a checker to verify against (§57).
- **Gradual typing** — the design principle allowing typed and
  untyped code to coexist, with a project adopting annotations
  incrementally rather than all at once (§80).

## 95. Final Mental Model

```
WRITE PYTHON CODE
    ↓
ADD TYPE INFORMATION            (§3–§38 — variables, functions, collections, generics, protocols, ...)
    ↓
STATIC TYPE CHECKER               (§39 — reads the code; never runs it)
    ↓
FIND TYPE-RELATED PROBLEMS          (§40–§47 — diagnostics, None-safety, narrowing)
    ↓
FIX CODE
    ↓
RUFF FORMAT/LINT                        (§59 — a separate, complementary layer)
    ↓
RUN TESTS                                 (§60 — verifies actual behavior)
    ↓
CI VALIDATION                               (§83 — independently re-verifies everything above)
    ↓
PRODUCTION
```

The critical distinction this entire chapter has built toward, stated
one final time, in full, as five separate, non-overlapping
responsibilities:

- **Type hints communicate intent.** They are documentation, written
  as code, read by both humans and tools — with no inherent runtime
  effect of their own (§3–§4).
- **Type checkers analyze code statically.** They verify that
  declared and inferred types are used consistently, across an entire
  codebase, without ever executing a single line of it (§39–§41).
- **Runtime validation protects system boundaries.** Only actual,
  executed code — never an annotation — can reject or convert data
  that doesn't match expectations, and this is where untrusted,
  external input (JSON, CLI arguments, environment variables, database
  rows) must always be handled (§48).
- **Tests verify behavior.** Only running code against known inputs
  and checking the actual output confirms that logic — not just type
  consistency — is correct (§60).
- **Ruff enforces formatting and linting.** A fast, complementary
  layer catching structural and stylistic issues type checking was
  never designed to address (§59, and
  [05-ruff-formatting-and-linting.md](05-ruff-formatting-and-linting.md)
  in full).

## Final Takeaways

Type hints do not make Python "statically typed" in the way a
compiled language is — Python remains, and will remain, dynamically
typed at its core, running exactly the same code whether it's
annotated or not. What type hints *do* provide is an optional,
genuinely powerful layer of **communicated intent** — precise,
checkable documentation of what every function, variable, and class
actually expects and promises — that a static type checker can verify
automatically, across an entire codebase, catching an entire category
of mistake (type inconsistency) before a single test is ever run or a
single user is ever affected. None of this replaces runtime
validation at real system boundaries, and none of it replaces tests
verifying that your logic is actually correct, not just consistent —
each of the five layers in §95's final mental model earns its place by
catching something none of the others structurally can. The habit
worth carrying forward from this chapter, and from this whole module,
is the same one repeated at every layer: write code, communicate its
contracts explicitly and precisely, let automated tooling verify those
contracts continuously, and reserve human judgment for exactly the
things — is this the right design, is this logic actually correct —
that no tool, however sophisticated, can determine on its own.





