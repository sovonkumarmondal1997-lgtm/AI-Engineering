# Functions, Parameters, and Return Values — Complete Study Guide and Exercise Solutions

**Source lesson:** `03-functions-parameters-and-return-values.md`  
**Roadmap location:** Stage 1 → Module 03 — Control Flow, Functions, Scope, and Errors → Lesson 03  
**Scope:** Complete teaching summary of the lesson, its code patterns and seven examples, project-tree assessment, and solutions to all six “Try it yourself” exercises.

---

# Part A — Complete lesson summary

## 1. Why functions matter

A function is a **named, reusable group of instructions** that performs a particular task. Without functions, a program can become one long sequence of instructions. When the same logic is needed in several places, copying and pasting it creates problems: a bug must be fixed in every copy, and one copy can easily be forgotten.

Functions solve this by letting you write logic once and call it whenever needed. They improve:

- **Reusability:** one implementation can be used many times.
- **Readability:** a name such as `calculate_total()` communicates the purpose without exposing every implementation detail.
- **Maintainability:** a correction in one function benefits every caller.
- **Problem decomposition:** a large task can be divided into smaller, understandable operations.

A function is also the foundation of modular software. In later data engineering and AI systems, different functions can validate records, calculate metrics, transform data, call services, or return results to an agent.

## 2. Defining a function versus calling it

A function definition creates the function. A function call executes its body. These are two different operations.

```python
def greet_user():
    print("Hello! Welcome to the program.")

greet_user()
greet_user()
```

Output:

```text
Hello! Welcome to the program.
Hello! Welcome to the program.
```

Understand each part:

1. `def` is Python's keyword for defining a function.
2. `greet_user` is the function name. A meaningful name should normally describe an action, often beginning with a verb.
3. `()` contains the function's parameters. This function has none.
4. `:` marks the beginning of the function body.
5. The indented `print()` statement belongs to the function.
6. The `def` statement creates the function but does not execute its body.
7. `greet_user()` is a function call. Each call executes the body once.

The function can be called as many times as needed without rewriting its body.

## 3. Parameters and arguments

A **parameter** is a variable name in the function definition. An **argument** is the actual value supplied when calling the function. During the call, Python binds the argument value to the parameter name.

```python
def greet_by_name(name):
    print(f"Hello, {name}!")

greet_by_name("Ada")
greet_by_name("Grace")
```

Output:

```text
Hello, Ada!
Hello, Grace!
```

Here, `name` is the parameter. `"Ada"` and `"Grace"` are arguments supplied in two separate calls.

A function can have multiple parameters:

```python
def calculate_total(unit_price, quantity):
    print(unit_price * quantity)

calculate_total(4.5, 3)
```

Output:

```text
13.5
```

`unit_price` and `quantity` are parameters. The arguments `4.5` and `3` are matched to them in that order. The function multiplies them and displays the result.

## 4. `print()` versus `return`

This is the most important distinction in the lesson.

- `print(value)` displays a value for a person to see. It does not send that value back to the caller.
- `return value` ends the function and sends a value back to the calling code. The caller can store it, compare it, calculate with it, or pass it to another function.

```python
def calculate_total_with_print(unit_price, quantity):
    print(unit_price * quantity)

def calculate_total_with_return(unit_price, quantity):
    return unit_price * quantity

result_a = calculate_total_with_print(4.5, 3)
print("result_a is:", result_a)

result_b = calculate_total_with_return(4.5, 3)
print("result_b is:", result_b)
```

Output:

```text
13.5
result_a is: None
result_b is: 13.5
```

The first function displays `13.5`, but it has no explicit return statement. Therefore, `result_a` receives `None`. The second function returns `13.5`, so `result_b` stores that number.

A function with no explicit `return` automatically returns `None`. A bare `return` also returns `None`.

```python
def calculate_total_with_print(unit_price, quantity):
    print(unit_price * quantity)

result = calculate_total_with_print(4.5, 3)
print(result)
print(type(result))
```

Output:

```text
13.5
None
<class 'NoneType'>
```

This is expected Python behavior, not an error.

### Reusing a return value

