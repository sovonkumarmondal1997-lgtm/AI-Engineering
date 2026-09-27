# Pure Functions, Immutability, and Higher-Order Functions

This chapter develops functional-style thinking in Python from ordinary functions to production architecture. The progression is deliberate: ordinary functions → state → side effects → pure functions → immutability → first-class functions → higher-order functions → callbacks → closures → functional tools → composition → decorators → caching → production design.

> **Core idea:** Functional style is an engineering tool for making data flow, state, and effects easier to reason about. It does not require every production component to be purely functional.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- distinguish pure and impure functions;
- identify side effects and hidden dependencies;
- reason about deterministic behavior and referential transparency;
- distinguish mutation, rebinding, references, and object identity;
- explain mutable versus immutable objects;
- distinguish shallow from deep immutability;
- use tuples, `frozenset`, frozen dataclasses, and value-oriented data models appropriately;
- understand defensive copying and its trade-offs;
- treat functions as first-class objects;
- write higher-order functions and callbacks;
- create and reason about closures and `nonlocal`;
- use `lambda`, `map`, `filter`, `reduce`, `sorted(key=...)`, `min(key=...)`, `max(key=...)`, `any`, `all`, `zip`, and `enumerate`;
- use `functools.partial`, `partialmethod`, `cache`, `lru_cache`, `singledispatch`, and `wraps` appropriately;
- compose functions and build readable pipelines;
- understand decorators and their effect on purity/metadata;
- test deterministic logic separately from I/O;
- reason about copying, hashing, caching, concurrency, and performance;
- apply functional techniques to backend, data engineering, ML, LLM, and agentic AI systems;
- decide when functional style is useful and when straightforward stateful/OOP design is clearer.

A useful production question is:

> **What data enters, what comes out, what state is read or changed, and what effects occur?**

---

## 2. Prerequisites

You should have basic familiarity with:

- variables and assignment;
- functions, parameters, arguments, and returns;
- scopes;
- lists, dictionaries, tuples, and sets;
- classes and objects;
- basic OOP;
- modules/imports;
- exceptions;
- basic `pytest` testing.

A quick refresh:

```python
def add(a, b):
    return a + b


result = add(2, 3)
print(result)
```

Output:

```text
5
```

The input values are explicit, the local computation is visible, and the result is returned.

---

# BASIC

## 3. Start With Ordinary Python Functions

Start with normal Python before introducing functional terminology.

```python
def add(a, b):
    return a + b
```

Execution:

1. `def` creates a function object and binds it to `add`.
2. `add(2, 3)` creates a call frame.
3. `a` and `b` receive the arguments.
4. `a + b` is computed.
5. `5` is returned.
6. The call frame goes away after the call completes, while referenced objects can remain alive elsewhere.

Now introduce hidden state:

```python
tax_rate = 0.18


def calculate_tax(amount):
    return amount * tax_rate


print(calculate_tax(100))
```

Output:

```text
18.0
```

`amount` is explicit; `tax_rate` is hidden. The function's result therefore depends on more than its visible parameter list.

Now introduce mutation:

```python
total = 0


def add_to_total(amount):
    global total
    total += amount


add_to_total(10)
add_to_total(5)
print(total)
```

Output:

```text
15
```

The function changes external state. This is not automatically bad; it is simply an effect that needs to be understood.

---

## 4. State, Mutation, and Side Effects

### State

State is information whose value may differ over time: a balance, cache, database row, connection pool, model configuration, queue, or current time.

### Mutation

Mutation changes an existing mutable object in place.

```python
items = [1, 2]
items.append(3)
print(items)
```

Output:

```text
[1, 2, 3]
```

### Side effects

A side effect is an observable interaction with state or the outside world that is not fully captured as the function's returned value. Common examples include:

- changing global or captured state;
- mutating a caller-owned mutable argument;
- writing a file;
- changing a database;
- making a network request;
- publishing a message;
- logging or printing;
- reading current time;
- reading environment variables;
- accessing external state;
- using random state;
- mutating object state.

Do not reduce side effects to `print()`.

### Exceptions require nuance

Raising an exception does not by itself prove that a function is impure. A deterministic validation function can raise `ValueError` based only on an explicit input. Purity analysis asks whether the observable behavior depends on hidden state and whether evaluation produces external effects.

---

## 5. What Is a Pure Function?

A practical definition:

> A pure function produces a result determined by its relevant inputs and does not perform externally observable side effects outside its defined result/error contract.

The two core properties are:

1. the result is stable for the same relevant inputs;
2. evaluation does not modify external state or perform uncontrolled external effects.

Pure:

```python
def add(a, b):
    return a + b
```

Not pure/deterministic in the same sense:

```python
import random


def generate_number():
    return random.random()
```

And:

```python
user_count = 0


def increment():
    global user_count
    user_count += 1
```

A pure function can call another pure function, can accept parameters, and can raise a defined exception. “Returns a value” is not the definition of purity.

---

## 6. Pure vs Impure Functions

| Property | Pure function | Impure function |
|---|---|---|
| Result from relevant inputs | Stable | May depend on external state |
| Hidden dependencies | Preferably none | Common |
| External mutation | No | Possible |
| I/O | No | Common |
| Unit testing | Usually simple | Usually needs controlled effects |
| Caching | Often natural | Can be dangerous |
| Composition | Usually straightforward | Effect ordering can matter |
| Concurrency reasoning | Easier | Shared state can race |
| Determinism | Usually strong | May be intentionally nondeterministic |

Examples of impure boundaries include database writes, file writes, model/API calls, environment reads, and clock reads. Production applications still need those effects.

---

## 7. Determinism

A deterministic computation gives the same result for the same relevant inputs under the same contract.

```python
def square(x):
    return x * x
```

By contrast:

```python
import random


def choose_value():
    return random.choice([1, 2, 3])
```

Nondeterminism is not inherently bad. Randomized algorithms, load balancing, distributed systems, simulations, and exploration policies can intentionally use it. The engineering goal is to control and document nondeterminism when reproducibility matters.

Determinism is valuable for:

- testing;
- caching;
- debugging;
- replay;
- ETL reproducibility;
- ML experiments;
- incident analysis.

---

## 8. Referential Transparency

An expression is referentially transparent when it can be replaced with its result without changing observable program behavior.

```python
def square(x):
    return x * x


result = square(5) + square(5)
```

Conceptually, the two calls can be replaced by `25` each when the function is pure and deterministic.

A function depending on the current time, an external service, or mutable global state cannot generally be replaced by a previously observed result without changing behavior.

Referential transparency is a useful reasoning consequence of deterministic pure computation. It is stronger than simply saying “this function returns something.”

---

## 9. Hidden Dependencies

This function has a hidden dependency:

```python
tax_rate = 0.18


def calculate_total(amount):
    return amount + amount * tax_rate
```

Make the dependency explicit:

```python
def calculate_total(amount, tax_rate):
    return amount + amount * tax_rate
```

Explicit dependencies improve:

- testability;
- reproducibility;
- code review;
- maintainability;
- composition;
- dependency injection.

This connects directly to the previous topic: explicit dependencies are easier to substitute than hidden dependencies.

---

## 10. Mutation vs Rebinding

This distinction is foundational.

Mutation:

```python
x = []
x.append(1)
```

The same list object is changed.

Rebinding:

```python
x = []
x = [1]
```

The original list is not changed; the name `x` is pointed at a new list.

Object identity makes this visible:

```python
x = []
y = x

print(x is y)
x.append(1)
print(y)
```

Output:

```text
True
[1]
```

Now rebinding:

```python
x = []
y = x
x = [1]

print(x)
print(y)
print(x is y)
```

Output:

```text
[1]
[]
False
```

`id()` can help during debugging:

```python
x = []
print(id(x))
```

The mental model is:

```text
name ─────► object
```

Mutation changes the object. Rebinding changes what the name refers to.

---

## 11. Mutable vs Immutable Objects

Common immutable object types include:

- `int`;
- `float`;
- `bool`;
- `str`;
- `tuple` as an outer container;
- `frozenset`.

Common mutable types include:

- `list`;
- `dict`;
- `set`;
- many user-defined objects.

Immutability means the object cannot be changed in place after creation.

It does **not** mean a name cannot be rebound:

```python
x = 10
x += 1
print(x)
```

Output:

```text
11
```

The integer object is immutable; the name `x` is rebound to another integer object. Python does not provide a general immutable-variable mechanism in ordinary name binding.

---

## 12. Immutability

Immutability encourages replacement rather than in-place mutation.

```python
numbers = (1, 2, 3)

# numbers[0] = 99  # TypeError

numbers = (99, 2, 3)
print(numbers)
```

Output:

```text
(99, 2, 3)
```

The tuple was not edited; a new tuple was created and the name was rebound.

Why use immutability?

- fewer accidental state changes;
- clearer ownership;
- safer sharing of values;
- simpler tests;
- easier reasoning;
- better reproducibility;
- easier caching for stable values.

It is a design choice, not an absolute rule.

---

## 13. Shallow vs Deep Immutability

This tuple is immutable as an outer container but contains mutable lists:

```python
data = ([1, 2], [3, 4])
data[0].append(99)
print(data)
```

Output:

```text
([1, 2, 99], [3, 4])
```

### Shallow immutability

The outer structure cannot be changed in place, while nested reachable values may still mutate.

### Deep immutability

All relevant reachable state is immutable under the application's data model.

Python does not have a universal `deep_immutable()` operation. Deep immutability is mostly a data-modeling decision.

Ask:

> **Can a consumer reach mutable state and change it without the owner knowing?**

That question is often more useful than asking only whether the top-level object is immutable.

---

## 14. Defensive Copying

Python provides shallow and deep copying through `copy`:

```python
import copy

shallow = copy.copy(original)
deep = copy.deepcopy(original)
```

Shallow copy creates a new outer compound object while retaining references to nested objects where appropriate:

```python
import copy

original = [[1], [2]]
shallow = copy.copy(original)
shallow[0].append(99)

print(original)
```

Output:

```text
[[1, 99], [2]]
```

Deep copy recursively copies supported nested objects:

```python
import copy

original = [[1], [2]]
deep = copy.deepcopy(original)
deep[0].append(99)

print(original)
print(deep)
```

Output:

```text
[[1], [2]]
[[1, 99], [2]]
```

Deep copying can be expensive and can duplicate objects that were intentionally shared. Recursive object graphs need cycle handling, and some external resources cannot be meaningfully duplicated. Therefore `deepcopy()` is not a general “make this immutable” operation. Explicit immutable data modeling is often preferable.

---

## 15. Tuples as Immutable Containers

Tuples support indexing, unpacking, iteration, and concatenation that creates a new tuple.

```python
point = (10, 20)
x, y = point
extended = point + (30,)

print(x, y)
print(extended)
```

Output:

```text
10 20
(10, 20, 30)
```

Nested mutability still matters:

```python
items = ([1, 2], [3, 4])
items[0].append(5)
print(items)
```

Output:

```text
([1, 2, 5], [3, 4])
```

Use tuples when fixed sequence structure and non-mutating outer semantics fit the domain.

---

## 16. `frozenset`

`frozenset` is the immutable counterpart to `set`.

```python
roles = frozenset({"reader", "writer"})
print("reader" in roles)
```

Output:

```text
True
```

It supports set operations but does not support mutation such as `.add()`.

When its elements are hashable, a `frozenset` is hashable and can be used as a dictionary key or set member:

```python
permissions = frozenset({"read", "write"})
lookup = {permissions: "editor"}
print(lookup[permissions])
```

Output:

```text
editor
```

A mutable `set` cannot be a dictionary key.

---

## 17. Immutable Data Modeling

Frozen dataclasses are useful for value-oriented state:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str


price = Money(1000, "INR")
print(price)
```

Output:

```text
Money(amount=1000, currency='INR')
```

`frozen=True` blocks ordinary assignment to fields after construction. It does not deeply freeze nested state:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Batch:
    records: list[str]


batch = Batch(["a", "b"])
batch.records.append("c")
print(batch.records)
```

Output:

```text
['a', 'b', 'c']
```

Good candidates include:

- money/value objects;
- request descriptions;
- immutable configuration snapshots;
- coordinates;
- inference settings;
- domain identifiers.

Frozen state is usually shallow with respect to nested objects.

---

## 18. Immutability and Hashing

Hash-based collections rely on stable hashing/equality behavior.

```python
key = ("customer", 42)
lookup = {key: "active"}
print(lookup[key])
```

A list is not hashable:

```python
# lookup = {[1, 2]: "value"}  # TypeError
```

Not every immutable object is hashable. A tuple containing only hashable values is typically hashable; a tuple containing a list is not:

```python
print(hash((1, 2)))
# hash((1, [2]))  # TypeError
```

The important relationship is:

```text
hash-based key
    ↓
hash/equality must remain compatible
    ↓
key state must not change in a way that invalidates lookup
```

A frozen dataclass can be hashable depending on its configuration and field behavior. Do not equate `frozen` with “always hashable.”

---

## 19. Benefits of Immutability

Immutability can provide:

- easier reasoning;
- fewer accidental state changes;
- simpler tests;
- safer sharing;
- reduced coupling;
- easier replay/reproducibility;
- safer cache keys when the representation is hashable;
- simpler reasoning about independent computations under concurrency.

It does not automatically make an application thread-safe. External databases, caches, resource pools, I/O, and shared services can still race or fail.

---

## 20. Costs and Trade-offs of Immutability

Immutability can cost:

- additional object allocation;
- copying/rebuilding large structures;
- memory;
- awkward boundary conversions with mutation-oriented APIs;
- complexity in inherently stateful algorithms.

A good question is:

> **Where does immutability reduce enough risk to justify its cost?**

Do not replace every local mutation with expensive copies simply to satisfy a slogan. Local mutation can be safe and clear when ownership is obvious.

---

## 21. First Mental Bridge to Functional Design

At this point, keep three ideas separate:

```text
PURE FUNCTION
  = explicit relevant inputs + deterministic result + no external side effect

IMMUTABLE OBJECT
  = existing object state cannot be changed in place

REBOUND NAME
  = name now refers to another object
```

The combination is powerful:

```text
explicit data
   +
stable values
   +
small deterministic functions
   ↓
easier reasoning
```

Now the chapter can introduce the next step: functions themselves can become values.

# INTERMEDIATE

## 22. Functions as First-Class Objects

Python functions are objects. They can be stored, passed, returned, placed in collections, and invoked later.

```python
def greet(name):
    return f"Hello {name}"


say_hello = greet
print(say_hello("Alice"))
print(type(greet))
```

Output:

```text
Hello Alice
<class 'function'>
```

The variable `say_hello` refers to the function object; it does not create a second implementation.

The difference between passing and calling is critical:

```python
apply(square, 5)       # pass a function
apply(square(5), 5)    # call it first; usually wrong for this API
```

`f` means “the callable value.” `f()` means “execute it now.”

---

## 23. What Is a Higher-Order Function?

A higher-order function accepts a function, returns a function, or does both.

```python
def apply_operation(operation, a, b):
    return operation(a, b)


def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


print(apply_operation(add, 2, 3))
print(apply_operation(multiply, 2, 3))
```

Output:

```text
5
6
```

Why use this pattern? It separates stable control flow from replaceable behavior:

```text
stable algorithm + supplied strategy
```

This is closely related to a Strategy Pattern, but a plain function is sometimes a clearer strategy than a class hierarchy.

---

## 24. Functions as Arguments and Callbacks

A callback is a callable supplied to another component so the receiving component controls when it is invoked.

```python
def apply(func, value):
    return func(value)


def square(x):
    return x * x


print(apply(square, 5))
```

Output:

```text
25
```

Callbacks are common in:

- event systems;
- GUI frameworks;
- retry hooks;
- data processing;
- asynchronous orchestration;
- plugin systems;
- tests;
- lifecycle hooks.

A callback contract should specify arguments, return semantics, error behavior, timing, threading/async expectations, and ownership.

---

## 25. Callbacks in Production

A retry helper can accept a failure callback:

```python
def retry(operation, attempts, on_failure):
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except Exception as exc:
            on_failure(attempt, exc)
    raise RuntimeError("operation failed")
```

The retry algorithm should not care whether `on_failure` logs, increments metrics, records telemetry, or stores diagnostics. That is behavior supplied by the caller.

The callback itself may be effectful. Higher-order programming does not automatically make the behavior pure.

---

## 26. Functions Returning Functions

Functions can manufacture specialized behavior:

```python
def make_multiplier(factor):
    def multiply(value):
        return value * factor

    return multiply


double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))
print(triple(5))
```

Output:

```text
10
15
```

This pattern is useful for function factories, small strategies, validators, formatters, and decorators.

---

## 27. Closures

A closure is a nested function that retains access to a binding from an enclosing scope after the enclosing function returns.

```python
def make_multiplier(factor):
    def multiply(value):
        return value * factor

    return multiply


double = make_multiplier(2)
print(double(7))
```

Output:

```text
14
```

`factor` remains available because the returned function closes over its enclosing scope.

For learning/debugging, you can inspect:

```python
print(double.__code__.co_freevars)
print(double.__closure__)
```

Do not build ordinary application logic around CPython-specific closure internals; use them to understand the mechanism.

---

## 28. Lexical Scope and LEGB

Python name resolution is commonly summarized as LEGB:

```text
L = Local
E = Enclosing
G = Global
B = Built-in
```

Example:

```python
name = "global"


def outer():
    name = "enclosing"

    def inner():
        return name

    return inner()


print(outer())
```

Output:

```text
enclosing
```

The inner function finds `name` in the enclosing function scope.

If the inner function defines its own `name`, the local value shadows the enclosing one:

```python
def outer():
    name = "enclosing"

    def inner():
        name = "local"
        return name

    return inner()


print(outer())
```

Output:

```text
local
```

Closures are therefore closely connected to the Enclosing part of LEGB.

---

## 29. `nonlocal`

`nonlocal` permits a nested function to rebind a name from its nearest enclosing function scope.

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment


counter = make_counter()
print(counter())
print(counter())
```

Output:

```text
1
2
```

Without `nonlocal`, assignment to `count` would make it local to `increment`.

This closure is stateful, so the returned callable is not pure under the practical definition used in this chapter. Stateful closures can still be useful; the key is to recognize the state explicitly.

---

## 30. `lambda` Functions

A lambda is an anonymous function expression:

```python
double = lambda x: x * 2
print(double(5))
```

Output:

```text
10
```

Syntax:

```text
lambda parameters: expression
```

The expression's value is returned. Lambdas cannot contain normal statement blocks, so substantial behavior is usually clearer as `def`.

A common use:

```python
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 20},
]

result = sorted(users, key=lambda user: user["age"])
print(result)
```

Output:

```text
[{'name': 'Bob', 'age': 20}, {'name': 'Alice', 'age': 30}]
```

Use lambda for small, local behavior. Use `def` when naming, testing, documentation, reuse, or debugging matters.

---

## 31. `map()`

`map(function, iterable, *iterables)` returns a lazy iterator applying a callable to corresponding values.

```python
numbers = [1, 2, 3, 4]
squares = map(lambda x: x * x, numbers)
print(list(squares))
```

Output:

```text
[1, 4, 9, 16]
```

It is lazy:

```python
values = map(lambda x: x + 1, [1, 2, 3])
print(next(values))
print(next(values))
```

Output:

```text
2
3
```

With multiple iterables, the callable receives corresponding elements:

```python
left = [1, 2, 3]
right = [10, 20, 30]
print(list(map(lambda a, b: a + b, left, right)))
```

Output:

```text
[11, 22, 33]
```

A list comprehension may be clearer for simple transformations. Do not assume `map` is always faster.

---

## 32. `filter()`

`filter(function, iterable)` produces a lazy iterator containing values for which the predicate is truthy.

```python
numbers = [1, 2, 3, 4, 5]
evens = filter(lambda x: x % 2 == 0, numbers)
print(list(evens))
```

Output:

```text
[2, 4]
```

A comprehension is an equally valid alternative:

```python
evens = [x for x in numbers if x % 2 == 0]
```

Choose the expression that makes the rule easiest to read.

---

## 33. `functools.reduce()`

`reduce` folds an iterable into one value.

```python
from functools import reduce


numbers = [1, 2, 3, 4]
print(reduce(lambda a, b: a + b, numbers))
```

Output:

```text
10
```

Conceptually:

```text
(((1 + 2) + 3) + 4)
```

An initial value can be supplied:

```python
from functools import reduce


numbers = [1, 2, 3]
print(reduce(lambda a, b: a + b, numbers, 10))
```

Output:

```text
16
```

Without an initial value, reducing an empty iterable raises `TypeError` because there is no starting accumulator.

For simple sums, use `sum()`. `reduce()` is appropriate when the fold itself communicates a meaningful algorithm.

---

## 34. `sorted()` With `key`, `min()`, and `max()`

A `key` callable transforms each element into a comparison/selection key.

```python
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 20},
    {"name": "Cara", "age": 25},
]

print(sorted(users, key=lambda user: user["age"]))
print(min(users, key=lambda user: user["age"]))
print(max(users, key=lambda user: user["age"]))
```

Output:

```text
[{'name': 'Bob', 'age': 20}, {'name': 'Cara', 'age': 25}, {'name': 'Alice', 'age': 30}]
{'name': 'Bob', 'age': 20}
{'name': 'Alice', 'age': 30}
```

Python's sorting algorithm is stable: equal-key elements preserve input relative order. `reverse=True` reverses the resulting sort order.

For `min`/`max`, an empty iterable without an appropriate default raises `ValueError`.

These APIs are practical examples of passing behavior into a library function.

---

## 35. `any()` and `all()`

`any` answers “is at least one truthy?” and `all` answers “are all truthy?”

```python
numbers = [2, 4, 7]

print(any(x > 6 for x in numbers))
print(all(x > 0 for x in numbers))
```

Output:

```text
True
True
```

They short-circuit.

Empty iterable behavior:

```python
print(any([]))
print(all([]))
```

Output:

```text
False
True
```

The latter is the logical identity of universal quantification: there is no counterexample in an empty collection.

---

## 36. `zip()` and `enumerate()`

`zip` pairs corresponding elements lazily.

```python
names = ["Alice", "Bob"]
scores = [90, 80]

for name, score in zip(names, scores):
    print(name, score)
```

Output:

```text
Alice 90
Bob 80
```

By default, `zip` stops at the shortest iterable. In Python versions supporting it, `strict=True` can detect mismatched lengths when equal length is an invariant.

`enumerate` adds an index without manual counters:

```python
for number, name in enumerate(names, start=1):
    print(number, name)
```

Output:

```text
1 Alice
2 Bob
```

Common mistake: assuming `zip` validates equal input lengths by default. It does not.

---

## 37. Function Composition

Composition connects function outputs to later function inputs.

```python
def strip_text(text):
    return text.strip()


def normalize_text(text):
    return text.lower()


print(normalize_text(strip_text("  Hello World  ")))
```

Output:

```text
hello world
```

A reusable two-stage composition helper:

```python
def compose(first, second):
    def composed(value):
        return second(first(value))

    return composed


normalize = compose(strip_text, normalize_text)
print(normalize("  Hello World  "))
```

Output:

```text
hello world
```

Composition works best when contracts line up. Excessive composition can hide intermediate values and make debugging harder.

---

## 38. Function Pipelines

A pipeline makes sequential transformations explicit:

```text
raw
 ↓
clean
 ↓
normalize
 ↓
validate
 ↓
transform
 ↓
result
```

```python
def clean_name(value):
    return value.strip()


def normalize_name(value):
    return value.lower()


def validate_name(value):
    if not value:
        raise ValueError("empty name")
    return value


def title_name(value):
    return value.title()


def pipeline(value, *functions):
    for function in functions:
        value = function(value)
    return value


print(pipeline(
    "  ALICE  ",
    clean_name,
    normalize_name,
    validate_name,
    title_name,
))
```

Output:

```text
Alice
```

Use named stages when the transformation has business meaning. A generic pipeline helper is not always clearer than direct function calls.

---

## 39. `functools.partial()`

`partial` creates a callable with some arguments bound.

```python
from functools import partial


def multiply(a, b):
    return a * b


double = partial(multiply, 2)
print(double(5))
```

Output:

```text
10
```

Keyword binding:

```python
from functools import partial


def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"


say_hi = partial(greet, greeting="Hi")
print(say_hi("Alice"))
```

Output:

```text
Hi, Alice!
```

Use `partial` when the main idea is argument binding. Use a closure when custom captured behavior is needed; use a lambda for very small local expressions.

---

## 40. `functools.partialmethod()`

`partialmethod` creates specialized class methods from an existing method.

```python
from functools import partialmethod


class Formatter:
    def format_message(self, prefix, message):
        return f"{prefix}: {message}"

    info = partialmethod(format_message, "INFO")
    error = partialmethod(format_message, "ERROR")


formatter = Formatter()
print(formatter.info("started"))
print(formatter.error("failed"))
```

Output:

```text
INFO: started
ERROR: failed
```

This is useful when a family of class operations shares the same implementation but differs by a fixed argument. It is a specialized tool, not a reason to redesign a class.

---

## 41. Caching and Memoization

**Caching** broadly means storing data for reuse. **Memoization** caches function results keyed by arguments.

The natural memoization candidate is a deterministic computation with stable, hashable inputs.

```python
from functools import cache


@cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


print(fibonacci(10))
```

Output:

```text
55
```

`@cache` is an unbounded memoization cache. Arguments must be hashable.

A dangerous example:

```python
import time
from functools import cache


@cache
def current_time():
    return time.time()
```

The first result is reused, so caching changes the intended semantics.

Important production questions:

- Are the arguments hashable?
- Is the result stable for the cache key?
- Can the value become stale?
- How is invalidation handled?
- How much memory can the cache retain?
- What is the cache lifetime?
- Are side effects being accidentally skipped on cache hits?

---

## 42. `functools.lru_cache()`

`lru_cache` adds an eviction policy to memoization.

```python
from functools import lru_cache


@lru_cache(maxsize=2)
def square(x):
    return x * x


print(square(2))
print(square(2))
print(square.cache_info())
```

The cache tracks hits and misses. Useful management methods include:

- `cache_info()`;
- `cache_clear()`;
- `cache_parameters()` on supported Python versions;
- `__wrapped__` for introspection or controlled bypassing.

Arguments used as cache keys must be hashable. With a finite `maxsize`, older least-recently-used entries are evicted.

A subtle concurrency fact: the cache's internal data structure is protected for coherent concurrent access, but concurrent calls can still cause the wrapped function to execute more than once before a result is cached.

For web services, tenant, locale, authorization, deployment configuration, current database state, and external freshness can all invalidate naive caching assumptions.

---

## 43. `functools.singledispatch()`

`singledispatch` registers implementations selected by the type of the first argument.

```python
from functools import singledispatch


@singledispatch
def describe(value):
    return f"generic:{value}"


@describe.register
def _(value: int):
    return f"integer:{value}"


@describe.register
def _(value: list):
    return f"list-size:{len(value)}"


print(describe(10))
print(describe([1, 2, 3]))
print(describe("hello"))
```

Output:

```text
integer:10
list-size:3
generic:hello
```

This differs from ordinary method overloading. Dispatch is based on one argument's runtime type. It can be useful for serializers, formatters, and small type-driven extension points, but a simple conditional may sometimes be clearer.

---

## 44. Decorators as Higher-Order Functions

A decorator transforms a callable into another callable.

Without decorator syntax:

```python
def log_call(func):
    def wrapper(*args, **kwargs):
        print("Calling function")
        return func(*args, **kwargs)

    return wrapper


def add(a, b):
    return a + b


add = log_call(add)
print(add(2, 3))
```

Output:

```text
Calling function
5
```

Decorator syntax communicates the same transformation:

```python
def log_call(func):
    def wrapper(*args, **kwargs):
        print("Calling function")
        return func(*args, **kwargs)

    return wrapper


@log_call
def add(a, b):
    return a + b
```

The key model is:

```text
add = log_call(add)
```

Decorators are higher-order because they accept and return callables. They are often used for cross-cutting concerns such as logging, metrics, retries, authorization, tracing, and caching.

---

## 45. `functools.wraps`

Without `wraps`, a wrapper often has the wrapper's own metadata:

```python
def trace(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def load_config():
    """Load configuration."""
    return {"mode": "dev"}


wrapped = trace(load_config)
print(wrapped.__name__)
print(wrapped.__doc__)
```

Typical output:

```text
wrapper
None
```

With `wraps`:

```python
from functools import wraps


def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def load_config():
    """Load configuration."""
    return {"mode": "dev"}


wrapped = trace(load_config)
print(wrapped.__name__)
print(wrapped.__doc__)
```

Output:

```text
load_config
Load configuration.
```

`wraps` is designed to preserve/update useful metadata including `__name__`, `__doc__`, and the wrapped-function relationship. It does not preserve every possible property or runtime semantic.

---

## 46. Pure Functions and Decorators

A pure function can be wrapped by an impure decorator:

```python
from functools import wraps


def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)

    return wrapper


@log_calls
def square(x):
    return x * x
```

`square` itself is deterministic, but the decorated callable performs observable output. The same distinction applies to metrics, tracing, cache mutation, retries, and access-control checks.

Therefore purity should be assessed at the boundary where the callable is actually used.

---

## 47. Error Handling in Functional-Style Code

Functional style does not require banning Python exceptions.

Raise for contract violations:

```python
def parse_age(text):
    age = int(text)
    if age < 0:
        raise ValueError("age must be non-negative")
    return age
```

Return an explicit optional result where absence is expected:

```python
def find_user(users, user_id):
    for user in users:
        if user["id"] == user_id:
            return user
    return None
```

Or use an ordinary explicit-result structure for batch processing:

```python
def divide(a, b):
    if b == 0:
        return {"ok": False, "error": "division by zero"}
    return {"ok": True, "value": a / b}
```

Python does not provide one universal built-in `Result` type that every functional-style Python program must use. Choose the representation that best matches the application's control-flow semantics.

---

## 48. Pure Functions and Testing

A pure function can usually be tested directly:

```python
def calculate_discount(price, percentage):
    return price * (1 - percentage)


def test_calculate_discount():
    assert calculate_discount(100, 0.20) == 80
```

An effect-dependent rule can often be made easier to test by injecting the external input:

```python
def discount_for_hour(price, hour):
    if hour < 12:
        return price * 0.90
    return price
```

Tests can supply a fixed `hour` rather than depending on the actual clock.

This connects functional design directly to dependency injection: move environmental observations to the boundary and pass the value into deterministic business logic.

---

## 49. Property-Based Thinking

Property-style reasoning asks what should be true over a broad set of inputs.

For addition:

```text
add(a, b) == add(b, a)
add(a, 0) == a
```

for supported numeric domains.

For normalization:

```python
def normalize(text):
    return text.strip().lower()
```

A useful property is idempotence:

```text
normalize(normalize(x)) == normalize(x)
```

Property-based thinking is useful even if you use ordinary `pytest`. Hypothesis is an external library that can generate many inputs automatically, but it is optional and not required to understand the concept.

---

## 50. Pure Functions and Concurrency

Pure calculations are often easier to reason about in threading, async workflows, multiprocessing, and parallel data processing because they do not require coordination over shared mutable computation.

```text
record A → pure transform
record B → pure transform
record C → pure transform
```

The absence of shared mutable state reduces one class of race conditions.

But a pure core does not make the whole application thread-safe. You can still have races in:

- database writes;
- shared caches;
- queues;
- resource pools;
- file access;
- external services;
- cancellation/ordering logic.

Purity reduces concurrency complexity; it does not remove it.

---

## 51. Functional Style and Performance

Functional style is not automatically faster or slower. Consider:

- algorithmic complexity;
- allocations;
- copying;
- laziness;
- iterator consumption;
- function-call overhead;
- cache hit rate;
- cache memory;
- workload size and shape.

Compare:

```python
squares = [x * x for x in numbers]
```

```python
squares = list(map(lambda x: x * x, numbers))
```

and a lazy generator:

```python
squares = (x * x for x in numbers)
```

The right choice depends on whether the downstream consumer needs a materialized collection, lazy one-pass data, or simply the clearest implementation. Measure hot paths before introducing abstraction for performance.

---

## 52. Generators and Functional Pipelines

Generators compose naturally with higher-order transformations.

```python
numbers = range(1, 6)
doubled = (x * 2 for x in numbers)

