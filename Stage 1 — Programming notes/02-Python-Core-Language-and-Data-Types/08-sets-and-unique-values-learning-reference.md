# Sets and Unique Values --- Complete Learning Reference

**Source lesson:** `08-sets-and-unique-values(1).md`

# Part 1 --- Lesson summary (under 1,200 words)

## 1. What a set is and when to use it

A **set** is an unordered collection of unique, hashable values. Use it
when you care which distinct values exist or need to test membership,
not their positions or how often they appeared. Examples include unique
website visitors, article tags, and comparing course rosters. A set
automatically removes duplicates:

``` python
numbers = {1, 2, 2, 3, 3, 3}
print(numbers)  # {1, 2, 3}
```

## 2. Creating sets and the empty-set trap

A set literal uses curly braces with one or more values:

``` python
colors = {"red", "green", "blue"}
empty_set = set()
empty_dict_not_set = {}
print(type(empty_set))           # <class 'set'>
print(type(empty_dict_not_set))  # <class 'dict'>
```

`{}` always creates an empty dictionary. Use `set()` for an empty set.

## 3. Membership and unordered behavior

`in` and `not in` test membership efficiently:

``` python
colors = {"red", "green", "blue"}
print("red" in colors)         # True
print("purple" in colors)      # False
print("purple" not in colors)  # True
```

Sets have no fixed order, so do not rely on their printed order, or use
indexing/slicing. `colors[0]` raises
`TypeError: 'set' object is not subscriptable`. If you need predictable
display order, use `sorted()`; it returns a list, and values must be
mutually comparable:

``` python
numbers = {5,  1, 4, 2, 3}
print(sorted(numbers))  # [1, 2, 3, 4, 5]
```

A mixed set of integers and strings cannot be sorted directly in Python
3.

## 4. Add, remove, and clear

``` python
colors = {"red", "green"}
colors.add("blue")
print(sorted(colors))  # ['blue', 'green', 'red']
colors.remove("red")
print(sorted(colors))  # ['blue', 'green']
colors.clear()
print(colors)          # set()
```

These methods mutate the original set. `.remove(value)` raises
`KeyError` if absent; `.discard(value)` silently does nothing if absent.

## 5. Set operations and relationships

Given `a = {1, 2, 3}` and `b = {2, 3, 4}`:

-   **Union**: all values in either set: `a.union(b)` or `a | b` →
    `{1, 2, 3, 4}`.
-   **Intersection**: shared values: `a.intersection(b)` or `a & b` →
    `{2, 3}`.
-   **Difference**: values in the first set but not second:
    `a.difference(b)` or `a - b` → `{1}`. Direction matters.
-   **Symmetric difference**: values in exactly one set:
    `a.symmetric_difference(b)` or `a ^ b` → `{1, 4}`.

Use `sorted(...)` when showing results in a predictable order.
Relationship checks return booleans rather than new sets:

``` python
a = {1, 2, 3}
print({1, 2}.issubset(a))       # True
print(a.issuperset({1, 2}))     # True
print(a.isdisjoint({10, 20}))   # True
```

Subset means every member of the smaller set is in the other; superset
is the reverse; disjoint means no shared members. Operators `<=`, `<`,
`>=`, `>` also test subset/superset (strict forms require unequal sets),
but named methods are clearer.

## 6. Hashability, conversions, and frozenset

Set members must be **hashable**, just like dictionary keys. Numbers,
strings, booleans, and tuples whose contents are all hashable can be
members. Lists and dictionaries cannot:

``` python
valid_set = {1, "two", False, (3, 4)}
invalid_set = {[1, 2]}  # TypeError: unhashable type: 'list'
```

Hashable and immutable are not synonyms, although many common hashable
built-ins are immutable.

Converting a list to a set removes duplicates, but loses original order:

``` python
numbers = [3, 1, 2, 3, 1, 4]
unique_numbers = set(numbers)
print(unique_numbers)           # order not guaranteed
back_to_list = list(unique_numbers)  # order not guaranteed
```

If first-seen order must be preserved, a set alone is not sufficient.
`frozenset` is an optional immutable set:

``` python
frozen = frozenset({1, 2, 3})
print(frozen)  # frozenset({1, 2, 3})
frozen.add(4)  # AttributeError: no add method
```

It supports membership and set operations, but not mutating methods.

## 7. Three lesson examples

