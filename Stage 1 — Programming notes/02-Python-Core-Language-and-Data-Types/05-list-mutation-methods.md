# 05 — List Mutation Methods

> **Lesson goal:** Understand every commonly used Python list method in this lesson, how to call it, whether it changes the original list, what it returns, and when it is useful in data-engineering and Python applications.
>
> **Prerequisite:** Basic Python variables, strings, numbers, `print()`, and list indexing.

---

## 1. What is a Python list?

A **list** is an ordered, mutable collection in Python. It can store multiple values, preserve their order, contain duplicate values, and hold values of different data types.

```python
documents = ["invoice_001.pdf", "invoice_002.pdf", "invoice_003.pdf"]

print(documents)
print(documents[0])
```

Output:

```text
['invoice_001.pdf', 'invoice_002.pdf', 'invoice_003.pdf']
invoice_001.pdf
```

- **Ordered** means each item has a position (index), starting at `0`.
- **Mutable** means the list can be changed after it is created.
- **Duplicate values** are allowed.

The methods in this lesson let you add, remove, rearrange, search, count, sort, and copy list elements.

## 2. Important terms: mutation and return value

Before learning the methods, understand these two terms:

### Mutation

A method **mutates** a list when it changes the existing list object itself.

```python
numbers = [10, 20, 30]
numbers.append(40)

print(numbers)
```

Output:

```text
[10, 20, 30, 40]
```

The original `numbers` list has changed. A new list was not required.

### Return value

A method's **return value** is the result that the method gives back to the caller.

Some list methods modify the list and return `None`. Other methods return useful information, such as the removed item or the position of a matching item.

```python
numbers = [10, 20, 30]
result = numbers.append(40)

print(numbers)
print(result)
```

Output:

```text
[10, 20, 30, 40]
None
```

**Important:** Do not assume that a method returns the modified list just because it changes the list.

---

## 3. `append(item)` — Add one item to the end

### Purpose

`append(item)` adds **one object** to the end of the existing list. It mutates the list and returns `None`.

### Syntax

```python
list_name.append(item)
```

### Example 1: Append a string

```python
documents = ["report_001.pdf", "report_002.pdf"]

documents.append("report_003.pdf")

print(documents)
```

Output:

```text
['report_001.pdf', 'report_002.pdf', 'report_003.pdf']
```

**Explanation:**

1. `documents` initially contains two file names.
2. `documents.append("report_003.pdf")` adds the supplied string after the current last item.
3. The original `documents` list now contains three elements.

### Example 2: Append a list as one nested item

```python
batches = ["batch_001", "batch_002"]

batches.append(["batch_003", "batch_004"])

print(batches)
print(len(batches))
```

Output:

```text
['batch_001', 'batch_002', ['batch_003', 'batch_004']]
3
```

**Explanation:** `append()` adds the entire inner list as a single element. It does not take the inner list apart. That is why the outer list has three elements, and its third element is itself a list.

### Example 3: Check the return value

```python
numbers = [1, 2, 3]

result = numbers.append(4)

print(numbers)
print(result)
```

Output:

```text
[1, 2, 3, 4]
None
```

### Data-engineering use case

Use `append()` when processing one record at a time and collecting each processed record in a list.

```python
processed_records = []

record = {"id": 101, "status": "valid"}
processed_records.append(record)

print(processed_records)
```

### Key points

- Adds exactly one object.
- Adds it at the end.
- Mutates the original list.
- Returns `None`.
- Use it when one item (including a nested list or dictionary) should become one element of the destination list.

---

## 4. `extend(iterable)` — Add each element from an iterable

### Purpose

`extend(iterable)` takes an iterable and adds each of its elements individually to the end of the list. It mutates the original list and returns `None`.

An **iterable** is an object that Python can loop over, such as a list, tuple, string, set, or dictionary.

### Syntax

```python
list_name.extend(iterable)
```

### Example 1: Extend with another list

```python
existing_files = ["file_001.csv", "file_002.csv"]
new_files = ["file_003.csv", "file_004.csv"]

existing_files.extend(new_files)

print(existing_files)
```

Output:

```text
['file_001.csv', 'file_002.csv', 'file_003.csv', 'file_004.csv']
```

**Explanation:** Python takes each item from `new_files` and adds it to `existing_files`. The two new file names become two separate elements.

### Example 2: Compare `append()` and `extend()`

```python
append_target = [1, 2]
extend_target = [1, 2]
source = [3, 4]

append_target.append(source)
extend_target.extend(source)

print(append_target)
print(extend_target)
```

Output:

```text
[1, 2, [3, 4]]
[1, 2, 3, 4]
```

**Explanation:**

- `append(source)` adds `source` as one nested list element.
- `extend(source)` adds the elements `3` and `4` separately.

This is the most important difference between these two methods.

### Example 3: Extend with a tuple