```python
def calculate_total(unit_price, quantity):
    return unit_price * quantity

order_total = calculate_total(4.5, 3)
tax = order_total * 0.08
final_amount = order_total + tax

print(f"Order total: ${order_total:.2f}")
print(f"Final amount with tax: ${final_amount:.2f}")
```

Output:

```text
Order total: $13.50
Final amount with tax: $14.58
```

The returned number is stored in `order_total`, then used in further calculations. `:.2f` formats a number with two digits after the decimal point.

**Rule:** Use `print()` when the immediate goal is displaying something. Use `return` when the rest of the program needs the result.

## 5. Positional arguments

A positional argument is matched to a parameter by its position in the call. The order must match the function definition.

```python
def describe_student(name, score):
    print(f"{name} scored {score}.")

describe_student("Ada", 92)
describe_student(92, "Ada")
```

Output:

```text
Ada scored 92.
92 scored Ada.
```

In the first call, `"Ada"` is assigned to `name` and `92` to `score`. In the second call, Python still follows position, so `92` becomes `name` and `"Ada"` becomes `score`. Python does not know the intended meaning of those values, so this can produce incorrect output without raising an error.

## 6. Keyword arguments

A keyword argument names the parameter explicitly using `parameter=value`. This makes the call less dependent on order and often improves clarity.

```python
def describe_student(name, score):
    print(f"{name} scored {score}.")

describe_student(score=92, name="Ada")
describe_student("Ada", score=92)
```

Output:

```text
Ada scored 92.
Ada scored 92.
```

Both calls work. In the first, both arguments are matched by name. In the second, `"Ada"` is positional and `score=92` is a keyword argument.

**Ordering rule:** ordinary positional arguments must appear before keyword arguments. This is invalid:

```python
describe_student(name="Ada", 92)
```

It raises a `SyntaxError` because a positional argument follows a keyword argument. The exact wording of Python's error can vary by version.

## 7. Default parameter values

A parameter can have a default value. Python uses it when the caller does not supply that argument. The caller can still override the default.

```python
def build_greeting(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(build_greeting("Ada"))
print(build_greeting("Grace", "Welcome back"))
print(build_greeting("Alan", greeting="Good morning"))
```

Output:

```text
Hello, Ada!
Welcome back, Grace!
Good morning, Alan!
```

- `build_greeting("Ada")` uses the default `"Hello"`.
- `build_greeting("Grace", "Welcome back")` overrides it positionally.
- `build_greeting("Alan", greeting="Good morning")` overrides it by keyword.

A default is a fallback, not a fixed value. If a caller supplies a value, that supplied value takes priority.

Immutable values such as strings, numbers, Booleans, and `None` are generally safe defaults from the perspective of shared mutation. Python evaluates default expressions once, when the function is defined. That timing matters greatly for mutable defaults.

## 8. The mutable default argument trap

Do not use a mutable object such as a list `[]`, dictionary `{}`, or set as a default parameter when you expect a fresh object on every call.

```python
def add_item_unsafe(item, items=[]):
    items.append(item)
    return items

first_list = add_item_unsafe("apple")
print(first_list)

second_list = add_item_unsafe("banana")
print(second_list)
```

Output:

```text
['apple']
['apple', 'banana']
```

Why does this happen?

1. Python evaluates `items=[]` once when it executes the `def` statement.
2. That creates one list object.
3. Calls that omit `items` reuse that same list.
4. The first call appends `"apple"` to it.
5. The second call appends `"banana"` to the same object.
6. Both returned references point to the shared, mutated list.

This is an aliasing problem: two names can refer to the same mutable object.

### Safe pattern: use `None`

```python
def add_item_safe(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

first_list = add_item_safe("apple")
print(first_list)

second_list = add_item_safe("banana")
print(second_list)
```

Output:

```text
['apple']
['banana']
```

The default is the immutable value `None`. Each call without an `items` argument enters the guard, creates a new list inside the function, and appends to that independent list.

The function can also accept an existing list:

```python
existing_cart = ["milk"]
updated_cart = add_item_safe("eggs", existing_cart)
print(updated_cart)
```

Output:

```text
['milk', 'eggs']
```

Because `items` is not `None`, the function uses the supplied list and appends to it.

