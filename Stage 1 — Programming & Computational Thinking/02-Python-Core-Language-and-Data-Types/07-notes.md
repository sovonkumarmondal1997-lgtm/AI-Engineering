# Dictionaries and Lookups

This lesson teaches you how to store structured information in Python and retrieve it using meaningful names instead of numerical positions. Dictionaries are essential for Data Engineering because they are commonly used for records, configurations, API responses, and data processing.

---

## 1. What is a dictionary?

A dictionary (`dict`) stores information as key-value pairs.

```python
person = {"name": "Ada", "age": 30}
```

- `"name"` and `"age"` are keys.
- `"Ada"` and `30` are values.

Unlike lists, which retrieve data using positions, dictionaries retrieve data using keys.

Create dictionaries:

```python
empty_dict = {}
scores = {"Ada": 95, "Grace": 88}
```

**Remember:** `{}` creates an empty dictionary, not an empty set.

---

## 2. Dictionary keys and values

- Keys must be unique and hashable.
- Common valid keys: strings, numbers, booleans, and tuples containing hashable values.
- Lists and dictionaries cannot be keys because they are unhashable.
- Values can be any type, including lists and dictionaries.
- If a key appears twice, the last value silently replaces the earlier one.

**An important detail:** `1`, `True`, and `1.0` compare equal in Python, so they refer to the same dictionary key.

---

## 3. Looking up values safely

**Direct lookup:**

```python
person = {"name": "Ada", "age": 30}

print(person["name"])
```

If the key does not exist, Python raises `KeyError`.

**Safer lookup:**

```python
person.get("email")          # None
person.get("email", "N/A")   # N/A
```

Use `.get()` when missing keys are expected. Use direct lookup when a missing key indicates a programming error.

---

## 4. Adding, updating, and removing data

```python
person["age"] = 30   # Add
person["age"] = 31   # Update
del person["age"]    # Remove
```

`del` raises `KeyError` if the key is missing.

For safer removal:

```python
removed = person.pop("age", "not found")
```

The `pop()` method removes the key and returns its value, or returns the default if missing.

---

## 5. Checking whether a key exists

```python
"name" in person       # True
"email" not in person  # True
```

**Important:** `in` checks dictionary keys, not values.

---

## 6. Iterating through dictionaries

| Syntax | What it returns |
|---|---|
| `for key in data` | Keys |
| `data.keys()` | All keys |
| `data.values()` | All values |
| `data.items()` | Key-value pairs |

Example:

```python
scores = {"Ada": 95, "Grace": 88}

for name, score in scores.items():
    print(name, score)
```

`.items()` is usually clearest when you need both the key and value. These methods return live dictionary views, which reflect changes to the dictionary.

---

## 7. Dictionary insertion order

Modern Python (3.7+) preserves insertion order.

However, do not make business logic depend on that order unless it is intentionally part of your design and documented.

---

## 8. Aliasing and copying

```python
original = {"a": 1}
alias = original
```

Both variables refer to the same dictionary. Changing one affects the other.

For an independent outer dictionary:

```python
copy_dict = original.copy()
```

This is a shallow copy: nested mutable values, such as lists, are still shared.

---

## 9. Common dictionary use cases

- Inventory: `{"apples": 50, "bread": 12}`
- User profiles: `{"name": "Ada", "email": "ada@example.com"}`
- Counting categories or word frequency.
- Configuration settings with default values.

The file demonstrates all four through inventory updates, category counting, and safe configuration lookup.

---

## 10. Complete dictionary method reference

The appendix covers these 11 methods:

| Method | Purpose |
|---|---|
| `clear()` | Remove everything |
| `copy()` | Create a shallow copy |
| `dict.fromkeys()` | Create keys with a shared starting value |
| `get()` | Safely retrieve a value |
| `items()` | Get key-value pairs |
| `keys()` | Get keys |
| `pop()` | Remove a selected key and return its value |
| `popitem()` | Remove and return the most recently inserted pair |
| `setdefault()` | Return existing value or insert a default |
| `update()` | Merge pairs into the existing dictionary |
| `values()` | Get values |

Important differences:

- `.get()` reads without modifying; `.setdefault()` inserts a missing key.
- `.update()` changes the original dictionary.
- `dict.fromkeys(keys, [])` shares the same list across all keys. Avoid this when each key needs its own list.

---

## 11. Other built-in functions and operators

- `len(data)`: number of key-value pairs.
- `list(data)`: list of keys.
- `sorted(data)`: sorted list of keys.
- `==`: compares dictionary contents, regardless of insertion order.
- `dict([("a", 1), ("b", 2)])`: creates a dictionary from two-item tuples.
- `|`: merges dictionaries into a new dictionary (Python 3.9+), without modifying the originals.

**Practice:** Build a book dictionary, update stock quantities, safely remove settings, count letters in `"mississippi"`, demonstrate aliasing and copying, and iterate using `.items()`.

**Connection to Data and AI Engineering:** Dictionaries represent API responses, structured model outputs, tool arguments, agent configurations, and retrieved records. Safe lookups and careful copying help prevent production bugs.

**Completion goal:** Understand dictionary creation, valid keys, lookups, mutation, iteration, insertion order, copying, methods, and merging.
