# Exceptions, Validation, and Useful Errors

## Why exceptions and validation matter

Real programs receive real, messy input: a user types letters where a
number was expected, a dictionary is missing a key you assumed would be
there, a list turns out to be empty. Something in your program has to
decide what happens next — crash with a confusing message, silently
produce a wrong answer, or fail clearly and helpfully. This lesson is
about making that choice on purpose. You will learn to recognize
Python's built-in error types, validate data before you rely on it,
catch only the specific problems you actually expect, and write error
messages that tell a person exactly what went wrong and how to fix it.
Handled well, an error is not a failure of your program — it is your
program behaving exactly as designed when it meets something it was
never supposed to accept in the first place.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain the difference between a syntax error and a runtime
  **exception**, and read a **traceback** to find the real cause of a
  problem.
- Recognize `ValueError`, `TypeError`, `KeyError`, `IndexError`,
  `ZeroDivisionError`, and `NameError`, and explain what usually causes
  each one.
- Explain the difference between expected invalid input and a genuine
  programmer bug, and explain why bare `except:` and broad `except
  Exception:` are poor beginner habits.
- Validate data at the boundary of a program, before the main work
  begins, and write error messages that explain what went wrong and how
  to fix it.
- Write a `try`/`except` block that catches a specific exception, and
  explain what code should stay outside the `try` block.
- Use `else` and `finally` correctly, and explain exactly when each one
  runs.
- Use `raise` to reject invalid input from inside a function, and
  explain why silently returning an incorrect value instead is
  dangerous.
- Write one small, minimal custom exception, and explain when a custom
  exception is worth creating.
- List the qualities of a genuinely useful error message.

## Prerequisites

- [Conditionals, Guards, and Boolean Logic](01-conditionals-guards-and-boolean-logic.md) —
  validation in this lesson relies heavily on the guard-style `if`/`elif`
  chains taught there.
- [Functions, Parameters, and Return Values](03-functions-parameters-and-return-values.md) —
  this lesson assumes functions, parameters, and `return` are already
  comfortable.
- [Pure Functions and Side Effects](06-pure-functions-and-side-effects.md) —
  raising a clear exception, instead of silently returning a wrong
  value, is a direct extension of that lesson's "predictable return
  values" idea.
- [Type Conversion and Truthiness](../02-Python-Core-Language-and-Data-Types/09-type-conversion-and-truthiness.md) —
  the short `try`/`except ValueError` preview shown there is formalized
  fully in this lesson.
- [Dictionaries and Lookups](../02-Python-Core-Language-and-Data-Types/07-dictionaries-and-lookups.md) —
  `KeyError` and `.get()` are both reused directly here.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Syntax error** | An error Python finds while reading your code, before any of it runs, because the code does not follow Python's grammar. |
| **Exception** | An error that happens while a program is running, interrupting its normal, top-to-bottom flow. |
| **Traceback** | The report Python prints when an exception is not handled, showing the sequence of calls that led to the error and, at the end, the error itself. |
| **Raise** | To cause an exception to happen on purpose, using the `raise` statement. |
| **`try` block** | A block of code Python attempts to run, watching for a specific kind of exception. |
| **`except` block** | A block that runs only if the matching exception happened inside the `try` block. |
| **`else` block** (in a `try` statement) | A block that runs only if the `try` block completed normally, with no exception. |
| **`finally` block** | A block that runs when control leaves the `try` statement, whether it finished normally, an exception happened, or it exited with something like `return`. |
| **Validation** | Checking that data meets the rules a program needs, before using that data for real work. |
| **Boundary** | The point where data first enters a program or a function, and where it should be validated. |
| **Custom exception** | A new exception type you define yourself, for a specific rule in your own program. |

## Step-by-step explanation

### 1. Errors and exceptions

A **syntax error** is a mistake in your code's grammar, found by Python
*before* any of the program runs — you already met this in
[Python Files, the Interpreter, the REPL, and Indentation](../02-Python-Core-Language-and-Data-Types/01-python-files-interpreter-repl-and-indentation.md),
for example forgetting the colon after an `if`. An **exception** is
different: it is an error that happens *while* the program is actually
running, because of the specific data or situation it encounters at that
moment — code that is perfectly valid Python can still raise an
exception if, say, it tries to divide by a number that turns out to be
zero.