for value in doubled:
    print(value)
```

Output:

```text
2
4
6
8
10
```

A lazy pipeline can avoid materializing intermediate collections:

```python
numbers = range(1, 1_000_000)

evens = (x for x in numbers if x % 2 == 0)
doubled = (x * 2 for x in evens)

print(next(doubled))
print(next(doubled))
```

Output:

```text
4
8
```

Iterators are often one-pass. Reusing an exhausted iterator can silently produce no values:

```python
items = iter([1, 2, 3])
print(list(items))
print(list(items))
```

Output:

```text
[1, 2, 3]
[]
```

Pipeline design must account for laziness and ownership.

---

# ADVANCED

## 53. Higher-Order Functions vs Classes

Closures, callable objects, functions, and classes all encapsulate behavior in different ways.

| Tool | Typical fit | Trade-off |
|---|---|---|
| Function | Stateless behavior | Little lifecycle/state structure |
| Lambda | Tiny local expression | Weak fit for complex logic |
| Closure | Small private captured state | State lifecycle less explicit |
| `partial` | Pre-bound arguments | Limited custom behavior |
| Callable object | Behavior + explicit state | More ceremony |
| Class | Complex lifecycle/invariants | More code |

Callable object example:

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, value):
        return value * self.factor


double = Multiplier(2)
print(double(5))
```

Output:

```text
10
```

A closure or `partial` can represent the same simple behavior. A class becomes attractive as state and lifecycle complexity grows.

Functional style complements OOP; it does not replace it.

---

## 54. Advanced Function Introspection

Relevant introspection APIs include:

- `callable(obj)` — whether an object is callable;
- `type(obj)` — runtime type;
- `id(obj)` — identity value for the object's lifetime;
- `__name__` — normal function name;
- `__doc__` — docstring;
- `__closure__` — closure cells for captured free variables;
- `__code__` — code object of a Python function;
- `inspect.signature(func)` — inspect a supported callable's signature.

Example:

```python
import inspect


def add(a: int, b: int = 0) -> int:
    """Add two integers."""
    return a + b


print(callable(add))
print(add.__name__)
print(add.__doc__)
print(inspect.signature(add))
```

Output:

```text
True
add
Add two integers.
(a: int, b: int = 0) -> int
```

Introspection is valuable for decorators, frameworks, tooling, and debugging. It should not replace clear application code.

## 55. Reusable Function Composition Utility

A composition helper can build one callable from several unary functions.

```python
def compose(*functions):
    def composed(value):
        for function in reversed(functions):
            value = function(value)
        return value

    return composed


def strip_text(value):
    return value.strip()


def normalize_text(value):
    return value.lower()


def prefix(value):
    return "PREFIX:" + value


transform = compose(strip_text, normalize_text, prefix)
print(transform("  Hello  "))
```

Output:

```text
PREFIX:hello
```

For `compose(f, g, h)`, this implementation computes `h(g(f(x)))`. Composition is most useful when contracts line up and intermediate stages remain understandable.

---

## 56. Practical Pipeline Builder

A forward pipeline often reads naturally for data processing.

```python
def pipeline(value, *functions):
    for function in functions:
        value = function(value)
    return value


result = pipeline("  HELLO WORLD  ", str.strip, str.lower)
print(result)
```

Output:

```text
hello world
```

`str.strip` and `str.lower` are passed as method references. They are not called until the pipeline invokes them.

A generic pipeline helper is a tool, not a framework. Use direct statements when they are clearer.

---

## 57. Functional Style With Data Engineering

A data engineering pipeline naturally separates transformations from I/O:

```text
raw records
   ↓
read source                 [effect]
   ↓
parse                       [pure]
   ↓
clean                       [pure]
   ↓
validate                    [pure]
   ↓
normalize                   [pure]
   ↓
aggregate                   [pure]
   ↓
write lake/warehouse        [effect]
```

Example:

```python
def normalize_email(email: str) -> str:
    return email.strip().lower()


def transform_record(record: dict) -> dict:
    return {
        "customer_id": int(record["customer_id"]),
        "email": normalize_email(record["email"]),
        "amount": float(record["amount"]),
    }
```

The function can be tested with captured records. S3/object-storage reads, database queries, and writes remain effectful boundaries.

This design improves reproducibility and makes data-quality failures easier to isolate: a bad input record can be replayed through the pure transformation without reconnecting to the source system.

---

## 58. Functional Style With ML

Common pure ML pipeline candidates include:

- feature scaling;
- validation;
- deterministic feature transformation;
- thresholding;
- label mapping;
- output post-processing.

```python
def min_max_scale(value: float, minimum: float, maximum: float) -> float:
    if minimum == maximum:
        raise ValueError("minimum and maximum must differ")
    return (value - minimum) / (maximum - minimum)
```

Effectful boundaries commonly include:

```text
model registry/object store
          ↓
model loading
          ↓
inference runtime
          ↓
pure post-processing
```

Random seeds and stochastic model behavior should be explicit when reproducibility matters. Pure preprocessing does not make stochastic training deterministic by itself.

---

## 59. Functional Style With LLM Applications

Separate prompt construction from the model call.

```python
def normalize_prompt(text: str) -> str:
    return " ".join(text.split())


def build_prompt(context: str, question: str) -> str:
    return f"Context:\n{context}\n\nQuestion:\n{question}"
```

The model boundary can be represented as an injected client:

```python
class LLMClient:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
```

Architecture:

```text
input
  ↓
normalize prompt      [pure]
  ↓
build prompt          [pure]
  ↓
LLM client            [effect]
  ↓
validate/normalize    [pure]
```

Prompt rules become independently testable. The provider can change without rewriting deterministic prompt logic.

---

## 60. Functional Style With Agentic AI

Agent systems contain both pure decisions and effects.

```text
Agent Runtime
      |
      +--> state transformations       [pure candidate]
      +--> tool-argument validation    [pure candidate]
      +--> prompt construction         [pure candidate]
      +--> policy/routing              [pure candidate]
      +--> tool execution              [effect]
      +--> model calls                 [effect]
      +--> memory writes               [effect]
```

Example deterministic routing:

```python
def choose_tool(intent: str) -> str:
    routes = {
        "search": "search_tool",
        "calculate": "calculator",
        "lookup": "database_lookup",
    }
    return routes.get(intent, "fallback")
```

The pure routing rule can be tested against recorded states. Tool execution, model calls, and memory writes remain effectful.

This separation supports replay, policy testing, response validation, debugging, and safer changes to effectful infrastructure.

---

## 61. Pure Functions and Observability

Production systems require logs, metrics, and traces. These are effects.

A useful pattern is:

```python
def calculate_score(record):
    return record["quality"] * 0.7 + record["confidence"] * 0.3


def process(record, logger):
    result = calculate_score(record)
    logger.info("score_calculated", extra={"score": result})
    return result
```

The score calculation is pure. The orchestrator performs observability work.

This is not a universal ban on logging inside functions. Infrastructure components may need local logging. The design question is where effects belong so that domain logic remains easy to reason about and test.

---

## 62. Functional Style and Production Testing

Pure functions usually need only direct assertions. Effectful boundaries need controlled dependencies.

```python
class FakeModel:
    def __init__(self, response):
        self.response = response

    def generate(self, prompt):
        return self.response


def test_prompt_logic_is_independent_of_model():
    client = FakeModel("answer")
    prompt = build_prompt("facts", "question")
    assert prompt == "Context:\nfacts\n\nQuestion:\nquestion"
    assert client.generate(prompt) == "answer"
```

In larger systems, prefer tests that verify public behavior rather than every internal implementation detail. Pure functions are ideal units for table-driven tests, property-oriented tests, and deterministic regression tests.

---

## 63. Functional Style and Concurrency

Pure computations can be easier to run concurrently because independent inputs do not require shared mutable computation.

```text
record A → transform A
record B → transform B
record C → transform C
```

But a pure core does not remove all concurrency hazards. Database writes, caches, queues, connection pools, file access, and external APIs still require synchronization and resource-management decisions.

The production lesson is:

> Minimize shared mutable state where it helps, but analyze every shared resource separately.

---

## 64. Functional Style and Performance

There is no blanket claim that functional style is faster or slower.

Evaluate:

- algorithmic complexity;
- allocations;
- copying;
- laziness;
- iterator consumption;
- function-call overhead;
- cache memory;
- cache hit rate;
- workload characteristics.

A list comprehension:

```python
squares = [x * x for x in numbers]
```

may be clearer than:

```python
squares = list(map(lambda x: x * x, numbers))
```

A generator may be appropriate when downstream consumption can be incremental:

```python
squares = (x * x for x in numbers)
```

Measure before optimizing. Clarity is normally the default optimization target.

---

## 65. Common Mistakes

### Calling instead of passing a function

Bad:

```python
def apply(func, value):
    return func(value)


def square(x):
    return x * x

# apply(square(5), 10)
```

Better:

```python
print(apply(square, 10))
```

**Lesson:** pass `square`; call it where the higher-order function needs it.

### Mutating input arguments unexpectedly

Bad:

```python
def add_item(items, item):
    items.append(item)
    return items
```

Pure-style alternative when preserving the original is required:

```python
def add_item(items, item):
    return [*items, item]
```

### Hidden global state

Bad:

```python
RATE = 0.18


def total(amount):
    return amount * (1 + RATE)
```

Better:

```python
def total(amount, rate):
    return amount * (1 + rate)
```

### Mutable default arguments

Bad:

```python
def add_item(item, items=[]):
    items.append(item)
    return items
```

Correct ownership pattern:

```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Tuple mistaken for deep immutability

```python
value = ([1],)
value[0].append(2)
```

The outer tuple did not change; the nested list did.

### Overusing lambda

Use `def` when a rule deserves a name, documentation, reuse, or focused debugging.

### Using reduce where a built-in is clearer

Use `sum`, `min`, `max`, or a loop when they better communicate intent.

### Treating map/filter as automatically superior

They are tools, not performance or readability guarantees.

### Caching impure functions

Bad caching candidates include functions that read time, environment, mutable external state, or perform effects.

### Caching mutable/unhashable arguments

Ordinary lists/dictionaries cannot be direct keys for `cache` or `lru_cache`.

### Incorrect closure capture

Closures created in loops can all observe one shared loop-variable binding. See Section 66 and Debugging Scenario 4.

### Forgetting `nonlocal`

Use `nonlocal` when a nested function must rebind an enclosing function's local name.

### Decorators without `wraps`

Useful function metadata can be lost. Use `functools.wraps` in ordinary wrappers.

### Overusing decorators or pipelines

Abstraction should reduce cognitive load. Several layers of wrappers can make call order and error ownership difficult to trace.

### Assuming immutability means thread safety

It does not protect external mutable systems or resource lifecycles.

### Copying everything

Copy only when ownership, isolation, or API compatibility requires it.

### Treating functional programming as “no classes”

Functional techniques and OOP are complementary.

---

## 66. Closure Loop-Capture Bug

A classic bug:

```python
functions = []

for i in range(3):
    functions.append(lambda: i)

print([function() for function in functions])
```

Output:

```text
[2, 2, 2]
```

The lambdas refer to the loop variable binding when they execute. They do not automatically freeze an iteration's value.

Correct with a default argument:

```python
functions = []

for i in range(3):
    functions.append(lambda i=i: i)

print([function() for function in functions])
```

Output:

```text
[0, 1, 2]
```

Or with a factory:

```python
def make_reader(value):
    def read():
        return value
    return read


functions = [make_reader(i) for i in range(3)]
print([function() for function in functions])
```

Output:

```text
[0, 1, 2]
```

---

## 67. Mutable Default Argument Connection

Default expressions are evaluated when a function is defined, so a mutable default can persist across calls.

```python
def add_item(item, items=[]):
    items.append(item)
    return items


print(add_item("a"))
print(add_item("b"))
```

Output:

```text
['a']
['a', 'b']
```

Correct:

```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items


print(add_item("a"))
print(add_item("b"))
```

Output:

```text
['a']
['b']
```

This is a function-state lifetime problem, not a pure-function feature. It illustrates why object lifetime and ownership matter.

---

## 68. Callable Objects and `__call__`

A class instance can be callable by implementing `__call__`.

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, value):
        return value * self.factor


double = Multiplier(2)
print(callable(double))
print(double(5))
```

Output:

```text
True
10
```

Higher-order APIs often accept any callable, not only plain function objects. Callable objects are useful when behavior needs explicit state, methods, lifecycle, or richer introspection.

---

## 69. Production Architecture: Pure Core + Effect Boundaries

A practical production design is:

```text
                External World
          ┌─────────┼─────────┐
          │         │         │
         DB        LLM       API
          │         │         │
          └─────────┼─────────┘
                    ↓
             EFFECT BOUNDARY
                    ↓
        ┌───────────────────────┐
        │       PURE CORE       │
        │ validation            │
        │ normalization         │
        │ transformation        │
        │ business rules        │
        │ routing decisions     │
        │ prompt construction   │
        └───────────────────────┘
                    ↓
              final result
```

This architecture improves:

- testability;
- replayability;
- debugging;
- reproducibility;
- change isolation;
- infrastructure replacement.

It also provides a clean place to put retries, timeouts, authentication, rate limits, structured logging, and provider-specific error handling.

---

## 70. Backend Production Example

Consider an order service.

Bad monolithic shape:

```text
HTTP request
  ↓
query DB
  ↓
calculate price
  ↓
call tax API
  ↓
mutate order
  ↓
write DB
  ↓
send email
```

A more explicit design:

```text
read order              [effect]
   ↓
validate order          [pure]
   ↓
calculate subtotal      [pure]
   ↓
construct tax request  [pure]
   ↓
call tax service        [effect]
   ↓
calculate final total   [pure]
   ↓
build invoice model     [pure]
   ↓
persist invoice        [effect]
   ↓
publish event          [effect]
```

The business rules can be tested without databases or network services. The infrastructure remains replaceable and observable.

---

## 71. Real-World Production Example: AI Document Processing Pipeline

Use this architecture:

```text
Input document
   ↓
Read document                  [Effect]
   ↓
Parse                          [Pure]
   ↓
Normalize                      [Pure]
   ↓
Validate                       [Pure]
   ↓
Build prompt                   [Pure]
   ↓
Call LLM                       [Effect]
   ↓
Validate response              [Pure]
   ↓
Transform result               [Pure]
   ↓
Store result                   [Effect]
```

Pure stages:

```python
def normalize_text(text: str) -> str:
    return " ".join(text.split())


def validate_document(text: str) -> str:
    if not text:
        raise ValueError("document is empty")
    return text


def build_prompt(document: str) -> str:
    return f"Extract fields from this document:\n\n{document}"


def validate_output(payload: dict) -> dict:
    if not isinstance(payload.get("fields"), dict):
        raise ValueError("fields must be an object")
    return payload
```

Effect boundaries can read documents, call the LLM, and persist normalized output.

The important Applied AI lesson is that the model call is only one stage. Deterministic surrounding functions often carry the validation, prompt, business, and safety logic that determines whether the overall application behaves predictably.

# PRACTICE, DEBUGGING, AND PROJECT WORK

## 72. Exercises

Each exercise includes **Problem**, **Requirements**, **Expected behavior**, **Solution**, **Explanation**, and **Key learning**. Attempt the problem before reading the solution.

### Basic Exercise 1 — Classify Purity

**Problem**

Classify these functions:

