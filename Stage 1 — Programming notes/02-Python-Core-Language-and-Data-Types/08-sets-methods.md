# 08 — Python Set Methods

> **Learning level:** Beginner to practical Python / data engineering  
> **Language:** Python 3  
> **Purpose:** Understand every public, non-dunder `set` method in the lesson, how each behaves, what it returns, whether it mutates the original set, and where sets are useful in data-engineering applications.

---

## 1. What is a set?

A **set** is a mutable collection that stores **unique, hashable elements**. Duplicate values are automatically eliminated.

```python
numbers = {10, 20, 10, 30, 20}
print(numbers)
```

Possible output:

```text
{10, 20, 30}
```

The important properties are:

1. **Unique elements:** a set stores one occurrence of each equal value.
2. **Unordered collection:** sets do not promise positional order. Never depend on the order shown by `print()` or a loop.
3. **No indexing or slicing:** expressions such as `numbers[0]` and `numbers[1:3]` are invalid.
4. **Hashable elements:** values must be hashable. Common examples include integers, floats, strings, booleans, and tuples containing only hashable values.
5. **Mutable container:** you can add and remove elements from a normal `set`.

### 1.1 Creating a set

```python
# Set literal
languages = {"Python", "Java", "Go"}

# Construct a set from an iterable
scores = set([80, 90, 80, 95])

print(sorted(languages))
print(sorted(scores))
```

Output:

```text
['Go', 'Java', 'Python']
[80, 90, 95]
```

`set(iterable)` consumes an iterable and keeps only unique elements.

### 1.2 Creating an empty set: `set()` versus `{}`

```python
empty_set = set()
empty_dictionary = {}

print(type(empty_set))
print(type(empty_dictionary))
```

Output:

```text
<class 'set'>
<class 'dict'>
```

**Important:** `{}` creates an empty dictionary, not an empty set. Use `set()` to create an empty set.

### 1.3 Sets can contain only hashable elements

```python
valid_values = {1, "Python", (10, 20)}
print(valid_values)
```

The tuple is valid because both values inside it are hashable integers.

These examples raise `TypeError` because lists and dictionaries are mutable and unhashable:

```python
# invalid_set = {[1, 2], [3, 4]}
# invalid_set = {{"name": "Ada"}}
```

A tuple containing a list is also unhashable:

```python
# invalid_set = {(1, [2, 3])}  # TypeError
```

Use an immutable, hashable representation when appropriate. For example, a list of coordinate pairs can sometimes be represented as a set of tuples:

```python
coordinates = {(12, 7), (4, 9), (12, 7)}
print(sorted(coordinates))
```

Output:

```text
[(4, 9), (12, 7)]
```

---

## 2. How to inspect set methods in your Python installation

Run this command in a terminal:

```bash
python3 -c "print([m for m in dir(set) if not m.startswith('_')])"
```

It displays the public, non-dunder attributes and methods available on the built-in `set` type in that Python installation. The exact display order is not an API guarantee.

You can also inspect an individual method:

```python
help(set.union)
help(set.difference_update)
```

The lesson covers all **17 public, non-dunder set methods** listed below.

| # | Method | Main purpose | Mutates the set on which it is called? |
|---:|---|---|---|
| 1 | `add(value)` | Add one element | Yes |
| 2 | `clear()` | Remove every element | Yes |
| 3 | `copy()` | Make a shallow copy | No |
| 4 | `difference(other)` | Elements only in the first set | No |
| 5 | `difference_update(other)` | Remove elements found in other iterables | Yes |
| 6 | `discard(value)` | Remove an element if present | Yes |
| 7 | `intersection(other)` | Elements shared by the sets | No |
| 8 | `intersection_update(other)` | Keep only shared elements | Yes |
| 9 | `isdisjoint(other)` | Check whether there is no overlap | No |
| 10 | `issubset(other)` | Check whether this set is contained in another | No |
| 11 | `issuperset(other)` | Check whether this set contains another | No |
| 12 | `pop()` | Remove and return an arbitrary element | Yes |
| 13 | `remove(value)` | Remove a required element | Yes |
| 14 | `symmetric_difference(other)` | Elements present in exactly one input | No |
| 15 | `symmetric_difference_update(other)` | Replace this set with the symmetric difference | Yes |
| 16 | `union(other)` | Combine unique elements | No |
| 17 | `update(other)` | Add elements from other iterables | Yes |

**Core distinction:** methods such as `difference()` and `union()` create and return a new set; their corresponding `*_update()` methods change the existing set and return `None`.

---

# Part A — The 17 Set Methods

## 3. `add(value)` — Add one element

### What does it do?

`add(value)` inserts one element into the set. If an equal value already exists, the set remains unchanged because sets cannot contain duplicates.

- **Mutation:** Yes; changes the original set if the value was not already present.
- **Return value:** `None`.
- **Error:** `TypeError` if the value is unhashable.

### Example 1: Add one integer

```python
numbers = {10, 20, 30}

result = numbers.add(40)

print(numbers)
print(result)
```

Output (set display order may vary):

```text
{10, 20, 30, 40}
None
```

`numbers.add(40)` changes `numbers` itself. It does not return the updated set. The return value is `None`.

### Example 2: Add a duplicate

```python
numbers = {10, 20, 30}
numbers.add(20)

print(sorted(numbers))
```

Output:

```text
[10, 20, 30]
```

The set remains unchanged because `20` is already present.

### Example 3: Add a string

```python
languages = {"Python", "Java"}
languages.add("Go")

print(sorted(languages))
```

Output:

```text
['Go', 'Java', 'Python']
```

### Common mistake: assigning the return value

Incorrect when you intend to retain the set:

```python
numbers = {1, 2, 3}
numbers = numbers.add(4)  # numbers becomes None
```

Correct:

```python
numbers = {1, 2, 3}
numbers.add(4)
print(sorted(numbers))
```

### Data-engineering use case

While processing incoming event records, use `add()` to record a distinct customer ID or event type:

```python
unique_customer_ids = set()

unique_customer_ids.add("customer-101")
unique_customer_ids.add("customer-102")
unique_customer_ids.add("customer-101")

print(sorted(unique_customer_ids))
```

Output:

```text
['customer-101', 'customer-102']
```

---

## 4. `clear()` — Remove all elements

### What does it do?

`clear()` removes every element from an existing set. The set object remains available, but it becomes empty.

- **Mutation:** Yes.
- **Return value:** `None`.
- **Error:** None for a normal set.

### Example

```python
active_users = {"alice", "bob", "carol"}

result = active_users.clear()

print(active_users)
print(result)
print(len(active_users))
```

Output:

```text
set()
None
0
```

### Verify that the original object was emptied

```python
records = {"A", "B", "C"}

same_reference = records
records.clear()

print(records)
print(same_reference)
```

Output:

```text
set()
set()
```

Both names refer to the same set object. Clearing it through `records` is visible through `same_reference` too.

### Data-engineering use case

A temporary set can be cleared before the next independent processing batch:

```python
batch_event_types = {"created", "updated"}

# Finish processing the current batch.
batch_event_types.clear()

# Start collecting values for the next batch.
batch_event_types.add("deleted")

print(batch_event_types)
```

Output:

```text
{'deleted'}
```

Use `clear()` only when you intentionally want to empty that particular set object. Do not clear a set if another part of the application is still using the same object.