**An exception interrupts a program's normal flow.** Unless something
catches it, an exception stops the program immediately, skipping every
line that would otherwise have run next:

```text
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

print(calculate_average([]))
print("This line never runs.")
```

Saved as `average.py` and run, this produces a **traceback** and stops —
`"This line never runs."` genuinely never prints:

```text
Traceback (most recent call last):
  File "average.py", line 4, in <module>
    print(calculate_average([]))
          ~~~~~~~~~~~~~~~~~^^^^
  File "average.py", line 2, in calculate_average
    return sum(numbers) / len(numbers)
           ~~~~~~~~~~~~~^~~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

**A traceback is evidence, and should be read before searching
online.** Read it from the **bottom up**:

- The **last line**, `ZeroDivisionError: division by zero`, names the
  exception type and its message — start here.
- Each `File "...", line N, in ...` entry above it shows one step in the
  chain of calls that led to the failure, with the **most recent call
  last** — here, the program called `calculate_average([])` from line 4,
  which then failed on line 2, inside `calculate_average` itself.
- The line of source code shown under each entry, sometimes with `^` or
  `~` marks underneath (on modern Python versions), points at exactly
  which part of that line was being evaluated when things went wrong.

A traceback almost always tells you the exact file, line, and reason for
a failure — reading it carefully first, before guessing or searching
online, is one of the most valuable habits you can build as a
programmer.

### 2. Common standard exceptions

Python provides many built-in exception types, each describing a
specific kind of problem. Six come up constantly:

**`ValueError`** — the right *type* of value, but an invalid one for
what you are trying to do:

```text
int("abc")
```

```text
ValueError: invalid literal for int() with base 10: 'abc'
```

**`TypeError`** — an operation or function was given a value of an
inappropriate type, or the operation is not supported for that type:

```text
"5" + 3
```

```text
TypeError: can only concatenate str (not "int") to str
```

**`KeyError`** — looking up a dictionary key that does not exist:

```text
{"a": 1}["b"]
```

```text
KeyError: 'b'
```

**`IndexError`** — looking up a list (or string) position that does not
exist:

```text
[1, 2, 3][10]
```

```text
IndexError: list index out of range
```

**`ZeroDivisionError`** — dividing a number by zero:

```text
10 / 0
```

```text
ZeroDivisionError: division by zero
```

**`NameError`** — using a name Python has never seen defined, often a
typo:

```text
print(undefined_name)
```

```text
NameError: name 'undefined_name' is not defined
```

Recognizing these six by name, and knowing roughly what causes each one,
lets you understand a traceback's final line at a glance, before reading
anything else.

These exception types form an **inheritance hierarchy**: some are more
specific kinds of broader ones. A small part of it looks like this:

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

`KeyError` and `IndexError` are more specific subclasses of
`LookupError`, and `Exception` is much broader than any of them. This is
why `except Exception:` catches so many different exception types at
once, including ones you never intended to handle.

### 3. Expected invalid input versus programmer bugs

Not every exception deserves the same response. It helps to sort them
into two very different categories:

- **Expected invalid input** — a user typing letters where a number was
  wanted, a required field left blank, a percentage outside `0`–`100`.
  This is completely normal, and your program should handle it
  deliberately, usually with validation (Section 4) or a targeted
  `try`/`except` (Section 5).
- **A bug in your own code** — a typo in a variable name, calling a
  function with the arguments in the wrong order, forgetting a needed
  step. This should usually be **fixed**, not caught and hidden.

**This is exactly why bare `except:` and broad `except Exception:` are
poor beginner habits — they catch *both* categories at once, with no way
to tell them apart:**

```python
def calculate_total(price, quantity):
    try:
        return pdice * quantity
    except:
        return 0

