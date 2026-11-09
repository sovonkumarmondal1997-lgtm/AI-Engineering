# 04 — Choosing Lists, Dictionaries, Sets, Stacks, and Queues
## Complete Study Guide, Learning-Level Assessment, Exercises, and Mini-Project

**Source lesson:** `04-choosing-lists-dictionaries-sets-stacks-and-queues.md`  
**Purpose:** Learn each concept in plain language, understand the examples and complexity, and practise all 20 exercises using the Python foundations already covered.

---

# Part A — Complete lesson summary (under 5,000 words)

## 1. What this chapter teaches

A data structure organizes multiple values so that particular operations are efficient. The correct choice depends on what the program does repeatedly:

| Requirement | Best-fit structure |
|---|---|
| Preserve a sequence and access items by position | `list` |
| Find a value using an identifier/key | `dict` |
| Store unique values and check membership | `set` |
| Remove the newest item first (LIFO) | Stack, implemented with a `list` |
| Remove the oldest item first (FIFO) | Queue, implemented with `collections.deque` |

A data type describes one value (`int`, `str`, `bool`, `float`). A data structure describes how multiple values are organized. For example:

```python
age = 30                 # int: one value
ages = [30, 25, 40]       # list: multiple ordered values
```

A stack and queue are behaviours, not separate built-in Python types. Python lists can implement stacks; `collections.deque` is the recommended tool for queues.

## 2. Decide before writing code

Ask these questions about the workload:

1. Is this an ordered sequence?
2. Do I need key-to-value lookup?
3. Must values be unique?
4. Must the newest item be removed first (LIFO)?
5. Must the oldest item be removed first (FIFO)?
6. Will membership checks happen often?
7. Do I need indexed access?
8. Must insertion order be preserved?
9. Do I need efficient operations at the front, back, or both?
10. Which operation will happen most often?

Quick mapping:

```text
Key-based lookup       -> dictionary
Unique values          -> set
Ordered/indexed items  -> list
LIFO                   -> stack (list)
FIFO                   -> queue (deque)
```

A real program may need several structures together.

## 3. Lists: ordered, mutable sequences

```python
numbers = [10, 20, 30, 40]
print(numbers[0])    # 10: indexes start at zero
print(numbers[-1])   # 40: -1 means last item
print(numbers[1:3])  # [20, 30]: stop index 3 is excluded
```

A list is ordered, mutable, and allows duplicates. Slicing creates a new list; it does not change the original.

### List methods and operations

**`append(x)`** adds its argument as one item:

```python
items = [1, 2]
items.append(3)
print(items)  # [1, 2, 3]
```

**`extend(iterable)`** adds each item from the iterable:

```python
items = [1, 2]
items.extend([3, 4])
print(items)  # [1, 2, 3, 4]
```

The difference matters:

```python
items = [1, 2]
items.append([3, 4])
print(items)  # [1, 2, [3, 4]]: nested list; one new element

items = [1, 2]
items.extend([3, 4])
print(items)  # [1, 2, 3, 4]: two new elements
```

**`insert(index, x)`** inserts at a position and shifts later items right:

```python
items = [1, 2, 3]
items.insert(0, 0)
print(items)  # [0, 1, 2, 3]
```

**`remove(value)`** removes the first matching value, returns `None`, and raises `ValueError` if absent:

```python
items = [1, 2, 3, 2]
items.remove(2)
print(items)  # [1, 3, 2]
```

**`pop(index=-1)`** removes and returns the item at a position; by default it removes the last item:

```python
items = [1, 2, 3]
last = items.pop()      # 3; items becomes [1, 2]
first = items.pop(0)    # 1; items becomes [2]
```

**`remove`, `pop`, and `del`:**

```python
items = [10, 20, 30]
items.remove(20)       # remove by VALUE; no removed value returned
del items[0]           # remove by POSITION; no value returned
value = items.pop(0)   # remove by POSITION and return the value
```

**Other list operations:**

- `clear()` removes all items.
- `index(value)` returns the first matching index; raises `ValueError` if absent.
- `count(value)` counts occurrences.
- `copy()` creates a separate shallow copy.
- `sort()` sorts the same list in place and returns `None`.
- `reverse()` reverses the same list in place and returns `None`.
- `len(items)` returns the number of items.
- `value in items` checks membership.
- `del items[i]` deletes by index.

