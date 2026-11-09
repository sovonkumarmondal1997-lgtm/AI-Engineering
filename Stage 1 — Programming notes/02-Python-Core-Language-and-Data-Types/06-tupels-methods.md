# 06 — Tuple Methods and Built-in Operations

> **Purpose:** Learn every public method available on Python tuples and understand how to use the built-in functions and iteration tools commonly used with tuples. The examples progress from basic operations to practical data-engineering-style records.
>
> **Prerequisites:** Basic Python variables, strings, numbers, lists, `for` loops, functions, and `try`/`except`.

---

## 1. What is a tuple?

A **tuple** is an ordered collection of Python objects. It is commonly used when a group of values should remain in a fixed order and the tuple itself should not be structurally changed after creation.

```python
point = (12, 7)
print(point)
print(type(point))
```

**Output:**

```text
(12, 7)
<class 'tuple'>
```

The tuple contains two values:

- `point[0]` is `12`.
- `point[1]` is `7`.

Tuples support indexing, slicing, iteration, unpacking, and many operations from Python's built-in functions. Unlike lists, tuples do not provide methods such as `append()`, `extend()`, `insert()`, `remove()`, or `sort()` because the tuple's sequence of references cannot be modified in place.

### 1.1 Creating tuples correctly

```python
empty_tuple = ()
one_item_tuple = (42,)
coordinates = (12, 7)
colors = "red", "green", "blue"

print(empty_tuple, type(empty_tuple))
print(one_item_tuple, type(one_item_tuple))
print(coordinates, type(coordinates))
print(colors, type(colors))
```

**Output:**

```text
() <class 'tuple'>
(42,) <class 'tuple'>
(12, 7) <class 'tuple'>
('red', 'green', 'blue') <class 'tuple'>
```

**Important:** The comma creates a one-item tuple, not the parentheses. `(42)` is the integer `42`; `(42,)` is a tuple containing one item.

```python
not_a_tuple = (42)
one_item_tuple = (42,)

print(type(not_a_tuple))   # <class 'int'>
print(type(one_item_tuple))  # <class 'tuple'>
```

---

## 2. The actual public tuple methods

Python tuples have **two public, non-dunder methods**:

1. `count(value)` — count how many times a value occurs.
2. `index(value, start, stop)` — find the index of the first matching value in a selected range.

Neither method mutates the tuple. Both return an integer. `index()` raises `ValueError` if the value is not found; `count()` simply returns `0` when there are no matches.

### 2.1 `count(value)` — count occurrences

**Purpose:** Return the number of times a specified value appears in the tuple.

**Syntax:**

```python
tuple_name.count(value)
```

**Example 1 — Count repeated numbers**

```python
numbers = (10, 20, 10, 30, 10, 40)

result = numbers.count(10)

print(result)
print(numbers)
```

**Output:**

```text
3
(10, 20, 10, 30, 10, 40)
```

**Explanation:**

1. `numbers` refers to a tuple containing six integers.
2. `numbers.count(10)` scans the tuple and counts values equal to `10`.
3. The value `10` occurs at indices `0`, `2`, and `4`.
4. The method returns the integer `3`.
5. The original tuple remains unchanged.

**Example 2 — Count strings**

```python
departments = ("Sales", "IT", "Finance", "IT", "HR", "IT")

it_count = departments.count("IT")
print(f"IT department appears {it_count} times.")
```

**Output:**

```text
IT department appears 3 times.
```

**Example 3 — Value not present**

```python
statuses = ("success", "failed", "success")

print(statuses.count("pending"))
```

**Output:**

```text
0
```

**Key points:**

- `count()` does not change the tuple.
- It returns an integer.
- It does not raise `ValueError` when the value is absent.
- It compares values using equality (`==`).
- Time complexity is **O(n)** because it may inspect every item.

**Practical use:** Count how many records in a fixed batch have a particular status, category, or label. For large or frequently changing data, a dictionary or `collections.Counter` may be more suitable for repeated frequency lookups.

### 2.2 `index(value, start, stop)` — find the first matching position

**Purpose:** Return the zero-based index of the first occurrence of a value.

**Syntax:**

```python
tuple_name.index(value)
tuple_name.index(value, start)
tuple_name.index(value, start, stop)
```

`start` and `stop` are optional search boundaries. The search includes `start` and excludes `stop`, just like slicing.

**Example 1 — Find a value's index**

```python
languages = ("Python", "Java", "SQL", "Python", "Go")

position = languages.index("SQL")
print(position)
```

**Output:**

```text
2
```

**Explanation:**

1. Tuple indexing starts at `0`.
2. `"Python"` is at index `0`.
3. `"Java"` is at index `1`.
4. `"SQL"` is at index `2`.
5. `index("SQL")` returns `2`, the first matching position.

**Example 2 — Duplicate values return the first match**

```python
numbers = (5, 8, 3, 8, 10)

print(numbers.index(8))
```

**Output:**

```text
1
```

The value `8` occurs at indices `1` and `3`. `index()` returns the first occurrence, which is index `1`.

**Example 3 — Search from a starting position**

```python
numbers = (5, 8, 3, 8, 10)

print(numbers.index(8, 2))
```

**Output:**

```text
3
```

The search begins at index `2`, so the `8` at index `1` is ignored. The next matching `8` is at index `3`.

