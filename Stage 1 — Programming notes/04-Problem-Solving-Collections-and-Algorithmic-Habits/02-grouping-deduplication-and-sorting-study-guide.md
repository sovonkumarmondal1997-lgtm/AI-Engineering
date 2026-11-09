# Grouping, Deduplication, and Sorting — Complete Study Guide

**Source lesson:** `02-grouping-deduplication-and-sorting.md`  
**Roadmap location:** Stage 1 → `04-Problem-Solving-Collections-and-Algorithmic-Habits` → Lesson 02  
**Scope:** Source lesson concepts and examples, learning-level assessment, all 20 exercises, and the customer transaction mini-project.

---

# Part A — Complete lesson summary and teaching notes

## 1. What this chapter teaches

The previous lesson covered **search, count, filter, map, and aggregate** on a flat collection. This lesson adds three ways to organize data:

- **Grouping:** put records with the same key together.
- **Deduplication:** keep one item for each explicitly defined identity.
- **Sorting:** arrange items by a chosen order.

Example input:

```python
transactions = [
    {"customer": "A", "amount": 100},
    {"customer": "B", "amount": 250},
    {"customer": "A", "amount": 300},
    {"customer": "C", "amount": 150},
    {"customer": "B", "amount": 50},
]
```

Questions this data can answer include total spend per customer, unique customers, duplicate records, highest transaction amount, and transactions grouped by customer.

These patterns are used in database `GROUP BY` queries, ETL ingestion, reporting, log processing, APIs, and ML/AI data preparation. The chapter assumes Python 3.7+ because dictionary insertion order is guaranteed from Python 3.7 and it briefly demonstrates `dataclasses`.

## 2. Grouping: organize records by a key

Grouping transforms a flat collection into groups. For example:

```python
names = ["Alice", "Bob", "Alice", "Charlie", "Bob"]
```

Conceptually, Alice belongs with Alice, Bob with Bob, and Charlie forms a group of one.

For category records:

```python
records = [
    ("sales", 100),
    ("support", 200),
    ("sales", 150),
    ("support", 50),
]
```

The intended groups are `sales → [100, 150]` and `support → [200, 50]`.

Know these terms:

- **Group key:** decides the group (`"sales"` or `"support"`).
- **Group value:** the value stored (`amount`).
- **Group membership:** the rule that maps an item to a group (the tuple's first element).
- **Group container:** the overall dictionary.
- **Accumulator:** the list or other value that grows for each group.

### 2.1 Manual dictionary grouping

```python
groups = {}

for category, amount in records:
    if category not in groups:
        groups[category] = []
    groups[category].append(amount)

print(groups)
# {'sales': [100, 150], 'support': [200, 50]}
```

Line by line:

1. `groups = {}` creates an empty dictionary.
2. `for category, amount in records` loops over tuples and unpacks each into two variables.
3. `if category not in groups` checks whether that category key exists.
4. `groups[category] = []` creates its empty list the first time it appears.
5. `.append(amount)` adds the current amount to that category's list.

The state grows like this: `{}` → `{"sales": [100]}` → add support → append 150 to sales → append 50 to support. A dictionary is efficient because average key lookup/insertion is O(1). Searching a list of groups for the correct key on every record could make the full process O(n²), rather than O(n).

### 2.2 `setdefault()`

```python
groups = {}
for category, amount in records:
    groups.setdefault(category, []).append(amount)
```

`dict.setdefault(key, default)` returns the existing value if the key exists; otherwise it inserts `default` and returns that new value. Therefore `.append()` can be chained. It is shorter than the explicit `if`, but the explicit version is often easier for beginners to read. Both have the same result.

### 2.3 `defaultdict`

```python
from collections import defaultdict

groups = defaultdict(list)
for category, amount in records:
    groups[category].append(amount)

print(dict(groups))
# {'sales': [100, 150], 'support': [200, 50]}
```

`defaultdict(list)` uses `list` as a **default factory**. When a missing key is accessed with `groups[key]`, Python calls `list()` to create `[]`, stores it, and returns it. Thus no explicit initialization is needed. A plain dictionary raises `KeyError` for `plain["missing"]`; a `defaultdict(list)` creates and returns `[]`.

The factory controls the accumulator:

| Factory | Initial value | Purpose |
|---|---|---|
| `list` | `[]` | collect all values |
| `int` | `0` | count or sum |
| `set` | `set()` | collect unique values |

`defaultdict(int)` counts words:

```python
words = ["cat", "dog", "cat", "bird", "cat"]
counts = defaultdict(int)
for word in words:
    counts[word] += 1
print(dict(counts))  # {'cat': 3, 'dog': 1, 'bird': 1}
```

This is grouping with a numeric accumulator instead of a list. `Counter(words)` from the previous lesson is another purpose-built frequency counter.

### 2.4 Grouping plus aggregation

To calculate total spending per customer:

```python
transactions = [
    {"customer": "A", "amount": 100},
    {"customer": "B", "amount": 250},
    {"customer": "A", "amount": 300},
    {"customer": "B", "amount": 50},
]

totals = {}
for transaction in transactions:
    customer = transaction["customer"]
    amount = transaction["amount"]
    if customer not in totals:
        totals[customer] = 0
    totals[customer] += amount

print(totals)  # {'A': 400, 'B': 300}
```

The zero is the starting/identity value for addition. The same calculation with `defaultdict` is:

```python
totals = defaultdict(int)
for transaction in transactions:
    totals[transaction["customer"]] += transaction["amount"]
print(dict(totals))  # {'A': 400, 'B': 300}
```

“Group by X, then sum/count/average Y” is common in dashboards, ETL rollups, banking, log metrics, reporting, and ML feature preparation.

### 2.5 The accumulator changes the result

```python
records = [("A", 10), ("A", 20), ("B", 30), ("A", 10)]

as_lists = defaultdict(list)
for key, value in records:
    as_lists[key].append(value)
# A: [10, 20, 10]; B: [30]

as_counts = defaultdict(int)
for key, value in records:
    as_counts[key] += 1
# A: 3; B: 1

as_sums = defaultdict(int)
for key, value in records:
    as_sums[key] += value
# A: 40; B: 30

as_unique = defaultdict(set)
for key, value in records:
    as_unique[key].add(value)
# A: {10, 20}; B: {30}

minimums = {}
for key, value in records:
    if key not in minimums or value < minimums[key]:
        minimums[key] = value
# A: 10; B: 30
```

A list preserves repeated values; a set removes repeats; an integer can count or sum; a comparison can retain minimum/maximum. Choose the accumulator based on the answer required.

### 2.6 Dictionary comprehensions are not grouping accumulators

This loses earlier records when keys repeat:

```python
records = [("sales", 100), ("support", 200), ("sales", 150)]
broken = {category: amount for category, amount in records}
# {'sales': 150, 'support': 200} — first sales amount overwritten
```

A comprehension assigns a value for each key; it does not naturally append to an existing value. Use a loop, `setdefault()`, or `defaultdict` for grouping. Comprehensions are useful to reshape an already-built result:

```python
totals = {"A": 400, "B": 300}
labeled = {customer: f"${amount}" for customer, amount in totals.items()}
# {'A': '$400', 'B': '$300'}
```

### 2.7 `itertools.groupby`: consecutive groups only

```python
from itertools import groupby

records = [("A", 10), ("A", 20), ("B", 30), ("B", 40)]
for key, group in groupby(records, key=lambda record: record[0]):
    print(key, list(group))
# A [('A', 10), ('A', 20)]
# B [('B', 30), ('B', 40)]
```

The key function selects the tuple's first element. Each `group` is an iterator, so `list(group)` materializes it for printing/reuse.

Important: `groupby` only combines **adjacent** equal keys. With `[("A", 10), ("B", 30), ("A", 20)]`, it produces A, B, A as three groups. Sort by the same key first when you need all equal keys together:

```python
unsorted_records = [("A", 10), ("B", 30), ("A", 20)]
sorted_records = sorted(unsorted_records, key=lambda r: r[0])
for key, group in groupby(sorted_records, key=lambda r: r[0]):
    print(key, list(group))
```

Use dictionary/`defaultdict` grouping for general unsorted input. Use `groupby` for already-sorted or streaming data when a full grouped dictionary is undesirable.

## 3. Deduplication: define what “same” means

For `[1, 2, 2, 3, 3, 3, 4]`, duplicate values seem obvious. Records are harder: identity may mean the whole value, an ID, email, customer ID, transaction ID, or a composite such as `(customer_id, date)`. Choosing the wrong identity can silently delete valid records or leave duplicates behind.

### 3.1 `set()` for unique values

```python
numbers = [1, 2, 2, 3, 3, 3, 4]
unique = set(numbers)
print(unique)  # {1, 2, 3, 4}
```

A set cannot contain duplicate values. Membership/insertion uses hashing and is O(1) average case. But sets do **not** guarantee original insertion order. Use `set()` only when order is irrelevant; use `sorted(set(items))` when you want unique values in sorted order.

### 3.2 Preserve first-seen order

```python
items = [3, 1, 2, 3, 1, 4]
seen = set()
result = []

for item in items:
    if item not in seen:
        seen.add(item)
        result.append(item)

print(result)  # [3, 1, 2, 4]
```

`seen` gives fast membership checks; `result` stores accepted items in original order. The first occurrence is retained. For simple hashable values, the compact equivalent is:

```python
unique_in_order = list(dict.fromkeys(items))
# [3, 1, 2, 4]
```

This works because Python 3.7+ dictionaries preserve insertion order and dictionary keys are unique. Values must be hashable.

### 3.3 Deduplicate dictionaries by a field

Lists and dictionaries are unhashable, so `set(users)` raises `TypeError`. Set elements/dictionary keys must be hashable and have stable hashes; numbers, strings, tuples of hashable values, and frozensets are common examples.

First-write-wins:

```python
users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 1, "name": "Alice Updated"},
]
seen_ids = set()
unique_users = []
for user in users:
    if user["id"] not in seen_ids:
        seen_ids.add(user["id"])
        unique_users.append(user)
# Keeps Alice for id 1; later id 1 is discarded.
```

Last-write-wins:

```python
users_by_id = {}
for user in users:
    users_by_id[user["id"]] = user
unique_users = list(users_by_id.values())
# Keeps Alice Updated for id 1.
```

First-write-wins is suitable when the earliest record is authoritative; last-write-wins when later records are corrections/current state. This is a business rule, not a purely technical choice. Updating an existing dictionary key replaces its value but does not move its original insertion position.

### 3.4 Composite-key deduplication

When identity depends on multiple fields, build a tuple:

```python
records = [
    {"customer_id": "C1", "date": "2026-01-01", "amount": 50},
    {"customer_id": "C1", "date": "2026-01-01", "amount": 999},
    {"customer_id": "C1", "date": "2026-01-02", "amount": 75},
    {"customer_id": "C2", "date": "2026-01-01", "amount": 20},
]
seen_keys = set()
unique_records = []
for record in records:
    key = (record["customer_id"], record["date"])
    if key not in seen_keys:
        seen_keys.add(key)
        unique_records.append(record)
```

A tuple of hashable values is hashable. This handles business uniqueness such as one record per customer per day.

## 4. Sorting: put data into a defined order

Sorting arranges values by comparison. Python's built-in sort is optimized; normally you should use it rather than write your own sorting algorithm.

### 4.1 `sorted()` versus `list.sort()`

```python
numbers = [5, 2, 9, 1]
sorted_numbers = sorted(numbers)
# numbers remains [5, 2, 9, 1]
# sorted_numbers is [1, 2, 5, 9]

numbers = [5, 2, 9, 1]
result = numbers.sort()
# numbers is now [1, 2, 5, 9]; result is None
```

`sorted(iterable)` returns a new list and accepts any iterable. `list.sort()` is a list method; it sorts the original list in place and returns `None`. Never write `numbers = numbers.sort()` because that replaces the variable with `None`. Use `.sort()` alone or assign `sorted(numbers)` to a new variable.

### 4.2 Ascending, descending, and `reversed()`

```python
numbers = [5, 2, 9, 1]
sorted(numbers)                 # [1, 2, 5, 9]
sorted(numbers, reverse=True)   # [9, 5, 2, 1]
numbers.sort(reverse=True)      # in-place descending sort
list(reversed(numbers))         # simply flips existing order; does not sort
```

`reverse=True` asks the sorting operation to order largest-to-smallest. `reversed()` only walks the current sequence from end to beginning. Sorting ascending and then reversing the whole result can change relative order among equal keys; use `reverse=True` for descending sorting.

### 4.3 Strings and key functions

```python
names = ["Charlie", "Alice", "Bob"]
sorted(names)  # ['Alice', 'Bob', 'Charlie']

names = ["charlie", "Alice", "bob"]
sorted(names)  # uppercase sorts before lowercase by code point
sorted(names, key=str.lower)  # ['Alice', 'bob', 'charlie']
```

Default string sorting is case-sensitive/lexicographic. `key=str.lower` compares lowercase forms but returns the original strings unchanged.

A **key function** computes what should be compared:

```python
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 20},
    {"name": "Charlie", "age": 25},
]
sorted(users, key=lambda user: user["age"])
# Bob (20), Charlie (25), Alice (30)
```

The lambda receives one record and returns its age. Python computes each key once per item, then compares the keys. A named function is also valid:

```python
def get_age(user):
    return user["age"]

sorted(users, key=get_age)
```

Use a named function when the logic is more complex, reusable, or worth unit testing.

### 4.4 Multiple sort keys

Tuple keys sort by the first field, then the second to break ties:

```python
employees = [
    {"department": "A", "salary": 50000},
    {"department": "B", "salary": 60000},
    {"department": "A", "salary": 70000},
]
sorted(employees, key=lambda e: (e["department"], e["salary"]))
# A/50000, A/70000, B/60000
```

For department ascending and salary descending, negate the numeric salary:

```python
sorted(employees, key=lambda e: (e["department"], -e["salary"]))
# A/70000, A/50000, B/60000
```

Negation is for numeric fields. For independently reversed nonnumeric keys, use stable multi-pass sorting.

### 4.5 Sorting custom objects

```python
from dataclasses import dataclass

@dataclass
class Employee:
    name: str
    salary: int

employees = [Employee("Ada", 70000), Employee("Bob", 50000)]
sorted(employees, key=lambda employee: employee.salary)
# Bob then Ada
```

The key accesses an attribute instead of a dictionary field. The sorting mechanism is the same. Dataclasses are only introduced here as a small illustration, not a full OOP lesson.

### 4.6 Stable sorting

Python sorting is **stable**: items with equal keys keep their original relative order.

```python
records = [("A", 2), ("B", 1), ("A", 1)]
sorted(records, key=lambda record: record[1])
# [('B', 1), ('A', 1), ('A', 2)]
```

The two records with key `1` retain B before A because that was their input order. Stability permits two passes:

```python
by_salary = sorted(employees, key=lambda e: e["salary"])       # secondary key
by_department = sorted(by_salary, key=lambda e: e["department"])  # primary key
```

The second stable sort preserves salary order inside each department. A tuple key is usually clearer and is the default recommendation.

### 4.7 `None` and missing values

`sorted([1, None, 2])` raises `TypeError` because Python cannot order `None` against an integer. Mixed incompatible types (such as strings and numbers) also fail. To put `None` last:

```python
values = [1, None, 2, None, 3]
sorted(values, key=lambda v: (v is None, v))
# [1, 2, 3, None, None]
```

The first tuple element is `False` for real values and `True` for `None`, so real values come first. For a possibly missing dictionary field, use `.get("field", default)` in the key function instead of direct indexing.

## 5. Combining the patterns

### 5.1 Group, then rank

```python
totals = {"A": 400, "B": 300, "C": 500}
ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
# [('C', 500), ('A', 400), ('B', 300)]
```

`.items()` gives `(customer, total)` pairs; `item[1]` selects total; `reverse=True` puts the highest first.

### 5.2 Deduplicate, then sort

```python
numbers = [5, 3, 5, 1, 3, 2]
unique_sorted = sorted(set(numbers))
# [1, 2, 3, 5]
```

For “one customer's highest transaction,” sort descending **before** first-write-wins deduplication:

```python
transactions = [
    {"customer": "B", "amount": 100},
    {"customer": "A", "amount": 500},
    {"customer": "B", "amount": 900},
    {"customer": "C", "amount": 200},
]
by_amount = sorted(transactions, key=lambda t: t["amount"], reverse=True)
seen = set()
top_per_customer = []
for t in by_amount:
    if t["customer"] not in seen:
        seen.add(t["customer"])
        top_per_customer.append(t)
# B/900, A/500, C/200
```

The order of operations determines which record survives.

### 5.3 Group and deduplicate together

```python
customers = [
    {"customer_id": "C1", "country": "UK"},
    {"customer_id": "C2", "country": "US"},
    {"customer_id": "C1", "country": "UK"},
    {"customer_id": "C3", "country": "UK"},
]
customers_by_country = defaultdict(set)
for customer in customers:
    customers_by_country[customer["country"]].add(customer["customer_id"])
# UK: {'C1', 'C3'}; US: {'C2'}
```

The dictionary groups by country; each set removes repeated IDs. Set order is not guaranteed; use `sorted()` for predictable order.

### 5.4 Deduplicate → group → aggregate → sort

```python
transactions = [
    {"transaction_id": "T1", "customer_id": "C1", "category": "food", "amount": 100},
    {"transaction_id": "T1", "customer_id": "C1", "category": "food", "amount": 100},
    {"transaction_id": "T2", "customer_id": "C1", "category": "travel", "amount": 500},
    {"transaction_id": "T3", "customer_id": "C2", "category": "food", "amount": 200},
]

unique_by_id = {}
for t in transactions:
    unique_by_id[t["transaction_id"]] = t
deduplicated = list(unique_by_id.values())  # last-write-wins

by_customer = defaultdict(list)
for t in deduplicated:
    by_customer[t["customer_id"]].append(t)

by_category_total = defaultdict(int)
for t in deduplicated:
    by_category_total[t["category"]] += t["amount"]

customer_totals = {
    customer: sum(t["amount"] for t in txns)
    for customer, txns in by_customer.items()
}
ranked = sorted(customer_totals.items(), key=lambda item: item[1], reverse=True)
# category totals: food 300, travel 500
# ranked: [('C1', 600), ('C2', 200)]
```

The example demonstrates deduplication, two groupings, aggregation, and sorting. It is a data-cleaning/reporting pipeline.

The previous five patterns also fit:

```python
# SEARCH
next((t for t in transactions if t["transaction_id"] == "T2"), None)

# FILTER
[t for t in transactions if t["status"] == "completed"]

# COUNT
sum(t["status"] == "completed" for t in transactions)

# MAP
[t["amount"] for t in transactions]

# AGGREGATE
sum(t["amount"] for t in transactions)

# DEDUPLICATE (last-write-wins)
list({t["transaction_id"]: t for t in transactions}.values())

# GROUP
defaultdict(list)  # keyed by customer

# SORT
sorted(customer_totals.items(), key=lambda item: item[1], reverse=True)
```

A realistic report may chain **deduplicate → filter → group → aggregate → sort**.

## 6. Industry applications

- **Banking:** group by account to build statements and fraud views.
- **Data engineering:** deduplicate by a business key such as `(source_system, record_id)` so ingestion retries do not double-count.
- **Log processing:** group errors by service to identify failing components.
- **Backend APIs:** sort by timestamp so newest feed items appear first.
- **ML preprocessing:** deduplicate training examples; repeated examples can bias training and inflate evaluation if duplicates leak across splits.
- **AI data pipelines:** group documents by source and deduplicate by `document_id` to reduce duplicate corpus content and retrieval skew.

## 7. Common mistakes to avoid

1. Appending to `groups[key]` before creating the key → `KeyError`; initialize it or use `setdefault`/`defaultdict`.
2. Grouping by the entire dictionary instead of the intended field → wrong key or unhashable-type error.
3. Assigning `groups[key] = value` repeatedly → overwrites earlier values instead of accumulating.
4. Confusing grouping (membership) with sorting (order).
5. Accidentally creating a `defaultdict` key just by reading `groups["new_key"]`.
6. Assuming `itertools.groupby` combines non-adjacent equal keys.
7. Calling `groupby` without sorting/contiguous keys first.
8. Using `set()` when original order matters.
9. Depending on a set's displayed order.
10. Trying `set(list_of_dicts)`; dictionaries are unhashable.
11. Choosing the wrong identity field.
12. Deleting legitimate repeated business events (e.g. two real $5 purchases).
13. Confusing identical field values with identical real-world entities.
14. Choosing first-write-wins when last-write-wins was required, or vice versa.
15. Expecting `.sort()` to return a sorted list or mutate when using `sorted()`.
16. Writing `numbers = numbers.sort()`; the variable becomes `None`.
17. Reversing the list rather than using `reverse=True` for descending sort.
18. Sorting on the wrong field.
19. Using a key function that returns an unexpected type or accesses absent data.
20. Sorting incomparable values such as `None` and integers or strings and numbers.
21. Sorting when order is not required; it adds cost without improving search/aggregation.

## 8. Edge cases and performance

- Empty input: grouping returns `{}`, deduplication an empty list/set, `sorted([])` returns `[]`.
- One item: one single-member group; sorting leaves it effectively unchanged.
- All duplicates: deduplication leaves one; grouping still retains all unless its accumulator is a set.
- No duplicates: deduplication returns the original values.
- Conflicting duplicate records: explicitly decide which version survives.
- Missing fields: direct `record["field"]` can raise `KeyError`; use `.get()` or validate the record.
- `None`: can be a valid group/dedup value, but needs special handling for sorting.
- Mixed types: `1` and `"1"` are different keys/identities; sorting mixed int/string values raises `TypeError`.
- Case: `"UK"` and `"uk"` are different unless normalized; use `.lower()` where appropriate.
- Negative and zero values group/sum/sort normally; `0` and `-0.0` compare equal.
- Already sorted or reverse-sorted input: Python's Timsort can exploit existing runs.

Typical complexity:

| Operation | Time | Extra space |
|---|---:|---:|
| Dictionary grouping | O(n) average | O(n) for stored values/groups |
| Set deduplication | O(n) average | O(u), unique values |
| Seen-set deduplication | O(n) average | O(u) plus output |
| Sorting | O(n log n) | `sorted()` creates O(n) output; `.sort()` still may use temporary memory |

Sorting is more expensive than one linear pass. If a pipeline needs grouping and sorting, group/aggregate first and sort the smaller result when the business logic permits. `sorted(set(items))` materializes a set and then a sorted list. Unlike a one-item-at-a-time filter/map, sorting needs enough of the collection to determine final order.

Classic sorting algorithms: bubble, insertion, and selection sort are intuitive but roughly O(n²); merge sort and quicksort use divide-and-conquer and commonly achieve O(n log n); Python uses **Timsort**, a stable hybrid that performs particularly well on already or partially sorted data. Production code should normally use Python's built-in sorting rather than hand-writing a sort.

## 9. Debugging and testing

Print the group key and dictionary before/after each iteration:

```python
groups = defaultdict(list)
for record in records:
    key = record["category"]
    print(f"record={record}, key={key}, groups before={dict(groups)}")
    groups[key].append(record["amount"])
    print(f"groups after={dict(groups)}")
```

For deduplication, print the identity key, `seen` before, and whether the record is kept:

```python
seen = set()
result = []
for item in items:
    key = item["id"]
    kept = key not in seen
    print(item, key, seen, kept)
    if kept:
        seen.add(key)
        result.append(item)
```

For sorting, print each item and its computed key:

```python
for item in items:
    print(item, "→ key:", key_function(item))
```

Tests from the lesson:

```python
def group_by_category(records):
    groups = defaultdict(list)
    for category, amount in records:
        groups[category].append(amount)
    return dict(groups)

def test_grouping():
    assert group_by_category([("a", 1), ("a", 2)]) == {"a": [1, 2]}
    assert group_by_category([("a", 1), ("b", 2)]) == {"a": [1], "b": [2]}
    assert group_by_category([]) == {}

def deduplicate_by_id(records):
    seen = set()
    result = []
    for record in records:
        if record["id"] not in seen:
            seen.add(record["id"])
            result.append(record)
    return result

def test_deduplication():
    a, b = {"id": 1}, {"id": 2}
    assert deduplicate_by_id([a, b]) == [a, b]
    assert deduplicate_by_id([a, a, a]) == [a]
    assert deduplicate_by_id([a, b, a]) == [a, b]
    assert deduplicate_by_id([{"id": 1, "v": 1}, {"id": 1, "v": 2}]) == [{"id": 1, "v": 1}]

def test_sorting():
    assert sorted([3, 1, 2]) == [1, 2, 3]
    assert sorted([3, 1, 2], reverse=True) == [3, 2, 1]
    assert sorted([("a", 2), ("b", 2)], key=lambda x: x[1]) == [("a", 2), ("b", 2)]
    assert sorted([]) == []
    assert sorted([5]) == [5]
    assert sorted(["Bob", "alice"], key=str.lower) == ["alice", "Bob"]

test_grouping()
test_deduplication()
test_sorting()
print("All tests passed.")
```

A function definition does not run the test. Call each test function. A successful `assert` is silent; a failing one raises `AssertionError` at the failed condition.

## 10. Pattern recognition and final takeaways

- “Which items belong together?” → grouping (`dict`, `setdefault`, `defaultdict`, `groupby`).
- “Which items represent the same thing?” → deduplication (`set`, seen-set, `dict.fromkeys`, record identity).
- “In what order should items appear?” → sorting (`sorted`, `.sort`, `key=`, `reverse=True`).

Common pipelines: `GROUP → AGGREGATE`; `FILTER → GROUP → AGGREGATE`; `GROUP → AGGREGATE → SORT`; `DEDUPLICATE → SORT`; `GROUP → DEDUPLICATE`; and `DEDUPLICATE → FILTER → GROUP → AGGREGATE → SORT`.

The main engineering discipline is to decide the grouping key, duplicate identity, winner policy, and sort key **before** coding.

---

# Part B — Learning-level assessment from the Stage 1 project tree

The roadmap places this lesson at:

`Stage 1 — Programming & Computational Thinking/04-Problem-Solving-Collections-and-Algorithmic-Habits/02-grouping-deduplication-and-sorting.md`

Its immediate companion is `01-search-count-filter-map-and-aggregate.md`. The module then progresses to Big-O, choosing collection types, comprehensions/readable code, recursion, and parsing/regular expressions. Earlier Stage 1 foundations include computational thinking; Python core types (strings, lists, tuples, dictionaries, sets, conversion, mutability); and control flow/functions/scope/errors. Later modules cover files/structured data/CLI, modules and code quality, testing/debugging, OOP/data modelling, and production-oriented Python.

**Your current learning position:** foundational Python moving into algorithmic problem-solving with collections. The earlier lesson work on strings, sets, dictionaries, lists, tuples, loops, and the search/count/filter/map/aggregate patterns supports this chapter. You should be able to read simple loops, unpack tuples, access dictionary fields, use collection methods, and write basic functions.

**What the project tree can and cannot prove:** it shows the intended curriculum and prerequisite sequence; it does not prove that every folder, lesson, exercise, or project has been completed or mastered. Practical proficiency must be checked by independently predicting outputs, writing the 20 exercises, and explaining why each key/identity/accumulator is correct.

The solutions below deliberately stay within the chapter's concepts and earlier foundations. `defaultdict`, `groupby`, lambdas, comprehensions, and `dataclasses` are introduced by this lesson; the mini-project uses functions because the source lesson itself requires them. No pandas, SQL, Spark, external packages, advanced OOP, or later-stage tools are needed.

---

# Part C — All 20 exercises solved step by step

## Level 1 — Beginner

### 1. Group words by first letter

```python
words = ["apple", "banana", "avocado", "blueberry", "cherry"]
groups = {}
for word in words:                         # visit each word
    groups.setdefault(word[0], []).append(word)  # first letter → list
print(groups)
# {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
```

`word[0]` is the group key. `setdefault` creates a list when needed; `append` stores the word.

### 2. Remove duplicate numbers

```python
numbers = [4, 2, 4, 1, 2, 3]
print(set(numbers))  # {1, 2, 3, 4}
```

A set keeps one copy of each hashable number. Order is not guaranteed, which is allowed by this exercise.

### 3. Sort numbers

```python
numbers = [8, 3, 9, 1]
print(sorted(numbers))  # [1, 3, 8, 9]
```

`sorted` returns a new ascending list; it does not change `numbers`.

### 4. Sort names alphabetically, ignoring case

```python
names = ["Zoe", "amir", "Bella"]
print(sorted(names, key=str.lower))  # ['amir', 'Bella', 'Zoe']
```

The key compares lowercase forms but keeps original capitalization in the output.

### 5. Count items per category

```python
items = [("fruit", "apple"), ("veg", "carrot"), ("fruit", "banana")]
counts = {}
for category, item in items:               # unpack each tuple
    counts[category] = counts.get(category, 0) + 1  # prior count + 1
print(counts)  # {'fruit': 2, 'veg': 1}
```

`get(category, 0)` supplies zero for a new category, then the count increases.

## Level 2 — Intermediate

### 6. Group transactions by customer

```python
transactions = [
    {"customer": "A", "amount": 50},
    {"customer": "B", "amount": 20},
    {"customer": "A", "amount": 30},
]
groups = defaultdict(list)
for t in transactions:
    groups[t["customer"]].append(t["amount"])  # collect amount per customer
print(dict(groups))  # {'A': [50, 30], 'B': [20]}
```

The customer is the key; the amount is the stored group value.

### 7. Deduplicate IDs and preserve order

```python
ids = ["C3", "C1", "C3", "C2", "C1"]
print(list(dict.fromkeys(ids)))  # ['C3', 'C1', 'C2']
```

Dictionary keys are unique and retain first insertion order.

### 8. Sort users by age

```python
users = [{"name": "A", "age": 40}, {"name": "B", "age": 25}]
print(sorted(users, key=lambda u: u["age"]))
# [{'name': 'B', 'age': 25}, {'name': 'A', 'age': 40}]
```

The lambda extracts age; the full dictionaries are returned in age order.

### 9. Sort transactions by amount descending

```python
ranked = sorted(transactions, key=lambda t: t["amount"], reverse=True)
# order of amounts: 50, 30, 20
```

`key` selects amount and `reverse=True` puts the largest first.

### 10. Group and calculate totals

```python
totals = defaultdict(int)
for t in transactions:
    totals[t["customer"]] += t["amount"]  # add to customer's running total
print(dict(totals))  # {'A': 80, 'B': 20}
```

Each customer starts at zero automatically and accumulates their amounts.

## Level 3 — Advanced

### 11. Deduplicate dictionaries by ID — first wins

```python
records = [{"id": 1, "v": "x"}, {"id": 2, "v": "y"}, {"id": 1, "v": "z"}]
seen, result = set(), []
for r in records:
    if r["id"] not in seen:  # accept first occurrence only
        seen.add(r["id"])
        result.append(r)
print(result)  # id 1 keeps x; id 2 keeps y
```

The set stores hashable IDs, not dictionaries. The list preserves record order.

### 12. Keep latest record for each ID — last wins

```python
by_id = {}
for r in records:
    by_id[r["id"]] = r  # later record replaces earlier value
print(list(by_id.values()))  # id 1 keeps z; id 2 keeps y
```

Dictionary assignment overwrites the value for an existing ID.

### 13. Group customers by country

```python
customers = [{"id": "C1", "country": "UK"}, {"id": "C2", "country": "US"}, {"id": "C3", "country": "UK"}]
groups = defaultdict(list)
for c in customers:
    groups[c["country"]].append(c["id"])
print(dict(groups))  # {'UK': ['C1', 'C3'], 'US': ['C2']}
```

Country is the grouping key; customer ID is appended to its list.

### 14. Group unique products by category

```python
sales = [("food", "apple"), ("food", "apple"), ("tech", "phone")]
groups = defaultdict(set)
for category, product in sales:
    groups[category].add(product)  # set suppresses repeated product
print(dict(groups))  # food {'apple'}; tech {'phone'}
```

The outer dictionary groups; each inner set deduplicates.

### 15. Sort customers by total spending

```python
totals = {"A": 80, "B": 20}
ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
print(ranked)  # [('A', 80), ('B', 20)]
```

`.items()` creates customer/total pairs; `item[1]` is the total.

## Level 4 — Production-oriented

### 16. Deduplicate events using a composite key

```python
events = [
    {"user_id": "U1", "event_type": "click", "day": "2026-01-01"},
    {"user_id": "U1", "event_type": "click", "day": "2026-01-01"},
    {"user_id": "U1", "event_type": "click", "day": "2026-01-02"},
]
seen, unique = set(), []
for e in events:
    key = (e["user_id"], e["event_type"], e["day"])  # combined identity
    if key not in seen:
        seen.add(key)
        unique.append(e)
print(len(unique))  # 2
```

All three fields together define identity; the repeated first-day event is discarded.

### 17. Group logs by service and count severity

```python
logs = [
    {"service": "auth", "severity": "ERROR"},
    {"service": "auth", "severity": "INFO"},
    {"service": "billing", "severity": "ERROR"},
]
groups = defaultdict(lambda: defaultdict(int))
for log in logs:
    groups[log["service"]][log["severity"]] += 1
print({s: dict(counts) for s, counts in groups.items()})
# {'auth': {'ERROR': 1, 'INFO': 1}, 'billing': {'ERROR': 1}}
```

The outer key is service; the inner key is severity; the inner integer counts events.

### 18. Calculate totals by category

```python
totals = defaultdict(int)
for t in transactions:  # use the §29 transaction records
    totals[t["category"]] += t["amount"]
print(dict(totals))  # {'food': 300, 'travel': 500}
```

Each category has a running amount total.

### 19. Produce a ranked customer report

```python
grouped = defaultdict(list)
for t in transactions:
    grouped[t["customer_id"]].append(t["amount"])
totals = {c: sum(amounts) for c, amounts in grouped.items()}
ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
report = [{"customer": c, "total": total} for c, total in ranked]
print(report)
```

First collect amounts by customer, then sum each list, sort by total descending, and reshape each tuple into a dictionary.

### 20. Build the data-cleaning pipeline

```python
def deduplicate(transactions):
    by_id = {}
    for t in transactions:
        by_id[t["transaction_id"]] = t  # last occurrence wins
    return list(by_id.values())

def pipeline(transactions):
    unique = deduplicate(transactions)
    completed = [t for t in unique if t["status"] == "completed"]
    grouped = defaultdict(list)
    for t in completed:
        grouped[t["customer_id"]].append(t["amount"])
    totals = {c: sum(amounts) for c, amounts in grouped.items()}
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)

transactions = [
    {"transaction_id": "T1", "customer_id": "C1", "category": "food", "amount": 100, "status": "completed"},
    {"transaction_id": "T1", "customer_id": "C1", "category": "food", "amount": 150, "status": "completed"},
    {"transaction_id": "T2", "customer_id": "C2", "category": "travel", "amount": 300, "status": "failed"},
]
print(pipeline(transactions))  # [('C1', 150)]
```

The stages are last-write-wins deduplication, completed-only filtering, grouping, summing, and descending ranking. Failed T2 is excluded; corrected T1 amount 150 survives.

---

# Part D — Mini project: Customer Transaction Analysis Pipeline

## Requirements and decisions

Input records contain `transaction_id`, `customer_id`, `category`, `amount`, `status`, and `timestamp`. The output must include deduplicated records, completed records, per-customer totals and counts, per-category totals, ranked customers, and the top customer.

The source project chooses **last-write-wins**: later records with the same transaction ID are treated as corrected resubmissions. It assumes the transaction ID is present and asks you to decide how to handle missing amounts/categories, unexpected statuses, empty input, and customers with no completed transactions.

## Reference implementation

```python
from collections import defaultdict

def deduplicate_transactions(transactions):
    unique_by_id = {}
    for transaction in transactions:
        unique_by_id[transaction["transaction_id"]] = transaction
    return list(unique_by_id.values())

def filter_completed(transactions):
    return [t for t in transactions if t["status"] == "completed"]

def group_by_customer(transactions):
    groups = defaultdict(list)
    for t in transactions:
        groups[t["customer_id"]].append(t)
    return groups

def customer_totals(grouped):
    return {
        customer: sum(t["amount"] for t in txns)
        for customer, txns in grouped.items()
    }

def customer_counts(grouped):
    return {customer: len(txns) for customer, txns in grouped.items()}

def totals_by_category(transactions):
    totals = defaultdict(int)
    for t in transactions:
        totals[t["category"]] += t["amount"]
    return dict(totals)

def rank_customers(totals):
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)

def build_summary(transactions):
    deduplicated = deduplicate_transactions(transactions)
    completed = filter_completed(deduplicated)
    grouped = group_by_customer(completed)
    totals = customer_totals(grouped)
    counts = customer_counts(grouped)
    ranking = rank_customers(totals)
    return {
        "deduplicated_transactions": deduplicated,
        "completed_transactions": completed,
        "customer_totals": totals,
        "customer_counts": counts,
        "category_totals": totals_by_category(completed),
        "ranking": ranking,
        "top_customer": ranking[0] if ranking else None,
    }
```

**How the functions work:** `deduplicate_transactions` overwrites an ID's previous record, implementing last-write-wins. `filter_completed` removes non-completed records. `group_by_customer` builds one transaction list per customer. `customer_totals` sums amounts; `customer_counts` counts records. `totals_by_category` aggregates by category. `rank_customers` sorts totals highest-first. `build_summary` calls these small steps in order and returns one dictionary. `ranking[0] if ranking else None` safely handles no completed transactions.

## Dry-run sample and expected result

```python
transactions = [
    {"transaction_id": "T1", "customer_id": "C1", "category": "food", "amount": 100, "status": "completed", "timestamp": "2026-01-01"},
    {"transaction_id": "T1", "customer_id": "C1", "category": "food", "amount": 150, "status": "completed", "timestamp": "2026-01-02"},
    {"transaction_id": "T2", "customer_id": "C1", "category": "travel", "amount": 500, "status": "failed", "timestamp": "2026-01-01"},
    {"transaction_id": "T3", "customer_id": "C2", "category": "food", "amount": 200, "status": "completed", "timestamp": "2026-01-01"},
]
summary = build_summary(transactions)
print(summary)
```

Expected key results:

- Deduplicated: corrected T1 amount 150, failed T2 amount 500, and T3 amount 200.
- Completed: T1 and T3 only.
- Customer totals: `{'C1': 150, 'C2': 200}`.
- Customer counts: `{'C1': 1, 'C2': 1}`.
- Category totals: `{'food': 350}`.
- Ranking: `[('C2', 200), ('C1', 150)]`.
- Top customer: `('C2', 200)`.

**Important reasoning:** T1's later version replaces its earlier version; failed T2 never enters customer/category calculations; and the empty-ranking check prevents an `IndexError`.

---

# Part E — Interview revision questions

Be able to explain:

1. Grouping versus filtering; how to group manually with a dictionary.
2. `defaultdict` versus `setdefault`; why `defaultdict(int)` counts.
3. Why `itertools.groupby` needs consecutive keys.
4. Why deduplication requires a business identity.
5. Why sets require hashable elements and do not preserve insertion order.
6. How to deduplicate dictionaries by one field or a composite key.
7. First-write-wins versus last-write-wins and when each is correct.
8. `sorted()` versus `.sort()`; why `.sort()` returns `None`.
9. Key functions, tuple keys, stable sorting, and `reverse=True` versus `reversed()`.
10. How to handle `None`/missing fields in a sort.
11. Why grouping/deduplication are usually O(n) and sorting O(n log n).
12. Why deduplicating before aggregation prevents double-counting.

**Scenario practice:** deduplicate retried transaction messages by a transaction ID; produce sales per region ranked highest-first; retain latest customer state; deduplicate events by `(user_id, event_timestamp)`; explain why grouping/aggregation before sorting can reduce work.

---

# Final checklist

- [ ] I can identify a grouping key, group value, accumulator, duplicate identity, winner rule, and sort key before coding.
- [ ] I can implement grouping with a plain dictionary, `setdefault`, and `defaultdict`.
- [ ] I know when the accumulator should be a list, integer, or set.
- [ ] I understand why `groupby` only groups consecutive keys.
- [ ] I can deduplicate simple values and dictionaries while preserving order when needed.
- [ ] I can choose first-write-wins or last-write-wins deliberately.
- [ ] I can use composite tuple keys.
- [ ] I can explain and use `sorted`, `.sort`, `key`, `reverse`, and stable sorting.
- [ ] I can combine deduplication, filtering, grouping, aggregation, and sorting in a small pipeline.
- [ ] I can test empty, single-item, duplicate, missing-field, and mixed-type cases.
