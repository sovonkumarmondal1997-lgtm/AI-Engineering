# Roadmap — Module 1.24: Functions and OOP Gap Lessons

This is the learning roadmap for the twenty-fourth module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn,
**in what order**, **how** to practise each topic, and **how to prove to
yourself** that you have learned it.

This module exists because a careful audit of the Stage 1 curriculum found
specific gaps in two core topics:

- **Functions** — Modules 1.3 (parameters, defaults, scope, purity), 1.4
  (recursion), 1.8 (higher-order functions), 1.9 (generators, decorators,
  `functools`, typing) already cover most of the topic, but there was **no
  dedicated lesson** on first-class functions, lambdas, closures and
  `nonlocal`, `map`/`filter`/`reduce` and key functions, or callable objects.
- **Object-oriented programming** — Modules 1.8 and 1.9 cover design-level
  OOP (encapsulation, composition, inheritance, dataclasses, protocols), but
  nothing covered **classes from first principles**, the object
  **construction** protocol (`__init__` vs `__new__`), or cooperative use of
  `super()` in inheritance. Advanced topics (MRO internals, descriptors,
  slots, ABCs, metaclasses) live in Modules 1.11 and 1.12 and are **not
  repeated here**.

So this module is deliberately compact: it **fills the holes** and then
gives you two **review checklists** (functions, classes) that tie Stage 1
together.

> **Where to take this module.** Lessons 01–07 (functions) are best taken
> right after Module 1.9; lessons 08–10 (classes, construction, `super()`)
> are best taken **before** Modules 1.11–1.12, which assume them. Lessons 07
> and 11 (design review checklists) fit well at the end of Stage 1. If you
> prefer to follow numeric order, read lessons 01–10 before starting 1.11.

> Target: **Python 3.12+**.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain that functions are objects and use them as values: pass, return, store, inspect, and call dynamically.
- Write and read `lambda` expressions, and decide when a named function is better.
- Explain **closures**, free variables and cells; use `nonlocal`; diagnose the **late-binding** loop pitfall.
- Use `map`, `filter`, `reduce`, `sorted(key=)`, `min/max(key=)`, comprehensions and `operator` helpers fluently — and know when each is the clearest choice.
- Create **callable objects** with `__call__`, and choose between function, closure, `partial` and callable class.
- Review a function for design quality (naming, parameters, purity, errors, typing, tests) and refactor it.
- Build classes from first principles: instance/class attributes, methods, `self`, `__repr__`, equality, encapsulation conventions.
- Explain the **construction protocol**: `__new__` → `__init__`; use alternative constructors and factory classmethods; avoid heavy work in `__init__`.
- Use inheritance and `super()` correctly for **single inheritance and constructor chaining**, and recognise when composition is better.
- Review a class for design quality and refactor it.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Variables, types, mutability | Module 1.2 | Closures capture variables; object identity |
| Conditionals, loops, function basics | Module 1.3 (01–04) | Foundation |
| Scope and lifetime | Module 1.3 (05) | LEGB → closures and `nonlocal` |
| Pure functions and side effects | Module 1.3 (06) | Function review checklist |
| Collections, comprehensions, sorting | Module 1.4 | `map`/`filter`/`key=` |
| Recursion | Module 1.4 (06) | Functions calling themselves |
| Testing with pytest | Module 1.7 | Every exercise has tests |
| Encapsulation, composition, inheritance basics | Module 1.8 (01, 02) | Classes in context |
| Class vs instance attributes | Module 1.8 (04) | Reinforced from first principles |
| Dataclasses | Module 1.8 (03) | Compared with hand-written classes |
| Decorators, `functools` | Module 1.9 (02, 09) | Closures underlie decorators |

