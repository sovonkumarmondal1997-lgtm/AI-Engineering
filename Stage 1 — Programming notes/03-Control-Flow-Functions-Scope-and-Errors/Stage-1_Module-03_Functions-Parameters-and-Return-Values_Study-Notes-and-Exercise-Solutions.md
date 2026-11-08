# Stage 1 — Functions, Parameters, and Return Values
## Lesson Summary, Worked Examples, and Exercise Solutions

**Source lesson:** `03-functions-parameters-and-return-values.md`  
**Roadmap location:** Stage 1 — Programming & Computational Thinking → Control Flow, Functions, Scope and Errors

---

# Part 1 — Lesson Summary and Step-by-Step Teaching

## 1. Why functions matter

A function is a **named, reusable group of instructions**. Without functions, you may copy the same calculation or validation code into several places. That creates maintenance problems: if the logic changes or contains a bug, every copy must be found and fixed. A function puts the logic in one place, makes programs easier to read, and makes individual pieces easier to test.

There are two different actions:

- **Define:** `def` creates the function. It does not execute its body.
- **Call:** write the function name followed by parentheses to execute it.

```python
def greet_user():
    print("Hello! Welcome to the program.")

greet_user()
greet_user()
```

The `def` line creates `greet_user`; the two calls execute it twice and print the greeting twice. Use meaningful, action-oriented names such as `greet_user`, `calculate_total`, and `is_score_valid`.

## 2. Parameters and arguments

A **parameter** is the placeholder name in the function definition. An **argument** is the actual value supplied when calling it.

```python
def greet_by_name(name):
    print(f"Hello, {name}!")

greet_by_name("Ada")
greet_by_name("Grace")
```

`name` is the parameter; `"Ada"` and `"Grace"` are arguments. On each call, the supplied value is bound to the local parameter name.

A function can accept multiple parameters:

```python
def calculate_total(unit_price, quantity):
    print(unit_price * quantity)

calculate_total(4.5, 3)
```

`4.5` is matched to `unit_price`, and `3` to `quantity`; output is `13.5`.

## 3. `print()` versus `return`

This is the most important distinction in the lesson:

- `print(value)` displays a value for a person to see.
- `return value` sends a value back to the calling code so the program can store, calculate with, or otherwise reuse it. `return` immediately ends that function call.

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

The first function prints `13.5` but returns nothing explicitly, so Python returns `None` automatically. The second returns `13.5`, which is stored in `result_b`. A plain `return` also returns `None`.

A returned value can be reused:

```python
def calculate_total(unit_price, quantity):
    return unit_price * quantity

order_total = calculate_total(4.5, 3)
tax = order_total * 0.08
final_amount = order_total + tax

print(f"Order total: ${order_total:.2f}")
print(f"Final amount with tax: ${final_amount:.2f}")
```

Output: `$13.50` and `$14.58`. The function returns a number, allowing the rest of the program to calculate tax and the final amount.

## 4. Positional and keyword arguments

**Positional arguments** are matched by order. Order matters:

```python
def describe_student(name, score):
    print(f"{name} scored {score}.")

describe_student("Ada", 92)
describe_student(92, "Ada")
```

The first prints `Ada scored 92.`; the second prints `92 scored Ada.`. Python matches by position and cannot infer the intended meaning.

**Keyword arguments** name the parameter, so their order in the call does not matter:

```python
describe_student(score=92, name="Ada")
describe_student("Ada", score=92)
```

Both print `Ada scored 92.`. You may mix positional and keyword arguments, but ordinary positional arguments must come before keyword arguments. `describe_student(name="Ada", 92)` raises `SyntaxError`.

## 5. Default arguments

A default value is used when the caller omits that argument. The caller can override it:

```python
def build_greeting(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(build_greeting("Ada"))
print(build_greeting("Grace", "Welcome back"))
print(build_greeting("Alan", greeting="Good morning"))
```

Output: `Hello, Ada!`, `Welcome back, Grace!`, `Good morning, Alan!`. The default `"Hello"` is a fallback, not a fixed rule. Defaults are evaluated once when the function is defined. Immutable defaults such as strings, numbers, Booleans and `None` do not have the shared-mutation problem described next.

## 6. Mutable default arguments: the common trap

Do not use a mutable object such as `[]`, `{}` or `set()` directly as a default. The default list is created once at function definition time, so calls that omit the argument share the same list:

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

Both variables refer to the same list object. This is an aliasing bug: the second call changes the list returned by the first call too.

Use `None` as the default and create a fresh list inside the function:

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

Output: `['apple']` then `['banana']`. The `is None` guard creates a new list for each call that omits `items`. If a caller supplies an existing list, the function uses and mutates that supplied list.

## 7. Keyword-only parameters

A standalone `*` in a function definition makes every parameter after it **keyword-only**. Such parameters must be passed by name:

```python
def format_report(title, *, uppercase=False):
    if uppercase:
        return title.upper()
    return title

print(format_report("monthly summary"))
print(format_report("monthly summary", uppercase=True))
```

Output: `monthly summary` and `MONTHLY SUMMARY`. `title` can be positional or keyword; `uppercase` must be written as `uppercase=True`. Passing `True` positionally raises `TypeError`. Naming options makes calls clearer than passing unexplained values such as bare `True`.

## 8. Returning multiple values

Comma-separated values in a `return` are packed into a tuple. The caller can unpack that tuple:

```python
def find_lowest_and_highest(numbers):
    return min(numbers), max(numbers)

result = find_lowest_and_highest([42, 7, 19, 88, 3])
print(result)
print(type(result))

lowest, highest = find_lowest_and_highest([42, 7, 19, 88, 3])
print(lowest, highest)
```

Output: `(3, 88)`, `<class 'tuple'>`, then `3 88`. Unpacking gives the returned values clear names. This example requires a non-empty collection; `min()` and `max()` raise `ValueError` for an empty one.

## 9. Docstrings

A **docstring** is the first string inside a function. It documents the function and is available through `function.__doc__` or `help()`.

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

The calculation prints `40.0`; the second print displays the docstring. Python removes the shared indentation when exposing a docstring. A useful docstring explains what the function does, what its parameters mean, and what it returns.

## 10. All seven lesson examples

1. **Greeting:** `greet_user(name)` prints a greeting; `build_greeting(name)` returns the same text. Assigning the first call stores `None`; assigning the second stores the message. Output includes the greeting, `greet_user gave back: None`, and the returned greeting.
2. **Order total:** `calculate_total(unit_price, quantity)` returns the multiplication. With `12.50` and `4`, the order total is `$50.00`; adding a `$5` shipping fee gives `$55.00`.
3. **Discount default:** `calculate_discounted_price(price, discount_rate=0.10)` returns `price * (1 - discount_rate)`. Price 80 gives `$72.00` at the default 10%; overriding with `discount_rate=0.25` gives `$60.00`.
4. **Score validation:** `is_score_valid(score, minimum=0, maximum=100)` returns `score >= minimum and score <= maximum`. A loop checks `[85, -5, 100, 101]`; outputs valid, invalid, valid, invalid respectively.
5. **Lowest/highest:** return `min(numbers), max(numbers)` and unpack into `lowest, highest`. For `[72, 95, 68, 88, 91]`, outputs are 68 and 95.
6. **Safe list:** `add_item_safe(item, items=None)` creates a new list only when `items is None`, appends the item and returns the list. Separate calls produce `['apples']` and `['bread']`; passing `['milk']` returns `['milk', 'eggs']`.
7. **Report formatting:** `format_report(title, *, uppercase=False, border=False)` uses a docstring, conditionally applies `.upper()` and surrounds the result with dashes. Calls produce `monthly summary`, `MONTHLY SUMMARY`, and `--- MONTHLY SUMMARY ---`.

## 11. Common mistakes and why this matters later

Avoid confusing `print` with `return`; forgetting that no explicit return means `None`; swapping positional arguments; placing a positional argument after a keyword; using mutable defaults; passing keyword-only options positionally; and writing docstrings that merely repeat the function name without explaining inputs and output.

In later data and AI engineering, functions can implement reusable processing steps and agent tools. Tools need to **return** results for the calling system to use. A shared mutable default can accidentally mix state between unrelated calls. Docstrings can help people and, depending on the framework, can contribute to descriptions an AI model reads when deciding how to call a tool.

---

# Part 2 — Current-Level Assessment and Exercise Solutions

## Learning-level assessment

The roadmap context available from your Stage 1 project tree places this lesson after computational thinking, Python core types, conditionals/Boolean logic, and loops. The lesson itself lists those topics plus tuples/unpacking and mutability/immutability as prerequisites. This is a sensible progression: functions now combine values, decisions, iteration and reusable logic.

Your current level is **beginner progressing toward intermediate**. You should be able to write basic loops and conditionals; the next skill is to package those operations into small functions with clear inputs and returned outputs. The solutions below stay within the lesson's scope: `def`, parameters, arguments, `return`, defaults, `None` guards, keyword-only parameters, tuples/unpacking, conditionals and basic loops. The roadmap file itself was not re-uploaded with this lesson, so this assessment uses the Stage 1 structure available in our prior roadmap context rather than claiming a fresh audit of every project-tree file.

## Exercise 1 — Rectangle area

**Task:** Write `calculate_area(width, height)`, return the area, call it with different values and print results.

```python
def calculate_area(width, height):
    return width * height

area_one = calculate_area(5, 4)
area_two = calculate_area(3.5, 2)

print(area_one)
print(area_two)
```

**Line by line:**
1. `def` defines a function named `calculate_area`.
2. `width` and `height` are its two parameters.
3. `return width * height` multiplies them and sends the result to the caller.
4. The first call supplies 5 and 4; its returned value, 20, is stored in `area_one`.
5. The second call supplies 3.5 and 2; 7.0 is stored in `area_two`.
6–7. `print()` displays the returned values.

