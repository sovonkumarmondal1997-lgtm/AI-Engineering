# Grouping, Deduplication, and Sorting

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Recognize when a problem is a **grouping**, **deduplication**, or
  **sorting** problem, and identify the grouping key, the identity used
  to define a duplicate, and the sort key before writing any code.
- Group data manually with a plain dictionary, then move to
  `dict.setdefault()` and `collections.defaultdict` once you understand
  what they save you from writing.
- Deduplicate values and records correctly — including choosing between
  "first write wins" and "last write wins" — and preserve order when it
  matters.
- Sort data with `sorted()` and `list.sort()`, understand exactly how
  they differ, and use `key=` functions (including multi-key sorting)
  confidently.
- Combine grouping, deduplication, sorting, and the five patterns from
  the previous chapter (search, count, filter, map, aggregate) into
  realistic data-processing pipelines.
- Reason about the time and space cost of each pattern, and know why
  sorting is fundamentally more expensive than a single pass over data.
- Recognize and avoid the classic bugs in each pattern, and debug them
  systematically when they occur.

## 2. Why These Patterns Matter

Consider one small dataset:

```python
transactions = [
    {"customer": "A", "amount": 100},
    {"customer": "B", "amount": 250},
    {"customer": "A", "amount": 300},
    {"customer": "C", "amount": 150},
    {"customer": "B", "amount": 50},
]
```

Now consider the questions someone might ask about it:

- *How much did each customer spend?*
- *Which customers exist, without repeats?*
- *How can duplicate customer records be removed?*
- *How can transactions be ordered from highest to lowest amount?*
- *How can transactions be organized by customer?*

The previous chapter,
[Search, Count, Filter, Map, and Aggregate](01-search-count-filter-map-and-aggregate.md),
gave you five patterns for asking questions about a flat collection. But
none of those five naturally answer "how much did *each* customer
spend" — that question needs the data organized *by customer* first.
This chapter introduces the three patterns that organize data before (or
after) those five patterns are applied:

- **GROUPING** — *"Put related items together."* Every transaction
  belongs to exactly one customer; grouping collects all of one
  customer's transactions so they can be examined together.
- **DEDUPLICATION** — *"Keep only the unique items, according to some
  definition of identity."* If the same transaction ID appears twice
  (say, because a system retried a request), you need one copy, not two.
- **SORTING** — *"Put items into a defined order."* A report of
  customers is far more useful ranked from highest spender to lowest
  than in whatever order they happened to appear in the raw data.

These three appear everywhere real data is processed: databases group
rows with `GROUP BY`; data engineers deduplicate records ingested from
unreliable sources; backend APIs sort search results; log processors
group errors by service; ML pipelines deduplicate training examples
before deduplicated, duplicate examples silently bias a model. Learn
these three patterns in plain Python first, and every one of those
systems will make more sense, because they are all doing the same thing
this chapter teaches — just at a larger scale.

## 3. Grouping Fundamentals

### 3.1 What does it mean to group items?

Start as simply as possible:

```python
names = ["Alice", "Bob", "Alice", "Charlie", "Bob"]
```

If you were asked "which names are the same," you would naturally start
collecting matching names together in your head: *Alice, Alice* together;
*Bob, Bob* together; *Charlie* alone. That mental sorting-into-piles is
exactly what grouping is: **taking a flat collection and reorganizing it
so that items sharing something in common end up together.**

### 3.2 Grouping by category

```python
records = [
    ("sales", 100),
    ("support", 200),
    ("sales", 150),
    ("support", 50),
]
```

The intended, conceptual result:

```
sales   → [100, 150]
support → [200, 50]
```

Every record is a `(category, amount)` pair. Grouping needs four
ingredients:

| Term | Meaning in this example |
|---|---|
| **Group key** | The value that decides which group an item belongs to — here, `"sales"` or `"support"`. |
| **Group value** | What actually gets stored for each item once it is placed in a group — here, the `amount`. |
| **Group membership** | The rule connecting an item to its group — here, "the first element of the tuple." |
| **Group container** | The overall structure holding every group — here, something mapping each category to its list of amounts. |
| **Accumulator** | The per-group collection that grows as more matching items are found — here, each category's list. |

A dictionary is the natural group container in Python: its keys are the
group keys, and its values are the per-group accumulators.

## 4. Manual Grouping with Dictionaries

### 4.1 The fundamental algorithm

```python
records = [
    ("sales", 100),
    ("support", 200),
    ("sales", 150),
    ("support", 50),
]

groups = {}

for category, amount in records:
    if category not in groups:
        groups[category] = []

    groups[category].append(amount)

print(groups)
# {'sales': [100, 150], 'support': [200, 50]}
```

Line by line:

- `groups = {}` — start with an empty group container; nothing has been
  organized yet.
- `for category, amount in records:` — this loop **unpacks** each tuple
  directly into two named variables as it iterates, which is why the
  loop variable is written as `category, amount` instead of a single
  name.
- `if category not in groups:` — checks membership on the dictionary's
  *keys* (recall §4.7 of the previous chapter) to see whether this group
  has been started yet.
- `groups[category] = []` — the first time a category is seen, its
  accumulator (an empty list) must be created before anything can be
  appended to it.
- `groups[category].append(amount)` — every time, matching or not, the
  current amount is appended to its category's list.

### 4.2 Tracing execution

| iteration | current record | group key | `groups` **before** | `groups` **after** |
|---|---|---|---|---|
| 1 | `("sales", 100)` | `"sales"` | `{}` | `{"sales": [100]}` |
| 2 | `("support", 200)` | `"support"` | `{"sales": [100]}` | `{"sales": [100], "support": [200]}` |
| 3 | `("sales", 150)` | `"sales"` | `{"sales": [100], "support": [200]}` | `{"sales": [100, 150], "support": [200]}` |
| 4 | `("support", 50)` | `"support"` | `{"sales": [100, 150], "support": [200]}` | `{"sales": [100, 150], "support": [200, 50]}` |

Notice the key line of the algorithm is really answering one question
every iteration: *"has this key been seen before? If not, prepare a
place for it; either way, add the current value to it."* That question-
and-answer shape is the heart of grouping, and every tool in the next
two sections is just a shorter way of writing exactly that.

### 4.3 Why a dictionary?

A dictionary lets you go directly from a group key to that group's
accumulator without scanning anything — the same O(1) average-case
lookup behavior discussed for set membership in the previous chapter
(§17 there). A list of `(key, [values])` pairs could technically hold
the same information, but finding the right group would mean scanning
the whole list every time — turning an O(n) grouping pass into an O(n²)
one. The dictionary is not just convenient; it is what keeps grouping
efficient.

## 5. `setdefault()`

### 5.1 What it does

The `if category not in groups: groups[category] = []` step in §4.1 is
so common that dictionaries provide a shortcut for it:

```python
groups = {}

for category, amount in records:
    groups.setdefault(category, []).append(amount)

print(groups)
# {'sales': [100, 150], 'support': [200, 50]}
```

`dict.setdefault(key, default)` means: *"if `key` is already in the
dictionary, return its current value; otherwise, set it to `default`
first, and then return that."* Either way, it **returns the value now
associated with `key`** — which is why `.append(amount)` can be chained
directly onto it.

### 5.2 Why it can be convenient — and why it can also be confusing

`setdefault()` collapses a two-line check into one line, which is
genuinely useful once you are comfortable with it. But it also hides
what is happening: readers unfamiliar with `setdefault()` have to know
its exact contract (creates the key if missing, *and* returns the
resulting value) to understand the line at all. Beginners often find the
explicit `if key not in groups: groups[key] = []` version from §4.1
easier to reason about, precisely because every step is visible. Neither
version is "wrong" — `setdefault()` is not automatically better just
because it is shorter; it is better only once its behavior is second
nature to you and to whoever reads your code next.

| | Explicit `if` (§4.1) | `setdefault()` (§5.1) |
|---|---|---|
| Lines needed | 2 (check + create) + 1 (append) | 1 |
| Readability for beginners | Every step visible | Requires knowing `setdefault`'s contract |
| Behavior | Identical | Identical |

## 6. `defaultdict`

### 6.1 What it is and why it exists

`collections.defaultdict` solves the exact same problem as
`setdefault()`, but by changing the dictionary itself rather than
changing how you call it:

```python
from collections import defaultdict

groups = defaultdict(list)

for category, amount in records:
    groups[category].append(amount)

print(groups)
# defaultdict(<class 'list'>, {'sales': [100, 150], 'support': [200, 50]})
print(dict(groups))
# {'sales': [100, 150], 'support': [200, 50]}
```

`defaultdict(list)` takes a **default factory** — here, the built-in
`list` function itself, not a list. Whenever you access a key that does
not exist yet, the `defaultdict` calls that factory (`list()`, producing
`[]`) automatically, stores the result under that key, and gives it back
to you — all before your `.append()` even runs. This is why the loop
body needs no `if` and no `setdefault()`: `groups[category]` simply
*cannot* raise a `KeyError` or come back empty-but-uninitialized; a
`defaultdict` guarantees every key you touch already has a value the
first time you touch it.

### 6.2 `dict` vs. `defaultdict`

```python
plain = {}
plain["missing"]           # KeyError!

from collections import defaultdict
safe = defaultdict(list)
safe["missing"]             # [] — created automatically, no error
```

A `defaultdict` behaves exactly like a normal `dict` in every other way
(iteration, `.items()`, `.keys()`, `.values()`, membership with `in`) —
the *only* difference is what happens when you access a key that is not
there yet.

### 6.3 `defaultdict(int)` for counting

The factory does not have to be `list`. Passing `int` gives every new
key a starting value of `0` (because `int()` with no arguments returns
`0`), which is exactly what a running count needs:

```python
from collections import defaultdict

words = ["cat", "dog", "cat", "bird", "cat"]
counts = defaultdict(int)

for word in words:
    counts[word] += 1

print(dict(counts))   # {'cat': 3, 'dog': 1, 'bird': 1}
```

This should look familiar: it is the manual grouping algorithm from
§4.1, with `.append(amount)` replaced by `+= 1`. **Grouping and
counting are close relatives** — counting-by-category is grouping where
the accumulator is a running number instead of a growing list. (For
frequency counting specifically, recall that `collections.Counter` from
the previous chapter's §5.6 is a purpose-built alternative to this exact
pattern — `Counter(words)` and the loop above produce the same result.)

### 6.4 Choosing the factory

| Factory | New key starts as | Used for |
|---|---|---|
| `list` | `[]` | collecting every matching item |
| `int` | `0` | running counts or sums per group |
| `set` | `set()` | collecting unique matching items per group |

## 7. Grouping and Aggregation

