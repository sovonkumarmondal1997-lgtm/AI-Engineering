# Decorators

> **Stage 1 — Programming and Computational Thinking**  
> **Module 1.9 — Advanced Production-Oriented Python Foundations**

This chapter teaches Python decorators from first principles. The goal is not to memorize `@something` syntax. The goal is to understand the chain of ideas that makes decorators possible:

```text
Python functions are objects
        ↓
functions can be assigned to names
        ↓
functions can be passed as arguments
        ↓
functions can be returned from functions
        ↓
nested functions + closures
        ↓
higher-order functions
        ↓
decorator problem
        ↓
manual decorator
        ↓
@decorator syntax
        ↓
wrappers
        ↓
arguments + return values
        ↓
functools.wraps
        ↓
reusable production patterns
        ↓
engineering judgment
```

By the end, you should be able to read unfamiliar decorator-heavy Python code, write small decorators safely, test them, debug them, and decide when a decorator improves the design and when it hides too much behavior.

---

# 1. Introduction — What Is a Decorator?

## 1.1 Start with the problem, not the syntax

Suppose an application has many functions:

```python
def create_user():
    ...

def delete_user():
    ...

def update_user():
    ...
```

Imagine that all three functions need some additional behavior:

- record that the function started,
- record that it completed,
- validate a precondition,
- measure duration,
- check an application policy,
- or retry a small category of transient failures.

A beginner may copy that code into every function:

```python
def create_user():
    print("Starting")
    # real work
    print("Finished")


def delete_user():
    print("Starting")
    # real work
    print("Finished")
```

The problem is not that this code is impossible to understand. The problem is duplication. If the cross-cutting behavior changes, many functions must be edited.

A decorator gives us another design option: keep the core function focused on its main job and apply a reusable wrapper around it.

### Analogy

Think of a package that already contains a product. You can put a protective outer layer around the package without opening the package and rewriting the product.

That is only an analogy. A Python decorator does not physically wrap memory or create a magical package. At the language level, a decorator receives a callable and typically returns another callable.

## 1.2 Technical definition

A **decorator** is a callable that accepts another callable and returns a callable, commonly to modify or extend the behavior observed when the decorated callable is used.

For a simple function decorator:

```text
decorator(function) -> wrapper
```

The returned object may be:

- a nested wrapper function,
- another function,
- a callable object,
- or, in more advanced designs, another appropriate callable.

Decorators are possible because Python functions are objects that can be assigned, passed around, and returned.

---

# 2. Prerequisite — Functions Are Objects

Before learning decorators, establish the foundation.

## 2.1 Defining a function creates a function object

```python
def greet():
    print("Hello")
```

The name `greet` refers to a function object.

```python
print(greet)
```

Typical output:

```text
<function greet at 0x...>
```

The exact memory-related display is implementation-dependent and should not be relied on.

The important point is:

```text
greet
  ↓
function object
```

`greet` is a reference to that object.

## 2.2 Assigning a function to another name

```python
def greet():
    print("Hello")


another_name = greet

another_name()
```

Output:

```text
Hello
```

Both names refer to the same function object.

```python
print(greet is another_name)
```

Output:

```text
True
```

There was no copy of the function. We simply created another reference to the same object.

### Important distinction

These two expressions mean very different things:

```python
greet
```

and:

```python
greet()
```

The first refers to the function object.

The second **calls** the function.

That distinction is essential for decorators.

If you write:

```python
run_function(greet)
```

you are passing the function itself.

If you write:

```python
run_function(greet())
```

you are calling `greet` first and passing its return value.

---

# 3. Passing Functions as Arguments

Python permits a function to be passed to another function.

## 3.1 Simple example

```python
def greet():
    print("Hello")


def run_function(function):
    function()


run_function(greet)
```

Output:

```text
Hello
```

The parameter `function` refers to the same function object that was passed in.

Conceptually:

```text
greet
  ↓
function parameter
  ↓
function()
  ↓
execute greet
```

## 3.2 Why this matters

Consider:

```python
def add_one(value):
    return value + 1


def square(value):
    return value * value


def execute(operation, value):
    return operation(value)


print(execute(add_one, 5))
print(execute(square, 5))
```

Output:

```text
6
25
```

`execute` does not need to know the implementation of every possible operation. It receives a callable and invokes it.

This is called **higher-order behavior**.

## 3.3 Common beginner mistake

Incorrect:

```python
execute(square(5), 10)
```

That evaluates `square(5)` immediately and passes `25`, not the function.

Correct:

```python
execute(square, 10)
```

Here `square` is passed as an object.

---

# 4. Returning Functions

The other half of the decorator mechanism is returning a function.

## 4.1 A function can create another function

```python
def create_greeting():
    def greet():
        print("Hello")

    return greet
```

Now:

```python
greeting = create_greeting()
greeting()
```

Output:

```text
Hello
```

The outer function returned the inner function object.

Conceptually:

```text
create_greeting()
      ↓
inner function object
      ↓
greeting
```

## 4.2 What happens when `create_greeting()` is called?

Step 1:

```python
create_greeting()
```

The outer function starts executing.

Step 2:

```python
def greet():
    print("Hello")
```

The inner function is created.

Step 3:

```python
return greet
```

The function object is returned.

Step 4:

```python
greeting = ...
```

The `greeting` name now refers to the returned function.

Step 5:

```python
greeting()
```

calls that returned function.

This pattern is the skeleton of many decorators.

---

# 5. Nested Functions

A function defined inside another function is a **nested function**.

```python
def outer():
    def inner():
        print("Inside inner")

    inner()


outer()
```

Output:

```text
Inside inner
```

## 5.1 Why use nested functions?

Nested functions are useful when a helper function:

- is only relevant inside one outer function,
- needs access to values from the outer scope,
- or is used as an implementation detail.

Decorators commonly use a nested function called a **wrapper**.

## 5.2 Scope

The nested `inner` function is defined inside `outer`.

Its name is not automatically available as a top-level name:

```python
def outer():
    def inner():
        print("Inside")


outer()

# print(inner)  # NameError
```

The nested function exists in the local scope created by `outer`.

This becomes especially interesting when the inner function is returned.

---

# 6. Closures

Closures are an important prerequisite for understanding many decorators.

## 6.1 A simple closure

```python
def make_multiplier(factor):
    def multiply(number):
        return number * factor

    return multiply


double = make_multiplier(2)

print(double(10))
```

Output:

```text
20
```

Where did `factor` come from when `double(10)` ran?

`factor` was defined in the enclosing scope of `multiply`.

Even after `make_multiplier` finished, the returned function retained access to that captured value.

## 6.2 Mental model

```text
make_multiplier(2)
        ↓
factor = 2
        ↓
create multiply()
        ↓
return multiply
        ↓
double refers to multiply
        ↓
double(10)
        ↓
multiply uses captured factor = 2
        ↓
20
```

## 6.3 What is a closure?

A closure is a function together with the referenced values from its enclosing lexical scope that the function retains access to.

You do not need to memorize a low-level implementation structure yet. The practical idea is:

> A nested function can remember values from its surrounding scope.

## 6.4 Inspecting a closure

```python
def make_multiplier(factor):
    def multiply(number):
        return number * factor

    return multiply


double = make_multiplier(2)

print(double.__closure__)
```

You may see implementation-oriented information describing closure cells.

That is useful for inspection, but the language-level behavior is more important than the exact representation.

## 6.5 Why closures matter for decorators

A decorator wrapper often needs to remember the original function:

```text
decorator(function)
      ↓
wrapper remembers function
      ↓
wrapper(*args, **kwargs)
      ↓
function(*args, **kwargs)
```

That remembered function is one reason closures are so common in decorator implementations.

---

# 7. Higher-Order Functions

A **higher-order function** is a function that operates on functions or other callables.

Common patterns include:

1. accepts a function as an argument,
2. returns a function,
3. or does both.

For example:

```python
def apply_twice(function, value):
    return function(function(value))


def add_one(number):
    return number + 1


print(apply_twice(add_one, 10))
```

Output:

```text
12
```

Decorators are built from this higher-order-function capability.

## Conceptual chain

```text
Functions are objects
        ↓
Functions can be passed around
        ↓
Functions can be returned
        ↓
Nested functions
        ↓
Closures
        ↓
Higher-order functions
        ↓
Decorators
```

---

# 8. What Problem Do Decorators Solve?

Suppose we have:

```python
def add(a, b):
    return a + b


def subtract(a, b):
    return a - b
```

Now suppose both need logging.

## 8.1 Naive duplication

```python
def add(a, b):
    print("Starting add")
    result = a + b
    print("Finished add")
    return result


def subtract(a, b):
    print("Starting subtract")
    result = a - b
    print("Finished subtract")
    return result
```

This works, but the logging concern has become duplicated inside the business logic.

Now imagine 50 functions need the same behavior.

## 8.2 Separate the concern

We would like something conceptually like:

```text
logging behavior
       +
actual function
       =
decorated function
```

The decorator allows us to write that reusable behavior once.

The most important insight is:

> A decorator lets us change what happens around a callable without editing its core implementation directly.

This does not mean the original function object is mutated. In a common function-decorator design, the name is rebound to a wrapper returned by the decorator.

---

# 9. First Decorator — Manual Implementation

Before using `@`, build the decorator explicitly.

## 9.1 Basic decorator

