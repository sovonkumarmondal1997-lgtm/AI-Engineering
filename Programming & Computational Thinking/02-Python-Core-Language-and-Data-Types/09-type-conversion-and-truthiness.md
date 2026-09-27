# Type Conversion and Truthiness

## Why type conversion and truthiness matter

Real data rarely arrives already in the exact type your program needs.
Text typed by a user is always text, even if it looks like a number; a
value read from a file is text until you decide otherwise; a list of
unique tags needs to become a set before you can compare it with another
one. **Type conversion** is how you deliberately turn one type of value
into another, on purpose, instead of hoping Python will guess correctly.
**Truthiness** is a closely related idea: every value in Python, not just
`True` and `False`, has a built-in answer to the question "if this were
used as a yes/no decision, which would it be?" Both skills are about the
same underlying discipline: knowing exactly what type and what "shape" a
value has, rather than assuming.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what a type is and why Python needs to know each value's type.
- Explain implicit conversion, and that not every type combination
  converts automatically.
- Convert values explicitly with `int()`, `float()`, `str()`, and
  `bool()`, and explain the errors each can raise.
- Convert between collections with `list()`, `tuple()`, `set()`, and
  `dict()`, and explain how order, duplicates, and shape can change.
- Inspect and check a value's type with `type()` and `isinstance()`, and
  explain why `isinstance()` is usually the more practical choice.
- Write an introductory `try`/`except ValueError` block to handle bad
  input safely.
- Define truthiness, list Python's standard falsy values, and demonstrate
  truthiness inside `if` statements.
- Explain when `if value:` is a fine check, and when an explicit check
  like `if value is None:` is required instead.
- Use `any()` and `all()` to summarize a list of true/false-like values.

## Prerequisites

- [Variables, Basic Types, and None](02-variables-basic-types-and-none.md) —
  you were told there that type conversion would be covered later; this
  lesson is that promise kept, and reuses the same `int`/`float`/`bool`/
  `str`/`None` vocabulary.
- [Operators and Precedence](03-operators-and-precedence.md) — the
  `is None` rule from that lesson is applied directly in this lesson's
  truthiness discussion.
- [Dictionaries and Lookups](07-dictionaries-and-lookups.md) and
  [Sets and Unique Values](08-sets-and-unique-values.md) — this lesson's
  collection-conversion section assumes both are already familiar.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Type conversion** | Turning a value of one type into an equivalent value of a different type. |
| **Implicit conversion** | Conversion Python performs automatically, without you asking for it. |
| **Explicit conversion** | Conversion you request deliberately, using a function such as `int()`. |
| **Truncation** | Cutting off a number's decimal part completely, without rounding, always moving toward zero. |
| **`ValueError`** | The error Python raises when a value has the right type but the wrong content to be converted, such as `int("abc")`. |
| **Truthiness** | How Python treats any value when a `True`/`False` decision is needed, even if the value is not literally a `bool`. |
| **Falsy** | Describes a value that counts as `False` in a `True`/`False` decision. |
| **Truthy** | Describes a value that counts as `True` in a `True`/`False` decision. |
| **`isinstance()`** | A built-in function that checks whether a value is of a given type, returning `True` or `False`. |
| **Exception handling (preview)** | Code that deliberately catches an error instead of letting it stop the program; introduced only briefly here, and covered fully in Module 1.3. |

## Step-by-step explanation

### 1. What a type is, and why Python needs to know it

As you learned in
[Variables, Basic Types, and None](02-variables-basic-types-and-none.md),
every value has a **type**, which decides what you are allowed to do with
it. `type()` reports a value's type directly:

```python
print(type(5))       # <class 'int'>
print(type(5.0))     # <class 'float'>
print(type("5"))     # <class 'str'>
print(type(True))    # <class 'bool'>
```

Notice `5`, `5.0`, and `"5"` all "mean the same thing" to a human reader,
but are three genuinely different types to Python, each with different
rules — `5 + 1` works, but `"5" + 1` does not, as you saw in that same
earlier lesson. Type conversion is how you deliberately turn one of these
into another, when your program actually needs to.

### 2. Implicit conversion

**Implicit conversion** happens automatically, without you writing any
conversion code. The most common example: combining an `int` and a
`float` with an operator automatically produces a `float`, since a `float`
can represent everything an `int` can, plus fractional values:

```python
count = 3
price = 2.5
total = count * price

print(total)          # 7.5
print(type(total))    # <class 'float'>
```

Python decided, on its own, that the safest way to combine a whole number
and a decimal number was to treat the result as a decimal number too.

**Not every combination converts automatically.** Combining a `str` and
an `int` directly, for example, does *not* implicitly convert either side
— Python refuses to guess whether you meant "5 the number" or "5 the
character," and raises an error instead, exactly as you saw earlier:

```python
print("5" + 3)
```

```text
TypeError: can only concatenate str (not "int") to str
```

This is a deliberate safety feature: implicit conversion only happens in
the small number of cases where there is one obviously correct answer
(like `int` and `float`); everywhere else, Python asks you to say exactly
what you mean.

### 3. Explicit conversion: doing it on purpose

**Explicit conversion** means calling a built-in function to convert a
value's type deliberately. This lesson covers the core toolbox: `int()`,
`float()`, `str()`, `bool()`, and the collection converters `list()`,
`tuple()`, `set()`, and `dict()` — several of which you have already used
informally in earlier lessons without this lesson's full explanation.

### 4. `int()`: converting to a whole number

`int()` converts suitable text or a `float` into an `int`:

```python
print(int("42"))    # 42   — text that looks like a whole number
print(int(3.9))      # 3    — a float, truncated
print(int(-3.9))     # -3   — truncated toward zero, not toward negative infinity
```

**Truncation toward zero:** converting a `float` to an `int` always cuts
off the decimal part completely — it never rounds. Notice `int(-3.9)`
gives `-3`, not `-4`: truncation always moves *toward* zero, regardless of
the number's sign.

**`ValueError` for invalid text:** text that does not represent a valid
whole number cannot be converted:

```python
print(int("abc"))
```

```text
ValueError: invalid literal for int() with base 10: 'abc'
```

**Optional: converting number bases.** `int()` accepts an optional second
argument specifying what base the text is written in — for example, base
`2` for binary text:

```python
print(int("101", 2))   # 5   — "101" read as a binary number
```

This is a genuinely optional, occasional-use feature; you are not expected
to memorize it, only to recognize that `int()` can do this if you ever
need to parse a number written in a different base.

### 5. `float()`: converting to a decimal number

`float()` converts suitable text or an `int` into a `float`:

```python
print(float("3.14"))   # 3.14
print(float(7))         # 7.0
```

Just like `int()`, invalid text raises `ValueError`:

```python
print(float("abc"))
```

```text
ValueError: could not convert string to float: 'abc'
```

### 6. `str()`: converting to displayable text

`str()` converts virtually any value into its text representation:

```python
age = 30
print("Age: " + str(age))   # Age: 30
```

This directly answers the question left open in
[Variables, Basic Types, and None](02-variables-basic-types-and-none.md):
back then, `"Age: " + age` raised a `TypeError`, and the safe workaround
was `print("Age:", age)`. Now you have the real fix — `str(age)` converts
`age` into text first, so `+` has two matching `str` values to join,
exactly as `+` requires.

### 7. `bool()` and truthiness

`bool()` converts any value into `True` or `False`. To understand exactly
*how* it decides, you need **truthiness**: Python's rule for how every
value behaves when a `True`/`False` decision is needed, even values that
are not literally `bool` to begin with.

#### Falsy values

A small, fixed set of values count as **falsy** — they behave as `False`:

```python
print(bool(False))     # False
print(bool(None))      # False
print(bool(0))          # False
print(bool(0.0))        # False
print(bool(""))         # False  — empty string
print(bool([]))         # False  — empty list
print(bool(()))         # False  — empty tuple
print(bool({}))         # False  — empty dictionary
print(bool(set()))      # False  — empty set
```

Every one of these is falsy: `False` itself, `None`, numeric zero (as an
`int` or a `float`), and every *empty* built-in collection.

#### Truthy values

Everything else is **truthy** — in particular, every non-empty string,
every non-zero number, and every non-empty collection:

```python
print(bool(True))       # True
print(bool("hello"))     # True  — any non-empty string
print(bool(42))          # True  — any non-zero number
print(bool([1, 2]))      # True  — any non-empty collection
```

