# 07 — Python Dictionary Methods

> **Audience:** Beginner Python learner progressing toward data engineering  
> **Focus:** Every public, non-dunder dictionary method, how it behaves, what it returns, whether it mutates the original dictionary, and where it is useful in data-engineering code.

---

## 1. Learning objectives

After completing this lesson, you should be able to:

1. Create dictionaries and access their keys and values safely.
2. Use all 11 public, non-dunder dictionary methods without skipping any.
3. Distinguish methods that mutate a dictionary from methods that only read it or create a new object.
4. Understand dictionary views and why they are *live* rather than frozen snapshots.
5. Avoid shared mutable defaults when using `dict.fromkeys()`.
6. Build dictionaries from pairs, inspect them, compare them, and merge them.
7. Apply dictionaries to configuration, API responses, records, counters, and data pipelines.

## 2. What is a dictionary?

A Python dictionary stores data as **key-value pairs**. A key identifies a value.

```python
student = {
    "name": "Ada",
    "age": 20,
    "course": "Python",
}

print(student)
print(student["name"])
```

**Output**

```text
{'name': 'Ada', 'age': 20, 'course': 'Python'}
Ada
```

In this example:

- `"name"`, `"age"`, and `"course"` are keys.
- `"Ada"`, `20`, and `"Python"` are values.
- `student` is the dictionary variable.

### 2.1 Important dictionary rules

- Dictionary keys must be **hashable**. Common examples are strings, integers, and tuples containing only hashable values.
- Values can be of many types, including strings, numbers, lists, other dictionaries, and custom objects.
- Keys are unique. Assigning a value to an existing key replaces its previous value.
- Insertion order is guaranteed in Python 3.7 and later. Updating an existing key does not move it to the end.
- Dictionaries are mutable: entries can be added, changed, and removed.

```python
record = {"id": 101, "status": "new"}
record["status"] = "processed"  # Replace an existing value.
record["source"] = "api"        # Add a new key-value pair.
print(record)
```

**Output**

```text
{'id': 101, 'status': 'processed', 'source': 'api'}
```

---

## 3. Understand the method behavior before using it

The following table covers all 11 public, non-dunder dictionary methods in this lesson.

| Method | Main purpose | Mutates original dictionary? | Typical return value |
|---|---|---:|---|
| `clear()` | Remove every entry | Yes | `None` |
| `copy()` | Make a shallow copy | No | New dictionary |
| `dict.fromkeys(keys, value)` | Create keys with a common initial value | Creates a new dictionary | New dictionary |
| `get(key, default=None)` | Read a value safely | No | Found value or default |
| `items()` | View key-value pairs | No | Dynamic view of pairs |
| `keys()` | View keys | No | Dynamic view of keys |
| `pop(key[, default])` | Remove a key and return its value | Yes, when key exists | Removed value or default |
| `popitem()` | Remove and return the last inserted pair | Yes | Two-item tuple |
| `setdefault(key, default=None)` | Read a value, or insert a default when missing | Sometimes | Existing value or inserted default |
| `update(other)` | Add or overwrite entries | Yes | `None` |
| `values()` | View values | No | Dynamic view of values |

**Key distinction:** `clear()`, `pop()`, `popitem()`, `setdefault()` (when the key is absent), and `update()` can change the original dictionary. `copy()` creates a new outer dictionary. `get()`, `items()`, `keys()`, and `values()` do not change the dictionary. `dict.fromkeys()` creates a new dictionary.

---

# Part A — All 11 dictionary methods

## 4. `clear()` — remove every key-value pair

### Purpose

`clear()` removes all entries from the existing dictionary. The dictionary object remains, but it becomes empty.

### Syntax

```python
dictionary.clear()
```

### Example

```python
user_session = {
    "user_id": 501,
    "username": "ada",
    "active": True,
}

print("Before:", user_session)

result = user_session.clear()

print("After:", user_session)
print("Return value:", result)
```

**Output**

```text
Before: {'user_id': 501, 'username': 'ada', 'active': True}
After: {}
Return value: None
```

### Line-by-line explanation

1. `user_session` refers to a dictionary with three entries.
2. `user_session.clear()` removes all three entries from that same dictionary.
3. `user_session` now refers to the same dictionary object, but it is empty.
4. `clear()` returns `None`; it does not return the emptied dictionary.

### Important mistake

Do not write this when you want to keep the dictionary contents:

```python
cache = {"token": "abc123"}
cache.clear()
print(cache)  # {}
```

### Data-engineering use case

You may clear a temporary in-memory dictionary after a batch has been successfully processed. Do not clear a dictionary that is still shared by another part of the application.

---

## 5. `copy()` — make a shallow copy

### Purpose

`copy()` creates a **new dictionary object** containing the same keys and values as the original dictionary. It is a *shallow copy*: nested mutable objects are still shared.

### Syntax

```python
new_dictionary = original_dictionary.copy()
```

### Example 1 — copying a dictionary with immutable values

```python
source_config = {
    "host": "localhost",
    "port": 5432,
}

backup_config = source_config.copy()

backup_config["port"] = 5433

print("Original:", source_config)
print("Copy:", backup_config)
```

**Output**

```text
Original: {'host': 'localhost', 'port': 5432}
Copy: {'host': 'localhost', 'port': 5433}
```

### Explanation

1. `source_config.copy()` creates another dictionary object.
2. `backup_config` points to the new outer dictionary.
3. Updating `backup_config["port"]` changes only the copy's entry.
4. The original `source_config` remains unchanged.

### Example 2 — shallow-copy limitation with a nested list

```python
original = {
    "name": "pipeline-A",
    "steps": ["extract", "transform"],
}

copied = original.copy()

copied["name"] = "pipeline-B"
copied["steps"].append("load")

print("Original:", original)
print("Copied:", copied)
```

**Output**

