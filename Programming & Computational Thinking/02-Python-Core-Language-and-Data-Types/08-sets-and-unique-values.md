# Sets and Unique Values

## Why sets matter

Sometimes the question you need to answer is not "in what order are these
things?" (a list) or "what value is stored under this name?" (a
dictionary) — it is simply "what distinct things do I have, and does this
particular one belong among them?" A **set** is Python's tool for exactly
that: an unordered collection that automatically keeps only unique values
and answers membership questions extremely efficiently. Sets also give you
the mathematical operations you may already know from school — union,
intersection, difference — directly as working Python tools, useful
whenever you need to compare two groups of things: which visitors came on
both days, which tags two articles share, which items are in one list but
not another.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what a set is, when to use one, and that it automatically
  removes duplicate values.
- Create sets with set literals and `set()`, and explain why `{}` creates
  an empty dictionary rather than an empty set.
- Check membership with `in` and `not in`.
- Explain that sets are unordered, and know why indexing, slicing, and
  relying on printed order are all incorrect for sets.
- Add, remove, and clear values in a set.
- Perform and explain union, intersection, difference, symmetric
  difference, and subset/superset/disjoint checks, using both method and
  operator syntax.
- Explain which value types can be set members and why lists and
  dictionaries cannot.
- Convert between lists and sets to remove duplicates, and explain why the
  original order is not preserved.
- Recognize `frozenset` as an optional, immutable variant of a set.
- Use the most common set methods and built-in functions confidently, and
  know how to look up any other set method in the appendix.

## Prerequisites

- [Dictionaries and Lookups](07-dictionaries-and-lookups.md) — sets share
  the same `{}` syntax ambiguity with dictionaries, addressed directly in
  Section 3.
- [Lists: Mutation, Copying, and Aliasing](05-lists-mutation-copying-and-aliasing.md) —
  converting a list to a set to remove duplicates, in Section 9, assumes
  you are already comfortable with lists.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Set** | An unordered collection of unique values, usually written between curly braces, such as `{1, 2, 3}`. |
| **Set literal** | A set written directly in code using curly braces and comma-separated values. |
| **Unordered** | Having no fixed position or sequence; a set does not remember "first," "second," and so on. |
| **Membership** | Whether a particular value exists inside a collection, checked with `in` or `not in`. |
| **Hashable** | Able to be stored in a set (or used as a dictionary key) because the object has a stable hash value and consistent equality behavior. Many common hashable built-in values are immutable, but hashable and immutable are not synonyms. |
| **Union** | Every value that appears in either of two sets (or both). |
| **Intersection** | Only the values that appear in both of two sets. |
| **Difference** | The values that appear in one set but not in another. |
| **Symmetric difference** | The values that appear in exactly one of two sets, but not both. |
| **Subset** | A set whose every value also appears in another set. |
| **Superset** | A set that contains every value of another set. |
| **Disjoint** | Describes two sets that share no values at all. |
| **`frozenset`** | An immutable version of a set, which cannot be changed after creation. |

## Step-by-step explanation

### 1. What a set is, and when it is useful

A **set** is an unordered collection of values, written between curly
braces: `{"red", "green", "blue"}`. Use a set whenever you care about
*which distinct values exist* and need to check membership quickly, but do
not care about their order or how many times a value was originally
seen — tracking unique visitors to a page, tags applied to an article, or
which items two groups have in common.

### 2. Sets store unique values only

Creating a set from values that include duplicates keeps only one copy of
each:

```python
numbers = {1, 2, 2, 3, 3, 3}
print(numbers)   # {1, 2, 3}
```

This happens automatically, with no extra code required — a set simply
cannot contain the same value twice, by definition.

### 3. Creating sets

A **set literal** lists values directly between curly braces:

```python
colors = {"red", "green", "blue"}
```

**Creating an empty set:** curly braces alone, `{}`, do **not** create an
empty set — as you learned in the previous lesson, `{}` always creates an
empty **dictionary**. To create a genuinely empty set, you must use
`set()` instead:

```python
empty_set = set()
empty_dict_not_set = {}

print(type(empty_set))            # <class 'set'>
print(type(empty_dict_not_set))   # <class 'dict'>
```

This is one of the most common beginner mix-ups with sets: the moment a
set literal has at least one value, `{...}` correctly means "set" — but an
*empty* pair of curly braces always means "dictionary," with no exception.

### 4. Membership checks

