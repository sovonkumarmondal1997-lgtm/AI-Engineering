# Operator and Functional Composition

> **Target:** Python 3.12+  
> **Module:** Stage 1 — Programming & Computational Thinking → `13-Standard-Library-Toolkit/` → Lesson 02  
> **Focus:** `operator`, key extractors, callable composition, reusable transformations, sorting, and production data pipelines.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain why Python's `operator` module exposes language operations as ordinary callables.
- Use `itemgetter`, `attrgetter`, and `methodcaller` with `sorted`, `max`, `map`, and `itertools.groupby`.
- Choose between an operator function, a lambda, direct attribute access, and a comprehension based on clarity.
- Use `reduce` appropriately while preferring clearer built-ins when they express the intent.
- Implement and test right-to-left `compose` and left-to-right `pipe` functions.
- Use `partial` to bind arguments, and distinguish in-place operators from ordinary operators.
- Sort by mixed ascending/descending priorities without relying on unsafe key negation.
- Design a typed, testable transformation pipeline with explicit error and mutation behavior.
- Understand pickling constraints and measure performance without treating one benchmark as a universal truth.

### Prerequisites

You should already understand functions and return values, first-class functions, iterables, dictionaries, tuples, mutability and aliasing, exceptions, type hints, and basic unit testing. Familiarity with `functools.partial` and `reduce`, generators, and the Python object model will help.

**Scope boundary:** this lesson uses `functools` and `itertools` where they help explain composition and data transformations; it does not replace the dedicated lessons on higher-order functions, `functools`, or iteration recipes. It also does not attempt to teach operator overloading in full: the data model connection is introduced here and developed in the advanced object-model lessons.

## 2. Foundations: first-class functions and callable objects

Python functions are values. You can assign a function to a name, store it in a collection, return it from another function, or pass it as an argument. An object is callable if it supports the call operation, typically through `__call__`.

```python
def double(value: int) -> int:
    return value * 2

operation = double                 # no parentheses: keep the function object
print(operation(7))                 # 14
print(sorted([("ana", 31), ("bo", 25)], key=lambda row: row[1]))
# [('bo', 25), ('ana', 31)]
```

`key=` expects a callable that receives one item and returns a value used for ordering. `map(function, iterable)` calls a function for each item and returns a lazy iterator. `max(iterable, key=...)` uses a key function to compare items but returns the original winning item. `itertools.groupby(iterable, key=...)` groups *adjacent* items whose keys compare equal; sort first when you need all equal keys together.

A callable object can also hold configuration:

```python
from operator import itemgetter

by_age_then_name = itemgetter(1, 0)
print(by_age_then_name(("ana", 31)))  # (31, 'ana')
```

**Why this matters:** APIs that accept callables let you separate *what operation to perform* from *which data to process*. Small reusable callables are useful in sorting, ETL, validation, mapping, and test code. The trade-off is that overly abstract chains can hide control flow; a clear loop is often better than a clever expression.

## 3. Beginner level: operator functions

The `operator` module provides function equivalents for many Python operators and common item/attribute/method access patterns. Instead of writing a small lambda such as `lambda a, b: a + b`, you can pass `operator.add` directly.

```python
from operator import add, mul, eq, lt, not_, contains, getitem

print(add(4, 5))                         # 9
print(mul(4, 5))                         # 20
print(eq("ready", "ready"))             # True
print(lt(3, 8))                          # True
print(not_(0))                           # True
print(contains(["a", "b"], "b"))        # True
print(getitem({"region": "west"}, "region"))  # west
```

### 3.1 The most useful functions

| Function | Equivalent expression | Practical use |
|---|---|---|
| `operator.add(a, b)` | `a + b` | Generic addition or reduction |
| `operator.mul(a, b)` | `a * b` | Multiplication or product reduction |
| `operator.eq(a, b)` | `a == b` | Predicate or configurable comparison |
| `operator.lt(a, b)` | `a < b` | Explicit less-than comparator logic |
| `operator.not_(x)` | `not x` | Invert truthiness as a callable |
| `operator.contains(container, item)` | `item in container` | Callable membership check |
| `operator.getitem(obj, key)` | `obj[key]` | Generic item lookup |

**Argument order matters:** `contains(container, item)` is equivalent to `item in container`, not `container in item`. Likewise, `getitem(obj, key)` receives the object first and key second.

`not_` returns the Boolean inverse of truthiness; it is not the same as bitwise inversion `~x`. `eq` and `lt` follow the behavior of the underlying objects, including any custom comparison methods.

### 3.2 Operator function or lambda?

```python
from operator import add

values = [10, 20, 30]
print(list(map(lambda value: value + 1, values)))  # [11, 21, 31]
print(list(map(add, values, [1, 1, 1])))           # [11, 21, 31]
```

`map(add, ...)` passes corresponding elements from its iterables to `add`. It is concise when the operation is already named and has the right signature. A lambda is more flexible when the logic is specific, such as `lambda row: row["price"] * row["quantity"]`. Direct expressions and comprehensions are often clearer than either option for simple transformations:

```python
squares = [value * value for value in values]
```

Do not replace a readable comprehension with a complicated functional expression merely to avoid a loop.

## 4. Key extractors and method callers

Key extractors create callables that fetch data from each input. They are especially useful with APIs that accept `key=` or a mapping function.

### 4.1 `itemgetter`: sequence and mapping access

`itemgetter(key)` returns a callable that retrieves one item. `itemgetter(key1, key2, ...)` returns a tuple of the requested values in the specified order.