```python
numbers = [10, 20]

numbers.extend((30, 40))

print(numbers)
```

Output:

```text
[10, 20, 30, 40]
```

### Example 4: Extend with a string

```python
letters = ["A", "B"]

letters.extend("CD")

print(letters)
```

Output:

```text
['A', 'B', 'C', 'D']
```

**Explanation:** A string is iterable. Python iterates over it one character at a time, so `"C"` and `"D"` are added separately.

### Example 5: Extend with a dictionary

```python
fields = ["id"]

fields.extend({"name": "Asha", "status": "valid"})

print(fields)
```

Output:

```text
['id', 'name', 'status']
```

**Explanation:** Iterating over a dictionary produces its keys by default, not its values or key-value pairs.

### Data-engineering use case

Use `extend()` when a function returns a batch of records and you want to combine that batch with the records already collected.

```python
all_records = [
    {"id": 1, "amount": 250},
    {"id": 2, "amount": 400},
]

next_batch = [
    {"id": 3, "amount": 150},
    {"id": 4, "amount": 700},
]

all_records.extend(next_batch)

print(all_records)
```

### Key points

- Adds each element from the iterable.
- Does not add the iterable as one nested object.
- Mutates the original list.
- Returns `None`.
- Be careful when extending with strings (characters) or dictionaries (keys).

---

## 5. `insert(index, item)` — Insert an item at a position

### Purpose

`insert(index, item)` places one item at a specified position in the list. Existing elements at that position and after it shift to the right. It mutates the list and returns `None`.

### Syntax

```python
list_name.insert(index, item)
```

### Example 1: Insert at the beginning

```python
tasks = ["transform", "load"]

tasks.insert(0, "extract")

print(tasks)
```

Output:

```text
['extract', 'transform', 'load']
```

**Explanation:** Index `0` is the first position. The new item is inserted before the previous first item.

### Example 2: Insert in the middle

```python
pipeline_steps = ["extract", "load"]

pipeline_steps.insert(1, "transform")

print(pipeline_steps)
```

Output:

```text
['extract', 'transform', 'load']
```

**Explanation:** Index `1` is the position between the first and second elements. The previous item at index `1` shifts to index `2`.

### Example 3: Insert at or beyond the end

```python
numbers = [10, 20, 30]

numbers.insert(3, 40)
numbers.insert(100, 50)

print(numbers)
```

Output:

```text
[10, 20, 30, 40, 50]
```

**Explanation:** An index greater than the list length inserts the item at the end; it does not create empty positions.

### Example 4: Use a negative index

```python
letters = ["A", "C", "D"]

letters.insert(-2, "B")

print(letters)
```

Output:

```text
['A', 'B', 'C', 'D']
```

**Explanation:** A negative index is interpreted relative to the end. Here, `-2` identifies the position before the original second-last element.

### Data-engineering use case

Use `insert()` when a small, ordered list of pipeline steps needs a new step at a specific position. For large lists, repeated insertion near the beginning can be inefficient because many elements must shift.

### Key points

- Takes an index and one item.
- Inserts before the item currently at that position.
- Mutates the original list.
- Returns `None`.
- An index beyond the end inserts at the end.

---

## 6. `remove(value)` — Remove the first matching value

### Purpose

`remove(value)` searches for the first element equal to `value` and removes that element. It mutates the list and returns `None`.

If the value does not exist, Python raises a `ValueError`.

### Syntax

```python
list_name.remove(value)
```

### Example 1: Remove an existing value

```python
statuses = ["pending", "valid", "failed", "valid"]

statuses.remove("valid")

print(statuses)
```

Output:

```text
['pending', 'failed', 'valid']
```

**Explanation:** There are two occurrences of `"valid"`, but `remove()` removes only the first matching occurrence. The second one remains.

### Example 2: Remove a number

```python
numbers = [10, 20, 30, 20, 40]

numbers.remove(20)

print(numbers)
```

Output:

```text
[10, 30, 20, 40]
```

### Example 3: Handle a value that may be absent

```python
failed_files = ["a.csv", "b.csv", "c.csv"]
file_to_remove = "d.csv"

if file_to_remove in failed_files:
    failed_files.remove(file_to_remove)
else:
    print("File was not present in the list.")

print(failed_files)
```

Output:

```text
File was not present in the list.
['a.csv', 'b.csv', 'c.csv']
```

**Explanation:** The membership test (`in`) prevents `remove()` from raising `ValueError` in this example.

### Example 4: Understand the error

```python
numbers = [1, 2, 3]

numbers.remove(99)
```

This raises an error similar to:

```text
ValueError: list.remove(x): x not in list
```

### Data-engineering use case

You might remove a known item from a small in-memory work queue after it has been handled. For high-volume queues or frequent removals, use a data structure designed for queue operations rather than repeatedly searching and shifting a large list.

### Key points