#### Truthiness in `if` statements

`if` (from Module 1.1) uses exactly this same truthiness rule — an `if`
does not require a literal `bool`, it accepts *any* value and treats it
according to truthiness:

```python
name = ""

if name:
    print("Name provided.")
else:
    print("No name provided.")
```

```text
No name provided.
```

`name` is an empty string, which is falsy, so the `else` branch runs —
even though the code never wrote `if name == "":` or anything resembling
an explicit comparison.

#### `if value:` versus `if value is None:`

`if value:` is convenient, but it treats `0`, `False`, `None`, and `""`
**identically** — all falsy, all triggering the same branch. This is
exactly wrong whenever `0`, `False`, or `""` are themselves meaningful,
valid values that should be treated differently from "no value at all":

```python
score = 0

if score:
    print("Has a score.")
else:
    print("No score.")
```

```text
No score.
```

This is misleading: `score` genuinely *is* `0` — a real, valid score, not
a missing one — yet `if score:` cannot tell the difference between "the
score is zero" and "the score was never recorded." The fix, using the
`is None` rule from
[Operators and Precedence](03-operators-and-precedence.md), checks
specifically for absence:

```python
score = 0

if score is None:
    print("Score not recorded yet.")
else:
    print(f"Score: {score}")
```

```text
Score: 0
```