`in` and `not in` check whether a value exists in a set — and do so very
efficiently, which is one of a set's biggest practical advantages over a
list for this exact question:

```python
colors = {"red", "green", "blue"}

print("red" in colors)      # True
print("purple" in colors)   # False
print("purple" not in colors)  # True
```

### 5. Sets are unordered

A set has **no fixed order** — it does not remember which value was added
first, and the order Python happens to print a set in should never be
relied on.

**Do not use indexes or slices** — sets do not support them at all:

```python
colors = {"red", "green", "blue"}
print(colors[0])
```

```text
TypeError: 'set' object is not subscriptable
```

**Do not rely on printed order** for anything your program's correctness
depends on — the order shown by `print(some_set)` is an implementation
detail, not a guarantee, and can even differ between separate runs for
some value types.

**Use `sorted()` when a predictable display order is required:**
`sorted(...)` (from earlier lessons) works on a set and always returns a
new, ordered **list**:

```python
numbers = {5, 1, 4, 2, 3}
print(sorted(numbers))   # [1, 2, 3, 4, 5]
```

### 6. Adding, removing, and clearing values

```python
colors = {"red", "green"}

colors.add("blue")
print(sorted(colors))   # ['blue', 'green', 'red']

colors.remove("red")
print(sorted(colors))   # ['blue', 'green']

colors.clear()
print(colors)   # set()
```

`.add()`, `.remove()`, and `.clear()` all mutate the set in place — this
lesson's appendix covers each in full, alongside `.discard()`, a safer
alternative to `.remove()` covered there too.

### 7. Set operations

Sets support the classic mathematical operations directly, each available
both as a **method** and as an **operator** — this lesson shows both, so
you can recognize either style when reading other people's code:

```python
a = {1, 2, 3}
b = {2, 3, 4}

print(sorted(a.union(b)))                    # [1, 2, 3, 4]   — everything in either set
print(sorted(a | b))                          # [1, 2, 3, 4]   — same result, operator form

print(sorted(a.intersection(b)))              # [2, 3]          — only what's in BOTH
print(sorted(a & b))                          # [2, 3]

print(sorted(a.difference(b)))                # [1]             — in a, but NOT in b
print(sorted(a - b))                          # [1]

print(sorted(a.symmetric_difference(b)))      # [1, 4]          — in exactly one, not both
print(sorted(a ^ b))                          # [1, 4]
```

**Union** combines everything; **intersection** keeps only shared values;
**difference** (`a - b`, read "a minus b") keeps what is unique to the
*first* set; **symmetric difference** keeps whatever is unique to *either*
set individually, excluding anything shared by both.

Three more comparisons check the *relationship* between two sets, rather
than building a new one:

```python
a = {1, 2, 3}
print({1, 2}.issubset(a))        # True   — every value in {1, 2} is also in a
print(a.issuperset({1, 2}))       # True   — a contains every value of {1, 2}
print(a.isdisjoint({10, 20}))      # True   — a and {10, 20} share nothing at all
```

A **subset** check asks "is everything in this smaller set also in the
other?"; a **superset** check is the same question asked from the other
direction; **disjoint** asks "do these two sets share nothing whatsoever?"

### 8. Hashable values

Just like dictionary keys from the previous lesson, set members must be
**hashable**. Many common hashable values are immutable, but hashability
and immutability are different concepts. Numbers, text, booleans, and
tuples (as long as everything inside the tuple is itself hashable) can all
be set members:

```python
valid_set = {1, "two", False, (3, 4)}
print(valid_set)   # some order of: {1, 'two', False, (3, 4)}
```

Lists and dictionaries **cannot** be set members, because they are
unhashable — for exactly the same reason they cannot be dictionary keys:

```python
invalid_set = {[1, 2]}
```

```text
TypeError: unhashable type: 'list'
```

A set relies on stable hashing and equality behavior to find its members
reliably, so every member must be hashable. Common mutable built-in objects
such as lists are unhashable, so Python refuses to put them in a set
rather than risking unreliable lookups.

### 9. Converting between lists and sets

Converting a list to a set is the standard, idiomatic way to **remove
duplicates**:

```python
numbers = [3, 1, 2, 3, 1, 4]
unique_numbers = set(numbers)
print(unique_numbers)   # some order of: {1, 2, 3, 4}

back_to_list = list(unique_numbers)
print(back_to_list)     # some order — NOT guaranteed to match the original
```

