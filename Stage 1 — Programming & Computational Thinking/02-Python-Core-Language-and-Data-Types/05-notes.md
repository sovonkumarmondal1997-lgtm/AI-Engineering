# Lists: Mutation, Copying, and Aliasing

This lesson explains how Python stores multiple values in a list, how to modify lists, and how to avoid bugs when multiple variables refer to the same list.

---

## 1. What is a list?

A list is an ordered, changeable collection of values. It is useful when you need to store several related items together.

```python
fruits = ["apple", "banana", "cherry"]
scores = [10, 20, 30]
empty_list = []
mixed = ["Ada", 30, True]
```

Key properties:

- Lists preserve the order in which items are added.
- Lists allow duplicate values.
- Lists can contain different data types.
- Lists are written using square brackets `[]`.

---

## 2. Indexing and slicing

Indexing accesses an individual element. Python starts counting from `0`.

```python
fruits = ["apple", "banana", "cherry"]

print(fruits[0])   # apple
print(fruits[-1])  # cherry
```

Negative indexes count backward: `-1` is the last item, `-2` is the second-last.

Accessing a position that does not exist raises `IndexError`. Use `len()` to check a calculated positive index before accessing it.

Slicing extracts multiple elements and creates a new list.

```python
numbers = [10, 20, 30, 40, 50]

numbers[1:3]   # [20, 30]
numbers[:2]    # [10, 20]
numbers[-2:]   # [40, 50]
numbers[::2]   # [10, 30, 50]
numbers[::-1]  # reversed list
```

The stop index is excluded. You can also check membership using `"banana" in fruits` or `"orange" not in fruits`; both return Boolean values.

---

## 3. Mutation: changing a list

Lists are mutable, meaning you can change the existing list without creating a new one.

```python
cart = ["apples", "bread"]

cart.append("milk")          # Add
cart[0] = "green apples"     # Replace
cart.remove("bread")         # Remove by value
cart.reverse()               # Reorder
cart.clear()                 # Remove everything
```

These operations modify the original list directly.

---

## 4. Mutating methods vs new results

Some operations change the original list and return `None`.

```python
numbers = [3, 1, 2]

result = numbers.sort()

print(numbers)  # [1, 2, 3]
print(result)   # None
```

Never write `numbers = numbers.sort()`: it replaces your list with `None`.

Use `sorted(numbers)` for a new sorted list. Use `list(reversed(numbers))` for a new reversed list.

---

## 5. Aliasing: two names, one list

Aliasing happens when two variables refer to the same list.

```python
first_list = [1, 2, 3]
second_list = first_list

second_list.append(4)

print(first_list)   # [1, 2, 3, 4]
```

Both names point to one list, so changing it through either name affects both. Reassignment to a new list is different: it changes what one variable refers to.

---

## 6. Copying lists

To create an independent outer list, use:

```python
copy_a = first_list.copy()
copy_b = first_list[:]
copy_c = list(first_list)
```

Changing these copied outer lists does not change the original.

**Shallow copying:** These methods copy only the outer list. If it contains nested lists, the inner lists remain shared.

```python
matrix = [[1, 2], [3, 4]]
shallow = matrix.copy()

shallow[0].append(99)  # Also changes matrix
```

For fully independent nested mutable objects, use `copy.deepcopy()` from Python's `copy` module.

---

## 7. Useful built-in functions and iteration

| Function | Purpose |
|---|---|
| `len()` | Counts elements |
| `min()` / `max()` | Finds smallest/largest |
| `sum()` | Adds numeric elements |
| `sorted()` | Returns a new sorted list |
| `reversed()` | Returns a reverse iterator |
| `enumerate()` | Provides index and value |
| `any()` | `True` if at least one value is truthy |
| `all()` | `True` if every value is truthy |

Use `for item in my_list` to visit elements in order.

---

## 8. Complete list-method reference

The appendix covers all 11 public list methods:

| Method | Purpose |
|---|---|
| `append()` | Add one item at the end |
| `extend()` | Add multiple items individually |
| `insert()` | Add an item at a position |
| `remove()` | Remove first matching value |
| `pop()` | Remove and return an item by index; defaults to last |
| `clear()` | Remove all items |
| `index()` | Find first matching position |
| `count()` | Count occurrences |
| `reverse()` | Reverse in place |
| `sort()` | Sort in place; supports `reverse=True` |
| `copy()` | Create a shallow copy |

**Remember:** `append()` adds an entire list as one item; `extend()` adds its elements individually. `remove()` works by value; `pop()` works by position.

---

## 9. Common mistakes and practical exercises

**Avoid:**

- Assuming assignment creates a copy.
- Assigning the result of `.sort()` or `.reverse()`.
- Accessing an invalid index.
- Confusing `.remove()` with `.pop()`.
- Assuming shallow copies independently copy nested lists.
- Assuming lists remove duplicates or enforce one data type.

**Practice:** Create a to-do list, calculate exam statistics without changing original order, demonstrate aliasing and copying, sort scores descending, and test shallow copying with nested lists.

**Why this matters in Data and AI Engineering:** Lists store batches of records, documents, conversation messages, retrieved results, and agent tool calls. Understanding mutation and copying prevents accidental changes to shared application data.

**Completion goal:** Be able to create, access, slice, modify, iterate over, copy, and safely manage nested lists.
