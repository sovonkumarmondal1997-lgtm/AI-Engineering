# Tuples and Unpacking

## Why tuples matter

In [Module 1.1's Sequence, Selection, Iteration, and Abstraction
lesson](../01-Computational-Thinking-and-Program-Design/04-sequence-selection-iteration-and-abstraction.md),
a function returned three counts at once — `return positive_count,
negative_count, zero_count` — and you were told, "this is called returning
a tuple of values, which you will study properly in Module 1.2." This
lesson is that promise kept. A **tuple** is Python's tool for grouping a
small, fixed set of related values together — a coordinate, a color, a
function's several results — with a built-in guarantee that those values
cannot be accidentally changed later. You will also learn **unpacking**,
the elegant technique for pulling a tuple's values back out into separate,
named variables in a single line, which you already saw briefly in that
same Module 1.1 example.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what a tuple is and decide when a tuple is a better choice than
  a list.
- Create tuples in every common way, including the single-item tuple, and
  explain why the trailing comma matters.
- Index, slice, and iterate over a tuple, and explain that tuples keep
  order and allow duplicates, just like lists.
- Explain why tuples are **immutable**, show the error that results from
  trying to change one, and explain the difference between mutating an
  item and reassigning the variable.
- Explain tuple **packing** and **unpacking**, and use unpacking to assign
  several variables at once, swap two variables, and capture a function's
  multiple return values.
- Use extended unpacking (`*rest`) to capture "everything else" from a
  tuple.
- Convert between tuples and lists with `tuple()` and `list()`, and
  explain when conversion is actually useful.
- Recognize the practical situations where a tuple is the right tool: a
  fixed coordinate, a function's related results, or a small record that
  should not change by accident.
- Use `count()`, `index()`, and the common built-in functions that work on
  tuples confidently.

## Prerequisites

- [Lists: Mutation, Copying, and Aliasing](05-lists-mutation-copying-and-aliasing.md) —
  tuples are best understood by contrast with lists, which this lesson
  refers back to constantly.
- [Sequence, Selection, Iteration, and Abstraction](../01-Computational-Thinking-and-Program-Design/04-sequence-selection-iteration-and-abstraction.md) —
  the `count_signs` example there already showed a first, informal preview
  of a function returning a tuple and that tuple being unpacked; this
  lesson formalizes exactly that pattern.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Tuple** | An ordered, **unchangeable** collection of values, usually written between round brackets, such as `(3, 5)`. |
| **Immutable** | Unable to be changed in place; every "change" to a tuple actually requires creating a different tuple. |
| **Packing** | Combining several values together into a single tuple, often just by separating them with commas. |
| **Unpacking** | Assigning a tuple's values to several variables at once, in one statement. |
| **Single-item tuple** | A tuple holding exactly one value, which requires a trailing comma (`(5,)`) to be recognized as a tuple at all. |
| **Extended unpacking** | Unpacking that uses `*name` to collect "all the remaining values" into a list, alongside ordinary variables. |
| **Record** | A small, fixed group of related values treated as one unit, such as a name paired with a birth year. |

## Step-by-step explanation

### 1. What a tuple is, and when it beats a list

A **tuple** is an ordered collection of values, written between round
brackets: `(3, 5)`. It looks and behaves a great deal like the lists from
the previous lesson — you can index it, slice it, and loop over it — with
one crucial difference: a tuple is **immutable**, meaning its contents can
never be changed after it is created. Reach for a tuple instead of a list
whenever the values genuinely belong together as a fixed, complete group
that should not grow, shrink, or change — a coordinate `(x, y)`, an RGB
color `(255, 0, 0)`, or a calendar date `(2024, 1, 15)`. Reach for a list
instead when you expect to add, remove, or reorder items over time, such as
a shopping cart or a to-do list.

### 2. Creating tuples

An **empty tuple** and a populated tuple:

```python
empty_tuple = ()
coordinates = (3, 5)
```

**Tuples without parentheses:** the parentheses are often optional — Python
recognizes a tuple by the **commas**, not the brackets. Both lines below
create identical tuples:

```python
colors = "red", "green", "blue"
print(colors)         # ('red', 'green', 'blue')
print(type(colors))   # <class 'tuple'>
```

Most Python code still uses parentheses anyway, purely for readability —
this course does the same, except where the parentheses are removed to
teach packing directly, in Section 5.

