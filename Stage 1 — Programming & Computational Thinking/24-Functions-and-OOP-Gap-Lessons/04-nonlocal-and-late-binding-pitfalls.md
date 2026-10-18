# Nonlocal and Late-Binding Pitfalls

> **Target:** Python 3.12+  
> **Audience:** Learners who can define functions, use collections, and read basic closures; data engineers building callbacks, pipeline helpers, and reliable asynchronous or threaded work.  
> **Purpose:** Explain why assignment changes name resolution, how closures retain access to variables rather than snapshotting values, and how to make deferred behavior correct and testable.

## Learning objectives

By the end of this lesson, you should be able to:

- Explain why reading an enclosing variable usually works while assigning to that name creates a local binding unless declared `nonlocal` or `global`.
- Diagnose `UnboundLocalError` using Python's compile-time local-name classification.
- Distinguish rebinding a name from mutating the object to which it refers; explain why `+=` is still assignment syntax.
- Use `nonlocal` and `global` within their exact rules and identify when shared state is a design smell.
- Predict late-binding behavior for lambdas and nested functions created in loops, including the classic `[2, 2, 2]` result.
- Choose among default-argument binding, `functools.partial`, a callback factory, explicit arguments, and a small state class.
- Avoid callback timing bugs in GUI-style handlers, scheduled jobs, threads, asynchronous tasks, and deferred operations.
- Contrast closure lookup at call time with default-argument evaluation at function-definition time, including the mutable-default trap.
- Explain class-body scope, comprehension scope, and assignment-expression (`:=`) behavior relevant to closures.
- Inspect name classification with `symtable` and bytecode with `dis`, apply Ruff rules such as `B023`, and write regression tests that lock in intended callback values.

## Prerequisites and placement in the module

This lesson follows **Lesson 01 — First-Class Functions and Callables**, **Lesson 02 — Lambda Expressions and When Not to Use Them**, and **Lesson 03 — Closures and Captured Variables**. It assumes familiarity with function calls, parameters, mutable objects, LEGB lookup, and basic closure syntax. Lesson 03 introduced free variables and closure cells; this lesson uses those ideas to diagnose scope and deferred-execution bugs rather than repeating closure mechanics from first principles.

The module roadmap identifies the central failure modes: `UnboundLocalError`, counters that fail to increment, and callbacks that all observe the final loop value. The goal is to make these behaviors predictable and testable. Advanced topics such as descriptors and garbage-collection details belong in their dedicated modules and are not developed here.

---

## 1. The first rule: reading is not assigning

### Bug first: a read followed by an assignment

```python
def make_adder():
    total = 10

    def add(amount):
        print("before:", total)
        total += amount
        return total

    return add

add = make_adder()
add(5)
```

**Expected behavior:** the call raises `UnboundLocalError` before printing `before:`. The exact exception message can vary by Python version, but it typically says that the local variable `total` was referenced before assignment.

**Why it fails:** Python analyzes each function body when compiling it. Since `total` is assigned in `add` by `total += amount`, Python classifies `total` as a local name throughout `add`. The `print(total)` expression therefore tries to read that local before it has been initialized. The enclosing `total` is not consulted for that name inside `add`.

This is not a runtime rule that changes depending on which line runs first. It is a consequence of compile-time name classification.

### Correct it with `nonlocal`

```python
def make_adder():
    total = 10

    def add(amount):
        nonlocal total
        print("before:", total)
        total += amount
        return total

    return add

add = make_adder()
print(add(5))
print(add(2))
```

**Expected output:**

```text
before: 10
15
before: 15
17
```

`nonlocal total` says that assignments to `total` in `add` target an existing binding in the nearest enclosing **function** scope that contains that name. The inner function updates the same binding on each call.

### Reading, rebinding, and mutation are different operations

| Operation | Example | Does it rebind the name? | Scope consequence |
|---|---|---:|---|
| Read | `print(total)` | No | An enclosing binding can be read through normal name lookup. |
| Rebind | `total = total + amount` | Yes | `total` is local unless declared `nonlocal` or `global`. |
| Augmented assignment | `total += amount` | Yes | It is an assignment operation and triggers the same local-name classification. |
| Mutate an object | `items.append(value)` | No | The existing name still refers to the same list; no `nonlocal` is needed just to mutate it. |
| Mutate through a subscript | `counts[key] += 1` | No rebinding of `counts` | The object is changed; the name `counts` is only read to find the object. |

An augmented assignment may call an in-place operation on an object, but it is still an assignment statement for name-binding purposes. For immutable values such as integers, `x += 1` normally produces a new integer and binds `x` to it. For mutable objects, `x += ...` may mutate in place, but `x` is still classified as local if that statement occurs in a function without a scope declaration.

### Mutation works without `nonlocal` — but understand the design

```python
def make_counter():
    state = {"value": 0}

    def increment():
        state["value"] += 1
        return state["value"]

    return increment

counter = make_counter()
print(counter())
print(counter())
```

**Expected output:**

```text
1
2
```

The inner function does not assign a new object to the name `state`; it reads the existing dictionary and mutates one of its entries. That is why `nonlocal state` is unnecessary. This can be useful when a small mutable record is the clearest representation, but do not use a dictionary merely to evade a scope declaration. A `nonlocal` integer often communicates the intended state transition more directly.

### A list example: mutation versus rebinding

```python
def build_examples():
    values = []

    def append_value(value):
        values.append(value)  # mutation; valid without nonlocal

    def replace_values():
        nonlocal values
        values = ["replacement"]  # rebinding; requires nonlocal

    return values, append_value, replace_values

values, append_value, replace_values = build_examples()
append_value("first")
print(values)
replace_values()
print(values)
```

**Expected output:**

```text
['first']
['first']
```

The returned `values` variable and the closure initially refer to the same list. `replace_values()` rebinds the closure's `values` cell to a new list, but the outer local variable returned by `build_examples()` still refers to the original list. This is a useful reminder that rebinding a name does not retroactively change every other reference to the old object.

---

## 2. `nonlocal` and `global`: precise rules

### `nonlocal`: update a binding in an enclosing function

Use `nonlocal` when a nested function must rebind a name owned by an enclosing function.

```python
def make_sequence(start=0):
    current = start

    def next_value():
        nonlocal current
        current += 1
        return current

    return next_value

next_id = make_sequence(40)
print(next_id())
print(next_id())
```