**Example 4 — Search within a start/stop range**

```python
numbers = (5, 8, 3, 8, 10)

print(numbers.index(8, 2, 4))
```

**Output:**

```text
3
```

The search range is indices `2` and `3`; the stop index `4` is excluded. The matching value is found at index `3`.

**Example 5 — Handle a value that does not exist**

```python
numbers = (10, 20, 30)

try:
    position = numbers.index(99)
    print(position)
except ValueError:
    print("The value was not found in the tuple.")
```

**Output:**

```text
The value was not found in the tuple.
```

**Why is `try`/`except` useful here?** `index()` raises a `ValueError` when it cannot find the requested value. Catching that specific exception allows the program to handle the missing value without terminating unexpectedly.

**Key points:**

- `index()` returns an integer position, not the value itself.
- It returns the first match in the specified search range.
- It does not mutate the tuple.
- It raises `ValueError` if no match exists in the range.
- Time complexity is **O(n)** in the worst case.

**Practical use:** Find the position of a field or status in a small, fixed tuple of column names or labels. For repeated lookups, a dictionary mapping names to positions is generally more efficient and clearer.

---

## 3. Inspecting tuple methods with `dir()` and `help()`

Python provides built-in inspection tools that let you discover what an object or type supports.

### 3.1 `dir(tuple)`

```python
print(dir(tuple))
```

This displays names available on the tuple type, including special methods such as `__len__` and `__getitem__`.

To display only the public names that are not surrounded by leading and trailing double underscores:

```python
public_names = [
    name
    for name in dir(tuple)
    if not name.startswith("_")
]

print(public_names)
```

**Output:**

```text
['count', 'index']
```

These are the two public tuple methods you need to learn.

### 3.2 `help(tuple)`

```python
help(tuple)
```

This displays Python's documentation for the tuple type, including its methods and supported behavior. The exact formatting depends on the Python version and environment.

You can also inspect one method directly:

```python
help(tuple.count)
help(tuple.index)
```

---

## 4. Built-in functions and iteration tools that work with tuples

The following are **not tuple methods**. They are Python built-ins or built-in types/functions that accept a tuple or work with its elements:

| Function/tool | Purpose | Result |
|---|---|---|
| `len()` | Count the number of items | Integer |
| `min()` | Find the smallest item | An item from the tuple |
| `max()` | Find the largest item | An item from the tuple |
| `sum()` | Add numeric items | Number |
| `sorted()` | Return items in sorted order | New list |
| `reversed()` | Provide items in reverse order | Reverse iterator |
| `enumerate()` | Pair each item with an index | Enumerate iterator |
| `tuple()` | Create/convert to a tuple | Tuple |

We will examine each one individually.

### 4.1 `len(tuple)` — get the number of items

**Purpose:** Return the total number of elements in a tuple.

**Syntax:**

```python
len(tuple_name)
```

**Example:**

```python
employees = ("Asha", "Rahul", "Priya", "Daniel")

number_of_employees = len(employees)
print(number_of_employees)
```

**Output:**

```text
4
```

**Explanation:**

1. `employees` contains four elements.
2. `len(employees)` returns the number of elements.
3. The result is stored in `number_of_employees`.
4. `print()` displays `4`.

**Example — Validate that a tuple is not empty**

```python
readings = (18.5, 22.0, 19.5)

if len(readings) > 0:
    print("Readings are available.")
else:
    print("No readings are available.")
```

**Output:**

```text
Readings are available.
```

**Key points:**

- `len()` returns an integer.
- It does not change the tuple.
- It also works with strings, lists, dictionaries, and other supported collections.
- For a tuple, retrieving its length is **O(1)**.

### 4.2 `min(tuple)` — find the smallest item

**Purpose:** Return the smallest item according to Python's comparison rules.

**Syntax:**

```python
min(tuple_name)
```

**Example — Find the minimum score**

```python
scores = (72, 95, 68, 88, 91)

lowest_score = min(scores)
print(lowest_score)
```

**Output:**

```text
68
```

**Explanation:** Python compares the values and returns the smallest one, `68`. The tuple is not changed.

**Example — Find the earliest/lowest temperature reading**

```python
temperatures = (18.5, 22.0, 19.5, 25.0, 20.5)

print(min(temperatures))
```

**Output:**

```text
18.5
```

**Important:** `min()` requires comparable values. A tuple containing incompatible values such as an integer and a string may raise `TypeError` when Python cannot compare them. Calling `min()` on an empty tuple raises `ValueError`.

```python
empty_values = ()

try:
    print(min(empty_values))
except ValueError:
    print("Cannot find a minimum in an empty tuple.")
```

**Output:**

```text
Cannot find a minimum in an empty tuple.
```

**Key points:**

- Returns the smallest item; it does not return its index.
- Does not mutate the tuple.
- Time complexity is **O(n)**.
- An empty tuple causes `ValueError`.

### 4.3 `max(tuple)` — find the largest item

**Purpose:** Return the largest item according to Python's comparison rules.

**Syntax:**

```python
max(tuple_name)
```

**Example:**

```python
scores = (72, 95, 68, 88, 91)

highest_score = max(scores)
print(highest_score)
```

**Output:**

```text
95
```

