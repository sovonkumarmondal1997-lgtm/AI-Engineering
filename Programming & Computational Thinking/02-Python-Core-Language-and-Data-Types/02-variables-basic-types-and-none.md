# Variables, Basic Types, and None

## Why this topic matters

In Module 1.1 you already used variables and were told, "every value has a
type — you will study types in detail in Module 1.2." This lesson is that
promise kept. Every single piece of data your programs will ever touch —
an age, a price, a name, whether something is finished, or whether a piece
of information is even available yet — belongs to one of Python's basic
types. Knowing exactly what each type represents, and what it does not, is
what lets you predict how your code will behave instead of guessing.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what a variable is, and create, assign, and reassign one with a
  meaningful name.
- Name Python's five basic types covered here — `int`, `float`, `bool`,
  `str`, and `None` — and give a real-world example of each.
- Use `type()` to check what type a value actually is.
- Explain what `None` means, and explain why it is different from `0`,
  `False`, and `""` (an empty string).
- Explain why directly combining text and a number with `+` causes an
  error, and describe one safe way to avoid it.

## Prerequisites

- [Python Files, the Interpreter, the REPL, and Indentation](01-python-files-interpreter-repl-and-indentation.md)
- [Values, Expressions, Statements, and Variables](../01-Computational-Thinking-and-Program-Design/02-values-expressions-statements-and-variables.md) —
  this lesson assumes you already know what a variable and an assignment
  statement are; here, the focus shifts specifically to **types**.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Type** | A label that tells Python (and you) what *kind* of value something is, and what you're allowed to do with it. |
| **`int`** | A whole number type, with no decimal point, such as `7` or `-3`. Short for "integer." |
| **`float`** | A number type that includes a decimal point, such as `3.14` or `7.0`. Short for "floating-point number." |
| **`bool`** | A type with exactly two possible values, `True` or `False`. Short for "Boolean." |
| **`str`** | A text type, always written between quotation marks, such as `"hello"`. Short for "string." |
| **`None`** | A special, single value meaning "no value is available here" — not zero, not false, not empty text, but genuinely nothing yet. |
| **`type()`** | A built-in instruction that tells you the type of any value, for example `type(7)`. |

## Step-by-step explanation

### 1. A quick recap: variables and assignment

As you learned in
[Values, Expressions, Statements, and Variables](../01-Computational-Thinking-and-Program-Design/02-values-expressions-statements-and-variables.md),
a **variable** is a name attached to a value using `=`:

```python
age = 25
```

You can also **reassign** a variable to point it at a new value later. This
lesson adds one new habit on top of that: giving variables **meaningful
names**. `age = 25` tells a reader what the number means; `x = 25` does
not. Prefer full, descriptive, lowercase words separated by underscores
(`total_price`, `is_subscribed`, `customer_name`) over single letters or
vague names — your code is read far more often than it is written, often by
your own future self.

### 2. What a "type" is, and why Python cares

Every value in Python has exactly one **type**, and that type decides what
you are allowed to do with it. You can add two numbers together, but adding
a number to a piece of text directly does not make sense — and Python will
refuse to guess what you meant. This lesson covers five basic types:
`int`, `float`, `bool`, `str`, and `None`.

### 3. `int`: whole numbers

An **`int`** is a whole number, positive or negative, with no decimal
point: `0`, `25`, `-3`. Use `int` for things that are naturally counted in
whole units: someone's age in years, a quantity of items, a number of
attempts.

```python
age = 25
items_in_cart = 4
```

### 4. `float`: numbers with a decimal point

A **`float`** is a number written with a decimal point: `3.14`, `7.0`,
`-0.5`. Use `float` for measurements or amounts that can meaningfully have
a fractional part: a price, a temperature, a height in meters. Even a value
like `7.0`, which looks like a whole number, is still a `float`, because of
the decimal point.

```python
price = 19.99
temperature = 36.6
```

### 5. `bool`: exactly two values

A **`bool`** (Boolean) can only ever be one of two values: `True` or
`False`, always written with a capital letter and no quotation marks. Use
`bool` for genuine yes/no, on/off facts: whether a task is finished,
whether a user is subscribed, whether a checkbox is ticked.

```python
is_completed = False
is_subscribed = True
```

### 6. `str`: text

A **`str`** (string) is text, always written between quotation marks —
either single (`'like this'`) or double (`"like this"`); this course uses
double quotes consistently. Use `str` for names, messages, labels, and any
other information that is fundamentally words or characters rather than a
number to calculate with.