**Expected output:**

```text
41
42
```

Rules and limits:

1. The name must already be bound in an enclosing **function** scope.
2. The module/global scope does not satisfy `nonlocal`.
3. A `nonlocal` declaration must appear before the name is used or assigned in that function body.
4. It does not create a new enclosing variable. It selects an existing binding.
5. The nearest enclosing function scope containing the name is selected.
6. It cannot be used at module level.

This is invalid because `rate` exists only at module scope, not in an enclosing function scope:

```python
rate = 0.1

def invalid():
    nonlocal rate  # SyntaxError: no binding for nonlocal 'rate' found
```

### `global`: update a module-level binding

`global` tells Python that assignments to the declared name target the module's global namespace.

```python
retry_count = 0

def record_retry():
    global retry_count
    retry_count += 1
    return retry_count

print(record_retry())
print(record_retry())
```

**Expected output:**

```text
1
2
```

`global` is valid inside a function even if the module-level name is not yet bound; the name will be looked up or assigned in the module namespace when the function runs. But it is not a way to refer to a caller's local variable, nor does it mean “process-wide shared state” across separate Python interpreters. In concurrent code, shared global state also needs a synchronization and lifecycle design.

Prefer explicit dependencies, returned state, closures, or small state objects for ordinary application behavior. Module-level state can be appropriate for deliberately process-wide configuration or carefully managed registries, but it creates hidden coupling and makes isolated tests harder.

### Side-by-side comparison

| Intent | Declaration | Binding selected | Typical use |
|---|---|---|---|
| Read an enclosing value | None | Normal lexical lookup | Read configuration captured by a factory. |
| Rebind a name owned by a surrounding function | `nonlocal name` | Nearest enclosing function binding | Closure counter, small stateful decorator. |
| Rebind a module-level name | `global name` | Module namespace | Explicitly module-scoped state (use sparingly). |
| Mutate a captured list/dict/object | Usually none | Same object, no name rebinding | Append to a queue or update a field in a captured state object. |
| Pass state explicitly | No declaration | Function parameter/local | Often best for pipeline transformations and testable business logic. |

---

## 3. Late binding: closures retain access, not a snapshot

A closure can keep access to a variable in an enclosing scope after the outer function has returned. That does **not** mean it freezes the variable's current value. When the inner function is called, it resolves the free variable through the retained binding.

### Bug first: loop-created lambdas

```python
callbacks = [lambda: i for i in range(3)]
print([callback() for callback in callbacks])
```

**Expected output:**

```text
[2, 2, 2]
```

**Why:** each lambda refers to the same loop variable binding `i` in the comprehension's implicit scope. The calls happen after the comprehension has finished, by which time `i` is bound to `2`. The lambdas do not store a separate snapshot for each iteration.

In Python 3, a comprehension has its own scope, so this particular `i` does not leak into the surrounding module/function scope. That scope isolation does not create a fresh `i` binding for each iteration. All three lambdas still share the comprehension's binding.

### Nested `def` has the same problem

```python
def make_callbacks():
    callbacks = []
    for i in range(3):
        def callback():
            return i
        callbacks.append(callback)
    return callbacks

print([callback() for callback in make_callbacks()])
```

**Expected output:**

```text
[2, 2, 2]
```

The syntax is different, but the name lookup behavior is the same. Defining a nested function in a loop does not automatically create a new lexical scope per iteration.

### Scope diagram

```text
make_callbacks / comprehension scope
┌──────────────────────────────────────────┐
│ i ──> 0, then 1, then 2                  │
│                                          │
│ callback_0 ─┐                            │
│ callback_1 ─┼── all resolve the same i ──┘
│ callback_2 ─┘
└──────────────────────────────────────────┘
After the loop, every callback reads i == 2.
```

The important question is not “what value did this function see when it was created?” It is “which binding will this function look up when it eventually runs?”

---

## 4. Three principal fixes and their trade-offs

### Fix A — bind the value in a default argument

```python
callbacks = [lambda i=i: i for i in range(3)]
print([callback() for callback in callbacks])
```

**Expected output:**

```text
[0, 1, 2]
```

The default expression `i` is evaluated each time the lambda object is created. Each lambda stores its own default value in `__defaults__`, so the function body uses that parameter rather than the changing outer binding.

**Trade-off:** compact and idiomatic for tiny callbacks. However, the lambda's public call signature now has a parameter named `i`; a caller can override it with `callback(99)`. That may be harmless for a private zero-argument callback, but can be surprising if the function is exposed or type-checked as part of an API. For longer logic, use a named factory.

A nested function can use the same pattern:

```python
def make_callbacks():
    callbacks = []
    for i in range(3):
        def callback(i=i):
            return i
        callbacks.append(callback)
    return callbacks

print([callback() for callback in make_callbacks()])
```

**Expected output:** `[0, 1, 2]`

### Fix B — bind arguments with `functools.partial`

```python
from functools import partial

def identify(index):
    return index

callbacks = [partial(identify, i) for i in range(3)]
print([callback() for callback in callbacks])
```

**Expected output:**

```text
[0, 1, 2]
```

`partial(identify, i)` creates a callable that will call `identify(i)` later. The integer argument is stored in the partial object when it is created, so it is not looked up from the loop variable at invocation time.

**Trade-off:** explicit, reusable, and usually clearer than an opaque lambda when binding arguments to an existing function. It preserves the original function as `partial.func` and exposes bound arguments through `partial.args`/`partial.keywords`. The resulting signature may be less obvious to some readers, and `partial` is not a universal substitute for a factory when each callback needs custom logic or state initialization.

### Fix C — use a factory function to create a separate scope

```python
def make_callback(index):
    def callback():
        return index
    return callback

callbacks = [make_callback(i) for i in range(3)]
print([callback() for callback in callbacks])
```

**Expected output:**

```text
[0, 1, 2]
```

Every call to `make_callback` creates a new invocation scope with its own `index` binding. Each returned closure retains access to its own binding.

**Trade-off:** the intent is explicit, and the factory can validate inputs, name callbacks, capture multiple dependencies, or add documentation. It adds a few lines and one helper function, but is often the most maintainable choice for nontrivial callbacks.

### Comparison table