**Explanation:** Python compares all the scores and returns the largest value, `95`. The original tuple remains unchanged.

**Example — Largest temperature reading**

```python
temperatures = (18.5, 22.0, 19.5, 25.0, 20.5)

print(max(temperatures))
```

**Output:**

```text
25.0
```

**Important:** Like `min()`, `max()` raises `ValueError` for an empty tuple and may raise `TypeError` if the values cannot be compared with one another.

**Key points:**

- Returns the largest item, not its index.
- Does not mutate the tuple.
- Time complexity is **O(n)**.

### 4.4 `sum(tuple)` — calculate the total

**Purpose:** Add the numeric values in an iterable and return their total.

**Syntax:**

```python
sum(tuple_name)
sum(tuple_name, start)
```

`start` is optional and defaults to `0`. It is added to the total.

**Example 1 — Add all scores**

```python
scores = (72, 95, 68, 88, 91)

total_score = sum(scores)
print(total_score)
```

**Output:**

```text
414
```

**Explanation:** Python adds `72 + 95 + 68 + 88 + 91` and returns `414`. The tuple remains unchanged.

**Example 2 — Use the optional starting value**

```python
numbers = (10, 20, 30)

print(sum(numbers, 100))
```

**Output:**

```text
160
```

The result is `100 + 10 + 20 + 30`, which equals `160`.

**Example 3 — Calculate an average using `sum()` and `len()`**

```python
scores = (72, 95, 68, 88, 91)

average = sum(scores) / len(scores)
print(average)
```

**Output:**

```text
82.8
```

**Important:** `sum()` is intended for numeric addition. It is not a general-purpose way to concatenate strings. An empty tuple produces `0` with the default starting value.

**Key points:**

- Returns the sum of the values plus the optional starting value.
- Does not mutate the tuple.
- Time complexity is **O(n)**.
- Use numeric values for ordinary summation.

### 4.5 `sorted(tuple)` — return a sorted list

**Purpose:** Return a new list containing the tuple's elements in sorted order.

**Syntax:**

```python
sorted(tuple_name)
sorted(tuple_name, reverse=True)
```

By default, `sorted()` sorts in ascending order. Setting `reverse=True` sorts in descending order.

**Example 1 — Ascending order**

```python
scores = (72, 95, 68, 88, 91)

sorted_scores = sorted(scores)

print(sorted_scores)
print(type(sorted_scores))
print(scores)
```

**Output:**

```text
[68, 72, 88, 91, 95]
<class 'list'>
(72, 95, 68, 88, 91)
```

**Explanation:**

1. The original variable `scores` refers to a tuple.
2. `sorted(scores)` reads its elements and sorts them.
3. It creates and returns a **new list**.
4. `sorted_scores` refers to that list.
5. The original tuple is unchanged.

**Example 2 — Descending order**

```python
scores = (72, 95, 68, 88, 91)

print(sorted(scores, reverse=True))
```

**Output:**

```text
[95, 91, 88, 72, 68]
```

**Example 3 — Convert the sorted result back to a tuple**

```python
scores = (72, 95, 68, 88, 91)

ascending_tuple = tuple(sorted(scores))
descending_tuple = tuple(sorted(scores, reverse=True))

print(ascending_tuple)
print(type(ascending_tuple))
print(descending_tuple)
```

**Output:**

```text
(68, 72, 88, 91, 95)
<class 'tuple'>
(95, 91, 88, 72, 68)
```

**Important distinction:** `sorted()` always returns a list. Use `tuple(sorted(...))` when the result must be a tuple.

**Key points:**

- `sorted()` does not mutate the original tuple.
- Its result is a list, not a tuple.
- `reverse=True` means descending order.
- Typical time complexity is **O(n log n)**.
- Values must be mutually comparable for the requested ordering.

### 4.6 `reversed(tuple)` — iterate in reverse order

**Purpose:** Return an iterator that yields the tuple's elements from last to first.

**Syntax:**

```python
reversed(tuple_name)
```

`reversed()` does not directly return a list or tuple. It returns a reverse iterator.

**Example 1 — Convert the reverse iterator into a list**

```python
numbers = (10, 20, 30, 40)

reverse_iterator = reversed(numbers)
reverse_list = list(reverse_iterator)

print(reverse_list)
print(numbers)
```

**Output:**

```text
[40, 30, 20, 10]
(10, 20, 30, 40)
```

**Explanation:**

1. `reversed(numbers)` creates an iterator over the tuple in reverse order.
2. `list(...)` consumes that iterator and stores the yielded values in a new list.
3. The original tuple stays unchanged.

**Example 2 — Iterate without creating a list**

```python
servers = ("server-01", "server-02", "server-03")

for server in reversed(servers):
    print(server)
```

**Output:**

```text
server-03
server-02
server-01
```

**Example 3 — Convert the result back to a tuple**

```python
numbers = (10, 20, 30, 40)

reverse_tuple = tuple(reversed(numbers))
print(reverse_tuple)
```

**Output:**

```text
(40, 30, 20, 10)
```

**Important distinctions:**

- `reversed(tuple)` returns a reverse iterator.
- `list(reversed(tuple))` returns a list.
- `tuple(reversed(tuple))` returns a tuple.
- The iterator is consumed as you iterate over it; it is not a reusable list.
- The original tuple is not modified.

**Key points:**