**Rule:** Avoid mutable defaults when you intend per-call fresh state. Use `None`, check `if items is None`, and create the mutable object inside the function.

## 9. Keyword-only parameters

A bare `*` in a function definition makes every parameter after it keyword-only. Such a parameter must be passed by name, never by position.

```python
def format_report(title, *, uppercase=False):
    if uppercase:
        return title.upper()
    return title

print(format_report("monthly summary"))
print(format_report("monthly summary", uppercase=True))
```

Output:

```text
monthly summary
MONTHLY SUMMARY
```

`title` can be positional or keyword-based. `uppercase` is after `*`, so it must be named.

This is invalid:

```python
format_report("monthly summary", True)
```

It raises a `TypeError` because `True` is supplied positionally for a keyword-only parameter. The exact error text can vary between Python versions.

Keyword-only options improve readability. `uppercase=True` communicates intent much better than an unexplained positional `True`.

## 10. Returning multiple values and unpacking

A function can return several comma-separated values. Python packs them into a tuple.

```python
def find_lowest_and_highest(numbers):
    return min(numbers), max(numbers)

result = find_lowest_and_highest([42, 7, 19, 88, 3])
print(result)
print(type(result))

lowest, highest = find_lowest_and_highest([42, 7, 19, 88, 3])
print(lowest, highest)
```

Output:

```text
(3, 88)
<class 'tuple'>
3 88
```

`return min(numbers), max(numbers)` returns one tuple containing two values. `result` stores the tuple. The second call unpacks the two tuple elements into `lowest` and `highest`.

This example requires a non-empty collection. `min()` and `max()` raise `ValueError` for an empty collection.

## 11. Docstrings

A **docstring** is a string placed as the first statement inside a function. It describes the function and is stored on the function object. You can inspect it using `function_name.__doc__` or `help(function_name)`.

```python
def calculate_discounted_price(price, discount_rate):
    """
    Calculate the price of an item after a discount is applied.

    price is the original price before any discount.
    discount_rate is the fraction to take off, such as 0.20 for 20 percent.
    Returns the discounted price as a number.
    """
    return price * (1 - discount_rate)

print(calculate_discounted_price(50, 0.20))
print(calculate_discounted_price.__doc__)
```

The first output is `40.0`. The next output is the function's description.

A useful beginner docstring should explain:

1. What the function does.
2. What its parameters mean.
3. What it returns.

Python removes the common indentation when storing a docstring, so the displayed text does not retain the code block's leading indentation. A clear plain-English docstring is enough at this stage.

---

## 12. All seven lesson examples, explained

### Example 1 — Greeting: `print` versus `return`

```python
def greet_user(name):
    print(f"Hello, {name}! Welcome back.")

def build_greeting(name):
    return f"Hello, {name}! Welcome back."

greet_result = greet_user("Ada")
print("greet_user gave back:", greet_result)

message = build_greeting("Ada")
print("build_greeting gave back:", message)
```

Output:

```text
Hello, Ada! Welcome back.
greet_user gave back: None
build_greeting gave back: Hello, Ada! Welcome back.
```

`greet_user` displays the message but returns no explicit value, so its caller receives `None`. `build_greeting` returns the message as a string; the caller stores it in `message`. Use `return` when the program must reuse the result.

### Example 2 — Order total and reuse

```python
def calculate_total(unit_price, quantity):
    return unit_price * quantity

order_total = calculate_total(12.50, 4)
shipping_fee = 5
final_amount = order_total + shipping_fee

print(f"Order total: ${order_total:.2f}")
print(f"Final amount (with shipping): ${final_amount:.2f}")
```

Output:

```text
Order total: $50.00
Final amount (with shipping): $55.00
```

The function performs one focused calculation and returns the product. The caller stores the result, adds shipping, and formats both amounts to two decimal places.

### Example 3 — Discount with a default argument

```python
def calculate_discounted_price(price, discount_rate=0.10):
    return price * (1 - discount_rate)

standard_price = calculate_discounted_price(80)
print(f"Standard discount price: ${standard_price:.2f}")

member_price = calculate_discounted_price(80, discount_rate=0.25)
print(f"Member discount price: ${member_price:.2f}")
```

Output:

```text
Standard discount price: $72.00
Member discount price: $60.00
```

The default discount is 10%, so the first call returns `80 * 0.90 = 72`. The second call overrides the rate with 25%, so it returns `80 * 0.75 = 60`.

### Example 4 — Validate a score range

```python
def is_score_valid(score, minimum=0, maximum=100):
    return score >= minimum and score <= maximum

scores_to_check = [85, -5, 100, 101]

for score in scores_to_check:
    if is_score_valid(score):
        print(score, "-> valid")
    else:
        print(score, "-> invalid")
```

Output:

```text
85 -> valid
-5 -> invalid
100 -> valid
101 -> invalid
```

The function returns a Boolean expression. A score is valid if it is at least the minimum and no greater than the maximum. The loop calls the same reusable rule for every score, and the caller uses the returned Boolean directly in an `if` condition.

### Example 5 — Return lowest and highest

```python
def find_lowest_and_highest(numbers):
    return min(numbers), max(numbers)

exam_scores = [72, 95, 68, 88, 91]
lowest, highest = find_lowest_and_highest(exam_scores)

print(f"Lowest score: {lowest}")
print(f"Highest score: {highest}")
```

Output:

```text
Lowest score: 68
Highest score: 95
```

The function returns a two-item tuple. The caller unpacks it into two meaningful names. The list must not be empty.

### Example 6 — Safely add an item to a list

```python
def add_item_safe(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

cart_one = add_item_safe("apples")
cart_two = add_item_safe("bread")

print("Cart one:", cart_one)
print("Cart two:", cart_two)

existing_cart = ["milk"]
updated_cart = add_item_safe("eggs", existing_cart)
print("Updated existing cart:", updated_cart)
```

Output:

```text
Cart one: ['apples']
Cart two: ['bread']
Updated existing cart: ['milk', 'eggs']
```

The `None` guard creates a fresh list for each call that omits `items`. If a caller supplies an existing list, the function appends to that list instead.

### Example 7 — Report formatting with keyword-only options and a docstring

```python
def format_report(title, *, uppercase=False, border=False):
    """
    Build a simple one-line report title.

    title is the text to display.
    uppercase, when True, converts the title to capital letters.
    border, when True, surrounds the title with dashes.
    Returns the formatted title as a string.
    """
    formatted_title = title
    if uppercase:
        formatted_title = formatted_title.upper()
    if border:
        formatted_title = f"--- {formatted_title} ---"
    return formatted_title

print(format_report("monthly summary"))
print(format_report("monthly summary", uppercase=True))
print(format_report("monthly summary", uppercase=True, border=True))
```

Output:

```text
monthly summary
MONTHLY SUMMARY
--- MONTHLY SUMMARY ---
```

`title` is an ordinary parameter. `uppercase` and `border` are keyword-only because they follow `*`. The function starts with the original title, optionally converts it to uppercase, optionally adds a dashed border, and returns the final string. Its docstring explains the purpose, options, and return value.

---

## 13. Common beginner mistakes

1. **Using `print()` when a value must be reused.** A printed value is not returned. Store a function's returned result instead.
2. **Forgetting the implicit `None`.** A function with no explicit return statement returns `None`.
3. **Swapping positional arguments.** Python follows order, not the meaning you intended.
4. **Putting a positional argument after a keyword argument.** This is a syntax error.
5. **Using a mutable default such as `[]` or `{}`.** The same object is reused across calls that omit the argument. Use the `None` guard pattern.
6. **Passing a keyword-only parameter positionally.** This raises `TypeError`; pass it by name.
7. **Writing an unhelpful docstring.** Explain the task, the inputs, and the returned result rather than merely repeating the function name.

## 14. Connection to Data Engineering and Applied AI

Functions are the building blocks of data pipelines and AI applications:

- A data validation function can accept a record and return `True` or `False`.
- A transformation function can accept a row and return a cleaned row.
- An aggregation function can accept values and return a total or summary.
- An agent tool can accept named arguments and return a result that the agent can reason about.
- Keyword-only options make configuration explicit.
- Docstrings can describe what a tool does and what its inputs and outputs mean.
- Mutable-default mistakes can cause state to leak between otherwise independent requests.