**Tools:** Python 3.12+, `pytest`, `ruff`, `mypy`/`pyright`, `dis` and `inspect` (for peeking), and a debugger (Module 1.7).
[`pythontutor.com`](https://pythontutor.com) is excellent for visualising closures and objects.

---

## 3. How the module is organised

```text
Phase A — Functions as Values                    (Basics → Intermediate)
  01 first-class functions and callables
  02 lambda expressions
  03 closures and captured variables
  04 nonlocal and late-binding pitfalls
Phase B — Functional Toolkit and Callables       (Intermediate)
  05 map, filter, reduce and key functions
  06 callable objects with __call__
  07 function design review and refactoring checklist
Phase C — Classes from First Principles          (Basics → Intermediate)
  08 classes and objects from first principles
  09 __init__, __new__ and object construction
  10 inheritance and super() constructor chaining
Phase D — Consolidation                          (Intermediate)
  11 class design review and refactoring checklist
```

Pace: about 2 weeks part-time (one lesson per session; two review lessons
double as consolidation exercises).

---

## Lesson 01 — `01-first-class-functions-and-callables.md`

**Why it matters.** "Functions are objects" is the idea that makes
decorators, callbacks, `sorted(key=...)`, dispatch tables, strategies and
`functools` possible. Until it is intuitive, those topics feel like magic.

### Basic — what to learn

- A function is an object with a type (`function`), identity, attributes and behaviour; `def` creates the object and binds a name.
- Functions can be: assigned to variables, stored in lists/dicts, passed as arguments, returned from functions, and compared by identity.
- Calling vs referring: `f` (the function object) vs `f()` (the call); the classic bug of forgetting parentheses or adding them too early (`callback=do_work()`).

```python
def square(x): return x * x
def cube(x):   return x ** 3

ops = {"square": square, "cube": cube}
print(ops["cube"](3))                      # 27
print(square, type(square), square.__name__)

def apply(fn, values):                     # a higher-order function
    return [fn(v) for v in values]

print(apply(square, [1, 2, 3]))            # [1, 4, 9]
```
- Basic callbacks: pass a function that will be called later (`sorted(words, key=len)`).

### Intermediate — what to learn

- Function attributes: `__name__`, `__qualname__`, `__doc__`, `__module__`, `__defaults__`, `__kwdefaults__`, `__annotations__`, `__code__`, `__dict__` (you can attach attributes — use sparingly).
- What counts as **callable**: functions, lambdas, methods (bound/unbound), builtins, classes (calling a class creates an instance), instances of classes defining `__call__`, `functools.partial` objects; test with `callable(obj)`.
- **Bound methods**: `obj.method` is an object remembering `obj` (`__self__`) and the function (`__func__`); `unbound` access via the class gives a plain function.
- **Dispatch tables** instead of `if/elif` chains:

```python
def handle_start(ctx): ...
def handle_stop(ctx): ...
HANDLERS = {"start": handle_start, "stop": handle_stop}

def dispatch(cmd, ctx):
    try:
        handler = HANDLERS[cmd]
    except KeyError:
        raise ValueError(f"unknown command {cmd!r}; expected one of {sorted(HANDLERS)}") from None
    return handler(ctx)
```
- Returning functions (function factories): `def make_multiplier(n): return lambda x: x * n` (previews closures).
- Passing functions with arguments: `functools.partial(fn, a, b=2)`; `callable` type hints: `Callable[[int, int], int]`, `Callable[..., Any]`.
- Using functions as strategies: pass a `pricing` or `validator` function into a pipeline instead of subclassing.

### Advanced — what to learn

- How a call actually works: arguments bound to parameters, a new frame created (Module 1.19 lesson 03); `inspect.signature` to inspect parameters; `inspect.getsource`.
- Descriptors: why functions defined in a class become bound methods (functions implement `__get__` — see Module 1.11 lesson 06); `staticmethod`/`classmethod` wrappers.
- Function identity pitfalls: `lambda` in a loop, comparing functions, storing bound methods in sets/dicts (new bound-method object each access, but equality compares `__self__` and `__func__`), garbage-collection of callbacks, bound methods keeping objects alive (memory leaks; `weakref.WeakMethod` — Module 1.13 lesson 10).
- Typing callables precisely: `Callable[[A, B], R]`, `Protocol` with `__call__` for keyword arguments, `ParamSpec`, `TypeVar` for generic higher-order functions: `def apply[T, R](fn: Callable[[T], R], xs: Iterable[T]) -> list[R]`.
- Functions as the unit of reuse in data pipelines: composing transformations (`pipe(value, f, g, h)`), registry of transform steps, config-driven selection by name.
- Design trade-offs: function vs class for stateless behaviour; when a dict of functions beats polymorphism; testing higher-order functions with simple fakes.
- Callbacks and inversion of control: event handlers, hooks (`atexit`, `signal`, `sys.excepthook`), observer pattern basics (Module 1.20 lesson 04).

### Common mistakes

- `register(handler())` instead of `register(handler)`.
- Storing a function call's *result* in a dispatch table by accident.
- Assuming lambdas/closures capture values (not variables) — see lesson 04.

### Self-check

1. Name five different ways a function can be used as a value, with a one-line example for each.
2. Replace a 5-branch `if/elif` command handler with a dispatch table including a helpful error.
3. Write `compose(*fns)` and `pipe(value, *fns)` with type hints and tests.

---

## Lesson 02 — `02-lambda-expressions-and-when-not-to-use-them.md`

**Why it matters.** `lambda` is everywhere in `sorted(key=...)`, pandas
`apply`, callbacks and quick scripts — and overused when a named function
or `operator` helper would be clearer. Knowing its limits prevents both
cargo-cult use and unreadable code.

### Basic — what to learn

- Syntax: `lambda params: expression` — an anonymous function whose body is **one expression** (no statements, no assignments, no `return`; the expression's value is returned).
- Equivalent to a `def` with a single `return`.
- Common uses: short `key` functions, simple callbacks, inline small transformations.

```python
words = ["banana", "Apple", "cherry"]
print(sorted(words, key=lambda w: w.lower()))      # case-insensitive sort
print(sorted(words, key=len))                       # no lambda needed
pairs = [("a", 3), ("b", 1)]
print(min(pairs, key=lambda p: p[1]))               # ('b', 1)
```
- Lambdas can have default args, `*args`, `**kwargs`; they are ordinary function objects (`type(lambda: 0)` is `function`, name is `<lambda>`).

### Intermediate — what to learn

- **When to prefer a named function**: logic longer than a line, reused code, anything needing a docstring/tests, any time a descriptive name clarifies intent, tracebacks (they show `<lambda>`), debugging, pickling (lambdas can't be pickled — matters for `multiprocessing`), type annotations.
- **Alternatives** that read better: `operator.itemgetter/attrgetter/methodcaller` (Module 1.13 lesson 02), `str.lower` as a key (`key=str.lower`), `functools.partial`, comprehensions, `len`, `abs`, `bool`.
- PEP 8: don't assign a lambda to a name (`f = lambda x: 2*x`) — use `def`. (Ruff rule `E731`.)
- Lambdas with conditionals (`lambda x: a if x else b`), with default argument tricks to freeze values (`lambda x, n=n: x * n`) — and why this fixes loop-capture bugs (lesson 04).
- Typical library usage: pandas (`df.apply(lambda r: ..., axis=1)` is slow and opaque—prefer vectorised operations, Stage 2), `sorted`/`max` keys, `threading.Thread(target=lambda: ...)`, GUI/event callbacks, `defaultdict(lambda: 0)` (prefer `int`/`list`), `re.sub(pattern, lambda m: ..., s)`.

```python
from collections import defaultdict
d = defaultdict(lambda: defaultdict(int))     # nested counters — idiomatic use of lambda as a factory
d["a"]["x"] += 1
```

### Advanced — what to learn

- Lambda semantics under the hood: a lambda has its own scope and closes over *variables* of the enclosing scope (lesson 03); late binding means lambdas created in a loop see the final value.
- Performance: no speed difference vs `def`; function call overhead exists either way; `operator.itemgetter` is faster than an equivalent lambda for hot keys (measure with `timeit`).
- Readability heuristics and linting: `ruff` rules (`E731`, `PLW0108` unnecessary lambda, `C417` unnecessary map, `FURB118` use `operator`), "if you need a comment to explain the lambda, use `def`".
- Higher-order patterns where lambdas are idiomatic: sort keys, small predicates, defaults factories, lazy evaluation thunks (`lambda: expensive()`), deferred arguments in `functools.partial` alternatives, test stubs (`fake = lambda *a, **k: 42`).
- Type hints for lambdas: you can't annotate lambda parameters directly; annotate the variable/parameter that holds it (`key: Callable[[Item], float]`) — another reason to use `def` when types matter.
- Security and safety: never build lambdas from untrusted strings with `eval` (Module 1.12 lesson 09).
- Functional-style pipelines: `functools.reduce(lambda acc, x: ..., items, init)` — often less readable than a loop; use `sum`, `any`, `all`, `itertools.accumulate`, or an explicit loop.
- Code review exercise: take 15 lambdas from open-source projects and decide for each: keep / replace with `operator` / replace with `def` / replace with comprehension; justify.

### Common mistakes

- Cramming multi-step logic into a lambda.
- Assigning lambdas to names instead of defining functions.
- Using `lambda x: f(x)` where `f` itself would do.

### Self-check

1. Rewrite three lambdas using `operator.itemgetter`, `str.lower` and a named function; explain each choice.
2. Why can't a lambda contain an assignment statement, and what does that tell you about its intended use?
3. Show a case where a lambda breaks `multiprocessing` and the fix.

---

## Lesson 03 — `03-closures-and-captured-variables.md`

**Why it matters.** Closures are how functions "remember" their
surroundings. They underlie decorators, callbacks with state, function
factories, memoisation, partial application and many framework patterns.
Misunderstanding them causes the notorious loop-capture bug.

### Basic — what to learn

- Recall scope (LEGB): Local → Enclosing → Global → Built-in (Module 1.3 lesson 05).
- A **closure** is a function that retains access to variables from the enclosing function scope **after that function has returned**.
- Minimal example:

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c1, c2 = make_counter(), make_counter()
print(c1(), c1(), c2())      # 1 2 1   — each closure has its own `count`
```
- Use cases: function factories (`make_multiplier(n)`), private state without a class, simple memoisation, callbacks that need context.

### Intermediate — what to learn

- **Free variables** (referenced but not defined locally) and **cells**: the compiler creates a cell object per captured variable; the closure keeps references to those cells. Inspect: `fn.__closure__`, `fn.__code__.co_freevars`, `cell.cell_contents`.
- Closures capture **variables, not values**: if the variable changes later, the closure sees the new value.
- Closure vs class: a closure with mutable state ≈ an object with one method; choose a class when you need multiple methods, inspection, pickling, or documentation.
- Closures for configuration: `make_validator(min_len, max_len)` returning a validating function; `make_logger(prefix)`; rate-limiter/accumulator patterns.
- Closures in decorators (Module 1.9 lesson 02): the wrapper closes over the decorated function and decorator arguments.
- Lifetime: captured variables live as long as the closure; large captured objects can keep memory alive (leaks) — don't capture big DataFrames unintentionally.

```python
def make_validator(min_len: int, max_len: int):
    def validate(s: str) -> str:
        if not (min_len <= len(s) <= max_len):
            raise ValueError(f"length must be {min_len}–{max_len}, got {len(s)}")
        return s
    return validate

validate_name = make_validator(2, 20)
print(validate_name.__closure__[0].cell_contents)   # a cell with 2 or 20
```

### Advanced — what to learn

- Compile-time mechanics: the symbol table decides local/free/cell variables (Module 1.19 lesson 01); bytecode: `MAKE_CELL`, `LOAD_CLOSURE`, `LOAD_DEREF`, `STORE_DEREF` (Module 1.19 lesson 02) — see them with `dis.dis`.
- Closures and comprehensions: since Python 3.12 comprehensions are inlined (PEP 709) but still have separate-scope semantics for the iteration variable; lambdas defined inside comprehensions still close over the comprehension's variables.
- **Memoisation** with closures vs `functools.cache` (thread-safety, unhashable arguments, cache invalidation, memory growth).
- Closures and concurrency: shared mutable cells across threads need locks; closures sent to `multiprocessing` can't be pickled — use top-level functions or `partial`.
- Closures capturing `self` in methods (memory cycles, callbacks keeping objects alive); `weakref` for callbacks; prefer explicit parameters over implicit capture when passing across layers.
- Functional programming idioms: currying (`curry(f)(a)(b)`), partial application (`functools.partial` is preferred and picklable), function composition factories, memoised factories.
- Testing closures: test the returned function's behaviour; independence of separate instances; verifying captured configuration via observable behaviour rather than `__closure__` introspection.
- Debugging closures: inspect `__closure__`, `co_freevars`, print `id(cell)`; use Python Tutor to visualise frames and cells.
- Exercise: implement `once(fn)`, `memoize(fn)`, `rate_limited(calls, period, clock=time.monotonic)`, and `counter_factory()`; add tests with a fake clock (Module 1.16 lesson 07).

### Common mistakes

- Expecting a closure to snapshot the variable's value at creation time.
- Mutating captured state from multiple threads without locks.
- Capturing large objects unintentionally.

### Self-check

1. What are free variables and cells, and how can you inspect them?
2. When would you choose a class over a closure for stateful behaviour?
3. Implement `memoize` as a closure and compare behaviour and limits with `functools.cache`.

---

## Lesson 04 — `04-nonlocal-and-late-binding-pitfalls.md`

**Why it matters.** `UnboundLocalError`, counters that don't increment,
buttons that all print the last index, and "why is my callback list all the
same?" — these classic bugs come from how assignment, scope and late binding
interact. Two small keywords and a few patterns remove them.

### Basic — what to learn

- Reading a variable from an enclosing scope works automatically; **assigning** to it creates a new **local** variable unless declared `nonlocal` (enclosing function) or `global` (module).
- `UnboundLocalError`: a name assigned anywhere in a function is local for the *entire* function (decided at compile time).

```python
def broken():
    total = 0
    def add(n):
        total += n          # UnboundLocalError: assignment makes `total` local to add()
        return total
    return add

def fixed():
    total = 0
    def add(n):
        nonlocal total
        total += n
        return total
    return add
```
- `global` for module-level state — and why to avoid it (Module 1.3 lesson 05): hidden coupling, hard testing.
- Mutating a captured **mutable object** (list/dict) doesn't need `nonlocal` because you aren't rebinding the name (`counter["n"] += 1`) — but is that clearer than `nonlocal`?

### Intermediate — what to learn

- **Late binding in closures**: closures look up the variable when *called*, not when *created*.

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])              # [2, 2, 2]   (surprise!)

# Fix 1: default argument freezes the value at definition time
funcs = [lambda i=i: i for i in range(3)]
# Fix 2: functools.partial
from functools import partial
funcs = [partial(lambda i: i, i) for i in range(3)]
# Fix 3: factory function creates a new scope per iteration
def make(i): return lambda: i
funcs = [make(i) for i in range(3)]
```
- The same bug in: callbacks created in loops (GUI buttons, scheduled jobs), `threading.Thread(target=lambda: work(i))`, deferred SQL/queries, test parametrisation by loops, decorators in loops.
- Late binding in **default arguments is the opposite**: defaults are evaluated **once at definition time** (mutable-default trap: `def f(x, acc=[])`). Contrast the two behaviours side by side and memorise: *closures: late; defaults: early*.
- `nonlocal` vs `global` rules: `nonlocal` requires the name to already exist in an enclosing function scope (not module); can't be used at module level; combine with nested functions in decorators/counters.
- Class bodies are not enclosing scopes for methods: methods can't see class-level names unqualified (use `self.`/`ClassName.`).
- Comprehension scoping: iteration variable doesn't leak (Python 3), but the walrus `:=` target does (Module 1.15 lesson 02).

### Advanced — what to learn

- How the compiler decides: symbol-table analysis marks names as local/global/free/cell; `nonlocal` makes the name a free variable that is *stored* via `STORE_DEREF`; view with `dis` and `symtable` (Module 1.19 lessons 01–02).
- Closures and **thread/async timing**: callbacks scheduled later (`loop.call_later`, `threading.Timer`, task callbacks) executing after loop variables changed; use partial/default args or `functools.partial` objects; `asyncio.TaskGroup` with loop-created tasks closing over loop variables.
- Avoiding hidden state: prefer returning new values or using small classes/dataclasses to hold mutable state when `nonlocal` chains become hard to follow; "functional core" style (Module 1.8 lesson 07).
- Linting: Ruff `B023` (function definition does not bind loop variable), `PLW0603` (global statement), `PLW0602`; mypy/pyright warnings for possibly-unbound variables; use them in CI.
- Testing for late-binding bugs: tests that create multiple closures from a loop and assert distinct behaviour; parametrised tests instead of loop-generated test functions; regression tests for each discovered bug.
- Comparisons with other languages: JavaScript `var` vs `let` closures in loops, Java's effectively-final requirement, Go's loop-variable semantics change (1.22) — why the Python behaviour surprises people (and why Python hasn't changed it).
- Defensive patterns: explicit factory functions with docstrings for loop-created callbacks; naming conventions (`make_*`, `build_*`); small helper `bind(fn, *args)` implemented via `partial`; avoiding lambda-in-loop in reviews.
- Exercise: collect the six canonical late-binding bugs (list of lambdas, thread targets, tkinter-like callbacks simulated, scheduled jobs, class-body comprehension surprise, default mutable argument) into a `pitfalls/` test module — each with a failing test, the fix, and a Ruff rule or review note that would have caught it.

### Common mistakes

- Using `global` to share state "because `nonlocal` is confusing".
- Creating callbacks in loops with bare `lambda` or nested `def` and no binding.
- Forgetting that augmented assignment (`+=`) is an assignment.

### Self-check

1. Why does `total += n` fail in a nested function without `nonlocal`, but `items.append(n)` works?
2. Give three fixes for the loop-lambda bug and the trade-offs of each.
3. Explain "closures bind late, defaults bind early" with a code example for each.

---

## Lesson 05 — `05-map-filter-reduce-and-sorting-with-key-functions.md`

**Why it matters.** Transforming, selecting, aggregating and ordering data
are the daily work of data and AI engineers. Knowing the functional toolbox
*and* its idiomatic Python alternatives (comprehensions, generator
expressions, `sum`/`any`/`all`, `sorted(key=)`) lets you pick the clearest,
most efficient form — and read others' code.

### Basic — what to learn

- `map(fn, iterable)` → lazy iterator of `fn(x)`; `filter(pred, iterable)` → lazy iterator of items where `pred(x)` is truthy (`filter(None, xs)` drops falsy items); `functools.reduce(fn, iterable[, initial])` → folds to a single value.
- Laziness: `map`/`filter` return iterators (single-use); wrap with `list(...)` to materialise; they work with multiple iterables (`map(operator.add, a, b)`).
- Idiomatic equivalents: comprehensions and generator expressions are usually clearer:

```python
nums = [1, 2, 3, 4, 5]
squares_of_evens = list(map(lambda x: x*x, filter(lambda x: x % 2 == 0, nums)))   # works
squares_of_evens = [x*x for x in nums if x % 2 == 0]                                # preferred
total = sum(x*x for x in nums if x % 2 == 0)
```
- `sorted(iterable, key=..., reverse=...)`, `list.sort()`, `min/max(iterable, key=...)`; `key` function is called once per element (decorate–sort–undecorate); sorting is **stable**.
- Common keys: `len`, `str.lower`, `abs`, `lambda p: p[1]`, `operator.itemgetter(1)`, `operator.attrgetter("name")`.

### Intermediate — what to learn

- Multi-key and mixed-direction sorting: tuple keys (`key=lambda r: (r.dept, -r.salary)`), two-pass stable sort (sort by secondary key first, then primary), `functools.cmp_to_key` for legacy comparators, locale-aware keys (`locale.strxfrm`), `None` handling in keys (`(x is None, x)`).
- `reduce` use cases: composing functions, merging dicts/sets (`reduce(operator.or_, sets)`), running products; often replaced by `sum`, `math.prod`, `any`, `all`, `itertools.accumulate`, `"".join`, or a clear loop; give the reader the clearest option.
- Aggregation patterns: counting (`collections.Counter`), grouping (`itertools.groupby` after sort, `defaultdict(list)`), top-K (`heapq.nlargest`, `sorted(...)[:k]`), min/max with default (`max(xs, default=None)`).
- `any`/`all` with generator expressions for short-circuiting; `next((x for x in xs if pred(x)), default)` for "find first".
- `zip`, `enumerate`, `reversed`, `itertools` helpers as companions (Module 1.13 lesson 01); `zip(strict=True)` (3.10+).
- When `map` with a named function is best: `list(map(int, strings))`, `map(str.strip, lines)`, `map(json.loads, lines)` — concise and no lambda.
- Data-oriented examples: normalising records, cleaning columns, filtering invalid rows with a validator, scoring candidates, sorting model results by metric then name, picking best run by validation loss.

```python
runs = [{"id": "a", "loss": 0.31, "ts": 3}, {"id": "b", "loss": 0.27, "ts": 1}, {"id": "c", "loss": 0.27, "ts": 2}]
best = min(runs, key=lambda r: (r["loss"], r["ts"]))            # ties broken by timestamp
leaderboard = sorted(runs, key=operator.itemgetter("loss", "ts"))
```

### Advanced — what to learn

- Laziness and memory: streaming pipelines (`filter → map → islice`) with constant memory vs materialised lists; single-pass iterators vs re-iterables; accidental exhaustion bugs; `itertools.tee` costs.
- Performance: comprehension vs `map` with a builtin (can be faster) vs `map` with a lambda (usually slower); `sum` vs `reduce`; `sorted` key-calls vs repeated attribute lookups; measure (Module 1.17 lesson 03); vectorise numeric work with NumPy/pandas (Stage 2) instead of Python-level loops.
- Correctness traps: `sorted` on mixed types (`TypeError`), NaN in keys (inconsistent ordering), unstable assumptions about `set` ordering, mutating the list while iterating, key functions with side effects, `reduce` without an initial value on empty input (`TypeError`), floating-point accumulation order (`math.fsum`).
- Functional-style API design: accept `key=` callables in your own functions (`top_k(items, k, key=...)`), `default=` parameters, `Callable` type hints, keyword-only `key` conventions; make behaviour match `sorted/min/max`.
- Parallel map: `concurrent.futures.Executor.map`, `multiprocessing.Pool.map` (pickling constraints: no lambdas), chunking; compare with Spark/Dask map operations (Stage 2).
- Higher-order helpers: `functools.reduce` for pipelines, `functools.partial` to adapt functions to `map`, `operator.methodcaller`, `itertools.starmap` for argument tuples.
- Refactoring exercise: take five code snippets with manual loops/accumulators and nested lambdas, rewrite with the clearest tool, and document why; also take five `reduce`/`map(lambda)` one-liners and rewrite them as loops/comprehensions where clearer.
- Testing: property-based tests on sorting helpers (idempotence, stability, permutation of input — Hypothesis, Stage 2), table-driven tests for tie-breaking.

### Common mistakes

- Exhausting an iterator and then reusing it.
- Using `reduce` where `sum`/`join` is clearer.
- Sorting with an expensive key repeatedly instead of precomputing once.

### Self-check

1. Rewrite `reduce(lambda a, b: a + b, xs)` and `list(filter(lambda x: x > 0, xs))` in the most idiomatic forms.
2. How do you sort by `name` ascending then `score` descending without a custom comparator?
3. Implement `top_k(items, k, *, key=None, reverse=False)` using `heapq`, with tests that match `sorted(...)[:k]`.

---

## Lesson 06 — `06-callable-objects-with-call.md`

**Why it matters.** Sometimes behaviour needs **state**, **configuration**
and **a function-like call syntax** at once: validators with settings,
retry policies, rate limiters, feature transforms in ML pipelines
(`scaler(x)`), tool objects for agents, middleware. Callable objects
(`__call__`) fit exactly there.

### Basic — what to learn

- Defining `__call__(self, *args, **kwargs)` makes instances callable: `obj(...)` ≡ `type(obj).__call__(obj, ...)`.
- Stateful callable example:

```python
class Counter:
    def __init__(self, start: int = 0) -> None:
        self.n = start
    def __call__(self, step: int = 1) -> int:
        self.n += step
        return self.n

tick = Counter()
print(tick(), tick(), tick(5))          # 1 2 7
print(callable(tick))                   # True
```
- Configurable callable: construct once with settings, call many times with data:

```python
class Scaler:
    def __init__(self, factor: float) -> None: self.factor = factor
    def __call__(self, x: float) -> float: return x * self.factor
double = Scaler(2)
print(list(map(double, [1, 2, 3])))     # [2, 4, 6]
```

### Intermediate — what to learn

- **Choosing among tools** for "a function with configuration/state":

| Need | Use |
| --- | --- |
| Stateless behaviour | plain function |
| Fix some arguments | `functools.partial` (picklable, simple) |
| Small private state | closure with `nonlocal` |
| State + several methods, inspectability, pickling, docs, inheritance | callable class (or regular class with a named method) |
| Many variations of one behaviour | strategy functions/classes in a registry |

- Callable classes in practice: PyTorch `nn.Module.__call__` (invokes `forward` with hooks), scikit-learn-style transformers (`fit`/`transform` are usually methods—not `__call__`), Keras layers, Django/ASGI middleware classes, `logging.Filter` objects, validators in Pydantic/attrs, decorators implemented as classes (Module 1.12 lesson 03).
- Making callable objects well-behaved: `__repr__` showing configuration, `__eq__`/`__hash__` when used as keys/dispatch, type hints on `__call__`, docstrings; `functools.update_wrapper(self, fn)` for class-based decorators.
- Callable objects as **dependencies** (`Clock`, `IdGenerator`, `Sleeper` — Module 1.16 lesson 07): pass `now=Clock()`-like callables; fakes are trivial (`lambda: fixed`).
- Using callables with higher-order functions: `map`, `sorted(key=...)`, `threading.Thread(target=obj)`, `atexit.register(obj)`, `signal.signal(sig, obj)`, `Executor.submit(obj, ...)` — all accept any callable.
- Pitfalls: confusing a class (callable that builds instances) with instances being callable; calling an object that is not callable (`TypeError: 'X' object is not callable`); forgetting `self` state is shared across calls and threads.

### Advanced — what to learn

- Typing: `Protocol` with `__call__` to describe callbacks with keyword args (`class Handler(Protocol): def __call__(self, event: Event, *, retry: bool = ...) -> None: ...`); `Callable` aliases; generics (`Callable[[T], R]`); `ParamSpec` for wrappers.
- Metaclass `__call__` vs instance `__call__`: calling a *class* triggers `type.__call__` → `__new__` → `__init__` (lesson 09); calling an *instance* triggers its class's `__call__`; both are "callable" with different protocols — draw the lookup path.
- Performance and specialisation: calling instances adds a Python-level frame; for hot loops, a plain function or bound method can be faster; measure; `__call__` lookup uses the type slot (`tp_call`), implemented efficiently.
- Concurrency and state: callable objects with internal mutable state need locks (`threading.Lock`) or per-thread instances; avoid sharing across processes without considering pickling (state copied).
- Callable objects for agents/tools (preview of later stages): a `Tool` class with `name`, `description`, JSON schema, and `__call__(**kwargs)`; validation, timeouts, retries, logging; registry of tools by name.
- Serialization: pickle/unpickle of callable instances works if class is importable; closures and lambdas don't; use callable classes (or `partial` of module-level functions) for multiprocessing and job queues.
- Testing: assert both configuration (via public attributes or `__repr__`) and call behaviour; inject fake callables to test higher-level code; property-based tests for pure callable objects.
- Design review exercise: given a 120-line procedural function with many parameters and shared mutable state, refactor into (a) pure functions + dataclass config, (b) a callable class, (c) closures; compare readability, testability and extensibility; decide and document.

### Common mistakes

- Callable class when a function (or `partial`) suffices.
- Hidden mutable state making calls non-repeatable.
- Forgetting that instances in `multiprocessing` are copied per process.

### Self-check

1. When does `obj(x)` call `type(obj).__call__`, and what does `Counter()(...)` vs `Counter(...)` mean?
2. Pick the right tool (function / partial / closure / callable class) for five described scenarios and justify.
3. Implement a `RetryPolicy` callable class with `__call__(fn, *args)` and tests using a fake clock and sleep.

---

## Lesson 07 — `07-function-design-review-and-refactoring-checklist.md`

**Why it matters.** Functions are where logic lives; most bugs, test
difficulty and maintenance cost trace back to poorly designed functions.
This lesson turns the whole "Functions" thread (Modules 1.3–1.9 + lessons
01–06) into a practical **review and refactoring checklist** you can apply
to your own code and in code review.

### Basic — what to learn (the checklist, level 1)

1. **Name**: verb phrase describing what it does (`parse_invoice`, `is_valid_email`), no vague names (`process`, `handle`, `do_stuff`), consistent vocabulary.
2. **Single responsibility**: describable in one sentence without "and"; if not, split.
3. **Size & nesting**: ideally < 20–30 lines, nesting ≤ 2–3 levels; use guard clauses/early returns.
4. **Parameters**: ≤ 3–4; no boolean flags that switch behaviour; sensible defaults; no mutable defaults; keyword-only for options (Module 1.15 lesson 03).
5. **Return value**: consistent type (don't return `str` sometimes and `None` other times without a type); don't return error codes mixed with data; document `None`.
6. **Docstring** with summary, parameters (units!), returns, raises, one example for public functions (Module 1.6 lesson 07).
7. **Type hints** on all public functions.
8. **Tests**: at least happy path, boundary, invalid input, and one regression test per fixed bug.

```python
# smell: flag argument, mixed returns, vague name
def process(data, flag):
    if flag:
        return clean(data)
    return None if not data else data.strip()

# better: two functions, clear names, one return type
def clean_text(text: str) -> str: ...
def strip_or_empty(text: str | None) -> str:
    return text.strip() if text else ""
```

### Intermediate — what to learn (level 2)

- **Purity & side effects** (Module 1.3 lesson 06): separate computation from I/O; make side effects explicit in the name (`save_`, `send_`, `write_`); inject dependencies (clock, file, client) instead of reaching for globals; avoid mutating arguments (or document it loudly); return new values.
- **Error handling**: validate inputs at boundaries (Module 1.3 lesson 07); raise specific exceptions with helpful messages; don't catch `Exception` to hide bugs; don't use exceptions for ordinary control flow in hot paths; clean up resources with context managers.
- **Abstraction levels**: a function should operate at one level of abstraction (don't mix business rules with string formatting and file I/O); extract helper functions named after intent.
- **Parameter design**: group related parameters in a dataclass (parameter object), accept abstract inputs (`Iterable`, `Mapping`) and return concrete outputs, avoid `**kwargs` pass-through unless forwarding, avoid positional parameters whose order is easy to mix (`transfer(src, dst, amount)` → keyword-only), units in names or types.
- **Idempotence & determinism** for pipeline functions: same inputs → same outputs; no hidden time/random dependencies (inject or seed); safe to retry (Module 1.10 lesson 04).
- **Complexity** control: cyclomatic complexity (`radon cc`, Ruff `C901`), early returns, dispatch tables, polymorphism/`match` instead of long `if` chains; avoid deep recursion where loops suffice (Module 1.19 lesson 03).
- **Performance sanity**: avoid accidental O(n²) (`in list`, repeated concatenation), repeated parsing/compiling in loops, building large lists when a generator will do; but measure before optimising (Module 1.17).
- **Refactoring steps** (Module 1.23 lesson 03): characterise with tests → rename → extract function → introduce parameter object → remove flag argument → inject dependency → replace conditional with dispatch/polymorphism → simplify → re-run tests after each step.

### Advanced — what to learn (level 3)

- **Contracts**: preconditions/postconditions/invariants documented and (selectively) enforced with explicit checks or assertions in debug paths (never `assert` for user input); property-based tests encoding contracts (Hypothesis); `typing.assert_never`, `Literal`, `NewType`, value objects to make invalid states unrepresentable.
- **API-level function design** (Module 1.20 lessons 06–07): stability, deprecation of parameters, accepting `key=`/`default=` conventions, return types that can evolve (results objects), async/sync twins, documented thread-safety, resource ownership.
- **Concurrency considerations**: functions touching shared state; thread-safe vs not; async functions must not block the event loop (no `time.sleep`, blocking I/O) and must handle cancellation; avoid hidden global caches; document reentrancy.
- **Observability**: structured logging with context, metrics/timing decorators (Module 1.12 lesson 03), tracing spans, error reporting with context (exception notes — Module 1.15 lesson 04); avoid logging secrets (Module 1.22).
- **Security review of functions**: untrusted inputs, injection sinks, path handling, subprocess, deserialisation (Module 1.22) — mark "trust boundary" functions and keep them small.
- **Review at scale**: automated gates (Ruff rule sets `C90`, `PLR`, `D`, `ANN`, `FBT`, `ARG`, `B`; mypy strict on new modules), docstring coverage (`interrogate`), complexity ratchet (no function above N), PR checklist items; sampling reviews of the longest/most complex functions each sprint.
- **Data/AI-specific function design**: transformations as pure, vectorised, typed functions over DataFrames/arrays (Stage 2); separating feature computation from model code; deterministic preprocessing functions shared between training and serving (avoid train/serve skew); prompt-building functions as pure, versioned, tested units; tool-calling functions with strict schemas, timeouts and idempotency keys (later stages).
- **Anti-pattern gallery** with fixes: God function, hidden global dependence, output parameter mutation, boolean trap, stringly-typed options, swallowed exceptions, mixed I/O and logic, accidental generator exhaustion, lambda soup, deep nesting, copy-paste variants, speculative parameters.
- Exercise: pick **three** functions from your earlier module projects (Stage 1 projects in `00-Stage-1-Overview/Projects/`) and for each: score against the 20-item checklist, list violations, refactor in small commits with tests, show before/after metrics (lines, complexity, parameters, test count), and write a one-paragraph review note as if reviewing a colleague's PR.

### Common mistakes

- Treating the checklist as a rigid score rather than a conversation tool.
- Extracting functions with vague names that just move complexity around.
- Refactoring without tests.

### Self-check

1. Turn a function with a boolean flag and mixed return types into two well-typed functions.
2. Apply the checklist to a 60-line function and produce a prioritised refactoring plan.
3. Configure Ruff/mypy so CI enforces five of the checklist items automatically.

---

## Lesson 08 — `08-classes-and-objects-from-first-principles.md`

**Why it matters.** Module 1.8 taught *when and how to design* with classes.
This lesson makes sure the **mechanics** are solid: what a class is, what an
object is, how attributes and methods are resolved, what `self` really is,
and how Python's conventions (not enforced access modifiers) work. Without
this foundation, advanced OOP (Modules 1.11–1.12) feels like magic.

### Basic — what to learn

- A **class** is a blueprint (and itself an object); an **object/instance** is a value created from it; `class` statement creates a class object; calling the class creates an instance.
- Attributes and methods:

```python
class Account:
    interest_rate = 0.02                       # class attribute (shared)

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner                     # instance attributes
        self.balance = balance

    def deposit(self, amount: float) -> None:  # method
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount

    def __repr__(self) -> str:
        return f"Account(owner={self.owner!r}, balance={self.balance!r})"

a = Account("Ana", 100)
a.deposit(50)
print(a, Account.interest_rate)
```
- `self` is just the first parameter: `a.deposit(50)` is sugar for `Account.deposit(a, 50)`.
- Instance dict: `a.__dict__`; class dict: `Account.__dict__`; `type(a) is Account`; `isinstance(a, Account)`.
- Class vs instance attributes and the shadowing rule (Module 1.8 lesson 04): reading looks on the instance, then the class; assigning on the instance creates an instance attribute (doesn't change the class one).
- `__repr__` (developer-oriented) and `__str__` (user-oriented); define `__repr__` first.
- Methods vs functions; `@staticmethod`, `@classmethod` (first parameter `cls`) — when each is appropriate.

### Intermediate — what to learn

- **Encapsulation by convention**: `_protected`, `__private` (name mangling → `_Account__x`, to avoid accidental clashes in subclasses, not for security), public API small and documented; properties (`@property`) for validated or computed attributes (details in Module 1.11 lesson 05).
- **Invariants**: a class should keep its data valid at all times — validate in `__init__` and mutators; don't expose internal mutable state (return copies/tuples/read-only views).
- **Equality & hashing** basics: default is identity; implement `__eq__` (and `__hash__` for immutable value objects) — or use `@dataclass` (Module 1.8 lesson 03). Full rules in Module 1.11 lesson 01.
- **Mutability pitfalls**: mutable default args in `__init__` (`def __init__(self, items=[])`), class-level mutable attributes shared by all instances (`tags = []`), aliasing (two names, one object), shallow vs deep copy.
- **Methods that return `self` vs new objects**; fluent APIs; immutable value objects via `frozen=True` dataclasses.
- **Object lifecycle**: creation (`__init__`), use, destruction (garbage collection; avoid `__del__`); resource management with context managers (`__enter__`/`__exit__`, Module 1.9 lesson 03).
- Using classes for: entities with identity and mutable state (accounts, jobs), services with dependencies (clients, repositories), value objects, simple namespaces (prefer dataclasses/`SimpleNamespace`), stateful iterators; **not** for bags of unrelated functions (use a module).
- Introspection tools: `vars(obj)`, `dir(obj)`, `type(obj)`, `obj.__class__`, `isinstance/issubclass`, `hasattr/getattr`, `inspect.getmembers`; REPL exploration habits.
- Writing tests for a class: construct valid/invalid instances, behaviour of each method, invariants after sequences of operations, string representation, equality.

### Advanced — what to learn

- Attribute lookup mechanics (preview of Module 1.11 lesson 06): instance `__dict__` → class → base classes via MRO; methods are functions stored on the class and bound on access; why `obj.method` creates a bound method object; why monkeypatching a class attribute affects all instances.
- Object model facts: every class is an instance of `type`; `object` is the base of all classes; objects have identity (`id`), type, value; memory layout basics (`__dict__`, `__weakref__`, `__slots__` — Module 1.11 lesson 07).
- Class design heuristics: cohesion (methods use the same data), small public surface, tell-don't-ask, avoid "anemic" classes with all logic elsewhere vs "god" classes; prefer composition (Module 1.8 lesson 01) and dataclasses for data; avoid setters that bypass invariants; make illegal states unrepresentable (enums, value objects).
- Class-level things: constants, registries, counters (and thread-safety), alternative constructors (lesson 09), class methods vs static methods vs module functions (prefer module functions for helpers that don't need `cls`).
- Mutable global/class state hazards in tests and concurrency; dependency injection instead of class-level singletons.
- Type annotations for classes: attribute annotations in class body, `ClassVar`, `Self`, `Final`, generics (`class Box[T]`), protocols; `__slots__`/dataclasses interplay; checking with mypy/pyright strict.
- Serialisation of objects: `to_dict`/`from_dict` methods, JSON encoders, dataclasses `asdict`, pickling concerns (Module 1.11 lesson 11, Module 1.22 lesson 02); versioned schemas.
- Documenting classes: class docstring (purpose, invariants, thread-safety), attribute docs, examples; `__doc__`, Sphinx/mkdocstrings.
- Exercise: implement three small classes from scratch — `Stopwatch` (stateful, context manager), `Money` (value object, immutable, equality/hash, arithmetic), `JobQueue` (entity with invariants and methods) — with full tests, `__repr__`, type hints and docstrings; then re-implement `Money` and `JobQueue` using dataclasses and compare the code and trade-offs.

### Common mistakes

- Class-level mutable attributes shared by accident.
- Exposing internals so invariants can be broken.
- Using a class where a function or dataclass would do.

### Self-check

1. What does `a.deposit(50)` expand to, and what does `self` refer to?
2. Why is `tags = []` in a class body usually a bug and what is the fix?
3. Implement `Money` as an immutable value object with `__eq__`, `__hash__`, `__repr__`, and arithmetic that rejects mixed currencies.

---

## Lesson 09 — `09-init-new-and-object-construction.md`

**Why it matters.** "How is an object created?" has a two-step answer in
Python (`__new__` allocates, `__init__` initialises) that explains
immutable-type subclassing, singletons, caching, factories, and weird
behaviour when constructors do too much. It is the bridge to the data model
(Module 1.11) and metaclasses (Module 1.12).

### Basic — what to learn

- `Foo(args)` → `type.__call__(Foo, args)` → `Foo.__new__(Foo, args)` returns an instance → if it is an instance of `Foo`, `Foo.__init__(instance, args)` runs.
- `__init__` initialises an already-created instance, **returns `None`** (returning anything else raises `TypeError`); `__new__` creates (and returns) the instance (static method receiving `cls`).
- In 99 % of classes you only write `__init__`.
- Keep `__init__` simple: assign attributes, validate arguments; avoid I/O, network, heavy computation, threads starting, or calling overridable methods.

```python
class Demo:
    def __new__(cls, *args, **kwargs):
        print("__new__", cls.__name__)
        return super().__new__(cls)
    def __init__(self, x):
        print("__init__", x)
        self.x = x

Demo(5)        # __new__ Demo  ->  __init__ 5
```

### Intermediate — what to learn

- **When `__new__` is needed**: subclassing immutable built-ins (`int`, `str`, `tuple`, `frozenset`, `bytes`) where the value is fixed at creation:

```python
class Celsius(float):
    def __new__(cls, value: float):
        if value < -273.15:
            raise ValueError("below absolute zero")
        return super().__new__(cls, value)
```
  Also: singletons/instance caching (flyweight) — usually better done with a factory or module-level instance; returning an instance of another class (then `__init__` of `cls` is **not** called).
- **Alternative constructors** with `@classmethod`: `from_dict`, `from_json`, `from_env`, `from_path`, `parse`, `default`; return `cls(...)` so subclasses work (`cls`, not the hard-coded class name).

```python
@dataclass
class Config:
    host: str
    port: int
    @classmethod
    def from_env(cls, env=os.environ) -> "Config":
        return cls(env.get("HOST", "localhost"), int(env.get("PORT", 5432)))
```
- **Validation & normalisation** in `__init__` vs factories; avoid partially-initialised objects (every instance should be valid after construction).
- **Default arguments**: no mutable defaults (`items=None` then `self.items = list(items or [])`); copy incoming mutable arguments if you keep them (`list(items)`) to avoid aliasing surprises.
- **Many parameters**: keyword-only parameters, parameter objects, dataclasses (`__init__` generated), builders (Module 1.20 lesson 02).
- **Dependency injection through constructors**: pass collaborators (client, clock, repository) rather than creating them inside; defaults for convenience (`clock: Callable[[], datetime] = utc_now`).
- **Resource-owning objects**: don't open files/connections in `__init__` unless the class is a context manager that also closes them; consider `open()`/`connect()` methods or `@classmethod` + `with`.
- Testing construction: valid/invalid arguments, alternative constructors, subclass behaviour, no hidden I/O (use fakes).

### Advanced — what to learn

- Full construction protocol details: `type.__call__` logic; `__new__` + `__init__` argument forwarding; classes without `__init__`; `object.__new__` rejecting extra args when `__init__`/`__new__` both overridden mismatched; `__init_subclass__` runs at *class* creation, not instance creation (Module 1.12 lesson 05); metaclass `__call__` can override instance creation altogether (Module 1.12 lesson 07).
- Singletons and caches done properly: module-level instance, `functools.cache` on a factory, DI container; `__new__`-based singleton pitfalls (`__init__` re-runs on each call, thread-safety, subclass behaviour, testing difficulty).
- Pickling/copying and construction: `copy.copy` and unpickling **do not call `__init__`**; they use `__reduce__`/`__new__`/`__setstate__` (Module 1.11 lesson 11) — invariants established in `__init__` must be re-established in `__setstate__`; dataclasses with `__post_init__` and `InitVar`.
- Inheritance and construction: subclass `__init__` should call `super().__init__(...)` (lesson 10); constructors calling overridable methods can see half-initialised subclasses (a classic bug); template for safe construction: initialise own state first, then call `super().__init__`, or use factories/hooks after construction.
- Immutable value objects: frozen dataclasses (`object.__setattr__` in `__post_init__`), `NamedTuple`, `__slots__`, custom `__new__` for tuples; hashing consistency.
- Async construction: `__init__` can't be `async`; use `async classmethod create()` or async context manager (`async with Client.open() as c`) — a common stumbling block in async code.
- Typing constructors: `Self` return types for alternative constructors, overloaded `__init__`/`__new__`, generics `Box[int](...)`, `type[T]` factories, `dataclass_transform`.
- Performance: object creation cost; `__slots__`, dataclass `slots=True`, avoiding per-object dictionaries for millions of instances (Module 1.11 lesson 07); object pools/flyweights when profiling shows creation cost.
- Reading real constructors: `pathlib.Path.__new__`, `datetime.fromisoformat`, `Decimal.__new__`, `collections.namedtuple` internals, `dataclasses`-generated `__init__` (`inspect.getsource` / `dis`), `argparse.ArgumentParser.__init__` (lots of parameters—what would you change?).
- Exercise: implement (1) `PositiveInt(int)` with `__new__` validation; (2) `Settings.from_env/from_toml/from_dict` alternative constructors with subclass support; (3) a connection wrapper that opens lazily, closes in `__exit__`, and is not opened in `__init__`; (4) show that `copy.copy` bypasses `__init__` and fix a class that breaks because of it; with tests.

### Common mistakes

- Doing I/O or heavy work in `__init__`.
- Returning a value from `__init__`.
- Using `Foo.from_dict` implemented as `Foo(...)` (breaks subclasses).

### Self-check

1. Trace what happens, step by step, when you call `Demo(5)`.
2. Why does subclassing `int` require `__new__`?
3. Explain why `copy.copy(obj)` doesn't call `__init__` and what that implies for invariants.

---

## Lesson 10 — `10-inheritance-and-super-constructor-chaining.md`

**Why it matters.** Inheritance is easy to misuse and easy to break —
usually by not calling `super().__init__()` correctly, by overriding methods
without preserving the contract, or by using it for code reuse where
composition is simpler. This lesson covers the **practical, single-inheritance
core** (`super()`, constructor chaining, overriding, polymorphism); the
deeper mechanics — MRO, C3 linearisation, cooperative multiple inheritance,
mixins — are in Module 1.11 (lessons 08–09).

### Basic — what to learn

- Syntax: `class Child(Parent):`; the child inherits attributes and methods; the **is-a** test ("a `SavingsAccount` *is an* `Account`").
- Overriding methods; calling the parent version with `super()`:

```python
class Account:
    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner, self.balance = owner, balance
    def describe(self) -> str:
        return f"{self.owner}: {self.balance:.2f}"

class SavingsAccount(Account):
    def __init__(self, owner: str, balance: float = 0.0, rate: float = 0.02) -> None:
        super().__init__(owner, balance)          # constructor chaining
        self.rate = rate
    def describe(self) -> str:
        return super().describe() + f" (rate {self.rate:.1%})"

print(SavingsAccount("Ana", 100).describe())
```
- If a subclass defines `__init__` and forgets `super().__init__()`, the parent's attributes are never set → `AttributeError` later.
- `isinstance(obj, Parent)` is `True` for subclasses; `issubclass`; `type(obj) is Child` for exact type; prefer `isinstance` for checks.
- Polymorphism: code written against the parent works with any child (`for acct in accounts: acct.describe()`).

### Intermediate — what to learn

- **Constructor chaining patterns**: always call `super().__init__(...)` first (or deliberately after setting what the parent needs); forward only the arguments the parent expects; keep signatures compatible (**Liskov Substitution Principle**: a subclass should be usable anywhere the parent is — same preconditions or weaker, same postconditions or stronger).
- `super()` without arguments (Python 3) vs `Parent.__init__(self, ...)` — prefer `super()`; the second hard-codes the parent and breaks in multiple inheritance (Module 1.11 lesson 08).
- Overriding rules of thumb: keep the same signature (or add optional keyword-only parameters), don't narrow accepted inputs, don't widen exceptions, document overriding contracts; use `@typing.override` (3.12) to catch accidental mismatches.
- **Template method** (parent defines the algorithm, children override steps) vs passing strategy functions (lesson 01 / Module 1.20 lesson 04); **abstract methods** via `abc.ABC` (introduction; deep dive in Module 1.11 lesson 10): parent declares what children must implement.
- `super()` in other methods: extend rather than replace behaviour (`save`, `describe`, `validate`); `super().__repr__()`, `super().__eq__(other)` patterns.
- **Class attributes and inheritance**: children inherit class attributes; overriding in the child affects only that class; mutable class attributes shared by hierarchy (bug source).
- **Inheritance vs composition decision table**:

| Situation | Prefer |
| --- | --- |
| True is-a relationship with substitutable behaviour | Inheritance (shallow) |
| Reuse some behaviour of another class | Composition (has-a) |
| Behaviour varies by configuration | Strategy/function injection |
| Many orthogonal features | Composition / small mixins (carefully) |
| Parent is a framework base class meant to be subclassed | Inheritance (follow its contract) |

- Common pitfalls: deep hierarchies, "implementation inheritance" for code reuse, overriding without understanding the parent, parent constructors calling overridable methods, forgetting to chain `__init__`, inheriting from built-in containers (`list`, `dict`) and breaking invariants (use `collections.UserList/UserDict` or composition).

### Advanced — what to learn

- **Fragile base class problem**: changes in the parent break children; mitigate with small parent surface, documented extension points, composition, `final` methods (`@typing.final`), tests inherited by subclasses (contract tests).
- **Liskov violations in practice**: the Rectangle/Square example; a read-only subclass of a mutable parent; subclass that raises `NotImplementedError` for an inherited method (refused bequest) — refactor to a different hierarchy or composition.
- **Constructor chaining in dataclasses**: field ordering with defaults, `kw_only=True`, `__post_init__` chaining with `super().__post_init__()`, `InitVar` (Module 1.15 lesson 07); inheritance of `frozen`/`slots` rules.
- **Keyword-only cooperative constructors**: `def __init__(self, *, a, b, **kwargs): super().__init__(**kwargs)` — the foundation for cooperative multiple inheritance (full treatment in Module 1.11 lesson 08); recognise when a hierarchy might later need it.
- **`__init_subclass__`, class attributes and registries** as lightweight hooks instead of complex inheritance (Module 1.12 lesson 05).
- **Testing hierarchies**: write a base `ContractTests` class that every subclass's test inherits (parametrised fixture providing the class under test) to enforce substitutability; test `super()` chaining by asserting parent state set; mutation testing on overridden methods (Module 1.16 lesson 02).
- **Refactoring from inheritance to composition**: replace subclass with delegate (Module 1.23 lesson 03) step by step: introduce interface (Protocol), move behaviour to a collaborator, inject it, deprecate the subclass.
- **Frameworks and inheritance**: Django models/views, Airflow operators, PyTorch `nn.Module` (must call `super().__init__()` before assigning submodules), scikit-learn estimators (`BaseEstimator`, `fit/predict` contract, `__init__` must not do work or modify parameters), unittest `TestCase` (`setUp` chaining), `threading.Thread` subclasses (call `super().__init__()`), `Exception` subclasses (call `super().__init__(msg)`; picklable) — what each requires and what breaks if you forget.
- **Designing for extension vs closing for modification**: when to mark classes/methods as not meant for subclassing (`@final`, documentation), provide hooks, or offer plugin/strategy registries instead.
- **Metrics**: depth of inheritance tree, number of overridden methods, fan-out; code review smells (deep hierarchies, parallel hierarchies, subclass-per-config); refactoring targets.
- Exercise: model a small domain (notification channels: Email/SMS/Slack with retry and templating) first with a deep hierarchy and then with composition + strategy + a thin base class; compare tests, extensibility and complexity; write a short ADR recommending one; add contract tests; then add a new channel and measure the change footprint in each design.

### Common mistakes

- Forgetting `super().__init__()`.
- Changing method signatures or semantics in overrides.
- Inheriting just to reuse code.

### Self-check

1. What goes wrong if `SavingsAccount.__init__` doesn't call `super().__init__()`?
2. Give an example of a Liskov violation and two ways to fix the design.
3. Implement a parent with a template method and two children; write a contract-test mixin that all children must pass.

---

## Lesson 11 — `11-class-design-review-and-refactoring-checklist.md`

**Why it matters.** Classes encode your system's concepts. Poorly designed
classes (too big, anemic, leaky, tightly coupled) are the main source of
rigid, untestable code. This lesson turns the "OOP" thread (Modules 1.8, 1.9,
lessons 08–10, and the previews of 1.11–1.12) into a practical **class
design checklist** for self-review and code review.

### Basic — what to learn (the checklist, level 1)

1. **Purpose & name**: a noun that matches the domain; describable in one sentence; no `Manager`/`Helper`/`Util`/`Processor` unless truly justified.
2. **Single responsibility & cohesion**: methods use the same data; if the class has two reasons to change, split it.
3. **Is it a class at all?** Data only → dataclass/NamedTuple/TypedDict; stateless helpers → module functions; one method + state → closure/callable; behaviour + invariants → class.
4. **Construction**: `__init__` only assigns/validates; alternative constructors for parsing/loading; no I/O; no mutable defaults; every instance valid after construction.
5. **Public API small**: clear methods with verbs; internals prefixed `_`; no attribute exposure that breaks invariants; properties for computed/validated values.
6. **`__repr__`** for debugging; `__eq__`/`__hash__` consistent (or dataclass); `__str__` when user-facing text is needed.
7. **Type hints & docstrings** for public API (attributes, invariants, thread-safety notes).
8. **Tests**: construction, each public method, invariants after sequences of calls, error cases, equality/representation.

```python
# smell: manager class with unrelated responsibilities and public mutable state
class OrderManager:
    def __init__(self): self.orders = []; self.db = connect(); self.log = open("log.txt", "a")
    def add(self, o): ...; def email(self, o): ...; def report(self): ...; def export_csv(self): ...

# better: separate concerns, inject collaborators
@dataclass(frozen=True)
class Order: ...
class OrderRepository(Protocol): ...
class OrderService:
    def __init__(self, repo: OrderRepository, notifier: Notifier) -> None: ...
```

### Intermediate — what to learn (level 2)

- **Encapsulation & Law of Demeter**: don't reach through objects (`order.customer.address.city`); provide methods that do the work ("tell, don't ask"); avoid exposing internal collections (return tuples/copies or read-only views); keep invariants inside.
- **Coupling & cohesion**: constructor injection of collaborators (clock, repository, HTTP client, notifier) through small Protocols (Module 1.8 lesson 05); avoid global state/singletons; avoid circular dependencies between classes/modules (`import-linter`).
- **Inheritance review** (lesson 10): is-a really true? shallow? contract tests? `super()` chaining correct? Liskov respected? Prefer composition when behaviour varies by configuration.
- **State & lifecycle**: explicit states (enum + transition table, Module 1.9 lesson 06); valid transitions enforced; resource management (context manager, `close()`); no half-initialised objects; idempotent operations where retried.
- **Error handling**: domain exceptions, helpful messages, no swallowed errors; methods either succeed or leave the object unchanged (strong exception safety) where feasible; validation at boundaries.
- **Mutability policy**: prefer immutable value objects; if mutable, limit mutators, document thread-safety; avoid aliasing bugs (defensive copies on input/output of mutable containers).
- **Testing design**: depends on abstractions → easy fakes; no need for heavy mocking; deterministic (injected clock/random); avoid testing private methods; use builders/factories for test data.
- **Dataclass vs class**: use dataclass for data-centric types; add behaviour methods sparingly; use `frozen=True` for value objects, `slots=True` for memory (Module 1.15 lesson 07).
- **Common refactorings** (Module 1.23 lesson 03): Extract Class, Move Method, Replace Primitive with Object, Replace Inheritance with Delegation, Introduce Parameter Object, Replace Conditional with Polymorphism/Strategy, Encapsulate Collection, Hide Delegate, Remove Middle Man.

### Advanced — what to learn (level 3)

- **Domain modelling**: entities (identity, lifecycle) vs value objects (immutable, equality by value) vs aggregates (consistency boundaries) vs services (stateless operations) vs repositories/ports (persistence abstractions) — lightweight DDD vocabulary in Python; avoid over-engineering for small scripts.
- **Anemic vs rich models**: where should rules live? Balance: invariants and core rules inside entities/value objects; orchestration in services; I/O in adapters (functional core / imperative shell — Module 1.8 lesson 07).
- **Concurrency & async**: thread-safety of shared mutable objects (locks, immutability, confinement), async methods and resource cleanup (`async with`, cancellation safety), avoiding blocking calls in async methods.
- **Performance & memory**: instance count considerations (`__slots__`, dataclass slots, columnar structures instead of millions of small objects — Module 1.11 lesson 07; Stage 2), object pooling, lazy attributes (`cached_property`), avoiding repeated heavy `__post_init__` work.
- **Evolution**: public vs private surface, deprecations (Module 1.20 lesson 07), versioned serialisation (`schema_version`), backwards-compatible constructors (keyword-only additions), protocols to decouple from concrete classes, plugin extension points (Module 1.20 lesson 05).
- **Typing sophistication**: `Protocol`s for collaborators, `Self`, generics with bounds, `@final`/`@override`, `Literal`/`Enum` state types, `TypedDict`/dataclass for DTOs at boundaries, Pydantic models at I/O edges (Stage 2/7).
- **ML/AI-flavoured classes**: estimators/transformers with `fit/transform` contracts (no work in `__init__`, parameters stored as given, learned state with trailing underscore), dataset classes (`__len__`/`__getitem__`), `nn.Module` subclasses (`super().__init__()`), config objects (frozen dataclass/Pydantic) separate from runtime state, tool/agent classes with schemas, prompt templates as value objects; keep experiment code reproducible and serialisable.
- **Architecture-level review**: layers and dependency direction, module cohesion, circular imports, boundary objects; use dependency graphs and metrics (lines per class, methods per class, coupling) as prompts for discussion, not rules.
- **Review tooling**: Ruff rule families (`PLR0904` too many public methods, `PLR0902` too many instance attributes, `PLR0913` arguments, `C901`, `SLF001` private access, `D`, `ANN`), `pylint` design checks, `radon`, `import-linter`, `mypy --strict`, `vulture`; set thresholds with a "ratchet" so legacy code doesn't block progress.
- **Pair/mob design sessions**: CRC cards (Class–Responsibility–Collaborator) to model before coding; sketch interactions; test-drive the API from the caller's viewpoint.
- Exercise: take a class (≥ 200 lines) from an earlier Stage 1 project or open source, score it against the 20-item checklist, draw its collaborators, then refactor in ≥ 8 small commits (extract class, inject collaborators via Protocols, move method, replace primitives with value objects, remove inheritance misuse, add tests), measuring complexity and coupling before/after; write the review note and an ADR for any non-obvious design decision.
- Capstone for the module: **Stage 1 consolidation review** — pick any one Stage 1 project (`00-Stage-1-Overview/Projects/`) and produce a joint *function + class* design review document with metrics, prioritised findings, completed refactorings and remaining recommendations; present it as if to a team lead.

### Common mistakes

- Classes named `Manager`/`Handler` that accumulate unrelated methods.
- Public mutable attributes that let outside code break invariants.
- Reaching for inheritance (or a new class) as the default tool.

### Self-check

1. Apply the checklist to a class you wrote earlier and list the three highest-impact fixes.
2. Show how to replace a subclass-per-variant design with composition and a registry.
3. Define the invariants of a `Job` class and write tests that try to violate them through its public API.

---

## 4. Practice questions (`practice-questions.md`)

About **40 questions** (functions 20, classes 20):

| Phase | Question types |
| --- | --- |
| A | Predict output for closures/`nonlocal`/loop-lambdas; fix late-binding bugs; dispatch-table refactors |
| B | Choose `map`/comprehension/`reduce`/`key` forms; multi-key sorting; pick function vs `partial` vs closure vs callable class |
| C | Trace object construction (`__new__`/`__init__`); alternative constructors; spot missing `super().__init__()`; Liskov examples |
| D | Score and refactor given functions/classes with the checklists; write review comments |

Include 8 **"what does this print?"** items (closure counters, loop lambdas, mutable defaults, class attribute shadowing, `__init__` return, `super()` order, bound-method identity, `copy` vs `__init__`).

---

## 5. Module mini-project

**Build `gapcheck`**, a tiny library plus tests and a review report that exercises everything in this module:

1. `gapcheck.functional`: `compose`, `pipe`, `once`, `memoize` (closure-based), `bind_loop(fn, values)` (late-binding-safe callback factory), `top_k(items, k, key=…)`, with type hints and tests (including loop-capture regression tests).
2. `gapcheck.callables`: a `RetryPolicy` callable class, a `RateLimiter` callable class with injectable clock, and `partial`-based adapters; tests with fake clocks.
3. `gapcheck.model`: `Money` (value object), `Account` + `SavingsAccount` (constructor chaining, template method, contract tests), `Celsius(float)` using `__new__`, `Config` with `from_env/from_dict` alternative constructors.
4. A **design review document** (`REVIEW.md`) applying the function checklist (lesson 07) and class checklist (lesson 11) to two functions and two classes from earlier Stage 1 projects, with before/after code and metrics.
5. CI configuration (Ruff with `B023`, `E731`, `PLR`, `C901`, `FBT`; mypy strict on `gapcheck`; pytest with ≥ 90 % branch coverage).

Acceptance: all tests pass; all lint/type checks pass; each late-binding and construction pitfall has a failing-then-passing test; the review document contains concrete, actionable findings with commits showing the fixes.

---

## 6. Completion checklist

- [ ] I can use functions as values (pass, return, store, dispatch) and type them with `Callable`/`Protocol`.
- [ ] I can write lambdas where appropriate and replace them with better tools when not.
- [ ] I can explain closures, cells and `nonlocal`, and diagnose/fix late-binding bugs.
- [ ] I can pick between `map`/`filter`/`reduce`, comprehensions, `sum`/`any`/`all`, and `key=` functions.
- [ ] I can design callable objects and choose among function, `partial`, closure and callable class.
- [ ] I can review and refactor a function with a concrete checklist.
- [ ] I can build classes from first principles with correct attributes, methods, equality and representation.
- [ ] I can explain `__new__` vs `__init__`, write alternative constructors and keep constructors light.
- [ ] I can use inheritance and `super()` correctly for constructor chaining and know when to prefer composition.
- [ ] I can review and refactor a class with a concrete checklist.
- [ ] I completed the `gapcheck` mini-project.

**Next:** Return to **Module 1.11 — Advanced Python Data Model and Object Design** if you took this module before it, or proceed to **Stage 2 — Python for Data Engineering** if you have completed Modules 1.11–1.23 in numeric order.
