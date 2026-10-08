# Functions, Parameters, and Return Values

## Why functions matter

Every program you have written so far has been one long list of
instructions, read from top to bottom. That works for small programs, but
it breaks down quickly once the same few steps need to happen in several
places — greeting a user, calculating a total, checking a score. Copying
and pasting the same lines everywhere is fragile: if you ever find a bug
in that logic, or need to change it, you have to find and fix every copy,
and it is easy to miss one. A **function** solves this by giving a group
of instructions a name, once, so it can be reused anywhere, as many times
as needed, and fixed in exactly one place if it is ever wrong. Functions
are also how you make a large problem manageable: instead of one huge
block of code, you build a program out of many small, clearly named
pieces, each doing one understandable job.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what a function is, and the difference between **defining** a
  function and **calling** it.
- Write a function using `def`, with a clear, meaningful name, and call
  it correctly.
- Use **parameters** to accept input into a function, and pass matching
  **arguments** when calling it.
- Use `return` to send a result back to the caller, and explain exactly
  how `return` differs from `print`.
- Explain why a function with no explicit `return` gives back `None`.
- Call a function using **positional arguments** and **keyword
  arguments**, and explain the ordering rules for each.
- Give a parameter a **default value**, override it when needed, and
  explain why a mutable default value (like `[]`) is dangerous — and how
  to avoid that danger using `None`.
- Define **keyword-only** parameters using `*`, and explain why they can
  make a function call clearer.
- Return more than one value from a function, and unpack the result into
  separate variables.
- Write a short, useful **docstring** describing what a function does.

## Prerequisites

- [Conditionals, Guards, and Boolean Logic](01-conditionals-guards-and-boolean-logic.md) —
  this lesson's validation examples use `if`/`elif`/`else` and the
  `is None` guard pattern taught there.
- [For/While Loops and Loop Control](02-for-while-loops-and-loop-control.md) —
  a couple of examples loop over a list of inputs to call a function
  several times.
- [Sequence, Selection, Iteration, and Abstraction](../01-Computational-Thinking-and-Program-Design/04-sequence-selection-iteration-and-abstraction.md) —
  your first, informal look at `def`, parameters, and `return`; this
  lesson gives all of it a complete, formal treatment.
- [Tuples and Unpacking](../02-Python-Core-Language-and-Data-Types/06-tuples-and-unpacking.md) —
  returning multiple values from a function relies directly on tuple
  packing and unpacking, taught fully there.
- [Mutability and Immutability](../02-Python-Core-Language-and-Data-Types/10-mutability-and-immutability.md) —
  the "labels on boxes" model that explains exactly why a mutable default
  argument is dangerous.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Function** | A named, reusable group of instructions that can be run whenever it is needed. |
| **Function definition** | The `def` block that creates a function and describes what it does; running the `def` statement creates the function but does not run its body. |
| **Function call** | The line that actually runs a function's instructions, written as the function's name followed by parentheses. |
| **Parameter** | A name listed inside the parentheses in the function's definition; during a call, the supplied argument is bound to it. |
| **Argument** | The actual value supplied for a parameter when a function is called. |
| **`return`** | A statement that ends a function immediately and sends a value back to whatever called it. |
| **`None`** | The value a function gives back automatically if it has no `return` statement, or a plain `return` with nothing after it. |
| **Positional argument** | An argument matched to a parameter purely by its position/order in the function call. |
| **Keyword argument** | An argument passed by explicitly naming the parameter it belongs to, such as `score=92`. |
| **Default value** | A value a parameter uses automatically if the caller does not supply an argument for it. |
| **Keyword-only parameter** | A parameter that can only ever be supplied as a keyword argument, never positionally. |
| **Docstring** | A short piece of text, written as the very first line(s) inside a function, describing what it does. |

## Step-by-step explanation

### 1. What a function is

A **function** is a named, reusable group of instructions. Instead of
retyping the same steps everywhere they are needed, you write them once,
give them a name, and run that name whenever you need those steps to
happen again. This matters for three concrete reasons:

- **Less repetition.** The instructions exist in exactly one place, no
  matter how many times they are used.
- **Easier to read.** A well-named function call, like
  `calculate_total(price, quantity)`, tells a reader *what* is happening
  without forcing them to read every detail of *how* it happens.
- **Easier to test and change.** If the logic inside a function turns out
  to be wrong, there is exactly one place to fix it, and every place that
  uses the function is automatically fixed too.

There are two completely separate steps involved: **defining** a function
(writing down its instructions and giving them a name) and **calling** it
(actually running those instructions). Running a `def` statement creates
the function and gives it its name, but it does not run the function's
body — the body runs only when the function is called.

### 2. Basic function syntax

A function is defined with the **`def`** keyword, followed by the
**function name**, **parentheses**, and a **colon**, with the function's
instructions **indented** underneath — exactly the same indentation rule
that `if` and `for` already use.

```python
def greet_user():
    print("Hello! Welcome to the program.")

greet_user()
greet_user()
```

```text
Hello! Welcome to the program.
Hello! Welcome to the program.
```

`def greet_user():` defines a function named `greet_user` that takes no
input. Nothing is printed yet at this point — running the `def` creates
the function, but its body has not run. `greet_user()` — the name followed by parentheses — is
the **function call**: it actually runs the indented block. Calling it
twice runs the same instructions twice, printing the same message each
time, without the message ever being retyped.

**Meaningful function names:** a function's name should describe the
action it performs, usually starting with a verb — `greet_user`,
`calculate_total`, `is_score_valid` — so a reader can guess what it does
without reading its body. This mirrors the meaningful-variable-name habit
from
[Variables, Basic Types, and None](../02-Python-Core-Language-and-Data-Types/02-variables-basic-types-and-none.md),
applied to actions instead of values.

### 3. Parameters and arguments

A **parameter** is a name listed inside a function's parentheses when it
is *defined*. An **argument** is the actual value supplied for that
parameter when the function is *called*; during the call, the argument is
bound to the parameter's name. The words
are easy to mix up, but the distinction matters: a parameter is part of
the *recipe*; an argument is a real ingredient you hand over when you
actually cook it.

```python
def greet_by_name(name):
    print(f"Hello, {name}!")

greet_by_name("Ada")
greet_by_name("Grace")
```

```text
Hello, Ada!
Hello, Grace!
```

`name` is the parameter — a name written in the function's definition
that becomes a local name inside the function while a call runs.
`"Ada"` and `"Grace"` are arguments — the real values bound to `name` on
each separate call. A
function can take more than one parameter, separated by commas:

```python
def calculate_total(unit_price, quantity):
    print(unit_price * quantity)

calculate_total(4.5, 3)
```

```text
13.5
```

`unit_price` and `quantity` are two separate parameters; `4.5` and `3`
are the two matching arguments, supplied in the same order the
parameters were listed.

### 4. Return values

So far, these functions only `print(...)` their result — they display it,
but do not hand it back to the rest of the program. **`return`** is
different: it ends the function immediately and sends a value back to
whatever called it, so that value can be stored or used later.

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

```text
13.5
result_a is: None
result_b is: 13.5
```

`calculate_total_with_print` only *displays* `13.5` — it never sends
anything back, so `result_a = calculate_total_with_print(4.5, 3)` stores
**`None`**, Python's "nothing was returned" value, not `13.5`.
`calculate_total_with_return` uses `return` instead, so `result_b`
correctly stores `13.5`, ready to be used again. **This is the single
most important distinction in this lesson:** `print()` only shows a
value on the screen, for a human to look at; `return` hands a value back
into the program itself, so *other code* can keep working with it.

**A function with no `return` gives back `None`.** This is not an error
— it is Python's consistent rule that *every* function call produces a
value, even one that never explicitly says what to hand back:

```python
def calculate_total_with_print(unit_price, quantity):
    print(unit_price * quantity)

result = calculate_total_with_print(4.5, 3)
print(result)
print(type(result))
```

```text
13.5
None
<class 'NoneType'>
```

