# Search, Count, Filter, Map, and Aggregate

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Recognize five recurring problem shapes — **search, count, filter, map,
  aggregate** — hiding inside almost any data-processing task, before you
  write a single line of code.
- Solve each of the five with a plain `for` loop first, so you understand
  the mechanics, and only then reach for Python's more expressive tools
  (`in`, `any()`, `all()`, `next()`, comprehensions, `map()`, `filter()`,
  `sum()`, `min()`, `max()`, `Counter`, `reduce()`).
- Explain *why* each compact tool works, not just *that* it works, by
  tracing it back to the loop it replaces.
- Compose these patterns together (filter → map → aggregate, search →
  transform, and so on), which is what real data-processing code actually
  looks like.
- Judge when a compact expression improves readability and when it hurts
  it — production code is read far more often than it is written.
- Reason about the time and space cost of each pattern in simple Big-O
  terms, and know why early termination matters for search.
- Spot the classic beginner mistakes for each pattern before they cause a
  bug, and know how to debug them systematically when they do.

## 2. Why These Patterns Matter

Consider one small collection of numbers:

```python
numbers = [10, 20, 30, 40, 50]
```

Now consider the different questions someone might ask about it:

- *Is 30 present?*
- *How many values are greater than 25?*
- *Which values are greater than 25?*
- *Add 5 to every value.*
- *What is the total?*
- *What is the maximum?*
- *What is the average?*

Every one of these questions looks at the *same* data, but each one asks
something structurally different. If you tried to answer all seven with
one all-purpose piece of code, it would be a tangled mess of `if`
statements. Instead, experienced programmers recognize that each question
belongs to one of five reusable **shapes**:

| Question | Shape |
|---|---|
| Is 30 present? | **SEARCH** — find something |
| How many values are greater than 25? | **COUNT** — determine how many |
| Which values are greater than 25? | **FILTER** — keep some items |
| Add 5 to every value. | **MAP** — transform every item |
| What is the total / maximum / average? | **AGGREGATE** — combine many items into one result |

These five shapes are not Python tricks. They are **problem-solving
patterns** — ways of thinking about a task before you write any code at
all. A senior engineer looking at a vague request like "find our most
valuable customers" mentally breaks it down as: *filter* customers by
some spending threshold, *map* each one to their name, and maybe
*aggregate* to get a total. The Python syntax is just the last, easiest
step. The hard part — and the part this chapter trains — is recognizing
which shape (or combination of shapes) a problem actually is.

This matters because the same five shapes reappear everywhere you will
work as an engineer: validating a batch of records, summarizing log
files, cleaning a dataset before feeding it to a model, checking API
responses, building a report from a database query. Learn to see these
shapes once, and you will recognize them for the rest of your career.

## 3. The Foundation: Iteration

Every one of the five patterns is built on top of one more basic idea:
**iteration** — visiting each item in a collection, one at a time, and
doing something at each step. You already met `for` loops in Module 03;
this section reviews exactly what happens on the inside so search, count,
filter, map, and aggregate all read as small variations on the same
skeleton.

### 3.1 The vocabulary

| Term | Meaning |
|---|---|
| **Iterable** | Something you can loop over — a list, tuple, set, string, or dictionary. |
| **Item** | One element produced by the iterable during looping. |
| **Current item** | The specific item the loop is looking at during one pass. |
| **Condition** | A `True`/`False` test applied to the current item. |
| **Accumulator** | A variable that carries a running result forward from one iteration to the next (a running total, a running count, a running "have I found it yet"). |
| **Result collection** | A new list (or other container) being built up one item at a time. |
| **Early return / `break`** | Stopping the loop before it reaches the end, because the answer is already known. |
| **`continue`** | Skipping the rest of the current pass and moving straight to the next item, without stopping the loop. |

### 3.2 A single loop, traced step by step

```python
numbers = [10, 20, 30, 40]

for number in numbers:
    print(number)
```

Trace table:

| iteration | current value (`number`) | action |
|---|---|---|
| 1 | 10 | print 10 |
| 2 | 20 | print 20 |
| 3 | 30 | print 30 |
| 4 | 40 | print 40 |

After the fourth iteration there are no items left, so the loop ends on
its own — this is the default behavior: **visit every item**.

### 3.3 Visiting every item vs. stopping early vs. skipping

These are three different behaviors, and beginners often blur them
together:

```python
# Visit every item — no break, no continue.
for number in numbers:
    print(number)

# Stop early — break leaves the loop immediately.
for number in numbers:
    if number == 30:
        print("found it")
        break          # loop ends here; 40 is never visited

# Skip an item — continue moves to the next iteration.
for number in numbers:
    if number == 30:
        continue       # nothing happens for 30, but the loop keeps going
    print(number)
```

- **Visiting every item** is the default; you use it when you must
  examine everything (mapping, most aggregation).
- **Stopping early** (`break`) is used when you only need to know *that*
  something happened, and further looking is wasted work (search).
- **Skipping** (`continue`) is used when certain items should be ignored
  but the loop must otherwise continue (filtering, done manually).

### 3.4 Collecting results vs. accumulating a single result

Two very different things can happen inside a loop body:

```python
# Collecting: build a new list, one item can become zero, one, or more items.
result = []
for number in numbers:
    if number > 20:
        result.append(number)
# result = [30, 40]

# Accumulating: combine everything down to a single value.
total = 0
for number in numbers:
    total += number
# total = 100
```

`result` grows a container; `total` is a single number that gets updated
in place. Filtering and mapping *collect*; counting and aggregating
*accumulate*. Search does a bit of both: it accumulates a single boolean
(or the found item) and then stops.

Every pattern in this chapter is one of these two loop shapes, with a
different condition or a different action inside. Once that clicks, the
rest of this chapter is really about **which loop shape fits which
question**, and then which Python tool expresses that loop shape most
clearly.

## 4. Search

### 4.1 What it is and why it exists

**Search** answers: *"Does this exist, and if so, where/what is it?"*
Every time you check whether a username is taken, whether a product ID
is valid, or whether any transaction in a batch failed, you are
searching.

### 4.2 Simple intuition

You are looking through a box of items for one that matches. You look at
one item at a time. The moment you find a match, you stop — there is no
reason to keep looking once you have your answer.

### 4.3 Manual loop: does a value exist?

```python
numbers = [10, 20, 30, 40]

found = False
for number in numbers:
    if number == 30:
        found = True
        break

print(found)   # True
```

Line by line:

- `found = False` — the accumulator starts pessimistic: assume it is not
  there until proven otherwise.
- `for number in numbers:` — visit each item in order.
- `if number == 30:` — the search condition.
- `found = True` — record success.
- `break` — stop immediately; continuing would only waste time re-checking
  items after the answer is already known.

Trace table:

| iteration | current value | condition (`number == 30`) | `found` |
|---|---|---|---|
| 1 | 10 | False | False |
| 2 | 20 | False | False |
| 3 | 30 | **True** | **True**, then `break` |

Notice iteration 4 (`40`) never happens — that is early termination doing
its job.

### 4.4 Why `break` matters

Without `break`, the loop would keep running and possibly overwrite
`found` back to `False` if a later, non-matching item were checked
carelessly, or — at best — waste time scanning items that can no longer
change the answer:

```python
# Without break: correct here, but wasteful — every remaining
# item is still visited even after the answer is already known.
found = False
for number in numbers:
    if number == 30:
        found = True
print(found)
```

For a 4-item list the waste is invisible. For a 50-million-row log file,
scanning all of it after already finding what you need is a real
performance bug.

### 4.5 What happens when the item is absent

```python
numbers = [10, 20, 30, 40]
found = False
for number in numbers:
    if number == 999:
        found = True
        break
print(found)   # False — the loop reaches the end naturally, no break needed
```

If nothing matches, the loop simply runs out of items and `found` stays
`False`. This is correct and expected — always confirm your code handles
the "nothing found" case, because it is easy to test only the success
path.

### 4.6 Empty collections and duplicates

```python
empty = []
found = False
for number in empty:
    if number == 30:
        found = True
        break
print(found)   # False — the loop body never runs at all
```

An empty collection is not an error case for search — the loop simply
never executes, and the initial `found = False` is already the correct
answer.

Duplicates do not change a plain existence search — `30 in [30, 30, 30]`
is still just `True`. Duplicates *do* matter once you start asking "how
many" or "which one," which is why counting and searching are separate
patterns even though they look similar at first.

### 4.7 Python's membership operators: `in` and `not in`

The loop above is such a common need that Python provides it directly:

```python
numbers = [10, 20, 30, 40]

print(30 in numbers)       # True
print(999 in numbers)      # False
print(999 not in numbers)  # True
```

`30 in numbers` performs *exactly* the loop-and-break logic from §4.3
internally. Use `in`/`not in` whenever the question is a plain
"does this exact value exist" — writing out the loop yourself at that
point only adds noise.

#### Membership across collection types

```python
# list — checks each element, O(n)
30 in [10, 20, 30]

# tuple — same idea, O(n)
30 in (10, 20, 30)

# set — checks via hashing, average O(1) (see §17)
30 in {10, 20, 30}

# string — checks for a substring, not just a single character
"cat" in "concatenate"     # True

# dictionary — checks KEYS by default, not values!
prices = {"apple": 1, "banana": 2}
"apple" in prices           # True  — key lookup
1 in prices                 # False — 1 is a VALUE, not a key
1 in prices.values()        # True  — explicit value lookup
```

Be precise here: **`in` on a dictionary checks its keys.** This is one
of the most common sources of confusion for beginners moving from lists
to dictionaries. If you need to check values, say so explicitly with
`.values()`; if you need to check key-value pairs together, use
`.items()`:

```python
("apple", 1) in prices.items()   # True
```

### 4.8 Searching with a condition, not just an exact value

Real searches are rarely "does this literal value exist." More often
they are "find the first item that satisfies some rule":

```python
numbers = [10, 20, 30, 40, 60]

# First number greater than 50
result = None
for number in numbers:
    if number > 50:
        result = number
        break
print(result)   # 60
```

The same shape works for records, not just numbers:

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
print(first_active)   # {"name": "Grace", "active": True}
```

```python
transactions = [{"amount": 10}, {"amount": 250}, {"amount": 400}]