```python
original = [1, 2, 3]
duplicate = original.copy()
duplicate.append(4)
print(original)   # [1, 2, 3]
print(duplicate)  # [1, 2, 3, 4]
```

The copy is independent as a list, but `copy()` is shallow: nested mutable objects are not recursively copied.

### When lists fit

Use lists for ordered events, steps, results, duplicate-preserving data, indexed access, end-appending, and workloads that mostly iterate through items.

Avoid using a list for repeated lookup by ID, frequent membership checks, or FIFO removal from the front.

### List complexity: why the position matters

| Operation | Typical cost | Reason |
|---|---:|---|
| `items[i]` | O(1) | Direct index access |
| `append(x)` | O(1) amortized | Usually uses reserved capacity; occasional resize is spread across appends |
| `pop()` | O(1) | Removes the last item; no shifting |
| `insert(0, x)` | O(n) | Existing items shift right |
| `pop(0)` | O(n) | Remaining items shift left |
| `x in items` | O(n) worst case | May scan all items |
| `remove(value)` | O(n) | Search plus shifting |
| `count(value)` | O(n) | Must inspect every item |
| `index(value)` | O(n) | May scan from the beginning |

**Rule:** list operations at the end are cheap; insertion/removal near the front or middle can require shifting many elements.

## 4. Dictionaries: key-to-value lookup

A dictionary stores key-value pairs. You ask for a value using its key, not its position.

```python
user = {
    "id": 101,
    "name": "Alice",
    "email": "alice@example.com"
}
print(user["name"])  # Alice
```

`keys()`, `values()`, and `items()` return dynamic views, not lists:

```python
for key in user.keys():
    print(key)

for value in user.values():
    print(value)

for key, value in user.items():
    print(key, value)

print(list(user.keys()))  # explicitly create a list
```

### Dictionary operations

```python
user = {"id": 101, "name": "Alice"}

print(user["name"])             # direct lookup: Alice
# user["phone"]                 # KeyError if missing

print(user.get("phone"))        # None if missing
print(user.get("phone", "N/A")) # N/A if missing
```

Use `dict[key]` when the key must exist and absence is a bug. Use `get()` when absence is an expected possibility.

Other operations:

- `dict.update(other)` merges pairs and overwrites matching keys; mutates in place and returns `None`.
- `dict.setdefault(key, default)` returns the existing value or inserts and returns the default.
- `dict.pop(key)` removes and returns the value; absent key raises `KeyError` unless a default is supplied.
- `dict.popitem()` removes and returns the most recently inserted pair (Python 3.7+ insertion-order guarantee).
- `dict.clear()` removes all pairs.
- `dict.copy()` returns a shallow copy.
- `key in dict` checks keys, not values.
- `del dict[key]` removes a pair; missing key raises `KeyError`.
- `len(dict)` returns the number of pairs.

```python
user.update({"name": "Alicia", "active": True})
name = user.pop("name")
```

### Insertion and update

The same assignment inserts or updates depending on the dictionary's existing state:

```python
user = {"id": 101}
user["name"] = "Alice"    # insert: key was absent
user["name"] = "Alicia"   # update: key existed
```

Nested dictionaries are useful for records indexed by ID:

```python
users = {
    101: {"name": "Alice", "active": True},
    102: {"name": "Bob", "active": False}
}
print(users[101]["name"])  # Alice
users[101]["active"] = False
```

Use a dictionary when records have natural identifiers, repeated lookup matters, or you need counting/grouping (`word -> count`, `category -> total`, `customer_id -> customer`). Lookup, insertion, update, deletion, and key membership are typically O(1) average-case because of hashing. This is an average-case expectation, not an unconditional guarantee.

## 5. Sets: unique values and fast membership

A set is mutable and unordered, and stores unique hashable elements. Adding a duplicate does not create another element. Sets have no index and make no ordering promise.

```python
tags = {"python", "ai", "data"}
tags.add("data")  # already present: no change
```

Operations:

- `add(x)` adds an element; duplicate addition is harmless.
- `remove(x)` removes it; missing element raises `KeyError`.
- `discard(x)` removes it if present; missing element is harmless.
- `pop()` removes and returns an arbitrary element; empty set raises `KeyError`.
- `clear()` removes all elements.
- `copy()` creates a shallow copy.
- `len(s)` counts elements; `x in s` tests membership.

Choose `remove()` when presence is expected and absence indicates a problem; choose `discard()` when absence is normal.

### Set algebra

```python
a = {1, 2, 3}
b = {2, 3, 4}

a.union(b)                  # {1, 2, 3, 4}: in either set
a.intersection(b)           # {2, 3}: in both
a.difference(b)              # {1}: in a but not b
a.symmetric_difference(b)   # {1, 4}: in exactly one

a | b   # union
a & b   # intersection
a - b   # difference
a ^ b   # symmetric difference

{1, 2}.issubset({1, 2, 3})       # True
{1, 2, 3}.issuperset({1, 2})     # True
{1, 2}.isdisjoint({3, 4})       # True: no shared elements
```

Sets fit deduplication, repeated membership checks, visited IDs, permissions, unique customer IDs, and comparing groups. Do not use a set if positions, order, or duplicates matter. Set membership/add/remove/discard are O(1) average-case. A list membership check can be O(n); repeated checks can therefore turn an otherwise linear task into quadratic work. A set uses extra memory for its hash structure.

## 6. Stacks: LIFO

A stack behaves like a pile of plates: the newest item is removed first. This is **LIFO — Last In, First Out**.

```python
stack = []
stack.append("A")
stack.append("B")
stack.append("C")

item = stack.pop()
print(item)   # C
print(stack)  # ['A', 'B']
```

The conventional stack operations map to list operations:

| Stack action | Python | Cost |
|---|---|---:|
| Push | `stack.append(x)` | O(1) amortized |
| Pop | `stack.pop()` | O(1) |
| Peek without removal | `stack[-1]` | O(1) |
| Check empty | `not stack` or `len(stack) == 0` | O(1) |

Always guard against an empty stack: `pop()` and `stack[-1]` raise `IndexError`.

The lesson uses a unique sentinel so a real stored `None` is distinguishable from an empty result:

```python
EMPTY = object()

def safe_pop(stack):
    if not stack:
        return EMPTY
    return stack.pop()

def peek(stack):
    if not stack:
        return EMPTY
    return stack[-1]

stack = [None]
print(safe_pop(stack) is EMPTY)  # False: popped a real None
print(safe_pop(stack) is EMPTY)  # True: stack was empty
```

A caller checks identity with `is EMPTY`. Stack use cases include undo/redo, function-call returns, expression evaluation, matching parentheses, depth-first search/backtracking, and browser history. The latter algorithmic applications are conceptual here, not taught in depth.

Use the list's end as the stack top. `append()` and `pop()` there are O(1); using the front would introduce O(n) shifts.

## 7. Queues: FIFO and `deque`

A queue behaves like a checkout line. The oldest item is served first: **FIFO — First In, First Out**. Add with enqueue at the rear; remove with dequeue from the front.

A list can implement FIFO behavior, but it is inefficient at scale:

```python
queue = []
queue.append("A")
queue.append("B")
first = queue.pop(0)  # A, but every remaining item shifts left
```

Each `pop(0)` is O(n). Repeating front removals across a large workload can accumulate substantial shifting work.

Use `collections.deque` (pronounced “deck,” double-ended queue):

```python
from collections import deque

queue = deque()
queue.append("A")
queue.append("B")
first = queue.popleft()
print(first)  # A
print(queue)  # deque(['B'])
```

Core operations are O(1):

| Method | Effect |
|---|---|
| `append(x)` | Add right/rear |
| `appendleft(x)` | Add left/front |
| `pop()` | Remove and return right/back |
| `popleft()` | Remove and return left/front |

A deque is internally organized in blocks to support efficient operations at both ends. It is ideal for queues; arbitrary middle indexing is slower than list indexing.

Queue operations:

| Queue action | `deque` operation | Cost |
|---|---|---:|
| Enqueue | `queue.append(x)` | O(1) |
| Dequeue | `queue.popleft()` | O(1) |
| Peek front | `queue[0]` | O(1) |
| Check empty | `not queue` or `len(queue) == 0` | O(1) |

Guard an empty queue because `popleft()` and `queue[0]` raise `IndexError`:

```python
EMPTY = object()

def safe_dequeue(queue):
    if not queue:
        return EMPTY
    return queue.popleft()
```

Again, the sentinel distinguishes an empty queue from a real `None` item. A deque can also add left/remove right if a workload genuinely needs both ends.

Queue use cases include job/task processing, request handling, breadth-first search (conceptually), event processing, producer-consumer workflows, and scheduling.

## 8. Compare the structures

### Stack versus queue

| | Stack | Queue |
|---|---|---|
| Rule | LIFO | FIFO |
| Add | Top | Rear |
| Remove | Top | Front |
| Python implementation | List `append`/`pop()` | `deque` `append`/`popleft()` |
| Example | Undo history | Task queue |

Add A, B, C: stack pops C first; queue dequeues A first.

### List, dictionary, and set

| Feature | List | Dictionary | Set |
|---|---|---|---|
| Purpose | Ordered sequence | Key-value mapping | Unique membership |
| Duplicates | Allowed | Keys unique; values may repeat | Not retained |
| Access | Index | Key | Membership |
| Ordering | Preserves sequence | Insertion order (Python 3.7+) | No defined order |

A dictionary stores a value associated with a key; a set only answers whether a value is present. If every dictionary value is unused or merely `True`, a set may better express the requirement.

### List versus deque

Lists are strong at arbitrary indexed access and end operations. Deques are strong at both-end operations. Use a list for sequences and middle indexing; use a deque when efficient front operations are required.

## 9. Choosing structures for common problems

1. Ordered transactions → list; append is O(1) amortized.
2. Repeated customer lookup by ID → dictionary; build once in O(n) average-case, then lookup in O(1) average-case.
3. Remove duplicate IDs → set; O(n) average-case overall rather than a naive O(n²) list-membership pattern. If order matters, use a seen set plus an output list.
4. Check whether an ID was processed → set. Use a dictionary if metadata such as a timestamp must also be stored.
5. Process tasks in arrival order → deque; `popleft()` is O(1).
6. Undo latest action → list as stack; append/pop at end are O(1).
7. Access by position → list; O(1).
8. Find common elements → sets and intersection; average O(n + m), rather than nested-loop O(n × m).
9. Count occurrences → dictionary or `Counter`; one-pass O(n) average-case.
10. Group records by category → dictionary or `defaultdict(list)`; one-pass O(n) average-case.

## 10. Production systems combine structures

One structure does not need to perform every job. A system may use:

```python
from collections import deque

transactions = []               # arrival order
transactions_by_id = {}         # fast record lookup
seen_ids = set()                 # duplicate detection
pending_transactions = deque()  # FIFO processing
```

### Banking example

The lesson's banking model uses:

- `transaction_log`: list for audit/arrival order.
- `transactions_by_id`: dictionary for retrieving a transaction.
- `seen_transaction_ids`: set for duplicate rejection.
- `pending_queue`: deque for FIFO processing.
- `processed_ids`: set for checking completed work.

On receipt, check the ID in the set; if new, add it to the set and log, index it in the dictionary, and enqueue its ID. Processing removes the oldest ID with `popleft()`, marks it processed, and retrieves the record from the dictionary.

### Data engineering example

- Metadata dictionary maps source IDs to metadata.
- Seen-ID set prevents duplicate records.
- Deque holds records waiting for downstream processing.
- List accumulates the final ordered result.

The pipeline dequeues a record, looks up metadata with `.get()`, creates an enriched record, and appends it to output. The source example uses `{**record, "metadata": metadata}` to make a new dictionary containing the record fields plus/overriding the metadata field.

### AI/ML document example

- Set: unique document IDs.
- Dictionary: document ID to metadata.
- Deque: pending documents in FIFO order.
- Set: processed document IDs.
- List: ordered output.