### 7.1 Why grouping usually exists in the first place

In practice, nobody groups data just to look at the groups — grouping
almost always exists so an **aggregation** (§8 of the previous chapter)
can be computed *per group*. "How much did each customer spend" is a
grouped aggregation: group the transactions by customer, then sum each
group's amounts.

```python
transactions = [
    {"customer": "A", "amount": 100},
    {"customer": "B", "amount": 250},
    {"customer": "A", "amount": 300},
    {"customer": "B", "amount": 50},
]
```

Goal:

```
A → 400
B → 300
```

### 7.2 Manual accumulator approach

```python
totals = {}

for transaction in transactions:
    customer = transaction["customer"]
    amount = transaction["amount"]

    if customer not in totals:
        totals[customer] = 0

    totals[customer] += amount

print(totals)   # {'A': 400, 'B': 300}
```

This is structurally identical to the plain aggregation loop from the
previous chapter's §8.2 (`total = 0; total += number`), except there is
now one running total *per customer* instead of one total overall. The
`if customer not in totals: totals[customer] = 0` line establishes each
customer's identity element (`0`, the correct starting point for a sum —
see the previous chapter's §8.6 on identity values) the first time that
customer is seen.

### 7.3 The same thing with `defaultdict(int)`

```python
from collections import defaultdict

totals = defaultdict(int)

for transaction in transactions:
    totals[transaction["customer"]] += transaction["amount"]

print(dict(totals))   # {'A': 400, 'B': 300}
```

One line inside the loop, because `defaultdict(int)` handles the "has
this customer been seen before" question automatically.

### 7.4 Why this pattern matters so much

"Group by X, then sum/count/average Y" is arguably the single most
common data-processing operation in industry — it is the operation
behind almost every dashboard metric, financial report, and analytics
query:

- **Analytics** — revenue per product, sessions per user, errors per
  service.
- **ETL** — rolling up raw event data into daily/customer/region
  summaries before loading it into a warehouse.
- **Banking** — total spend per account, per merchant category, per
  month.
