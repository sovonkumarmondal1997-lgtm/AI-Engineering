# Type Conversion and Truthiness --- Complete Learning Reference

**Source lesson:** `09-type-conversion-and-truthiness(1).md`

# Part 1 --- Complete lesson summary (under 1,200 words)

## 1. Why types and conversion matter

Every Python value has a **type**, which determines what operations are
valid. For example, `5` is an integer, `5.0` is a float, and `"5"` is
text. They may look similar to us, but Python treats them differently:

``` python
print(type(5))       # <class 'int'>
print(type(5.0))     # <class 'float'>
print(type("5"))     # <class 'str'>
print(type(True))    # <class 'bool'>
```

`5 + 1` works, but `"5" + 1` raises `TypeError`. **Type conversion**
deliberately changes a value from one type to another.

## 2. Implicit and explicit conversion

**Implicit conversion** happens automatically in a few compatible cases.
For example:

``` python
count = 3
price = 2.5
total = count * price
print(total)        # 7.5
print(type(total))  # <class 'float'>
```

Python produces a float when an integer and float are combined. But it
does not guess how to combine text and a number:

``` python
print("5" + 3)
# TypeError: can only concatenate str (not "int") to str
```

**Explicit conversion** means you request a conversion using a function
such as `int()` or `str()`.

## 3. Numeric and text conversions

-   `int(value)` converts suitable text or a float to an integer. A
    float is **truncated toward zero**, not rounded: `int(3.9)` is `3`;
    `int(-3.9)` is `-3`. Invalid text such as `int("abc")` raises
    `ValueError`. Optional base conversion: `int("101", 2)` gives `5`.
-   `float(value)` converts suitable text or an integer to a float:
    `float("3.14")` gives `3.14`; `float(7)` gives `7.0`. Invalid
    numeric text raises `ValueError`.
-   `str(value)` converts a value to text. For example, `age = 30`;
    `print("Age: " + str(age))` prints `Age: 30`. This fixes the earlier
    error from trying to concatenate a string and integer directly.
-   `bool(value)` converts a value to `True` or `False` according to
    truthiness.

## 4. Truthiness and `if`

**Truthiness** is how Python treats any value when a yes/no decision is
needed.

Standard falsy values include `False`, `None`, numeric zero (`0`,
`0.0`), and empty built-in collections/strings (`""`, `[]`, `()`, `{}`,
`set()`). Examples:

``` python
print(bool(False))  # False
print(bool(None))   # False
print(bool(0))      # False
print(bool(""))     # False
print(bool([]))     # False
print(bool({}))     # False
```

Standard truthy examples include `True`, non-empty strings, non-zero
numbers, and non-empty collections:

``` python
print(bool(True))      # True
print(bool("hello"))   # True
print(bool(42))        # True
print(bool([1, 2]))    # True
```

An `if` statement uses truthiness; it does not require a literal
boolean:

``` python
name = ""
if name:
    print("Name provided.")
else:
    print("No name provided.")
# No name provided.
```

But `if value:` treats `0`, `False`, `None`, and `""` alike. If zero is
a valid value and only `None` means "missing", use an explicit check:

``` python
score = 0
if score is None:
    print("Score not recorded yet.")
else:
    print(f"Score: {score}")
# Score: 0
```

Use `if value:` when all falsy values should count the same (for
example, checking whether a list is non-empty). Use `if value is None:`
when absence must be distinguished from valid zero, false, or empty
text.

`any(iterable)` is `True` if at least one element is truthy.
`all(iterable)` is `True` only if every element is truthy:

``` python
responses = [True, False, True]
print(any(responses))  # True
print(all(responses))  # False

scores = [0, 85, 90]
print(any(scores))     # True
print(all(scores))     # False
```

## 5. Collection conversion

The converters build a collection of the requested type:

``` python
print(list("abc"))                       # ['a', 'b', 'c']
print(tuple([1, 2, 3]))                   # (1, 2, 3)
print(set([1, 2, 2, 3]))                  # {1, 2, 3}
print(dict([("a", 1), ("b", 2)]))         # {'a': 1, 'b': 2}
```

