# Function Arguments, Defaults, and Docstrings

## Why function interfaces matter

You already know how to write a function, give it parameters, and get a
value back with `return`. This lesson does not repeat that — instead, it
focuses on something just as important: **how a function is called**.
Two functions that compute the exact same thing can feel completely
different to use, depending on how their arguments are structured. A
function that forces the caller to remember five values in an exact,
unlabeled order invites mistakes. A function with clear required inputs,
sensible optional settings, and a short description of what it expects is
far harder to misuse — and far easier for *you*, reading your own code a
month later, to trust without re-reading its entire body. This lesson is
about designing that experience deliberately, not just making a function
"work."

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain why a function's parameter list is a **contract** between the
  function and whoever calls it, and choose parameter names that reveal
  what each one expects.
- Explain the difference between a **required** parameter and one with a
  **default value**, and read the `TypeError` Python raises when a
  required argument is missing.
- Explain why incorrect **positional** argument order can create bugs
  that do not crash the program but quietly produce the wrong answer.
- Use **keyword arguments** to make a call self-explanatory, and state
  the rule for mixing positional and keyword arguments in one call.
- Give a parameter a safe **default value**, override it, and explain why
  defaults must be immutable.
- Explain, in your own words, exactly why `items=[]` as a default is
  dangerous, and apply the safe `None`-based replacement pattern.
- Define and correctly call a function with **keyword-only** parameters,
  and explain why they reduce mistakes.
- Write a concise **docstring** that documents a function's purpose,
  parameters, return value, and any important assumptions, and read it
  back using `help()`.
- List the qualities of a well-designed function contract: clear names,
  clear parameter meaning, sensible defaults, predictable return values,
  and clear errors for invalid calls.

## Prerequisites

- [Functions, Parameters, and Return Values](03-functions-parameters-and-return-values.md) —
  this lesson assumes `def`, parameters, function calls, and `return` are
  already comfortable, and builds directly on top of them.
- [Mutability and Immutability](../02-Python-Core-Language-and-Data-Types/10-mutability-and-immutability.md)
  and
  [Lists: Mutation, Copying, and Aliasing](../02-Python-Core-Language-and-Data-Types/05-lists-mutation-copying-and-aliasing.md) —
  the mutable default argument danger in this lesson is a direct,
  real-world consequence of aliasing, first taught there.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Function signature** | The `def` line of a function: its name and its parameter list, describing what it needs and (by convention) what kind of result to expect. |
| **Interface / contract** | The agreement a function makes with its caller: "give me these inputs, in this shape, and I will hand back this kind of result." |
| **Required parameter** | A parameter with no default value; the caller must supply a matching argument, or Python raises an error. |
| **`TypeError`** | The error Python raises when a function call does not match its signature — for example, a missing required argument, or too many arguments. |
| **Positional argument** | An argument matched to a parameter purely by its position/order in the call. |
| **Keyword argument** | An argument passed by explicitly naming the parameter it belongs to. |
| **Default value** | A value a parameter uses automatically when the caller does not supply an argument for it. |
| **Mutable default argument** | A default value that is itself a mutable object (such as `[]`); dangerous, because Python creates it only once, not fresh on every call. |
| **Keyword-only parameter** | A parameter that can only be supplied by name, never by position, because it appears after a `*` in the function's parameter list. |
| **Docstring** | A short string written as the first line(s) inside a function, documenting what it does. |
| **`help()`** | A built-in function that displays a function's signature and docstring together, as a reader-friendly reference. |

## Step-by-step explanation

### 1. Function interface recap: a signature is a contract

A function's **signature** — its name and parameter list — is the part a
caller actually needs to read to use it correctly. They should not need
to read the function's *body* at all. Think of it as a **contract**:
"give me these inputs, and I promise to hand back this kind of result."

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

print(format_price(19.99))
```

```text
$19.99
```

Just from the line `def format_price(amount, currency="$"):`, a caller
can already tell a great deal: the function needs an `amount`, it
*optionally* accepts a `currency` (since it has a default), and its name
strongly suggests it returns a formatted price. **Meaningful names make
this contract readable at a glance** — `format_price(amount, currency)`
tells you what to supply; a signature like `format_price(a, b)` would
force you to go read the body just to understand what to pass in. Every
concept in this lesson — required parameters, defaults, keyword-only
options, docstrings — is really about making this contract as clear as
possible.

### 2. Required parameters

A **required parameter** has no default value, so the caller *must*
supply a matching argument. A function can have one required parameter,
or several:

```python
def greet_by_username(username):
    return f"Welcome, {username}!"