print(calculate_total(9.99, 3))
```

```text
0
```

This function has a genuine bug: `pdice` is a typo for `price`, which
should raise `NameError` and stop the program, loudly announcing exactly
what is wrong. Instead, the bare `except:` silently swallows **every**
possible exception — including this real bug — and returns `0`, a
plausible-looking but completely wrong answer. Nobody would ever notice
this bug from the output alone; it would need to be found by luck or by
painstaking testing. **Prefer catching a specific, expected exception type**
(`except ValueError:`, `except KeyError:`) over a bare `except:` or
`except Exception:`. A specific `except` is clearer and safer, because it
catches only that exception type and lets other kinds of bug surface
immediately. It is not a guarantee, though: an unrelated bug can still
raise the same exception type, which is why the `try` block should also
stay narrow (Section 5).

### 4. Input validation

**Validation** and **exception handling** are related but not identical.
Validation checks whether data satisfies the rules a program requires,
which can stop invalid data before it reaches later logic. Exception
handling decides how the program responds when an exception is actually
raised. They often work together, but one does not replace the other.

**Validation** means checking that data meets the rules your program
needs, at the **boundary** — the point where the data first arrives —
before you do any real work with it. A validation check typically
confirms: the value is actually **present**, it has the right **type**,
it falls within an allowed **range**, it is not unexpectedly **empty**,
and any **required keys** actually exist.

```python
def validate_price(price):
    if not isinstance(price, (int, float)):
        return "Price must be a number."
    if isinstance(price, bool):
        return "Price must be a number."
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

```text
19.99 -> valid
-5 -> Price must be greater than zero.
twenty -> Price must be a number.
0 -> Price must be greater than zero.
```

This reuses the guard-style `if` chain from
[Conditionals, Guards, and Boolean Logic](01-conditionals-guards-and-boolean-logic.md):
each check handles one specific way the input could be invalid, and
`None` means "no problem found." (`isinstance(price, bool)` is checked
separately because, in Python, `bool` is technically a kind of `int` —
without this check, `True` would incorrectly pass as a valid price.)
Every message states **what** was wrong and, where possible, **what was
expected instead** — never just "invalid input."

### 5. `try` and `except`

A **`try` block** tells Python "attempt this code, and watch for a
specific kind of exception." If that exception happens, the matching
**`except` block** runs instead of letting the program crash:

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

```text
5.0
Cannot divide by zero.
None
```

`except ZeroDivisionError:` catches **only** that specific exception —
this is deliberate, following Section 3's rule: catch exactly the
exception you expect, nothing broader.

**Store the exception as a name — commonly `error` — only when its
message is genuinely useful to show:**

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

```text
25
Could not parse age: invalid literal for int() with base 10: 'twenty'
None
```

`except ValueError as error:` captures the exception object itself in
`error`; printing it shows its message directly, exactly as it would
have appeared in a traceback — useful here, since `int()`'s own message
already clearly names the invalid text.

**What should stay outside the `try` block:** keep the `try` block as
narrow as practical around the operation(s) whose expected exception you
intend to handle. Unrelated code inside `try` means an unrelated bug of
the same exception type can be caught by accident, and a narrow `try`
makes the handler's intent clear:

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

```text
Invalid price or quantity.
None
```

`unit_price` and `quantity` here are perfectly valid numbers — the real
bug is `"Total: $" + line_total`, which forgot to convert `line_total` to
text with `str(...)` first, and genuinely raises `TypeError` for a
completely different reason. Because that buggy line was placed inside
the same `try` block, it gets caught by `except TypeError:` and
misreported as "Invalid price or quantity" — a real bug, now hidden
behind a misleading message. Moving only the truly risky line inside
`try` avoids this entirely:

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

```text
Total: $6
```

Now only the line that can actually fail for the reason you are
expecting sits inside `try` — any other bug in the rest of the function
will surface immediately and honestly, instead of being absorbed by an
unrelated `except`.

### 6. `else` and `finally`

A `try` statement can add two more optional blocks. **`else` runs only
if the `try` block completes normally, without an exception** (if the
`try` block exits early with `return`, `break`, or `continue`, `else`
does not run). **`finally` runs whenever control leaves the `try`
statement** — after normal completion, after an exception, or when
leaving by something like `return` — so it is the right place for a step
that should happen regardless of the outcome:

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

```text
Parsed age: 25
Finished checking one value.
'twenty' is not a valid whole number.
Finished checking one value.
```