**Storing and reusing a returned value:** once a function returns
something useful, you can store it in a variable and use it in further
calculations, exactly like any other value:

```python
def calculate_total(unit_price, quantity):
    return unit_price * quantity

order_total = calculate_total(4.5, 3)
tax = order_total * 0.08
final_amount = order_total + tax

print(f"Order total: ${order_total:.2f}")
print(f"Final amount with tax: ${final_amount:.2f}")
```

```text
Order total: $13.50
Final amount with tax: $14.58
```

`order_total` holds the real number `calculate_total` returned, so it can
be multiplied, added to, and reused freely in the lines that follow —
this would be impossible if `calculate_total` had only `print`ed its
result.

### 5. Positional arguments

An argument passed by **position** is matched to whichever parameter sits
in the same position in the function's definition. **Order matters:**

```python
def describe_student(name, score):
    print(f"{name} scored {score}.")

describe_student("Ada", 92)
describe_student(92, "Ada")
```

```text
Ada scored 92.
92 scored Ada.
```

The first call matches `"Ada"` to `name` and `92` to `score`, exactly as
intended. The second call swaps the order: Python does not know that
`describe_student` "means" a name first — it simply matches `92` to
`name` and `"Ada"` to `score`, in position order, producing the
nonsensical `92 scored Ada.`. Python does not detect this kind of mistake
for you; the values are the right *types* to be accepted, just in the
wrong *meaning* — a strong reason to keep parameter order easy to
remember, or to use keyword arguments, covered next.

### 6. Keyword arguments

A **keyword argument** names the parameter it belongs to directly in the
call, using `parameter_name=value`. This removes any dependence on
order, and often makes a call easier to read:

```python
def describe_student(name, score):
    print(f"{name} scored {score}.")

describe_student(score=92, name="Ada")
describe_student("Ada", score=92)
```

```text
Ada scored 92.
Ada scored 92.
```

The first call names both arguments, so their order in the call no
longer matters — Python matches each one by name instead of by position,
and both calls above are correct. The second call **mixes** a positional
argument (`"Ada"`) with a keyword argument (`score=92`) — this is
allowed, as long as every positional argument comes *before* every
keyword argument.

**Ordinary positional arguments cannot follow keyword arguments.** Once a
call has supplied a keyword argument, another ordinary positional
argument cannot come after it:

```text
describe_student(name="Ada", 92)
```

```text
SyntaxError: positional argument follows keyword argument
```

This call raises a `SyntaxError` because an ordinary positional argument
cannot follow a keyword argument. The exact wording of the message can
vary between Python versions; the exception type and the rule are what
matter.

### 7. Default arguments

A parameter can be given a **default value** in the function definition,
used automatically whenever the caller does not supply an argument for
it. Default values are useful whenever a parameter has one sensible,
common value most callers will want, while still allowing it to be
overridden when needed.

```python
def build_greeting(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(build_greeting("Ada"))
print(build_greeting("Grace", "Welcome back"))
print(build_greeting("Alan", greeting="Good morning"))
```

```text
Hello, Ada!
Welcome back, Grace!
Good morning, Alan!
```

`build_greeting("Ada")` supplies no second argument, so `greeting`
automatically uses its default, `"Hello"`. The next two calls each
**override** that default, once positionally and once with a keyword
argument, showing that a default is only ever used when the caller stays
silent about that parameter — supplying any value, in any valid way,
always takes priority over the default.

**Keep defaults to safe, immutable values.** A default of a `str`, a
number, a `bool`, or `None` — all immutable, as you learned in
[Mutability and Immutability](../02-Python-Core-Language-and-Data-Types/10-mutability-and-immutability.md) —
does not have the mutation-sharing problem that mutable defaults have,
because that default value cannot be changed in place. (Defaults are still
evaluated once, when the function is defined.) Section 8 shows exactly what goes wrong when a
default value is *mutable* instead.

### 8. The mutable default argument warning

**This is one of the most famous beginner traps in Python.** Using a
mutable value, such as `[]`, as a default argument does **not** create a
fresh, empty list every time the function is called with no argument —
it creates **one single list, only once**, when the function is defined,
and every call that relies on the default silently **shares that same
list**:

```python
def add_item_unsafe(item, items=[]):
    items.append(item)
    return items

first_list = add_item_unsafe("apple")
print(first_list)

second_list = add_item_unsafe("banana")
print(second_list)
```

```text
['apple']
['apple', 'banana']
```

This looks deeply wrong, and it is: `second_list` was clearly meant to
start fresh, with just `"banana"` — instead, it shows both items, because
`first_list` and `second_list` are secretly **the exact same list
object**, mutated a second time. This is precisely the **aliasing**
danger from
[Lists: Mutation, Copying, and Aliasing](../02-Python-Core-Language-and-Data-Types/05-lists-mutation-copying-and-aliasing.md):
`items=[]` creates one list when `def` runs, and every call that skips
the `items` argument reuses that *same* list, not a new one — the
default value is evaluated exactly **once**, not once per call.

**The safe pattern: use `None` as the default, and create a new list
inside the function.** Since `None` is immutable, it can safely be reused
as a default forever — the actual, real list is only created fresh each
time the function body runs:

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

```text
['apple']
['banana']
```

`if items is None: items = []` (the guard pattern from
[Conditionals, Guards, and Boolean Logic](01-conditionals-guards-and-boolean-logic.md))
builds a genuinely **new**, independent list every single time the
function is called without an `items` argument, so nothing is ever
accidentally shared between separate calls. **The rule to remember: never
use a mutable value — `[]`, `{}`, or `set()` — directly as a default
argument. Use `None`, and build the real mutable value inside the
function body instead.**

### 9. Keyword-only arguments

Placing a lone **`*`** in a function's parameter list marks every
parameter *after* it as **keyword-only** — it can never be supplied
positionally, only by name. This is useful for options that are easy to
misread if just left as bare values in a call.

```python
def format_report(title, *, uppercase=False):
    if uppercase:
        return title.upper()
    return title

print(format_report("monthly summary"))
print(format_report("monthly summary", uppercase=True))
```

```text
monthly summary
MONTHLY SUMMARY
```

`title` remains an ordinary parameter, positional or keyword. `uppercase`
comes after the `*`, so it **must** be passed by name if it is passed at
all:

```text
print(format_report("monthly summary", True))
```

```text
TypeError: format_report() takes 1 positional argument but 2 were given
```

Here `True` is supplied positionally, but `uppercase` is keyword-only, so
Python rejects the call with a `TypeError`: `uppercase` must be supplied
by name. (The exact message text can vary between Python versions.) A
bare `True` is also unclear to a human reader, while `uppercase=True`
states its purpose directly, which is exactly why keyword-only parameters
are worth using for options like this.

### 10. Returning multiple values

A `return` statement can send back several values at once, separated by
commas — Python **packs** them into a single **tuple**, exactly as
covered in
[Tuples and Unpacking](../02-Python-Core-Language-and-Data-Types/06-tuples-and-unpacking.md).

```python
def find_lowest_and_highest(numbers):
    return min(numbers), max(numbers)

result = find_lowest_and_highest([42, 7, 19, 88, 3])
print(result)
print(type(result))

lowest, highest = find_lowest_and_highest([42, 7, 19, 88, 3])
print(lowest, highest)
```

```text
(3, 88)
<class 'tuple'>
3 88
```

`return min(numbers), max(numbers)` packs two values into one two-item
tuple behind the scenes. Capturing the whole call in one variable
(`result`) shows the raw tuple, `(3, 88)`. **Unpacking** the same call
directly into `lowest, highest` — the exact tuple-unpacking pattern from
Module 1.2 — immediately gives each value its own clear name, which is
almost always clearer to read than working with an unnamed tuple
afterward.

### 11. Docstrings

A **docstring** is a string written as the very first line (or lines)
inside a function's body, describing what the function does. Python
treats it specially: it is stored on the function itself and can be read
back later, using `.__doc__` or the built-in `help()`.

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