```python
from operator import itemgetter

people = [("ana", 31), ("bo", 25), ("cy", 31)]
print(sorted(people, key=itemgetter(1, 0)))
# [('bo', 25), ('ana', 31), ('cy', 31)]

records = [
    {"id": 3, "dept": "data", "salary": 120},
    {"id": 1, "dept": "platform", "salary": 150},
    {"id": 2, "dept": "data", "salary": 135},
]
print(list(map(itemgetter("id", "dept"), records)))
# [(3, 'data'), (1, 'platform'), (2, 'data')]
print(sorted(records, key=itemgetter("dept", "id")))
# [{'id': 2, 'dept': 'data', 'salary': 135},
#  {'id': 3, 'dept': 'data', 'salary': 120},
#  {'id': 1, 'dept': 'platform', 'salary': 150}]
```

For one key, the result is that value. For multiple keys, the result is a tuple. A missing dictionary key raises `KeyError`, just as direct indexing does; `itemgetter` does not provide a default value.

### 4.2 `attrgetter`: attributes and nested attributes

`attrgetter("name")` retrieves an attribute. A dotted name such as `"owner.name"` follows nested attribute access. Multiple names return a tuple.

```python
from dataclasses import dataclass
from operator import attrgetter

@dataclass
class Owner:
    name: str

@dataclass
class Job:
    owner: Owner
    priority: int

jobs = [Job(Owner("Mira"), 2), Job(Owner("Ari"), 1)]
print([attrgetter("owner.name")(job) for job in jobs])
# ['Mira', 'Ari']
print([(job.owner.name, job.priority)
       for job in sorted(jobs, key=attrgetter("priority", "owner.name"))])
# [('Ari', 1), ('Mira', 2)]
```

Attribute lookup errors propagate, usually as `AttributeError`. `attrgetter` is a good fit for ordinary attribute access; it is not a general query language and does not safely handle missing attributes by itself.

### 4.3 `methodcaller`: call a named method

`methodcaller(name, *args, **kwargs)` creates a callable that invokes the named method on the object it receives. The positional and keyword arguments are stored when the callable is created.

```python
from operator import methodcaller

normalise = methodcaller("strip")
replace_spaces = methodcaller("replace", " ", "_")
print(list(map(normalise, ["  alpha ", " beta  "])))
# ['alpha', 'beta']
print(replace_spaces("data engineering"))
# data_engineering
print(list(map(methodcaller("upper"), ["a", "b"])))
# ['A', 'B']
```

The method is looked up and invoked on each input object. If the method is missing or raises an exception, that exception propagates. For complex transformations that need branching or several steps, a named function is usually easier to read and debug.

### 4.4 Supplying key functions to standard APIs

```python
from itertools import groupby
from operator import itemgetter

rows = [
    {"dept": "data", "name": "Ana", "score": 9},
    {"dept": "platform", "name": "Bo", "score": 7},
    {"dept": "data", "name": "Cy", "score": 8},
]
by_dept = itemgetter("dept")
ordered = sorted(rows, key=by_dept)
print(max(rows, key=itemgetter("score"))["name"])  # Ana
print(list(map(itemgetter("name"), rows)))           # ['Ana', 'Bo', 'Cy']
for dept, group in groupby(ordered, key=by_dept):
    print(dept, [row["name"] for row in group])
# data ['Ana', 'Cy']
# platform ['Bo']
```

`groupby` produces groups only for consecutive equal keys. Sorting by the same key first is the usual approach when all records for a key must be in one group. Each group is an iterator sharing the underlying source; consume a group before advancing to the next one, or materialize it deliberately.

### 4.5 Choosing among direct access, lambda, and getters

| Form | Example | Prefer it when |
|---|---|---|
| Direct access | `row["id"]` | You are transforming one known record inline |
| `itemgetter` | `itemgetter("id")` | A reusable item lookup is needed, especially as `key=` |
| `attrgetter` | `attrgetter("owner.name")` | A reusable attribute/nested-attribute lookup is needed |
| `methodcaller` | `methodcaller("strip")` | The same method call is applied to many values |
| Lambda | `lambda row: row["qty"] * row["price"]` | The key or transformation is an expression not represented by one getter |
| Named function | `def net(row): ...` | Logic deserves a name, validation, branching, documentation, or tests |

The standard getters are often concise and can be pickled in common cases, but do not assume they are always faster for every input or Python version. Measure representative workloads before optimizing.

## 5. Intermediate level: reduction and partial application

### 5.1 `functools.reduce` with `operator`

`reduce(function, iterable)` repeatedly combines items into one result. With no initializer, it starts from the first item and therefore fails on an empty iterable. With an initializer, that value is used even when the iterable is empty.

```python
from functools import reduce
from operator import add, mul

print(reduce(add, [1, 2, 3, 4]))       # 10
print(reduce(mul, [1, 2, 3, 4], 1))    # 24
print(reduce(add, [], 0))              # 0
```

For simple sums and products, `sum(values)` and `math.prod(values)` generally express intent more clearly. `any()` and `all()` express existential and universal conditions and short-circuit; they are clearer than reducing Booleans manually.

```python
import math

values = [2, 3, 4]
print(sum(values))                    # 9
print(math.prod(values))              # 24
print(any(value < 0 for value in values))  # False
print(all(value > 0 for value in values))  # True
```

Use `reduce` when the operation genuinely describes a fold that lacks a clearer built-in, or when the accumulator is a domain-specific structure. Be careful about operation order and associativity. Floating-point addition can vary slightly with grouping because it is not mathematically associative under finite precision.

### 5.2 `functools.partial`: fix selected arguments

`partial(function, *args, **kwargs)` returns a callable with some arguments pre-bound. It is useful for configuring reusable transformations without introducing a wrapper function for every configuration.

```python
from functools import partial
from operator import mul

def apply_discount(price: float, rate: float) -> float:
    return price * (1 - rate)

triple = partial(mul, 3)
print(triple(7))  # 21

round_to_2 = partial(round, ndigits=2)
print(round_to_2(3.14159))  # 3.14

# Fix a named argument to create a configured transformation.
with_discount = partial(apply_discount, rate=0.10)
print(with_discount(50.0))  # 45.0

from operator import itemgetter
region_of = itemgetter("region")
print(region_of({"region": "west"}))  # west
```

