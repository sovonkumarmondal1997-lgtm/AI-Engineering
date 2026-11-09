# 01 — Search, Count, Filter, Map, and Aggregate
## Study Notes, Worked Examples, Exercises, and Mini-Project Solutions

**Source lesson:** `01-search-count-filter-map-and-aggregate.md`  
**Curriculum location:** Stage 1 → Module 04 — Problem-Solving, Collections and Algorithmic Habits  
**Purpose:** Understand the source lesson and complete every exercise and the mini-project using the Python concepts in this lesson.

---

# Part A — Complete lesson summary and teaching notes

## 1. Learning objectives and why the five patterns matter

Almost every data-processing task can be recognized as one or more of five patterns:

| Pattern | Question | Result |
|---|---|---|
| Search | Does something exist? What is the first match? | Boolean or one item |
| Count | How many items match? | Integer |
| Filter | Which items should remain? | Smaller collection |
| Map | What should each item become? | Transformed collection |
| Aggregate | What single value summarizes the items? | One value |

Example input:

```python
numbers = [10, 20, 30, 40, 50]
```

- Is `30` present? Search.
- How many values exceed `25`? Count.
- Keep values above `25`. Filter.
- Add `5` to every value. Map.
- Calculate total, maximum, or average. Aggregate.

These are problem-solving patterns, not merely Python syntax. Data engineering uses them to validate batches, clean records, summarize logs, transform API responses, and prepare model-training data. A larger task often combines them: **filter → map → aggregate**.

## 2. Foundation: iteration

**Iteration** means visiting items in an iterable one at a time. Lists, tuples, sets, strings, and dictionaries are common iterables.

Important vocabulary:

- **Iterable:** an object that can supply items to a loop.
- **Item/current item:** the value being processed in the current pass.
- **Condition:** a test that evaluates to `True` or `False`.
- **Accumulator:** a variable holding a running result, such as a count or total.
- **Result collection:** a new list/container built as matching or transformed items are encountered.
- **`break`:** leave the loop immediately.
- **`continue`:** skip the rest of this pass and move to the next item.
- **Early return:** leave the whole function immediately.

```python
numbers = [10, 20, 30, 40]

for number in numbers:
    print(number)
```

The loop visits `10`, `20`, `30`, and `40` in that order.

```python
# Visit every item
for number in numbers:
    print(number)

# Stop when 30 is found
for number in numbers:
    if number == 30:
        print("found it")
        break

# Skip 30, but continue processing later values
for number in numbers:
    if number == 30:
        continue
    print(number)
```

A loop can build a collection or accumulate one value:

```python
result = []
for number in numbers:
    if number > 20:
        result.append(number)
# [30, 40]

total = 0
for number in numbers:
    total += number
# 100
```

Filtering/mapping normally build collections; counting/aggregation normally update a single accumulator. These are useful mental models; built-in operations can use optimized internal implementations rather than literally executing the same Python loop.

## 3. Search

Search asks whether a value exists or asks for the first item matching a condition. A search can stop once the answer is known.

### 3.1 Manual search and early termination

```python
numbers = [10, 20, 30, 40]

found = False
for number in numbers:
    if number == 30:
        found = True
        break

print(found)  # True
```

Line by line: initialize `found` to `False`; visit each number; compare it with `30`; set `found` to `True` on a match; `break` avoids checking unnecessary later items. If the value is absent, the loop finishes and `found` remains `False`. An empty list also returns `False` because the loop body never runs. Duplicates do not change an existence answer.

Without `break`, the result may still be correct, but the loop wastes work after finding the answer. On a very large collection, early termination matters.

### 3.2 Membership: `in` and `not in`

```python
numbers = [10, 20, 30, 40]
print(30 in numbers)       # True
print(999 in numbers)      # False
print(999 not in numbers)  # True
```

Use membership for an exact-value existence question. Behaviour depends on the collection:

```python
30 in [10, 20, 30]                 # list: sequential search
30 in (10, 20, 30)                 # tuple: sequential search
30 in {10, 20, 30}                 # set: hash-based membership
"cat" in "concatenate"             # substring search
prices = {"apple": 1, "banana": 2}
"apple" in prices                  # True: dictionary keys
1 in prices                        # False: not a key
1 in prices.values()               # True: explicit value search
("apple", 1) in prices.items()      # True: key/value pair
```

Dictionary membership checks keys by default, not values.

### 3.3 Search by condition

```python
numbers = [10, 20, 30, 40, 60]
result = None
for number in numbers:
    if number > 50:
        result = number
        break
print(result)  # 60
```

The same pattern works with dictionaries/records:

```python
users = [
    {"name": "Ada", "active": False},
    {"name": "Grace", "active": True},
    {"name": "Alan", "active": True},
]
first_active = None
for user in users:
    if user["active"]:
        first_active = user
        break
# first_active is Grace's record
```

A reusable function can return the first match:

```python
def find_first(collection, condition):
    for item in collection:
        if condition(item):
            return item
    return None

def is_large(number):
    return number > 100

print(find_first([5, 250, 40], is_large))  # 250
print(find_first([5, 20, 40], is_large))   # None
```

`return` exits the function; `break` exits only the current loop.

### 3.4 `any()`, `all()`, and `next()`

```python
numbers = [10, 20, 30, 40]
any(number > 25 for number in numbers)  # True
all(number > 0 for number in numbers)   # True
all(number > 25 for number in numbers)  # False
```

- `any()` asks whether at least one item is truthy; it stops at the first `True`.
- `all()` asks whether every item is truthy; it stops at the first `False`.
- `any([])` is `False`; `all([])` is `True` (there are no counterexamples to the universal statement). Check whether empty input should be allowed to pass your business rule.

A generator expression such as `number > 25 for number in numbers` produces values one at a time. `any()`/`all()` consume it lazily.

To retrieve the first matching item, use `next()`:

```python
first_big = next((x for x in numbers if x > 25), None)
```

`next(generator, default)` returns the first generated value, or `None` if no value is produced. Without the default, an exhausted generator raises `StopIteration`.

Choose appropriately:

| Need | Tool |
|---|---|
| Exact value exists? | `in` / `not in` |
| Any item meets a condition? | `any()` |
| Every item meets a condition? | `all()` |
| First matching item? | `next((...), default)` |
| Complex multi-step search logic? | Loop with `break` or function with `return` |

## 4. Count

Count asks how many items satisfy a condition. Unlike search, a correct count normally needs to inspect every item.

### 4.1 Manual accumulator

```python
numbers = [10, 20, 30, 40]
count = 0
for number in numbers:
    if number > 20:
        count += 1
print(count)  # 2
```

Initialize the accumulator before the loop. It becomes `1` for each match.

### 4.2 Counting tools

```python
len(numbers)                 # 4: all items
[10, 20, 10, 30, 10].count(10)  # 3: occurrences of one exact value
sum(number > 20 for number in numbers)  # 2: conditional count
```

Python booleans behave numerically as `True == 1` and `False == 0`:

```python
True + True + False  # 2
int(True), int(False)  # (1, 0)
```

Therefore, summing a condition counts how many times it is true. Use it when the condition remains readable.

### 4.3 Frequency counting with `Counter`

A manual frequency dictionary increments a key for every occurrence. `collections.Counter` provides that functionality directly:

```python
from collections import Counter

words = ["cat", "dog", "cat", "bird"]
counts = Counter(words)
counts["cat"]          # 2
counts["fish"]         # 0, unlike a normal missing dictionary key
counts.most_common()   # [('cat', 2), ('dog', 1), ('bird', 1)]
counts.most_common(1)  # top one
counts.update(["cat", "owl"])  # add more occurrences
```

Typical uses include word frequencies, transaction statuses, and log severity frequencies.

| Question | Tool |
|---|---|
| Total number of items | `len()` |
| Occurrences of one value | `.count(value)` |
| Number satisfying a condition | loop accumulator or `sum(condition for ...)` |
| Frequency of every distinct value | `Counter()` |

## 5. Filter

Filter answers “which original items should I keep?” It selects items without changing them.

```python
numbers = [10, 20, 30, 40, 50]
result = []
for number in numbers:
    if number > 20:
        result.append(number)
# [30, 40, 50]
```

The original list remains unchanged; output order is preserved. A list comprehension expresses the same logic:

```python
result = [number for number in numbers if number > 20]
```

Read it as: output expression `number`, for each `number` in `numbers`, only if the condition is true. Multiple conditions work normally:

```python
[n for n in numbers if n > 10 and n < 50]
[n for n in numbers if n < 10 or n > 50]
[n for n in numbers if not (n > 10 and n < 50)]
```

Filtering other data types:

```python
words = ["cat", "elephant", "dog", "hippopotamus"]
long_words = [word for word in words if len(word) > 4]

users = [
    {"name": "Ada", "active": False},
    {"name": "Grace", "active": True},
    {"name": "Alan", "active": True},
]
active_users = [user for user in users if user["active"]]
eligible = [user for user in users
            if user["active"] and user.get("age", 0) >= 18]
```

`.get("age", 0)` avoids a `KeyError` if the key is missing; choose the default according to the meaning of your data.

The built-in `filter()` is lazy and returns an iterator, not a list:

```python
numbers = [10, 20, 30, 40, 50]
result = filter(lambda x: x > 20, numbers)
list(result)  # [30, 40, 50]
```

`lambda x: x > 20` is equivalent to a short function returning that comparison. Prefer a list comprehension for beginner-friendly, readable filtering; use named functions for complex conditions.

## 6. Map / transform

Filter selects which items remain. Map changes what each item becomes. With one input iterable, map produces one output for each input item; it does not drop items.