- Use `reversed()` when you want to process values from last to first.
- Use a `for` loop to consume values one at a time.
- Converting to a list or tuple materializes the values in a new collection.

### 4.7 `enumerate(tuple)` — access each item with its index

**Purpose:** Return an iterator that produces pairs containing an index and the corresponding item.

**Syntax:**

```python
enumerate(tuple_name)
enumerate(tuple_name, start=0)
```

The default index starts at `0`. You can choose a different starting index using `start`.

**Example 1 — Iterate through tuple values with their positions**

```python
scores = (72, 95, 68, 88, 91)

for position, score in enumerate(scores):
    print(position, score)
```

**Output:**

```text
0 72
1 95
2 68
3 88
4 91
```

**Explanation:**

1. `enumerate(scores)` creates an iterator.
2. On each loop, it yields a pair: `(index, value)`.
3. `position` receives the index.
4. `score` receives the value.
5. The loop prints both values for every item.

**Example 2 — Start numbering from 1**

```python
employees = ("Asha", "Rahul", "Priya")

for employee_number, employee in enumerate(employees, start=1):
    print(employee_number, employee)
```

**Output:**

```text
1 Asha
2 Rahul
3 Priya
```

**Example 3 — Convert the enumerate iterator into a list**

```python
colors = ("red", "green", "blue")

indexed_colors = list(enumerate(colors))
print(indexed_colors)
```

**Output:**

```text
[(0, 'red'), (1, 'green'), (2, 'blue')]
```

Each pair produced by `enumerate()` is a tuple. The outer result here is a list because it was wrapped with `list()`.

**Key points:**

- `enumerate()` returns an iterator, not a list or tuple.
- Each yielded item is a two-item tuple: `(index, value)`.
- The optional `start` argument changes the starting index.
- It does not modify the original tuple.
- It is generally preferable to manually maintaining a counter when you need both an index and a value.

**Practical use:** Track row positions while validating a batch of records, identify the position of a rejected input, or label records while iterating through a fixed collection.

### 4.8 `tuple(iterable)` — create or convert to a tuple

**Purpose:** Create a tuple from an iterable, such as a list, string, range, or iterator.

**Syntax:**

```python
tuple()
tuple(iterable)
```

**Example 1 — Convert a list into a tuple**

```python
employee_list = ["Asha", "Rahul", "Priya"]
employee_tuple = tuple(employee_list)

print(employee_tuple)
print(type(employee_tuple))
```

**Output:**

```text
('Asha', 'Rahul', 'Priya')
<class 'tuple'>
```

**Example 2 — Convert a string into a tuple of characters**

```python
word = "DATA"
characters = tuple(word)

print(characters)
```

**Output:**

```text
('D', 'A', 'T', 'A')
```

**Example 3 — Convert an iterator into a tuple**

```python
numbers = (10, 20, 30)
reverse_iterator = reversed(numbers)
reverse_tuple = tuple(reverse_iterator)

print(reverse_tuple)
```

**Output:**

```text
(30, 20, 10)
```

**Important:** Converting an iterable to a tuple consumes its iterator if it is an iterator. The resulting tuple is a new tuple containing the yielded objects. This is a shallow conversion; it does not recursively clone nested objects.

---

## 5. The combined score example from the lesson

This example combines `len()`, `min()`, `max()`, `sum()`, `sorted()`, and `enumerate()`.

```python
scores = (72, 95, 68, 88, 91)

print(len(scores), min(scores), max(scores), sum(scores))
print(sorted(scores))

for position, score in enumerate(scores):
    print(position, score)
```

**Output:**

```text
5 68 95 414
[68, 72, 88, 91, 95]
0 72
1 95
2 68
3 88
4 91
```

**Line-by-line explanation:**

1. `scores = (72, 95, 68, 88, 91)` creates a tuple of five scores.
2. `len(scores)` returns `5`, because there are five values.
3. `min(scores)` returns `68`, the lowest score.
4. `max(scores)` returns `95`, the highest score.
5. `sum(scores)` returns `414`, the total of all scores.
6. `sorted(scores)` returns a new list in ascending order. It does not change `scores`.
7. `enumerate(scores)` provides each score together with its zero-based position.
8. The `for` loop unpacks each pair into `position` and `score` and prints them.

---

## 6. Practical lesson example 1 — Fixed point coordinates

A coordinate point is a good tuple use case because it represents a fixed pair of values: an x-coordinate and a y-coordinate.

```python
point = (12, 7)

print(f"Point coordinates: x = {point[0]}, y = {point[1]}")

try:
    point[0] = 99
except TypeError as error:
    print(f"Cannot modify the tuple: {error}")

print(point)
```

**Output:**

```text
Point coordinates: x = 12, y = 7
Cannot modify the tuple: 'tuple' object does not support item assignment
(12, 7)
```

**Line-by-line explanation:**

1. `point = (12, 7)` creates a tuple containing two integers.
2. `point[0]` accesses the first item, `12`.
3. `point[1]` accesses the second item, `7`.
4. The f-string inserts those values into the output text.
5. `point[0] = 99` attempts to replace the first item.
6. Python raises `TypeError` because tuple item assignment is not supported.
7. The `except TypeError` block catches that specific error and prints a message.
8. `print(point)` confirms the original tuple remains `(12, 7)`.