The `partial` object prepends stored positional arguments and merges stored keyword arguments with call-time keywords (call-time values override matching stored keyword values). It does not validate domain-specific constraints by itself. Prefer a named function when the configuration needs a meaningful name or custom validation.

## 6. Function composition and pipeline design

Composition combines functions so that one function's output becomes another function's input. The words `compose` and `pipe` are conventions rather than built-in Python APIs:

- **`compose(f, g)(x)`** conventionally means `f(g(x))`: evaluate right to left.
- **`pipe(x, f, g)`** conventionally means `g(f(x))`: start with a value and apply functions left to right.

The direction is a design choice. Document it and test it explicitly; composition bugs can produce plausible but incorrect data.

### 6.1 A small, explicit implementation

This implementation deliberately supports only unary functions. It treats an empty composition as the identity function and an empty pipe as the original value. This is convenient for building pipelines dynamically.

```python
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")

# Heterogeneous function chains are difficult to express perfectly with
# ordinary Callable annotations; Any marks the boundary of this small helper.
Unary = Callable[[Any], Any]

def compose(*functions: Unary) -> Unary:
    """Return a callable that applies functions right to left."""
    def composed(value: Any) -> Any:
        result = value
        for function in reversed(functions):
            result = function(result)
        return result
    return composed

def pipe(value: T, *functions: Callable[[Any], Any]) -> Any:
    """Apply functions to value from left to right; empty pipe is identity."""
    result: Any = value
    for function in functions:
        result = function(result)
    return result

clean_name = compose(
    lambda text: text.replace(" ", "_"),
    str.lower,
    str.strip,
)
print(clean_name("  Hello World  "))  # hello_world
print(pipe("  Hello World  ", str.strip, str.lower,
           lambda text: text.replace(" ", "_")))  # hello_world
print(compose()(42))                  # 42
print(pipe(42))                       # 42
print(compose(lambda x: x + 1)(3))     # 4
print(pipe(3, lambda x: x + 1))        # 4
print(compose(lambda x: x * 2, lambda x: x + 3)(4))  # 14
print(pipe(4, lambda x: x + 3, lambda x: x * 2))     # 14
```

**Order walkthrough:** in `compose(lambda x: x * 2, lambda x: x + 3)(4)`, the rightmost function runs first: `4 + 3 = 7`, then `7 * 2 = 14`. In `pipe(4, add_three, double)`, `add_three` runs first and `double` second.

An equivalent reduce-based `compose` can be concise but often harder to reason about:

```python
from functools import reduce

def compose_reduce(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions,
                  lambda x: x)

print(compose_reduce(lambda x: x * 2, lambda x: x + 3)(4))  # 14
print(compose_reduce()(9))  # 9
```

The loop implementation is often easier to debug and step through. Avoid obscuring order to achieve a one-liner.

### 6.2 Exception propagation and side effects

These helpers do not swallow exceptions: if any function raises, later functions are not called and the exception propagates to the caller. This is usually the correct default. Add context at a deliberate boundary if needed; do not silently convert failures to plausible records.

Composition itself does not make functions pure. If one stage mutates a shared object, writes a file, calls a network service, or reads global state, the pipeline inherits that side effect. For transformation pipelines, prefer small deterministic functions that return new values. Put I/O at the edges and make failure policy explicit.

### 6.3 Typing composed functions

`Callable` works well for a pipeline whose functions share a simple input/output type. Heterogeneous chains such as `str -> dict -> list[str]` are harder to represent precisely with a single `Callable` alias because each stage has a different type. The example uses `Any` at the generic composition boundary and relies on tests and type-checking at named transformation boundaries.

`ParamSpec` is valuable when writing decorators or wrappers that preserve a function's *argument signature*. It does not automatically solve arbitrary heterogeneous function-chain typing. This compact wrapper shows the problem it does solve:

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def logged_call(function: Callable[P, R]) -> Callable[P, R]:
    """Illustrate a signature-preserving wrapper; logging omitted."""
    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return function(*args, **kwargs)
    return wrapper

@logged_call
def format_record(record_id: int, *, prefix: str = "row") -> str:
    return f"{prefix}-{record_id}"

print(format_record(7, prefix="txn"))  # txn-7
```

`Callable[P, R]` preserves the wrapped function's parameter specification and return type for static type checkers; `@wraps` also preserves useful runtime metadata. This is a wrapper/decorator example, not a fully typed heterogeneous `compose`. For production pipelines, prefer explicit typed stages, protocols, or a library with well-defined typing if the pipeline's type relationships are important. Do not claim the composition helper is fully statically type-safe simply because it has annotations.

### 6.4 Point-free style: when abstraction helps

Point-free style defines a transformation by combining functions without naming the input argument at each step. For example, `itemgetter("region")` can be passed directly as a key rather than writing `lambda row: row["region"]`.

Benefits include reuse and less boilerplate when the operations are familiar. Costs include hidden data flow, difficult type inference, and harder debugging when chains become long. A good rule: keep a pipeline short enough that a reviewer can mentally trace its input, output, and failure behavior. Use named stages for business rules.

## 7. Sorting and data-transformation patterns

### 7.1 Mixed ascending and descending priorities

Python's sort is stable: records with equal keys preserve their relative order. For mixed directions, a robust approach is to apply stable sorts from the *least significant* priority to the *most significant* priority, reversing each pass as needed.

```python
from operator import itemgetter

