# Variables, Basic Types, and None

**Lesson summary, learner-level assessment, and solved exercises**

Source lesson: `02-variables-basic-types-and-none.md`\
Curriculum reference: Stage 1 --- Programming & Computational Thinking.

------------------------------------------------------------------------

## Part 1 --- Complete lesson summary (under 1,000 words)

### 1. Why this lesson matters

In the previous lesson, variables were used before their types were
studied. This lesson explains the kinds of values Python programs
handle. A value's type determines what it represents and which
operations make sense. The lesson covers `int`, `float`, `bool`, `str`,
and the special value `None`.

### 2. Variables, assignment, and meaningful names

A variable is a name bound to an object. Assignment uses `=`:

``` python
age = 25
```

Here, `age` refers to an integer object representing 25. Reassignment
binds the same name to another object. Python does not permanently lock
a variable name to its first type.

Use descriptive lowercase names with underscores, such as `total_price`,
`is_subscribed`, and `customer_name`, rather than vague names such as
`x`. Meaningful names make code easier to read and maintain.

### 3. What a type means

Every Python object has one type. Its type tells you what kind of value
it is and what operations are supported. The four foundational types in
this lesson are:

-   **`int`:** Whole numbers, positive, negative, or zero, without a
    decimal point. Examples: `0`, `25`, `-3`. Use for counts such as age
    in whole years or number of attempts.

``` python
age = 25
items_in_cart = 4
```

-   **`float`:** Floating-point numbers, commonly written with a decimal
    point or scientific notation. Examples: `3.14`, `7.0`, `-0.5`,
    `1e3`. Use for measurements or amounts with fractional parts, such
    as price, temperature, or height. `7.0` is still a `float`. Floats
    use finite binary precision, so values such as `0.1` may not be
    represented exactly. For exact-decimal financial calculations,
    `decimal.Decimal` may be appropriate; floats remain useful for many
    measurements and everyday calculations.

``` python
price = 19.99
temperature = 36.6
```

-   **`bool`:** Exactly two values: `True` and `False` (capitalized,
    without quotes). Use for yes/no facts such as whether a task is
    complete or a user is subscribed. Python detail: `bool` is a
    subclass of `int`, so Boolean values can participate in some numeric
    operations as `1` and `0`.

``` python
is_completed = False
is_subscribed = True
```

-   **`str`:** Text. String literals use single or double quotation
    marks; this course consistently uses double quotes. Use for names,
    messages, labels, and other textual information. `"7"` is text, not
    the integer `7`.

``` python
first_name = "Amara"
```

-   **`None`:** A special singleton value whose type is `NoneType`. It
    commonly represents the absence of a meaningful value---for example,
    information not supplied yet or information that does not apply. It
    is not zero, false, or empty text.

``` python
middle_name = None
```

`None` differs from `""`: the empty string is an actual string
containing zero characters. Depending on the application, it can mean
that a value is known to be blank.

### 4. Inspecting types with `type()`

Use the built-in `type()` to inspect a value:

``` python
print(type(25))       # <class 'int'>
print(type(19.99))    # <class 'float'>
print(type(True))     # <class 'bool'>
print(type("hello"))  # <class 'str'>
print(type(None))     # <class 'NoneType'>
```

The result `<class 'int'>` means the value's type is `int`. This is
especially useful while learning and debugging.

### 5. Reassignment can change the type

``` python
signup_status = "not started"
print(type(signup_status))  # <class 'str'>

signup_status = True
print(type(signup_status))  # <class 'bool'>
```

First the name refers to a `str`; after reassignment it refers to a
`bool`. This is normal Python behavior.

### 6. `None` is not `0`, `False`, or `""`

These values may all feel like "nothing" in ordinary language, but
Python treats them as different values:

``` python
print(None == 0)      # False
print(None == False)  # False
print(None == "")     # False
```

Here `==` means "is equal to." `None` means no meaningful value is
available; `0`, `False`, and `""` are actual values with distinct
meanings.

### 7. The three lesson examples

**Example 1 --- Values and their types**

``` python
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

Five descriptive variables hold the four basic types and `None`. Each
`print` displays a value and its type. Output:

``` text
25 <class 'int'>
19.99 <class 'float'>
True <class 'bool'>
Amara <class 'str'>
None <class 'NoneType'>
```

`None` is printable; it is not an error or blank text.

**Example 2 --- Optional information arriving later**

``` python
phone_number = None
print(phone_number)
print(type(phone_number))