```text
Original: {'name': 'pipeline-A', 'steps': ['extract', 'transform', 'load']}
Copied: {'name': 'pipeline-B', 'steps': ['extract', 'transform', 'load']}
```

Why did the original `steps` list change? The outer dictionaries are different, but both contain a reference to the **same nested list**.

### Object identity check

```python
original = {"items": [10, 20]}
copied = original.copy()

print(original is copied)                 # False: different dictionaries
print(original["items"] is copied["items"])  # True: same nested list
```

### When a deep copy is needed

Use `copy.deepcopy()` from the `copy` module when you need to recursively copy nested mutable objects.

```python
import copy

original = {"items": [10, 20]}
deep_copied = copy.deepcopy(original)

deep_copied["items"].append(30)

print(original)      # {'items': [10, 20]}
print(deep_copied)   # {'items': [10, 20, 30]}
```

A deep copy can be expensive or unsuitable for some custom objects. Choose it deliberately rather than using it automatically.

### Data-engineering use case

A pipeline may copy a configuration dictionary before applying job-specific overrides. Remember that `.copy()` does not isolate nested lists or nested dictionaries.

---

## 6. `dict.fromkeys(keys, value)` — create a dictionary from keys

### Purpose

`dict.fromkeys()` is a **class method** that creates a new dictionary. Each supplied key gets the same specified value.

### Syntax

```python
new_dictionary = dict.fromkeys(iterable_of_keys, value)
```

The `value` argument is optional. When omitted, each key receives `None`.

### Example 1 — initialize keys with the same value

```python
columns = ["customer_id", "name", "email"]

column_status = dict.fromkeys(columns, "pending")

print(column_status)
```

**Output**

```text
{'customer_id': 'pending', 'name': 'pending', 'email': 'pending'}
```

### Explanation

1. `columns` is an iterable containing three strings.
2. `dict.fromkeys(columns, "pending")` creates a new dictionary.
3. Each string becomes a key.
4. Each key initially maps to the value `"pending"`.

### Example 2 — omit the value argument

```python
fields = ["name", "age", "city"]

result = dict.fromkeys(fields)

print(result)
```

**Output**

```text
{'name': None, 'age': None, 'city': None}
```

### Critical warning — mutable defaults are shared

This is a common and important dictionary bug:

```python
result = dict.fromkeys(["a", "b"], [])

result["a"].append(1)

print(result)
print(result["a"] is result["b"])
```

**Output**

```text
{'a': [1], 'b': [1]}
True
```

Both keys refer to the **same list object**. `dict.fromkeys()` does not create a fresh list for every key.

### Correct approach — create an independent list per key

Use a dictionary comprehension:

```python
keys = ["a", "b"]

result = {key: [] for key in keys}

result["a"].append(1)

print(result)
print(result["a"] is result["b"])
```

**Output**

```text
{'a': [1], 'b': []}
False
```

### Data-engineering use case

You may initialize a status map for columns, files, or job names. A shared immutable default such as `"pending"` is safe. For independent mutable values such as lists or dictionaries, use a comprehension or a loop that creates a fresh object per key.

---

## 7. `get(key, default=None)` — retrieve a value safely

### Purpose

`get()` retrieves the value associated with a key. If the key does not exist, it returns the supplied default. If no default is supplied, it returns `None`.

Unlike bracket access (`dictionary[key]`), `get()` does **not** raise `KeyError` when the key is missing.

### Syntax

```python
dictionary.get(key)
dictionary.get(key, default)
```

### Example 1 — key exists

```python
employee = {
    "name": "Grace",
    "department": "Engineering",
}

name = employee.get("name")

print(name)
```

**Output**

```text
Grace
```

### Example 2 — key does not exist

```python
employee = {
    "name": "Grace",
    "department": "Engineering",
}

salary = employee.get("salary")

print(salary)
```

**Output**

```text
None
```

The dictionary is not changed by `get()`.

### Example 3 — provide a default value

```python
employee = {
    "name": "Grace",
    "department": "Engineering",
}

salary = employee.get("salary", 0)

print(salary)
```

**Output**

```text
0
```

### Compare `get()` with bracket access

```python
record = {"id": 1001}

print(record.get("status", "unknown"))  # unknown
print(record["id"])                      # 1001

# This would raise KeyError because "status" is missing:
# print(record["status"])
```

### Important distinction: missing key versus stored `None`

```python
record = {"middle_name": None}

print(record.get("middle_name"))          # None: key exists, value is None
print(record.get("nickname", "missing"))  # missing: key does not exist
print("middle_name" in record)             # True
print("nickname" in record)                # False
```

If you must distinguish a missing key from a key whose value is `None`, use `in` or a unique sentinel object.

```python
MISSING = object()
value = record.get("middle_name", MISSING)

if value is MISSING:
    print("Key is absent")
else:
    print("Key exists; value:", value)
```

### Data-engineering use case

API payloads often omit optional fields. `payload.get("phone")` lets your code handle an absent optional field without an exception. Validate required fields separately; using `get()` should not silently turn missing required data into valid data.

---

## 8. `items()` — view key-value pairs

### Purpose

`items()` returns a **dynamic dictionary view** containing key-value pairs. Each pair is presented as a two-item tuple `(key, value)`.

### Syntax

```python
view = dictionary.items()
```

### Example 1 — inspect all key-value pairs

```python
student = {
    "name": "Ada",
    "age": 20,
    "score": 95,
}

print(student.items())
```

**Example output**

```text
dict_items([('name', 'Ada'), ('age', 20), ('score', 95)])
```

The exact display is Python's view representation. To get a regular list of pairs, use `list(student.items())`.

### Example 2 — loop through keys and values

```python
student = {
    "name": "Ada",
    "age": 20,
    "score": 95,
}

for key, value in student.items():
    print(key, "->", value)
```

**Output**