**Why the original order is not preserved:** a set never stored any order
information in the first place — as soon as `numbers` became a set, the
knowledge of "which value came first" was gone. Converting back to a list
with `list(...)` produces *a* list containing the same unique values, but
in whatever order the set currently holds them, which may or may not
resemble the original list's order. If you specifically need "unique
values, in their original first-seen order," a set alone is not the right
tool — that need is better met with a different technique, beyond this
lesson's scope.

### 10. `frozenset`: an optional, immutable set

Python also provides `frozenset`, an immutable version of a set — created
once, and never changeable afterward, in exactly the same spirit as a
tuple compared to a list:

```python
frozen = frozenset({1, 2, 3})
print(frozen)   # frozenset({1, 2, 3})

frozen.add(4)
```

```text
AttributeError: 'frozenset' object has no attribute 'add'
```

This is entirely **optional** for a beginner to use in your own code —
plain, mutable sets are correct for the overwhelming majority of everyday
situations in this course. Just recognize `frozenset` if you encounter it
in other code: it behaves like a regular set for membership checks and
set operations, but supports none of the mutating methods from Section 6.

## Examples

### Example 1 — Tracking unique visitors

```python
visitor_log = ["alice", "bob", "alice", "carol", "bob", "alice"]

unique_visitors = set(visitor_log)

print(sorted(unique_visitors))
print(f"Total visits: {len(visitor_log)}")
print(f"Unique visitors: {len(unique_visitors)}")
print("dave" in unique_visitors)
```

**Plain-English explanation:**

- `visitor_log` is a list (from Topic 5) recording every single visit, in
  order, including repeats — Alice visited three times.
- `set(visitor_log)` converts it into a set, automatically collapsing the
  repeated names down to one entry each.
- `sorted(unique_visitors)` gives a predictable display order for
  printing: `['alice', 'bob', 'carol']`.
- `len(visitor_log)` counts every visit, including repeats:
  `Total visits: 6`. `len(unique_visitors)` counts only distinct people:
  `Unique visitors: 3` — this contrast is exactly why sets are useful for
  this kind of question.
- `"dave" in unique_visitors` checks membership directly, printing
  `False`, since Dave never visited.

### Example 2 — Comparing two course rosters

```python
python_students = {"Ada", "Grace", "Alan", "Linus"}
data_students = {"Grace", "Linus", "Marie", "Katherine"}

both_courses = python_students & data_students
print(sorted(both_courses))

only_python = python_students - data_students
print(sorted(only_python))

all_students = python_students | data_students
print(sorted(all_students))
```

**Plain-English explanation:**

- Two sets represent students enrolled in two different courses.
- `python_students & data_students` (intersection) finds students taking
  **both** courses: `['Grace', 'Linus']`.
- `python_students - data_students` (difference) finds students in the
  Python course but **not** the data course: `['Ada', 'Alan']` — notice
  this is not symmetric; `data_students - python_students` would give a
  different result.
- `python_students | data_students` (union) finds every student enrolled
  in **either** course, with no duplicates, even though `"Grace"` and
  `"Linus"` belong to both:
  `['Ada', 'Alan', 'Grace', 'Katherine', 'Linus', 'Marie']`.
- This example shows exactly the kind of "compare two groups" question
  sets answer far more directly than writing the equivalent logic by hand
  with lists and loops.

### Example 3 — Finding shared tags between two articles

```python
article_a_tags = ["python", "tutorial", "beginner", "python"]
article_b_tags = ["python", "advanced", "tips"]

tags_a = set(article_a_tags)
tags_b = set(article_b_tags)

shared_tags = tags_a.intersection(tags_b)
print(sorted(shared_tags))

all_unique_tags = tags_a.union(tags_b)
print(sorted(all_unique_tags))

print(tags_a.issubset(all_unique_tags))
```

**Plain-English explanation:**

- Each article's tags start as an ordinary list, including one accidental
  duplicate (`"python"` twice in `article_a_tags`) — a very realistic
  situation for tags collected from user input.
- `set(article_a_tags)` and `set(article_b_tags)` both clean up duplicates
  and put each article's tags into a set, ready for set operations.
- `tags_a.intersection(tags_b)` finds the one tag both articles share:
  `['python']`.
- `tags_a.union(tags_b)` finds every distinct tag across both articles:
  `['advanced', 'beginner', 'python', 'tips', 'tutorial']`.