```text
40.0

Calculate the price of an item after a discount is applied.

price is the original price before any discount.
discount_rate is the fraction to take off, such as 0.20 for 20 percent.
Returns the discounted price as a number.
```

Notice that `.__doc__` prints the description without the extra leading
spaces the docstring appeared to have in the source code — modern Python
automatically removes that shared indentation, so you do not need to
worry about it when writing or reading a docstring back.

A good, simple docstring states three things in plain English: **what**
the function does, **what its parameters mean**, and **what it
returns** — exactly as shown above. There is no special format required
at this stage; a clear, short, plain-English description is enough. Not
every tiny function needs one, but any function whose purpose is not
completely obvious from its name benefits from a short docstring.

## Examples

### Example 1 — Greeting a user: `print` versus `return`

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

**Plain-English explanation:**

- `greet_user` and `build_greeting` both build the exact same message,
  but `greet_user` only `print`s it, while `build_greeting` `return`s it.
- Calling `greet_user("Ada")` immediately displays the greeting on the
  screen, as a side effect of running the function — but the function
  itself hands back `None`, since it has no `return` statement, so
  `greet_result` stores `None`.
- Calling `build_greeting("Ada")` displays nothing by itself, but hands
  the whole message back as a real value, which `message` correctly
  stores, ready to be printed, combined with other text, or used however
  the rest of the program needs.
- This is the core lesson of this whole topic: choose `print()` when a
  human just needs to *see* something right now, and `return` when the
  *program* needs to keep using the result afterward.

**Expected output:**

```text
Hello, Ada! Welcome back.
greet_user gave back: None
build_greeting gave back: Hello, Ada! Welcome back.
```

### Example 2 — Calculating an order total and reusing the result

```python
def calculate_total(unit_price, quantity):
    return unit_price * quantity

order_total = calculate_total(12.50, 4)
shipping_fee = 5
final_amount = order_total + shipping_fee

print(f"Order total: ${order_total:.2f}")
print(f"Final amount (with shipping): ${final_amount:.2f}")
```

**Plain-English explanation:**

- `calculate_total` takes two parameters, `unit_price` and `quantity`,
  and returns their product — a single, focused job.
- `calculate_total(12.50, 4)` matches `12.50` to `unit_price` and `4` to
  `quantity` by position, returning `50.0`, which `order_total` stores.
- Because the function *returned* a usable number rather than only
  printing it, the rest of the program can immediately reuse
  `order_total` in a further calculation — adding `shipping_fee` to
  produce `final_amount` — without ever needing to recompute the
  multiplication.

**Expected output:**

```text
Order total: $50.00
Final amount (with shipping): $55.00
```

### Example 3 — Calculating a discount with a default argument

```python
def calculate_discounted_price(price, discount_rate=0.10):
    return price * (1 - discount_rate)

standard_price = calculate_discounted_price(80)
print(f"Standard discount price: ${standard_price:.2f}")

member_price = calculate_discounted_price(80, discount_rate=0.25)
print(f"Member discount price: ${member_price:.2f}")
```

**Plain-English explanation:**

- `discount_rate=0.10` gives every ordinary customer a sensible default
  10% discount, without every single call needing to state it
  explicitly.
- `calculate_discounted_price(80)` supplies only `price`, so
  `discount_rate` automatically uses its default, `0.10`, giving `$72.00`.
- `calculate_discounted_price(80, discount_rate=0.25)` explicitly
  overrides the default with a keyword argument for a member discount,
  giving `$60.00` instead — proving the default is only ever a fallback,
  never a fixed rule.

**Expected output:**

```text
Standard discount price: $72.00
Member discount price: $60.00
```

### Example 4 — Validating a score range

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

**Plain-English explanation:**

- `is_score_valid` takes a `score` and two default-valued boundaries,
  `minimum` and `maximum`, and directly returns the result of a Boolean
  comparison — there is no need for an `if`/`else` inside the function,
  since `score >= minimum and score <= maximum` already evaluates to
  `True` or `False`.