**The rule to remember:** use plain `if value:` when *any* falsy value
should be treated the same way (a common, fine case — for example, "is
this list non-empty?"). Use an explicit check like `if value is None:`
whenever `0`, `False`, or `""` need to be treated as real, distinct,
valid values rather than lumped in with "nothing was provided."

#### `any()` and `all()`

`any()` and `all()` apply truthiness across a whole list at once. `any()`
returns `True` if **at least one** value is truthy; `all()` returns `True`
only if **every** value is truthy:

```python
responses = [True, False, True]
print(any(responses))   # True   — at least one True
print(all(responses))   # False  — not every value is True

scores = [0, 85, 90]
print(any(scores))   # True   — at least one non-zero (truthy) value
print(all(scores))   # False  — the 0 is falsy, so not every value is truthy
```

Notice `any(scores)` and `all(scores)` both apply truthiness directly to
the numbers themselves — `0` counts as falsy, `85` and `90` count as
truthy — without needing to write out `> 0` comparisons by hand.

### 8. Converting collections

`list()`, `tuple()`, `set()`, and `dict()` — already used informally in
earlier lessons — all convert an existing collection (or suitable value)
into their respective type:

```python
print(list("abc"))                       # ['a', 'b', 'c']
print(tuple([1, 2, 3]))                   # (1, 2, 3)
print(set([1, 2, 2, 3]))                  # {1, 2, 3}
print(dict([("a", 1), ("b", 2)]))         # {'a': 1, 'b': 2}
```

`list("abc")` splits a string into a list of its individual characters.
`tuple([1, 2, 3])` and `set([1, 2, 2, 3])` build a tuple and a set from a
list, exactly as covered in
[Tuples and Unpacking](06-tuples-and-unpacking.md) and
[Sets and Unique Values](08-sets-and-unique-values.md). `dict(...)`
expects a collection of two-item pairs and builds key-value pairs from
them, as first shown in
[Dictionaries and Lookups](07-dictionaries-and-lookups.md).

**Conversions can change order, remove duplicates, or fail outright:**

- Converting a list to a **set** removes duplicates — `[1, 2, 2, 3]`
  became `{1, 2, 3}` above — and, as you learned in the sets lesson, does
  not preserve the original order.
- `dict(...)` requires its input to already be shaped as pairs; feeding it
  something the wrong shape raises an error rather than guessing how to
  pair things up:

  ```python
  print(dict(["a", "b", "c"]))
  ```

  ```text
  ValueError: dictionary update sequence element #0 has length 1; 2 is required
  ```

  Each string here has only one character, not the two elements
  `dict(...)` needs to form a key and a value — Python reports exactly
  which element failed and why, rather than silently producing something
  unexpected.

### 9. Inspecting and checking types

`type()` reports a value's exact type, as you have already seen throughout
this lesson. `isinstance(value, type)` asks a slightly different, often
more useful question: "is this value of this type?" — returning `True` or
`False` directly:

```python
value = 42

print(type(value))              # <class 'int'>
print(type(value) == int)        # True
print(isinstance(value, int))    # True
```

Both `type(value) == int` and `isinstance(value, int)` give the same
answer here. **`isinstance()` is usually more practical for basic
validation**: it reads more directly as a yes/no question ("is this an
`int`?") without the slightly awkward detour through `type()` and `==`,
and it is the idiomatic, conventional way experienced Python code checks
a value's type — you will see it used far more often than
`type(...) == ...` comparisons in real code.

### 10. Safe conversion: an introductory preview

Converting untrusted input — such as text a user typed — can always fail
with a `ValueError`. Rather than letting that error crash the whole
program, you can catch it deliberately:

```python
user_input = "twenty"

try:
    age = int(user_input)
    print(f"Age: {age}")
except ValueError:
    print("That doesn't look like a valid number.")
```

```text
That doesn't look like a valid number.
```

Read this as: "try to run this code; if it raises a `ValueError` while
doing so, run this other code instead, rather than stopping the program."
This is only a brief, introductory preview — full exception handling,
including other exception types, `else`, and `finally`, is covered
properly in Module 1.3. For now, just recognize this shape: `try:` the
risky conversion, `except ValueError:` handle the failure gracefully.

## Examples

### Example 1 — Converting text-based scores for a calculation

```python
raw_scores = ["85", "92", "78", "90"]

total = 0
for raw_score in raw_scores:
    total += int(raw_score)

average = total / len(raw_scores)
print(f"Average score: {average:.1f}")
```

**Plain-English explanation:**

- `raw_scores` holds scores as **text**, exactly as they might arrive from
  a text file or a user typing them in — not yet usable in arithmetic.
- The `for` loop (from Module 1.1) visits each text score in turn.
  `int(raw_score)` explicitly converts it to a real number before adding
  it to `total`, using the running-total pattern from earlier lessons.
- `average = total / len(raw_scores)` computes the average using ordinary
  division, reusing `len()` from the lists lesson.
- The f-string, with the `.1f` format specifier from
  [Strings: Indexing, Slicing, and Formatting](04-strings-indexing-slicing-and-formatting.md),
  prints `Average score: 86.2`.
- Without the explicit `int(raw_score)` conversion, `total += raw_score`
  would have tried to add a `str` to an `int`, raising a `TypeError`
  immediately — this example shows exactly why explicit conversion is
  often a required first step, not an optional nicety.

### Example 2 — Checking form data with truthiness

```python
form = {"name": "Ada", "email": "", "phone": "555-0142"}

filled_fields = []
for value in form.values():
    filled_fields.append(bool(value))

print(filled_fields)
print(f"All fields filled: {all(filled_fields)}")
print(f"At least one field filled: {any(filled_fields)}")
```

**Plain-English explanation:**

- `form` represents data a user submitted — `"email"` was left blank.
- The loop visits each value using `.values()` (from the dictionaries
  lesson), and `bool(value)` converts each one to `True` or `False` using
  truthiness: non-empty strings are truthy, the empty string is falsy.
  `filled_fields` ends up as `[True, False, True]`.
- `all(filled_fields)` checks whether **every** field was filled in:
  `False`, because `"email"` was empty.
- `any(filled_fields)` checks whether **at least one** field was filled
  in: `True`.
- This is a realistic, common pattern: converting a group of values to
  their truthiness with `bool()`, then summarizing them with `any()` and
  `all()`, instead of writing several separate `==` comparisons by hand.

### Example 3 — Safely parsing a batch of user-entered ages

```python
def parse_age(raw_value):
    try:
        return int(raw_value)
    except ValueError:
        return None

for raw_value in ["25", "thirty", "42"]:
    age = parse_age(raw_value)
    if age is None:
        print(f"'{raw_value}' is not a valid age.")
    else:
        print(f"Parsed age: {age}")
```

**Plain-English explanation:**

- `parse_age` wraps the `try`/`except ValueError` preview from Section 10
  inside a small, reusable function (from Module 1.1): it attempts the
  conversion and `return`s the real number if it succeeds, or `None` if it
  fails — turning a possible crash into a clear, checkable result instead.
- The `for` loop tries three different raw values, one of which
  (`"thirty"`) is not a valid number at all.
- `if age is None:` uses the exact rule from Section 7: since a real,
  valid age could theoretically be `0`, checking `is None` (rather than
  plain `if age:`) is what correctly distinguishes "this failed to parse"
  from "this parsed to a falsy-but-valid number."
- Running this prints:
  ```text
  Parsed age: 25
  'thirty' is not a valid age.
  Parsed age: 42
  ```
- This example ties together explicit conversion, the `try`/`except`
  preview, and the `is None` truthiness rule into one small, realistic,
  safe input-handling pattern.

## Common beginner mistakes

- **Assuming `input()` returns a number.** `input()` (covered in Stage 0
  and used throughout this course) always returns a `str`, even if the
  user types digits — convert it explicitly with `int()` or `float()`
  before doing arithmetic with it.
- **Converting invalid text with `int()` or `float()`** without expecting
  the possibility of `ValueError` — always consider whether the text
  actually came from a trusted, already-validated source.
- **Losing duplicates when converting a list to a set**, and being
  surprised the resulting collection is shorter than expected — this is
  `set()`'s defining behavior, not a bug.
- **Assuming collection order is always preserved after conversion.**
  Converting to a `set`, in particular, does not preserve order at all;
  only conversions that stay within ordered types (like `list()` on a
  tuple) reliably preserve order.
- **Treating `0`, `False`, `None`, and `""` as interchangeable**, just
  because they are all falsy. They are four different values with four
  different meanings, as you first learned in
  [Variables, Basic Types, and None](02-variables-basic-types-and-none.md).
- **Using `if value:` when the program specifically needs to distinguish
  "missing" from "a valid zero or empty value."** As Section 7 showed,
  reach for `if value is None:` (or a similarly explicit check) whenever
  that distinction actually matters.

## Try it yourself

Do not look up full solutions. Predict the output before running each one.

1. Convert the text `"17"` to an `int`, add `3` to it, and print the
   result together with its type using `type()`.
2. Predict, then check: what does `int(9.99)` give you? What about
   `int(-9.99)`? Explain the pattern in one sentence.
3. Write a small `try`/`except ValueError` block that attempts to convert
   the text `"twelve"` to an `int`, and prints a friendly message instead
   of crashing.
4. Given `raw_tags = ["python", "python", "ai", "beginner"]`, convert it
   to a set to find how many *distinct* tags there are.
5. Create a dictionary representing a survey response where one answer is
   legitimately `0` (for example, `{"rating": 0, "comment": "none yet"}`).
   Write the correct `is None`-based check to distinguish "rating is
   zero" from "rating was never answered" (even though, in this exact
   dictionary, it was answered).
6. Given `flags = [True, True, False]`, predict the output of `any(flags)`
   and `all(flags)` before running them.

## Summary

- Every value has a **type**; **implicit conversion** happens
  automatically in a few safe cases (like combining an `int` and a
  `float`), but most type combinations require **explicit conversion**.
- `int()` and `float()` convert suitable text or numbers, truncating
  decimals toward zero and raising `ValueError` on invalid text; `int()`
  optionally accepts a base for reading numbers like binary text.
- `str()` converts any value to text, which is what actually fixes the
  "cannot join text and a number with `+`" error from earlier lessons.
- `bool()` converts any value using **truthiness**: `False`, `None`,
  numeric zero, and every empty built-in collection are **falsy**;
  everything else is **truthy**.
- `list()`, `tuple()`, `set()`, and `dict()` convert between collection
  types, and can change order, remove duplicates, or fail if the input's
  shape does not fit.
- `type()` reports a value's exact type; `isinstance()` is usually the
  more practical, idiomatic way to check it.
- `if value:` is convenient but conflates every falsy value; use an
  explicit check like `if value is None:` whenever `0`, `False`, or `""`
  need to be treated as meaningfully different from "missing."
- `any()` and `all()` summarize a list of values using truthiness, without
  writing manual comparisons.
- A `try`/`except ValueError` block is an introductory way to handle a
  conversion that might fail, without crashing the program.

## Completion checklist

- [ ] I can explain the difference between implicit and explicit
      conversion, with an example of each.
- [ ] I can use `int()`, `float()`, and `str()`, and explain the errors
      each can raise.
- [ ] I can list Python's falsy values from memory and explain why
      everything else is truthy.
- [ ] I can explain when `if value:` is appropriate and when an explicit
      `is None` check is required instead.
- [ ] I can use `any()` and `all()` correctly on a list of values.
- [ ] I can convert between lists, tuples, sets, and dictionaries, and
      explain how order, duplicates, or shape can be affected.
- [ ] I can use `isinstance()` and explain why it is usually preferred
      over comparing `type(...) == ...`.
- [ ] I can write a simple `try`/`except ValueError` block.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

Type conversion and truthiness are constant, practical concerns in AI
systems: a tool's arguments often arrive as text and must be converted
before use, a model's response might contain a number formatted as a
string, and deciding whether a retrieved value is "present" often comes
down to exactly the `if value:` versus `if value is None:` distinction
from this lesson — treating a genuinely empty-but-valid result the same
as "nothing came back" is a realistic, easy-to-miss bug in retrieval and
tool-response handling. The `try`/`except ValueError` preview here is also
the first look at a pattern you will use constantly once real programs
receive input they cannot fully control: convert defensively, and handle
the failure clearly instead of letting it crash the whole system.

---

## Appendix: Conversion and Inspection Function Reference

This appendix collects every conversion and inspection function this
lesson covers, in one place, for quick reference. You do not need to
memorize this list — you have already seen every function below used and
explained in context above; this appendix exists purely so you can look
one up quickly later without re-reading the whole lesson.

#### `int(value)` / `int(text, base)`

Converts suitable text or a `float` to a whole number, truncating any
decimal part toward zero; the optional second form reads text as a number
in a given base.

```python
print(int("42"))       # 42
print(int(3.9))         # 3
print(int("101", 2))    # 5
```

**Common error:** `ValueError` on text that is not a valid whole number,
such as `int("abc")`.

#### `float(value)`

Converts suitable text or an `int` to a decimal number.

```python
print(float("3.14"))   # 3.14
print(float(7))          # 7.0
```

**Common error:** `ValueError` on text that is not a valid number, such as
`float("abc")`.

#### `str(value)`

Converts virtually any value into its text representation.

```python
print(str(30))     # 30      (as text, ready to concatenate with +)
print(str(True))    # True
print(str(None))    # None
```

**Warning:** `str(value)` almost never raises an error — nearly every
Python value can be turned into some text representation.

#### `bool(value)`

Converts any value to `True` or `False`, using truthiness (Section 7).

```python
print(bool(0))        # False
print(bool("hi"))     # True
```

**Warning:** `bool(value)` never raises an error either; every value has
a defined truthiness.

#### `list(iterable)`

Converts a suitable collection (a string, tuple, set, or dictionary's
keys) into a `list`.

```python
print(list("abc"))         # ['a', 'b', 'c']
print(list((1, 2, 3)))      # [1, 2, 3]
```

#### `tuple(iterable)`

Converts a suitable collection into a `tuple`.

```python
print(tuple([1, 2, 3]))   # (1, 2, 3)
```

#### `set(iterable)`

Converts a suitable collection into a `set`, automatically removing
duplicates and discarding order.

```python
print(set([1, 2, 2, 3]))   # {1, 2, 3}
```

#### `dict(pairs)`

Converts a collection of two-item pairs into a `dict`.

```python
print(dict([("a", 1), ("b", 2)]))   # {'a': 1, 'b': 2}
```

**Common error:** `ValueError` (or `TypeError`, depending on exactly what
was passed) if the input is not actually shaped as a collection of
two-item pairs.

#### `type(value)`

Returns a value's exact type.

```python
print(type(42))   # <class 'int'>
```

#### `isinstance(value, type)`

Returns `True` if `value` is of the given type, `False` otherwise; usually
the more practical, idiomatic choice for basic type validation (Section
9).

```python
print(isinstance(42, int))     # True
print(isinstance(42, str))     # False
```

#### `any(iterable)`

Returns `True` if at least one value in `iterable` is truthy.

```python
print(any([False, False, True]))   # True
```

#### `all(iterable)`

Returns `True` only if every value in `iterable` is truthy.

```python
print(all([True, True, False]))   # False
```