- Removes by **value**, not by index.
- Removes only the first matching occurrence.
- Mutates the original list.
- Returns `None`.
- Raises `ValueError` if the value is absent.

---

## 7. `pop(index=-1)` — Remove and return an item

### Purpose

`pop()` removes an item from a list and **returns the removed item**. If no index is supplied, it removes the last item. It mutates the list.

### Syntax

```python
list_name.pop()       # Remove and return the last item
list_name.pop(index)  # Remove and return the item at index
```

### Example 1: Pop the last item

```python
tasks = ["extract", "transform", "load"]

removed_task = tasks.pop()

print("Removed:", removed_task)
print("Remaining:", tasks)
```

Output:

```text
Removed: load
Remaining: ['extract', 'transform']
```

**Explanation:** With no argument, `pop()` uses index `-1`, which means the last element.

### Example 2: Pop by index

```python
documents = ["doc_001.pdf", "doc_002.pdf", "doc_003.pdf"]

removed_document = documents.pop(1)

print("Removed:", removed_document)
print("Remaining:", documents)
```

Output:

```text
Removed: doc_002.pdf
Remaining: ['doc_001.pdf', 'doc_003.pdf']
```

**Explanation:** Index `1` is the second element. That element is removed and returned.

### Example 3: Capture the returned item for processing

```python
pending_jobs = ["job_101", "job_102", "job_103"]

next_job = pending_jobs.pop(0)

print("Job selected for processing:", next_job)
print("Jobs still pending:", pending_jobs)
```

Output:

```text
Job selected for processing: job_101
Jobs still pending: ['job_102', 'job_103']
```

This works as a simple demonstration of taking the first item from a list. However, repeatedly using `pop(0)` on a large list is inefficient because the remaining items must shift left. For a production FIFO queue, Python's `collections.deque` is usually a better choice.

### Example 4: Pop from an empty list

```python
empty_list = []
empty_list.pop()
```

This raises:

```text
IndexError: pop from empty list
```

Check before popping when the list might be empty:

```python
if pending_jobs:
    next_job = pending_jobs.pop(0)
    print(next_job)
else:
    print("No jobs are pending.")
```

### Key points

- Removes an item by index.
- Defaults to the last item (`index=-1`).
- Mutates the original list.
- Returns the removed item (unlike `remove()`).
- Raises `IndexError` if the list is empty or the index is out of range.

---

## 8. `clear()` — Remove all elements

### Purpose

`clear()` removes every element from the existing list. The list object remains, but it becomes empty. It mutates the list and returns `None`.

### Syntax

```python
list_name.clear()
```

### Example 1: Clear a list

```python
temporary_records = [101, 102, 103, 104]

temporary_records.clear()

print(temporary_records)
print(len(temporary_records))
```

Output:

```text
[]
0
```

### Example 2: The list object is still the same object

```python
records = ["record_1", "record_2"]
same_list = records

records.clear()

print(records)
print(same_list)
print(records is same_list)
```

Output:

```text
[]
[]
True
```

**Explanation:** Both variables refer to the same list object. Clearing it through `records` is visible through `same_list` as well.

### Data-engineering use case

A temporary list might be cleared after a batch has been written successfully. Do this only when no other part of the application still needs the collected records.

### Key points

- Removes all elements.
- Does not delete the variable or replace the list with a different object.
- Mutates the original list.
- Returns `None`.
- Be careful with aliases: other variables referring to the same list also see it become empty.

---

## 9. `index(value)` — Find the first matching position

### Purpose

`index(value)` returns the index of the first element equal to `value`. It does not mutate the list.

If the value is absent, it raises `ValueError`.

### Syntax

```python
list_name.index(value)
list_name.index(value, start)
list_name.index(value, start, stop)
```

The optional `start` and `stop` arguments restrict the search to a slice-like range. The `stop` position is excluded.

### Example 1: Find an item's index

```python
columns = ["customer_id", "name", "email", "status"]

position = columns.index("email")

print(position)
```

Output:

```text
2
```

**Explanation:** List indexing starts at `0`, so `"email"` is at index `2`.

### Example 2: Find the first occurrence when duplicates exist

```python
numbers = [10, 20, 30, 20, 40]

position = numbers.index(20)

print(position)
```

Output:

```text
1
```

**Explanation:** `20` occurs at indexes `1` and `3`; `index()` returns the first position only.

### Example 3: Search from a starting position

```python
numbers = [10, 20, 30, 20, 40]

position = numbers.index(20, 2)

print(position)
```

Output:

```text
3
```

**Explanation:** The search starts at index `2`, so the occurrence at index `1` is ignored.

### Example 4: Search within a range

```python
numbers = [10, 20, 30, 20, 40]

position = numbers.index(20, 2, 4)

print(position)
```

Output:

```text
3
```

**Explanation:** Python searches indexes `2` and `3`. The `stop` index `4` is excluded.