For production code, a function should have a clear responsibility, clear inputs, and a predictable return value. Returning data is usually more reusable than printing it.

## 15. Lesson completion checklist

You should be able to:

- Distinguish a function definition from a function call.
- Define a function using `def` and a meaningful name.
- Explain parameters versus arguments.
- Use `return` and explain how it differs from `print`.
- Explain why a function without an explicit return gives back `None`.
- Call functions with positional, keyword, and default arguments.
- Explain positional/keyword ordering rules.
- Avoid mutable default arguments using `None`.
- Define and call keyword-only parameters using `*`.
- Return multiple values and unpack the tuple.
- Write and inspect a useful docstring.

---

# Part B — Project-tree analysis and your current level

## 1. Exact location in the roadmap

The supplied project tree places this lesson at:

```text
Stage 1 — Programming & Computational Thinking/
└── 03-Control-Flow-Functions-Scope-and-Errors/
    ├── 01-conditionals-guards-and-boolean-logic.md
    ├── 02-for-while-loops-and-loop-control.md
    ├── 03-functions-parameters-and-return-values.md  <-- this lesson
    ├── 04-function-arguments-defaults-and-docstrings.md
    ├── 05-scope-lifetime-and-global-state.md
    ├── 06-pure-functions-and-side-effects.md
    ├── 07-exceptions-validation-and-useful-errors.md
    ├── README.md
    └── practice-questions.md
```

The lesson follows conditionals and loops. It uses their `if` statements and loops to demonstrate validation and repeated function calls. It also relies on earlier Stage 1 topics: tuples/unpacking and mutability/immutability.

## 2. Wider Stage 1 progression

The roadmap organizes the learning sequence as follows:

- **Module 01 — Computational Thinking and Program Design:** algorithms, expressions, input-process-output, sequence/selection/iteration/abstraction, decomposition, edge cases, dry runs, and state.
- **Module 02 — Python Core Language and Data Types:** Python syntax, variables, operators, strings, lists, tuples, dictionaries, sets, truthiness, and mutability.
- **Module 03 — Control Flow, Functions, Scope, and Errors:** conditionals, loops, functions, arguments, scope, side effects, validation, and exceptions.
- **Module 04 — Problem-Solving, Collections, and Algorithmic Habits:** searching, aggregation, grouping, sorting, Big-O, data-structure selection, comprehensions, recursion, and parsing.
- **Later modules:** files and CLI programs, packages and dependencies, testing/debugging, object-oriented design, production Python, and advanced Python topics.

The roadmap also defines four Stage 1 projects: Personal Expense Ledger CLI, Log Investigation and Reliability CLI, Data Quality and Transformation Pipeline, and Rule-Based Risk Review Engine. Functions will help divide each project into small, testable operations.

## 3. Your current learning level

Your recorded progress includes substantial work in Module 04: collection processing, grouping/deduplication/sorting, Big-O, data-structure selection, comprehensions, recursion, parsing/regular expressions, and a 35-question practice set. You have also worked through the earlier Module 03 lessons on conditionals and loops.

**Assessment: beginner progressing toward intermediate in Python engineering.** This function lesson is foundational, but it is not your first exposure to the programming constructs it uses. It formalizes a skill that you need before moving into scope, side effects, exceptions, testing, and larger projects.

### Exercise-solution scope

The six exercises are solved using only concepts taught in this lesson and its prerequisites:

- `def`, function calls, parameters, and arguments
- `return`, `print`, and `None`
- Positional, keyword, and default arguments
- `if` conditions and `None` guards
- Lists, basic arithmetic, and tuple unpacking
- Keyword-only parameters and docstrings

I do not introduce classes, file handling, pandas, external libraries, decorators, or advanced abstractions. The goal is to make the function mechanics explicit.

---

# Part C — All six exercise solutions

## Exercise 1 — Calculate the area of a rectangle

**Task:** Write `calculate_area(width, height)` to return the rectangle's area. Call it with different values and print the results.

### Solution

```python
def calculate_area(width, height):
    return width * height

area_one = calculate_area(5, 3)
area_two = calculate_area(8, 4)

print("Area one:", area_one)
print("Area two:", area_two)
```