The underlying design is the same as banking and data engineering: uniqueness uses a set, lookup uses a dictionary, FIFO uses a deque, and ordered output uses a list.

## 11. Memory trade-offs

- A list is relatively compact for general-purpose sequential storage.
- Dictionaries and sets use extra internal storage for hashing, trading memory for fast lookup/membership.
- Deque uses block-based storage to make both ends efficient, with some overhead compared with a plain list.
- A set removes duplicates, so information about repeated occurrences is lost.
- Building an index/set costs time and memory up front but can avoid expensive repeated scans later.

Do not choose a dictionary or set automatically. For a tiny collection with rare lookups, a list may be simpler and adequate. Choose based on actual workload and operation frequency.

## 12. Common beginner mistakes

**Lists**
1. Repeatedly searching a list by ID instead of building a dictionary index.
2. Using `pop(0)` as a large queue instead of `deque`.
3. Confusing `append()` with `extend()`.
4. Confusing `remove(value)` with `pop(index)`.
5. Modifying a list while iterating, which can skip or repeat items.

**Dictionaries**
6. Using a list when key lookup is required.
7. Assuming `dict[key]` returns `None` when missing; it raises `KeyError`.
8. Forgetting that `for x in dict` iterates keys; use `.values()` or `.items()` when needed.
9. Misunderstanding `.get()` and its default (`None` unless supplied).

**Sets**
10. Trying to use indexes such as `some_set[0]`.
11. Expecting duplicates to be preserved.
12. Using `remove()` when an item may be absent; use `discard()` if absence is normal.
13. Treating a set as a drop-in list replacement despite lost order/duplicates.

**Stacks and queues**
14. Removing from the wrong end of a stack; use `append()` and `pop()` at the same end.
15. Peeking an empty stack; guard before `stack[-1]`.
16. Using `list.pop(0)` for a queue; use `deque.popleft()`.
17. Confusing FIFO with LIFO.

**General**
18. Choosing a structure only because it is familiar.
19. Ignoring operation complexity and input size.
20. Ignoring memory overhead.
21. Choosing by convenient syntax instead of the full set of requirements.

## 13. Edge cases to check

- Empty list: iteration is fine; `pop()`/`pop(0)` raise `IndexError`.
- Empty dict: `dict[key]` raises `KeyError`; `.get()` safely returns its default.
- Empty set: `.pop()` raises `KeyError`.
- Empty stack: `pop()`/`[-1]` raise `IndexError`.
- Empty queue: `popleft()`/`[0]` raise `IndexError`.
- Duplicate list values are preserved; duplicate dictionary keys overwrite earlier values; duplicate set values collapse.
- `None` can be a valid item/value in these structures. Use a unique sentinel if `None` must be distinguishable from “no item.”
- Removing an absent list value with `remove()` raises `ValueError`; dict deletion raises `KeyError`; set `remove()` raises `KeyError`; set `discard()` is safe.
- Mutating a list while iterating may skip/repeat items. Adding/removing dictionary keys or set elements during iteration can raise `RuntimeError` because the collection changed size.
- Large lists retain cheap indexing/end operations but front operations grow with collection size. Dict/set lookups and deque end operations remain typically efficient under the chapter's average-case assumptions.

## 14. The 12-step selection process

1. Identify what the data represents.
2. Identify the most common operations.
3. Decide whether order matters.
4. Decide whether duplicates matter.
5. Determine whether lookup by key is needed.
6. Determine whether membership checks dominate.
7. Determine whether LIFO or FIFO is needed.
8. Estimate input size.
9. Compare the time costs of candidate structures.
10. Consider memory overhead.
11. Choose the simplest structure that satisfies the real requirements.
12. Validate it against realistic and much larger workloads.

## 15. Mini-project architecture and final takeaways

The source mini-project is a transaction engine with nine requirements: preserve arrival order, reject duplicate IDs, index by ID, queue pending work, track processed work, support lookup, process FIFO, undo the most recently processed action, and produce ordered output.

Its structures are: arrival-log list; ID dictionary; seen-ID set; pending deque; processed-history list used as a stack; final-result list. Ingestion performs set membership, set add, list append, dictionary insert, and deque append. Processing dequeues, looks up, pushes to history, and appends to output. Undo pops the history stack and final-result list.