```python
numbers = [1, 2, 3, 4]
filtered = [n for n in numbers if n > 2]  # [3, 4]
doubled = [n * 2 for n in numbers]        # [2, 4, 6, 8]
```

Manual mapping:

```python
result = []
for number in numbers:
    result.append(number * 2)
```

Comprehension mapping:

```python
doubled = [number * 2 for number in numbers]
```

Built-in `map()` is lazy and returns an iterator:

```python
result = map(lambda x: x * 2, numbers)
list(result)  # [2, 4, 6, 8]
```

A named function can replace the lambda. Mapping can change types or extract structured fields:

```python
[str(n) for n in [1, 2]]  # ['1', '2']
users = [{"name": "Ada"}, {"name": "Grace"}]
names = [user["name"] for user in users]
```

Use a plain loop when a transformation needs several intermediate steps or branches. Do not force complicated logic into a comprehension.

## 7. Aggregate

Aggregate combines many values into one result: total, minimum, maximum, average, or product.

```python
numbers = [10, 20, 30, 40]
total = 0
for number in numbers:
    total += number
# 100

sum(numbers)  # 100
min(numbers)  # 10
max(numbers)  # 40
len(numbers)  # 4
```

Empty-input behaviour matters:

```python
sum([])                 # 0
min([])                 # ValueError
max([])                 # ValueError
max([], default=None)   # None
```

Guard a possibly empty list:

```python
values = []
largest = max(values) if values else None
```

Average:

```python
numbers = [10, 20, 30, 40]
average = sum(numbers) / len(numbers)  # 25.0
average = sum(numbers) / len(numbers) if numbers else 0
```

`statistics.mean(numbers)` communicates statistical intent; `statistics.mean([])` raises `StatisticsError`. The `statistics` module also provides `median()` and `stdev()`.

Product uses `math.prod()`:

```python
import math
math.prod([2, 3, 4])  # 24

product = 1
for number in [2, 3, 4]:
    product *= number
```

Accumulator identity values: `0` for sum/count, `1` for product, `False` for “any”, and `True` for “all”.

Aggregate only selected or transformed values with generator expressions:

```python
numbers = [5, 15, 25, 35]
sum(number for number in numbers if number > 10)  # 75
sum(number * 2 for number in numbers)             # 160
```

A generator expression avoids constructing an intermediate list when the values are consumed immediately.

## 8. `reduce()` and general accumulation

`functools.reduce()` repeatedly combines a running result with the next item:

```python
from functools import reduce

numbers = [10, 20, 30, 40]
total = reduce(lambda acc, n: acc + n, numbers)
# 100
```

Without an initial value, the first item becomes the initial accumulator. An explicit initial value is useful for empty input or when a specific identity is required:

```python
total = reduce(lambda acc, n: acc + n, numbers, 0)
```

Do not use `reduce()` for ordinary addition when `sum()` is clearer. A possible use is combining dictionaries:

```python
pieces = [{"a": 1}, {"b": 2}, {"c": 3}]
merged = reduce(lambda acc, piece: {**acc, **piece}, pieces, {})
# {'a': 1, 'b': 2, 'c': 3}

# Often easier to read:
merged = {}
for piece in pieces:
    merged.update(piece)
```

Prefer purpose-built tools (`sum`, `min`, `max`, `math.prod`, `str.join`) or an explicit loop when they communicate intent better.

## 9. Compare and compose the patterns

| Pattern | Output | Common tools |
|---|---|---|
| Search | Boolean or first item | `in`, `any`, `next`, loop + `break` |
| Count | Integer | `len`, `.count`, `sum`, `Counter` |
| Filter | Subset | comprehension, `filter` |
| Map | Transformed collection | comprehension, `map` |
| Aggregate | Single value | `sum`, `min`, `max`, `math.prod`, `statistics.mean`, `reduce` |

Using one transaction dataset:

```python
transactions = [
    {"amount": 100, "status": "completed"},
    {"amount": 250, "status": "failed"},
    {"amount": 400, "status": "completed"},
    {"amount": 50, "status": "completed"},
]

first_completed = next(
    (t for t in transactions if t["status"] == "completed"), None
)
completed_count = sum(t["status"] == "completed" for t in transactions)
completed = [t for t in transactions if t["status"] == "completed"]
amounts = [t["amount"] for t in transactions]
total_completed = sum(
    t["amount"] for t in transactions if t["status"] == "completed"
)  # 550
```

Composition examples:

```python
# Filter then map, in separate steps
completed = [t for t in transactions if t["status"] == "completed"]
amounts = [t["amount"] for t in completed]

# Same operation in one comprehension
amounts = [t["amount"] for t in transactions
           if t["status"] == "completed"]

# Filter → map → aggregate
total = sum(t["amount"] for t in transactions
            if t["status"] == "completed")

# Search → transform
first = next((t for t in transactions
              if t["status"] == "completed"), None)
first_amount = first["amount"] if first else None

# Filter → count; map → aggregate
failed_count = sum(1 for t in transactions if t["status"] == "failed")
total_amount = sum(t["amount"] for t in transactions)
```