records = [
    {"team": "A", "score": 90, "name": "Mira"},
    {"team": "A", "score": 95, "name": "Ari"},
    {"team": "B", "score": 95, "name": "Bo"},
    {"team": "A", "score": 95, "name": "Zoe"},
]
# Primary: score descending; secondary: team ascending; tertiary: name ascending.
ordered = sorted(records, key=itemgetter("name"))
ordered = sorted(ordered, key=itemgetter("team"))
ordered = sorted(ordered, key=itemgetter("score"), reverse=True)
print([(r["score"], r["team"], r["name"]) for r in ordered])
# [(95, 'A', 'Ari'), (95, 'A', 'Zoe'), (95, 'B', 'Bo'), (90, 'A', 'Mira')]
```

Why reverse the passes? Each stable pass preserves the ordering established by earlier passes among equal values. The most important key must be sorted last.

For numeric keys, a tuple such as `(row["team"], -row["score"])` may work for team ascending and score descending, but negation is not a universal descending-sort transform. It fails for strings and many custom types, and can be problematic for special numeric values. Avoid `-key` as a general sorting trick. Stable multi-pass sorting is broadly applicable; it costs multiple passes but remains explicit.

`reverse=True` reverses the order of the complete key ordering for that pass, not just one field of a tuple. That is why stable multi-pass sorting is useful for mixed directions.

### 7.2 Sort and group structured records

```python
from itertools import groupby
from operator import itemgetter

rows = [
    {"dept": "ops", "user": "Lia", "active": True},
    {"dept": "data", "user": "Ari", "active": True},
    {"dept": "data", "user": "Bo", "active": False},
]
by_dept = itemgetter("dept")
for dept, group in groupby(sorted(rows, key=by_dept), key=by_dept):
    active_users = [row["user"] for row in group if row["active"]]
    print(dept, active_users)
# data ['Ari']
# ops ['Lia']
```

This materializes only the sorted input because `sorted()` must order all rows. For a large dataset that does not fit memory, use an external sort, a database query with `ORDER BY`, or an already sorted stream. Do not imply that `groupby` itself sorts or collects all records.

### 7.3 Transform with small reusable stages

```python
from operator import itemgetter

raw = [
    {"id": " 001 ", "name": " ANA ", "amount": "12.50"},
    {"id": "002", "name": "Bo", "amount": "bad"},
]

def clean_id(row: dict[str, str]) -> dict[str, str]:
    return {**row, "id": row["id"].strip()}

def clean_name(row: dict[str, str]) -> dict[str, str]:
    return {**row, "name": row["name"].strip().title()}

def parse_amount(row: dict[str, str]) -> dict[str, object]:
    return {**row, "amount": float(row["amount"])}

first = pipe(raw[0], clean_id, clean_name, parse_amount)
print(first)
# {'id': '001', 'name': 'Ana', 'amount': 12.5}
print(itemgetter("id", "name")(first))  # ('001', 'Ana')
```

The second record raises `ValueError` in `parse_amount`. That is intentional: invalid input must have an explicit policy. A real ingestion pipeline might reject the record, collect a structured validation error, or route it to a quarantine stream. Do not silently replace invalid numeric data with zero unless the business rule explicitly says to do so.

## 8. In-place operators and Python's data model

### 8.1 `iadd` versus `add`

`operator.add(a, b)` performs the ordinary addition operation. `operator.iadd(a, b)` performs the in-place addition operation (`a += b`) where the object's type supports it. “In-place” does not guarantee mutation: the object may mutate itself and return itself, or it may return a new object.

```python
from operator import add, iadd

left = [1, 2]
right = [3]
result = add(left, right)
print(left, result)  # [1, 2] [1, 2, 3]

items = [1, 2]
alias = items
returned = iadd(items, [3])
print(items, alias, returned, items is returned)
# [1, 2, 3] [1, 2, 3] [1, 2, 3] True

number = 10
number = iadd(number, 5)
print(number)  # 15
```

For lists, in-place addition mutates the list and existing aliases observe the change. For integers, the value is immutable, so `iadd` returns the result of addition and the caller must rebind a name to it. The same distinction matters for other in-place operations such as `isub`, `imul`, `itruediv`, `ifloordiv`, `imod`, `ipow`, `iand`, `ior`, `ixor`, `ilshift`, and `irshift`.

**Production rule:** treat `i*` operations as potentially mutating. Check the concrete type and aliasing behavior before using them in shared state or transformations that are expected to be pure.

### 8.2 Custom classes and numerical libraries

Operator functions do not hard-code arithmetic for built-in types. They invoke Python's operator protocol, which commonly dispatches to methods such as `__add__`, `__mul__`, `__eq__`, `__lt__`, `__getitem__`, and in-place methods such as `__iadd__`. If an operation is unsupported, Python may try a reflected method such as `__radd__` where applicable, or raise `TypeError`.

This is why `operator.add` can work with a custom vector class or array type, not only integers. NumPy arrays, for example, define elementwise arithmetic behavior, so `operator.add(array_a, array_b)` typically delegates to that array type's addition semantics. For pandas objects, operators may align by labels and propagate missing values according to pandas rules. Those behaviors are library-specific; they are not promises made by the `operator` module. This lesson does not require NumPy or pandas.

### 8.3 `index`, `length_hint`, and `call`

- `operator.index(obj)` requests the exact integer index protocol (`__index__`). It is intended for integer-like values used as indexes or sizes; unlike `int(obj)`, it does not accept arbitrary values that merely convert to an integer. It raises `TypeError` if the object does not implement the protocol.
- `operator.length_hint(obj, default=0)` asks for an estimated length, using `__len__` or `__length_hint__` when available. The estimate can be unavailable or imperfect; do not use it as a correctness guarantee.
- `operator.call(obj, *args, **kwargs)` calls `obj(*args, **kwargs)`. It was added in **Python 3.11**. It can be useful when a call operation itself needs to be passed as a function, but direct `obj(...)` syntax is usually clearer.

```python
from operator import call, index, length_hint