- The `for` loop (from
  [For/While Loops and Loop Control](02-for-while-loops-and-loop-control.md))
  calls `is_score_valid(score)` once per score, reusing the exact same
  validation rule for every one, instead of repeating the comparison four
  times by hand.
- `if is_score_valid(score):` uses the function's returned `bool` value
  directly as the condition — a genuine, real function *return value*
  driving a decision in the calling code, tying this lesson directly back
  to [Conditionals, Guards, and Boolean Logic](01-conditionals-guards-and-boolean-logic.md).

**Expected output:**

```text
85 -> valid
-5 -> invalid
100 -> valid
101 -> invalid
```

### Example 5 — Returning the lowest and highest values

```python
def find_lowest_and_highest(numbers):
    return min(numbers), max(numbers)

exam_scores = [72, 95, 68, 88, 91]
lowest, highest = find_lowest_and_highest(exam_scores)

print(f"Lowest score: {lowest}")
print(f"Highest score: {highest}")
```

**Plain-English explanation:**

- `find_lowest_and_highest` computes two related results from one list
  and returns them together as a packed tuple, `(lowest, highest)`.
- `lowest, highest = find_lowest_and_highest(exam_scores)` immediately
  unpacks that tuple into two clearly named variables at the call site —
  far more readable than working with one unnamed, two-item result.
- This is the exact "return several related values, then unpack them"
  pattern first previewed in Module 1.1 and formalized in
  [Tuples and Unpacking](../02-Python-Core-Language-and-Data-Types/06-tuples-and-unpacking.md),
  now shown as a genuinely useful, reusable function.

**Expected output:**

```text
Lowest score: 68
Highest score: 95
```

### Example 6 — Safely adding items to a list

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

**Plain-English explanation:**

- `add_item_safe` uses the safe default pattern from Section 8:
  `items=None`, then `if items is None: items = []` builds a genuinely
  new list on every call that does not supply one.
- `cart_one` and `cart_two` are each built from a separate call with no
  `items` argument, and — unlike the unsafe version — they correctly end
  up as two completely independent, single-item lists.
- `existing_cart` shows the function also works correctly when a real
  list *is* supplied: `items is None` is `False` this time, so the
  existing list is used and mutated directly, exactly as intended,
  adding `"eggs"` to the list that was already there.

**Expected output:**

```text
Cart one: ['apples']
Cart two: ['bread']
Updated existing cart: ['milk', 'eggs']
```

### Example 7 — Formatting a report with keyword-only options

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

**Plain-English explanation:**

- `title` stays an ordinary parameter; `uppercase` and `border` are both
  **keyword-only**, since they come after the lone `*` — every call below
  correctly names them, so nobody reading the code has to guess what a
  bare `True` or `False` means.
- The docstring states, in plain English, exactly what `format_report`
  does, what each parameter controls, and what it returns — useful even
  though the function is short, since `border` and `uppercase` are not
  fully self-explanatory from the function name alone.
- Each call builds on the last: no options applied, then `uppercase`
  alone, then both `uppercase` and `border` together — showing that
  keyword-only options can be combined freely, in any order, precisely
  because they are always identified by name.

**Expected output:**

```text
monthly summary
MONTHLY SUMMARY
--- MONTHLY SUMMARY ---
```

## Common beginner mistakes

- **Confusing `print()` with `return`.** `print()` only displays a value
  for a human to see; `return` hands a value back so the *program* can
  keep using it. A function that only prints its result cannot have that
  result stored or reused — `result = my_function()` would store `None`.
- **Forgetting that a function without `return` gives back `None`**, and
  being confused when a stored result turns out to be `None` instead of
  the expected value.
- **Getting positional argument order wrong**, silently producing a
  nonsensical but non-crashing result, as in
  `describe_student(92, "Ada")` from Section 5.
- **Placing a positional argument after a keyword argument**, which
  raises a `SyntaxError`.
- **Using a mutable value like `[]` or `{}` directly as a default
  argument.** As Section 8 showed in detail, this creates exactly one
  shared object reused across every call that relies on the default —
  always use `None` and build the real value inside the function body
  instead.