| Pattern | Readability | Signature / API impact | Testability | Best fit |
|---|---|---|---|---|
| Default argument (`lambda i=i: ...`) | Very concise; can look like a trick | Adds a parameter that callers can override | Easy to test, but inspect the callable's intended contract | Tiny private callback with a simple captured scalar. |
| `partial(fn, value)` | Clear when binding an existing function | Binds arguments to the original function; inspect with care | Very good; the underlying function can be tested directly | Existing function plus fixed positional/keyword arguments. |
| Factory (`make_callback(value)`) | Most explicit for richer behavior | Returned callback can remain zero-argument | Excellent; factory and callback behavior can be tested separately | Validation, multiple captured values, logging, state, or nontrivial logic. |
| Explicit callback arguments | Usually clearest overall | Moves the value to the call site / framework contract | Excellent; dependencies are visible | When the caller/framework lets you pass the value at invocation time. |
| Small state class | More structure, but named state | Methods make state transitions explicit | Excellent for complex invariants and multiple operations | Several related methods, validation, lifecycle, or shared mutable state. |

### Prefer explicit arguments when the API supports them

If the framework already calls a callback with the event or job context, use that contract rather than capturing a loop variable unnecessarily. For example, `def on_click(event, index): ...` is only useful if the GUI framework or a binding layer will actually provide `index`; otherwise a factory or `partial` is required. Always check the framework's callback signature before choosing a pattern.

### Defensive callback factory

```python
def make_partition_callback(partition_id, process_partition):
    """Return a zero-argument callback for one partition."""
    if not isinstance(partition_id, str) or not partition_id:
        raise ValueError("partition_id must be a non-empty string")

    def callback():
        return process_partition(partition_id)

    return callback


def process_partition(partition_id):
    return f"processed:{partition_id}"

callbacks = [
    make_partition_callback(partition_id, process_partition)
    for partition_id in ("north", "south", "west")
]
print([callback() for callback in callbacks])
```

**Expected output:**

```text
['processed:north', 'processed:south', 'processed:west']
```

The factory validates the captured input and produces a stable zero-argument callable. In a production pipeline, the injected `process_partition` dependency also makes the callback easy to test with a fake function. Do not overbuild a factory for a one-line private callback; choose the simplest form that keeps the binding obvious.

---

## 5. Callback timing in real code

Late binding becomes operationally important when creation and execution are separated. A callback may be created now but run after a loop, a UI event, a timer, a thread start, or an asynchronous suspension point.

### GUI-style callback registration

#### Bug

```python
buttons = []
for label in ("Load", "Validate", "Publish"):
    buttons.append((label, lambda: print("clicked", label)))

for _, handler in buttons:
    handler()
```

**Expected output:**

```text
clicked Publish
clicked Publish
clicked Publish
```

#### Corrected with a factory

```python
def make_click_handler(label):
    def on_click():
        print("clicked", label)
    return on_click

buttons = [
    (label, make_click_handler(label))
    for label in ("Load", "Validate", "Publish")
]

for _, handler in buttons:
    handler()
```

**Expected output:**

```text
clicked Load
clicked Validate
clicked Publish
```

A real GUI toolkit may pass an event object to handlers. Adapt the function signature to that toolkit's documented contract; the binding principle is unchanged.

### Scheduled jobs and timers

#### Bug: create jobs in a loop, run them after the loop

```python
from threading import Timer

seen = []
timers = []
for job_id in range(3):
    timers.append(Timer(0.01, lambda: seen.append(job_id)))

for timer in timers:
    timer.start()
for timer in timers:
    timer.join()

print(seen)
```

**Expected output:** the list contains three `2` values, though thread scheduling may change their order relative to one another: `[2, 2, 2]`.

#### Corrected with `partial`

```python
from functools import partial
from threading import Timer

seen = []
timers = [Timer(0.01, partial(seen.append, job_id)) for job_id in range(3)]
for timer in timers:
    timer.start()
for timer in timers:
    timer.join()

print(sorted(seen))
```

**Expected output:**

```text
[0, 1, 2]
```

For a production scheduler, prefer passing job identity as explicit data to the scheduler if supported. Timers are useful to demonstrate deferred execution, but they are not a durable job queue and should not be used as one in a production data platform.

### Threads: bind the target argument before starting

#### Bug

```python
from threading import Thread

results = []
threads = []
for partition in range(3):
    threads.append(Thread(target=lambda: results.append(partition)))

for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(sorted(results))
```

**Expected output:**

```text
[2, 2, 2]
```

The loop finishes before the worker threads are guaranteed to execute the lambda. Each lambda reads the same final `partition` binding. The GIL does not make late binding disappear, and thread scheduling is not a reliable way to capture values.

#### Corrected with a direct target and arguments

```python
from threading import Thread

results = []
threads = [Thread(target=results.append, args=(partition,)) for partition in range(3)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(sorted(results))
```

**Expected output:**

```text
[0, 1, 2]
```

`Thread` accepts `target` and `args`; use that interface rather than wrapping the call in a closure. For more involved work, define a named worker function and pass its arguments explicitly. If multiple threads update a non-thread-safe shared object, argument binding alone does not solve the separate synchronization problem.

### Async tasks: a coroutine can execute after the loop advances

The following example uses `asyncio` only to show callback timing; it is not a general asynchronous-programming tutorial.

#### Bug

```python
import asyncio

async def main():
    tasks = []
    for partition in range(3):
        async def worker():
            await asyncio.sleep(0)
            return partition
        tasks.append(asyncio.create_task(worker()))
    print(await asyncio.gather(*tasks))

asyncio.run(main())
```

**Expected output:**

```text
[2, 2, 2]
```

Each `worker` function closes over the same `partition` variable in `main`. Task creation schedules execution; it does not snapshot free variables. By the time the workers resume after `await`, the loop has finished and `partition` is `2`.

#### Corrected by binding a parameter at each function definition

```python
import asyncio

async def main():
    tasks = []
    for partition in range(3):
        async def worker(partition=partition):
            await asyncio.sleep(0)
            return partition
        tasks.append(asyncio.create_task(worker()))
    print(await asyncio.gather(*tasks))

asyncio.run(main())
```

**Expected output:**

```text
[0, 1, 2]
```