print(index(True))                 # 1 (bool implements the index protocol)
print(length_hint(iter([1, 2, 3])))  # commonly 3; an estimate, not a contract
print(call(str.upper, "hello"))    # HELLO
```

`bool` is a subclass of `int`, so `operator.index(True)` returns `1`. If an application requires a positive, non-Boolean integer, validate that rule separately. `length_hint` is an optimization hint, not a replacement for consuming or validating an iterable.

## 9. Performance and serialization considerations

### 9.1 Fair `timeit` methodology

The speed of `lambda`, `itemgetter`, and comprehensions depends on the operation, data shape, Python build/version, and where time is spent. Do not claim that `itemgetter` is always faster or that a comprehension is always slower. The following script measures comparable key extraction/sorting tasks locally and prints the result on the machine where it is run.

```python
from operator import itemgetter
from statistics import median
from timeit import repeat

rows = [(f"user-{i:06d}", i % 1000) for i in range(20_000)]
key_lambda = lambda row: row[1]
key_itemgetter = itemgetter(1)

sort_cases = {
    "sort + lambda key": lambda: sorted(rows, key=key_lambda),
    "sort + itemgetter key": lambda: sorted(rows, key=key_itemgetter),
}
extract_cases = {
    "extract + map(lambda)": lambda: list(map(key_lambda, rows)),
    "extract + map(itemgetter)": lambda: list(map(key_itemgetter, rows)),
    "extract + comprehension": lambda: [row[1] for row in rows],
}
number = 5
repeats = 5
for group_name, cases in (("sorting", sort_cases), ("extraction", extract_cases)):
    print(group_name)
    for name, statement in cases.items():
        samples = repeat(statement, number=number, repeat=repeats)
        per_run = [sample / number for sample in samples]
        print(f"  {name}: median {median(per_run):.6f}s/run across {repeats} repeats")
```

Interpret this carefully:

- The two sorting cases perform the same full sort with the same input and key values, so they are a reasonable comparison of the key-callable choice.
- The three extraction cases produce the same list of field values. They compare `map` with a lambda, `map` with `itemgetter`, and a list comprehension without creating a new lambda for each row.
- Sorting and extraction are **different workloads**; compare results only within the same group.
- This script uses five repeats of five calls and reports the median per-call time. Increase repetitions if results are noisy; for rigorous comparisons, alternate case order, report spread as well as median, and run multiple processes or a dedicated benchmark tool when appropriate.
- Use realistic data sizes and distributions, avoid measuring one-time setup, and do not run unrelated CPU-heavy tasks at the same time.
- Repeat on the target Python version and deployment environment. A microbenchmark may not predict an end-to-end ETL pipeline dominated by I/O, parsing, allocations, or database work.

### 9.2 Pickling and multiprocessing

Multiprocessing often needs to serialize the callable and its arguments so another process can reconstruct the work. Standard pickle generally supports top-level functions and many built-in callable objects, but it does not serialize arbitrary executable code.

- **`itemgetter` / `attrgetter` / `methodcaller`:** common instances are picklable when their stored keys/names/arguments are themselves picklable. Verify the actual object with `pickle.dumps` in the Python version and context you deploy.
- **`functools.partial`:** usually picklable when its underlying callable, bound arguments, and bound keyword values are picklable. A partial around a lambda remains unpicklable by standard pickle because the wrapped lambda is not picklable.
- **Lambda:** standard `pickle` generally cannot pickle lambda functions, including lambdas assigned to a variable, because functions are pickled by qualified module/name and lambdas do not have a stable importable global name.
- **Local/nested functions:** generally not picklable by standard pickle for the same importability reasons. Top-level named functions in an importable module are the safest default.

The exact multiprocessing start method and platform matter. Under spawn-based process creation, workers need importable code and the usual `if __name__ == "__main__":` guard in executable scripts. Picklability is necessary for many process-pool uses, but not sufficient: the function's arguments and return values must also be transferable, and worker startup overhead may dominate small tasks. Third-party serializers may behave differently; do not assume they are installed or safe by default.

A small check can confirm the behavior on your runtime (define the named function at module scope in a real `.py` module):

```python
import pickle
from functools import partial
from operator import itemgetter

def add_fee(amount: float, fee: float) -> float:
    return amount + fee

serializable_getter = itemgetter("id")
serializable_partial = partial(add_fee, fee=2.5)
print(pickle.loads(pickle.dumps(serializable_getter))({"id": 7}))  # 7
print(pickle.loads(pickle.dumps(serializable_partial))(10.0))      # 12.5

try:
    pickle.dumps(lambda value: value + 1)
except (AttributeError, pickle.PicklingError) as error:
    print(type(error).__name__)  # commonly AttributeError
```

The precise exception text/type can vary by context; the important point is that standard pickle does not serialize the lambda's code as a self-contained object.

## 10. Common mistakes and debugging

1. **Confusing `compose` and `pipe` order.** Write down each intermediate value or test with deliberately noncommutative functions such as `+ 3` and `* 2`.
2. **Using `reduce` for every aggregation.** Prefer `sum`, `math.prod`, `any`, or `all` when they directly describe the intent.
3. **Assuming `itemgetter` supplies defaults.** Missing keys still raise `KeyError`.
4. **Forgetting `groupby` groups are adjacent and lazy.** Sort first when necessary and consume each group before advancing.
5. **Negating arbitrary sort keys.** `-value` is not a generic way to reverse strings or custom objects.
6. **Assuming `iadd` always mutates.** Immutable objects are rebound to a returned result; mutable objects may change in place.
7. **Using `length_hint` as a guarantee.** It is an estimate for allocation optimization, not correctness.
8. **Assuming annotations make composition fully type-safe.** Heterogeneous pipelines need explicit stage contracts and tests.
9. **Making point-free chains too clever.** Give business rules meaningful names.
10. **Assuming every callable can be pickled.** Test the actual callable and bound state; prefer importable top-level functions for process workers.
11. **Benchmarking unlike workloads.** Separate sort benchmarks from extraction benchmarks and measure on the target runtime.
12. **Hiding invalid-data behavior.** Let errors propagate or handle them at an explicit validation boundary; avoid silent coercion.

When debugging, inspect the callable's input and output at each stage, test a minimal record, and verify exception types. For a pipeline with side effects, test both the successful path and the failure path to establish which effects may already have happened when an exception occurs.

## 11. Unit tests and edge cases

The following tests use `pytest`. Save them in a file such as `test_operator_composition.py` alongside the helper implementations. The tests intentionally cover order, empty and single-stage composition, multi-stage behavior, missing fields, sort direction, exception propagation, and mutation.

```python
from operator import attrgetter, iadd, itemgetter, methodcaller
import pytest