**Single-item tuples and the required comma:** this is the single most
common beginner trap with tuples. A trailing comma is **required** to
create a tuple with just one value — without it, Python just sees ordinary
parentheses around a single value, not a tuple at all:

```python
single_item = (5,)     # a one-item TUPLE
not_a_tuple = (5)      # just the int 5, in parentheses

print(type(single_item), single_item)   # <class 'tuple'> (5,)
print(type(not_a_tuple), not_a_tuple)   # <class 'int'> 5
```

The comma, not the parentheses, is what actually makes it a tuple —
`5,` (with no parentheses at all) is technically already a one-item tuple.
Writing `(5,)` is simply the clearer, conventional way to show that intent.

### 3. Ordering, duplicates, indexing, and slicing

Tuples share these behaviors with lists exactly: they keep the order
values were placed in, they allow duplicate values, and they support
zero-based indexing (including negative indexes) and slicing:

```python
numbers = (10, 20, 10, 30)

print(numbers[0])     # 10   — first item
print(numbers[-1])    # 30   — last item, negative index
print(numbers[1:3])   # (20, 10)  — a slice, itself a new tuple
```

Just as with lists, `numbers[1:3]` returns every item from index `1` up to,
but not including, index `3`. The one difference to notice: slicing a
tuple returns a **tuple**, not a list — the result always matches the type
of what you sliced.

### 4. Tuple immutability

A tuple's contents can never be changed once created — no item can be
replaced, added, or removed. Trying to assign to a tuple position raises an
error:

```python
point = (3, 5)
point[0] = 99
```

```text
TypeError: 'tuple' object does not support item assignment
```

This is deliberate: a tuple offers a guarantee that nothing else in your
program can quietly modify it behind your back — useful for exactly the
"small, fixed record" situations from Section 1.

**Mutating an item versus reassigning the variable:** immutability only
blocks changing a tuple's *contents*. It does **not** stop you from
pointing the same variable name at a completely different tuple:

```python
point = (3, 5)
point = (99, 5)
print(point)   # (99, 5)
```

This is not a contradiction. `point[0] = 99` tried to change the *existing*
tuple in place, which is forbidden. `point = (99, 5)` never touches the
original tuple at all — it builds a brand-new tuple and reassigns the name
`point` to point at it instead, exactly like reassigning any other
variable, as you learned in
[Values, Expressions, Statements, and Variables](../01-Computational-Thinking-and-Program-Design/02-values-expressions-statements-and-variables.md).

### 5. Tuple packing

**Packing** is combining several values together into one tuple. You have
already done this throughout this lesson — every time you wrote
`(3, 5)` or `3, 5`, you *packed* two values into one tuple. The parentheses
are often optional, as Section 2 showed:

```python
coordinates = 4, 9
print(coordinates)        # (4, 9)
print(type(coordinates))  # <class 'tuple'>
```

Even with no brackets in sight, Python still builds a genuine tuple here —
the comma alone is what signals "pack these values together."

### 6. Tuple unpacking

**Unpacking** is the reverse of packing: assigning a tuple's values to
several variables at once, in one statement, with the variable count
matching the tuple's length.

```python
coordinates = (4, 9)
x, y = coordinates

print(x)   # 4
print(y)   # 9
```

**Matching variable count to value count:** if the number of variables on
the left does not match the number of values in the tuple, Python raises
an error rather than guessing:

```python
coordinates = (4, 9, 1)
x, y = coordinates
```

```text
ValueError: too many values to unpack (expected 2, got 3)
```

**Swapping two variables without a temporary variable:** unpacking makes
Python's famous one-line swap possible:

```python
a = 1
b = 2
a, b = b, a
print(a, b)   # 2 1
```

Here is exactly why this works, and it depends on packing happening
*before* unpacking: Python first evaluates the entire right-hand side,
`b, a`, packing the *current* values of `b` and `a` into one temporary
tuple, `(2, 1)` — before it assigns anything at all. Only after that whole
tuple is built does Python unpack it into `a` and `b` on the left. Because
the right-hand side is fully packed first, using the original values of
both variables, there is no risk of overwriting `a` before `b` has had a
chance to read it — the usual reason other languages need a separate
temporary variable to swap two values safely.

**Unpacking a function's returned values:** as previewed in Module 1.1,
a function can `return` several values separated by commas — which
actually packs them into one tuple — and the caller can unpack that tuple
directly:

```python
def min_max(numbers):
    return min(numbers), max(numbers)

lowest, highest = min_max([4, 8, 1, 9])
print(lowest, highest)   # 1 9
```

