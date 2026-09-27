# Counter, defaultdict, and deque

> **Stage 1 — Programming & Computational Thinking**  
> **Module:** `09-Advanced-Production-Oriented-Python-Foundations`  
> **Target file:** `08-counter-defaultdict-and-deque.md`

## Learning objective

This chapter develops three specialized containers from Python's standard library:

- `collections.Counter`
- `collections.defaultdict`
- `collections.deque`

The goal is not to memorize method names. The goal is to recognize an access pattern, select a suitable data structure, understand its semantics, reason about its time and memory behavior, and use it safely inside production-oriented Python systems.

The teaching progression is:

**problem → reason the structure exists → simpler alternative → basic syntax → execution model → API → complexity → mistakes → debugging → testing → production use → Applied AI Engineering → architecture decisions → exercises → final mental model**

## What you should be able to answer

By the end, you should be able to explain:

1. What problem `Counter` solves.
2. Why `Counter` is more expressive than a manual counting dictionary.
3. Why `defaultdict` exists and when automatic initialization is useful.
4. How `defaultdict` handles a missing key.
5. Why `d[key]` and `d.get(key)` behave differently for `defaultdict`.
6. Why `deque` is appropriate for FIFO queues and bounded buffers.
7. Why repeated `list.pop(0)` operations are a poor fit for large FIFO workloads.
8. Which operations are typically constant-time, linear-time, or workload-dependent.
9. Why an in-memory collection is not a database, durable queue, or distributed state store.
10. How these structures appear in data engineering, backend systems, ML pipelines, and Applied AI systems.

---

# Part I — Why specialized collections exist

## 1. Why Specialized Collections Exist

Python's built-in containers are powerful:

| Type | Main idea | Typical use |
|---|---|---|
| `list` | ordered mutable sequence | general sequences |
| `dict` | key → value mapping | lookups and associations |
| `set` | unique collection | membership and uniqueness |
| `tuple` | ordered immutable sequence | fixed records / immutable sequences |

Specialized collections exist because common workloads repeatedly need behavior that is more specific than a generic list or dictionary.

Three recurring patterns are:

```text
How many times did each thing occur?
    → Counter

What should I automatically create for a new key?
    → defaultdict

How do I add/remove from either end efficiently?
    → deque
```

### Manual counting with a dictionary

```python
items = ["apple", "banana", "apple", "orange", "banana", "apple"]

counts = {}

for item in items:
    if item not in counts:
        counts[item] = 0
    counts[item] += 1

print(counts)
```

Output:

```text
{'apple': 3, 'banana': 2, 'orange': 1}
```

This is correct. It is also a reusable pattern.

### Manual grouping with a dictionary

```python
records = [
    ("fruit", "apple"),
    ("fruit", "banana"),
    ("vehicle", "car"),
]

groups = {}

for key, value in records:
    if key not in groups:
        groups[key] = []
    groups[key].append(value)

print(groups)
```

The repeated initialization pattern is exactly what `defaultdict` can express.

### List used as a queue

```python
queue = []

queue.append("job-1")
queue.append("job-2")
queue.append("job-3")

job = queue.pop(0)

print(job)
```

The logical result is correct, but `pop(0)` requires the remaining list elements to move. For repeated FIFO removal, `deque.popleft()` is a much better match to the access pattern.

### Engineering lesson

A specialized collection is not merely a "faster container." It communicates a specific **semantic intent**.

---

## 2. The `collections` Module

The `collections` module provides specialized container datatypes as alternatives to Python's general-purpose built-ins. The current Python documentation lists `deque`, `Counter`, and `defaultdict` among these specialized types. citeturn838217view0

```python
from collections import Counter, defaultdict, deque
```

Conceptually:

```text
collections
    |
    +-- Counter
    |     |
    |     +-- element → count
    |
    +-- defaultdict
    |     |
    |     +-- key → factory-created value
    |
    +-- deque
          |
          +-- left ← sequence → right
```

These structures can make code:

- shorter;
- clearer;
- more expressive;
- better aligned with a workload.

But specialization is valuable only when the semantics actually fit the problem.

---

# Part II — Counter

## 3. Counter Fundamentals

`Counter` is a dictionary subclass designed for counting hashable objects. Elements are stored as keys and their counts as dictionary values. Counts may be positive, zero, or negative. citeturn838217view0

```python
from collections import Counter

counts = Counter(["apple", "banana", "apple"])

print(counts)
print(counts["apple"])
print(counts["banana"])
```

Typical output:

```text
Counter({'apple': 2, 'banana': 1})
2
1
```

Conceptually:

```text
apple  → 2
banana → 1
```

### Why use Counter?

Use it when the main question is:

> How often did each item occur?

Examples:

- event counts;
- error counts;
- status-code frequency;
- class-label distribution;
- token frequency;
- tool-call outcomes.

### What would we do without it?

A normal dictionary is enough:

```python
counts = {}

for value in values:
    counts[value] = counts.get(value, 0) + 1
```

`Counter` adds counting-specific semantics and operations.

---

## 4. What Is a Hashable Element?

Counter keys follow normal mapping-key rules: the element must be hashable.

Common examples:

```python
Counter(["a", "b", "a"])
Counter([1, 2, 1])
Counter([("region", "east"), ("region", "east")])
```

A mutable list is not suitable as a dictionary key:

```python
# Counter([[1, 2], [1, 2]])  # TypeError
```

If a mutable sequence is logically the identity of an item, a tuple may be suitable:

```python
Counter([(1, 2), (1, 2), (3, 4)])
```

Do not confuse "iterable" with "hashable":

```text
Counter input → iterable of elements
Each element → must be usable as a mapping key
```

---

## 5. Creating Counter Objects

### Empty Counter

```python
from collections import Counter

counts = Counter()
print(counts)
```

Result:

```text
Counter()
```

Use this when counts will be accumulated incrementally.

### `Counter(iterable)`

```python
counts = Counter("banana")
print(counts)
```

A string is an iterable of characters.

### `Counter(mapping)`

```python
counts = Counter({"a": 3, "b": 2})
print(counts)
```

Here the mapping values are initial counts.

### `Counter(**kwargs)`

```python
counts = Counter(a=3, b=2)
print(counts)
```

Useful for small, explicit examples.

### Constructor comparison

| Constructor | Meaning | Example |
|---|---|---|
| `Counter()` | empty | `Counter()` |
| `Counter(iterable)` | count iterable elements | `Counter("banana")` |
| `Counter(mapping)` | use mapping values as counts | `Counter({"a": 3})` |
| `Counter(**kwargs)` | keyword counts | `Counter(a=3)` |

### Common mistake

Do not confuse a mapping containing counts with a sequence that should itself be counted.

```python
data = {"a": 3, "b": 2}

counts = Counter(data)
```

The resulting counts are based on the mapping values already supplied.

---

## 6. Counter with Strings

```python
from collections import Counter

counts = Counter("mississippi")

print(counts["s"])
print(counts["i"])
print(counts["p"])
```

Expected:

```text
4
4
2
```

The string is iterated character-by-character.

### Unicode note

Counter counts whatever elements are produced by iteration. For a string, that means Python string elements, not necessarily linguistic grapheme clusters. This matters in internationalized text processing: "character frequency" can mean different things at different abstraction levels.

---

## 7. Counter with Lists and Domain Data

### Event types

```python
events = [
    "success",
    "failure",
    "success",
    "timeout",
]

counts = Counter(events)

print(counts)
```

### Log levels

```python
levels = ["INFO", "INFO", "ERROR", "WARNING", "ERROR", "ERROR"]

level_counts = Counter(levels)

print(level_counts["ERROR"])
```

Result:

```text
3
```

### Model labels

```python
predicted_labels = [
    "positive",
    "negative",
    "positive",
    "neutral",
    "positive",
]

label_counts = Counter(predicted_labels)

print(label_counts)
```

### Tokens

```python
tokens = ["the", "model", "uses", "the", "tool", "model"]

token_counts = Counter(tokens)

print(token_counts.most_common(3))
```

This is useful for local document statistics, evaluation summaries, and diagnostics.

---

## 8. Counter Lookup and Missing Values

A normal dictionary raises `KeyError` for a missing key:

```python
data = {"a": 10}

# data["missing"]  # KeyError
```

A Counter returns zero:

```python
from collections import Counter

counts = Counter(["a", "a", "b"])

print(counts["a"])
print(counts["missing"])
```

Output:

```text
2
0
```

The zero is part of Counter's counting semantics. citeturn838217view0

### Zero is not the same as membership

```python
counts = Counter(["a"])

print(counts["missing"])
print("missing" in counts)
```

Output:

```text
0
False
```

So:

```text
lookup result = 0
stored key     = no
```

### Explicit zero

```python
counts["unseen"] = 0

print(counts["unseen"])
print("unseen" in counts)
```

Now the key exists.

The documentation distinguishes assigning zero from deleting an entry: a zero-valued entry remains stored until deleted. citeturn838217view0

---

## 9. `elements()`

`elements()` returns an iterator that repeats each element according to its count.

```python
counts = Counter(a=3, b=2)

print(list(counts.elements()))
```

Output:

```text
['a', 'a', 'a', 'b', 'b']
```

### Important behavior

- It returns an iterator.
- Positive integer counts control repetition.
- Zero counts are ignored.
- Negative counts are ignored.
- It preserves encounter order for emitted elements.

```python
counts = Counter(a=3, b=0, c=-2)

print(list(counts.elements()))
```

Output:

```text
['a', 'a', 'a']
```

The current documentation specifies that `elements()` requires integer counts and ignores values below one. citeturn838217view0

### Production caution

Do not expand a giant Counter into a list just because `elements()` exists. If the total number of represented occurrences is huge, materializing them can create an unnecessary memory spike.

---

## 10. `most_common()`

`most_common()` returns `(element, count)` pairs ordered from most common to least common.

```python
counts = Counter(["error", "info", "error", "warning", "error", "info"])

print(counts.most_common())
```

Typical output:

```text
[('error', 3), ('info', 2), ('warning', 1)]
```

### Top N

```python
print(counts.most_common(2))
```

Result:

```text
[('error', 3), ('info', 2)]
```

### Common uses

```text
top error types
top labels
top tokens
top event categories
top model outcomes
```

### Tie ordering

Modern Python documentation specifies that equal-count items retain first-encounter order. citeturn838217view0

### Zero

```python
print(counts.most_common(0))
```

Result:

```text
[]
```

For top-N questions, use the API directly rather than sorting a separately materialized list unless the broader algorithm requires it.

---

## 11. `total()`

`total()` computes the arithmetic sum of the stored counts.

```python
counts = Counter(a=10, b=5, c=0)

print(counts.total())
```

Output:

```text
15
```

`Counter.total()` was added in Python 3.10. citeturn838217view0

### `len()` versus `total()`

```python
counts = Counter(a=10, b=5)

print(len(counts))
print(counts.total())
```

Output:

```text
2
15
```

Interpretation:

```text
len(counts) → number of stored keys
total()     → sum of their counts
```

### Signed counts

```python
counts = Counter(a=5, b=-2)

print(counts.total())
```

Result:

```text
3
```

`total()` is arithmetic summation, not "number of positive entries."

---

## 12. `update()`

This is one of the most important Counter-specific APIs.

`Counter.update()` **adds** counts rather than replacing values as `dict.update()` normally does. citeturn838217view0

### Iterable form

```python
counts = Counter(["a", "b"])

counts.update(["a", "a", "c"])

print(counts)
```

Result:

```text
Counter({'a': 3, 'b': 1, 'c': 1})
```

### Mapping form

```python
counts = Counter(a=2, b=1)

counts.update({"a": 4, "b": 5})

print(counts)
```

Result:

```text
Counter({'a': 6, 'b': 6})
```

### Contrast with `dict.update()`

```python
data = {"a": 2}
data.update({"a": 4})
print(data)
```

Result:

```text
{'a': 4}
```

But:

```python
counts = Counter(a=2)
counts.update({"a": 4})
print(counts)
```

Result:

```text
Counter({'a': 6})
```

### Critical distinction

```text
Counter.update() → accumulate
dict.update()   → replace existing mapping values
```

If you need assignment:

```python
counts["a"] = 4
```

---

## 13. `subtract()`

`subtract()` decrements counts and may retain zero or negative values. citeturn838217view0

```python
counts = Counter(a=5, b=2)

counts.subtract({"a": 2, "b": 4})

print(counts)
```

Result:

```text
Counter({'a': 3, 'b': -2})
```

### Iterable form

```python
counts = Counter(["a", "a", "b"])

counts.subtract(["a", "b"])

print(counts)
```

Result:

```text
Counter({'a': 1, 'b': 0})
```

### Compare to binary subtraction

```python
left = Counter(a=1)
right = Counter(a=3)

print(left - right)
```

The negative result is not retained.

Use:

```python
result = Counter(a=1)
result.subtract(right)
```

when signed differences matter.

---

## 14. Counter Arithmetic

The main multiset-style operations are:

```python
c1 + c2
c1 - c2
c1 & c2
c1 | c2
```

The current documentation defines these as count addition, positive-only subtraction, minimum, and maximum, respectively. Results from these multiset operations keep only positive counts. citeturn838217view0

### Addition

```python
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)

print(c1 + c2)
```

Result:

```text
Counter({'a': 4, 'b': 3})
```

### Subtraction

```python
print(c1 - c2)
```

Conceptually:

```text
a → 3 - 1 = 2
b → 1 - 2 = -1
```

The result keeps:

```text
a → 2
```

and drops `b`.

### Intersection

```python
print(c1 & c2)
```

Conceptually:

```text
a → min(3, 1) = 1
b → min(1, 2) = 1
```

### Union

```python
print(c1 | c2)
```

Conceptually:

```text
a → max(3, 1) = 3
b → max(1, 2) = 2
```

### Unary operations

```python
c = Counter(a=2, b=-4)

print(+c)
print(-c)
```

Result:

```text
Counter({'a': 2})
Counter({'b': 4})
```

Unary plus keeps positive counts; unary minus inverts signed counts and keeps the positive results. citeturn838217view0

---

## 15. Counter Rich Comparisons

Modern Python supports:

```text
==
!=
<
<=
>
>=
```

for Counter objects. These comparisons treat missing elements as zero counts. Rich comparisons were added in Python 3.10, and Counter equality changed in that release to treat missing elements as zero. citeturn838217view0

```python
required = Counter(cpu=4, memory=16)
available = Counter(cpu=8, memory=32)

print(required <= available)
```

Result:

```text
True
```

This can model a count-based "required resources fit within available resources" question when the domain semantics truly match.

### Explicit zero and absent key

```python
Counter(a=1) == Counter(a=1, b=0)
```

is `True` in modern Python.

### Version caution

Do not assume that code relying on rich Counter comparison semantics behaves identically on pre-3.10 Python.

---

## 16. Zero and Negative Counts

Counter can store:

```text
positive counts
zero counts
negative counts
```

Example:

```python
c = Counter(a=3)

c["a"] -= 5

print(c["a"])
```

Output:

```text
-2
```

### Why allow negatives?

Counter is primarily intended for positive tallies, but the standard library permits signed numeric counts to support useful applications such as deltas and reconciliation. citeturn838217view0

### Cleaning non-positive counts

```python
c = Counter(a=3, b=0, c=-2)

print(+c)
```

Result:

```text
Counter({'a': 3})
```

### Important semantic distinction

```text
Counter mutation / subtract()
    → can preserve zero and negative values

Counter multiset operators
    → output only positive results
```

Do not choose an operator until you know which behavior you want.

---

## 17. Counter as a Dictionary-Like Structure