first_large = None
for t in transactions:
    if t["amount"] > 100:
        first_large = t
        break
print(first_large)   # {"amount": 250}
```

The general shape is always:

```python
for item in collection:
    if condition(item):
        return item   # or: result = item; break
```

Inside a function, `return item` does exactly what `break` does inside a
bare loop — it stops the search the instant an answer is found, but it
also hands the value straight back to the caller.

### 4.9 `any()` — "is at least one item true?"

Checking "does at least one item satisfy this condition" is common
enough that Python provides `any()`:

```python
numbers = [10, 20, 30, 40]

has_large_number = any(number > 25 for number in numbers)
print(has_large_number)   # True
```

`number > 25 for number in numbers` is a **generator expression** — it
looks like a list comprehension (covered fully in §6.3) but without the
square brackets, and it produces values one at a time instead of
building a whole list. `any(...)` pulls values from it one at a time and
stops — early termination again — the moment it sees a `True`:

```python
# What any() does internally, conceptually:
def any_manual(iterable_of_booleans):
    for value in iterable_of_booleans:
        if value:
            return True
    return False
```

If every value is `False` (or the collection is empty), `any()` returns
`False`. **`any([])` is `False`** — there is no item to be true, so the
honest answer is no.

```python
any(user["active"] for user in users)          # True if any user is active
any(t["amount"] > 1000 for t in transactions)  # True if any transaction is large
```

### 4.10 `all()` — "is every item true?"

`all()` is the natural complement: it asks whether *every* item
satisfies the condition, and stops early the moment it finds one that
does not:

```python
numbers = [10, 20, 30, 40]

all_positive = all(number > 0 for number in numbers)
print(all_positive)   # True

all_large = all(number > 25 for number in numbers)
print(all_large)      # False — 10 and 20 fail the test
```

```python
def all_manual(iterable_of_booleans):
    for value in iterable_of_booleans:
        if not value:
            return False
    return True
```

**`all([])` is `True`** — this often surprises beginners. Logically,
"every item in an empty collection satisfies the condition" is
vacuously true because there are no counterexamples. This matters in
practice: `all(user["active"] for user in [])` is `True`, so if your code
relies on `all()` to gate an action, make sure an empty input is really
meant to pass.

| | `any()` | `all()` |
|---|---|---|
| Meaning | at least one True | every one True |
| Empty collection | `False` | `True` |
| Stops early on | first `True` | first `False` |

### 4.11 `next()` — grabbing the first match directly

`any()` and `all()` only answer yes/no questions. When you want the
*actual first matching item* (not just whether one exists), `next()` on
a generator expression is the idiomatic tool:

```python
numbers = [10, 20, 30, 40]

first_big = next((x for x in numbers if x > 25), None)
print(first_big)   # 30
```

Read this piece by piece:

- `(x for x in numbers if x > 25)` is a generator expression — it does
  not build a list; it produces matching values one at a time, on
  demand.
- `next(generator, default)` pulls exactly one value out of the
  generator. Because the generator only computes values as they are
  asked for, `next()` only forces it to check `10`, then `20`, then
  `30` — and stops as soon as `30` satisfies the condition. Numbers after
  it (`40`) are never even examined. This is early termination again,
  just expressed through laziness instead of an explicit `break`.
- The second argument, `None`, is the **default** returned if nothing
  matches — without it, `next()` raises `StopIteration` on no match,
  which is rarely what you want in application code.

```python
# Without a default — dangerous unless you are certain something matches:
next(x for x in numbers if x > 1000)   # raises StopIteration!

# With a default — safe:
next((x for x in numbers if x > 1000), None)   # None
```

This is the cleanest, most Pythonic way to express "find the first item
matching a condition," and it directly replaces the manual loop-with-
break from §4.8:

```python
first_active = next((u for u in users if u["active"]), None)
first_large_transaction = next((t for t in transactions if t["amount"] > 100), None)
```

### 4.12 Comparing the three search tools

| Tool | Answers | Example |
|---|---|---|
| Manual loop + `break` | Full control; used when the logic around the match is more than one line | shown in §4.3, §4.8 |
| `in` / `not in` | "Does this *exact value* exist?" | `30 in numbers` |
| `any()` | "Does *any item* satisfy a *condition*?" (yes/no only) | `any(n > 25 for n in numbers)` |
| `next(..., default)` | "What is the *first item* that satisfies a *condition*?" | `next((n for n in numbers if n > 25), None)` |

Use the simplest tool that answers the actual question. Reaching for a
manual loop when `in` would do adds noise; reaching for `next()` when you
only needed a yes/no from `any()` makes the reader work harder than
necessary.

## 5. Count

### 5.1 What it is and why it exists

**Count** answers: *"How many items satisfy some condition?"* It is
closely related to search, but instead of stopping at the first match,
it must look at *every* item to get an accurate total — there is no
early termination for counting in general.

### 5.2 Manual loop with an accumulator

```python
numbers = [10, 20, 30, 40]

count = 0
for number in numbers:
    if number > 20:
        count += 1

print(count)   # 2
```

Trace table:

| iteration | current value | `number > 20` | `count` after this iteration |
|---|---|---|---|
| 1 | 10 | False | 0 |
| 2 | 20 | False | 0 |
| 3 | 30 | True | 1 |
| 4 | 40 | True | 2 |

`count` is an **accumulator** initialized to `0` before the loop starts —
forgetting this initialization (or putting it inside the loop, where it
would reset every iteration) is one of the most common bugs beginners
write; see §14.

### 5.3 `len()` — counting *everything*, unconditionally

```python
numbers = [10, 20, 30, 40]
print(len(numbers))   # 4
```

`len()` answers a different, simpler question: *"how many items are in
this collection, period"* — with no condition at all. Do not confuse
"how many items total" with "how many items satisfy a condition":

```python
len(numbers)                          # 4  — total size
sum(1 for n in numbers if n > 20)     # 2  — conditional count (see below)
```

### 5.4 `list.count(value)` — counting occurrences of one specific value

```python
numbers = [10, 20, 10, 30, 10]
print(numbers.count(10))   # 3
```

`.count(value)` answers *"how many times does this exact value appear"* —
narrower than a general condition, but very direct when that is exactly
what you need.

### 5.5 Conditional counting with `sum(...)`

To count how many items satisfy an arbitrary condition without writing
out the loop, use `sum()` over a generator expression of booleans:

```python
numbers = [10, 20, 30, 40]
count = sum(number > 20 for number in numbers)
print(count)   # 2
```

**Why this works:** in Python, `bool` is a subtype of `int` — `True`
behaves as `1` and `False` behaves as `0` in any numeric context:

```python
print(True + True + False)   # 2
print(int(True), int(False)) # 1 0
```

So `sum(number > 20 for number in numbers)` is really summing a sequence
of `1`s and `0`s — one for every item that passes the test, zero for
every item that fails it — which is exactly a count. This is a genuinely
useful idiom, but use it only while it stays readable:

```python
# Fine — clear at a glance:
active_count = sum(user["active"] for user in users)

# Getting cluttered — a named helper or explicit loop reads better:
weird_count = sum(
    1 for u in users
    if u["active"] and u["signup_year"] >= 2022 and u["country"] in allowed
)
```

### 5.6 `collections.Counter` — counting frequencies

Everything so far counts *how many satisfy one condition*. Often you
instead need *how many of each distinct value* appear — a frequency
table. Writing that by hand looks like this:

```python
words = ["cat", "dog", "cat", "bird"]

counts = {}
for word in words:
    if word in counts:
        counts[word] += 1
    else:
        counts[word] = 1

print(counts)   # {"cat": 2, "dog": 1, "bird": 1}
```

`collections.Counter` does exactly this, in one call:

```python
from collections import Counter

words = ["cat", "dog", "cat", "bird"]
counts = Counter(words)
print(counts)                    # Counter({'cat': 2, 'dog': 1, 'bird': 1})
print(counts["cat"])             # 2
print(counts["fish"])            # 0 — missing keys default to 0, unlike a plain dict
```

A `Counter` behaves like a dictionary (you can index it, iterate its
keys, check membership) but is specialized for tallying:

```python
counts.most_common()        # [('cat', 2), ('dog', 1), ('bird', 1)] — sorted, most frequent first
counts.most_common(1)       # [('cat', 2)] — just the top N
counts.update(["cat", "owl"])  # add more items to the running tally
```

Typical uses: counting word frequency in text, counting how many
transactions fall into each status ("completed", "failed", "pending"),
counting how many log lines are at each severity level.

```python
statuses = ["completed", "failed", "completed", "completed", "failed"]
Counter(statuses).most_common()
# [('completed', 3), ('failed', 2)]
```

### 5.7 Choosing the right counting tool

| Question | Tool |
|---|---|
| How many items total? | `len(collection)` |
| How many times does one specific value appear? | `collection.count(value)` |
| How many items satisfy a condition? | manual loop with accumulator, or `sum(condition for item in collection)` |
| How many of *each* distinct value appear? | `collections.Counter(collection)` |

## 6. Filter

### 6.1 What it is and why it exists

**Filter** answers: *"Which items should I keep?"* It takes an input
collection, applies a condition to each item, and produces a new
collection containing only the items that passed.

```
Input collection → condition → keep matching items → output collection
```

### 6.2 Manual loop

```python
numbers = [10, 20, 30, 40, 50]

result = []
for number in numbers:
    if number > 20:
        result.append(number)

print(result)   # [30, 40, 50]
```

- `result = []` — an empty **result collection**, built up one match at a
  time.
- `if number > 20:` — the filtering condition.
- `result.append(number)` — the *original, unmodified* item is kept —
  filtering never changes values, only selects which ones survive (that
  is mapping's job, §7).
- The original `numbers` list is untouched; filtering produces a new
  list rather than mutating the input, which is what you want almost
  every time.
- Output order matches input order — filtering does not reorder items,
  it only removes some.

### 6.3 List comprehensions

Python offers a compact syntax for exactly this loop shape:

```python
result = [number for number in numbers if number > 20]
print(result)   # [30, 40, 50]
```

Breaking the syntax into its four parts, matched against the loop above:

```
[  number     for number in numbers    if number > 20  ]
   ^expression   ^for item in collection   ^condition
