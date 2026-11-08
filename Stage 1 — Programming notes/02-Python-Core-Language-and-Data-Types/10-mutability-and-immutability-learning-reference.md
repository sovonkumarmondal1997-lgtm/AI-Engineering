# Mutability and Immutability --- Learning Reference

## Part 1 --- Lesson Summary and Teaching Notes

### 1. Objects, references, and the "labels on boxes" model

Every Python value---such as `5`, `"Ada"`, or `[1, 2, 3]`---is an
**object**. A variable name is a reference (a label) bound to an object;
it does not contain a separate copy.

``` python
first_name = "Ada"
also_first_name = first_name

print(first_name)       # Ada
print(also_first_name)  # Ada
```

Both names refer to the same object: **aliasing**.

Reassignment moves one name to another object; it does not change the
old object:

``` python
first_name = "Ada"
also_first_name = first_name
first_name = "Grace"

print(first_name)       # Grace
print(also_first_name)  # Ada
```

`also_first_name` still refers to `"Ada"`.

### 2. Mutable and immutable types

A **mutable** object can be changed in place. An **immutable** object
cannot be changed in place; an apparent change creates a new result and
rebinds the variable.

  Immutable                Mutable
  ------------------------ ---------
  `int`, `float`, `bool`   `list`
  `str`                    `dict`
  `tuple`                  `set`
  `frozenset`, `None`      

For example, `age = age + 1` does not alter the original integer object.
It makes `age` refer to the result of the addition. Lists, dictionaries,
and sets can have their contents changed in place.

### 3. Reassignment versus mutation

These operations are different:

``` python
list_a = [1, 2, 3]
list_b = list_a          # alias
list_b = [9, 9, 9]       # reassignment

print(list_a)  # [1, 2, 3]
print(list_b)  # [9, 9, 9]
```

The second name now refers to a new list, so the first list is
unaffected.

``` python
list_a = [1, 2, 3]
list_b = list_a          # alias
list_b.append(4)         # mutation

print(list_a)  # [1, 2, 3, 4]
print(list_b)  # [1, 2, 3, 4]
```

`append()` changes the one shared list. Both names show the change
because both refer to that same object.

### 4. Equality (`==`) versus identity (`is`)

-   `==` compares values.
-   `is` asks whether two names refer to the exact same object.

``` python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)  # True: same values
print(a is b)  # False: separate lists
print(a is c)  # True: same object
```

Use `==` for ordinary value comparisons. Use `is` mainly to check
`None`:

``` python
value = None
print(value is None)  # True
```

Do not use `is` to compare ordinary strings or numbers. Python
implementations may reuse some immutable objects, so identity results
can be incidental. For example, `"hello"` and a string built using
`"".join(["h", "e", "l", "l", "o"])` can be equal without being the same
object.

`id(value)` returns an identity number. Comparing `id(a) == id(b)` can
help observe whether two names refer to the same object, but the number
itself has no useful meaning and may differ between runs.

### 5. Making copies: shallow copying

Plain assignment (`second = first`) creates an alias, not a copy. These
approaches make a new outer collection:

``` python
original = [1, 2, 3]
alias = original
copy_method = original.copy()
copy_slice = original[:]
copy_constructor = list(original)

alias.append(99)

print(original)          # [1, 2, 3, 99]
print(copy_method)       # [1, 2, 3]
print(copy_slice)        # [1, 2, 3]
print(copy_constructor) # [1, 2, 3]
```

All three copies are **shallow copies**: they copy the outer collection,
but nested mutable objects remain shared.

``` python
matrix = [[1, 2], [3, 4]]
shallow = matrix.copy()
shallow[0].append(99)

print(matrix)   # [[1, 2, 99], [3, 4]]
print(shallow)  # [[1, 2, 99], [3, 4]]
```

The inner list is shared. Deep copying can copy nested objects too, but
the lesson identifies that as a later-module topic; you do not need to
use it now.

### 6. Important edge cases

**A tuple can contain a mutable object.** The tuple's positions cannot
be reassigned, but a list stored in one position can still be changed:

``` python
record = ("Ada", [90, 85, 92])
record[1].append(100)
print(record)  # ('Ada', [90, 85, 92, 100])

record[0] = "Grace"  # TypeError: tuple does not support item assignment
```

