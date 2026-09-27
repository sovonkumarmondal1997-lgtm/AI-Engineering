# Context Managers in Python

> **Stage 1 — Programming and Computational Thinking**  
> **Module 1.9 — Advanced Production-Oriented Python Foundations**

This chapter teaches Python context managers from first principles to practical production-oriented use. The central idea is simple:

> **Acquire a resource, use it inside a clearly defined boundary, and make cleanup happen reliably when the boundary is left.**

The goal is not to memorize `with`, `__enter__`, or `__exit__`. The goal is to understand the resource lifecycle that those features model.

---

## Learning objectives

By the end of this chapter, you should be able to:

- explain what a resource is and why resources need lifecycle management;
- use `with` confidently for built-in and custom context managers;
- explain what `as` receives;
- explain `__enter__()` and `__exit__()`;
- reason about normal completion, exceptions, cleanup, and exception suppression;
- implement a small class-based context manager;
- implement a generator-based context manager with `contextlib.contextmanager`;
- use `nullcontext`, `closing`, and `ExitStack` when they make the lifecycle clearer;
- understand nested and multiple context managers;
- test failure-path cleanup;
- recognize common mistakes and hidden behavior;
- decide when a context manager improves a design and when ordinary code is clearer.

---

# 1. Introduction — What Is a Resource?

A **resource** is something a running program acquires and uses for some amount of time, and for which continued ownership or use has consequences.

Typical examples include:

- an open file;
- a network connection;
- a database connection;
- a lock;
- a temporary file;
- a temporary directory;
- an operating-system or external-system handle.

A useful first mental model is:

```text
Acquire resource
      ↓
   Use it
      ↓
 Release resource
```

The difficult part is usually not acquisition. It is making the final step reliable.

### A simple analogy

Imagine borrowing a library book:

```text
Take the book
    ↓
Read the book
    ↓
Return the book
```

The analogy helps because the ownership boundary is obvious. You are allowed to use the book after borrowing it, but eventually it must be returned.

The analogy is not a literal description of Python. A file object is not a "book" and `__exit__()` is not a physical return desk. The useful similarity is the **lifecycle boundary**.

### Why resource management is an engineering problem

Consider code that opens a file and then performs several operations:

```python
file = open("data.txt", "r", encoding="utf-8")

data = file.read()
parsed = data.strip()
result = parsed.upper()

file.close()
```

This looks fine when every statement succeeds.

But imagine that `file.read()` raises an exception. Execution does not automatically jump to the final `file.close()` line. The file can remain open longer than intended.

Resource management therefore asks a more general question:

> **How do we guarantee that cleanup belongs to the lifecycle of the resource rather than to one particular successful execution path?**

That question leads directly to `try/finally`, and then to context managers.

### Production perspective

This topic matters in production Python because resources are limited and often external to the Python object itself.

A process can have:

- a limited number of file descriptors;
- a limited pool of connections;
- locks that other threads need;
- temporary resources that should not accumulate;
- external handles that must be released.

A resource leak is not automatically a memory leak. A program can have plenty of available memory and still fail because it has exhausted operating-system resources, connection pools, locks, or another external capacity.

---

# 2. Why Resource Cleanup Matters

Resource cleanup matters because acquisition often creates a responsibility.

For example:

```text
open file       → eventually close file
acquire lock    → eventually release lock
create temp dir → eventually remove it
start transaction → eventually finish it
```

The exact lifecycle depends on the resource, but the engineering principle is the same.

## What can go wrong?

### Open files

Repeatedly opening files without closing them can eventually exhaust the process's available file descriptors.

### Locks

If code acquires a lock and fails before releasing it, other code may remain blocked.

### Connections

A connection that is never returned to a pool can reduce capacity for other work.

### Temporary resources

Temporary files or directories can accumulate and create storage or operational problems.

### Application-level resources

Some resources are not operating-system handles at all. They can still have lifecycle rules, such as "enter a transaction and either commit or roll back."

### Resource leak categories

It is useful to distinguish several categories:

| Leak type | Example | Consequence |
|---|---|---|
| Memory-related | Objects remain referenced unnecessarily | Memory pressure |
| OS-resource-related | File descriptor remains open | "Too many open files" |
| Application-level | Lock remains held | Other work cannot proceed |
| External-system-related | Connection is never released | Pool exhaustion or capacity loss |

The important point is:

> **"Cleanup" is broader than freeing memory.**

---

# 3. Manual Resource Management

Before using a context manager, understand the lower-level pattern.

For a file:

```python
file = open("data.txt", "r", encoding="utf-8")

try:
    contents = file.read()
finally:
    file.close()
```

### Line-by-line reasoning

```python
file = open("data.txt", "r", encoding="utf-8")
```

1. Python asks the operating system and file machinery to open the file.
2. `open()` returns a file object.
3. We store that object in `file`.

The potentially failing operation happens inside the `try` block:

```python
try:
    contents = file.read()
finally:
    file.close()
```

The `finally` block contains the cleanup operation.

The `finally` block is intended for cleanup that must happen as control leaves the `try` statement through normal completion or an exception.

### Why `finally` matters

Compare this:

```python
file = open("data.txt", "r", encoding="utf-8")

contents = file.read()

file.close()
```

The `close()` call is reachable only if the preceding statements complete normally.

With `finally`:

```python
file = open("data.txt", "r", encoding="utf-8")

try:
    contents = file.read()
finally:
    file.close()
```

The cleanup is structurally attached to the operation.

### An important limitation

`try/finally` is powerful, but manually writing resource lifecycle code for every resource can become repetitive and easy to get subtly wrong.

That is one reason Python provides the `with` statement and the context-manager protocol.

---

# 4. The `with` Statement

Now the same file operation becomes:

```python
with open("data.txt", "r", encoding="utf-8") as file:
    contents = file.read()
```

This is not merely shorter syntax. It expresses a lifecycle boundary.

A useful mental model is:

```text
enter
  ↓
run the block
  ↓
exit / cleanup
```

If the body raises an exception, the context-manager machinery still gets an opportunity to perform exit/cleanup logic.

## What each part means

```python
with open("data.txt", "r", encoding="utf-8") as file:
    contents = file.read()
```

- `with` starts a context-management statement.
- `open(...)` produces an object used as the context manager.
- `as file` binds the value returned by that manager's `__enter__()` method.
- The indented block is the managed operation.
- When the block ends, Python invokes the manager's exit behavior.

### The key mental model

Do not memorize:

> "`with` means close the file."

That is too narrow.

Memorize:

> **"`with` creates a boundary around a lifecycle: enter before the block, exit after the block."**

A file closes because file objects implement a context-manager protocol whose exit behavior closes the file.

---

# 5. What Does `as` Mean?

Consider:

```python
with open("data.txt", "r", encoding="utf-8") as file:
    print(file)
```

A common beginner assumption is:

> "`file` must always be the exact same object returned by `open()`."

That is not the general rule.

Conceptually:

```python
manager = open("data.txt", "r", encoding="utf-8")
value = manager.__enter__()
```

The name after `as` receives **whatever `__enter__()` returns**.

For many context managers, `__enter__()` returns the manager itself:

```python
class ManagedResource:
    def __enter__(self):
        return self
```

But a context manager can return another object:

```python
class ResourceProvider:
    def __enter__(self):
        return "useful value"

    def __exit__(self, exc_type, exc_value, traceback):
        return False


with ResourceProvider() as value:
    print(value)
```

Expected output:

```text
useful value
```

Here, the object controlling the context and the value bound to `value` are not the same object.

### Rule to remember

```text
with manager as name:
              ↑
              receives __enter__()'s return value
```

---

# 6. Context Manager — Simple Definition

A **context manager** is an object that defines how a managed context is entered and exited.

At a conceptual level:

```text
Setup / acquisition
        ↓
Enter managed block
        ↓
Use resource
        ↓
Leave managed block
        ↓
Cleanup
```

The abstraction is useful because it places lifecycle behavior next to the boundary where the resource is used.

Without a context manager, setup and cleanup can be separated by many lines of code.

With one:

```python
with resource_manager() as resource:
    do_work(resource)
```

the lifetime is visible to the reader.

That visibility is a maintainability benefit, not merely a syntax benefit.

---

# 7. The Context Manager Protocol

Python's context-manager protocol is based on two special methods:

```python
__enter__()
__exit__()
```

The high-level flow is:

```text
with manager as value:
        ↓
manager.__enter__()
        ↓
value = returned value
        ↓
execute block
        ↓
manager.__exit__(...)
```

These methods have distinct responsibilities.

| Method | Main responsibility |
|---|---|
| `__enter__()` | Enter/acquire/setup and provide the `as` value |
| `__exit__()` | Exit/cleanup and optionally suppress an exception |

The exact mechanics include important exception behavior, which we will build carefully.

### Important distinction

The protocol is the **language-level contract**.

CPython has an implementation of that contract, but you should reason primarily from the language semantics:

> A `with` statement asks an object to enter a context and later asks it to exit the context.

---

# 8. `__enter__()` in Detail

A class-based context manager can define:

```python
class ManagedResource:
    def __enter__(self):
        print("Entering")
        return self
```

When the context is entered, Python calls `__enter__()`.