### Example 5: Handle a missing value

```python
columns = ["customer_id", "name", "email"]

if "phone" in columns:
    print(columns.index("phone"))
else:
    print("Column not found.")
```

Output:

```text
Column not found.
```

Without the membership check, `columns.index("phone")` would raise `ValueError`.

### Key points

- Searches by value and returns an integer index.
- Returns the first matching index.
- Does not mutate the list.
- Supports optional `start` and `stop` boundaries.
- Raises `ValueError` when no matching value is found in the searched range.

---

## 10. `count(value)` — Count occurrences of a value

### Purpose

`count(value)` returns the number of times a value appears in the list. It does not mutate the list.

### Syntax

```python
list_name.count(value)
```

### Example 1: Count repeated strings

```python
statuses = ["success", "failed", "success", "pending", "success"]

success_count = statuses.count("success")

print(success_count)
```

Output:

```text
3
```

**Explanation:** `"success"` appears three times in the list.

### Example 2: Count a number

```python
response_codes = [200, 404, 200, 500, 200, 404]

print(response_codes.count(404))
```

Output:

```text
2
```

### Example 3: Count a value that does not exist

```python
numbers = [1, 2, 3, 2]

print(numbers.count(99))
```

Output:

```text
0
```

Unlike `index()` and `remove()`, `count()` does not raise an error when the value is absent.

### Data-engineering use case

For a small in-memory batch, `count()` can quickly show how many records have a particular status. For large datasets, use a database aggregation or a suitable dataframe operation rather than repeatedly scanning a large Python list.

```python
record_statuses = ["valid", "invalid", "valid", "valid", "invalid"]

valid_records = record_statuses.count("valid")
invalid_records = record_statuses.count("invalid")

print("Valid:", valid_records)
print("Invalid:", invalid_records)
```

Output:

```text
Valid: 3
Invalid: 2
```

### Key points

- Returns the number of matching elements.
- Does not mutate the list.
- Returns `0` if the value is absent.
- Counts all occurrences, not only the first one.

---

## 11. `reverse()` — Reverse the list in place

### Purpose

`reverse()` reverses the current order of the elements in the same list. It mutates the list and returns `None`.

It does **not** sort the values. It simply changes their order from last-to-first.

### Syntax

```python
list_name.reverse()
```

### Example 1: Reverse a list of strings

```python
tasks = ["extract", "transform", "load"]

tasks.reverse()

print(tasks)
```

Output:

```text
['load', 'transform', 'extract']
```

### Example 2: Reverse a list of numbers

```python
numbers = [10, 30, 20, 50, 40]

numbers.reverse()

print(numbers)
```

Output:

```text
[40, 50, 20, 30, 10]
```

**Explanation:** The original order is reversed exactly. The numbers are not arranged numerically.

### Example 3: Check the return value

```python
letters = ["A", "B", "C"]

result = letters.reverse()

print(letters)
print(result)
```

Output:

```text
['C', 'B', 'A']
None
```

### Important distinction: `reverse()` versus `reversed()`

- `list_name.reverse()` changes the existing list and returns `None`.
- `reversed(list_name)` returns an iterator in reverse order and leaves the original list unchanged.

```python
numbers = [1, 2, 3]

reversed_iterator = reversed(numbers)

print(list(reversed_iterator))
print(numbers)
```

Output:

```text
[3, 2, 1]
[1, 2, 3]
```

### Key points

- Reverses the existing order; it does not sort.
- Mutates the original list.
- Returns `None`.
- Use `reversed()` or slicing (`numbers[::-1]`) when you need a reversed result without changing the original list.

---

## 12. `sort(reverse=True)` — Sort the list in place

### Purpose

`sort()` arranges the elements of a list in order. It mutates the original list and returns `None`.

The actual method supports the following parameters:

```python
list_name.sort(*, key=None, reverse=False)
```

- `reverse=False` is the default and sorts in ascending order.
- `reverse=True` sorts in descending order.
- `key` optionally supplies a function that determines the sort value for each element.

### Example 1: Sort numbers in ascending order

```python
numbers = [50, 10, 40, 20, 30]

numbers.sort()

print(numbers)
```

Output:

```text
[10, 20, 30, 40, 50]
```

### Example 2: Sort numbers in descending order

```python
numbers = [50, 10, 40, 20, 30]

numbers.sort(reverse=True)

print(numbers)
```

Output:

```text
[50, 40, 30, 20, 10]
```

**Explanation:** `reverse=True` tells Python to place larger values before smaller values.

### Example 3: Sort strings alphabetically

```python
names = ["Ravi", "Asha", "Zoya", "Kabir"]

names.sort()

print(names)
```

Output:

```text
['Asha', 'Kabir', 'Ravi', 'Zoya']
```

### Example 4: Sort strings in reverse alphabetical order