The chapter's interview themes include data type versus data structure, list/dict/set selection, LIFO/FIFO, why `pop(0)` is inefficient, why deque works, average-case hashing, append versus extend, remove versus pop, safe missing-key access, and designing combined transaction/document pipelines.

**Decision-table recap:** list for ordered/indexed sequence; dict for key lookup; set for uniqueness/membership; list-as-stack for LIFO; deque for FIFO and both-end operations; dict/defaultdict for grouping; set/dict strategy for deduplication.

**Core principle:** name the operation that will happen most often, choose the structure that makes it efficient, then account for order, duplicates, input size, and memory.

---

# Part B — Your current learning level and roadmap alignment

Your Stage 1 roadmap places this lesson in **Module 04 — Problem-Solving, Collections, and Algorithmic Habits**, after:
- Module 01: computational thinking, algorithms, variables, input/process/output, decomposition, preconditions, dry runs, and state.
- Module 02: Python core types, strings, lists, tuples, dictionaries, sets, conversion, and mutability.
- Module 03: conditionals, Boolean logic, loops, functions, arguments, scope, pure functions, validation, and exceptions.
- Earlier Module 04 lessons: search/count/filter/map/aggregate, then grouping/deduplication/sorting, then Big-O.

The broader Stage 1 tree contains 24 modules, 212 numbered lessons, and four stage-level projects. Later topics include files/CLI, modules, testing, OOP, advanced Python, profiling, packaging, internals, security, and code review. A roadmap shows intended sequence; it does not prove that every later lesson has been completed.

**Assessment:** beginner progressing toward intermediate. You have the prerequisites to learn the five structures and reason about their operations and Big-O costs. The key skill to practise is explaining *why* a structure fits the workload, rather than memorizing a method name.

**Solution scope:** the exercise answers below use variables, `if`, loops, functions, lists, dictionaries, sets, indexing, `append`, `pop`, `get`, `deque`, and basic Big-O reasoning. The source mini-project presents a class, but OOP belongs to a later roadmap stage; its equivalent is shown with ordinary functions and shared collections. No pandas, SQL, Spark, recursion, comprehensions, or advanced abstractions are required.

---

# Part C — All 20 progressive exercises solved (under 2,000 words)

## Level 1 — Beginner

### 1. Add three names and print the last

```python
names = ["Alice", "Bob"]       # create ordered list
names.append("Charlie")        # add one name at the end
names.append("Diana")
names.append("Eve")
print(names[-1])               # -1 means the final item: Eve
```

### 2. Map user IDs to names

```python
users = {101: "Alice", 102: "Bob", 103: "Charlie"}  # ID -> name
print(users[102])                                  # key lookup: Bob
```

### 3. Remove duplicate numbers

```python
numbers = [4, 2, 4, 1, 2, 3]
unique = set(numbers)     # set keeps one of each value
print(unique)             # {1, 2, 3, 4}; order is not guaranteed
```

### 4. Implement a stack

```python
stack = []
stack.append("A")         # push A
stack.append("B")         # push B
stack.append("C")         # push C
print(stack.pop())        # C: last in, first out
print(stack.pop())        # B
```

### 5. Implement a queue

```python
from collections import deque
queue = deque()
queue.append("task1")     # enqueue at rear
queue.append("task2")
queue.append("task3")
print(queue.popleft())    # task1: first in, first out
print(queue.popleft())    # task2
```

## Level 2 — Intermediate

### 6. Choose the best structure

(a) Shopping cart order → **list**, because order and repeated items can matter.  
(b) Phone book name-to-number → **dict**, because a name is the lookup key.  
(c) Taken usernames → **set**, because only unique membership matters.  
(d) Printer jobs → **deque**, because jobs are processed FIFO.  
(e) Text-editor undo → **list as stack**, because the latest action is undone first.  
(f) Leaderboard with duplicate scores → **list**, because duplicates must remain.  
(g) Frequently checked IP blocklist → **set**, for O(1) average membership.  
(h) Orders grouped by customer → **dict of lists**, customer key maps to their orders.  
(i) Browser back history → **list as stack**, latest page is returned to first.  
(j) Online user IDs → **set**, because the question is whether an ID is present.

