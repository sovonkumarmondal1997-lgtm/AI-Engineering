# Exceptions, Validation, and Useful Errors — Study Notes and Exercise Solutions

## Part 1 — Lesson summary and step-by-step teaching

### 1. Syntax errors, exceptions, and tracebacks

A **syntax error** is detected before a program runs, such as forgetting the colon after `if`. An **exception** happens while valid Python code is running and interrupts normal execution unless handled.

```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

print(calculate_average([]))
print("This line never runs.")
```

The empty list has length `0`, so division raises `ZeroDivisionError`; the last print is skipped. Python displays a **traceback**. Read it from the bottom up: the final line gives the exception type/message; the lines above show the calls and source locations that led to it.

### 2. Six common built-in exceptions

| Exception | Typical cause | Lesson example |
|---|---|---|
| `ValueError` | Correct general type, unacceptable value | `int("abc")` |
| `TypeError` | Wrong/incompatible type for an operation | `"5" + 3` |
| `KeyError` | Missing dictionary key | `{"a": 1}["b"]` |
| `IndexError` | List/string position does not exist | `[1, 2, 3][10]` |
| `ZeroDivisionError` | Division by zero | `10 / 0` |
| `NameError` | Name was never defined, often a typo | `print(undefined_name)` |

Some exceptions are subclasses of broader ones: `KeyError` and `IndexError` are under `LookupError`; these and `ValueError`/`TypeError` are under `Exception`, itself under `BaseException`. Therefore `except Exception:` catches many different problems.

### 3. Invalid input versus a programming bug

Invalid user input is expected (for example, letters where a number is required); validate it or catch its specific exception. A programmer bug (such as a misspelled variable) should normally be fixed, not hidden.

```python
def calculate_total(price, quantity):
    try:
        return pdice * quantity  # typo: should be price
    except:
        return 0

print(calculate_total(9.99, 3))  # 0: wrong answer, bug hidden
```

Bare `except:` hides the `NameError` and every other exception. Broad `except Exception:` has a similar problem. Prefer the specific exception you expect, and keep the `try` block narrow. A specific handler can still catch a same-type bug if unrelated code is put inside it.

### 4. Validate at the input boundary

A **boundary** is where data first enters a program/function. Check presence, type, range, emptiness, and required dictionary keys before using the data.

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

for price in [19.99, -5, "twenty", 0]:
    error = validate_price(price)
    if error is None:
        print(price, "-> valid")
    else:
        print(price, "->", error)
```

The guards check one invalid condition at a time. `None` means no error. `bool` needs a separate check because `bool` is a subclass of `int`; otherwise `True` could pass. `math.isfinite()` rejects `nan` and infinity, which ordinary `<= 0` checks do not reject.

Validation checks whether data meets rules; exception handling decides what to do when an exception occurs. They work together but are not the same thing.

### 5. `try`, `except`, and narrow handling

```python
def safe_divide(numerator, denominator):
    try:
        return numerator / denominator
    except ZeroDivisionError:
        print("Cannot divide by zero.")
        return None
```

Python attempts the `try` code. Only a `ZeroDivisionError` runs this `except`; other exceptions still surface. `None` clearly signals no numeric result, unlike `0`, which could be a genuine answer.

```python
def parse_age(raw_age):
    try:
        return int(raw_age)
    except ValueError as error:
        print(f"Could not parse age: {error}")
        return None
```

`as error` stores the exception so its message can be displayed when useful.

Keep only the risky operation inside `try`. In the lesson's first receipt example, both multiplication and string concatenation were inside the `try`; concatenating `"Total: $" + line_total` raised `TypeError` even though the price and quantity were valid, so the handler misleadingly blamed the inputs. Correct version:

```python
def build_receipt_line(item_name, unit_price, quantity):
    try:
        line_total = unit_price * quantity
    except TypeError:
        print("Invalid price or quantity.")
        return None
    summary = "Total: $" + str(line_total)
    return summary
```

Now only multiplication is guarded; unrelated errors in building the text are not mislabeled.

### 6. `else` and `finally`

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
```

`else` runs only if `try` finishes normally. `finally` runs whenever control leaves the `try` statement, including success, exception, or `return`. Use it for work that must happen regardless of outcome. If `try` exits early with `return`, `break`, or `continue`, its `else` does not run.

### 7. Raising and propagating exceptions

Use `raise` to reject invalid data at the point it is discovered:

```python
def calculate_discounted_price(price, discount_percentage):
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError(
            f"Invalid discount_percentage: {discount_percentage}. "
            "Expected a number between 0 and 100."
        )
    return price * (1 - discount_percentage / 100)
```

For `(100, 20)` the answer is `80.0`; `(100, 150)` raises a clear `ValueError`. Returning a fake value such as `0` would let incorrect data flow into totals or invoices.