```

| Comprehension part | Loop equivalent |
|---|---|
| `[...]` | `result = []` and eventually returning `result` |
| `number` (the expression) | `result.append(number)` |
| `for number in numbers` | `for number in numbers:` |
| `if number > 20` | `if number > 20:` |

The comprehension is not a different feature — it is the *exact same
loop*, written in one line because this loop shape is used so often that
Python gives it dedicated syntax.

### 6.4 Multiple conditions

```python
numbers = [5, 15, 25, 35, 45, 55]

result = [number for number in numbers if number > 10 and number < 50]
print(result)   # [15, 25, 35, 45]
```

`and`, `or`, and `not` combine conditions exactly as they do in a normal
`if` statement:

```python
[n for n in numbers if n > 10 and n < 50]        # both must be true
[n for n in numbers if n < 10 or n > 50]         # either can be true
[n for n in numbers if not (n > 10 and n < 50)]  # negate the whole thing
```

### 6.5 Filtering strings, dictionaries, and records

```python
words = ["cat", "elephant", "dog", "hippopotamus"]
long_words = [word for word in words if len(word) > 4]
print(long_words)   # ['elephant', 'hippopotamus']
```

```python
users = [
    {"name": "Ada", "active": False},
    {"name": "Grace", "active": True},
    {"name": "Alan", "active": True},
]

active_users = [
    user for user in users
    if user["active"]
]
print(active_users)
# [{'name': 'Grace', 'active': True}, {'name': 'Alan', 'active': True}]
```

Nested conditions on records read most clearly when you keep each
comparison simple and combine with `and`/`or` rather than nesting many
`if`s:

```python
eligible_users = [
    user for user in users
    if user["active"] and user.get("age", 0) >= 18
]
```

`user.get("age", 0)` avoids a `KeyError` if some records are missing the
`"age"` key — an important habit once real, messy data is involved (more
on missing keys in §16).

### 6.6 The built-in `filter()`

Python also has a `filter()` built-in:

```python
numbers = [10, 20, 30, 40, 50]
result = filter(lambda x: x > 20, numbers)
print(result)          # <filter object at 0x...>  — NOT a list!
print(list(result))    # [30, 40, 50]
```

Two things to notice:

- **`filter()` returns an iterator**, not a list. It computes matching
  items lazily, one at a time, as they are requested — it does not build
  the whole result up front. If you need an actual list (to index it,
  loop over it twice, or print it directly), wrap it in `list(...)`.
- `lambda x: x > 20` is a tiny, unnamed function. `lambda parameters:
  expression` is shorthand for a function that takes `parameters` and
  returns `expression`. Here it is exactly equivalent to:

  ```python
  def is_greater_than_20(x):
      return x > 20
  ```

  A `lambda` is only ever appropriate for a condition this short and
  self-explanatory; anything more complex deserves a real, named
  function so the reader does not have to decode it.

**In practice, prefer the list comprehension over `filter()` for
beginners and in most application code** — `[x for x in numbers if x >
20]` reads left-to-right like English, while `filter(lambda x: x > 20,
numbers)` requires understanding both `lambda` and the fact that the
result is not yet a list. `filter()` is still worth recognizing because
you will encounter it in other people's code, and it can be marginally
more memory-efficient for very large data when combined with other
lazy tools (see §9).

## 7. Map / Transform

### 7.1 Filter vs. Map — the key distinction

This distinction trips up many beginners, so state it plainly:

- **FILTER** changes **which items remain**. The surviving items are
  unchanged; some items disappear.
- **MAP** changes **what each item becomes**. Every input item produces
  exactly one output item — nothing is dropped, but every value can
  change.

```python
numbers = [1, 2, 3, 4]

# FILTER — keeps some, changes nothing
evens = [n for n in numbers if n % 2 == 0]    # [2, 4]  (length changed, values didn't)

# MAP — keeps everything, changes each value
doubled = [n * 2 for n in numbers]            # [2, 4, 6, 8]  (length unchanged, values did)
```

### 7.2 Manual loop

```python
numbers = [1, 2, 3, 4]

result = []
for number in numbers:
    result.append(number * 2)

print(result)   # [2, 4, 6, 8]
```

Every single input item produces exactly one output item appended to
`result` — the output length **always matches** the input length for a
true map (this is a useful sanity check when debugging).

### 7.3 List comprehension

```python
result = [number * 2 for number in numbers]
print(result)   # [2, 4, 6, 8]
```

Same four-part breakdown as filtering, minus the `if`:

```
[  number * 2   for number in numbers  ]
   ^expression     ^for item in collection
```

The expression before `for` is what gets computed and collected for
every item — this is exactly `result.append(number * 2)` from the loop.

### 7.4 The built-in `map()`

```python
numbers = [1, 2, 3, 4]
result = map(lambda x: x * 2, numbers)
print(result)          # <map object at 0x...> — also an iterator
print(list(result))    # [2, 4, 6, 8]
```

Just like `filter()`, `map()` returns an iterator, so wrap it in
`list(...)` when you need an actual list. One input item always produces
one output item — `map()` cannot drop or duplicate items, only transform
them.

`map()` also works with a real, named function, which often reads more
clearly than a `lambda`, especially when the transformation has a
meaningful name:

```python
def square(number):
    return number * number

numbers = [1, 2, 3, 4]
print(list(map(square, numbers)))   # [1, 4, 9, 16]
```

Compare with the comprehension:

```python
print([square(number) for number in numbers])   # [1, 4, 9, 16]
```

Both are equally valid; many Python style guides prefer the
comprehension because it does not require the reader to know that
`map()` returns an iterator. **Prefer whichever reads more clearly at
the call site** — for a single, already-named function, `map()` can be
just as clear as the comprehension; for anything needing a `lambda`, the
comprehension is almost always easier to read.

### 7.5 Mapping to other types and structured data

```python
numbers = [1, 2, 3]
as_strings = [str(number) for number in numbers]
print(as_strings)   # ['1', '2', '3']
```

```python
users = [{"name": "Ada"}, {"name": "Grace"}, {"name": "Alan"}]
names = [user["name"] for user in users]
print(names)   # ['Ada', 'Grace', 'Alan']
```

Extracting one field from every record in a list of dictionaries is one
of the single most common real-world uses of mapping — you will do this
constantly when working with API responses, database rows, and CSV
data.

### 7.6 When a plain loop beats both

```python
# Comprehension — fine when the transformation is simple:
doubled = [n * 2 for n in numbers]

# Explicit loop — often easier to debug when the transformation
# is more involved or needs intermediate steps:
result = []
for n in numbers:
    adjusted = n * 2
    if adjusted > 100:
        adjusted = 100          # clamp
    result.append(adjusted)
```

Once a transformation needs more than one expression, or has its own
internal branching, cramming it into a comprehension hurts readability.
A plain loop — or a named helper function called from a comprehension —
is the better production choice. Readability is revisited in depth in
§18.

## 8. Aggregate

### 8.1 What it is and why it exists

**Aggregate** answers: *"Take many values and combine them into one
result."* Totals, minimums, maximums, averages, and products are all
aggregations.

### 8.2 Manual loop

```python
numbers = [10, 20, 30, 40]

total = 0
for number in numbers:
    total += number

print(total)   # 100
```

`total` is an accumulator, exactly like `count` in §5.2, except it adds
the *value* itself instead of adding `1` for a match.

### 8.3 Built-in aggregation functions

```python
numbers = [10, 20, 30, 40]

print(sum(numbers))   # 100
print(min(numbers))   # 10
print(max(numbers))   # 40
print(len(numbers))   # 4
```

Each of these is a small, well-tested replacement for a manual
accumulator loop — there is rarely a reason to hand-write a total or
maximum loop in real code once you know these exist. It is still worth
having written the loop yourself at least once (§8.2), because it is
exactly what `sum()` does internally, and understanding that makes the
edge cases in §8.4 make sense rather than feeling arbitrary.

### 8.4 Edge cases: empty collections

```python
sum([])    # 0    — safe: 0 is the "identity" for addition (adding it changes nothing)
```

```python
min([])    # ValueError: min() arg is an empty sequence
max([])    # ValueError: max() arg is an empty sequence
```

Why the difference? `sum()` has a sensible, safe answer for "no items":
zero. But `min()` and `max()` have no honest single answer for "the
smallest/largest of nothing" — there is no number that means "no
maximum," so Python refuses to guess and raises an error instead. Always
guard `min()`/`max()` when the input might be empty:

```python
values = []
largest = max(values) if values else None
```

`min()` and `max()` also accept a `default` keyword for the same
purpose:

```python
largest = max(values, default=None)
```

### 8.5 Average

```python
numbers = [10, 20, 30, 40]
average = sum(numbers) / len(numbers)
print(average)   # 25.0
```

The empty-list problem strikes again — `len([])` is `0`, and dividing by
zero raises `ZeroDivisionError`. Guard it the same way:

```python
average = sum(numbers) / len(numbers) if numbers else 0
```

`statistics.mean()` does the same calculation and raises a clearer,
purpose-built error on empty input:

```python
import statistics

print(statistics.mean(numbers))   # 25
statistics.mean([])               # StatisticsError: mean requires at least one data point
```

Reach for `statistics.mean()` in code whose intent is explicitly
statistical — it self-documents, and the standard library also offers
`statistics.median()` and `statistics.stdev()` alongside it for related
needs (not covered further here, as they belong to their own topics).

### 8.6 Product with `math.prod()`

```python
import math

numbers = [2, 3, 4]
print(math.prod(numbers))   # 24
```

Equivalent manual loop:

```python
product = 1                # identity for multiplication — NOT 0!
for number in numbers:
    product *= number
```

Note the accumulator starts at `1`, not `0` — multiplying by `0` would
zero out the whole result. This is a subtle but important detail: every
accumulator has a correct **identity value** to start from (`0` for sum
and count, `1` for product, `False` for "any," `True` for "all").

### 8.7 Aggregating with a condition, and aggregating transformed values

Aggregation composes naturally with filtering and mapping, using a
generator expression instead of a plain variable:

```python
numbers = [5, 15, 25, 35]