# Include the compose() and pipe() definitions from Section 6.1 in this file.

def test_compose_order_and_pipe_order():
    double = lambda value: value * 2
    add_three = lambda value: value + 3
    assert compose(double, add_three)(4) == 14  # add_three, then double
    assert pipe(4, add_three, double) == 14     # add_three, then double
    assert compose(add_three, double)(4) == 11  # double, then add_three

def test_empty_and_single_function_cases():
    assert compose()(42) == 42
    assert pipe(42) == 42
    assert compose(str.upper)("abc") == "ABC"
    assert pipe("abc", str.upper) == "ABC"

def test_itemgetter_multiple_fields_and_missing_key():
    row = {"dept": "data", "id": 7}
    assert itemgetter("dept", "id")(row) == ("data", 7)
    with pytest.raises(KeyError):
        itemgetter("missing")(row)

def test_attrgetter_missing_attribute():
    with pytest.raises(AttributeError):
        attrgetter("missing")(object())

def test_incompatible_pipeline_signature_propagates():
    with pytest.raises(TypeError):
        pipe("not-an-integer", lambda value: value + 1)

def test_methodcaller_arguments():
    assert methodcaller("replace", " ", "_")("data engineering") == "data_engineering"

def test_mixed_direction_stable_sort():
    rows = [
        {"score": 9, "team": "B", "name": "Bo"},
        {"score": 9, "team": "A", "name": "Zoe"},
        {"score": 9, "team": "A", "name": "Ari"},
        {"score": 8, "team": "A", "name": "Mira"},
    ]
    result = sorted(rows, key=itemgetter("name"))
    result = sorted(result, key=itemgetter("team"))
    result = sorted(result, key=itemgetter("score"), reverse=True)
    assert [row["name"] for row in result] == ["Ari", "Zoe", "Bo", "Mira"]

def test_exceptions_propagate_and_stop_later_stages():
    calls = []
    def fail(value):
        calls.append("fail")
        raise ValueError("bad input")
    def later(value):
        calls.append("later")
        return value
    with pytest.raises(ValueError, match="bad input"):
        pipe(1, fail, later)
    assert calls == ["fail"]

def test_iadd_mutates_list_and_alias_observes_it():
    values = [1]
    alias = values
    returned = iadd(values, [2])
    assert values == [1, 2]
    assert alias is values
    assert returned is values
```

Run with:

```bash
python -m pytest -q
```

Also test these edge cases in your own pipeline:

- Empty input and a one-record input.
- Missing required fields, missing attributes, `None`, wrong value types, and numeric values too large to represent as a finite float.
- Equal sort keys (confirm stable order is the desired behavior).
- Functions that raise before or after a side effect.
- A `partial` whose bound argument is not picklable.
- A process-pool callable in a separate importable module, using the platform's real start method.

## 12. Mini-project: structured-record transformation pipeline

### Goal

Build a small, deterministic pipeline for transaction-like records. It should validate required fields, normalize identifiers and category labels, parse amounts, filter out non-positive transactions, sort the accepted records by amount descending and identifier ascending, and return both accepted records and structured rejection details. Keep transformation logic pure: no file/network/database calls inside the core functions.

### Input contract

Each input is a mapping with string fields `id`, `category`, and `amount`. Amounts arrive as strings. A valid record has a non-empty ID, a non-empty category, and a finite positive amount. Invalid rows are rejected with a reason rather than silently dropped.

```python
from collections.abc import Iterable, Mapping
from math import isfinite
from operator import itemgetter
from typing import Any

Record = dict[str, Any]


def validate_record(raw: Mapping[str, object]) -> tuple[Record | None, str | None]:
    """Return (normalised record, None) or (None, rejection reason)."""
    required = ("id", "category", "amount")
    missing = [field for field in required if field not in raw]
    if missing:
        return None, f"missing fields: {', '.join(missing)}"

    record_id = raw["id"]
    category = raw["category"]
    amount_raw = raw["amount"]
    if not isinstance(record_id, str) or not record_id.strip():
        return None, "id must be a non-empty string"
    if not isinstance(category, str) or not category.strip():
        return None, "category must be a non-empty string"
    if isinstance(amount_raw, bool) or not isinstance(amount_raw, (str, int, float)):
        return None, "amount must be numeric"
    try:
        amount = float(amount_raw)  # accepts numeric strings and numeric values
    except OverflowError:
        return None, "amount must be finite"
    except ValueError:
        return None, "amount must be numeric"
    if not isfinite(amount):
        return None, "amount must be finite"
    if amount <= 0:
        return None, "amount must be positive"

    return {
        "id": record_id.strip(),
        "category": category.strip().casefold(),
        "amount": amount,
    }, None


def process_records(rows: Iterable[Mapping[str, object]]) -> tuple[list[Record], list[dict[str, str]]]:
    accepted: list[Record] = []
    rejected: list[dict[str, str]] = []
    for position, raw in enumerate(rows, start=1):
        record, error = validate_record(raw)
        if error is not None:
            rejected.append({"row": str(position), "reason": error})
            continue
        assert record is not None
        accepted.append(record)

    # Stable multi-key sort: amount descending, then id ascending.
    accepted.sort(key=itemgetter("id"))
    accepted.sort(key=itemgetter("amount"), reverse=True)
    return accepted, rejected