- **Log processing** — error count per service, per severity level.
- **Metrics/reporting** — any "per X" number in a report.
- **ML feature preparation** — aggregating raw event logs into
  per-user or per-session features (e.g., "number of purchases in the
  last 30 days per customer") before training a model.

## 8. Different Grouping Structures

The accumulator you choose per group changes what the grouped result
*means* — not just its type:

```python
from collections import defaultdict

records = [
    ("A", 10), ("A", 20), ("B", 30), ("A", 10),
]

# Group values into LISTS — keeps every value, including duplicates:
as_lists = defaultdict(list)
for key, value in records:
    as_lists[key].append(value)
# {'A': [10, 20, 10], 'B': [30]}

# Count items per group:
as_counts = defaultdict(int)
for key, value in records:
    as_counts[key] += 1
# {'A': 3, 'B': 1}

# Sum values per group:
as_sums = defaultdict(int)
for key, value in records:
    as_sums[key] += value
# {'A': 40, 'B': 30}

# Group UNIQUE values per group — duplicates within a group collapse:
as_unique = defaultdict(set)
for key, value in records:
    as_unique[key].add(value)
# {'A': {10, 20}, 'B': {30}}

# Minimum / maximum per group requires a small comparison inside the loop:
minimums = {}
for key, value in records:
    if key not in minimums or value < minimums[key]:
        minimums[key] = value
# {'A': 10, 'B': 30}
```

Notice `as_lists["A"]` has three entries (`10` appears twice) while
`as_unique["A"]` has only two (`{10, 20}`) — the *same* grouping key,
producing different results, purely because of the accumulator's type.
Always ask explicitly: *do I want every matching value, or only the
distinct ones, or just a running number?*

## 9. Dictionary Comprehensions and Grouping

A dictionary comprehension (`{key: value for ...}`, introduced briefly
in the previous chapter's §12) can build a dictionary in one expression,
but it is a poor fit for grouping in its most literal form, because a
comprehension has no natural way to say "append to whatever is already
there" — each key can only be assigned once per comprehension pass.

```python
# This does NOT group correctly — later duplicate keys simply
# overwrite earlier ones, silently discarding data:
records = [("sales", 100), ("support", 200), ("sales", 150)]
broken = {category: amount for category, amount in records}
print(broken)   # {'sales': 150, 'support': 200}  — the first sales record vanished!
```

Comprehensions are, however, a good fit for the simpler, *non-
accumulating* transformations that often sit next to grouping — for
example, turning an already-grouped dictionary into a summary:

```python
totals = {"A": 400, "B": 300}
labeled = {customer: f"${amount}" for customer, amount in totals.items()}
# {'A': '$400', 'B': '$300'}
```

**Emphasize readable code over clever code here:** do not force a
grouping operation into a dictionary comprehension just because a
comprehension exists — §4's explicit loop, `setdefault()`, or
`defaultdict` are the right tools for genuine accumulation. Reach for a
comprehension only once grouping is already done and you are reshaping
the result.

## 10. `itertools.groupby`

### 10.1 A different kind of grouping

`itertools.groupby` groups **consecutive** equal keys in an iterable —
it is not the same operation as the dictionary-based grouping above, and
confusing the two is a common and consequential mistake.

```python
from itertools import groupby

records = [
    ("A", 10),
    ("A", 20),
    ("B", 30),
    ("B", 40),
]

for key, group in groupby(records, key=lambda record: record[0]):
    print(key, list(group))
```

```text
A [('A', 10), ('A', 20)]
B [('B', 30), ('B', 40)]
```

- `key=lambda record: record[0]` is the **key function** — it tells
  `groupby` what to compare between consecutive items, exactly the same
  idea as the `key=` functions used for sorting later in this chapter
  (§21).
- `group` is itself an **iterator** over the items sharing that key —
  which is why it must be wrapped in `list(...)` to print or reuse it,
  the same lazy-iterator behavior as `map()` and `filter()` from the
  previous chapter (§7.4, §6.6).
- Critically, `groupby` only ever compares an item to the *one right
  before it*. The moment the key changes, it closes the current group —
  even if that same key appears again later.

### 10.2 The critical requirement: sort first

```python
unsorted_records = [
    ("A", 10),
    ("B", 30),
    ("A", 20),   # "A" reappears after "B" — groupby will NOT merge it back!
]

for key, group in groupby(unsorted_records, key=lambda r: r[0]):
    print(key, list(group))
```

```text
A [('A', 10)]
B [('B', 30)]
A [('A', 20)]
```

Three groups came out, not two — `"A"` was split into two separate
groups because the second `"A"` record was not adjacent to the first.
**This is the single most important thing to know about `groupby`:** it
has no memory of keys it has already seen; it only notices when the
*current* key differs from the *previous* key. To get one group per
distinct key (the SQL `GROUP BY`-style result most people actually
want), the data must be sorted by the grouping key first:

```python
sorted_records = sorted(unsorted_records, key=lambda r: r[0])
for key, group in groupby(sorted_records, key=lambda r: r[0]):
    print(key, list(group))
```

```text
A [('A', 10), ('A', 20)]
B [('B', 30)]
```

### 10.3 Dictionary grouping vs. `groupby`

| | Dictionary / `defaultdict` grouping | `itertools.groupby` |
|---|---|---|
| Order requirement | none — works on data in any order | data must be pre-sorted by the grouping key |
| Result shape | one dictionary, all groups available at once | a one-pass iterator; groups are consumed as you go |
| Ease of understanding | very direct: "look up this key" | more subtle: "consecutive matching keys only" |
| Typical use | general-purpose grouping — the default choice | large sorted or streaming data, where building a full dictionary is undesirable |

**For most everyday grouping, prefer `defaultdict`** — it is simpler,
does not require sorting first, and does not carry `groupby`'s
"consecutive only" surprise. Reach for `groupby` when you are already
working with sorted or streaming data and want to avoid holding an
entire grouped dictionary in memory at once.

## 11. Deduplication Fundamentals

### 11.1 What does "duplicate" mean?

```python
numbers = [1, 2, 2, 3, 3, 3, 4]
```

Here, "duplicate" seems obvious — `2` and `3` each repeat. But
deduplication is not always this simple, because it requires deciding,
explicitly, **what makes two items "the same."** This decision is called
defining the item's **identity**. For plain numbers or strings, identity
is just the value itself. For records, identity is usually a specific
field, or a combination of fields:

| Deduplicate by... | Example |
|---|---|
| entire value | two identical numbers, strings, or tuples |
| an ID | two user records with the same `"id"` |
| an email | two signups with the same email address, even if names differ |
| a customer ID | two orders placed under the same customer |
| a transaction ID | two log entries recording the same transaction, possibly with different timestamps |
| a combination of fields | two events with the same `(customer_id, date)` pair |

This is one of the most important engineering judgment calls in this
chapter: **choosing the wrong identity silently produces the wrong
result**, either by discarding records that were not truly duplicates,
or by keeping records that were.

## 12. Deduplication with `set()`

### 12.1 The basic tool

```python
numbers = [1, 2, 2, 3, 3, 3, 4]
unique = set(numbers)
print(unique)   # {1, 2, 3, 4}
```

A **set** is a collection that, by definition, cannot contain duplicate
values — attempting to add a value already present simply has no
effect. Converting a list to a set is therefore an immediate way to
discard duplicates, relying on the same hashing-based membership
mechanism discussed for fast `in` checks in the previous chapter's §17.

### 12.2 The critical limitation: no preserved order

```python
numbers = [3, 1, 2, 3, 1]
print(set(numbers))   # e.g. {1, 2, 3} — NOT necessarily in the original order
```

Sets do not preserve insertion order as a general guarantee — **do not
treat `set(...)` as any kind of ordering operation.** If you need the
unique values in their original order of first appearance, `set()` alone
is the wrong tool; you need §13's order-preserving approach instead. If
you need them in a specific *sorted* order, wrap the result with
`sorted()` (§26), which is an entirely separate step, not something
`set()` provides.

## 13. Order-Preserving Deduplication

### 13.1 The "seen set" pattern

```python
items = [3, 1, 2, 3, 1, 4]

seen = set()
result = []

for item in items:
    if item not in seen:
        seen.add(item)
        result.append(item)

print(result)   # [3, 1, 2, 4]
```

Trace it:

| iteration | item | `item not in seen`? | `seen` after | `result` after |
|---|---|---|---|---|
| 1 | 3 | True | `{3}` | `[3]` |
| 2 | 1 | True | `{3, 1}` | `[3, 1]` |
| 3 | 2 | True | `{3, 1, 2}` | `[3, 1, 2]` |
| 4 | 3 | False | `{3, 1, 2}` | `[3, 1, 2]` (unchanged) |
| 5 | 1 | False | `{3, 1, 2}` | `[3, 1, 2]` (unchanged) |
| 6 | 4 | True | `{3, 1, 2, 4}` | `[3, 1, 2, 4]` |

`seen` exists purely to answer "have I already kept one of these?" in
O(1) average time; `result` is the actual output, built in the original
order the unique values first appeared. This two-container idea — a set
for fast membership checks, a list for the ordered output — is an
important, reusable algorithmic pattern well beyond deduplication.

### 13.2 `list(dict.fromkeys(items))`

Modern Python dictionaries preserve **insertion order** as a language
guarantee (since Python 3.7), and `dict.fromkeys(items)` builds a
dictionary using each item in `items` as a key (discarding duplicate
keys automatically, exactly as any dictionary would), while remembering
the order those keys were first inserted:

```python
items = [3, 1, 2, 3, 1, 4]
unique_in_order = list(dict.fromkeys(items))
print(unique_in_order)   # [3, 1, 2, 4]
```

This produces the exact same result as the seen-set loop in §13.1, in
one line, because a dictionary already *is* essentially a built-in
"seen set with order" — this line only works because each item is
**hashable** (usable as a dictionary key), the same requirement covered
next in §14.

### 13.3 Comparing the three deduplication approaches

| Approach | Preserves order? | Readability | When to use |
|---|---|---|---|
| `set(items)` | No | Very simple | Order genuinely does not matter |
| `list(dict.fromkeys(items))` | Yes | Compact, but requires knowing the idiom | Order matters, values are simple and hashable |
| Manual seen-set loop (§13.1) | Yes | Most explicit, easiest to extend | Order matters *and* you need extra logic per item (e.g., logging discarded duplicates, or the record case in §14) |

## 14. Deduplicating Records

### 14.1 Why `set(list_of_dicts)` does not work

```python
users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
set(users)   # TypeError: unhashable type: 'dict'
```

Dictionaries (and lists) are **mutable**, and Python does not allow
mutable objects to be used as set elements or dictionary keys, because
their contents — and therefore their identity for hashing purposes —
could change after being added. Only **hashable** values (numbers,
strings, tuples of hashable values, frozensets) can go in a set or serve
as a dictionary key. This is exactly why `dict.fromkeys()` from §13.2
only worked for plain numbers — it would fail the same way on a list of
dictionaries.

### 14.2 The correct strategy: deduplicate by a chosen field

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

print(unique_users)
# [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
```

This is exactly the seen-set pattern from §13.1, except `seen_ids`
tracks the *hashable identity field* (`user["id"]`, an `int`) rather
than the unhashable dictionary itself. Notice the result kept the
**first** record for `id=1` ("Alice") and discarded the second ("Alice
Updated") — this is **first-write-wins** behavior, because the `if ...
not in seen_ids` check only lets the earliest match through.

### 14.3 Last-write-wins

Sometimes the most recent record should win instead — for example, when
later records represent corrections or updates:

```python
users_by_id = {}

for user in users:
    users_by_id[user["id"]] = user

unique_users = list(users_by_id.values())
print(unique_users)
# [{'id': 1, 'name': 'Alice Updated'}, {'id': 2, 'name': 'Bob'}]
```

Because dictionary assignment (`users_by_id[user["id"]] = user`) simply
overwrites whatever was previously stored under that key, the *last*
record processed for a given ID is the one that survives. `id=1` now
holds "Alice Updated," not "Alice" — the opposite outcome from §14.2,
using the same input data.

### 14.4 First-write-wins vs. last-write-wins: choose deliberately

| | First-write-wins (§14.2) | Last-write-wins (§14.3) |
|---|---|---|
| Keeps | the earliest record seen | the most recent record seen |
| Appropriate when | earlier records are authoritative (e.g., original signup data) | later records are corrections/updates (e.g., a "latest known state" table) |
| Risk if chosen wrongly | silently keeps stale data | silently discards the original, possibly meaningful, record |

**This choice is a business decision, not a technical one** — the code
for each is almost identical, but choosing the wrong rule for the
situation can silently discard important information (an original
signup timestamp, an initial fraud flag, etc.). Always confirm which
rule is intended before deduplicating real records.

## 15. Composite-Key Deduplication

### 15.1 When one field is not enough

Sometimes uniqueness is defined by a *combination* of fields rather than
a single one — for example, "one transaction per customer per day" would
use `(customer_id, date)` as the identity, even if individual
`customer_id` or `date` values repeat on their own.

```python
records = [
    {"customer_id": "C1", "date": "2026-01-01", "amount": 50},
    {"customer_id": "C1", "date": "2026-01-01", "amount": 999},  # same customer+date — duplicate
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

print(unique_records)
# [{'customer_id': 'C1', 'date': '2026-01-01', 'amount': 50},
#  {'customer_id': 'C1', 'date': '2026-01-02', 'amount': 75},
#  {'customer_id': 'C2', 'date': '2026-01-01', 'amount': 20}]
```

A **tuple** is used as the composite key because tuples of hashable
values are themselves hashable, and therefore usable in a set — exactly
the same requirement from §14.1. This pattern — build a tuple key,
check/add it in a seen-set — extends the single-field pattern from §14.2
to any number of fields, and is a core technique in real-world data
engineering, where "uniqueness" is very often a compound business rule
rather than a single ID column.

## 16. Sorting Fundamentals

### 16.1 What does sorting mean?

```python
numbers = [5, 2, 9, 1, 3]
```

Sorting means **rearranging items into a defined order**, based on
repeatedly comparing pairs of items (*is this one smaller, larger, or
equal to that one?*) and placing them accordingly. You do not need to
hand-write a sorting algorithm to use sorting effectively — Python's
built-in sorting is highly optimized (§35 discusses this briefly) — but
it helps to know, conceptually, that sorting is fundamentally about
**comparison** and **rearrangement**, because that is exactly what a
`key=` function (§21) will let you control.

## 17. `sorted()`

```python
numbers = [5, 2, 9, 1]
sorted_numbers = sorted(numbers)

print(numbers)          # [5, 2, 9, 1]  — UNCHANGED
print(sorted_numbers)   # [1, 2, 5, 9]  — a brand-new list
```

`sorted(iterable)` **returns a new list** in sorted order and leaves its
input completely untouched. It accepts any iterable, not just
lists — you can pass a tuple, a set, a dictionary's keys, or a
generator expression, and always get back a sorted list.

## 18. `list.sort()`

```python
numbers = [5, 2, 9, 1]
result = numbers.sort()

print(numbers)   # [1, 2, 5, 9]  — the ORIGINAL list is now sorted, in place
print(result)    # None
```

`.sort()` is a **method that exists only on lists**. It sorts the list
**in place** — mutating the original — and its return value is always
`None`.

### 18.1 A very common bug

```python
numbers = [5, 2, 9, 1]
numbers = numbers.sort()   # BUG!
print(numbers)              # None
```

Because `.sort()` returns `None`, reassigning its result back onto the
variable destroys the sorted list, replacing it with `None`. This is one
of the single most common beginner mistakes with sorting — the fix is to
either call `.sort()` on its own line (no assignment) or use `sorted()`
if a new variable is genuinely wanted.

### 18.2 `sorted()` vs. `list.sort()`

| Feature | `sorted()` | `list.sort()` |
|---|---|---|
| Return value | a new, sorted list | `None` |
| Mutates original? | No | Yes, in place |
| Works on | any iterable | lists only |
| Typical use | when the original order must be preserved, or the input is not already a list | when the original list does not need to be kept, and in-place sorting saves memory |
| Memory | allocates a new list | no extra list allocated (sorts existing storage) |

## 19. Ascending and Descending Order

```python
numbers = [5, 2, 9, 1]

sorted(numbers)                 # [1, 2, 5, 9]   — ascending (default)
sorted(numbers, reverse=True)   # [9, 5, 2, 1]   — descending

numbers.sort(reverse=True)      # sorts numbers in place, descending
```

`reverse=True` tells the sort itself to arrange items from largest to
smallest — it does **not** sort ascending and then flip the list
afterward, even though the result often looks the same for simple cases.
This distinction matters once a `key=` function or duplicate keys are
involved: `reverse=True` and Python's stable sort (§24) interact in a
well-defined way, whereas sorting ascending and then reversing the whole
list afterward can silently change the relative order of items that
compare equal.

**`sorted(..., reverse=True)` is not the same operation as
`reversed(...)`:**

```python
numbers = [5, 2, 9, 1]

sorted(numbers, reverse=True)   # [9, 5, 2, 1] — sorted descending
list(reversed(numbers))          # [1, 9, 2, 5] — original order, simply flipped end-to-end
```

`reversed()` does not compare or reorder values by size at all — it just
walks the existing sequence back-to-front. Use `reversed()` only when
you want the literal existing order flipped; use `sorted(...,
reverse=True)` when you want the largest values first.

## 20. Sorting Strings

```python
names = ["Charlie", "Alice", "Bob"]
print(sorted(names))   # ['Alice', 'Bob', 'Charlie']
```

Strings sort **lexicographically** — character by character, using each
character's underlying code point, which for ordinary letters matches
alphabetical order. This has one sharp edge:

```python
names = ["charlie", "Alice", "bob"]
print(sorted(names))   # ['Alice', 'bob', 'charlie']
```

All uppercase letters have lower code points than all lowercase letters
in Python's default ordering, so `"Alice"` (capital A) sorts before
`"bob"` and `"charlie"` regardless of alphabetical intuition — this is
**case-sensitive** sorting, and it very often is not what you actually
want.

### 20.1 `key=str.lower`

```python
names = ["charlie", "Alice", "bob"]
print(sorted(names, key=str.lower))   # ['Alice', 'bob', 'charlie']
```

`key=str.lower` tells `sorted()`: *"before comparing two items, apply
`str.lower` to each of them, and compare those results instead."*
Crucially, the **original strings are not changed** — only the
comparison uses the lowercased version; the output still contains
`"Alice"` with its original capitalization, correctly positioned. This
is the first and simplest example of a **key function**, covered fully
next.

## 21. Key Functions

### 21.1 The concept

```python
sorted(items, key=function)
```

Conceptually: *"Use this function to compute the value to compare, for
every item, instead of comparing the items themselves."* This is what
makes sorting complex data (not just plain numbers or strings) possible
at all — there is no single obvious way to compare two whole
dictionaries, so you must tell `sorted()` exactly what to look at.

```python
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 20},
    {"name": "Charlie", "age": 25},
]

sorted(users, key=lambda user: user["age"])
```

```text
[{'name': 'Bob', 'age': 20}, {'name': 'Charlie', 'age': 25}, {'name': 'Alice', 'age': 30}]
```

`key=lambda user: user["age"]` is called once per item (not once per
*pair* of items — Python is smart enough to compute each key only once,
which also makes key functions efficient even for expensive
computations). The lambda takes one user dictionary and returns just its
`"age"`, and `sorted()` compares those extracted ages instead of trying
to compare whole dictionaries directly (which would raise a `TypeError`,
since dictionaries have no defined `<` comparison).

### 21.2 A named function instead of a `lambda`

```python
def get_age(user):
    return user["age"]

sorted(users, key=get_age)
```

This produces an identical result to the `lambda` version. A named
function is often clearer once the key logic is doing anything beyond a
single, obvious field access — the function name (`get_age`) documents
the intent directly, and it can be reused elsewhere or unit-tested on
its own, unlike an inline `lambda`.

## 22. Multiple Sort Keys

### 22.1 Tuple keys

```python
employees = [
    {"department": "A", "salary": 50000},
    {"department": "B", "salary": 60000},
    {"department": "A", "salary": 70000},
]

sorted(
    employees,
    key=lambda employee: (employee["department"], employee["salary"]),
)
```

```text
[{'department': 'A', 'salary': 50000},
 {'department': 'A', 'salary': 70000},
 {'department': 'B', 'salary': 60000}]
```

`key=lambda employee: (employee["department"], employee["salary"])`
returns a **tuple** for each employee. Python compares tuples
element-by-element: it compares the first elements first (department);
only when two items have equal first elements does it move on to
compare the second elements (salary) to break the tie. This is exactly
how a spreadsheet's "sort by column A, then by column B" behaves, and it
is the standard way to express "sort by X, then by Y" in Python.

### 22.2 Mixed ascending/descending order

`reverse=True` applies to the *entire* sort, so it cannot flip just one
key in a tuple directly. The clearest way to sort one field ascending
and another descending is to negate the numeric field being sorted
descending:

```python
sorted(
    employees,
    key=lambda employee: (employee["department"], -employee["salary"]),
)
```

```text
[{'department': 'A', 'salary': 70000},
 {'department': 'A', 'salary': 50000},
 {'department': 'B', 'salary': 60000}]
```

Negating `salary` makes larger salaries sort as smaller numbers, which
reverses their relative order *within* each department, while
department itself still sorts normally ascending. This trick only works
directly on numbers; for non-numeric fields needing independent reverse
order, a two-pass stable sort (§24) is the clearer approach — keep this
section's technique for the common case of one text key plus one
numeric key.

## 23. Sorting Custom Objects

The same `key=` idea applies directly to your own objects, including
dataclasses:

```python
from dataclasses import dataclass

@dataclass
class Employee:
    name: str
    salary: int

employees = [Employee("Ada", 70000), Employee("Bob", 50000)]

sorted(employees, key=lambda employee: employee.salary)
```

```text
[Employee(name='Bob', salary=50000), Employee(name='Ada', salary=70000)]
```

`key=lambda employee: employee.salary` accesses an attribute instead of
a dictionary field, but the mechanics are otherwise identical to every
example so far. This chapter is not the place for a full treatment of
classes or dataclasses (that belongs to a later module) — the point here
is only that sorting works the same way regardless of what kind of
Python object you are sorting.

## 24. Stable Sorting

### 24.1 What stability means

```python
records = [
    ("A", 2),
    ("B", 1),
    ("A", 1),
]

sorted(records, key=lambda record: record[1])
```

```text
[('B', 1), ('A', 1), ('A', 2)]
```

`("B", 1)` and `("A", 1)` have the same sort key (`1`), so there are two
equally "correct" orderings between them. Python's sort is **stable**:
when two items compare equal under the key, their **original relative
order is preserved** — `("B", 1)` appeared before `("A", 1)` in the
input, and it still does in the output. Python's sort is guaranteed to
behave this way; you can rely on it.

### 24.2 Why stability is useful: sorting in two passes

Stability makes it possible to sort by a secondary key first, then
stable-sort by the primary key, and get the same multi-key result as
the tuple-key approach from §22.1:

```python
employees = [
    {"department": "A", "salary": 50000},
    {"department": "B", "salary": 60000},
    {"department": "A", "salary": 70000},
]

# Pass 1: sort by the secondary key (salary) first.
by_salary = sorted(employees, key=lambda e: e["salary"])

# Pass 2: stable-sort by the primary key (department).
# Because sort is stable, employees within the same department
# keep the relative salary order established in pass 1.
by_department_then_salary = sorted(by_salary, key=lambda e: e["department"])
```

This produces the same result as `sorted(employees, key=lambda e:
(e["department"], e["salary"]))` from §22.1. **The single tuple-key
version is generally clearer** and is the recommended default — the
two-pass version is worth knowing because it explains *why* tuple-key
sorting works (it relies on exactly this stability guarantee), and
because it is occasionally necessary when the secondary sort needs
`reverse=True` independently of the primary key in a way a tuple key
cannot express directly.

## 25. `None` and Missing Values

```python
sorted([1, None, 2])
```

```text
TypeError: '<' not supported between instances of 'NoneType' and 'int'
```

Python refuses to guess how `None` compares to a number — there is no
universally correct answer to "is `None` smaller or larger than `2`" —
so it raises an error rather than silently picking one. The same problem
occurs sorting a mix of genuinely incompatible types (e.g., a list
containing both strings and numbers), and when a `key=` function tries
to read a dictionary field that some records are missing (`KeyError`
inside the key function itself).

**Safe strategies:**

```python
values = [1, None, 2, None, 3]

# Push None values to the end, sort everything else normally:
sorted(values, key=lambda v: (v is None, v))
```

```text
[1, 2, 3, None, None]
```

`(v is None, v)` builds a tuple key where the first element is `False`
(`0`) for real values and `True` (`1`) for `None` — so all real values
sort before all `None`s (tuple comparison checks the first element
first, exactly as in §22.1) — and real values still sort correctly
relative to each other by their own value as the tuple's second element.
For missing dictionary keys, use `.get("field", default)` inside the key
function (mirroring the previous chapter's §16 guidance) rather than
`record["field"]`, so a missing key produces a safe fallback instead of
crashing the entire sort.

## 26. Grouping + Sorting

Grouped results are usually more useful once ordered — for example,
ranking customers by total spending rather than leaving them in
whatever order `dict` happened to store them:

```python
totals = {"A": 400, "B": 300, "C": 500}

ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
print(ranked)
# [('C', 500), ('A', 400), ('B', 300)]
```

- `totals.items()` produces `(key, value)` tuples — `("A", 400)`,
  `("B", 300)`, `("C", 500)` — this is how a dictionary is turned into
  something `sorted()` can be given a key function over.
- `key=lambda item: item[1]` selects the second tuple element (the
  total) to sort by, ignoring the customer name for comparison purposes.
- `reverse=True` puts the highest spender first, matching the intent of
  a "ranking."

This is one of the most common finishing steps in a data-processing
pipeline: **group, then rank the groups.**

## 27. Deduplication + Sorting

```python
numbers = [5, 3, 5, 1, 3, 2]
unique_sorted = sorted(set(numbers))
print(unique_sorted)   # [1, 2, 3, 5]
```

This reads as a small pipeline: **DEDUPLICATE → SORT** — first collapse
to unique values with `set()`, then order the result with `sorted()`.

### 27.1 Does the order of operations matter?

For plain deduplicate-then-sort, `sorted(set(numbers))` is
straightforward and almost always what is wanted. But the *reverse*
order — sort first, then deduplicate — is a different, useful pipeline
when order-preserving deduplication (§13) is required together with a
specific ranking, for example: "list each unique customer once, in
order of their largest transaction, highest first":

```python
transactions = [
    {"customer": "B", "amount": 100},
    {"customer": "A", "amount": 500},
    {"customer": "B", "amount": 900},
    {"customer": "C", "amount": 200},
]

# Sort by amount descending FIRST...
by_amount_desc = sorted(transactions, key=lambda t: t["amount"], reverse=True)

# ...then deduplicate by customer, keeping the first (highest-amount) occurrence:
seen = set()
top_transaction_per_customer = []
for t in by_amount_desc:
    if t["customer"] not in seen:
        seen.add(t["customer"])
        top_transaction_per_customer.append(t)

print(top_transaction_per_customer)
# [{'customer': 'B', 'amount': 900}, {'customer': 'A', 'amount': 500}, {'customer': 'C', 'amount': 200}]
```

Here, sorting *before* deduplicating is essential — it determines
*which* transaction survives the dedup for each customer (the largest
one), because §13's "first-write-wins" seen-set logic keeps whichever
record it encounters first. Deduplicating first and sorting afterward
would give the same *set* of customers, but the wrong record would have
been kept for each. **When deduplication uses "first wins" logic, sort
order before deduplication controls which record wins.**

## 28. Grouping + Deduplication

```python
from collections import defaultdict

customers = [
    {"customer_id": "C1", "country": "UK"},
    {"customer_id": "C2", "country": "US"},
    {"customer_id": "C1", "country": "UK"},   # same customer, appears again
    {"customer_id": "C3", "country": "UK"},
]

customers_by_country = defaultdict(set)

for customer in customers:
    customers_by_country[customer["country"]].add(customer["customer_id"])

print(dict(customers_by_country))
# {'UK': {'C1', 'C3'}, 'US': {'C2'}}
```

`defaultdict(set)` combines grouping and deduplication in one loop: each
country groups its customers (`defaultdict`'s job), and each group is a
`set`, so a customer ID appearing twice for the same country — as `C1`
does — is only stored once (the `set`'s job). This is the natural result
of choosing a set as the per-group accumulator, as previewed in §8.

## 29. Grouping + Deduplication + Aggregation

```python
transactions = [
    {"transaction_id": "T1", "customer_id": "C1", "category": "food", "amount": 100},
    {"transaction_id": "T1", "customer_id": "C1", "category": "food", "amount": 100},  # duplicate T1
    {"transaction_id": "T2", "customer_id": "C1", "category": "travel", "amount": 500},
    {"transaction_id": "T3", "customer_id": "C2", "category": "food", "amount": 200},
]
```

A realistic sequence of operations on this data:

```python
# 1. Deduplicate by transaction ID (last-write-wins is a reasonable default here).
unique_by_id = {}
for t in transactions:
    unique_by_id[t["transaction_id"]] = t
deduplicated = list(unique_by_id.values())

# 2. Group by customer, collecting each customer's transactions.
by_customer = defaultdict(list)
for t in deduplicated:
    by_customer[t["customer_id"]].append(t)

# 3. Group by category, summing amounts.
by_category_total = defaultdict(int)
for t in deduplicated:
    by_category_total[t["category"]] += t["amount"]

# 4. Sort customers by total spending, highest first.
customer_totals = {
    customer_id: sum(t["amount"] for t in txns)
    for customer_id, txns in by_customer.items()
}
ranked_customers = sorted(customer_totals.items(), key=lambda item: item[1], reverse=True)

print(deduplicated)
print(dict(by_category_total))
print(ranked_customers)
```

```text
[{'transaction_id': 'T1', ...}, {'transaction_id': 'T2', ...}, {'transaction_id': 'T3', ...}]
{'food': 300, 'travel': 500}
[('C1', 600), ('C2', 200)]
```

This one example chains **deduplicate → group (two different ways) →
aggregate → sort** — exactly the shape of a realistic data-cleaning and
reporting task, and a preview of the mini project in §40.

## 30. Combining with Search/Count/Filter/Map/Aggregate

This chapter builds directly on
[Search, Count, Filter, Map, and Aggregate](01-search-count-filter-map-and-aggregate.md).
Grouping, deduplication, and sorting are rarely used alone — they
combine with all five earlier patterns constantly. Using one shared
dataset:

```python
transactions = [
    {"id": "T1", "customer": "A", "amount": 100, "status": "completed"},
    {"id": "T2", "customer": "B", "amount": 250, "status": "failed"},
    {"id": "T3", "customer": "A", "amount": 400, "status": "completed"},
    {"id": "T1", "customer": "A", "amount": 100, "status": "completed"},  # duplicate ID
]
```

- **SEARCH** — find a transaction by ID:
  `next((t for t in transactions if t["id"] == "T2"), None)`
- **FILTER** — keep completed transactions:
  `[t for t in transactions if t["status"] == "completed"]`
- **COUNT** — count completed transactions:
  `sum(t["status"] == "completed" for t in transactions)`
- **MAP** — extract amounts:
  `[t["amount"] for t in transactions]`
- **AGGREGATE** — total amount:
  `sum(t["amount"] for t in transactions)`
- **DEDUPLICATE** — remove duplicate transaction IDs:
  `list({t["id"]: t for t in transactions}.values())`
- **GROUP** — group by customer:
  `defaultdict(list)` keyed by `t["customer"]`
- **SORT** — rank customers by total spending after grouping and
  aggregating (as in §29).

A realistic report — "total completed spending per customer, ranked
highest first, with duplicate transactions removed" — needs *all eight*
patterns in sequence: **deduplicate → filter → group → aggregate →
sort**. Real data-processing work is almost always a composition like
this, not any single pattern in isolation.

## 31. Real-World Engineering Examples

**Banking** — group transactions by customer to compute per-account
statements.
INPUT: a flat list of transaction records → OPERATION: group by
`account_id` → OUTPUT: one list of transactions per account → WHY:
statements and fraud checks need a customer's activity considered as a
whole, not one transaction at a time.

**Data engineering** — deduplicate records by business key during
ingestion.
INPUT: raw records from a source system that occasionally sends retries
→ OPERATION: deduplicate by `(source_system, record_id)` →
OUTPUT: a clean, unique record set → WHY: downstream aggregations
silently double-count values if duplicate ingested records are not
removed first.

**Log processing** — group errors by service.
INPUT: a stream of log lines → OPERATION: group by the `service` field →
OUTPUT: per-service error lists or counts → WHY: on-call engineers need
to know *which service* is failing, not just that failures are
happening somewhere.

**Backend engineering** — sort API results by timestamp.
INPUT: a list of records fetched from a database or cache → OPERATION:
`sorted(records, key=lambda r: r["timestamp"], reverse=True)` → OUTPUT:
most recent items first → WHY: users expect feeds, notifications, and
histories to appear in a predictable, usually recency-based, order.

**Machine learning preprocessing** — remove duplicate training examples.
INPUT: a dataset assembled from multiple sources → OPERATION:
deduplicate by exact text match or a normalized/composite key → OUTPUT:
a clean training set → WHY: duplicate examples bias a model toward
overfitting on whatever happens to repeat, and inflate reported accuracy
if duplicates leak across train/test splits.

**AI data pipeline** — group documents by source, then deduplicate
document IDs.
INPUT: documents ingested from several data sources for retrieval or
fine-tuning → OPERATION: group by `source`, deduplicate by
`document_id` within each source → OUTPUT: a clean, organized document
collection → WHY: the same document is often re-crawled or re-submitted
multiple times, and ungrouped, un-deduplicated corpora waste storage and
skew retrieval results toward duplicated content.

## 32. Common Mistakes

**Grouping**

1. *Forgetting to initialize groups.*
```python
# WRONG
groups = {}
for category, amount in records:
    groups[category].append(amount)   # KeyError on the first occurrence of any category!
```
→ Why wrong: `groups[category]` cannot be appended to before it exists.
```python
# CORRECT
groups.setdefault(category, []).append(amount)
# or: use defaultdict(list)
```

2. *Using the wrong grouping key.*
```python
# WRONG — groups by the whole record instead of just the customer
groups = defaultdict(list)
for t in transactions:
    groups[t].append(t["amount"])   # dict is unhashable, or every record becomes its own group
```
→ Correct: identify the actual field that defines a group before
writing the loop (`t["customer"]`, not `t`).

3. *Overwriting previous values instead of accumulating.*
```python
# WRONG — plain assignment replaces, it does not collect
groups = {}
for category, amount in records:
    groups[category] = amount   # each new record erases the previous one!
```
→ Correct: append to a list (or add to a set, or `+=` to a running
total) — never plain-assign inside a grouping loop.

4. *Confusing grouping with sorting.* Grouping organizes items by shared
identity; sorting orders items. Producing "customers ranked by total
spend" needs *both*, in sequence (§26) — neither replaces the other.

5. *Misunderstanding `defaultdict`.* Accessing a `defaultdict` key —
even just to read it, e.g., `print(groups["new_key"])` — silently
*creates* that key with the default value. This can add unexpected keys
if you inspect a `defaultdict` casually while debugging.

6. *Misunderstanding `groupby`.* Assuming `itertools.groupby` behaves
like SQL's `GROUP BY` (collecting *all* matching keys regardless of
position) is the single most consequential `groupby` mistake — see §10.2
for the concrete example.

7. *Using `groupby` without sorting first.* Following directly from #6 —
always sort by the same key you pass to `groupby` unless the input is
already known to be grouped consecutively (e.g., already sorted upstream).

**Deduplication**

8. *Using `set()` when order matters.*
```python
# WRONG, if the original order needs to be preserved
unique = list(set(customer_ids))
```
→ Correct: use the seen-set pattern (§13.1) or `dict.fromkeys()` (§13.2).

9. *Assuming `set()` preserves any particular ordering.* Even when a
`set()`'s iteration order happens to look sensible for a specific input,
this is not a guarantee — never depend on it.

10. *Trying `set(list_of_dicts)`.*
```python
set(users)   # TypeError: unhashable type: 'dict'
```
→ Correct: deduplicate by an extracted, hashable field (§14.2) or a
composite tuple key (§15).

11. *Choosing the wrong identity key.* Deduplicating by name when email
is the real business identity (or vice versa) can merge genuinely
distinct people, or fail to merge genuine duplicates.

12. *Accidentally deleting meaningful duplicate records.* Not every
repeated value is a data-quality problem — two transactions for the same
customer, on the same day, for the same amount, might be entirely
legitimate. Deduplicate only against a field that truly defines
uniqueness for the business problem at hand (e.g., a transaction ID),
not against fields that can validly repeat (e.g., amount).

13. *Confusing "duplicate value" with "duplicate business entity."* Two
records can have every visible field identical yet represent two real,
separate events (e.g., two identical $5 coffee purchases minutes apart);
conversely, two records can look different yet represent one entity
(e.g., "Bob Smith" and "Robert Smith" with the same email). Deduplication
logic must reflect the actual business rule, not just "do these fields
match."

14. *Accidentally keeping the wrong duplicate* by using first-write-wins
when last-write-wins was intended, or vice versa (§14.4) — always state
explicitly which one is required before writing the loop.

**Sorting**

15. *Confusing `sorted()` and `.sort()`.* Expecting `.sort()` to return
the sorted list (it returns `None`), or expecting `sorted()` to modify
the original list in place (it does not) — see §18.

16. *Assigning the result of `list.sort()`.*
```python
numbers = numbers.sort()   # numbers is now None!
```
→ Correct: call `numbers.sort()` on its own line, or use `sorted_numbers
= sorted(numbers)` if a new variable is wanted.

17. *Forgetting `reverse=True`* and instead trying to reverse the input
first, then sort — which does not produce descending order for equal
keys the same way (see §19's note on stability interactions).

18. *Sorting by the wrong field* — e.g., sorting transactions by
`"customer"` when the intent was to rank by `"amount"`. Always
double-check the `key=` function extracts the field the requirement
actually names.

19. *Using an incorrect key function* that returns the wrong type or
raises an error partway through (e.g., a `key=` function that assumes a
field always exists — see mistake #20 and §25).

20. *Mixing incomparable values,* such as `sorted([1, None, 2])` or a
list mixing strings and numbers — raises `TypeError` (§25). Clean or
normalize the data, or use a key function that maps every value to a
comparable form, before sorting.

21. *Unnecessarily sorting when ordering is not required.* Sorting costs
O(n log n) (§34) — calling `sorted()` before a search or an aggregation
that does not care about order (e.g., before `sum()` or before `any()`)
wastes time for no benefit.

## 33. Edge Cases

| Situation | Grouping | Deduplication | Sorting |
|---|---|---|---|
| Empty collection | result is an empty dict | result is an empty list/set | `sorted([])` → `[]`; `[].sort()` → no error, stays `[]` |
| One item | one group with one member | the single item, unchanged | a one-item list is trivially "sorted" already |
| All duplicates | one group containing every item | collapses to a single unique item | (not directly relevant — duplicates just sort next to each other, stably) |
| No duplicates | each item forms its own group of one | output equals input | normal sort behavior |
| Duplicate records with conflicting field values | depends entirely on which record's fields end up in the group's accumulator | must choose first-write-wins or last-write-wins explicitly (§14.4) | if sorting by a field that conflicts between "duplicates," the sort key itself may be ambiguous — resolve the duplicate first |
| Missing keys | a lookup like `record["key"]` raises `KeyError` inside the loop — use `.get()` | the same — identity fields must be checked for presence before using them as keys | a `key=` function reading a missing field raises `KeyError` mid-sort — guard with `.get(field, default)` |
| `None` values | `None` can be a valid group key (e.g., "unknown category") — handle it like any other key | `None` can be a legitimate value to deduplicate or a sentinel for "missing" — decide which before writing the check | comparing `None` to real values raises `TypeError` (§25) — sort around it explicitly |
| Mixed data types | group keys of different types (e.g., `1` and `"1"`) are treated as distinct keys | identity comparison is exact — `1` and `"1"` are not duplicates of each other | sorting a list mixing types (e.g., `int` and `str`) raises `TypeError` |
| Case differences | `"UK"` and `"uk"` form two different groups unless explicitly normalized | `"Alice"` and `"alice"` are not duplicates unless explicitly normalized (e.g., `.lower()`) | case-sensitive by default (§20) — normalize with a `key=` function if case should be ignored |
| Negative numbers / zero | group and sum normally — no special handling needed | `0` and `-0` behave as equal (`0 == -0.0` is `True` for numeric comparisons) — rarely an issue in practice, but worth knowing | sort normally; no special handling needed |
| Duplicate IDs | grouping by an ID naturally handles repeats — every matching record joins the same group | the exact scenario deduplication is designed for (§14) | if two records share a sort key, stability (§24) determines their relative order in the output |
| Empty groups | a group key is never created unless at least one item has that key — there is no such thing as an "empty group" appearing on its own | not applicable | not applicable |
| Already-sorted input | `sorted()`/`.sort()` still run in O(n log n) — Python's Timsort (§35) can be notably faster in practice on already-sorted or partially-sorted data, but it does not skip the comparison-based guarantee | not applicable | as above |
| Reverse-sorted input | sorts normally; Timsort recognizes descending runs efficiently as well | not applicable | as above |
| Large datasets | dictionary-based grouping stays roughly linear; watch memory if every group holds large lists | set-based approaches stay roughly linear; watch memory for very large seen-sets | sorting cost grows as O(n log n) — noticeably slower than a single grouping/deduplication pass at large scale (§34) |

## 34. Performance and Complexity

| Operation | Typical time complexity | Notes |
|---|---|---|
| Dictionary-based grouping | O(n) average case | one pass over the data; each lookup/insert into the dictionary is O(1) average case |
| Set-based deduplication (`set(items)`) | O(n) average case | each insertion checks/updates the set in O(1) average case |
| Order-preserving (seen-set) deduplication | O(n) average case | same per-item cost as plain set deduplication, plus building the result list |
| Sorting (`sorted()` / `.sort()`) | O(n log n) | comparison-based sorting cannot, in general, do better than n log n comparisons |

**Sorting is fundamentally more expensive than one linear pass.** Doubling
the input size roughly doubles the cost of grouping or deduplication,
but more than doubles the cost of sorting (because of the extra `log n`
factor) — this is why unnecessary sorting (mistake #21 in §32) is worth
avoiding on large data, and why, when a pipeline needs both grouping and
sorting, it is worth doing the grouping/aggregation *first* to shrink
the data, and sorting the smaller, grouped result afterward (as in §26
and §29), rather than sorting the full raw dataset before grouping it.

**Space considerations:**

- Grouping into lists holds every original item somewhere — total space
  is proportional to the input size, O(n).
- Deduplication with a set holds only the unique items — space is
  proportional to the number of *distinct* values, which can be much
  smaller than n if there are many duplicates.
- `sorted()` allocates an entirely new list — O(n) additional space on
  top of the original.
- `list.sort()` sorts in place — no additional O(n) list is allocated
  for the result itself (though the algorithm may use a small amount of
  temporary working space internally).

Being aware of these trade-offs matters most at real production scale —
for a few hundred records none of this is perceptible, but for millions
of records, the difference between an in-place `.sort()` and a
`sorted()` call that duplicates the whole list, or between grouping
before sorting versus sorting the raw data first, can be the difference
between a report that runs in milliseconds and one that runs in minutes.

## 35. Sorting Algorithm Concepts

You do not need to implement a sorting algorithm to use sorting well,
but it helps to know that several classic approaches exist, at a purely
conceptual level:

- **Bubble sort, insertion sort, selection sort** — simple, intuitive
  approaches that repeatedly compare and swap neighboring or nearby
  items; easy to understand, but slow (roughly O(n²)) on large data.
- **Merge sort, quicksort** — faster, "divide and conquer" approaches
  that split the data into smaller pieces, sort those, and recombine
  them, achieving O(n log n) in typical or best cases.
- **Timsort** — the algorithm Python's `sorted()` and `list.sort()`
  actually use internally. It is a hybrid, stable, highly optimized
  sort, particularly efficient on data that already contains sorted or
  partially sorted runs (very common in real-world data).

Production Python developers essentially never hand-implement a sorting
algorithm, because Timsort is already fast, stable, thoroughly tested,
and exposed through two simple, well-understood interfaces
(`sorted()`/`.sort()`). Understanding the *conceptual* existence of
these algorithms is useful for interviews and for general algorithmic
literacy; understanding their internal implementation in depth, and a
full treatment of Big-O notation, belongs to the dedicated upcoming
chapter,
[Big-O, Time, and Space Complexity](03-big-o-time-and-space-complexity.md) —
this chapter only needs you to know *that* sorting costs O(n log n) and
*why* that makes it more expensive than a single O(n) pass.

## 36. Memory and Intermediate Collections

Every step in a pipeline that produces a new list or set costs memory —
being deliberate about *when* a full collection needs to exist helps
control that cost.

```python
items = [3, 1, 2, 3, 1]

set(items)                 # builds one intermediate set — O(n) extra space
sorted(set(items))         # builds the set, THEN builds a whole new sorted list from it
```

`sorted(set(items))` necessarily **materializes** (fully builds, in
memory) both the intermediate set and the final sorted list — there is
no way to produce a *sorted* result without first having the complete
set of values available to compare, since sorting is not a one-item-at-
a-time operation the way filtering or mapping can be.

This is a meaningful difference from the lazy, one-item-at-a-time
processing possible with generator expressions and `map()`/`filter()`
(previous chapter, §7.4, §17): those can produce results without ever
holding the whole collection in memory at once, because each output
item depends only on one input item. Sorting and full-set deduplication
cannot offer that same guarantee, because determining an item's position
in sorted order — or confirming that no earlier duplicate exists —
inherently requires knowledge of (at least a large part of) the whole
collection. Keep this distinction in mind when the input is very large:
grouping, deduplication, and sorting are inherently more memory-hungry
than filtering or mapping.

## 37. Debugging

### 37.1 Tracing a grouping bug

```python
groups = defaultdict(list)
for record in records:
    key = record["category"]
    print(f"record={record}, key={key}, groups before={dict(groups)}")
    groups[key].append(record["amount"])
    print(f"groups after={dict(groups)}")
```

| iteration | record | key | groups before | groups after |
|---|---|---|---|---|
| 1 | `{...}` | `"sales"` | `{}` | `{"sales": [100]}` |
| 2 | `{...}` | `"support"` | `{"sales": [100]}` | `{"sales": [100], "support": [200]}` |

If the printed `key` is not what you expect, the bug is in how the key
is extracted (wrong field name, wrong type). If `groups` after does not
grow as expected, check whether `.append()` is actually inside the loop
and using the current item.

### 37.2 Tracing a deduplication bug

```python
seen = set()
result = []
for item in items:
    key = item["id"]
    kept = key not in seen
    print(f"item={item}, key={key}, seen before={seen}, kept={kept}")
    if kept:
        seen.add(key)
        result.append(item)
```

| item | dedup key | seen before | kept/discarded | result |
|---|---|---|---|---|
| `{"id": 1, ...}` | `1` | `set()` | kept | `[{"id": 1, ...}]` |
| `{"id": 1, ...}` | `1` | `{1}` | discarded | `[{"id": 1, ...}]` (unchanged) |
| `{"id": 2, ...}` | `2` | `{1}` | kept | `[{"id": 1, ...}, {"id": 2, ...}]` |

If an item you expected to be discarded was kept (or vice versa), print
`key` for both records side by side — the identity field itself is
almost always the source of the mismatch (wrong field name, mismatched
types like `"1"` vs `1`, or unnormalized case).

### 37.3 Debugging a sort

If `sorted()`/`.sort()` produces unexpected order, print the *key
values*, not just the items themselves:

```python
for item in items:
    print(item, "→ key:", key_function(item))
```

This immediately reveals whether the key function is extracting the
field you think it is, whether it is returning the type you expect
(e.g., a string `"20"` instead of an integer `20`, which sorts
completely differently), and whether `reverse=True` is set the way you
intended.

## 38. Testing

**Grouping**
```python
from collections import defaultdict

def group_by_category(records):
    groups = defaultdict(list)
    for category, amount in records:
        groups[category].append(amount)
    return dict(groups)

def test_grouping():
    assert group_by_category([("a", 1), ("a", 2)]) == {"a": [1, 2]}   # one group
    assert group_by_category([("a", 1), ("b", 2)]) == {"a": [1], "b": [2]}  # multiple groups
    assert group_by_category([]) == {}                                # empty input
```

**Deduplication**
```python
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
    assert deduplicate_by_id([a, b]) == [a, b]              # no duplicates
    assert deduplicate_by_id([a, a, a]) == [a]                # all duplicates
    assert deduplicate_by_id([a, b, a]) == [a, b]              # mixed duplicates, order preserved
    assert deduplicate_by_id([{"id": 1, "v": 1}, {"id": 1, "v": 2}]) == [{"id": 1, "v": 1}]  # duplicate records — first wins
```

**Sorting**
```python
def test_sorting():
    assert sorted([3, 1, 2]) == [1, 2, 3]                       # ascending
    assert sorted([3, 1, 2], reverse=True) == [3, 2, 1]           # descending
    assert sorted([("a", 2), ("b", 2)], key=lambda x: x[1]) == [("a", 2), ("b", 2)]  # duplicate keys stay in original relative order
    assert sorted([]) == []                                       # empty list
    assert sorted([5]) == [5]                                     # one item
    assert sorted(["Bob", "alice"], key=str.lower) == ["alice", "Bob"]  # custom key
```

## 39. Progressive Coding Exercises

Full reasoning and solutions are in **§44 — Answer Key / Solutions**.
Attempt each exercise yourself first.

### Level 1 — Beginner

**1. Group words by first letter.**
Input: `words = ["apple", "banana", "avocado", "blueberry", "cherry"]`
Expected output: `{"a": ["apple", "avocado"], "b": ["banana", "blueberry"], "c": ["cherry"]}`
Hints: use `word[0]` as the grouping key.

**2. Remove duplicate numbers.**
Input: `numbers = [4, 2, 4, 1, 2, 3]`
Expected output (order does not matter here): a collection containing
each of `1, 2, 3, 4` exactly once.
Constraints: use `set()`.

**3. Sort numbers.**
Input: `numbers = [8, 3, 9, 1]`
Expected output: `[1, 3, 8, 9]`

**4. Sort names alphabetically.**
Input: `names = ["Zoe", "amir", "Bella"]`
Expected output: `["amir", "Bella", "Zoe"]`
Hints: think about case sensitivity (§20).

**5. Count items per category.**
Input: `items = [("fruit", "apple"), ("veg", "carrot"), ("fruit", "banana")]`
Expected output: `{"fruit": 2, "veg": 1}`

### Level 2 — Intermediate

**6. Group transactions by customer.**
Input:
```python
transactions = [
    {"customer": "A", "amount": 50},
    {"customer": "B", "amount": 20},
    {"customer": "A", "amount": 30},
]
```
Expected output: `{"A": [50, 30], "B": [20]}` (list of amounts per
customer)

**7. Deduplicate customer IDs while preserving order.**
Input: `ids = ["C3", "C1", "C3", "C2", "C1"]`
Expected output: `["C3", "C1", "C2"]`
Constraints: use either the seen-set pattern or `dict.fromkeys()`.

**8. Sort users by age.**
Input: `users = [{"name": "A", "age": 40}, {"name": "B", "age": 25}]`
Expected output: `[{"name": "B", "age": 25}, {"name": "A", "age": 40}]`

**9. Sort transactions by amount descending.**
Input: same `transactions` as exercise 6.
Expected output: transactions ordered `50, 30, 20`.

**10. Group and calculate totals.**
Input: same `transactions` as exercise 6.
Expected output: `{"A": 80, "B": 20}`

### Level 3 — Advanced

**11. Deduplicate dictionaries by ID.**
Input:
```python
records = [{"id": 1, "v": "x"}, {"id": 2, "v": "y"}, {"id": 1, "v": "z"}]
```
Expected output (first wins): `[{"id": 1, "v": "x"}, {"id": 2, "v": "y"}]`

**12. Keep the latest record for each ID.**
Input: same `records` as exercise 11, but assume list order reflects
arrival order and later should win.
Expected output: two records, with `id: 1` showing `"v": "z"`.

**13. Group customers by country.**
Input:
```python
customers = [{"id": "C1", "country": "UK"}, {"id": "C2", "country": "US"}, {"id": "C3", "country": "UK"}]
```
Expected output: `{"UK": ["C1", "C3"], "US": ["C2"]}` (list of customer
IDs per country)

**14. Group unique products by category.**
Input:
```python
sales = [("food", "apple"), ("food", "apple"), ("tech", "phone")]
```
Expected output: `{"food": {"apple"}, "tech": {"phone"}}`

**15. Sort customers by total spending.**
Input: a dictionary of `{customer_id: total_spend}` (build it from any
transaction list of your choice, or reuse exercise 10's output).
Expected output: a list of `(customer_id, total)` tuples, highest
spender first.

### Level 4 — Production-oriented

**16. Deduplicate event records using a composite business key.**
Input:
```python
events = [
    {"user_id": "U1", "event_type": "click", "day": "2026-01-01"},
    {"user_id": "U1", "event_type": "click", "day": "2026-01-01"},  # duplicate
    {"user_id": "U1", "event_type": "click", "day": "2026-01-02"},
]
```
Expected output: two events (the duplicate on `2026-01-01` removed),
keyed by `(user_id, event_type, day)`.

**17. Group log events by service and severity.**
Input:
```python
logs = [
    {"service": "auth", "severity": "ERROR"},
    {"service": "auth", "severity": "INFO"},
    {"service": "billing", "severity": "ERROR"},
]
```
Expected output: a nested structure, e.g.
`{"auth": {"ERROR": 1, "INFO": 1}, "billing": {"ERROR": 1}}`.
Hints: this needs a `defaultdict` of `defaultdict(int)` — think about
what the outer and inner grouping keys are.

**18. Calculate grouped transaction totals.**
Reuse the transaction dataset from §29. Report total spending per
category.

**19. Produce a ranked customer report.**
Reuse the transaction dataset from §29 or §14. Report each customer's
total spend, sorted highest to lowest, formatted as a list of
`{"customer": ..., "total": ...}` dictionaries.

**20. Build a small data-cleaning pipeline.**
Input: any transaction list containing duplicate transaction IDs, a mix
of `"completed"` and `"failed"` statuses, and multiple customers.
Requirements: deduplicate → filter (completed only) → group (by
customer) → aggregate (sum per customer) → sort (highest spender first).
Expected output: a ranked list of `(customer, total)` pairs, reflecting
only real, completed transactions.

## 40. Mini Project — Customer Transaction Analysis Pipeline

### Requirements

Given a list of transaction dictionaries with fields `transaction_id`,
`customer_id`, `category`, `amount`, `status`, and `timestamp`, build a
pipeline that:

1. Removes duplicate transaction IDs.
2. Clearly defines which duplicate record wins.
3. Filters to valid/completed transactions.
4. Groups transactions by customer.
5. Calculates total spending per customer.
6. Calculates transaction count per customer.
7. Groups spending by category.
8. Sorts customers by total spending.
9. Identifies the highest-spending customer.
10. Produces a final summary structure.

### Before implementing, define:

- **Problem statement** — in your own words: this pipeline turns a raw,
  possibly messy transaction feed into a clean, ranked spending report,
  for a use case such as a finance team's monthly customer review.
- **Inputs** — the raw transaction list.
- **Outputs** — a deduplicated, filtered transaction list; a
  per-customer summary (total and count); a per-category total; a
  ranked list of customers; the single highest-spending customer; one
  combined summary structure.
- **Assumptions** — is `transaction_id` guaranteed to be present on
  every record? Is `amount` always a non-negative number? Can `status`
  contain values other than `"completed"`/`"failed"`? Can the list be
  empty?
- **Business key** — `transaction_id` is the identity used to detect
  duplicates.
- **Deduplication rule** — decide explicitly: is the *last* occurrence
  of a given `transaction_id` the authoritative one (e.g., because later
  records represent corrected retries), or the *first* (e.g., because
  the first submission is authoritative and later repeats are simple
  network retries)? This project uses **last-write-wins**, on the
  assumption that a repeated transaction ID represents a corrected
  resubmission.
- **Edge cases** — an empty transaction list; a customer with zero
  completed transactions (should they appear in the ranking at all?); a
  transaction missing `amount` or `category`; every transaction having
  the same customer.
- **Pseudocode:**
  ```
  deduplicate transactions by transaction_id, keeping the last occurrence
  filter to only "completed" transactions
  group the filtered transactions by customer_id
  for each customer: sum amounts (total), count transactions
  group the filtered transactions by category, summing amounts
  sort customers by total spending, descending
  the first entry in the sorted ranking is the highest-spending customer
  assemble all of the above into one summary dictionary
  ```
- **Dry run** — before coding, manually trace three or four small sample
  transactions (including one duplicate ID and one failed transaction)
  through every pseudocode step by hand, confirming the expected
  intermediate result at each stage.

### Reference Implementation

```python
from collections import defaultdict


def deduplicate_transactions(transactions):
    """Last-write-wins deduplication by transaction_id."""
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


def customer_totals(grouped_by_customer):
    return {
        customer_id: sum(t["amount"] for t in txns)
        for customer_id, txns in grouped_by_customer.items()
    }


def customer_counts(grouped_by_customer):
    return {
        customer_id: len(txns)
        for customer_id, txns in grouped_by_customer.items()
    }


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
        "customer_totals": totals,
        "customer_counts": counts,
        "category_totals": totals_by_category(completed),
        "ranking": ranking,
        "top_customer": ranking[0] if ranking else None,
    }