The default value is evaluated when each `worker` function object is created, so each call to `worker()` creates a coroutine with that invocation's bound argument. An equally clear alternative is a module-level `async def worker(partition): ...` and `asyncio.create_task(worker(partition))`, which makes the input explicit and avoids a nested function entirely.

### Event-loop callbacks: `call_later` also defers execution

```python
import asyncio

async def main():
    loop = asyncio.get_running_loop()
    seen = []
    finished = asyncio.Event()

    def mark_finished():
        finished.set()

    for partition in range(3):
        loop.call_later(0, lambda: seen.append(partition))
    loop.call_later(0, mark_finished)
    await finished.wait()
    print(seen)

asyncio.run(main())
```

**Expected output:**

```text
[2, 2, 2]
```

The event-loop callbacks run after the loop has advanced. Bind the callback argument through the event-loop API when possible:

```python
import asyncio

async def main():
    loop = asyncio.get_running_loop()
    seen = []
    finished = asyncio.Event()

    def mark_finished():
        finished.set()

    for partition in range(3):
        loop.call_later(0, seen.append, partition)
    loop.call_later(0, mark_finished)
    await finished.wait()
    print(sorted(seen))

asyncio.run(main())
```

**Expected output:**

```text
[0, 1, 2]
```

`loop.call_later(delay, callback, *args)` passes the supplied arguments to the callback at invocation time, avoiding the closure entirely. The same binding concern applies when scheduling callbacks with `loop.call_soon`, adding task done-callbacks, or creating tasks inside an `asyncio.TaskGroup`; prefer explicit callback arguments or `worker(partition)` when the API supports them.

### `asyncio.TaskGroup` does not create a fresh closure scope

`TaskGroup` manages task lifetime and failure propagation; it does not snapshot free variables in a nested function.

```python
import asyncio

async def main():
    results = []
    async with asyncio.TaskGroup() as group:
        for partition in range(3):
            async def worker():
                await asyncio.sleep(0)
                results.append(partition)
            group.create_task(worker())
    print(results)

asyncio.run(main())
```

**Expected output:**

```text
[2, 2, 2]
```

Pass the partition as an argument instead:

```python
import asyncio

async def worker(partition, results):
    await asyncio.sleep(0)
    results.append(partition)

async def main():
    results = []
    async with asyncio.TaskGroup() as group:
        for partition in range(3):
            group.create_task(worker(partition, results))
    print(sorted(results))

asyncio.run(main())
```

**Expected output:**

```text
[0, 1, 2]
```

This is the same lexical-binding issue as `create_task`; the task-group API improves structured concurrency, not closure capture semantics.

### Deferred operations and query builders

The same pitfall can affect deferred predicates, lazy transformations, query callbacks, and test helpers.

```python
predicates = []
for column in ("country", "region", "status"):
    predicates.append(lambda row: row[column] == "ready")

row = {"country": "ready", "region": "ready", "status": "ready"}
print([predicate(row) for predicate in predicates])
```

**Expected output:**

```text
[True, True, True]
```

This data does not expose the bug because all three fields have the same value. Use contrasting test data to prove that each predicate uses the intended column:

```python
predicates = []
for column in ("country", "region", "status"):
    predicates.append(lambda row: row[column] == "ready")

row = {"country": "ready", "region": "blocked", "status": "ready"}
print([predicate(row) for predicate in predicates])
```

**Actual output:**

```text
[True, True, True]
```

That output is misleading: every predicate checks `status`, which is `ready`. If each predicate checked its intended column, the result would be `[True, False, True]`. A regression test must use contrasting values and assert the intended key per callback. See the test section below. When a query library supports structured expressions or explicit bound parameters, prefer those over ad hoc closures.

---

## 6. Closures bind late; defaults bind early

The two mechanisms have opposite timing rules:

- A closure's free variable is looked up through its retained binding when the function executes.
- A function's default argument expressions are evaluated once when the `def` statement executes, creating that function object.

### Default arguments freeze the reference/value at definition time

```python
def make_reader():
    value = "first"
    def read(snapshot=value):
        return snapshot
    value = "second"
    return read

reader = make_reader()
print(reader())
```

**Expected output:**

```text
first
```

The default stores the object reference bound to `value` when `read` was defined. For immutable strings and integers, this often looks like a value snapshot. For mutable objects, it stores a reference to the same object, not a deep copy.

### Mutable default argument trap

#### Bug

```python
def collect(value, items=[]):
    items.append(value)
    return items

print(collect("a"))
print(collect("b"))
```

**Expected output:**

```text
['a']
['a', 'b']
```

The list is created once when `def collect` executes and reused on every call that omits `items`.

#### Corrected with a `None` sentinel

```python
def collect(value, items=None):
    if items is None:
        items = []
    items.append(value)
    return items

print(collect("a"))
print(collect("b"))
```

**Expected output:**

```text
['a']
['b']
```

This pattern creates a fresh list per call while still allowing callers to supply their own list. It is different from the intentional `lambda i=i` callback fix: that default deliberately binds a loop value; a mutable default such as `items=[]` often accidentally shares state.

| Mechanism | When is the name/value selected? | Does it make a mutable object copy? |
|---|---|---|
| Closure free variable | When the function reads the retained binding during a call | No |
| Default argument | When the function definition executes | No; the object reference is stored |
| `partial(fn, value)` | When the partial object is created, it stores the supplied argument reference/value | No |
| Factory parameter | Each factory call creates a separate local binding | No automatic deep copy; objects passed in can still be shared |

---

## 7. Class bodies are not enclosing scopes for methods

A class body executes in a namespace used to build the class, but that namespace is not a lexical enclosing function scope for methods defined in the class.

### Bug first

```python
prefix = "module"

class Reporter:
    prefix = "class"

    def report(self):
        return prefix

print(Reporter().report())
```

**Expected output:**

```text
module
```

`report` resolves the unqualified name `prefix` using the function's normal lexical/global lookup. It does not search `Reporter`'s class namespace. Since the module has a global `prefix`, that is what the method returns.

### Corrected: access the intended attribute

```python
class Reporter:
    prefix = "class"

    def report(self):
        return self.prefix

print(Reporter().report())
```

**Expected output:**

```text
class
```

Use `self.prefix` for instance lookup, `type(self).prefix` or `Reporter.prefix` when class-level access is intended, and explicit parameters when the value is per-call data. Be careful with `Reporter.prefix` if subclasses are meant to override the attribute; `type(self).prefix` respects the runtime class.