```text
name -> Ada
age -> 20
score -> 95
```

### Example 3 — create a snapshot list

```python
student = {"name": "Ada", "score": 95}

pairs_snapshot = list(student.items())
student["score"] = 98

print(pairs_snapshot)
print(student.items())
```

**Output**

```text
[('name', 'Ada'), ('score', 95)]
dict_items([('name', 'Ada'), ('score', 98)])
```

`pairs_snapshot` is a separate list made at that moment. The `items()` view reflects the dictionary's current entries.

### Data-engineering use case

Use `items()` to process field/value pairs in a record, configuration, or API response:

```python
row = {"customer_id": 101, "country": "IN", "active": True}

for field_name, field_value in row.items():
    print(f"Field {field_name} has value {field_value}")
```

---

## 9. `keys()` — view dictionary keys

### Purpose

`keys()` returns a dynamic view of all keys in the dictionary.

### Syntax

```python
view = dictionary.keys()
```

### Example 1 — inspect keys

```python
employee = {
    "name": "Alan",
    "role": "Data Engineer",
    "location": "Kolkata",
}

print(employee.keys())
```

**Output**

```text
dict_keys(['name', 'role', 'location'])
```

### Example 2 — loop through keys

```python
employee = {
    "name": "Alan",
    "role": "Data Engineer",
    "location": "Kolkata",
}

for key in employee.keys():
    print(key)
```

**Output**

```text
name
role
location
```

Writing `for key in employee:` is also a direct way to iterate over dictionary keys; `.keys()` is useful when you specifically want to communicate that you are working with the keys view.

### Example 3 — test whether a key exists

```python
config = {"host": "localhost", "port": 5432}

print("host" in config.keys())  # True
print("user" in config.keys())  # False
```

For ordinary key membership, the simpler and idiomatic form is:

```python
print("host" in config)  # True
```

### Example 4 — the view is live

```python
config = {"host": "localhost"}
keys_view = config.keys()

print(list(keys_view))

config["port"] = 5432

print(list(keys_view))
```

**Output**

```text
['host']
['host', 'port']
```

The same `keys_view` object reflects the added key.

### Data-engineering use case

Check whether an incoming record has the required columns before transforming it:

```python
required_fields = {"customer_id", "email"}
record = {"customer_id": 101, "email": "ada@example.com", "city": "Delhi"}

missing_fields = required_fields - record.keys()
print(missing_fields)  # set()
```

This set operation works because dictionary key views support set-like operations.

---

## 10. `pop(key[, default])` — remove a key and return its value

### Purpose

`pop()` removes the specified key and returns the value that was stored under it.

- If the key exists, it is removed and its value is returned.
- If the key is missing and a default is supplied, the default is returned without changing the dictionary.
- If the key is missing and no default is supplied, Python raises `KeyError`.

### Syntax

```python
dictionary.pop(key)
dictionary.pop(key, default)
```

The square brackets in `pop(key[, default])` mean that `default` is optional; they are not typed in the call.

### Example 1 — remove an existing key

```python
job = {
    "job_id": 7001,
    "status": "completed",
    "retry_count": 0,
}

removed_status = job.pop("status")

print("Removed value:", removed_status)
print("Updated dictionary:", job)
```

**Output**

```text
Removed value: completed
Updated dictionary: {'job_id': 7001, 'retry_count': 0}
```

### Example 2 — missing key with a default

```python
job = {"job_id": 7001}

status = job.pop("status", "not-provided")

print(status)
print(job)
```

**Output**

```text
not-provided
{'job_id': 7001}
```

### Example 3 — missing key without a default

```python
job = {"job_id": 7001}

try:
    job.pop("status")
except KeyError as error:
    print("Missing key:", error)
```

**Example output**

```text
Missing key: 'status'
```

### Data-engineering use case

After validating a control field, you might remove it from a record before sending the remaining fields to a downstream transformation:

```python
record = {"_source_file": "batch-01.csv", "customer_id": 101, "amount": 250}
source_file = record.pop("_source_file", None)

print(source_file)
print(record)
```

Be careful: `pop()` changes the original record. Copy it first when the caller must retain the original.

---

## 11. `popitem()` — remove and return the last inserted pair

### Purpose

`popitem()` removes and returns the most recently inserted key-value pair as a two-item tuple.

In Python 3.7 and later, dictionaries preserve insertion order, so `popitem()` has defined **last-in, first-out (LIFO)** behavior.

### Syntax

```python
key, value = dictionary.popitem()
```

It accepts no arguments. Calling it on an empty dictionary raises `KeyError`.

### Example 1 — remove the last inserted pair

```python
pipeline = {
    "extract": "done",
    "transform": "done",
    "load": "pending",
}

removed_pair = pipeline.popitem()

print("Removed pair:", removed_pair)
print("Remaining dictionary:", pipeline)
```

**Output**

```text
Removed pair: ('load', 'pending')
Remaining dictionary: {'extract': 'done', 'transform': 'done'}
```

### Example 2 — unpack the returned tuple

```python
settings = {"debug": False, "timeout": 30, "retries": 3}

last_key, last_value = settings.popitem()

print(last_key)
print(last_value)
print(settings)
```

**Output**

```text
retries
3
{'debug': False, 'timeout': 30}
```

### Example 3 — empty dictionary

```python
empty = {}

try:
    empty.popitem()
except KeyError:
    print("Cannot remove an item from an empty dictionary.")
```

**Output**

```text
Cannot remove an item from an empty dictionary.
```

### Data-engineering use case

`popitem()` can be useful when deliberately consuming entries from a dictionary in reverse insertion order. It is not a substitute for a production queue when you need concurrency control, durable delivery, or explicit retry semantics.

---

## 12. `setdefault(key, default=None)` — get a value or insert a default

### Purpose

`setdefault()` checks whether a key exists.