These chains appear in ETL, backend authorization/response formatting, analytics KPIs, and AI/ML data cleaning and feature preparation.

## 10. Applying patterns to collections and strings

Dictionary comprehensions filter and map key/value pairs:

```python
prices = {"apple": 1, "banana": 3, "cherry": 2}
cheap = {name: price for name, price in prices.items() if price < 3}
doubled = {name: price * 2 for name, price in prices.items()}
sum(prices.values())  # 6
max(prices.values())  # 3
```

Use sets when you need repeated membership checks and do not need duplicates/order:

```python
allowed_ids = {101, 205, 309}
if user_id in allowed_ids:
    ...
```

Strings are iterable too:

```python
message = "2024-01-01 ERROR: connection refused"
words = message.split()
"ERROR" in message
log = "ERROR: retry. ERROR: retry. INFO: ok."
log.count("ERROR")  # 2
long_words = [word for word in words if len(word) > 4]
lowered = [word.lower() for word in words]
total_chars = sum(len(word) for word in words)
```

## 11. Engineering examples from the lesson

**Bank transactions**

```python
transactions = [
    {"id": "T1", "amount": 100, "status": "completed"},
    {"id": "T2", "amount": 250, "status": "failed"},
    {"id": "T3", "amount": 400, "status": "completed"},
]
failed = [t for t in transactions if t["status"] == "failed"]
failed_count = sum(t["status"] == "failed" for t in transactions)
failed_amount = sum(t["amount"] for t in transactions
                    if t["status"] == "failed")
ids = [t["id"] for t in transactions]
has_t2 = any(t["id"] == "T2" for t in transactions)
```

**Logs**

```python
log_lines = [
    "INFO: server started",
    "ERROR: disk full",
    "INFO: request handled",
    "ERROR: connection refused",
]
has_errors = any("ERROR" in line for line in log_lines)
error_count = sum("ERROR" in line for line in log_lines)
errors = [line for line in log_lines if "ERROR" in line]
messages = [line.split(": ", 1)[1] for line in log_lines]
characters = sum(len(line) for line in log_lines)
```

**Customers**

```python
customers = [
    {"name": "Ada", "spend": 500, "country": "UK"},
    {"name": "Grace", "spend": 1200, "country": "US"},
    {"name": "Alan", "spend": 300, "country": "UK"},
]
has_us = any(c["country"] == "US" for c in customers)
over_400 = sum(c["spend"] > 400 for c in customers)
high_value = [c for c in customers if c["spend"] > 400]
names = [c["name"] for c in customers]
revenue = sum(c["spend"] for c in customers)  # 2000
```

**Data quality**

```python
records = [
    {"id": 1, "email": "a@example.com"},
    {"id": 2, "email": None},
    {"id": 3, "email": "c@example.com"},
]
has_missing = any(r["email"] is None for r in records)
missing_count = sum(r["email"] is None for r in records)
valid = [r for r in records if r["email"] is not None]
emails = [r["email"].lower() for r in records
          if r.get("email") is not None]
valid_rate = (sum(r["email"] is not None for r in records) / len(records)
              if records else 0)
```

**AI/ML preprocessing**

```python
examples = [
    {"text": "great product", "label": "positive"},
    {"text": "", "label": "positive"},
    {"text": "terrible service", "label": "negative"},
]
has_empty = any(ex["text"] == "" for ex in examples)
usable_count = sum(ex["text"] != "" for ex in examples)
clean = [ex for ex in examples if ex["text"] != ""]
texts = [ex["text"] for ex in examples if ex["text"] != ""]
lengths = [len(ex["text"]) for ex in examples if ex["text"] != ""]
average_length = sum(lengths) / len(lengths) if lengths else None
```

For the sample, the usable text lengths are 13 and 15, so the average is `14.0` if counting characters exactly. The source lesson states `14.5`; this appears inconsistent with the literal sample strings and should be checked rather than silently assumed.

## 12. Common mistakes and their corrections