This rule is distinct from a closure nested inside a method: nested functions can close over the method's local variables, but methods do not lexically close over the class body's namespace.

---

## 8. Comprehension scope and `:=`

### The iteration variable does not leak in Python 3

```python
values = [number * 2 for number in range(3)]
print(values)
print("number" in globals())
```

**Expected output:**

```text
[0, 2, 4]
False
```

A comprehension's iteration variable is scoped to the comprehension. Python 3.12's comprehension implementation may optimize the execution strategy, but the observable scope rule remains: the iteration variable does not leak into the surrounding scope.

### Assignment expression target behaves differently

```python
values = [captured := number * 2 for number in range(3)]
print(values)
print(captured)
```

**Expected output:**

```text
[0, 2, 4]
4
```

The target of `:=` in a comprehension binds in the containing scope (with specific restrictions), rather than in the comprehension's iteration-variable scope. This is an intentional exception to the intuition that every name written inside a comprehension is isolated.

### A `:=` target can itself be captured late

```python
callbacks = [(lambda: captured) for number in range(3) if (captured := number)]
print([callback() for callback in callbacks])
```

**Expected output:**

```text
[2, 2]
```

The filter runs for `number == 1` and `number == 2`, assigning `captured` in the containing scope. Both lambdas refer to that same `captured` binding, which is `2` after the comprehension finishes. The result is intentionally subtle; avoid this combination in production code unless there is a compelling reason and explicit tests.

### Class-body comprehensions cannot resolve class-local names

A comprehension has its own execution scope. A class namespace is not an enclosing lexical scope for that comprehension, so a name assigned earlier in the class body is not available to the comprehension as an unqualified local name.

```python
class Scale:
    factor = 10
    values = [factor * number for number in range(3)]
```

**Actual behavior:** class creation raises `NameError` because the comprehension cannot resolve `factor` from the class namespace. It may resolve a same-named module global if one exists, which can make this bug especially confusing.

A clear fix is to perform the calculation in a method after the class has been created:

```python
class Scale:
    factor = 10

    @classmethod
    def values(cls):
        return [cls.factor * number for number in range(3)]

print(Scale.values())
```

**Expected output:**

```text
[0, 10, 20]
```

This is distinct from a method's unqualified global lookup and from the special containing-scope rule for a comprehension's `:=` target.

Relevant restrictions: assignment expressions cannot rebind a comprehension's iteration variable, a `:=` expression is prohibited in the iterable expression of a comprehension, and assignment expressions inside comprehensions are prohibited in a class body. That last restriction exists because the comprehension's nested scope cannot assign its target into the class namespace. The rules around `:=` in comprehensions are specific enough that complex use should be rewritten into an ordinary loop for clarity.

---

## 9. Inspect the compiler's decisions with `symtable` and `dis`

These tools help explain the behavior rather than relying on intuition. The symbol table reports how names are classified by the compiler; `dis` shows the bytecode emitted by the running Python implementation.

### `symtable`: local, free, global, and cell concepts

```python
import symtable

source = '''
def outer():
    value = 10
    def inner(amount):
        nonlocal value
        value += amount
        return len(str(value))
    return inner
'''

top = symtable.symtable(source, "<example>", "exec")
outer_table = next(child for child in top.get_children() if child.get_name() == "outer")
inner_table = next(child for child in outer_table.get_children() if child.get_name() == "inner")

for name in ("value", "inner"):
    symbol = outer_table.lookup(name)
    print("outer", name, "local=", symbol.is_local(), "referenced=", symbol.is_referenced())
for name in ("value", "amount", "len"):
    symbol = inner_table.lookup(name)
    print("inner", name, "local=", symbol.is_local(), "free=", symbol.is_free(), "global=", symbol.is_global(), "parameter=", symbol.is_parameter())
```

**Expected classifications (formatting follows the `print` calls):**

- In `outer`, `value` is local to `outer`; the nested function uses it, so it is conceptually a **cell variable** in `outer`.
- In `inner`, `value` is a **free variable** and is declared nonlocal; `amount` is a local parameter; `len` is global/built-in lookup (the symbol table reports it as global, not as a local/free variable).
- `inner` is a local name in `outer`.

`Symbol.is_free()` and `Symbol.is_local()` are public APIs; a cell variable is inferred from the relationship between the outer and inner symbol tables. Do not depend on a `Symbol.is_cell()` method for Python 3.12 compatibility. The symbol table API is documented, but exact helper methods can vary by Python version.

### `dis`: inspect closure access

```python
import dis

def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter = make_counter()
print("freevars:", counter.__code__.co_freevars)
print("cellvars on increment:", counter.__code__.co_cellvars)
dis.dis(counter)
```

**Expected stable facts:**

```text
freevars: ('count',)
cellvars on increment: ()
```

The disassembly shows a closure-cell read/update sequence. In CPython versions commonly used with Python 3.12+, look for operations such as `COPY_FREE_VARS`, `LOAD_DEREF`, and `STORE_DEREF`; exact bytecode and offsets are implementation/version details and can change between releases. The inner function has `count` in `co_freevars`; the outer function that creates it would list `count` in its `co_cellvars`.

### Why `UnboundLocalError` is a compile-time classification issue

```python
import dis

def broken(value):
    print(value)
    value = 5

dis.dis(broken)
```

**Expected observation:** the disassembly uses a local-variable load for `value` before the local store. The function fails at runtime because that local slot has not yet been initialized. This demonstrates why the compiler does not fall back to a global or enclosing value for the earlier read.

Use `symtable` to answer “how did the compiler classify this name?” and `dis` to answer “what operations did this interpreter emit?” Avoid writing tests that require a particular complete disassembly string across Python versions.

---

## 10. Linting and static analysis

### Ruff: catch loop-variable binding mistakes

Ruff's `B023` rule (from the `flake8-bugbear` family) flags function definitions in loops that use a loop variable without binding it. It is directly relevant to late-binding callback bugs.

Example to lint:

```python
callbacks = []
for item in ("a", "b", "c"):
    callbacks.append(lambda: item)
```

Depending on the configured rule set and Ruff version, the diagnostic is associated with `B023` and explains that the function definition does not bind the loop variable. The rule can detect a common shape of bug, not every possible delayed-execution or shared-state defect.