- If the key exists, it returns its current value and does not replace it.
- If the key does not exist, it inserts the key with the default value and returns that value.
- If the default is omitted, the inserted value is `None`.

### Syntax

```python
dictionary.setdefault(key)
dictionary.setdefault(key, default)
```

### Example 1 — key already exists

```python
config = {"timeout": 30}

value = config.setdefault("timeout", 60)

print("Returned value:", value)
print("Dictionary:", config)
```

**Output**

```text
Returned value: 30
Dictionary: {'timeout': 30}
```

The existing value `30` is kept. The default `60` is ignored.

### Example 2 — key does not exist

```python
config = {"timeout": 30}

value = config.setdefault("retries", 3)

print("Returned value:", value)
print("Dictionary:", config)
```

**Output**

```text
Returned value: 3
Dictionary: {'timeout': 30, 'retries': 3}
```

The missing key is inserted.

### Example 3 — initialize a group of records

```python
orders_by_status = {}

orders = [
    ("pending", 101),
    ("completed", 102),
    ("pending", 103),
]

for status, order_id in orders:
    orders_by_status.setdefault(status, []).append(order_id)

print(orders_by_status)
```

**Output**

```text
{'pending': [101, 103], 'completed': [102]}
```

### Explanation of the grouping example

1. `orders_by_status` starts as an empty dictionary.
2. For the first `pending` order, `setdefault("pending", [])` inserts a new empty list and returns it.
3. `.append(101)` adds the order ID to that list.
4. For `completed`, the method inserts another list and order `102` is appended.
5. For the second `pending` order, the existing list is returned; `103` is appended to it.

### Important caution

`setdefault()` evaluates the default argument expression before the method call. In the example, a new `[]` is constructed on each loop iteration, even when the key already exists. The unused list is simply not inserted.

For more complex grouping or custom initialization, an explicit `if key not in dictionary` or `collections.defaultdict` may be clearer.

### Data-engineering use case

Group incoming records by status, country, event type, or source using a dictionary of lists. For large-scale data processing, consider whether the entire grouping fits in memory; use a database or distributed processing engine when it does not.

---

## 13. `update(other)` — add or overwrite entries in place

### Purpose

`update()` adds new key-value pairs to the existing dictionary and overwrites values for keys that already exist. It mutates the original dictionary and returns `None`.

### Syntax

```python
dictionary.update(other)
```

`other` can be:

- Another mapping, such as a dictionary.
- An iterable containing two-item entries, such as a list of tuples.
- Keyword arguments.

### Example 1 — update from another dictionary

```python
defaults = {
    "host": "localhost",
    "port": 5432,
    "debug": False,
}

environment_settings = {
    "port": 6432,
    "debug": True,
    "region": "ap-south-1",
}

result = defaults.update(environment_settings)

print("Updated dictionary:", defaults)
print("Return value:", result)
```

**Output**

```text
Updated dictionary: {'host': 'localhost', 'port': 6432, 'debug': True, 'region': 'ap-south-1'}
Return value: None
```

### Explanation

1. `defaults` initially has three entries.
2. `update(environment_settings)` reads the other mapping.
3. `port` and `debug` already exist, so their values are overwritten.
4. `region` is new, so it is inserted.
5. `defaults` itself is modified.
6. The return value is `None`.

### Example 2 — update from a list of two-item tuples

```python
user = {"name": "Ada"}

user.update([
    ("age", 36),
    ("country", "United Kingdom"),
])

print(user)
```

**Output**

```text
{'name': 'Ada', 'age': 36, 'country': 'United Kingdom'}
```

### Example 3 — update with keyword arguments

```python
settings = {"debug": False}

settings.update(timeout=60, retries=5)

print(settings)
```

**Output**

```text
{'debug': False, 'timeout': 60, 'retries': 5}
```

Keyword argument names are strings, so this form is suitable when the desired keys are valid Python keyword names.

### Common mistake — assigning the return value

Incorrect:

```python
config = {"debug": False}
config = config.update({"timeout": 30})
print(config)  # None
```

Correct:

```python
config = {"debug": False}
config.update({"timeout": 30})
print(config)  # {'debug': False, 'timeout': 30}
```

### Data-engineering use case

Use `update()` when applying environment-specific settings to an existing configuration object, or enriching a record with additional metadata. Remember that the original dictionary changes.

---

## 14. `values()` — view dictionary values

### Purpose

`values()` returns a dynamic view of the values currently stored in a dictionary.

### Syntax

```python
view = dictionary.values()
```

### Example 1 — inspect values

```python
scores = {
    "Ada": 95,
    "Grace": 88,
    "Alan": 76,
}

print(scores.values())
```

**Output**

```text
dict_values([95, 88, 76])
```

### Example 2 — loop through values

```python
scores = {
    "Ada": 95,
    "Grace": 88,
    "Alan": 76,
}

for score in scores.values():
    print(score)
```

**Output**

```text
95
88
76
```

### Example 3 — calculate with values

```python
scores = {
    "Ada": 95,
    "Grace": 88,
    "Alan": 76,
}

all_scores = list(scores.values())

print("Values:", all_scores)
print("Total:", sum(all_scores))
print("Average:", sum(all_scores) / len(all_scores))
```

**Output**

```text
Values: [95, 88, 76]
Total: 259
Average: 86.33333333333333
```

### Example 4 — the view is live

```python
scores = {"Ada": 95, "Grace": 88}
values_view = scores.values()

print(list(values_view))

scores["Alan"] = 76

print(list(values_view))
```

**Output**

```text
[95, 88]
[95, 88, 76]
```

### Important detail

A values view can contain duplicate values. For example, two employees can have the same salary. Unlike key views, values views are not set-like.

### Data-engineering use case

Use `values()` to calculate aggregates over a dictionary of numeric metrics, or to inspect all records stored as dictionary values.

---

# Part B — Dictionary views and related operations

