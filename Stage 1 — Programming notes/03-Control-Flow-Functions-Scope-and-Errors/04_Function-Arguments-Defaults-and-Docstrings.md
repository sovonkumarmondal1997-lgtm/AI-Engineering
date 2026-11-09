# Stage 1 — Function Arguments, Defaults, and Docstrings
## Study Notes and Exercise Solutions

This guide follows the uploaded lesson `04-function-arguments-defaults-and-docstrings.md`. It stays within the Python concepts covered in that lesson.

---

# Part 1 — Lesson summary and step-by-step teaching

## 1. A function signature is a contract

A function signature is its name and parameter list. It tells the caller what information to provide and which values are optional. Clear names make the function easier to use without reading its internal code.

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

print(format_price(19.99))
```

`amount` is required; `currency` is optional because it has a default. The output is `$19.99`. The `:.2f` formats the number to two decimal places.

## 2. Required parameters

A parameter without a default is required.

```python
def greet_by_username(username):
    return f"Welcome, {username}!"

print(greet_by_username("ada99"))
```

Output: `Welcome, ada99!`

A function can have multiple required parameters:

```python
def calculate_total(price, quantity):
    return price * quantity

print(calculate_total(9.99, 3))
```

Output: `29.97`

Both `price` and `quantity` must be supplied. If one is missing, Python raises `TypeError`:

```python
calculate_total(9.99)
# TypeError: missing 1 required positional argument: 'quantity'

calculate_total()
# TypeError: missing 2 required positional arguments: 'price' and 'quantity'
```

Read the error as Python telling you which part of the function contract was not satisfied.

## 3. Positional arguments

Python matches positional arguments to parameters by order.

```python
def schedule_meeting(start_time, end_time):
    return f"Meeting from {start_time} to {end_time}"

print(schedule_meeting("1:00 PM", "3:00 PM"))
print(schedule_meeting("3:00 PM", "1:00 PM"))
```

The first call is sensible; the second produces `Meeting from 3:00 PM to 1:00 PM`. It does not crash because both values are strings and both positions were filled. Python cannot know that the caller swapped their intended meanings. This is a silent logic bug.

## 4. Keyword arguments

A keyword argument identifies its parameter by name:

```python
def calculate_total(price, quantity):
    return price * quantity

print(calculate_total(price=9.99, quantity=3))
print(calculate_total(quantity=3, price=9.99))
print(calculate_total(9.99, quantity=3))
```

All three calls return `29.97`. Naming arguments makes calls easier to understand and removes order ambiguity for those named arguments.

You may mix positional and keyword arguments, but ordinary positional arguments must come first:

```python
calculate_total(quantity=3, 9.99)
# SyntaxError: positional argument follows keyword argument
```

## 5. Default arguments

A default lets the caller omit an optional argument. The caller can override it.

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

print(format_price(19.99))                 # $19.99
print(format_price(19.99, "€"))            # €19.99
print(format_price(19.99, currency="£"))   # £19.99
```

The default is used only when the caller does not supply `currency`. Immutable defaults such as strings, numbers, booleans, and `None` are safe choices.

## 6. The mutable default argument trap

Python evaluates a default argument once, when it creates the function—not afresh on every call.

```python
def add_task(task, tasks=[]):
    tasks.append(task)
    return tasks

print(add_task("Write report"))
print(add_task("Buy groceries"))
```

Outputs:
```text
['Write report']
['Write report', 'Buy groceries']
```

Both calls reuse and mutate the same list. This is shared state (aliasing), not a new list per call.

Use `None` as the default and create a list inside the function when needed:

```python
def add_task(task, tasks=None):
    if tasks is None:
        tasks = []
    tasks.append(task)
    return tasks

print(add_task("Write report"))
print(add_task("Buy groceries"))
```

Outputs:
```text
['Write report']
['Buy groceries']
```

The `tasks = []` line runs separately on each call that omits `tasks`. The same principle applies to mutable defaults such as `{}` and `set()`.

## 7. Keyword-only parameters

A standalone `*` in the parameter list makes every parameter after it keyword-only.

```python
def calculate_total(price, quantity, *, include_tax=False):
    subtotal = price * quantity
    if include_tax:
        return subtotal * 1.08
    return subtotal

print(calculate_total(10, 2))                       # 20
print(calculate_total(10, 2, include_tax=True))     # 21.6
```