Typical responsibilities include:

- acquiring a resource;
- validating that setup succeeded;
- initializing temporary state;
- returning the object or another useful value to the block.

## Returning `self` is common, not mandatory

This pattern is common:

```python
class Connection:
    def __enter__(self):
        self.open_connection()
        return self
```

But a manager could instead return a lower-level handle:

```python
class ResourceProvider:
    def __enter__(self):
        self.handle = acquire_handle()
        return self.handle
```

The `as` variable then receives the handle.

### What if `__enter__()` fails?

This is an important boundary.

If `__enter__()` raises while trying to acquire the resource, the managed body is not entered. The object's `__exit__()` is not called as the successful context exit for that manager.

That means:

> **Acquisition logic inside `__enter__()` must clean up any partial acquisition if the acquisition process itself can fail after obtaining part of a resource.**

In more complicated designs, `ExitStack` or smaller acquisition steps can help make partial cleanup explicit.

---

# 9. `__exit__()` in Detail

A context manager's exit method has the form:

```python
def __exit__(self, exc_type, exc_value, traceback):
    ...
```

The three exception-related arguments tell the context manager what happened in the managed block.

## `exc_type`

The exception class, such as:

```python
ValueError
```

when an exception occurred.

## `exc_value`

The actual exception instance, such as:

```python
ValueError("invalid value")
```

## `traceback`

The traceback object associated with the exception.

### When there was no exception

For normal completion, the values are conceptually:

```python
exc_type is None
exc_value is None
traceback is None
```

### When an exception occurred

Python provides the exception information to `__exit__()`.

This lets a context manager distinguish:

```text
Normal completion
      vs.
Exceptional completion
```

That distinction is useful for cleanup, logging, rollback-like behavior, or deliberate suppression.

### A debugging example

```python
class DebugContext:
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("exc_type:", exc_type)
        print("exc_value:", exc_value)
        print("traceback is None:", traceback is None)
        return False


with DebugContext():
    print("inside")
```

Expected output has:

```text
enter
inside
exc_type: None
exc_value: None
traceback is None: True
```

Now add an exception:

```python
class DebugContext:
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("exc_type:", exc_type)
        print("exc_value:", exc_value)
        print("traceback is None:", traceback is None)
        return False


with DebugContext():
    raise ValueError("bad input")
```

The context manager sees information about the exception before the exception continues propagating.

---

# 10. Build Your First Custom Context Manager

Start with the smallest useful class:

```python
class ManagedResource:
    def __enter__(self):
        print("Resource acquired")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Resource released")
        return False


with ManagedResource() as resource:
    print("Using resource")
```

Expected output:

```text
Resource acquired
Using resource
Resource released
```

## Execution trace

### Step 1

Python creates:

```python
ManagedResource()
```

### Step 2

Python enters the context:

```python
resource.__enter__()
```

The method prints:

```text
Resource acquired
```

and returns `self`, so `resource` inside the block refers to that object.

### Step 3

Python executes:

```python
print("Using resource")
```

### Step 4

Python exits the context and invokes:

```python
resource.__exit__(None, None, None)
```

The manager prints:

```text
Resource released
```

### Exception path

```python
class ManagedResource:
    def __enter__(self):
        print("Resource acquired")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Resource released")
        return False


try:
    with ManagedResource():
        print("Before failure")
        raise RuntimeError("Something failed")
except RuntimeError as exc:
    print("Caught:", exc)
```

Expected output:

```text
Resource acquired
Before failure
Resource released
Caught: Something failed
```

Notice:

- cleanup happened;
- the exception was not suppressed;
- the outer `except` still received the error.

This separation is fundamental.

---

# 11. Context Manager With Real State

A custom manager can own state and a real resource.

Here is a small educational file wrapper:

```python
class FileReporter:
    def __init__(self, path):
        self.path = path
        self.file = None

    def __enter__(self):
        self.file = open(self.path, "w", encoding="utf-8")
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file is not None:
            self.file.close()
        return False


with FileReporter("report.txt") as file:
    file.write("Hello from a context manager.\n")
```

### Lifecycle

```text
FileReporter(path)
       ↓
__enter__()
       ↓
open file
       ↓
return file
       ↓
with block uses file
       ↓
__exit__()
       ↓
close file
```

### Why `self.file = None`?

The initial state makes the object's lifecycle explicit.

Before entering:

`self.file is None`

After successful acquisition:

`self.file` refers to an open file object.

On exit, we check whether there is something to close.

### A design caution

For production code, prefer Python's built-in file context manager whenever it already expresses exactly what you need:

```python
with open("report.txt", "w", encoding="utf-8") as file:
    file.write("Hello\n")
```

Custom wrappers are justified when they add meaningful domain behavior, not merely to reimplement standard library features.

---

# 12. Exception Handling in `__exit__()`

The key signature is:

```python
def __exit__(self, exc_type, exc_value, traceback):
    ...
```

## No exception

Consider:

```python
class DebugContext:
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("type:", exc_type)
        print("value:", exc_value)
        print("traceback:", traceback)
        return False


with DebugContext():
    print("work")
```

The exit method receives `None` values because the body completed normally.

## Exception path

Now:

```python
class DebugContext:
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("type:", exc_type)
        print("value:", exc_value)
        print("traceback type:", type(traceback).__name__)
        return False


with DebugContext():
    raise ValueError("invalid input")
```

The manager receives information about the `ValueError`.

### Why does this matter?

The context manager can make a decision.

For example:

```python
def __exit__(self, exc_type, exc_value, traceback):
    cleanup()
    return False
```

means:

> Clean up, but let the exception continue propagating.

Whereas returning a truthy value means:

> Clean up and tell the `with` machinery that this exception has been handled.

That second behavior is powerful and therefore easy to misuse.

---

# 13. Returning `True` From `__exit__()`

A context manager can intentionally suppress an exception.

```python
class SuppressExample:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return True


with SuppressExample():
    raise ValueError("Something went wrong")

print("Program continues")
```

Expected output:

```text
Program continues
```

The `ValueError` does not propagate out of the `with` statement because `__exit__()` returned a truthy value.

## What exactly does `True` mean?

It does **not** mean:

- the resource was cleaned successfully;
- the operation succeeded;
- the exception never happened.

It means:

> **The context manager is indicating that the exception should be suppressed.**

### Why this can be dangerous

Consider:

```python
class BadContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return True


with BadContext():
    important_operation()
```

If `important_operation()` fails, the failure silently disappears.

That can create:

- incorrect results;
- hidden data corruption;
- missing alerts;
- broken invariants;
- extremely confusing debugging sessions.

### Production rule

Unless exception suppression is deliberate and documented, a context manager should normally return `False` or `None`.

---

# 14. Cleanup vs Exception Suppression

Keep these concepts separate:

```text
Cleanup
  ≠
Exception suppression
```

A manager can clean up without suppressing:

```python
class CleanupOnly:
    def __enter__(self):
        print("acquire")

    def __exit__(self, exc_type, exc_value, traceback):
        print("cleanup")
        return False


try:
    with CleanupOnly():
        raise RuntimeError("failure")
except RuntimeError:
    print("exception propagated")
```

Expected output:

```text
acquire
cleanup
exception propagated
```

This is a normal and common production pattern.

### The engineering idea

A resource manager's first responsibility is often:

> **Leave the resource in a safe state.**

Whether an application error should be suppressed is a separate policy decision.

---

# 15. Conceptual Expansion of `with`

Consider:

```python
with manager as value:
    do_work(value)
```

A useful conceptual model for a single context manager is:

```python
manager = ...
value = manager.__enter__()

try:
    do_work(value)
except BaseException as exc:
    suppress = manager.__exit__(
        type(exc),
        exc,
        exc.__traceback__,
    )
    if not suppress:
        raise
else:
    manager.__exit__(None, None, None)
```

This is a **conceptual model**, not a claim that CPython literally replaces every `with` statement with this exact source code.

It is useful because it exposes the key ideas:

```text
enter
  ↓
run block
  ↓
normal path ─────────┐
                     ↓
                 __exit__
                     ↑
exception path ──────┘
                     ↓
       suppress or propagate
```

## Important nuance: failed acquisition

If `__enter__()` raises, the managed block is not executed and that manager's successful `__exit__()` path is not entered.

This matters in designs where acquisition itself has multiple steps.

---

# 16. Nested Context Managers

Context managers can be nested:

```python
with resource_a() as a:
    with resource_b() as b:
        use(a, b)
```

Lifecycle order is:

```text
Enter A
  ↓
Enter B
  ↓
Use A and B
  ↓
Exit B
  ↓
Exit A
```

The cleanup order is the reverse of acquisition order.

## Why reverse order?

Suppose B depends on A:

```text
A provides foundation
B uses A
```

It is usually safer to release B before A.

This is the same reason nested function calls and many other resource lifecycles follow a stack-like structure.

### Example

```python
class NamedContext:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print(f"enter {self.name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"exit {self.name}")
        return False


with NamedContext("A"):
    with NamedContext("B"):
        print("inside")
```

Expected output:

```text
enter A
enter B
inside
exit B
exit A
```

---

# 17. Multiple Context Managers

Python also supports:

```python
with resource_a() as a, resource_b() as b:
    use(a, b)
```