Output: `20` and `7.0`.

## Exercise 2 — Positional order and keyword arguments

**Task:** Define `greet(name, greeting)` and compare wrong positional order, correct positional order and keyword arguments.

```python
def greet(name, greeting):
    return f"{greeting}, {name}!"

print(greet("Hello", "Ada"))
print(greet("Ada", "Hello"))
print(greet(greeting="Hello", name="Ada"))
```

**Line by line:**
1. The function has `name` first and `greeting` second.
2. The f-string builds and returns the greeting.
3. `"Hello"` is incorrectly bound to `name`, and `"Ada"` to `greeting`; output is `Ada, Hello!`.
4. Arguments are now in the intended order; output is `Hello, Ada!`.
5. Keywords identify each parameter explicitly, so their order does not matter; output is `Hello, Ada!`.

This demonstrates that Python follows the parameter order for positional arguments, not the meaning you intended.

## Exercise 3 — Apply tax with a default rate

**Task:** Use an 8% default tax rate, then override it with a keyword argument.

```python
def apply_tax(price, tax_rate=0.08):
    return price * (1 + tax_rate)

standard_total = apply_tax(100)
special_total = apply_tax(100, tax_rate=0.05)

print(standard_total)
print(special_total)
```

**Line by line:**
1. `price` is required; `tax_rate` defaults to `0.08`.
2. The function returns the price multiplied by one plus the tax rate.
3. Calling with only 100 uses 8%, returning 108.0.
4. The keyword argument overrides the default with 5%, returning 105.0.
5–6. Print both returned values.

Output: `108.0` and `105.0`.

## Exercise 4 — Demonstrate and fix a mutable default

**Task:** Call an unsafe `add_tag` three times without supplying `tags`, observe the shared list, then fix it with `None`.

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

**Line by line:**
1. Defines the unsafe function with one default list, created once.
2. Appends the new tag to that shared list.
3. Returns the same list object.
4–6. Each call adds to the same list, so outputs grow cumulatively: `['python']`, then `['python', 'data']`, then `['python', 'data', 'engineering']`.
7. Defines the safe version with immutable `None` as the default.
8. Checks whether the caller omitted `tags`.
9. Creates a new list for that call if needed.
10. Appends the tag.
11. Returns the list.
12–14. Each call creates its own list, so each output contains only its own tag.

## Exercise 5 — Return total, count and average

**Task:** Return three values together and unpack them. The input is assumed non-empty.

```python
def summarize_numbers(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    return total, count, average

values = [10, 20, 30, 40]
total, count, average = summarize_numbers(values)

print(total)
print(count)
print(average)
```

**Line by line:**
1. Defines a function that receives a collection of numbers.
2. `sum()` calculates the total: 100.
3. `len()` counts the items: 4.
4. Dividing total by count calculates the average: 25.0.
5. The comma-separated return values are packed into a tuple.
6. `values` is the sample input.
7. The returned three-item tuple is unpacked into three named variables.
8–10. Print the total, count and average.

Output: `100`, `4`, `25.0`. The non-empty-input assumption matters because dividing by zero would fail for an empty collection.

## Exercise 6 — Keyword-only `bold` and a docstring

**Task:** Define `make_label(text, *, bold=False)`, document it and call it with the default and with `bold=True`.

```python
def make_label(text, *, bold=False):
    """Return the label text, optionally surrounded by bold markers."""
    if bold:
        return f"**{text}**"
    return text

print(make_label("Important"))
print(make_label("Important", bold=True))
```

**Line by line:**
1. Defines the function. `text` is an ordinary parameter; `bold` is keyword-only because it follows `*`, and defaults to `False`.
2. The docstring explains the function's purpose and option.
3. Checks whether bold formatting was requested.
4. If true, returns the text surrounded by `**` markers.
5. Otherwise, returns the original text.
6. Calls with the default `False`, producing `Important`.
7. Calls with `bold=True`, producing `**Important**`.

The `**` markers are plain text here; the function is building a label string, not applying formatting to a user interface.

---

## Completion checklist

- [ ] I can distinguish a function definition from a function call.
- [ ] I can distinguish parameters from arguments.
- [ ] I understand why `return` is different from `print()` and why no explicit return produces `None`.
- [ ] I can use positional, keyword, default and keyword-only arguments correctly.
- [ ] I can explain and prevent mutable-default aliasing with the `None` pattern.
- [ ] I can return multiple values and unpack the tuple.
- [ ] I can write a useful docstring.
- [ ] I can complete all six exercises without copying the solutions.

**Learning boundary:** These solutions do not introduce later topics such as `*args`, `**kwargs`, recursion, decorators, type annotations, exceptions, classes, comprehensions or external libraries. Wait until those topics appear in your roadmap before adding them to this lesson's exercises.
