# 07 — Exceptions, Validation, and Useful Errors
## Complete Lesson Summary, Project-Tree Review, and Exercise Solutions

**Roadmap position:** Stage 1 — Programming & Computational Thinking → Module 03 — Control Flow, Functions, Scope, and Errors → Lesson 07  
**Source lesson:** `07-exceptions-validation-and-useful-errors.md`

---

# Part A — Complete lesson summary (under 5,000 words)

## 1. Why exceptions and validation matter

Real programs receive imperfect input. A user may type text where a number is expected, a dictionary may not contain a key, or a list may be empty. The program must decide how to respond.

There are three broad possibilities:

1. Stop with a confusing error.
2. Continue silently and produce an incorrect result.
3. Detect the problem and report it clearly.

The goal of this lesson is to make the third response deliberate. You learn to recognize common Python exceptions, validate input before using it, catch only expected exceptions, and provide useful messages.

An error handled correctly is not necessarily a failure of the program. It can be the program enforcing its rules.

## 2. Learning outcomes and prerequisites

By the end of the lesson, you should be able to:

- Distinguish a syntax error from a runtime exception.
- Read a traceback and identify the actual cause.
- Recognize `ValueError`, `TypeError`, `KeyError`, `IndexError`, `ZeroDivisionError`, and `NameError`.
- Distinguish invalid user input from a programming bug.
- Explain why bare `except:` and broad `except Exception:` are dangerous.
- Validate input at the boundary before business logic uses it.
- Write narrow `try`/`except` blocks for specific expected failures.
- Use `else`, `finally`, and `raise` correctly.
- Define a minimal custom exception when a domain rule needs its own name.
- Write clear, safe error messages.

The source identifies these prerequisites:

- **Conditionals, Guards, and Boolean Logic:** validation uses guard-style `if`/`elif` checks.
- **Functions, Parameters, and Return Values:** validation and exceptions are used inside functions.
- **Pure Functions and Side Effects:** raising a clear exception is preferable to silently returning a misleading value.
- **Type Conversion and Truthiness:** `int()` conversion can raise `ValueError`.
- **Dictionaries and Lookups:** missing dictionary keys raise `KeyError`; `.get()` provides a default.

## 3. Key terms

| Term | Meaning |
|---|---|
| Syntax error | Python finds invalid grammar before the program runs, such as a missing colon. |
| Exception | A runtime error that interrupts normal program flow. |
| Traceback | Python's report showing the calls that led to an unhandled exception and the final error. |
| `raise` | Deliberately causes an exception. |
| `try` | Contains code Python attempts to execute while watching for selected exceptions. |
| `except` | Handles a matching exception raised inside the associated `try`. |
| `else` | Runs only when the `try` block completes normally. |
| `finally` | Runs whenever control leaves the `try` statement, including after an exception or `return`. |
| Validation | Checks whether data satisfies the rules the program requires. |
| Boundary | The point where data first enters a program or function. |
| Custom exception | A new exception type created to name a specific rule in your program. |

## 4. Syntax errors versus runtime exceptions

A **syntax error** is found before execution because the code does not follow Python grammar. For example, forgetting the colon after an `if` statement.

An **exception** occurs while valid Python code is running. The code may be grammatically correct but fail for the actual data it receives. Dividing by zero is one example.

Consider:

```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

print(calculate_average([]))
print("This line never runs.")
```

The empty list has length zero. Therefore, the function attempts to divide by zero. The second `print()` is never reached because an unhandled exception stops normal execution.

Python displays a traceback similar to:

```text
Traceback (most recent call last):
  File "average.py", line 4, in <module>
    print(calculate_average([]))
  File "average.py", line 2, in calculate_average
    return sum(numbers) / len(numbers)
ZeroDivisionError: division by zero
```

### How to read a traceback

Read it **from the bottom upward**:

1. The final line gives the exception type and message: `ZeroDivisionError: division by zero`.
2. The `File`, `line`, and `in` entries show the call sequence.
3. In this example, line 4 called `calculate_average([])`, and line 2 failed inside the function.
4. The displayed source line and any caret/tilde markers help identify the expression being evaluated when the error occurred.

A traceback is evidence. Read it carefully before guessing or searching for a solution.

## 5. Six common built-in exceptions

### 5.1 `ValueError`

The value has an acceptable general type for the operation, but its content is invalid.

```python
int("abc")
```

Output:

```text
ValueError: invalid literal for int() with base 10: 'abc'
```

`int()` can convert numeric text such as `"25"`, but it cannot convert `"abc"` into an integer.

### 5.2 `TypeError`

An operation or function receives a type it cannot use.

```python
"5" + 3
```

Output:

```text
TypeError: can only concatenate str (not "int") to str
```

The `+` operation here is trying to combine a string and an integer.

### 5.3 `KeyError`

A dictionary lookup requests a key that does not exist.

```python
{"a": 1}["b"]
```

Output:

```text
KeyError: 'b'
```

### 5.4 `IndexError`

A list or string lookup requests a position that does not exist.

```python
[1, 2, 3][10]
```

Output:

```text
IndexError: list index out of range
```

