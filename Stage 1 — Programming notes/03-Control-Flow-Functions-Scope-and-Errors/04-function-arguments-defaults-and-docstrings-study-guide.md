# Function Arguments, Defaults, and Docstrings — Complete Study Guide and Exercise Solutions

**Source lesson:** `04-function-arguments-defaults-and-docstrings.md`  
**Roadmap:** Stage 1 — Programming & Computational Thinking → Module 03 — Control Flow, Functions, Scope, and Errors → Lesson 04

---

# Part A — Complete lesson summary

## 1. Why function interfaces matter

You already learned how to define a function, pass parameters, and return a value. This lesson focuses on designing the way other parts of a program call that function.

A function can calculate the correct result and still be difficult or dangerous to use if its inputs are unclear. For example, a function that accepts five unlabeled values in a strict order makes the caller remember what each value means. A well-designed function instead has meaningful parameter names, clearly identifies required and optional inputs, uses sensible defaults, and explains its behavior.

This is called **function interface design**. It matters in data engineering because pipeline functions are called by other functions, scheduled jobs, services, and sometimes AI agents. A clear interface reduces misuse.

## 2. Learning outcomes

By the end of the lesson, you should be able to:

- Treat a function signature as a contract between a function and its caller.
- Identify required parameters and understand missing-argument `TypeError` messages.
- Explain why swapped positional arguments can silently create incorrect results.
- Use keyword arguments and correctly mix positional and keyword arguments.
- Choose safe defaults and override them.
- Explain and fix the mutable default argument problem.
- Define and call keyword-only parameters.
- Write a useful docstring and inspect it with `help()`.
- Evaluate whether a function has clear names, sensible defaults, predictable returns, and useful errors.

## 3. Prerequisites and key terms

The lesson assumes that you understand `def`, function calls, parameters, `return`, lists, mutability, and aliasing. The mutable-default issue is a direct application of list mutation and aliasing.

| Term | Meaning |
|---|---|
| Function signature | The function name and its parameter list, including required, defaulted, and keyword-only parameters. |
| Interface / contract | The agreement about what inputs the caller supplies and what result the function provides. |
| Required parameter | A parameter with no default; the caller must provide its argument. |
| `TypeError` | An exception raised when an operation or function call receives an invalid form of input, such as a missing required argument or too many positional arguments. |
| Positional argument | An argument matched to a parameter by its position. |
| Keyword argument | An argument matched by explicitly naming its parameter. |
| Default value | The value used when the caller omits an optional argument. |
| Mutable default | A mutable object such as `[]` used as a default; it is created once and can be shared across calls. |
| Keyword-only parameter | A parameter after `*` in the function definition; it must be supplied by name. |
| Docstring | A string at the beginning of a function body that documents the function. |
| `help()` | A built-in function that displays a function's signature and documentation. |

## 4. Function signature as a contract

A function's signature tells the caller how to use it. A caller should be able to understand the required inputs and optional settings without reading the implementation.

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

print(format_price(19.99))
```

Output:

```text
$19.99
```

Step by step:

1. `def` defines the function.
2. `format_price` is a descriptive function name.
3. `amount` is a required parameter because it has no default.
4. `currency="$"` is optional because it has a default.
5. `return` sends the formatted string to the caller.
6. `format_price(19.99)` supplies the required amount and uses the default dollar sign.

The names `amount` and `currency` make the contract clear. Names such as `a` and `b` would hide the meaning.

## 5. Required parameters

A required parameter has no default. The caller must supply an argument for it.

```python
def greet_by_username(username):
    return f"Welcome, {username}!"

print(greet_by_username("ada99"))
```

Output:

```text
Welcome, ada99!
```

The function has one required parameter: `username`.

A function can require more than one argument:

```python
def calculate_total(price, quantity):
    return price * quantity

print(calculate_total(9.99, 3))
```

Output:

```text
29.97
```

Both `price` and `quantity` are required.

If the caller forgets one:

```python
print(calculate_total(9.99))
```

Python raises:

```text
TypeError: calculate_total() missing 1 required positional argument: 'quantity'
```

If the caller supplies neither:

```python
print(calculate_total())
```

Python raises:

```text
TypeError: calculate_total() missing 2 required positional arguments: 'price' and 'quantity'
```

The exact wording can vary by Python version. The important point is that Python identifies the function and the missing parameter. This is Python enforcing the function's contract instead of guessing a value.

## 6. Positional arguments and the danger of incorrect order

A positional argument is matched to a parameter based on its location in the call.

```python
def schedule_meeting(start_time, end_time):
    return f"Meeting from {start_time} to {end_time}"