```python
names = ["Ravi", "Asha", "Zoya", "Kabir"]

names.sort(reverse=True)

print(names)
```

Output:

```text
['Zoya', 'Ravi', 'Kabir', 'Asha']
```

### Example 5: Sort using `key`

Suppose each record is a dictionary, and you want to sort records by their `amount` field.

```python
transactions = [
    {"id": 101, "amount": 500},
    {"id": 102, "amount": 200},
    {"id": 103, "amount": 800},
]

transactions.sort(key=lambda record: record["amount"])

print(transactions)
```

Output:

```text
[
    {'id': 102, 'amount': 200},
    {'id': 101, 'amount': 500},
    {'id': 103, 'amount': 800}
]
```

**Explanation:** The `key` function extracts each dictionary's `amount`. Python sorts the dictionaries using those extracted numbers.

To sort the same records from highest amount to lowest amount:

```python
transactions.sort(key=lambda record: record["amount"], reverse=True)
```

### Example 6: Important — `sort()` returns `None`

```python
numbers = [3, 1, 2]

result = numbers.sort()

print(numbers)
print(result)
```

Output:

```text
[1, 2, 3]
None
```

**Common mistake:**

```python
numbers = [3, 1, 2]
numbers = numbers.sort()  # Wrong if you expect numbers to remain the sorted list

print(numbers)
```

Output:

```text
None
```

The list was sorted, but the assignment replaced the variable with the method's return value (`None`).

**Correct approach:**

```python
numbers = [3, 1, 2]
numbers.sort()

print(numbers)
```

### Example 7: Use `sorted()` when you need a new sorted list

```python
original_numbers = [3, 1, 2]
sorted_numbers = sorted(original_numbers)

print("Original:", original_numbers)
print("Sorted:", sorted_numbers)
```

Output:

```text
Original: [3, 1, 2]
Sorted: [1, 2, 3]
```

`sorted()` creates and returns a new sorted list; it does not mutate the original list.

### Important limitation

The values being compared must be mutually orderable. For example, sorting a list containing both integers and strings with the default ordering raises `TypeError` in Python 3.

### Key points

- `sort()` sorts the existing list.
- Default is ascending order (`reverse=False`).
- `reverse=True` gives descending order.
- `key` can define the field or rule used for sorting.
- Mutates the original list and returns `None`.
- Use `sorted()` when you need a separate sorted list.

---

## 13. `copy()` — Create a shallow copy of a list

### Purpose

`copy()` creates a **new list object** containing the same element references as the original list. It does not change the original list.

This is called a **shallow copy**.

### Syntax

```python
new_list = original_list.copy()
```

### Example 1: Copy a list of immutable values

```python
original_numbers = [10, 20, 30]
copied_numbers = original_numbers.copy()

copied_numbers.append(40)

print("Original:", original_numbers)
print("Copy:", copied_numbers)
```

Output:

```text
Original: [10, 20, 30]
Copy: [10, 20, 30, 40]
```

**Explanation:** The outer lists are separate objects. Appending to the copy does not append to the original.

### Example 2: Confirm that the lists are different objects

```python
original = ["A", "B", "C"]
copied = original.copy()

print(original == copied)
print(original is copied)
```

Output:

```text
True
False
```

- `==` checks whether the lists have equal contents.
- `is` checks whether both variables refer to the exact same object.

The contents are initially equal, but the list objects are different.

### Example 3: The shallow-copy behavior with nested lists

```python
original = [[1, 2], [3, 4]]
copied = original.copy()

copied.append([5, 6])
copied[0].append(99)

print("Original:", original)
print("Copy:", copied)
```

Output:

```text
Original: [[1, 2, 99], [3, 4]]
Copy: [[1, 2, 99], [3, 4], [5, 6]]
```

**Why did the original change?**

1. `original.copy()` created a new outer list.
2. The nested lists inside it were not copied; both outer lists refer to the same nested list objects.
3. `copied.append([5, 6])` added a new nested list only to `copied`.
4. `copied[0].append(99)` changed a nested list shared by both outer lists. Therefore, the change is visible through `original` too.

This distinction is important when lists contain dictionaries, lists, or other mutable objects.

### Example 4: Make a deep copy when nested objects must be independent

When you need to copy nested mutable objects as well, use `deepcopy()` from Python's `copy` module.

```python
from copy import deepcopy

original = [[1, 2], [3, 4]]
deep_copied = deepcopy(original)

deep_copied[0].append(99)

print("Original:", original)
print("Deep copy:", deep_copied)
```

Output:

```text
Original: [[1, 2], [3, 4]]
Deep copy: [[1, 2, 99], [3, 4]]
```

`deepcopy()` recursively copies nested objects in common cases. It can be more expensive and may have special behavior for some object types, so use it when independent nested state is actually required.

### Data-engineering use case

Suppose a pipeline receives a batch of records and one processing step needs its own list to add or remove records without changing the caller's outer list.