```python
def log_call(function):
    def wrapper():
        print("Function is starting")
        function()
        print("Function is finished")

    return wrapper
```

Then:

```python
def greet():
    print("Hello")


greet = log_call(greet)

greet()
```

Output:

```text
Function is starting
Hello
Function is finished
```

## 9.2 Line-by-line explanation

### Line 1

```python
def log_call(function):
    def wrapper():
        print("Starting")
        function()
        print("Finished")

    return wrapper
```

`log_call` receives a callable.

After:

```python
greet = log_call(greet)
```

the parameter `function` refers to the original `greet`.

### Line 2

```python
def wrapper():
    print("Inside wrapper")
```

The decorator creates a new function.

That wrapper controls what happens around the original function.

### Line 3

```python
print("Function is starting")
```

New behavior before the original function.

### Line 4

```python
function()
```

Call the original function.

### Line 5

```python
print("Function is finished")
```

New behavior after the original function.

### Line 6

```python
return wrapper
```

Return the new callable.

## 9.3 The most important line

```python
greet = log_call(greet)
```

Before that line:

```text
greet → original function
```

After that line:

```text
greet → wrapper
```

The wrapper still has access to the original function through its enclosing scope.

That is the core mental model of a basic decorator.

---

# 10. The `@decorator` Syntax

Only after understanding manual reassignment should we introduce decorator syntax.

```python
def log_call(function):
    def wrapper():
        print("Function is starting")
        function()
        print("Function is finished")

    return wrapper


@log_call
def greet():
    print("Hello")


greet()
```

Output:

```text
Function is starting
Hello
Function is finished
```

## 10.1 What does `@log_call` mean?

Conceptually:

```python
@log_call
def greet():
    print("Hello")
```

is equivalent to:

```python
def greet():
    print("Hello")


greet = log_call(greet)
```

This is why understanding the explicit form is more important than memorizing the `@` symbol.

## 10.2 Important precision

The `@` syntax is convenient syntax for applying a decorator during function definition.

It does not mean:

> "Python permanently attached a decorator to the function object."

In the common case, the function name is rebound to the callable returned by the decorator.

---

# 11. Basic Decorator Execution Flow

A useful model is:

```text
Original function
      ↓
Decorator receives function
      ↓
Decorator creates wrapper
      ↓
Decorator returns wrapper
      ↓
Function name refers to returned wrapper
      ↓
Call decorated function
      ↓
Wrapper executes
      ↓
Original function executes
      ↓
Wrapper continues
```

## 11.1 Decoration time vs execution time

This distinction is critical.

Consider:

```python
def decorator(function):
    print("Decorating:", function.__name__)

    def wrapper():
        print("Before")
        function()
        print("After")

    return wrapper


@decorator
def greet():
    print("Hello")


print("About to call")
greet()
```

Expected output:

```text
Decorating: greet
About to call
Before
Hello
After
```

Notice:

```text
Decorating: greet
```

appears before:

```text
About to call
```

The decorator application happens while the function definition is being evaluated.

The wrapper's internal behavior occurs later, when `greet()` is called.

### Mental model

**Decoration time:**

```text
define greet
    ↓
call decorator(greet)
    ↓
receive wrapper
    ↓
bind greet to wrapper
```

**Execution time:**

```text
greet()
    ↓
wrapper()
    ↓
original function()
```

## 11.2 Why this matters in production

Code executed during decoration may happen when a module is imported.

That means expensive work, I/O, registration, or unexpected side effects inside the decorator itself can affect import-time behavior.

A good default is to keep decoration cheap and predictable.

---

# 12. Decorators With Function Arguments

Our first decorator only works with functions that take no arguments:

```python
def log_call(function):
    def wrapper():
        function()

    return wrapper
```

This breaks:

```python
@log_call
def greet(name):
    print(f"Hello, {name}")


greet("Sovon")
```

Why?

The wrapper was defined as:

```python
def wrapper():
    print("Inside wrapper")
```

but the call supplies one positional argument.

That leads to a `TypeError`.

## 12.1 General argument forwarding

A practical decorator wrapper commonly uses:

```python
def log_call(function):
    def wrapper(*args, **kwargs):
        print("Starting")
        result = function(*args, **kwargs)
        print("Finished")
        return result

    return wrapper
```

Now:

```python
@log_call
def greet(name):
    print(f"Hello, {name}")


greet("Sovon")
```

Output:

```text
Starting
Hello, Sovon
Finished
```

## 12.2 What is `*args`?

`*args` collects extra positional arguments into a tuple.

Example:

```python
def show_arguments(*args):
    print(args)


show_arguments(10, 20, 30)
```

Output:

```text
(10, 20, 30)
```

## 12.3 What is `**kwargs`?

`**kwargs` collects keyword arguments into a dictionary.

```python
def show_keywords(**kwargs):
    print(kwargs)


show_keywords(name="Sovon", active=True)
```

Output:

```text
{'name': 'Sovon', 'active': True}
```

## 12.4 Forwarding them

This:

```python
function(*args, **kwargs)
```

unpacks the collected arguments back into the original call.

Conceptually:

```text
caller
  ↓
wrapper(*args, **kwargs)
  ↓
collect arguments
  ↓
function(*args, **kwargs)
  ↓
reconstruct original call
```

## 12.5 Important limitation

`*args, **kwargs` is a practical general-purpose forwarding pattern, but it does not magically guarantee perfect semantic preservation for every possible callable.

Decorators can still change:

- signature visibility,
- annotations,
- error messages,
- timing,
- side effects,
- introspection behavior,
- async behavior,
- or other semantics.

Use it because it fits the design, not because it is a magic compatibility switch.

---

# 13. Preserving Return Values

A common decorator bug is forgetting to return the result.

## 13.1 Incorrect

```python
def decorator(function):
    def wrapper(*args, **kwargs):
        function(*args, **kwargs)

    return wrapper


@decorator
def add(a, b):
    return a + b


result = add(2, 3)
print(result)
```

Output:

```text
None
```

Why?

The original function returned `5`, but the wrapper did not return that value.

The result was discarded.

## 13.2 Correct

```python
def decorator(function):
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        return result

    return wrapper
```

Now:

```python
@decorator
def add(a, b):
    return a + b


print(add(2, 3))
```

Output:

```text
5
```

The shorter form is also valid:

```python
def decorator(function):
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

## 13.3 The contract principle

A decorator should deliberately define what it changes.

For a decorator intended only to add logging:

```text
input behavior  → preserve
return behavior → preserve
exception behavior → usually preserve unless explicitly documented
core business behavior → preserve
```

Unexpected contract changes are a major source of decorator bugs.

---

# 14. `functools.wraps`

A wrapper is a new function.

That creates an important metadata problem.

## 14.1 Without `wraps`

```python
def decorator(function):
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper


@decorator
def greet(name):
    """Greet a person by name."""
    return f"Hello, {name}"


print(greet.__name__)
print(greet.__doc__)
```

Typical result:

```text
wrapper
None
```

The decorated name points to the wrapper, so introspection sees wrapper metadata.

## 14.2 Use `functools.wraps`

```python
from functools import wraps


def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper


@decorator
def greet(name):
    """Greet a person by name."""
    return f"Hello, {name}"


print(greet.__name__)
print(greet.__doc__)
```

Output:

```text
greet
Greet a person by name.
```

## 14.3 What `wraps` is for

`functools.wraps` is a convenience decorator used when defining wrappers.

It helps preserve important function metadata and establishes the `__wrapped__` relationship used by introspection tooling.

The exact set of copied/updated metadata follows the standard-library behavior of `functools.update_wrapper`.

For everyday decorator writing, the practical rule is:

> When you create a wrapper around a function, use `@wraps(original_function)` unless you have a deliberate reason not to.

## 14.4 Why metadata matters

Metadata supports:

- debugging,
- tracebacks and readable diagnostics,
- documentation tools,
- introspection,
- tests,
- developer tooling,
- code comprehension.

Without metadata preservation, a decorated function may become harder to understand.

---

# 15. A Production-Quality Basic Decorator

A useful basic pattern is a timing decorator.

```python
from functools import wraps
from time import perf_counter
from collections.abc import Callable
from typing import Any