if __name__ == "__main__":
    sample = [
        {"id": " T-2 ", "category": " Travel ", "amount": "125.50"},
        {"id": "T-1", "category": "food", "amount": "42"},
        {"id": "T-3", "category": "misc", "amount": "bad"},
        {"id": "T-4", "category": "food", "amount": "0"},
        {"id": "T-5", "category": "TRAVEL", "amount": "125.50"},
    ]
    accepted, rejected = process_records(sample)
    print(accepted)
    print(rejected)
```

Expected output:

```text
[{'id': 'T-2', 'category': 'travel', 'amount': 125.5}, {'id': 'T-5', 'category': 'travel', 'amount': 125.5}, {'id': 'T-1', 'category': 'food', 'amount': 42.0}]
[{'row': '3', 'reason': 'amount must be numeric'}, {'row': '4', 'reason': 'amount must be positive'}]
```

### Mini-project tests

```python
def test_process_records_accepts_normalises_and_sorts():
    accepted, rejected = process_records([
        {"id": " B ", "category": " FOOD ", "amount": "10"},
        {"id": "A", "category": "travel", "amount": "10"},
        {"id": "C", "category": "food", "amount": "15"},
    ])
    assert [row["id"] for row in accepted] == ["C", "A", "B"]
    assert accepted[1]["category"] == "travel"
    assert rejected == []

def test_process_records_reports_multiple_invalid_rows():
    accepted, rejected = process_records([
        {"id": "A", "category": "food"},
        {"id": "B", "category": "food", "amount": "nan"},
        {"id": "C", "category": "food", "amount": "-1"},
    ])
    assert accepted == []
    assert [item["reason"] for item in rejected] == [
        "missing fields: amount", "amount must be finite", "amount must be positive"
    ]

def test_process_records_empty_input():
    assert process_records([]) == ([], [])

def test_process_records_rejects_integer_too_large_for_float():
    accepted, rejected = process_records([
        {"id": "HUGE", "category": "test", "amount": 10**10000},
    ])
    assert accepted == []
    assert rejected == [{"row": "1", "reason": "amount must be finite"}]
```

**Design discussion:** the example intentionally collects rejected rows instead of aborting the entire batch. Other systems may need fail-fast behavior, a maximum rejection threshold, source row identifiers, or durable quarantine output. Decide the policy before production deployment. The pipeline currently keeps all accepted and rejected rows in memory; for very large input, process bounded batches and write results incrementally. That streaming concern belongs with the iteration and file-processing lessons.

### Roadmap self-checks: worked answers

The module roadmap calls out these three checks explicitly.

**1. Sort dictionaries by department ascending, then salary descending, without a lambda.** Use stable sorts from the least significant key to the most significant key:

```python
from operator import itemgetter