### 7. Build a dictionary index for repeated user lookup

```python
users_by_id = {}
for user in users:                         # visit each user once
    users_by_id[user["id"]] = user         # store record under its ID

for target_id in target_ids:               # perform 1,000 lookups
    found = users_by_id.get(target_id)     # average O(1) lookup
```

Building the index costs O(n) average-case. Then 1,000 lookups cost O(1,000) average-case. Repeated linear scans could cost O(1,000 × 100,000).

### 8. Flag repeated order IDs

```python
seen = set()
duplicate_ids = []

for order_id in incoming_order_ids:  # inspect each ID
    if order_id in seen:             # already appeared?
        duplicate_ids.append(order_id)
    else:
        seen.add(order_id)            # remember first occurrence

print(duplicate_ids)
```

### 9. Safe undo function

```python
def undo(stack):
    if not stack:       # empty stack guard
        return None
    return stack.pop()  # remove and return newest action
```

### 10. Process tasks until the queue is empty

```python
from collections import deque
tasks = deque()
tasks.append("task1")
tasks.append("task2")
tasks.append("task3")

while tasks:                          # continue while work remains
    current = tasks.popleft()         # remove oldest task
    print("Processing:", current)
```

## Level 3 — Advanced

### 11. Index transactions by ID

```python
transactions_by_id = {}
for transaction in transactions:
    transactions_by_id[transaction["id"]] = transaction

print(transactions_by_id["T1"])
print(transactions_by_id["T2"])
print(transactions_by_id["T3"])
```

Each record is stored under its ID; subsequent lookups are O(1) average-case.

### 12. Keep only the first record for each ID

```python
processed_ids = set()
unique_records = []

for record in incoming_records:
    record_id = record["id"]
    if record_id not in processed_ids:
        processed_ids.add(record_id)
        unique_records.append(record)
```

The set checks uniqueness; the list preserves the arrival order of accepted records.

### 13. Process transactions FIFO and track IDs

```python
from collections import deque
pending = deque(transactions)
processed_ids = set()

while pending:
    transaction = pending.popleft()        # oldest first
    processed_ids.add(transaction["id"])   # record completion
    print("Processed", transaction["id"])
```

### 14. Combine dict, set, and deque

```python
from collections import deque
records_by_id = {}
seen_ids = set()
pending = deque()

for record in incoming_records:
    record_id = record["id"]
    if record_id in seen_ids:
        continue
    seen_ids.add(record_id)                # duplicate gate
    records_by_id[record_id] = record      # fast lookup
    pending.append(record)                 # arrival-order queue

while pending:
    record = pending.popleft()
    print("Processing", records_by_id[record["id"]])
```

### 15. Compare list and set membership

```python
def contains_list(collection, target):
    return target in collection            # O(n) worst case

def contains_set(collection, target):
    return target in collection            # O(1) average-case

ids_list = [101, 102, 103, 104]
ids_set = set(ids_list)                    # prepare hash set

print(contains_list(ids_list, 103))
print(contains_set(ids_set, 103))
```

The answers are the same; the lookup cost differs. A list may scan every element, while a set uses hashing. Converting once has a cost, so the advantage is strongest when membership is checked repeatedly.

## Level 4 — Production-oriented

### 16. Event intake with uniqueness and FIFO

```python
from collections import deque
seen_event_ids = set()
event_queue = deque()

def submit_event(event):
    if event["id"] in seen_event_ids:
        return False
    seen_event_ids.add(event["id"])
    event_queue.append(event)
    return True

def process_event():
    if not event_queue:
        return None
    return event_queue.popleft()
```

The set rejects duplicates; the deque preserves FIFO processing. Both end operations are O(1) average/typical.

### 17. Group logs by service, preserving each group's order

```python
logs_by_service = {}

for entry in log_entries:
    service = entry["service"]
    if service not in logs_by_service:
        logs_by_service[service] = []
    logs_by_service[service].append(entry)
```

The dictionary maps each service to a list. Appending preserves that service's arrival order.

### 18. Banking transaction design