A helpful conceptual model is nested contexts:

```python
with resource_a() as a:
    with resource_b() as b:
        use(a, b)
```

The combined form is often easier to read when the resources have a closely related lifecycle.

## Entry order

Resources are entered from left to right:

```text
A enters
B enters
```

## Exit order

Resources exit from right to left:

```text
B exits
A exits
```

## Why this matters

The order is observable.

If `B` depends on `A`, this is reasonable:

```python
with A() as a, B(a) as b:
    use(b)
```

The dependency is represented by the acquisition order.

### If the second `__enter__()` fails

Python exits the contexts that were already successfully entered.

For example:

```text
Enter A → succeeds
Enter B → fails
Exit A
Propagate B's failure
```

This behavior is one reason context managers are useful for composing multiple resources safely.

---

# 18. Real Python Example — File Handling

Files are one of the clearest examples of context management.

```python
with open("data.txt", "r", encoding="utf-8") as file:
    for line in file:
        print(line.rstrip())
```

The file object returned by `open()` supports the context-manager protocol.

## Lifecycle

```text
open(...)
   ↓
__enter__()
   ↓
file bound to "file"
   ↓
read lines
   ↓
leave block
   ↓
__exit__()
   ↓
file closed
```

### Why this is better than manually closing

Compare:

```python
file = open("data.txt", "r", encoding="utf-8")
try:
    process(file)
finally:
    file.close()
```

with:

```python
with open("data.txt", "r", encoding="utf-8") as file:
    process(file)
```

The second expresses the ownership boundary more directly.

### Production habit

When a library or standard-library resource already supports a correct context manager, prefer its native context-manager interface.

---

# 19. File Writing and Safe Resource Handling

Writing follows the same lifecycle:

```python
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("Hello\n")
```

Three cases matter.

### Case 1: write succeeds

The block completes normally, then cleanup runs.

### Case 2: an exception occurs

The context manager still gets its exit opportunity as control leaves the block.

### Case 3: the block ends early

For example:

```python
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("first line\n")
    if should_stop():
        return
```

The context is exited before the surrounding function returns.

### A practical note about data durability

Closing a file and having data reach durable storage are related but not identical concerns. Context management handles the file object's lifecycle; it does not magically guarantee every possible durability property of every storage system.

For ordinary application code, however, the essential lesson is:

> Keep file ownership inside a visible `with` boundary unless a different lifecycle is intentionally required.

---

# 20. Context Managers and Locks

Python locks can naturally form context boundaries.

```python
import threading

lock = threading.Lock()
shared_state = {"count": 0}

with lock:
    shared_state["count"] += 1

print(shared_state)
```

The lifecycle is:

```text
acquire lock
    ↓
critical section
    ↓
release lock
```

### Why a context manager fits

If the code inside the critical section raises an exception, the lock should still be released.

Writing:

```python
lock.acquire()
try:
    shared_state["count"] += 1
finally:
    lock.release()
```

is more verbose and more error-prone than the context-managed form:

```python
with lock:
    shared_state["count"] += 1
```

### Scope of this discussion

This section is about resource boundaries, not about concurrency design in general.

Questions such as:

- lock granularity;
- deadlocks;
- starvation;
- contention;
- thread safety;

belong to broader concurrency engineering.

For this chapter, remember:

> **A lock has an acquire/use/release lifecycle, so it is naturally expressible as a context.**

---

# 21. Context Managers and Transactions

A transaction-like lifecycle often looks like:

```text
begin
  ↓
perform operations
  ↓
success → commit
failure → rollback
  ↓
cleanup
```

A context manager can express the boundary cleanly.

An educational version might look like:

```python
class Transaction:
    def __enter__(self):
        print("BEGIN")
        return self

    def commit(self):
        print("COMMIT")

    def rollback(self):
        print("ROLLBACK")

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False


with Transaction():
    print("perform operations")
```

Expected output:

```text
BEGIN
perform operations
COMMIT
```

Now:

```python
try:
    with Transaction():
        print("perform operations")
        raise RuntimeError("operation failed")
except RuntimeError:
    print("failure reached caller")
```

Expected output:

```text
BEGIN
perform operations
ROLLBACK
failure reached caller
```

### Important production distinction

This is a **transaction-like teaching example**, not a database transaction implementation.

Real transaction systems have domain-specific rules involving isolation, durability, commit protocols, connection state, and failure modes.

The context-manager lesson is simply:

> If the lifecycle is "enter a transactional boundary, do work, then commit or roll back on exit," a context manager can communicate that structure clearly.

---

# 22. Context Managers for Temporary State

Not every context manager controls a file or handle.

Some context managers temporarily change program state and restore it afterward.

The lifecycle is:

```text
save old state
     ↓
apply temporary state
     ↓
run block
     ↓
restore old state
```

## A small custom example

```python
class TemporaryConfiguration:
    def __init__(self, settings, temporary_values):
        self.settings = settings
        self.temporary_values = temporary_values
        self.previous_values = {}

    def __enter__(self):
        for key, new_value in self.temporary_values.items():
            self.previous_values[key] = self.settings.get(key)
            self.settings[key] = new_value
        return self.settings

    def __exit__(self, exc_type, exc_value, traceback):
        for key, old_value in self.previous_values.items():
            if old_value is None:
                self.settings.pop(key, None)
            else:
                self.settings[key] = old_value
        return False


settings = {"mode": "normal", "debug": False}

with TemporaryConfiguration(
    settings,
    {"mode": "maintenance", "debug": True},
) as current:
    print(current)

print(settings)
```

Expected output:

```text
{'mode': 'maintenance', 'debug': True}
{'mode': 'normal', 'debug': False}
```

### Why `finally` still matters conceptually

The restore operation should happen on both success and failure.

A class-based manager gets that behavior through `__exit__()`.

A generator-based manager usually puts restoration in `finally` around `yield`.

---

# 23. Context Managers for Timing

A context manager can define a timing boundary:

```python
with Timer("operation"):
    perform_work()
```

Here is a small implementation using the standard library:

```python
from time import perf_counter


class Timer:
    def __init__(self, name):
        self.name = name
        self.start = None

    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = perf_counter() - self.start
        print(f"{self.name}: {elapsed:.6f} seconds")
        return False


with Timer("small operation"):
    total = sum(range(100_000))
    print("total:", total)
```

The exact duration varies by machine and workload.

## Why `perf_counter()`?

For elapsed-duration measurement, `time.perf_counter()` is designed for high-resolution performance timing.

### What this is and is not

Useful:

- quick instrumentation;
- understanding whether an operation is unexpectedly slow;
- timing application code paths.

Not a complete benchmark framework.

A reliable benchmark needs to consider:

- repeated runs;
- warm-up effects;
- system load;
- input characteristics;
- statistical variation.

Do not treat one timing context as proof of a performance conclusion.

---

# 24. Context Managers With `contextlib`

The standard library provides helpers in `contextlib`.

One of the most important is:

```python
from contextlib import contextmanager
```

It lets you express simple context-manager lifecycles using a generator-style function.

```python
from contextlib import contextmanager


@contextmanager
def managed_resource():
    print("Enter")
    try:
        yield
    finally:
        print("Exit")


with managed_resource():
    print("Inside")
```

Expected output:

```text
Enter
Inside
Exit
```

Several concepts are working together here:

```text
@contextmanager
      +
generator function
      +
yield
      +
try/finally
      ↓
generator-based context manager
```

This is a compact way to express a simple setup/cleanup boundary.

---

# 25. `@contextmanager` in Detail

Consider:

```python
from contextlib import contextmanager


@contextmanager
def managed_resource():
    print("Enter")
    try:
        yield
    finally:
        print("Exit")
```

The function contains a `yield`, so calling it creates generator-style state rather than immediately running the whole body to completion.

At context-entry time, the machinery advances to the `yield`.

The lifecycle is:

```text
context-manager function called
           ↓
context manager object created
           ↓
enter
           ↓
execute until yield
           ↓
yielded value becomes the "as" value
           ↓
with block executes
           ↓
context resumes
           ↓
finally cleanup executes
```

### Why the exact structure matters

A `@contextmanager` function is expected to describe one enter/exit boundary. In normal use, it has one meaningful `yield` separating setup from cleanup.

A simple pattern is:

```python
@contextmanager
def managed_resource():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)
```

Think of:

```python
yield resource
```

as the **boundary marker**:

- everything before it is enter/setup work;
- the caller's `with` block happens at the boundary;
- execution continues after `yield` when the context is exiting.

---

# 26. `@contextmanager` With a Returned Value

A common reason to use a generator-based context manager is to make a resource available through `as`.

For example:

```python
from contextlib import contextmanager


@contextmanager
def open_text_file(path):
    file = open(path, "r", encoding="utf-8")
    try:
        yield file
    finally:
        file.close()


with open_text_file("data.txt") as file:
    for line in file:
        print(line.rstrip())
```

The relationship is:

```text
yield file
    ↓
file on the left of "as"
```

More precisely:

```python
with open_text_file(...) as file:
    ...
```

causes the yielded value to become the bound context value.

### Why `try/finally`?

Without it:

```python
@contextmanager
def unsafe_file(path):
    file = open(path, "r", encoding="utf-8")
    yield file
    file.close()
```

the explicit `close()` line might never execute if the managed block raises before the generator resumes normally.

With `finally`:

```python
@contextmanager
def safe_file(path):
    file = open(path, "r", encoding="utf-8")
    try:
        yield file
    finally:
        file.close()
```

cleanup is tied to the context's exit path.

For ordinary file handling, `open()` itself already supports `with`, so the custom wrapper should only be used when it provides a meaningful abstraction.

---

# 27. `try/finally` With `@contextmanager`

The most important pattern is:

```python
from contextlib import contextmanager


@contextmanager
def managed_resource():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)
```

The `finally` block means:

```text
acquire
  ↓
yield / user block
  ↓
resume
  ↓
release
```

If the user block raises, the exception is propagated through the context-manager machinery and the `finally` section still executes as part of unwinding, assuming normal Python control flow continues through the context boundary.

## A concrete example without hidden functions

```python
from contextlib import contextmanager


@contextmanager
def managed_list():
    items = []
    print("acquire list-like resource")
    try:
        yield items
    finally:
        print("cleanup list-like resource")
        items.clear()


with managed_list() as items:
    items.append("data")
    print(items)
```

Expected output:

```text
acquire list-like resource
['data']
cleanup list-like resource
```

The list is only a stand-in for a resource with an explicit lifecycle.

---

# 28. Exception Behavior With `@contextmanager`

Exception behavior is easier to understand if you focus on the `yield` boundary.

```python
from contextlib import contextmanager


@contextmanager
def demo():
    print("before yield")
    try:
        yield "value"
    except ValueError as exc:
        print("generator saw:", exc)
        raise
    finally:
        print("cleanup")


try:
    with demo() as value:
        print("inside:", value)
        raise ValueError("bad input")
except ValueError:
    print("caller received ValueError")
```

Expected output:

```text
before yield
inside: value
generator saw: bad input
cleanup
caller received ValueError
```

Conceptually, the exception reaches the context manager at the point where execution had yielded control to the `with` block.

This makes the surrounding `try/except/finally` meaningful.

### Safe pattern

Use:

```python
try:
    yield resource
finally:
    release(resource)
```

when cleanup must happen regardless of whether the body succeeds or fails.

Use `except` around `yield` only when you intentionally need to inspect or translate a specific failure.

---

# 29. `contextlib.nullcontext`

Sometimes a function optionally receives a context manager.

For example, suppose a helper can either use an already-open file or open its own file.

`nullcontext` can simplify the optional boundary:

```python
from contextlib import nullcontext


def read_first_line(file=None, path=None):
    if file is not None:
        context = nullcontext(file)
    elif path is not None:
        context = open(path, "r", encoding="utf-8")
    else:
        raise ValueError("Provide either file or path")

    with context as managed_file:
        return managed_file.readline().rstrip("\n")
```

The idea is:

```text
already have a resource
        ↓
need a no-op context boundary
        ↓
nullcontext(value)
```

When `path` is used, the file context controls the file lifecycle.

When `file` is supplied by the caller, `nullcontext(file)` provides a uniform interface without taking ownership of closing the caller's file.

### Why this matters

A common design question is:

> "Who owns this resource?"

`nullcontext` can help express:

> "This branch provides a resource that this function does not own."

That ownership clarity is more important than the helper itself.

---

# 30. `contextlib.closing`

Some objects expose a useful `.close()` method but do not implement the context-manager protocol.

`contextlib.closing` provides a simple adapter:

```python
from contextlib import closing


class ResourceWithClose:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True
        print("closed")


resource = ResourceWithClose()

with closing(resource) as managed:
    print("using resource:", managed.closed)

print("after context:", resource.closed)
```

Expected output:

```text
using resource: False
closed
after context: True
```

The essential contract is:

```text
enter
  ↓
use object
  ↓
call object.close() on exit
```

### When is `closing` useful?

When:

- the resource has a `.close()` method;
- the object does not provide the context-manager protocol;
- you want a clear context boundary.

### Prefer native support when available

If the resource already has a correct built-in context-manager implementation:

```python
with resource:
    ...
```

is generally clearer than:

```python
with closing(resource):
    ...
```

---

# 31. Other Relevant `contextlib` Utilities

For this topic, the most directly useful `contextlib` tools are:

| Utility | Purpose |
|---|---|
| `contextmanager` | Build a context manager from a generator-style lifecycle |
| `nullcontext` | Provide an optional/no-op context boundary |
| `closing` | Adapt a `.close()`-based resource |
| `ExitStack` | Dynamically compose and clean up multiple contexts |

The standard library contains other `contextlib` helpers, but a production engineer should resist turning every module into a reference-manual tour.

The right question is:

> **Which utility makes the resource lifecycle easier to express and review?**

---

# 32. `ExitStack`

Ordinary nesting works well when the resources are known in advance:

```python
with resource_a() as a, resource_b() as b:
    use(a, b)
```

But sometimes the number of resources is dynamic.

For example:

```python
paths = ["a.txt", "b.txt", "c.txt"]
```

and the set of files to open is determined at runtime.

`ExitStack` can help:

```python
from contextlib import ExitStack


paths = ["a.txt", "b.txt", "c.txt"]

with ExitStack() as stack:
    files = [
        stack.enter_context(open(path, "r", encoding="utf-8"))
        for path in paths
    ]

    for file in files:
        print(file.readline().rstrip())
```

## Why this works

Each successful `enter_context()` registers the entered context for cleanup.

Conceptually:

```text
enter A
register A cleanup

enter B
register B cleanup

enter C
register C cleanup

use resources

exit C
exit B
exit A
```

### Why reverse-order cleanup?

The stack follows a last-in, first-out lifecycle.

This is useful when later resources may depend on earlier ones.

### When should you reach for `ExitStack`?

Use it when the resource composition is genuinely dynamic or when conditional acquisition would otherwise produce deeply nested or awkward cleanup logic.

Do not use it merely because it exists. For two fixed resources, ordinary `with` syntax is usually easier to read.

---

# 33. Reusable vs Single-Use Context Managers

A crucial production habit is:

> **Never assume that every context-manager object can be reused.**

Consider a stateful class:

```python
class SimpleState:
    def __init__(self):
        self.active = False

    def __enter__(self):
        if self.active:
            raise RuntimeError("Already active")
        self.active = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.active = False
        return False


manager = SimpleState()

with manager:
    print("first use")

with manager:
    print("second use")
```

This class is deliberately designed to be reusable because it resets its state.

Other classes may not have that property.

## Generator-based context-manager lifecycle

A context manager produced by `@contextmanager` is tied to a generator lifecycle.

For example:

```python
from contextlib import contextmanager


@contextmanager
def one_lifecycle():
    print("enter")
    try:
        yield
    finally:
        print("exit")


manager = one_lifecycle()

with manager:
    print("first")
```

The **manager instance** represents one generator lifecycle.

Trying to reuse the same instance for another independent `with` is not the same as calling the generator function again:

```python
with manager:
    ...
```

The safe pattern for independent uses is:

```python
with one_lifecycle():
    ...

with one_lifecycle():
    ...
```

Each call creates a fresh context manager instance.

### The important distinction

```text
Reusable design
    vs
one lifecycle per object
```

Read the contract of the object instead of assuming.

---

# 34. Context Managers With State

A context manager can maintain state that changes during the managed lifetime.

Here is a temporary-mode example:

```python
class TemporaryMode:
    def __init__(self, state, key, temporary_value):
        self.state = state
        self.key = key
        self.temporary_value = temporary_value
        self.previous_value = None
        self.had_previous_value = False

    def __enter__(self):
        self.had_previous_value = self.key in self.state
        if self.had_previous_value:
            self.previous_value = self.state[self.key]

        self.state[self.key] = self.temporary_value
        return self.state

    def __exit__(self, exc_type, exc_value, traceback):
        if self.had_previous_value:
            self.state[self.key] = self.previous_value
        else:
            self.state.pop(self.key, None)
        return False


configuration = {"mode": "normal"}

with TemporaryMode(configuration, "mode", "debug"):
    print(configuration)

print(configuration)
```

Expected output:

```text
{'mode': 'debug'}
{'mode': 'normal'}
```

## Why save the previous state?

Because temporary state management is generally a reversible operation:

```text
remember old state
       ↓
apply temporary state
       ↓
run block
       ↓
restore old state
```

### Nested temporary state

Good designs should think about nesting:

```text
normal
  ↓
temporary A
  ↓
temporary B
  ↓
restore A
  ↓
restore normal
```

A simple "always restore to one fixed value" implementation may break this pattern.

---

# 35. Context Managers and Decorators

Decorators and context managers both introduce boundaries, but around different units.

From the previous topic:

```text
Decorator
─────────
callable
   ↓
wrapper behavior
   ↓
callable execution
```

Context management:

```text
Context manager
───────────────
enter
  ↓
with block
  ↓
exit / cleanup
```

### The useful distinction

A decorator is usually concerned with **callable behavior**.

A context manager is usually concerned with **block lifetime and resource/state management**.

For example:

```python
@log_call
def process():
    ...
```

wraps a function invocation.

Whereas:

```python
with lock:
    process()
```

defines a resource boundary around the block.

### Where `@contextmanager` fits

`@contextmanager` is interesting because it combines several concepts you already know:

```text
decorator
   +
generator-style control flow
   +
yield
   +
try/finally
   ↓
context-manager implementation
```

It does not make decorators and context managers the same abstraction. It is a library mechanism for implementing context-manager behavior conveniently.

---

# 36. Context Managers and Generators

The generator relationship is easiest to understand around `yield`.

A generator can pause:

```python
def example():
    print("before")
    yield "value"
    print("after")
```

In a context manager:

```python
from contextlib import contextmanager


@contextmanager
def example_context():
    print("before")
    try:
        yield "value"
    finally:
        print("cleanup")
```

The `yield` forms a boundary:

```text
before
  ↓
yield
  ↓
with block executes
  ↓
generator resumes
  ↓
cleanup
```

This is why the generator-based form is so useful for simple acquire/use/release lifecycles.

The broader generator mechanics belong to the iterators/generators chapter. Here, focus on one idea:

> **`yield` gives the caller control temporarily, and execution resumes after the `with` block so cleanup can run.**

---

# 37. Common Context-Manager Mistakes

Context managers are simple once understood, but their failure modes are important.

## Mistake 1: Forgetting cleanup

### Why it happens

The programmer focuses on successful execution and puts cleanup after the operation.

### Incorrect

```python
resource = acquire()
use(resource)
release(resource)
```

If `use()` raises, `release()` may not run.

### Better

```python
resource = acquire()
try:
    use(resource)
finally:
    release(resource)
```

or create/use a context manager when the lifecycle is reusable.

---

## Mistake 2: Not using `finally` in a generator-based manager

### Incorrect

```python
from contextlib import contextmanager


@contextmanager
def unsafe_resource():
    resource = acquire()
    yield resource
    release(resource)
```

### Why it fails

If the managed block raises, control may not reach the plain `release()` line.

### Better

```python
from contextlib import contextmanager


@contextmanager
def safe_resource():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)
```

---

## Mistake 3: Accidentally suppressing exceptions

### Incorrect

```python
def __exit__(self, exc_type, exc_value, traceback):
    cleanup()
    return True
```

### Why it happens

The developer believes `True` means "cleanup succeeded."

It does not.

### Correct approach

Return a truthy value only when suppression is an intentional part of the context-manager contract.

```python
def __exit__(self, exc_type, exc_value, traceback):
    cleanup()
    return False
```

---

## Mistake 4: Returning the wrong object from `__enter__()`

### Symptom

The variable after `as` behaves differently than expected.

### Example

```python
class Example:
    def __enter__(self):
        return "not the manager"

    def __exit__(self, exc_type, exc_value, traceback):
        return False


with Example() as resource:
    resource.do_something()
```

This fails because `resource` is a string.

### Lesson

Remember:

```text
as-variable = __enter__() return value
```

---

## Mistake 5: Not initializing state

### Problem

`__exit__()` expects:

```python
self.resource
```

but acquisition failed before that attribute existed.

### Better

Initialize lifecycle state in `__init__()`:

```python
class Example:
    def __init__(self):
        self.resource = None
```

Then make cleanup tolerant of the actual lifecycle state.

---

## Mistake 6: Acquiring outside the context boundary

### Problem

```python
resource = acquire()

with ResourceManager(resource):
    use(resource)
```

The manager might only control cleanup, while acquisition has already happened elsewhere.

That can be valid, but it changes ownership.

### Better question

Ask:

> Who owns acquisition and who owns release?

If the context manager is intended to own the complete lifecycle, acquisition should normally belong near `__enter__()`.

---

## Mistake 7: Too much business logic in `__enter__()` / `__exit__()`

A context manager should not become a dumping ground.

Bad smell:

```python
def __enter__(self):
    validate_tenant()
    calculate_pricing()
    write_audit_event()
    load_configuration()
    ...
```

Some of those operations may be legitimate lifecycle actions, but once the context manager becomes responsible for unrelated business rules, the abstraction becomes hard to reason about.

### Better

Keep the lifecycle behavior small and explicit.

---

## Mistake 8: Yielding multiple times incorrectly with `@contextmanager`

A generator-based context manager describes one enter/exit boundary.

This is the shape you normally want:

```python
@contextmanager
def managed():
    acquire()
    try:
        yield value
    finally:
        release()
```

Multiple independent yields do not mean "run the context multiple times." They change the generator protocol and can cause `RuntimeError` because the contextmanager machinery expects the generator to provide one boundary value and then finish appropriately.

---

## Mistake 9: Assuming cleanup can never fail

Cleanup is code.

Code can fail.

For example:

```python
def __exit__(self, exc_type, exc_value, traceback):
    self.resource.close()
    return False
```

If `close()` itself raises, the exit operation can fail.

This is why cleanup should be:

- small;
- reliable;
- carefully tested;
- observable when failures matter.

---

## Mistake 10: Hiding important business behavior

This is a maintainability failure.

If a business operation only looks like:

```python
with operation_policy():
    do_work()
```

but `operation_policy()` secretly performs major mutations, retries, state transitions, and external calls, the code becomes difficult to read.

A context manager should make a lifecycle **clearer**, not create hidden control flow.

---

# 38. Cleanup Failure

Cleanup deserves its own design attention.

Suppose:

```python
try:
    do_work()
finally:
    cleanup()
```

and `cleanup()` raises.

Then the cleanup exception can affect what the caller ultimately sees.

A context manager has the same fundamental issue.

## Why this matters

Imagine:

```text
original operation fails
        ↓
cleanup starts
        ↓
cleanup also fails
```

Now there are two failures to reason about.

A careless context manager can make diagnosis harder because the cleanup failure may become the exception that escapes the boundary.

### Production guidance

Keep cleanup:

- small;
- deterministic where possible;
- independently testable;
- observable when failures matter;
- safe to call repeatedly when the resource's semantics allow it.

### Idempotency

Some cleanup operations are safer when repeated:

```python
resource.close()
resource.close()
```

may be harmless for one resource type.

That does **not** mean every cleanup operation is automatically idempotent.

For your own context manager, define and test the expected lifecycle rather than assuming a second cleanup is safe.

---

# 39. Context-Manager Design Principles

Use these rules as engineering heuristics.

## 1. Keep the managed boundary obvious

Prefer:

```python
with resource() as r:
    process(r)
```

over an abstraction whose ownership rules are invisible.

## 2. Keep `__enter__()` focused

Typical responsibilities:

- acquire;
- initialize;
- return the value used by the block.

## 3. Keep `__exit__()` focused

Typical responsibilities:

- release;
- restore;
- commit/rollback-like lifecycle action;
- intentionally suppress selected exceptions only when that is part of the contract.

## 4. Do not silently suppress exceptions

A failure that should be visible must remain visible.

## 5. Use `finally` for generator-based cleanup

The standard pattern is:

```python
try:
    yield resource
finally:
    release(resource)
```

## 6. Keep context managers small

A context manager should ideally describe one coherent lifecycle.

## 7. Avoid hidden business logic

The resource boundary should not hide major domain behavior.

## 8. Document lifecycle assumptions

State clearly when the manager:

- acquires;
- releases;
- owns;
- does not own;
- can be reused;
- suppresses exceptions.

## 9. Test both success and failure paths

A resource manager that only works when everything goes right is not production-safe.

## 10. Consider simpler code first

A small `try/finally` can be more understandable than a custom context manager used once.

---

# 40. When NOT to Use a Context Manager

Context managers are not automatically "better Python."

Use one when there is a meaningful lifecycle:

```text
enter/setup
    ↓
work
    ↓
exit/cleanup
```

### Good fit

```python
with open(path, "r", encoding="utf-8") as file:
    process(file)
```

### Potentially unnecessary

Suppose you only need:

```python
value = normalize(value)
```

Turning that into:

```python
with normalization_context():
    value = ...
```

would not automatically improve the design.

## Avoid a context manager when

- there is no meaningful resource or lifecycle boundary;
- a simple function communicates the operation better;
- the context hides critical business logic;
- the abstraction creates surprising side effects;
- setup/cleanup is trivial and explicit code is clearer.

### Engineering principle

> **Use the simplest abstraction that correctly manages the lifecycle.**

"Correctly" matters. The goal is not the fewest lines. The goal is a clear and safe design.

---

# 41. Production Use Cases

Context managers appear throughout real Python systems.

## File handling

```python
with open(path, "r", encoding="utf-8") as file:
    process(file)
```

**Problem solved:** file lifecycle.

**Trade-off:** very little; this is a canonical use.

---

## Temporary files and directories

The standard library provides temporary-resource context managers.

```python
from tempfile import TemporaryDirectory


with TemporaryDirectory() as directory:
    print("temporary directory:", directory)
```

The directory has a clear lifetime.

**Trade-off:** the contents are temporary; code must not assume the path continues to exist after the context ends.

---

## Locks

```python
with lock:
    update_shared_state()
```

**Problem solved:** ensure release on exit.

**Trade-off:** the context does not solve broader concurrency design problems.

---

## Transaction-like boundaries

```python
with transaction():
    perform_operations()
```