The caller decides how to respond:

```python
discount_requests = [(100, 20), (50, 150)]
for price, discount_percentage in discount_requests:
    try:
        final_price = calculate_discounted_price(price, discount_percentage)
        print(f"Final price: ${final_price:.2f}")
    except ValueError as error:
        print(f"Skipping this request: {error}")
```

The valid request prints `$80.00`; the invalid one is reported and the loop continues. If a function does not catch an exception, it **propagates** up through its callers until a matching handler is found. For example, `parse_number(text)` returning `int(text)`, called by `process_value(text)`, lets `ValueError` from `"abc"` travel to an outer `try/except`.

### 8. Minimal custom exceptions

Use a custom exception only when a meaningful rule deserves its own name:

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

`pass` means the class needs no extra body. It is an `Exception` subtype. Output: `green`, then `Rejected: Cannot go from red to yellow.` Do not create a custom type for every function; `ValueError` or `TypeError` is usually sufficient. Full class design comes later.

### 9. Useful error messages

A good message identifies the invalid value (when safe), states the expected rule, does not expose secrets, helps both user and developer, and fails safely.

```python
def validate_age_bad(age):
    if age < 0 or age > 120:
        raise ValueError("Invalid input.")

def validate_age_good(age):
    if isinstance(age, bool) or not isinstance(age, int) or age < 0 or age > 120:
        raise ValueError(
            f"Invalid age: {age}. Age must be a whole number between 0 and 120."
        )
```

For `-5`, the first message is vague; the second states the value and required range.

### 10. All seven lesson examples

1. **Safe division:** `safe_divide()` catches only `ZeroDivisionError`, returns `None` on failure, and a loop processes `(10,2)`, `(7,0)`, `(9,3)` without stopping. Output: `5.0`, cannot divide by zero, `3.0`.
2. **Age parsing:** `parse_age()` uses `try/except/else/finally`; `"25"` and `"42"` parse, `"thirty"` returns `None`; `finally` prints `Checked input` for every item.
3. **Price validation:** `validate_price()` raises `TypeError` for wrong type/Boolean and `ValueError` for non-finite or non-positive values. A caller catches `(TypeError, ValueError)` and reports each rejected value.
4. **Optional dictionary key:** `order[key]` with a missing key raises `KeyError`, which can be caught; `order.get(key, "No note provided.")` is simpler when a default is enough. For `{"item":"Notebook","quantity":2}`, missing note gives the default; item gives `Notebook`.
5. **Discount range:** `calculate_discounted_price()` raises `ValueError` for percentages outside 0–100. A batch loop handles each request; only `(100,20)` succeeds, while 150 and -10 are rejected.
6. **Traffic-light state:** `InvalidTransitionError` represents illegal transitions. Starting red, requests green, red, yellow produce green, rejection of green-to-red, then yellow.
7. **Registration validation:** `validate_registration(data)` collects messages in a list for missing/blank name, missing or unparseable/out-of-range age, and a simple email check. It returns all errors rather than stopping at the first. The email check only checks for `@` not at either end; it is not full email validation. A valid Ada record is accepted; a blank name, `"abc"` age, and malformed email are all reported for the second record.

### 11. Common mistakes and key takeaways

Avoid bare/broad catches, oversized `try` blocks, putting success-only code in `try` instead of `else`, duplicating unconditional cleanup instead of using `finally`, silently returning fake values, vague messages, and unnecessary custom exception classes. Read tracebacks bottom-up; validate at boundaries; catch specific expected failures; raise when a function's input violates its contract; let genuine bugs remain visible. These habits later help validate structured model outputs, tool arguments, and API responses in AI systems.

---

## Part 2 — Project-tree-based level assessment and exercise solutions

### Your current level and the permitted scope

The supplied project tree shows that you have completed the roadmap sequence up to `03-Control-Flow-Functions-Scope-and-Errors/`, including conditionals, loops, functions, defaults/docstrings, scope/global state, pure functions/side effects, and this exceptions lesson. It also lists earlier foundations in computational thinking, variables, operators, strings, lists, tuples, dictionaries, sets, type conversion, mutability, and truthiness. These are enough for the exercises below.

The tree also lists future topics such as testing, file I/O, OOP, generators, advanced typing, and packaging. They are **not** prerequisites for these solutions and are not introduced here. The tree contains later projects with CLI, data-quality, and risk-review structures, but a folder tree alone does not prove their implementation or completion. The project-tree text is a supplied snapshot, not evidence that every listed file has been completed.

### Exercise 1 — Trigger each of the six exceptions

Run each snippet separately so one exception does not prevent the others from running.