- `tags_a.issubset(all_unique_tags)` confirms that every one of article
  A's tags is, unsurprisingly, also present in the combined set of all
  tags: `True` — a sanity check that holds by definition for any union,
  useful here mainly to demonstrate `issubset()` in a realistic context.

## Common beginner mistakes

- **Writing `{}` expecting an empty set.** `{}` is always an empty
  dictionary; use `set()` for an empty set.
- **Trying to index or slice a set.** `my_set[0]` always raises
  `TypeError`; sets have no positions to index into.
- **Relying on the order a set prints in.** That order is not guaranteed
  and should never affect your program's logic; use `sorted(my_set)` if
  a predictable order is genuinely needed for display.
- **Trying to put a list (or dictionary) inside a set.** Set members must
  be hashable (lists and dictionaries are not); Python raises `TypeError`
  immediately.
- **Expecting `list(some_set)` to preserve the original list's order**
  after converting to a set and back — as Section 9 explained, the set
  never remembered that order in the first place.
- **Confusing `difference()` (`a - b`) with `symmetric_difference()`
  (`a ^ b`).** `a - b` only removes `b`'s values from `a`; `^` finds
  values unique to *either* set — these give different results whenever
  the two sets are not identical.

## Try it yourself

Do not look up full solutions. Predict the output before running each one.

1. Create a set of your three favorite fruits, then check whether
   `"mango"` is a member using `in`.
2. Given `tags = ["a", "b", "a", "c", "b", "a"]`, convert it to a set to
   find how many *distinct* tags there are, and print that count using
   `len()`.
3. Create two sets representing the ingredients of two recipes. Print
   which ingredients they share, which are unique to the first recipe,
   and all ingredients combined — using the operator forms (`&`, `-`,
   `|`).
4. Given `attendees = {"Ada", "Grace", "Alan"}` and
   `speakers = {"Ada", "Marie"}`, use `.isdisjoint()` to check whether any
   attendee is also a speaker, and explain in one sentence what the result
   means.
5. Write one line that safely removes `"blue"` from a set of colors
   without raising an error, even if `"blue"` might not be present (hint:
   look up `.discard()` in the appendix).
6. Create a `frozenset` from a small set of numbers, and confirm — by
   trying to call `.add()` on it and observing the error — that it truly
   cannot be changed.

## Summary

- A **set** is an unordered collection of unique values; use one to track
  distinct items or answer "does this exist?" quickly.
- Sets automatically remove duplicates; creating one from repeated values
  keeps only one copy of each.
- `{...}` with at least one value creates a set; `{}` alone always creates
  an empty **dictionary** — use `set()` for an empty set.
- Sets are **unordered**: no indexing, no slicing, and no relying on
  printed order; use `sorted(my_set)` when a predictable order is needed.
- Union (`|`), intersection (`&`), difference (`-`), and symmetric
  difference (`^`) each have both a method and an operator form; subset,
  superset, and disjoint checks compare two sets' relationship rather than
  building a new set.
- Set members must be **hashable**; lists and dictionaries are unhashable,
  so they cannot be set members.
- Converting a list to a set and back is the standard way to remove
  duplicates, but does not preserve the original order.
- `frozenset` is an optional, immutable variant of a set.

## Completion checklist

- [ ] I can explain what a set is and when it is a better choice than a
      list or dictionary.
- [ ] I can create sets with a literal and with `set()`, and explain why
      `{}` alone is a dictionary, not a set.
- [ ] I can check membership with `in` and `not in`.
- [ ] I can explain why sets are unordered and what that rules out.
- [ ] I can add, remove, and clear values in a set.
- [ ] I can perform union, intersection, difference, and symmetric
      difference, using both method and operator syntax.
- [ ] I can explain why lists and dictionaries cannot be set members.
- [ ] I can convert a list to a set to remove duplicates, and explain why
      order is not preserved.
- [ ] I have completed the "try it yourself" exercises above.
- [ ] I know the appendix exists and can find a set method in it when I
      need one.

## Connection to later Applied AI and Agentic AI engineering work

Sets show up constantly in exactly the kind of bookkeeping AI systems
need: which documents have already been retrieved and should not be
fetched again, which tools an agent is currently allowed to call, which
user IDs have already been processed in a batch job, or which words appear
in one piece of text but not another. The set operations from this
lesson — especially intersection and difference — are a direct, readable
way to answer "what's shared" and "what's different" between two
collections, instead of writing manual loops and `if` checks to do the
same comparison by hand. Recognizing when a problem is really a set
question, rather than a list or dictionary question, is a design skill
that will save you real complexity later.