```python
source_batch = [
    {"id": 1, "status": "valid"},
    {"id": 2, "status": "invalid"},
]

working_batch = source_batch.copy()
working_batch.append({"id": 3, "status": "valid"})

print("Source batch size:", len(source_batch))
print("Working batch size:", len(working_batch))
```

Output:

```text
Source batch size: 2
Working batch size: 3
```

**Caution:** The dictionaries inside `source_batch` and `working_batch` are shared. Updating a dictionary in `working_batch` also affects the same dictionary visible through `source_batch`. Use `deepcopy()` or construct new dictionaries when independent record objects are required.

### Key points

- Creates a new outer list.
- Does not mutate the original list.
- Is a shallow copy: nested mutable objects remain shared.
- Use `deepcopy()` when nested mutable objects also need independent copies.

---

## 14. Inspecting list methods with `dir(list)`

Python provides the built-in `dir()` function to inspect the attributes and methods available on an object or type.

### Example 1: Display all names provided by the list type

```python
print(dir(list))
```

This displays public names as well as special (dunder) methods such as `__add__`, `__contains__`, and `__len__`.

### Example 2: Display names that do not start with double underscores

```python
list_methods = [name for name in dir(list) if not name.startswith("__")]

print(list_methods)
```

Typical output:

```text
['append', 'clear', 'copy', 'count', 'extend', 'index', 'insert', 'pop', 'remove', 'reverse', 'sort']
```

The order shown by `dir()` is alphabetical. These are the 11 non-dunder list methods covered in this lesson.

### Example 3: Inspect the documentation for a specific method

```python
help(list.append)
help(list.sort)
```

You can also inspect an individual list instance:

```python
records = ["a", "b"]
print(dir(records))
```

### What are dunder methods?

Dunder means **double underscore**. Names such as `__len__` and `__getitem__` are special methods Python uses to implement language operations. For example:

```python
records = ["a", "b", "c"]

print(len(records))       # Uses the list's length behavior
print(records[0])        # Uses the list's item-access behavior
print("b" in records)    # Uses the list's membership behavior
```

You do not need to call most dunder methods directly in ordinary application code. Prefer the normal Python syntax and built-in functions.

---

## 15. Summary: all 11 methods at a glance

| Method | Main purpose | Mutates original list? | Return value / behavior |
|---|---|---:|---|
| `append(item)` | Add one item at the end | Yes | `None` |
| `extend(iterable)` | Add each element from an iterable | Yes | `None` |
| `insert(index, item)` | Insert one item at a position | Yes | `None` |
| `remove(value)` | Remove the first matching value | Yes | `None`; `ValueError` if absent |
| `pop(index=-1)` | Remove an item by index | Yes | The removed item; `IndexError` for an invalid index |
| `clear()` | Remove all items | Yes | `None` |
| `index(value)` | Find the first matching position | No | Index; `ValueError` if absent |
| `count(value)` | Count matching values | No | Number of occurrences |
| `reverse()` | Reverse the current order | Yes | `None` |
| `sort(reverse=True)` | Sort in place; descending when `reverse=True` | Yes | `None` |
| `copy()` | Create a shallow copy | No | A new outer list |

> **Correction to remember:** `sort(reverse=True)` is a valid call, but the method's default is `reverse=False`. The full signature also supports `key`, as shown earlier.

---

## 16. Common mistakes and how to avoid them

### Mistake 1: Expecting `append()` to unpack a list

```python
numbers = [1, 2]
numbers.append([3, 4])
print(numbers)
```

Output: `[1, 2, [3, 4]]`

Use `extend()` when you want `[1, 2, 3, 4]`.

### Mistake 2: Assigning the result of a mutating method

```python
numbers = [3, 1, 2]
numbers = numbers.sort()
```

Now `numbers` is `None`, because `sort()` mutates the list and returns `None`. Call `numbers.sort()` on its own line.

The same return-value rule applies to `append()`, `extend()`, `insert()`, `remove()`, `clear()`, and `reverse()`.

### Mistake 3: Confusing `remove()` and `pop()`

```python
numbers = [10, 20, 30]
numbers.remove(20)  # Remove by value

removed = numbers.pop(0)  # Remove by index and return the item
```

`remove(20)` looks for the value `20`. `pop(0)` removes the element at index `0` and returns it.

### Mistake 4: Assuming `copy()` duplicates nested records

`copy()` creates a new outer list, not independent copies of nested dictionaries or lists. Be explicit about whether nested objects may be shared.

### Mistake 5: Assuming `reverse()` sorts values

`reverse()` flips the current order. `sort()` arranges values according to their ordering rules.

### Mistake 6: Ignoring exceptions

- `remove(value)` and `index(value)` raise `ValueError` if the value is not found.
- `pop(index)` raises `IndexError` if the list is empty or the index is invalid.