---

## 5. `copy()` — Create a shallow copy

### What does it do?

`copy()` returns a new set containing the same elements as the original set.

- **Mutation:** Does not mutate the original set.
- **Return value:** A new set object.
- **Copy type:** Shallow copy.

### Example 1: Copy a set

```python
original = {10, 20, 30}

copied = original.copy()

print(sorted(original))
print(sorted(copied))
print(original is copied)
```

Output:

```text
[10, 20, 30]
[10, 20, 30]
False
```

The two sets have equal contents, but `is` returns `False` because they are different set objects.

### Example 2: Mutate the copy

```python
original = {"Python", "Java"}
copied = original.copy()

copied.add("Go")

print(sorted(original))
print(sorted(copied))
```

Output:

```text
['Java', 'Python']
['Go', 'Java', 'Python']
```

Adding an element to `copied` does not add it to `original`.

### What does shallow mean for a set?

A shallow copy creates a new outer set. It does not recursively clone the element objects. Set members must be hashable, and their hash/equality behavior must remain stable while they are members of the set.

For ordinary sets of integers or strings, this distinction is usually straightforward because those values are immutable.

### Data-engineering use case

Keep a working copy of a set of approved schema field names before calculating changes:

```python
approved_columns = {"customer_id", "email", "created_at"}
working_columns = approved_columns.copy()

working_columns.add("country")

print(sorted(approved_columns))
print(sorted(working_columns))
```

Output:

```text
['created_at', 'customer_id', 'email']
['country', 'created_at', 'customer_id', 'email']
```

---

## 6. `difference(other)` — Find elements present only in the first set

### What does it do?

`difference(other)` returns the elements that are in the set before the dot but are not in the other iterable(s).

- **Mutation:** No.
- **Return value:** A new set.
- **Operator equivalent:** `-` for set operands.
- **Direction matters:** `A.difference(B)` is not generally equal to `B.difference(A)`.

### Example 1: Basic difference

```python
python_students = {"Ada", "Grace", "Alan", "Linus"}
data_students = {"Grace", "Linus", "Marie", "Katherine"}

python_only = python_students.difference(data_students)

print(sorted(python_only))
print(sorted(python_students))
```

Output:

```text
['Ada', 'Alan']
['Ada', 'Alan', 'Grace', 'Linus']
```

`python_only` contains names found in `python_students` but not in `data_students`. The original `python_students` set is unchanged.

### Example 2: Difference in the opposite direction

```python
python_students = {"Ada", "Grace", "Alan", "Linus"}
data_students = {"Grace", "Linus", "Marie", "Katherine"}

print(sorted(data_students.difference(python_students)))
```

Output:

```text
['Katherine', 'Marie']
```

### Example 3: Difference with multiple iterables

```python
available = {"A", "B", "C", "D", "E"}

result = available.difference({"B", "C"}, ["E"])

print(sorted(result))
```

Output:

```text
['A', 'D']
```

The method accepts one or more iterables.

### Operator equivalent

```python
A = {1, 2, 3, 4}
B = {3, 4, 5}

print(sorted(A - B))
```

Output:

```text
[1, 2]
```

### Data-engineering use case: identify missing records

```python
source_ids = {101, 102, 103, 104, 105}
loaded_ids = {101, 102, 105}

not_loaded = source_ids.difference(loaded_ids)

print(sorted(not_loaded))
```

Output:

```text
[103, 104]
```

This identifies IDs present in the source batch but absent from the loaded-ID collection. A real pipeline should also define the comparison scope, account for batch boundaries, and validate records in the source and target systems.

---

## 7. `difference_update(other)` — Remove elements found in other iterables

### What does it do?

`difference_update(other)` removes from the original set every element that occurs in the supplied iterable(s).

- **Mutation:** Yes.
- **Return value:** `None`.
- **Operator equivalent:** `-=` for set operands.
- **Difference from `difference()`:** this method changes the original set instead of returning a separate result.

### Example 1: Basic difference update

```python
python_students = {"Ada", "Grace", "Alan", "Linus"}
data_students = {"Grace", "Linus", "Marie", "Katherine"}

result = python_students.difference_update(data_students)

print(sorted(python_students))
print(result)
```

Output:

```text
['Ada', 'Alan']
None
```

The original `python_students` set is changed in place.

### Example 2: Remove values from multiple iterables

```python
numbers = {1, 2, 3, 4, 5, 6}

numbers.difference_update({2, 4}, [6])

print(sorted(numbers))
```

Output:

```text
[1, 3, 5]
```

### Operator equivalent

```python
numbers = {1, 2, 3, 4}
numbers -= {2, 4}

print(sorted(numbers))
```

Output:

```text
[1, 3]
```

### Data-engineering use case

Remove already-processed identifiers from a pending-work set:

```python
pending_ids = {1001, 1002, 1003, 1004}
processed_ids = {1001, 1003}

pending_ids.difference_update(processed_ids)

print(sorted(pending_ids))
```

Output:

```text
[1002, 1004]
```

Be deliberate: any other variable referencing `pending_ids` sees the mutation too.

---

## 8. `discard(value)` — Remove an element if it exists

### What does it do?

`discard(value)` removes the specified value if it is present. If it is absent, the method does nothing and does not raise an error.

- **Mutation:** Yes, only when the value is present.
- **Return value:** `None`.
- **Error for missing value:** No `KeyError`.

### Example 1: Discard an existing value

```python
active_users = {"alice", "bob", "carol"}

result = active_users.discard("bob")

print(sorted(active_users))
print(result)
```

Output:

```text
['alice', 'carol']
None
```

### Example 2: Discard a missing value

```python
active_users = {"alice", "carol"}

active_users.discard("dave")

print(sorted(active_users))
```

Output:

```text
['alice', 'carol']
```

No error is raised because `dave` was not present.

### `discard()` versus `remove()`

| Behavior | `discard(value)` | `remove(value)` |
|---|---|---|
| Value exists | Removes it | Removes it |
| Value is absent | Does nothing | Raises `KeyError` |
| Return value | `None` | `None` |
| Appropriate when | Absence is normal | Absence indicates an error |

### Data-engineering use case

Remove an optional flag from a collection of record attributes, where the flag may or may not be present:

```python
record_flags = {"validated", "has_email", "legacy_format"}

record_flags.discard("legacy_format")
record_flags.discard("manual_review")  # Safe if absent.

print(sorted(record_flags))
```

Output:

```text
['has_email', 'validated']
```

---

## 9. `intersection(other)` — Find shared elements

### What does it do?

`intersection(other)` returns a new set containing only the elements found in the original set and in every supplied iterable.

- **Mutation:** No.
- **Return value:** A new set.
- **Operator equivalent:** `&` for set operands.
- **Typical use:** Find common IDs, permissions, tags, or categories.

### Example 1: Find students enrolled in both courses

```python
python_students = {"Ada", "Grace", "Alan", "Linus"}
data_students = {"Grace", "Linus", "Marie", "Katherine"}

common_students = python_students.intersection(data_students)

print(sorted(common_students))
print(sorted(python_students))
```

Output:

```text
['Grace', 'Linus']
['Ada', 'Alan', 'Grace', 'Linus']
```

### Example 2: Find common values from multiple iterables