**Engineering lesson:** Tuples are useful for fixed records such as coordinates, database connection parameters, or a known pair of dimensions. Do not use a tuple when the sequence itself must be modified frequently.

---

## 7. Practical lesson example 2 — Temperature statistics function

A function can calculate multiple statistics and return them together as a tuple. The caller can then unpack the returned values into separate variables.

```python
def calculate_temperature_statistics(readings):
    if len(readings) == 0:
        raise ValueError("At least one temperature reading is required.")

    lowest = min(readings)
    highest = max(readings)
    average = sum(readings) / len(readings)

    return lowest, highest, average


temperatures = (18.5, 22.0, 19.5, 25.0, 20.5)

lowest, highest, average = calculate_temperature_statistics(temperatures)

print(f"Lowest: {lowest}")
print(f"Highest: {highest}")
print(f"Average: {average:.1f}")
```

**Output:**

```text
Lowest: 18.5
Highest: 25.0
Average: 21.1
```

**Line-by-line explanation:**

1. `def calculate_temperature_statistics(readings):` defines a function with one parameter.
2. `if len(readings) == 0:` checks whether the input contains any readings.
3. `raise ValueError(...)` rejects empty input with a meaningful error. Without this guard, `min()` and `max()` would fail on an empty collection, and the average calculation would divide by zero.
4. `lowest = min(readings)` finds the minimum reading.
5. `highest = max(readings)` finds the maximum reading.
6. `average = sum(readings) / len(readings)` calculates the arithmetic mean.
7. `return lowest, highest, average` returns the three values as a tuple. Parentheses are optional in this return expression; Python packs the comma-separated values into a tuple.
8. `temperatures` stores the five readings in a tuple.
9. `lowest, highest, average = ...` unpacks the returned three-item tuple into three variables.
10. The f-strings display the statistics. `:.1f` formats the average to one digit after the decimal point.

**Why return a tuple?** The function has one logical result containing three related values. Returning a tuple keeps those values together while allowing the caller to unpack them conveniently.

**What if the function returns the wrong number of values?** If the caller expects three values but the function returns two or four, Python raises `ValueError` during unpacking. The number of targets must match the number of returned items unless starred unpacking is used.

---

## 8. Practical lesson example 3 — Birth records and tuple unpacking

A tuple can represent one fixed record, while a list can hold multiple records. This pattern is common when processing rows returned by a database query or reading structured records.

```python
birth_records = [
    ("Ada Lovelace", 1815),
    ("Alan Turing", 1912),
    ("Grace Hopper", 1906),
    ("Charles Babbage", 1791),
]

for name, year in birth_records:
    if year < 1900:
        print(f"{name} was born before 1900.")
    else:
        print(f"{name} was born in 1900 or later.")
```

**Output:**

```text
Ada Lovelace was born before 1900.
Alan Turing was born in 1900 or later.
Grace Hopper was born in 1900 or later.
Charles Babbage was born before 1900.
```

**Line-by-line explanation:**

1. `birth_records` is a list containing four records.
2. Each record is a two-item tuple: `(name, year)`.
3. `for name, year in birth_records:` iterates over the list one record at a time.
4. Python unpacks the first tuple's two values into `name` and `year`.
5. `if year < 1900:` checks whether the year is earlier than 1900.
6. The `if` branch prints a message for a person born before 1900.
7. The `else` branch handles a year of 1900 or later.
8. The loop repeats for the remaining tuples.

**Engineering lesson:** A list of tuples is useful for a small, ordered collection of fixed-shape records. In production systems, use clear schemas or named structures such as dataclasses, `NamedTuple`, or validated models when field meaning, optional values, or schema evolution become more complex.

---

## 9. Tuple immutability: what can and cannot change?

A tuple is **immutable at the container level**. This means you cannot replace, add, or remove its elements after it has been created.

```python
values = (10, 20, 30)

# Each of these attempts would raise TypeError:
# values[0] = 99
# values.append(40)
# del values[1]
```

However, immutability does not automatically make every object stored inside a tuple immutable. A tuple can contain a mutable object, such as a list. The list can still be changed.

```python
record = ("batch-001", ["new", "validated"])

record[1].append("loaded")

print(record)
```

**Output:**

```text
('batch-001', ['new', 'validated', 'loaded'])
```

The tuple still points to the same list object, but the contents of that nested list have changed.

> **Important distinction:** A tuple prevents reassignment of its slots. It does not recursively freeze every object referenced by those slots.

### 9.1 Why this matters in data engineering

Suppose two parts of a pipeline share the same tuple containing a mutable list. One component may change that nested list, and the other component will see the change too. This is a shared-reference issue, not a failure of tuple immutability.

```python
shared_record = ("document-101", ["received"])

pipeline_a_record = shared_record
pipeline_b_record = shared_record

pipeline_a_record[1].append("processed")

print(pipeline_b_record)
```

**Output:**

```text
('document-101', ['received', 'processed'])
```

Both variables refer to the same tuple, and the tuple refers to the same nested list. A tuple does not make that nested list private or immutable.

For application state, prefer immutable nested values where appropriate, or make an intentional copy before handing mutable data to another component. A shallow copy only duplicates the outer container; it does not recursively copy nested objects.

---

## 10. Tuple packing and unpacking