# Aggregate only the values that pass a condition (filter → aggregate):
total_of_large = sum(number for number in numbers if number > 10)
print(total_of_large)   # 75

# Aggregate transformed values (map → aggregate):
total_doubled = sum(number * 2 for number in numbers)
print(total_doubled)    # 160
```

`sum(number for number in numbers if number > 10)` uses a **generator
expression** — the same shape as a list comprehension, but without `[
]`. The difference matters: `sum([n for n in numbers if n > 10])` first
builds an entire intermediate list, *then* sums it; `sum(n for n in
numbers if n > 10)` — no brackets — never builds that list at all. Values
are produced and immediately added to the running total, one at a time.
For a handful of numbers this makes no practical difference; for a
file with ten million rows, skipping the intermediate list can save a
meaningful amount of memory. Prefer the generator-expression form (no
brackets) whenever the list itself is not needed for anything else.

## 9. Reduce and General Accumulation

Everything in §8 is really a specialized case of one general idea:
**combine a sequence of values into one, by repeatedly combining a
running result with the next value.** `functools.reduce()` exposes that
general idea directly.

```python
from functools import reduce

numbers = [10, 20, 30, 40]
total = reduce(lambda running_total, number: running_total + number, numbers)
print(total)   # 100
```

Trace exactly what `reduce()` does, step by step:

| step | running total | next number | new running total |
|---|---|---|---|
| 1 | 10 (starts as the first item) | 20 | 10 + 20 = 30 |
| 2 | 30 | 30 | 30 + 30 = 60 |
| 3 | 60 | 40 | 60 + 40 = 100 |

`reduce(function, iterable)` calls `function(running_result, next_item)`
over and over, carrying the result forward, until the iterable is
exhausted. You can also supply an explicit starting value as a third
argument — important when the iterable might be empty, or the identity
value is not simply "the first item":

```python
total = reduce(lambda acc, n: acc + n, numbers, 0)   # starts from 0, not from numbers[0]
```

**`reduce()` is powerful but should not be your default.** It exists to
handle accumulation logic that *has no dedicated function* — the moment
a purpose-built tool exists (`sum()`, `min()`, `max()`, `math.prod()`,
`"".join()`), that tool is clearer:

```python
# Technically works, but needlessly obscure:
total = reduce(lambda acc, n: acc + n, numbers)

# Much clearer — say what you mean:
total = sum(numbers)
```

A reasonable use of `reduce()` is combining values in a way that has no
built-in shortcut — for example, merging a list of dictionaries into
one:

```python
from functools import reduce

pieces = [{"a": 1}, {"b": 2}, {"c": 3}]
merged = reduce(lambda acc, piece: {**acc, **piece}, pieces, {})
print(merged)   # {'a': 1, 'b': 2, 'c': 3}
```

Here there is no single built-in that merges an arbitrary list of
dictionaries, so `reduce()` earns its place. Even so, many engineers
would still write this as an explicit loop, because the loop is easier
for the next reader to step through:

```python
merged = {}
for piece in pieces:
    merged.update(piece)
```

**Rule of thumb:** reach for `sum`/`min`/`max`/a comprehension first;
reach for `reduce()` only when none of them fit, and even then, compare
it against a plain loop before committing to it.

## 10. Search vs Count vs Filter vs Map vs Aggregate

| Pattern | Question it answers | Shape of output | Typical Python tools |
|---|---|---|---|
| **Search** | Does X exist / what is the first X? | A single item, or `True`/`False` | `in`, `not in`, `any()`, `all()`, `next()`, loop + `break` |
| **Count** | How many satisfy a condition? | A single integer | `len()`, `.count()`, `sum(condition for ...)`, `Counter` |
| **Filter** | Which items should I keep? | A smaller (or equal-sized) collection | list comprehension with `if`, `filter()` |
| **Map** | What does each item become? | A same-sized collection, transformed | list comprehension, `map()` |
| **Aggregate** | What single result summarizes all items? | A single value | `sum()`, `min()`, `max()`, `math.prod()`, `statistics.mean()`, `reduce()` |

### One dataset, five questions

```python
transactions = [
    {"amount": 100, "status": "completed"},
    {"amount": 250, "status": "failed"},
    {"amount": 400, "status": "completed"},
    {"amount": 50,  "status": "completed"},
]
```

**Search** — find the first completed transaction:

```python
first_completed = next(
    (t for t in transactions if t["status"] == "completed"), None
)
# {'amount': 100, 'status': 'completed'}
```

**Count** — how many transactions completed:

```python
completed_count = sum(t["status"] == "completed" for t in transactions)
# 3
```

**Filter** — keep only completed transactions:

```python
completed = [t for t in transactions if t["status"] == "completed"]
# [{'amount': 100, ...}, {'amount': 400, ...}, {'amount': 50, ...}]
```

**Map** — extract just the amounts:

```python
amounts = [t["amount"] for t in transactions]
# [100, 250, 400, 50]
```

**Aggregate** — total amount of completed transactions:

```python
total_completed = sum(
    t["amount"] for t in transactions if t["status"] == "completed"
)
# 550
```

The same list of dictionaries answered five structurally different
questions. Recognizing *which* question is being asked — before writing
any code — is the actual skill this chapter is training.

## 11. Composing the Patterns

Real code rarely uses one pattern in isolation; it chains them.

### 11.1 Filter → Map, written explicitly, then compactly

```python
# Step by step:
completed = [
    t for t in transactions
    if t["status"] == "completed"
]
amounts = [
    t["amount"]
    for t in completed
]
```

```python
# Equivalent, combined into one comprehension:
amounts = [
    t["amount"]
    for t in transactions
    if t["status"] == "completed"
]
```

Both give `[100, 400, 50]`. The combined form still has the same four
parts as any comprehension — expression, `for`, `if` — just written
across multiple lines for readability. Prefer breaking a comprehension
across lines like this once it stops fitting comfortably on one.

### 11.2 Filter → Map → Aggregate, as one expression

```python
total = sum(
    t["amount"]
    for t in transactions
    if t["status"] == "completed"
)
# 550
```

Read right to left in terms of *evaluation*, left to right in terms of
*what it says*: "sum the amount of each transaction in transactions,
but only for those whose status is completed." This is a generator
expression (no `[ ]`) being consumed directly by `sum()` — nothing but
the running total is ever held in memory at once.

### 11.3 Other common compositions

```python
# Search → Transform: find a record, then pull one field from it.
first_completed = next((t for t in transactions if t["status"] == "completed"), None)
first_amount = first_completed["amount"] if first_completed else None

# Filter → Count
failed_count = sum(1 for t in transactions if t["status"] == "failed")

# Map → Aggregate
total_amount = sum(t["amount"] for t in transactions)   # map (extract) + aggregate (sum) in one pass
```

### 11.4 Why composition matters

Nearly all practical data work is a pipeline of these patterns:

- **Data engineering / ETL** — filter out invalid rows, map raw fields
  into a clean schema, aggregate for a summary table.
- **Backend systems** — filter a user's records by permission, map them
  into a response format, count them for pagination.
- **Analytics** — filter to a date range, map to the metric of interest,
  aggregate to a single KPI.
- **AI/ML preprocessing** — filter out malformed examples, map raw text
  into tokens or features, aggregate to compute dataset statistics
  (mean, count, min/max) before training.

Once you can name a task as "filter → map → aggregate" (or any other
chain), the code almost writes itself — the hard design work is already
done.

## 12. Applying the Patterns to Python Collections

The five patterns are not list-specific — they apply to every Python
collection.

```python
# --- Search ---
"apple" in ["apple", "banana"]          # list
"apple" in ("apple", "banana")          # tuple
"apple" in {"apple", "banana"}          # set
"apple" in {"apple": 1, "banana": 2}    # dict — checks KEYS

# --- Filter ---
prices = {"apple": 1, "banana": 3, "cherry": 2}
cheap = {name: price for name, price in prices.items() if price < 3}
# {'apple': 1, 'cherry': 2}   — a dict comprehension

# --- Map ---
doubled_prices = {name: price * 2 for name, price in prices.items()}
# {'apple': 2, 'banana': 6, 'cherry': 4}

# --- Count ---
sum(1 for price in prices.values() if price < 3)   # 2

# --- Aggregate ---
sum(prices.values())     # 6
max(prices.values())     # 3
```

A dictionary comprehension (`{key: value for ... }`) is the same idea as
a list comprehension, applied to key-value pairs instead of single
items — filtering and mapping both work over `.items()`, `.keys()`, or
`.values()` depending on what you need.

### Sets and fast membership

```python
allowed_ids = {101, 205, 309}   # a set literal

if user_id in allowed_ids:      # membership check
    ...