1. **Filter used for a yes/no search:** building a full list is unnecessary; use `any(...)`.
2. **`len()` used for conditional count:** `len(transactions)` counts all records; use `sum(condition for ...)`.
3. **Mutating a list while iterating:** removing an item shifts later positions and can skip items. Build a new filtered list instead.
4. **Accumulator not initialized:** set `total = 0` before the loop.
5. **Unconditional early return:** `return number < 0` inside a loop exits on its first item. Put the return inside the matching `if`, then return `False` after the loop.
6. **Wrong comparison boundary:** “at least 20” means `>= 20`, not `> 20`.
7. **Accidental nested list:** `[[n for n in numbers if n > 20]]` creates a list containing another list.
8. **Map confused with filter:** `map(lambda x: x > 20, numbers)` returns booleans for all inputs; use filter/comprehension to keep matching numbers.
9. **Unclear `map` + `filter` chain:** a comprehension is often clearer.
10. **Unnecessary intermediate list:** prefer `sum(n for n in numbers if n > 20)` over `sum([n for n in numbers if n > 20])`.
11. **`reduce()` instead of a clear built-in:** use `sum(numbers)` for addition.
12. **Empty average:** guard division by zero.
13. **Empty `min`/`max`:** use a condition or `default=`.
14. **String length mistaken for word count:** `len(sentence)` counts characters; `len(sentence.split())` counts words.
15. **Dictionary membership misunderstood:** `in dictionary` checks keys; use `.values()` for values.
16. **Iterator mistaken for list:** `map`/`filter` return one-pass iterators; wrap with `list()` if you need list operations such as `len()`.
17. **Overly clever nested one-liners:** use named intermediate results or a plain loop when that is easier to read and debug.

## 13. Edge cases to check

- Empty input: search → `False`/`None`; count → `0`; filter/map → `[]`; sum → `0`; min/max need a default or guard.
- One item: verify the single value is handled.
- Duplicates: search still returns existence/first match; count counts each occurrence; filter/map preserve duplicate occurrences.
- All match / none match: test both conditions.
- `None`: decide explicitly whether to keep, skip, or search for it; numeric aggregates may raise `TypeError` if `None` is included.
- Zero: zero is a valid number, not the same as missing. Avoid `if record["count"]` if zero is valid.
- Negative values: ensure conditions do not accidentally exclude them.
- Missing dictionary keys: `record["field"]` can raise `KeyError`; `.get("field")` safely returns `None` or a chosen default.
- Malformed records: validate types/fields before comparing or aggregating.

Example of the zero trap:

```python
records = [{"count": 0}, {"count": 5}]
# Wrong if zero is valid:
nonzero_looking = [r for r in records if r["count"]]
# Explicit missing-value rule:
valid = [r for r in records if r["count"] is not None]
```

Example of missing keys:

```python
records = [{"amount": 100}, {"status": "ok"}]
# [r["amount"] for r in records]  # KeyError
safe_amounts = [r.get("amount", 0) for r in records]  # [100, 0]
```

## 14. Performance and Big-O

Let `n` be the number of items.

| Pattern | Typical time | Notes |
|---|---|---|
| Search list/tuple | `O(n)` worst case | May stop early; best case can be `O(1)` |
| Search set/dict membership | expected `O(1)` | Hash-based lookup |
| Count | `O(n)` | Must inspect all items |
| Filter | `O(n)` | Visits all items |
| Map | `O(n)` | Visits all items |
| Aggregate | `O(n)` | Visits all items |

`O(n)` means doubling the input roughly doubles the work. Built-ins can be faster in real execution because some are implemented in optimized code, but their Big-O complexity remains `O(n)` when they inspect every item.

Space:
- Filter into a list: up to `O(n)` extra space.
- Map into a list: `O(n)` extra space.
- Generator expression: approximately `O(1)` extra space for the generator, because it produces values one at a time.

```python
sum([n * 2 for n in numbers if n > 10])  # intermediate list
sum(n * 2 for n in numbers if n > 10)    # generator; no intermediate list
```

For repeated membership checks on large data, prefer a set if duplicates and ordering are not required.

## 15. Readability, debugging, and testing

Production priorities in this lesson: correctness, readability, maintainability, testability, then raw performance. A clear multi-line comprehension or loop is better than a clever nested expression.

Use:
- a plain loop for multiple steps, multiple changing variables, or complex branching;
- a comprehension for one clear expression and condition;
- a generator expression when another function immediately consumes the values.

Trace a wrong result:

```python
total = 0
for number in numbers:
    print(f"number={number}, total before={total}")
    if number > 20:
        total += number
    print(f"total after={total}")
```

Inspect current item, condition result, accumulator before/after, and result list. A debugger adds breakpoints and step-by-step state inspection. Check initialization, comparison (`>` vs `>=`, `==` vs `is`), placement of `break`/`return`, indentation/`append`, empty input, dictionary keys versus values, `None`, and zero.

Tests should cover normal, empty, all-match, no-match, duplicate, negative, and type-change cases:

```python
def test_search():
    assert 30 in [10, 20, 30]
    assert 99 not in [10, 20, 30]
    assert 10 in [10, 10, 20]
    assert 10 not in []

def test_count():
    assert sum(n > 100 for n in [1, 2, 3]) == 0
    assert sum(n > 1 for n in [1, 2, 3]) == 2
    assert sum(n > 0 for n in [1, 2, 3]) == 3
    assert sum(n > 0 for n in []) == 0

def test_filter():
    assert [n for n in [1, 2, 3] if n > 0] == [1, 2, 3]
    assert [n for n in [1, 2, 3] if n > 10] == []
    assert [n for n in [1, 2, 3] if n > 1] == [2, 3]
    assert [n for n in [] if n > 0] == []

def test_map():
    assert [n * 2 for n in [1, 2, 3]] == [2, 4, 6]
    assert [n * 2 for n in []] == []
    assert [str(n) for n in [1, 2]] == ["1", "2"]

def test_aggregate():
    assert sum([1, 2, 3]) == 6
    assert sum([5]) == 5
    assert sum([]) == 0
    assert sum([-1, -2, 3]) == 0
    assert sum([0, 0, 0]) == 0
    assert min([3, -1, 2]) == -1
    assert max([], default=None) is None

test_search()
test_count()
test_filter()
test_map()
test_aggregate()
print("All tests passed.")
```

Defining a test function does not execute it; direct calls above do. `pytest` can discover and run `test_...` functions automatically.

## 16. Pattern-recognition checklist and review

Ask in order:

1. Need to find/check existence? Search.
2. Need to know how many? Count.
3. Need to keep some items? Filter.
4. Need to change each item? Map.
5. Need to combine many into one result? Aggregate.

Common compositions: filter→map, filter→aggregate, filter→count, map→aggregate, search→transform, and filter→map→aggregate.

Final principles: iteration underlies all five patterns; compact tools correspond to familiar loop logic; composition is common in real engineering; check empty/missing/`None`/zero/duplicate cases; choose clarity over cleverness.

---

# Part B — Exercise solutions with line-by-line explanations

All 20 exercises below are solved using the techniques in this lesson. The explanation is deliberately concise to stay within the requested 2,000-word exercise section.

## Level 1 — Beginner

### 1.1 Search for 42

```python
numbers = [3, 12, 42, 7]
print(42 in numbers)  # True

found = False
for number in numbers:
    if number == 42:
        found = True
        break
print(found)  # True
```

- `in` directly checks exact membership.
- Manual version starts with “not found”.
- The loop checks each number; a match sets `found`.
- `break` stops after the match.

### 1.2 Count occurrences of 5

```python
numbers = [5, 3, 5, 5, 2]
print(numbers.count(5))  # 3
```

`.count(5)` counts every occurrence of the exact value `5`.

### 1.3 Keep even numbers

```python
numbers = [1, 2, 3, 4, 5, 6]
evens = [n for n in numbers if n % 2 == 0]
print(evens)  # [2, 4, 6]
```

The comprehension visits each `n`; `% 2 == 0` identifies even numbers; only matching values enter the new list.

### 1.4 Double every number

```python
numbers = [1, 2, 3]
doubled = [n * 2 for n in numbers]
print(doubled)  # [2, 4, 6]
```

Every input produces one output; there is no filter condition.

### 1.5 Calculate total

```python
numbers = [4, 8, 15, 16]
total = sum(numbers)
print(total)  # 43
```

`sum()` adds every value and returns one number.

## Level 2 — Intermediate

### 2.1 Count numbers above 50

```python
numbers = [10, 60, 55, 20, 90]
count = sum(n > 50 for n in numbers)
print(count)  # 3
```

Each comparison produces `True` or `False`; Python treats them as `1` or `0` when summed.

### 2.2 Filter active users

```python
users = [
    {"name": "A", "active": True},
    {"name": "B", "active": False},
]
active_users = [u for u in users if u["active"]]
print(active_users)  # [{'name': 'A', 'active': True}]
```

Each dictionary is checked; only records with a true `active` value are retained unchanged.

### 2.3 Extract user names

```python
names = [u["name"] for u in users]
print(names)  # ['A', 'B']
```

This maps every dictionary to its `name`; it does not filter inactive users.

### 2.4 Safe average

```python
numbers = [2, 4, 6, 8]
average = sum(numbers) / len(numbers) if numbers else 0
print(average)  # 5.0
```

`sum()` computes the total; `len()` computes item count; the conditional expression returns `0` for an empty list, avoiding division by zero.

### 2.5 First person younger than 18

```python
people = [{"name": "A", "age": 25}, {"name": "B", "age": 15}]
person = next((p for p in people if p["age"] < 18), None)
print(person)  # {'name': 'B', 'age': 15}
```

The generator yields only matching people; `next()` takes the first; `None` is returned if nobody matches.

## Level 3 — Records and dictionaries

Use the shared input:

```python
transactions = [
    {"id": "T1", "amount": 100, "status": "completed"},
    {"id": "T2", "amount": 200, "status": "failed"},
]
```

### 3.1 Keep completed transactions

```python
completed = [t for t in transactions if t["status"] == "completed"]
print(completed)
# [{'id': 'T1', 'amount': 100, 'status': 'completed'}]
```

Filter retains only records whose status matches exactly.

### 3.2 Count failed transactions

```python
failed_count = sum(t["status"] == "failed" for t in transactions)
print(failed_count)  # 1
```

Every comparison contributes `1` for a failed record and `0` otherwise.

### 3.3 Total completed amount