Valid list positions here are `0`, `1`, and `2`.

### 5.5 `ZeroDivisionError`

A division operation uses zero as the denominator.

```python
10 / 0
```

Output:

```text
ZeroDivisionError: division by zero
```

### 5.6 `NameError`

The code uses a name Python has not defined, often because of a typo.

```python
print(undefined_name)
```

Output:

```text
NameError: name 'undefined_name' is not defined
```

Knowing these names helps you understand the final line of a traceback quickly.

### Exception hierarchy

A simplified part of Python's exception hierarchy is:

```text
BaseException
└── Exception
    ├── ValueError
    ├── TypeError
    ├── LookupError
    │   ├── KeyError
    │   └── IndexError
    └── ...
```

`KeyError` and `IndexError` are specific subclasses of `LookupError`. `Exception` is much broader. Consequently, `except Exception:` can catch many different failures that your code did not intend to handle.

## 6. Expected invalid input versus programmer bugs

These two categories must not be confused.

**Expected invalid input** is a normal possibility at a program boundary:

- A user enters letters instead of a number.
- A required field is blank.
- A percentage is outside the allowed range.

The program should validate or handle these cases deliberately.

**A programmer bug** is a defect in the code:

- A variable name is misspelled.
- Arguments are passed in the wrong order.
- A required programming step was forgotten.

A programmer bug should usually be fixed, not hidden by an exception handler.

### Why bare `except:` is dangerous

The lesson gives this deliberately faulty example:

```python
def calculate_total(price, quantity):
    try:
        return pdice * quantity
    except:
        return 0

print(calculate_total(9.99, 3))
```

Output:

```text
0
```

`pdice` is a typo for `price`. It should cause `NameError`. However, bare `except:` catches the error and returns `0`. The output looks plausible, but it is wrong. The real bug has been hidden.

Prefer a specific handler such as `except ValueError:` or `except KeyError:`. Avoid bare `except:` and broad `except Exception:` for ordinary input handling.

A specific handler is not a guarantee that no bug will be hidden: an unrelated bug might raise the same exception type. This is another reason to keep the `try` block narrow.

## 7. Input validation at the boundary

Validation and exception handling are related, but they are not the same:

- **Validation** checks whether data meets required rules.
- **Exception handling** decides what to do when an exception is raised.

Validation should happen at the **boundary**, where data first enters a function or program, before the main work relies on it.

Typical checks include:

- Is the value present?
- Is it the expected type?
- Is it within the allowed range?
- Is it unexpectedly empty?
- Are required dictionary keys present?

### Complete source example: validating a price

```python
import math

def validate_price(price):
    if not isinstance(price, (int, float)):
        return "Price must be a number."
    if isinstance(price, bool):
        return "Price must be a number."
    if not math.isfinite(price):
        return "Price must be a finite number."
    if price <= 0:
        return "Price must be greater than zero."
    return None

prices_to_check = [19.99, -5, "twenty", 0]

for price in prices_to_check:
    error = validate_price(price)
    if error is None:
        print(price, "-> valid")
    else:
        print(price, "->", error)
```

Output:

```text
19.99 -> valid
-5 -> Price must be greater than zero.
twenty -> Price must be a number.
0 -> Price must be greater than zero.
```

Step by step:

1. `import math` makes the `math` module available.
2. `isinstance(price, (int, float))` accepts integer or floating-point numbers.
3. The separate Boolean check matters because Python treats `bool` as a subtype of `int`; otherwise `True` could pass as a price.
4. `math.isfinite(price)` rejects non-finite values such as `float("nan")` and `float("inf")`.
5. `price <= 0` rejects zero and negative prices.
6. `return None` means no validation problem was found.
7. The loop tests each value and prints either `valid` or the returned error message.

This validator's rule is: a price must be a non-Boolean, finite number greater than zero. Each error message explains what is wrong and what is expected.

## 8. `try` and `except`

A `try` block contains an operation that may raise an expected exception. If the specified exception occurs, the matching `except` block runs.

### Safe division

```python
def safe_divide(numerator, denominator):
    try:
        return numerator / denominator
    except ZeroDivisionError:
        print("Cannot divide by zero.")
        return None

print(safe_divide(10, 2))
print(safe_divide(10, 0))
```

Output:

```text
5.0
Cannot divide by zero.
None
```

Only `ZeroDivisionError` is caught. Other exception types are allowed to surface.

`None` is used to represent the absence of a successful numeric result. Returning `0` would be ambiguous because zero can be a legitimate result.

### Capturing an exception with `as`

```python
def parse_age(raw_age):
    try:
        return int(raw_age)
    except ValueError as error:
        print(f"Could not parse age: {error}")
        return None

print(parse_age("25"))
print(parse_age("twenty"))
```

Output:

```text
25
Could not parse age: invalid literal for int() with base 10: 'twenty'
None
```

`except ValueError as error` stores the exception object in the variable `error`. Its message can be displayed when that detail is useful.

### Keep the `try` block narrow

Only put the operation whose expected exception you intend to handle inside `try`. Unrelated code inside the same block may raise the same exception type for a completely different reason.