print(greet_by_username("ada99"))
```

```text
Welcome, ada99!
```

```python
def calculate_total(price, quantity):
    return price * quantity

print(calculate_total(9.99, 3))
```

```text
29.97
```

`calculate_total` has **two** required parameters, `price` and
`quantity` — both must be supplied, in some form, or the call fails.

**The `TypeError` for a missing required argument:** if a caller forgets
one, Python does not guess or silently substitute anything — it stops
the program immediately, naming exactly which parameter was missing:

```text
print(calculate_total(9.99))
```

```text
TypeError: calculate_total() missing 1 required positional argument: 'quantity'
```

If more than one required argument is missing, Python names all of them
at once:

```text
print(calculate_total())
```

```text
TypeError: calculate_total() missing 2 required positional arguments: 'price' and 'quantity'
```

This is a genuinely useful error, not just a crash: it tells you the
exact function, and the exact parameter name(s), that need attention —
read it as Python enforcing its half of the "contract" from Section 1.

### 3. Positional arguments

A **positional argument** is matched to a parameter purely by its
**order** in the call. This is convenient for short calls, but it comes
with a real risk: swapped positional arguments do not always produce an
obviously wrong result — sometimes they produce a **plausible-looking,
subtly wrong** one:

```python
def schedule_meeting(start_time, end_time):
    return f"Meeting from {start_time} to {end_time}"

print(schedule_meeting("1:00 PM", "3:00 PM"))
print(schedule_meeting("3:00 PM", "1:00 PM"))
```

```text
Meeting from 1:00 PM to 3:00 PM
Meeting from 3:00 PM to 1:00 PM
```

Both lines run without any error — both arguments are perfectly valid
strings, in the type the function expects. The second call is simply
*wrong*: a meeting cannot sensibly run from `3:00 PM` to `1:00 PM`
earlier the same day, but Python has no way to know that; it only checks
that a value was supplied for each position, not whether the values were
supplied in the *order the caller actually meant*. This is precisely why
argument order deserves real care: a bug like this can sit in a program
for a long time, since nothing crashes to reveal it.

### 4. Keyword arguments

A **keyword argument** names its parameter directly, using
`parameter_name=value`, removing any dependence on order:

```python
def calculate_total(price, quantity):
    return price * quantity

print(calculate_total(price=9.99, quantity=3))
print(calculate_total(quantity=3, price=9.99))
print(calculate_total(9.99, quantity=3))
```

```text
29.97
29.97
29.97
```

All three calls produce the identical result. The first two show that,
once every argument is named, their order in the call no longer matters
at all — Python matches each one by name. The third call **mixes** a
positional argument (`9.99`, matched to `price` by position) with a
keyword argument (`quantity=3`); this is allowed, and is a very common,
readable style: supply the "obvious" arguments positionally, and name
anything that benefits from extra clarity.

**Why this improves readability:** compare `calculate_total(9.99, 3)`
with `calculate_total(price=9.99, quantity=3)` — the second version tells
a reader exactly what each number means, without them needing to recall
the function's parameter order from memory.

**Positional arguments cannot come after keyword arguments.** Once a call
uses a keyword argument, every argument after it must also be a keyword
argument:

```text
print(calculate_total(quantity=3, 9.99))
```

```text
SyntaxError: positional argument follows keyword argument
```

Python raises this error immediately, before the program even starts
running, rather than risk guessing which parameter a stray positional
value was meant to fill.

### 5. Default arguments

A **default value** lets a parameter be skipped entirely by the caller,
falling back to a sensible, pre-chosen value:

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

print(format_price(19.99))
print(format_price(19.99, "€"))
print(format_price(19.99, currency="£"))
```

```text
$19.99
€19.99
£19.99
```

`currency="$"` means "assume US dollars unless told otherwise" — the
overwhelming majority of callers can ignore this parameter entirely.
The second and third calls both **override** the default, once
positionally and once by keyword, proving a default is only ever used
when the caller stays completely silent about that parameter.