```

```python
transactions = [
    {"transaction_id": "T1", "customer_id": "C1", "category": "food", "amount": 100, "status": "completed", "timestamp": "2026-01-01"},
    {"transaction_id": "T1", "customer_id": "C1", "category": "food", "amount": 150, "status": "completed", "timestamp": "2026-01-02"},  # corrected T1
    {"transaction_id": "T2", "customer_id": "C1", "category": "travel", "amount": 500, "status": "failed", "timestamp": "2026-01-01"},
    {"transaction_id": "T3", "customer_id": "C2", "category": "food", "amount": 200, "status": "completed", "timestamp": "2026-01-01"},
]

summary = build_summary(transactions)
print(summary)
```

```text
{'customer_totals': {'C1': 150, 'C2': 200},
 'customer_counts': {'C1': 1, 'C2': 1},
 'category_totals': {'food': 350},
 'ranking': [('C2', 200), ('C1', 150)],
 'top_customer': ('C2', 200)}
```

Key reasoning: `T1`'s corrected `$150` version (the later occurrence)
replaced the original `$100` version, per the last-write-wins rule;
`T2` was excluded entirely from every downstream calculation because it
never completed (it never even reaches `group_by_customer`); and
`top_customer` handles the empty-ranking edge case explicitly (`if
ranking else None`) rather than assuming at least one completed
transaction always exists.

## 41. Interview Questions

**Grouping**

- What is grouping, conceptually, and how does it differ from filtering?
- How would you group a list of records using a plain dictionary, from
  scratch?
- What is `defaultdict`, and what problem does it solve compared to a
  regular `dict`?
- What is `setdefault()`, and how does it differ from `defaultdict`?
- Why does `defaultdict(int)` work for counting, but `defaultdict(list)`
  would not?
- Why does `itertools.groupby` require the input to be sorted by the
  grouping key first? What happens if it is not?

**Deduplication**

- What is deduplication, and why does it require defining "identity"?
- Why can sets remove duplicates? What property of set elements makes
  this possible?
- Why might `set()` be inappropriate when order matters?
- How do you deduplicate a list of dictionaries, given that dictionaries
  are not hashable?
- What is a business key, and how does it differ from a database's
  auto-generated ID?
- What is a composite key, and when would you need one for
  deduplication?
- What is the difference between first-write-wins and last-write-wins
  deduplication? Give a scenario where each is the correct choice.

**Sorting**

- What is the difference between `sorted()` and `list.sort()`?
- Why does `list.sort()` return `None` instead of the sorted list?
- What is a key function, and why is it needed for sorting anything more
  complex than plain numbers?
- What does `reverse=True` do, and how is it different from calling
  `reversed()` on a list?
- What is stable sorting, and why does it matter when sorting by
  multiple fields?
- What happens if you try to sort a list containing both numbers and
  `None`? How would you handle that safely?
- What is the time complexity of sorting, and why is it more expensive
  than a single pass over the data?

**Scenario-based**

- "You receive a stream of transaction records from a system that
  occasionally retries failed sends, producing exact duplicates. How
  would you deduplicate them, and what would you use as the identity?"
- "How would you produce a report of total sales per region, ranked from
  highest to lowest, starting from a flat list of sale records?"
- "A teammate's report code calls `sorted()` on the full raw dataset
  before grouping it by customer. What would you suggest, and why?"
- "You need to keep the *latest* version of each customer record from a
  feed where customers are occasionally updated. Walk through how you'd
  implement that, and what could go wrong if you used the wrong
  strategy."
- "How would you deduplicate events uniquely identified by the
  combination of `user_id` and `event_timestamp`, when neither field
  alone is unique?"
- "Why might grouping millions of records before sorting be faster than
  sorting them first and grouping afterward?"

## 42. Pattern Recognition Cheat Sheet

```
"Which items belong together?"
    → GROUPING       (dict, setdefault(), defaultdict, itertools.groupby)