Useful Ruff rules for this lesson:

- `B023` — function definition does not bind loop variable.
- `PLW0602` — global variable is not assigned (a `global` declaration that is unnecessary or misleading).
- `PLW0603` — use of the `global` statement; a useful review signal for hidden module state.
- `PLW0604` — `global` at module level (where it has no useful effect).
- `F823` — local variable referenced before assignment, useful for the `UnboundLocalError` pattern when enabled through the relevant rule set.

Rule availability depends on the Ruff version and selected rule families. `B023` requires enabling the `B` rules (or the specific rule); `PLW...` rules require enabling the `PL` family. Ruff does not prove callback correctness and does not replace tests.

A minimal `pyproject.toml` configuration for these checks is:

```toml
[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "B", "PL"]
```

This enables a broader set of style and bug-risk checks than this lesson alone requires. In a real repository, review the full rule set and exclusions instead of copying a broad configuration blindly. `mypy` or `pyright` can catch some statically evident possibly-unbound or type-contract issues, but neither is a general detector for Python's runtime late-binding semantics.

---

## 11. Regression tests: prove each callback keeps the intended value

The key regression principle is to test behavior after all callbacks have been created and after the loop has finished. A test that invokes each callback immediately inside the loop can pass while the deferred callback bug remains.

The following test module is self-contained apart from its test-runner dependency. Save it as `test_late_binding_pitfalls.py` and run `pytest -q` with `pytest` installed. A few tests intentionally assert the reproducible buggy behavior; paired tests assert the corrected behavior.

```python
from functools import partial
import asyncio
from threading import Event, Thread, Timer

import pytest


def buggy_callbacks():
    return [lambda: index for index in range(3)]


def callbacks_with_defaults():
    return [lambda index=index: index for index in range(3)]


def identify(index):
    return index


def callbacks_with_partial():
    return [partial(identify, index) for index in range(3)]


def make_callback(index):
    def callback():
        return index
    return callback


def callbacks_with_factory():
    return [make_callback(index) for index in range(3)]


def test_buggy_callbacks_demonstrate_late_binding():
    assert [callback() for callback in buggy_callbacks()] == [2, 2, 2]


def test_default_argument_fix_binds_each_index():
    assert [callback() for callback in callbacks_with_defaults()] == [0, 1, 2]


def test_partial_fix_binds_each_index():
    assert [callback() for callback in callbacks_with_partial()] == [0, 1, 2]


def test_factory_fix_creates_separate_bindings():
    assert [callback() for callback in callbacks_with_factory()] == [0, 1, 2]


def test_nonlocal_counter_updates_enclosing_binding():
    def make_counter():
        value = 0
        def increment():
            nonlocal value
            value += 1
            return value
        return increment

    counter = make_counter()
    assert [counter(), counter(), counter()] == [1, 2, 3]


def test_mutating_captured_dict_needs_no_nonlocal():
    def make_counter():
        state = {"value": 0}
        def increment():
            state["value"] += 1
            return state["value"]
        return increment

    counter = make_counter()
    assert [counter(), counter()] == [1, 2]


def test_gui_style_callbacks_bind_each_label():
    labels = ("Load", "Validate", "Publish")
    buggy = []
    for label in labels:
        buggy.append(lambda: label)
    assert [handler() for handler in buggy] == ["Publish", "Publish", "Publish"]

    fixed = [lambda label=label: label for label in labels]
    assert [handler() for handler in fixed] == ["Load", "Validate", "Publish"]


def test_thread_loop_closure_bug_is_deterministic_with_event_gate():
    release_workers = Event()
    results = []
    threads = []

    for partition in range(3):
        def worker():
            assert release_workers.wait(timeout=2)
            results.append(partition)
        threads.append(Thread(target=worker))

    for thread in threads:
        thread.start()
    release_workers.set()
    for thread in threads:
        thread.join(timeout=2)
        assert not thread.is_alive()

    assert sorted(results) == [2, 2, 2]


def test_timer_loop_closure_bug_is_deterministic_with_event_gate():
    release_callbacks = Event()
    results = []
    timers = []

    for job_id in range(3):
        def callback():
            assert release_callbacks.wait(timeout=2)
            results.append(job_id)
        timers.append(Timer(0.01, callback))

    for timer in timers:
        timer.start()
    release_callbacks.set()
    for timer in timers:
        timer.join(timeout=2)
        assert not timer.is_alive()

    assert sorted(results) == [2, 2, 2]


def test_timer_partial_binds_each_job_id():
    results = []
    timers = [Timer(0.01, partial(results.append, job_id)) for job_id in range(3)]
    for timer in timers:
        timer.start()
    for timer in timers:
        timer.join(timeout=2)
        assert not timer.is_alive()
    assert sorted(results) == [0, 1, 2]


def test_class_body_comprehension_cannot_see_class_local_name():
    source = "class Scale:\n    factor = 10\n    values = [factor * number for number in range(3)]\n"
    with pytest.raises(NameError, match="factor"):
        exec(source, {})


def test_assignment_expression_in_class_comprehension_is_rejected():
    source = "class Bad:\n    values = [(captured := number) for number in range(3)]\n"
    with pytest.raises(SyntaxError, match="class body"):
        compile(source, "<class-comprehension>", "exec")


def test_mutable_default_bug_reuses_the_same_list():
    def collect(value, items=[]):
        items.append(value)
        return items

    first = collect("a")
    second = collect("b")
    assert first is second
    assert second == ["a", "b"]


def test_default_argument_captures_reference_at_definition_time():
    def build():
        current = "first"
        def read(snapshot=current):
            return snapshot
        current = "second"
        return read

    assert build()() == "first"


def test_none_sentinel_prevents_mutable_default_leakage():
    def collect(value, items=None):
        if items is None:
            items = []
        items.append(value)
        return items

    assert collect("a") == ["a"]
    assert collect("b") == ["b"]


module_name = "module"


def test_class_method_does_not_lexically_capture_class_namespace():
    class Example:
        module_name = "class"
        def read(self):
            return module_name

    assert Example().read() == "module"


def test_comprehension_walrus_target_can_be_late_bound():
    callbacks = [
        (lambda: captured)
        for number in range(3)
        if (captured := number)
    ]
    assert [callback() for callback in callbacks] == [2, 2]


def test_async_tasks_capture_explicit_arguments():
    async def worker(partition):
        await asyncio.sleep(0)
        return partition

    async def run():
        tasks = [asyncio.create_task(worker(partition)) for partition in range(3)]
        return await asyncio.gather(*tasks)

    assert asyncio.run(run()) == [0, 1, 2]


def test_async_closure_bug_is_reproducible():
    async def run():
        tasks = []
        for partition in range(3):
            async def worker():
                await asyncio.sleep(0)
                return partition
            tasks.append(asyncio.create_task(worker()))
        return await asyncio.gather(*tasks)

    assert asyncio.run(run()) == [2, 2, 2]


def test_event_loop_callback_arguments_bind_each_partition():
    async def run():
        loop = asyncio.get_running_loop()
        results = []
        finished = asyncio.Event()
        for partition in range(3):
            loop.call_later(0, results.append, partition)
        loop.call_later(0, finished.set)
        await finished.wait()
        return sorted(results)

    assert asyncio.run(run()) == [0, 1, 2]


def test_task_group_does_not_fix_late_binding_but_arguments_do():
    async def run_buggy():
        results = []
        async with asyncio.TaskGroup() as group:
            for partition in range(3):
                async def worker():
                    await asyncio.sleep(0)
                    results.append(partition)
                group.create_task(worker())
        return results

    async def run_fixed():
        results = []
        async def worker(partition):
            await asyncio.sleep(0)
            results.append(partition)
        async with asyncio.TaskGroup() as group:
            for partition in range(3):
                group.create_task(worker(partition))
        return sorted(results)

    assert asyncio.run(run_buggy()) == [2, 2, 2]
    assert asyncio.run(run_fixed()) == [0, 1, 2]
```