`price` and `quantity` may be positional or keyword arguments. `include_tax` must be named. Calling `calculate_total(10, 2, True)` raises `TypeError` because the function accepts only two positional arguments. Requiring the name makes the option's purpose obvious.

## 8. Docstrings and `help()`

A docstring is the string placed first inside a function. It should explain the function's purpose, parameters, return value, and important assumptions.

```python
def format_price(amount, currency="$"):
    """
    Format a number as a price string.

    amount is the numeric price to display.
    currency is the symbol before the amount; it defaults to "$".
    Returns a string such as "$19.99".
    """
    return f"{currency}{amount:.2f}"

help(format_price)
```

`help()` displays the signature, including the default, and the docstring. A useful docstring helps someone use the function without inspecting its body.

## 9. Design a clear function contract

A well-designed function has:
1. A clear action-oriented function name and meaningful parameter names.
2. Parameter meanings that are understandable from the signature.
3. Sensible defaults, preferably immutable.
4. Predictable return values (for example, consistently returning a number or string).
5. Clear errors when a call is invalid.

Compare unclear `calc(a, b, c=1)` with `calculate_total(price, quantity, *, include_tax=False)`. The second explains the inputs and makes the optional tax choice explicit. A clear signature does not automatically validate input types; the lesson points to a later validation lesson for that.

## 10. All six lesson examples

- **`format_price`**: required `amount`, default currency, and keyword override. `format_price(42.5)` gives `$42.50`; `format_price(42.5, currency="€")` gives `€42.50`.
- **`create_greeting`**: loops through `["Ada", "Grace", "Alan"]` using the default `"Hello"`; a final keyword override gives Marie `"Welcome back"`.
- **`calculate_total`**: computes `price * quantity`; the keyword-only `include_tax=True` applies 8%. For 12.50 × 4, outputs are `$50.00` and `$54.00`.
- **`add_task`**: `None` creates a fresh list when omitted; passing Monday's list back in intentionally adds another task to it. Tuesday gets an independent list.
- **`schedule_meeting`**: three required positional parameters; swapping same-type strings can create a nonsensical sentence without an error. Omitting `topic` raises `TypeError`.
- **`build_invoice_line`**: combines required `item_name`, `unit_price`, `quantity`, keyword-only `currency="$"` and `tax_included=False`, a docstring, and a predictable string result. Outputs: `Notebook x4: $14.00`, `Notebook x4: $15.12`, and `Notebook x4: €15.12`.

## 11. Common mistakes to avoid

- Vague names such as `a` and `b`.
- Assuming Python detects swapped same-type positional arguments.
- Putting a positional argument after a keyword argument (`SyntaxError`).
- Using `[]`, `{}`, or `set()` as a default when each call should get fresh state; use `None`.
- Passing a keyword-only option positionally (`TypeError`).
- Writing a docstring that does not explain inputs and output.
- Assuming a signature checks input types; it does not.

---

# Part 2 — Current-level assessment and all exercise solutions

## Your current learning level

From the Stage 1 roadmap context available from our earlier work, you have studied computational thinking and Python fundamentals, including loops and the preceding functions/parameters/return-values lesson. The earlier project-tree review also identified some Stage 1 overview and project files as incomplete or stubs. I do **not** have a newly attached, complete project-tree snapshot in this turn, so I cannot claim to have freshly audited every folder or project.

For this lesson, the appropriate level is **beginner progressing toward confident intermediate Python**: use `def`, parameters, `return`, loops, lists, conditionals, and `None`; focus now on designing and calling functions safely. The solutions below do not introduce later validation, exception-handling, classes, or advanced Python topics.

## Exercise 1 — Temperature conversion with a default

```python
def convert_temperature(celsius, to_unit="fahrenheit"):
    if to_unit == "fahrenheit":
        return (celsius * 9 / 5) + 32
    return celsius

print(convert_temperature(0))
print(convert_temperature(0, to_unit="celsius"))
```

- `def` defines a function with required `celsius` and optional `to_unit`.
- `"fahrenheit"` is the default, so the first call needs only `0`.
- The `if` checks the requested unit; the formula converts Celsius to Fahrenheit.
- Otherwise the function returns the original Celsius value.
- The second call overrides the default by keyword.
- Output: `32.0`, then `0`.