Appending changes the inner list, not the tuple's slot. Assigning to
`record[0]` attempts to change a tuple slot and is rejected.

**`+=` depends on mutability.** For a list it changes the existing list
in place; for a tuple or string it creates a new result and rebinds the
name.

``` python
numbers = [1, 2, 3]
original_id = id(numbers)
numbers += [4]
print(numbers)                         # [1, 2, 3, 4]
print(id(numbers) == original_id)      # True

coordinates = (1, 2, 3)
original_id = id(coordinates)
coordinates += (4,)
print(coordinates)                     # (1, 2, 3, 4)
print(id(coordinates) == original_id)  # False
```

This difference matters when another variable aliases the same object:
list mutation is visible through aliases; tuple/string rebinding affects
only that variable name.

**Hashability.** Dictionary keys and set members must be hashable: their
hash must remain stable and agree with equality. Many immutable built-in
values are hashable, but mutability and hashability are not identical. A
tuple is hashable only if every item inside it is hashable:

``` python
valid_key = (1, 2)
data = {valid_key: "point"}  # valid

invalid_key = (1, [2, 3])
bad_data = {invalid_key: "point"}  # TypeError: unhashable type: 'list'
```

The inner list is unhashable, so the containing tuple is unhashable too.

### 7. Safe engineering habits

-   Copy a collection intentionally before changing it when you do not
    own it or cannot be sure nobody else uses it.
-   Avoid unexpectedly mutating shared input.
-   Use clear names such as `scores_copy`.
-   Test aliasing deliberately by making two names refer to one object
    and mutating through one.
-   Inspect with `print`, `==`, `is`, or `id()` rather than guessing.

### 8. The lesson's three practical examples

**Shopping cart:** `cart_b = cart_a` creates an alias.
`cart_b.append("milk")` changes the shared list, so both names show
`['apples', 'bread', 'milk']`. Later, `cart_b = ["eggs"]` reassigns only
`cart_b`; `cart_a` remains unchanged.

**Student record:** `student = ("Ada", [90, 85, 92])` is a tuple
containing a list. Appending `78` changes the inner list.
`sum(student[1]) / len(student[1])` calculates the updated average,
displayed with `f"Average: {average:.1f}"` as `Average: 86.2`. Using the
whole tuple as a dictionary key raises `TypeError` because it contains
an unhashable list.

**Curving scores safely:** Starting with `[55, 82, 91, 40]`, one method
uses `.copy()` and a `for position in range(len(curved_via_copy))` loop
to add five to each copied item. Another creates an empty list and
appends `score + 5` for each original score. Both produce
`[60, 87, 96, 45]` while leaving the original unchanged.

### 9. Common mistakes and quick reference

Do not assume assignment copies data, that `.copy()` duplicates nested
objects, or that everything inside a tuple is immutable. Avoid `is` for
value comparisons and do not use a tuple containing a list as a
dictionary key.

Quick reference: - `=` binds a name; it does not copy. - `==` compares
values; `is` compares identity (use it mainly for `None`). - `.copy()`,
`[:]`, `list(x)`, `dict(x)`, and `set(x)` create shallow outer copies;
`set()` also removes duplicates. - `+=` mutates a list in place but
creates a new tuple/string result.

**Applied AI connection:** Shared conversation history, tool inputs, or
agent state can be accidentally changed when components share a mutable
object. Copy intentionally, avoid unexpected mutation, name copies
clearly, and test aliasing.

------------------------------------------------------------------------

## Part 2 --- Current Learning-Level Assessment

### Position in the Stage 1 project tree

Your Stage 1 roadmap progresses from computational thinking and Python
fundamentals through control flow, collections, files/CLI programs,
modules, testing/debugging, and object-oriented design. It also contains
later advanced Python topics and practical projects such as a personal
expense ledger CLI, log investigation CLI, data-quality pipeline, and
rule-based risk review engine.

Based on the learning sequence available from our previous lessons, you
have covered the early Python core topics: variables and basic types,
operators, strings, lists, tuples/unpacking, dictionaries/lookups, sets,
type conversion, truthiness, and now mutability/immutability. This
lesson consolidates those collection concepts rather than introducing a
completely separate programming area.

**Current assessment:** You are progressing through the early Stage 1
Python foundations. You have encountered the concepts needed to
understand this lesson, but reading a lesson or having a roadmap does
not by itself prove independent proficiency. Your practical mastery is
still unverified until you can predict outputs, run the exercises,
explain aliasing versus copying, and debug mistakes without following a
solution.