The lesson's first receipt example is intentionally too broad:

```python
def build_receipt_line(item_name, unit_price, quantity):
    try:
        line_total = unit_price * quantity
        summary = "Total: $" + line_total
    except TypeError:
        print("Invalid price or quantity.")
        return None
    return summary

print(build_receipt_line("Pen", 2, 3))
```

Output:

```text
Invalid price or quantity.
None
```

The multiplication is valid: `2 * 3` produces `6`. The actual bug is concatenating a string with the integer `6`. The `+` operation raises `TypeError`, and the broad `try` incorrectly reports that the price or quantity is invalid.

The corrected version is:

```python
def build_receipt_line(item_name, unit_price, quantity):
    try:
        line_total = unit_price * quantity
    except TypeError:
        print("Invalid price or quantity.")
        return None

    summary = "Total: $" + str(line_total)
    return summary

print(build_receipt_line("Pen", 2, 3))
```

Output:

```text
Total: $6
```

Now the `try` block contains only the multiplication. The string conversion and concatenation happen outside it, so unrelated bugs are not mislabeled as invalid numeric input.

## 9. `else` and `finally`

A `try` statement can have two optional blocks in addition to `except`.

- `else` runs only if the `try` block completes normally without an exception. If the `try` block exits early using `return`, `break`, or `continue`, `else` does not run.
- `finally` runs whenever control leaves the `try` statement: after success, after an exception, or when leaving through something like `return`.

Example:

```python
def parse_age(raw_age):
    try:
        age = int(raw_age)
    except ValueError:
        print(f"'{raw_age}' is not a valid whole number.")
    else:
        print(f"Parsed age: {age}")
    finally:
        print("Finished checking one value.")

parse_age("25")
parse_age("twenty")
```

Output:

```text
Parsed age: 25
Finished checking one value.
'twenty' is not a valid whole number.
Finished checking one value.
```

For `"25"`, conversion succeeds, so `else` runs. For `"twenty"`, conversion raises `ValueError`, so `except` runs and `else` is skipped. `finally` runs in both cases.

Use `finally` for an action that must happen regardless of success or failure, such as a cleanup or logging step.

## 10. Raising exceptions with `raise`

`raise` deliberately creates an exception. A function can use it to reject invalid input immediately.

```python
def calculate_discounted_price(price, discount_percentage):
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError(
            f"Invalid discount_percentage: {discount_percentage}. "
            "Expected a number between 0 and 100."
        )
    return price * (1 - discount_percentage / 100)

print(calculate_discounted_price(100, 20))
```

Output:

```text
80.0
```

A discount of `20` means 20%, so the customer pays 80% of the original price.

Calling it with `150` raises:

```text
ValueError: Invalid discount_percentage: 150. Expected a number between 0 and 100.
```

The function refuses invalid data instead of silently returning `0` or the original price. A wrong placeholder could flow into totals, reports, or invoices and become difficult to trace.

### The caller decides how to respond

```python
def calculate_discounted_price(price, discount_percentage):
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError(
            f"Invalid discount_percentage: {discount_percentage}. "
            "Expected a number between 0 and 100."
        )
    return price * (1 - discount_percentage / 100)

discount_requests = [(100, 20), (50, 150)]

for price, discount_percentage in discount_requests:
    try:
        final_price = calculate_discounted_price(price, discount_percentage)
        print(f"Final price: ${final_price:.2f}")
    except ValueError as error:
        print(f"Skipping this request: {error}")
```

Output:

```text
Final price: $80.00
Skipping this request: Invalid discount_percentage: 150. Expected a number between 0 and 100.
```

The function's responsibility is to reject invalid data clearly. The caller decides to skip that request and continue processing the batch.

### Exception propagation

An exception does not need to be handled inside the function where it occurs. If no matching handler exists there, it propagates to the caller.

```python
def parse_number(text):
    return int(text)

def process_value(text):
    return parse_number(text)

try:
    process_value("abc")
except ValueError:
    print("The caller handled the invalid input.")
```

Output:

```text
The caller handled the invalid input.
```

Flow:

```text
process_value()
    ↓
parse_number()
    ↓
int("abc") raises ValueError
    ↓
No handler inside parse_number()
    ↓
Exception propagates through process_value()
    ↓
Caller catches ValueError
```

This is called **exception propagation**. A caller higher in the call chain can decide how to handle the failure.

## 11. Small custom exceptions

Built-in exceptions are usually enough. However, sometimes a specific business or domain rule deserves its own exception name.

```python
class InvalidTransitionError(Exception):
    pass

def change_traffic_light(current_color, requested_color):
    allowed_next = {"red": "green", "green": "yellow", "yellow": "red"}

    if requested_color != allowed_next[current_color]:
        raise InvalidTransitionError(
            f"Cannot go from {current_color} to {requested_color}."
        )
    return requested_color

print(change_traffic_light("red", "green"))

try:
    change_traffic_light("red", "yellow")
except InvalidTransitionError as error:
    print(f"Rejected: {error}")
```

Output:

```text
green
Rejected: Cannot go from red to yellow.
```

