# Sets and Unique Values — Simple Explanation

A set in Python is a collection that stores only unique values and does not maintain a fixed order. Use it when you want to find distinct items, check whether something exists, or compare two groups.

---

## 1. Why sets are useful

Unlike lists, which preserve order and allow duplicates, sets automatically remove duplicates.

```python
numbers = {1, 2, 2, 3, 3}
print(numbers)  # {1, 2, 3}
```

Common uses include tracking unique website visitors, article tags, and shared items between groups.

---

## 2. Creating sets

Use curly braces for a set containing values:

```python
colors = {"red", "green", "blue"}
```

**Important:** `{}` creates an empty dictionary, not an empty set.

```python
empty_set = set()
empty_dict = {}
```

---

## 3. Membership checking

Use `in` and `not in` to check whether a value exists.

```python
colors = {"red", "green", "blue"}

print("red" in colors)        # True
print("purple" not in colors) # True
```

Membership checking is one of the main advantages of sets.

---

## 4. Sets are unordered

Sets do not remember the positions of their elements.

- No indexing: `colors[0]` causes `TypeError`.
- No slicing.
- Never depend on the order displayed by `print()`.

Use `sorted()` when you need predictable display order. It returns a new list.

```python
numbers = {5, 1, 4, 2, 3}
print(sorted(numbers))  # [1, 2, 3, 4, 5]
```

All elements must be mutually comparable for sorting.

---

## 5. Adding and removing values

```python
colors = {"red", "green"}

colors.add("blue")    # Add
colors.remove("red")  # Remove; error if missing
colors.clear()        # Remove everything
```

These methods modify the original set. The appendix also explains `.discard()`, which safely removes a value without an error if it is absent.

---

## 6. Mathematical set operations

Suppose:

```python
a = {1, 2, 3}
b = {2, 3, 4}
```

| Operation | Operator | Meaning | Result |
|---|---|---|---|
| Union | `a \| b` | Everything in either set | `{1, 2, 3, 4}` |
| Intersection | `a & b` | Values shared by both | `{2, 3}` |
| Difference | `a - b` | Values in `a`, not `b` | `{1}` |
| Symmetric difference | `a ^ b` | Values in exactly one set | `{1, 4}` |

Each operation also has a method form, such as `.union()`, `.intersection()`, `.difference()`, and `.symmetric_difference()`.

Three relationship checks:

- `.issubset()`: Every value in one set exists in another.
- `.issuperset()`: One set contains every value of another.
- `.isdisjoint()`: Two sets have no shared values.

---

## 7. Hashable values

Set members must be hashable, meaning Python can reliably identify and look them up.

Numbers, strings, booleans, and tuples containing only hashable values can be members.

Lists and dictionaries cannot be members because they are unhashable.

---

## 8. Converting lists into sets

Use `set()` to remove duplicates from a list:

```python
numbers = [3, 1, 2, 3, 1, 4]
unique_numbers = set(numbers)
```

You can convert back using `list(unique_numbers)`, but the original order is not preserved.

---

## 9. Frozenset

`frozenset` is an immutable version of a set. Once created, it cannot be modified.

```python
frozen = frozenset({1, 2, 3})
frozen.add(4)  # AttributeError
```

It supports membership checks and set operations but not methods that modify the collection.

---

## 10. Practical examples

- **Unique visitors:** Convert visitor logs into a set to count distinct visitors.
- **Course rosters:** Use intersection to find students enrolled in both courses, difference to find students in only one, and union to combine all students.
- **Article tags:** Use sets to remove duplicate tags and identify shared tags.

---

## 11. Complete set method reference

The appendix covers all 17 public set methods:

| Method group | Methods |
|---|---|
| Add/remove | `add()`, `remove()`, `discard()`, `pop()`, `clear()` |
| Copy | `copy()` |
| Compare/combine | `union()`, `intersection()`, `difference()`, `symmetric_difference()` |
| Modify using another set | `update()`, `intersection_update()`, `difference_update()`, `symmetric_difference_update()` |
| Relationships | `issubset()`, `issuperset()`, `isdisjoint()` |

Important distinctions:

- `remove()` raises `KeyError` if the value is missing; `discard()` does not.
- `pop()` removes and returns an arbitrary value; it raises `KeyError` on an empty set.
- Methods ending in `_update()` modify the original set and return `None`.
- `union()` creates a new set; `update()` modifies the existing one.

The appendix also covers `len()`, `sorted()`, `min()`, `max()`, `set()`, `frozenset()`, and comparison operators (`<`, `<=`, `>`, `>=`). Named relationship methods are recommended for readability.

---

## 12. Common mistakes and practice

Avoid using `{}` for an empty set, indexing sets, relying on their printed order, inserting lists or dictionaries, expecting list order to survive conversion, and confusing difference with symmetric difference.

Practice by creating fruit sets, counting unique tags, comparing recipe ingredients, checking whether attendees and speakers overlap, safely removing a missing value with `.discard()`, and testing `frozenset` immutability.

---

## Connection to Applied AI and Agentic AI

Sets help track already-retrieved documents, permitted agent tools, processed user IDs, and unique words. They simplify comparisons between collections without requiring manual loops.

**Completion goal:** Understand when to choose a set over a list or dictionary, create and modify sets, perform all four set operations, and explain hashability and `frozenset`.