**Always keep defaults immutable:** a default of a `str`, a number, a
`bool`, or `None` is always safe — none of these can be silently changed
after the fact. Section 6 shows, in detail, exactly what goes wrong with
a *mutable* default instead.

### 6. The mutable default argument danger

Using a mutable value, such as `[]`, as a default argument is one of the
most well-known traps in Python, and it deserves to be understood
thoroughly, not just avoided by habit.

```python
def add_task(task, tasks=[]):
    tasks.append(task)
    return tasks

todo_list_a = add_task("Write report")
print(todo_list_a)

todo_list_b = add_task("Buy groceries")
print(todo_list_b)
```

```text
['Write report']
['Write report', 'Buy groceries']
```

`todo_list_b` was clearly meant to start as a brand-new list containing
only `"Buy groceries"` — instead, it contains both tasks. **Why this
happens, in simple terms:** a default value is created **exactly once**,
the moment Python reads the `def` line, not fresh on every call. So
`tasks=[]` builds *one* empty list when `add_task` is defined, and every
call that skips the `tasks` argument reuses that *same* list, mutating it
further each time. This is exactly the **aliasing** danger from
[Lists: Mutation, Copying, and Aliasing](../02-Python-Core-Language-and-Data-Types/05-lists-mutation-copying-and-aliasing.md):
two separate-looking calls end up sharing one list under the hood,
because nothing ever built a second one.

**The safe standard pattern:** use `None` as the default — since `None`
is immutable, it is completely safe to reuse — and build a genuinely new
list *inside* the function body, only when one was not supplied:

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

```text
['Write report']
['Buy groceries']
```

Now every call that omits `tasks` gets a fresh, independent list, because
`tasks = []` runs again, from scratch, inside the function body, on every
single call — not once, at definition time. **The rule to remember: never
write `def f(x=[]):`, `def f(x={}):`, or `def f(x=set()):`. Use `None`,
and build the real, empty collection inside the function instead.**

### 7. Keyword-only arguments

A lone **`*`** in a function's parameter list marks every parameter after
it as **keyword-only** — it can only ever be supplied by name. This is
ideal for options that would be easy to misread as a bare value in a
call, such as `verbose`, `currency`, or `include_tax`:

```python
def calculate_total(price, quantity, *, include_tax=False):
    subtotal = price * quantity
    if include_tax:
        return subtotal * 1.08
    return subtotal

print(calculate_total(10, 2))
print(calculate_total(10, 2, include_tax=True))
```

```text
20
21.6
```

`price` and `quantity` remain ordinary parameters — positional or
keyword, either is fine. `include_tax` comes after the `*`, so it
**must** always be named:

```text
print(calculate_total(10, 2, True))
```

```text
TypeError: calculate_total() takes 2 positional arguments but 3 were given
```

Without `calculate_total(10, 2, True)` being rejected, a reader (and a
future version of you) would have no way to know what that bare `True`
even means. `include_tax=True` states its purpose directly in the call
itself — this is exactly why options like this are worth making
keyword-only: it prevents an entire category of unclear, easy-to-misread
calls.

### 8. Docstrings

A **docstring** is a string written as the very first thing inside a
function's body. A useful docstring briefly covers four things: the
function's **purpose**, what each **parameter** means, what it
**returns**, and any **important assumption** the caller should know
about.

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

```text
Help on function format_price in module __main__:

format_price(amount, currency='$')
    Format a number as a price string.

    amount is the numeric price to display.
    currency is the symbol to place in front of the amount, and
    defaults to "$" when the caller does not supply one.
    Returns a string such as "$19.99".
```

`help(format_price)` displays the function's full signature — including
its default value, `currency='$'` — together with the docstring, exactly
as a reader would want to see it before using the function, without ever
opening the file that defines it. This is intentionally simple:
plain-English sentences describing purpose, parameters, and return value
are enough at this stage — there is no need for special tags, sections,
or a documentation framework to get real value from a docstring.

### 9. Designing clear function contracts

Pulling everything in this lesson together, a well-designed function
signature has five qualities:

- **Clear names** — the function name is a verb phrase describing the
  action (`calculate_total`, not `calc`); parameter names describe what
  they hold (`price`, `quantity`, not `a`, `b`).