### 10.1 Packing

**Packing** means placing multiple comma-separated values into one tuple.

```python
employee = "Sovon", "Data Engineer", 75000

print(employee)
print(type(employee))
```

**Output:**

```text
('Sovon', 'Data Engineer', 75000)
<class 'tuple'>
```

### 10.2 Unpacking

**Unpacking** means assigning tuple elements to individual variables.

```python
employee = ("Sovon", "Data Engineer", 75000)

name, role, salary = employee

print(name)
print(role)
print(salary)
```

**Output:**

```text
Sovon
Data Engineer
75000
```

The number of variables on the left must match the number of values in the tuple when ordinary unpacking is used.

```python
record = ("document-101", "processed", 3)

try:
    document_id, status = record
except ValueError as error:
    print(error)
```

**Output:**

```text
too many values to unpack (expected 2)
```

### 10.3 Starred unpacking with `*rest`

Starred unpacking captures zero or more remaining items in a **list**, not a tuple.

```python
record = ("document-101", "processed", 3, "warehouse")

document_id, *rest = record

print(document_id)
print(rest)
print(type(rest))
```

**Output:**

```text
document-101
['processed', 3, 'warehouse']
<class 'list'>
```

If you need a tuple after unpacking, convert it explicitly:

```python
record = ("document-101", "processed", 3, "warehouse")

document_id, *rest = record
rest_tuple = tuple(rest)

print(rest_tuple)
print(type(rest_tuple))
```

**Output:**

```text
('processed', 3, 'warehouse')
<class 'tuple'>
```

---

## 11. Common mistakes and how to avoid them

### Mistake 1 — Forgetting the comma in a single-item tuple

```python
wrong = (100)
correct = (100,)

print(type(wrong))
print(type(correct))
```

**Output:**

```text
<class 'int'>
<class 'tuple'>
```

**Correction:** Use the trailing comma: `(100,)`.

### Mistake 2 — Assuming every object inside a tuple is immutable

```python
items = ("files", ["a.csv", "b.csv"])
items[1].append("c.csv")
print(items)
```

**Output:**

```text
('files', ['a.csv', 'b.csv', 'c.csv'])
```

**Correction:** The tuple's slots cannot be reassigned, but a nested mutable object can still be modified.

### Mistake 3 — Trying to mutate a tuple

```python
numbers = (10, 20, 30)

try:
    numbers[0] = 99
except TypeError as error:
    print(error)
```

**Output:**

```text
'tuple' object does not support item assignment
```

**Correction:** Use a list if in-place changes are required. Alternatively, construct a new tuple with the desired values.

### Mistake 4 — Confusing `=` with `==`

```python
status = "success"       # Assignment: store a value.
print(status == "success")  # Comparison: check equality.
```

**Output:**

```text
True
```

**Correction:** Use `=` to assign a value and `==` to compare two values.

### Mistake 5 — Unpacking the wrong number of values

```python
record = ("doc-01", "loaded", 200)

try:
    document_id, status = record
except ValueError as error:
    print(error)
```

**Output:**

```text
too many values to unpack (expected 2)
```

**Correction:** Match the number of variables to the number of tuple elements, or use starred unpacking when the number of remaining elements can vary.

### Mistake 6 — Assuming `*rest` is a tuple

```python
first, *rest = (10, 20, 30)

print(rest)
print(type(rest))
```

**Output:**

```text
[20, 30]
<class 'list'>
```

**Correction:** Starred unpacking collects the remaining values in a list. Use `tuple(rest)` when a tuple is required.

### Mistake 7 — Assuming `sorted()` returns a tuple

```python
values = (3, 1, 2)
result = sorted(values)

print(result)
print(type(result))
```

**Output:**

```text
[1, 2, 3]
<class 'list'>
```

**Correction:** Use `tuple(sorted(values))` if you specifically need a tuple result.

### Mistake 8 — Assuming `reversed()` returns a list or tuple

```python
values = (1, 2, 3)
result = reversed(values)

print(type(result))
print(list(result))
```

**Output:**

```text
<class 'reversed'>
[3, 2, 1]
```

**Correction:** Convert it with `list()` or `tuple()` if you need a materialized collection.

### Mistake 9 — Calling `index()` without handling a missing value

```python
statuses = ("new", "loaded", "failed")

try:
    position = statuses.index("pending")
except ValueError:
    print("Status not found.")
```

**Output:**

```text
Status not found.
```

**Correction:** Handle `ValueError` when the requested value may not exist. You can also check membership with `in` before calling `index()`, though that means searching the tuple twice in the found case.

### Mistake 10 — Calling `min()`, `max()`, or calculating an average on empty data

```python
readings = ()

if readings:
    print(min(readings), max(readings), sum(readings) / len(readings))
else:
    print("No readings are available.")
```

**Output:**

```text
No readings are available.
```

**Correction:** Validate that data exists before calculating statistics. `min()` and `max()` raise `ValueError` on an empty tuple, and division by `len(readings)` would cause `ZeroDivisionError`.

### Mistake 11 — Converting types unnecessarily

```python
values = (10, 20, 30)

print(sum(values))       # Directly accepts a tuple.
print(max(values))       # Directly accepts a tuple.
print(len(values))       # Directly accepts a tuple.
```