The minimal syntax is:

```python
class InvalidTransitionError(Exception):
    pass
```

It creates a new exception type that is also an `Exception`. `pass` means no additional body is needed. The name makes the domain rule explicit: an invalid state transition.

Do not create a custom exception for every function. Use `ValueError` or `TypeError` with a clear message in ordinary cases. A custom exception is worthwhile when the rule itself deserves a distinct name. Full class design is intentionally left to a later module.

## 12. Designing useful error messages

A useful error message should:

1. State what input was invalid, when it is safe to show.
2. State the expected format, range, or rule.
3. Avoid exposing secrets or sensitive values. Never echo a password in an error.
4. Help both the person using the program and the developer diagnosing it.
5. Fail safely instead of allowing invalid data to continue through the program.

Example:

```python
def validate_age_bad(age):
    if age < 0 or age > 120:
        raise ValueError("Invalid input.")

def validate_age_good(age):
    if isinstance(age, bool) or not isinstance(age, int) or age < 0 or age > 120:
        raise ValueError(
            f"Invalid age: {age}. Age must be a whole number between 0 and 120."
        )

try:
    validate_age_bad(-5)
except ValueError as error:
    print("Bad message:", error)

try:
    validate_age_good(-5)
except ValueError as error:
    print("Good message:", error)
```

Output:

```text
Bad message: Invalid input.
Good message: Invalid age: -5. Age must be a whole number between 0 and 120.
```

The second message identifies the received value and the rule it violated. The good validator also checks type and excludes Boolean values, because `bool` is a subtype of `int`.

## 13. All seven lesson examples

The source then applies the concepts in seven complete examples.

### Example 1 — Safe division

```python
def safe_divide(numerator, denominator):
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return None

results = [(10, 2), (7, 0), (9, 3)]

for numerator, denominator in results:
    result = safe_divide(numerator, denominator)
    if result is None:
        print(f"{numerator} / {denominator} -> cannot divide by zero")
    else:
        print(f"{numerator} / {denominator} -> {result}")
```

Output:

```text
10 / 2 -> 5.0
7 / 0 -> cannot divide by zero
9 / 3 -> 3.0
```

The function catches only the expected `ZeroDivisionError`. The loop continues after the middle pair fails. `None` represents failure without confusing it with a valid numeric zero, and `is None` checks that result explicitly.

### Example 2 — Parsing an age with all four blocks

```python
def parse_age(raw_age):
    try:
        age = int(raw_age)
    except ValueError:
        print(f"'{raw_age}' is not a valid age. Please enter a whole number.")
        return None
    else:
        return age
    finally:
        print(f"Checked input: '{raw_age}'")

for raw_age in ["25", "thirty", "42"]:
    age = parse_age(raw_age)
    print("Result:", age)
```

Output:

```text
Checked input: '25'
Result: 25
'thirty' is not a valid age. Please enter a whole number.
Checked input: 'thirty'
Result: None
Checked input: '42'
Result: 42
```

`"thirty"` is realistic invalid input for `int()`. The `else` returns the parsed age only on success. `finally` prints after every attempt, even when the function returns from `except` or `else`.

### Example 3 — Price validation with specific exceptions

```python
import math

def validate_price(price):
    if not isinstance(price, (int, float)) or isinstance(price, bool):
        raise TypeError(f"Invalid price: {price!r}. Expected a number.")
    if not math.isfinite(price):
        raise ValueError(f"Invalid price: {price}. Price must be a finite number.")
    if price <= 0:
        raise ValueError(f"Invalid price: {price}. Price must be greater than zero.")

prices_to_check = [19.99, -5, "twenty"]

for price in prices_to_check:
    try:
        validate_price(price)
        print(f"{price} -> valid")
    except (TypeError, ValueError) as error:
        print(f"{price} -> rejected: {error}")
```

Output:

```text
19.99 -> valid
-5 -> rejected: Invalid price: -5. Price must be greater than zero.
twenty -> rejected: Invalid price: 'twenty'. Expected a number.
```

Wrong type raises `TypeError`. A numeric value that is non-finite or not greater than zero raises `ValueError`. The tuple in `except (TypeError, ValueError)` catches exactly those two anticipated types.

### Example 4 — Optional dictionary value

```python
def get_shipping_note_direct(order, key):
    try:
        return order[key]
    except KeyError:
        return "No note provided."

def get_shipping_note_safe(order, key):
    return order.get(key, "No note provided.")

order = {"item": "Notebook", "quantity": 2}

print(get_shipping_note_direct(order, "note"))
print(get_shipping_note_safe(order, "note"))
print(get_shipping_note_safe(order, "item"))
```

Output:

```text
No note provided.
No note provided.
Notebook
```

Both functions handle a missing optional key. `.get(key, default)` is simpler when the only response is one default value. `try`/`except KeyError` is useful when missing-key handling requires several statements or a different action.

### Example 5 — Discount percentage range