- **Clear parameter meaning** — a reader can guess what to pass in from
  the names alone, without reading the function's body.
- **Sensible defaults** — optional settings default to whatever most
  callers actually want, using only immutable default values.
- **Predictable return values** — the function always returns the same
  *kind* of thing (always a number, always a formatted string), rather
  than sometimes returning a real result and sometimes `None`.
- **Clear errors for invalid calls** — missing a required argument
  produces a specific, readable `TypeError`, naming exactly what went
  wrong, rather than the program continuing with a nonsensical result.

Compare a poorly designed signature with a well-designed one for the same
task:

```text
def calc(a, b, c=1):          # unclear names, unclear meaning
    ...

def calculate_total(price, quantity, *, include_tax=False):   # clear
    ...
```

The second signature needs no extra explanation to use correctly — the
names, the required/optional split, and the keyword-only tax flag all
communicate the contract directly. **One honest limitation to know
about:** nothing shown in this lesson stops a caller from passing the
*wrong type* of value, such as `calculate_total("ten", 2)` — Python will
either raise a different error while trying to use it, or, in rarer
cases, silently produce a strange result. Explicitly checking that
inputs are valid, and raising clear errors on purpose when they are not,
is covered fully in
[Exceptions, Validation, and Useful Errors](07-exceptions-validation-and-useful-errors.md).
For now, a clear name, a sensible default, and a predictable return value
are already a strong, professional foundation.

## Examples

### Example 1 — `format_price`: defaults with an override

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

domestic_price = format_price(42.5)
foreign_price = format_price(42.5, currency="€")

print(domestic_price)
print(foreign_price)
```

**Plain-English explanation:**

- `format_price` has one required parameter, `amount`, and one optional
  parameter, `currency`, defaulting to `"$"`.
- `format_price(42.5)` supplies only `amount`, so `currency` falls back
  to its default, producing `$42.50`.
- `format_price(42.5, currency="€")` explicitly overrides the default
  with a keyword argument, producing `€42.50` — the same underlying
  amount, formatted for a different currency, with no change to the
  function itself.

**Expected output:**

```text
$42.50
€42.50
```

### Example 2 — `create_greeting`: keyword arguments across a batch of calls

```python
def create_greeting(name, greeting="Hello"):
    return f"{greeting}, {name}!"

visitors = ["Ada", "Grace", "Alan"]

for visitor in visitors:
    print(create_greeting(visitor))

print(create_greeting("Marie", greeting="Welcome back"))
```

**Plain-English explanation:**

- `create_greeting` takes a required `name` and an optional `greeting`,
  defaulting to `"Hello"`.
- The `for` loop calls `create_greeting(visitor)` once per visitor,
  relying on the default greeting for all three, since nothing about
  them is different yet.
- The final call, outside the loop, uses a **keyword argument**,
  `greeting="Welcome back"`, to give one specific visitor, `"Marie"`, a
  different message — naming the argument makes it immediately obvious
  *what* is being customized, without needing to check the function's
  parameter order.

**Expected output:**

```text
Hello, Ada!
Hello, Grace!
Hello, Alan!
Welcome back, Marie!
```

### Example 3 — `calculate_total`: a keyword-only tax option

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

**Plain-English explanation:**

- `price` and `quantity` are required and ordinary; `include_tax` is
  **keyword-only**, thanks to the `*`, and defaults to `False`.
- `calculate_total(12.50, 4)` never mentions `include_tax`, so it stays
  `False`, and the function returns the plain subtotal, `50.0`.
- `calculate_total(12.50, 4, include_tax=True)` explicitly opts into the
  tax calculation by name — there is no way to accidentally trigger this
  behavior with a stray, unnamed `True` in the call, precisely because
  `include_tax` cannot be supplied positionally.
- Notice the function's return value is **predictable**: it always
  returns a plain number representing a total, whether or not tax was
  included — exactly the "predictable return values" quality from
  Section 9.

**Expected output:**

```text
Without tax: $50.00
With tax: $54.00
```

### Example 4 — `add_task`: the safe mutable-default pattern in use

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

**Plain-English explanation:**

- `add_task` uses the safe pattern from Section 6: `tasks=None`, then
  `if tasks is None: tasks = []` builds a genuinely new list whenever the
  caller does not supply one.
- The first call, `add_task("Write report")`, has no `tasks` argument, so
  a fresh list is created and returned, now holding one task.
- The second call **explicitly passes** `mondays_tasks` back in as the
  `tasks` argument, so this time `tasks is None` is `False` — the
  *existing* list is reused and mutated on purpose, correctly growing
  Monday's list to two tasks.
- `tuesdays_tasks = add_task("Plan sprint")` again supplies no `tasks`
  argument, and — unlike the unsafe version from Section 6 — correctly
  starts a brand-new, independent list, with no trace of Monday's tasks
  in it.

**Expected output:**

```text
Monday: ['Write report', 'Review code']
Tuesday: ['Plan sprint']
```

### Example 5 — `schedule_meeting`: required parameters, order, and a missing argument

```python
def schedule_meeting(start_time, end_time, topic):
    return f"'{topic}' runs from {start_time} to {end_time}."