```python
A = {1, 2, 3, 4, 5}
B = {2, 3, 4, 6}
C = {0, 2, 3, 7}

print(sorted(A.intersection(B, C)))
```

Output:

```text
[2, 3]
```

Only values present in all three collections are returned.

### Operator equivalent

```python
A = {1, 2, 3, 4}
B = {3, 4, 5}

print(sorted(A & B))
```

Output:

```text
[3, 4]
```

### Data-engineering use case

Find customer IDs present in both an ingestion batch and an allowlist:

```python
incoming_customer_ids = {101, 102, 103, 104}
approved_customer_ids = {102, 104, 106}

approved_incoming = incoming_customer_ids.intersection(approved_customer_ids)

print(sorted(approved_incoming))
```

Output:

```text
[102, 104]
```

A set intersection is useful for membership analysis. It does not preserve input row order or duplicate counts, so it is not a replacement for a relational join when row-level multiplicity matters.

---

## 10. `intersection_update(other)` — Keep only shared elements

### What does it do?

`intersection_update(other)` changes the original set so that it contains only elements also present in every supplied iterable.

- **Mutation:** Yes.
- **Return value:** `None`.
- **Operator equivalent:** `&=` for set operands.
- **Difference from `intersection()`:** this method updates the existing set rather than returning a new one.

### Example 1: Keep only common students

```python
python_students = {"Ada", "Grace", "Alan", "Linus"}
data_students = {"Grace", "Linus", "Marie", "Katherine"}

result = python_students.intersection_update(data_students)

print(sorted(python_students))
print(result)
```

Output:

```text
['Grace', 'Linus']
None
```

### Example 2: Intersect with multiple iterables

```python
numbers = {1, 2, 3, 4, 5, 6}

numbers.intersection_update({2, 3, 4}, [3, 4, 5])

print(sorted(numbers))
```

Output:

```text
[3, 4]
```

### Operator equivalent

```python
numbers = {1, 2, 3, 4, 5}
numbers &= {2, 3, 5}

print(sorted(numbers))
```

Output:

```text
[2, 3, 5]
```

### Data-engineering use case

Filter a set of candidate file names down to those allowed by a configured list:

```python
candidate_files = {"customers.csv", "orders.csv", "debug.log"}
allowed_files = {"customers.csv", "orders.csv", "products.csv"}

candidate_files.intersection_update(allowed_files)

print(sorted(candidate_files))
```

Output:

```text
['customers.csv', 'orders.csv']
```

---

## 11. `isdisjoint(other)` — Check whether two collections have no common elements

### What does it do?

`isdisjoint(other)` checks whether the set and the supplied iterable have no elements in common.

- **Mutation:** No.
- **Return value:** Boolean (`True` or `False`).
- **Meaning:** `True` means no overlap; `False` means at least one shared element exists.

### Example 1: No overlap

```python
team_a = {"Ada", "Grace"}
team_b = {"Linus", "Guido"}

print(team_a.isdisjoint(team_b))
```

Output:

```text
True
```

No member is shared by both sets.

### Example 2: At least one shared value

```python
team_a = {"Ada", "Grace", "Linus"}
team_b = {"Linus", "Guido"}

print(team_a.isdisjoint(team_b))
```

Output:

```text
False
```

`Linus` is shared.

### Example 3: Check against a list

```python
blocked_users = {"user-10", "user-20"}
incoming_users = ["user-30", "user-40"]

print(blocked_users.isdisjoint(incoming_users))
```

Output:

```text
True
```

The method accepts an iterable, not only another set.

### Data-engineering use case

Check whether a batch contains any IDs from a prohibited-ID collection:

```python
restricted_ids = {9001, 9002, 9003}
batch_ids = {1001, 1002, 1003}

if restricted_ids.isdisjoint(batch_ids):
    print("No restricted IDs found")
else:
    print("Batch contains restricted IDs")
```

Output:

```text
No restricted IDs found
```

This is a simple in-memory membership check, not a substitute for an authoritative compliance control or database constraint.

---

## 12. `issubset(other)` — Check whether all elements are contained in another collection

### What does it do?

`issubset(other)` returns `True` when every element in the set before the dot also occurs in the supplied iterable.

- **Mutation:** No.
- **Return value:** Boolean.
- **Operator equivalent:** `<=` for set operands.
- **Important:** A set is a subset of itself.

### Example 1: Subset is true

```python
required_tags = {"python", "beginner"}
all_tags = {"python", "beginner", "tutorial", "data"}

print(required_tags.issubset(all_tags))
```

Output:

```text
True
```

Every required tag occurs in `all_tags`.

### Example 2: Subset is false

```python
required_tags = {"python", "advanced"}
all_tags = {"python", "beginner", "tutorial"}

print(required_tags.issubset(all_tags))
```

Output:

```text
False
```

The `advanced` tag is missing from `all_tags`.

### Operator equivalent

```python
A = {1, 2}
B = {1, 2, 3}

print(A <= B)
```

Output:

```text
True
```

### Data-engineering use case

Validate whether an incoming record includes every required field name:

```python
required_fields = {"customer_id", "email", "created_at"}
incoming_fields = {"customer_id", "email", "created_at", "country"}

if required_fields.issubset(incoming_fields):
    print("Required schema fields are present")
else:
    print("Required schema fields are missing")
```

Output:

```text
Required schema fields are present
```

This checks field-name presence only. It does not validate data types, nullability, constraints, or field values.

---

## 13. `issuperset(other)` — Check whether a set contains another collection

### What does it do?

`issuperset(other)` returns `True` when every element in the supplied iterable is also present in the set before the dot.

- **Mutation:** No.
- **Return value:** Boolean.
- **Operator equivalent:** `>=` for set operands.
- **Relationship:** `A.issuperset(B)` is equivalent to `B.issubset(A)`.

### Example 1: Superset is true

```python
all_permissions = {"read", "write", "delete", "export"}
required_permissions = {"read", "write"}

print(all_permissions.issuperset(required_permissions))
```

Output:

```text
True
```

`all_permissions` contains both required permissions.

### Example 2: Superset is false

```python
all_permissions = {"read", "write"}
required_permissions = {"read", "delete"}

print(all_permissions.issuperset(required_permissions))
```

Output:

```text
False
```

The `delete` permission is missing.

### Operator equivalent

```python
A = {1, 2, 3, 4}
B = {2, 3}

print(A >= B)
```

Output:

```text
True
```

### Data-engineering use case

Check whether a service's configured capabilities include the capabilities required by a pipeline:

```python
service_capabilities = {"read", "write", "batch", "stream"}
pipeline_requirements = {"read", "write"}

print(service_capabilities.issuperset(pipeline_requirements))
```

Output:

```text
True
```

This is a capability-set comparison example; real authorization must also enforce identity, policy, resource scope, and other security rules.

---

## 14. `pop()` — Remove and return an arbitrary element

### What does it do?

`pop()` removes and returns an arbitrary element from a non-empty set.

- **Mutation:** Yes.
- **Return value:** The removed element.
- **Error:** Raises `KeyError` if the set is empty.
- **Important:** It does not accept an index.

### Example 1: Pop one element

```python
tasks = {"extract", "transform", "load"}

removed_task = tasks.pop()

print(removed_task)
print(tasks)
```

The first output is one element from the set. The exact element is not specified, so do not write code that expects a particular task to be returned.