`list()` makes a list from an iterable; `tuple()` makes a tuple; `set()`
removes duplicates and does not guarantee order; `dict()` needs two-item
key/value pairs. Wrong-shaped input such as `dict(["a", "b", "c"])`
raises `ValueError` because each element is not a key/value pair.
Conversion can therefore change order, remove duplicates, or fail.

## 6. Type inspection and safe conversion

`type(value)` reports the exact type. `isinstance(value, int)` asks
whether a value is an integer and returns a boolean. Although
`type(value) == int` works for the simple example, `isinstance()` is
generally the clearer, idiomatic validation check:

``` python
value = 42
print(type(value))              # <class 'int'>
print(type(value) == int)       # True
print(isinstance(value, int))   # True
```

Untrusted text may not convert. A `try`/`except ValueError` block
handles that failure rather than stopping the program:

``` python
user_input = "twenty"
try:
    age = int(user_input)
    print(f"Age: {age}")
except ValueError:
    print("That doesn't look like a valid number.")
# That doesn't look like a valid number.
```

This is only an introduction; full exception handling is taught in
Module 1.3.

## 7. The lesson's three practical examples

**Text-based scores:** `raw_scores = ["85", "92", "78", "90"]`. Start
`total = 0`, loop through each text score, add `int(raw_score)`,
calculate `average = total / len(raw_scores)`, and print
`f"Average score: {average:.1f}"`. Output: `Average score: 86.2`.
Conversion is necessary before arithmetic.

**Form completeness:**
`form = {"name": "Ada", "email": "", "phone": "555-0142"}`. Loop over
`form.values()`, append `bool(value)` to `filled_fields`, then use
`all(filled_fields)` and `any(filled_fields)`. The list becomes
`[True, False, True]`; all fields filled is `False`, at least one filled
is `True`.

**Parsing ages safely:** define `parse_age(raw_value)`, try
`return int(raw_value)`, and on `ValueError` return `None`. Loop over
`["25", "thirty", "42"]`; use `if age is None` to print an invalid-age
message, otherwise print the parsed age. Outputs: `Parsed age: 25`,
`'thirty' is not a valid age.`, `Parsed age: 42`. The explicit `None`
check avoids confusing a valid zero with a failed conversion.

## 8. Common mistakes and reference functions

Remember: `input()` always returns text; invalid numeric text can raise
`ValueError`; list-to-set conversion removes duplicates and does not
preserve order; and `0`, `False`, `None`, and `""` are different values
even though all are falsy. Do not use `if value:` when you need to
distinguish missing data from a valid zero or empty value.

The appendix recaps these functions: `int(value)` / `int(text, base)`,
`float(value)`, `str(value)`, `bool(value)`, `list(iterable)`,
`tuple(iterable)`, `set(iterable)`, `dict(pairs)`, `type(value)`,
`isinstance(value, type)`, `any(iterable)`, and `all(iterable)`. Their
behavior and examples are explained above. Check your Python version
with `python3 --version`; the lesson also includes a checklist for
testing these skills.

The lesson connects these ideas to AI and agentic systems: tool
arguments and model outputs may arrive as text, and an empty-but-valid
result must not be confused with a missing result. Convert defensively
and handle invalid input clearly.

# Part 2 --- Current learning-level assessment

Your Stage 1 project tree begins with computational thinking, then
Python core language and data types, control flow/functions/errors,
collections and algorithmic habits, files/structured data/CLI programs,
modules and code quality, testing/debugging, and object-oriented design.
It later expands into production Python, data modelling, advanced
testing, performance, packaging, security, refactoring, and projects
such as an expense-ledger CLI, log-investigation CLI, data-quality
pipeline, and rule-based risk-review engine.

**Your current position:** Early Stage 1, progressing through Python
core language and collection fundamentals. The completed sequence
includes strings, lists, tuples, dictionaries, sets, and now type
conversion and truthiness. This lesson combines those skills with basic
loops, conditionals, functions, and introductory error handling.