print(schedule_meeting("1:00 PM", "3:00 PM"))
print(schedule_meeting("3:00 PM", "1:00 PM"))
```

Output:

```text
Meeting from 1:00 PM to 3:00 PM
Meeting from 3:00 PM to 1:00 PM
```

Both calls execute because both arguments are strings, which the function can use. However, the second call may represent an invalid meeting interval. Python does not understand the business meaning of the values; it only maps the first argument to `start_time` and the second to `end_time`.

This is a subtle bug: the program does not crash, but its result is wrong. When a function has several values of the same type, use careful ordering or keyword arguments.

## 7. Keyword arguments and mixing argument styles

A keyword argument explicitly names the parameter using `parameter=value`.

```python
def calculate_total(price, quantity):
    return price * quantity

print(calculate_total(price=9.99, quantity=3))
print(calculate_total(quantity=3, price=9.99))
print(calculate_total(9.99, quantity=3))
```

All three calls output:

```text
29.97
```

Explanation:

- The first call names both arguments.
- The second call names both arguments in the opposite order. It still works because Python matches by name.
- The third call supplies `price` positionally and `quantity` by keyword.

This is allowed and commonly used. The important ordering rule is:

**Ordinary positional arguments must come before ordinary keyword arguments.**

This is invalid:

```python
calculate_total(quantity=3, 9.99)
```

It raises a `SyntaxError` because a positional argument follows a keyword argument. Python cannot safely guess which parameter the trailing positional value should fill.

Keyword arguments make calls self-explanatory. Compare `calculate_total(9.99, 3)` with `calculate_total(price=9.99, quantity=3)`: the latter communicates the meaning of each number directly.

## 8. Default arguments

A default value allows the caller to omit an argument. Python uses the default only when the caller does not provide a value for that parameter.

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

print(format_price(19.99))
print(format_price(19.99, "€"))
print(format_price(19.99, currency="£"))
```

Output:

```text
$19.99
€19.99
£19.99
```

- The first call omits `currency`, so it uses `"$"`.
- The second overrides the default positionally with `"€"`.
- The third overrides it using the keyword `currency="£"`.

Prefer immutable defaults such as strings, numbers, Booleans, and `None` when the function should not share mutable state between calls.

## 9. Mutable default argument danger

A mutable object can change after it is created. Lists, dictionaries, and sets are mutable. Python evaluates a default argument once, when the function is defined, not again for every call.

Unsafe example:

```python
def add_task(task, tasks=[]):
    tasks.append(task)
    return tasks

todo_list_a = add_task("Write report")
print(todo_list_a)

todo_list_b = add_task("Buy groceries")
print(todo_list_b)
```

Output:

```text
['Write report']
['Write report', 'Buy groceries']
```

Why?

1. Python creates one empty list when it executes the `def` statement.
2. The first call omits `tasks`, so it uses that list and appends `"Write report"`.
3. The second call also omits `tasks`, so it reuses the same list.
4. It appends `"Buy groceries"` to the already populated list.
5. The second result therefore contains both tasks.

This is related to **aliasing**: different calls appear independent, but they share a reference to the same list object.

### Safe pattern: use `None`

```python
def add_task(task, tasks=None):
    if tasks is None:
        tasks = []
    tasks.append(task)
    return tasks

todo_list_a = add_task("Write report")
print(todo_list_a)

todo_list_b = add_task("Buy groceries")
print(todo_list_b)
```

Output:

```text
['Write report']
['Buy groceries']
```

Step by step:

1. `tasks=None` uses a safe immutable default.
2. `if tasks is None:` checks whether the caller omitted a list.
3. `tasks = []` creates a fresh list inside this function call.
4. `tasks.append(task)` adds the new task.
5. `return tasks` returns that call's list.

Because the list is created inside the function body, each call that omits `tasks` gets a new list.

You can also deliberately pass an existing list:

```python
my_tasks = ["Read documentation"]
updated_tasks = add_task("Run tests", my_tasks)
print(updated_tasks)
```

Output:

```text
['Read documentation', 'Run tests']
```

Here, the supplied list is reused and mutated intentionally. The `None` pattern does not prohibit mutation; it prevents accidental sharing through the default.

**Rule:** Avoid `[]`, `{}`, or `set()` as defaults when each call should start with fresh mutable state. Use `None` and construct the collection inside the function.

## 10. Keyword-only parameters

A standalone `*` in a function definition makes every parameter after it keyword-only. Such parameters must be supplied by name.

```python
def calculate_total(price, quantity, *, include_tax=False):
    subtotal = price * quantity
    if include_tax:
        return subtotal * 1.08
    return subtotal

print(calculate_total(10, 2))
print(calculate_total(10, 2, include_tax=True))
```

Output:

```text
20
21.6
```

`price` and `quantity` are ordinary parameters; they can be supplied positionally or by keyword. `include_tax` follows `*`, so it must be named.

This is invalid:

```python
calculate_total(10, 2, True)
```

It raises a `TypeError` because the function accepts only two positional arguments. The explicit call `calculate_total(10, 2, include_tax=True)` is easier to understand than an unexplained `True`.

Keyword-only parameters are useful for optional settings such as `verbose`, `currency`, or `include_tax`.

## 11. Docstrings and `help()`

A docstring is a string placed as the first statement in a function body. A useful docstring explains:

1. The function's purpose.
2. What each parameter means.
3. What the function returns.
4. Important assumptions the caller should know.

```python
def format_price(amount, currency="$"):
    """
    Format a number as a price string.

    amount is the numeric price to display.
    currency is the symbol to place in front of the amount, and
    defaults to "$" when the caller does not supply one.
    Returns a string such as "$19.99".
    """
    return f"{currency}{amount:.2f}"

help(format_price)
```

`help(format_price)` displays the function signature, including the default value, and the docstring. The displayed output is similar to:

```text
Help on function format_price in module __main__:

format_price(amount, currency='$')
    Format a number as a price string.

    amount is the numeric price to display.
    currency is the symbol to place in front of the amount, and
    defaults to "$" when the caller does not supply one.
    Returns a string such as "$19.99".
```

At this stage, plain-English sentences are sufficient. You do not need a documentation framework or special docstring format to explain a function clearly.

## 12. Designing a clear function contract

A well-designed function contract has five qualities:

1. **Clear names:** use action-oriented function names such as `calculate_total`, and meaningful parameter names such as `price` and `quantity`.
2. **Clear parameter meaning:** a caller should understand what to supply without reading the function body.
3. **Sensible defaults:** optional settings should default to what most callers need; prefer immutable defaults.
4. **Predictable return values:** return a consistent kind of result rather than sometimes returning a value and sometimes `None` unexpectedly.
5. **Clear errors for invalid calls:** Python should be able to report missing or excess arguments clearly.

Compare:

```python
def calc(a, b, c=1):
    ...
```

with:

```python
def calculate_total(price, quantity, *, include_tax=False):
    ...
```

The second signature makes the purpose of the inputs and the optional tax setting much clearer.

One limitation: a signature and docstring do not automatically validate the types or business validity of supplied values. For example, passing `"ten"` as a price may cause an error during multiplication, or produce an unintended result in some contexts. Explicit input validation and deliberate error handling are covered in the later lesson on exceptions and validation.

---

## 13. All six lesson examples

### Example 1 — `format_price`: default with override

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

domestic_price = format_price(42.5)
foreign_price = format_price(42.5, currency="€")

print(domestic_price)
print(foreign_price)
```

Output:

```text
$42.50
€42.50
```

`amount` is required. `currency` is optional and defaults to `"$"`. The first call uses the default. The second overrides it with the euro symbol by keyword. The function itself does not need to change.

### Example 2 — `create_greeting`: keyword arguments in repeated calls

```python
def create_greeting(name, greeting="Hello"):
    return f"{greeting}, {name}!"

visitors = ["Ada", "Grace", "Alan"]

for visitor in visitors:
    print(create_greeting(visitor))