## 15. Dictionary views are live, not frozen copies

The methods `keys()`, `values()`, and `items()` return **view objects**. A view is a dynamic window into the dictionary, not a separate list containing a fixed snapshot.

### Demonstration

```python
metrics = {"rows_read": 100, "rows_written": 90}

keys_view = metrics.keys()
values_view = metrics.values()
items_view = metrics.items()

print("Before:", list(keys_view), list(values_view), list(items_view))

metrics["rows_rejected"] = 10

print("After:", list(keys_view), list(values_view), list(items_view))
```

**Output**

```text
Before: ['rows_read', 'rows_written'] [100, 90] [('rows_read', 100), ('rows_written', 90)]
After: ['rows_read', 'rows_written', 'rows_rejected'] [100, 90, 10] [('rows_read', 100), ('rows_written', 90), ('rows_rejected', 10)]
```

### Create a snapshot when needed

Wrap the view in `list()` to create a list snapshot of the entries at that time:

```python
record = {"id": 1, "status": "new"}

keys_snapshot = list(record.keys())
values_snapshot = list(record.values())
items_snapshot = list(record.items())

record["status"] = "processed"
record["source"] = "api"

print(keys_snapshot)
print(values_snapshot)
print(items_snapshot)
print(record)
```

**Output**

```text
['id', 'status']
[1, 'new']
[('id', 1), ('status', 'new')]
{'id': 1, 'status': 'processed', 'source': 'api'}
```

The lists are snapshots of the key/value references at creation time. This is not a deep copy of nested objects.

### Do not change dictionary size while iterating over its live view

Adding or removing dictionary entries while iterating directly over a view can raise `RuntimeError: dictionary changed size during iteration`.

Risky pattern:

```python
# Risky: changing dictionary size during iteration.
# for key in metrics.keys():
#     if key.startswith("rows_"):
#         del metrics[key]
```

Safer pattern — iterate over a snapshot of keys:

```python
metrics = {
    "rows_read": 100,
    "rows_written": 90,
    "debug_mode": True,
}

for key in list(metrics.keys()):
    if key.startswith("rows_"):
        del metrics[key]

print(metrics)
```

**Output**

```text
{'debug_mode': True}
```

Changing values for existing keys while iterating is generally allowed, but adding or removing keys during iteration should be avoided. Use a snapshot when the key set must change.

---

## 16. Related built-in functions and dictionary operations

The following are not dictionary methods, but they are commonly used with dictionaries and are part of this lesson.

### 16.1 `len(dictionary)` — count key-value pairs

```python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}

print(len(scores))
```

**Output**

```text
3
```

`len()` returns the number of entries, not the total number of characters or the sum of values.

### 16.2 `list(dictionary)` — create a list of keys

```python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}

print(list(scores))
```

**Output**

```text
['Ada', 'Grace', 'Alan']
```

When a dictionary is iterated directly, Python iterates over its keys. These are equivalent for this purpose:

```python
list(scores)
list(scores.keys())
```

### 16.3 `sorted(dictionary)` — return sorted keys

```python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}

print(sorted(scores))
```

**Output**

```text
['Ada', 'Alan', 'Grace']
```

`sorted()` returns a **new list**; it does not sort or mutate the dictionary. By default, dictionary iteration supplies keys, so `sorted(scores)` sorts the keys.

### 16.4 Sort dictionary items by key or value

Sort by key:

```python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}

print(sorted(scores.items()))
```

**Output**

```text
[('Ada', 95), ('Alan', 76), ('Grace', 88)]
```

Sort by value (ascending):

```python
print(sorted(scores.items(), key=lambda item: item[1]))
```

**Output**

```text
[('Alan', 76), ('Grace', 88), ('Ada', 95)]
```

Sort by value (descending):

```python
print(sorted(scores.items(), key=lambda item: item[1], reverse=True))
```

**Output**

```text
[('Ada', 95), ('Grace', 88), ('Alan', 76)]
```

In `lambda item: item[1]`, each `item` is a `(key, value)` tuple and index `1` selects the value.

### 16.5 Dictionary equality with `==`

```python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}

other_scores = {"Grace": 88, "Ada": 95, "Alan": 76}

print(scores == other_scores)
```

**Output**

```text
True
```

Dictionary equality compares key-value content. It does **not** require the dictionaries to have the same insertion order.

Use `==` to compare dictionary contents. Use `is` only when you want to test whether two variables refer to the exact same object.

### 16.6 `dict()` — build a dictionary from pairs

The `dict()` constructor can build a dictionary from an iterable of two-item iterables.

```python
pairs = [
    ("a", 1),
    ("b", 2),
]

new_dict = dict(pairs)

print(new_dict)
```

**Output**

```text
{'a': 1, 'b': 2}
```

It can also be constructed with keyword arguments:

```python
settings = dict(host="localhost", port=5432)
print(settings)
```

**Output**

```text
{'host': 'localhost', 'port': 5432}
```

If the input contains the same key more than once, the later value wins:

```python
pairs = [("status", "new"), ("status", "done")]
print(dict(pairs))
```

**Output**

```text
{'status': 'done'}
```

### 16.7 Merge dictionaries with the `|` operator (Python 3.9+)

The dictionary merge operator `|` creates a **new dictionary**. It does not mutate either input dictionary.

```python
defaults = {
    "debug": False,
    "timeout": 30,
}

overrides = {
    "timeout": 60,
}

merged = defaults | overrides

print("Merged:", merged)
print("Defaults:", defaults)
print("Overrides:", overrides)
```

**Output**

```text
Merged: {'debug': False, 'timeout': 60}
Defaults: {'debug': False, 'timeout': 30}
Overrides: {'timeout': 60}
```

When both dictionaries contain the same key, the **right-hand dictionary wins**.

### 16.8 Merge more than two dictionaries