The roadmap shows what you intend to study; it does not prove mastery by
itself. Since no independently executed outputs are included with this
request, practical proficiency remains unverified. The solutions below
stay within the concepts already introduced in the lesson and earlier
Stage 1 topics. The `try`/`except` examples are kept to the lesson's
introductory `ValueError` pattern; I do not introduce advanced exception
handling.

# Part 3 --- All six exercises solved step by step (under 1,500 words)

## Exercise 1 --- Convert text, add, and inspect its type

``` python
number = int("17")
result = number + 3
print(result)
print(type(result))
```

-   `int("17")` converts the text `"17"` into integer `17`.
-   `number + 3` performs integer addition, producing `20`.
-   `print(result)` displays `20`.
-   `type(result)` checks the result's type: `int`.

Output:

``` text
20
<class 'int'>
```

## Exercise 2 --- Predict truncation

``` python
print(int(9.99))
print(int(-9.99))
```

-   `int(9.99)` removes the decimal portion; it does not round, so the
    result is `9`.
-   `int(-9.99)` also removes the decimal portion toward zero, so the
    result is `-9`, not `-10`.

Output:

``` text
9
-9
```

Rule: converting a float to an integer truncates toward zero.

## Exercise 3 --- Handle invalid numeric text

``` python
raw_value = "twelve"

try:
    number = int(raw_value)
    print(number)
except ValueError:
    print("Please enter a valid whole number.")
```

-   `raw_value` stores text, not a number.
-   `try` marks the conversion that might fail.
-   `int(raw_value)` cannot convert `"twelve"` and raises `ValueError`.
-   Python then runs the `except ValueError` block.
-   The friendly message is printed instead of allowing this conversion
    error to stop the program.

Output: `Please enter a valid whole number.`

## Exercise 4 --- Count distinct tags

``` python
raw_tags = ["python", "python", "ai", "beginner"]
unique_tags = set(raw_tags)
distinct_count = len(unique_tags)
print(distinct_count)
```

-   `raw_tags` is a list containing four entries, including a repeated
    `"python"`.
-   `set(raw_tags)` creates a set and removes the duplicate.
-   The distinct values are `"python"`, `"ai"`, and `"beginner"`.
-   `len(unique_tags)` counts those three distinct values.

Output: `3`

## Exercise 5 --- Distinguish a zero rating from no answer

``` python
survey = {"rating": 0, "comment": "none yet"}

if survey["rating"] is None:
    print("Rating was not answered.")
else:
    print(f"Rating: {survey['rating']}")
```

-   `survey` stores the rating and comment in a dictionary.
-   `survey["rating"]` looks up the rating using its key.
-   `is None` checks specifically whether the value is the special
    `None` value.
-   The rating is `0`, not `None`, so the `else` branch runs.
-   The f-string displays the actual rating.

Output: `Rating: 0`

If the rating were `None`, the first branch would report that it was not
answered. Do not use `if survey["rating"]:` here because zero is falsy
even though it is a valid answer.

## Exercise 6 --- Predict `any()` and `all()`

``` python
flags = [True, True, False]

print(any(flags))
print(all(flags))
```

-   `any(flags)` asks whether at least one item is truthy. There are
    `True` values, so it returns `True`.
-   `all(flags)` asks whether every item is truthy. One item is `False`,
    so it returns `False`.

Output:

``` text
True
False
```

------------------------------------------------------------------------

# Completion checklist

-   [ ] I can explain implicit versus explicit conversion.
-   [ ] I can use `int()`, `float()`, `str()`, and `bool()`.
-   [ ] I understand truncation toward zero and `ValueError`.
-   [ ] I can list the standard falsy values.
-   [ ] I know when to use `if value:` and when to use
    `if value is None:`.
-   [ ] I can use `any()` and `all()`.
-   [ ] I can convert between lists, tuples, sets, and dictionaries.
-   [ ] I can use `type()` and `isinstance()`.
-   [ ] I can write the introductory `try`/`except ValueError` pattern.
-   [ ] I have run all six exercises and checked the outputs.