print(create_greeting("Marie", greeting="Welcome back"))
```

Output:

```text
Hello, Ada!
Hello, Grace!
Hello, Alan!
Welcome back, Marie!
```

`name` is required and `greeting` defaults to `"Hello"`. The `for` loop calls the function once per visitor and relies on the default. The final call overrides the greeting for Marie using a keyword argument.

### Example 3 — `calculate_total`: keyword-only tax option

```python
def calculate_total(price, quantity, *, include_tax=False):
    subtotal = price * quantity
    if include_tax:
        return subtotal * 1.08
    return subtotal

price_without_tax = calculate_total(12.50, 4)
price_with_tax = calculate_total(12.50, 4, include_tax=True)

print(f"Without tax: ${price_without_tax:.2f}")
print(f"With tax: ${price_with_tax:.2f}")
```

Output:

```text
Without tax: $50.00
With tax: $54.00
```

`price` and `quantity` are required ordinary parameters. `include_tax` is keyword-only and defaults to `False`. The first call returns the subtotal; the second explicitly requests an 8% tax calculation. Both calls return a number, so the return type is predictable.

### Example 4 — `add_task`: safe mutable-default pattern

```python
def add_task(task, tasks=None):
    if tasks is None:
        tasks = []
    tasks.append(task)
    return tasks

mondays_tasks = add_task("Write report")
mondays_tasks = add_task("Review code", mondays_tasks)

tuesdays_tasks = add_task("Plan sprint")

print("Monday:", mondays_tasks)
print("Tuesday:", tuesdays_tasks)
```

Output:

```text
Monday: ['Write report', 'Review code']
Tuesday: ['Plan sprint']
```

The first call creates a new Monday list. The second call deliberately passes that existing list back, so the function appends `"Review code"` to it. The Tuesday call omits the list, so it creates a different list. Monday and Tuesday do not share default state.

### Example 5 — `schedule_meeting`: required parameters, order, and missing argument

```python
def schedule_meeting(start_time, end_time, topic):
    return f"'{topic}' runs from {start_time} to {end_time}."

correct_booking = schedule_meeting("1:00 PM", "2:00 PM", "Budget review")
print(correct_booking)

confusing_booking = schedule_meeting("2:00 PM", "Budget review", "1:00 PM")
print(confusing_booking)
```

Output:

```text
'Budget review' runs from 1:00 PM to 2:00 PM.
'1:00 PM' runs from 2:00 PM to Budget review.
```

The three required parameters must be supplied. The first call follows their order. The second swaps values: Python does not crash because all three are strings, but the sentence becomes nonsensical. Omitting `topic`, as in `schedule_meeting("1:00 PM", "Budget review")`, raises a `TypeError` naming the missing `topic` parameter. Python can detect a missing argument, but it cannot infer that same-type values were supplied in the wrong semantic order.

### Example 6 — `build_invoice_line`: a complete function contract

```python
def build_invoice_line(item_name, unit_price, quantity, *, currency="$", tax_included=False):
    """
    Build one formatted line of an invoice.

    item_name is the product's name, shown as-is.
    unit_price is the price of a single unit, before tax.
    quantity is how many units were purchased.
    currency is the symbol shown before every amount, and defaults to "$".
    tax_included, when True, adds 8% tax to the line total.
    Returns the formatted line as a single string.
    """
    line_total = unit_price * quantity
    if tax_included:
        line_total = line_total * 1.08

    return f"{item_name} x{quantity}: {currency}{line_total:.2f}"