```python
first_name = "Amara"
```

Note that `"7"` (with quotes) is a `str` containing the character `7`, not
the number seven — this distinction causes one of the most common beginner
mistakes, covered later in this lesson.

### 7. `None`: no value available yet

**`None`** is a single, special value that means "there is genuinely no
value here yet" — not zero, not false, not an empty piece of text, but the
complete absence of a value. Use `None` when information does not exist
yet, has not been provided, or is not applicable:

```python
middle_name = None
```

This says "we do not have a middle name to store right now" — very
different from `middle_name = ""`, which would say "we know the middle name
is an empty piece of text" (an unusual, but different, claim). You will
practice this distinction directly in Example 2 below.

### 8. Using `type()` to check a value's type

While learning, if you are ever unsure what type a value is, `type()` will
tell you:

```python
print(type(25))          # <class 'int'>
print(type(19.99))       # <class 'float'>
print(type(True))        # <class 'bool'>
print(type("hello"))     # <class 'str'>
print(type(None))        # <class 'NoneType'>
```

Read `<class 'int'>` as simply "this value's type is `int`" — `type()` is a
tool for you to inspect your own code while learning, not something you
will print in a finished program.

### 9. A variable's type can change after reassignment

A Python variable does not have a fixed type forever — only the *value* it
currently points to has a type. Reassigning a variable can point it at a
completely different type of value:

```python
signup_status = "not started"
print(type(signup_status))   # <class 'str'>

signup_status = True
print(type(signup_status))   # <class 'bool'>
```

This is normal and intentional in Python, but it can surprise beginners who
expect a variable to "lock in" its first type — it does not.

### 10. `None` is not `0`, `False`, or `""`

Because `None`, `0`, `False`, and `""` can all *feel* like "nothing" in
everyday language, it helps to see directly that Python treats them as
completely different values. Recall `==` from
[Sequence, Selection, Iteration, and Abstraction](../01-Computational-Thinking-and-Program-Design/04-sequence-selection-iteration-and-abstraction.md) —
you will study it fully in the next lesson; for now, just read it as "is
equal to":

```python
print(None == 0)     # False
print(None == False) # False
print(None == "")    # False
```

All three print `False`, confirming that `None` is equal to none of them.
`None` means "nothing has been provided at all," while `0`, `False`, and
`""` are all real, specific values that just happen to represent "small" or
"empty" amounts of something.

## Examples

### Example 1 — All five types together, inspected with `type()`

```python
age = 25
price = 19.99
is_subscribed = True
name = "Amara"
middle_name = None

print(age, type(age))
print(price, type(price))
print(is_subscribed, type(is_subscribed))
print(name, type(name))
print(middle_name, type(middle_name))
```

**Plain-English explanation:**

- Five variables are created, one of each basic type covered in this
  lesson, each with a name that describes what it holds.
- Each `print(...)` call passes two things separated by a comma: the value
  itself, and `type(...)` applied to that same value — showing both the
  value and its type side by side.
- Running this prints five lines, for example:
  `25 <class 'int'>`, `19.99 <class 'float'>`,
  `True <class 'bool'>`, `Amara <class 'str'>`, and
  `None <class 'NoneType'>`.
- Notice `middle_name` prints as `None` — not blank, not an error — because
  `None` is a real, printable value, just one that represents "not
  available."

### Example 2 — `None` representing "not entered yet," then reassigned

```python
phone_number = None
print(phone_number)
print(type(phone_number))

phone_number = "555-0142"
print(phone_number)
print(type(phone_number))
```

**Plain-English explanation:**

- `phone_number = None` represents a real, common situation: a user has not
  entered their phone number yet, so there is nothing meaningful to store.
  This is different from setting it to `""`, which would claim "the phone
  number is known to be blank."
- The first two `print` lines confirm the current state: the value is
  `None`, and its type is `NoneType`.
- `phone_number = "555-0142"` is an ordinary reassignment: later in the
  program, once real information becomes available, the same variable is
  pointed at an actual `str` value instead.
- The last two `print` lines now show the phone number as text, with type
  `str`. This is the exact pattern you will use constantly for optional
  data: start a variable at `None` to mean "not yet known," and reassign it
  once real data arrives.

### Example 3 — Combining text and a number directly causes an error

```python
age = 25
print("Age: " + age)
```

**Plain-English explanation:**