---

## Appendix: Complete `set` Method Reference

This appendix was generated against the Python version installed in this
environment — check `python3 --version` yourself if you want to confirm
your own. Run
`python3 -c "print([m for m in dir(set) if not m.startswith('_')])"`
in a terminal at any time to list every public method your own installed
Python provides.

**You do not need to memorize this appendix.** Read through it once to
know what exists, get comfortable with the methods used throughout the
lesson above, and come back here as a reference whenever you need a
method you do not use every day. Every method below is a **public
instance method** of `set`; none of Python's internal "dunder" methods
(like `__len__`) or private methods are included. For every method, the
note explicitly states whether it **mutates** the original set or
**returns a new set or value** without changing it.

#### `add(value)`

Adds `value` to the set. If `value` is already present, nothing changes
(no error, no duplicate).

```python
colors = {"red", "green"}
colors.add("blue")
print(sorted(colors))   # ['blue', 'green', 'red']
```

**Mutates the set in place; returns `None`.**

#### `clear()`

Removes every value, leaving the set empty.

```python
colors = {"red", "green"}
colors.clear()
print(colors)   # set()
```

**Mutates the set in place; returns `None`.**

#### `copy()`

Returns a new, independent copy of the set.

```python
original = {1, 2, 3}
duplicate = original.copy()
duplicate.add(4)

print(sorted(original))    # [1, 2, 3]
print(sorted(duplicate))    # [1, 2, 3, 4]
```

**Does not mutate the original; returns a new set.**

#### `difference(other)`

Returns a new set containing values in this set but **not** in `other`.

```python
a = {1, 2, 3}
b = {2, 3, 4}
print(sorted(a.difference(b)))   # [1]
```

**Does not mutate either set; returns a new set.** Equivalent operator:
`a - b`.

#### `difference_update(other)`

Like `difference()`, but mutates this set in place instead of returning a
new one.

```python
a = {1, 2, 3}
a.difference_update({2, 3})
print(a)   # {1}
```

**Mutates the set in place; returns `None`.**

#### `discard(value)`

Removes `value` from the set if present. Unlike `.remove()`, does
**nothing** (no error) if `value` is not present.

```python
s = {1, 2, 3}
s.discard(2)
print(sorted(s))   # [1, 3]

s.discard(99)   # no error, even though 99 was never in s
print(sorted(s))   # [1, 3]
```

**Mutates the set in place if the value was present; returns `None`.**
Prefer `.discard()` over `.remove()` whenever "this value might already
be absent" is a normal possibility you do not want to treat as an error.

#### `intersection(other)`

Returns a new set containing only values present in **both** sets.

```python
print(sorted({1, 2, 3}.intersection({2, 3, 4})))   # [2, 3]
```

**Does not mutate either set; returns a new set.** Equivalent operator:
`a & b`.

#### `intersection_update(other)`

Like `intersection()`, but mutates this set in place instead of returning
a new one.

```python
a = {1, 2, 3}
a.intersection_update({2, 3, 4})
print(sorted(a))   # [2, 3]
```

**Mutates the set in place; returns `None`.**

#### `isdisjoint(other)`

Returns `True` if this set and `other` share **no** values at all.

```python
print({1, 2}.isdisjoint({3, 4}))   # True
print({1, 2}.isdisjoint({2, 3}))   # False
```

**Does not mutate; returns a `bool`.**

#### `issubset(other)`

Returns `True` if every value in this set also appears in `other`.

```python
print({1, 2}.issubset({1, 2, 3}))   # True
```

**Does not mutate; returns a `bool`.** Equivalent operator: `a <= b`.

#### `issuperset(other)`

Returns `True` if this set contains every value in `other`.

```python
print({1, 2, 3}.issuperset({1, 2}))   # True
```

**Does not mutate; returns a `bool`.** Equivalent operator: `a >= b`.

#### `pop()`

Removes and returns an **arbitrary** value from the set. Raises
`KeyError` if the set is empty.

```python
s = {1, 2, 3}
removed = s.pop()
print(type(removed))   # <class 'int'>
print(len(s))            # 2
```