print(build_invoice_line("Notebook", 3.50, 4))
print(build_invoice_line("Notebook", 3.50, 4, tax_included=True))
print(build_invoice_line("Notebook", 3.50, 4, currency="€", tax_included=True))
```

Output:

```text
Notebook x4: $14.00
Notebook x4: $15.12
Notebook x4: €15.12
```

`item_name`, `unit_price`, and `quantity` are required. `currency` and `tax_included` are keyword-only options with immutable defaults. The function calculates the line total, optionally adds 8% tax, and returns one formatted string. The docstring explains the purpose, every parameter, and the return value. `help(build_invoice_line)` can display this contract to a caller.

## 14. Common beginner mistakes

- Using vague parameter names such as `a`, `b`, or `x`.
- Assuming Python detects incorrect positional order. It detects missing arguments, but cannot always detect semantically swapped values of the same type.
- Putting a positional argument after a keyword argument, which causes `SyntaxError`.
- Using `[]`, `{}`, or `set()` as a default when each call should receive fresh state.
- Passing a keyword-only parameter positionally, which causes `TypeError`.
- Writing a docstring that only repeats the function name instead of explaining inputs and output.
- Assuming a signature automatically validates input types. It does not; explicit validation belongs to the later exceptions/validation lesson.

## 15. Connection to Applied AI and Agentic AI

An AI agent or another software component may call a function as a tool. The caller needs to know which arguments are required, which are optional, how to pass options, and what result will come back.

- Clear signatures make tools easier to call correctly.
- Keyword-only options prevent ambiguous values such as an unexplained `True`.
- Predictable return values make downstream processing simpler.
- Useful docstrings help engineers and tool-using systems understand the function's purpose and inputs.
- Safe defaults prevent state from leaking between separate calls or requests.

The same discipline applies to data pipeline functions, API service functions, validation operations, and transformation steps.

## 16. Completion checklist

You should be able to explain the function contract, identify required parameters, read missing-argument `TypeError` messages, use positional and keyword arguments, mix them correctly, override defaults, explain and fix mutable defaults, define keyword-only options, write docstrings, inspect them with `help()`, and name the five qualities of a well-designed contract.

---

# Part B — Project-tree analysis and current learning level

## 1. Where this lesson fits

The supplied roadmap places this file in:

```text
Stage 1 — Programming & Computational Thinking/
└── 03-Control-Flow-Functions-Scope-and-Errors/
    ├── 01-conditionals-guards-and-boolean-logic.md
    ├── 02-for-while-loops-and-loop-control.md
    ├── 03-functions-parameters-and-return-values.md
    ├── 04-function-arguments-defaults-and-docstrings.md  <-- current lesson
    ├── 05-scope-lifetime-and-global-state.md
    ├── 06-pure-functions-and-side-effects.md
    ├── 07-exceptions-validation-and-useful-errors.md
    ├── README.md
    └── practice-questions.md
```

The immediate learning sequence is deliberate:

1. Conditionals teach decision-making.
2. Loops teach repetition.
3. Functions teach reusable operations and return values.
4. This lesson teaches how to design a safe and understandable function interface.
5. Scope and lifetime explain where variables exist and how state behaves.
6. Pure functions and side effects distinguish predictable computation from operations that change external state.
7. Exceptions and validation teach deliberate handling of invalid inputs and failures.

This lesson builds directly on the previous functions lesson and the earlier lessons on lists, mutability, and aliasing.

## 2. Wider Stage 1 structure

The Stage 1 project tree progresses through these areas:

- **Module 01 — Computational Thinking and Program Design:** algorithms, expressions, variables, input/process/output, sequence/selection/iteration/abstraction, decomposition, preconditions, postconditions, edge cases, pseudocode, dry runs, and state modelling.
- **Module 02 — Python Core Language and Data Types:** Python files and interpreter, variables and basic types, operators, strings, lists, tuples, dictionaries, sets, type conversion, truthiness, mutability, and immutability.
- **Module 03 — Control Flow, Functions, Scope, and Errors:** conditionals, loops, functions, argument design, scope, side effects, exceptions, and validation.
- **Module 04 — Problem-Solving, Collections, and Algorithmic Habits:** searching, counting, filtering, mapping, aggregation, grouping, deduplication, sorting, Big-O, data-structure selection, comprehensions, recursion, and parsing/regular expressions.
- **Module 05 — Text Files, Structured Data, and CLI Programs:** file operations, paths, CSV, JSON, encodings, command-line arguments, streams, logging, and configuration.
- **Module 06 — Modules, Packages, Dependencies, and Code Quality:** imports, project layout, dependency management, formatting, linting, type hints, and documentation.
- **Module 07 — Testing and Systematic Debugging:** unit/integration/end-to-end tests, pytest, test design, boundary tests, debugging, tracebacks, logging, and mocks.
- **Module 08 onward:** object-oriented design, production-oriented Python, production habits, advanced Python internals, metaprogramming, standard-library tools, binary/text processing, modern language features, advanced testing, profiling, packaging, and distribution.

The roadmap also contains four Stage 1 capstone projects:

1. Personal Expense Ledger CLI.
2. Log Investigation and Reliability CLI.
3. Data Quality and Transformation Pipeline.
4. Rule-Based Risk Review Engine.

Function contracts matter in all four. For example, an expense project can have a function to calculate a transaction total; a log tool can have a function to classify an event; a data-quality pipeline can have validation and transformation functions; and a risk engine can have a function that calculates a score from clearly named inputs.

## 3. Your current level and exercise boundaries

Your recorded progress includes the earlier Module 03 lessons and substantial Module 04 practice: searching and aggregation, grouping/deduplication/sorting, Big-O, data-structure selection, comprehensions, recursion, parsing, and regular expressions. You have also completed the preceding functions lesson.

**Assessment: beginner progressing toward intermediate in Python engineering.** Your exposure to collections and algorithmic problem-solving is already beyond the basics, while Module 03 is currently building the discipline needed to turn individual snippets into reliable reusable components.

The six exercises below stay within this lesson and its prerequisites: function definitions, parameters, positional/keyword/default arguments, `None`, lists, conditionals, loops, strings, basic arithmetic, return values, and docstrings. No classes, pandas, external libraries, decorators, file handling, or advanced validation frameworks are introduced.

---

# Part C — All six exercises with solutions

## Exercise 1 — Temperature conversion with a default unit

**Task:** Write `convert_temperature(celsius, to_unit="fahrenheit")`. Call it once with the default and once overriding the unit by keyword.

### Solution

```python
def convert_temperature(celsius, to_unit="fahrenheit"):
    if to_unit == "fahrenheit":
        return (celsius * 9 / 5) + 32
    elif to_unit == "celsius":
        return celsius
    else:
        return None