For `"25"`, the `try` block succeeds, so `else` runs and reports the
parsed age; for `"twenty"`, the `try` block fails, so `except` runs
instead, and `else` is skipped entirely. **`finally` runs in both
cases**, printing its message either way — this is its defining feature:
code you want to run no matter what happened belongs in `finally`, not
duplicated in both `try` and `except`.

### 7. Raising exceptions

**`raise`** deliberately causes an exception, on purpose, from inside
your own code — most often used inside a function to reject invalid
input immediately, rather than letting bad data quietly continue:

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

```text
80.0
```

Calling this function with an invalid percentage stops the program
immediately, with a clear message naming exactly what was wrong:

```text
print(calculate_discounted_price(100, 150))
```

```text
ValueError: Invalid discount_percentage: 150. Expected a number between 0 and 100.
```

**Why returning an incorrect value silently is dangerous:** imagine
`calculate_discounted_price` instead returned `0`, or the original
`price` unchanged, whenever the percentage was invalid. That wrong number
would flow silently into every later calculation — a total, a report, an
invoice — with no error, no warning, and no way to trace it back to its
real cause. Raising a clear exception the moment invalid data is
discovered stops the problem exactly where it started.

**A caller can, and usually should, handle a raised exception
appropriately**, rather than letting it crash the whole program:

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

```text
Final price: $80.00
Skipping this request: Invalid discount_percentage: 150. Expected a number between 0 and 100.
```

The function's job is only to refuse invalid input clearly; the caller
decides what to actually do about it — here, skip that one request and
continue processing the rest, instead of stopping entirely.

An exception also does not have to be handled in the function where it
happens. If no handler exists there, it **propagates** up to the caller:

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

```text
The caller handled the invalid input.
```

```text
process_value()
    ↓
parse_number()
    ↓
ValueError
    ↓
no handler here
    ↓
exception propagates to caller
    ↓
caller handles it
```

`int("abc")` raises `ValueError` inside `parse_number`; neither function
catches it, so it passes back up through each caller until the `try`
at the top handles it.

### 8. Small custom exceptions

Sometimes the built-in exception types (`ValueError`, `TypeError`, and
so on) do not clearly capture *what kind* of rule was actually broken. A
**custom exception** — a new exception type you define yourself — is
worth creating only when it makes a specific rule in your own program
clearer to anyone reading the code that raises or catches it.

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

```text
green
Rejected: Cannot go from red to yellow.
```

`class InvalidTransitionError(Exception): pass` is the **minimal**
syntax needed to create a genuinely new exception type: it says "this is
a new kind of thing, and it counts as an `Exception`," with `pass`
meaning "nothing extra needs adding — the name itself is the whole
point." Catching `except InvalidTransitionError:` is far clearer to a
reader than catching a generic `except ValueError:` would have been,
because the name states the exact domain rule being enforced: an invalid
state transition, specifically — not just "some value was wrong somehow."

**Do not overuse this.** Full class design — attributes, custom
behavior, and everything else a class can do — is covered properly in a
later module; this lesson uses only the smallest possible pattern needed
to name a new exception. Most of the time, a plain `ValueError` or
`TypeError` with a clear message is already good enough — reach for a
custom exception only when a specific rule in your program genuinely
deserves its own name.

### 9. Designing useful errors

A genuinely useful error message does five things:

- **States what input was invalid.** Name the actual value, when it is
  safe to show.
- **States the expected format, range, or rule.** Do not just say
  something is wrong — say what "right" would have looked like.
- **Avoids exposing secrets or sensitive values.** A validation error
  about a password, for example, should never echo the password itself
  back in the message.
- **Is helpful to both users and developers.** A message read by a
  person using the program should make sense to them; the exception
  type and any extra detail should also help a developer diagnose the
  problem later.
- **Fails safely.** Raising a clear exception the moment something
  invalid is found — rather than continuing with bad data — is itself
  part of good error design, tying directly back to Section 7.

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

```text
Bad message: Invalid input.
Good message: Invalid age: -5. Age must be a whole number between 0 and 120.
```