```python
def calculate_discounted_price(price, discount_percentage):
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError(
            f"Invalid discount_percentage: {discount_percentage}. "
            "Expected a number between 0 and 100."
        )
    return price * (1 - discount_percentage / 100)

discount_requests = [(100, 20), (50, 150), (80, -10)]

for price, discount_percentage in discount_requests:
    try:
        final_price = calculate_discounted_price(price, discount_percentage)
        print(f"Final price: ${final_price:.2f}")
    except ValueError as error:
        print(f"Skipping this request: {error}")
```

Output:

```text
Final price: $80.00
Skipping this request: Invalid discount_percentage: 150. Expected a number between 0 and 100.
Skipping this request: Invalid discount_percentage: -10. Expected a number between 0 and 100.
```

The function raises for percentages outside the inclusive range `0`–`100`. The caller handles each bad request individually, so one invalid item does not stop the rest of the batch. This example validates the discount range; it does not add separate type or price validation.

### Example 6 — Traffic-light transition and custom exception

```python
class InvalidTransitionError(Exception):
    pass

def change_traffic_light(current_color, requested_color):
    allowed_next = {"red": "green", "green": "yellow", "yellow": "red"}

    if requested_color != allowed_next[current_color]:
        raise InvalidTransitionError(
            f"Cannot go from {current_color} to {requested_color}."
        )
    return requested_color

current_color = "red"
requested_colors = ["green", "red", "yellow"]

for requested_color in requested_colors:
    try:
        current_color = change_traffic_light(current_color, requested_color)
        print(f"Light is now {current_color}.")
    except InvalidTransitionError as error:
        print(f"Rejected: {error}")
```

Output:

```text
Light is now green.
Rejected: Cannot go from green to red.
Light is now yellow.
```

The valid transitions are red → green, green → yellow, and yellow → red. The first request succeeds. The second request is invalid because the current state is green; it is rejected and does not update `current_color`. The third request succeeds. The custom exception names this domain-specific rule.

### Example 7 — Registration validator that collects every error

```python
def validate_registration(data):
    errors = []

    if "name" not in data or data["name"].strip() == "":
        errors.append("Name is required.")

    if "age" not in data:
        errors.append("Age is required.")
    else:
        try:
            age = int(data["age"])
            if age < 0 or age > 120:
                errors.append(f"Age must be between 0 and 120, got {age}.")
        except ValueError:
            errors.append(f"Age must be a whole number, got '{data['age']}'.")

    email = data.get("email", "")
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        errors.append("A valid email address is required.")

    return errors

submissions = [
    {"name": "Ada", "age": "30", "email": "ada@example.com"},
    {"name": "", "age": "abc", "email": "not-an-email"},
]

for submission in submissions:
    errors = validate_registration(submission)
    if errors:
        print("Registration rejected:")
        for error in errors:
            print(" -", error)
    else:
        print("Registration accepted.")
```

Output:

```text
Registration accepted.
Registration rejected:
 - Name is required.
 - Age must be a whole number, got 'abc'.
 - A valid email address is required.
```

Step by step:

1. `errors = []` creates a list to collect all validation problems.
2. The name check verifies that the key exists and the value is not empty or whitespace-only.
3. The age check first checks for the required key.
4. If present, `int(data["age"])` attempts conversion. A `ValueError` adds a useful message instead of stopping validation.
5. A successfully converted age is checked against the inclusive range `0`–`120`.
6. `data.get("email", "")` supplies an empty string if the optional lookup has no value; the validation then rejects it.
7. The email rule is intentionally basic: `@` must exist and cannot be the first or last character. It is not a complete email-address validator.
8. The function returns the full list of errors. An empty list means no errors were found.
9. The caller prints every error, rather than forcing the user to correct one problem and submit again to discover another.

The source assumes `data` is a dictionary, `name` and `email` values are strings, and the age value is suitable for attempting `int()` conversion. It does not implement every possible type check.

## 14. Common beginner mistakes

- Catching every exception with bare `except:` or `except Exception:` and hiding real bugs.
- Putting unrelated operations inside one `try` block.
- Putting success-only logic in `try` instead of using `else`.
- Duplicating cleanup or logging code instead of putting it in `finally`.
- Returning a misleading placeholder such as `0`, `-1`, or `None` when invalid input should be rejected with `raise`.
- Writing vague messages such as `"Invalid input."`.
- Creating custom exceptions for every function instead of naming only meaningful domain rules.

## 15. Lesson summary and completion criteria

Remember these rules:

- Syntax errors are found before execution; exceptions occur at runtime.
- Read tracebacks from the bottom up.
- Learn the six common exception types and their causes.
- Handle expected invalid input deliberately; fix programmer bugs instead of hiding them.
- Validate data at the boundary.
- Catch specific exceptions and keep `try` narrow.
- `else` means successful `try`; `finally` runs when control leaves the `try` statement.
- Use `raise` to reject invalid data clearly.
- Let exceptions propagate to a caller when that caller is the right place to decide what happens next.
- Create a custom exception only when a meaningful domain rule needs its own name.
- Error messages should identify the invalid input and expected rule without revealing secrets.

You are ready to move on when you can explain each rule, read a traceback, write a narrow exception handler, validate a function's inputs, and complete the exercises below without copying the solutions.