**Problem solved:** make the commit/rollback boundary explicit.

**Trade-off:** the underlying transaction system still determines the real semantics.

---

## Temporary configuration

```python
with temporary_mode("debug"):
    run_operation()
```

**Problem solved:** restore state reliably.

**Trade-off:** hidden global state can still be difficult to reason about, especially in concurrent code.

---

## Timing and instrumentation

```python
with Timer("stage"):
    run_stage()
```

**Problem solved:** define a measurement boundary.

**Trade-off:** timing instrumentation itself can affect the shape of code and should not be mistaken for rigorous benchmarking.

---

## Output redirection

The standard library contains context managers such as:

```python
from contextlib import redirect_stdout
```

which can temporarily route output.

The important lifecycle lesson is not the specific utility:

```text
save/replace state
     ↓
run operation
     ↓
restore state
```

---

## Testing and temporary resources

Tests frequently need short-lived:

- files;
- directories;
- locks;
- temporary state.

A context manager can make setup and teardown visible around the exact code under test.

---

# 42. Applied AI Engineering Connection

Context managers are a general Python mechanism that can support AI engineering systems. They do not create an AI system by themselves.

Useful future examples include:

### Temporary files during document processing

```text
create temporary artifact
        ↓
process document
        ↓
cleanup artifact
```

### Temporary directories in dataset transformations

A pipeline may materialize intermediate artifacts in a temporary directory and remove them afterward.

### Evaluation pipeline resource cleanup

An evaluation stage may temporarily open resources, create files, or acquire synchronization primitives.

### Timing a processing stage

```python
with Timer("evaluation stage"):
    run_evaluation()
```

This gives a clear measurement boundary.

### Locks around shared state

If multiple workers eventually share application state, a lock context can make ownership explicit.

### Temporary configuration

Some processing operations may need temporary settings that must be restored even when processing fails.

### External-tool lifecycle

A future AI engineering system might launch a local process or acquire a resource used by a tool. A context manager can make its lifetime explicit.

The key principle remains:

> **Context managers are lifecycle infrastructure. They help AI systems manage resources safely; they are not themselves an AI architecture.**

---

# 43. Debugging Context Managers

When a context manager misbehaves, debug the lifecycle before debugging the business logic.

## Problem: `__enter__()` fails

### Symptom

The block never runs.

### Debugging strategy

Add an explicit entry trace:

```python
class DebugContext:
    def __enter__(self):
        print("ENTER: starting acquisition")
        self.resource = acquire()
        print("ENTER: acquired")
        return self.resource

    def __exit__(self, exc_type, exc_value, traceback):
        print("EXIT")
        release(self.resource)
        return False
```

If you see:

```text
ENTER: starting acquisition
```

but never:

```text
ENTER: acquired
```

the acquisition path failed.

Remember that a failed `__enter__()` means the body was never entered.

---

## Problem: `__exit__()` is never observed

Ask:

1. Did `__enter__()` succeed?
2. Is the correct object actually being used as the context manager?
3. Is the code reaching the `with` statement?
4. Did the program terminate outside normal Python unwinding?

Add lifecycle traces.

---

## Problem: exception disappeared

Inspect the return value:

```python
def __exit__(self, exc_type, exc_value, traceback):
    print("suppressing:", exc_type is not None)
    return True
```

If `True` is being returned unintentionally, you found the cause.

---

## Problem: cleanup happens too early

Check the scope:

```python
with Resource() as resource:
    do_first(resource)

do_second(resource)
```

The resource's managed lifetime ended before `do_second()`.

The fix may simply be to move `do_second()` into the context.

---

## Problem: `as` contains the wrong value

Print the value returned from `__enter__()`:

```python
class Example:
    def __enter__(self):
        value = create_value()
        print("returning:", value)
        return value

    def __exit__(self, exc_type, exc_value, traceback):
        return False
```

Remember:

```text
as-variable = __enter__() result
```

---

## Problem: nested cleanup order surprises you

Use labeled managers:

```python
class TraceContext:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print("enter", self.name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("exit", self.name)
        return False
```

Then:

```python
with TraceContext("A"), TraceContext("B"):
    print("work")
```

The output makes the lifecycle order obvious.

### Debugging habit

When a context manager is confusing, temporarily make the lifecycle visible:

```text
ENTER
BODY
EXIT
```

Then add exception details:

```text
ENTER
BODY
EXIT: exception=ValueError(...)
```

Small, targeted traces are usually more useful than adding logs everywhere.

---

# 44. Testing Context Managers

Testing should focus on the **contract**, not merely implementation details.

The important scenarios are:

1. normal execution;
2. exception execution;
3. intentional suppression;
4. `__enter__()` return value;
5. nested contexts;
6. cleanup failure.

## Test normal acquisition and release

Using plain assertions:

```python
class TrackingResource:
    def __init__(self):
        self.entered = False
        self.exited = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.exited = True
        return False


resource = TrackingResource()

with resource as active:
    assert active is resource
    assert resource.entered is True
    assert resource.exited is False

assert resource.exited is True
```

The test checks lifecycle behavior visible to a caller.

---

## Test exception-path cleanup

```python
class TrackingResource:
    def __init__(self):
        self.exited = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.exited = True
        return False


resource = TrackingResource()

try:
    with resource:
        raise ValueError("expected failure")
except ValueError:
    pass

assert resource.exited is True
```

The important assertion is that cleanup still happened.

---

## Test suppression explicitly

If suppression is intentionally part of the contract:

```python
class ExpectedFailureContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return exc_type is ValueError


with ExpectedFailureContext():
    raise ValueError("expected")
```

Then test that another exception still propagates:

```python
try:
    with ExpectedFailureContext():
        raise TypeError("not suppressible")
except TypeError:
    pass
else:
    raise AssertionError("TypeError should propagate")
```

### Production testing principle

Test the **policy**:

> Which failures are supposed to propagate and which, if any, are intentionally suppressed?

---

## Test the `as` value

```python
class ValueContext:
    def __enter__(self):
        return {"status": "ready"}

    def __exit__(self, exc_type, exc_value, traceback):
        return False


with ValueContext() as value:
    assert value == {"status": "ready"}
```

This verifies the public contract of `__enter__()`.

---

## Pytest-style equivalent

If a project uses pytest, the intent can be expressed compactly:

```python
def test_context_manager_releases_on_failure():
    resource = TrackingResource()

    with pytest.raises(ValueError):
        with resource:
            raise ValueError("failure")

    assert resource.exited is True
```

The important testing principle is independent of the testing framework: assert the externally meaningful lifecycle behavior.

---

## Avoid over-testing

Do not write tests that depend unnecessarily on:

- exact private implementation steps;
- CPython-specific internals;
- incidental local variable names.

Prefer tests such as:

```text
resource acquired
resource released
exception propagated
expected exception suppressed
```

rather than:

```text
__exit__ happened to be called from this particular helper method
```

---

# 45. Complete Class-Based Example — Safe File Writer

Here is a small cohesive example that demonstrates:

- constructor state;
- `__enter__()`;
- `__exit__()`;
- resource acquisition;
- cleanup;
- exception behavior;
- logging;
- type hints;
- testable state.

```python
import logging
from typing import TextIO


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafeFileWriter:
    def __init__(self, path: str):
        self.path = path
        self._file: TextIO | None = None
        self.lines_written = 0

    def __enter__(self) -> "SafeFileWriter":
        logger.info("Opening %s", self.path)
        self._file = open(self.path, "w", encoding="utf-8")
        return self

    def write_line(self, text: str) -> None:
        if self._file is None:
            raise RuntimeError("File is not open")

        self._file.write(text + "\n")
        self.lines_written += 1

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if self._file is not None:
            logger.info(
                "Closing %s after %d lines",
                self.path,
                self.lines_written,
            )
            self._file.close()
            self._file = None

        return False


with SafeFileWriter("output.txt") as writer:
    writer.write_line("first")
    writer.write_line("second")

print("lines:", writer.lines_written)
```

## Architecture of the example

```text
SafeFileWriter(path)
       │
       ├── __enter__
       │      └── acquire file
       │
       ├── write_line
       │      └── business/use operation
       │
       └── __exit__
              └── close file
```

### Why `__enter__()` returns `self`

The caller needs the writer API:

```python
with SafeFileWriter("output.txt") as writer:
    writer.write_line("hello")
```

Returning `self` makes that interface natural.

### Why return `False` from `__exit__()`?

The writer's responsibility is cleanup.

It should not silently claim that an unrelated application exception was handled.

### Why set `_file = None` after close?

This makes the object's post-exit state explicit and reduces the chance that later methods accidentally use a closed handle.

### Production note

This example is intentionally educational. For ordinary file writing, prefer:

```python
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("first\n")
```

Custom classes become valuable when they add meaningful domain behavior around the resource.

---

# 46. Complete `@contextmanager` Example

Now express a similar lifecycle using `contextlib`.

```python
from contextlib import contextmanager
from typing import Iterator, TextIO


@contextmanager
def managed_text_file(path: str) -> Iterator[TextIO]:
    file = open(path, "r", encoding="utf-8")
    try:
        yield file
    finally:
        file.close()


with managed_text_file("input.txt") as file:
    for line in file:
        print(line.rstrip())
```