default_result = convert_temperature(25)
celsius_result = convert_temperature(25, to_unit="celsius")

print(f"Default conversion: {default_result:.1f} F")
print(f"Celsius result: {celsius_result:.1f} C")
```

Expected output:

```text
Default conversion: 77.0 F
Celsius result: 25.0 C
```

### Line-by-line explanation

1. `def convert_temperature(celsius, to_unit="fahrenheit"):` defines two parameters. `celsius` is required; `to_unit` defaults to Fahrenheit.
2. `if to_unit == "fahrenheit":` checks whether Fahrenheit output was requested.
3. `return (celsius * 9 / 5) + 32` applies the Celsius-to-Fahrenheit formula and returns the result.
4. `elif to_unit == "celsius":` checks for Celsius output.
5. `return celsius` returns the original temperature because it is already in Celsius.
6. `else: return None` handles an unsupported unit. This is a simple fallback for this exercise; a later validation lesson will teach more explicit error handling.
7. `convert_temperature(25)` omits `to_unit`, so the default `"fahrenheit"` is used.
8. `convert_temperature(25, to_unit="celsius")` overrides the default by keyword.
9. The two `print()` calls display the returned values to one decimal place.

**Important:** `None` indicates that this small exercise did not recognize the requested unit. In production code, invalid units should be reported with a clear deliberate error.

## Exercise 2 — Three required parameters and swapped positional arguments

**Task:** Create a function with three required parameters, call it correctly, then swap two arguments and explain why Python does not raise an error.

### Solution

```python
def describe_delivery(customer_name, city, package_count):
    return f"{customer_name} in {city} receives {package_count} packages."

correct_result = describe_delivery("Asha", "Pune", 3)
swapped_result = describe_delivery("Pune", "Asha", 3)

print(correct_result)
print(swapped_result)

# The second call is wrong because customer_name and city were swapped.
# Python does not raise an error because both supplied values are strings.
```

Expected output:

```text
Asha in Pune receives 3 packages.
Pune in Asha receives 3 packages.
```

### Line-by-line explanation

1. `def describe_delivery(customer_name, city, package_count):` defines three required parameters. None has a default.
2. The `return` statement builds and returns a sentence using all three values.
3. `describe_delivery("Asha", "Pune", 3)` supplies arguments in the correct order: name, city, count.
4. `describe_delivery("Pune", "Asha", 3)` swaps the first two arguments.
5. Python still assigns the first string to `customer_name` and the second string to `city`, because positional matching depends only on order.
6. Both values are valid strings, so the function executes. Python cannot infer that the caller intended the opposite semantic meaning.
7. The comments record why the second result is wrong but does not cause a Python exception.

**Key concept:** A function call can be syntactically valid and still be logically incorrect. Keyword arguments can make the call safer: `describe_delivery(customer_name="Asha", city="Pune", package_count=3)`.

## Exercise 3 — Reproduce and repair the mutable default bug

**Task:** Call a function with `tags=[]` three times without supplying `tags`, observe the shared list, then repair it with `None`.

### Unsafe version — reproduce the bug

```python
def add_tag_unsafe(tag, tags=[]):
    tags.append(tag)
    return tags