Counter supports familiar mapping operations.

```python
counts = Counter(a=3, b=2)

print(list(counts.keys()))
print(list(counts.values()))
print(list(counts.items()))
```

### Iteration

```python
for element in counts:
    print(element)
```

Iteration is over stored keys/elements.

### Membership

```python
print("a" in counts)
print("missing" in counts)
```

Membership tests key presence, not whether its count is positive.

### Conversion

```python
regular_dict = dict(counts)

print(regular_dict)
```

The conversion preserves the stored keys and values, including zero or negative values.

### `len()`

```python
print(len(counts))
```

This counts stored entries, not total occurrences.

---

## 18. Counter Dictionary-Like APIs

### `get()`

```python
counts = Counter(a=2)

print(counts.get("a"))
print(counts.get("missing"))
print(counts.get("missing", 99))
```

The important point is that `get()` is the optional-lookup method, while:

```python
counts["missing"]
```

uses Counter's zero-count semantics.

### `setdefault()`

```python
counts = Counter()

value = counts.setdefault("a", 0)

print(value)
print(counts)
```

This is available as a dictionary operation. It is not the primary Counter idiom for frequency counting.

### `pop()`

```python
counts = Counter(a=3, b=2)

removed = counts.pop("a")

print(removed)
print(counts)
```

An optional default can be provided:

```python
removed = counts.pop("missing", 0)
```

### `popitem()`

```python
counts = Counter(a=3, b=2)

item = counts.popitem()

print(item)
print(counts)
```

This removes and returns a stored mapping entry. It does **not** mean "remove the most common item."

### `clear()`

```python
counts.clear()
```

Removes all stored entries.

### `copy()`

```python
other = counts.copy()
```

Creates a shallow copy of the Counter container.

### `update()`

Already covered: it accumulates counts.

### `fromkeys()`

`Counter` does not implement the normal `dict.fromkeys()` class method. The standard-library documentation explicitly calls this out. citeturn838217view0

This is an important reminder:

```text
Counter is a dict subclass
≠
Counter has identical behavior for every dict API
```

---

## 19. Counter Performance

For hash-based mappings, individual lookup and update operations are typically expected O(1) average time.

If an input has:

```text
n = total input elements
u = distinct elements
```

then building:

```python
Counter(iterable)
```

conceptually requires:

```text
time   → O(n)
memory → O(u) for stored key/count entries
```

### Lookup

```python
counts[item]
```

is a mapping lookup, typically expected O(1).

### Update

A batch of `m` incoming elements requires work proportional to the number of supplied elements:

```text
update(batch) ≈ O(m)
```

subject to ordinary hash-table behavior.

### `most_common()`

Ranking work depends on:

- number of distinct elements;
- requested `n`;
- implementation strategy.

For a production system, do not assume a specific top-N algorithm unless you have verified the Python implementation/version. Benchmark the workload that matters.

### Practical principle

Use Counter because it matches the frequency-counting problem, not because it is guaranteed to beat every hand-written dictionary in every workload.

---

## 20. Counter Use Cases

### Word frequency

```python
text = "ai systems need reliable systems"

counts = Counter(text.split())

print(counts.most_common())
```

### Character frequency

```python
Counter("engineering")
```

### Event frequency

```python
events = ["success", "error", "success", "timeout", "error"]

event_counts = Counter(events)
```

### HTTP status counts

```python
status_codes = [200, 200, 500, 404, 200, 500]

status_counts = Counter(status_codes)
```

### Model prediction distribution

```python
predicted_labels = ["A", "B", "A", "A", "C"]

distribution = Counter(predicted_labels)
```

### Data-quality anomalies

```python
issues = [
    "missing_id",
    "invalid_email",
    "missing_id",
    "unknown_country",
]

issue_counts = Counter(issues)
```

### Agent action frequency

```python
actions = ["search", "search", "tool_call", "search", "respond"]

action_counts = Counter(actions)
```

---

## 21. Counter in Data Engineering

A pipeline often needs compact summary statistics.

```python
validation_results = [
    "accepted",
    "accepted",
    "missing_id",
    "invalid_email",
    "missing_id",
    "accepted",
]

counts = Counter(validation_results)

print(counts)
```

You can then derive:

```python
rejected = counts["missing_id"] + counts["invalid_email"]

print(rejected)
```

Typical uses:

- rejected-record summaries;
- validation failure counts;
- pipeline health checks;
- partition statistics;
- anomaly summaries.

### Important architecture boundary

The Counter is a local aggregation object. It is not the durable source of truth.

A production pipeline may:

```text
raw events
    → durable log/storage
    → processing
    → Counter for local aggregation
    → exported metrics
```

---

## 22. Counter in Applied AI

### Prediction distribution

```python
prediction_counts = Counter(predicted_labels)
```

This can reveal whether predictions are highly skewed toward one label.

### Tool-call outcomes

```python
tool_results = [
    "success",
    "success",
    "timeout",
    "rate_limited",
    "success",
]

print(Counter(tool_results))
```

### Model-provider failures

```python
provider_outcomes = [
    "provider_a:success",
    "provider_a:success",
    "provider_b:timeout",
    "provider_a:error",
]

print(Counter(provider_outcomes))
```

### Evaluation categories

```python
evaluation_labels = [
    "correct",
    "correct",
    "hallucination",
    "missing_citation",
]

evaluation_counts = Counter(evaluation_labels)
```

The pattern is:

```text
raw observations
    → local frequency aggregation
    → metric / diagnosis
```

---

## 23. Counter Common Mistakes

### Mistake: treating a missing key like a normal dict key

**BAD**

```python
counts = Counter()

if counts["unknown"] is None:
    print("missing")
```

**WHY**

A missing Counter key returns `0`.

**CORRECT**

```python
if "unknown" not in counts:
    print("not stored")
```

### Mistake: treating `update()` as assignment

**BAD**

```python
counts = Counter(a=2)
counts.update({"a": 10})

assert counts["a"] == 10
```

**WHY**

The result is `12`.

**CORRECT**

```python
counts["a"] = 10
```

when replacement is intended.

### Mistake: assuming `-` retains negative values

**BAD**

```python
result = Counter(a=1) - Counter(a=3)
assert result["a"] == -2
```

**WHY**

Multiset subtraction keeps positive results.

**CORRECT**

```python
result = Counter(a=1)
result.subtract(Counter(a=3))
assert result["a"] == -2
```

### Mistake: deleting while iterating

**BAD**

```python
for key in counts:
    if counts[key] == 0:
        del counts[key]
```

**WHY**

The mapping is being mutated while iterating.

**CORRECT**

```python
for key in [k for k, v in counts.items() if v == 0]:
    del counts[key]
```

or normalize with:

```python
counts = +counts
```

when dropping all non-positive counts is the actual requirement.

### Mistake: using Counter for arbitrary state

**BAD**

```python
runtime_state = Counter()
runtime_state["model_name"] = "model-a"
```

**WHY**

Counter communicates that values are counts.

**CORRECT**

Use a dict for arbitrary state:

```python
runtime_state = {"model_name": "model-a"}
```

---


# Part III — defaultdict

## 24. defaultdict Fundamentals

`defaultdict` is a subclass of `dict` that supplies a value for a missing key through a `default_factory`. Most of the remaining mapping behavior is inherited from `dict`. citeturn309077view1

The problem it solves is repeated initialization.

### Normal dictionary grouping

```python
groups = {}

key = "fruit"
value = "apple"

if key not in groups:
    groups[key] = []

groups[key].append(value)

print(groups)
```

### defaultdict grouping

```python
from collections import defaultdict

groups = defaultdict(list)

groups["fruit"].append("apple")

print(groups)
```

The `defaultdict` version moves the initialization rule into the data structure declaration:

```python
groups = defaultdict(list)
```

This says:

> If a new key is accessed with `[]`, initialize its value using `list()`.

---

## 25. `default_factory`

The constructor can be summarized as:

```python
defaultdict(default_factory)
```

The first argument becomes the `default_factory` attribute.

It must be:

- callable;
- or `None`.

Examples:

```python
defaultdict(list)
defaultdict(set)
defaultdict(int)
defaultdict(float)
```

Conceptually:

```text
defaultdict(list)
    missing key → list()

defaultdict(set)
    missing key → set()

defaultdict(int)
    missing key → int() → 0

defaultdict(float)
    missing key → float() → 0.0
```

The factory is called without arguments for a missing `d[key]` lookup. citeturn309077view1

### What does "callable" mean?

A callable is something Python can call:

```python
list
set
int
float
make_config
lambda: 0
```

This is not callable:

```python
[]
```

so:

```python
# defaultdict([])  # TypeError
```

is wrong.

Use:

```python
defaultdict(list)
```

instead.

---

## 26. defaultdict with `list`

This is the classic grouping pattern:

```python
from collections import defaultdict

groups = defaultdict(list)

groups["fruit"].append("apple")
groups["fruit"].append("banana")
groups["vehicle"].append("car")

print(dict(groups))
```

Expected:

```text
{
    'fruit': ['apple', 'banana'],
    'vehicle': ['car']
}
```

### Step-by-step execution

When Python evaluates:

```python
groups["fruit"]
```

for the first time:

1. `"fruit"` is not present.
2. `defaultdict` invokes `default_factory`.
3. Here the factory is `list`.
4. `list()` creates a new empty list.
5. The list is stored under `"fruit"`.
6. The new list is returned.
7. `.append("apple")` mutates that list.

On the second access:

```python
groups["fruit"].append("banana")
```

the key exists, so the normal stored list is returned.

The standard-library documentation demonstrates this exact grouping technique. citeturn309077view1

---

## 27. defaultdict with `set`

Use a set when each group's values must be unique.

```python
from collections import defaultdict

users_by_role = defaultdict(set)

users_by_role["admin"].add("alice")
users_by_role["admin"].add("alice")
users_by_role["admin"].add("bob")

print(dict(users_by_role))
```

Expected conceptually:

```text
admin → {'alice', 'bob'}
```

Typical uses:

- unique relationships;
- inverted indexes;
- deduplication;
- graph adjacency;
- many-to-many mappings.

### Example: documents by source

```python
documents_by_source = defaultdict(set)

documents_by_source["internal"].add("doc-1")
documents_by_source["internal"].add("doc-1")
documents_by_source["external"].add("doc-2")
```

The duplicate `"doc-1"` is retained only once.

---

## 28. defaultdict with `int`

Because:

```python
int()
```

returns:

```text
0
```

this is useful for accumulation:

```python
from collections import defaultdict

counts = defaultdict(int)

for value in ["a", "a", "b"]:
    counts[value] += 1

print(dict(counts))
```

Result:

```text
{'a': 2, 'b': 1}
```

### Compare with Counter

```python
from collections import Counter

counts = Counter(["a", "a", "b"])
```

Both approaches can count.

The distinction is semantic:

```text
defaultdict(int)
    → general automatic numeric initialization

Counter
    → frequency/counting abstraction
```

If you need:

```text
most_common()
total()
elements()
Counter arithmetic
```

Counter directly expresses the task.

---

## 29. defaultdict with `float`

`float()` returns `0.0`.

```python
from collections import defaultdict

totals = defaultdict(float)

totals["usd"] += 12.50
totals["usd"] += 7.25
totals["eur"] += 5.00

print(dict(totals))
```

Expected:

```text
{'usd': 19.75, 'eur': 5.0}
```

### Production note

This demonstrates automatic numeric initialization. It is not a recommendation to use binary floating-point for financial calculations that require exact decimal semantics.

For such domains, an appropriate factory may be based on `decimal.Decimal`:

```python
from decimal import Decimal

amounts = defaultdict(Decimal)
```

The broader lesson is:

```text
factory → default value type
```

---

## 30. Custom Default Factories

The factory can be a named function:

```python
from collections import defaultdict

def make_config():
    return {
        "enabled": True,
        "retries": 3,
    }

configs = defaultdict(make_config)

print(configs["model-a"])
print(configs["model-b"])
```

Each missing key causes a new call to `make_config()`.

### Fresh mutable object per key

```python
configs = defaultdict(dict)

first = configs["a"]
second = configs["b"]

print(first is second)
```

Expected:

```text
False
```

This is important.

The factory is called each time a new key needs a value.

### Stateful factory

A factory can also intentionally contain state, but that is an advanced design and should be explicit:

```python
def make_counter():
    return {"requests": 0}
```

The important production principle is:

> A default factory should create a value whose independent lifetime matches the key.

---

## 31. defaultdict with `lambda`

Valid:

```python
values = defaultdict(lambda: 0)
```

Usually clearer:

```python
values = defaultdict(int)
```

Likewise:

```python
defaultdict(list)
defaultdict(set)
```

is clearer than:

```python
defaultdict(lambda: [])
defaultdict(lambda: set())
```

### When lambda is reasonable

A tiny custom default expression may be acceptable:

```python
defaults = defaultdict(lambda: {"enabled": True})
```

For domain-heavy configuration, a named function can be easier to test and review:

```python
def default_model_config():
    return {"enabled": True}

configs = defaultdict(default_model_config)
```

---

## 32. `__missing__()` — the Actual Missing-Key Hook

The API name is:

```python
__missing__(key)
```

There is not a separate public `missing()` method.

For `defaultdict`, `__missing__()` is invoked by dictionary `__getitem__()` when a requested key is absent. If a factory exists, its return value is inserted and returned. If the factory is `None`, a `KeyError` is raised. citeturn309077view1

Conceptually:

```text
d[key]
   |
   +-- key exists? → return stored value
   |
   +-- missing?
          |
          v
     __missing__(key)
          |
          v
   default_factory()
          |
          v
      store value
          |
          v
       return
```

### Factory exceptions

If the factory raises an exception, `defaultdict` propagates that exception.

```python
def broken_factory():
    raise RuntimeError("cannot initialize")

d = defaultdict(broken_factory)

# d["x"]  # RuntimeError
```

This can be useful because failures are not silently converted into arbitrary defaults.

---

## 33. `d[key]` Versus `d.get(key)`

This distinction deserves special attention.

### Bracket lookup can create a key

```python
from collections import defaultdict

d = defaultdict(list)

value = d["missing"]

print(value)
print(dict(d))
```

Output:

```text
[]
{'missing': []}
```

### `get()` does not invoke the factory

```python
d = defaultdict(list)

value = d.get("missing")

print(value)
print(dict(d))
```

Output:

```text
None
{}
```

The official documentation specifies that `__missing__()` is not called by `get()`. citeturn309077view1

### Decision

Use:

```python
d[key]
```

when you want automatic initialization.

Use:

```python
d.get(key)
```

when you want optional lookup without factory-driven creation.

---

## 34. Accidental Key Creation

A read can mutate a `defaultdict`:

```python
from collections import defaultdict

d = defaultdict(list)

print(d)

_ = d["missing"]

print(d)
```

The second output contains `"missing"`.

### Why this matters

Diagnostic code can accidentally affect program state:

```python
print(d["unknown"])
```

or:

```python
if d["unknown"]:
    ...
```

Both can create the key.

### Safer inspection

```python
value = d.get("unknown")
```

or:

```python
if "unknown" in d:
    ...
```

Use the operation that matches the intended state transition.

---

## 35. defaultdict Versus dict

| Behavior | `dict` | `defaultdict` |
|---|---|---|
| missing `d[key]` | `KeyError` | factory result or `KeyError` if factory is `None` |
| automatic initialization | no | yes |
| `get()` calls factory | no | no |
| grouping | explicit | concise |
| read can create state | no | yes, via `[]` |
| general mapping | excellent | useful when default semantics are intentional |