## Lifecycle

```text
call managed_text_file(path)
          ↓
open file
          ↓
yield file
          ↓
with block executes
          ↓
resume generator
          ↓
finally
          ↓
close file
```

## Exception case

```python
try:
    with managed_text_file("input.txt") as file:
        raise RuntimeError("processing failed")
except RuntimeError as exc:
    print("caller saw:", exc)
```

The `finally` block closes the file before the exception continues outward.

### Why this style is concise

The generator naturally expresses:

```text
setup
yield control
cleanup
```

That is a very good fit for a simple lifecycle with one central resource.

---

# 47. Class-Based vs `@contextmanager`

Neither style is universally superior.

| Aspect | Class-based | `@contextmanager` |
|---|---|---|
| Amount of code | Usually more explicit | Usually less code |
| Lifecycle methods | Explicit `__enter__` / `__exit__` | Expressed around `yield` |
| State handling | Natural for rich state | Good for simple state |
| Readability | Often clearer for complex lifecycles | Often clearer for simple setup/cleanup |
| Complex conditional exit behavior | Flexible | Possible, but can become harder to read |
| Reusing a context-manager class | Possible when designed for it | Each function call creates a fresh lifecycle |
| Teaching lifecycle protocol | Excellent | Excellent after protocol is understood |
| Best fit | Complex or stateful managers | Small cohesive setup/cleanup boundaries |

## Decision criteria

Choose a class when:

- the context manager owns substantial state;
- lifecycle methods have complex logic;
- the object has a meaningful identity during the context;
- class methods make the contract clearer.

Choose `@contextmanager` when:

- the lifecycle is compact;
- setup happens before one `yield`;
- cleanup happens after the `yield`, usually in `finally`;
- a generator makes the code easier to understand than a class.

### A useful engineering rule

> **Choose the form that makes the lifecycle easiest for the next engineer to understand and test.**

---

# 48. Practical Mini-Project — Safe File Processing Context

## Project name

**Safe File Processing Context**

## Goal

Build a small utility that demonstrates the complete resource-management lifecycle.

The project should not become a large application.

Its purpose is to reinforce this chapter:

```text
resource
   ↓
context boundary
   ↓
processing
   ↓
cleanup
```

## Requirements

Your implementation should:

1. open an input file safely;
2. provide a managed file object to the caller;
3. track simple processing statistics;
4. ensure cleanup on success;
5. ensure cleanup when processing fails;
6. include a timing context manager;
7. use `@contextmanager` for at least one component;
8. test normal execution;
9. test exception execution;
10. document lifecycle behavior.

## Suggested design

A small project could contain:

```text
safe_file_processing.py
```

with conceptual components:

```text
SafeFileProcessor
    │
    ├── managed file lifecycle
    ├── line statistics
    └── error-safe cleanup

Timer
    └── processing duration

@contextmanager
    └── one simple temporary lifecycle
```

### Suggested processing flow

```text
open input
   ↓
enter context
   ↓
read lines
   ↓
update statistics
   ↓
exit context
   ↓
close resource
```

### Example expected behavior

Given:

```text
INFO first
ERROR bad input
INFO second
ERROR another issue
```

the processor might report:

```text
lines_processed = 4
error_lines = 2
```

The exact statistics are yours to define.

## Test scenarios

At minimum:

### Normal path

- file opens;
- lines are processed;
- statistics are correct;
- cleanup occurs.

### Failure path

Force an exception during processing and verify:

- the exception reaches the caller;
- the file is still closed;
- state is left consistent.

### Empty file

Expect zero processed lines.

### Missing file

The context should fail clearly during acquisition rather than pretending a resource exists.

## Extension challenges

After the basic version works:

- add a temporary directory context;
- record processing duration;
- create a context manager that temporarily changes a configuration value;
- dynamically manage several input files with `ExitStack`;
- document which component owns each resource.

Do not add a framework or database. The purpose is to master the lifecycle abstraction.

---

# 49. Progressive Coding Exercises

Do these in order. Avoid looking for a complete solution immediately; the goal is to force the lifecycle model into your own reasoning.

## Level 1 — Basic

### Exercise 1: Use `with open()`

Take:

```python
file = open("data.txt", "r", encoding="utf-8")
try:
    data = file.read()
finally:
    file.close()
```

Rewrite it using `with`.

Then explain, in your own words, what lifecycle the `with` statement represents.

### Exercise 2: Explain `as`

Write a custom context manager whose `__enter__()` returns a dictionary:

```python
{"status": "ready"}
```

Use the value after `as` and print it.

---

## Level 2 — Protocol

### Exercise 3: First custom context manager

Implement:

```python
class MessageContext:
    ...
```

Requirements:

- print `"ENTER"` during entry;
- print `"EXIT"` during exit;
- return `self`.

Use it with:

```python
with MessageContext():
    print("WORK")
```

### Exercise 4: Inspect exceptions

Modify the context manager so `__exit__()` prints:

- exception type;
- exception value.

Run it once without an exception and once with a `ValueError`.

---

## Level 3 — Resource management

### Exercise 5: Safe file writer

Create a class-based context manager that opens a text file for writing and closes it on exit.

Test:

- normal writing;
- exception during writing;
- empty content.

### Exercise 6: Temporary state manager

Create a context manager that temporarily changes:

```python
settings["mode"]
```

and restores the previous value afterward.

Test nested use.

### Exercise 7: Timer

Implement:

```python
with Timer("operation"):
    ...
```

using `time.perf_counter()`.

Print the elapsed duration.

---

## Level 4 — `contextlib`

### Exercise 8: Convert to `@contextmanager`

Rewrite your safe file writer as a generator-based context manager.

Requirements:

- acquire before `yield`;
- `yield` the resource;
- clean up in `finally`.

### Exercise 9: `nullcontext`

Design a function that accepts either:

- an existing file object; or
- a path.

Use `nullcontext` so both cases share one `with` structure.

### Exercise 10: `closing`

Create a small object that only has:

```python
close()
```

and adapt it using `closing`.

---

## Level 5 — Advanced

### Exercise 11: Multiple contexts

Create two custom context managers that record their entry and exit order.

Use:

```python
with A(), B():
    ...
```

Predict the output before running it.

### Exercise 12: `ExitStack`

Given a runtime list of file paths, open all readable files using `ExitStack`.

Requirements:

- no deeply nested `with`;
- all successfully opened files are cleaned up;
- a failure during later acquisition does not leak earlier resources.

### Exercise 13: Suppression

Write a context manager that suppresses only `ValueError`.

Verify that `TypeError` still propagates.

---

## Level 6 — Production reasoning

### Exercise 14: Design review

A teammate proposes:

```python
class EverythingContext:
    def __enter__(self):
        load_config()
        authenticate()
        start_transaction()
        create_temp_files()
        log_event()
        return self

    def __exit__(self, *args):
        save_metrics()
        cleanup_temp_files()
        commit_or_rollback()
        send_notifications()
```

Write a review explaining:

- which responsibilities belong to lifecycle management;
- which may be unrelated business concerns;
- what failure modes you would investigate;
- whether the abstraction remains understandable.

### Exercise 15: Debug an intentionally broken manager

Create a manager containing at least three bugs:

- wrong `__enter__()` return value;
- accidental exception suppression;
- missing cleanup on failure.

Write tests that expose all three.

### Exercise 16: Architecture question

You need to manage:

```text
5 optional resources
```

whose existence depends on runtime configuration.

Explain when you would choose:

```text
nested with
ExitStack
```

and what makes one design easier to maintain.

---

# 50. Knowledge Check

Use these questions as checkpoints. Try answering without looking back at the chapter.

## Basic

### 1. What is a resource?

Explain it as a lifecycle-managed object or external capacity used by a program.

### 2. Why does resource cleanup matter?

Your answer should mention that resources other than memory can be exhausted or left in unsafe states.

### 3. What does `with` do?

Expected reasoning:

> It establishes a context boundary that enters a context before the block and exits it afterward.

### 4. What is a context manager?

Expected reasoning:

> An object that controls enter/exit behavior around a managed block.

### 5. What does `as` mean?

Expected reasoning:

> The name after `as` receives the return value of `__enter__()`.

---

## Intermediate

### 6. What are `__enter__()` and `__exit__()`?

Explain their roles separately rather than saying "they open and close things."

### 7. What arguments does `__exit__()` receive?

Explain:

```text
exc_type
exc_value
traceback
```

and how they differ between normal and exceptional completion.

### 8. Why is `finally` important?

Explain why cleanup should not depend only on successful execution.

### 9. What happens when an exception occurs inside a `with` block?

Explain:

```text
exception occurs
        ↓
__exit__ receives exception information
        ↓
cleanup/policy runs
        ↓
exception propagates unless intentionally suppressed
```

### 10. What does returning `True` from `__exit__()` mean?

It signals that the exception should be suppressed.

It does not mean cleanup succeeded.

---

## Advanced

### 11. Explain the context-manager protocol.

Describe:

```text
__enter__()
__exit__()
```

and their lifecycle relationship.

### 12. Compare class-based and generator-based context managers.

Discuss:

- state;
- readability;
- lifecycle complexity;
- testability;
- maintainability.