`return min(numbers), max(numbers)` packs two values into a tuple behind
the scenes; `lowest, highest = min_max(...)` immediately unpacks that
tuple into two clearly named variables, in one readable line — much
clearer than working with one combined, unnamed value.

### 7. Extended unpacking with `*`

Sometimes you want just the first item (or the first and last), with
"everything else" collected together, without knowing in advance exactly
how many items that will be. A single starred name, `*rest`, does exactly
this:

```python
numbers = (1, 2, 3, 4, 5)
first, *rest = numbers

print(first)   # 1
print(rest)    # [2, 3, 4, 5]
```

`first` takes the one value at the start; `*rest` scoops up **every**
remaining value into a **list** (not a tuple — this is worth remembering,
since it is easy to assume it stays a tuple). The starred name can go
anywhere, including the middle, to capture everything between a fixed
first and last item:

```python
numbers = (1, 2, 3, 4, 5)
first, *middle, last = numbers
print(first, middle, last)   # 1 [2, 3, 4] 5
```

Keep extended unpacking to simple, clear cases like these — capturing "the
rest" of a small tuple — rather than more elaborate patterns.

### 8. Converting between tuples and lists

`tuple()` and `list()`, the same built-in functions you already used to
build a fresh list copy in the previous lesson, also convert between the
two types directly:

```python
coordinates_list = [3, 5]
coordinates_tuple = tuple(coordinates_list)
print(coordinates_tuple)   # (3, 5)

back_to_list = list(coordinates_tuple)
print(back_to_list)        # [3, 5]
```

**When conversion is useful:** if you receive a tuple but genuinely need
to mutate it — say, adding items in a loop — convert it to a list first
with `list(...)`, do the mutating work, and convert back with `tuple(...)`
only if the result specifically needs to be immutable again. **When
conversion is unnecessary:** do not reach for `tuple()` or `list()` out of
habit on data that already suits its current type well — if you never
need to mutate a group of values, a tuple usually needs no conversion at
all, and converting "just in case" adds a step without a real benefit.

### 9. Practical use cases

Three realistic situations where a tuple is the natural choice:

- **A fixed coordinate or pair of related values**, such as
  `location = (40.7128, -74.0060)` — a latitude and longitude that belong
  together and should not accidentally be edited separately.
- **A function returning several related values at once**, such as
  `min_max(...)` in Section 6 — the values are naturally grouped, and the
  caller unpacks them into clearly named variables immediately.
- **A small record that should not change accidentally**, such as
  `birth_record = ("Ada", 1815)` — pairing a name with a fixed fact about
  it, where accidentally overwriting one field later would be a real bug
  you want Python to prevent outright.

### 10. Built-in functions that work with tuples

The same general-purpose built-in functions from the lists lesson work
directly on tuples too:

```python
scores = (72, 95, 68, 88, 91)

print(len(scores))    # 5    — how many elements
print(min(scores))    # 68   — the smallest value
print(max(scores))    # 95   — the largest value
print(sum(scores))    # 414  — the total

print(sorted(scores))          # [68, 72, 88, 91, 95]  — a NEW list, not a tuple!
print(list(reversed(scores)))  # [91, 88, 68, 95, 72]  — also a list

for position, score in enumerate(scores):
    print(position, score)
```

```text
0 72
1 95
2 68
3 88
4 91
```

Notice `sorted(...)` and `reversed(...)` both hand back a **list**, even
though the input was a tuple — neither function tries to preserve
immutability for you. If you specifically need a sorted or reversed
**tuple** back, wrap the result in `tuple(...)`, as covered in Section 8:
`tuple(sorted(scores))`.

## Examples

### Example 1 — Representing a fixed point

```python
point = (12, 7)

print(point)
print(f"x = {point[0]}, y = {point[1]}")

try:
    point[0] = 99
except TypeError as error:
    print("Could not change the point:", error)
```

**Plain-English explanation:**

- `point = (12, 7)` packs two coordinates together as one fixed unit — a
  natural fit for a tuple, since a point's x and y values belong together
  and should not be edited separately by accident.
- The f-string reads each coordinate by index, exactly like a list:
  `x = 12, y = 7`.
- The `try`/`except` block (a preview of full exception handling, coming
  in Module 1.3) attempts the same illegal mutation from Section 4, and
  catches the resulting `TypeError` instead of letting it stop the
  program, printing:
  `Could not change the point: 'tuple' object does not support item assignment`.