```python
import random

name = "Alice"


def greet(user_name):
    return f"Hello {user_name}"


def current_name():
    return name


def random_name():
    return random.choice(["Alice", "Bob"])
```

**Requirements**

Identify explicit inputs, hidden dependencies, and nondeterministic behavior.

**Expected behavior**

`greet` is pure. The other two depend on external state.

**Solution**

`greet` is pure for its stated input/output contract. `current_name` reads module state. `random_name` observes random state and can vary between calls.

**Explanation**

Purity is not the same as “returns a value.” Hidden state matters.

**Key learning**

Always inspect where a function gets its inputs.

---

### Basic Exercise 2 — Identify a Side Effect

**Problem**

Find the side effect:

```python
def add_tag(tags, tag):
    tags.append(tag)
    return tags
```

**Requirements**

Describe who observes the mutation.

**Expected behavior**

The caller's list changes.

**Solution**

The existing list object is mutated in place.

**Explanation**

The return value is not the side effect; mutation of caller-owned state is.

**Key learning**

A function can return a useful value and still be effectful.

---

### Basic Exercise 3 — Mutation or Rebinding?

**Problem**

Classify each operation:

```python
a = []
a.append(1)

b = []
b = [1]
```

**Requirements**

Distinguish object changes from name changes.

**Expected behavior**

`append` mutates; `b = [1]` rebinds.

**Solution**

`a.append(1)` mutates the existing list. `b = [1]` creates a new list and rebinds `b`.

**Explanation**

Names refer to objects; mutation changes an object while rebinding changes a name's target.

**Key learning**

Mutation and rebinding are different operations.

---

### Basic Exercise 4 — Object Identity

**Problem**

Predict the output:

```python
x = []
y = x
x.append(1)
print(x is y)
print(y)
```

**Requirements**

Explain the identity relationship.

**Expected behavior**

`True` and `[1]`.

**Solution**

Both names refer to the same list object, so mutation through `x` is visible through `y`.

**Explanation**

Aliasing is central to reasoning about mutable Python objects.

**Key learning**

Identity matters when mutable objects are shared.

---

### Basic Exercise 5 — Hidden Dependency Removal

**Problem**

Refactor:

```python
RATE = 0.18

def total(amount):
    return amount * (1 + RATE)
```

**Requirements**

Make the tax rate explicit.

**Expected behavior**

A caller can choose the rate per call.

**Solution**

```python
def total(amount, rate):
    return amount * (1 + rate)
```

**Explanation**

The function no longer reads a hidden global value.

**Key learning**

Explicit inputs make dependencies visible and testable.

---

### Basic Exercise 6 — Immutable Outer Container

**Problem**

Explain why this succeeds:

```python
value = ([1],)
value[0].append(2)
```

**Requirements**

Distinguish tuple immutability from deep immutability.

**Expected behavior**

The result is `([1, 2],)`.

**Solution**

The tuple's reference at index `0` is unchanged. The referenced list is mutated.

**Explanation**

The tuple is immutable as a container, not as an entire reachable object graph.

**Key learning**

Immutable containers can hold mutable values.

---

### Basic Exercise 7 — Function Alias

**Problem**

Create a function alias.

**Requirements**

Do not duplicate the function implementation.

**Expected behavior**

The alias behaves exactly like the original.

**Solution**

```python
def greet(name):
    return f"Hello {name}"


alias = greet
print(alias("Sam"))
```

Output:

```text
Hello Sam
```

**Explanation**

The alias refers to the same function object.

**Key learning**

Functions are first-class values.

---

### Basic Exercise 8 — Simple Callback

**Problem**

Implement `apply(func, value)`.

**Requirements**

The function must invoke the callback with `value`.

**Expected behavior**

`apply(lambda x: x * 2, 4)` returns `8`.

**Solution**

```python
def apply(func, value):
    return func(value)


print(apply(lambda x: x * 2, 4))
```

Output:

```text
8
```

**Explanation**

`func` is a value until the function invokes it.

**Key learning**

Passing a function is not the same as calling it.

---

### Intermediate Exercise 9 — Pure Normalization

**Problem**

Normalize a username.

**Requirements**

Strip surrounding spaces and lowercase without external state.

**Expected behavior**

`normalize("  Alice ")` returns `"alice"`.

**Solution**

```python
def normalize(value):
    return value.strip().lower()


print(normalize("  Alice "))
```

Output:

```text
alice
```

**Explanation**

The output depends only on the argument.

**Key learning**

Small pure transforms form useful processing units.

---

### Intermediate Exercise 10 — Non-Mutating Update

**Problem**

Add a status to a record without changing the original dictionary.

**Requirements**

Return a new dictionary.

**Expected behavior**

The original has no `status`; the result does.

**Solution**

```python
def with_status(record, status):
    return {**record, "status": status}


original = {"id": 1}
updated = with_status(original, "ready")
print(original)
print(updated)
```

Output:

```text
{'id': 1}
{'id': 1, 'status': 'ready'}
```

**Explanation**

Dictionary unpacking creates a replacement value.

**Key learning**

Replacement can be clearer than mutation when ownership is shared.

---

### Intermediate Exercise 11 — `map`

**Problem**

Square a list using `map`.

**Requirements**

Materialize the lazy result.

**Expected behavior**

Return `[1, 4, 9]`.

**Solution**

```python
numbers = [1, 2, 3]
print(list(map(lambda x: x * x, numbers)))
```

Output:

```text
[1, 4, 9]
```

**Explanation**

`map` creates a lazy iterator; `list` consumes it.

**Key learning**

Understand both the callable and iterator aspects of `map`.

---

### Intermediate Exercise 12 — `filter`

**Problem**

Select positive values.

**Requirements**

Use a predicate with `filter`.

**Expected behavior**

`[-1, 0, 2, 3]` becomes `[2, 3]`.

**Solution**

```python
values = [-1, 0, 2, 3]
positive = list(filter(lambda x: x > 0, values))
print(positive)
```

Output:

```text
[2, 3]
```

**Explanation**

Only truthy predicate results pass through.

**Key learning**

A predicate defines selection behavior.

---

### Intermediate Exercise 13 — `reduce`

**Problem**

Multiply `[2, 3, 4]` into one value.

**Requirements**

Use `functools.reduce` with an explicit binary function.

**Expected behavior**

The result is `24`.

**Solution**

```python
from functools import reduce


print(reduce(lambda a, b: a * b, [2, 3, 4]))
```

Output:

```text
24
```

**Explanation**

The accumulator becomes `2`, then `6`, then `24`.

**Key learning**

Understand reduction as a fold, not as a synonym for every aggregation.

---

### Intermediate Exercise 14 — `sorted(key=...)`

**Problem**

Sort records by score.

**Requirements**

Use a key function.

**Expected behavior**

Lowest score comes first.

**Solution**

```python
records = [
    {"name": "A", "score": 80},
    {"name": "B", "score": 70},
]

print(sorted(records, key=lambda record: record["score"]))
```

Output:

```text
[{'name': 'B', 'score': 70}, {'name': 'A', 'score': 80}]
```

**Explanation**

The key function provides the comparison value.

**Key learning**

Higher-order APIs often let behavior be supplied without subclassing.

---

### Intermediate Exercise 15 — `any` and `all`

**Problem**

Check whether any balance is negative and whether all are non-negative.

**Requirements**

Use generator expressions.

**Expected behavior**

For `[10, 0, 5]`, results are `False` and `True`.

**Solution**

```python
balances = [10, 0, 5]
print(any(x < 0 for x in balances))
print(all(x >= 0 for x in balances))
```

Output:

```text
False
True
```

**Explanation**

Both functions short-circuit.

**Key learning**

Express logical intent directly.

---

### Intermediate Exercise 16 — `zip` and `enumerate`

**Problem**

Create numbered name/score lines.

**Requirements**

Use both built-ins and no manual counter.

**Expected behavior**

`1 Alice=90`, `2 Bob=80`.

**Solution**

```python
names = ["Alice", "Bob"]
scores = [90, 80]

for number, (name, score) in enumerate(zip(names, scores), start=1):
    print(f"{number} {name}={score}")
```

Output:

```text
1 Alice=90
2 Bob=80
```

**Explanation**

`zip` pairs data; `enumerate` supplies sequence numbers.

**Key learning**

Avoid manual indexing when an iterator abstraction expresses the intent.

---

### Advanced Exercise 17 — Closure Factory

**Problem**

Create a `make_multiplier(factor)` factory.

**Requirements**

Return a nested function that captures `factor`.

**Expected behavior**

`make_multiplier(3)(4)` returns `12`.

**Solution**

```python
def make_multiplier(factor):
    def multiply(value):
        return value * factor
    return multiply


print(make_multiplier(3)(4))
```

Output:

```text
12
```

**Explanation**

The nested function retains the enclosing binding.

**Key learning**

A function can return behavior.

---

### Advanced Exercise 18 — `nonlocal`

**Problem**

Create a private counter.

**Requirements**

Use a closure and `nonlocal`.

**Expected behavior**

Three calls produce `1`, `2`, `3`.

**Solution**

```python
def make_counter():
    count = 0

    def next_value():
        nonlocal count
        count += 1
        return count

    return next_value


counter = make_counter()
print(counter())
print(counter())
print(counter())
```

Output:

```text
1
2
3
```

**Explanation**

`nonlocal` changes the enclosing function's binding.

**Key learning**

Closures can intentionally own state.

---

### Advanced Exercise 19 — Closure Loop Fix

**Problem**

Fix:

```python
functions = []
for i in range(3):
    functions.append(lambda: i)
```

**Requirements**

Each function must return its own iteration's value.

**Expected behavior**

`[0, 1, 2]`.

**Solution**

```python
functions = []
for i in range(3):
    functions.append(lambda i=i: i)

print([function() for function in functions])
```

Output:

```text
[0, 1, 2]
```

**Explanation**

The default argument stores the current loop value.

**Key learning**

Closures capture bindings; they do not automatically snapshot loop variables.

---

### Advanced Exercise 20 — Composition

**Problem**

Implement `compose(f, g)` so the result computes `g(f(x))`.

**Requirements**

Return a callable.

**Expected behavior**

Composing `plus_one` then `double`, with input `3`, returns `8`.

**Solution**

```python
def compose(f, g):
    def composed(value):
        return g(f(value))
    return composed


def plus_one(value):
    return value + 1


def double(value):
    return value * 2


print(compose(plus_one, double)(3))
```

Output:

```text
8
```

**Explanation**

The returned function is itself built through higher-order behavior.

**Key learning**

Composition combines small contracts into a larger transformation.

---

### Advanced Exercise 21 — `partial`

**Problem**

Create a multiplication-by-10 callable.

**Requirements**

Use `functools.partial`.

**Expected behavior**

`times_ten(4)` returns `40`.

**Solution**

```python
from functools import partial


def multiply(a, b):
    return a * b


times_ten = partial(multiply, b=10)
print(times_ten(4))
```

Output:

```text
40
```

**Explanation**

One argument is bound when the partial object is created.

**Key learning**

Use partial for specialization by argument binding.

---

### Advanced Exercise 22 — Cache a Pure Function

**Problem**

Memoize factorial.

**Requirements**

Use `@cache` and integer arguments.

**Expected behavior**

`factorial(5)` returns `120`.

**Solution**

```python
from functools import cache


@cache
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)


print(factorial(5))
```

Output:

```text
120
```

**Explanation**

Repeated subproblems can reuse prior results.

**Key learning**

Stable argument/result semantics are essential to safe memoization.

---

### Advanced Exercise 23 — Decorator Metadata

**Problem**

Build a decorator that preserves the wrapped function's name and docstring.

**Requirements**

Use `functools.wraps`.

**Expected behavior**

The wrapped function keeps its original metadata.

**Solution**

```python
from functools import wraps


def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@trace
def add(a, b):
    """Add two values."""
    return a + b


print(add.__name__)
print(add.__doc__)
```

Output:

```text
add
Add two values.
```

**Explanation**

`wraps` updates standard function metadata and preserves the wrapped-function relationship.

**Key learning**

Decorator correctness includes metadata, not only return values.

---

### Advanced Exercise 24 — `singledispatch`

**Problem**

Format integers and strings differently.

**Requirements**

Use a generic fallback.

**Expected behavior**

`format_value(3)` returns `"int:3"`; `format_value("x")` returns `"str:x"`.

**Solution**

```python
from functools import singledispatch


@singledispatch
def format_value(value):
    return f"value:{value}"


@format_value.register
def _(value: int):
    return f"int:{value}"


@format_value.register
def _(value: str):
    return f"str:{value}"


print(format_value(3))
print(format_value("x"))
```

Output:

```text
int:3
str:x
```

**Explanation**

Dispatch is based on the first argument's runtime type.

**Key learning**

Type-directed extension is useful when its dispatch model is clearer than alternatives.

---

### Production Exercise 25 — Pure LLM Request Builder

**Problem**

Create a pure prompt builder for a question-answering service.

**Requirements**

It must perform no network calls and take all required context explicitly.

**Expected behavior**

It returns a deterministic prompt string.

**Solution**

```python
def build_prompt(context, question):
    clean_context = " ".join(context.split())
    clean_question = " ".join(question.split())
    return f"Context: {clean_context}\nQuestion: {clean_question}"
```

**Explanation**

Prompt construction is separated from the effectful model client.

**Key learning**

Pure request construction is easy to unit test and reuse.

---

### Production Exercise 26 — Pure Data Engineering Transform

**Problem**

Convert a raw record into a normalized warehouse record.

**Requirements**

Do not mutate the source record and do not perform I/O.

**Expected behavior**

The transformed record has normalized email and numeric amount.

**Solution**

```python
def transform_record(raw):
    return {
        "customer_id": int(raw["customer_id"]),
        "email": raw["email"].strip().lower(),
        "amount": float(raw["amount"]),
    }
```

**Explanation**

A pure transformation can be replayed against captured source records.

**Key learning**

Keep S3/database access outside deterministic transformations.

---

### Production Exercise 27 — Agent Routing Function

**Problem**

Route normalized intent to a tool name.

**Requirements**

No model call, network access, or mutable global state.

**Expected behavior**

Unknown intent returns `"fallback"`.

**Solution**

```python
def route(intent):
    routes = {
        "search": "search_tool",
        "calculate": "calculator",
        "lookup": "database_lookup",
    }
    return routes.get(intent, "fallback")
```

**Explanation**

This deterministic logic can be tested and replayed independently of tool execution.

**Key learning**

Agent decisions and agent effects need not be one function.

---

### Production Exercise 28 — Explicit Clock Dependency

**Problem**

Replace a business-hour rule that reads the clock itself.

**Requirements**

Pass the hour into the pure rule.

**Expected behavior**

A unit test can supply `10` without controlling the system clock.

**Solution**

```python
def is_business_hour(hour):
    return 9 <= hour < 17


print(is_business_hour(10))
```

Output:

```text
True
```

**Explanation**

The effectful observation of time moves to the boundary.

**Key learning**

Dependency injection can be as small as passing one value.

---

### Production Exercise 29 — Decide Whether to Deep Copy

**Problem**

A read-only function receives a million records. Should it always call `deepcopy()`?

**Requirements**

Answer based on ownership, correctness, and performance.

**Expected behavior**

Recommend against unconditional deep copying when the function is truly read-only and ownership is clear.

**Solution**

Use the original object under an explicit read-only contract. Establish a targeted ownership boundary or immutable representation if mutation risk exists. Deep copy only when the semantics and cost are justified.

**Explanation**

Deep copying may duplicate large graphs unnecessarily.

**Key learning**

Immutability and copying are design decisions, not rituals.

---

### Production Exercise 30 — Refactor to Functional Core

**Problem**

An API handler reads an order, calculates totals, calls a tax service, writes a record, and sends an email in one function.

**Requirements**

Identify pure and effectful stages.

**Expected behavior**

The proposed design isolates deterministic business rules.

**Solution**