## 16. Connection to later Applied AI and Agentic AI engineering

Later, model outputs, tool arguments, and API responses must be treated as untrusted input. They may be missing fields, have the wrong type, or violate a required range.

The same reasoning applies:

- Validate structured output at the boundary.
- Distinguish an expected failure (such as an empty model result or a tool timeout) from a bug in your own code.
- Report failures clearly so a caller or agent can decide whether to retry, ask for clarification, or stop safely.
- Do not hide failures behind broad exception handlers or misleading return values.

---

# Part B — Project-tree review and current learning-level assessment

## 1. Where this lesson sits

The retrieved roadmap project tree places this lesson here:

```text
Stage 1 — Programming & Computational Thinking/
├── 00-Stage-1-Overview/
│   ├── Projects/
│   ├── README.md
│   └── learning-plan.md
├── 01-Computational-Thinking-and-Program-Design/
├── 02-Python-Core-Language-and-Data-Types/
├── 03-Control-Flow-Functions-Scope-and-Errors/
│   ├── 01-conditionals-guards-and-boolean-logic.md
│   ├── 02-for-while-loops-and-loop-control.md
│   ├── 03-functions-parameters-and-return-values.md
│   ├── 04-function-arguments-defaults-and-docstrings.md
│   ├── 05-scope-lifetime-and-global-state.md
│   ├── 06-pure-functions-and-side-effects.md
│   ├── 07-exceptions-validation-and-useful-errors.md  ← current lesson
│   ├── README.md
│   └── practice-questions.md
├── 04-Problem-Solving-Collections-and-Algorithmic-Habits/
├── 05-Text-Files-Structured-Data-and-CLI-Programs/
├── 06-Modules-Packages-Dependencies-and-Code-Quality/
├── 07-Testing-and-Systematic-Debugging/
└── 08-Object-Oriented-Design-Data-Modelling-and-Functional-Style/
```

The Stage 1 overview contains four stage-level project briefs: a personal expense ledger CLI, a log investigation and reliability CLI, a data quality and transformation pipeline, and a rule-based risk review engine. The tree also defines module-level `README.md`, lesson files, `practice-questions.md`, and project/lab conventions.

The roadmap tree is a planned repository structure, not proof that every listed file is complete or implemented. This review uses the retrieved tree to locate the lesson and assess prerequisite coverage; it does not claim to have re-audited every physical file in your repository.

## 2. Learning progression relevant to this lesson

Your earlier work establishes the concepts this lesson depends on:

- **Conditionals and guards:** `if`, `elif`, `else`, Boolean conditions, and early checks.
- **Loops:** `for`, `while`, `break`, `continue`, and processing multiple records.
- **Functions:** parameters, return values, and separating a function's responsibility from its caller.
- **Arguments and defaults:** required and optional parameters, keyword-only parameters, and docstrings.
- **Scope and global state:** local/global names and avoiding hidden state.
- **Pure functions and side effects:** predictable return values and avoiding silent mutation.
- **Collections and problem solving:** lists, dictionaries, sets, searching, filtering, grouping, and aggregation.
- **Parsing:** strings, conversions, and regular expressions.

The current lesson combines these skills: guard checks validate input; functions raise or return results; loops process batches; dictionaries are checked for missing keys; and callers decide how to handle failures.

## 3. Current level assessment

**Assessment: beginner progressing toward intermediate Python programming.**

This is not a beginner's first exposure to Python. You have already worked through functions, control flow, scope, side effects, collections, algorithmic habits, parsing, and practice problems. You are now building the error-handling discipline required for reliable data-processing programs.

Your next capability target within this lesson is to become comfortable with:

1. Predicting which exception a statement can raise.
2. Reading tracebacks before changing code.
3. Separating invalid external data from defects in your own implementation.
4. Validating input before business logic runs.
5. Keeping exception handlers narrow and specific.
6. Designing functions that raise meaningful errors and callers that recover appropriately.
7. Writing validators that collect multiple independent field errors.

**Scope discipline:** the solutions below use only the lesson's concepts and the earlier foundations listed above. They use functions, conditionals, loops, lists, dictionaries, string methods, type conversion, and exception handling. They do not introduce OOP designs, external libraries, testing frameworks, or advanced validation packages. The one custom exception is included because the current lesson explicitly teaches the minimal `class Name(Exception): pass` pattern.

---

# Part C — All six exercises solved step by step (under 3,500 words)

## Exercise 1 — Intentionally cause each of the six standard exceptions

Each snippet is intentionally faulty. Run each one separately so the first exception does not prevent the remaining examples from running.

### 1. `ValueError`

```python
age = int("twenty")
```

**Cause:** `int()` expects text representing an integer. `"twenty"` is text, but it does not contain a valid integer representation, so Python raises `ValueError`.

### 2. `TypeError`

```python
total = "500" + 100
```

**Cause:** the `+` operation is given a string and an integer. Convert one value first if combining them is intended, for example `int("500") + 100`.

### 3. `KeyError`

```python
customer = {"name": "Asha", "city": "Kolkata"}
print(customer["email"])
```