Expected output:

```text
Area one: 15
Area two: 32
```

### Line-by-line explanation

1. `def calculate_area(width, height):` defines a function with two parameters.
2. `width` represents the rectangle's width; `height` represents its height.
3. `return width * height` multiplies the two values and sends the result back to the caller.
4. `area_one = calculate_area(5, 3)` calls the function with width 5 and height 3. The returned value, 15, is stored in `area_one`.
5. `area_two = calculate_area(8, 4)` calls the same function with different arguments. It returns 32.
6. The two `print()` statements display the stored results.

**Key concept:** One function can be reused with different arguments. Returning the area allows the caller to store or reuse the result.

## Exercise 2 — Compare positional and keyword arguments

**Task:** Write `greet(name, greeting)`. Call it once with positional arguments in the wrong order, once with the correct positional order, and once with keyword arguments. Compare the output.

### Solution

```python
def greet(name, greeting):
    return f"{greeting}, {name}!"

wrong_order = greet("Welcome", "Ada")
correct_order = greet("Ada", "Welcome")
keyword_call = greet(greeting="Welcome", name="Ada")

print("Wrong positional order:", wrong_order)
print("Correct positional order:", correct_order)
print("Keyword arguments:", keyword_call)
```

Expected output:

```text
Wrong positional order: Ada, Welcome!
Correct positional order: Welcome, Ada!
Keyword arguments: Welcome, Ada!
```

### Line-by-line explanation

1. `def greet(name, greeting):` defines two parameters. The first argument belongs to `name`; the second belongs to `greeting`.
2. `return f"{greeting}, {name}!"` builds and returns a greeting string.
3. `greet("Welcome", "Ada")` is intentionally in the wrong order. Python assigns `"Welcome"` to `name` and `"Ada"` to `greeting`, so the returned text is `"Ada, Welcome!"`.
4. `greet("Ada", "Welcome")` uses the correct positional order, so the result is `"Welcome, Ada!"`.
5. `greet(greeting="Welcome", name="Ada")` uses keyword arguments. The names determine the mapping, so their order in the call does not matter.
6. The print statements display the three returned strings.

**Key concept:** Positional arguments depend on order; keyword arguments depend on parameter names. Python cannot infer your intended meaning when positional values are swapped.

## Exercise 3 — Apply tax with a default rate

**Task:** Write `apply_tax(price, tax_rate=0.08)` to return the price including tax. Call it once with the default rate and once with a keyword override.

### Solution

```python
def apply_tax(price, tax_rate=0.08):
    return price * (1 + tax_rate)

default_total = apply_tax(100)
custom_total = apply_tax(100, tax_rate=0.18)

print(f"Total with default tax: ${default_total:.2f}")
print(f"Total with custom tax: ${custom_total:.2f}")
```

Expected output:

```text
Total with default tax: $108.00
Total with custom tax: $118.00
```

### Line-by-line explanation

1. `def apply_tax(price, tax_rate=0.08):` defines a function with a required price and a default tax rate of 8%.
2. `return price * (1 + tax_rate)` calculates the original price plus tax. For 8%, the multiplier is `1.08`.
3. `apply_tax(100)` supplies only the price. Python uses the default `tax_rate` of `0.08`, returning 108.
4. `apply_tax(100, tax_rate=0.18)` overrides the default with an 18% rate, returning 118.
5. The f-strings display the results with two decimal places.

**Key concept:** A default value is used only when the caller omits that argument. A supplied argument overrides it.

## Exercise 4 — Demonstrate and fix a mutable default argument

**Task:** Deliberately create `add_tag(tag, tags=[])`, call it three times without supplying `tags`, observe the shared-list bug, and fix it using `None`.

### Unsafe version — intentionally demonstrates the bug

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

### Why this happens

1. `tags=[]` creates one list when Python defines the function.
2. Each call omits `tags`, so each call reuses that same list object.
3. The first call appends `"python"`.
4. The second appends `"data"` to the existing list.
5. The third appends `"engineering"` to the same list.
6. All three variables refer to that same list, so printing any of them shows all three values.

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

### Line-by-line explanation of the safe version