- This is exactly the guarantee a tuple provides: `point` can be trusted
  to keep holding `(12, 7)` for as long as the variable exists, unless it
  is deliberately reassigned to an entirely new tuple.

### Example 2 — A function returning related values, unpacked

```python
def temperature_stats(readings):
    lowest = min(readings)
    highest = max(readings)
    average = sum(readings) / len(readings)
    return lowest, highest, average

readings = (18.5, 22.0, 19.5, 25.0, 20.5)
lowest, highest, average = temperature_stats(readings)

print(f"Lowest: {lowest}")
print(f"Highest: {highest}")
print(f"Average: {average:.1f}")
```

**Plain-English explanation:**

- `temperature_stats` computes three related numbers from one tuple of
  readings, and `return lowest, highest, average` packs all three into a
  single tuple to hand back to the caller — one function call, three
  results, cleanly grouped together.
- `lowest, highest, average = temperature_stats(readings)` immediately
  unpacks that returned tuple into three clearly named variables — far
  more readable than working with one unnamed, three-item result.
- The final three lines, reusing f-string formatting from
  [Strings: Indexing, Slicing, and Formatting](04-strings-indexing-slicing-and-formatting.md),
  print:
  ```text
  Lowest: 18.5
  Highest: 25.0
  Average: 21.1
  ```
- This is the packing-and-unpacking pattern from Section 6 in a realistic
  setting: a function that naturally produces several related results at
  once, consumed immediately with clear, individual names.

### Example 3 — Iterating over a list of small records

```python
birth_records = [("Ada", 1815), ("Grace", 1906), ("Alan", 1912)]

for name, year in birth_records:
    if year < 1900:
        print(f"{name} was born before 1900.")
    else:
        print(f"{name} was born in {year}.")
```

**Plain-English explanation:**

- `birth_records` is a **list** (from the previous lesson) whose elements
  are each a **tuple** (this lesson) — a very common real-world
  combination: a changeable collection of fixed, small records.
- `for name, year in birth_records:` unpacks each two-item tuple directly
  in the loop header, on every pass through the loop — `name` and `year`
  are freshly assigned from whichever tuple is currently being visited,
  without any separate indexing step.
- The `if`/`else` (from Module 1.1) then reports each record differently
  depending on the year, printing:
  ```text
  Ada was born before 1900.
  Grace was born in 1906.
  Alan was born in 1912.
  ```
- This example shows why tuples and lists work so well together: the list
  handles "however many records there happen to be," while each
  individual tuple guarantees that one record's fields stay bundled
  together and cannot be accidentally scrambled.

## Common beginner mistakes

- **Forgetting the trailing comma on a single-item tuple.** `(5)` is just
  the number `5`; `(5,)` is a one-item tuple. Always check with `type(...)`
  if you are unsure.
- **Trying to mutate a tuple like a list.** `point[0] = 99` always raises
  `TypeError`; if you need to change values, either build a new tuple with
  the updated values, or use a list instead from the start.
- **Confusing `=` assignment with `==` comparison.** As in every earlier
  lesson, `x = 5` assigns the value `5` to `x`; `x == 5` asks whether `x`
  is currently equal to `5` and produces `True` or `False`. This applies
  to unpacking too: `a, b = b, a` is an assignment (a swap), not a
  comparison.
- **Unpacking into the wrong number of variables.** `x, y = (1, 2, 3)`
  raises `ValueError: too many values to unpack`; `x, y, z = (1, 2)`
  raises the opposite error, about too *few* values. Count carefully, or
  use extended unpacking (`*rest`) when the count can vary.
- **Assuming `*rest` stays a tuple.** As Section 7 showed, the starred
  name in extended unpacking always collects its values into a **list**,
  even though it was unpacked from a tuple.
- **Converting between tuples and lists "just in case."** Reach for
  `tuple()` or `list()` only when you actually need the other type's
  behavior (mutability, or an immutability guarantee) — not as a default
  habit.

## Try it yourself

Do not look up full solutions. Predict the output before running each one.

1. Create a tuple holding your favorite color's RGB values, such as
   `(255, 105, 180)`. Print each component using indexing, then try to
   change one value and observe the error.
2. Write one line that creates a single-item tuple containing the number
   `7`, and one line that (by mistake) creates a plain `int` instead using
   the same number. Use `type()` to confirm the difference.
3. Given `record = ("Mercury", 0, 57_900_000)` (name, moon count, distance
   from the Sun in km), unpack it into three well-named variables and
   print a sentence describing the planet using an f-string.