**Cause:** the dictionary has no `"email"` key. Direct indexing raises `KeyError`. If the key is optional, use `customer.get("email", "Not provided")`.

### 4. `IndexError`

```python
scores = [75, 82, 91]
print(scores[5])
```

**Cause:** the list has valid indexes `0`, `1`, and `2`. Index `5` does not exist.

### 5. `ZeroDivisionError`

```python
total = 100
count = 0
average = total / count
```

**Cause:** the denominator is zero. Check that `count` is non-zero before dividing.

### 6. `NameError`

```python
customer_name = "Asha"
print(custmer_name)
```

**Cause:** `custmer_name` is a misspelling. The defined variable is `customer_name`. This is a programmer bug, not invalid user input; fix the typo rather than catching and hiding it.

**What to learn:** exception names describe different failure categories. The final traceback line tells you which category occurred.

## Exercise 2 — Write `parse_price(raw_price)`

Requirements: convert input text to a `float`, catch `ValueError`, print a clear message on failure, return the number on success, and test `"19.99"`, `"free"`, and `""`.

### Solution

```python
def parse_price(raw_price):
    try:
        price = float(raw_price)
    except ValueError:
        print(f"Invalid price '{raw_price}'. Please enter a numeric price.")
        return None
    return price


print(parse_price("19.99"))
print(parse_price("free"))
print(parse_price(""))
```

### Line-by-line explanation

1. `def parse_price(raw_price):` defines a function that receives the raw input.
2. `try:` starts a narrow exception-handling block.
3. `price = float(raw_price)` attempts to convert the text to a floating-point number.
4. `except ValueError:` handles text that cannot be converted, such as `"free"` or an empty string.
5. The `print()` explains what was invalid and what the user should enter.
6. `return None` indicates that no valid price was produced.
7. `return price` runs only when conversion succeeds.

Expected output:

```text
19.99
Invalid price 'free'. Please enter a numeric price.
None
Invalid price ''. Please enter a numeric price.
None
```

`float()` accepts `"19.99"`. It raises `ValueError` for `"free"` and `""`. This exercise checks conversion only; it does not reject negative or zero prices. Those are separate business validation rules.

## Exercise 3 — Reintroduce and then fix the oversized `try` block

The original problem is that string concatenation is inside the same `try` as multiplication. A `TypeError` caused by the formatting line is then incorrectly described as invalid price or quantity.

### Incorrect version

```python
def build_receipt_line(item_name, unit_price, quantity):
    try:
        line_total = unit_price * quantity
        summary = "Total: $" + line_total
    except TypeError:
        print("Invalid price or quantity.")
        return None
    return summary


print(build_receipt_line("Pen", 2, 3))
```

**Predict the result:** multiplication gives integer `6`. Then Python tries to add string `"Total: $"` to integer `6`, causing `TypeError`. Because both lines are inside `try`, the handler catches that error and prints:

```text
Invalid price or quantity.
None
```

That message is misleading. The supplied price and quantity were valid; the formatting code was wrong.

### Corrected version

```python
def build_receipt_line(item_name, unit_price, quantity):
    try:
        line_total = unit_price * quantity
    except TypeError:
        print("Invalid price or quantity.")
        return None

    summary = "Total: $" + str(line_total)
    return summary


print(build_receipt_line("Pen", 2, 3))
```

Output:

```text
Total: $6
```

### Explanation

- Only multiplication remains inside `try`, because that is the operation for which this handler intends to catch an input-type problem.
- `str(line_total)` converts the numeric total into text.
- String concatenation now occurs outside the `try`, so an unrelated formatting bug will not be mislabeled as invalid input.

**Lesson:** keep a `try` block as small as practical. A specific exception handler can still hide an unrelated bug if that bug happens to raise the same exception type inside the block.

## Exercise 4 — Validate a username with `raise ValueError`

Rules:

- Username must not be empty.
- Username must not contain a space.
- Username must not be longer than 20 characters.
- Decide how non-string input is handled.

We will explicitly reject non-string input with `TypeError`, because the function requires a string. For string values, rule violations raise `ValueError`.

### Solution

```python
def validate_username(username):
    if not isinstance(username, str):
        raise TypeError("Username must be text.")

    if username == "":
        raise ValueError("Username cannot be empty.")

    if " " in username:
        raise ValueError("Username cannot contain spaces.")

    if len(username) > 20:
        raise ValueError("Username cannot be longer than 20 characters.")

    return True


usernames = ["sovon", "", "data engineer", "this_username_is_too_long", 123]

for username in usernames:
    try:
        validate_username(username)
        print(f"Accepted: {username}")
    except (TypeError, ValueError) as error:
        print(f"Rejected: {username!r} -> {error}")
```

Output:

```text
Accepted: sovon
Rejected: '' -> Username cannot be empty.
Rejected: 'data engineer' -> Username cannot contain spaces.
Rejected: 'this_username_is_too_long' -> Username cannot be longer than 20 characters.
Rejected: 123 -> Username must be text.
```

### Line-by-line explanation