Validate the input or handle the expected exception when absence is normal in your application.

---

## 17. Performance: approximate time complexity

Let `n` be the number of elements in the list, and let `k` be the number of elements added by `extend()`.

| Method | Typical time complexity | Why it matters |
|---|---:|---|
| `append(item)` | Amortized `O(1)` | Usually adds at the end without shifting existing elements. |
| `extend(iterable)` | `O(k)` amortized | Work grows with the number of incoming elements. |
| `insert(index, item)` | `O(n)` | Elements may need to shift to make room. |
| `remove(value)` | `O(n)` | May scan for a match and shift later elements. |
| `pop()` at end | `O(1)` | Removes the final element. |
| `pop(index)` away from end | `O(n)` | Later elements may need to shift. |
| `clear()` | `O(n)` | References to the existing elements must be released. |
| `index(value)` | `O(n)` | May inspect every element. |
| `count(value)` | `O(n)` | Checks every element. |
| `reverse()` | `O(n)` | Swaps elements across the list. |
| `sort()` | `O(n log n)` worst case | Python uses an adaptive sorting algorithm; already ordered data can be faster. |
| `copy()` | `O(n)` | Copies the outer list's element references. |

These are practical high-level complexity estimates, not timing guarantees. Actual runtime depends on list size, data, and the operation's position.

---

## 18. Production perspective: lists in data-engineering applications

Lists commonly represent in-memory collections such as:

- A batch of documents waiting to be parsed.
- A group of conversation messages sent to a model.
- A sequence of tool calls produced by an agent.
- Search results returned by a retrieval component.
- Records collected from an API before writing to a destination.

Consider this simplified batch-processing example:

```python
# Records collected from two API pages
page_1_records = [
    {"id": 1, "status": "valid"},
    {"id": 2, "status": "invalid"},
]

page_2_records = [
    {"id": 3, "status": "valid"},
    {"id": 4, "status": "valid"},
]

# Combine both pages into one batch
all_records = page_1_records.copy()
all_records.extend(page_2_records)

# Count statuses in this small in-memory batch
statuses = [record["status"] for record in all_records]
valid_count = statuses.count("valid")

# Sort records by ID for predictable presentation
all_records.sort(key=lambda record: record["id"])

print("Records:", all_records)
print("Valid records:", valid_count)
```

Output:

```text
Records: [{'id': 1, 'status': 'valid'}, {'id': 2, 'status': 'invalid'}, {'id': 3, 'status': 'valid'}, {'id': 4, 'status': 'valid'}]
Valid records: 3
```

This example demonstrates a few methods together:

1. `copy()` creates a separate outer list from page 1.
2. `extend()` adds the records from page 2 individually.
3. `count()` counts the `"valid"` status values.
4. `sort()` orders the list by each record's `id`.

### Shared-mutation risk in application state

Suppose two components refer to the same messages list:

```python
messages = [
    {"role": "user", "content": "Summarize this document."}
]

messages_for_logging = messages
messages_for_model = messages

messages_for_logging.clear()

print(messages_for_model)
```

Output:

```text
[]
```

Both variables point to the same list. Clearing it for logging also cleared the model's messages. This kind of accidental shared mutation can cause missing conversation history, lost tool-call records, or corrupted processing state.

A separate outer list can prevent operations such as `append()`, `remove()`, or `clear()` on one list from changing the other list's membership:

```python
messages = [
    {"role": "user", "content": "Summarize this document."}
]

messages_for_logging = messages.copy()
messages_for_model = messages.copy()

messages_for_logging.clear()

print("Logging list:", messages_for_logging)
print("Model list:", messages_for_model)
```

Output:

```text
Logging list: []
Model list: [{'role': 'user', 'content': 'Summarize this document.'}]
```

However, both copied lists still refer to the same dictionary inside them. If you mutate that dictionary, the change is visible through both lists. Use `deepcopy()` or create independent record dictionaries when that is the required behavior.

**Engineering rule:** Before mutating a list, know whether it is owned by your function or shared with another part of the application. Copy deliberately when you need an independent collection, and choose shallow versus deep copying based on the nested objects.

---

## 19. Practice exercises

Try these exercises without looking at the solutions first. Use `print()` to inspect your results.

### Exercise 1 — `append()`

Start with:

```python
files = ["sales.csv", "customers.csv"]
```

Append `"orders.csv"` and print the updated list.

### Exercise 2 — `extend()`

Start with:

```python
batch_1 = [101, 102]
batch_2 = [103, 104]
```

Extend `batch_1` with `batch_2`. Print the result and confirm that the result has four elements.

### Exercise 3 — `insert()`

Start with:

```python
steps = ["extract", "load"]
```

Insert `"transform"` at index `1`.

### Exercise 4 — `remove()`

Start with:

```python
statuses = ["valid", "invalid", "valid", "pending"]
```