4. Write a function that takes a list of numbers and returns both the
   total and the count as a tuple. Unpack the result into two variables at
   the call site.
5. Given `values = (10, 20, 30, 40, 50)`, use extended unpacking to
   capture the first value, the last value, and everything in between, in
   one line.
6. Swap the values of two variables, `first_name` and `last_name`, using
   the one-line swap technique — no temporary variable allowed.

## Summary

- A **tuple** is an ordered, **immutable** collection of values, written
  with round brackets (often optional); use one for a small, fixed group
  of related values that should not change.
- Tuples support indexing, negative indexes, slicing, and iteration, just
  like lists, and they allow duplicate values.
- A single-item tuple requires a trailing comma — `(5,)`, not `(5)`.
- Trying to change a tuple's contents raises `TypeError`; reassigning the
  variable to a brand-new tuple is a completely different, always-allowed
  operation.
- **Packing** combines several values into one tuple; **unpacking**
  assigns a tuple's values to several variables at once, and requires the
  variable count to match the value count.
- `a, b = b, a` swaps two variables safely, because Python fully packs the
  right-hand side into a temporary tuple before unpacking it into the
  left-hand names.
- Extended unpacking (`*rest`) captures "everything else" from a tuple
  into a list.
- `tuple()` and `list()` convert between the two types when you actually
  need the other type's behavior.

## Completion checklist

- [ ] I can create a tuple in each of the common ways, including a
      correct single-item tuple.
- [ ] I can index, slice, and iterate over a tuple.
- [ ] I can explain why tuples are immutable and show the error from
      trying to mutate one.
- [ ] I can explain the difference between mutating an item and
      reassigning the whole variable.
- [ ] I can unpack a tuple into matching variables, swap two variables in
      one line, and unpack a function's multiple return values.
- [ ] I can use extended unpacking (`*rest`) and explain that it produces
      a list.
- [ ] I can convert between tuples and lists, and explain when doing so is
      actually useful.
- [ ] I have completed the "try it yourself" exercises above.
- [ ] I know the appendix exists and can find a tuple method in it when I
      need one.

## Connection to later Applied AI and Agentic AI engineering work

Tuples are exactly the right tool whenever an AI system needs to hand back
several fixed, related pieces of information at once and guarantee they
will not be silently altered afterward — a model's response paired with
its confidence score, a tool call's result paired with a status code, or a
retrieved document paired with its relevance ranking. The unpacking
pattern from this lesson — `result, confidence = call_model(...)` — is one
you will write constantly once you are working with functions that wrap
AI calls or tool invocations, and reaching for an immutable tuple instead
of a list for this kind of fixed, small result communicates a clear
intent: "these values belong together, and nothing downstream should be
able to change them by accident."

---

## Appendix: Complete `tuple` Method Reference

This appendix was generated against the Python version installed in this
environment — check `python3 --version` yourself if you want to confirm
your own. Run
`python3 -c "print([m for m in dir(tuple) if not m.startswith('_')])"`
in a terminal at any time to list every public method your own installed
Python provides.

A tuple has far fewer methods than a list or a string — exactly **two** —
precisely *because* it is immutable: there is no `.append()`, `.remove()`,
`.sort()`, or any other method that would change a tuple's contents, since
none of that is allowed. Every method below is a **public instance
method**; none of Python's internal "dunder" methods (like `__len__`) or
private methods are included. Both methods below only ever **read**
information from the tuple — neither one mutates it, which could not be
otherwise for an immutable type.

#### `count(value)`

Returns how many times `value` appears in the tuple.

```python
numbers = (1, 2, 2, 3, 2)
print(numbers.count(2))   # 3
```

**Does not mutate the tuple (it cannot); returns an `int`.**

#### `index(value)`

Returns the position of the **first** element equal to `value`. Raises
`ValueError` if `value` is not found anywhere in the tuple.

```python
colors = ("red", "green", "blue")
print(colors.index("blue"))   # 2
```

```python
colors = ("red", "green", "blue")
print(colors.index("purple"))
```

```text
ValueError: tuple.index(x): x not in tuple
```

**Does not mutate the tuple (it cannot); returns an `int`, or raises
`ValueError` if the value is missing.**

## Appendix summary

That covers both public, non-dunder methods on `tuple` available in this
Python installation. Because a tuple is immutable, this is the complete
picture — there is no larger reference to grow into here, unlike the
appendices for `str` and `list`.