### Example 2: Pop until the set is empty

```python
tasks = {"extract", "transform", "load"}

while tasks:
    task = tasks.pop()
    print("Processing:", task)
```

Output order is not guaranteed. The loop continues until the set is empty.

### Example 3: Empty set raises `KeyError`

```python
empty_values = set()

# empty_values.pop()  # KeyError: 'pop from an empty set'
```

You can check before popping:

```python
if empty_values:
    value = empty_values.pop()
else:
    print("No values available")
```

### `set.pop()` versus `list.pop()`

| Collection | `pop()` behavior |
|---|---|
| Set | Removes and returns an arbitrary element; no index argument |
| List | Removes and returns the last element by default, or an element at a supplied index |

### Data-engineering use case

A set can serve as a simple work pool when task order does not matter:

```python
pending_partitions = {"2026-11-01", "2026-11-02", "2026-11-03"}

while pending_partitions:
    partition = pending_partitions.pop()
    print("Handle partition:", partition)
```

Do not use `set.pop()` for ordered scheduling, priority queues, retries requiring deterministic order, or durable task management. Use an appropriate queue or scheduler for those requirements.

---

## 15. `remove(value)` — Remove a required element

### What does it do?

`remove(value)` removes a specified element from the set.

- **Mutation:** Yes when the value exists.
- **Return value:** `None`.
- **Error:** Raises `KeyError` if the value is absent.

### Example 1: Remove an existing element

```python
active_users = {"alice", "bob", "carol"}

result = active_users.remove("bob")

print(sorted(active_users))
print(result)
```

Output:

```text
['alice', 'carol']
None
```

### Example 2: Remove a missing element

```python
active_users = {"alice", "carol"}

# active_users.remove("dave")  # KeyError: 'dave'
```

If absence is a normal condition, use `discard()` instead.

### Example 3: Handle the expected error

```python
active_users = {"alice", "carol"}

try:
    active_users.remove("dave")
except KeyError:
    print("The requested user was not present")
```

Output:

```text
The requested user was not present
```

### Data-engineering use case

Remove a required ID only when its presence is an invariant that should be enforced:

```python
pending_ids = {101, 102, 103}

try:
    pending_ids.remove(102)
    print("ID removed")
except KeyError:
    print("Data consistency issue: ID was not pending")
```

Output:

```text
ID removed
```

Use `remove()` when a missing element should be visible as an error or condition to investigate.

---

## 16. `symmetric_difference(other)` — Find elements present in exactly one set

### What does it do?

`symmetric_difference(other)` returns elements that appear in one input or the other, but **not in both**.

- **Mutation:** No.
- **Return value:** A new set.
- **Operator equivalent:** `^` for set operands.
- **Difference from `difference()`:** it includes unique elements from both sides, not only from the left-hand set.

### Example 1: Basic symmetric difference

```python
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

result = A.symmetric_difference(B)

print(sorted(result))
print(sorted(A))
```

Output:

```text
[1, 2, 5, 6]
[1, 2, 3, 4]
```

Values `3` and `4` are excluded because they occur in both sets. Values `1` and `2` occur only in `A`; values `5` and `6` occur only in `B`.

### Example 2: Compare two tag collections

```python
article_a_tags = {"python", "tutorial", "beginner"}
article_b_tags = {"python", "advanced", "tips"}

changed_tags = article_a_tags.symmetric_difference(article_b_tags)

print(sorted(changed_tags))
```

Output:

```text
['advanced', 'beginner', 'tips', 'tutorial']
```

### Operator equivalent

```python
A = {1, 2, 3}
B = {2, 3, 4}

print(sorted(A ^ B))
```

Output:

```text
[1, 4]
```

### Data-engineering use case

Identify column names that differ between two schema versions:

```python
schema_v1 = {"customer_id", "email", "created_at"}
schema_v2 = {"customer_id", "email", "country"}

changed_columns = schema_v1.symmetric_difference(schema_v2)

print(sorted(changed_columns))
```

Output:

```text
['country', 'created_at']
```

This shows which names differ, but it does not label a column as added or removed. Use directional differences for that:

```python
added_columns = schema_v2 - schema_v1
removed_columns = schema_v1 - schema_v2

print("Added:", sorted(added_columns))
print("Removed:", sorted(removed_columns))
```

Output:

```text
Added: ['country']
Removed: ['created_at']
```

---

## 17. `symmetric_difference_update(other)` — Update a set to its symmetric difference

### What does it do?

`symmetric_difference_update(other)` changes the original set so that it contains elements present in exactly one of the original set and the supplied iterable.

- **Mutation:** Yes.
- **Return value:** `None`.
- **Operator equivalent:** `^=` for set operands.

### Example 1: Basic update

```python
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

result = A.symmetric_difference_update(B)

print(sorted(A))
print(result)
```

Output:

```text
[1, 2, 5, 6]
None
```

`A` is changed in place. `B` is unchanged.

### Example 2: Update with a list

```python
numbers = {1, 2, 3}

numbers.symmetric_difference_update([3, 4, 5])

print(sorted(numbers))
```

Output:

```text
[1, 2, 4, 5]
```

The method accepts an iterable.

### Operator equivalent

```python
A = {1, 2, 3}
A ^= {3, 4}

print(sorted(A))
```

Output:

```text
[1, 2, 4]
```

### Data-engineering use case

Update a working set of changed field names as a second schema is compared:

```python
changed_fields = {"email", "created_at"}
new_comparison = {"created_at", "country"}

changed_fields.symmetric_difference_update(new_comparison)

print(sorted(changed_fields))
```

Output:

```text
['country', 'email']
```

Because this mutates `changed_fields`, make a copy first if the original collection must be retained.

---

## 18. `union(other)` — Combine elements from multiple collections

### What does it do?

`union(other)` returns a new set containing all unique elements from the original set and the supplied iterable(s).

- **Mutation:** No.
- **Return value:** A new set.
- **Operator equivalent:** `|` for set operands.
- **Duplicates:** Automatically eliminated.

### Example 1: Combine course rosters

```python
python_students = {"Ada", "Grace", "Alan", "Linus"}
data_students = {"Grace", "Linus", "Marie", "Katherine"}

all_students = python_students.union(data_students)

print(sorted(all_students))
```

Output:

```text
['Ada', 'Alan', 'Grace', 'Katherine', 'Linus', 'Marie']
```

Students enrolled in both courses occur once in the union.

### Example 2: Union of more than two iterables

```python
A = {1, 2}
B = {2, 3}
C = {3, 4}

print(sorted(A.union(B, C)))
```

Output:

```text
[1, 2, 3, 4]
```

### Operator equivalent

```python
A = {1, 2, 3}
B = {3, 4, 5}

all_values = A | B

print(sorted(all_values))
print(sorted(A))
```

Output:

```text
[1, 2, 3, 4, 5]
[1, 2, 3]
```

The original `A` remains unchanged.

### Data-engineering use case

Combine the identifiers observed in multiple ingestion partitions:

```python
partition_1_ids = {101, 102, 103}
partition_2_ids = {103, 104}
partition_3_ids = {105, 101}

all_ids = partition_1_ids.union(partition_2_ids, partition_3_ids)

print(sorted(all_ids))
```

Output:

```text
[101, 102, 103, 104, 105]
```