`"Invalid input."` tells nobody anything useful — not what was invalid,
not what was expected, not how to fix it. The second message states the
actual value received and the exact rule it broke, in one short
sentence. Validation, clear errors, and safe failure work together: good
validation finds the problem early; a good error message explains it
clearly; failing loudly (rather than continuing with bad data) keeps the
rest of the program trustworthy.

## Examples

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

**Plain-English explanation:**

- `safe_divide` catches exactly one, specific, **expected** exception —
  a denominator of zero is a completely normal thing to happen when
  processing a batch of real number pairs, not a bug.
- The `for` loop tries three pairs; the middle one deliberately divides
  by zero, letting you see the safe function handle exactly that case
  without stopping the rest of the loop.
- Returning `None` on failure (rather than `0`, which could be confused
  with a real result) and checking `is None` afterward reuses the exact
  truthiness lesson from
  [Type Conversion and Truthiness](../02-Python-Core-Language-and-Data-Types/09-type-conversion-and-truthiness.md).

**Expected output:**

```text
10 / 2 -> 5.0
7 / 0 -> cannot divide by zero
9 / 3 -> 3.0
```

### Example 2 — Parsing an age with `try`/`except`/`else`/`finally`

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

**Plain-English explanation:**

- `"thirty"` is **expected invalid input** — exactly the kind of thing a
  real user might type, and precisely why this function validates by
  catching `ValueError` rather than assuming the text will always be
  numeric.
- `else: return age` runs only when `int(raw_age)` succeeded with no
  exception — returning from inside `else` is intentional here, keeping
  the "happy path" clearly separate from the failure path in `except`.
- `finally: print(...)` runs after **every** attempt, successful or not,
  confirming that this step (logging which input was checked) can never
  accidentally be skipped, however the `try` block turns out.

**Expected output:**

```text
Checked input: '25'
Result: 25
'thirty' is not a valid age. Please enter a whole number.
Checked input: 'thirty'
Result: None
Checked input: '42'
Result: 42
```

### Example 3 — Validating a price by raising specific exceptions

```python
def validate_price(price):
    if not isinstance(price, (int, float)) or isinstance(price, bool):
        raise TypeError(f"Invalid price: {price!r}. Expected a number.")
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

**Plain-English explanation:**

- `validate_price` **raises** two different, specific exception types
  for two genuinely different problems: the wrong *type* of value raises
  `TypeError`, while a validly-typed but out-of-range value raises
  `ValueError` — each name accurately describes the actual problem.
- `except (TypeError, ValueError) as error:` lists both expected
  exception types together in a tuple, catching either one — this is
  still precise and intentional, unlike a bare `except:`, because both
  types were specifically anticipated by this validation function.
- Every rejected price is **expected invalid input** from a realistic
  batch of user-submitted prices, not a bug — exactly the situation
  validation and specific exception handling are meant for.

**Expected output:**

```text
19.99 -> valid
-5 -> rejected: Invalid price: -5. Price must be greater than zero.
twenty -> rejected: Invalid price: 'twenty'. Expected a number.
```

### Example 4 — Looking up an optional dictionary value

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

**Plain-English explanation:**

- `get_shipping_note_direct` shows that `KeyError` is a completely
  **expected**, normal thing to happen when a key is genuinely optional
  — catching it here is the right tool.
- `get_shipping_note_safe` reaches the identical result using `.get(key,
  default)` from
  [Dictionaries and Lookups](../02-Python-Core-Language-and-Data-Types/07-dictionaries-and-lookups.md)
  — for this simple "missing key means use a default" case, `.get()` is
  usually clearer than writing a `try`/`except KeyError` block at all.
- `try`/`except KeyError` remains the better choice over `.get()` once
  handling a missing key needs more than one simple substitute value —
  for example, several statements, or a different action entirely.

**Expected output:**

```text
No note provided.
No note provided.
Notebook
```

### Example 5 — Validating a discount percentage range

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

**Plain-English explanation:**

- `calculate_discounted_price` **raises** `ValueError` the moment an
  out-of-range percentage is discovered, rather than silently clamping
  it or returning an unchanged price — exactly Section 7's warning
  against returning an incorrect value silently.
- Both invalid requests here (`150` and `-10`) are **expected invalid
  input** — real percentages submitted from somewhere else in a program
  can easily be out of range, and this function's whole job is to catch
  that before any money is actually calculated.
- The `for` loop's `try`/`except` lets processing continue for every
  request in the batch, reporting each invalid one individually, instead
  of one bad request crashing the entire batch.

**Expected output:**

```text
Final price: $80.00
Skipping this request: Invalid discount_percentage: 150. Expected a number between 0 and 100.
Skipping this request: Invalid discount_percentage: -10. Expected a number between 0 and 100.
```

### Example 6 — A traffic-light transition with a custom exception

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

**Plain-English explanation:**

- `InvalidTransitionError` is a **minimal custom exception**, worth
  defining here because "an invalid state transition" is a specific,
  meaningful domain rule for a traffic light — clearer than reusing a
  generic `ValueError` for it.
- The light starts `"red"`. Requesting `"green"` is a legal transition
  and succeeds; requesting `"red"` again right after (while the light is
  now `"green"`) is **not** legal, and is correctly rejected without
  changing `current_color`; requesting `"yellow"` next succeeds, since
  `green -> yellow` is allowed.
- An invalid requested transition here represents **expected invalid
  input** — some other part of a program might mistakenly request an
  illegal transition, and this function's entire purpose is to refuse it
  clearly, by name, rather than silently accepting it.

**Expected output:**

```text
Light is now green.
Rejected: Cannot go from green to red.
Light is now yellow.
```

### Example 7 — A registration validator that reports every error

```python
def validate_registration(data):
    errors = []

    if "name" not in data or data["name"] == "":
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

    if "email" not in data or "@" not in data.get("email", ""):
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