1. `def add_tag_safe(tag, tags=None):` uses `None` as the default rather than a mutable list.
2. `if tags is None:` checks whether the caller omitted a list.
3. `tags = []` creates a new list inside this particular function call.
4. `tags.append(tag)` adds the supplied tag to that call's list.
5. `return tags` returns the resulting list.
6. Each of the three calls omits `tags`, so each call creates an independent list.
7. The print statements therefore show one tag per list.

**Key concept:** Use `None` as the default and construct a mutable object inside the function when a fresh object is required per call.

## Exercise 5 — Return total, count, and average

**Task:** Write `summarize_numbers(numbers)` that returns the total, count, and average as three values. Unpack them into separate variables. The input is guaranteed to be non-empty.

### Solution

```python
def summarize_numbers(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    return total, count, average

values = [10, 20, 30, 40]

total, count, average = summarize_numbers(values)

print("Total:", total)
print("Count:", count)
print("Average:", average)
```

Expected output:

```text
Total: 100
Count: 4
Average: 25.0
```

### Line-by-line explanation

1. `def summarize_numbers(numbers):` defines a function that accepts one collection.
2. `total = sum(numbers)` adds all numbers and stores the sum.
3. `count = len(numbers)` gets the number of items.
4. `average = total / count` divides the total by the count. The exercise guarantees a non-empty collection, so `count` is not zero.
5. `return total, count, average` returns the three values together. Python packs them into a tuple.
6. `values = [10, 20, 30, 40]` creates the input list.
7. `total, count, average = summarize_numbers(values)` calls the function and unpacks the returned tuple into three variables.
8. The print statements display each result separately.

**Key concept:** Multiple comma-separated return values are packed into a tuple and can be unpacked into meaningful variable names.

## Exercise 6 — Build a label with a keyword-only option

**Task:** Write `make_label(text, *, bold=False)` with a short docstring. Call it once using the default and once overriding `bold`.

### Solution

```python
def make_label(text, *, bold=False):
    """Return the label text, optionally surrounded by bold markers."""
    if bold:
        return f"**{text}**"
    return text

normal_label = make_label("Data Engineering")
bold_label = make_label("Data Engineering", bold=True)

print(normal_label)
print(bold_label)
```

Expected output:

```text
Data Engineering
**Data Engineering**
```

### Line-by-line explanation

1. `def make_label(text, *, bold=False):` defines a function with an ordinary `text` parameter and a keyword-only `bold` parameter.
2. The `*` means every parameter after it must be supplied by keyword.
3. The docstring describes what the function returns and the optional behavior.
4. `if bold:` checks whether bold formatting was requested.
5. `return f"**{text}**"` returns the text surrounded by Markdown bold markers when `bold` is true.
6. `return text` returns the unchanged text when `bold` is false.
7. `make_label("Data Engineering")` omits `bold`, so its default `False` is used.
8. `make_label("Data Engineering", bold=True)` overrides the default using the required keyword form.
9. The print statements display the two returned strings.

**Key concept:** Keyword-only parameters make optional behavior explicit and make function calls easier to understand.

---

# Part D — Quick revision sheet

| Concept | Remember |
|---|---|
| Define | `def function_name(...):` creates a function; it does not execute the body. |
| Call | `function_name(...)` executes the function. |
| Parameter | A named placeholder in the definition. |
| Argument | A value supplied in the call. |
| `print()` | Displays a value; does not return it to the caller. |
| `return` | Ends the function and sends a value back. |
| No explicit return | The function call evaluates to `None`. |
| Positional argument | Matched by order. |
| Keyword argument | Matched by parameter name. |
| Default value | Used when the caller omits that argument. |
| Mutable default | Avoid `[]`, `{}`, or `set()` as shared defaults; use `None` and create inside. |
| Keyword-only | Parameters after `*` must be passed by name. |
| Multiple return values | Packed into a tuple; can be unpacked. |
| Docstring | First string in the function body; describes purpose, inputs, and output. |

## Final self-check

Before moving to the next lesson, make sure you can write a small function from scratch, explain every argument it receives, identify what it returns, and predict what happens when a caller omits a defaulted argument. You should also be able to spot the shared mutable-default bug and correct it without copying the solution.