**Mutates the set in place; returns the removed value.** "Arbitrary" here
means Python does not specify which element will be chosen, so your
program logic should not depend on which element is returned. This is a
consequence of sets having no defined order, unlike a list's `.pop()`,
which always removes from a specific, chosen position.

#### `remove(value)`

Removes `value` from the set. Raises `KeyError` if `value` is not
present.

```python
s = {1, 2, 3}
s.remove(2)
print(sorted(s))   # [1, 3]

s.remove(99)
```

```text
KeyError: 99
```

**Mutates the set in place if found; returns `None`.** This is the key
difference from `.discard()`: `.remove()` treats a missing value as an
error worth raising; `.discard()` treats it as a normal, silent no-op.
Use `.remove()` when a value's absence would itself indicate a bug in
your program; use `.discard()` when it would not.

#### `symmetric_difference(other)`

Returns a new set containing values that appear in **exactly one** of the
two sets, not both.

```python
print(sorted({1, 2, 3}.symmetric_difference({2, 3, 4})))   # [1, 4]
```

**Does not mutate either set; returns a new set.** Equivalent operator:
`a ^ b`.

#### `symmetric_difference_update(other)`

Like `symmetric_difference()`, but mutates this set in place instead of
returning a new one.

```python
a = {1, 2, 3}
a.symmetric_difference_update({2, 3, 4})
print(sorted(a))   # [1, 4]
```

**Mutates the set in place; returns `None`.**

#### `union(other)`

Returns a new set containing every value from **both** sets, with no
duplicates.

```python
print(sorted({1, 2}.union({2, 3})))   # [1, 2, 3]
```

**Does not mutate either set; returns a new set.** Equivalent operator:
`a | b`.

#### `update(other)`

Adds every value from `other` into this set, in place — the mutating
counterpart to `union()`.

```python
a = {1, 2}
a.update({3, 4})
print(sorted(a))   # [1, 2, 3, 4]
```

**Mutates the set in place; returns `None`.** This is the key difference
from `union()`: `union()` leaves both original sets untouched and hands
back a brand-new set; `update()` changes this set directly and returns
nothing. Choose `union()` when you want a new combined set while keeping
the originals; choose `update()` when you specifically want to grow this
set with more values.

## Appendix summary

That covers all 17 public, non-dunder methods on `set` available in this
Python installation. Come back to this reference whenever you need it —
you are not expected to remember all of it, only to know it exists and
how to find what you need.

## Appendix: Built-in Functions and Operators Used With Sets

```python
numbers = {5, 3, 8, 1}

print(len(numbers))      # 4     — how many values
print(sorted(numbers))   # [1, 3, 5, 8]  — a predictable, ordered list
print(min(numbers))       # 1     — smallest value, when values are comparable
print(max(numbers))       # 8     — largest value

a = {1, 2, 3}
b = {2, 3, 4}
print(sorted(a | b))   # [1, 2, 3, 4]   — union
print(sorted(a & b))   # [2, 3]          — intersection
print(sorted(a - b))   # [1]             — difference
print(sorted(a ^ b))   # [1, 4]          — symmetric difference
```

`len()`, `sorted()`, `min()`, and `max()` all work on sets exactly as you
would expect from the previous lessons — `min()`/`max()` require every
value to be mutually comparable (all numbers, for example), just as they
do for lists and tuples.

`set()` and `frozenset()` both build a new collection from any
iterable, such as a list:

```python
print(set([1, 2, 2, 3]))         # {1, 2, 3}
print(frozenset([1, 2, 2, 3]))   # frozenset({1, 2, 3})
```

The four set-relationship comparison operators — `<=`, `<`, `>=`, and
`>` — check subset and superset relationships directly:

```python
print({1, 2} <= {1, 2, 3})   # True   — subset (allows equal sets too)
print({1, 2} < {1, 2, 3})    # True   — proper subset (must be strictly smaller)
print({1, 2, 3} >= {1, 2})   # True   — superset (allows equal sets too)
print({1, 2, 3} > {1, 2})    # True   — proper superset (must be strictly larger)
```

**A beginner readability warning:** because `<=`, `<`, `>=`, and `>` also
mean ordinary numeric comparison everywhere else in Python, using them for
sets can look confusing to a reader who has not paused to remember that
the operands are sets, not numbers. The explicit method names —
`.issubset(...)` and `.issuperset(...)`, from the appendix above — say the
same thing far more clearly. This course recommends reaching for the
named methods in your own code, and only recognizing the operator forms
when reading code written by someone else.