### Readability trade-off

A `defaultdict` can reduce boilerplate:

```python
groups[key].append(value)
```

but can also hide a mutation:

```python
value = groups[key]
```

Good engineering uses the feature when its implicit behavior is understood and desirable.

---

## 36. defaultdict Methods

### `__getitem__`

```python
d[key]
```

Potentially invokes the factory.

### `get`

```python
d.get(key)
```

Does not invoke the factory.

### `setdefault`

```python
d.setdefault(key, default)
```

Uses the normal dictionary operation.

### `keys`

```python
d.keys()
```

Returns the mapping's keys view.

### `values`

```python
d.values()
```

Returns the mapping's values view.

### `items`

```python
d.items()
```

Returns key-value pairs.

### `pop`

```python
value = d.pop(key)
```

Removes the stored key. It does not manufacture a value merely so it can be popped.

### `popitem`

```python
key, value = d.popitem()
```

Removes and returns a stored entry.

### `clear`

```python
d.clear()
```

Removes all entries.

### `copy`

```python
other = d.copy()
```

Creates a shallow copy of the mapping.

### `update`

```python
d.update(other)
```

Uses normal dictionary update semantics. Do not confuse it with `Counter.update()`.

### `default_factory`

```python
print(d.default_factory)
```

The attribute records the callable used by `__missing__()`.

It is writable:

```python
d.default_factory = set
```

but changing the factory dynamically can make behavior difficult to reason about. Treat such mutation as an explicit design decision.

---

## 37. defaultdict and `setdefault()`

### Normal dictionary with `setdefault`

```python
groups = {}

records = [
    ("fruit", "apple"),
    ("fruit", "banana"),
]

for key, value in records:
    groups.setdefault(key, []).append(value)
```

### defaultdict

```python
groups = defaultdict(list)

for key, value in records:
    groups[key].append(value)
```

Both produce the same grouping.

### Key differences

`defaultdict`:

- declares one default policy for the mapping;
- makes grouping concise;
- can create values on bracket lookup.

`setdefault()`:

- keeps the mapping a normal `dict`;
- makes the default explicit at the individual operation;
- is useful when only occasional initialization is needed.

### Engineering question

Ask:

> Is automatic initialization part of the stable data model, or just a one-off convenience?

That answer often determines which form is clearer.

---

## 38. Nested defaultdict

Nested grouping can use:

```python
from collections import defaultdict

data = defaultdict(lambda: defaultdict(list))

data["model-a"]["success"].append("r1")
data["model-a"]["failure"].append("r2")

print(dict(data))
```

Conceptually:

```text
model-a
    ├── success → ["r1"]
    └── failure → ["r2"]
```

### Good use

Hierarchical data can be natural:

```text
department → role → users
model → status → events
country → region → records
```

### Maintainability warning

This can become unreadable:

```python
data = defaultdict(
    lambda: defaultdict(
        lambda: defaultdict(
            list
        )
    )
)
```

Do not optimize for minimum lines of code.

Optimize for:

```text
clear data model
clear invariants
clear ownership
```

---

## 39. Recursive Default Factory

For arbitrary-depth tree-like structures:

```python
from collections import defaultdict

def tree():
    return defaultdict(tree)

root = tree()

root["a"]["b"]["c"] = 1

print(root["a"]["b"]["c"])
```

Every missing level is another tree.

### Why it works

```text
root["a"]
    → tree()

root["a"]["b"]
    → tree()

root["a"]["b"]["c"]
    → assignment
```

### Why to be cautious

It can create large structures through accidental reads:

```python
_ = root["a"]["b"]["c"]["d"]
```

It also makes serialization and type reasoning less obvious.

Use it when arbitrary depth is a real requirement, not simply because the pattern is clever.

---

## 40. defaultdict for Grouping

### Users by department

```python
users_by_department = defaultdict(list)

users_by_department["engineering"].append("alice")
users_by_department["engineering"].append("bob")
users_by_department["finance"].append("charlie")
```

### Documents by category

```python
documents_by_category = defaultdict(list)

documents_by_category["technical"].append("doc-1")
documents_by_category["technical"].append("doc-2")
documents_by_category["legal"].append("doc-3")
```

### Transactions by account

```python
transactions_by_account = defaultdict(list)

transactions_by_account["acct-1"].append(100)
transactions_by_account["acct-1"].append(-20)
```

### Model outputs by class

```python
outputs_by_class = defaultdict(list)

outputs_by_class["positive"].append({"request_id": "r1"})
outputs_by_class["negative"].append({"request_id": "r2"})
```

### Events by type

```python
events_by_type = defaultdict(list)

events_by_type["timeout"].append("r10")
events_by_type["success"].append("r11")
```

All of these use:

```text
group key → collection of related values
```

---

## 41. defaultdict for Graph Representation

A graph adjacency representation can be:

```python
from collections import defaultdict

graph = defaultdict(set)

graph["A"].add("B")
graph["A"].add("C")
graph["B"].add("D")

print(dict(graph))
```

Conceptually:

```text
A → {B, C}
B → {D}
```

A set is appropriate because duplicate edges are naturally collapsed:

```python
graph["A"].add("B")
graph["A"].add("B")
```

The same data-structure pattern appears in:

- relationship indexes;
- dependency maps;
- routing tables;
- document-link graphs.

This is a representation lesson, not a full graph-algorithms chapter.

---

## 42. defaultdict Performance and Memory

For hash-based mappings, existing-key lookup and insertion have expected O(1) average-time behavior.

A missing lookup adds:

```text
factory invocation
+
value creation
+
mapping insertion
```

So the factory's own cost matters.

For grouping `n` records:

```text
time ≈ O(n)
```

because the input must be processed.

Memory is influenced by:

```text
number of keys
+
number of grouped values
+
size of factory-created objects
```

### Critical memory implication

`defaultdict(list)` does not magically store data cheaply.

If one group receives one million large objects:

```python
groups["large"].append(...)
```

the list still contains those objects.

The specialized container removes initialization boilerplate; it does not remove the underlying data cost.

---

## 43. defaultdict Common Mistakes

### Mistake 1 — accidental creation

**BAD**

```python
if not groups["unknown"]:
    print("missing")
```

**WHY**

The lookup can create `"unknown"`.

**IMPROVED**

```python
if not groups.get("unknown"):
    print("missing")
```

or:

```python
if "unknown" not in groups:
    print("missing")
```

### Mistake 2 — using `get()` when initialization is required

**BAD**

```python
value = groups.get("fruit")
value.append("apple")
```

**WHY**

`value` may be `None`.

**IMPROVED**

```python
groups["fruit"].append("apple")
```

when automatic creation is intended.

### Mistake 3 — shared mutable state

**BAD**

```python
shared = []

groups = defaultdict(lambda: shared)

groups["a"].append(1)

print(groups["b"])
```

Output:

```text
[1]
```

**WHY**

Both keys reference the same list.

**IMPROVED**

```python
groups = defaultdict(list)
```

### Mistake 4 — unnecessary lambda

**LESS CLEAR**

```python
defaultdict(lambda: 0)
```

**CLEARER**

```python
defaultdict(int)
```

### Mistake 5 — too much nesting

**BAD**

```python
data["country"]["region"]["city"]["type"].append(record)
```

when the schema is difficult to understand.

**IMPROVED**

Use named structures or flatter representations when the nested shape becomes business logic rather than temporary grouping.

### Mistake 6 — unexpected serialization

A `defaultdict` is a mapping subclass, but serializers may not all treat subclasses exactly the same way.

Normalize intentionally when building a simple API payload:

```python
payload = dict(groups)
```

For nested groups, normalize the nested values to the required public schema.

### Mistake 7 — unexpected factory behavior

Do not dynamically change:

```python
d.default_factory
```

without documenting why.

A mapping that can switch from:

```text
list defaults
```

to:

```text
set defaults
```

mid-lifecycle becomes much harder to reason about.

---

# Part IV — deque

## 44. deque Fundamentals

`deque` means **double-ended queue**.

It is a generalization of stacks and queues, with operations designed for both ends. The Python documentation describes appends and pops from either side as approximately O(1) and explains that `list.pop(0)` incurs O(n) movement costs. citeturn309077view0

Visual model:

```text
LEFT                                  RIGHT
  ↓                                      ↓
[ A ] [ B ] [ C ] [ D ] [ E ]
  ↑                                      ↑
appendleft()                          append()
popleft()                              pop()
```

The essential mental model is:

```text
left ← elements → right
```

### Main workloads

- FIFO queues;
- LIFO stacks;
- sliding windows;
- recent-event history;
- bounded buffers;
- round-robin rotation.

---

## 45. deque Versus list Queue

A list implementation:

```python
queue = []

queue.append("job-1")
queue.append("job-2")
queue.append("job-3")

job = queue.pop(0)
```

works logically.

But removing index `0` requires the remaining elements to be shifted.

The deque version:

```python
from collections import deque

queue = deque()

queue.append("job-1")
queue.append("job-2")
queue.append("job-3")

job = queue.popleft()
```

matches the FIFO access pattern directly.

The official documentation explicitly recommends deque for efficient appends/pops at either end and documents the O(n) movement cost associated with `list.pop(0)`. citeturn309077view0

### No universal rule

Do not translate this into:

```text
deque is always better than list
```

Instead:

```text
deque → end-oriented access
list  → general sequence/random access
```

---

## 46. deque Creation

### Empty

```python
from collections import deque

d = deque()
print(d)
```

### From iterable

```python
d = deque([1, 2, 3])
print(d)
```

### With maximum length

```python
d = deque([1, 2, 3], maxlen=3)

print(d)
print(d.maxlen)
```

The constructor loads iterable elements from left to right and can specify a maximum size. citeturn309077view0

---

## 47. `append()`

`append(x)` adds to the right side.

```python
d = deque(["B", "C"])

d.append("D")

print(d)
```

Output:

```text
deque(['B', 'C', 'D'])
```

Typical queue interpretation:

```text
enqueue → append
```

---

## 48. `appendleft()`

`appendleft(x)` adds to the left.

```python
d = deque(["B", "C"])

d.appendleft("A")

print(d)
```

Output:

```text
deque(['A', 'B', 'C'])
```

Typical uses:

- urgent local work;
- newest-item-first buffers;
- double-ended algorithms.

Do not use it solely because it is available; the end-oriented access pattern should justify it.

---

## 49. `pop()`

`pop()` removes and returns the rightmost item.

```python
d = deque(["A", "B", "C"])

item = d.pop()

print(item)
print(d)
```

Output:

```text
C
deque(['A', 'B'])
```

On an empty deque, `pop()` raises `IndexError`. citeturn309077view0

---

## 50. `popleft()`

`popleft()` removes and returns the leftmost item.

```python
d = deque(["A", "B", "C"])

item = d.popleft()

print(item)
print(d)
```

Output:

```text
A
deque(['B', 'C'])
```

On an empty deque, it raises `IndexError`. citeturn309077view0

This is the key FIFO operation.

---

## 51. `extend()`

`extend(iterable)` appends multiple elements to the right.

```python
d = deque([1, 2])

d.extend([3, 4, 5])

print(d)
```

Output:

```text
deque([1, 2, 3, 4, 5])
```

### Remember that strings are iterable

```python
d = deque([1])

d.extend("abc")

print(d)
```

Output:

```text
deque([1, 'a', 'b', 'c'])
```

To append the entire string as one item:

```python
d.append("abc")
```

---

## 52. `extendleft()`

`extendleft(iterable)` adds items to the left one at a time.

```python
d = deque()

d.extendleft([1, 2, 3])

print(d)
```

Result:

```text
deque([3, 2, 1])
```

### Step-by-step

```text
[]
[1]
[2, 1]
[3, 2, 1]
```

The input order is reversed because each new element goes to the left.

This behavior is explicitly documented. citeturn309077view0

### Preserve original order on the left

```python
d = deque()

d.extendleft(reversed([1, 2, 3]))

print(d)
```

Result:

```text
deque([1, 2, 3])
```

Use `extendleft()` deliberately; it is one of the most common beginner surprises.

---

## 53. `rotate()`

`rotate(n)` rotates the deque.

Positive:

```python
d = deque([1, 2, 3, 4])

d.rotate(1)

print(d)
```

Result:

```text
deque([4, 1, 2, 3])
```

Negative:

```python
d.rotate(-2)
```

means rotate left by two positions.

The documentation gives these one-step equivalences for a non-empty deque:

```python
d.rotate(1)
```

has the effect of:

```python
d.appendleft(d.pop())
```

and:

```python
d.rotate(-1)
```

has the effect of:

```python
d.append(d.popleft())
```

citeturn309077view0

### Uses

- round-robin scheduling;
- cycling active iterators;
- rotating a work frontier;
- specialized deque algorithms.

### Complexity caution

Do not claim every rotation is strictly O(1). Cost depends on the number of positions moved and implementation behavior. For performance-critical code, measure the actual workload.

---

## 54. `remove()`

`remove(value)` removes the first matching value.

```python
d = deque(["a", "b", "a", "c"])

d.remove("a")

print(d)
```

Output:

```text
deque(['b', 'a', 'c'])
```

If the value is absent:

```python
# d.remove("missing")
```

raises `ValueError`. citeturn309077view0

This is a search operation, so it should not be mentally grouped with the constant-time end operations.

---

## 55. `count()`

`count(value)` counts matching items.

```python
d = deque(["a", "b", "a", "a"])

print(d.count("a"))
```

Output:

```text
3
```

This requires inspecting the sequence, so the work grows with the deque size.

If you repeatedly need frequency analysis, ask whether:

```python
Counter(...)
```

would be a better primary data structure.

---

## 56. `index()`

`index(value[, start[, stop]])` finds the first matching value within the optional range.

```python
d = deque(["a", "b", "c", "b"])

print(d.index("b"))
```

Output:

```text
1
```

With a start position:

```python
print(d.index("b", 2))
```

Output:

```text
3
```

If not found, `ValueError` is raised.

### Design implication

Frequent search-by-key is usually a signal to evaluate a mapping or index rather than using a deque as the primary lookup structure.

---

## 57. `insert()`

`insert(i, value)` inserts at a position.

```python
d = deque(["a", "c"])

d.insert(1, "b")

print(d)
```

Output:

```text
deque(['a', 'b', 'c'])
```

Middle insertion is not the same class of workload as `append()` or `popleft()`.

For a bounded deque, an insertion that would exceed `maxlen` raises `IndexError` rather than evicting an opposite-end item. citeturn309077view0

This is an important edge case when designing bounded buffers.

---

## 58. `reverse()`

`reverse()` reverses the deque in place and returns `None`.

```python
d = deque([1, 2, 3])

result = d.reverse()

print(result)
print(d)
```

Output:

```text
None
deque([3, 2, 1])
```

### Common mistake

**BAD**

```python
d = d.reverse()
```

After that statement, `d` is `None`.

**CORRECT**

```python
d.reverse()
```

---

## 59. `copy()`

`copy()` creates a shallow copy.

```python
d = deque([1, 2, 3])

other = d.copy()

other.append(4)

print(d)
print(other)
```

Output:

```text
deque([1, 2, 3])
deque([1, 2, 3, 4])
```

Shallow copy means the deque container is new, but contained objects are not recursively copied.

```python
payload = []

d = deque([payload])
other = d.copy()

other[0].append("x")

print(d[0])
```

Output:

```text
['x']
```

Both deques reference the same inner list.

---

## 60. `maxlen`

`maxlen` is the maximum size of a deque, or `None` for an unbounded deque. citeturn309077view0