1. `def validate_username(username):` defines the validation function.
2. `isinstance(username, str)` checks whether the supplied value is text.
3. If not, `raise TypeError(...)` rejects the wrong data type.
4. `username == ""` detects an empty string and raises `ValueError`.
5. `" " in username` checks whether a literal space occurs anywhere in the username.
6. `len(username) > 20` rejects strings longer than 20 characters.
7. `return True` means all validation rules passed.
8. The `usernames` list contains valid and invalid examples, including a non-string value.
9. The `for` loop tests each value independently.
10. The caller's `try` contains the function call. If it succeeds, the username is accepted.
11. `except (TypeError, ValueError) as error` catches the two anticipated validation failures and prints their messages.
12. `!r` in the f-string shows a representation of the value, making an empty string visible as `''`.

The function does not strip whitespace or automatically modify a username. A username containing spaces is rejected exactly as required.

## Exercise 5 — Create `EmptyCartError` and `checkout(cart)`

Requirements: define a small custom exception, raise it when `cart` is an empty list, and catch it in the caller.

### Solution

```python
class EmptyCartError(Exception):
    pass


def checkout(cart):
    if cart == []:
        raise EmptyCartError("Cannot checkout because the cart is empty.")

    return "Checkout successful."


shopping_cart = []
try:
    result = checkout(shopping_cart)
    print(result)
except EmptyCartError as error:
    print(f"Checkout rejected: {error}")


shopping_cart = ["Notebook", "Pen"]
try:
    result = checkout(shopping_cart)
    print(result)
except EmptyCartError as error:
    print(f"Checkout rejected: {error}")
```

Output:

```text
Checkout rejected: Cannot checkout because the cart is empty.
Checkout successful.
```

### Line-by-line explanation

1. `class EmptyCartError(Exception):` creates a new exception type derived from Python's standard `Exception`.
2. `pass` means no additional class implementation is required for this lesson.
3. `def checkout(cart):` defines a function that receives the cart.
4. `if cart == []:` checks whether the cart is empty.
5. `raise EmptyCartError(...)` rejects checkout and provides a meaningful message.
6. `return "Checkout successful."` is reached only when the cart is not empty.
7. `shopping_cart = []` creates an empty cart for the first test.
8. The caller wraps only the checkout operation in `try`.
9. `except EmptyCartError as error` catches this exact domain-specific failure.
10. The second cart contains two items, so the function returns the success message.

The custom exception is useful because `EmptyCartError` describes a specific business rule. In a larger system, other parts of the program could catch this exception separately from unrelated validation errors.

This exercise assumes `cart` is a list, as specified. It does not add a type check for other possible inputs.

## Exercise 6 — Replace the vague message `"Invalid input."`

Chosen rule: quantity must be a whole number greater than zero.

### Weak message

```python
raise ValueError("Invalid input.")
```

### Improved message

```python
quantity = 0

if quantity <= 0:
    raise ValueError(
        f"Invalid quantity: {quantity}. "
        "Quantity must be a whole number greater than zero."
    )
```

### Explanation

- `quantity = 0` is the received value in this example.
- `quantity <= 0` checks the selected business rule.
- `raise ValueError(...)` rejects the invalid quantity.
- The message identifies the actual value (`0`) and states the expected rule (a whole number greater than zero).

The message is more useful than `"Invalid input."` because a developer or user can understand what failed and what value is expected.

This small example assumes the value is already an integer. A complete validator would also check its type and exclude Boolean values, as the lesson's price and age validators demonstrate.

---

# Part D — Revision sheet

| Situation | Correct tool or response |
|---|---|
| Code grammar is invalid | Fix the syntax error before running. |
| Runtime operation fails | Read the traceback from the bottom up. |
| Numeric text cannot be converted | Catch `ValueError` if this is expected input. |
| Wrong type is supplied | Validate the type or handle a specific `TypeError` where appropriate. |
| Optional dictionary key may be absent | Prefer `.get(key, default)` for a simple default. |
| Expected operation may raise a known exception | Use a narrow `try` and a specific `except`. |
| Code should run only after successful `try` | Put it in `else`. |
| Code must run when leaving the `try` statement | Put it in `finally`. |
| A function receives invalid data | Raise a clear exception instead of returning a misleading placeholder. |
| Caller should decide whether to skip or retry | Let the exception propagate to that caller. |
| A meaningful domain rule needs its own error identity | Define a minimal custom exception. |
| A message says only `"Invalid input."` | State the invalid value and the expected rule, without exposing secrets. |

## Completion checklist

- [ ] I can distinguish syntax errors from runtime exceptions.
- [ ] I can read a traceback from the bottom up.
- [ ] I can explain all six common exception types.
- [ ] I can distinguish invalid external input from a programming bug.
- [ ] I avoid bare and unnecessarily broad exception handlers.
- [ ] I validate values at the function boundary.
- [ ] I keep `try` blocks narrow.
- [ ] I understand when `else` and `finally` run.
- [ ] I can raise `ValueError` or `TypeError` with a useful message.
- [ ] I understand exception propagation.
- [ ] I can create and catch a minimal custom exception.
- [ ] I have completed all six exercises.

---

**End of lesson 07 study guide.**