```python
base = {"timeout": 30, "debug": False}
environment = {"timeout": 45}
job = {"debug": True, "retries": 3}

final_config = base | environment | job

print(final_config)
```

**Output**

```text
{'timeout': 45, 'debug': True, 'retries': 3}
```

The right-most occurrence of a duplicate key supplies the final value.

### 16.9 Difference between `update()` and `|`

Use `.update()` when you want to mutate an existing dictionary:

```python
config = {"debug": False, "timeout": 30}
config.update({"timeout": 60})

print(config)
```

**Output**

```text
{'debug': False, 'timeout': 60}
```

Use `|` when you want a new merged dictionary and want to preserve the inputs:

```python
defaults = {"debug": False, "timeout": 30}
overrides = {"timeout": 60}

config = defaults | overrides

print(config)
print(defaults)
```

**Output**

```text
{'debug': False, 'timeout': 60}
{'debug': False, 'timeout': 30}
```

### 16.10 Check your Python version

The dictionary merge operator `|` requires Python 3.9 or later.

```bash
python3 --version
```

Example output (your version may differ):

```text
Python 3.12.0
```

For older Python versions, a common alternative is:

```python
merged = defaults.copy()
merged.update(overrides)
```

This creates a copy first, then updates the copy, leaving `defaults` unchanged.

---

## 17. Inspect dictionary methods with `dir()` and `help()`

Python lets you inspect the methods available on built-in types.

### List public, non-dunder dictionary methods

```bash
python3 -c "print([m for m in dir(dict) if not m.startswith('_')])"
```

This filters out names beginning with `_`, so the output focuses on public names.

### Inspect one method

```python
help(dict.get)
help(dict.update)
help(dict.pop)
```

`dir(dict)` shows names; `help()` provides documentation for a selected object.

---

# Part C — Practical data-engineering examples

## 18. Example 1 — safely read an API response

An API response is commonly represented as a dictionary after JSON decoding.

```python
api_response = {
    "customer_id": 1001,
    "name": "Ada",
    "active": True,
}

customer_id = api_response.get("customer_id")
email = api_response.get("email", "not-provided")

print("Customer ID:", customer_id)
print("Email:", email)
```

**Output**

```text
Customer ID: 1001
Email: not-provided
```

**Engineering note:** `.get()` is suitable for optional fields. For required fields, validate presence and type explicitly so malformed records are not silently accepted.

## 19. Example 2 — validate required fields

```python
required_fields = {"customer_id", "name", "email"}

record = {
    "customer_id": 1001,
    "name": "Ada",
    "active": True,
}

missing_fields = required_fields - record.keys()

if missing_fields:
    print("Invalid record. Missing:", sorted(missing_fields))
else:
    print("Record is valid.")
```

**Output**

```text
Invalid record. Missing: ['email']
```

The `keys()` view supports set operations, so it can be compared directly with a set of required field names.

## 20. Example 3 — count events by type

```python
events = [
    "click",
    "view",
    "click",
    "purchase",
    "view",
    "click",
]

counts = {}

for event in events:
    counts[event] = counts.get(event, 0) + 1

print(counts)
```

**Output**

```text
{'click': 3, 'view': 2, 'purchase': 1}
```

**How it works:**

1. For the first event, `counts.get(event, 0)` returns `0` because the key is absent.
2. The code adds one and stores the result under that event key.
3. When the event appears again, `get()` returns its current count.
4. The count is incremented and saved back.

A standard-library alternative for counting is `collections.Counter`.

## 21. Example 4 — group records by country with `setdefault()`

```python
customers = [
    {"id": 1, "name": "Ada", "country": "IN"},
    {"id": 2, "name": "Grace", "country": "US"},
    {"id": 3, "name": "Alan", "country": "IN"},
]

customers_by_country = {}

for customer in customers:
    country = customer["country"]
    customers_by_country.setdefault(country, []).append(customer)

for country, country_customers in customers_by_country.items():
    print(country, "->", [customer["name"] for customer in country_customers])
```

**Output**

```text
IN -> ['Ada', 'Alan']
US -> ['Grace']
```

Each country key maps to a list of customer records. A fresh list is inserted the first time each country appears.

## 22. Example 5 — merge pipeline configuration

```python
base_config = {
    "batch_size": 500,
    "retries": 2,
    "write_mode": "append",
}

production_config = {
    "batch_size": 2000,
    "retries": 5,
}

pipeline_config = base_config | production_config

print(pipeline_config)
print(base_config)
```

**Output (Python 3.9+)**

```text
{'batch_size': 2000, 'retries': 5, 'write_mode': 'append'}
{'batch_size': 500, 'retries': 2, 'write_mode': 'append'}
```

The production settings override matching defaults, while the original base configuration remains unchanged.

---

# Part D — Common mistakes and how to correct them

## 23. Mistake 1 — expecting `update()` to return a dictionary

Incorrect:

```python
config = {"debug": False}
config = config.update({"timeout": 30})
print(config)  # None
```

Correct:

```python
config = {"debug": False}
config.update({"timeout": 30})
print(config)  # {'debug': False, 'timeout': 30}
```

`update()` mutates the existing dictionary and returns `None`.

## 24. Mistake 2 — confusing `get()` with `pop()`

```python
record = {"status": "new"}

print(record.get("status"))  # Reads; keeps the key.
print(record)                 # {'status': 'new'}

print(record.pop("status")) # Reads and removes the key.
print(record)                 # {}
```

Use `get()` for non-mutating lookup. Use `pop()` when you intend to remove the key and retrieve its value.

## 25. Mistake 3 — assuming `.copy()` recursively copies nested data

```python
original = {"tags": ["new"]}
copied = original.copy()
copied["tags"].append("urgent")

print(original)  # {'tags': ['new', 'urgent']}
```

The nested list is shared. Use `copy.deepcopy()` when an independent recursive copy is required.