```python
int("abc")                 # ValueError
"5" + 3                    # TypeError
{"a": 1}["b"]              # KeyError
[1, 2, 3][10]              # IndexError
10 / 0                     # ZeroDivisionError
print(undefined_name)      # NameError
```

- `int("abc")`: text cannot be converted to an integer.
- `"5" + 3`: Python cannot concatenate text and an integer.
- `{"a": 1}["b"]`: key `"b"` does not exist.
- `[1, 2, 3][10]`: index 10 is outside the list.
- `10 / 0`: denominator is zero.
- `undefined_name`: no variable with that name has been defined.

### Exercise 2 — Parse a price safely

```python
def parse_price(raw_price):
    try:
        price = float(raw_price)
    except ValueError:
        print(f"Invalid price '{raw_price}'. Enter a number such as 19.99.")
        return None
    return price

for raw_price in ["19.99", "free", ""]:
    result = parse_price(raw_price)
    print("Result:", result)
```

1. The function receives raw text.
2. `try` attempts to convert it to a floating-point number.
3. If conversion raises `ValueError`, the handler prints a useful instruction and returns `None`.
4. If conversion succeeds, execution reaches `return price`.
5. The loop tests a valid number, non-numeric text, and empty text.

Expected results: `19.99`; a clear error for `"free"` and `""`; `None` for both failed conversions. This exercise assumes the argument is text, as specified.

### Exercise 3 — Reproduce and fix an oversized `try`

**Buggy version:**

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

1. `2 * 3` succeeds and produces integer `6`.
2. `"Total: $" + 6` raises `TypeError` because text and integer cannot be concatenated.
3. The broad scope of this `try` catches that unrelated formatting error.
4. It prints the misleading message `Invalid price or quantity.` and returns `None`.

**Fixed version:**

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

Only multiplication is inside `try`. `str(line_total)` converts `6` into `"6"` so concatenation works. Output: `Total: $6`.

### Exercise 4 — Validate usernames and report rejected values

Assumption: username must be a string, non-empty, contain no spaces, and have at most 20 characters. Non-string input raises `TypeError`; rule violations raise `ValueError`.

```python
def validate_username(username):
    if not isinstance(username, str):
        raise TypeError("Username must be text.")
    if username == "":
        raise ValueError("Username cannot be empty.")
    if " " in username:
        raise ValueError("Username cannot contain spaces.")
    if len(username) > 20:
        raise ValueError("Username cannot exceed 20 characters.")
    return True

usernames = ["ada", "", "ada lovelace", "this_username_is_too_long"]

for username in usernames:
    try:
        validate_username(username)
        print(f"Accepted: {username}")
    except (TypeError, ValueError) as error:
        print(f"Rejected '{username}': {error}")
```

1. The first guard rejects non-string data with `TypeError`.
2. The next guards check empty text, spaces, and length separately.
3. Each invalid case raises a specific `ValueError` message.
4. Valid input reaches `return True`.
5. The caller catches only the two expected validation exceptions and continues to the next username.

### Exercise 5 — Custom empty-cart exception

```python
class EmptyCartError(Exception):
    pass

def checkout(cart):
    if len(cart) == 0:
        raise EmptyCartError("Cannot checkout: the cart is empty.")
    return "Checkout accepted."

carts = [[], ["notebook", "pen"]]

for cart in carts:
    try:
        result = checkout(cart)
        print(result)
    except EmptyCartError as error:
        print(f"Checkout rejected: {error}")
```

1. The class creates a named exception type for the empty-cart rule.
2. `checkout(cart)` receives a list.
3. `len(cart) == 0` checks whether it contains no items.
4. An empty list raises `EmptyCartError`; a non-empty list returns a success message.
5. The caller catches exactly `EmptyCartError`, reports it, and continues.

Expected: first an empty-cart rejection, then `Checkout accepted.`

### Exercise 6 — Replace a vague validation message

Rule chosen: quantity must be a positive whole number.

```python
def validate_quantity(quantity):
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError(
            f"Invalid quantity: {quantity}. "
            "Quantity must be a whole number greater than zero."
        )

try:
    validate_quantity(0)
except ValueError as error:
    print(error)
```

1. The condition rejects Booleans, non-integers, and zero/negative integers.
2. `raise ValueError(...)` stops invalid quantity from being accepted.
3. The message names the received value and explains the expected rule.
4. The caller catches the expected error and prints its message.

Expected: `Invalid quantity: 0. Quantity must be a whole number greater than zero.`

### Completion checklist

Before moving on, make sure you can explain: syntax error versus exception; traceback reading; the six built-in exception types; invalid input versus a code bug; boundary validation; narrow `try`; `except`, `else`, and `finally`; `raise` and propagation; custom exception purpose; and clear error messages. These are the exact skills this lesson expects.