### What these tests prove

- The test for the buggy callback intentionally asserts the bug's output so a reader can reproduce and understand the failure mode. In a production codebase, the regression test for a fixed behavior should assert the intended distinct values.
- The three fixes are tested independently. A future refactor that accidentally removes the binding should fail a test.
- The mutable-default example uses `None`, and the class-scope example distinguishes module-level and class-level names.
- The async test deliberately yields once so the tasks run after the loop has progressed. The explicit-argument version proves that arguments are bound at coroutine creation/call time rather than read from a shared outer variable.

For a real bug, first write a failing test against the incorrect behavior, implement the smallest correction, then keep a regression assertion for the intended behavior. Do not retain a test that blesses the bug as the only test of the feature.

### Thread callback regression test without timing assumptions

Use a deterministic unit test for binding logic whenever possible. If testing actual threads, synchronize the worker start so the loop completes before callbacks read the captured name; otherwise the test may pass or fail depending on scheduling.

```python
from threading import Event, Thread


def test_thread_callbacks_bind_each_partition():
    release_workers = Event()
    results = []
    threads = []

    for partition in range(3):
        def worker(partition=partition):
            release_workers.wait()
            results.append(partition)
        threads.append(Thread(target=worker))

    for thread in threads:
        thread.start()
    release_workers.set()
    for thread in threads:
        thread.join()

    assert sorted(results) == [0, 1, 2]
```

The default argument is evaluated on each loop iteration when each `worker` function object is defined. The `Event` prevents workers from reading their parameters until after all worker functions have been created. For larger thread tests, use timeouts and ensure cleanup if an assertion fails so a hung worker cannot stall the test suite.

---

## 12. Common mistakes and review checklist

### Common mistakes

1. **Assuming assignment searches outward.** It does not: local-name classification is decided for the function body at compile time.
2. **Forgetting that `+=` is assignment.** `total += 1` still needs the correct binding declaration when `total` belongs to an enclosing function.
3. **Using `global` to avoid learning `nonlocal`.** This introduces module-level coupling and makes tests harder to isolate.
4. **Confusing mutation with rebinding.** `state["count"] += 1` mutates an object; `state = {...}` rebinds the name.
5. **Assuming closures snapshot values.** A closure retains access to a binding; it does not automatically freeze the current value.
6. **Calling callbacks inside the loop while testing.** This may hide a bug that only appears when callbacks are invoked later.
7. **Treating default arguments as copies.** Defaults store references; mutable objects are not cloned.
8. **Using a default-argument binding trick in a public API without considering the signature.** Callers can override that default parameter.
9. **Assuming a class namespace is the lexical parent of methods.** Use `self`, `type(self)`, or the class name deliberately.
10. **Assuming every name in a comprehension is isolated.** Iteration variables are isolated in Python 3, but a `:=` target binds in the containing scope.
11. **Assuming a linter proves correctness.** Ruff catches recognized patterns, not every closure or scheduling error.
12. **Using a closure for a complex state machine.** When state and transitions become hard to describe, use a small class or explicit state parameter.

### Code-review questions

- Is the callback invoked immediately or later? What could change before invocation?
- Which exact binding will each free variable resolve to when the callback runs?
- Does any assignment, augmented assignment, or `del` make a name local?
- Would `nonlocal` express the intended update more clearly than mutating a container?
- Is a default argument binding intentional, and is it safe for callers to override?
- Can the API accept explicit arguments or a `partial` instead of a closure?
- Are callbacks created in a loop covered by tests that call them after the loop?
- Are shared mutable objects accessed from multiple threads? If so, what protects them?
- Does the callback's name and signature communicate its purpose?
- Is the implementation simple enough for a teammate to debug from a traceback?

---

## 13. Exercises with solutions

Try each exercise before reading its solution. Predict the output or exception first, then run the code.

### Exercise 1 — diagnose `UnboundLocalError`

What happens here, and why?

```python
threshold = 10

def check(value):
    print(threshold)
    threshold = value
    return threshold

check(4)
```

**Solution:** the call raises `UnboundLocalError` before the first print. Since `threshold` is assigned anywhere in `check`, Python treats it as local throughout the function. If the intention is to change the module binding, declare `global threshold` before use; if the intention is to compute a local result, rename the local variable (for example, `new_threshold`) or pass the value explicitly. Do not add `global` unless changing module state is genuinely intended.

### Exercise 2 — mutation or rebinding?

Does this need `nonlocal`?

```python
def build():
    values = []
    def add(value):
        values.append(value)
    return values, add
```