The project tree is a learning plan, not evidence that every planned
module or project has been completed. Do not move to advanced copying or
unrelated topics yet. First become comfortable with the six exercises
below using only the concepts already introduced.

------------------------------------------------------------------------

## Part 3 --- All Six Exercises Solved Step by Step

### Exercise 1 --- Alias, mutate, then reassign

``` python
items_a = ["pen", "book"]
items_b = items_a          # Both names refer to the same list.

items_b.append("ruler")    # Mutates the shared list.
print(items_a)             # ['pen', 'book', 'ruler']
print(items_b)             # ['pen', 'book', 'ruler']

items_b = ["pencil"]       # Reassigns only items_b to a new list.
print(items_a)             # ['pen', 'book', 'ruler']
print(items_b)             # ['pencil']
```

Line by line: the assignment on line 2 creates an alias, not a copy.
`append()` changes the shared list, so both names show the new item. The
final assignment gives `items_b` a different list; it does not alter
`items_a`.

### Exercise 2 --- Compare string values and identities

``` python
a = "python"
b = "python"

print(a == b)  # True: the string values are equal.
print(a is b)  # Do not rely on this identity result.

c = "".join(["p", "y", "t", "h", "o", "n"])
print(a == c)  # True: both contain "python".
print(a is c)  # Do not rely on this for string comparison.
```

`==` is the correct test because the requirement is to compare text
values. `is` tests whether the names refer to one exact object. Python
may reuse some objects, so its result is an implementation detail, not a
reliable value comparison.

### Exercise 3 --- Dictionary alias and independent shallow copy

``` python
student = {"name": "Ada", "score": 90}
same_student = student

print(student is same_student)  # True: alias, same dictionary.

student_copy = student.copy()
print(student_copy is student)  # False: a different outer dictionary.
print(student_copy == student)  # True: currently equal contents.
```

The second name refers to the original dictionary, so identity is
`True`. `.copy()` creates a new outer dictionary. Its contents currently
match, so equality is `True`, but identity is `False`.

### Exercise 4 --- Show that a shallow copy shares nested lists

``` python
data = {"scores": [10, 20]}
data_copy = data.copy()          # New outer dictionary.

data_copy["scores"].append(30)    # Mutates the shared inner list.

print(data)                      # {'scores': [10, 20, 30]}
print(data_copy)                 # {'scores': [10, 20, 30]}
```

`.copy()` duplicates the dictionary structure, but the value stored
under `"scores"` is the same inner list in both dictionaries. Appending
through the copy therefore changes the list visible through the original
too.

### Exercise 5 --- Tuple containing a list: mutation and dictionary key

``` python
record = ("Ada", [90, 85])

record[1].append(92)       # Legal: changes the inner list.
print(record)              # ('Ada', [90, 85, 92])

records = {}
records[record] = "student"  # TypeError: unhashable type: 'list'
```

The tuple's slots remain unchanged, so changing the list inside it is
allowed. But dictionary keys must be hashable. This tuple contains a
list, which is unhashable, so Python raises `TypeError`.

### Exercise 6 --- Make a new sorted list without changing the input

``` python
given_list = [40, 10, 30, 20]

sorted_list = given_list.copy()  # Copy the outer list.
sorted_list.sort()               # Sort only the copy.

print(given_list)                # [40, 10, 30, 20]
print(sorted_list)               # [10, 20, 30, 40]
```

First, `.copy()` creates a separate list. Then `.sort()` changes that
separate list in place. The original list remains in its original order.
This uses only copying, lists, and a method already covered by the
lesson.

------------------------------------------------------------------------

## Final Practice Checklist

Before considering this lesson complete, make sure you can explain in
your own words:

-   Why `second = first` creates an alias rather than a copy.
-   Why mutating a shared list affects both variable names.
-   Why reassignment affects only the name being reassigned.
-   Why `==` compares values and `is` compares identity.
-   Why `.copy()` is shallow when nested mutable values exist.
-   Why a tuple can contain a list that changes, but cannot use that
    tuple as a dictionary key.
-   Why `+=` behaves differently for lists versus tuples and strings.
-   How to create a sorted copy while preserving the original list.