"Which items represent the same thing?"
    → DEDUPLICATION  (set(), seen-set loop, dict.fromkeys(), last/first-write-wins)

"In what order should the items appear?"
    → SORTING        (sorted(), list.sort(), key=, reverse=True)
```

Common combinations, roughly in order of how often they appear in real
data work:

```
GROUP → AGGREGATE
FILTER → GROUP → AGGREGATE
GROUP → AGGREGATE → SORT
DEDUPLICATE → SORT
GROUP → DEDUPLICATE
DEDUPLICATE → FILTER → GROUP → AGGREGATE → SORT
```

These combinations are the backbone of ETL pipelines, analytics
queries, backend reporting endpoints, data-quality checks, ML dataset
preparation, and AI data pipelines — the same handful of shapes,
composed in different orders depending on what a given task needs.

## 43. Final Review

- **Grouping** organizes a flat collection by a chosen key, using a
  dictionary as the group container — start with a manual `if key not
  in groups` check, then simplify with `setdefault()` or `defaultdict`
  once the underlying mechanism is second nature.
- Grouping almost always exists to support a **per-group aggregation**
  (`defaultdict(int)` for sums/counts, `defaultdict(list)` for
  collecting values, `defaultdict(set)` for unique values per group).
- `itertools.groupby` groups only **consecutive** matching keys and
  requires pre-sorted input — it is not a drop-in replacement for
  dictionary-based grouping.
- **Deduplication** requires explicitly choosing an **identity** — the
  whole value, one field, or a composite tuple key — and deciding
  whether order must be preserved (`set()` does not preserve it; the
  seen-set pattern and `dict.fromkeys()` do).
- Deduplicating records requires choosing **first-write-wins** or
  **last-write-wins** deliberately — this is a business decision with
  real consequences for which data survives.
- **Sorting** with `sorted()` returns a new list and leaves the input
  untouched; `list.sort()` sorts in place and returns `None` — mixing
  these up (especially `x = x.sort()`) is a classic bug.
- **`key=` functions** let you sort anything by any computed value,
  including multiple fields via tuple keys, and Python's sort is
  **stable**, which is what makes multi-pass and tuple-key sorting
  behave predictably.
- Grouping and deduplication are typically O(n); sorting is O(n log n)
  — do the cheaper operations first when a pipeline needs both, to
  shrink the data sorting has to work on.
- These three patterns compose constantly with **search, count, filter,
  map, and aggregate** from the previous chapter — real data-processing
  pipelines chain several of these eight patterns together in sequence.

## 44. Answer Key / Solutions

### Level 1

**1.** Group by the first character of each word — the same shape as
§4.1, with `word[0]` as the key.
```python
words = ["apple", "banana", "avocado", "blueberry", "cherry"]
groups = {}
for word in words:
    groups.setdefault(word[0], []).append(word)