This produces unique IDs. It does not preserve duplicate counts or record order.

---

## 19. `update(other)` — Add elements from other iterables to the original set

### What does it do?

`update(other)` adds all unique elements from one or more iterables to the set on which it is called.

- **Mutation:** Yes.
- **Return value:** `None`.
- **Operator equivalent:** `|=` for set operands.
- **Difference from `union()`:** `update()` modifies the existing set; `union()` returns a new set.

### Example 1: Update with another set

```python
python_students = {"Ada", "Grace"}
data_students = {"Grace", "Linus"}

result = python_students.update(data_students)

print(sorted(python_students))
print(result)
```

Output:

```text
['Ada', 'Grace', 'Linus']
None
```

### Example 2: Update with a list

```python
numbers = {1, 2, 3}

numbers.update([3, 4, 5, 5])

print(sorted(numbers))
```

Output:

```text
[1, 2, 3, 4, 5]
```

The list's duplicate `5` is added only once.

### Example 3: Update with multiple iterables

```python
numbers = {1, 2}

numbers.update({2, 3}, [3, 4], (4, 5))

print(sorted(numbers))
```

Output:

```text
[1, 2, 3, 4, 5]
```

### Operator equivalent

```python
A = {1, 2, 3}
A |= {3, 4, 5}

print(sorted(A))
```

Output:

```text
[1, 2, 3, 4, 5]
```

### Data-engineering use case

Accumulate distinct event names while reading multiple batches:

```python
observed_events = {"user_created", "user_updated"}
new_batch_events = ["order_created", "user_updated", "payment_received"]

observed_events.update(new_batch_events)

print(sorted(observed_events))
```

Output:

```text
['order_created', 'payment_received', 'user_created', 'user_updated']
```

---

# Part B — The Three Lesson Examples

## 20. Lesson example 1: Unique visitors

### Requirement

A website records visitor names, including repeated visits. We want the number of visits, the number of distinct visitors, and a membership check for a visitor who may not have appeared.

### Code

```python
visitor_log = ["alice", "bob", "alice", "carol", "bob", "alice"]

unique_visitors = set(visitor_log)

print(sorted(unique_visitors))
print(len(visitor_log))
print(len(unique_visitors))
print("dave" in unique_visitors)
```

Output:

```text
['alice', 'bob', 'carol']
6
3
False
```

### Step-by-step explanation

1. `visitor_log` is a list. It preserves the six visit records, including repeated names.
2. `set(visitor_log)` creates a new set from the list and removes duplicate names.
3. `sorted(unique_visitors)` creates a sorted list for predictable display. It does not sort or mutate the set.
4. `len(visitor_log)` returns `6`, the total number of visits recorded.
5. `len(unique_visitors)` returns `3`, the number of distinct visitors.
6. `"dave" in unique_visitors` returns `False` because the visitor is not in the set.

**Important distinction:** total visits and distinct visitors are different metrics. Converting the log to a set is useful for distinct counting, but it intentionally discards repeat counts and order.

---

## 21. Lesson example 2: Course rosters

### Requirement

Compare the students enrolled in two courses. We need students in both courses, students only in Python, and all students across either course.

### Code

```python
python_students = {"Ada", "Grace", "Alan", "Linus"}
data_students = {"Grace", "Linus", "Marie", "Katherine"}

common_students = python_students.intersection(data_students)
python_only = python_students.difference(data_students)
all_students = python_students.union(data_students)

print("Both courses:", sorted(common_students))
print("Python only:", sorted(python_only))
print("Either course:", sorted(all_students))
```

Output:

```text
Both courses: ['Grace', 'Linus']
Python only: ['Ada', 'Alan']
Either course: ['Ada', 'Alan', 'Grace', 'Katherine', 'Linus', 'Marie']
```

### Understand the three operations

| Operation | Meaning | Result |
|---|---|---|
| `A.intersection(B)` | Present in A and B | Grace, Linus |
| `A.difference(B)` | Present in A but not B | Ada, Alan |
| `A.union(B)` | Present in A or B, or both | All six unique names |

The order in which the input sets were written does not determine the order of their elements. `sorted()` is used only to display results consistently.

---

## 22. Lesson example 3: Article tags

### Requirement

Two articles have tags. We want the common tags, all unique tags, and to verify that every tag from article A occurs in the combined collection.

### Code

```python
article_a_tags = ["python", "tutorial", "beginner", "python"]
article_b_tags = ["python", "advanced", "tips"]

tags_a = set(article_a_tags)
tags_b = set(article_b_tags)

common_tags = tags_a.intersection(tags_b)
all_unique_tags = tags_a.union(tags_b)

print("Common tags:", sorted(common_tags))
print("All tags:", sorted(all_unique_tags))
print("A is subset of all tags:", tags_a.issubset(all_unique_tags))
```

Output:

```text
Common tags: ['python']
All tags: ['advanced', 'beginner', 'python', 'tips', 'tutorial']
A is subset of all tags: True
```

### Step-by-step explanation

1. `set(article_a_tags)` removes the repeated `python` tag from article A.
2. `set(article_b_tags)` creates the unique tags for article B.
3. `intersection()` returns tags shared by both articles. Here, the shared tag is `python`.
4. `union()` combines every unique tag from both articles.
5. `issubset()` verifies whether every tag in `tags_a` is present in `all_unique_tags`.
6. The subset check returns `True` because `all_unique_tags` was created from both `tags_a` and `tags_b`.

---

# Part C — Related Built-ins and Set Operators

## 23. `len(set)` — Count unique elements

`len()` returns the number of elements in the set.

```python
numbers = {5, 3, 8, 1, 3}
print(len(numbers))
```

Output:

```text
4
```

The repeated `3` is stored once, so the set has four elements.

## 24. `sorted(set)` — Return a sorted list

`sorted()` accepts an iterable and returns a **new list** containing its elements in sorted order.

```python
numbers = {5, 3, 8, 1}
result = sorted(numbers)

print(result)
print(type(result))
print(numbers)
```

Output:

```text
[1, 3, 5, 8]
<class 'list'>
{1, 3, 5, 8}
```

Important points:

- `sorted()` does not mutate the set.
- The result is a list, not a set.
- The sorted list is useful when deterministic display or ordered processing is needed.
- The set itself remains unordered.
- Values must be mutually comparable under the ordering used. Mixed incompatible types can raise `TypeError`.

Descending order:

```python
numbers = {5, 3, 8, 1}
print(sorted(numbers, reverse=True))
```

Output:

```text
[8, 5, 3, 1]
```

## 25. `min(set)` — Find the smallest element

```python
numbers = {5, 3, 8, 1}
print(min(numbers))
```

Output:

```text
1
```

`min()` returns the smallest element according to Python's ordering rules. It raises `ValueError` for an empty set unless a `default` is supplied.

```python
empty_values = set()
print(min(empty_values, default=None))
```

Output:

```text
None
```

## 26. `max(set)` — Find the largest element

```python
numbers = {5, 3, 8, 1}
print(max(numbers))
```

Output:

```text
8
```

`max()` returns the largest element according to Python's ordering rules. It raises `ValueError` for an empty set unless a `default` is supplied.

```python
empty_values = set()
print(max(empty_values, default=0))
```

Output:

```text
0
```

## 27. `set(iterable)` — Build a mutable set