```

Using a **set** for membership checks (rather than a list) is a common,
important habit: checking `in` on a list has to potentially scan every
item, while a set can check membership without scanning the whole
collection (see §17 for why). If a collection exists only to answer
"is X in here," and you do not need duplicates or order, a set is
usually the right container. Collection choice in general is its own
full topic later in this module — the point here is only that all five
patterns still apply once you have made that choice.

## 13. Strings and Text Processing

Strings are iterables of characters, and support the same five patterns.

```python
message = "2024-01-01 ERROR: connection refused"
words = message.split()
```

**Search** — does the message contain "error" (as a substring)?

```python
"ERROR" in message          # True
```

**Count** — how many times does a substring occur?

```python
log = "ERROR: retry. ERROR: retry. INFO: ok."
log.count("ERROR")          # 2
```

**Filter** — keep words longer than 4 characters:

```python
long_words = [word for word in words if len(word) > 4]
# ['2024-01-01', 'ERROR:', 'connection', 'refused']
```

**Map** — convert every word to lowercase:

```python
lowered = [word.lower() for word in words]
```

**Aggregate** — total number of characters across all words:

```python
total_chars = sum(len(word) for word in words)
```

These same five moves are exactly what you use when scanning application
logs for errors, cleaning user input, or preprocessing text before
feeding it into any downstream data or AI pipeline: search for markers,
count occurrences, filter relevant lines, map to a normalized form,
aggregate into a summary.

## 14. Real-World Engineering Examples

For each example: **INPUT → PATTERN → LOGIC → OUTPUT.**

### 14.1 Banking transactions

```python
transactions = [
    {"id": "T1", "amount": 100, "status": "completed"},
    {"id": "T2", "amount": 250, "status": "failed"},
    {"id": "T3", "amount": 400, "status": "completed"},
]
```

- *Find all failed transactions.* → **FILTER**
  `[t for t in transactions if t["status"] == "failed"]`
- *Count failed transactions.* → **COUNT**
  `sum(t["status"] == "failed" for t in transactions)`
- *Calculate total failed amount.* → **FILTER → AGGREGATE**
  `sum(t["amount"] for t in transactions if t["status"] == "failed")`
- *Extract transaction IDs.* → **MAP**
  `[t["id"] for t in transactions]`
- *Check whether transaction "T2" exists.* → **SEARCH**
  `any(t["id"] == "T2" for t in transactions)`

### 14.2 Log processing

```python
log_lines = [
    "INFO: server started",
    "ERROR: disk full",
    "INFO: request handled",
    "ERROR: connection refused",
]
```

- *Does the log contain any errors?* → **SEARCH**
  `any("ERROR" in line for line in log_lines)`
- *How many error lines are there?* → **COUNT**
  `sum("ERROR" in line for line in log_lines)`
- *Keep only error lines.* → **FILTER**
  `[line for line in log_lines if "ERROR" in line]`
- *Strip the level prefix from every line.* → **MAP**
  `[line.split(": ", 1)[1] for line in log_lines]`
- *Total characters logged.* → **AGGREGATE**
  `sum(len(line) for line in log_lines)`

### 14.3 Customer records

```python
customers = [
    {"name": "Ada", "spend": 500, "country": "UK"},
    {"name": "Grace", "spend": 1200, "country": "US"},
    {"name": "Alan", "spend": 300, "country": "UK"},
]
```

- *Is there a customer from "US"?* → **SEARCH**
  `any(c["country"] == "US" for c in customers)`
- *How many customers spent over 400?* → **COUNT**
  `sum(c["spend"] > 400 for c in customers)`
- *High-value customers (spend > 400).* → **FILTER**
  `[c for c in customers if c["spend"] > 400]`
- *Just the customer names.* → **MAP**
  `[c["name"] for c in customers]`
- *Total revenue.* → **AGGREGATE**
  `sum(c["spend"] for c in customers)`

### 14.4 Data quality checks

```python
records = [
    {"id": 1, "email": "a@example.com"},
    {"id": 2, "email": None},
    {"id": 3, "email": "c@example.com"},
]
```

- *Is there any record with a missing email?* → **SEARCH**
  `any(r["email"] is None for r in records)`
- *How many records are missing an email?* → **COUNT**
  `sum(r["email"] is None for r in records)`
- *Keep only valid (non-null-email) records.* → **FILTER**
  `[r for r in records if r["email"] is not None]`
- *Normalize emails to lowercase (skipping missing ones).* → **MAP**
  `[(r["email"] or "").lower() for r in records]`
- *Percentage of records that are valid.* → **FILTER → COUNT → AGGREGATE**
  `sum(r["email"] is not None for r in records) / len(records)`

### 14.5 AI/ML preprocessing

```python
examples = [
    {"text": "great product", "label": "positive"},
    {"text": "", "label": "positive"},
    {"text": "terrible service", "label": "negative"},
]
```

- *Is there any example with empty text?* → **SEARCH**
  `any(ex["text"] == "" for ex in examples)`
- *How many usable (non-empty) examples exist?* → **COUNT**
  `sum(ex["text"] != "" for ex in examples)`
- *Drop malformed examples before training.* → **FILTER**
  `[ex for ex in examples if ex["text"] != ""]`
- *Extract just the text field for tokenization.* → **MAP**
  `[ex["text"] for ex in examples if ex["text"] != ""]`
- *Average text length across the clean dataset.* → **FILTER → MAP → AGGREGATE**
  `sum(len(ex["text"]) for ex in examples if ex["text"] != "") / sum(ex["text"] != "" for ex in examples)`

## 15. Common Mistakes

**1. Confusing search with filter.**
```python
# WRONG — this "finds" every match but the intent was existence-checking
result = [t for t in transactions if t["status"] == "failed"]
if result:          # works, but says "did filtering give me a nonempty list?"
    ...
```
→ Why wrong: it is technically correct but obscures intent and does
unnecessary work (scans everything, builds a list, just to ask yes/no).
```python
# CORRECT
if any(t["status"] == "failed" for t in transactions):
    ...
```
Lesson: if the real question is yes/no or "just the first one," use a
search tool (`any`, `next`, `in`), not a filter.

**2. Confusing count with `len()`.**
```python
# WRONG — len() of the wrong thing
failed_count = len(transactions)     # this is the TOTAL, not failed count
```
→ Why wrong: `len()` counts everything, ignoring the condition entirely.
```python
# CORRECT
failed_count = sum(t["status"] == "failed" for t in transactions)
```
Lesson: `len()` answers "how many total," never "how many match."

**3. Modifying a list while iterating over it.**
```python
# WRONG
numbers = [1, 2, 3, 4]
for number in numbers:
    if number % 2 == 0:
        numbers.remove(number)   # mutates the list mid-iteration!
print(numbers)   # [1, 3] — looks right by luck here, but is unreliable
```
→ Why wrong: removing an item shifts every later item one position to
the left, so the loop's internal position counter skips the item that
slid into the just-vacated slot. This can silently drop items depending
on the exact data.
```python
# CORRECT — build a new list instead of mutating the old one
numbers = [n for n in numbers if n % 2 != 0]
```
Lesson: never add to or remove from a collection you are actively
looping over — filter into a new collection instead.

**4. Forgetting to initialize an accumulator.**
```python
# WRONG
for number in numbers:
    total += number   # NameError: total is not defined
```
→ Why wrong: the accumulator must exist with a starting value *before*
the loop begins.
```python
# CORRECT
total = 0
for number in numbers:
    total += number
```

**5. Returning too early / forgetting `break`.**
```python
# WRONG — inside a function, this returns after checking only the FIRST item
def any_negative(numbers):
    for number in numbers:
        return number < 0   # returns on iteration 1, no matter what!
```
→ Why wrong: `return` inside the loop body, without a guarding `if`, ends
the function on the very first pass.
```python
# CORRECT
def any_negative(numbers):
    for number in numbers:
        if number < 0:
            return True
    return False
```
Lesson: `return`/`break` must be conditional — inside an `if` — not
unconditionally the first statement in the loop body.

**6. Using the wrong condition (off-by-one logic, not off-by-one index).**
```python
# WRONG — intends "at least 20", writes "more than 20"
adults = [p for p in people if p["age"] > 20]   # excludes exactly 20!
```
→ Why wrong: `>` and `>=` are easy to swap by accident; always re-read
the requirement's exact wording ("at least," "more than," "up to").
```python
# CORRECT
adults = [p for p in people if p["age"] >= 20]
```

**7. Accidentally creating nested lists.**
```python
# WRONG
result = [[n for n in numbers if n > 20]]   # extra brackets → list-of-one-list!
print(result)   # [[30, 40, 50]] — not [30, 40, 50]
```
→ Why wrong: an extra pair of `[ ]` around the comprehension wraps the
whole result in another list.
```python
# CORRECT
result = [n for n in numbers if n > 20]
```

**8. Confusing `map()` with `filter()`.**
```python
# WRONG — using map() where filtering was intended
result = list(map(lambda x: x > 20, numbers))
print(result)   # [False, False, True, True, True] — booleans, not the numbers!
```
→ Why wrong: `map()` transforms every item (here, into a boolean); it
never removes items. The person wanted to keep only large numbers, not
convert every number into `True`/`False`.
```python
# CORRECT
result = list(filter(lambda x: x > 20, numbers))
# or, more idiomatically:
result = [x for x in numbers if x > 20]
```

**9. Using `map()`/`filter()` when a comprehension is clearer.**
```python
# Harder to read at a glance:
result = list(map(lambda x: x * 2, filter(lambda x: x > 20, numbers)))
```
```python
# Clearer:
result = [x * 2 for x in numbers if x > 20]
```
Lesson: chaining `map()` and `filter()` together is a strong signal that
a single comprehension would be more readable.

**10. Creating unnecessary intermediate lists.**
```python
# Less efficient — builds a full list just to sum it
total = sum([n for n in numbers if n > 20])
```
```python
# Better — a generator expression never builds the intermediate list
total = sum(n for n in numbers if n > 20)
```
Lesson: drop the square brackets when the comprehension's result is
immediately consumed by another function like `sum()`, `any()`, `all()`,
`max()`, or `min()`.

**11. Using `reduce()` when `sum()` (or another built-in) is clearer.**
```python
# Needlessly obscure:
from functools import reduce
total = reduce(lambda acc, n: acc + n, numbers, 0)
```
```python
# Say what you mean:
total = sum(numbers)
```

**12. Forgetting the empty-input case.**
```python
average = sum(numbers) / len(numbers)   # ZeroDivisionError if numbers == []
```
```python
average = sum(numbers) / len(numbers) if numbers else 0
```

**13. Using `min()`/`max()` on a possibly-empty collection.**
```python
largest = max(values)   # ValueError if values == []
```
```python
largest = max(values, default=None)
```

**14. Accidentally counting strings incorrectly.**
```python
# WRONG — len() on a string counts CHARACTERS, not words
sentence = "the quick brown fox"
word_count = len(sentence)          # 19, not 4!
```
```python
# CORRECT
word_count = len(sentence.split())  # 4
```

**15. Misunderstanding dictionary membership.**
```python
prices = {"apple": 1, "banana": 2}
1 in prices          # False — checks KEYS, and 1 isn't a key here
```
```python
1 in prices.values()          # True — check values explicitly
"apple" in prices              # True — key check, as intended
```

**16. Forgetting that `map()` and `filter()` return iterators.**
```python
result = filter(lambda x: x > 20, numbers)
print(len(result))   # TypeError: object of type 'filter' has no len()
```
```python
result = list(filter(lambda x: x > 20, numbers))
print(len(result))   # works
```
Lesson: an iterator from `map()`/`filter()` has no length and can only be
consumed once — convert to `list()` if you need to inspect, re-use, or
measure it.

**17. Using overly clever one-liners.**
```python
# WRONG — technically works, painful to read and debug
result = [y for y in (x * 2 for x in numbers if x > 10) if y < 100]
```
```python
# CORRECT — split into named, sequential steps
above_ten = [x for x in numbers if x > 10]
doubled = [x * 2 for x in above_ten]
result = [y for y in doubled if y < 100]
```
Lesson: nesting comprehensions inside comprehensions to save lines almost
always costs more in readability than it saves in length. See §18.

## 16. Edge Cases

Systematic edge-case thinking means checking each pattern against the
same checklist of inputs:

| Input situation | Search | Count | Filter | Map | Aggregate |
|---|---|---|---|---|---|
| Empty collection | returns "not found" / `False` / `None` — never errors | `0` | `[]` | `[]` | `sum`→`0`; `min`/`max`→error unless `default=` given |
| One item | works normally, just one iteration | `0` or `1` | `[]` or `[item]` | `[transformed_item]` | that one value is the result |
| Duplicate values | first match found, others irrelevant | each duplicate counted separately | duplicates kept if they match | each duplicate transformed independently | duplicates all contribute to the total |
| All items match | search finds the first immediately | count equals `len()` | output equals input | (mapping is unaffected by matching) | (aggregation is unaffected by matching) |
| No items match | not found | `0` | `[]` | (mapping never filters) | `sum` of nothing is `0`; average and min/max need guards |
| `None` values present | `is None` search needed, not `==` | must decide if `None` counts | must decide whether to keep or drop `None` | must decide how to transform `None` (often skip it) | `sum`/`min`/`max` raise `TypeError` if `None` reaches them unfiltered |
| Zero as a value | `0 in [...]` is valid — do not confuse with "not found" | `0` is a legitimate matched value | `0` might wrongly look "falsy" and get excluded by mistake | `0` transforms like any number | `0` contributes to `sum`, may become `min` |
| Negative numbers | works normally — do not assume all values are positive | works normally | comparisons (`> 0`) may unintentionally exclude everything negative | works normally | `min`/`max`/`sum` all handle negatives correctly |
| Missing dictionary keys | `r.get("key")` needed instead of `r["key"]` to avoid `KeyError` | same | same | same | same |
| Malformed records (wrong type, missing fields) | guard with `.get()` or a type check before comparing | same | same | same | same |

Two edge cases deserve special emphasis:

**Zero vs. falsy.** In Python, `0`, `""`, `[]`, and `None` are all
"falsy," but they are not the same thing. A filter like `if r["count"]`
silently excludes legitimate zero counts:

```python
# WRONG — excludes records where count is legitimately 0
records = [{"count": 0}, {"count": 5}]
nonzero_looking = [r for r in records if r["count"]]   # drops count=0!