def measure_time(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            elapsed = perf_counter() - start
            print(f"{function.__name__} took {elapsed:.6f} seconds")

    return wrapper
```

Example:

```python
@measure_time
def add_numbers(a: int, b: int) -> int:
    return a + b


print(add_numbers(10, 20))
```

Possible output:

```text
add_numbers took 0.000001 seconds
30
```

The exact timing depends on the machine and environment.

## Engineering decisions

### `@wraps(function)`

Preserves useful metadata.

### `*args, **kwargs`

Allows broad practical argument forwarding.

### `Callable[..., Any]`

Communicates that a callable is being wrapped without introducing overly complex generic typing.

### `try/finally`

Measures both successful and failing calls.

That can be important when the goal is observability rather than only timing successful operations.

### `perf_counter()`

Provides an appropriate monotonic timing source for elapsed-duration measurement.

This is measurement instrumentation, not a complete benchmarking methodology.

---

# 16. Decorator for Logging

For production-oriented logging, prefer the standard `logging` module rather than `print`.

## 16.1 Basic logging decorator

```python
import logging
from functools import wraps
from typing import Any


logger = logging.getLogger(__name__)


def log_call(function):
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info("Calling %s", function.__name__)
        try:
            result = function(*args, **kwargs)
        except Exception:
            logger.exception("Function %s failed", function.__name__)
            raise
        else:
            logger.info("Function %s completed", function.__name__)
            return result

    return wrapper
```

Example setup:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s %(message)s",
)
```

Then:

```python
@log_call
def greet(name: str) -> str:
    return f"Hello, {name}"


print(greet("Sovon"))
```

The exact log formatting depends on configuration.

## 16.2 Why not automatically log arguments?

This is tempting:

```python
logger.info("args=%r kwargs=%r", args, kwargs)
```

But arguments may contain:

- passwords,
- tokens,
- personal information,
- large payloads,
- authentication headers,
- confidential business data.

Production logging should be designed with data sensitivity in mind.

A useful default is to log:

- function identity,
- lifecycle event,
- duration,
- error status,
- correlation identifiers when appropriate,

without automatically dumping arbitrary arguments.

## 16.3 Exception handling principle

This decorator uses:

```python
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed")
    raise
```

The `raise` matters.

The decorator logs the failure while preserving the original exception behavior.

It does not silently convert failures into success.

---

# 17. Decorator for Timing

A timing decorator can be small:

```python
from functools import wraps
from time import perf_counter


def measure_time(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            elapsed = perf_counter() - start
            print(f"{function.__name__}: {elapsed:.6f}s")

    return wrapper
```

Example:

```python
@measure_time
def compute_total(limit):
    total = 0
    for number in range(limit):
        total += number
    return total


print(compute_total(100_000))
```

## 17.1 Why `finally`?

Suppose the function raises an exception.

If timing is meant to measure all attempts, `finally` ensures the elapsed duration is still recorded.

## 17.2 Is this a benchmarking framework?

No.

A decorator like this is useful for application-level instrumentation.

It does not automatically account for:

- warm-up effects,
- system noise,
- repeated runs,
- statistical variability,
- compiler/interpreter effects,
- workload representativeness.

For rigorous performance analysis, measure systematically rather than relying on one decorated call.

---

# 18. Decorator for Validation

Decorators can enforce simple preconditions at a function boundary.

```python
from functools import wraps


def require_positive(function):
    @wraps(function)
    def wrapper(value):
        if value <= 0:
            raise ValueError("value must be positive")
        return function(value)

    return wrapper
```

Use it:

```python
@require_positive
def describe_value(value):
    return f"Accepted: {value}"


print(describe_value(5))
```

Output:

```text
Accepted: 5
```

Invalid input:

```python
describe_value(-1)
```

raises:

```text
ValueError: value must be positive
```

## 18.1 Why this separation can help

Core function:

```python
def describe_value(value):
    return f"Accepted: {value}"
```

Decorator:

```python
@require_positive
def process(value):
    return value * 2
```

The validation rule is separated from the main operation.

## 18.2 Keep validation decorators small

Do not build a universal validation framework here.

A decorator is appropriate when the condition is:

- reusable,
- conceptually clear,
- cross-cutting,
- and easy for a reader to discover.

If every function gets a different complicated validation decorator, readability can decline.

---

# 19. Decorator for Authorization-Like Checks

A common application pattern is conceptually:

```python
@requires_role("admin")
def delete_record():
    ...
```

A small educational implementation can use a context object:

```python
from functools import wraps


def requires_role(required_role):
    def decorator(function):
        @wraps(function)
        def wrapper(user, *args, **kwargs):
            if required_role not in user.get("roles", set()):
                raise PermissionError(
                    f"Role {required_role!r} is required"
                )
            return function(user, *args, **kwargs)

        return wrapper

    return decorator
```

Example:

```python
@requires_role("admin")
def delete_record(user, record_id):
    return f"Deleted record {record_id}"


admin = {"roles": {"admin", "analyst"}}

print(delete_record(admin, 42))
```

Output:

```text
Deleted record 42
```

A non-admin user would receive `PermissionError`.

## 19.1 Important security limitation

This is an educational example, not a complete authorization architecture.

A decorator alone does not create a security boundary.

Real authorization requires appropriate handling of:

- identity,
- authentication,
- authorization policy,
- credential verification,
- trust boundaries,
- privilege management,
- audit requirements,
- error handling.

The decorator can be one enforcement point in a larger architecture.

---

# 20. Decorator With Exception Handling

A decorator can catch selected expected exceptions and add observability.

```python
import logging
from functools import wraps


logger = logging.getLogger(__name__)


def log_expected_errors(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (ValueError, TypeError):
            logger.exception("Expected input-related error in %s",
                             function.__name__)
            raise

    return wrapper
```

## 20.1 Why catch only selected exceptions?

This:

```python
try:
    result = convert_value("10")
except (ValueError, TypeError):
    logger.exception("Input conversion failed")
    raise
```

communicates intent.

This:

```python
try:
    result = perform_operation()
except Exception:
    logger.exception("Operation failed")
    raise
```

catches a much broader category.

Broad catches can be appropriate in carefully designed boundaries, but they create a serious risk of accidentally hiding failures.

Bad:

```python
def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            return None

    return wrapper
```

This changes failure into apparent success.

A caller can no longer distinguish:

```text
successful None
```

from:

```text
failed operation that decorator swallowed
```

That is usually dangerous.

## Engineering rule

When handling exceptions inside a decorator:

1. catch only exceptions you have a reason to handle,
2. preserve error information,
3. do not silently convert failures unless that is explicitly the function contract,
4. document any changed error semantics.

---

# 21. Retry Decorators

Retries are useful for some transient failures.

Suppose an operation occasionally fails with a temporary connection-related error.

A small educational retry decorator might look like:

```python
from functools import wraps
import time


def retry(max_attempts, retryable_exceptions=(Exception,), delay=0.0):
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            attempt = 1

            while True:
                try:
                    return function(*args, **kwargs)
                except retryable_exceptions:
                    if attempt >= max_attempts:
                        raise

                    if delay > 0:
                        time.sleep(delay)

                    attempt += 1

        return wrapper

    return decorator
```

Example:

```python
attempts = 0


@retry(max_attempts=3, retryable_exceptions=(RuntimeError,))
def unstable_operation():
    global attempts
    attempts += 1

    if attempts < 3:
        raise RuntimeError("Temporary failure")

    return "success"


print(unstable_operation())
```

Output:

```text
success
```

## 21.1 What the decorator does

For:

```python
@retry(max_attempts=3, retryable_exceptions=(RuntimeError,))
def operation():
    return "ok"
```

the factory stores configuration:

```text
max_attempts = 3
retryable_exceptions = (RuntimeError,)
```

The resulting decorator then receives the function.

At execution time, the wrapper performs attempts.

## 21.2 Retry is not universally safe

Do not retry every failure.

For example, a validation failure is generally not fixed by trying again.

More importantly, retries can be dangerous for non-idempotent operations.

Suppose this operation:

```python
charge_customer()
```

successfully charges a customer, but the client times out before receiving the response.

Blindly retrying may create a duplicate charge.

This leads to a key production concept:

> Retry policy must consider the operation's semantics, not only the exception type.

## 21.3 Production retry concerns

A production retry mechanism may need:

- bounded retries,
- exponential backoff,
- jitter,
- timeouts,
- explicit retryable error categories,
- observability,
- cancellation behavior,
- idempotency strategy,
- load protection.

The small decorator above is intentionally educational. It is not a distributed-systems retry framework.

## 21.4 Retry can amplify load

Suppose a dependency is already overloaded.

If every caller retries aggressively:

```text
request
 ↓ fail
retry
 ↓ fail
retry
 ↓ fail
retry
```

the retries themselves create more traffic.

This is why production retry design must consider the system, not just the local function.

---

# 22. Decorator Factories / Parameterized Decorators

There is an important difference between:

```python
@retry
def operation():
    ...
```

and:

```python
@retry(3)
def operation():
    ...
```

The second calls `retry(3)` first.

Therefore `retry` must return a decorator.

## 22.1 Three layers

Consider:

```python
def repeat(times):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = function(*args, **kwargs)
            return result

        return wrapper

    return decorator
```

There are three distinct layers.

### Layer 1: configuration

```python
repeat(times)
```

Receives decorator configuration.

### Layer 2: decoration

```python
decorator(function)
```

Receives the target function.

### Layer 3: execution

```python
wrapper(*args, **kwargs)
```

Runs when the decorated function is called.

Diagram:

```text
repeat(times)
      ↓
decorator(function)
      ↓
wrapper(*args, **kwargs)
```

## 22.2 Full example

```python
from functools import wraps


def repeat(times):
    if times < 1:
        raise ValueError("times must be at least 1")

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            result = None

            for _ in range(times):
                result = function(*args, **kwargs)

            return result

        return wrapper

    return decorator


@repeat(3)
def greet(name):
    print(f"Hello, {name}")
    return "done"


result = greet("Sovon")
print(result)
```

Output:

```text
Hello, Sovon
Hello, Sovon
Hello, Sovon
done
```

## 22.3 When does each part execute?

For:

```python
@repeat(3)
def greet(name):
    ...
```

the conceptual process is:

```text
repeat(3)
    ↓
returns decorator
    ↓
decorator(greet)
    ↓
returns wrapper
    ↓
greet name is bound to wrapper
```

Only later:

```python
greet("Sovon")
```

calls the wrapper.

That three-level distinction is one of the most important advanced decorator concepts.

---

# 23. Multiple Decorators

Consider:

```python
@decorator_a
@decorator_b
def process():
    ...
```

The conceptual equivalence is:

```python
process = decorator_a(decorator_b(process))
```

The decorators therefore form nested wrappers.

## 23.1 Execution example

```python
from functools import wraps


def decorator_a(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print("A before")
        result = function(*args, **kwargs)
        print("A after")
        return result

    return wrapper


def decorator_b(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print("B before")
        result = function(*args, **kwargs)
        print("B after")
        return result

    return wrapper


@decorator_a
@decorator_b
def process():
    print("process")


process()
```

Output:

```text
A before
B before
process
B after
A after
```

## 23.2 Why?

The structure is:

```text
A wrapper
    ↓
B wrapper
    ↓
original process
```

So the outer wrapper starts first.

After the inner function returns, control moves back outward.

---

# 24. Decorator Order — Important

Consider:

```python
@authenticate
@log_call
def operation():
    ...
```

Conceptually:

```python
operation = authenticate(log_call(operation))
```

This means:

```text
authenticate
    ↓
log_call
    ↓
operation
```

Now compare:

```python
@log_call
@authenticate
def operation():
    ...
```

Conceptually:

```python
operation = log_call(authenticate(operation))
```

Now:

```text
log_call
    ↓
authenticate
    ↓
operation
```

The order is not universally "right" or "wrong". It depends on the intended semantics.

## 24.1 Why order matters

Suppose the authentication check rejects a request.

Do you want the logging decorator to record an attempted call?

Maybe yes.

Do you want the internal business operation to run before authorization?

No.

The important engineering question is:

> What behavior should surround what other behavior?

## 24.2 Other combinations where order matters

Examples include:

- validation + logging,
- authorization + logging,
- retry + timing,
- caching + timing,
- tracing + error handling.

For instance, timing outside retry measures all attempts:

```text
timing
  ↓
retry
  ↓
operation
```

Timing inside retry may measure each individual attempt:

```text
retry
  ↓
timing
  ↓
operation
```

Both can be useful, but they measure different things.

---

# 25. Decorating Functions That Return Values

A decorator should normally preserve the wrapped function's contract unless intentionally documented otherwise.

## 25.1 String return

```python
from functools import wraps


def identity_decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper


@identity_decorator
def get_message():
    return "hello"


print(get_message())
```

Output:

```text
hello
```

## 25.2 Numeric return

```python
@identity_decorator
def calculate_total(a, b):
    return a + b


print(calculate_total(4, 6))
```

Output:

```text
10
```

## 25.3 Dictionary return

```python
@identity_decorator
def build_record():
    return {"status": "ok", "count": 3}


print(build_record())
```

## 25.4 `None` return

```python
@identity_decorator
def notify():
    print("notification sent")


result = notify()
print(result)
```

Output:

```text
notification sent
None
```

The decorator is not required to convert `None` into something else.

## Engineering principle

A decorator that adds logging should generally not unexpectedly change:

```text
what the function returns
```

or:

```text
which exceptions it raises
```

unless the new contract is intentional and documented.

---

# 26. Decorating Methods

Methods introduce one important issue: `self`.

```python
from functools import wraps


def log_call(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print(f"Calling {function.__name__}")
        return function(*args, **kwargs)

    return wrapper


class Calculator:
    @log_call
    def add(self, a, b):
        return a + b


calculator = Calculator()

print(calculator.add(2, 3))
```

Output:

```text
Calling add
5
```

## 26.1 Where does `self` go?

When calling:

```python
calculator.add(2, 3)
```

the instance is bound to the method and becomes the first argument received by the wrapper.

Conceptually:

```text
wrapper(calculator, 2, 3)
```

The use of:

```python
*args
```

allows the decorator to accept that instance without hard-coding `self`.

## 26.2 Practical method model

At class definition time, the decorator is applied to the function stored in the class namespace.

Later, accessing the function through an instance participates in Python's method binding mechanism.

You do not need full descriptor theory to use decorators correctly here.

The practical lesson is:

> A decorator for methods must preserve the calling convention expected by the method.

---

# 27. `staticmethod` and `classmethod`

Python includes built-in decorators that change how methods behave.

## 27.1 `staticmethod`

```python
class MathTools:
    @staticmethod
    def add(a, b):
        return a + b


print(MathTools.add(2, 3))
```

Output:

```text
5
```

There is no automatic instance parameter.

## 27.2 `classmethod`

```python
class User:
    category = "standard"

    @classmethod
    def describe(cls):
        return f"category={cls.category}"


print(User.describe())
```

Output:

```text
category=standard
```

`classmethod` supplies the class as the first argument.

## 27.3 These are decorators too

This demonstrates that decorators are not just a custom trick you invent.

Python uses decorators to provide standard language features.

```text
@staticmethod
@classmethod
@property
```

are all examples of decorator syntax.

## 27.4 Combining decorators

Order can matter.

For example, custom decorators combined with `staticmethod` or `classmethod` may behave differently depending on which decorator receives the function-like object first.

Do not blindly rearrange:

```python
@custom_decorator
@staticmethod
def helper():
    ...
```

into:

```python
@staticmethod
@custom_decorator
def helper():
    ...
```

without understanding what object each decorator expects.

A good engineering practice is to keep combinations explicit and test them.

---

# 28. `property`

`property` is another built-in decorator-like tool that demonstrates how a method can be exposed through attribute-style access.

```python
class Person:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

Now:

```python
person = Person("A", "K")

print(person.full_name)
```

Output:

```text
A K
```

Notice:

```python
person.full_name
```

not:

```python
person.full_name()
```

The method has been transformed into managed attribute access.

## 28.1 Why is this useful for learning decorators?

It shows that decorator syntax can change how a callable-like implementation is exposed.

The decorator is not merely "add logging before and after."

## 28.2 Setter

You can define a setter:

```python
class Person:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value:
            raise ValueError("name cannot be empty")
        self._name = value
```

The `@name.setter` form works with the existing property object.

Again, the important goal here is understanding the concept, not mastering the descriptor system behind it.

---

# 29. Class Decorators

Decorators are not limited to functions.

A decorator can receive a class and return a class.

## 29.1 Minimal example

```python
def add_feature(cls):
    cls.feature_enabled = True
    return cls
```

Then:

```python
@add_feature
class Example:
    pass


print(Example.feature_enabled)
```

Output:

```text
True
```

## 29.2 Mental model

```text
class definition
    ↓
class object created
    ↓
add_feature(class)
    ↓
returns class
    ↓
Example refers to returned class
```

This is conceptually similar to a function decorator.

## 29.3 Why use class decorators?

They can be useful for:

- registration,
- adding configuration,
- attaching metadata,
- systematic class transformation.

But class decorators can also hide where behavior comes from.

Use them when the transformation is obvious and reusable.

---

# 30. Stateful Decorators

A decorator can keep state in a closure.

## 30.1 Call counter

```python
from functools import wraps


def call_counter(function):
    count = 0

    @wraps(function)
    def wrapper(*args, **kwargs):
        nonlocal count
        count += 1
        print(f"Call number: {count}")
        return function(*args, **kwargs)

    return wrapper
```

Use it:

```python
@call_counter
def greet(name):
    return f"Hello, {name}"


print(greet("A"))
print(greet("B"))
print(greet("C"))
```

Output:

```text
Call number: 1
Hello, A
Call number: 2
Hello, B
Call number: 3
Hello, C
```

## 30.2 How state persists

The variable:

```python
count
```

belongs to the enclosing scope created when the decorator runs.

The wrapper retains access to it.

`nonlocal` means:

> use the variable from the nearest enclosing function scope rather than creating a new local variable.

## 30.3 Lifecycle

For:

```python
@call_counter
def greet(name):
    return f"Hello, {name}"
```

the decorator is executed once during decoration.

A `count` is created.

Every later call to the wrapper updates that same captured state.

```text
decoration
   ↓
count = 0
   ↓
wrapper created
   ↓
call #1 → count = 1
   ↓
call #2 → count = 2
   ↓
call #3 → count = 3
```

## 30.4 Concurrency considerations

Stateful decorators require extra care in concurrent environments.

Problems can arise if multiple executions update shared state at the same time and the state is not designed for that execution model.

Possible concerns include:

- race conditions,
- process-local state,
- thread safety,
- async interleaving,
- inconsistent metrics.

Do not assume a closure is automatically safe just because it is convenient.

If state is important, choose a deliberate state-management design.

---

# 31. Decorators and Closures

Now connect the pieces.

A common decorator pattern looks like:

```text
Nested function
      ↓
closure captures original function
      ↓
decorator returns wrapper
      ↓
wrapper calls original function
      ↓
wrapper may also use captured state
```

Example:

```python
def decorator(function):
    def wrapper(*args, **kwargs):
        print("Before")
        result = function(*args, **kwargs)
        print("After")
        return result

    return wrapper
```

What does the wrapper need to remember?

It needs access to:

```python
function
```

That reference is captured from the enclosing `decorator` scope.

This is why closures and decorators are so often taught together.

## Important precision

Not every decorator must use a closure.

For example, a callable class can act as a decorator:

```python
class Logger:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        print("Calling")
        return self.function(*args, **kwargs)
```

The callable object stores the function as instance state rather than using a nested-function closure.

Therefore:

> Closures are a common implementation technique for decorators, not a universal requirement.

---

# 32. Advanced Introspection

Decorators can affect what developers see when inspecting a function.

## 32.1 Useful attributes

```python
from functools import wraps


def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper


@decorator
def greet(name):
    """Return a greeting."""
    return f"Hello, {name}"
```

Now:

```python
print(greet.__name__)
print(greet.__doc__)
print(greet.__wrapped__)
```

Typical output:

```text
greet
Return a greeting.
<function greet at 0x...>
```

The exact function representation varies.

## 32.2 What is `__wrapped__`?

When `functools.wraps` is used, the wrapper receives a `__wrapped__` reference to the original wrapped callable.

This can help tools and developers understand the wrapper relationship.

## 32.3 `inspect.signature`

```python
from inspect import signature

print(signature(greet))
```

With good decorator metadata, introspection can often expose the original signature more usefully.

However, introspection is not magic. Complicated decorator stacks can still make behavior harder to reason about.

## Production lesson

Good decorator design should support the developer who has to debug the system at 2 a.m.

Metadata preservation is part of that design.

---

# 33. Decorators and Type Hints

Decorators can complicate static typing because a wrapper may accept and return values corresponding to another callable's signature.

For an introductory example:

```python
from collections.abc import Callable
from functools import wraps
from typing import Any


def log_call(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"Calling {function.__name__}")
        return function(*args, **kwargs)

    return wrapper
```

This says:

- `function` is callable,
- it can accept arbitrary arguments for this simplified typing example,
- the decorator returns another callable.

## 33.1 Why typing can become harder

Suppose we want the decorator to preserve the exact relationship between:

```text
input parameter types
```

and:

```text
return type
```

Then advanced typing machinery may be needed.

Modern Python typing can express richer callable transformations, but that quickly becomes more complex.

### Engineering guideline

For beginner and intermediate decorators:

```python
Callable[..., Any]
```

may be sufficient when exact signature preservation is not the teaching target.

For shared libraries with strict static typing requirements, learn more advanced callable typing deliberately rather than adding complicated type parameters mechanically.

---

# 34. Decorators and Async Functions

A synchronous decorator does not automatically become correct for an asynchronous function.

Consider:

```python
def ordinary_decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print("Before")
        result = function(*args, **kwargs)
        print("After")
        return result

    return wrapper
```

If the decorated target is:

```python
@ordinary_decorator
async def fetch_data():
    ...
```

calling `fetch_data()` creates a coroutine object.

The synchronous wrapper does not `await` it.

So:

```text
wrapper
  ↓
calls async function
  ↓
receives coroutine object
  ↓
prints "After"
  ↓
returns coroutine
```

The actual asynchronous body may not run at that point.

## 34.1 Small educational async decorator

```python
from functools import wraps
import asyncio


def async_logging(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        print(f"Starting {function.__name__}")
        try:
            return await function(*args, **kwargs)
        finally:
            print(f"Finished {function.__name__}")

    return wrapper


@async_logging
async def greet():
    await asyncio.sleep(0.01)
    return "Hello"


print(asyncio.run(greet()))
```

Output:

```text
Starting greet
Finished greet
Hello
```

## 34.2 Important boundary

This section only establishes the concept.

Async concurrency, cancellation, task scheduling, event loops, and synchronization belong to a broader topic.

The important decorator lesson is:

> A decorator must match the execution model of the callable it wraps.

Do not assume that a synchronous wrapper can be pasted around an `async def` function unchanged.

---

# 35. Decorator Debugging

Decorator bugs often look mysterious because a simple function call is now going through one or more wrappers.

The solution is to reduce the problem to the decorator mechanism.

---

## 35.1 Symptom: "Why did my function become `None`?"

### Cause

The wrapper forgot to return the wrapped result.

Incorrect:

```python
def decorator(function):
    def wrapper(*args, **kwargs):
        function(*args, **kwargs)

    return wrapper
```

Fix:

```python
def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

---

## 35.2 Symptom: "Why is my function name `wrapper`?"

### Cause

`functools.wraps` was not used.

Incorrect:

```python
def decorator(function):
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

Fix:

```python
from functools import wraps


def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

---

## 35.3 Symptom: "Why are my arguments not working?"

### Cause

The wrapper signature is too restrictive.

Incorrect:

```python
def decorator(function):
    def wrapper():
        return function()

    return wrapper
```

Fix, when appropriate:

```python
def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

---

## 35.4 Symptom: "Why did the decorator run at import time?"

Example:

```python
def decorator(function):
    print("DECORATING")
    return function


@decorator
def greet():
    pass
```

You will see:

```text
DECORATING
```

when the module is evaluated.

That is expected.

### Cause

Decoration occurs when the definition is evaluated, not when `greet()` is called.

### Fix

Do not treat this as an error unless import-time side effects are unintended.

If expensive work is happening during decoration, move that work to execution time when appropriate.

---

## 35.5 Symptom: "Why are multiple decorators behaving unexpectedly?"

### Cause

Decorator nesting and order.

Use the conceptual expansion:

```python
@a
@b
def function():
    ...
```

becomes:

```python
function = a(b(function))
```

Draw the wrapper stack explicitly.

---

## 35.6 Symptom: "Why is the function being called twice?"

Look for a decorator such as:

```python
def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        function(*args, **kwargs)
        return function(*args, **kwargs)

    return wrapper
```

The original function is called twice.

A reliable debugging method is to add a temporary trace:

```python
print("wrapper entered")
print("calling original")
result = function(*args, **kwargs)
print("original returned")
```

---

## 35.7 Symptom: "Why did my decorated method fail because of `self`?"

Check whether the decorator:

- accepts positional arguments,
- forwards all arguments,
- accidentally removed the first bound argument,
- or changes the expected method signature.

Start with:

```python
def wrapper(*args, **kwargs):
    print(args)
    print(kwargs)
    return function(*args, **kwargs)
```

This is a debugging tool, not necessarily the final implementation.

---

## 35.8 Symptom: "Why did my async function stop behaving correctly?"

Check whether the wrapper is synchronous:

```python
def wrapper(*args, **kwargs):
    return function(*args, **kwargs)
```

around an async function.

A coroutine-producing function generally needs an async-aware wrapper:

```python
async def wrapper(*args, **kwargs):
    return await function(*args, **kwargs)
```

---

## 35.9 Traceback-oriented debugging

A stack trace involving decorators may show wrapper frames.

That is one more reason to use:

```python
from functools import wraps

def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

and keep wrappers small.

When debugging, inspect:

```python
print(function.__name__)
print(function.__wrapped__)
```

where appropriate.

Also ask:

```text
How many wrappers are around this callable?
What order are they in?
Which wrapper changed the behavior?
```

---

# 36. Testing Decorators

A decorator is code. It needs tests.

The tests should focus primarily on observable behavior.

## 36.1 Example decorator

```python
from functools import wraps


def add_marker(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        return f"[marked] {result}"

    return wrapper
```

## 36.2 Test normal execution

Pytest-style:

```python
def test_add_marker():
    @add_marker
    def greet():
        return "hello"

    assert greet() == "[marked] hello"
```

## 36.3 Test positional arguments

```python
def test_add_marker_with_arguments():
    @add_marker
    def add(a, b):
        return str(a + b)

    assert add(2, 3) == "[marked] 5"
```

## 36.4 Test keyword arguments

```python
def test_add_marker_with_keywords():
    @add_marker
    def greet(name):
        return f"hello {name}"

    assert greet(name="Sovon") == "[marked] hello Sovon"
```

## 36.5 Test return values

The test should verify that the decorator deliberately produces the intended return contract.

For a transparent decorator:

```python
def identity_decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper


def test_identity_preserves_return_value():
    @identity_decorator
    def calculate():
        return 42

    assert calculate() == 42
```

## 36.6 Test exceptions

```python
import pytest


def test_decorator_preserves_exception():
    @identity_decorator
    def fail():
        raise ValueError("bad input")

    with pytest.raises(ValueError, match="bad input"):
        fail()
```

The test verifies that the decorator does not silently swallow the exception.

## 36.7 Test metadata

```python
def test_decorator_preserves_metadata():
    @identity_decorator
    def greet():
        """Return a greeting."""
        return "hello"

    assert greet.__name__ == "greet"
    assert greet.__doc__ == "Return a greeting."
```

## 36.8 Test multiple decoration

```python
def test_decorator_can_be_applied_multiple_times():
    @identity_decorator
    @identity_decorator
    def greet():
        return "hello"

    assert greet() == "hello"
```

Whether multiple application is semantically appropriate depends on the decorator.

## 36.9 Edge cases

Test:

- zero-like values,
- empty strings,
- missing optional arguments,
- invalid inputs,
- exceptions,
- functions returning `None`,
- method usage,
- one or more stacked decorators.

## 36.10 Test behavior, not implementation details

Avoid tests that merely assert:

```text
there is exactly one nested function called wrapper
```

unless that internal structure is actually part of your contract.

Test what users of the decorator can observe.

---

# 37. Common Decorator Mistakes

## Mistake 1 — Forgetting to return the wrapper

### Why it happens

The developer creates the wrapper but forgets:

```python
return wrapper
```

### Incorrect

```python
def decorator(function):
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    # missing return wrapper
```

### Correct

```python
def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

---

## Mistake 2 — Forgetting to return the original result

### Incorrect

```python
def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        function(*args, **kwargs)

    return wrapper
```

### Correct

```python
def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

---

## Mistake 3 — Forgetting arguments

### Incorrect

```python
def decorator(function):
    def wrapper():
        return function()

    return wrapper
```

### Better general-purpose pattern

```python
def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

---

## Mistake 4 — Forgetting `functools.wraps`

### Why it happens

The code still "works," so the metadata problem is not visible immediately.

### Correct approach

```python
from functools import wraps

def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

---

## Mistake 5 — Catching every exception and hiding it

### Incorrect

```python
def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            return None

    return wrapper
```

This destroys useful failure semantics.

### Correct principle

Catch errors only when you have a defined reason to handle them.

---

## Mistake 6 — Doing expensive work during decoration

### Risky pattern

```python
def decorator(function):
    load_huge_configuration()
    return function
```

This may execute when a module is imported.

The operation may be better performed lazily at call time or during an explicit initialization phase, depending on the application.

---

## Mistake 7 — Confusing decoration time and execution time

Remember:

```python
@decorator
def function():
    ...
```

applies the decorator while the definition is evaluated.

The wrapper logic runs later when the function is called.

---

## Mistake 8 — Changing behavior too dramatically

A decorator that sounds like:

```python
@log_calls
def process_task(task_id):
    return {"task_id": task_id, "status": "processed"}
```

should not secretly:

- modify arguments,
- cache results,
- swallow errors,
- perform network I/O,
- change return types,

unless that is explicitly part of its contract.

Names should communicate behavior.

---

## Mistake 9 — Excessive nesting

Five decorators may be reasonable in a carefully designed boundary.

Twenty layers of behavior around a small function may be difficult to understand.

The problem is not the number itself. The problem is the resulting mental load.

---

## Mistake 10 — Using decorators when a normal function is clearer

Sometimes:

```python
result = validate_and_process(data)
```

is clearer than:

```python
@validate
def process(data):
    ...
```

Especially if validation is unique to one call path.

---

## Mistake 11 — Hidden global state

A decorator can accidentally close over mutable global state.

That can make:

- tests harder,
- behavior environment-dependent,
- concurrent execution harder to reason about.

State should have an explicit lifecycle and ownership model.

---

## Mistake 12 — Wrong decorator order

A change from:

```python
@a
@b
def function():
    ...
```

to:

```python
@b
@a
def function():
    ...
```

can change behavior.

Treat order as part of the function's design.

---

## Mistake 13 — Incorrect async decoration

A normal synchronous wrapper may return a coroutine instead of awaiting it.

Use an async-aware decorator when wrapping async functions.

---

## Mistake 14 — Breaking method binding

A decorator that assumes only ordinary functions may accidentally break method calls.

For general method-friendly wrappers, forwarding:

```python
def wrapper(*args, **kwargs):
    return function(*args, **kwargs)
```

is often useful.

---

# 38. When Not to Use Decorators

This section is as important as learning how to write them.

Decorators are a tool, not a badge of advanced Python knowledge.

## 38.1 Use a decorator when

A decorator is a reasonable candidate when:

- the behavior is reusable,
- the behavior is cross-cutting,
- the behavior is conceptually separate from the core operation,
- applying it does not surprise the reader,
- the composition remains understandable.

Examples:

```text
logging
timing
instrumentation
simple validation
selected retry policies
```

## 38.2 Avoid a decorator when

Avoid one when:

- the behavior is used once,
- it hides important business logic,
- explicit control flow is clearer,
- it causes surprising side effects,
- it makes debugging significantly harder,
- a simple helper function communicates the intent better.

### Compare

Decorator:

```python
@validate_customer
def process_customer(customer):
    ...
```

Explicit:

```python
validate_customer(customer)
process_customer(customer)
```

Neither is automatically superior.

The correct engineering choice depends on clarity and reuse.

## 38.3 Engineering principle

> Do not use advanced language features merely because they exist.

A simpler design that a team can understand and maintain is often preferable to a clever abstraction.

---

# 39. Decorator Overuse and Hidden Behavior

Imagine this:

```python
@authenticate
@validate
@retry
@cache
@log_call
@measure_time
def process():
    ...
```

Each decorator might be reasonable by itself.

Together, the reader must understand:

```text
authentication
validation
retry semantics
cache semantics
logging
timing
order
exception behavior
state
```

## 39.1 Hidden control flow

The source appears to contain:

```python
process()
```

but the runtime behavior may be closer to:

```text
authenticate
    ↓
validate
    ↓
retry
    ↓
cache
    ↓
log
    ↓
timing
    ↓
process
```

That can be powerful.

It can also be hard to debug.

## 39.2 Stack traces

A failing function may pass through several wrapper frames.

A developer has to determine:

```text
Which layer generated this behavior?
```

## 39.3 Testing complexity

You may need to test:

- each decorator independently,
- their composition,
- order-sensitive cases,
- interaction with exceptions,
- interaction with caching,
- interaction with retries.

## 39.4 Maintenance burden

A decorator can be technically reusable while still being socially expensive for a development team.

If only the original author understands what the stack does, the abstraction has failed its maintainability goal.

## Principle

> Decorators should improve clarity, not merely reduce lines of code.

---

# 40. Decorators vs Alternative Designs

Decorators are one option among several.

| Design | Useful when | Main strength | Main risk |
|---|---|---|---|
| Decorator | Reusable cross-cutting behavior | Concise application at a boundary | Hidden control flow |
| Helper function | Explicit operation needs to be reused | Very clear call flow | More explicit call-site code |
| Function composition | Several operations form a visible pipeline | Behavior is explicit | Can become verbose |
| Class | Stateful behavior or larger abstraction | Encapsulated state and methods | More structural overhead |
| Context manager | Setup/cleanup around a block | Resource lifecycle is explicit | Different abstraction shape |
| Dependency injection concept | Behavior/dependencies should be supplied explicitly | Testability and explicit dependencies | More design structure |

The table is a selection aid, not a strict rule.

## 40.1 A simple decision path

```text
Need reusable cross-cutting behavior?
          ↓
Would a decorator make the intent clearer?
       /       \
     Yes        No
      ↓          ↓
 consider       use simpler
 decorator       design
```

---

# 41. Production Use Cases

Decorators appear frequently in production Python because they can attach consistent behavior to many callables.

## 41.1 Logging

Problem:

```text
many functions need lifecycle logging
```

Decorator benefit:

```text
one reusable policy
```

Trade-off:

```text
logs may become noisy or expose sensitive data
```

---

## 41.2 Timing and metrics

Problem:

```text
measure execution duration
```

Decorator benefit:

```text
instrumentation can be applied consistently
```

Trade-off:

```text
timing adds overhead and may measure the wrong boundary
```

---

## 41.3 Validation

Problem:

```text
common precondition must be enforced
```

Decorator benefit:

```text
validation policy can be reused
```

Trade-off:

```text
too many hidden validation rules can surprise readers
```

---

## 41.4 Authorization boundaries

Problem:

```text
some operations require a policy check
```

Decorator benefit:

```text
boundary policy can be visibly attached
```

Trade-off:

```text
authorization architecture is larger than a decorator
```

---

## 41.5 Caching

Conceptually:

```python
@cache
def expensive_calculation(key):
    ...
```

A decorator can place caching behavior around a function.

Trade-offs include:

- cache invalidation,
- memory,
- stale results,
- argument hashability,
- shared-state behavior.

The decorator is not the whole caching architecture.

---

## 41.6 Retries

Problem:

```text
some operations fail transiently
```

Decorator benefit:

```text
retry policy can be attached at a specific boundary
```

Trade-off:

```text
incorrect retries can duplicate side effects or amplify load
```

---

## 41.7 Tracing and instrumentation concepts

A decorator can capture:

```text
start
 ↓
function call
 ↓
success/failure
 ↓
duration
```

This is useful for observability.

---

## 41.8 Feature flags conceptually

A decorator may select behavior based on application configuration.

Trade-off:

The control flow can become less obvious because behavior depends on external state.

---

## 41.9 Transaction boundaries conceptually

Some systems use decorators to express a transaction boundary:

```python
@transactional
def update_records():
    ...
```

The exact implementation depends on the underlying persistence system.

The learning point is that decorators can express a boundary around a unit of work.

---

# 42. Applied AI Engineering Connection

Decorators are a general Python mechanism. They do not create AI systems by themselves.

They can, however, support engineering concerns around AI-related code.

## 42.1 Time a model or tool call

```python
@measure_time
def run_model_input(text):
    ...
```

This could help instrument local application code.

---

## 42.2 Log tool execution

```python
@log_call
def fetch_document(document_id):
    ...
```

The decorator can add observability without mixing logging into the core function.

---

## 42.3 Validate inputs

```python
@require_positive
def evaluate_sample(sample_id):
    ...
```

The exact validation will depend on the application.

---

## 42.4 Carefully selected retries

```python
@retry(
    max_attempts=3,
    retryable_exceptions=(TemporaryFailure,),
)
def fetch_remote_resource():
    ...
```

The important engineering question is whether retrying that operation is safe.

---

## 42.5 Instrument evaluation functions

```python
@measure_time
def evaluate_answer(example):
    ...
```

You may want:

```text
duration
success/failure
count
```

around repeated evaluation operations.

Again, decorators are supporting infrastructure, not the AI architecture itself.

---

# 43. Complete Production-Style Example

Now combine several concepts into one small example.

We will build a task-processing function with:

- type hints,
- logging,
- timing,
- validation,
- `functools.wraps`,
- clean separation of concerns,
- tests.

## 43.1 Requirements

Suppose:

```python
process_task(task_id)
```

should:

1. validate that the ID is positive,
2. log execution,
3. measure duration,
4. return a predictable result.

## 43.2 Implementation

```python
from collections.abc import Callable
from functools import wraps
import logging
from time import perf_counter
from typing import Any


logger = logging.getLogger(__name__)


def require_positive_id(
    function: Callable[..., Any],
) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(task_id: int, *args: Any, **kwargs: Any) -> Any:
        if task_id <= 0:
            raise ValueError("task_id must be positive")

        return function(task_id, *args, **kwargs)

    return wrapper


def log_calls(
    function: Callable[..., Any],
) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info("Starting %s", function.__name__)

        try:
            result = function(*args, **kwargs)
        except Exception:
            logger.exception("Failed %s", function.__name__)
            raise
        else:
            logger.info("Completed %s", function.__name__)
            return result

    return wrapper


def measure_time(
    function: Callable[..., Any],
) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()

        try:
            return function(*args, **kwargs)
        finally:
            elapsed = perf_counter() - start
            logger.info(
                "%s took %.6f seconds",
                function.__name__,
                elapsed,
            )

    return wrapper


@log_calls
@measure_time
@require_positive_id
def process_task(task_id: int) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "status": "processed",
    }
```

## 43.3 Decorator order

The source says:

```python
@log_calls
@measure_time
@require_positive_id
def process_task(task_id: int):
    return {"task_id": task_id, "status": "processed"}
```

Conceptually:

```python
process_task = log_calls(
    measure_time(
        require_positive_id(
            process_task
        )
    )
)
```

So:

```text
log_calls
    ↓
measure_time
    ↓
require_positive_id
    ↓
process_task
```

## 43.4 Execution flow

A successful call:

```python
process_task(10)
```

travels approximately like:

```text
log wrapper starts
      ↓
timing wrapper starts
      ↓
validation wrapper checks task_id
      ↓
original process_task executes
      ↓
validation returns
      ↓
timing records duration
      ↓
log wrapper records completion
      ↓
result returned
```

A bad call:

```python
process_task(-1)
```

will fail at validation.

That means the original business function does not execute.

## 43.5 Why this design is useful

Each decorator has one clear responsibility:

```text
log_calls           → observability
measure_time        → timing
require_positive_id → precondition
process_task        → actual task operation
```

This is a separation-of-concerns benefit.

## 43.6 Trade-offs

This design also adds complexity.

The reader has to inspect three decorators to understand a call.

That is acceptable when the behaviors are:

- small,
- reusable,
- well named,
- documented,
- tested.

It becomes less attractive when every function has a large stack of hidden policies.

## 43.7 Production note

A mature application might use richer observability systems, structured logs, metrics, tracing, or policy layers.

This chapter deliberately keeps the implementation within the Python standard library and small enough to understand fully.

---

# 44. Practical Mini-Project — Production Function Instrumentation Toolkit

## 44.1 Goal

Build a small reusable module of decorators for instrumentation and validation.

Do not build a framework.

The goal is to demonstrate understanding.

## 44.2 Required decorators

Implement:

```text
log_calls
measure_time
validate_positive
retry
one parameterized decorator
```

## 44.3 Required engineering practices

Every decorator should:

- use `functools.wraps`,
- support `*args` and `**kwargs` where appropriate,
- preserve return values,
- have a clear purpose,
- have tests,
- document limitations.

## 44.4 Suggested structure

```text
production_function_instrumentation/
├── decorators.py
└── test_decorators.py
```

Keep the project intentionally small.

## 44.5 Expected behaviors

### `log_calls`

Given:

```python
@log_calls
def greet(name):
    return f"Hello {name}"
```

the decorator should record that the function was called and whether it completed or failed.

### `measure_time`

Given:

```python
@measure_time
def work():
    ...
```

record elapsed duration.

### `validate_positive`

Given:

```python
@validate_positive
def double(value):
    return value * 2
```

reject invalid values.

### `retry`

Given a controlled transient failure, the decorator should retry only the configured exception category and stop after the configured maximum.

### Parameterized decorator

Build something such as:

```python
@repeat(2)
def greet():
    ...
```

## 44.6 Testing scenarios

Test:

```text
normal function
function with positional args
function with keyword args
return value
None return
exception
metadata
stacked decorators
invalid configuration
method decoration
retry success after failure
retry exhaustion
```

## 44.7 Decorator ordering exercise

Create:

```python
@log_calls
@measure_time
def work():
    ...
```

and:

```python
@measure_time
@log_calls
def work():
    ...
```

Observe what changes.

Write a short explanation of the difference.

## 44.8 Document limitations

Your project documentation should answer:

```text
Does retry handle every exception?
Is logging safe for sensitive arguments?
Is timing suitable for rigorous benchmarking?
Is the stateful decorator safe under concurrency?
Can decorators change debugging behavior?
```

---

# 45. Progressive Coding Exercises

Do these without immediately looking for a finished solution.

## Level 1 — Fundamentals

### Exercise 1: Create a simple decorator

Write:

```python
@announce
def greet():
    print("Hello")
```

Expected behavior:

```text
Starting
Hello
Finished
```

### Exercise 2: Preserve a return value

Write a decorator around:

```python
def add(a, b):
    return a + b
```

Verify:

```python
add(2, 3) == 5
```

---

## Level 2 — Arguments and metadata

### Exercise 3: Positional arguments

Create a decorator that works with:

```python
def multiply(a, b):
    return a * b
```

### Exercise 4: Keyword arguments

Verify that:

```python
multiply(a=4, b=5)
```

works.

### Exercise 5: Metadata

Add:

```python
from functools import wraps

def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

and verify:

```python
__name__
__doc__
```

are preserved.

---

## Level 3 — Practical decorators

### Exercise 6: Timing

Create:

```python
@measure_time
def calculate():
    ...
```

Record elapsed time.

### Exercise 7: Logging

Use:

```python
logging
```

instead of `print`.

Log start and completion.

### Exercise 8: Validation

Create:

```python
@require_positive
def square_root_input(value):
    ...
```

Reject invalid values.

---

## Level 4 — Composition

### Exercise 9: Parameterized decorator

Implement:

```python
@repeat(3)
def greet():
    ...
```

### Exercise 10: Two decorators

Create:

```python
@outer
@inner
def work():
    ...
```

Print messages before and after and explain the execution order.

### Exercise 11: Reverse the order

Swap them:

```python
@inner
@outer
def work():
    ...
```

Explain what changed.

---

## Level 5 — State and object behavior

### Exercise 12: Stateful decorator

Implement a call counter.

The first call should report:

```text
1
```

the second:

```text
2
```

etc.

### Exercise 13: Method decorator

Decorate:

```python
class Calculator:
    @your_decorator
    def add(self, a, b):
        return a + b
```

Make sure method binding still works.

### Exercise 14: Class decorator

Create a class decorator that adds simple metadata:

```python
@mark_service
class Example:
    pass
```

---

## Level 6 — Engineering reasoning

### Exercise 15: Broken decorator debugging

Debug this intentionally broken code:

```python
def broken(function):
    def wrapper(*args, **kwargs):
        print("Before")
        function(*args, **kwargs)
        print("After")
    # missing return wrapper
```

Identify the failure.

### Exercise 16: Another broken decorator

Debug:

```python
def broken(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        function(*args, **kwargs)

    return wrapper
```

What happens to the return value?

### Exercise 17: Architecture question

You have a function that requires a policy check, logging, and timing.

Would you use:

```python
@policy
@log
@timing
def operation():
    ...
```

or explicit helper functions?

Explain the trade-offs, not just the syntax.

---

# 46. Knowledge Check

## Basic

### 1. What is a decorator?

Your answer should mention:

```text
callable
receives another callable
returns a callable
adds or changes behavior
```

Do not merely say "a function with @".

### 2. Why are functions called first-class objects?

Reason toward:

```text
they can be assigned
passed
returned
stored
used as values
```

### 3. What does `@decorator` mean?

Explain its conceptual relationship to:

```python
function = decorator(function)
```

### 4. What is a wrapper function?

Describe the callable that controls execution around the wrapped callable.

### 5. What is a closure?

Explain captured state from an enclosing lexical scope.

## Intermediate

### 6. Why do decorators commonly use `*args` and `**kwargs`?

Discuss practical argument forwarding.

### 7. Why should `functools.wraps` normally be used?

Discuss metadata and introspection.

### 8. Why must a wrapper return the original result?

Discuss preservation of the function's return contract.

### 9. What is the difference between decoration time and execution time?

Use a concrete trace.

### 10. How do multiple decorators work?

Expand:

```python
@a
@b
def f():
    ...
```

into an explicit conceptual form.

## Advanced

### 11. Explain decorator factories.

Distinguish:

```text
configuration
decoration
execution
```

### 12. Explain decorator order.

Discuss how nesting changes execution and semantics.

### 13. Explain stateful decorators.

Discuss:

```text
closure
nonlocal
lifecycle
concurrency considerations
```

### 14. Why can decorators complicate debugging?

Discuss:

```text
wrapper frames
hidden control flow
stacking
metadata
execution order
```

### 15. When should a decorator not be used?

Discuss situations where explicit code is clearer.

### 16. How can decorators affect introspection?

Discuss:

```python
__name__
__doc__
__wrapped__
inspect.signature
```

### 17. Why can a synchronous decorator be incorrect for an async function?

Explain the coroutine boundary and `await`.

### 18. What are the trade-offs of many decorators?

Discuss:

```text
reuse vs readability
centralization vs hidden behavior
composition vs debugging
```

---

# 47. Interview Questions

This section should be used for reasoning practice, not memorization.

## 1. What is a decorator in Python?

**Expected reasoning direction:**

Start with first-class callables, then explain:

```text
decorator(callable) → callable
```

Mention that a common implementation returns a wrapper and that the function name is rebound.

---

## 2. How does `@decorator` syntax work?

**Expected reasoning direction:**

Show:

```python
@decorator
def f():
    ...
```

and explain the conceptual equivalent:

```python
f = decorator(f)
```

Do not confuse this with mutating the original function object.

---

## 3. Explain decorators using higher-order functions.

**Expected reasoning direction:**

Explain that decorators rely on functions being passed around and returned.

---

## 4. Explain closures and their relationship to decorators.

**Expected reasoning direction:**

A nested wrapper can retain access to the original function through its enclosing scope.

Then mention that closures are common, not mandatory.

---

## 5. What does `functools.wraps` do?

**Expected reasoning direction:**

Discuss metadata preservation and the `__wrapped__` relationship.

A strong answer should explain why this matters to developers and tools.

---

## 6. Why use `*args` and `**kwargs`?

**Expected reasoning direction:**

Explain general positional and keyword argument forwarding.

A strong answer should acknowledge that broad forwarding does not guarantee perfect semantic preservation for every callable.

---

## 7. What happens if a decorator does not return the wrapper?

**Expected reasoning direction:**

The decorated name may become whatever the decorator returned, potentially `None`, making the function unusable.

---

## 8. What happens if a wrapper does not return the original result?

**Expected reasoning direction:**

The caller receives the wrapper's implicit `None`, even if the original returned a value.

---

## 9. How do you write a parameterized decorator?

**Expected reasoning direction:**

Explain the three layers:

```text
factory(configuration)
    ↓
decorator(function)
    ↓
wrapper(args)
```

---

## 10. How does decorator order work?

**Expected reasoning direction:**

Expand:

```python
@a
@b
def f():
    ...
```

into:

```python
f = a(b(f))
```

Then discuss execution order.

---

## 11. How would you implement a timing decorator?

**Expected reasoning direction:**

Use:

```text
start
try call
finally calculate elapsed
```

and choose a suitable monotonic timing source such as `perf_counter`.

Do not call it a rigorous benchmark system.

---

## 12. How would you implement a retry decorator safely?

**Expected reasoning direction:**

A strong answer should mention:

```text
retryable exceptions
bounded attempts
backoff
jitter
timeouts
idempotency
observability
load amplification
```

The candidate should explicitly state that not every operation is safe to retry.

---

## 13. How would you decorate a method?

**Expected reasoning direction:**

Explain that `self` participates in the arguments received by the wrapper and that argument forwarding must preserve the method's calling convention.

---

## 14. What is a class decorator?

**Expected reasoning direction:**

A callable receives a class object and returns an appropriate class object or replacement.

---

## 15. When should decorators not be used?

**Expected reasoning direction:**

Discuss readability, hidden behavior, uniqueness of use, debugging, surprising side effects, and simpler alternatives.

---

## 16. How can decorators make production systems harder to debug?

**Expected reasoning direction:**

Discuss nested wrappers, stack traces, hidden policies, order, side effects, and metadata.

---

## 17. How would you test a decorator?

**Expected reasoning direction:**

Test observable contract:

```text
normal result
arguments
keywords
exception behavior
metadata
edge cases
composition
```

---

## 18. How would you explain decorators to a junior developer?

**Expected reasoning direction:**

Start with:

```text
functions are objects
```

then:

```text
pass a function
return a function
wrap the function
```

Only after that introduce `@`.

A strong explanation should avoid starting with metaprogramming jargon.

---

# 48. Final Mental Model

The entire topic can now be compressed into one chain.

```text
Python functions are objects
        ↓
Can assign functions to names
        ↓
Can pass functions as arguments
        ↓
Can return functions
        ↓
Nested functions can access enclosing scope
        ↓
Closures preserve access to captured values
        ↓
Decorator receives a callable
        ↓
Decorator creates/returns another callable
        ↓
@decorator applies that callable transformation
        ↓
Calling decorated function
        ↓
Wrapper executes
        ↓
Wrapper may add reusable behavior
        ↓
Wrapper may call original function
        ↓
Return value / exception semantics should be deliberately preserved
```

## Core formula

A useful simplified formula is:

```text
decorator(function) → wrapper
```

Then:

```python
@decorator
def function():
    ...
```

conceptually becomes:

```python
function = decorator(function)
```

When the name is later called:

```python
function(...)
```

the object bound to that name is the returned callable.

## Closure mental model

```text
decorator(original_function)
        ↓
wrapper captures original_function
        ↓
wrapper is returned
        ↓
name points to wrapper
        ↓
wrapper invokes original_function
```

## Parameterized decorator mental model

```text
@factory(configuration)
def function():
    ...
```

becomes conceptually:

```text
factory(configuration)
        ↓
decorator
        ↓
decorator(function)
        ↓
wrapper
```

## Production principle

> Use decorators when they improve clarity and separate reusable cross-cutting concerns.

And equally important:

> Do not use decorators merely because the feature is available.

A production-quality decorator should be:

- understandable,
- narrowly scoped,
- correctly ordered,
- testable,
- observable,
- explicit about side effects,
- careful with exceptions,
- careful with state,
- compatible with the callable's execution model,
- and worth the abstraction cost.

---

# Appendix A — Quick Reference

## Basic decorator

```python
from functools import wraps


def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        # before
        result = function(*args, **kwargs)
        # after
        return result

    return wrapper
```

## Apply decorator

```python
@decorator
def function():
    ...
```

Conceptually:

```python
function = decorator(function)
```

## Parameterized decorator

```python
def factory(option):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapper

    return decorator
```

Use:

```python
@factory(option=3)
def function():
    ...
```

## Multiple decorators

```python
@a
@b
def f():
    ...
```

Conceptually:

```python
f = a(b(f))
```

## Method-friendly wrapper

```python
def decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper
```

## Async-aware wrapper

```python
def decorator(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        return await function(*args, **kwargs)

    return wrapper
```

---

# Appendix B — Diagnostic Checklist

When a decorator behaves unexpectedly, ask these questions in order:

```text
1. What callable does the decorated name refer to?
2. Did the decorator return a callable?
3. Did the wrapper return the wrapped result?
4. Are arguments forwarded correctly?
5. Is @wraps being used?
6. Did the decorator execute during definition/import time?
7. Are multiple decorators stacked?
8. What is their order?
9. Is mutable or shared state involved?
10. Is the target a method, class, or async function?
11. What exception behavior did the wrapper introduce?
12. Can the same behavior be expressed more clearly without a decorator?
```

A particularly useful debugging technique is to temporarily reduce a complex stack:

```python
@a
@b
@c
def function():
    ...
```

to:

```python
def function():
    ...
```

Then add one decorator at a time.

This turns a complex debugging problem into a controlled experiment.

---

# Appendix C — Engineering Checklist Before Shipping a Decorator

Use this checklist during code review.

## Purpose

- Is the decorator solving a real repeated problem?
- Is the behavior cross-cutting?
- Is the purpose obvious from the name?

## Contract

- Are arguments preserved?
- Is the return value preserved?
- Are exceptions preserved or intentionally transformed?
- Are side effects documented?

## Metadata

- Is `functools.wraps` used?
- Is introspection still reasonable?

## Composition

- Does it compose predictably with other decorators?
- Does order matter?
- Is the required order obvious?

## State

- Does the decorator maintain state?
- What is the state lifecycle?
- Is shared state safe under the intended execution model?

## Performance

- Does the wrapper add meaningful overhead?
- Is expensive work happening during decoration?
- Is lazy execution preferable for any expensive behavior?

## Debugging

- Are wrapper layers understandable?
- Do errors remain actionable?
- Can developers identify the original callable?

## Testing

- Are normal calls covered?
- Are positional and keyword arguments covered?
- Are return values covered?
- Are exceptions covered?
- Are edge cases covered?
- Is composition covered where relevant?

## Design judgment

- Would a helper function be clearer?
- Would explicit composition be clearer?
- Is the abstraction worth its cognitive cost?

---

# Final Takeaway

A decorator is not primarily an `@` symbol.

The `@` syntax is the final, convenient expression of a deeper Python mechanism:

```text
functions are objects
        ↓
higher-order functions
        ↓
nested functions
        ↓
closures
        ↓
callable transformation
        ↓
wrappers
        ↓
decorators
```

The most important engineering habit is to keep the wrapper's behavior understandable.

A good decorator says:

> "Apply this small, reusable concern around this callable."

A problematic decorator says:

> "There is a lot of invisible behavior here; you will need to inspect six files to find out what this function actually does."

The difference is engineering judgment.

In production Python, the goal is not to maximize decorator usage. The goal is to use decorators selectively so that reusable cross-cutting behavior becomes easier to apply **without making the program harder to understand, debug, test, and maintain**.