- **Trying to pass a keyword-only parameter positionally**, which raises
  a `TypeError`, because the function does not accept that argument
  positionally.
- **Writing a docstring that just repeats the function's name** (for
  example, `"""Calculates a total."""` for a function called
  `calculate_total`) instead of explaining what the parameters mean and
  what is actually returned.

## Try it yourself

Do not look up full solutions. Predict the output before running each
one.

1. Write a function `calculate_area(width, height)` that returns the area
   of a rectangle. Call it with different values and print the results.
2. Write a function `greet(name, greeting)` and call it once with
   positional arguments in the wrong order, once with correct positional
   arguments, and once using keyword arguments — compare all three
   outputs.
3. Write a function `apply_tax(price, tax_rate=0.08)` that returns the
   price including tax. Call it once using the default rate and once
   overriding it with a keyword argument.
4. Deliberately write a function with a mutable default argument, such as
   `def add_tag(tag, tags=[]):`, call it three times with no `tags`
   argument, and observe the shared-list bug for yourself before fixing
   it using the `None` pattern from Section 8.
5. Write a function `summarize_numbers(numbers)` that returns three
   values — the total, the count, and the average — packed together, and
   unpack all three into separate variables at the call site. Assume the
   input collection is non-empty.
6. Write a function `make_label(text, *, bold=False)` with one
   keyword-only parameter, and a short docstring explaining what it
   does. Call it twice: once with the default, and once overriding
   `bold`.

## Summary

- A **function** is a named, reusable group of instructions, created with
  `def` and run with a function call; defining a function does not run
  it.
- **Parameters** are named placeholders in a function's definition;
  **arguments** are the real values supplied when the function is
  called.
- `return` sends a value back to the caller so it can be stored and
  reused; `print()` only displays a value and hands nothing back. A
  function with no `return` gives back `None`.
- **Positional arguments** are matched by order; **keyword arguments**
  are matched by name and can appear in any order, but ordinary
  positional arguments must come before keyword arguments in a call.
- A **default value** lets a parameter be skipped entirely; prefer an
  immutable default (`None`, a number, a string, a `bool`), never a
  mutable one like `[]`, which would be silently shared across every
  call that relies on it.
- A **`*`** in a function's parameter list makes every parameter after it
  **keyword-only**, which can make a call's intent much clearer.
- `return`ing several comma-separated values packs them into a tuple,
  which the caller can unpack directly into named variables.
- A **docstring**, written as the first line(s) inside a function, briefly
  documents what it does, what its parameters mean, and what it returns.

## Completion checklist

- [ ] I can explain the difference between defining a function and
      calling it.
- [ ] I can write a function with one or more parameters and call it with
      matching arguments.
- [ ] I can explain, with an example, exactly how `return` differs from
      `print()`, and what a function with no `return` gives back.
- [ ] I can call a function using positional arguments, keyword
      arguments, and a mix of both, in the correct order.
- [ ] I can give a parameter a default value, override it, and explain
      why a mutable default value is dangerous — and how to avoid that
      danger using `None`.
- [ ] I can define and correctly call a function with a keyword-only
      parameter.
- [ ] I can return multiple values from a function and unpack them into
      separate variables.
- [ ] I can write a short, useful docstring for a function.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

Python functions are one common way you will later implement the
individual "tools" an AI agent can call: each tool can be a function with
clearly named parameters, sensible defaults, and a well-defined return
value the rest of the system can depend on. The `print()` versus `return` distinction becomes even
more important there — an agent's tools need to *return* structured
results the calling code can act on, not merely print something a human
happens to be watching. The mutable-default-argument warning from Section
8 is a genuinely common, real production bug in exactly this kind of
code: a tool function that accidentally shares one mutable list or
dictionary across unrelated calls can silently corrupt an agent's state
in ways that are very difficult to trace back to their cause. Clear
docstrings, in turn, are often used as a source for a tool's description
— the text an AI model itself reads to decide when and how to call that
tool correctly. Which parts of a function a framework uses (docstrings,
annotations, or other metadata) depends on the framework.