# CORRECT — be explicit about what "missing" means
valid = [r for r in records if r["count"] is not None]
```

**Missing keys.** `r["key"]` raises `KeyError` the instant one record
lacks that key; `.get("key")` (optionally with a default) returns `None`
or a fallback instead of crashing:

```python
records = [{"amount": 100}, {"status": "ok"}]   # second record has no "amount"
[r["amount"] for r in records]              # KeyError!
[r.get("amount", 0) for r in records]       # [100, 0] — safe
```

## 17. Performance and Big-O

Every pattern in this chapter, in its general form, must at least glance
at each item once, so all five share the same baseline cost:

| Pattern | Typical time complexity | Notes |
|---|---|---|
| Search | O(n) worst case | but often stops early — best case O(1), average depends on where the match is |
| Count | O(n) | must inspect every item — no early termination for an exact count |
| Filter | O(n) | visits every item once |
| Map | O(n) | visits every item once |
| Aggregate | O(n) | visits every item once |

Here, **n** is the number of items in the collection, and O(n) means the
work grows proportionally with the size of the input — twice the data,
roughly twice the time.

**Early termination matters for search.** `in`, `any()`, and `next()`
all stop the moment they find a match, so while the *worst case* (item
is last, or absent) is O(n), a match near the start of a large
collection can be found almost instantly. Count and full aggregation
have no such shortcut — you must know about every item to know a total
or a count, so they are always full O(n) scans.

**Space complexity** differs more between the patterns:

- Filtering into a new list: O(n) additional space in the worst case
  (if every item matches).
- Mapping into a new list: O(n) additional space (every item produces
  one output item).
- A **generator expression** instead of a list: O(1) additional space
  for the generator itself — it produces one value at a time and never
  holds the whole result in memory.

```python
sum([n * 2 for n in numbers if n > 10])   # builds a full intermediate list — O(n) space
sum(n * 2 for n in numbers if n > 10)     # no intermediate list — O(1) extra space
```

This is why §8.7 and §15 (mistake #10) both recommend dropping the
brackets when a comprehension's result feeds straight into `sum()`,
`any()`, `all()`, `min()`, or `max()` — the answer is identical, but the
memory profile is not.

Being a Python **built-in** does not automatically mean O(1). `sum()`,
`min()`, `max()`, and `list.count()` are all still O(n) — they still
have to visit every relevant item; they are just implemented in fast,
compiled C code under the hood rather than interpreted Python, so they
are faster in practice, not faster in Big-O terms.

**Set membership vs. list membership.** Checking `x in some_list`
requires scanning up to every item — O(n). Checking `x in some_set` uses
hashing internally and is, on average, O(1) — roughly constant time
regardless of the set's size. This is why, when a collection exists
mainly to answer repeated "is this here?" questions, a set is usually
the right choice over a list (the deep mechanics of hashing belong to a
later Big-O chapter — the takeaway here is simply: **many membership
checks on large data → prefer a set**).

## 18. Readability vs Cleverness

Production code is optimized, in order, for: **correctness, readability,
maintainability, testability**, and only then, raw performance. A
technique that saves three lines but forces the next reader to puzzle
over it for five minutes is a net loss.

Compare three ways of solving the same problem:

```python
# 1. Long explicit loop — most verbose, easiest to step through with a debugger
result = []
for transaction in transactions:
    if transaction["status"] == "completed" and transaction["amount"] > 100:
        result.append(transaction["amount"])
total = 0
for amount in result:
    total += amount
```

```python
# 2. Compact comprehension — clear, and the most common production style for this shape
total = sum(
    t["amount"]
    for t in transactions
    if t["status"] == "completed" and t["amount"] > 100
)
```

```python
# 3. Nested one-liner — technically shorter, but harder to verify at a glance
total = sum(a for a in (t["amount"] for t in transactions if t["status"] == "completed") if a > 100)
```

Version 2 is usually the sweet spot: it fits on a few lines, its four
parts (expression, `for`, `if`) are still easy to pick out, and it avoids
building an unnecessary intermediate list. Version 3 saves nothing
meaningful over version 2 and costs real readability — nesting one
generator expression inside another to dodge writing two conditions is
exactly the kind of "cleverness" to avoid.

**"Shorter code is not automatically better code."** Use a plain loop
when: the logic has multiple steps, needs to update more than one
variable, or would require nesting comprehensions to force it into one
expression. Use a comprehension or generator expression when: the logic
is a single, clear condition and a single, clear expression. This is a
judgment call, and it is fine — expected, even — to write the loop
first and simplify only if the simpler version is genuinely clearer.

## 19. Debugging

### 19.1 Systematic print-based tracing

When a filter, map, count, or aggregate produces the wrong answer, add a
`print()` inside the loop body to see exactly what the code sees at each
step, rather than guessing:

```python
total = 0
for number in numbers:
    print(f"number={number}, total before={total}")
    if number > 20:
        total += number
    print(f"total after={total}")
```

This immediately reveals the four most common failure points:

- **Wrong condition** — the printed `number` values pass or fail the
  `if` in a way you did not expect; compare against the printed
  condition result directly (`print(number, number > 20)`).
- **Wrong accumulator** — `total before` and `total after` show exactly
  when and by how much the accumulator changes; if it never changes, the
  condition is never true, or the accumulator update is outside the
  `if`/loop entirely.
- **Missing `append`** (for filter/map) — print `result` after every
  iteration; if it never grows, the `append()` call is missing, is
  indented outside the loop, or is inside the wrong branch.
- **Incorrect `return`** — for search-style functions, print immediately
  before every `return` to confirm it is only reached when intended (see
  mistake #5 in §15).

### 19.2 Debugger inspection

Once print-tracing gets tedious, a debugger lets you pause execution
inside the loop and inspect state directly, without editing the code:

- Set a breakpoint on the line inside the loop body.
- At each pause, inspect the **current item**, the **condition's
  result**, the **accumulator**'s current value, and the **result
  list**'s current contents.
- Step forward one iteration at a time and watch exactly when the
  accumulator or result list changes — this pinpoints the exact
  iteration where behavior diverges from expectations.

### 19.3 A checklist for "why is my result wrong"

- Is the accumulator initialized *before* the loop, with the correct
  identity value (`0` for sum/count, `1` for product)?
- Is the condition using the right comparison (`>` vs. `>=`, `==` vs.
  `is`)?
- For search: is `break`/`return` inside the `if`, not unconditionally
  the loop's first statement?
- For filter/map: is `.append()` (or the comprehension's expression)
  actually inside the loop and using the current item?
- Is the result empty when you expected matches? Print `len(collection)`
  first — an empty *input* is a much simpler bug than a wrong condition.
- Are you checking a dictionary's keys when you meant its values (or
  vice versa)?
- Could `None`, `0`, or missing keys be silently breaking a condition?

## 20. Testing

Testing each pattern means deliberately checking the boundary cases from
§16, not just one "normal" example.

**Search**
```python
def test_search():
    assert 30 in [10, 20, 30]           # existing value
    assert 99 not in [10, 20, 30]       # missing value
    assert 10 in [10, 10, 20]           # duplicate value
    assert 10 not in []                 # empty collection
```

**Count**
```python
def test_count():
    assert sum(n > 100 for n in [1, 2, 3]) == 0      # zero matches
    assert sum(n > 1 for n in [1, 2, 3]) == 2        # some matches
    assert sum(n > 0 for n in [1, 2, 3]) == 3        # all match
    assert sum(n > 0 for n in []) == 0               # empty collection