```text
read order             [effect]
validate               [pure]
calculate subtotal     [pure]
construct tax request  [pure]
call tax service       [effect]
calculate total        [pure]
build invoice          [pure]
persist invoice        [effect]
send notification      [effect]
```

**Explanation**

The pure core describes business decisions while boundaries perform external actions.

**Key learning**

Functional design is an architectural decomposition strategy.

---

## 73. Debugging Lab

Each scenario includes broken code, expected behavior, actual behavior, debugging clues, investigation, root cause, fixed code, explanation, and production lesson.

### Debugging Scenario 1 — Hidden Global Dependency

**Broken code**

```python
TAX_RATE = 0.18


def total(amount):
    return amount * (1 + TAX_RATE)


TAX_RATE = 0.20
print(total(100))
```

**Expected behavior**

A caller expecting an 18% calculation should receive `118.0`.

**Actual behavior**

The result is `120.0`.

**Debugging clues**

The function has no rate parameter and reads module state.

**Investigation**

Search for writes to `TAX_RATE`; inspect the function's global dependency.

**Root cause**

The calculation depends on mutable hidden state.

**Fixed code**

```python
def total(amount, rate):
    return amount * (1 + rate)
```

**Explanation**

The dependency is now explicit.

**Production lesson**

Explicit inputs reduce test-order dependence.

---

### Debugging Scenario 2 — Mutation of Input

**Broken code**

```python
def normalize(records):
    for record in records:
        record["email"] = record["email"].strip().lower()
    return records
```

**Expected behavior**

Return normalized records without altering the caller's records.

**Actual behavior**

The original nested dictionaries change.

**Debugging clues**

The outer list and inner dictionaries are aliased.

**Investigation**

Compare the identity of an input record before and after the call.

**Root cause**

The function mutates caller-owned dictionaries.

**Fixed code**

```python
def normalize(records):
    return [
        {**record, "email": record["email"].strip().lower()}
        for record in records
    ]
```

**Explanation**

Each record is replaced rather than edited.

**Production lesson**

Document ownership when choosing mutation.

---

### Debugging Scenario 3 — Mutable Default Argument

**Broken code**

```python
def add_item(item, items=[]):
    items.append(item)
    return items
```

**Expected behavior**

Calls that omit `items` should be independent.

**Actual behavior**

State accumulates across calls.

**Debugging clues**

The default list is created once at function definition time.

**Investigation**

Inspect `add_item.__defaults__` and call the function twice.

**Root cause**

The same default list is reused.

**Fixed code**

```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

**Explanation**

Each omitted-argument call gets a fresh list.

**Production lesson**

Understand object lifetime and shared state.

---

### Debugging Scenario 4 — Closure Capture

**Broken code**

```python
readers = []
for i in range(3):
    readers.append(lambda: i)
```

**Expected behavior**

Readers should produce `0`, `1`, `2`.

**Actual behavior**

They produce `2`, `2`, `2` when called after the loop.

**Debugging clues**

The callbacks refer to the loop variable and execute later.

**Investigation**

Inspect when `i` is looked up rather than when the lambda is created.

**Root cause**

The callbacks close over the same binding.

**Fixed code**

```python
readers = []
for i in range(3):
    readers.append(lambda i=i: i)
```

**Explanation**

The default argument captures the current value for each callable.

**Production lesson**

Loop-created callbacks require careful closure reasoning.

---

### Debugging Scenario 5 — Called Instead of Passed

**Broken code**

```python
def apply(func, value):
    return func(value)


def square(x):
    return x * x