Use a list for arrival/audit order, a dictionary for transaction-ID lookup, a set for duplicate rejection, a deque for FIFO pending work, and optionally a list-as-stack for undo. Each structure handles a distinct requirement. Test duplicate IDs, unknown lookups, and empty queue/stack cases.

### 19. AI document queue

```python
from collections import deque
known_ids = set()
metadata_by_id = {}
pending_documents = deque()
processed_ids = set()
ordered_output = []

def submit_document(document):
    doc_id = document["id"]
    if doc_id in known_ids:
        return False
    known_ids.add(doc_id)
    metadata_by_id[doc_id] = document.get("metadata", {})
    pending_documents.append(document)
    return True

def process_documents():
    while pending_documents:
        document = pending_documents.popleft()
        doc_id = document["id"]
        processed_ids.add(doc_id)
        ordered_output.append({
            "id": doc_id,
            "metadata": metadata_by_id[doc_id]
        })
```

The set enforces unique IDs; dictionary retrieves metadata; deque processes FIFO; output list preserves processing order.

### 20. Multi-source data-ingestion design

Use a set (or a set per source if IDs are only unique within each source) for deduplication, a dictionary keyed by source ID for metadata, and a list for final ordered output. During ingestion, reject seen record IDs; during processing, use `.get(source_id)` so unknown metadata can deliberately become `None`; append processed records to the output list. A single list would make repeated membership/lookup slower; a dictionary alone does not directly express the final ordered output requirement.

---

# Part D — Mini-project: Transaction Processing Data-Structure Engine

The source mini-project combines arrival order, uniqueness, ID lookup, FIFO processing, processed history, undo, and final ordered output. Because classes/OOP are later in your roadmap, this version uses functions and shared collections while preserving the same data-structure design.

```python
from collections import deque

arrival_log = []
transactions_by_id = {}
seen_ids = set()
pending_queue = deque()
processed_stack = []
final_result = []

def receive(transaction):
    transaction_id = transaction["id"]
    if transaction_id in seen_ids:
        return False

    seen_ids.add(transaction_id)
    arrival_log.append(transaction)
    transactions_by_id[transaction_id] = transaction
    pending_queue.append(transaction_id)
    return True

def process_next():
    if not pending_queue:
        return None

    transaction_id = pending_queue.popleft()
    transaction = transactions_by_id[transaction_id]
    processed_stack.append(transaction)
    final_result.append(transaction)
    return transaction

def undo_last_processed():
    if not processed_stack:
        return None

    transaction = processed_stack.pop()
    final_result.pop()
    return transaction

def lookup(transaction_id):
    return transactions_by_id.get(transaction_id)
```

**Dry run:**

```python
receive({"id": "T1", "amount": 100})   # accepted
receive({"id": "T2", "amount": 250})   # accepted
receive({"id": "T1", "amount": 999})   # rejected duplicate

process_next()   # T1
process_next()   # T2
print(final_result)
# [{'id': 'T1', 'amount': 100}, {'id': 'T2', 'amount': 250}]

undo_last_processed()                  # removes T2 from processed output
print(final_result)
# [{'id': 'T1', 'amount': 100}]

print(lookup("T1"))
# {'id': 'T1', 'amount': 100}
```

**Complexity:** receive is O(1) average-case/amortized per transaction; process is O(1) per transaction under the stated assumptions; undo is O(1) because it pops from the end of two lists; lookup is O(1) average-case. The arrival log and lookup index deliberately remain after undo: undo reverses the latest processed output/history action, not the original receipt.

---

# Part E — Final revision checklist

Before choosing a structure, make sure you can answer:

- Does order matter? Do duplicates matter?
- Do I need a position, a key, or only membership?
- Is the behavior LIFO or FIFO?
- Is the workload dominated by lookup, membership, insertion, removal, or iteration?
- What are the average/worst-case time costs?
- Is the extra memory for a set/dictionary justified?
- Have I handled empty structures, missing keys, duplicate IDs, and `None` values?
- Can I justify using more than one structure when the system has multiple requirements?

**Stop point:** this completes the lesson and its exercises. Do not move to the next roadmap topic until you can independently explain why each chosen structure fits its operation.