```

**Filter**
```python
def test_filter():
    assert [n for n in [1, 2, 3] if n > 0] == [1, 2, 3]   # everything matches
    assert [n for n in [1, 2, 3] if n > 10] == []          # nothing matches
    assert [n for n in [1, 2, 3] if n > 1] == [2, 3]       # mixed matches
    assert [n for n in [] if n > 0] == []                  # empty collection
```

**Map**
```python
def test_map():
    assert [n * 2 for n in [1, 2, 3]] == [2, 4, 6]   # normal transformation
    assert [n * 2 for n in []] == []                  # empty collection
    assert [str(n) for n in [1, 2]] == ["1", "2"]     # transformation correctness / type change
```

**Aggregate**
```python
def test_aggregate():
    assert sum([1, 2, 3]) == 6            # normal values
    assert sum([5]) == 5                  # one value
    assert sum([]) == 0                   # empty collection
    assert sum([-1, -2, 3]) == 0          # negative values
    assert sum([0, 0, 0]) == 0            # zero values
    assert min([3, -1, 2]) == -1
    assert max([], default=None) is None  # empty collection, guarded
```

These small, deliberate tests catch the exact mistakes listed in §15
before they reach production — notice each test targets one specific
edge case from §16 rather than one generic "happy path" example.

## 21. Progressive Coding Exercises

Work through these roughly in order. Full solutions with reasoning are
in **§26 — Answer Key / Solutions**; try each one yourself first.

### Level 1 — Beginner

**1.1 — Search for a value.**
Problem: Given a list of numbers, determine whether `42` is present.
Input: `numbers = [3, 12, 42, 7]`
Expected output: `True`
Constraints: solve it with `in` first, then with a manual loop.
Hint: what is the simplest possible tool for "does this exact value
exist"?

**1.2 — Count occurrences.**
Problem: Count how many times the value `5` appears.
Input: `numbers = [5, 3, 5, 5, 2]`
Expected output: `3`
Constraints: use `.count()`.

**1.3 — Filter even numbers.**
Problem: Return only the even numbers.
Input: `numbers = [1, 2, 3, 4, 5, 6]`
Expected output: `[2, 4, 6]`
Constraints: use a list comprehension.
Hint: an even number satisfies `n % 2 == 0`.

**1.4 — Double every number.**
Problem: Return a new list with every value doubled.
Input: `numbers = [1, 2, 3]`
Expected output: `[2, 4, 6]`
Constraints: use a list comprehension.

**1.5 — Calculate total.**
Problem: Return the sum of all values.
Input: `numbers = [4, 8, 15, 16]`
Expected output: `43`
Constraints: use `sum()`.

### Level 2 — Intermediate

**2.1 — Count above a threshold.**
Problem: Count how many numbers exceed `50`.
Input: `numbers = [10, 60, 55, 20, 90]`
Expected output: `3`
Constraints: use `sum(condition for ...)`.

**2.2 — Filter active users.**
Problem: Return only the users whose `"active"` field is `True`.
Input: `users = [{"name": "A", "active": True}, {"name": "B", "active": False}]`
Expected output: `[{"name": "A", "active": True}]`
Constraints: list comprehension over dictionaries.

**2.3 — Extract names.**
Problem: Return a list of just the `"name"` values from the users above.
Input: same `users` list as 2.2.
Expected output: `["A", "B"]`
Constraints: use mapping.

**2.4 — Calculate average.**
Problem: Return the average of a list of numbers, safely handling an
empty list by returning `0`.
Input: `numbers = [2, 4, 6, 8]`
Expected output: `5.0`
Constraints: guard the empty-list case.
Hint: what does `sum([]) / len([])` do, and how do you prevent it?

**2.5 — Find first matching record.**
Problem: Find the first user younger than 18.
Input: `people = [{"name": "A", "age": 25}, {"name": "B", "age": 15}]`
Expected output: `{"name": "B", "age": 15}`
Constraints: use `next()` with a generator expression and a default of
`None`.

### Level 3 — Advanced (dictionaries/records)

**3.1 — Transaction filtering.**
Problem: Return all transactions with `"status"` equal to `"completed"`.
Input:
```python
transactions = [
    {"id": "T1", "amount": 100, "status": "completed"},
    {"id": "T2", "amount": 200, "status": "failed"},
]
```
Expected output: `[{"id": "T1", "amount": 100, "status": "completed"}]`

**3.2 — Failed transaction count.**
Problem: Count how many transactions failed, using the same data as 3.1.
Expected output: `1`

**3.3 — Total completed amount.**
Problem: Sum the `"amount"` of only the completed transactions from 3.1.
Expected output: `100`
Constraints: solve this as one filter → aggregate expression.

**3.4 — Extract IDs.**
Problem: Return a list of every transaction's `"id"`, using the data
from 3.1.
Expected output: `["T1", "T2"]`

**3.5 — Find first high-value transaction.**
Problem: Find the first transaction with `"amount"` greater than `150`.
Input: same as 3.1.
Expected output: `{"id": "T2", "amount": 200, "status": "failed"}`
Constraints: use `next()`.

**3.6 — Calculate statistics.**
Problem: Given a list of numeric `"amount"` values across all
transactions in 3.1 (regardless of status), report the count, total,
minimum, and maximum, safely handling an empty list.
Expected output: `(2, 300, 100, 200)` as `(count, total, minimum,
maximum)`.

### Level 4 — Production-oriented

**4.1 — Log severity summary.**
Problem: Given a list of log lines, each beginning with `"INFO:"`,
`"WARNING:"`, or `"ERROR:"`, produce a frequency count of each severity
level.
Input:
```python
logs = ["INFO: ok", "ERROR: fail", "INFO: ok", "WARNING: slow", "ERROR: fail"]
```
Expected output: `Counter({'INFO': 2, 'ERROR': 2, 'WARNING': 1})`
Hint: map each line to its prefix before counting.

**4.2 — Customer spend report.**
Problem: Given a list of customer records with `"spend"` values, return
a summary dictionary with: total customers, number of "high spenders"
(spend > 1000), and average spend (0 if the list is empty).
Input:
```python
customers = [{"spend": 500}, {"spend": 1500}, {"spend": 2000}]
```
Expected output: `{"total": 3, "high_spenders": 2, "average_spend": 1333.33...}`

**4.3 — Data quality audit.**
Problem: Given a list of records that may be missing the `"email"` key
entirely, or have it set to `None`, report how many records are usable
(have a non-`None` email).
Input:
```python
records = [{"email": "a@x.com"}, {"id": 2}, {"email": None}]
```
Expected output: `1`
Hint: use `.get("email")` to avoid a `KeyError` on the record missing the
key entirely.

**4.4 — Preprocessing pipeline.**
Problem: Given a list of text examples, drop any with empty or
whitespace-only text, lowercase the remainder, and report both the
cleaned list and the average length of the cleaned examples.
Input:
```python
examples = ["Great!", "   ", "Terrible.", ""]
```
Expected output: cleaned list `["great!", "terrible."]`, average length
`7.0`

## 22. Mini Project — Transaction Analysis Engine

### Requirements

Given a list of transaction dictionaries, each with `"id"`, `"amount"`,
and `"status"` (one of `"completed"` or `"failed"`), build a small
analysis engine that:

1. Searches for a transaction by a given ID.
2. Counts failed transactions.
3. Filters to just the completed transactions.
4. Maps completed transactions to their amounts.
5. Aggregates the total completed transaction amount.
6. Calculates the average completed transaction amount.
7. Determines whether *any* transaction exceeds a given threshold.
8. Produces a small summary report combining all of the above.

Before writing any code, write out:

- **Problem statement** — in your own words, what does this program do
  and for whom (e.g., a finance team reviewing a batch of transactions)?
- **Inputs** — the transaction list; a target ID for the search; a
  threshold amount for the "any large transaction" check.
- **Outputs** — a found transaction or `None`; an integer count; a list
  of dictionaries; a list of numbers; a total; an average; a boolean; a
  summary report (a dictionary is a reasonable shape).
- **Assumptions** — is `"status"` guaranteed to be exactly `"completed"`
  or `"failed"`? Are amounts guaranteed to be non-negative numbers? Can
  the transaction list be empty?
- **Edge cases** — an empty transaction list; searching for an ID that
  does not exist; every transaction failed (no completed transactions to
  average); a threshold no transaction exceeds.
- **Pseudocode** — sketch each of the eight requirements as one or two
  lines of plain English before translating to Python.

Only after that, implement it. A reasonable shape:

```python
def find_transaction_by_id(transactions, target_id):
    ...

def count_failed(transactions):
    ...

def filter_completed(transactions):
    ...

def completed_amounts(transactions):
    ...

def total_completed_amount(transactions):
    ...

def average_completed_amount(transactions):
    ...

def has_transaction_above(transactions, threshold):
    ...

def build_summary(transactions, threshold):
    ...
```

A full worked solution, including the reasoning for each edge case, is
in §26.

## 23. Interview Questions

**Conceptual**

- What is the difference between search and filter?
- What is the difference between map and filter?
- What is an accumulator, and why must it be initialized before a loop?
- What does `any()` do, and what does it return for an empty collection?
- What does `all()` do, and what does it return for an empty collection?
- What does `next()` do, and why does it usually need a default value?
- Why does `map()` return an iterator instead of a list?
- Why can generator expressions save memory compared to list
  comprehensions?
- What is the time complexity of searching an unsorted list? Does it
  change if the item is near the start versus the end?
- Why is set membership generally faster than list membership?
- When is an explicit loop clearer than a comprehension?
- Why might `reduce()` be less readable than `sum()` for adding numbers?
- What happens when `min()` receives an empty list, and how do you guard
  against it?
- What is the difference between `list.count(value)` and counting items
  that satisfy a general condition?
- What does `in` check when applied to a dictionary?

**Scenario-based**

- "You have a list of 10 million customer records and need to check
  whether a specific ID exists. Would you use a list or a set, and why?"
- "You need the first user in a list who has an expired subscription.
  Walk through two different ways to write this, and say which you'd
  ship."
- "A teammate wrote `sum([x for x in data if x > 0])` inside a hot loop
  processing millions of records. What would you suggest changing, and
  why?"
- "How would you count how many records in a large dataset are missing a
  required field, without loading the whole dataset into a new list?"
- "You're asked to calculate an average, but the input could be an empty
  list. Walk through how you'd handle that safely, and why the naive
  version fails."
- "Someone on your team wrote a five-line nested comprehension to filter,
  transform, and sum data in one expression. How would you decide
  whether to leave it or refactor it?"
- "How would you explain, to someone who has never used Python, why
  `filter()` and `map()` don't immediately give you a usable list?"

## 24. Pattern Recognition Cheat Sheet

Ask these questions, in order, whenever you face a new data problem:

```
"Do I need to FIND something (or check if it exists)?"
    → SEARCH        (in, any(), next(), loop + break)