phone_number = "555-0142"
print(phone_number)
print(type(phone_number))
```

Initially the phone number has not been supplied, so it is `None`
(`NoneType`). Later, reassignment stores a string. The first two outputs
are `None` and `<class 'NoneType'>`; the last two are `555-0142` and
`<class 'str'>`. This is a common pattern for optional data.

**Example 3 --- A string and integer cannot be joined directly with
`+`**

``` python
age = 25
print("Age: " + age)
```

`+` can add compatible numeric values or concatenate strings, but it
does not directly combine a `str` and an `int`. The code is
grammatically valid but raises a runtime `TypeError`, typically:

``` text
TypeError: can only concatenate str (not "int") to str
```

For this lesson, safely pass both values to `print` separated by a
comma:

``` python
age = 25
print("Age:", age)
```

Output: `Age: 25`. `print` can display multiple values of different
types; `+` cannot combine these mismatched types.

### 8. Common mistakes and key takeaways

-   Joining text and a number with `+` causes `TypeError`; use
    comma-separated arguments to `print` for now.
-   `None`, `0`, `False`, and `""` are different values.
-   `None` (no quotes) is the special value; `"None"` is ordinary text.
-   Prefer meaningful names over `x`, `y`, or `d1`.
-   Reassignment can bind a name to an object of a different type.
-   Later AI applications also handle optional form fields, API values,
    and tool results. Correctly distinguishing "not supplied" (`None`)
    from zero, false, or empty text prevents bugs.

------------------------------------------------------------------------

## Part 2 --- Learner-level assessment from the Stage 1 project tree

The Stage 1 tree progresses from computational thinking and program
design into Python core language and data types, control flow/functions,
collections and algorithmic habits, files/structured data/CLI programs,
modules/packages/code quality, testing/debugging, and
object-oriented/data modelling concepts. It also includes advanced
Python and production topics, plus applied projects such as a
data-quality/transformation pipeline and a rule-based risk-review
engine.

This lesson belongs to the Python core-language foundation and builds on
variables/assignment and the earlier lesson about Python files, the
interpreter, the REPL, and indentation. The current lesson expects
familiarity with assignment and basic equality/condition vocabulary.

**Assessment:** The tree shows what the curriculum plans to teach; it
does not prove that every topic has been completed or mastered. The
conversation contains no independently submitted exercise results for
this lesson, so demonstrated proficiency cannot yet be verified. Treat
the learner's current working level for this topic as
*beginner/foundational, with mastery pending practical verification*.
The solutions below use only the lesson's concepts and its stated
prerequisites; they do not depend on later topics.

------------------------------------------------------------------------

## Part 3 --- All five exercises solved step by step (under 1,500 words)

### Exercise 1 --- Create personal variables and print their types

Replace the example values with your own:

``` python
age = 25
height_in_meters = 1.70
has_finished_exercise = False

print(age, type(age))
print(height_in_meters, type(height_in_meters))
print(has_finished_exercise, type(has_finished_exercise))
```

Line by line:

1.  `age = 25` binds `age` to an integer (`int`).
2.  `height_in_meters = 1.70` binds the height to a floating-point
    number (`float`).
3.  `has_finished_exercise = False` stores a Boolean (`bool`). Change it
    to `True` when finished.
4.  Each `print` displays the variable's value and `type(...)` result.

Expected output with the sample values:

``` text
25 <class 'int'>
1.7 <class 'float'>
False <class 'bool'>
```

### Exercise 2 --- Represent a discount code that has not arrived yet

``` python
discount_code = None
print(discount_code)
print(type(discount_code))

discount_code = "SAVE10"
print(discount_code)
print(type(discount_code))
```

Line by line: first, `discount_code = None` means the customer has not
entered a code. The next two lines display `None` and its type,
`NoneType`. Then `discount_code = "SAVE10"` reassigns the name to actual
text. The final two lines display `SAVE10` and `<class 'str'>`.

Expected output:

``` text
None
<class 'NoneType'>
SAVE10
<class 'str'>
```

### Exercise 3 --- Predict and verify five types

Before running the code, predict:

  Value    Expected type
  -------- ---------------
  `10`     `int`
  `10.0`   `float`
  `True`   `bool`
  `"10"`   `str`
  `None`   `NoneType`

Verify with:

``` python
print(type(10))
print(type(10.0))
print(type(True))
print(type("10"))
print(type(None))
```

Expected output:

``` text
<class 'int'>
<class 'float'>
<class 'bool'>
<class 'str'>
<class 'NoneType'>
```

The quotation marks make `"10"` text; without quotes, `10` is an
integer.

### Exercise 4 --- Trigger and fix a mixed-type `+` error

**Deliberately incorrect code:**

``` python
age = 25
print("Age: " + age)
```

`age` is an `int`, while `"Age: "` is a `str`. Python cannot concatenate
these two types directly, so execution raises a `TypeError`, commonly:

``` text
TypeError: can only concatenate str (not "int") to str
```

Exact wording can vary by Python version.

**Corrected code:**

``` python
age = 25
print("Age:", age)
```

The first line stores the integer. The second passes the text and
integer as separate arguments to `print`, which can display both.
Output:

``` text
Age: 25
```

### Exercise 5 --- Replace a vague variable name

Original:

``` python
x = 42
```

Improved:

``` python
person_age = 42
print(person_age)
```

Line by line: `person_age = 42` binds the integer 42 to a descriptive
name. `print(person_age)` displays the value. Output is `42`.

**Why the new name is better:** `person_age` tells the reader what `42`
represents, whereas `x` gives no useful meaning and makes the code
harder to understand later.

------------------------------------------------------------------------

## Completion checklist

-   [ ] I can create and reassign variables using meaningful names.
-   [ ] I can identify `int`, `float`, `bool`, `str`, and `NoneType`.
-   [ ] I have used `type()` to inspect values.
-   [ ] I can explain why `None` differs from `0`, `False`, and `""`.
-   [ ] I can explain why `"Age: " + 25` fails and use comma-separated
    `print` arguments instead.
-   [ ] I completed all five exercises and checked the outputs on my
    machine.

**Scope note:** The code and outputs above are expected results for the
examples shown. Exercise 1's personal values are placeholders; replace
them with your own information before running the program.