first = add_tag_unsafe("python")
second = add_tag_unsafe("data")
third = add_tag_unsafe("engineering")

print(first)
print(second)
print(third)
```

Expected output:

```text
['python', 'data', 'engineering']
['python', 'data', 'engineering']
['python', 'data', 'engineering']
```

### Explanation

1. `tags=[]` creates one list when Python defines the function.
2. The first call appends `"python"` to that list.
3. The second call reuses the same default list and appends `"data"`.
4. The third call reuses it again and appends `"engineering"`.
5. All three variables refer to the same list object, so each print shows all three tags.

### Safe version — use `None`

```python
def add_tag_safe(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags

first = add_tag_safe("python")
second = add_tag_safe("data")
third = add_tag_safe("engineering")

print(first)
print(second)
print(third)
```

Expected output:

```text
['python']
['data']
['engineering']
```

### Line-by-line explanation

1. `def add_tag_safe(tag, tags=None):` makes `None` the default value.
2. `if tags is None:` checks whether the caller omitted a list.
3. `tags = []` creates a new list for this function call.
4. `tags.append(tag)` adds the current tag to that list.
5. `return tags` sends the list back to the caller.
6. Each call omits `tags`, so each one creates a separate list.
7. The print statements therefore show one independent tag in each list.

**Key concept:** The default `None` is shared safely, while the mutable list is constructed separately during each call.

## Exercise 4 — Keyword-only parameter and positional-call error

**Task:** Write `send_notification(message, *, urgent=False)`. Demonstrate the default, the keyword override, and the error from trying to pass `urgent` positionally.

### Solution

```python
def send_notification(message, *, urgent=False):
    if urgent:
        return f"URGENT: {message}"
    return message

normal_message = send_notification("The pipeline completed.")
urgent_message = send_notification("The pipeline failed.", urgent=True)

print(normal_message)
print(urgent_message)

# This call is intentionally invalid:
# send_notification("The pipeline failed.", True)
```

Expected output from the valid calls:

```text
The pipeline completed.
URGENT: The pipeline failed.
```

If you uncomment the invalid call, Python raises an error similar to:

```text
TypeError: send_notification() takes 1 positional argument but 2 were given
```

### Line-by-line explanation

1. `def send_notification(message, *, urgent=False):` defines `message` as an ordinary required parameter and `urgent` as a keyword-only parameter.
2. The `*` is the separator: every parameter after it must be passed by name.
3. `if urgent:` checks whether the caller requested urgent handling.
4. `return f"URGENT: {message}"` returns a message with an urgent prefix when `urgent` is true.
5. `return message` returns the original message when `urgent` is false.
6. The first call omits `urgent`, so the default `False` is used.
7. The second call uses `urgent=True` by keyword.
8. The commented invalid call tries to provide `True` as a second positional argument. It is invalid because `urgent` is keyword-only.

**Key concept:** Use keyword-only parameters for options whose meaning should be explicit at the call site.

## Exercise 5 — Add a docstring and inspect it with `help()`

**Task:** Add a docstring to a function from the previous lesson's exercises, covering purpose, parameters, and return value. Confirm it with `help()`.

### Solution

```python
def calculate_area(width, height):
    """
    Calculate the area of a rectangle.

    width is the rectangle's width.
    height is the rectangle's height.
    Returns the area as width multiplied by height.
    """
    return width * height

print(calculate_area(5, 3))
help(calculate_area)
```

Expected first output:

```text
15
```

`help(calculate_area)` displays information similar to:

```text
Help on function calculate_area in module __main__:

calculate_area(width, height)
    Calculate the area of a rectangle.

    width is the rectangle's width.
    height is the rectangle's height.
    Returns the area as width multiplied by height.
```

### Line-by-line explanation

1. `def calculate_area(width, height):` defines a function with two required parameters.
2. The triple-quoted string is the docstring because it is the first statement in the function body.
3. `Calculate the area of a rectangle.` explains the function's purpose.
4. `width is ...` explains the first parameter.
5. `height is ...` explains the second parameter.
6. `Returns ...` explains the returned value.
7. `return width * height` performs the calculation and returns the result.
8. `print(calculate_area(5, 3))` calls the function and displays `15`.
9. `help(calculate_area)` displays the signature and stored docstring.

**Key concept:** A useful docstring lets another engineer understand how to call a function without reading its implementation.

## Exercise 6 — Redesign `calc(a, b, c=1)` with a clear contract

**Task:** Invent a real task for the unclear signature and rewrite it with a clear function name, meaningful parameter names, and a keyword-only option if appropriate.

### Original unclear signature

```python
def calc(a, b, c=1):
    ...
```

A caller cannot tell what `a`, `b`, or `c` represent. The function name `calc` is also vague.

### Improved design — calculate an order total with optional tax

```python
def calculate_order_total(unit_price, quantity, *, tax_rate=0.0):
    subtotal = unit_price * quantity
    total = subtotal * (1 + tax_rate)
    return total

basic_total = calculate_order_total(25, 2)
taxed_total = calculate_order_total(25, 2, tax_rate=0.08)

print(f"Basic total: ${basic_total:.2f}")
print(f"Taxed total: ${taxed_total:.2f}")
```

Expected output:

```text
Basic total: $50.00
Taxed total: $54.00
```

### Line-by-line explanation

1. `def calculate_order_total(unit_price, quantity, *, tax_rate=0.0):` gives the function an action-oriented name and meaningful parameters.
2. `unit_price` is the price of one unit.
3. `quantity` is how many units are ordered.
4. `*` makes `tax_rate` keyword-only, so the caller must make the tax choice explicit.
5. `tax_rate=0.0` is a sensible immutable default: no tax is added unless requested.
6. `subtotal = unit_price * quantity` calculates the pre-tax amount.
7. `total = subtotal * (1 + tax_rate)` adds the specified fraction of tax.
8. `return total` returns a number that the caller can reuse.
9. `calculate_order_total(25, 2)` uses the default tax rate of zero, returning 50.
10. `calculate_order_total(25, 2, tax_rate=0.08)` explicitly requests 8% tax, returning 54.
11. The print statements display each result to two decimal places.

### Why this is a better contract

- `calculate_order_total` explains the action.
- `unit_price` and `quantity` explain the required inputs.
- `tax_rate` explains the optional setting.
- The keyword-only marker prevents an ambiguous third positional value.
- The default is immutable and sensible for the assumed task.
- The function always returns a numeric total.

---

# Part D — Quick revision sheet

| Concept | Remember |
|---|---|
| Function signature | Name plus parameter list; the caller-facing contract. |
| Required parameter | Has no default; caller must provide an argument. |
| Missing argument | Raises `TypeError` naming the missing parameter. |
| Positional argument | Matched by order; wrong order can silently produce wrong output. |
| Keyword argument | Matched by parameter name; improves clarity. |
| Mixing styles | Ordinary positional arguments must precede ordinary keyword arguments. |
| Default argument | Used when caller omits that parameter; can be overridden. |
| Safe defaults | Prefer immutable values such as strings, numbers, Booleans, and `None`. |
| Mutable default | A list/dict/set default is created once and reused. |
| `None` pattern | Check `if value is None`, then create a fresh collection inside the function. |
| Keyword-only | Parameters after `*` must be supplied by name. |
| Docstring | First string in the function body; describes purpose, inputs, output, assumptions. |
| `help()` | Displays a function's signature and docstring. |
| Function contract quality | Clear names, clear parameter meaning, sensible defaults, predictable returns, clear errors. |

## Final self-check

Before moving to the next lesson, you should be able to design a function call that is clear without reading the function body, explain why a swapped positional call can be wrong without crashing, identify the shared-list default bug, use `None` to avoid it, require an option to be passed by keyword, and write a docstring that `help()` can display.