"Do I need to know HOW MANY?"
    → COUNT         (len(), .count(), sum(condition for ...), Counter)

"Do I need to KEEP SOME ITEMS and discard others?"
    → FILTER        (list comprehension with if, filter())

"Do I need to CHANGE EACH ITEM into something else?"
    → MAP           (list comprehension, map())

"Do I need to COMBINE MANY ITEMS INTO ONE RESULT?"
    → AGGREGATE     (sum(), min(), max(), math.prod(), statistics.mean(), reduce())
```

Common compositions, in the order you will use them most:

```
FILTER → MAP              (keep some records, then pull one field from each)
FILTER → AGGREGATE        (keep some records, then total/average them)
FILTER → COUNT            (how many records match a condition)
MAP → AGGREGATE           (transform every value, then combine them)
SEARCH → TRANSFORM        (find one record, then extract/reshape it)
FILTER → MAP → AGGREGATE  (the most common real-world pipeline shape)
```

## 25. Final Review

- Iteration is the mechanism underneath all five patterns; each pattern
  is just a different combination of a condition, an accumulator or
  result collection, and (sometimes) early termination.
- **Search** finds an item or a yes/no answer and stops as soon as it
  can — `in`, `any()`, `all()`, `next()`.
- **Count** always visits everything and answers "how many" — `len()`,
  `.count()`, `sum(condition for ...)`, `Counter`.
- **Filter** keeps a subset of items unchanged — comprehension with
  `if`, `filter()`.
- **Map** transforms every item, keeping the same count — comprehension,
  `map()`.
- **Aggregate** combines everything into one value — `sum()`, `min()`,
  `max()`, `math.prod()`, `statistics.mean()`, `reduce()`.
- Every compact tool in this chapter is a stand-in for a loop you could
  write yourself — when a compact tool's behavior is surprising, mentally
  expand it back into its loop form.
- Composition (filter → map → aggregate, and similar chains) is how
  these patterns are actually used in real engineering work.
- Always check the edge cases: empty input, missing keys, `None` values,
  zero as a legitimate value, and duplicates.
- Prefer the tool that most directly states your intent; prefer
  readability over cleverness every time the two are in tension.

## 26. Answer Key / Solutions

### Level 1

**1.1** `42 in numbers` directly asks the membership question — no loop
needed. The manual version confirms *why* it works: a loop checking
`number == 42` and breaking on success is exactly what `in` does
internally.
```python
numbers = [3, 12, 42, 7]
print(42 in numbers)   # True
```

**1.2** `.count()` is built exactly for tallying one specific value.
```python
numbers = [5, 3, 5, 5, 2]
print(numbers.count(5))   # 3
```

**1.3** The comprehension keeps items where `n % 2 == 0` is true;
non-matching items are simply never appended.
```python
numbers = [1, 2, 3, 4, 5, 6]
print([n for n in numbers if n % 2 == 0])   # [2, 4, 6]
```

**1.4** Every item is transformed — no `if`, because nothing is
excluded, only changed.
```python
numbers = [1, 2, 3]
print([n * 2 for n in numbers])   # [2, 4, 6]
```

**1.5** `sum()` replaces a manual total-accumulator loop.
```python
numbers = [4, 8, 15, 16]
print(sum(numbers))   # 43
```

### Level 2

**2.1** `sum(condition for ...)` works because `True`/`False` behave as
`1`/`0` — this sums up how many items passed the condition.
```python
numbers = [10, 60, 55, 20, 90]
print(sum(n > 50 for n in numbers))   # 3
```

**2.2** A straightforward filter — `user["active"]` is already a
boolean, so it can be used directly as the condition.
```python
users = [{"name": "A", "active": True}, {"name": "B", "active": False}]
print([u for u in users if u["active"]])
# [{'name': 'A', 'active': True}]
```

**2.3** Mapping extracts one field; note this returns *every* user's
name, active or not — extraction (map) is a separate concern from
selection (filter).
```python
print([u["name"] for u in users])   # ['A', 'B']
```

**2.4** The `if numbers else 0` guard prevents `ZeroDivisionError` when
the list is empty, since `sum([]) / len([])` would divide by zero.
```python
numbers = [2, 4, 6, 8]
average = sum(numbers) / len(numbers) if numbers else 0
print(average)   # 5.0
```

**2.5** `next()` pulls the first match from the generator and stops;
`None` is returned if no one under 18 exists, instead of raising an
error.
```python
people = [{"name": "A", "age": 25}, {"name": "B", "age": 15}]
result = next((p for p in people if p["age"] < 18), None)
print(result)   # {'name': 'B', 'age': 15}
```

### Level 3

**3.1**
```python
transactions = [
    {"id": "T1", "amount": 100, "status": "completed"},
    {"id": "T2", "amount": 200, "status": "failed"},
]
print([t for t in transactions if t["status"] == "completed"])
# [{'id': 'T1', 'amount': 100, 'status': 'completed'}]
```

**3.2** Reusing `sum(condition for ...)` from §5.5.
```python
print(sum(t["status"] == "failed" for t in transactions))   # 1
```

**3.3** Filter and aggregate combined into a single generator
expression — no intermediate list is built.
```python
print(sum(t["amount"] for t in transactions if t["status"] == "completed"))   # 100
```

**3.4** Plain mapping, no filtering — every transaction's ID is
included regardless of status.
```python
print([t["id"] for t in transactions])   # ['T1', 'T2']
```

**3.5**
```python
result = next((t for t in transactions if t["amount"] > 150), None)
print(result)   # {'id': 'T2', 'amount': 200, 'status': 'failed'}
```

**3.6** Guard against the empty case before computing min/max, since
both raise `ValueError` on an empty sequence; count and total have safe
defaults (`0`) even when empty.
```python
amounts = [t["amount"] for t in transactions]
count = len(amounts)
total = sum(amounts)
minimum = min(amounts) if amounts else None
maximum = max(amounts) if amounts else None
print((count, total, minimum, maximum))   # (2, 300, 100, 200)
```

### Level 4

**4.1** Map each line to its severity prefix (the text before the
colon), then let `Counter` tally the results — this is filter/map logic
feeding directly into a counting tool.
```python
from collections import Counter

logs = ["INFO: ok", "ERROR: fail", "INFO: ok", "WARNING: slow", "ERROR: fail"]
levels = [line.split(":")[0] for line in logs]
print(Counter(levels))
# Counter({'INFO': 2, 'ERROR': 2, 'WARNING': 1})
```

**4.2** Three independent computations over the same list: a plain
count, a conditional count, and a guarded average.
```python
customers = [{"spend": 500}, {"spend": 1500}, {"spend": 2000}]

total = len(customers)
high_spenders = sum(c["spend"] > 1000 for c in customers)
spends = [c["spend"] for c in customers]
average_spend = sum(spends) / len(spends) if spends else 0

summary = {"total": total, "high_spenders": high_spenders, "average_spend": average_spend}
print(summary)
# {'total': 3, 'high_spenders': 2, 'average_spend': 1333.3333333333333}
```

**4.3** `.get("email")` returns `None` uniformly whether the key is
missing entirely or explicitly set to `None`, so one condition handles
both malformed shapes safely.
```python
records = [{"email": "a@x.com"}, {"id": 2}, {"email": None}]
usable = sum(r.get("email") is not None for r in records)
print(usable)   # 1
```

**4.4** Filtering first removes blank/whitespace-only entries (using
`.strip()` so pure-whitespace strings are also treated as empty), then
mapping lowercases what remains, then aggregation computes the average
length — a full filter → map → aggregate pipeline.
```python
examples = ["Great!", "   ", "Terrible.", ""]

cleaned = [text.lower() for text in examples if text.strip()]
average_length = sum(len(t) for t in cleaned) / len(cleaned) if cleaned else 0

print(cleaned)          # ['great!', 'terrible.']
print(average_length)   # 7.0
```

### Mini Project — Reference Solution

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

def build_summary(transactions, threshold):
    return {
        "failed_count": count_failed(transactions),
        "completed_count": len(filter_completed(transactions)),
        "total_completed_amount": total_completed_amount(transactions),
        "average_completed_amount": average_completed_amount(transactions),
        "has_large_transaction": has_transaction_above(transactions, threshold),
    }
```

Key reasoning:

- `find_transaction_by_id` is a pure **search** — `next()` with a
  default of `None` handles the "not found" edge case without raising.
- `count_failed` never needs early termination — an accurate count
  requires looking at everything.
- `filter_completed` is reused inside `completed_amounts` rather than
  duplicating the condition — this keeps "what counts as completed" in
  exactly one place.
- `average_completed_amount` explicitly guards the empty case: if there
  are no completed transactions (e.g., every transaction failed), it
  returns `0` instead of raising `ZeroDivisionError`.
- `has_transaction_above` uses `any()`, which stops at the first
  transaction exceeding the threshold rather than scanning the whole
  list unnecessarily.
- `build_summary` composes all of the above — this is the filter → map →
  aggregate pipeline from §11, wired into one production-style report.

```python
transactions = [
    {"id": "T1", "amount": 100, "status": "completed"},
    {"id": "T2", "amount": 250, "status": "failed"},
    {"id": "T3", "amount": 400, "status": "completed"},
]

print(find_transaction_by_id(transactions, "T2"))
# {'id': 'T2', 'amount': 250, 'status': 'failed'}

print(build_summary(transactions, threshold=300))
# {'failed_count': 1, 'completed_count': 2, 'total_completed_amount': 500,
#  'average_completed_amount': 250.0, 'has_large_transaction': True}
```