```python
history = deque(maxlen=3)

history.append("event-1")
history.append("event-2")
history.append("event-3")
history.append("event-4")

print(history)
print(history.maxlen)
```

Output:

```text
deque(['event-2', 'event-3', 'event-4'], maxlen=3)
3
```

### The memory policy

```text
retain at most N items
```

This is a deliberate policy encoded in the data structure.

---

## 61. Bounded Deques

Useful examples:

```python
recent_logs = deque(maxlen=1000)
recent_requests = deque(maxlen=500)
recent_predictions = deque(maxlen=100)
recent_events = deque(maxlen=200)
```

Typical use cases:

- recent logs;
- recent requests;
- recent model predictions;
- rolling event history;
- bounded conversation/event context.

### Critical question

> Is automatic eviction correct?

If the answer is no, a bounded deque cannot be the sole source of that data.

### Unbounded versus bounded

```text
deque()
    → can grow without an explicit size bound

deque(maxlen=N)
    → retains at most N items
```

A production service should make this a deliberate memory decision rather than an accidental one.

---

## 62. deque Indexing

You can index:

```python
d[0]
d[-1]
```

Example:

```python
d = deque(["a", "b", "c"])

print(d[0])
print(d[-1])
```

Output:

```text
a
c
```

But a deque is not intended as a general random-access replacement for list.

The documentation states that indexed access is O(1) at both ends but slows to O(n) in the middle, and recommends lists for fast random access. citeturn309077view0

### Practical interpretation

Good:

```python
d[0]    # inspect left end
d[-1]   # inspect right end
```

Potentially poor design:

```python
for i in range(len(d)):
    expensive = d[i]
```

when random indexed access dominates the workload.

---

## 63. deque Iteration, Membership, and Reversal

### Iteration

```python
d = deque(["a", "b", "c"])

for item in d:
    print(item)
```

The iteration order is left-to-right.

### Membership

```python
print("b" in d)
```

This searches the deque.

### Reverse iteration

```python
for item in reversed(d):
    print(item)
```

The documentation also lists iteration, membership testing, `len()`, `reversed()`, and pickling among supported operations. citeturn309077view0

### `len()`

```python
print(len(d))
```

This returns the number of stored elements.

---

## 64. deque as Queue

FIFO means:

> **First In, First Out**

Canonical pattern:

```python
from collections import deque

queue = deque()

queue.append("job-1")
queue.append("job-2")
queue.append("job-3")

while queue:
    job = queue.popleft()
    print(job)
```

Output:

```text
job-1
job-2
job-3
```

The data structure's operations match the semantic vocabulary:

```text
enqueue → append
dequeue → popleft
```

---

## 65. deque as Stack

LIFO means:

> **Last In, First Out**

A deque can model a stack:

```python
stack = deque()

stack.append("A")
stack.append("B")
stack.append("C")

print(stack.pop())
print(stack.pop())
print(stack.pop())
```

Output:

```text
C
B
A
```

### Compare with list

A list is already excellent for a right-end stack:

```python
stack = []
stack.append("A")
stack.append("B")
stack.pop()
```

Use deque when additional double-ended operations are useful or when the broader buffer semantics point toward deque.

---

## 66. deque as a Double-Ended Buffer

A deque is a natural fit when both ends matter.

Example:

```python
buffer = deque()

buffer.append("normal-1")
buffer.appendleft("urgent-1")

print(buffer)
```

Output:

```text
deque(['urgent-1', 'normal-1'])
```

This can support:

- urgent work inserted at the left;
- oldest work removed from the left;
- newest work removed from the right;
- bounded event history;
- bidirectional processing.

---

## 67. deque for Sliding Windows

```python
from collections import deque

window = deque(maxlen=5)

for value in [10, 20, 30, 40, 50, 60]:
    window.append(value)
    print(list(window))
```

The final window is:

```text
[20, 30, 40, 50, 60]
```

### Simple rolling average

```python
window = deque(maxlen=3)

for value in [10, 20, 40, 50]:
    window.append(value)
    average = sum(window) / len(window)
    print(average)
```

This is easy to understand, but `sum(window)` scans the window each time.

### Incremental rolling sum

```python
window = deque(maxlen=3)
running_sum = 0

for value in [10, 20, 40, 50]:
    if len(window) == window.maxlen:
        running_sum -= window[0]

    window.append(value)
    running_sum += value

    print(running_sum / len(window))
```

This illustrates a broader engineering lesson:

> Data-structure choice and algorithm choice are related but not identical.

---

## 68. deque for Rate-Limiting Concepts

A local conceptual sliding-window rate limiter can store recent **monotonic** timestamps.

```python
from collections import deque
from time import monotonic

recent_requests = deque()

WINDOW_SECONDS = 60
LIMIT = 5

def allow_request() -> bool:
    now = monotonic()

    while recent_requests:
        oldest = recent_requests[0]

        if now - oldest < WINDOW_SECONDS:
            break

        recent_requests.popleft()

    if len(recent_requests) >= LIMIT:
        return False

    recent_requests.append(now)
    return True
```

### Why deque?

The oldest request is always at the left:

```python
recent_requests[0]
```

and stale requests can be discarded efficiently:

```python
recent_requests.popleft()
```

### Why monotonic timestamps?

Rate limiting measures elapsed duration, not calendar time. A monotonic clock is designed for elapsed-time measurement.

### Production boundary

This example is only a conceptual, single-process limiter.

A distributed production rate limiter may require:

```text
shared state
coordination
gateway enforcement
central cache
distributed token bucket
```

Do not treat a local deque as a distributed rate-limiting system.

---

## 69. deque for Breadth-First Search

The BFS queue pattern is:

```python
from collections import deque

queue = deque([start])

while queue:
    node = queue.popleft()
    # inspect node and add discovered neighbors
```

The point here is the queue discipline:

```text
oldest frontier item first
```

It is a data-structure example, not a complete graph-algorithms lesson.

---

## 70. deque for Producer-Consumer Concepts

A conceptual local buffer:

```text
Producer
    |
    v
  deque
    |
    v
Consumer
```

Producer:

```python
buffer.append(item)
```

Consumer:

```python
item = buffer.popleft()
```

A bounded deque can model a finite in-memory buffer.

### But not a complete concurrency abstraction

A plain deque does not provide:

- blocking wait;
- condition variables;
- task tracking;
- coordinated shutdown;
- multi-thread workflow semantics.

For those needs, a synchronized queue abstraction is more appropriate.

---

## 71. deque Thread-Safety and Application Correctness

The current Python documentation describes deque appends and pops as thread-safe, memory efficient, and approximately O(1) at either end. citeturn309077view0

That should not be interpreted as:

> "Every multi-step workflow using a deque is thread-safe."

Consider:

```python
if queue:
    item = queue.popleft()
```

There are two conceptual operations:

1. inspect whether the queue has an item;
2. remove the item.

Another thread may interleave work between those steps.

### General rule

```text
operation-level safety
    ≠
workflow-level correctness
```

When multiple threaded producers and consumers require coordinated waiting and task tracking, use the synchronization-oriented queue abstraction covered next.

---


# Part V — deque versus queue.Queue and structure selection

## 72. deque Versus `queue.Queue`

The standard `queue` module provides synchronized queues intended for multi-producer, multi-consumer threaded programs. `Queue` supplies locking semantics, blocking behavior, and task-tracking operations that a plain deque does not provide. citeturn838217view1

| Property | `deque` | `queue.Queue` |
|---|---|---|
| Primary role | container/data structure | synchronized queue abstraction |
| Add item | `append()` / `appendleft()` | `put()` |
| Remove item | `pop()` / `popleft()` | `get()` |
| Blocking wait | no | yes |
| `task_done()` | no | yes |
| `join()` | no | yes |
| Bounded capacity | `maxlen` | `maxsize` |
| Intended threaded coordination | no | yes |
| Distributed durability | no | no |

### `queue.Queue` example

```python
from queue import Queue

work = Queue(maxsize=10)

work.put("job-1")

job = work.get()

try:
    print(job)
finally:
    work.task_done()
```

### Why use `Queue`?

The problem is no longer just:

```text
"Where should the next item be stored?"
```

It becomes:

```text
"How should multiple workers coordinate access and waiting?"
```

That is a different abstraction.

The current queue documentation describes `Queue` as a synchronized queue for multi-producer, multi-consumer threaded use and documents `put()`, `get()`, `task_done()`, and `join()`. citeturn499290search1

### Process boundary

For multiple processes, a plain deque remains process-local. The standard library supplies process queues such as `multiprocessing.Queue`. citeturn499290search3

---

## 73. deque Versus list

| Workload | `list` | `deque` |
|---|---|---|
| append right | typically amortized O(1) | approximately O(1) |
| pop right | typically O(1) | approximately O(1) |
| add left | O(n) with index insertion | approximately O(1) |
| remove left | O(n) with `pop(0)` | approximately O(1) |
| random access | strong | slower toward middle |
| general sequence use | strong | specialized |
| bounded recent history | manual | built-in `maxlen` |

The documented reason for the queue difference is important: removing the first list element changes the position of the remaining elements, while deque is designed for both ends. citeturn309077view0

### Decision

Use a list when:

```text
general sequence + random access
```

dominates.

Use deque when:

```text
left/right end operations + queue/buffer behavior
```

dominates.

---

## 74. Counter Versus `defaultdict(int)`

Both can count:

```python
from collections import Counter, defaultdict

counter = Counter()
mapping = defaultdict(int)

for value in ["a", "a", "b"]:
    counter[value] += 1
    mapping[value] += 1

print(counter)
print(dict(mapping))
```

Both represent:

```text
a → 2
b → 1
```

### Why Counter is often clearer for counting

The declaration itself says:

```python
counter = Counter()
```

The reader knows immediately that counts are the primary data model.

It also provides specialized APIs:

```python
counter.most_common()
counter.total()
counter.elements()
counter.subtract(...)
```

### When defaultdict(int) is appropriate

Use it when the integer default is part of a more general accumulation design and you do not need Counter-specific semantics.

There is no universal winner.

---

## 75. defaultdict Versus dict and `setdefault()`

### Explicit dictionary

```python
groups = {}

for key, value in records:
    if key not in groups:
        groups[key] = []
    groups[key].append(value)
```

### `setdefault`

```python
groups = {}

for key, value in records:
    groups.setdefault(key, []).append(value)
```

### `defaultdict`

```python
groups = defaultdict(list)

for key, value in records:
    groups[key].append(value)
```

All can be correct.

### Choose by semantics

Use `dict` when:

```text
missing-key behavior must be explicit
```

Use `setdefault()` when:

```text
automatic initialization is local to a few operations
```

Use `defaultdict` when:

```text
the mapping has a stable default-creation policy
```

### Side-effect consideration

With `defaultdict`:

```python
groups[key]
```

can mutate the mapping.

With `dict`:

```python
groups[key]
```

raises instead.

That difference can matter during debugging, validation, and observability code.

---

## 76. Structure Selection by Access Pattern

Ask what your program does most often.

### Frequency

```text
How many times?
    → Counter
```

### Grouping

```text
Which values belong to this key?
    → defaultdict(list)
```

### Uniquely grouped values

```text
Which unique values belong to this key?
    → defaultdict(set)
```

### Numeric accumulation

```text
What numeric value should a new key start with?
    → defaultdict(int/float/etc.)
```

### FIFO

```text
Which item arrived first?
    → deque + popleft()
```

### LIFO

```text
Which item was added last?
    → list or deque + pop()
```

### Recent N

```text
Which are the most recent N items?
    → deque(maxlen=N)
```

### General mapping

```text
What value belongs to this key?
    → dict
```

### General sequence

```text
What is item i?
    → list
```

### Thread synchronization

```text
How do multiple threads safely wait and exchange tasks?
    → queue.Queue
```

### Persistence/distribution

```text
How does state survive process failure or become shared?
    → external durable/shared system
```

---

# Part VI — Complexity, memory, and internals

## 77. Practical Complexity Table

The following table uses **typical/expected** complexity language. It is not a claim that every implementation detail is an absolute language-level guarantee.

| Structure / operation | Typical behavior | Reason |
|---|---:|---|
| `Counter[key]` | expected O(1) lookup | hash-based mapping |
| `Counter[key] += 1` | expected O(1) | lookup + update |
| `Counter(iterable)` | O(n) | consumes input |
| `Counter.update(batch)` | O(m) over supplied elements | visits batch |
| `Counter.subtract(batch)` | O(m) over supplied elements | visits batch |
| `Counter.most_common()` | depends on distinct-key count and requested result | ranking |
| `defaultdict[key]` existing key | expected O(1) | dict lookup |
| `defaultdict[key]` missing key | lookup + factory + insertion | creates value |
| grouping n records | O(n) | process each record |
| `deque.append()` | approximately O(1) | right-end operation |
| `deque.appendleft()` | approximately O(1) | left-end operation |
| `deque.pop()` | approximately O(1) | right-end operation |
| `deque.popleft()` | approximately O(1) | left-end operation |
| `deque[i]` near an end | O(1) | efficient endpoint access |
| `deque[i]` in middle | slower, O(n)-like | traversal toward middle |
| `deque.count()` | O(n) | search |
| `deque.index()` | O(n) worst case | search |
| `deque.remove()` | O(n) worst case | search |
| `deque.insert()` | not an end operation | may reposition many items |

The Python documentation explicitly describes deque's end operations as approximately O(1) and notes that middle indexing slows to O(n). citeturn309077view0

### Complexity vocabulary

Do not say:

> "`deque` makes everything O(1)."

Say:

> "Deque is designed for efficient operations at both ends."

Do not say:

> "Counter is always faster than dict."

Say:

> "Counter is an expressive counting abstraction with expected constant-time mapping updates; actual performance depends on workload and implementation."

---

## 78. Memory Trade-Offs

### Counter

If there are:

```text
n = total events
u = distinct keys
```

then Counter storage for the mapping is driven primarily by `u`, not `n`.

```text
memory ≈ O(u)
```

for key/count entries, excluding the memory occupied by the original input.

A stream with many unique keys can therefore create a large Counter.

### defaultdict

A `defaultdict(list)` grows with:

```text
number of created keys
+
number and size of grouped values
```

If a value is a large Python object, the list holds its reference.

### deque

An unbounded deque grows with retained items:

```python
events = deque()
```

A bounded deque limits retained elements:

```python
events = deque(maxlen=1000)
```

### Explicit memory policy

Use:

```python
deque(maxlen=N)
```

when eviction is acceptable.

Do not use it as an accidental data-loss mechanism.

---

## 79. Internal Mechanics — Conceptual Model

### Counter

Think:

```text
hashable item
     ↓
dictionary key
     ↓
numeric count
```

The specialized behavior makes frequency operations convenient.

### defaultdict

Think:

```text
dictionary lookup
       ↓
missing?
       ↓ yes
default_factory()
       ↓
store result
       ↓
return result
```

### deque

Think:

```text
LEFT ← [ A ][ B ][ C ][ D ] → RIGHT
```

with explicit operations for both ends.

### What not to assume

Do not infer exact CPython memory layout from the conceptual diagram.

The Python-level contract concerns observable behavior and documented semantics. Low-level implementation details can change between implementations or versions.

---

## 80. Data Streaming with the Three Structures

A local streaming processor might use:

```text
Input events
    |
    +------→ Counter
    |          |
    |          +→ frequency statistics
    |
    +------→ defaultdict
    |          |
    |          +→ grouped records
    |
    +------→ deque
               |
               +→ recent/sliding history
```

### Example

```python
status_counts = Counter()
events_by_model = defaultdict(list)
recent_events = deque(maxlen=100)
```