```python
total = sum(t["amount"] for t in transactions
            if t["status"] == "completed")
print(total)  # 100
```

The generator filters to completed records and supplies their amounts to `sum()`; no intermediate list is needed.

### 3.4 Extract all transaction IDs

```python
ids = [t["id"] for t in transactions]
print(ids)  # ['T1', 'T2']
```

Map extracts the `id` from every record regardless of status.

### 3.5 First transaction above 150

```python
large = next((t for t in transactions if t["amount"] > 150), None)
print(large)  # {'id': 'T2', 'amount': 200, 'status': 'failed'}
```

`next()` returns the first record whose amount exceeds `150`; `None` is the safe not-found default.

### 3.6 Count, total, minimum, maximum

```python
amounts = [t["amount"] for t in transactions]
count = len(amounts)
total = sum(amounts)
minimum = min(amounts) if amounts else None
maximum = max(amounts) if amounts else None
print((count, total, minimum, maximum))  # (2, 300, 100, 200)
```

- Mapping extracts amounts.
- `len` and `sum` calculate count and total.
- The conditional guards prevent `min`/`max` from raising `ValueError` on empty input.

## Level 4 — Production-oriented

### 4.1 Log severity frequency

```python
from collections import Counter

logs = ["INFO: ok", "ERROR: fail", "INFO: ok",
        "WARNING: slow", "ERROR: fail"]
levels = [line.split(":")[0] for line in logs]
frequency = Counter(levels)
print(frequency)
# Counter({'INFO': 2, 'ERROR': 2, 'WARNING': 1})
```

`split(":")` separates the severity prefix; `[0]` selects it; `Counter` tallies each distinct prefix.

### 4.2 Customer spend report

```python
customers = [{"spend": 500}, {"spend": 1500}, {"spend": 2000}]
spends = [c["spend"] for c in customers]
summary = {
    "total": len(customers),
    "high_spenders": sum(c["spend"] > 1000 for c in customers),
    "average_spend": sum(spends) / len(spends) if spends else 0,
}
print(summary)
# {'total': 3, 'high_spenders': 2, 'average_spend': 1333.3333333333333}
```

Extract spend values; count all customers; conditionally count spend above `1000`; calculate a guarded average; collect the results in a dictionary.

### 4.3 Data quality audit

```python
records = [{"email": "a@x.com"}, {"id": 2}, {"email": None}]
usable = sum(record.get("email") is not None for record in records)
print(usable)  # 1
```

`.get()` handles both a missing key and a key containing `None`; `is not None` counts only usable email values.

### 4.4 Text preprocessing pipeline

```python
examples = ["Great!", "   ", "Terrible.", ""]
cleaned = [text.lower() for text in examples if text.strip()]
average_length = (
    sum(len(text) for text in cleaned) / len(cleaned)
    if cleaned else 0
)
print(cleaned)          # ['great!', 'terrible.']
print(average_length)   # 7.5
```

`strip()` removes surrounding whitespace for the test; whitespace-only and empty strings are excluded. `lower()` normalizes retained text. The final expression computes average cleaned-string length and guards empty output.

---

# Part C — Mini Project: Transaction Analysis Engine

## Requirements translated into functions

```python
def find_transaction_by_id(transactions, target_id):
    return next((t for t in transactions if t["id"] == target_id), None)

def count_failed(transactions):
    return sum(t["status"] == "failed" for t in transactions)

def filter_completed(transactions):
    return [t for t in transactions if t["status"] == "completed"]

def completed_amounts(transactions):
    return [t["amount"] for t in filter_completed(transactions)]

def total_completed_amount(transactions):
    return sum(completed_amounts(transactions))

def average_completed_amount(transactions):
    amounts = completed_amounts(transactions)
    return sum(amounts) / len(amounts) if amounts else 0

def has_transaction_above(transactions, threshold):
    return any(t["amount"] > threshold for t in transactions)

def build_summary(transactions, target_id, threshold):
    return {
        "found_transaction": find_transaction_by_id(transactions, target_id),
        "failed_count": count_failed(transactions),
        "completed_count": len(filter_completed(transactions)),
        "total_completed_amount": total_completed_amount(transactions),
        "average_completed_amount": average_completed_amount(transactions),
        "has_large_transaction": has_transaction_above(transactions, threshold),
    }
```

### Function-by-function explanation

1. `find_transaction_by_id`: generator checks IDs; `next` returns the first match; `None` handles an unknown ID.
2. `count_failed`: boolean comparisons are summed, so every failed record adds one.
3. `filter_completed`: creates a new list containing completed records only.
4. `completed_amounts`: reuses the filter function, then extracts each completed record's amount.
5. `total_completed_amount`: sums the extracted amounts; empty input safely totals zero.
6. `average_completed_amount`: calculates the mean; returns zero if there are no completed amounts, avoiding division by zero.
7. `has_transaction_above`: `any` returns as soon as an amount exceeds the threshold.
8. `build_summary`: combines the function results into one report dictionary.