print(groups)
# {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
```

**2.** `set()` is the direct tool for "unique values, order irrelevant."
```python
numbers = [4, 2, 4, 1, 2, 3]
print(set(numbers))   # {1, 2, 3, 4}
```

**3.** `sorted()` returns a new, ascending list; the original is
untouched.
```python
numbers = [8, 3, 9, 1]
print(sorted(numbers))   # [1, 3, 8, 9]
```

**4.** Without a key function, sorting is case-sensitive and puts
capitalized names before lowercase ones (§20); `key=str.lower` fixes
this.
```python
names = ["Zoe", "amir", "Bella"]
print(sorted(names, key=str.lower))   # ['amir', 'Bella', 'Zoe']
```

**5.** Grouping by category, counting members with `+= 1` per group —
identical shape to §6.3.
```python
items = [("fruit", "apple"), ("veg", "carrot"), ("fruit", "banana")]
counts = {}
for category, _ in items:
    counts[category] = counts.get(category, 0) + 1
print(counts)   # {'fruit': 2, 'veg': 1}
```

### Level 2

**6.**
```python
from collections import defaultdict

transactions = [
    {"customer": "A", "amount": 50},
    {"customer": "B", "amount": 20},
    {"customer": "A", "amount": 30},
]
groups = defaultdict(list)
for t in transactions:
    groups[t["customer"]].append(t["amount"])