An event can update all three:

```python
event = {
    "model": "model-a",
    "status": "success",
}

status_counts[event["status"]] += 1
events_by_model[event["model"]].append(event)
recent_events.append(event)
```

One event contributes to:

```text
aggregate
group
recent history
```

That is a useful pattern in local monitoring and stream transformations.

---

# Part VII — Applied AI Engineering

## 81. Applied AI Engineering — Log Analysis

Suppose an inference service emits events:

```python
logs = [
    {"status": "success", "provider": "a"},
    {"status": "timeout", "provider": "a"},
    {"status": "error", "provider": "b"},
    {"status": "timeout", "provider": "a"},
]
```

Count statuses:

```python
status_counts = Counter(log["status"] for log in logs)
```

Count providers:

```python
provider_counts = Counter(log["provider"] for log in logs)
```

Count failures:

```python
failure_counts = Counter(
    log["status"]
    for log in logs
    if log["status"] != "success"
)
```

Questions answered:

```text
Which status is most frequent?
Which provider has the most events?
Which failure categories are appearing?
```

### Production boundary

Keep raw logs in the durable observability system. Use Counter for local aggregation or batch summarization.

---

## 82. Applied AI Engineering — Grouping

Suppose a RAG ingestion worker receives:

```python
documents = [
    {"model": "embed-v1", "source": "wiki", "id": "d1"},
    {"model": "embed-v1", "source": "wiki", "id": "d2"},
    {"model": "embed-v2", "source": "web", "id": "d3"},
]
```

Group by source:

```python
documents_by_source = defaultdict(list)

for document in documents:
    documents_by_source[document["source"]].append(document)
```

Group by model:

```python
documents_by_model = defaultdict(list)

for document in documents:
    documents_by_model[document["model"]].append(document)
```

These are separate access patterns, so separate indexes can be clearer than one giant nested mapping.

---

## 83. Applied AI Engineering — Recent Agent Context

An agent debugging tool might need the most recent 20 events:

```python
recent_events = deque(maxlen=20)

recent_events.append({
    "type": "tool_call",
    "tool": "search",
})

recent_events.append({
    "type": "model_output",
    "tokens": 120,
})
```

This supports:

- recent tool calls;
- recent model outputs;
- local debugging;
- recent event inspection;
- bounded local history.

### Important distinction

This is not automatically:

- durable conversation history;
- vector memory;
- long-term agent memory;
- event sourcing.

It is a bounded in-memory buffer.

---

## 84. Applied AI Engineering — Evaluation Statistics

Suppose an evaluation loop records:

```python
results = [
    "correct",
    "correct",
    "hallucination",
    "missing_citation",
    "correct",
]
```

Use:

```python
counts = Counter(results)

print(counts)
print(counts.most_common())
```

The output can become a local summary that is later exported to a metrics system.

### Useful questions

```text
What is the distribution of evaluation outcomes?
Which failure category is most frequent?
Did the latest batch produce an unusual distribution?
```

Counter makes these questions natural.

---

## 85. Applied AI Engineering — Stream Processing

A conceptual AI-event processor:

```text
                inference events
                       |
          +------------+------------+
          |            |            |
          v            v            v
       Counter     defaultdict     deque
          |            |            |
          v            v            v
      statistics      groups      recent N
```

### Example responsibilities

```text
Counter
    status_counts
    model_counts
    failure_counts

defaultdict
    events_by_model
    errors_by_provider
    documents_by_source

deque
    recent_events
    recent_latencies
    recent_tool_calls
```

This decomposition prevents one data structure from being forced to solve unrelated access patterns.

---

# Part VIII — Production-style integrated example

## 86. Production-Style Complete Example — AI Inference Event Monitor

We will create an understandable, in-memory monitoring component around:

```python
{
    "request_id": "...",
    "model": "...",
    "status": "...",
    "latency_ms": ...,
    "timestamp": "...",
}
```

Requirements:

1. Count statuses.
2. Count model usage.
3. Group events by model.
4. Retain only the latest N events.
5. Inspect top failures.
6. Inspect events for a model.
7. Compute a simple recent latency summary.
8. Reject obviously invalid latency.
9. Keep the recent buffer bounded.
10. Make behavior testable.

### Implementation

```python
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean


@dataclass(frozen=True)
class InferenceEvent:
    request_id: str
    model: str
    status: str
    latency_ms: float
    timestamp: datetime


class InferenceMonitor:
    def __init__(self, recent_limit: int = 100) -> None:
        if recent_limit <= 0:
            raise ValueError("recent_limit must be positive")

        self.status_counts: Counter[str] = Counter()
        self.model_counts: Counter[str] = Counter()
        self.events_by_model: defaultdict[str, list[InferenceEvent]] = defaultdict(list)
        self.recent_events: deque[InferenceEvent] = deque(maxlen=recent_limit)

    def ingest(self, event: InferenceEvent) -> None:
        if event.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")

        if event.timestamp.tzinfo is None or event.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")

        self.status_counts[event.status] += 1
        self.model_counts[event.model] += 1
        self.events_by_model[event.model].append(event)
        self.recent_events.append(event)

    def top_failures(self, limit: int = 5) -> list[tuple[str, int]]:
        failures = Counter(
            {
                status: count
                for status, count in self.status_counts.items()
                if status != "success"
            }
        )
        return failures.most_common(limit)

    def recent(self) -> list[InferenceEvent]:
        return list(self.recent_events)

    def model_events(self, model: str) -> list[InferenceEvent]:
        return list(self.events_by_model.get(model, []))

    def latency_summary(self) -> dict[str, float]:
        latencies = [event.latency_ms for event in self.recent_events]

        if not latencies:
            return {
                "count": 0.0,
                "mean_ms": 0.0,
            }

        return {
            "count": float(len(latencies)),
            "mean_ms": mean(latencies),
        }


def make_event(
    request_id: str,
    model: str,
    status: str,
    latency_ms: float,
) -> InferenceEvent:
    return InferenceEvent(
        request_id=request_id,
        model=model,
        status=status,
        latency_ms=latency_ms,
        timestamp=datetime.now(timezone.utc),
    )


monitor = InferenceMonitor(recent_limit=3)

monitor.ingest(make_event("r1", "model-a", "success", 120.0))
monitor.ingest(make_event("r2", "model-a", "timeout", 500.0))
monitor.ingest(make_event("r3", "model-b", "success", 100.0))
monitor.ingest(make_event("r4", "model-a", "error", 450.0))

print(monitor.status_counts)
print(monitor.model_counts)
print(monitor.top_failures())
print([event.request_id for event in monitor.recent()])
print(monitor.latency_summary())
```

### Why the Counter fields exist

```python
self.status_counts
self.model_counts
```

They answer frequency questions.

### Why `defaultdict(list)` exists

```python
self.events_by_model
```

represents:

```text
model → list of events
```

### Why deque exists

```python
self.recent_events
```

represents:

```text
latest N events
```

and its `maxlen` makes that retention policy explicit.

### Why not use a list for recent events?

A list would require manual eviction:

```python
recent.append(event)

if len(recent) > recent_limit:
    recent.pop(0)
```

Deque directly models the end-oriented workload.

### Why not use `queue.Queue`?

The example is an in-memory monitor object, not a threaded producer-consumer queue.

If ingestion is asynchronous, a separate queue boundary can feed the monitor.

### Important limitation

`events_by_model` is intentionally **unbounded** in this educational example.

A real system may need:

```text
per-model bounded retention
external persistence
summary-only storage
sampling
expiration
```

The bounded recent deque controls one collection; it does not magically cap every other collection.

---

## 87. Production Example — Design Decisions

| Requirement | Structure | Reason |
|---|---|---|
| status frequency | `Counter` | direct frequency semantics |
| model frequency | `Counter` | direct frequency semantics |
| model grouping | `defaultdict(list)` | automatic list initialization |
| recent N events | `deque(maxlen=N)` | end-oriented bounded retention |
| threaded handoff | not implemented | separate synchronization problem |
| durable history | external system | process memory is ephemeral |

### Alternatives

#### Status counts as dict

```python
status_counts = {}
status_counts[status] = status_counts.get(status, 0) + 1
```

Valid, but Counter is more expressive for a frequency model.

#### Grouping with dict

```python
events_by_model = {}

if model not in events_by_model:
    events_by_model[model] = []

events_by_model[model].append(event)
```

Valid, but more verbose.

#### Recent history with list

```python
recent_events = []

recent_events.append(event)

if len(recent_events) > N:
    recent_events.pop(0)
```

Valid but repeatedly incurs front-removal work and distributes the retention policy across code.

#### Threaded queue

```python
from queue import Queue

incoming = Queue()
```

Useful if the problem includes multiple threaded producers/consumers and blocking task coordination. citeturn838217view1

### Architecture principle

Do not select data structures in isolation from the system boundary.

---

## 88. Production Limitations

The three structures are **in-memory**.

They are not automatically:

```text
database
distributed cache
durable queue
distributed stream processor
shared state service
```

### Process crash

If:

```python
status_counts = Counter()
```

exists only in process memory and the process crashes:

```text
Counter state → lost
```

### Multiple workers

With four workers:

```text
worker A → Counter
worker B → Counter
worker C → Counter
worker D → Counter
```

you have four local states.

If the system needs a global metric, the states must be merged or exported.

### Persistent architecture

A production pattern could be:

```text
raw inference events
       ↓
durable event/log system
       ↓
consumer
       ↓
local Counter/defaultdict/deque
       ↓
metrics / diagnostics
```

The collections are useful local processing tools, not the complete architecture.

---

# Part IX — Testing

## 89. Testing Counter

### Empty Counter

```python
from collections import Counter

def test_empty_counter():
    counts = Counter()
    assert counts == Counter()
```

### Basic counting

```python
def test_basic_counting():
    counts = Counter(["a", "a", "b"])

    assert counts["a"] == 2
    assert counts["b"] == 1
```

### Missing key

```python
def test_missing_key_returns_zero():
    counts = Counter()

    assert counts["missing"] == 0
    assert "missing" not in counts
```

### `most_common`

```python
def test_most_common():
    counts = Counter(["a", "a", "b"])

    assert counts.most_common(1) == [("a", 2)]
```

### `total`

```python
def test_total():
    counts = Counter(a=2, b=3)

    assert counts.total() == 5
```

### `update`

```python
def test_update_accumulates():
    counts = Counter(a=1)

    counts.update({"a": 2})

    assert counts["a"] == 3
```

### `subtract`

```python
def test_subtract_preserves_negative():
    counts = Counter(a=1)

    counts.subtract({"a": 3})

    assert counts["a"] == -2
```

### Zero and negative

```python
def test_zero_and_negative_counts():
    counts = Counter(a=1)

    counts["b"] = 0
    counts["c"] = -1

    assert counts["b"] == 0
    assert counts["c"] == -1
```

### Arithmetic

```python
def test_counter_arithmetic():
    left = Counter(a=3, b=1)
    right = Counter(a=1, b=2)

    assert left + right == Counter(a=4, b=3)
    assert left - right == Counter(a=2)
    assert left & right == Counter(a=1, b=1)
    assert left | right == Counter(a=3, b=2)
```

### Comparison

```python
def test_counter_comparison():
    smaller = Counter(a=1)
    larger = Counter(a=2)

    assert smaller <= larger
    assert smaller < larger
```

### Conversion

```python
def test_counter_to_dict():
    counts = Counter(a=2, b=1)

    assert dict(counts) == {"a": 2, "b": 1}
```

---

## 90. Testing defaultdict

### Missing key creates the default

```python
from collections import defaultdict

def test_defaultdict_list_factory():
    groups = defaultdict(list)

    groups["fruit"].append("apple")

    assert groups["fruit"] == ["apple"]
```

### Set factory

```python
def test_defaultdict_set_factory():
    groups = defaultdict(set)

    groups["admin"].add("alice")
    groups["admin"].add("alice")

    assert groups["admin"] == {"alice"}
```

### Integer factory

```python
def test_defaultdict_int_factory():
    counts = defaultdict(int)

    counts["a"] += 1
    counts["a"] += 1

    assert counts["a"] == 2
```

### Custom factory

```python
def make_config():
    return {"enabled": True}

def test_custom_factory_creates_independent_values():
    configs = defaultdict(make_config)

    first = configs["a"]
    second = configs["b"]

    assert first == {"enabled": True}
    assert second == {"enabled": True}
    assert first is not second
```

### `get()` does not create

```python
def test_defaultdict_get_does_not_create():
    groups = defaultdict(list)

    assert groups.get("missing") is None
    assert "missing" not in groups
```

### Bracket lookup creates

```python
def test_defaultdict_bracket_lookup_creates():
    groups = defaultdict(list)

    _ = groups["missing"]

    assert "missing" in groups
```

---

## 91. Testing deque

### Append and pop

```python
from collections import deque

def test_deque_right_operations():
    d = deque()

    d.append("a")
    d.append("b")

    assert d.pop() == "b"
    assert d.pop() == "a"
```

### Appendleft and popleft

```python
def test_deque_left_operations():
    d = deque()

    d.appendleft("b")
    d.appendleft("a")

    assert d.popleft() == "a"
    assert d.popleft() == "b"
```

### Extend

```python
def test_deque_extend():
    d = deque([1])

    d.extend([2, 3])

    assert list(d) == [1, 2, 3]
```

### Extendleft

```python
def test_deque_extendleft_reverses_input():
    d = deque()

    d.extendleft([1, 2, 3])

    assert list(d) == [3, 2, 1]
```

### Rotate

```python
def test_deque_rotate():
    d = deque([1, 2, 3])

    d.rotate(1)

    assert list(d) == [3, 1, 2]
```

### Maxlen

```python
def test_deque_maxlen():
    d = deque(maxlen=2)

    d.append(1)
    d.append(2)
    d.append(3)

    assert list(d) == [2, 3]
```

### Remove

```python
def test_deque_remove():
    d = deque(["a", "b", "a"])

    d.remove("a")

    assert list(d) == ["b", "a"]
```

### Count

```python
def test_deque_count():
    d = deque(["a", "b", "a"])

    assert d.count("a") == 2
```

### Index

```python
def test_deque_index():
    d = deque(["a", "b", "c"])

    assert d.index("b") == 1
```

### Reverse

```python
def test_deque_reverse():
    d = deque([1, 2, 3])

    d.reverse()

    assert list(d) == [3, 2, 1]
```

### Copy

```python
def test_deque_copy():
    original = deque([1, 2])
    other = original.copy()

    other.append(3)

    assert list(original) == [1, 2]
    assert list(other) == [1, 2, 3]
```

---

## 92. Testing the Integrated Inference Monitor

### Ingestion

```python
def test_monitor_ingests_event():
    monitor = InferenceMonitor(recent_limit=2)

    monitor.ingest(
        make_event("r1", "model-a", "success", 100.0)
    )

    assert monitor.status_counts["success"] == 1
    assert monitor.model_counts["model-a"] == 1
```

### Grouping

```python
def test_monitor_groups_by_model():
    monitor = InferenceMonitor()

    monitor.ingest(make_event("r1", "model-a", "success", 100.0))
    monitor.ingest(make_event("r2", "model-a", "timeout", 300.0))

    assert len(monitor.model_events("model-a")) == 2
```

### Recent retention

```python
def test_monitor_retains_recent_limit():
    monitor = InferenceMonitor(recent_limit=2)

    monitor.ingest(make_event("r1", "model-a", "success", 100.0))
    monitor.ingest(make_event("r2", "model-a", "success", 100.0))
    monitor.ingest(make_event("r3", "model-a", "success", 100.0))

    ids = [event.request_id for event in monitor.recent()]

    assert ids == ["r2", "r3"]
```