```python
values = [1, 2, 2, 3, 3, 3]
unique_values = set(values)

print(sorted(unique_values))
```

Output:

```text
[1, 2, 3]
```

The original list is unchanged. `set()` creates a new set and removes duplicate values.

## 28. `frozenset(iterable)` — Build an immutable set

A `frozenset` is an immutable set-like collection. Its elements must be hashable, and the collection cannot be modified after creation.

```python
values = [1, 2, 2, 3]
immutable_values = frozenset(values)

print(immutable_values)
print(type(immutable_values))
print(sorted(immutable_values))
```

Output:

```text
frozenset({1, 2, 3})
<class 'frozenset'>
[1, 2, 3]
```

These operations are invalid because a `frozenset` cannot be changed:

```python
# immutable_values.add(4)  # AttributeError
# immutable_values.clear()  # AttributeError
```

A `frozenset` supports non-mutating set operations such as `union()`, `intersection()`, and `difference()`. It is hashable when its elements are hashable, so it can itself be an element of another set or a dictionary key.

Example:

```python
permissions = frozenset({"read", "write"})
permission_groups = {permissions, frozenset({"read"})}

print(len(permission_groups))
```

Output:

```text
2
```

Use `frozenset` when the set of values should be immutable and may need to be used as a dictionary key or another set's member.

---

## 29. Set operators: `|`, `&`, `-`, and `^`

Python provides operators for the four main set combinations.

```python
a = {1, 2, 3}
b = {2, 3, 4}

print(sorted(a | b))  # Union
print(sorted(a & b))  # Intersection
print(sorted(a - b))  # Difference
print(sorted(a ^ b))  # Symmetric difference
```

Output:

```text
[1, 2, 3, 4]
[2, 3]
[1]
[1, 4]
```

| Operator | Method form | Meaning |
|---|---|---|
| `A \| B` | `A.union(B)` | Elements in A or B or both |
| `A & B` | `A.intersection(B)` | Elements in both A and B |
| `A - B` | `A.difference(B)` | Elements in A but not B |
| `A ^ B` | `A.symmetric_difference(B)` | Elements in exactly one of A and B |

### Important: method operands versus operator operands

Set methods such as `union()`, `intersection()`, and `difference()` accept arbitrary iterables as their arguments. The corresponding binary operators are stricter: their operands must be set-like values (`set` or `frozenset`), not an arbitrary list.

```python
values = {1, 2, 3}

print(sorted(values.union([3, 4])))
# [1, 2, 3, 4]

# values | [3, 4]  # TypeError: the | operator does not accept a list
```

Convert the list first when you want to use an operator:

```python
print(sorted(values | set([3, 4])))
```

Output:

```text
[1, 2, 3, 4]
```

### In-place set operators

The augmented operators update the left-hand set:

| In-place operator | Similar method |
|---|---|
| `A |= B` | `A.update(B)` |
| `A &= B` | `A.intersection_update(B)` |
| `A -= B` | `A.difference_update(B)` |
| `A ^= B` | `A.symmetric_difference_update(B)` |

Example:

```python
numbers = {1, 2, 3}
numbers |= {3, 4}
print(sorted(numbers))
```

Output:

```text
[1, 2, 3, 4]
```

---

# Part D — Critical Concepts and Common Mistakes

## 30. Mistake: using `{}` to create an empty set

Incorrect:

```python
empty_values = {}
print(type(empty_values))
```

Output:

```text
<class 'dict'>
```

Correct:

```python
empty_values = set()
print(type(empty_values))
```

Output:

```text
<class 'set'>
```

## 31. Mistake: trying to index or slice a set

Incorrect:

```python
numbers = {10, 20, 30}

# print(numbers[0])     # TypeError: 'set' object is not subscriptable
# print(numbers[0:2])   # TypeError
```

A set has no positional indexing. Convert it to a list only when you intentionally need a list representation:

```python
numbers = {10, 20, 30}
values = sorted(numbers)

print(values[0])
print(values[0:2])
```

Output:

```text
10
[10, 20]
```

The sorted list has a defined order. Converting an arbitrary set directly to a list does not recover the original insertion order, because sets do not preserve that as a contract.

## 32. Mistake: relying on the order of a set

Do not write logic that assumes a set will print or iterate in a particular sequence.

```python
colors = {"red", "green", "blue"}

for color in colors:
    print(color)
```

The order is not guaranteed. When predictable display order is required:

```python
for color in sorted(colors):
    print(color)
```

Output:

```text
blue
green
red
```

## 33. Mistake: inserting unhashable values

Incorrect:

```python
# values = {[1, 2], [3, 4]}       # TypeError
# values = {{"id": 1}}            # TypeError
```

Correct for coordinate pairs:

```python
coordinates = {(1, 2), (3, 4)}
print(sorted(coordinates))
```

Output:

```text
[(1, 2), (3, 4)]
```

The tuple values are hashable because they contain only hashable elements.

## 34. Mistake: assuming conversion to a list restores order

```python
original_list = ["b", "a", "b", "c"]
unique_set = set(original_list)
converted_list = list(unique_set)

print(sorted(converted_list))
```

Output:

```text
['a', 'b', 'c']
```

A set removes duplicates but does not preserve the original list's sequence. If both uniqueness and original encounter order are required, use a different technique:

```python
original_list = ["b", "a", "b", "c"]
unique_in_order = list(dict.fromkeys(original_list))

print(unique_in_order)
```

Output:

```text
['b', 'a', 'c']
```

This uses dictionary insertion order (guaranteed by the Python language from Python 3.7 onward) to preserve the first occurrence of each value.

## 35. Mistake: confusing difference and symmetric difference

Given:

```python
A = {1, 2, 3}
B = {2, 3, 4}
```

Directional difference:

```python
print(sorted(A - B))
```

Output:

```text
[1]
```

Symmetric difference:

```python
print(sorted(A ^ B))
```

Output:

```text
[1, 4]
```

- Difference (`A - B`) returns values only from the left-hand set.
- Symmetric difference (`A ^ B`) returns values unique to either set.

## 36. Mistake: using `remove()` when absence is expected

This can raise `KeyError`:

```python
users = {"alice", "bob"}
# users.remove("carol")
```

Use `discard()` when absence is acceptable:

```python
users = {"alice", "bob"}
users.discard("carol")
print(sorted(users))
```

Output:

```text
['alice', 'bob']
```

## 37. Mistake: expecting `pop()` to remove a particular element

A set has no index. `set.pop()` removes an arbitrary element. It does not mean “remove the last inserted element.”

If you need to remove a specific value, use `remove(value)` or `discard(value)`.

## 38. Mistake: assigning the result of an in-place method

Incorrect:

```python
numbers = {1, 2, 3}
numbers = numbers.update({4, 5})
print(numbers)  # None
```

Correct:

```python
numbers = {1, 2, 3}
numbers.update({4, 5})
print(sorted(numbers))
```

Output:

```text
[1, 2, 3, 4, 5]
```

Methods such as `add()`, `clear()`, `difference_update()`, `discard()`, `intersection_update()`, `remove()`, `symmetric_difference_update()`, and `update()` mutate the set and return `None`.

---

# Part E — New Set versus In-Place Mutation

## 39. The most important comparison table