print(dict(groups))   # {'A': [50, 30], 'B': [20]}
```

**7.** Either the seen-set loop or `dict.fromkeys()` gives the identical
order-preserving result.
```python
ids = ["C3", "C1", "C3", "C2", "C1"]
print(list(dict.fromkeys(ids)))   # ['C3', 'C1', 'C2']
```

**8.** A key function extracts `"age"` for comparison.
```python
users = [{"name": "A", "age": 40}, {"name": "B", "age": 25}]
print(sorted(users, key=lambda u: u["age"]))
# [{'name': 'B', 'age': 25}, {'name': 'A', 'age': 40}]
```

**9.** `reverse=True` puts the largest amount first.
```python
print(sorted(transactions, key=lambda t: t["amount"], reverse=True))
# amounts in order: 50, 30, 20
```

**10.** `defaultdict(int)` sums directly, per customer — the grouping +
aggregation pattern from §7.3.
```python
totals = defaultdict(int)
for t in transactions:
    totals[t["customer"]] += t["amount"]
print(dict(totals))   # {'A': 80, 'B': 20}
```

### Level 3

**11.** First-write-wins: the seen-set pattern from §14.2 naturally
keeps whichever record it reaches first.
```python
records = [{"id": 1, "v": "x"}, {"id": 2, "v": "y"}, {"id": 1, "v": "z"}]
seen, result = set(), []
for r in records:
    if r["id"] not in seen:
        seen.add(r["id"])
        result.append(r)