**Plain-English explanation:**

- `validate_registration` combines every idea from this lesson: it
  checks for **missing keys** (`"name" not in data`), an **empty
  value**, an **invalid type/format** (caught with `try`/`except
  ValueError` around `int(...)`), and an **out-of-range value** — all at
  the boundary, before any registration is actually accepted.
- The example assumes `data` is a dictionary, `data["age"]` is a value
  that `int(...)` can try to convert (such as text like `"30"`), and
  `data["email"]` is a string.
- Rather than raising on the first problem found, it **collects every
  error into a list** and keeps checking the remaining fields — this
  reports all of a submission's problems in one pass, instead of forcing
  a user to fix one mistake at a time, resubmitting repeatedly to
  discover the next one.
- The second submission fails all three checks at once (blank name,
  unparseable age, invalid-looking email); every message states plainly
  what was wrong, following Section 9's rules for a genuinely useful
  error.

**Expected output:**

```text
Registration accepted.
Registration rejected:
 - Name is required.
 - Age must be a whole number, got 'abc'.
 - A valid email address is required.
```

## Common beginner mistakes

- **Catching a bare `except:` or a broad `except Exception:`** instead
  of a specific exception type, hiding genuine bugs (like the `pdice`
  typo in Section 3) behind a plausible-looking but wrong result.
- **Putting more code than necessary inside a `try` block**, so an
  unrelated bug elsewhere in that block gets caught and misreported by
  an `except` meant for something completely different.
- **Confusing `else` with just putting more code inside `try`.** Code
  that should only run after a *guaranteed success* belongs in `else`,
  not appended to the end of `try`, where it would itself be watched for
  the same exception.
- **Forgetting that `finally` runs whenever control leaves the `try`
  statement**, and duplicating the same
  cleanup or logging step in both `try` and `except` instead of writing
  it once in `finally`.
- **Returning a silent, incorrect placeholder value** (like `0`, `-1`,
  or `None`) from a function that received invalid input, instead of
  `raise`-ing a clear exception the caller can actually detect and
  react to.
- **Writing a vague error message** such as `"Invalid input."` instead
  of stating what was invalid and what was expected, as Section 9
  demonstrated directly.
- **Creating a custom exception for every function**, instead of
  reserving one for a genuinely meaningful domain rule — most invalid
  input is already well described by a plain `ValueError` or `TypeError`
  with a clear message.

## Try it yourself

Do not look up full solutions. Predict the output before running each
one.