**Solution:** no. `add` mutates the list object referred to by `values`; it does not rebind the name. If it instead did `values = values + [value]`, then `values` would be local to `add` and would raise `UnboundLocalError` unless declared `nonlocal` (or unless the operation were rewritten to avoid rebinding).

### Exercise 3 — repair the callback list

```python
handlers = []
for name in ("bronze", "silver", "gold"):
    handlers.append(lambda: name)
```

Write three different corrections.

**Solution A — default argument:**

```python
handlers = [lambda name=name: name for name in ("bronze", "silver", "gold")]
```

**Solution B — partial:**

```python
from functools import partial

def return_name(name):
    return name

handlers = [partial(return_name, name) for name in ("bronze", "silver", "gold")]
```

**Solution C — factory:**

```python
def make_handler(name):
    def handler():
        return name
    return handler

handlers = [make_handler(name) for name in ("bronze", "silver", "gold")]
```

For all three, `[handler() for handler in handlers]` should return `['bronze', 'silver', 'gold']`. Choose based on signature clarity and complexity, not merely the number of lines.

### Exercise 4 — fix a thread target

A loop starts threads with `Thread(target=lambda: write_partition(partition))`. Name two safe alternatives.

**Solution:** pass `target=write_partition, args=(partition,)` directly; or bind the argument with `partial(write_partition, partition)`. A named factory or a small worker object is also appropriate if setup or state is more involved. Binding correctness does not make concurrent writes safe; the destination and retry/idempotency behavior still need their own design.

### Exercise 5 — predict defaults

```python
def make():
    state = []
    def callback(snapshot=state):
        return snapshot
    state = [1]
    return callback

result = make()
print(result())
```

**Solution:** prints `[]`. The default stores a reference to the original empty list at function-definition time. Rebinding the outer local `state` to `[1]` does not change the default reference.

### Exercise 6 — class attribute lookup

Why does a method return a module variable instead of the same-named class attribute? Rewrite it so it returns the instance's value and then the class's value.

**Solution:** the class namespace is not an enclosing lexical scope for a method. Use `self.value` to read the instance/class attribute through normal attribute lookup, or `type(self).value` to explicitly read the runtime class attribute.

### Exercise 7 — create a reliable callback test

Write a pytest test for a callback factory that creates handlers for partition IDs `"p0"`, `"p1"`, and `"p2"`. The test must call every handler only after all handlers have been created.

**Solution:**

```python
def make_handler(partition_id):
    return lambda: partition_id


def test_handlers_keep_partition_ids():
    handlers = [make_handler(partition_id) for partition_id in ("p0", "p1", "p2")]
    assert [handler() for handler in handlers] == ["p0", "p1", "p2"]
```

The important part is the factory call per partition and the assertion after the list has been built. In production code, prefer a named inner function if a lambda obscures validation or behavior.

---

## 14. Self-check

Answer without running code first:

1. Why can `print(x)` work in a nested function while `x += 1` raises `UnboundLocalError`?
2. What binding does `nonlocal x` select? Why can it not target a module-only name?
3. Why does `items.append(value)` not require `nonlocal items`, while `items = items + [value]` does?
4. Why do three lambdas created in a loop often return the same final value?
5. Explain all three fixes: default argument, `partial`, and factory. Which one keeps the returned callback zero-argument without relying on an overrideable default parameter?
6. Why is `Thread(target=worker, args=(item,))` often preferable to `Thread(target=lambda: worker(item))`?
7. What is the difference between a closure's free-variable lookup and a default argument's evaluation timing?
8. Why does `def collect(value, items=[])` share a list across calls?
9. Why does a method not find a same-named class attribute through an unqualified variable name?
10. What does `symtable` explain that `dis` does not, and vice versa?
11. What common bug shape does Ruff `B023` detect? What can it not prove?
12. How would you make a test deterministic when validating callbacks that run on threads?

### Answer key (brief)

1. Assignment makes `x` local throughout the function unless declared otherwise; the earlier read sees an uninitialized local.
2. The nearest enclosing function binding; `global` is the declaration for module scope.
3. `append` mutates the existing object; `items = ...` rebinds the name.
4. They share a binding that changes through the loop and is read later.
5. Default argument stores the current reference/value in the function default; `partial` stores arguments; a factory creates a distinct scope per call. `partial` and a factory can naturally return zero-argument callables.
6. The thread API passes the argument explicitly and avoids a closure around a changing loop variable.
7. Free variables are looked up through the retained binding when called; defaults are evaluated when the function is defined.
8. The list object is constructed once at definition time and reused.
9. Class namespaces are not lexical enclosing scopes for methods.
10. `symtable` reports compiler name classification; `dis` reports bytecode operations for the current interpreter.
11. A function defined in a loop that uses a loop variable without binding it; it cannot prove every callback's intended semantics.
12. Use a synchronization primitive such as `Event`, or test the deterministic binding helper without relying on thread timing.

---

## 15. Completion checklist

Mark each item only when you can explain it and demonstrate it in code.

- [ ] I can distinguish reading a free variable, rebinding a name, and mutating a captured object.
- [ ] I can explain why augmented assignment affects local-name classification.
- [ ] I can diagnose and fix `UnboundLocalError` without reflexively using `global`.
- [ ] I know the exact scope requirements for `nonlocal` and `global`.
- [ ] I can predict `[2, 2, 2]` from loop-created closures and explain the shared binding.
- [ ] I can implement and compare default-argument, `partial`, and factory fixes.
- [ ] I can choose explicit arguments or a state class when they make behavior clearer.
- [ ] I can recognize late binding in GUI, timer, thread, async, and deferred-operation callbacks.
- [ ] I can explain why default arguments bind early and why mutable defaults can leak state.
- [ ] I understand why methods do not close over class-body names.
- [ ] I can explain comprehension iteration-variable scope and the special containing-scope behavior of `:=`.
- [ ] I can use `symtable` and `dis` without relying on version-specific bytecode output.
- [ ] I can configure Ruff to check `B023` and review global-state warnings.
- [ ] I have a regression test that invokes all generated callbacks after creation and asserts the intended values.

## Key takeaway

**A closure retains access to a binding; it does not automatically snapshot the binding's value.** Assignment determines which scope owns a name, and deferred execution determines when a callback reads that name. Make the intended binding explicit—through a default argument, `partial`, a factory, or a normal argument—and protect the behavior with tests that run callbacks after they have all been created.