This exercise demonstrates defaults and keyword overrides. It supports only the two named unit choices in this simple exercise.

## Exercise 2 — Show a positional-order bug

```python
def describe_booking(customer, room, nights):
    return f"{customer} booked {room} for {nights} nights."

print(describe_booking("Asha", "Suite", 2))
print(describe_booking("Suite", "Asha", 2))
```

- The function expects values in the order `customer`, `room`, `nights`.
- The first call follows that order.
- The second swaps the first two strings.
- Python still runs it because both values are valid strings; it cannot infer their intended meanings.
- Output:
  - `Asha booked Suite for 2 nights.`
  - `Suite booked Asha for 2 nights.`

A keyword-based call such as `describe_booking(customer="Asha", room="Suite", nights=2)` makes the intent clearer.

## Exercise 3 — Demonstrate and fix a mutable default

```python
def add_tag_unsafe(tag, tags=[]):
    tags.append(tag)
    return tags

print(add_tag_unsafe("python"))
print(add_tag_unsafe("data"))
print(add_tag_unsafe("engineering"))

def add_tag_safe(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags

print(add_tag_safe("python"))
print(add_tag_safe("data"))
print(add_tag_safe("engineering"))
```

- In the unsafe function, `[]` is created once when the function is defined.
- Each call appends to that same list, so outputs accumulate: `['python']`, `['python', 'data']`, then `['python', 'data', 'engineering']`.
- In the safe function, `None` is the default.
- `if tags is None` creates a fresh list for that call.
- Each safe call therefore returns its own one-item list.

## Exercise 4 — Keyword-only notification option

```python
def send_notification(message, *, urgent=False):
    if urgent:
        return f"URGENT: {message}"
    return message

print(send_notification("Backup complete"))
print(send_notification("Server is down", urgent=True))
print(send_notification("Server is down", True))
```

- `message` is required.
- `*` makes `urgent` keyword-only; its default is `False`.
- The first call uses the default; the second explicitly enables urgency.
- The third call is deliberately invalid: Python raises `TypeError` because `urgent` cannot be supplied as a second positional argument.
- Expected valid outputs: `Backup complete` and `URGENT: Server is down`.

## Exercise 5 — Add a docstring and inspect it

```python
def calculate_area(width, height):
    """Return the area of a rectangle from its width and height."""
    return width * height

print(calculate_area(5, 4))
help(calculate_area)
```

- The function name describes the action.
- `width` and `height` are required parameters.
- The docstring is the first statement inside the function and describes its purpose and inputs.
- `return` sends the calculated area back to the caller.
- `help()` displays the function signature and docstring.
- The calculation prints `20`.

## Exercise 6 — Improve an unclear signature

Suppose `calc(a, b, c=1)` is intended to calculate a product subtotal, with an optional discount percentage.

```python
def calculate_subtotal(unit_price, quantity, *, discount_rate=0):
    subtotal = unit_price * quantity
    discount = subtotal * discount_rate
    return subtotal - discount

print(calculate_subtotal(10, 3))
print(calculate_subtotal(10, 3, discount_rate=0.10))
```

- `calculate_subtotal` clearly names the task.
- `unit_price` and `quantity` are required and have meaningful names.
- `discount_rate` is keyword-only because it follows `*`.
- Its default `0` means no discount unless the caller chooses one.
- The function calculates the subtotal, calculates the discount amount, and returns the amount after discount.
- Outputs: `30.0` and `27.0`.

The rate is supplied as a fraction: `0.10` means 10%. This is a simple exercise contract, not a full pricing or tax system.

---

## Readiness checklist

Before moving on, make sure you can explain and demonstrate:
- Required versus default parameters and the missing-argument `TypeError`.
- Positional order risks and keyword arguments.
- Why positional arguments must precede keyword arguments in a call.
- Why mutable defaults are shared and how the `None` pattern fixes that.
- How `*` creates keyword-only parameters.
- How a useful docstring and `help()` describe a function's contract.

**Learning boundary:** this lesson is about function interfaces and documentation. Input-type validation and deliberately raising custom errors belong to the later exceptions/validation lesson, so they are not added to these solutions.