| Non-mutating method | Result | Mutating counterpart | Effect |
|---|---|---|---|
| `copy()` | New set with same elements | — | Original unchanged |
| `difference()` | New set containing left-only values | `difference_update()` | Removes other values from original |
| `intersection()` | New set containing shared values | `intersection_update()` | Keeps only shared values in original |
| `symmetric_difference()` | New set containing values in exactly one input | `symmetric_difference_update()` | Replaces original contents with that result |
| `union()` | New set containing all unique values | `update()` | Adds values to original |

The following methods do not fit a new-set/in-place pair in this table:

| Method | Behavior |
|---|---|
| `add()` | Adds one element to the original set |
| `clear()` | Empties the original set |
| `discard()` | Removes a value if present |
| `isdisjoint()` | Returns a Boolean; does not mutate |
| `issubset()` | Returns a Boolean; does not mutate |
| `issuperset()` | Returns a Boolean; does not mutate |
| `pop()` | Removes and returns an arbitrary element |
| `remove()` | Removes a required element or raises `KeyError` |

## 40. Demonstrate the difference with object identity

```python
original = {1, 2, 3}

# Non-mutating operation: a new set is returned.
new_result = original.union({3, 4})

print(sorted(original))
print(sorted(new_result))
print(original is new_result)
```

Output:

```text
[1, 2, 3]
[1, 2, 3, 4]
False
```

Now compare it with `update()`:

```python
original = {1, 2, 3}

same_object = original
original.update({3, 4})

print(sorted(original))
print(sorted(same_object))
print(original is same_object)
```

Output:

```text
[1, 2, 3, 4]
[1, 2, 3, 4]
True
```

Both names refer to the same set object, so the mutation is visible through both names.

---

# Part F — Practical Data Engineering Applications

## 41. Use case 1: Find duplicate-free IDs in an ingestion batch

```python
incoming_ids = [101, 102, 101, 103, 102, 104]
unique_ids = set(incoming_ids)

print("Rows received:", len(incoming_ids))
print("Distinct IDs:", len(unique_ids))
print("Unique IDs:", sorted(unique_ids))
```

Output:

```text
Rows received: 6
Distinct IDs: 4
Unique IDs: [101, 102, 103, 104]
```

**Engineering interpretation:** the list represents rows or events received; the set represents distinct IDs. Do not use the set if duplicate frequency or original row order is needed for downstream logic.

## 42. Use case 2: Find IDs missing from the target

```python
source_ids = {1001, 1002, 1003, 1004, 1005}
target_ids = {1001, 1003, 1005}

missing_from_target = source_ids - target_ids

print(sorted(missing_from_target))
```

Output:

```text
[1002, 1004]
```

**Engineering interpretation:** this identifies IDs that exist in the in-memory source collection but are not present in the target collection. In a real reconciliation pipeline, compare equivalent snapshots or watermarks and account for late-arriving data, deletes, and transaction boundaries.

## 43. Use case 3: Detect schema additions and removals

```python
old_schema = {"customer_id", "name", "email", "created_at"}
new_schema = {"customer_id", "name", "phone", "created_at"}

added_columns = new_schema - old_schema
removed_columns = old_schema - new_schema
unchanged_columns = old_schema & new_schema

print("Added:", sorted(added_columns))
print("Removed:", sorted(removed_columns))
print("Unchanged:", sorted(unchanged_columns))
```

Output:

```text
Added: ['phone']
Removed: ['email']
Unchanged: ['created_at', 'customer_id', 'name']
```

**Engineering interpretation:** set comparisons help detect field-name changes. A production schema validator must also inspect types, nullability, nested structures, defaults, and compatibility rules.

## 44. Use case 4: Check required columns before processing

```python
required_columns = {"order_id", "customer_id", "order_total"}
incoming_columns = {"order_id", "customer_id", "order_total", "source_system"}

if required_columns.issubset(incoming_columns):
    print("Schema contains all required columns")
else:
    missing_columns = required_columns - incoming_columns
    print("Missing:", sorted(missing_columns))
```

Output:

```text
Schema contains all required columns
```

## 45. Use case 5: Identify unexpected columns

```python
allowed_columns = {"order_id", "customer_id", "order_total"}
incoming_columns = {"order_id", "customer_id", "order_total", "debug_payload"}

unexpected_columns = incoming_columns - allowed_columns

print(sorted(unexpected_columns))
```

Output:

```text
['debug_payload']
```

Unexpected does not automatically mean invalid. Your pipeline's schema-evolution policy should decide whether to reject, quarantine, log, or accept extra fields.

## 46. Use case 6: Determine whether a batch contains blocked IDs

```python
blocked_ids = {7001, 7002, 7003}
incoming_ids = {1001, 7002, 1002}

if not blocked_ids.isdisjoint(incoming_ids):
    print("At least one blocked ID is present")
else:
    print("No blocked IDs found")
```

Output:

```text
At least one blocked ID is present
```

For diagnostic detail:

```python
found_blocked_ids = blocked_ids.intersection(incoming_ids)
print(sorted(found_blocked_ids))
```

Output:

```text
[7002]
```

## 47. Use case 7: Accumulate unique event types from multiple batches

```python
observed_event_types = set()

batch_1 = ["created", "updated", "created"]
batch_2 = ["deleted", "updated"]
batch_3 = ["payment_received", "created"]

observed_event_types.update(batch_1)
observed_event_types.update(batch_2)
observed_event_types.update(batch_3)

print(sorted(observed_event_types))
```

Output:

```text
['created', 'deleted', 'payment_received', 'updated']
```

The set is a compact way to track which event types have appeared. It does not store event counts or event order.

---

# Part G — Time Complexity and Performance Notes

## 48. Average-case time complexity

Set operations are generally implemented using hash tables. The following are typical average-case complexities for common built-in set operations. Exact performance depends on collection size, hash distribution, and implementation details.

| Operation | Typical average-case complexity | Notes |
|---|---:|---|
| `value in my_set` | `O(1)` | Average membership lookup |
| `add(value)` | `O(1)` | Average insertion |
| `discard(value)` | `O(1)` | Average lookup/removal |
| `remove(value)` | `O(1)` | Average lookup/removal; raises if missing |
| `pop()` | `O(1)` | Removes an arbitrary element |
| `copy()` | `O(n)` | Copies all elements |
| `clear()` | `O(n)` | Releases/removes the stored entries |
| `len(my_set)` | `O(1)` | Set size is maintained |
| `union()` | `O(n + m)` | Proportional to input sizes in a typical case |
| `intersection()` | Often `O(min(n, m))` membership checks plus result construction | Implementation may optimize based on sizes |
| `difference()` | Typically `O(n)` membership checks against the other collection | Depends on input sizes and iterable behavior |
| `symmetric_difference()` | Typically `O(n + m)` | Builds the elements unique to either side |

Here, `n` and `m` are the sizes of the participating collections. These are useful mental models, not worst-case guarantees. Hash collisions can degrade performance.

### Why membership checks are useful

```python
allowed_ids = {101, 102, 103, 104, 105}

if 103 in allowed_ids:
    print("ID is allowed")
```

Output:

```text
ID is allowed
```

Sets are often a good fit for repeated membership tests, provided the values are hashable and uniqueness is desired.

---

# Part H — Practice Exercises

Try each exercise before looking at its solution. The exercises use the methods introduced in this document.