Remove the first `"valid"`. Print the list and confirm that one `"valid"` remains.

### Exercise 5 — `pop()`

Start with:

```python
jobs = ["job_1", "job_2", "job_3"]
```

Remove the last job using `pop()`. Store and print the returned job, then print the remaining list.

### Exercise 6 — `clear()`

Start with:

```python
temporary_results = [10, 20, 30]
```

Clear the list and print it.

### Exercise 7 — `index()`

Start with:

```python
columns = ["id", "name", "email", "status"]
```

Find and print the index of `"status"`.

### Exercise 8 — `count()`

Start with:

```python
codes = [200, 404, 200, 500, 404, 200]
```

Count and print how many times `200` appears.

### Exercise 9 — `reverse()`

Start with:

```python
priorities = ["low", "medium", "high"]
```

Reverse the list in place and print it.

### Exercise 10 — `sort()`

Start with:

```python
latencies = [120, 45, 300, 80, 60]
```

Sort the list from highest to lowest and print it.

### Exercise 11 — `copy()`

Start with:

```python
source_records = [1, 2, 3]
```

Make a copy, append `4` to the copy, and print both lists. Confirm that the original still has three elements.

### Exercise 12 — Combined data-engineering exercise

You receive two pages of document IDs:

```python
page_1 = ["doc_001", "doc_002"]
page_2 = ["doc_003", "doc_004"]
```

Create a working list from `page_1`, add the IDs from `page_2`, insert `"doc_000"` at the beginning, count how many IDs contain the string `"doc"` (you may use a loop to build a count), and sort the final list. Print the final list and the count.

---

## 20. Exercise solutions

### Solution 1

```python
files = ["sales.csv", "customers.csv"]
files.append("orders.csv")
print(files)
```

### Solution 2

```python
batch_1 = [101, 102]
batch_2 = [103, 104]
batch_1.extend(batch_2)
print(batch_1)
print(len(batch_1))
```

### Solution 3

```python
steps = ["extract", "load"]
steps.insert(1, "transform")
print(steps)
```

### Solution 4

```python
statuses = ["valid", "invalid", "valid", "pending"]
statuses.remove("valid")
print(statuses)
```

### Solution 5

```python
jobs = ["job_1", "job_2", "job_3"]
removed_job = jobs.pop()
print("Removed:", removed_job)
print("Remaining:", jobs)
```

### Solution 6

```python
temporary_results = [10, 20, 30]
temporary_results.clear()
print(temporary_results)
```

### Solution 7

```python
columns = ["id", "name", "email", "status"]
print(columns.index("status"))
```

### Solution 8

```python
codes = [200, 404, 200, 500, 404, 200]
print(codes.count(200))
```

### Solution 9

```python
priorities = ["low", "medium", "high"]
priorities.reverse()
print(priorities)
```

### Solution 10

```python
latencies = [120, 45, 300, 80, 60]
latencies.sort(reverse=True)
print(latencies)
```

### Solution 11

```python
source_records = [1, 2, 3]
working_records = source_records.copy()
working_records.append(4)

print("Original:", source_records)
print("Copy:", working_records)
```

### Solution 12

```python
page_1 = ["doc_001", "doc_002"]
page_2 = ["doc_003", "doc_004"]

working_documents = page_1.copy()
working_documents.extend(page_2)
working_documents.insert(0, "doc_000")

document_count = 0
for document_id in working_documents:
    if "doc" in document_id:
        document_count += 1

working_documents.sort()

print("Documents:", working_documents)
print("Document count:", document_count)
```

Expected output:

```text
Documents: ['doc_000', 'doc_001', 'doc_002', 'doc_003', 'doc_004']
Document count: 5
```

---

## 21. Final review checklist

You should now be able to explain and demonstrate all of the following:

- [ ] `append()` adds one object to the end of a list.
- [ ] `extend()` adds each element from an iterable.
- [ ] `insert()` adds one object at a specified position.
- [ ] `remove()` removes the first matching value.
- [ ] `pop()` removes and returns an item by index, using the last item by default.
- [ ] `clear()` empties the existing list object.
- [ ] `index()` returns the first matching position.
- [ ] `count()` returns the number of occurrences.
- [ ] `reverse()` reverses the current order in place.
- [ ] `sort()` sorts in place; `reverse=True` means descending order.
- [ ] `copy()` creates a shallow copy, so nested mutable objects can still be shared.
- [ ] `dir(list)` and `help()` help you inspect available methods and their documentation.
- [ ] You can distinguish a method that mutates a list from the value that method returns.
- [ ] You understand how shared references can cause accidental mutation in application state.

**Core engineering principle:** A Python list is mutable state. Know who owns it, who else can reference it, whether the operation changes it, and what the method returns. This discipline becomes essential when lists hold document batches, messages, tool calls, and search results in production data and AI applications.