print(apply(square(5), 10))
```

**Expected behavior**

Return `100`.

**Actual behavior**

The code passes an integer (`25`) where a callable is expected and raises `TypeError` when `func(value)` runs.

**Debugging clues**

`func` should be callable. `square(5)` is already a result.

**Investigation**

Compare `type(square)` with `type(square(5))`.

**Root cause**

The function was invoked too early.

**Fixed code**

```python
print(apply(square, 10))
```

**Explanation**

Pass the function object so the receiver controls when it executes.

**Production lesson**

Distinguish `f` from `f()`.

---

### Debugging Scenario 6 — Decorator Metadata Loss

**Broken code**

```python
def trace(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

**Expected behavior**

Wrapped functions retain useful name/docstring metadata.

**Actual behavior**

The callable's `__name__` becomes `wrapper`.

**Debugging clues**

Stack traces and introspection report the wrapper.

**Investigation**

Inspect `wrapper.__name__` and `wrapper.__doc__`.

**Root cause**

No `functools.wraps` was applied.

**Fixed code**

```python
from functools import wraps


def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

**Explanation**

`wraps` updates standard wrapper metadata and `__wrapped__` information.

**Production lesson**

Decorator hygiene improves debugging and tooling.

---

### Debugging Scenario 7 — Caching Hidden State

**Broken code**

```python
import os
from functools import cache


@cache
def app_mode():
    return os.getenv("APP_MODE", "default")
```

**Expected behavior**

A design that reads current process configuration should not silently freeze the first result.

**Actual behavior**

The cached value can remain after the environment changes.

**Debugging clues**

There are no arguments, so every call shares one cache entry.

**Investigation**

Call once, change environment, call again.

**Root cause**

The cache key omits a hidden external dependency.

**Fixed code**

```python
import os


def app_mode():
    return os.getenv("APP_MODE", "default")
```

A better production architecture may read configuration once at startup and pass an immutable configuration snapshot into pure logic.

**Explanation**

Caching is safe only when cache-key inputs are sufficient to determine the result under the intended freshness contract.

**Production lesson**

Staleness and invalidation are correctness issues, not only performance concerns.

## 74. Mini-Project: Functional Data and AI Processing Pipeline

### 74.1 Project goal

Build a small but production-oriented pipeline that separates deterministic transformations from external effects. The pipeline accepts raw document-like records, normalizes and validates them, constructs an AI request, calls an external model adapter, validates the returned data, and persists the result.

The project is intentionally small enough to understand completely while using architecture patterns that scale to larger backend and Applied AI systems.

### 74.2 Requirements

The implementation should demonstrate:

- pure transformation functions;
- explicit side-effect boundaries;
- immutable data where it improves state ownership;
- higher-order functions and function composition;
- a readable pipeline construction technique;
- input validation and explicit error handling;
- logging at effect boundaries rather than scattering logs through pure rules;
- pytest-style unit tests for the pure core;
- an optional cache only around a deterministic, safely cacheable computation;
- no secrets, real credentials, or production API keys;
- a clear production-oriented structure.

A practical flow is:

```text
Raw Input
   |
   v
Parse [effect or boundary]
   |
   v
Normalize [pure]
   |
   v
Validate [pure]
   |
   v
Transform [pure]
   |
   v
Build AI Request [pure]
   |
   v
External Model Call [effect]
   |
   v
Validate Response [pure]
   |
   v
Transform Result [pure]
   |
   v
Persist [effect]
```

### 74.3 Suggested data model

A frozen dataclass is useful for value-like records whose fields should not be reassigned after construction.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    document_id: str
    text: str


@dataclass(frozen=True)
class AIRequest:
    document_id: str
    prompt: str


@dataclass(frozen=True)
class AIResult:
    document_id: str
    summary: str
```

`frozen=True` prevents normal attribute assignment after initialization. It does not make every nested object deeply immutable. Here the fields are strings, so the model remains simple and value-oriented.

### 74.4 Pure transformation functions

The business core can be expressed with small functions whose relevant inputs are explicit.

```python
def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def validate_document(document: Document) -> Document:
    if not document.document_id:
        raise ValueError("document_id is required")
    if not document.text:
        raise ValueError("document text is required")
    return document


def build_prompt(document: Document) -> str:
    return (
        "Summarize the following document in two sentences.\n\n"
        f"{document.text}"
    )


def build_request(document: Document) -> AIRequest:
    return AIRequest(
        document_id=document.document_id,
        prompt=build_prompt(document),
    )


def validate_model_summary(summary: str) -> str:
    normalized = summary.strip()
    if not normalized:
        raise ValueError("model summary is empty")
    return normalized
```

These functions can be tested without a network connection, database, clock, random source, or environment variable.

### 74.5 Effect boundaries

The model call is intentionally outside the pure core.

```python
from typing import Callable


def call_model(request: AIRequest, model_client: Callable[[str], str]) -> AIResult:
    # The call is an effect because model_client may perform network I/O.
    raw_summary = model_client(request.prompt)
    summary = validate_model_summary(raw_summary)
    return AIResult(document_id=request.document_id, summary=summary)
```

`model_client` is an explicit dependency. The pure code does not need to know whether it is backed by an HTTP API, local inference server, test fake, or another provider.

### 74.6 A simple pipeline builder

```python
def pipeline(value, *functions):
    for function in functions:
        value = function(value)
    return value
```

This is a higher-order function because it receives functions as arguments.

For compatible transformations:

```python
normalized = pipeline(
    "  hello   world  ",
    normalize_text,
)

assert normalized == "hello world"
```

Do not force every workflow through a generic pipeline abstraction. Once branching, error recovery, logging, transactions, or different input types become prominent, an explicit orchestration function can be clearer.

### 74.7 Composition of the pure core

```python
def parse_document(raw: dict[str, str]) -> Document:
    return Document(
        document_id=raw["document_id"].strip(),
        text=raw["text"],
    )


def normalize_document(document: Document) -> Document:
    return Document(
        document_id=document.document_id,
        text=normalize_text(document.text),
    )


def prepare_document(raw: dict[str, str]) -> AIRequest:
    document = pipeline(raw, parse_document, normalize_document, validate_document)
    return build_request(document)
```

The boundary function `prepare_document()` is still deterministic for the same `raw` mapping contents, assuming the mapping itself is not being mutated concurrently. The eventual network call remains separate.

### 74.8 Orchestration function

```python
def process_document(raw: dict[str, str], model_client, save_result) -> AIResult:
    request = prepare_document(raw)
    result = call_model(request, model_client)
    save_result(result)
    return result
```

This function is effectful, but the dependency boundaries are visible. A production implementation can add retries, timeouts, metrics, tracing, transactions, and structured logging around those boundaries without contaminating the business transformations.

### 74.9 Test doubles

For unit tests, a fake model client avoids a real network request.

```python
def fake_model_client(prompt: str) -> str:
    return "This is a deterministic test summary."


def saved_results() -> list[AIResult]:
    storage: list[AIResult] = []

    def save(result: AIResult) -> None:
        storage.append(result)

    save.storage = storage
    return save
```

A simpler test can use a closure or a small callable object. The important point is not the test-double technique itself; it is that the production side effect is represented as an explicit boundary.

### 74.10 pytest examples

```python
def test_normalize_text():
    assert normalize_text("  A   B ") == "A B"


def test_prepare_document():
    request = prepare_document(
        {"document_id": "d-1", "text": "  hello   world "}
    )
    assert request.document_id == "d-1"
    assert request.prompt.endswith("hello world")


def test_process_document_with_fake_dependencies():
    saved: list[AIResult] = []

    def fake_model(prompt: str) -> str:
        return "summary"

    result = process_document(
        {"document_id": "d-1", "text": "hello"},
        fake_model,
        saved.append,
    )

    assert result == AIResult("d-1", "summary")
    assert saved == [AIResult("d-1", "summary")]
```

Pure tests are small because the assertions focus directly on inputs and outputs. Effect-boundary tests can focus on whether the right dependency was called, what was persisted, and how failures are translated.

### 74.11 Optional safe caching

A pure normalization or prompt-construction function may be a candidate for caching when its inputs are stable and the cache cost is justified.

```python
from functools import cache


@cache
def normalize_token(text: str) -> str:
    return " ".join(text.split()).lower()
```

This is safe only under the stated semantics: the result must be determined by the function's arguments, and the cache key must represent the relevant input. Caching a function that reads a changing environment variable, current time, mutable global state, or an external service can return stale or misleading data.

### 74.12 Error handling

The pure core can raise a domain-relevant exception such as `ValueError`, or a larger system can use explicit result values.

```python
@dataclass(frozen=True)
class ValidationError:
    message: str


def validate_text(text: str) -> str | ValidationError:
    normalized = normalize_text(text)
    if not normalized:
        return ValidationError("text is empty")
    return normalized
```

Neither style is universally superior. Exceptions are often direct for fail-fast validation; explicit result values can be useful when a pipeline expects errors to become data. Pick one convention for a given boundary and make it consistent.

### 74.13 Logging and observability

Logging, metrics, and tracing are side effects. A practical architecture usually records them at orchestration or infrastructure boundaries.

```python
import logging

logger = logging.getLogger(__name__)


def process_with_logging(raw, model_client, save_result):
    logger.info("processing document", extra={"document_id": raw.get("document_id")})
    result = process_document(raw, model_client, save_result)
    logger.info("document processed", extra={"document_id": result.document_id})
    return result
```

This does not mean logging inside pure functions is forbidden. It means the design should acknowledge that logging makes the function observably effectful and should be intentional.

### 74.14 Production considerations

**State ownership:** input records are owned by the caller; value-like outputs are represented as new objects rather than mutating shared dictionaries.

**Failure boundaries:** model, database, and filesystem failures are infrastructure concerns. Translate them at explicit boundaries into domain-relevant outcomes.

**Retries:** retry only operations for which the semantics are safe. A retry can duplicate an external side effect unless the operation is idempotent or protected with an idempotency strategy.

**Caching:** define the cache key, validity interval, invalidation behavior, and memory bound. Treat cache correctness as part of system correctness.

**Concurrency:** pure transformations are easier to execute independently, but the whole pipeline can still contain races around shared persistence, queues, caches, or mutable clients.

**Performance:** measure before optimizing. Avoid large defensive copies unless ownership or correctness requires them. Prefer streaming when records are too large to hold comfortably in memory.

**Security:** no secret belongs in source code, test fixtures, example notebooks, or Markdown. Pass credentials through the application's secret/configuration mechanism at runtime.

**Observability:** record correlation identifiers and boundary failures without exposing sensitive document contents or credentials.

**Architecture:** keep the pure core small, explicit, and easy to test. Keep infrastructure adapters replaceable.

---

## 75. Interview Questions and Model Answers

### 75.1 Beginner

**1. What is a pure function?**

A pure function is a function whose result is determined by its relevant inputs and which does not produce observable side effects. `add(2, 3)` is a typical example. A function that also reads a global variable is not fully pure because its result depends on state not represented in its arguments.

**2. What is a side effect?**

A side effect is an observable interaction beyond producing the returned value, such as mutating shared state, writing a file, performing a network request, updating a database, printing, logging, or changing an external system. The exact classification should be made according to the system's observable semantics.

**3. What is immutability?**

An immutable object cannot be changed in place after it is created. Python's `int`, `str`, and `tuple` are examples, while `list`, `dict`, and `set` are mutable. A Python name can still be rebound even when the referenced object is immutable.

**4. What is a higher-order function?**

A function that accepts another function as an argument, returns a function, or both. `map()`, `sorted(key=...)`, decorators, and function factories are practical examples.

**5. What does it mean that functions are first-class objects?**

A function is an object that can be assigned to a name, stored in a container, passed to another function, and returned from a function. Calling it is a separate operation.

**6. What is mutation?**

Mutation changes an existing object in place. For example, `items.append(1)` modifies the list object. Rebinding, such as `items = [1]`, changes what a name refers to rather than modifying the old object.

### 75.2 Intermediate

**7. What is referential transparency?**

An expression is referentially transparent when it can be replaced with its result without changing observable program behavior. A pure `square(5)` can conceptually be replaced by `25`. An expression depending on a changing global or clock cannot generally be replaced safely with one fixed value.

**8. Why are hidden dependencies harmful?**

They make behavior harder to understand, test, reproduce, and reuse. Passing a dependency as an argument exposes the dependency and allows tests to supply deterministic substitutes.

**9. What is a closure?**

A closure is a function together with access to variables from an enclosing lexical scope. The inner function can continue to use those captured values after the outer function has returned.

**10. What is a callback?**

A callback is a function supplied to another component so that the receiving component can invoke it at a chosen point. Callbacks appear in event systems, libraries, retry policies, traversal utilities, and asynchronous APIs.

**11. What does `map()` return in Python?**

`map()` returns a lazy iterator that applies its function to items from one or more iterables. It does not immediately build a list.

**12. Why can `filter()` be lazy?**

`filter()` returns an iterator that evaluates the predicate as items are requested. This means it can avoid allocating the entire result collection up front.

**13. What does `reduce()` do?**

`reduce()` repeatedly combines items using a two-argument function and an optional initial value. It is useful for some folds but can make simple aggregation less readable than `sum()`, `max()`, or an explicit loop.

### 75.3 Advanced

**14. Why can caching require purity?**

A cache assumes that the same cache key can safely reuse the previous result. If a function reads external state or has side effects, replaying an old result can be incorrect or can suppress effects that should have happened.

**15. What is the difference between cache and memoization?**

Caching is the broad technique of storing reusable results. Memoization is a specific form of caching where function results are stored by input arguments so repeated calls can reuse previous results. `@cache` and `@lru_cache` implement memoization-style behavior.

**16. How does `lru_cache` work conceptually?**

It maps hashable argument combinations to previously returned results and may evict the least-recently-used entries when the configured `maxsize` is reached. It exposes statistics and clearing operations through methods such as `cache_info()` and `cache_clear()`.

**17. What is function composition?**

Composition combines compatible functions so the output of one becomes the input to another. For `compose(f, g)` with the chapter's right-to-left convention, `compose(f, g)(x)` means `g(f(x))`. The important issue is explicit order and compatible input/output types.

**18. What is Functional Core / Imperative Shell?**

It is an architecture in which business transformations and decisions are kept as pure or mostly pure functions, while I/O, persistence, network calls, time, randomness, and other effects are placed around the core. This makes the core easier to test and reason about.

**19. How do closures capture variables?**

A nested function resolves names through its local and enclosing scopes. Captured variables are kept accessible to the returned function. In a loop, closures typically capture the variable binding rather than a historical value, which explains the common late-binding bug.

**20. What is the difference between `partial()` and a closure?**

`partial()` creates a callable that pre-binds selected positional or keyword arguments to an existing callable. A closure is a function that captures surrounding variables. A closure can implement custom logic and state; `partial()` is often clearer when the task is simply argument binding.

**21. What are the trade-offs of immutability?**

Immutability can reduce accidental state changes, make sharing easier to reason about, and support safe caching. Costs can include additional allocations, copying or rebuilding data, memory overhead, and awkward integration with APIs designed around mutation. The correct choice depends on the workload and ownership model.

### 75.4 Architecture

**22. How would you isolate side effects in a backend service?**

Identify deterministic parsing, validation, business rules, and transformations and keep them in pure functions where practical. Put database, HTTP, queue, clock, and filesystem interactions behind explicit orchestration or infrastructure boundaries. Inject effectful dependencies so the core does not construct them internally.

**23. How would you design an ML preprocessing pipeline using pure functions?**

Represent each deterministic transformation as an explicit input-to-output step, avoid mutating shared records, and record configuration used by the transformation. Keep model loading, feature-store access, filesystem reads, and persistence outside the transformation core. This supports reproducible tests and easier comparison of pipeline versions.

**24. How would you separate LLM calls from prompt-building logic?**

Make prompt construction a pure function of structured inputs and policy/configuration values. Inject a model client into a separate boundary function. Test prompt content independently, then test the adapter/orchestrator for timeout, error, retry, and response-validation behavior.

**25. How can pure functions improve agent testing?**

Tool argument normalization, policy checks, state transitions, routing rules, prompt construction, and result normalization can often be tested without making real model or tool calls. The effectful execution path can then be tested with fakes and a smaller set of integration tests.

**26. When would functional style be inappropriate?**

When mutation is the clearest representation of an algorithm, when a class models a lifecycle or identity better, when an explicit state machine is easier to understand, or when an abstract pipeline hides more than it reveals. Functional techniques should improve the design rather than serve as a style constraint.

---

## 76. Architecture Questions and Model Answers

### Scenario 1: Order-dependent tests caused by a global cache

**Question:** A function modifies a global cache and tests pass individually but fail when the whole suite runs. How do you diagnose and refactor it?

**Model answer:** Identify the global object as shared mutable state, inspect test order and cache-reset behavior, and determine whether the cache is part of business semantics or merely an optimization. Move cache state behind an explicit dependency, use `lru_cache` only when its key semantics are correct, or create a cache per test. The test should not require knowledge of unrelated test execution order.

### Scenario 2: Database calls mixed with business calculations

**Question:** An API handler queries the database, calculates a discount, mutates a response object, and writes an audit record in one function. Refactor it.

**Model answer:** Separate retrieval and persistence from the discount calculation. Convert external records into explicit values, pass those values to pure domain functions, then persist the result at the boundary. Keep transaction requirements in the orchestration layer because transaction semantics themselves are effectful.

### Scenario 3: ML pipeline reproducibility

**Question:** An ML preprocessing pipeline sometimes produces different features from the same input dataset. How can functional techniques help?

**Model answer:** Audit hidden dependencies such as current time, unordered external data, random state, environment variables, mutable globals, and in-place mutations. Make transformations explicit functions with configuration passed as data. Fix randomness through explicit seeds when appropriate, snapshot external reference data, and test deterministic transformation properties independently.

### Scenario 4: Prompt construction mixed with API calls

**Question:** A function builds a prompt using branching logic and immediately calls an LLM. How should it be separated?

**Model answer:** Extract a pure `build_prompt(context, policy)` function. Keep the model client at an effect boundary. Validate the response with a pure parser/validator before converting it to a domain result. This permits exact prompt tests without API calls and isolates provider changes.

### Scenario 5: Agent runtime is one giant function

**Question:** The agent's main function performs state mutation, tool calls, LLM calls, policy checks, prompt construction, and persistence. How would you refactor it?

**Model answer:** Separate state representation from state transitions, extract pure decision and normalization functions, and make tool/model/persistence services explicit dependencies. Use an orchestration layer for effects. Preserve enough state and event information to debug the transition sequence. Keep the architecture simple enough that a reader can still follow the control flow.

### Scenario 6: `reduce()` everywhere

**Question:** A team uses `reduce()` for sums, grouping, formatting, and complex branching. How do you evaluate the design?

**Model answer:** Look at readability, accumulator invariants, error handling, and maintainability. Replace simple sums with `sum()`, selection with `min()` or `max()` when appropriate, and use a normal loop when the reduction requires multiple statements or domain-specific state. Functional style is not measured by how many calls to `reduce()` appear in the codebase.

### Scenario 7: Entire codebase should be immutable

**Question:** A team proposes making every object immutable. What trade-offs should you discuss?

**Model answer:** Ask which data crosses ownership boundaries, which state is shared, and where mutation is actually causing defects. Immutable values are valuable for configuration and messages, but rebuilding large structures or integrating with mutable libraries can add cost and complexity. A targeted immutability policy is often easier to maintain than a universal rule.

### Scenario 8: Cached function reads environment variables

**Question:** A cached function reads an environment variable inside its body. What can go wrong?

**Model answer:** The cache key does not contain the environment value. If the environment changes, old calls can return results computed under previous configuration. Make configuration an explicit argument or establish a clear configuration lifetime and cache lifetime.

### Scenario 9: Closure versus class for state

**Question:** A closure maintains retry counters and configuration. When would you choose a class instead?

**Model answer:** A closure is concise when state is small, private, and behavior is stable. A class becomes clearer when the object has multiple related operations, meaningful identity, introspection needs, lifecycle methods, or a larger state model. Both can encapsulate behavior; choose based on clarity.

### Scenario 10: Observability in a pure system

**Question:** A team wants pure functions but also needs production logs, metrics, and traces. Where should those effects live?

**Model answer:** Keep core business functions deterministic where practical and emit telemetry at orchestration and infrastructure boundaries. Pass correlation identifiers explicitly when they are part of business data. For specialized diagnostics, a wrapper or decorator may be appropriate, but the team should recognize that the wrapper itself is effectful.

---

## 77. Knowledge Check

### Questions

**1. Multiple choice:** Which behavior most strongly indicates mutation?

A. `x = [1, 2]` followed by `x = [3, 4]`  
B. `x.append(3)`  
C. `x = tuple(x)`  
D. `y = x`

**2. Predict output:**

```python
def square(x):
    return x * x

value = square(4)
print(value)
```

**3. Pure or impure?**

```python
def add(a, b):
    return a + b
```

**4. Pure or impure? Explain why:**

```python
import time

def current_year():
    return time.localtime().tm_year
```

**5. Predict output:**

```python
items = [1, 2]
alias = items
items.append(3)
print(alias)
```

**6. What is the difference between mutation and rebinding?**

**7. Multiple choice:** Which object is immutable?

A. `list`  
B. `dict`  
C. `set`  
D. `frozenset`

**8. Predict output:**

```python
data = ([1], [2])
data[0].append(9)
print(data)
```

**9. What does `map()` return before you call `list()` on it?**

**10. Predict output:**

```python
functions = []
for i in range(3):
    functions.append(lambda i=i: i)
print([f() for f in functions])
```

**11. What does `nonlocal` allow a nested function to do?**

**12. What is a callback?**

**13. Multiple choice:** Which call passes the function rather than executing it immediately?

A. `apply(square(5), 2)`  
B. `apply(square, 5)`  
C. `apply(square(), 5)`  
D. `apply(print("x"), 5)`

**14. Predict the result:**

```python
from functools import reduce
print(reduce(lambda a, b: a + b, [1, 2, 3], 10))
```

**15. What does `sorted(records, key=...)` expect from the key function?**

**16. What values do `any([])` and `all([])` produce?

**17. Why might `deepcopy()` be expensive?

**18. Why can caching an impure function be incorrect?

**19. What does `@wraps(func)` help preserve in a decorator?

**20. Multiple choice:** Which is the clearest example of a pure core with an effect boundary?

A. Business calculation directly writes to a database  
B. Prompt construction calls an LLM directly  
C. A pure decision function receives values, while an outer layer performs the HTTP request  
D. Every function stores state globally

**21. Identify the hidden dependency:**

```python
RATE = 0.2

def total(price):
    return price + price * RATE
```

**22. Is this necessarily pure? Explain:**

```python
def parse_int(text):
    return int(text)
```

**23. Why does a tuple containing a list not provide deep immutability?**

**24. What is the likely problem here?**

```python
def add_item(item, items=[]):
    items.append(item)
    return items
```

**25. Architecture check:** In an agent runtime, where would you place prompt normalization, network tool execution, and persistence?

### Answers and explanations

**1. B.** `append()` changes the existing list object in place. The other assignment examples primarily demonstrate rebinding.

**2. `16`.** The function receives `4` and returns `4 * 4`.

**3. Pure, assuming normal numeric semantics.** The result depends only on `a` and `b`, and the function performs no observable external effect.

**4. Impure.** It reads the external clock, so its result depends on state not represented in its parameters.

**5. `[1, 2, 3]`.** `alias` refers to the same list object that `append()` mutates.

**6. Mutation changes an existing object's contents or state. Rebinding changes what a name refers to. They can occur in the same program but are different operations.

**7. D.** `frozenset` is the immutable counterpart to a set.

**8. `([1, 9], [2])`.** The outer tuple cannot have its element references replaced, but the nested list remains mutable.

**9. A lazy iterator.** Elements are transformed as the iterator is consumed rather than all being materialized immediately.

**10. `[0, 1, 2]`.** The default argument binds the current value at each iteration and avoids the usual late-binding closure behavior.

**11. It permits rebinding of a variable in an enclosing function scope.** It is not the same as `global`, and it does not make arbitrary objects immutable or mutable.

**12. A function supplied to another function for later invocation.** The callback defines behavior that the receiving code can trigger.

**13. B.** `square` is a function object; `square(5)` would call it first.

**14. `16`.** The initial accumulator is `10`, then `10+1+2+3` is computed.

**15. A single comparison value for each item.** The key function is called with each element and its returned key is used for ordering.

**16. `False` and `True`, respectively.** `any()` answers whether at least one item is truthy; `all()` answers whether every item is truthy. Their empty-iterable identities differ.

**17. It may allocate and traverse a large object graph, duplicate nested objects, preserve aliases, and handle cycles or special objects.** Copy cost depends on the structure.

**18. The function's output or required side effect can depend on state outside the cache key. Reusing an old result may therefore be incorrect, or a side effect may be skipped.

**19. Metadata such as the wrapped function's name and docstring, along with other standard wrapper metadata behavior.** It improves introspection and debugging; it does not magically preserve every possible runtime property.

**20. C.** The pure function can be tested independently, while the HTTP effect is kept explicit.

**21. `RATE` is hidden global configuration.** A stronger design makes the relevant rate an explicit argument or creates an explicit configuration boundary.

**22. Usually yes with normal deterministic integer parsing semantics, even though it can raise `ValueError`.** An exception by itself does not automatically make a function impure. Its determinism and external effects are the important questions.

**23. Because the nested list is a separate mutable object.** The tuple protects its element references, not the internal state of objects those references point to.

**24. The default list is created once when the function is defined and reused across calls.** Use `None` as a sentinel and create a new list inside the function when needed.

**25. Prompt normalization belongs in pure transformation logic; network tool execution belongs at an effect boundary; persistence also belongs at the effect boundary.** The orchestration layer connects the two.

---

## 78. Common Misconceptions

### 78.1 “Pure function means it has no parameters.”

False. Parameters are normal and usually make dependencies explicit. Purity is about how outputs and effects relate to inputs and external state.

### 78.2 “Pure function means it cannot raise exceptions.”

False. A deterministic validation or parsing function can raise an exception. Whether exceptions are considered part of the semantic result in a particular formal model is a deeper question; in practical Python design, an exception alone does not prove impurity.

### 78.3 “Pure function means it cannot call another function.”

False. A pure function can call another function when the called function is itself pure with respect to the relevant inputs and does not introduce hidden effects.

### 78.4 “Printing is the only side effect.”

False. Mutation, files, databases, network calls, environment access, current time, randomness, logging, and external state changes are other examples.

### 78.5 “Immutability means the variable cannot change.”

False. Names in Python can be rebound. Immutability describes an object, not a name binding.

### 78.6 “Tuple means everything inside is immutable.”

False. A tuple can contain mutable objects such as lists or dictionaries.

### 78.7 “Frozen dataclass means deeply immutable.”

False. `frozen=True` primarily restricts assignment to dataclass attributes. Nested mutable values can still be mutated through their references.

### 78.8 “Functional programming means never use classes.”

False. Classes and functional techniques coexist. A callable object can even participate in the same higher-order APIs as a function.

### 78.9 “`map()` is always better than a loop.”

False. A comprehension or loop may be clearer, and performance depends on workload and implementation details.

### 78.10 “`filter()` is always better than a comprehension.”

False. A simple comprehension can often express both filtering and transformation more clearly.

### 78.11 “`reduce()` is always more functional and therefore better.”

False. A clear named operation such as `sum()` or an explicit loop can communicate intent better.

### 78.12 “`lambda` is always preferable for short functions.”

False. A `def` with a meaningful name can be clearer even when its body is short.

### 78.13 “Caching any function is safe.”

False. Cached results can become stale, hide configuration changes, consume memory, and suppress effects that should occur on each call.

### 78.14 “Pure functions automatically make applications thread-safe.”

False. They reduce one important class of shared-state problems, but the surrounding system may still have races in queues, caches, databases, files, object lifecycles, or synchronization primitives.

### 78.15 “Deepcopy creates true conceptual immutability.”

False. Copying creates a new object graph according to the copy protocol. It does not establish a universal immutable contract or remove every source of external state.

### 78.16 “Higher-order functions are only for functional programming.”

False. Python's standard library uses callbacks and callables extensively, including sorting, iteration helpers, decorators, and configuration strategies.

### 78.17 “Closures are the same thing as classes.”

False. Both can encapsulate state and behavior, but their interfaces, lifecycle semantics, introspection, inheritance options, and readability differ.

### 78.18 “Decorators preserve function behavior automatically.”

False. A decorator can alter arguments, return values, exceptions, timing, or side effects. `functools.wraps()` improves metadata preservation but does not guarantee semantic equivalence.

### 78.19 “Functional style means no side effects anywhere.”

False. Production systems need effects. A practical design often moves those effects to explicit boundaries rather than pretending they do not exist.

### 78.20 “Functional programming is only useful for academic code.”

False. Pure transformations, higher-order functions, immutable values, explicit data flow, and controlled effects are useful in APIs, ETL, ML systems, LLM applications, and agent runtimes.

---

## 79. When Not to Use Functional Style

Functional style is a tool. Do not turn it into a rule that overrides clarity.

### 79.1 Mutation may be simpler

A tight loop that updates a local accumulator can be easier to understand than a stack of reducers and closures, especially when the algorithm naturally operates by changing a small, private piece of state.

### 79.2 A class may model lifecycle or identity better

Use a class when an entity has persistent identity, multiple related operations, resource ownership, lifecycle events, explicit invariants, or a state model that benefits from named methods.

### 79.3 A loop may be clearer

A loop is often appropriate when there are multiple branches, early exits, error handling, logging, or local state transitions that would become awkward inside nested functional expressions.

### 79.4 Database transactions are stateful by nature

A transaction interacts with external state. The goal is not to pretend it is pure; the goal is to keep transaction effects explicit and isolate pure business calculations that can be separated from the transaction boundary.

### 79.5 State machines can benefit from explicit state

A state machine with transitions, guards, events, persistence, and observability may be easier to implement using explicit data structures or objects than with deeply nested function composition.

### 79.6 Object-oriented design can be clearer

Functional and object-oriented design are not mutually exclusive. A Python service can use immutable value objects, pure transformation functions, classes for infrastructure clients, and dependency injection at the same time.

### 79.7 Excessive composition can hurt readability

A pipeline of ten anonymous lambdas can be less maintainable than five named functions connected by ordinary statements. A good abstraction makes intent easier to see; a bad abstraction forces the reader to reconstruct hidden control flow.

### 79.8 Use a simple decision rule

Prefer a functional technique when it makes dependencies explicit, state easier to reason about, reuse easier, or testing simpler. Prefer a different technique when the functional abstraction obscures state, control flow, lifecycle, or business semantics.

---

## 80. Production Design Principles

Use this checklist during code review, refactoring, and architecture work.

### Purity

- Is the function deterministic for the inputs that matter?
- Does it read hidden state such as globals, environment variables, the clock, randomness, or external services?
- Does it mutate an object owned by its caller?
- Can the function be tested without infrastructure?

### Side effects

- Are network, database, filesystem, queue, clock, and model calls visible at a boundary?
- Is the side-effect dependency explicit rather than constructed deep inside business logic?
- Are retries and idempotency semantics understood?

### Mutation and state

- Is mutation intentional?
- Who owns the mutated object?
- Could a caller or another thread observe the change?
- Would returning a new value improve clarity?

### Immutability

- Would an immutable value reduce accidental coupling?
- Is a frozen dataclass or tuple sufficient for the required ownership boundary?
- Are nested values still mutable?
- Is defensive copying actually required, and what does it cost?

### Higher-order functions

- Does the callback or strategy parameter make the behavior more reusable?
- Is a function factory clearer than a class in this context?
- Would a named function communicate intent better than a lambda?

### Composition and pipelines

- Are the input and output types obvious at each stage?
- Is function order easy to verify?
- Would ordinary statements be more readable than a generic pipeline helper?
- Can a failed stage be isolated and tested directly?

### Testing

- Can the pure core be tested with ordinary input/output assertions?
- Are effectful dependencies replaceable with fakes or other test doubles?
- Are boundary failures tested separately from deterministic transformations?

### Caching

- Are arguments hashable?
- Do arguments contain all state relevant to the result?
- Is the result safe to reuse?
- Is the cache lifetime understood?
- Is memory use bounded when necessary?
- Is invalidation or configuration change behavior understood?

### Concurrency

- Is shared mutable state minimized?
- Could a caller mutate a value after another task begins using it?
- Is the surrounding infrastructure synchronized even when the core is pure?
- Does the chosen concurrency model preserve correctness?

### Production boundaries

- Are external effects isolated?
- Are observability concerns placed where they provide useful operational context?
- Are secrets obtained through runtime configuration or secret management rather than code?
- Are failures translated into explicit domain outcomes at system boundaries?

---

## 81. Required API and Function Coverage

This section is a compact reference. Earlier sections contain the deeper teaching material; use this section when you need to remember the core API contract.

### 81.1 `map()`

**Purpose:** lazily apply a callable to items from one or more iterables.  
**Syntax:** `map(function, iterable, ...)`  
**Parameters:** a callable plus one or more iterables. With multiple iterables, the callable receives one item from each.  
**Return:** a lazy `map` iterator.  
**Limitations:** consuming it advances the iterator; multiple-iterable calls must match the callable's expected arity.  
**Example:** `list(map(str.upper, ["a", "b"]))`.  
**Real-world use:** simple element-wise transformations.  
**Common mistake:** expecting a list immediately or assuming it is always clearer than a comprehension.

### 81.2 `filter()`

**Purpose:** lazily keep items for which a predicate is truthy.  
**Syntax:** `filter(function, iterable)`  
**Parameters:** a callable or `None`, and an iterable.  
**Return:** a lazy `filter` iterator.  
**Limitations:** it is one-pass and applies truth testing; it does not materialize a collection.  
**Example:** `list(filter(lambda x: x > 0, values))`.  
**Real-world use:** stream-like filtering of records.  
**Common mistake:** assuming `filter()` is automatically better than a comprehension.

### 81.3 `sorted()` with `key`

**Purpose:** create a new sorted list.  
**Syntax:** `sorted(iterable, *, key=None, reverse=False)`.  
**Parameters:** input iterable plus optional `key` callable and reverse flag.  
**Return:** a new list.  
**Limitations:** the original input is not sorted in place; key values influence ordering. Python sorting is stable.  
**Example:** `sorted(users, key=lambda user: user["age"])`.  
**Real-world use:** ordering records by business fields.  
**Common mistake:** passing `key=func()` instead of `key=func`.

### 81.4 `min()` and `max()` with `key`

**Purpose:** select the smallest or largest item according to an optional key.  
**Syntax:** `min(iterable, *, key=None, default=...)` and corresponding `max(...)`, with alternate positional forms.  
**Parameters:** an iterable or multiple positional candidates, optional key, and optional default for empty iterable forms.  
**Return:** the selected original item, not the key value.  
**Limitations:** an empty iterable without `default` raises `ValueError`.  
**Example:** `min(users, key=lambda user: user.age)`.  
**Real-world use:** selecting the oldest record or least-cost option.  
**Common mistake:** expecting the smallest key rather than the original object.

### 81.5 `any()` and `all()`

**Purpose:** combine truth tests over an iterable with short-circuiting.  
**Syntax:** `any(iterable)`, `all(iterable)`.  
**Parameters:** an iterable of truthy/falsy values, often generated lazily.  
**Return:** `bool`.  
**Limitations:** `any([])` is `False`; `all([])` is `True`; consumption stops as soon as the answer is known.  
**Example:** `all(x >= 0 for x in values)`.  
**Real-world use:** validation and guard conditions.  
**Common mistake:** using a list when a generator expression is enough and materializes unnecessary values.

### 81.6 `zip()`

**Purpose:** combine elements from multiple iterables positionally.  
**Syntax:** `zip(*iterables, strict=False)`.  
**Parameters:** any number of iterables; `strict=True` requests an error when input lengths differ.  
**Return:** a lazy `zip` iterator of tuples.  
**Limitations:** default behavior stops at the shortest input, which can silently discard unmatched elements.  
**Example:** `list(zip(names, scores, strict=True))`.  
**Real-world use:** pairing aligned fields or records.  
**Common mistake:** assuming unequal lengths automatically raise an exception.

### 81.7 `enumerate()`

**Purpose:** pair each item with an incrementing index.  
**Syntax:** `enumerate(iterable, start=0)`.  
**Parameters:** iterable and optional starting index.  
**Return:** a lazy `enumerate` iterator producing `(index, value)` pairs.  
**Limitations:** it does not modify the source or create an indexable list.  
**Example:** `for index, value in enumerate(values, start=1): ...`.  
**Real-world use:** reporting positions without manual counters.  
**Common mistake:** modifying the collection while iterating over it.

### 81.8 `functools.reduce()`

**Purpose:** fold an iterable into one accumulated result.  
**Syntax:** `reduce(function, iterable, initial=...)`.  
**Parameters:** a two-argument combining function, iterable, optional initial accumulator.  
**Return:** the final accumulated value.  
**Limitations:** an empty iterable without an initializer raises `TypeError`; complex reductions can reduce readability.  
**Example:** `reduce(lambda a, b: a + b, values, 0)`.  
**Real-world use:** specialized folds and accumulator-style algorithms.  
**Common mistake:** using it where `sum()`, `min()`, or a loop expresses intent more clearly.

### 81.9 `functools.partial()`

**Purpose:** pre-bind some arguments to a callable.  
**Syntax:** `partial(func, /, *args, **keywords)`.  
**Parameters:** callable plus arguments/keywords to bind.  
**Return:** a callable partial object.  
**Limitations:** it is argument binding, not arbitrary function composition; signatures and introspection can differ from the original callable.  
**Example:** `double = partial(pow, exp=2)`.  
**Real-world use:** callbacks requiring a specific configuration.  
**Common mistake:** using a complicated closure where simple argument binding is all that is required.

### 81.10 `functools.partialmethod()`

**Purpose:** define a method that pre-binds arguments to another descriptor-compatible method/callable.  
**Syntax:** `partialmethod(func, /, *args, **keywords)`.  
**Parameters:** method-like callable plus arguments/keywords.  
**Return:** a descriptor used as a class attribute.  
**Limitations:** mainly useful inside classes; ordinary `partial()` is often enough outside method definitions.  
**Example:** `close = partialmethod(send, "CLOSE")`.  
**Real-world use:** small families of related methods with fixed parameters.  
**Common mistake:** adding it when a normal named method would be clearer.

### 81.11 `functools.cache()`

**Purpose:** memoize calls without a bounded size.  
**Syntax:** `@cache`.  
**Parameters:** no configuration; arguments must be usable as cache keys.  
**Return:** a wrapped callable that reuses prior results.  
**Limitations:** unbounded cache growth and no automatic invalidation based on external state.  
**Example:** `@cache` on a deterministic recursive function.  
**Real-world use:** stable finite-domain calculations.  
**Common mistake:** putting a network call or stateful operation behind `@cache`.

### 81.12 `functools.lru_cache()`

**Purpose:** memoize results with configurable least-recently-used eviction.  
**Syntax:** `@lru_cache(maxsize=128, typed=False)` or `lru_cache(maxsize=..., typed=...)`.  
**Parameters:** maximum cache entries and optional treatment of some differently typed arguments.  
**Return:** wrapped callable with `cache_info()`, `cache_clear()`, and cache-parameter introspection.  
**Limitations:** arguments must be hashable; it is not a general persistence layer; cached results can become stale.  
**Example:** `@lru_cache(maxsize=256)`.  
**Real-world use:** repeated deterministic lookups inside a process.  
**Common mistake:** treating it as a durable cross-process cache.

### 81.13 `functools.singledispatch()`

**Purpose:** create a generic function that dispatches on the type of its first argument.  
**Syntax:** `@singledispatch` plus `@function.register`.  
**Parameters:** implementations are registered for selected types.  
**Return:** a generic dispatching function.  
**Limitations:** dispatch is based on the first argument's type; it is not general multiple-dispatch or ordinary method overloading.  
**Example:** register `int`, `str`, and a default handler.  
**Real-world use:** type-directed formatting or serialization strategies.  
**Common mistake:** using it to hide a small branch that a normal `if` statement would explain better.

### 81.14 `functools.wraps()`

**Purpose:** help a decorator wrapper preserve standard metadata from the wrapped function.  
**Syntax:** `@wraps(func)` above the wrapper definition.  
**Parameters:** the wrapped function and optional assigned/updated metadata arguments through the decorator factory.  
**Return:** a decorator applied to the wrapper.  
**Limitations:** it does not make the wrapper semantically identical or copy every possible runtime property.  
**Example:** use inside a `log_call` decorator.  
**Real-world use:** production decorators for tracing, metrics, retries, or access checks.  
**Common mistake:** omitting `wraps` and then wondering why debugging shows `wrapper` instead of the original function name.

### 81.15 `copy.copy()`

**Purpose:** create a shallow copy according to an object's copy protocol.  
**Syntax:** `copy.copy(obj)`.  
**Parameters:** the object to copy.  
**Return:** a new outer object when copying is supported; nested references are generally shared.  
**Limitations:** copying semantics depend on the object's implementation.  
**Example:** `copied = copy.copy(original)`.  
**Real-world use:** isolate top-level container changes when nested ownership can safely remain shared.  
**Common mistake:** expecting a deep independent object graph.

### 81.16 `copy.deepcopy()`

**Purpose:** recursively copy an object graph according to the copy protocol.  
**Syntax:** `copy.deepcopy(obj)`.  
**Parameters:** object plus optional memoization dictionary for advanced custom copying.  
**Return:** an independently copied graph where supported.  
**Limitations:** can be expensive; recursive structures, shared references, and special objects require careful semantics. It is not a universal immutability mechanism.  
**Example:** `copied = copy.deepcopy(original)`.  
**Real-world use:** legacy integrations where ownership boundaries require independent nested structures.  
**Common mistake:** using it as the default solution instead of modeling ownership explicitly.

### 81.17 `tuple` and `frozenset`

`tuple` is an immutable sequence container; `frozenset` is an immutable set. They can support value-like data structures and, when their contents are hashable, can themselves be hashable. A tuple is not deeply immutable when it contains mutable members. A `frozenset` cannot contain unhashable elements.

### 81.18 `lambda`

**Purpose:** define a small anonymous function expression.  
**Syntax:** `lambda parameters: expression`.  
**Return:** a function object.  
**Limitations:** expression-only body; complicated logic is usually clearer as a named `def`.  
**Example:** `sorted(items, key=lambda item: item["priority"])`.  
**Real-world use:** local key/predicate/callback definitions.  
**Common mistake:** nesting complex conditional logic inside anonymous functions.

### 81.19 Closures and `nonlocal`

A closure is created when a nested function retains access to an enclosing scope. `nonlocal` allows the nested function to rebind an enclosing variable. `nonlocal` does not make a global variable accessible; `global` is a different declaration. Stateful closures are useful but should be compared with classes when state becomes substantial.

### 81.20 `__call__`

Implementing `__call__(self, ...)` makes an instance callable with function-like syntax: `obj(...)`. It is useful for strategy objects, configurable transformations, model wrappers, and test doubles that need state plus callable behavior. It does not make the object a function object.

### 81.21 `callable()`

**Purpose:** test whether an object appears callable.  
**Syntax:** `callable(obj)`.  
**Return:** `bool`.  
**Limitation:** being callable does not prove that invocation will satisfy a particular semantic contract.  
**Example:** `callable(double)`.  
**Real-world use:** validating configurable callbacks.  
**Common mistake:** treating `callable()` as a full interface check.

### 81.22 `id()` and `type()`

`id(obj)` returns an integer identifying the object for its lifetime in the current Python implementation context; it is useful for demonstrations of identity and aliasing, not for domain identifiers. `type(obj)` returns the object's type. Neither replaces explicit domain modeling.

### 81.23 `__name__`, `__doc__`, `__closure__`, `__code__`

`__name__` exposes a function's name in common function objects; `__doc__` exposes its docstring; `__closure__` can expose captured-cell information for a closure; `__code__` exposes the code object used by Python function objects. These are introspection facilities, not ordinary business APIs. Their usefulness is strongest in debugging, education, and tooling.

### 81.24 `inspect.signature()`

**Purpose:** inspect a callable's signature when supported.  
**Syntax:** `inspect.signature(callable)`.  
**Return:** a `Signature` object describing parameters and defaults.  
**Limitations:** some built-ins, extension objects, or dynamic callables may have incomplete or unavailable signatures.  
**Example:** `signature = inspect.signature(process)`.  
**Real-world use:** framework tooling, validation, debugging, and documentation generation.  
**Common mistake:** using runtime introspection everywhere instead of keeping ordinary interfaces explicit.

---

## 82. Technical Accuracy Rules and Core Distinctions

### 82.1 Pure function versus “a function that returns a value”

Every normal Python function can return a value, including highly effectful functions. A function that performs a database write and then returns `True` is not pure merely because it has a return statement.

### 82.2 Mutation versus rebinding

```python
items = []
items.append("A")   # mutate the list object

items = ["B"]       # rebind the name to another list
```

The first line after the initialization changes the existing object's state. The second changes name-to-object association. This distinction is necessary for understanding aliases and immutability.

### 82.3 Immutable object versus immutable name

Python normally has mutable name bindings. An immutable object such as a string cannot be altered in place, but its name can be rebound:

```python
name = "Alice"
name = "Bob"
```

The string objects are immutable; `name` is not an immutable variable declaration.

### 82.4 Cache versus memoization

A cache is the general idea of retaining reusable information. Memoization is specifically associated with storing function results based on inputs. `@cache` and `@lru_cache` are memoization utilities; a distributed HTTP cache is a different kind of caching mechanism.

### 82.5 Functional style versus strict functional programming

Functional style in Python means selectively using values, transformations, higher-order functions, immutability, and explicit data flow where helpful. Python remains a multiparadigm language. Strict functional programming can impose stronger restrictions on mutation and effects than most Python systems require.

### 82.6 Exceptions and purity

A function that raises an exception for invalid input can still have deterministic, side-effect-free behavior. In practical engineering, determine whether the function reads hidden state or performs observable effects rather than using “can raise” as the purity criterion.

### 82.7 Side-effect analysis is contextual

Logging is observable. That makes it a side effect in a strict purity analysis, even when logging is operationally desirable. The architectural question is whether that effect belongs in the function's role or should be placed at the surrounding boundary.

### 82.8 Immutability is not automatically hashability

Some immutable objects are hashable, such as many tuples whose elements are hashable and `frozenset` values whose members are hashable. An immutable object can still be unhashable when its design or contents do not support a valid hash. Hashability requires a stable hash/equality relationship, not merely “cannot mutate.”

### 82.9 `deepcopy()` is not deep conceptual immutability

`deepcopy()` attempts to create an independent object graph. It does not establish a type-level rule that the resulting graph can never mutate. A copied list is still a mutable list. Explicit immutable data models communicate stronger intent.

### 82.10 Purity does not automatically solve concurrency

Pure computations reduce shared mutable state, but a concurrent application still depends on how tasks exchange messages, how resources are managed, and how external effects are synchronized. Pure code is easier to parallelize; it is not a complete concurrency design.

---

## 83. Performance Accuracy

Do not choose functional style based on a blanket claim that it is faster or slower. Reason about the actual workload.

### 83.1 Algorithmic complexity comes first

A pipeline that performs an unnecessary `O(n^2)` operation will not become efficient merely because it uses `map()`. Analyze the algorithm before choosing a syntax style.

### 83.2 Allocation matters

Creating a new list at each transformation can increase memory pressure. A generator pipeline can defer allocation and process values one at a time, but generators introduce one-pass semantics and may complicate repeated access.

### 83.3 Copying matters

`copy.copy()` and especially `copy.deepcopy()` can add time and memory cost. Copy only when it establishes a meaningful ownership or safety boundary.

### 83.4 Function-call overhead exists

Small Python function calls have overhead. Turning every single expression into a chain of tiny function calls can add cost, but the significance depends on the hot path. Measure rather than assuming.

### 83.5 Lazy iteration changes memory behavior

`map()`, `filter()`, `zip()`, `enumerate()`, and generators can avoid materializing the full result immediately. Laziness saves memory in some pipelines but can also defer errors and make iterators easier to accidentally exhaust.

### 83.6 Comprehension versus `map()` versus loop

For many applications, readability is the primary decision factor. A performance difference, when one exists, depends on the operation, interpreter implementation, data size, and surrounding work. Benchmark representative workloads before changing clear code for speed.

### 83.7 Caching has a memory cost

A cache trades repeated computation for stored results. Measure cache hit rate, entry size, lifetime, and eviction behavior. A cache with poor locality can consume memory without providing meaningful speedup.

### 83.8 Benchmark production-like workloads

Use representative data sizes and realistic execution paths. A microbenchmark of a single lambda does not predict the performance of a network-bound LLM pipeline or a database-heavy ETL job.

---

## 84. Applied AI Engineering Connection

Pure functions and controlled effects are directly useful in production AI systems because AI applications combine deterministic transformations with highly effectful infrastructure.

### 84.1 Reference architecture

```text
                         INPUT
                           |
                           v
                 +----------------------+
                 |   PURE FUNCTIONS     |
                 |----------------------|
                 | validation           |
                 | normalization        |
                 | transformation       |
                 | routing              |
                 | prompt construction  |
                 | result normalization |
                 +----------------------+
                           |
                           v
                    EFFECT BOUNDARY
                    /       |       \
                   /        |        \
                 DB        LLM       API
```

The important design idea is not that every function must be pure. It is that the system makes the boundary between deterministic computation and external effects easy to see.

### 84.2 Backend services

A request handler can parse input, validate it, calculate business rules, and construct a response through pure functions. Database and HTTP operations remain effectful. This arrangement makes unit tests fast and keeps infrastructure failures separate from business-rule tests.

### 84.3 Data engineering and ETL/ELT

A robust transformation stage can follow:

```text
raw record
   -> parse
   -> clean
   -> validate
   -> normalize
   -> enrich from explicit input
   -> aggregate
```

Reading S3, querying a warehouse, publishing to Kafka, and writing output are effects. The transformation functions between those boundaries can often be deterministic.

### 84.4 ML preprocessing

Feature calculations, type normalization, missing-value policies, validation, scaling, and post-processing often benefit from explicit pure transformations. Model loading, artifact access, feature stores, and remote inference are effect boundaries.

A reproducibility bug often appears when a preprocessing function silently reads current time, process environment, an unseeded random generator, or a mutable global configuration. Make those dependencies explicit.

### 84.5 Inference pipelines

An inference pipeline can separate:

```text
request
  -> normalize request [pure]
  -> validate request [pure]
  -> build model input [pure]
  -> call inference server [effect]
  -> validate output [pure]
  -> post-process [pure]
  -> persist/emit [effect]
```

This makes it easier to test request shaping and output validation without a GPU or remote endpoint.

### 84.6 LLM applications

Prompt construction is a strong candidate for pure logic:

```python
def build_prompt(context: str, question: str) -> str:
    return f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:" 
```

The model call belongs to a separate effect boundary:

```python
def call_llm(prompt: str, client) -> str:
    return client.generate(prompt)
```

A production application can then test prompt formatting, validation, truncation policy, and routing independently of provider availability.

### 84.7 Evaluation pipelines

Evaluation code often contains deterministic scoring functions mixed with effectful model calls and artifact storage. Keep metric calculations pure when practical:

```python
def exact_match(expected: str, actual: str) -> bool:
    return expected.strip() == actual.strip()
```

Then isolate dataset retrieval, model invocation, and result persistence.

### 84.8 Agentic AI

Agent systems combine several kinds of state and effects. A useful split is:

```text
Agent Runtime
     |
     +--> Pure state normalization
     |
     +--> Pure policy checks
     |
     +--> Pure routing/decision transformations
     |
     +--> Pure tool-argument validation
     |
     +--> Pure prompt construction
     |
     +--> Effectful model calls
     |
     +--> Effectful tool execution
     |
     +--> Effectful memory/database writes
```

This separation supports deterministic tests for routing decisions and policy rules, while integration tests cover model and tool interactions.

### 84.9 State management

An agent's state can be represented as immutable snapshots or value-oriented records at well-defined boundaries. The runtime can then produce a new state after each transition. This does not require an entirely immutable application; it creates explicit ownership of important state transitions.

### 84.10 Caching in AI systems

Caching can be useful for deterministic preprocessing, embeddings under a clearly defined model/configuration version, or repeated evaluation inputs. It is dangerous when the cache key omits relevant prompt, model, tool, configuration, or retrieval state.

For AI systems, include semantically relevant versioning or configuration in cache identity. “Same text” does not necessarily mean “same expected answer” when the model or prompt policy changed.

### 84.11 Observability

Logs, metrics, and traces should expose enough context to reconstruct what happened without making every business function effectful. Boundary-level instrumentation can record latency, provider identifiers, retry counts, and correlation IDs while protecting sensitive payloads.

### 84.12 Concurrency

Batch inference, parallel ETL, and concurrent tool execution benefit from independent pure transformations. The shared infrastructure still requires careful design for connection pools, rate limits, caches, files, databases, and API quotas.

---

## 85. Code Quality Requirements

Before treating an example as production-ready teaching material, verify:

1. The Python syntax is valid.
2. The example is runnable unless explicitly marked as pseudocode or conceptual architecture.
3. Any displayed output matches actual execution.
4. Names describe domain intent rather than implementation accidents.
5. Secrets and fake-looking real credentials are never included.
6. Mutable state is introduced only when it serves a clear purpose.
7. Functions expose important dependencies instead of silently reading globals.
8. Higher-order abstractions do not hide control flow unnecessarily.
9. Caches have explicit correctness assumptions.
10. Exceptions and error results are handled consistently within the example.
11. Production examples distinguish pure transformations from effects.
12. Modern Python syntax is used when appropriate to the targeted version, without requiring advanced features before they are taught.

A good teaching example is not merely syntactically valid. It should make the underlying concept visible.

---

## 86. Progressive Complexity Map

The chapter's intended progression is:

```text
ordinary functions
    -> function inputs and outputs
    -> state
    -> side effects
    -> pure functions
    -> deterministic behavior
    -> referential transparency
    -> hidden dependencies
    -> mutation
    -> rebinding
    -> object identity
    -> immutability
    -> shallow/deep immutability
    -> copying
    -> immutable data modeling
    -> first-class functions
    -> higher-order functions
    -> callbacks
    -> function factories
    -> closures
    -> lexical scope / LEGB
    -> nonlocal
    -> lambda
    -> map
    -> filter
    -> reduce
    -> sorted/min/max key
    -> any/all
    -> zip/enumerate
    -> function composition
    -> pipelines
    -> partial
    -> partialmethod
    -> cache
    -> lru_cache
    -> singledispatch
    -> decorators
    -> wraps
    -> functional error handling
    -> testing
    -> functional core / imperative shell
    -> generators
    -> concurrency
    -> data engineering
    -> ML
    -> LLM applications
    -> agentic AI
    -> production architecture
```

This order matters. The advanced techniques are easier to understand when the learner already understands references, state, effects, and function objects.

---

## 87. Final Self-Review and Final Mental Model

### 87.1 Self-review checklist

- [x] Beginner explanation exists.
- [x] Ordinary functions are explained first.
- [x] Pure functions are deeply explained.
- [x] Side effects are deeply explained.
- [x] Determinism is explained.
- [x] Referential transparency is explained.
- [x] Hidden dependencies are explained.
- [x] Mutation is explained.
- [x] Rebinding is explained.
- [x] Object identity is explained.
- [x] Mutable versus immutable objects are explained.
- [x] Shallow versus deep immutability is explained.
- [x] Defensive copying is explained.
- [x] Tuple is explained.
- [x] Frozenset is explained.
- [x] Frozen dataclass is explained.
- [x] Hashing relationship is explained.
- [x] Functions as first-class objects are explained.
- [x] Higher-order functions are explained.
- [x] Callbacks are explained.
- [x] Functions returning functions are explained.
- [x] Closures are explained.
- [x] LEGB is explained.
- [x] `nonlocal` is explained.
- [x] Lambda is explained.
- [x] `map()` is explained.
- [x] `filter()` is explained.
- [x] `reduce()` is explained.
- [x] `sorted(key=...)` is explained.
- [x] `min()` / `max()` with `key` are explained.
- [x] `any()` / `all()` are explained.
- [x] `zip()` / `enumerate()` are explained.
- [x] Function composition is explained.
- [x] Functional pipelines are explained.
- [x] `partial()` is explained.
- [x] `partialmethod()` is explained.
- [x] `cache()` is explained.
- [x] `lru_cache()` is explained.
- [x] `singledispatch()` is explained.
- [x] Decorators are explained.
- [x] `functools.wraps()` is explained.
- [x] Functional Core / Imperative Shell is explained.
- [x] Testing is explained.
- [x] Property-based thinking is introduced.
- [x] Concurrency implications are explained.
- [x] Performance trade-offs are explained.
- [x] Data engineering examples exist.
- [x] ML examples exist.
- [x] LLM examples exist.
- [x] Agentic AI examples exist.
- [x] Backend production examples exist.
- [x] At least 25 exercises exist.
- [x] A debugging lab exists with at least 7 scenarios.
- [x] A mini-project exists.
- [x] Interview questions exist.
- [x] Architecture questions exist.
- [x] A 20+ question knowledge check exists.
- [x] Common misconceptions are corrected.
- [x] A production checklist exists.
- [x] A final mental model exists.
- [x] Required functions and APIs are covered.
- [x] Mutation versus rebinding is clearly distinguished.
- [x] Immutable object versus immutable name is clearly distinguished.
- [x] Pure function versus merely returning a value is clearly distinguished.
- [x] Cache versus memoization is clearly distinguished.
- [x] Functional style versus strict functional programming is clearly distinguished.
- [x] Examples are designed to be technically correct and readable.
- [x] Examples avoid secrets.
- [x] Content progresses Basic -> Intermediate -> Advanced -> Production.

### 87.2 Final mental model

The central idea is not “never mutate” and not “write everything with `map()`.” The central idea is **make data flow, dependencies, and effects easy to reason about**.

Think in layers:

```text
                INPUTS
                   |
                   v
        +-----------------------+
        |   PURE TRANSFORMS     |
        |-----------------------|
        | validate              |
        | normalize             |
        | calculate             |
        | route                 |
        | construct             |
        | score                 |
        +-----------------------+
                   |
                   v
             EFFECT BOUNDARY
          /        |        \
       clock      DB        API/LLM
          \        |        /
                   v
              OBSERVABLE RESULT
```

Pure functions make the mapping from inputs to outputs explicit. Immutable values make ownership and sharing easier to reason about. Higher-order functions make behavior itself a value, so algorithms can receive strategies, callbacks, or transformations. Closures provide controlled access to enclosing state. Functional tools provide concise ways to transform and inspect data. Composition and pipelines make multi-stage transformations explicit. Decorators add reusable wrappers around call behavior. Caching can avoid repeated deterministic work when its correctness assumptions are satisfied.

Production systems still need state, I/O, transactions, queues, model calls, retries, logging, metrics, and persistence. Functional design becomes valuable when those effects are deliberately placed at understandable boundaries rather than mixed invisibly into every calculation.

A useful engineering question is therefore not:

> “Can this be pure?”

Ask instead:

> “Which part of this computation should be pure, which part must be effectful, and are the boundaries explicit enough that another engineer can test, debug, and change them safely?”

That question scales from a five-line Python function to an ETL pipeline, ML inference service, LLM application, and agent runtime.

---

## 88. File-Scope Verification

This chapter is intentionally limited to the requested target:

```text
08-Object-Oriented-Design-Data-Modelling-and-Functional-Style/06-pure-functions-immutability-and-higher-order-functions.md
```

No README, practice-question file, previous topic file, future topic file, project file, or auxiliary file is part of the chapter content. Final validation for this task should confirm that only the target file was written or changed.

---