## 49. Exercise 1 — Create a set from a list

Given:

```python
numbers = [10, 20, 10, 30, 20, 40]
```

Create a set of unique numbers and print it in ascending order.

### Solution

```python
numbers = [10, 20, 10, 30, 20, 40]
unique_numbers = set(numbers)

print(sorted(unique_numbers))
```

Output:

```text
[10, 20, 30, 40]
```

## 50. Exercise 2 — Add an element

Create a set containing `"Python"` and `"SQL"`. Add `"Spark"` and print the sorted result.

### Solution

```python
skills = {"Python", "SQL"}
skills.add("Spark")

print(sorted(skills))
```

Output:

```text
['Python', 'SQL', 'Spark']
```

## 51. Exercise 3 — Find common values

Given:

```python
A = {10, 20, 30, 40}
B = {30, 40, 50, 60}
```

Print the common values.

### Solution

```python
A = {10, 20, 30, 40}
B = {30, 40, 50, 60}

print(sorted(A.intersection(B)))
```

Output:

```text
[30, 40]
```

## 52. Exercise 4 — Find left-only values

Using the same `A` and `B`, print values present in `A` but absent from `B`.

### Solution

```python
A = {10, 20, 30, 40}
B = {30, 40, 50, 60}

print(sorted(A.difference(B)))
```

Output:

```text
[10, 20]
```

## 53. Exercise 5 — Find the union

Using the same `A` and `B`, print every unique value.

### Solution

```python
A = {10, 20, 30, 40}
B = {30, 40, 50, 60}

print(sorted(A.union(B)))
```

Output:

```text
[10, 20, 30, 40, 50, 60]
```

## 54. Exercise 6 — Check subset membership

Check whether `{1, 2}` is a subset of `{1, 2, 3, 4}`.

### Solution

```python
small = {1, 2}
large = {1, 2, 3, 4}

print(small.issubset(large))
```

Output:

```text
True
```

## 55. Exercise 7 — Remove safely

Remove `"bob"` from a set if it exists, without raising an error if it does not.

### Solution

```python
users = {"alice", "bob", "carol"}
users.discard("bob")
users.discard("dave")

print(sorted(users))
```

Output:

```text
['alice', 'carol']
```

## 56. Exercise 8 — Use `difference_update()`

Start with `{1, 2, 3, 4, 5}` and remove `{2, 4}` from the original set.

### Solution

```python
numbers = {1, 2, 3, 4, 5}
numbers.difference_update({2, 4})

print(sorted(numbers))
```

Output:

```text
[1, 3, 5]
```

## 57. Exercise 9 — Use `symmetric_difference()`

Given `{1, 2, 3}` and `{3, 4, 5}`, find values present in exactly one set.

### Solution

```python
A = {1, 2, 3}
B = {3, 4, 5}

print(sorted(A.symmetric_difference(B)))
```

Output:

```text
[1, 2, 4, 5]
```

## 58. Exercise 10 — Check disjointness

Check whether `{1, 2}` and `{3, 4}` have any common elements.

### Solution

```python
A = {1, 2}
B = {3, 4}

print(A.isdisjoint(B))
```

Output:

```text
True
```

## 59. Exercise 11 — Identify missing target IDs

Given:

```python
source_ids = {101, 102, 103, 104}
target_ids = {101, 103}
```

Find the IDs missing from the target.

### Solution

```python
source_ids = {101, 102, 103, 104}
target_ids = {101, 103}

missing_ids = source_ids - target_ids
print(sorted(missing_ids))
```

Output:

```text
[102, 104]
```

## 60. Exercise 12 — Detect schema changes

Given:

```python
old_columns = {"id", "name", "email"}
new_columns = {"id", "name", "phone"}
```

Find added columns, removed columns, and unchanged columns.

### Solution

```python
old_columns = {"id", "name", "email"}
new_columns = {"id", "name", "phone"}

added = new_columns - old_columns
removed = old_columns - new_columns
unchanged = old_columns & new_columns

print("Added:", sorted(added))
print("Removed:", sorted(removed))
print("Unchanged:", sorted(unchanged))
```

Output:

```text
Added: ['phone']
Removed: ['email']
Unchanged: ['id', 'name']
```

---

# Part I — Quick Revision Reference

## 61. All 17 methods in one table

| # | Method | What it does | Return value | Mutates? |
|---:|---|---|---|---|
| 1 | `add(value)` | Adds one element | `None` | Yes |
| 2 | `clear()` | Removes all elements | `None` | Yes |
| 3 | `copy()` | Makes a shallow copy | New set | No |
| 4 | `difference(other)` | Returns left-only elements | New set | No |
| 5 | `difference_update(other)` | Removes other elements from this set | `None` | Yes |
| 6 | `discard(value)` | Removes value if present | `None` | Yes, if present |
| 7 | `intersection(other)` | Returns shared elements | New set | No |
| 8 | `intersection_update(other)` | Keeps only shared elements | `None` | Yes |
| 9 | `isdisjoint(other)` | Checks for no overlap | `bool` | No |
| 10 | `issubset(other)` | Checks whether this set is contained in other | `bool` | No |
| 11 | `issuperset(other)` | Checks whether this set contains other | `bool` | No |
| 12 | `pop()` | Removes and returns arbitrary element | Removed element | Yes |
| 13 | `remove(value)` | Removes required element | `None` | Yes |
| 14 | `symmetric_difference(other)` | Returns elements in exactly one set | New set | No |
| 15 | `symmetric_difference_update(other)` | Updates to symmetric difference | `None` | Yes |
| 16 | `union(other)` | Combines unique elements | New set | No |
| 17 | `update(other)` | Adds elements from iterables | `None` | Yes |

## 62. Important rules to remember

1. A set stores unique, hashable values.
2. Use `set()` for an empty set; `{}` creates a dictionary.
3. Sets do not support indexing or slicing.
4. Do not rely on set iteration or display order.
5. Use `sorted(my_set)` when you need deterministic ordered output; it returns a list.
6. `difference()` is directional; `symmetric_difference()` includes values unique to either side.
7. Use `discard()` when a value may be absent; use `remove()` when absence should raise `KeyError`.
8. `set.pop()` removes an arbitrary element, not an element at an index.
9. Non-mutating methods return a new set; in-place update methods return `None`.
10. Set methods accept iterables in many cases; set operators require set-like operands.
11. `frozenset` is immutable and can be hashable.
12. A set is useful for distinct values and membership checks, but it does not preserve duplicate counts or row order.

## 63. Verify your Python version

Run:

```bash
python3 --version
```

The core set methods in this lesson are available in modern Python 3 versions. `set` and `frozenset` are built-in types; no third-party package is required.

---

## Final engineering takeaway

Sets are especially useful in data engineering when you need to represent **unique identifiers**, perform **fast membership checks**, compare **source and target IDs**, detect **schema differences**, validate **required fields**, or combine categories without duplicates.

However, a set is not a replacement for a list, database table, or DataFrame. It discards duplicate occurrences and does not provide a stable positional order. Select the collection based on the information your pipeline must preserve:

- Use a **list** when sequence and duplicates matter.
- Use a **set** when uniqueness and membership tests matter.
- Use a **frozenset** when you need set semantics but the collection itself must be immutable.

**End of `08-sets-methods.md`.**