### Empty latency

```python
def test_monitor_empty_latency_summary():
    monitor = InferenceMonitor()

    assert monitor.latency_summary() == {
        "count": 0.0,
        "mean_ms": 0.0,
    }
```

### Unknown model

```python
def test_monitor_unknown_model():
    monitor = InferenceMonitor()

    assert monitor.model_events("unknown") == []
```

### Invalid latency

```python
import pytest

def test_monitor_rejects_negative_latency():
    monitor = InferenceMonitor()

    event = make_event("r1", "model-a", "success", -1.0)

    with pytest.raises(ValueError):
        monitor.ingest(event)
```

### Timezone-aware timestamp

The monitor's timestamp validation reinforces a broader production habit:

```text
make time assumptions explicit
```

The test suite should verify whatever timestamp contract the application adopts.

---

# Part X — Debugging

## 93. Debugging Counter

### Broken update assumption

```python
counts = Counter(a=3)
counts.update({"a": 7})

assert counts["a"] == 7
```

The assertion fails because the result is:

```text
10
```

#### Debug workflow

1. Inspect the object:

```python
print(counts)
```

2. Inspect the existing value:

```python
print(counts["a"])
```

3. Ask whether the operation means:
   - replacement; or
   - accumulation.

4. If replacement is intended:

```python
counts["a"] = 7
```

5. If accumulation is intended:

```python
counts.update({"a": 7})
```

---

### Broken subtraction assumption

```python
remaining = Counter(a=1) - Counter(a=3)

print(remaining)
```

The result does not contain `a`.

#### Diagnosis

Binary Counter subtraction is multiset subtraction and keeps only positive results.

Signed delta:

```python
remaining = Counter(a=1)
remaining.subtract(Counter(a=3))

print(remaining["a"])
```

Output:

```text
-2
```

---

### Broken missing-key assumption

```python
counts = Counter()

print(counts["missing"])
print("missing" in counts)
```

Output:

```text
0
False
```

The lookup result and membership state are different concepts.

---

### Broken iteration assumption

**BAD**

```python
for key in counts:
    if counts[key] <= 0:
        del counts[key]
```

Prefer to identify keys first:

```python
for key in [k for k, v in counts.items() if v <= 0]:
    del counts[key]
```

Or, when all non-positive counts should be removed:

```python
counts = +counts
```

---

## 94. Debugging defaultdict

### Accidental key creation

Broken:

```python
groups = defaultdict(list)

print(groups["unknown"])
print("unknown" in groups)
```

After the first line, `"unknown"` exists.

#### Diagnostic fix

```python
print(groups.get("unknown"))
print("unknown" in groups)
```

Now inspection does not create the group.

---

### Factory confusion

Broken:

```python
groups = defaultdict(lambda: shared_list)
```

where:

```python
shared_list = []
```

Every missing key receives the same object.

Fix:

```python
groups = defaultdict(list)
```

or a custom factory that creates a fresh object each time.

---

### Nested factory confusion

If the value type is hard to explain, the design may be too implicit.

Use a named factory:

```python
def make_model_state():
    return defaultdict(list)

model_states = defaultdict(make_model_state)
```

This is often easier to test and document than deeply nested anonymous lambdas.

---

### `get()` confusion

Broken:

```python
groups = defaultdict(list)

values = groups.get("fruit")
values.append("apple")
```

`values` can be `None`.

Correct when initialization is intended:

```python
groups["fruit"].append("apple")
```

---

## 95. Debugging deque

### `extendleft()` surprise

```python
d = deque()
d.extendleft([1, 2, 3])

print(list(d))
```

Output:

```text
[3, 2, 1]
```

Reason: sequential left insertion reverses the input.

---

### `maxlen` surprise

```python
d = deque(maxlen=3)

for x in [1, 2, 3, 4]:
    d.append(x)

print(list(d))
```

Output:

```text
[2, 3, 4]
```

Reason: old data is evicted.

---

### Indexing mistake

```python
d = deque([1, 2])

# d[10]
```

raises `IndexError`.

Do not assume deque indexing silently returns `None`.

---

### Remove mistake

```python
d = deque([1, 2, 3])

# d.remove(99)
```

raises `ValueError`.

If absence is expected:

```python
if 99 in d:
    d.remove(99)
```

Remember that this is a search plus a second operation, so concurrency-sensitive code should not treat it as an atomic "check and remove."

---

# Part XI — Common production mistakes

## 96. Common Production Mistakes

### Mistake 1 — specialized container chosen without an access-pattern analysis

Ask first:

```text
What operations dominate?
```

### Mistake 2 — hiding important mutation

With `defaultdict`:

```python
d[key]
```

can be mutating.

With bounded `deque`:

```python
append()
```

can evict old data.

With Counter:

```python
subtract()
```

can create negative counts.

Document surprising semantics.

### Mistake 3 — using Counter for arbitrary mapping state

```python
state = Counter()
```

is confusing when values are not counts.

Use a normal dict or domain object.

### Mistake 4 — nested defaultdicts become unreadable

Concise syntax can obscure the schema.

### Mistake 5 — assuming every deque operation is O(1)

Only the end-oriented operations are the main performance strength.

### Mistake 6 — using deque for frequent random access

If the application does a large amount of:

```python
d[i]
```

especially in the middle, reconsider list or another indexed structure.

### Mistake 7 — unbounded history

```python
events = deque()
```

in a service that runs indefinitely can create unbounded retention.

### Mistake 8 — treating in-memory state as durable

Crash means local state disappears unless persisted.

### Mistake 9 — assuming a local Counter is globally shared

Multiple workers create independent process-local objects.

### Mistake 10 — using deque as a complete producer-consumer abstraction

For threaded waiting and task tracking, evaluate `queue.Queue`. citeturn838217view1

### Mistake 11 — misunderstanding `extendleft()`

Always test order when this method is introduced into non-trivial code.

### Mistake 12 — using `maxlen` without a data-loss decision

Eviction is a feature only when discarding old records is acceptable.

---

# Part XII — Progressive exercises

## 97. Progressive Exercises

Solve each problem before consulting the later check guidance.

### Level 1 — Counter Basics

#### Exercise 1: words

Count:

```python
text = "ai engineering needs engineering discipline"
```

Requirements:

- use `Counter`;
- count complete words;
- verify the top frequency.

Hint:

```python
Counter(text.split())
```

#### Exercise 2: characters

Count:

```python
value = "mississippi"
```

Expected:

```text
i → 4
s → 4
p → 2
m → 1
```

#### Exercise 3: categories

Count:

```python
categories = ["a", "b", "a", "c", "b", "a"]
```

Then return the top two categories.

---

### Level 2 — Counter Analysis

#### Exercise 4: least common values

Given a Counter, return the three least common elements.

Constraints:

- preserve `(element, count)` pairs;
- do not use a third-party package.

Hint:

Start from `most_common()` and reason about reverse order.

#### Exercise 5: signed subtraction

Start with:

```python
counts = Counter(a=10)
```

Subtract 12 while preserving the negative result.

Expected:

```text
a → -2
```

#### Exercise 6: normalize

Given:

```python
counts = Counter(a=2, b=0, c=-1)
```

produce:

```text
Counter({'a': 2})
```

---

### Level 3 — defaultdict Grouping

#### Exercise 7: users by department

Input:

```python
records = [
    ("engineering", "alice"),
    ("finance", "bob"),
    ("engineering", "carol"),
]
```

Expected:

```text
engineering → ["alice", "carol"]
finance     → ["bob"]
```

Hint:

```python
defaultdict(list)
```

---

### Level 4 — defaultdict Graph

#### Exercise 8: adjacency sets

Input:

```python
edges = [
    ("A", "B"),
    ("A", "C"),
    ("B", "D"),
    ("A", "B"),
]
```

Create:

```text
A → {B, C}
B → {D}
```

Hint:

```python
defaultdict(set)
```

---

### Level 5 — deque FIFO

#### Exercise 9: queue

Process:

```text
job-1
job-2
job-3
```

in insertion order.

Hint:

```text
append + popleft
```

---

### Level 6 — deque LIFO

#### Exercise 10: stack

Push:

```text
A
B
C
```

and pop all items.

Expected:

```text
C
B
A
```

---

### Level 7 — bounded deque

#### Exercise 11: last five

Create:

```python
history = deque(maxlen=5)
```

Insert seven event IDs.

Expected:

```text
only the latest five remain
```

---

### Level 8 — sliding window

#### Exercise 12: last-three average

Keep only the latest three values and calculate the average after each insertion.

Bonus:

Maintain a rolling sum rather than recalculating `sum(window)`.

---

### Level 9 — combined structures

#### Exercise 13: event pipeline

For records containing:

```text
model
status
request_id
```

use:

```text
Counter
defaultdict
deque
```

to produce:

1. status counts;
2. events grouped by model;
3. latest N events.

Every structure must have one clear responsibility.

---

### Level 10 — Applied AI

#### Exercise 14: inference monitoring buffer

Build a monitor around:

```python
{
    "request_id": "...",
    "model": "...",
    "status": "...",
    "latency_ms": ...,
}
```

Requirements:

- event/status frequency;
- model frequency;
- grouping by model;
- latest N events;
- top failure categories;
- recent mean latency;
- invalid latency rejection;
- empty-input behavior;
- tests;
- documented production limitations.

Do not create separate project files. Keep the entire exercise in this chapter while practicing.

---

# Part XIII — Answer/check guidance

## 98. Answer and Check Guidance

### Level 1

```python
from collections import Counter

text = "ai engineering needs engineering discipline"

counts = Counter(text.split())

assert counts["engineering"] == 2
assert counts.most_common(1) == [("engineering", 2)]
```

### Level 2

```python
counts = Counter(a=10)

counts.subtract({"a": 12})

assert counts["a"] == -2
```

Normalize:

```python
normalized = +Counter(a=2, b=0, c=-1)

assert normalized == Counter(a=2)
```

### Level 3

```python
groups = defaultdict(list)

for department, user in records:
    groups[department].append(user)

assert groups["engineering"] == ["alice", "carol"]
```

### Level 4

```python
graph = defaultdict(set)

for source, target in edges:
    graph[source].add(target)

assert graph["A"] == {"B", "C"}
```

### Level 7

```python
history = deque(maxlen=5)

for value in range(7):
    history.append(value)

assert list(history) == [2, 3, 4, 5, 6]
```

### Level 9

A sound combined design is:

```text
Counter
    → aggregate counts

defaultdict
    → grouped records

deque
    → bounded recent records
```

If one collection is doing all three jobs, the design probably needs clearer boundaries.

---

# Part XIV — Knowledge checks

## 99. Knowledge Checks

Answer these without looking back.

### Counter

1. What is `Counter`?
2. Why does it exist?
3. What does "hashable element" mean?
4. What does `Counter()` create?
5. What does `Counter(iterable)` do?
6. What does `Counter(mapping)` mean?
7. What does a missing Counter key return?
8. Does a missing lookup necessarily create a key?
9. What does `elements()` return?
10. How are zero and negative counts handled by `elements()`?
11. What does `most_common()` return?
12. What does `most_common(n)` mean?
13. What does `total()` calculate?
14. When was `total()` added?
15. How does `Counter.update()` differ from `dict.update()`?
16. What does `subtract()` do?
17. Why can `subtract()` produce negative counts?
18. What do `+`, `-`, `&`, and `|` mean?
19. Why can Counter contain zero and negative counts?
20. What does unary `+counter` do?
21. What do modern Counter comparisons mean?
22. How does modern Counter equality treat missing keys and zero counts?
23. Does Counter implement `fromkeys()`?

### defaultdict

24. What is `defaultdict`?
25. What is `default_factory`?
26. What does the factory have to be?
27. When does the factory execute?
28. What happens if the factory is `None`?
29. What is `__missing__()`?
30. Why does `d[key]` potentially mutate a defaultdict?
31. Why does `d.get(key)` not invoke the factory?
32. Why is `defaultdict(list)` useful for grouping?
33. Why is `defaultdict(set)` useful for unique relationships?
34. Why is `defaultdict(int)` useful for numeric accumulation?
35. Why might Counter be clearer for pure frequency counting?
36. What is the danger of a shared mutable default?
37. Why can nested defaultdicts become unreadable?

### deque

38. What is deque?
39. Why is it useful for queues?
40. Why is repeated `list.pop(0)` inefficient?
41. What does `append()` do?
42. What does `appendleft()` do?
43. What does `pop()` do?
44. What does `popleft()` do?
45. What does `extend()` do?
46. Why does `extendleft()` reverse the input order?
47. What does `rotate()` do?
48. What does `remove()` do on a missing value?
49. What does `count()` do?
50. What does `index()` do?
51. What does `insert()` do?
52. What does `reverse()` return?
53. What does `copy()` mean by shallow copy?
54. What is `maxlen`?
55. Why can bounded deques discard data?
56. Why is deque not a general random-access list replacement?

### Architecture

57. When should you use `queue.Queue`?
58. Does a deque automatically synchronize a complete producer-consumer workflow?
59. Are these structures durable?
60. What happens to their in-memory state when the process crashes?
61. What changes when four workers each have their own Counter?
62. How could Counter, defaultdict, and deque cooperate in an AI monitoring pipeline?

---

# Part XV — Interview questions

## 100. Interview Questions

### Beginner

**1. What is Counter?**

Expected points:

- dict subclass;
- counts hashable objects;
- element → count;
- counting-specific operations.

**2. What is defaultdict?**

Expected points:

- dict subclass;
- default factory;
- missing-key initialization via `[]`.

**3. What is deque?**

Expected points:

- double-ended queue;
- efficient end operations;
- useful for queues, stacks, windows, and bounded buffers.

---

### Intermediate

**4. Counter versus dict?**

Discuss:

- frequency semantics;
- missing lookup;
- specialized APIs;
- dictionary compatibility with important differences.

**5. Counter versus defaultdict(int)?**

Discuss:

- both can count;
- Counter communicates counting intent;
- Counter provides additional counting operations.

**6. defaultdict versus setdefault()?**

Discuss:

- stable default policy versus local initialization;
- readability;
- side effects.

**7. deque versus list?**

Discuss:

- end operations;
- random access;
- FIFO workloads.

**8. deque versus queue.Queue?**

Discuss:

- container versus synchronized queue abstraction;
- blocking;
- task tracking;
- multiple threaded producers/consumers.

---

### Advanced

**9. Explain Counter arithmetic.**

```text
+ → corresponding counts added
- → subtract, keep positive outputs
& → minimum counts
| → maximum counts
```

**10. Explain signed Counter values.**

Counts may be zero or negative, especially for delta/reconciliation use cases, but multiset operations intentionally drop non-positive results.

**11. Explain defaultdict `__missing__()`.**

Mention:

- bracket lookup only;
- factory called with no arguments;
- result inserted;
- factory errors propagate.

**12. Why does extendleft reverse order?**

Because each incoming element is inserted on the left sequentially.

**13. Explain deque complexity.**

Mention:

- efficient operations at either end;
- indexing toward the middle is slower;
- search methods are linear-style operations.

**14. Why is queue.Queue not just a deque with different method names?**

Because it supplies synchronization-oriented semantics such as blocking and task tracking for threaded producer-consumer workflows. citeturn838217view1

---

### Production

**15. How would you analyze API error frequency?**

Use Counter for local aggregation and export the summary to a monitoring/metrics system.

**16. How would you group AI events by model?**

Use `defaultdict(list)` or a more specialized indexed representation when appropriate.