**Unique visitors:**
`visitor_log = ["alice", "bob", "alice", "carol", "bob", "alice"]`;
`unique_visitors = set(visitor_log)`. `sorted(unique_visitors)` displays
`['alice', 'bob', 'carol']`; `len(visitor_log)` is 6 visits,
`len(unique_visitors)` is 3 distinct visitors, and
`"dave" in unique_visitors` is `False`.

**Course rosters:**
`python_students = {"Ada", "Grace", "Alan", "Linus"}` and
`data_students = {"Grace", "Linus", "Marie", "Katherine"}`. Intersection
gives `['Grace', 'Linus']`; Python-only difference gives
`['Ada', 'Alan']`; union gives
`['Ada', 'Alan', 'Grace', 'Katherine', 'Linus', 'Marie']`.

**Article tags:**
`article_a_tags = ["python", "tutorial", "beginner", "python"]`,
`article_b_tags = ["python", "advanced", "tips"]`; convert each to a
set. Intersection gives `['python']`; union gives
`['advanced', 'beginner', 'python', 'tips', 'tutorial']`;
`tags_a.issubset(all_unique_tags)` is `True`.

Common mistakes: using `{}` for an empty set; indexing/slicing; relying
on print order; inserting unhashable lists/dicts; assuming set-to-list
conversion restores order; confusing directional difference with
symmetric difference.

## 8. Complete set method appendix (17 public methods)

-   `add(value)`: insert one value; mutates, returns `None`.
-   `clear()`: remove all; mutates, returns `None`.
-   `copy()`: independent shallow set copy; returns new set.
-   `difference(other)`: values only in this set; new set; operator `-`.
-   `difference_update(other)`: remove other's values from this set;
    mutates, returns `None`.
-   `discard(value)`: remove if present, no error if absent; mutates,
    returns `None`.
-   `intersection(other)`: shared values; new set; operator `&`.
-   `intersection_update(other)`: keep only shared values in this set;
    mutates, returns `None`.
-   `isdisjoint(other)`: whether no values are shared; returns `bool`.
-   `issubset(other)`: whether every value here is in other; returns
    `bool`.
-   `issuperset(other)`: whether other is contained here; returns
    `bool`.
-   `pop()`: remove and return an arbitrary value; mutates; empty set
    raises `KeyError`.
-   `remove(value)`: remove required value; mutates; absent value raises
    `KeyError`.
-   `symmetric_difference(other)`: values in exactly one set; new set;
    operator `^`.
-   `symmetric_difference_update(other)`: replace this set with
    symmetric difference; mutates, returns `None`.
-   `union(other)`: all values from both; new set; operator `|`.
-   `update(other)`: add all values from other; mutates, returns `None`.

Remember the difference between new-set methods and in-place `*_update`
methods. `.pop()` chooses an arbitrary value, unlike list `.pop()` which
removes a position. Prefer `.discard()` when absence is normal,
`.remove()` when absence is an error. `copy()` returns a new set.

Inspect methods in your own Python installation:

``` bash
python3 -c "print([m for m in dir(set) if not m.startswith('_')])"
```

Related built-ins and operators:

``` python
numbers = {5, 3, 8, 1}
print(len(numbers))     # 4
print(sorted(numbers)) # [1, 3, 5, 8]
print(min(numbers))     # 1
print(max(numbers))     # 8

a = {1, 2, 3}
b = {2, 3, 4}
print(sorted(a | b))    # [1, 2, 3, 4]
print(sorted(a & b))    # [2, 3]
print(sorted(a - b))    # [1]
print(sorted(a ^ b))    # [1, 4]
print(set([1, 2, 2, 3]))       # {1, 2, 3}
print(frozenset([1, 2, 2, 3])) # frozenset({1, 2, 3})
```

`len`, `sorted`, `min`, and `max` work as expected; `min`/`max` need
mutually comparable values. `set()` and `frozenset()` accept iterables.
Check your Python version with `python3 --version`.

# Part 2 --- Current learning-level assessment

Your Stage 1 roadmap progresses from computational thinking into Python
fundamentals and data types, then control flow/functions/errors,
collections and algorithmic habits, files/structured data/CLI programs,
modules/code quality, testing/debugging, and object-oriented design.
Later modules cover production Python, data modelling, metaprogramming,
the standard library, binary/text processing, advanced testing,
performance, packaging, CPython internals, design patterns,
visualization, security, and refactoring. Planned projects include an
expense-ledger CLI, log-investigation CLI, data-quality/transformation
pipeline, and rule-based risk-review engine.