- `age = 25` stores a whole number.
- `print("Age: " + age)` tries to use `+` to join the text `"Age: "`
  directly onto the number `age`. Python's `+` operator only works when
  both sides are the same kind of thing it knows how to combine — two
  numbers, or two pieces of text — and refuses to guess how to combine text
  with a number.
- Running this stops the program and shows:
  `TypeError: can only concatenate str (not "int") to str`. This is a
  **runtime** error (as you learned in
  [Algorithms, Programs, and Data](../01-Computational-Thinking-and-Program-Design/01-algorithms-programs-and-data.md)):
  the source code is grammatically valid Python, but it fails once it
  actually runs, because of the types involved.
- A safe fix, using only what you already know, is to pass `"Age: "` and
  `age` to `print` as two separate, comma-separated pieces — exactly like
  Example 2 in the previous lesson:

  ```python
  age = 25
  print("Age:", age)
  ```

  This prints `Age: 25` without error, because `print` is allowed to
  display several different-typed values one after another; it is only
  `+` that demands both sides match.

## Common beginner mistakes

- **Trying to join text and a number with `+`.** As Example 3 shows, this
  raises a `TypeError`; use `print(a, b)` with a comma instead, for now.
- **Confusing `None` with `0`, `False`, or `""`.** These are four different
  values with four different meanings; only `None` means "nothing has been
  provided at all."
- **Confusing the value `None` with the text `"None"`.** `None` (no quotes)
  is the special value; `"None"` (with quotes) is an ordinary four-letter
  piece of text and behaves completely differently.
- **Using vague, single-letter variable names** (`x`, `y`, `d1`) instead of
  names that describe what the value actually represents, making code much
  harder to read later.
- **Expecting a variable to "lock in" its first type.** As Example 9 in the
  step-by-step section showed, reassigning a variable can freely change
  which type of value it points to.

## Try it yourself

1. Create three variables describing yourself: your age (`int`), your
   height in meters (`float`), and whether you have finished this exercise
   (`bool`). Print each one together with its type, using the pattern from
   Example 1.
2. Create a variable called `discount_code` and set it to `None`, to mean
   "the customer has not entered one yet." Print it. Then, later in the
   same file, reassign it to a real code such as `"SAVE10"`, and print it
   again.
3. Without running any code, write down what `type()` would report for
   each of these five values: `10`, `10.0`, `True`, `"10"`, `None`. Then
   check yourself by running `print(type(...))` on each one.
4. Write a line of code that deliberately tries to combine text and a
   number directly with `+`, run it, and copy down the exact error message.
   Then fix it using the comma technique from Example 3.
5. Take a poorly named variable, `x = 42`, representing a person's age.
   Rename it to something meaningful, and write one sentence explaining why
   the new name is an improvement.

## Summary

- A **variable** is a name attached to a value; giving variables meaningful
  names makes code far easier to read and maintain.
- Python's five basic types covered here are **`int`** (whole numbers),
  **`float`** (decimal numbers), **`bool`** (`True`/`False`),
  **`str`** (text), and **`None`** (no value available yet).
- **`type()`** lets you inspect what type any value actually is, which is
  especially useful while you are still learning.
- **`None`** is a distinct value meaning "nothing here yet" — it is not
  equal to `0`, `False`, or `""`.
- A variable's type is not fixed; reassigning it can point it at a value of
  a completely different type.
- Combining text and a number directly with `+` raises a `TypeError`,
  because Python will not silently guess how to combine mismatched types.

## Completion checklist

- [ ] I can create, assign, and reassign a variable with a meaningful name.
- [ ] I can name all five basic types covered here and give a real-world
      example of each.
- [ ] I have used `type()` to check the type of a value myself.
- [ ] I can explain why `None` is different from `0`, `False`, and `""`.
- [ ] I can explain, using my own words, why `"text" + 25` fails, and how to
      print both pieces of information safely instead.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

AI systems constantly deal with optional information: a form field a user
has not filled in yet, an API response that leaves a value out entirely, a
tool call whose result has not come back yet. `None` is exactly how Python
represents "not present" throughout the code you will write later,
including when you validate the arguments an AI agent's tools receive or
check whether a configuration value was actually supplied. Getting
comfortable now with the difference between `None` and a merely "small" or
"empty" value — `0`, `False`, `""` — will save you from a whole category of
real bugs later, where "no answer yet" gets silently and incorrectly
treated as if it were a real, empty answer.