**17. How would you keep only the last 100 events?**

Use:

```python
deque(maxlen=100)
```

when automatic eviction is acceptable.

**18. How would you prevent memory from growing indefinitely?**

Use bounded structures, aggregation, sampling, external persistence, retention policies, or a combination.

**19. How would you handle several workers?**

Recognize that each process has local memory. Merge/export state or use shared/external state as required.

---

# Part XVI — Architecture scenarios

## 101. Architecture Scenarios

### Scenario 1 — API log analytics

Need:

```text
status → frequency
```

Candidate:

```python
Counter()
```

Questions:

- How many keys can exist?
- How often is aggregation flushed?
- Where do raw logs live?
- Is the count per process or global?

---

### Scenario 2 — AI inference monitoring

Need:

```text
status counts
model counts
events by model
last 100 events
```

A local design can use:

```text
Counter
Counter
defaultdict(list)
deque(maxlen=100)
```

Questions:

- Which state is durable?
- Which state is a local cache?
- How are worker totals merged?
- What information is safe to retain?

---

### Scenario 3 — RAG ingestion grouping

Need:

```text
source → documents
language → documents
```

Use grouping structures.

Questions:

- How large can a group become?
- Is all raw document state necessary in memory?
- Could the database become the source of truth?

---

### Scenario 4 — Agent recent history

Need the last 20 tool calls.

Use:

```python
deque(maxlen=20)
```

Questions:

- Is this only diagnostic context?
- Must history survive restarts?
- Could events contain large payloads?
- Is per-agent memory bounded?

---

### Scenario 5 — Sliding-window monitoring

Need:

```text
number of requests in the last 10 seconds
```

A local deque of monotonic timestamps is a conceptual building block.

Questions:

- Is the limit global or per worker?
- Does the implementation need distributed coordination?
- What happens when clocks or process restarts change local state?

---

### Scenario 6 — In-memory FIFO worklist

Need simple synchronous FIFO behavior.

Use:

```python
queue = deque()
queue.append(task)
task = queue.popleft()
```

Questions:

- Do producers need to block?
- Do consumers need to wait?
- Is task completion tracked?
- Is cross-thread or cross-process coordination required?

If yes, evaluate the relevant queue abstraction.

---

### Scenario 7 — Large production event stream

Need:

```text
billions of events
many workers
durability
replay
global aggregation
```

`Counter`, `defaultdict`, and `deque` can still be useful inside each worker, but they are no longer the complete system architecture.

---

# Part XVII — Debugging challenges

## 102. Debugging Challenges

### Challenge 1 — Counter update

```python
counts = Counter(a=3)
counts.update({"a": 7})

assert counts["a"] == 7
```

Task:

- diagnose;
- explain;
- correct.

---

### Challenge 2 — Counter negative result

```python
result = Counter(a=1) - Counter(a=3)

assert result["a"] == -2
```

Task:

- explain why the assertion fails;
- show signed subtraction.

---

### Challenge 3 — Counter zero key

```python
counts = Counter()
counts["a"] = 0

print(len(counts))
print("a" in counts)
```

Task:

- explain stored zero versus absent key.

---

### Challenge 4 — defaultdict mutation during inspection

```python
groups = defaultdict(list)

print(groups["unknown"])
print(dict(groups))
```

Task:

- identify the state change;
- show a non-mutating lookup.

---

### Challenge 5 — shared default factory

```python
shared = []

groups = defaultdict(lambda: shared)

groups["a"].append(1)

print(groups["b"])
```

Task:

- diagnose shared state;
- correct the factory.

---

### Challenge 6 — extendleft order

```python
d = deque()
d.extendleft(["A", "B", "C"])

assert list(d) == ["A", "B", "C"]
```

Task:

- determine actual order;
- explain why;
- correct if original order is required.

---

### Challenge 7 — maxlen eviction

```python
history = deque(maxlen=3)

for value in ["a", "b", "c", "d"]:
    history.append(value)

assert list(history) == ["a", "b", "c", "d"]
```

Task:

- explain the failed assertion;
- identify the memory/retention policy.

---

### Challenge 8 — wrong structure

```python
events = deque()

events.append({"request_id": "r1"})
events.append({"request_id": "r2"})

# events["r1"]
```

Task:

- identify the intended access pattern;
- choose a structure that supports it;
- explain whether a combination of deque plus dict could be useful.

---

# Part XVIII — API completeness

## 103. API Coverage Requirement

This chapter covers the relevant public API expected for this roadmap topic.

### Counter

```text
Counter()
Counter(iterable)
Counter(mapping)
Counter(**kwargs)

c[key]
elements()
most_common()
total()
update()
subtract()

keys()
values()
items()
get()
pop()
popitem()
clear()
copy()
setdefault()

dict(c)
len(c)
key in c

+
-
&
|
==
!=
<
<=
>
>=
```

Important special case:

```text
Counter.fromkeys()
```

is not implemented.

### defaultdict

```text
defaultdict()
defaultdict(default_factory)
default_factory
__missing__()
d[key]
get()
setdefault()

keys()
values()
items()
pop()
popitem()
clear()
copy()
update()

|
|=
```

`|` and `|=` were added for defaultdict with the dictionary merge operators in Python 3.9. citeturn309077view1

### deque

```text
deque()
deque(iterable)
deque(iterable, maxlen)

append()
appendleft()
pop()
popleft()

extend()
extendleft()
rotate()

remove()
count()
index()
insert()

reverse()
copy()
clear()

maxlen
len()
iteration
reversed()
membership
indexing
```

Current documentation also lists support for concatenation/repetition operations such as `__add__()`, `__mul__()`, and `__imul__()` from Python 3.5, but these are secondary to the access patterns emphasized in this chapter. citeturn309077view0

---

# Part XIX — Version and typing notes

## 104. Version Compatibility

### Counter

Current Python documentation records:

```text
Counter introduced → Python 3.1
subtract()          → Python 3.2
unary +/- and multiset in-place ops → Python 3.3
total()             → Python 3.10
rich comparisons    → Python 3.10
```

The equality semantics for missing elements also changed in Python 3.10. citeturn838217view0

### defaultdict

Merge operators:

```python
d1 | d2
d1 |= d2
```

were added in Python 3.9. citeturn309077view1

### deque

Current docs describe:

- `count()` added in 3.2;
- `copy()` added in 3.5;
- maximum length through read-only `maxlen`;
- generic typing support.

citeturn309077view0

### Modern typing

Modern Python type syntax can parameterize these runtime collections:

```python
from collections import Counter, defaultdict, deque

status_counts: Counter[str]
events_by_model: defaultdict[str, list[str]]
recent_ids: deque[str]
```

This is preferable to legacy `typing.Counter`, `typing.DefaultDict`, and `typing.Deque` aliases in modern code. The current typing documentation marks those aliases as deprecated in favor of the concrete collection classes supporting subscription. citeturn499290search2

---

# Part XX — Production reasoning drills

## 105. Production Reasoning Drills

### Drill 1 — unique request IDs

Suppose one process sees ten million unique request IDs.

Question:

```python
request_counts = Counter(request_ids)
```

Would keeping it forever be safe?

Reason:

```text
distinct keys ≈ number of events
memory can become large
```

Possible design responses:

```text
aggregate on lower-cardinality dimensions
flush periodically
sample
persist externally
expire old state
```

---

### Drill 2 — raw objects in grouped lists

Suppose:

```python
documents_by_model = defaultdict(list)
```

stores every full document object indefinitely.

Ask:

- How much memory can one model group use?
- Is all data needed in memory?
- Can only IDs be retained?
- Should the durable document store be the source of truth?

---

### Drill 3 — recent event buffer

Need last 100 events:

```python
recent = deque(maxlen=100)
```

Ask:

- Are all fields necessary?
- Can payloads be oversized?
- Is eviction acceptable?
- Should the event be persisted before it is evicted?

---

### Drill 4 — multiple workers

Four workers each keep:

```python
status_counts = Counter()
```

The dashboard asks for global status counts.

The answer is not "the Counter automatically combines."

You need:

```text
local aggregation
+
merge/export/shared state
```

---

### Drill 5 — concurrency boundary

Need:

```text
10 worker threads
producer sends work
consumers wait for work
```

The problem is now synchronization-oriented.

Evaluate:

```python
queue.Queue()
```

rather than treating a deque as the complete solution. citeturn838217view1

---

# Part XXI — Mini-project specification

## 106. Mini-Project — Production-Oriented AI Event Monitoring Buffer

### Objective

Design a small in-memory monitoring component that receives AI-system events and exposes operational summaries.

The implementation must use:

```text
Counter
defaultdict
deque
```

with one clear responsibility per structure.

### Functional requirements

1. Accept inference events.
2. Count event/status frequency.
3. Count model usage.
4. Group events by model.
5. Retain only the latest N recent events.
6. Identify top failure categories.
7. Inspect events by model.
8. Calculate a basic recent latency statistic.
9. Validate input.
10. Avoid unbounded recent-event growth.
11. Include tests.
12. Document production limitations.

### Data model

Suggested:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class InferenceEvent:
    request_id: str
    model: str
    status: str
    latency_ms: float
    timestamp: datetime
```

### Conceptual architecture

```text
                  InferenceEvent
                        |
                        v
                +---------------+
                |   Ingest      |
                +-------+-------+
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
     Counter        defaultdict        deque
        |               |               |
        v               v               v
   frequencies       groupings       recent N
```

### Data-structure decisions

#### Counter

```text
status → count
model → count
```

#### defaultdict

```text
model → events
```

#### deque

```text
latest N events
```

### Implementation tasks

1. Define the event type.
2. Define monitor initialization.
3. Validate `recent_limit`.
4. Validate latency.
5. Validate required identifiers.
6. Validate timestamp semantics.
7. Increment status.
8. Increment model count.
9. Add to model grouping.
10. Append to recent deque.
11. Implement failure summary.
12. Implement model lookup.
13. Implement recent-event access.
14. Implement latency summary.
15. Add tests.
16. Document memory behavior.
17. Document concurrency assumptions.
18. Document persistence assumptions.

### Edge cases

```text
empty monitor
empty model name
unknown status
unknown model lookup
negative latency
duplicate request IDs
very large event payloads
recent_limit = 0
recent_limit < 0
```

Whether duplicate request IDs are rejected or accepted is an application-level invariant. Choose and document one behavior.

### Testing requirements

At minimum test:

```text
event ingestion
counting
grouping
bounded retention
failure summary
empty input
unknown model
invalid latency
```

### Production limitations

Document explicitly:

```text
in-memory only
process-local
not durable
not globally synchronized
not a distributed queue
recent buffer intentionally evicts old entries
```

### Extension tasks

After completing the base project, consider:

- per-provider counts;
- counts by `(model, status)`;
- recent latency deque;
- rolling success rate;
- sampling;
- persistence interface;
- asynchronous queue boundary;
- multi-worker aggregation;
- observability export.

### No additional files

The project specification belongs entirely in this Markdown document. Do not create project files, exercise files, answer keys, or configuration files as part of this chapter.

---

# Part XXII — Final production checklist

## 107. Production Checklist

Before shipping code that uses these structures:

```text
[ ] Is the primary access pattern clear?
[ ] Is Counter actually being used for counting?
[ ] Is defaultdict being used intentionally?
[ ] Is deque being used for end-oriented operations?
[ ] Are accidental defaultdict key creations understood?
[ ] Is Counter missing-key behavior understood?
[ ] Is Counter.update() semantics understood?
[ ] Is Counter.subtract() semantics understood?
[ ] Are zero and negative counts intentional?
[ ] Is maxlen used when retention should be bounded?
[ ] Is automatic deque eviction acceptable?
[ ] Are deque middle/search operations understood?
[ ] Are complexity characteristics understood?
[ ] Are memory growth characteristics understood?
[ ] Are in-memory limitations understood?
[ ] Are concurrency requirements considered?
[ ] Are multiple workers considered?
[ ] Are persistence requirements considered?
[ ] Are edge cases tested?
[ ] Are surprising semantics documented?
[ ] Is the code readable to another engineer?
[ ] Could the local structure later be replaced by an external system?
```

---

# Part XXIII — Final decision framework

## 108. Final Decision Framework

When a new data-structure requirement arrives, do not begin with the class name.

Begin with the operation.

### Step 1 — Identify the question

```text
How many?
    → Counter

What belongs to this key?
    → defaultdict

What is at either end?
    → deque
```

### Step 2 — Identify memory policy

```text
bounded?
unbounded?
evictable?
persistent?
```

### Step 3 — Identify concurrency

```text
single-threaded?
multiple threads?
multiple processes?
multiple service replicas?
```

### Step 4 — Identify durability

```text
reconstructible?
must survive restart?
must be shared?
```

### Step 5 — Identify performance-critical operations

```text
lookup?
append?
popleft?
random access?
search?
ranking?
```

### Step 6 — Choose

```text
frequency                  → Counter
grouping                   → defaultdict
FIFO / both-end buffer     → deque
general mapping            → dict
general sequence           → list
threaded synchronized FIFO → queue.Queue
durable/shared state       → external system
```

### Exceptions are normal

A real application may use several:

```python
status_counts = Counter()
events_by_model = defaultdict(list)
recent_events = deque(maxlen=100)
```

The combination is often more expressive than forcing one structure to represent every access pattern.

---

# Part XXIV — Beginner mental model

## 109. Beginner-Friendly Mental Model

### Counter

Imagine a tally sheet:

```text
apple   |||
banana  ||
orange  |
```

Counter stores:

```text
apple  → 3
banana → 2
orange → 1
```

### defaultdict

Imagine a shelf where every new label automatically gets a new empty box.

```text
new key
   ↓
create empty box
   ↓
put value in box
```

Examples:

```text
defaultdict(list) → new empty list
defaultdict(set)  → new empty set
defaultdict(int)  → 0
```

### deque

Imagine people entering and leaving from both ends of a line:

```text
LEFT ← [ A ][ B ][ C ][ D ] → RIGHT
```

You can:

```text
add left
remove left
add right
remove right
```

That mental model is enough to understand why deque works well for queues and bounded buffers.

---

# Part XXV — Deep engineering mental model

## 110. Advanced Mental Model

A production engineer should see these classes as abstractions over **access patterns**.

### Counter

```text
Domain: frequency
Primary state:
    key → numeric count
Primary operations:
    increment
    aggregate
    rank
    compare
Risk:
    cardinality-driven memory growth
```

### defaultdict

```text
Domain: grouping / initialization
Primary state:
    key → value created by factory
Primary operations:
    lookup
    create
    accumulate
Risk:
    mutation during reads
    accidental keys
    nested complexity
```

### deque

```text
Domain: ordered buffer
Primary state:
    sequence with left/right ends
Primary operations:
    append
    popleft/pop
    rotate
    bounded retention
Risk:
    accidental eviction
    misuse for random access
    confusion with synchronization queues
```

This abstraction-level understanding transfers to other languages and systems.

---

# Part XXVI — One-page reference

## 111. One-Page Reference

```text
COUNTER
-------
Question:
    "How many?"

Example:
    counts = Counter(events)

Core:
    item → count

Important:
    c[key]              → 0 when missing
    c.elements()        → repeated positive integer counts
    c.most_common(n)    → top n
    c.total()           → sum
    c.update(x)         → add counts
    c.subtract(x)       → subtract, retain zero/negative
    c1 + c2             → add, positive results
    c1 - c2             → subtract, positive results
    c1 & c2             → minimum
    c1 | c2             → maximum


DEFAULTDICT
-----------
Question:
    "What should I create for a missing key?"