print(result)   # [{'id': 1, 'v': 'x'}, {'id': 2, 'v': 'y'}]
```

**12.** Last-write-wins: plain dictionary assignment overwrites earlier
entries for the same key, from §14.3.
```python
by_id = {}
for r in records:
    by_id[r["id"]] = r
print(list(by_id.values()))   # [..., {'id': 1, 'v': 'z'}]  (order may show id 2 first, then updated id 1)
```

**13.** Grouping by `"country"`, collecting `"id"` values — note this
collects into a list (duplicates within a country would be kept),
matching the exercise's specified output shape.
```python
customers = [{"id": "C1", "country": "UK"}, {"id": "C2", "country": "US"}, {"id": "C3", "country": "UK"}]
groups = defaultdict(list)
for c in customers:
    groups[c["country"]].append(c["id"])
print(dict(groups))   # {'UK': ['C1', 'C3'], 'US': ['C2']}
```

**14.** `defaultdict(set)` groups while automatically discarding
duplicate products within each category — §8 and §28's pattern.
```python
sales = [("food", "apple"), ("food", "apple"), ("tech", "phone")]
groups = defaultdict(set)
for category, product in sales:
    groups[category].add(product)
print(dict(groups))   # {'food': {'apple'}, 'tech': {'phone'}}
```

**15.** `.items()` plus a `key=` selecting the total, `reverse=True` for
highest-first — identical to §26.
```python
totals = {"A": 80, "B": 20}   # from exercise 10
ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
print(ranked)   # [('A', 80), ('B', 20)]
```

### Level 4

**16.** A tuple of the three identifying fields serves as the composite
key, following §15 exactly.
```python
events = [
    {"user_id": "U1", "event_type": "click", "day": "2026-01-01"},
    {"user_id": "U1", "event_type": "click", "day": "2026-01-01"},
    {"user_id": "U1", "event_type": "click", "day": "2026-01-02"},
]
seen, unique = set(), []
for e in events:
    key = (e["user_id"], e["event_type"], e["day"])
    if key not in seen:
        seen.add(key)
        unique.append(e)
print(len(unique))   # 2
```

**17.** A two-level grouping: group by service first, and within each
service's group, count by severity — a `defaultdict` whose factory is
itself a `defaultdict(int)`.
```python
logs = [
    {"service": "auth", "severity": "ERROR"},
    {"service": "auth", "severity": "INFO"},
    {"service": "billing", "severity": "ERROR"},
]
groups = defaultdict(lambda: defaultdict(int))
for log in logs:
    groups[log["service"]][log["severity"]] += 1
print({service: dict(counts) for service, counts in groups.items()})
# {'auth': {'ERROR': 1, 'INFO': 1}, 'billing': {'ERROR': 1}}
```

**18.** Reusing §29's `by_category_total` construction directly.
```python
totals = defaultdict(int)
for t in transactions:   # the deduplicated, completed set from §29
    totals[t["category"]] += t["amount"]
print(dict(totals))
```

**19.** Group, sum, then reshape the ranked tuples into the requested
dictionary shape.
```python
grouped = defaultdict(list)
for t in transactions:
    grouped[t["customer_id"]].append(t["amount"])

totals = {customer: sum(amounts) for customer, amounts in grouped.items()}
ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)

report = [{"customer": customer, "total": total} for customer, total in ranked]
print(report)
```

**20.** The full five-stage pipeline, composing every pattern from this
chapter and the previous one in sequence.
```python
def deduplicate(transactions):
    by_id = {}
    for t in transactions:
        by_id[t["transaction_id"]] = t   # last-write-wins
    return list(by_id.values())

def pipeline(transactions):
    deduplicated = deduplicate(transactions)
    completed = [t for t in deduplicated if t["status"] == "completed"]

    grouped = defaultdict(list)
    for t in completed:
        grouped[t["customer_id"]].append(t["amount"])

    totals = {customer: sum(amounts) for customer, amounts in grouped.items()}
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)

print(pipeline(transactions))
```

Each stage is small and independently testable — this is itself a
lesson worth taking from the mini project and this final exercise:
production data pipelines are usually built as a short sequence of
small, well-named, individually verifiable steps, exactly mirroring the
pattern-by-pattern structure of this chapter.