## 26. Mistake 4 — using `dict.fromkeys()` with a mutable value

Incorrect for independent lists:

```python
result = dict.fromkeys(["a", "b"], [])
```

Correct:

```python
result = {key: [] for key in ["a", "b"]}
```

The comprehension creates a fresh list for each key.

## 27. Mistake 5 — assuming dictionary views are lists

```python
record = {"id": 1, "status": "new"}

keys_view = record.keys()       # dict_keys view
keys_list = list(record.keys()) # independent list snapshot
```

Use `list()` when you specifically need a list or a snapshot.

## 28. Mistake 6 — changing dictionary size during iteration

Risky:

```python
# for key in record:
#     if key == "status":
#         del record[key]
```

Safer:

```python
for key in list(record):
    if key == "status":
        del record[key]
```

Iterating over a list snapshot avoids changing the dictionary's size while its iterator is active.

## 29. Mistake 7 — assuming `sorted(dictionary)` sorts by value

```python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}

print(sorted(scores))  # Sorts keys.
print(sorted(scores.items(), key=lambda item: item[1]))  # Sorts pairs by value.
```

The first call sorts keys. The second sorts key-value pairs using each pair's value.

## 30. Mistake 8 — using `|` on an older Python version

The dictionary merge operator requires Python 3.9+.

```python
# Python 3.9+
merged = first | second

# Compatible alternative for older Python versions:
merged = first.copy()
merged.update(second)
```

## 31. Mistake 9 — using `is` to compare dictionary contents

```python
first = {"x": 1}
second = {"x": 1}

print(first == second)  # True: same key-value content.
print(first is second)  # False: different objects.
```

Use `==` for content equality and `is` for object identity.

---

# Part E — Complexity and engineering considerations

## 32. Typical time complexity

For normal dictionary operations, average-case lookup, insertion, update of one key, and deletion are typically **O(1)**. These are average-case expectations, not a guarantee that every operation always takes constant time.

| Operation | Typical average-case time | Notes |
|---|---:|---|
| `get(key)` | O(1) | Hash lookup |
| `dictionary[key]` | O(1) | Hash lookup |
| `dictionary[key] = value` | O(1) | Insert or replace one entry |
| `key in dictionary` | O(1) | Checks keys |
| `pop(key)` | O(1) | Average case |
| `setdefault(key, value)` | O(1) | Average case, excluding cost of creating the default expression |
| `update(other)` | O(k) | `k` is the number of incoming entries, on average |
| `clear()` | O(n) | Removes `n` entries |
| `copy()` | O(n) | Copies `n` key-value references |
| `keys()` / `values()` / `items()` | O(1) to create view | Iterating over the view is O(n) |
| `len(dictionary)` | O(1) | Dictionary tracks its size |
| `sorted(dictionary)` | O(n log n) | Sorts the keys; produces a list |

Here, `n` is the number of entries already in the dictionary and `k` is the number of entries being added or processed. Hash collisions and unusual key behavior can affect performance.

## 33. Engineering rules for production code

1. **Know whether an operation mutates.** Do not accidentally modify a dictionary owned by another function or component.
2. **Use `.get()` for optional values, not to hide missing required data.** Validate required fields explicitly.
3. **Treat `.copy()` as shallow.** Nested lists and dictionaries can remain shared.
4. **Avoid mutable defaults with `dict.fromkeys()`.** Use a comprehension for separate mutable values.
5. **Treat views as dynamic.** Convert to a list when a stable iteration snapshot is required.
6. **Be explicit about merge precedence.** With `a | b`, values from `b` win for duplicate keys.
7. **Validate external data.** A dictionary can contain unexpected keys, missing fields, and values of unexpected types.
8. **Consider memory.** A dictionary containing millions of records may be too large for one process; use an appropriate database, object store, or distributed data-processing system when necessary.

---

# Part F — Practice exercises

Try each exercise before reading its solution. These exercises use only concepts introduced in this lesson.

## 34. Exercise 1 — clear a dictionary

Given:

```python
cache = {"a": 1, "b": 2, "c": 3}
```

Call the correct method to remove all entries. Print the dictionary and the method's return value.

### Solution

```python
cache = {"a": 1, "b": 2, "c": 3}

result = cache.clear()

print(cache)
print(result)
```

**Output**

```text
{}
None
```

## 35. Exercise 2 — copy before changing

Create a copy of this dictionary, then change the copy's `port` to `7000` without changing the original:

```python
config = {"host": "localhost", "port": 5432}
```

### Solution

```python
config = {"host": "localhost", "port": 5432}
config_copy = config.copy()

config_copy["port"] = 7000

print(config)
print(config_copy)
```

**Output**

```text
{'host': 'localhost', 'port': 5432}
{'host': 'localhost', 'port': 7000}
```

## 36. Exercise 3 — initialize keys with `fromkeys()`

Create a dictionary where `extract`, `transform`, and `load` all map to `"pending"`.

### Solution

```python
stages = ["extract", "transform", "load"]
status = dict.fromkeys(stages, "pending")

print(status)
```

**Output**

```text
{'extract': 'pending', 'transform': 'pending', 'load': 'pending'}
```

## 37. Exercise 4 — safely read an optional field

Read `email` from the record. Return `"not available"` when the key is missing.

```python
record = {"name": "Ada"}
```

### Solution

```python
record = {"name": "Ada"}
email = record.get("email", "not available")

print(email)
```

**Output**

```text
not available
```

## 38. Exercise 5 — print all key-value pairs

Use `items()` to print each field and its value:

```python
record = {"id": 101, "country": "IN"}
```

### Solution

```python
record = {"id": 101, "country": "IN"}

for key, value in record.items():
    print(key, value)
```

**Output**

```text
id 101
country IN
```

## 39. Exercise 6 — print all keys

Use `keys()` to display every key.