**Correction:** Do not convert a tuple to a list merely to call functions that already accept tuples. Convert only when the next operation requires a different type or when you intentionally need a different data structure.

---

## 12. Quick reference — tuple methods versus built-ins

| Name | Category | Changes original tuple? | Return/result | Important behavior |
|---|---|---:|---|---|
| `count(value)` | Tuple method | No | `int` | Returns `0` if absent |
| `index(value)` | Tuple method | No | `int` | First match; `ValueError` if absent |
| `len(values)` | Built-in function | No | `int` | Number of items |
| `min(values)` | Built-in function | No | Item | `ValueError` on empty input |
| `max(values)` | Built-in function | No | Item | `ValueError` on empty input |
| `sum(values)` | Built-in function | No | Number | Numeric summation; empty input defaults to `0` |
| `sorted(values)` | Built-in function | No | `list` | New sorted list; `reverse=True` for descending |
| `reversed(values)` | Built-in function | No | Iterator | Yields items from last to first |
| `enumerate(values)` | Built-in function | No | Iterator | Yields `(index, item)` pairs |
| `tuple(values)` | Built-in type/constructor | No | `tuple` | Creates a tuple from an iterable |

### Complexity overview

For a tuple containing `n` elements:

| Operation | Typical time complexity | Reason |
|---|---:|---|
| `len(values)` | O(1) | Tuple length is stored by the object |
| `values.count(x)` | O(n) | May inspect all elements |
| `values.index(x)` | O(n) | May search all elements |
| `min(values)` | O(n) | Compares the elements |
| `max(values)` | O(n) | Compares the elements |
| `sum(values)` | O(n) | Adds the elements |
| `sorted(values)` | O(n log n) typical | Sorts the elements and creates a list |
| `reversed(values)` | O(1) to create iterator | Values are yielded during iteration |
| `enumerate(values)` | O(1) to create iterator | Pairs are generated during iteration |
| `tuple(iterable)` | O(n) | Materializes the iterable's items |

These are typical algorithmic costs. Actual runtime also depends on the objects being compared, added, or iterated over.

---

## 13. Data engineering applications

Tuples are useful in data engineering when values have a fixed structure or should be passed together without changing the outer record.

### 13.1 Represent a database row

```python
row = (101, "Asha", "asha@example.com", "active")

user_id, name, email, status = row

print(f"User ID: {user_id}")
print(f"Name: {name}")
print(f"Email: {email}")
print(f"Status: {status}")
```

A database driver may return rows in tuple-like form. Unpacking can make each field available to the next processing step. For records with many columns, named fields or row-mapping interfaces can improve readability.

### 13.2 Track a batch result

```python
batch_result = ("batch-2026-001", 500, 492, 8)

batch_id, total_records, successful_records, failed_records = batch_result

success_rate = successful_records / total_records * 100

print(f"Batch: {batch_id}")
print(f"Success rate: {success_rate:.2f}%")
```

**Output:**

```text
Batch: batch-2026-001
Success rate: 98.40%
```

This tuple represents a fixed set of batch metrics. In production, validate that `total_records` is greater than zero before calculating a rate.

### 13.3 Identify invalid records by position

```python
statuses = ("loaded", "loaded", "failed", "loaded", "failed")

for row_number, status in enumerate(statuses, start=1):
    if status == "failed":
        print(f"Row {row_number} needs investigation.")
```

**Output:**

```text
Row 3 needs investigation.
Row 5 needs investigation.
```

`enumerate()` provides row positions while the loop processes each status.

### 13.4 Return multiple pipeline metrics from a function

```python
def summarize_batch(total, successful, failed):
    if total < 0 or successful < 0 or failed < 0:
        raise ValueError("Counts cannot be negative.")

    if successful + failed != total:
        raise ValueError("Successful and failed counts must add up to total.")

    success_rate = (successful / total * 100) if total else 0.0
    return total, successful, failed, success_rate


metrics = summarize_batch(500, 492, 8)
print(metrics)
```

**Output:**

```text
(500, 492, 8, 98.4)
```

The function returns a single tuple containing four related metrics. The checks ensure the counts are non-negative and reconcile correctly.

---

## 14. Practice exercises

Try each exercise yourself before looking at the solutions.

### Exercise 1 — Count a value

Given:

```python
numbers = (2, 4, 2, 6, 2, 8, 4)
```

Use `count()` to find how many times `2` appears.

### Exercise 2 — Find the first index

Given:

```python
cities = ("Kolkata", "Delhi", "Mumbai", "Delhi")
```

Use `index()` to find the first position of `"Delhi"`.

### Exercise 3 — Search after a position

Using the same `cities` tuple, find the position of the second `"Delhi"` by providing a starting index.

### Exercise 4 — Calculate statistics

Given:

```python
sales = (1200, 1500, 900, 1800, 1600)
```

Print the number of values, minimum, maximum, and total sales.

### Exercise 5 — Calculate an average

Using `sales`, calculate and print the average sale amount.

### Exercise 6 — Sort in ascending and descending order

Use `sorted()` to produce both orders. Print the type of each result.

### Exercise 7 — Reverse a tuple

Use `reversed()` and `tuple()` to create a new tuple with the elements in reverse order.

### Exercise 8 — Enumerate a tuple

Given:

```python
files = ("customers.csv", "orders.csv", "products.csv")
```

Print each filename with a number starting from `1`.

### Exercise 9 — Unpack a database record

Given:

```python
record = (501, "Rahul", "active")
```

Unpack it into `user_id`, `name`, and `status`, then print each value.

### Exercise 10 — Handle an empty tuple

Write code that checks whether `readings = ()` is empty before calculating its average.

### Exercise 11 — Return multiple values

Write a function that accepts a tuple of numeric readings and returns its minimum, maximum, and average as a tuple. Handle an empty tuple safely.

### Exercise 12 — Discover tuple methods

Use `dir(tuple)` and a list comprehension to print only public names that do not start with an underscore.

---

## 15. Practice exercise solutions

### Solution 1

```python
numbers = (2, 4, 2, 6, 2, 8, 4)
print(numbers.count(2))
```

**Output:** `3`

### Solution 2

```python
cities = ("Kolkata", "Delhi", "Mumbai", "Delhi")
print(cities.index("Delhi"))
```

**Output:** `1`

### Solution 3

```python
cities = ("Kolkata", "Delhi", "Mumbai", "Delhi")
print(cities.index("Delhi", 2))
```

**Output:** `3`

### Solution 4

```python
sales = (1200, 1500, 900, 1800, 1600)

print("Count:", len(sales))
print("Minimum:", min(sales))
print("Maximum:", max(sales))
print("Total:", sum(sales))
```

**Output:**

```text
Count: 5
Minimum: 900
Maximum: 1800
Total: 7000
```

### Solution 5

```python
sales = (1200, 1500, 900, 1800, 1600)
average = sum(sales) / len(sales)
print(average)
```

**Output:** `1400.0`

### Solution 6

```python
sales = (1200, 1500, 900, 1800, 1600)

ascending = sorted(sales)
descending = sorted(sales, reverse=True)

print(ascending)
print(type(ascending))
print(descending)
print(type(descending))
```

**Output:**

```text
[900, 1200, 1500, 1600, 1800]
<class 'list'>
[1800, 1600, 1500, 1200, 900]
<class 'list'>
```

### Solution 7

```python
sales = (1200, 1500, 900, 1800, 1600)
reversed_sales = tuple(reversed(sales))
print(reversed_sales)
```

**Output:** `(1600, 1800, 900, 1500, 1200)`

### Solution 8

```python
files = ("customers.csv", "orders.csv", "products.csv")

for number, filename in enumerate(files, start=1):
    print(number, filename)
```

**Output:**

```text
1 customers.csv
2 orders.csv
3 products.csv
```

### Solution 9

```python
record = (501, "Rahul", "active")
user_id, name, status = record

print(user_id)
print(name)
print(status)
```

**Output:**

```text
501
Rahul
active
```

### Solution 10

```python
readings = ()

if readings:
    average = sum(readings) / len(readings)
    print(average)
else:
    print("Cannot calculate an average: no readings.")
```

**Output:**

```text
Cannot calculate an average: no readings.
```

### Solution 11

```python
def statistics(readings):
    if not readings:
        raise ValueError("The readings tuple cannot be empty.")

    return min(readings), max(readings), sum(readings) / len(readings)


values = (10, 20, 30, 40)
lowest, highest, average = statistics(values)

print(lowest, highest, average)
```

**Output:**

```text
10 40 25.0
```

### Solution 12

```python
public_names = [
    name
    for name in dir(tuple)
    if not name.startswith("_")
]

print(public_names)
```

**Output:**

```text
['count', 'index']
```

---

## 16. Final revision checklist

Before moving to the next Python topic, make sure you can explain and demonstrate each item without copying the examples:

- [ ] Create an empty tuple, a one-item tuple, and a multi-item tuple.
- [ ] Explain why `(5,)` is a tuple but `(5)` is an integer.
- [ ] Use `count()` to count repeated values.
- [ ] Use `index()` with and without `start` and `stop`.
- [ ] Handle `ValueError` when `index()` cannot find a value.
- [ ] Use `len()`, `min()`, `max()`, and `sum()` on numeric tuples.
- [ ] Explain why `sorted()` returns a list.
- [ ] Explain why `reversed()` returns an iterator.
- [ ] Use `enumerate()` to get an index and a value together.
- [ ] Convert an iterable to a tuple using `tuple()`.
- [ ] Explain tuple packing and unpacking.
- [ ] Explain why starred unpacking stores the remaining items in a list.
- [ ] Explain the difference between an immutable tuple and mutable objects nested inside it.
- [ ] Return multiple values from a function as a tuple and unpack them at the call site.
- [ ] Validate empty data before computing statistics.

## 17. The main engineering takeaway

A tuple is best understood as an **ordered, fixed-size container of object references**. Its two public methods, `count()` and `index()`, inspect values without changing the tuple. Built-ins such as `len()`, `min()`, `max()`, `sum()`, `sorted()`, `reversed()`, and `enumerate()` let you inspect, calculate, order, and iterate over tuple data without adding mutation methods to the tuple itself.

In data engineering, tuples are useful for fixed-shape records, coordinates, query rows, and returning a small group of related results. Remember that tuple immutability is shallow: if a tuple contains a list or another mutable object, that nested object may still change. This distinction matters when multiple pipeline components share references to the same data.