correct_booking = schedule_meeting("1:00 PM", "2:00 PM", "Budget review")
print(correct_booking)

confusing_booking = schedule_meeting("2:00 PM", "Budget review", "1:00 PM")
print(confusing_booking)
```

**Plain-English explanation:**

- `schedule_meeting` has **three** required parameters, in this exact
  order: `start_time`, `end_time`, `topic`.
- `correct_booking` supplies all three positionally, in the order the
  function expects, producing a sensible sentence.
- `confusing_booking` supplies the same three pieces of information, but
  in the wrong order — `"1:00 PM"` (clearly meant as a time) ends up
  matched to `topic`, and `"Budget review"` (clearly meant as a topic)
  ends up matched to `end_time`. Nothing crashes, because every argument
  is still a valid `str`; the result is simply nonsense, exactly the
  subtle-bug risk from Section 3, now with three parameters instead of
  two, making the mismatch even easier to miss at a glance.
- Leaving out `topic` entirely —
  `schedule_meeting("1:00 PM", "Budget review")` — would instead raise
  `TypeError: schedule_meeting() missing 1 required positional argument:
  'topic'`, exactly the enforcement from Section 2: Python always
  detects a *missing* argument, but it can never detect an argument
  supplied in the *wrong position*, since both are equally valid values
  to it.

**Expected output:**

```text
'Budget review' runs from 1:00 PM to 2:00 PM.
'1:00 PM' runs from 2:00 PM to Budget review.
```

### Example 6 — `build_invoice_line`: a complete, well-designed contract

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

**Plain-English explanation:**

- `item_name`, `unit_price`, and `quantity` are required and clearly
  named; `currency` and `tax_included` are keyword-only, each with a
  sensible immutable default, so most calls only need to supply the
  three required pieces of information.
- The docstring states the function's purpose, what every parameter
  means, and exactly what is returned — a caller could use this function
  correctly from the docstring alone, via `help(build_invoice_line)`,
  without ever reading its body.
- The three calls show the required arguments alone, then with tax
  included, then with both tax and a different currency — every option
  is combined purely by name, so nothing about any call is ambiguous.
- This example draws together every idea from this lesson at once:
  required parameters, keyword-only options, safe defaults, and a
  documenting docstring — the full shape of a well-designed function
  contract from Section 9.

**Expected output:**

```text
Notebook x4: $14.00
Notebook x4: $15.12
Notebook x4: €15.12
```

## Common beginner mistakes

- **Choosing vague parameter names** (`a`, `b`, `data`, `x`) instead of
  names that reveal what each one actually represents, forcing every
  caller to go read the function's body just to use it correctly.
- **Assuming Python detects an incorrect argument order.** As Section 3
  and Example 5 showed, swapped positional arguments of the same type
  never raise an error — they simply produce a wrong, but "valid-looking,"
  result.
- **Placing a positional argument after a keyword argument**, raising
  `SyntaxError: positional argument follows keyword argument`.
- **Using a mutable value like `[]`, `{}`, or `set()` directly as a
  default argument.** As Section 6 demonstrated in full, this creates
  exactly one shared object reused across every call that relies on the
  default — always use `None`, and build the real value fresh inside the
  function body.
- **Trying to pass a keyword-only argument positionally**, which raises a
  `TypeError` naming exactly how many positional arguments the function
  actually accepts.
- **Writing a docstring that only restates the function's name** instead
  of explaining what each parameter means and what is actually returned.
- **Forgetting that Python still cannot check argument *types* for you.**
  A clear signature and a good docstring reduce mistakes, but they do
  not prevent someone from passing the wrong kind of value entirely —
  that is what
  [Exceptions, Validation, and Useful Errors](07-exceptions-validation-and-useful-errors.md)
  covers.

## Try it yourself

Do not look up full solutions. Predict the output before running each
one.

1. Write `convert_temperature(celsius, to_unit="fahrenheit")` with a
   sensible default, call it once using the default and once overriding
   it with a keyword argument.
2. Write a function with three required parameters of your own choosing,
   call it once correctly, then call it with two arguments swapped, and
   write down, in a comment, why the result is wrong but Python does not
   raise an error.
3. Deliberately write a function with a mutable default argument, such as
   `def add_tag(tag, tags=[]):`, call it three times with no `tags`
   argument, and observe the shared-list bug for yourself before fixing
   it using the `None` pattern from Section 6.
4. Write `send_notification(message, *, urgent=False)` with one
   keyword-only parameter, and show what error occurs if `urgent` is
   passed positionally instead.
5. Write a short, clear docstring for one function you already wrote in
   this lesson's exercises, covering its purpose, its parameters, and its
   return value, then confirm it displays correctly with
   `help(your_function_name)`.
6. Take the poorly named `def calc(a, b, c=1):` signature from Section 9,
   invent a real task for it, and rewrite it with a clear name, clear
   parameter names, and (if appropriate) a keyword-only option.

## Summary

- A function's **signature** is a contract: its name and parameters tell
  a caller what to supply, and clear names make that contract readable
  without needing to read the function's body.
- A **required parameter** has no default; omitting its argument raises a
  `TypeError` that names exactly which parameter is missing.
- **Positional arguments** are matched by order, which can silently
  produce a wrong-but-valid result if the order is mistaken; **keyword
  arguments** name their parameter directly and can appear in any order,
  but must come after every positional argument in the same call.
- A **default value** lets a parameter be skipped; always use an
  immutable default (`None`, a number, a string, a `bool`).
- A **mutable default argument**, such as `[]`, is created only once and
  silently shared across every call that relies on it — always use
  `None`, and build the real value inside the function body instead.
- A **`*`** in the parameter list makes every parameter after it
  **keyword-only**, preventing it from ever being passed positionally by
  mistake.
- A **docstring**, as the first line(s) inside a function, documents its
  purpose, parameters, return value, and assumptions, and can be read
  back with `help()`.
- A well-designed function contract has clear names, clear parameter
  meaning, sensible defaults, a predictable return value, and clear
  errors for invalid calls.

## Completion checklist

- [ ] I can explain why a function's signature acts as a contract with
      its caller, and choose parameter names that make that contract
      clear.
- [ ] I can explain the difference between a required parameter and one
      with a default, and read the `TypeError` for a missing argument.
- [ ] I can explain, with an example, how an incorrect positional
      argument order can produce a wrong result without raising an
      error.
- [ ] I can call a function using positional arguments, keyword
      arguments, and a correct mix of both.
- [ ] I can give a parameter a safe default value and override it.
- [ ] I can explain, in my own words, exactly why a mutable default
      argument is dangerous, and apply the safe `None` pattern to fix
      one.
- [ ] I can define and correctly call a function with a keyword-only
      parameter, and explain the error from calling it positionally.
- [ ] I can write a concise, useful docstring and read it back with
      `help()`.
- [ ] I can list the five qualities of a well-designed function contract.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

The habits in this lesson are exactly what separates a fragile "tool"
function from one an AI agent (or another engineer) can call reliably.
An agent that calls a tool function needs to trust its contract
completely: which arguments are required, which are optional, what a
missing argument reports, and what shape of value comes back every
single time. Keyword-only options are especially valuable here — a tool
call built from structured data (rather than typed by a person) benefits
enormously from being unambiguous, since there is no human eye to notice
a stray, unnamed `True` in the wrong position. A tool function's
docstring, similarly, often becomes the actual description an AI model
reads to decide when and how to call that tool — the same plain,
accurate, purpose-parameters-return description you practiced here is
exactly what that description needs to be.
