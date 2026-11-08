# Tuples and Unpacking

**Complete lesson summary, Stage 1 level assessment, and solved
exercises**

Source: `06-tuples-and-unpacking(1).md`

------------------------------------------------------------------------

## Part 1 --- Lesson summary (under 1,000 words)

### 1. What is a tuple, and when should you use one?

A **tuple** is an ordered collection of values. It is similar to a list,
but it is **immutable**: you cannot replace, add, or remove its own
elements after creation. Use a tuple for a small, fixed group of related
values, such as a coordinate `(x, y)`, RGB color, date, or function
results. Use a list when the collection needs to grow, shrink, or
change.

``` python
empty_tuple = ()
coordinates = (3, 5)
colors = "red", "green", "blue"
print(colors)        # ('red', 'green', 'blue')
print(type(colors))  # <class 'tuple'>
```

Python recognizes tuple packing by commas; parentheses are commonly used
for readability.

A one-item tuple needs a trailing comma:

``` python
single_item = (5,)
not_a_tuple = (5)
print(type(single_item))  # <class 'tuple'>
print(type(not_a_tuple))  # <class 'int'>
```

### 2. Ordering, duplicates, indexing, and slicing

Tuples preserve order, allow duplicates, use zero-based and negative
indexing, and support slicing just like lists. A slice returns another
tuple.

``` python
numbers = (10, 20, 10, 30)
print(numbers[0])    # 10
print(numbers[-1])   # 30
print(numbers[1:3])  # (20, 10)
```

### 3. Immutability: what can and cannot change

Changing a tuple element raises `TypeError`:

``` python
point = (3, 5)
point[0] = 99  # TypeError: tuple does not support item assignment
```

Reassigning the variable is different: it points the name at a new tuple
and is allowed.

``` python
point = (3, 5)
point = (99, 5)
print(point)  # (99, 5)
```

A tuple can contain a mutable object. The tuple's element reference
cannot be replaced, but the contained list can still be mutated:

``` python
container = ([1, 2],)
container[0].append(3)
print(container)  # ([1, 2, 3],)
```

Trying `container[0] = [9, 9]` still raises `TypeError`.

### 4. Packing and unpacking

**Packing** combines values into one tuple. **Unpacking** assigns its
values to separate variables. The number of ordinary target variables
must match the number of values.

``` python
coordinates = 4, 9
x, y = coordinates
print(x, y)  # 4 9
```

A mismatch such as `x, y = (4, 9, 1)` raises `ValueError`.

Unpacking makes swapping simple. Python evaluates and packs the
right-hand side before assigning the left-hand names:

``` python
a = 1
b = 2
a, b = b, a
print(a, b)  # 2 1
```

Functions can return several comma-separated values; Python packs them
into a tuple, which the caller can unpack:

``` python
def min_max(numbers):
    return min(numbers), max(numbers)

lowest, highest = min_max([4, 8, 1, 9])
print(lowest, highest)  # 1 9
```

### 5. Extended unpacking with `*`

A starred name captures the remaining values into a **list**, not a
tuple. It can appear at the start or middle:

``` python
numbers = (1, 2, 3, 4, 5)
first, *rest = numbers
print(first, rest)  # 1 [2, 3, 4, 5]

first, *middle, last = numbers
print(first, middle, last)  # 1 [2, 3, 4] 5
```

### 6. Convert between lists and tuples

Use `tuple()` and `list()` when you actually need the other type's
behavior---for example, convert a tuple to a list to mutate it.

``` python
coordinates_list = [3, 5]
coordinates_tuple = tuple(coordinates_list)
back_to_list = list(coordinates_tuple)
print(coordinates_tuple)  # (3, 5)
print(back_to_list)       # [3, 5]
```

Avoid conversions that serve no purpose.

### 7. Built-ins, methods, and practical examples

Tuples work with `len`, `min`, `max`, `sum`, `sorted`, `reversed`, and
`enumerate`. Note: `sorted(tuple)` returns a **list**; `reversed(tuple)`
returns an iterator, and `list(reversed(tuple))` makes a list. Wrap with
`tuple(...)` if you need a tuple result.

``` python
scores = (72, 95, 68, 88, 91)
print(len(scores), min(scores), max(scores), sum(scores))  # 5 68 95 414
print(sorted(scores))  # [68, 72, 88, 91, 95]
for position, score in enumerate(scores):
    print(position, score)
```

Three lesson examples:

-   **Fixed point:** `point = (12, 7)`; print the tuple and use
    `point[0]`/`point[1]` in an f-string. A `try`/`except TypeError`
    catches the error if you attempt `point[0] = 99`.
-   **Temperature statistics:** a function calculates `min`, `max`, and
    `sum(readings) / len(readings)`, returns all three as a tuple, and
    the caller unpacks them. For `(18.5, 22.0, 19.5, 25.0, 20.5)`,
    output is `Lowest: 18.5`, `Highest: 25.0`, `Average: 21.1`.
-   **Birth records:** a list contains tuples such as `("Ada", 1815)`.
    `for name, year in birth_records` unpacks each record; an
    `if`/`else` prints whether the person was born before 1900.

Common mistakes include forgetting the single-item comma, assuming
everything inside a tuple is immutable, trying to mutate a tuple,
confusing `=` with `==`, unpacking the wrong number of values, assuming
`*rest` is a tuple, and converting types unnecessarily.

### 8. Complete tuple method appendix

A tuple has only **two public non-dunder methods**, because it cannot be
changed:

-   `count(value)` returns the number of occurrences. Example:
    `(1, 2, 2, 3).count(2)` gives `2`.
-   `index(value)` returns the position of the first match. Example:
    `("red", "green", "blue").index("blue")` gives `2`; a missing value
    raises `ValueError`.

The lesson also shows `dir(tuple)` and this terminal command to inspect
methods in your installed Python:

``` bash
python3 -c "print([m for m in dir(tuple) if not m.startswith('_')])"
```

Tuples are useful in later AI systems for fixed result groups, such as a
model response with a confidence score or a tool result with a status
code.

------------------------------------------------------------------------

## Part 2 --- Current learning-level assessment from the entire Stage 1 project tree

Your Stage 1 tree starts with computational thinking and program design,
then Python fundamentals (variables, types, operators, strings, lists,
and now tuples). It continues into control flow, functions, scope and
errors; collections and algorithmic habits; files, structured data and
CLI programs; modules, packages and code quality; testing/debugging; and
object-oriented design and data modelling. Advanced modules cover
production Python, the data model, metaprogramming, the standard
library, binary/text processing, modern Python, advanced testing,
performance, packaging, CPython internals, design patterns,
visualization, security, refactoring, and functions/OOP gaps. Projects
include an expense-ledger CLI, log-investigation CLI,
data-quality/transformation pipeline, and rule-based risk-review engine.

**Assessment:** You are progressing through the early Python Core
Language/Data Types portion of Stage 1. This tuple lesson builds
directly on lists and the earlier sequence/unpacking preview. The
project tree describes planned coverage, not demonstrated mastery. Since
you have not supplied independently run exercise outputs here, I can
assess your curriculum position but cannot certify practical
proficiency. The solutions below use the lesson's concepts and
previously introduced foundations: variables, types, lists, indexing,
loops, conditionals, functions, built-ins, and f-strings.

------------------------------------------------------------------------

## Part 3 --- All six exercises solved step by step (under 1,500 words)

### Exercise 1 --- RGB tuple, indexing, and attempted mutation

``` python
rgb_color = (255, 105, 180)
print(rgb_color[0])
print(rgb_color[1])
print(rgb_color[2])
rgb_color[0] = 0
```

-   The tuple stores red, green, and blue components in that order.
-   Indexes `0`, `1`, and `2` print the three values.
-   The last line attempts to replace the first element. It raises
    `TypeError` because tuples are immutable. Run that final line
    separately if you want to see the error without stopping the earlier
    prints.

Output before the error:

``` text
255
105
180
TypeError: 'tuple' object does not support item assignment
```

### Exercise 2 --- One-item tuple versus integer

``` python
one_item_tuple = (7,)
plain_integer = (7)

print(type(one_item_tuple))
print(type(plain_integer))
```

-   `(7,)` has a comma, so Python creates a tuple.
-   `(7)` is just the integer `7` inside parentheses.
-   `type()` confirms the difference.

Output:

``` text
<class 'tuple'>
<class 'int'>
```

### Exercise 3 --- Unpack the planet record

``` python
record = ("Mercury", 0, 57900000)
planet_name, moon_count, distance_km = record

print(f"{planet_name} has {moon_count} moons and is {distance_km} km from the Sun.")
```

-   `record` groups the planet name, moon count, and distance.
-   The three variable names on the left unpack the three tuple values
    in order.
-   The f-string inserts each value into the sentence.

Output:

``` text
Mercury has 0 moons and is 57900000 km from the Sun.
```

### Exercise 4 --- Function returns total and count

``` python
def get_total_and_count(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total, count

scores = [10, 20, 30, 40]
total_score, number_of_scores = get_total_and_count(scores)

print(total_score)
print(number_of_scores)
```

-   The function receives a list of numbers.
-   `sum(numbers)` calculates the total; `len(numbers)` counts the
    items.
-   `return total, count` packs both results into a tuple.
-   The call-site assignment unpacks the returned tuple into two
    descriptive variables.

Output:

``` text
100
4
```

### Exercise 5 --- Capture first, middle, and last values

``` python
values = (10, 20, 30, 40, 50)
first, *middle, last = values

print(first)
print(middle)
print(last)
```

-   `first` receives the first value (`10`).
-   `last` receives the final value (`50`).
-   `*middle` collects all remaining values into a list
    (`[20, 30, 40]`).

Output:

``` text
10
[20, 30, 40]
50
```

### Exercise 6 --- Swap first and last names

``` python
first_name = "Ada"
last_name = "Lovelace"

first_name, last_name = last_name, first_name

print(first_name)
print(last_name)
```

-   The right-hand side is evaluated first, using the original values:
    `("Lovelace", "Ada")`.
-   Python then unpacks those values into the two names.
-   No temporary variable is required.

Output:

``` text
Lovelace
Ada
```

------------------------------------------------------------------------

## Completion checklist

-   [ ] I can create empty, multi-item, and single-item tuples.
-   [ ] I understand why `(7,)` is a tuple but `(7)` is an integer.
-   [ ] I can index, slice, and iterate over tuples.
-   [ ] I can explain tuple immutability versus variable reassignment
    and mutable objects inside tuples.
-   [ ] I can pack and unpack values, swap variables, and unpack
    function results.
-   [ ] I understand that `*rest` collects values into a list.
-   [ ] I can convert between lists and tuples when necessary.
-   [ ] I can use `count()`, `index()`, and the built-ins covered in the
    lesson.
-   [ ] I have run all six exercises and checked the outputs.