1. Write a function that intentionally causes each of the six standard
   exceptions from Section 2, one at a time (running each on its own),
   and write down, in your own words, what caused each one.
2. Write `parse_price(raw_price)` that converts text to a `float` using
   `try`/`except ValueError`, prints a clear message on failure, and
   returns the parsed number on success. Test it with `"19.99"`,
   `"free"`, and `""`.
3. Take the `build_receipt_line` "too much in `try`" example from
   Section 5, deliberately reintroduce the bug, and predict — before
   running it — what misleading message it will print. Then fix it by
   moving the unrelated line outside `try`.
4. Write a function `validate_username(username)` that raises `ValueError`
   with a clear message if the username is empty, contains a space, or
   is longer than 20 characters. Assume `username` is a string (or decide
   how non-string input should be handled). Write a caller that tries several
   usernames and reports which ones were rejected and why.
5. Write one small custom exception, `EmptyCartError`, and a function
   `checkout(cart)` that raises it if `cart` is an empty list. Handle it
   in a caller with a specific `except EmptyCartError:` block.
6. Take the bad error message `"Invalid input."` from Section 9 and
   rewrite it for a validation rule of your own choosing, making sure it
   states what was invalid and what was expected instead.

## Summary

- A **syntax error** is found before a program runs; an **exception**
  happens while it runs, and interrupts the program's normal flow
  unless something catches it. A **traceback** is evidence: read it
  bottom-up, starting with the exception type and message.
- `ValueError`, `TypeError`, `KeyError`, `IndexError`,
  `ZeroDivisionError`, and `NameError` each describe a specific, common
  kind of problem.
- **Expected invalid input** should be handled deliberately; a
  **programmer bug** should usually be fixed, not hidden — this is why
  bare `except:` and broad `except Exception:` are poor habits.
- **Validation** checks data at the boundary — presence, type, range,
  emptiness, required keys — before the main work begins, with error
  messages that explain what went wrong and how to fix it.
- `try` attempts risky code; `except` catches a **specific**, expected
  exception; keep the `try` block as narrow as practical around the
  risky operation.
- `else` runs only when `try` completes normally; `finally` runs
  whenever control leaves the `try` statement, success or failure.
- `raise` rejects invalid input immediately and clearly; silently
  returning a wrong value instead lets bad data spread unnoticed.
- A **custom exception**, using the minimal `class Name(Exception):
  pass` pattern, is worth creating only when it names a genuinely
  meaningful rule in your own program — not for every function.
- A useful error states what was invalid, what was expected, avoids
  exposing sensitive values, and helps both users and developers.

## Completion checklist

- [ ] I can explain the difference between a syntax error and a runtime
      exception, and read a traceback from the bottom up.
- [ ] I can recognize `ValueError`, `TypeError`, `KeyError`,
      `IndexError`, `ZeroDivisionError`, and `NameError`, and explain a
      common cause of each.
- [ ] I can explain the difference between expected invalid input and a
      programmer bug, and why bare `except:`/`except Exception:` are
      poor habits.
- [ ] I can validate data at a function's boundary and write a clear,
      specific error message for invalid data.
- [ ] I can write a `try`/`except` block that catches a specific
      exception, and explain what should stay outside the `try` block.
- [ ] I can use `else` and `finally` correctly and explain when each one
      runs.
- [ ] I can use `raise` to reject invalid input from a function, and
      explain why silently returning a wrong value is dangerous.
- [ ] I can write one minimal custom exception and explain when it is
      actually worth creating.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

Validating input and raising clear, specific exceptions is exactly how
you will later handle a model's structured output, a tool's arguments,
or an API response that does not match what your code expected — none of
which can ever be fully trusted just because it "looks" correct.
Deciding whether a failure is expected (a model returned an empty
result, a tool call timed out) or a genuine bug in your own code is a
judgment call an agent's error-handling logic has to make constantly,
and it is exactly the distinction from Section 3. A raised exception with
a clear, specific message is also often the very thing an agent needs to
decide what to do next — retry, ask for clarification, or give up safely
— which is only possible if the failure was reported honestly in the
first place, rather than hidden behind a broad `except Exception:` or a
silently wrong return value.