staff = [
    {"name": "Ari", "dept": "data", "salary": 120},
    {"name": "Bo", "dept": "data", "salary": 150},
    {"name": "Cy", "dept": "ops", "salary": 130},
]
by_salary_desc = sorted(staff, key=itemgetter("salary"), reverse=True)
by_dept_then_salary = sorted(by_salary_desc, key=itemgetter("dept"))
print([(row["dept"], row["salary"], row["name"]) for row in by_dept_then_salary])
# [('data', 150, 'Bo'), ('data', 120, 'Ari'), ('ops', 130, 'Cy')]
```

The salary pass runs first; the stable department pass then groups departments alphabetically while preserving salary-descending order within each department. No tuple-key negation or lambda is required.

**2. Why can `itemgetter` often be sent to a process pool while a lambda cannot?** Standard `pickle` can serialize common `itemgetter` instances as built-in callable objects when their stored keys are picklable. A lambda generally has no importable module-level name, and standard `pickle` serializes functions by reference rather than serializing their code. This is a rule of thumb, not a guarantee that every getter, its arguments, and the surrounding worker setup are serializable; test the exact callable in the deployment environment.

**3. Write and test `pipe(value, *functions)`.** Section 6.1 gives the implementation. These assertions pin down the left-to-right and empty-pipeline contracts:

```python
assert pipe(4, lambda value: value + 3, lambda value: value * 2) == 14
assert pipe(4) == 4
```

### Extension exercises

1. Add a `source` field and preserve it without mutating the original mapping.
2. Make the positive-amount rule configurable with `partial` or an explicit configuration object.
3. Add a pure `summarise_by_category` stage and test empty input.
4. Make the sort priority configurable, documenting the behavior for missing values.
5. Add a serialization test for `itemgetter("id")` and a top-level named worker function. Do not assume a lambda is picklable.
6. Decide whether an invalid row should be rejected, quarantined, or fail the batch; test the chosen policy.

## 13. Hands-on exercises

Try these before reading the suggested approaches.

1. **Tuple sort:** sort tuples `(name, score)` by score descending and name ascending. Do not negate the name.
2. **Mapping projection:** use `itemgetter` to transform a list of dictionaries into `(id, category)` tuples.
3. **Nested access:** define a dataclass `Event` with `source.name`; sort events by that nested name.
4. **Method caller:** use `methodcaller` to remove a prefix or replace a delimiter. Explain when a named function would be clearer.
5. **Reduction:** compute a product and a sum. Explain why `math.prod` and `sum` are preferable to `reduce` in this case.
6. **Composition:** implement `compose` and `pipe`; prove their order differs using subtraction or multiplication/addition.
7. **Mutation:** compare `add(list_a, list_b)` and `iadd(list_a, list_b)` with an alias to the first list.
8. **Serialization:** attempt to pickle `itemgetter("id")`, `partial` of a top-level function, and a lambda. Explain the observed results in your runtime.
9. **Benchmarking:** compare two equivalent sort-key implementations using the same input. Record Python version, data size, and trial count.
10. **Production design:** extend the mini-project with structured validation errors and deterministic tests for malformed rows.

## 14. Self-check questions with explained answers

### 1. Why use `itemgetter("dept")` instead of `lambda row: row["dept"]`?

Both work. `itemgetter` expresses a direct item lookup and is reusable; it is often convenient for `sorted`, `max`, and `groupby`. A lambda is better when the key requires computation or a fallback. Readability should decide, not a blanket rule that one is always faster.

### 2. What does `itemgetter("a", "b")(record)` return?

A two-item tuple `(record["a"], record["b"])`. If either key is missing, normal item lookup raises `KeyError`.

### 3. Why can `groupby` appear to lose earlier groups?

Its group iterators share the underlying source. Advancing the outer iterator advances the source, so a group that has not been consumed may no longer be available. Materialize a group only when needed and understand the memory cost.

### 4. Explain `compose(f, g)(x)` versus `pipe(x, f, g)`.

With the conventions in this lesson, both apply `g` after `f` when written as `compose(g, f)(x)` and `pipe(x, f, g)`. `compose` lists functions from outermost to innermost (right-to-left execution); `pipe` lists them in execution order (left-to-right).

### 5. Why is `sum()` clearer than `reduce(operator.add, values)`?

`sum` directly communicates numeric summation, handles an empty iterable with result `0`, and avoids unnecessary abstraction. `reduce` without an initializer raises on empty input.

### 6. Does `operator.iadd(a, b)` always mutate `a`?

No. Mutable types such as lists commonly mutate and return themselves. Immutable types such as integers produce a new result, which must be assigned if the caller wants to keep it.

### 7. Why is `key=lambda row: -row["name"]` invalid as a general descending sort technique?

Unary negation is not defined for strings and many custom values. Use stable sorting passes or a type-specific, well-defined key transformation.

### 8. When is `operator.index()` preferable to `int()`?

When an API requires the integer index protocol, such as a true integer-like index. `int()` may perform conversions that are not valid for index semantics. Apply separate validation for domain constraints such as positive values and excluding Booleans.

### 9. Is `length_hint()` guaranteed to return the exact remaining length?

No. It is an estimate intended to help optimize allocations. Code correctness must not depend on it.

### 10. Why does a `partial` of a lambda generally remain unpicklable with standard pickle?

`partial` stores a reference to the wrapped callable and bound arguments. It does not turn an unpicklable lambda into an importable top-level function. The wrapped callable and stored state must themselves be serializable under the selected mechanism.

### 11. What does a correct microbenchmark compare?

Equivalent operations over equivalent input, with setup handled consistently, multiple trials, and a recorded runtime/environment. Sorting and field extraction are different workloads and should not be ranked as if they performed the same work.

### 12. What is the main trade-off of point-free style?

It can remove repetitive parameter plumbing and encourage reuse, but long chains can obscure data flow, error locations, and type relationships. Prefer named stages when they encode business meaning.

## 15. Final mastery checklist

- [ ] I can explain why operator functions are first-class callables.
- [ ] I can use `add`, `mul`, `eq`, `lt`, `not_`, `contains`, and `getitem` with correct argument order.
- [ ] I can choose `itemgetter`, `attrgetter`, and `methodcaller` appropriately.
- [ ] I can pass key functions to `sorted`, `max`, `map`, and `groupby`.
- [ ] I understand `groupby`'s consecutive grouping and shared iterator behavior.
- [ ] I choose `sum`, `math.prod`, `any`, and `all` when they state intent better than `reduce`.
- [ ] I can explain and test `compose` versus `pipe`, including empty and one-function cases.
- [ ] I can use `partial` without hiding important configuration or validation.
- [ ] I understand mutation/rebinding behavior for `iadd` and related in-place operations.
- [ ] I know the meaning and limitations of `index`, `length_hint`, and `call` (Python 3.11+ for `call`).
- [ ] I can sort by mixed directions without unsafe key negation.
- [ ] I can describe callable pickling limits in multiprocessing contexts.
- [ ] I benchmark equivalent work and avoid universal performance claims.
- [ ] I can build a tested, deterministic transformation pipeline with explicit invalid-data behavior.

## 16. Quick reference

| Tool | Purpose | Watch out for |
|---|---|---|
| `operator.add`, `mul` | Callable arithmetic | Underlying type controls behavior |
| `operator.eq`, `lt` | Callable comparisons | Custom comparison semantics apply |
| `operator.not_` | Invert truthiness | Not bitwise `~` |
| `operator.contains(container, item)` | Callable membership | Container is the first argument |
| `operator.getitem(obj, key)` | Generic indexing | Missing key/index errors propagate |
| `itemgetter(*keys)` | Fetch one or more items | Multiple keys produce a tuple |
| `attrgetter(*names)` | Fetch attributes, including dotted paths | Missing attributes raise normally |
| `methodcaller(name, *args, **kwargs)` | Call a named method | Lookup/call errors propagate |
| `reduce(function, iterable[, initializer])` | Fold values into one | Empty iterable needs initializer |
| `sum`, `math.prod` | Sum/product | Usually clearer than `reduce` |
| `partial(function, ...)` | Bind arguments | Bound state must be serializable if pickling |
| `compose(*functions)` | Right-to-left function composition | This lesson's empty composition is identity |
| `pipe(value, *functions)` | Left-to-right transformation | This lesson's empty pipe returns value |
| `operator.iadd` and related `i*` | In-place operator protocol | May mutate or return a new object |
| `operator.index(obj)` | Integer index protocol | Does not mean arbitrary integer conversion |
| `operator.length_hint(obj, default)` | Estimate iterable length | Hint is not a correctness guarantee |
| `operator.call(obj, ...)` | Call a callable as a function | Added in Python 3.11; direct call is clearer |
| `sorted(..., key=...)` | Return a sorted list | Materializes input; sort is stable |
| `itertools.groupby(..., key=...)` | Group consecutive equal keys | Sort/group appropriately; consume each group |

**Production principle:** choose the simplest callable expression that makes the transformation's intent, type expectations, mutation behavior, and failure policy obvious to the next engineer.