Example:
    groups = defaultdict(list)

Core:
    key → automatically-created default

Important:
    d[key]              → may create
    d.get(key)          → does not invoke factory
    d.__missing__()     → missing-key hook
    default_factory     → callable or None

Common factories:
    list
    set
    int
    float
    custom function


DEQUE
-----
Question:
    "How do I efficiently work from the ends?"

Example:
    q = deque()

Core:
    left ← elements → right

Important:
    append()            → right
    appendleft()        → left
    pop()               → right
    popleft()           → left
    extend()            → right batch
    extendleft()        → left batch, reverses input order
    rotate()            → rotate right/left
    maxlen              → bounded retention

Queue:
    append + popleft

Stack:
    append + pop

Recent N:
    deque(maxlen=N)


ALTERNATIVES
------------
dict:
    general mapping

list:
    general ordered sequence / random access

queue.Queue:
    synchronized threaded queue

external system:
    persistence / distribution / coordination
```

---

# Part XXVII — Final self-review checklist

## 112. Final Self-Review Checklist

### Counter

```text
[ ] Counter fundamentals are clear.
[ ] Constructor forms are clear.
[ ] Hashable keys are understood.
[ ] Missing-key lookup is understood.
[ ] Zero versus absence is understood.
[ ] elements() is understood.
[ ] most_common() is understood.
[ ] total() is understood.
[ ] update() is understood.
[ ] subtract() is understood.
[ ] Arithmetic is understood.
[ ] Rich comparisons are understood.
[ ] Zero counts are understood.
[ ] Negative counts are understood.
[ ] Dict-like methods are understood.
[ ] fromkeys() non-support is known.
[ ] Performance is understood.
[ ] Use cases are understood.
```

### defaultdict

```text
[ ] defaultdict fundamentals are clear.
[ ] default_factory is clear.
[ ] list factory is clear.
[ ] set factory is clear.
[ ] int factory is clear.
[ ] float factory is clear.
[ ] custom factory is clear.
[ ] __missing__() is clear.
[ ] d[key] versus get() is clear.
[ ] accidental creation is understood.
[ ] setdefault comparison is understood.
[ ] nested defaultdict trade-offs are understood.
[ ] graph/grouping use cases are understood.
[ ] performance is understood.
[ ] memory behavior is understood.
```

### deque

```text
[ ] deque fundamentals are clear.
[ ] list comparison is clear.
[ ] append() is clear.
[ ] appendleft() is clear.
[ ] pop() is clear.
[ ] popleft() is clear.
[ ] extend() is clear.
[ ] extendleft() order is clear.
[ ] rotate() is clear.
[ ] remove() is clear.
[ ] count() is clear.
[ ] index() is clear.
[ ] insert() is clear.
[ ] reverse() is clear.
[ ] copy() is clear.
[ ] maxlen is clear.
[ ] bounded buffers are clear.
[ ] indexing behavior is clear.
[ ] iteration is clear.
[ ] queue use case is clear.
[ ] stack use case is clear.
[ ] sliding-window use case is clear.
[ ] queue.Queue boundary is clear.
```

### Production

```text
[ ] Complexity is understood.
[ ] Memory trade-offs are understood.
[ ] Data-structure selection is understood.
[ ] Concurrency boundary is understood.
[ ] Persistence boundary is understood.
[ ] Testing strategy is understood.
[ ] Debugging patterns are understood.
[ ] Applied AI connections are understood.
[ ] Integrated example is understood.
[ ] Mini-project is understood.
[ ] Production limitations are explicit.
```

---

# Part XXVIII — Final mastery questions

## 113. Final Mastery Test

Without looking at the answers, explain the following.

### Counter

1. Why use Counter instead of a normal dict?
2. Why does a missing Counter lookup return zero?
3. Why does zero not imply the key exists?
4. What is the difference between `update()` and `dict.update()`?
5. What is the difference between `subtract()` and `-`?
6. What do `&` and `|` mean?
7. Why can a Counter contain negative values?
8. When is unary `+` useful?
9. What does `total()` mean?
10. What does `most_common()` provide?

### defaultdict

11. What problem does defaultdict solve?
12. What is the default factory?
13. Why must it be callable?
14. What happens on `d[key]` when the key is absent?
15. Why does `d.get(key)` not create a default?
16. How can accidental reads create state?
17. How do `defaultdict(list)` and `defaultdict(set)` differ?
18. Why can a custom factory be safer than shared mutable state?
19. When is `defaultdict` less clear than a normal dict?

### deque

20. Why is deque a natural FIFO container?
21. Why is `list.pop(0)` expensive?
22. What does `extendleft()` do?
23. What does `rotate()` do?
24. What does `maxlen` guarantee?
25. Why can maxlen cause data loss?
26. Why is deque not a general replacement for list?
27. Which operations are its main performance strength?
28. Why is `queue.Queue` a different abstraction?

### Architecture

29. What happens if the process crashes?
30. What happens if there are four worker processes?
31. When does persistence become necessary?
32. When does a thread synchronization abstraction become necessary?
33. How would you use all three structures in an AI inference monitoring component?
34. What memory policy would you use for recent event history?
35. What metrics would you monitor for the in-memory structures themselves?

### Final challenge

For a new system requirement, write down:

```text
1. Domain question
2. Required operations
3. Access pattern
4. Candidate structure
5. Expected complexity
6. Memory growth
7. Mutation semantics
8. Concurrency model
9. Persistence requirement
10. Failure behavior
11. Tests
12. External-system boundary
```

Only then write the implementation.

---

# Part XXIX — Closing principle

## 114. Final Mental Model

### Counter

> **"How many times did each thing occur?"**

```text
item → count
```

### defaultdict

> **"What should I automatically create when this key does not exist?"**

```text
key → automatically-created default value
```

### deque

> **"How do I efficiently add and remove items from either end?"**

```text
LEFT ← [ elements ] → RIGHT
```

### Put them together

```text
Counter
    → frequency analysis

defaultdict
    → grouping / automatic initialization

deque
    → queues / stacks / sliding windows / bounded history
```

### The final engineering rule

> **Choose the data structure based on access pattern and semantic intent, then verify complexity, memory, mutation, concurrency, and persistence requirements.**

That is the transferable skill.

---


# Appendix A — API edge cases worth knowing

## 115. Counter API Edge Cases

### `del`

A Counter's zero-valued entry can be removed explicitly:

```python
counts = Counter(a=2)

counts["a"] = 0
print("a" in counts)

del counts["a"]

print("a" in counts)
```

Output:

```text
True
False
```

### `clear()`

```python
counts = Counter(a=1, b=2)

counts.clear()

assert counts == Counter()
```

### `copy()`

```python
counts = Counter(a=2)

clone = counts.copy()
clone["a"] += 1

assert counts["a"] == 2
assert clone["a"] == 3
```

### `pop()`

```python
counts = Counter(a=2, b=1)

value = counts.pop("a")

assert value == 2
assert "a" not in counts
```

Optional default:

```python
value = counts.pop("missing", 0)

assert value == 0
```

### `popitem()`

```python
counts = Counter(a=2, b=1)

item = counts.popitem()

assert item[0] in {"a", "b"}
```

Do not use `popitem()` when you need the most-common item. Use `most_common()` for that semantic question.

### `setdefault()`

```python
counts = Counter()

value = counts.setdefault("a", 0)

assert value == 0
assert counts["a"] == 0
```

This is dictionary behavior. It is not a replacement for Counter's counting-specific operations.

---

## 116. defaultdict API Edge Cases

### Empty constructor

```python
d = defaultdict()

try:
    d["missing"]
except KeyError:
    print("KeyError")
```

With no factory, missing `[]` lookup behaves as documented by `__missing__()` and raises `KeyError`. citeturn309077view1

### Constructor with initial mapping

```python
d = defaultdict(list, {"a": [1]})

print(d["a"])
```

Existing data is passed through the underlying dictionary construction semantics.

### `default_factory` inspection

```python
d = defaultdict(list)

assert d.default_factory is list
```

### `default_factory = None`

```python
d = defaultdict(list)

d.default_factory = None

try:
    d["missing"]
except KeyError:
    print("KeyError")
```

Changing the factory changes future missing-key behavior.

### `defaultdict.update()`

```python
d = defaultdict(list, {"a": [1]})

d.update({"a": [2], "b": [3]})

assert d["a"] == [2]
assert d["b"] == [3]
```

This is normal dictionary update behavior.

It does not concatenate list values automatically.

That distinction is especially important when comparing:

```text
Counter.update()
    → add counts

defaultdict.update()
    → ordinary mapping update
```

### Merge operators

Modern Python supports:

```python
left = defaultdict(list, {"a": [1]})
right = {"b": [2]}

merged = left | right

print(dict(merged))
```

These merge operators were added for dictionaries and defaultdict in Python 3.9. citeturn309077view1

Do not rely on merge behavior without checking the supported Python version in an older production environment.

---

## 117. deque API Edge Cases

### `clear()`

```python
d = deque([1, 2, 3])

d.clear()

assert len(d) == 0
```

### Empty operations

```python
d = deque()

try:
    d.pop()
except IndexError:
    print("empty")
```

Likewise:

```python
try:
    d.popleft()
except IndexError:
    print("empty")
```

### `maxlen` is read-only

```python
d = deque(maxlen=3)

print(d.maxlen)
```

Do not expect:

```python
d.maxlen = 10
```

to resize an existing deque.

If a different maximum is required, construct another deque with the desired `maxlen`.

### `reversed()`

```python
d = deque([1, 2, 3])

print(list(reversed(d)))
```

Result:

```text
[3, 2, 1]
```

### Membership

```python
d = deque(["a", "b", "c"])

assert "b" in d
assert "z" not in d
```

### Shallow copy

```python
original = deque([["a"]])
clone = original.copy()

clone[0].append("b")

assert original[0] == ["a", "b"]
```

This demonstrates that `copy()` does not recursively copy nested objects.

### Concatenation and repetition

Current Python deques support additional sequence operations such as `+`, `*`, and `*=`. These operations are secondary to the end-oriented workloads covered in this chapter; use them only when their sequence semantics improve clarity. citeturn309077view0

---

# Appendix B — Practical code review checklist

## 118. Code Review Questions

When reviewing a pull request containing one of these structures, ask:

### Counter review

```text
[ ] Is the data actually a frequency/count domain?
[ ] Are keys hashable?
[ ] Is missing-key zero semantics relied upon intentionally?
[ ] Is update() intended to accumulate?
[ ] Is subtract() intended to preserve signed values?
[ ] Could zero/negative counts persist unexpectedly?
[ ] Is most_common() appropriate for the required ranking?
[ ] Is cardinality bounded?
```

### defaultdict review

```text
[ ] Is automatic initialization intentional?
[ ] Is d[key] allowed to mutate on read?
[ ] Would dict/get() be clearer for inspection?
[ ] Is the factory independent per key?
[ ] Is a lambda hiding important domain behavior?
[ ] Is nesting still readable?
[ ] Are grouped values bounded?
```

### deque review

```text
[ ] Is the workload end-oriented?
[ ] Is FIFO intended?
[ ] Is LIFO intended?
[ ] Is maxlen necessary?
[ ] Is automatic eviction acceptable?
[ ] Is indexing being overused?
[ ] Are search operations unexpectedly on a hot path?
[ ] Is thread synchronization actually required?
```

### Architecture review

```text
[ ] Is state process-local?
[ ] Is persistence required?
[ ] Is state shared across workers?
[ ] Is external coordination required?
[ ] Is the in-memory structure merely a cache/buffer/aggregate?
```

---

# Appendix C — Compact production example test matrix

## 119. Integrated Example Test Matrix

| Concern | Example test |
|---|---|
| valid ingestion | one success event increments two Counters |
| repeated model | model count accumulates |
| repeated status | status count accumulates |
| grouping | model list contains expected events |
| recent history | only N latest events retained |
| empty recent state | summary returns defined empty result |
| unknown model | lookup returns empty result |
| negative latency | ingestion raises `ValueError` |
| invalid recent limit | constructor raises `ValueError` |
| timezone contract | invalid naive timestamp is rejected |
| failure summary | non-success statuses appear in top failures |
| memory policy | recent buffer has fixed `maxlen` |

This table is a useful bridge between unit tests and production requirements.

---

# Appendix D — Why this topic matters before concurrency and garbage collection

## 120. Roadmap Connection

This chapter intentionally prepares concepts used later in the roadmap.

### Before concurrency

You now understand:

```text
deque
    → local queue-like container

queue.Queue
    → synchronization-oriented queue
```

The later concurrency topic can build on that distinction rather than introducing "queue" as a single overloaded concept.

### Before object model and garbage collection

You now understand that:

```python
deque
defaultdict(list)
Counter
```

hold Python object references.

A long-lived collection can therefore keep referenced objects alive.

That makes:

```text
bounded retention
container lifetime
reference ownership
memory growth
```

important subjects for later object-model and garbage-collection study.

### Before caching and partial application

Counters and bounded buffers are common supporting structures for:

```text
local metrics
recent results
small caches
event windows
```

Later modules can build more specialized abstractions around them.

---

# Appendix E — Final engineering summary

## 121. Final Engineering Summary

The three structures solve different problems.

### Counter

Use when:

```text
the primary value is a count
```

Key API ideas:

```python
Counter(values)
counter[key]
counter.elements()
counter.most_common()
counter.total()
counter.update(...)
counter.subtract(...)
counter1 + counter2
counter1 - counter2
counter1 & counter2
counter1 | counter2
```

### defaultdict

Use when:

```text
a missing key should be initialized automatically
```

Key API ideas:

```python
defaultdict(list)
defaultdict(set)
defaultdict(int)
defaultdict(float)

d[key]
d.get(key)
d.setdefault(key, default)
d.default_factory
d.__missing__(key)
```

### deque

Use when:

```text
operations at one or both ends are central
```

Key API ideas:

```python
deque()
deque(values)
deque(values, maxlen=N)

d.append(x)
d.appendleft(x)
d.pop()
d.popleft()
d.extend(values)
d.extendleft(values)
d.rotate(n)
d.remove(x)
d.count(x)
d.index(x)
d.insert(i, x)
d.reverse()
d.copy()
d.clear()
d.maxlen
```

---

## 122. Final Mental Model — Memorize the Questions, Not Just the Classes

When you see a new problem, ask:

```text
Q1. Am I counting?
    YES → Counter

Q2. Am I grouping or accumulating values per key?
    YES → defaultdict

Q3. Do I need efficient operations from the left/right ends?
    YES → deque

Q4. Do I need general key → value mapping?
    YES → dict

Q5. Do I need general sequence + random access?
    YES → list

Q6. Do multiple threads need a coordinated blocking queue?
    YES → queue.Queue

Q7. Must state survive restart or be shared across workers?
    YES → external durable/shared system
```

Then ask:

```text
What is the memory bound?
What is the mutation behavior?
What is the expected complexity?
What happens on errors?
What happens on process crash?
What happens with multiple workers?
What must be tested?
```

This is the complete mental model for selecting these structures in production-oriented Python.


## 123. Final File-Scope Verification Note

This chapter is intentionally self-contained.

The requested deliverable consists of exactly one Markdown artifact:

```text
08-counter-defaultdict-and-deque.md
```

No Python source files, exercise files, answer-key files, configuration files, or additional Markdown artifacts are part of this deliverable.

The educational content above covers the requested standard-library structures, their relevant public APIs, conceptual internals, performance and memory characteristics, production limitations, testing and debugging, Applied AI Engineering use cases, architecture scenarios, exercises, interview preparation, and final decision framework.