### 13. Explain `@contextmanager`.

Explain how the decorator turns a generator-style function into a context manager around a single `yield` boundary.

### 14. Why is `try/finally` important around `yield`?

Because cleanup needs to happen whether the body succeeds or raises.

### 15. Why can exception suppression be dangerous?

Because it can convert a real failure into apparently successful execution.

### 16. How does `ExitStack` help?

It lets code compose and clean up context managers dynamically while retaining stack-like reverse cleanup.

### 17. What happens if cleanup itself fails?

Explain that cleanup is ordinary code and can raise, potentially complicating or changing the final exception observed by the caller.

### 18. When should a context manager not be used?

When there is no meaningful lifecycle boundary or when explicit simpler code communicates intent better.

### 19. How would you test a context manager?

At minimum:

```text
normal path
failure path
cleanup
suppression policy if applicable
as-value contract
```

### 20. How would you design a production-safe resource manager?

Strong reasoning should mention:

- ownership;
- lifecycle boundaries;
- cleanup;
- failure behavior;
- exception propagation;
- observability;
- testability;
- documentation;
- simple scope.

---

# 51. Interview Questions

These are not memorization questions. A strong answer should explain the mechanism and the engineering trade-offs.

## 1. What is a context manager in Python?

**Expected reasoning direction:** Define the lifecycle abstraction, then connect it to the `with` statement and cleanup.

---

## 2. Why do we use the `with` statement?

**Expected reasoning direction:** Explain resource/state boundaries and why explicit lifecycle management is safer and clearer.

---

## 3. Explain `__enter__()` and `__exit__()`.

**Expected reasoning direction:** `__enter__()` establishes/acquires and provides the `as` value; `__exit__()` handles exit/cleanup and can intentionally suppress exceptions.

---

## 4. How does Python conceptually execute a `with` statement?

**Expected reasoning direction:**

```text
create/get manager
      ↓
__enter__()
      ↓
bind "as" value
      ↓
run block
      ↓
__exit__()
      ↓
propagate or suppress exception
```

Also mention that this is a conceptual model, not literal source-code rewriting.

---

## 5. What does `as` receive?

**Expected reasoning direction:** Whatever `__enter__()` returns.

---

## 6. What happens if an exception occurs inside the block?

**Expected reasoning direction:** `__exit__()` receives exception information; cleanup can happen; a truthy return suppresses the exception, otherwise it propagates.

---

## 7. What does returning `True` from `__exit__()` do?

**Expected reasoning direction:** It suppresses the active exception. It is not a cleanup-success flag.

---

## 8. Why should exceptions generally not be silently suppressed?

**Expected reasoning direction:** Hidden failures can produce incorrect results, hide operational incidents, and complicate debugging.

---

## 9. How do you create a custom context manager?

**Expected reasoning direction:** Either define `__enter__()` and `__exit__()` on a class or use `contextlib.contextmanager` for a generator-based implementation.

---

## 10. How does `@contextmanager` work?

**Expected reasoning direction:** The decorated generator represents a single enter/use/exit lifecycle separated by `yield`.

---

## 11. Why is `try/finally` important with `@contextmanager`?

**Expected reasoning direction:** Cleanup must be attached to the lifecycle even if the managed body raises.

---

## 12. What is `nullcontext`?

**Expected reasoning direction:** A no-op context that can provide a uniform `with` structure without adding resource ownership/cleanup.

---

## 13. What is `ExitStack`?

**Expected reasoning direction:** A dynamic context stack that registers cleanup and exits resources in reverse order.

---

## 14. How would you manage multiple resources safely?

**Expected reasoning direction:** Use multiple `with` managers for fixed resources; use `ExitStack` when acquisition is dynamic or conditional.

---

## 15. How would you debug a context manager that does not clean up?

**Expected reasoning direction:**

```text
check __enter__
check __exit__
trace entry/exit
test exception path
inspect ownership
test cleanup failure
```

---

## 16. How would you test failure-path cleanup?

**Expected reasoning direction:** Deliberately raise an exception inside the block and assert that cleanup state is still correct.

---

## 17. When would you choose a class-based context manager?

**Expected reasoning direction:** Complex state, richer lifecycle logic, explicit identity, or when the class makes the contract easier to understand.

---

## 18. When would you choose `@contextmanager`?

**Expected reasoning direction:** Small, cohesive setup/cleanup around one `yield`.

---

## 19. Give a real production use case.

Good examples include:

- file lifecycle;
- lock acquisition;
- temporary directory;
- transaction boundary;
- temporary state;
- timing/instrumentation.

The answer should explain **why** the lifecycle fits the abstraction.

---

## 20. Explain the difference between cleanup and exception suppression.

**Expected reasoning direction:**

```text
cleanup = restore/release resource
suppression = decide whether exception propagates
```

They can occur together, but they are different responsibilities.

---

## 21. What happens if `__enter__()` fails?

**Expected reasoning direction:** The body is not entered, and that manager's normal `__exit__()` path is not executed. Acquisition code must account for partial setup if relevant.

---

## 22. Why is reverse-order cleanup important?

**Expected reasoning direction:** Later-acquired resources may depend on earlier ones, so releasing in reverse order reduces dependency problems.

---

## 23. How would you explain context managers to a junior engineer?

A strong answer should begin with:

```text
resource lifecycle:
acquire → use → release
```

then explain that `with` turns that lifecycle into an explicit code boundary.

---

# 52. Final Mental Model

Everything in this chapter can be compressed into one lifecycle:

```text
Resource lifecycle
       ↓
     Acquire
       ↓
   Enter context
       ↓
    Use resource
       ↓
    Exit context
       ↓
     Cleanup
```

The `with` statement expresses that boundary:

```text
with manager as value:
        ↓
   __enter__()
        ↓
value gets __enter__ result
        ↓
     run block
        ↓
    __exit__()
        ↓
cleanup + exception policy
```

There are two primary implementation styles.

## Class-based

```text
class Manager:
    __enter__()
    __exit__()
```

Use when the manager benefits from explicit object state and lifecycle methods.

## Generator-based

```text
@contextmanager
def manager():
    acquire
    try:
        yield resource
    finally:
        cleanup
```

Use when one compact setup/use/cleanup lifecycle is clearer.

## Exception model

```text
body succeeds
     ↓
__exit__(None, None, None)
     ↓
cleanup
```

or:

```text
body raises
     ↓
__exit__(exc_type, exc_value, traceback)
     ↓
cleanup
     ↓
False/None → exception propagates
True       → exception suppressed
```

### The production principle

> **A good context manager makes resource lifetime explicit, safe, predictable, and difficult to misuse.**

The deeper engineering lesson is even broader:

> **Resource-management code should make ownership and lifetime obvious.**

When a resource can be processed incrementally inside a meaningful boundary, a context manager can make that ownership easy to see.

When there is no meaningful lifecycle, do not create a context manager just because Python allows it.

Use the abstraction when it improves clarity, correctness, and maintainability.

---

# Quick Reference

## Core protocol

```python
class MyContext:
    def __enter__(self):
        # acquire/setup
        return value

    def __exit__(self, exc_type, exc_value, traceback):
        # cleanup
        return False
```

## Basic usage

```python
with MyContext() as value:
    use(value)
```

## Generator-based form

```python
from contextlib import contextmanager


@contextmanager
def my_context():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)
```

## Optional context

```python
from contextlib import nullcontext
```

## Adapt `.close()`

```python
from contextlib import closing
```

## Dynamic resources

```python
from contextlib import ExitStack
```

## Core rules to remember

```text
1. Understand ownership.
2. Make the lifecycle boundary visible.
3. Acquire/setup in the entry phase.
4. Clean up in the exit phase.
5. Use finally for generator-based cleanup.
6. Do not suppress exceptions accidentally.
7. Test both success and failure.
8. Do not assume every context manager instance is reusable.
9. Prefer native context-manager support when it already exists.
10. Use the simplest abstraction that safely manages the lifecycle.
```

---

# Self-Check Checklist

Before considering this topic complete, you should be able to explain each of these without copying the definitions:

- [ ] resource and resource lifecycle;
- [ ] why manual cleanup can fail;
- [ ] `try/finally`;
- [ ] `with`;
- [ ] `as`;
- [ ] context manager;
- [ ] `__enter__()`;
- [ ] `__exit__()`;
- [ ] exception information;
- [ ] exception suppression;
- [ ] cleanup vs suppression;
- [ ] nested contexts;
- [ ] multiple contexts;
- [ ] file handling;
- [ ] lock lifecycle;
- [ ] transaction-like boundary;
- [ ] temporary state;
- [ ] timing context;
- [ ] `contextlib.contextmanager`;
- [ ] `yield` in a context manager;
- [ ] `try/finally` around `yield`;
- [ ] `nullcontext`;
- [ ] `closing`;
- [ ] `ExitStack`;
- [ ] reusable vs one-lifecycle managers;
- [ ] stateful context managers;
- [ ] relationship to decorators;
- [ ] relationship to generators;
- [ ] cleanup failures;
- [ ] debugging;
- [ ] testing;
- [ ] production trade-offs;
- [ ] when not to use a context manager.

If you can explain those ideas and build a small context manager without memorizing a template, the foundation is solid.
