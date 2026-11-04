# Mutability and Immutability — Simple Explanation

This lesson explains whether Python objects can be changed after creation, how variables share objects, and how to avoid accidental changes to data. These concepts are important because they explain many common Python bugs.

---

## 1. Objects and references

Every Python value is an object. A variable is not a box containing data; it is a name or label referring to an object.

```python
first = [1, 2, 3]
second = first
```

Both names refer to the same list. This is called aliasing.

If you reassign `first = [9, 9]`, only the `first` label moves to a new list. `second` still refers to the original list.

---

## 2. Mutable vs immutable objects

- **Mutable:** Can be changed in place without creating a new object.
- **Immutable:** Cannot be changed in place. An apparent change creates a new object.

| Immutable types | Mutable types |
|---|---|
| `int` | `list` |
| `float` | `dict` |
| `bool` | `set` |
| `str` | |
| `tuple` | |
| `frozenset` | |
| `None` | |

For example, changing a list with `.append()` mutates the existing list. Changing a number through reassignment points the variable to a different number.

---

## 3. Reassignment vs mutation

This is the most important distinction.

**Reassignment:** Changes where a variable points.

```python
a = [1, 2, 3]
b = a
b = [9, 9, 9]
```

`a` remains `[1, 2, 3]`.

**Mutation:** Changes the shared object itself.

```python
a = [1, 2, 3]
b = a
b.append(4)
```

Now both `a` and `b` show `[1, 2, 3, 4]`.

---

## 4. Equality vs identity

Python provides two different comparison operators:

- `==` checks whether two objects have the same value.
- `is` checks whether two names refer to the exact same object.

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)  # True
print(a is b)  # False
print(a is c)  # True
```

**Important rule:** Use `==` for normal value comparisons. Reserve `is` mainly for checking `None`:

```python
if value is None:
    print("No value")
```

`id()` can help observe object identity. Its returned number has no independent meaning and should not be relied on.

---

## 5. Copying mutable objects

Assignment does not create a copy. To create an independent outer collection, use:

```python
original = [1, 2, 3]

copy1 = original.copy()
copy2 = original[:]
copy3 = list(original)
```

These create shallow copies: the outer collection is new, but nested mutable objects are still shared.

```python
matrix = [[1, 2], [3, 4]]
shallow = matrix.copy()

shallow[0].append(99)
```

The change is also visible in `matrix`, because the inner list is shared. Deep copying, which independently copies nested objects, is mentioned as a later topic.

---

## 6. Important edge cases

A tuple can contain a mutable list.

```python
record = ("Ada", [90, 85, 92])

record[1].append(100)  # Allowed
record[0] = "Grace"    # TypeError
```

The tuple's positions cannot be reassigned, but the list stored inside it can be changed.

The `+=` operator behaves differently by type:

- **List:** modifies the existing list in place.
- **Tuple or string:** creates a new object and reassigns the variable.

The file uses `id()` to demonstrate this difference.

**Hashability:** Dictionary keys and set members must be hashable. A tuple is hashable only if every item inside it is hashable. Therefore, `(1, 2)` can be a dictionary key, but `(1, [2, 3])` cannot because lists are unhashable.

---

## 7. Safe engineering habits

1. Copy data intentionally before modifying it.
2. Avoid unexpectedly changing shared input.
3. Use clear names such as `scores_copy`.
4. Test aliasing by assigning two names to the same object and mutating it.
5. When uncertain, inspect values using `print()`, `==`, `is`, or `id()`.

---

## 8. Practical examples in the file

- **Shopping cart:** Two variables share one cart; adding milk through one changes both. Reassigning one variable to a new cart does not affect the other.
- **Student record:** A tuple contains a mutable score list. The scores can change, but the tuple cannot be a dictionary key because it contains an unhashable list.
- **Curving scores:** Either copy the original list before adding five to every score, or build a new list. Both approaches preserve the original data.

---

## 9. Common mistakes and practice

Avoid assuming assignment creates a copy, being surprised by shared mutations, expecting shallow copies to duplicate nested objects, using `is` instead of `==`, assuming tuple contents are all immutable, and using unhashable values as dictionary keys.

The six exercises ask you to test aliasing and reassignment, compare equality and identity, copy dictionaries, test nested shallow copies, examine tuple/hashability behavior, and create a sorted copy without changing the original list.

---

## 10. Complete reference and AI engineering connection

The appendix summarizes `=`, `==`, `is`, `id()`, `.copy()`, `list()`, `dict()`, `set()`, `[:]`, and `+=`, including their behavior and limitations.

In Applied AI and Agentic AI systems, accidental shared mutation can corrupt conversation history, tool inputs, or agent state. Copying intentionally and understanding object references help keep these systems predictable.

**Completion goal:** Understand objects, references, mutability, aliasing, reassignment, copying, identity, and hashability well enough to prevent accidental data changes.