### Solution

```python
record = {"id": 101, "country": "IN"}

for key in record.keys():
    print(key)
```

**Output**

```text
id
country
```

## 40. Exercise 7 — remove a key safely

Remove `retry_count` and return `0` if it is absent.

### Solution

```python
job = {"job_id": 50, "retry_count": 2}

retry_count = job.pop("retry_count", 0)

print(retry_count)
print(job)
```

**Output**

```text
2
{'job_id': 50}
```

## 41. Exercise 8 — remove the last inserted pair

Use `popitem()` and unpack the returned pair.

### Solution

```python
job = {"extract": "done", "load": "pending"}

stage, status = job.popitem()

print(stage)
print(status)
print(job)
```

**Output**

```text
load
pending
{'extract': 'done'}
```

## 42. Exercise 9 — initialize a missing list with `setdefault()`

Group these values by category:

```python
records = [("A", 10), ("B", 20), ("A", 30)]
```

### Solution

```python
records = [("A", 10), ("B", 20), ("A", 30)]
grouped = {}

for category, value in records:
    grouped.setdefault(category, []).append(value)

print(grouped)
```

**Output**

```text
{'A': [10, 30], 'B': [20]}
```

## 43. Exercise 10 — update a dictionary

Change the `timeout` to `90` and add `retries` with value `4` using `update()`.

### Solution

```python
settings = {"timeout": 30, "debug": False}
settings.update({"timeout": 90, "retries": 4})

print(settings)
```

**Output**

```text
{'timeout': 90, 'debug': False, 'retries': 4}
```

## 44. Exercise 11 — inspect the values

Use `values()` to calculate the total number of processed rows:

```python
row_counts = {"file_a": 100, "file_b": 150, "file_c": 50}
```

### Solution

```python
row_counts = {"file_a": 100, "file_b": 150, "file_c": 50}

total_rows = sum(row_counts.values())
print(total_rows)
```

**Output**

```text
300
```

## 45. Exercise 12 — combine defaults and overrides

Use `|` to combine the dictionaries without modifying either input:

```python
defaults = {"timeout": 30, "debug": False}
overrides = {"timeout": 60}
```

### Solution (Python 3.9+)

```python
defaults = {"timeout": 30, "debug": False}
overrides = {"timeout": 60}

merged = defaults | overrides

print(merged)
print(defaults)
print(overrides)
```

**Output**

```text
{'timeout': 60, 'debug': False}
{'timeout': 30, 'debug': False}
{'timeout': 60}
```

---

# Part G — Final revision sheet

## 46. All 11 methods at a glance

| No. | Method | Remember |
|---:|---|---|
| 1 | `clear()` | Empty the existing dictionary; returns `None`. |
| 2 | `copy()` | Make a shallow copy; nested mutable values can be shared. |
| 3 | `dict.fromkeys()` | Build a new dictionary; mutable default values are shared among keys. |
| 4 | `get()` | Read a key safely; return a default if missing. |
| 5 | `items()` | Dynamic view of `(key, value)` pairs. |
| 6 | `keys()` | Dynamic view of keys. |
| 7 | `pop()` | Remove a specified key and return its value. |
| 8 | `popitem()` | Remove and return the most recently inserted pair. |
| 9 | `setdefault()` | Return an existing value or insert a default for a missing key. |
| 10 | `update()` | Add/overwrite entries in the original dictionary; returns `None`. |
| 11 | `values()` | Dynamic view of values. |

## 47. Quick mutation and return-value recap

| Operation | Changes original dictionary? | Result |
|---|---:|---|
| `d.clear()` | Yes | `None` |
| `d.copy()` | No | New shallow copy |
| `dict.fromkeys(keys, value)` | No; creates a new dictionary | New dictionary |
| `d.get(key, default)` | No | Value or default |
| `d.items()` | No | Live view |
| `d.keys()` | No | Live view |
| `d.pop(key, default)` | Yes if key exists | Removed value or default |
| `d.popitem()` | Yes | Removed `(key, value)` tuple |
| `d.setdefault(key, default)` | Only if key is absent | Existing or inserted value |
| `d.update(other)` | Yes | `None` |
| `d.values()` | No | Live view |
| `len(d)` | No | Integer count |
| `list(d)` | No | New list of keys |
| `sorted(d)` | No | New sorted list of keys |
| `dict(pairs)` | No; creates a new dictionary | New dictionary |
| `d1 | d2` | No; creates a new dictionary | Merged dictionary (Python 3.9+) |

## 48. Self-check questions

Make sure you can answer these without looking at the examples:

1. Which method empties a dictionary?
2. Why is `copy()` called a shallow copy?
3. Why can `dict.fromkeys(["x", "y"], [])` cause surprising behavior?
4. What does `get()` return when the requested key is absent and no default is supplied?
5. What is the difference between `items()`, `keys()`, and `values()`?
6. What does `pop()` do when its key is absent and no default is provided?
7. Which entry does `popitem()` remove in modern Python?
8. When does `setdefault()` mutate the dictionary?
9. Why should you not assign the result of `update()` back to the dictionary variable?
10. Why are dictionary views called live views?
11. What does `sorted(my_dict)` sort by?
12. Which side wins when the same key appears in both operands of `left | right`?
13. Which Python version introduced the dictionary merge operator `|`?
14. What is the difference between `==` and `is` for dictionaries?
15. How can you safely remove selected keys while iterating?

---

## 49. Final engineering takeaway

A Python dictionary is one of the most important data structures in data engineering because records, decoded JSON payloads, configuration objects, metadata, counters, and lookup tables are frequently represented as key-value mappings.

The most important habit is to understand **object mutation and ownership**. Know whether an operation changes the original dictionary, returns a new dictionary, returns a value, or returns a live view. This prevents accidental state changes, shared-reference bugs, and data corruption in larger applications.