**Current position:** Early Stage 1, Python core language and
collections. You have progressed through strings, lists, tuples,
dictionaries, and now sets. This lesson reuses list conversion, loops,
membership checks, and collection concepts. The project tree describes
intended curriculum coverage, not proof of mastery. Since you have not
supplied independently executed outputs here, I can identify your
learning position but cannot certify practical proficiency. The
solutions below stay within the current and previously learned concepts:
variables, sets, lists, `in`, `len`, `sorted`, loops, conditionals, and
set operations.

# Part 3 --- All six exercises solved step by step (under 1,500 words)

## Exercise 1 --- Favorite fruits and membership

``` python
favorite_fruits = {"mango", "apple", "banana"}
print("mango" in favorite_fruits)
```

-   Curly braces with values create a set.
-   `"mango" in favorite_fruits` checks whether the value exists.
-   Because mango is present, the result is `True`.

Output: `True`

## Exercise 2 --- Count distinct tags

``` python
tags = ["a", "b", "a", "c", "b", "a"]
unique_tags = set(tags)
distinct_count = len(unique_tags)
print(distinct_count)
```

-   `tags` is a list and includes repeated values.
-   `set(tags)` removes duplicates, leaving `{"a", "b", "c"}`.
-   `len()` counts the unique members: three.

Output: `3`

## Exercise 3 --- Compare recipe ingredients

``` python
recipe_one = {"flour", "sugar", "eggs", "milk"}
recipe_two = {"sugar", "eggs", "butter"}

shared = recipe_one & recipe_two
only_first = recipe_one - recipe_two
combined = recipe_one | recipe_two

print(sorted(shared))
print(sorted(only_first))
print(sorted(combined))
```

-   Each recipe is represented as a set of ingredients.
-   `&` finds ingredients used by both recipes.
-   `-` finds ingredients in the first recipe but not the second.
-   `|` combines all ingredients and removes duplicates.
-   `sorted()` makes the printed order predictable.

Output:

``` text
['eggs', 'sugar']
['flour', 'milk']
['butter', 'eggs', 'flour', 'milk', 'sugar']
```

## Exercise 4 --- Check attendees against speakers

``` python
attendees = {"Ada", "Grace", "Alan"}
speakers = {"Ada", "Marie"}

no_overlap = attendees.isdisjoint(speakers)
print(no_overlap)
```

-   `isdisjoint()` returns `True` only when the two sets share no
    values.
-   Both sets contain `"Ada"`, so they are not disjoint.

Output: `False`

Meaning: At least one attendee is also a speaker (Ada).

## Exercise 5 --- Safely remove blue

``` python
colors = {"red", "green", "blue"}
colors.discard("blue")
print(sorted(colors))
```

-   `.discard("blue")` removes blue if present.
-   If blue is absent, it does nothing and does not raise an error.
-   `sorted()` displays the remaining set in a predictable order.

Output: `['green', 'red']`

## Exercise 6 --- Create and test a frozenset

``` python
numbers = {10, 20, 30}
frozen_numbers = frozenset(numbers)

print(frozen_numbers)
frozen_numbers.add(40)
```

-   `numbers` is an ordinary mutable set.
-   `frozenset(numbers)` creates an immutable set from its values.
-   Printing shows `frozenset({10, 20, 30})` (the displayed member order
    is not guaranteed).
-   `.add(40)` fails because a frozenset cannot be modified.

Expected final error:

``` text
AttributeError: 'frozenset' object has no attribute 'add'
```

Run the final line separately if you want to inspect the error without
interrupting earlier output.

------------------------------------------------------------------------

# Completion checklist

-   [ ] I can explain why a set stores unique values and has no
    positional order.
-   [ ] I know `{}` is an empty dictionary and `set()` is an empty set.
-   [ ] I can use `in` and `not in`.
-   [ ] I can add, remove, discard, and clear values.
-   [ ] I can use union, intersection, difference, and symmetric
    difference.
-   [ ] I can explain hashability and why lists/dictionaries cannot be
    members.
-   [ ] I understand list-to-set conversion loses original order.
-   [ ] I can explain what `frozenset` does.
-   [ ] I have run all six exercises and checked the outputs.