### Run the project

```python
transactions = [
    {"id": "T1", "amount": 100, "status": "completed"},
    {"id": "T2", "amount": 250, "status": "failed"},
    {"id": "T3", "amount": 400, "status": "completed"},
]

print(find_transaction_by_id(transactions, "T2"))
# {'id': 'T2', 'amount': 250, 'status': 'failed'}

print(build_summary(transactions, target_id="T2", threshold=300))
# {
#   'found_transaction': {'id': 'T2', 'amount': 250, 'status': 'failed'},
#   'failed_count': 1,
#   'completed_count': 2,
#   'total_completed_amount': 500,
#   'average_completed_amount': 250.0,
#   'has_large_transaction': True
# }
```

The summary reports two completed transactions with total `500` and average `250.0`; one failed transaction; T2 is found; and T3 exceeds the threshold of `300`.

**Project assumptions to verify in a real application:** each record has `id`, `amount`, and `status`; statuses use the exact values `"completed"`/`"failed"`; amounts are numeric. The lesson asks you to think about whether amounts can be negative and whether the list can be empty. The functions above handle an empty list, but they do not validate malformed records or unexpected statuses; validation is outside this lesson's exercise scope.

---

# Part D — Interview questions and short answer guide

1. **Search vs filter:** search answers existence/first match; filter returns every matching item.
2. **Map vs filter:** map transforms each input; filter selects a subset unchanged.
3. **Accumulator:** running result initialized before iteration so each pass can update it.
4. **`any()` on empty:** `False`.
5. **`all()` on empty:** `True`; there is no counterexample.
6. **`next()`:** retrieves the next generated item; a default prevents `StopIteration` when no match exists.
7. **Why map returns an iterator:** lazy evaluation avoids building all outputs immediately.
8. **Why generators save memory:** values are produced one at a time instead of stored in an intermediate list.
9. **Unsorted list search:** worst-case `O(n)`; an early match can stop sooner.
10. **Set membership:** expected `O(1)` hashing versus `O(n)` sequential list search.
11. **When loop beats comprehension:** multi-step logic, branching, or several changing variables.
12. **Why sum over reduce:** `sum()` states intent directly and is easier to read.
13. **`min([])`:** raises `ValueError`; use `default=` or guard the empty input.
14. **`.count(value)` vs condition count:** exact-value frequency versus arbitrary predicate count.
15. **Dictionary `in`:** checks keys, not values.
16. **10 million IDs:** use a set for repeated membership checks when uniqueness/order are not required.
17. **First expired subscription:** manual loop + `break` or `next(generator, default)`; choose the clearer form.
18. **List before sum in a hot loop:** replace `sum([ ... ])` with `sum(... for ...)` to avoid an intermediate list.
19. **Count missing fields without a new list:** `sum(record.get("field") is None for record in records)`.
20. **Safe average:** check the collection before dividing by `len`; otherwise empty input divides by zero.
21. **Nested comprehension review:** split into named steps if a reader cannot quickly understand it.
22. **Lazy map/filter:** they return iterators; wrap with `list()` when a concrete reusable list is required.

---

# Part E — Current curriculum alignment and learning-level assessment

The supplied Stage 1 project tree places this lesson at:

`04-Problem-Solving-Collections-and-Algorithmic-Habits/01-search-count-filter-map-and-aggregate.md`

Its prerequisites are the earlier Stage 1 topics: variables and expressions, conditions, `for` loops, functions, lists, dictionaries, sets, and basic collection operations. The lesson then introduces list/generator comprehensions, `any`, `all`, `next`, `map`, `filter`, `Counter`, aggregation functions, and introductory Big-O reasoning.

The project tree includes later modules for files/CSV/JSON/CLI, packages, testing, OOP, production Python, and advanced topics. Those later topics should not be assumed as prerequisites for this lesson. The user's recent learning context includes Python string and set methods, while the supplied project tree identifies this chapter as Module 04. Therefore, this solution stays with loops, conditions, lists, dictionaries, functions, comprehensions, built-ins, and the standard-library `Counter`/`statistics`/`math` tools explicitly covered by the lesson.

**Progress checkpoint:** Before moving to the next lesson, be able to explain the difference between search/count/filter/map/aggregate, solve one example of each with a loop, then express it with the appropriate Python tool, and correctly handle empty collections and missing dictionary keys.

---

# Source accuracy notes

- The lesson's AI/ML example states that `"great product"` and `"terrible service"` have an average length of `14.5`. Counting the literal characters gives 13 and 15, hence `14.0`. The summary flags this arithmetic discrepancy rather than repeating it as correct.
- The source's `map()`/`filter()` iterator behaviour is retained: convert to `list()` when a list is specifically required.
- The mini-project implementation follows the source answer key; it does not add validation or advanced architecture that the lesson has not taught.
