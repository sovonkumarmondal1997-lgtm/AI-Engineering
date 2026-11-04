# Tuples and Unpacking

This lesson explains how Python groups related values using tuples, why tuples cannot be changed like lists, and how to unpack their values into separate variables.

---

## 1. What is a tuple?

A tuple is an ordered collection of values that cannot be structurally changed after creation. It is useful when multiple values belong together as a fixed group.

```python
coordinates = (3, 5)
colors = ("red", "green", "blue")
empty_tuple = ()
```

**Tuple vs List:**

| List | Tuple |
|---|---|
| Mutable (changeable) | Immutable (unchangeable) |
| Uses `[]` | Usually uses `()` |
| Good for changing collections | Good for fixed records |
| Example: shopping cart | Example: coordinates |

Both preserve order, allow duplicates, support indexing, slicing, and iteration.

---

## 2. Creating tuples

Parentheses are optional because commas create the tuple.

```python
colors = "red", "green", "blue"
```

**Important: Single-item tuple**

A trailing comma is mandatory.

```python
single = (5,)       # Tuple
not_tuple = (5)     # Integer
```

The comma makes the difference, not the parentheses.

---

## 3. Indexing and slicing

Tuples work like lists when reading values.

```python
numbers = (10, 20, 10, 30)

print(numbers[0])    # 10
print(numbers[-1])   # 30
print(numbers[1:3])  # (20, 10)
```

- Indexing starts at `0`.
- Negative indexing starts from the end.
- Slicing creates a new tuple, not a list.
- The stop index is excluded.

---

## 4. Immutability

You cannot replace, add, or remove a tuple's own elements.

```python
point = (3, 5)
point[0] = 99
```

This raises `TypeError`.

However, reassignment is allowed:

```python
point = (99, 5)
```

This creates a new tuple and points the variable to it.

**Important exception:** A tuple can contain mutable objects, such as lists. Those objects can still change.

```python
container = ([1, 2],)
container[0].append(3)
# ([1, 2, 3],)
```

The tuple structure remains unchanged, but its contained list changes.

---

## 5. Packing and unpacking

**Packing:** Combining multiple values into one tuple.

```python
coordinates = 4, 9
```

**Unpacking:** Assigning tuple values to multiple variables.

```python
coordinates = (4, 9)
x, y = coordinates
```

The number of variables must match the number of values, otherwise Python raises `ValueError`.

**Swapping variables:**

```python
a = 1
b = 2

a, b = b, a
```

Python first evaluates and packs the right-hand values, then unpacks them into the left-hand variables. No temporary variable is needed.

**Multiple function return values:**

```python
def min_max(numbers):
    return min(numbers), max(numbers)

lowest, highest = min_max([4, 8, 1, 9])
```

Python packs the returned values into a tuple, which the caller unpacks.

---

## 6. Extended unpacking with `*`

Use `*rest` when you want to collect remaining values.

```python
numbers = (1, 2, 3, 4, 5)
first, *rest = numbers
```

Result: `first = 1`, `rest = [2, 3, 4, 5]`.

**Remember:** The starred variable receives a list, not a tuple. It can also appear in the middle:

```python
first, *middle, last = numbers
```

---

## 7. Converting tuples and lists

```python
coordinates_list = [3, 5]
coordinates_tuple = tuple(coordinates_list)
back_to_list = list(coordinates_tuple)
```

Use `list()` when you need to modify tuple data. Convert back using `tuple()` if you need an immutable result. Avoid unnecessary conversions.

---

## 8. Built-in functions and tuple methods

| Function / Method | Purpose |
|---|---|
| `len()` | Counts elements |
| `min()` / `max()` | Finds smallest/largest |
| `sum()` | Adds numeric elements |
| `sorted()` | Returns a new list in sorted order |
| `reversed()` | Returns a reverse iterator |
| `enumerate()` | Provides index and value |
| `count()` | Counts occurrences |
| `index()` | Finds first matching position |

`sorted()` and `reversed()` do not automatically return tuples. Use `tuple(sorted(scores))` if you need a sorted tuple.

The appendix covers both public tuple methods: `count()` and `index()`. `index()` raises `ValueError` if the value is missing.

---

## 9. Practical applications and common mistakes

Tuples are useful for:

- Fixed coordinates: `(latitude, longitude)`.
- Function results: `(lowest, highest, average)`.
- Small records: `("Ada", 1815)`.
- Lists of records, such as `[("Ada", 1815), ("Grace", 1906)]`, which can be unpacked directly in a `for` loop.

Avoid forgetting the single-item comma, trying to mutate a tuple, unpacking the wrong number of values, assuming `*rest` creates a tuple, and converting types unnecessarily. Also distinguish assignment `=` from comparison `==`.

**Practice exercises:** Create an RGB tuple, test single-item tuples, unpack a planet record, write a function returning total and count, use extended unpacking, and swap two variables.

**Connection to Data and AI Engineering:** Tuples can group fixed results such as `(model_response, confidence_score)` or `(tool_result, status_code)`. Unpacking makes these results easy to use in separate variables.

**Completion goal:** Understand tuple creation, indexing, immutability, packing, unpacking, extended unpacking, conversion, methods, and practical use cases.
