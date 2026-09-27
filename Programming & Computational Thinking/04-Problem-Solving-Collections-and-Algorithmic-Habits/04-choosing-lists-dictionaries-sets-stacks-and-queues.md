# Choosing Lists, Dictionaries, Sets, Stacks, and Queues

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Answer, for an unfamiliar problem, **"what operations will I perform
  most often, and which data structure makes those operations cheap?"**
  — rather than reaching for whichever container feels familiar.
- Explain what a list, dictionary, set, stack, and queue each are built
  to do well, and — just as importantly — what each does poorly.
- Use the essential operations of each structure confidently, including
  `list`/`dict`/`set` methods and `collections.deque`.
- Explain, with reasoning grounded in the previous Big-O chapter, why
  `list.pop(0)` is a poor choice for a queue and why `deque` solves that
  problem.
- Recognize that real systems typically combine several data structures
  at once, each handling a different responsibility, rather than forcing
  one structure to do everything.
- Apply a repeatable decision process to choose a data structure for a
  new problem, and justify that choice in terms of required operations,
  ordering, duplicates, and complexity.

## 2. Why Data Structures Matter

Suppose you need to store customer information for a system with these
five requirements:

- Keep customers in the order they were added.
- Find a specific customer by their ID, quickly, over and over.
- Check whether a given email address has already signed up.
- Process customers in the exact order they arrived.
- Undo the most recent action a user took.

You could technically store every customer in a single Python list and
solve all five requirements against it — but you would pay for that
convenience with performance: finding a customer by ID would mean
scanning the whole list every time (previous chapter's §7 established
this as O(n)), and checking for a duplicate email would carry the same
cost. **One container is not equally good at everything** — each of the
five requirements above has a data structure purpose-built for it:

| Requirement | Natural fit |
|---|---|
| Keep items in order | **list** |
| Find something by a key, repeatedly | **dictionary** |
| Check whether something already exists, uniquely | **set** |
| Undo the most recent action (last thing in, first thing reversed) | **stack** |
| Process items in arrival order (first thing in, first thing handled) | **queue** |

This chapter's central claim, repeated throughout: **the right data
structure depends on the operations your workload actually performs,
not on which container looks most familiar or convenient to write.**
Choosing well can be the difference between a system that scales
comfortably and one that grinds to a halt — this is the same lesson the
previous chapter's dictionary-index example (§24 there) demonstrated
concretely, now generalized into a full decision-making skill covering
five core structures.

## 3. Data Structure vs Data Type

These two terms are related but answer different questions:

- A **data type** describes *what kind of value* something is —
  `int`, `str`, `bool`, `float`. It answers "what is this one value?"
- A **data structure** describes *how multiple values are organized and
  accessed* — a list, a dictionary, a set, a stack, a queue. It answers
  "how are these many values arranged, and how do I get to any one of
  them?"

```python
age = 30          # a data type: int — one value
ages = [30, 25, 40]   # a data structure: list — many values, organized in order
```

Python's built-in containers (`list`, `dict`, `set`) are the concrete
tools this chapter uses, but **stack** and **queue** are not separate
Python types — they are *behaviors* (LIFO and FIFO, defined in §17 and
§19) that Python's existing containers (`list`, `collections.deque`) can
implement. Recognizing this distinction matters: when this chapter says
"use a stack," it means "use a `list` in a specific, disciplined way,"
not "Python has a dedicated `Stack` class" (it does not, in the
standard library, for this purpose).

## 4. The Decision-First Framework

Before learning any structure's syntax, learn the questions that decide
which structure fits:

1. Do I need a **sequence** — items in a specific order, accessed by
   position?
2. Do I need **key → value lookup** — finding a value by a name or ID,
   not a position?
3. Do I need **uniqueness** — no duplicates allowed?
4. Do I need **LIFO** behavior — the most recently added item handled
   first?
5. Do I need **FIFO** behavior — the earliest added item handled first?
6. Do I need **fast membership testing** — "does X exist here?" checked
   often?
7. Do I need **indexed access** — "give me the 5th item"?
8. Do I need to **preserve insertion order**?
9. Do I need efficient insertion/deletion **at a particular end**
   (front, back, or both)?
10. Do I need to process items in **arrival order**?

A simple decision tree, to be refined with real complexity reasoning
throughout this chapter:

```
Need key-based lookup?          → dictionary
Need unique values only?        → set
Need an ordered, indexed sequence? → list
Need LIFO (undo-like) behavior? → stack (list used carefully)
Need FIFO (arrival-order) behavior? → queue (deque)
```

Real problems frequently need **more than one** of these at once — §29
and §30 return to this directly, showing that combining structures,
each responsible for one requirement, is the normal, expected shape of
production code, not a special case.

## 5. List Fundamentals

### 5.1 What it is

```python
numbers = [10, 20, 30, 40]
```

A **list** is an **ordered**, **mutable** collection that allows
**duplicates**. "Ordered" here means the list remembers the position
each item was placed in — the first item you add stays first unless you
explicitly move or remove it. "Mutable" means the list itself can be
changed after creation (items added, removed, or replaced) without
creating a new list. Lists can technically hold values of different
types at once (`[1, "two", 3.0]`), though most real code keeps a list's
items uniformly typed for clarity.

### 5.2 Indexing

```python
numbers = [10, 20, 30, 40]
print(numbers[0])    # 10 — first item, zero-based indexing
print(numbers[-1])   # 40 — last item, negative indices count from the end
```

Python uses **zero-based indexing** — the first item is at position
`0`, not `1`. Negative indices count backward from the end, so `-1` is
always the last item regardless of the list's length.

### 5.3 Slicing

```python
print(numbers[1:3])   # [20, 30]
```

`numbers[1:3]` returns a **new list** containing the items from index
`1` up to, but *not including*, index `3` — the previous chapter's
notation `numbers[2:100]` (§19 there) used exactly this convention.
Slicing never modifies the original list; it always produces a
separate, new one.

## 6. List Operations

For each operation: **what it does → example → return value → mutation
→ complexity → common mistake.** (Complexity is stated briefly here and
derived fully, from first principles, in §8, connecting directly to the
previous chapter's §19.)

**`append(x)`** — adds one item to the end.
```python
items = [1, 2]
items.append(3)
print(items)   # [1, 2, 3]
```
Returns `None`; mutates the list in place; O(1) amortized.

**`extend(iterable)`** — adds every item *from* an iterable, individually,
to the end.
```python
items = [1, 2]
items.extend([3, 4])
print(items)   # [1, 2, 3, 4]
```
Returns `None`; mutates in place; O(k), where `k` is the length of the
argument.

**The `append()` vs. `extend()` distinction — a critical, common
mistake:**
```python
items = [1, 2]
items.append([3, 4])
print(items)   # [1, 2, [3, 4]]  — the whole LIST [3, 4] became ONE new element!

items = [1, 2]
items.extend([3, 4])
print(items)   # [1, 2, 3, 4]    — each element of [3, 4] was added individually
```
`append()` always adds its argument as **one single new item**, even if
that argument is itself a list. `extend()` adds **each element of its
argument**, one at a time. Confusing the two silently produces a nested
list where a flat one was intended — a mistake worth checking for
explicitly (also listed in §36).

**`insert(index, x)`** — inserts `x` at a specific position, shifting
later items right.
```python
items = [1, 2, 3]
items.insert(0, 0)
print(items)   # [0, 1, 2, 3]
```
Returns `None`; mutates in place; O(n) — every item from `index` onward
must shift.

**`remove(value)`** — removes the **first** occurrence of `value`.
```python
items = [1, 2, 3, 2]
items.remove(2)
print(items)   # [1, 3, 2]  — only the FIRST 2 was removed
```
Returns `None`; mutates in place; raises `ValueError` if `value` is not
present; O(n) (must search for the value, then shift remaining items).

**`pop(index=-1)`** — removes and **returns** the item at `index`
(default: the last item).
```python
items = [1, 2, 3]
last = items.pop()       # 3, items is now [1, 2]
first = items.pop(0)     # 1, items is now [2]
```
Returns the removed item; mutates in place; raises `IndexError` on an
empty list or invalid index; **O(1) for the default (last item), O(n)
for any earlier position** (§8 explains why).

**`remove()` vs. `pop()` vs. `del`:**
```python
items = [10, 20, 30]

items.remove(20)      # remove BY VALUE — you don't need to know the position
del items[0]           # remove BY POSITION — no return value at all
value = items.pop(0)    # remove BY POSITION — AND get the removed value back
```
Use `remove()` when you know *what* to remove but not *where*; use
`pop()` when you know *where* and want the removed value back; use
`del` when you know *where* and do not need the value.

**`clear()`** — removes every item.
```python
items = [1, 2, 3]
items.clear()
print(items)   # []
```
Returns `None`; mutates in place; O(n) (must release every item).

**`index(value)`** — returns the position of the first matching value.
```python
items = [10, 20, 30]
print(items.index(20))   # 1
```
Raises `ValueError` if absent; O(n) (must scan from the start).

**`count(value)`** — counts occurrences of `value` (directly connecting
to the previous chapter's own §5.4 discussion of counting).
```python
items = [1, 2, 2, 3]
print(items.count(2))   # 2
```
Returns an integer; does not mutate; O(n) (must inspect every item).

**`copy()`** — returns a new, independent (shallow) copy.
```python
original = [1, 2, 3]
duplicate = original.copy()
duplicate.append(4)
print(original)    # [1, 2, 3]  — unaffected
print(duplicate)   # [1, 2, 3, 4]
```
Returns a new list; does not mutate the original; O(n) (every item must
be copied over).

**`sort()`** — sorts the list **in place** (as covered in depth in the
previous chapter's §18); returns `None`.

**`reverse()`** — reverses the list **in place**.
```python
items = [1, 2, 3]
items.reverse()
print(items)   # [3, 2, 1]
```
Returns `None`; mutates in place; O(n).

**`len(items)`, `in`, and `del`** — `len()` returns the item count in
O(1) (it does not scan — the previous chapter's §5.3 established this
distinction for `len()` generally); `value in items` is a membership
check, O(n) worst case (previous chapter's §7.2); `del items[i]` removes
by position without returning the value, O(n) if not the last position.

## 7. List Access Patterns

**Lists are a good fit when:**
- Data genuinely represents an **ordered sequence** — a chronological
  list of events, a sequence of steps, an ordered set of results.
- **Duplicates are meaningful and must be kept** — e.g., a list of all
  amounts spent, where the same amount can legitimately occur more than
  once.
- You need **indexed access** — "give me item 5," "give me the last 3
  items."
- The workflow is **append-heavy** — building a collection incrementally
  by adding to the end.
- You will mostly **iterate over everything**, rather than repeatedly
  looking things up by some identifier.

**Lists are a poor fit when:**
- You need **repeated lookup by some key or ID** — a list forces an
  O(n) scan every time (§8); a dictionary answers this in O(1)
  average-case.
- The requirement is really **"is this unique / does this already
  exist"** — a list's membership check is O(n); a set is built for
  exactly this (§13–§16).
- You need efficient **FIFO** processing — repeatedly removing from the
  *front* of a list is O(n) per removal (§8, and developed fully in
  §20–§21); a `deque` handles this properly.

## 8. List Complexity

Connecting directly to
[Big-O, Time, and Space Complexity](03-big-o-time-and-space-complexity.md),
whose §19 first introduced this table — here it is *derived*, not just
restated:

| Operation | Typical complexity | Why |
|---|---|---|
| `items[i]` (index access) | O(1) | Python lists are stored so any index can be jumped to directly, without scanning. |
| `items.append(x)` | O(1) amortized | Usually places the item in already-reserved space (previous chapter's §33 explains the occasional resize this amortizes over). |
| `items.pop()` (from the end) | O(1) | Removing the last item needs no shifting of anything else. |
| `items.insert(0, x)` | O(n) | Every existing item must shift one position to the right to make room at the front. |
| `items.pop(0)` | O(n) | Removing the first item requires shifting every remaining item one position to the left to close the gap. |
| `x in items` (membership) | O(n) worst case | May require scanning every item before concluding absence. |
| `items.remove(value)` | O(n) | Must first find `value` (a scan), then shift subsequent items left. |
| `items.count(value)` | O(n) | Must inspect every item — no early termination possible for an exact count. |
| `items.index(value)` | O(n) | Must scan from the start until a match is found. |

**Why these costs differ, in one sentence:** operations that touch only
the **end** of the list (`append`, `pop()`) never need to move anything
else, so they are cheap; operations that touch the **beginning or
middle** (`insert(0, ...)`, `pop(0)`, `remove(value)`) require shifting
every item after that position, which costs time proportional to how
many items must move — up to `n` of them. This single insight — "the end
is cheap, the front/middle is expensive" — explains nearly every
row in the table above, and is the direct reason §20–§21 exist: a list
used as a queue (repeatedly removing from the front) is fighting against
exactly this cost structure.

## 9. Dictionary Fundamentals

### 9.1 What it is

```python
user = {
    "id": 101,
    "name": "Alice",
    "email": "alice@example.com",
}
```

A **dictionary** stores data as **key → value** pairs: `"id"` is a
**key**, `101` is its associated **value**; together, `"id": 101` is one
**key-value pair**. Unlike a list, items are not found by position —
they are found by their key, directly. `user.keys()` would give
`["id", "name", "email"]`; `user.values()` would give `[101, "Alice",
"alice@example.com"]`.

### 9.2 Why dictionaries exist

Dictionaries exist to answer one specific, extremely common question
efficiently: **"given this identifier, give me its associated data" —
without scanning anything.** This was demonstrated concretely in the
previous chapter's §24 (building a `customer_id → customer` index) —
this section formalizes the structure that made that possible.

## 10. Dictionary Operations

**`dict[key]`** — direct lookup; raises `KeyError` if the key is absent.
```python
user = {"id": 101, "name": "Alice"}
print(user["name"])       # "Alice"
print(user["missing"])    # KeyError!
```

**`dict.get(key, default=None)`** — safe lookup; returns `default`
(itself defaulting to `None`) instead of raising, if the key is absent.
```python
print(user.get("name"))            # "Alice"
print(user.get("phone"))           # None — no error
print(user.get("phone", "N/A"))    # "N/A" — explicit fallback
```
**`dict[key]` vs. `dict.get(key)` — when to use which:** use `dict[key]`
when the key is *guaranteed* to be present and its absence would be a
genuine bug you want surfaced immediately as a loud `KeyError`; use
`dict.get(key, default)` when a missing key is an *expected, normal*
possibility (as the previous chapter's §16 taught for filtering
possibly-missing fields) and you want a graceful fallback instead of a
crash.

**`dict.keys()`, `dict.values()`, `dict.items()`** — return **views**
onto the dictionary's keys, values, or key-value-pair tuples,
respectively (already used extensively in the previous chapter's §26,
§28).
```python
for key in user.keys():
    print(key)
for value in user.values():
    print(value)
for key, value in user.items():
    print(key, value)
```

**`dict.update(other)`** — merges another dictionary's key-value pairs
in, overwriting any matching existing keys.
```python
user.update({"name": "Alicia", "active": True})
print(user)   # {'id': 101, 'name': 'Alicia', 'email': ..., 'active': True}
```
Returns `None`; mutates in place.

**`dict.setdefault(key, default)`** — already introduced in the previous
chapter's §5: returns the key's existing value if present, otherwise
sets it to `default` first and returns that.

**`dict.pop(key, default=...)`** — removes `key` and **returns** its
value; raises `KeyError` if the key is absent *and* no default was
given.
```python
user = {"id": 101, "name": "Alice"}
name = user.pop("name")
print(name, user)   # "Alice" {'id': 101}
```

**`dict.popitem()`** — removes and returns the **most recently
inserted** key-value pair, relying on the same insertion-order guarantee
discussed in the previous chapter's §13.2.
```python
last_pair = user.popitem()
```

**`dict.clear()`** — removes every key-value pair; returns `None`.

**`dict.copy()`** — returns a new, independent shallow copy, exactly
mirroring `list.copy()` from §6.

**`key in dict`** — membership, checking **keys** (per the previous
chapter's §4.7 — this remains one of the most important, easily
confused facts about dictionaries).

**`del dict[key]`** — removes a key-value pair by key; raises
`KeyError` if absent; returns nothing.

**`len(dict)`** — the number of key-value pairs, O(1).

**Typical complexity** for lookup, insertion, update, deletion, and
membership: all **O(1) average-case**, for the same hashing reasons
established in the previous chapter's §20 — repeated here deliberately,
because dictionary complexity is central to why this structure exists
at all.

## 11. Dictionary Insertion and Update

`dict[key] = value` is genuinely **two different operations depending on
context**, distinguished only by whether the key already exists:

```python
user = {"id": 101}

user["name"] = "Alice"    # INSERT — "name" did not exist before
user["name"] = "Alicia"   # UPDATE — "name" already existed, its value changes
```

Both look identical in code — the difference is entirely in the
dictionary's *prior state*, not the syntax. `update()` performs the same
insert-or-overwrite logic, but for many keys at once:

```python
user.update({"name": "Alicia", "phone": "555-0100"})
# "name" is overwritten (already existed); "phone" is newly inserted
```

**Nested dictionaries**, briefly and practically — a dictionary's values
can themselves be dictionaries:

```python
users = {
    101: {"name": "Alice", "active": True},
    102: {"name": "Bob", "active": False},
}

print(users[101]["name"])   # "Alice"
users[101]["active"] = False   # update a nested field
```

This is an extremely common real-world shape (a table of records,
keyed by ID, where each record is itself a small dictionary of fields)
— it is not treated as a separate topic here, only acknowledged as a
natural, direct extension of everything already covered.

## 12. Dictionary Use Cases

**Use a dictionary when:**
- Data has a **natural key** — a customer ID, a transaction ID, a word,
  a category.
- **Repeated lookup** by that key matters — the more lookups, the more
  a dictionary's O(1) average-case pays off over a list's O(n) scan.
- You need a genuine **key → value mapping**, not just a sequence.
- You need **counting** or **grouping** — both patterns from the
  previous chapter (§6.3 and §4 there) are built directly on
  dictionaries.

Common real examples: `customer_id → customer`, `word → count`,
`category → total`, `transaction_id → transaction` — every one of these
is "I have a natural identifier, and I will ask for records by that
identifier repeatedly," which is precisely a dictionary's purpose.

## 13. Set Fundamentals

### 13.1 What it is

```python
tags = {"python", "ai", "data"}
```

A **set** is an **unordered** collection of **unique** elements — adding
a value that is already present has no effect, and a set makes no
promise about the order its elements will be produced in during
iteration. Sets are **mutable** (you can add and remove elements after
creation), but the elements themselves must be **hashable** (the same
requirement discussed for dictionary keys, and directly connecting to
the previous chapter's §14.1 explanation of why `set(list_of_dicts)`
fails).

### 13.2 Why sets exist

"Does this exist?" is one of the most common questions in programming —
sets exist to answer it as efficiently as possible. Where a list would
require scanning to check membership (§8), a set answers the same
question using the same hashing mechanism as dictionary lookup (§10),
typically in O(1) average-case (§16).

## 14. Set Operations

**`add(x)`** — adds an element; has no effect if already present.
```python
tags = {"python", "ai"}
tags.add("data")
tags.add("python")   # already present — no change, no error
print(tags)           # {'python', 'ai', 'data'}  (order not guaranteed)
```

**`remove(x)`** — removes an element; **raises `KeyError` if absent.**

**`discard(x)`** — removes an element; **does nothing if absent, no
error.**
```python
tags.remove("data")     # works
tags.remove("missing")  # KeyError!

tags.discard("missing")  # silently does nothing — no error
```
**`remove()` vs. `discard()` — when to use which:** use `remove()` when
the element's presence is guaranteed and its absence should be treated
as a bug worth surfacing loudly; use `discard()` when "it might already
be gone, and that is fine" is a normal, expected case.

**`pop()`** — removes and returns an **arbitrary** element (sets have no
defined order, so "arbitrary" is not "the first" or "the last" in any
meaningful sense); raises `KeyError` on an empty set.

**`clear()`** — removes every element.

**`copy()`** — returns a new, independent shallow copy.

**Set algebra — union, intersection, difference, symmetric difference:**

```python
a = {1, 2, 3}
b = {2, 3, 4}

a.union(b)                  # {1, 2, 3, 4}       — everything in either
a.intersection(b)           # {2, 3}             — only what's in both
a.difference(b)             # {1}                — in a, but not in b
a.symmetric_difference(b)   # {1, 4}             — in exactly one, not both
```

The same four operations have operator shorthand:

```python
a | b   # union
a & b   # intersection
a - b   # difference
a ^ b   # symmetric difference
```

**Subset/superset/disjoint relationships:**

```python
{1, 2}.issubset({1, 2, 3})     # True  — every element of {1,2} is in {1,2,3}
{1, 2, 3}.issuperset({1, 2})   # True  — {1,2,3} contains all of {1,2}
{1, 2}.isdisjoint({3, 4})      # True  — no elements in common
```

**`len(some_set)`** and **`x in some_set`** work exactly as expected —
`in` is the operation whose typical O(1) average-case complexity (§16)
is the entire reason sets exist.

## 15. Set Use Cases

**Sets are ideal when:**
- The problem is fundamentally about **uniqueness** — no duplicates
  should exist, or duplicates should be collapsed away (directly
  connecting to the previous chapter's §12–§15 on deduplication).
- **Membership testing** ("does X exist here?") happens often, and needs
  to be fast.
- You need to **compare two collections** — common elements
  (intersection), everything combined (union), or what is unique to one
  side (difference).

Real examples: a set of `visited_ids` while traversing something once;
a set of `allowed_permissions` checked against a user's requested
action; a set of `unique_customer_ids`; a set of `known_document_ids`
to detect re-processing.

**Do NOT use a set when:**
- You need **indexed access** — sets have no positions; `some_set[0]`
  is not valid syntax.
- **Duplicates matter** — a set silently collapses them; if "how many
  times did this occur" matters, a set has already destroyed that
  information (recall the previous chapter's §16 "zero vs. falsy"-style
  caution: silently losing information is a real risk, not a
  hypothetical one).
- A **specific sequence order** is required — sets make no ordering
  guarantee at all.

## 16. Set Complexity

Membership, `add()`, `remove()`, and `discard()` are all **O(1)
average-case**, relying on the same hashing mechanism as dictionaries
(previous chapter's §21; re-derived from the Big-O chapter's §20–§21).
As with dictionaries, this is an average-case expectation under normal
conditions, not an unconditional guarantee for every conceivable input.

**Why `x in some_set` is typically much faster than `x in some_list` for
large collections:** list membership may require scanning up to every
one of the `n` items (O(n) worst case); set membership computes a hash
of `x` and jumps close to directly to where a match would be stored
(O(1) average-case) — for a collection checked for membership
*repeatedly*, this difference compounds directly into the kind of
`O(m × n)` vs. `O(n + m)` gap worked out concretely in the Big-O
chapter's §24. This is precisely why deduplication (previous chapter,
§12–§15) and repeated membership checks are two of the most common,
practically important reasons to reach for a set.

## 17. Stack Fundamentals

### 17.1 The analogy

Picture a stack of plates: you can only add a new plate to the **top**,
and you can only remove the **top** plate — never one from the middle or
bottom without first removing everything above it.

### 17.2 The rule: LIFO

A **stack** follows **LIFO — Last In, First Out**: whatever was added
*most recently* is the first thing removed.

### 17.3 Implementing a stack with a Python list

```python
stack = []

stack.append("A")
stack.append("B")
stack.append("C")

item = stack.pop()
print(item)    # "C" — the LAST item added is the FIRST one removed
print(stack)   # ["A", "B"]
```

Step by step: `append("A")` places `"A"` at the (only, so far) top;
`append("B")` and `append("C")` each place a new item on top of the
previous one, so the stack, top-to-bottom, conceptually reads `C, B, A`.
`stack.pop()` (with no argument, removing from the **end** — exactly
where every `append()` added) removes and returns `"C"`, the most
recently added item, leaving `["A", "B"]` behind — this is LIFO in
action.

## 18. Stack Operations

A stack is conventionally described using four operations — **push**,
**pop**, **peek**, and **is_empty** — even though Python's `list` has no
method literally named `push()`:

| Stack concept | Python list equivalent | Complexity | Note |
|---|---|---|---|
| push (add to top) | `stack.append(x)` | O(1) amortized | Same operation as any list append (§8). |
| pop (remove from top) | `stack.pop()` | O(1) | Removing from the **end** — the cheap end (§8) — is exactly what a stack needs. |
| peek (look at top without removing) | `stack[-1]` | O(1) | Direct index access; does not mutate. |
| is_empty | `len(stack) == 0` (or simply `not stack`) | O(1) | `len()` is O(1) (§6). |

**Handling an empty stack safely:**

```python
def safe_pop(stack):
    if not stack:
        return None
    return stack.pop()

def peek(stack):
    if not stack:
        return None
    return stack[-1]
```

Calling `.pop()` or indexing `stack[-1]` on an **empty** list raises
`IndexError` — always check `is_empty` first (or catch the exception
explicitly) rather than assuming a stack is non-empty, exactly the kind
of edge case discipline emphasized throughout this module.

**Why the list's *end* is used, not the front:** §8 already established
that `append()`/`pop()` at the end are O(1), while operations at the
front are O(n). A stack, by definition, only ever touches "the top" —
choosing the list's end as "the top" means every stack operation stays
O(1); choosing the front would silently make every operation O(n) for
no benefit.

## 19. Stack Use Cases

- **Undo/redo** — the most recently performed action is the first one
  undone; a natural LIFO fit.
- **Function call stack** — briefly touched on in the Big-O chapter's
  §29: each function call is "pushed," and the most recently called
  function is the first to "return" (be "popped").
- **Expression evaluation** and **parentheses matching** — checking
  whether `"(a(b)c)"` has balanced parentheses can be done by pushing
  each `(` and popping on each `)`, confirming everything matches by the
  end.
- **Depth-first search (DFS)** and **backtracking** — both explore "as
  deep as possible down one path before backing up," which is naturally
  expressed with a stack of "things still to explore." (These
  algorithms themselves are not taught in depth here — they belong to
  later, dedicated study; they are mentioned only as conceptual
  applications of LIFO.)
- **Browser back-button history**, conceptually — the most recently
  visited page is the first one you return to.

## 20. Queue Fundamentals

### 20.1 The analogy

Picture people waiting in a line at a checkout counter: the first
person to join the line is the first person served; everyone else waits
their turn in the order they arrived.

### 20.2 The rule: FIFO

A **queue** follows **FIFO — First In, First Out**: whatever was added
*first* is the first thing removed. The vocabulary: **enqueue** (add an
item, at the "rear" of the queue) and **dequeue** (remove an item, from
the "front" of the queue).

## 21. Why Not `list.pop(0)`?

A tempting, but flawed, first attempt at a queue:

```python
queue = []
queue.append("A")
queue.append("B")

first = queue.pop(0)   # "A" — removes and returns the FRONT item
```

This is *correct* in behavior — it does implement FIFO — but it is a
serious **performance** problem for a queue of any real size. Recall
§8's derivation directly: `pop(0)` removes the item at position `0` and
then must **shift every remaining item one position to the left** to
close the resulting gap — this is O(n) *every single time an item is
dequeued*. For a queue processing `m` items, repeated `pop(0)` calls
cost a total of roughly `O(m × n)` in the worst case — precisely the
kind of hidden, compounding cost the Big-O chapter warned against
(§37 there, mistake #13: "forgetting repeated function calls" inside a
loop can silently turn linear-looking code quadratic). **A list is
simply the wrong tool for repeated front-removal at scale** — this is
not a minor style preference; it is a structural performance mismatch
between the operation needed (remove from the front) and what the data
structure is actually good at (§8's "the end is cheap, the front is
expensive" rule, applied directly).

## 22. `deque`

### 22.1 What it is

```python
from collections import deque

queue = deque()
queue.append("A")
queue.append("B")

first = queue.popleft()
print(first)    # "A"
print(queue)     # deque(['B'])
```

`deque` (pronounced "deck," short for **double-ended queue**) is a
standard-library structure specifically designed so that adding and
removing items at **either end** — front or back — is efficient.

### 22.2 Core operations

| Method | Effect | Complexity |
|---|---|---|
| `deque.append(x)` | add to the **right** (rear) end | O(1) |
| `deque.appendleft(x)` | add to the **left** (front) end | O(1) |
| `deque.pop()` | remove and return from the **right** end | O(1) |
| `deque.popleft()` | remove and return from the **left** end | O(1) |

**This is the critical improvement over a plain list:** every one of
these four operations is O(1) — unlike a list, where operations at the
front cost O(n) (§8, §21). A `deque` is internally structured (a
doubly-linked block structure) specifically to make *both* ends equally
cheap, which is exactly the property a proper queue implementation
needs and a plain list structurally cannot offer.

## 23. Queue Operations

Mapping the conventional queue vocabulary directly onto `deque`:

| Queue concept | `deque` equivalent | Complexity |
|---|---|---|
| enqueue (add to the back of the line) | `queue.append(x)` | O(1) |
| dequeue (remove from the front of the line) | `queue.popleft()` | O(1) |
| peek/front (look without removing) | `queue[0]` | O(1) |
| is_empty | `len(queue) == 0` (or `not queue`) | O(1) |

**Handling an empty queue safely**, mirroring §18's stack guard:

```python
def safe_dequeue(queue):
    if not queue:
        return None
    return queue.popleft()
```

**Double-ended behavior when needed:** because `deque` supports both
ends equally well, `queue.appendleft(x)` and `queue.pop()` are also
available whenever a workload genuinely needs to add to the front or
remove from the back — for example, a work queue where certain items
must jump ahead of the normal FIFO order. This flexibility is a direct
consequence of `deque`'s design, not something bolted on for this
specific case.

## 24. Queue Use Cases

- **Task and job processing** — a worker takes the next task off the
  front of the queue, in the order tasks were submitted.
- **Request processing** — handling incoming requests in arrival order.
- **BFS (breadth-first search)**, conceptually — explores everything one
  "layer" away before moving further out, which is naturally expressed
  using a queue of "things still to visit" (again, not taught in depth
  here — only as a conceptual FIFO application, mirroring §19's
  treatment of DFS for stacks).
- **Event processing** — events are typically handled in the order they
  occurred.
- **Producer-consumer systems**, conceptually — one part of a system adds
  work to a queue; another part removes and processes it, independently
  and at its own pace. (This chapter does not cover concurrency itself —
  the queue's *role* in such a system is the only point being made
  here.)
- **Scheduling**, at a conceptual level — many scheduling systems are, at
  their core, a queue of pending work, sometimes with additional rules
  layered on top.

These ideas connect directly to backend systems, data engineering
pipelines, and AI processing pipelines, all of which routinely need to
process a stream of incoming work in a controlled, well-defined order.

## 25. Stack vs Queue

| | Stack | Queue |
|---|---|---|
| Rule | LIFO — Last In, First Out | FIFO — First In, First Out |
| Add | to the top | to the rear |
| Remove | from the top | from the front |
| Python tool | `list` (`append`/`pop()`) | `collections.deque` (`append`/`popleft()`) |
| Real-world example | a stack of plates; undo history | a checkout line; a task queue |

A concrete side-by-side trace, adding `"A"`, `"B"`, `"C"` in that order
to each:

```
STACK (list):  push A, B, C  →  [A, B, C]
               pop()          →  returns C  (the LAST one added)

QUEUE (deque): enqueue A, B, C  →  deque([A, B, C])
               popleft()        →  returns A  (the FIRST one added)
```

The same three items, added in the same order, produce **opposite**
removal orders — this single contrast is the entire conceptual
difference between the two structures, and everything else in §17–§24
is elaboration on exactly this point.

## 26. List vs Dictionary vs Set

| | List | Dictionary | Set |
|---|---|---|---|
| Core purpose | ordered sequence | key → value lookup | unique membership |
| Duplicates | allowed | keys must be unique; values can repeat | never allowed |
| Access by | position (index) | key | membership only (no positional access) |
| Ordering | preserves insertion order, indexable | preserves insertion order (not indexable by position) | no defined order |
| Typical use | sequences, records, iteration | lookup, counting, grouping | uniqueness, membership, set comparisons |

**Do not treat any one of these as universally "better."** The correct
structure depends entirely on the operation you need most: if you will
mostly *iterate in order* and occasionally access by position, a list
fits; if you will mostly *look something up by an identifier*, a
dictionary fits; if you will mostly *ask "does this exist"* or need
strict uniqueness, a set fits. Trying to force one structure to serve a
purpose it was not built for (e.g., using a list for repeated ID lookup)
does not fail outright — it simply costs far more than necessary, as
§8's complexity derivation makes concrete.

## 27. List vs `deque`

| | List | `deque` |
|---|---|---|
| Best at | indexed access (`items[i]`), append/pop at the **end** | efficient append/pop at **both** ends |
| Front operations | O(n) — `insert(0, x)`, `pop(0)` | O(1) — `appendleft(x)`, `popleft()` |
| Indexed access | O(1) | O(1) for the ends; accessing an arbitrary middle index is slower than for a list, because of `deque`'s internal block structure |
| Typical use | sequences accessed by position, or built up by appending to the end only | queues, sliding windows, anything needing efficient work at the front |

**Why `list.pop(0)` is usually inappropriate for a large queue:**
directly re-stating §21's derivation — every `pop(0)` call is O(n), so a
queue built on a plain list degrades badly as it grows, while the
identical workload on a `deque` stays O(1) per operation regardless of
size. **Rule of thumb:** if your workload needs indexed access into the
*middle* of a collection, or you will only ever add/remove at one end
(the end), a list is fine; the moment you need efficient work at the
*front*, reach for `deque` instead.

## 28. Dictionary vs Set

These two are easy to conflate because both rely on the same hashing
mechanism (§10, §16) — but they answer fundamentally different
questions:

- **Dictionary:** *"Give me the value associated with this key."*
  ```python
  users_by_id[user_id]   # → the actual customer record
  ```
- **Set:** *"Is this value present?"*
  ```python
  user_id in known_user_ids   # → True or False, nothing more
  ```

A dictionary **stores and returns data**; a set only **confirms
presence or absence** — it holds no associated payload beyond the
elements themselves. If you find yourself building a dictionary where
every value is unused, or is always simply `True`, that is a strong
signal the actual requirement is a set, not a dictionary. Conversely, if
you find yourself needing to answer "does X exist, *and if so, what is
its associated data*," that need cannot be met by a set alone — a
dictionary is required.

## 29. Choosing Based on Operations

This is the central skill of the entire chapter. For each problem
statement: **Requirement → Best-fit structure → Why → Alternative →
Complexity consideration.**

**1. Store ordered transactions.**
→ **List.** The requirement is explicitly about preserving arrival
order and (implicitly) allowing duplicates (two transactions can share
an amount). Alternative: none simpler — this is a list's exact purpose.
Complexity: O(1) amortized to append each new transaction.

**2. Find a customer by ID, repeatedly.**
→ **Dictionary**, keyed by customer ID. A list would force an O(n) scan
per lookup (§8); a dictionary answers in O(1) average-case (§10).
Alternative: a list, only acceptable if lookups are rare. Complexity: O(n)
average-case to build the index once, O(1) average-case per lookup
thereafter (mirroring the Big-O chapter's §24).

**3. Remove duplicate IDs.**
→ **Set** (or a seen-set pattern if order must be preserved — previous
chapter's §12–§13). A list would require checking `in` against a
growing list for every item — the exact O(n²) trap demonstrated in the
Big-O chapter's mini project (§41 there). Complexity: O(n) average-case
with a set, versus O(n²) with a naive list-based check.

**4. Check whether an ID was already processed.**
→ **Set** — this is a pure membership question, with no need for any
associated data beyond "seen or not." Alternative: a dictionary, if you
also need to store *something* about each processed ID (e.g., a
timestamp) — then the requirement has quietly grown into needing a
dictionary instead (§28). Complexity: O(1) average-case per check.

**5. Process tasks in arrival order.**
→ **`deque`**, used as a FIFO queue. A list's `pop(0)` would degrade to
O(n) per removal (§21); `deque.popleft()` stays O(1). Complexity: O(1)
amortized per enqueue and dequeue.

**6. Undo the latest action.**
→ **`list` used as a stack** (LIFO). The "latest" action is naturally
the top of a stack — `append()` to record an action, `pop()` to undo
it. Complexity: O(1) for both push and pop.

**7. Access an item by position.**
→ **List.** Positional/indexed access is a list's defining strength;
neither a dictionary, set, nor deque (for arbitrary middle positions)
offers this as cheaply. Complexity: O(1) for `items[i]`.

**8. Find common elements between two groups.**
→ **Set**, using `.intersection()` (§14). Comparing two lists
element-by-element for common items would be a nested-loop O(n × m)
operation; converting both to sets and intersecting is O(n + m) on
average. Complexity: O(n + m) average-case, versus O(n × m) naively.

**9. Count occurrences.**
→ **Dictionary** (or `collections.Counter`, per the previous chapter's
§5.6) — grouping by value while accumulating a count is a dictionary's
core strength. Complexity: O(n) average-case, one pass.

**10. Group records by category.**
→ **Dictionary** (specifically `defaultdict(list)`, per the previous
chapter's §6) — grouping is fundamentally a key → collection mapping.
Complexity: O(n) average-case, one pass, as fully derived in the
previous chapter's §7 and the Big-O chapter's §28.

The pattern across all ten: **name the operation the problem actually
needs (lookup? uniqueness? order? LIFO? FIFO?), then let that operation
— not habit — choose the structure.**

## 30. Combining Data Structures

Real systems rarely use just one structure — they typically use
**several, each responsible for a different requirement**, working
together:

```python
transactions = []               # LIST — preserves arrival order
transactions_by_id = {}         # DICT — fast lookup by transaction ID
seen_ids = set()                 # SET — fast duplicate detection
pending_transactions = deque()   # DEQUE — FIFO processing queue
```

Each structure here solves exactly one job, and no other structure in
the group is asked to do that job:

- `transactions` answers *"what happened, in order?"*
- `transactions_by_id` answers *"give me transaction X"*, quickly.
- `seen_ids` answers *"have I seen this ID before?"*, quickly.
- `pending_transactions` answers *"what should I process next?"*, in
  the correct order.

This is not over-engineering — it is the natural, expected result of
applying §29's operation-by-operation reasoning to a system that has
*more than one* requirement at once, which almost every real system
does. Recognizing this pattern — multiple structures, one responsibility
each — is one of the most practically important lessons in this
chapter, and §31–§33 develop it into three complete, realistic examples.

## 31. Real-World Banking Example

**Requirements:** preserve transactions in arrival order; look up a
transaction by ID; detect duplicate transaction IDs; process pending
transactions FIFO; track which transaction IDs have already been
processed.

```python
from collections import deque

transaction_log = []              # list — arrival order, for auditing/reporting
transactions_by_id = {}           # dict — O(1) average-case lookup by ID
seen_transaction_ids = set()       # set — O(1) average-case duplicate detection
pending_queue = deque()            # deque — FIFO processing order
processed_ids = set()              # set — O(1) average-case "already handled?" check


def receive_transaction(transaction):
    transaction_id = transaction["id"]

    if transaction_id in seen_transaction_ids:
        return False   # duplicate — reject

    seen_transaction_ids.add(transaction_id)
    transaction_log.append(transaction)
    transactions_by_id[transaction_id] = transaction
    pending_queue.append(transaction_id)
    return True


def process_next():
    if not pending_queue:
        return None
    transaction_id = pending_queue.popleft()
    processed_ids.add(transaction_id)
    return transactions_by_id[transaction_id]
```

**Why each structure exists:** `transaction_log` preserves the exact
order transactions arrived, for auditing. `transactions_by_id` and
`seen_transaction_ids` both exist purely for O(1) average-case lookups —
one returns data, one confirms presence (directly §28's distinction).
`pending_queue` guarantees transactions are processed in the order they
arrived, without paying `list.pop(0)`'s O(n) cost (§21). `processed_ids`
lets any later step cheaply ask "has this one already been handled?"
without re-scanning anything.

## 32. Real-World Data Engineering Example

**Requirements:** receive records from an external source; detect
duplicate record IDs; look up metadata by source ID; queue records for
downstream processing; preserve a final ordered result.

```python
from collections import deque

metadata_by_source_id = {"S1": {"origin": "api"}, "S2": {"origin": "batch"}}

seen_record_ids = set()        # duplicate detection
processing_queue = deque()      # FIFO — records queued in arrival order
final_ordered_result = []       # list — the clean, ordered output


def ingest_record(record):
    record_id = record["id"]

    if record_id in seen_record_ids:
        return   # duplicate — skip ingestion entirely

    seen_record_ids.add(record_id)
    processing_queue.append(record)


def process_pipeline():
    while processing_queue:
        record = processing_queue.popleft()
        metadata = metadata_by_source_id.get(record["source_id"])
        enriched_record = {**record, "metadata": metadata}
        final_ordered_result.append(enriched_record)
```

**Architecture, in one sentence:** a `set` gate keeps duplicates out
before they ever enter the pipeline; a `deque` holds work in FIFO order
until it is processed; a `dict` provides O(1) average-case metadata
enrichment per record; a plain `list` accumulates the clean, ordered
final output — four structures, four distinct responsibilities, exactly
mirroring §30's principle.

## 33. Real-World AI/ML Example

**Requirements:** enforce unique document IDs; look up document
metadata; hold documents pending processing; track which document IDs
have been processed; produce an ordered output for downstream use (e.g.,
feeding a model or an index).

```python
from collections import deque

known_document_ids = set()          # uniqueness gate
document_metadata = {}               # dict — id → metadata
pending_documents = deque()          # FIFO processing queue
processed_document_ids = set()       # tracks completed work
ordered_output = []                   # final, ordered result


def submit_document(document):
    doc_id = document["id"]
    if doc_id in known_document_ids:
        return False   # already submitted — reject

    known_document_ids.add(doc_id)
    document_metadata[doc_id] = document.get("metadata", {})
    pending_documents.append(document)
    return True


def process_documents():
    while pending_documents:
        document = pending_documents.popleft()
        doc_id = document["id"]
        processed_document_ids.add(doc_id)
        ordered_output.append(document)
```

This example is deliberately built from the exact same five structures
as §31 and §32 — standard Python only, no `pandas`, `numpy`, or ML
frameworks — because the *underlying data-structure reasoning* for an
AI data pipeline is identical to a banking or data-engineering pipeline:
uniqueness needs a set, lookup needs a dictionary, ordered processing
needs a deque, and ordered output needs a list. The domain changes; the
structural reasoning from §29 does not.

## 34. Memory Trade-offs

Different structures carry different memory overhead, conceptually
(this chapter deliberately avoids invented, fake byte counts — the
point is the *relative* trade-off, not a specific number):

- A plain **list** stores its elements about as compactly as Python
  allows for a general-purpose sequence.
- A **dictionary** and a **set** both need additional internal storage
  beyond just the elements themselves, to support the hashing mechanism
  that makes O(1) average-case lookup and membership possible (§10,
  §16) — this extra structure is the *price* of that speed.
- A **`deque`** organizes its storage in blocks to keep both ends
  efficient, which involves somewhat more overhead per element than a
  plain list optimized purely for sequential, one-ended access.

**The trade-offs to reason about, explicitly, every time:**
- **Memory vs. speed** — a dictionary or set costs more memory per
  element than a list, in exchange for dramatically faster lookup or
  membership testing (directly the Big-O chapter's §25 principle,
  applied here concretely).
- **Indexing vs. lookup** — a list is memory-efficient for pure
  sequential access; a dictionary trades some of that efficiency for
  key-based access.
- **Uniqueness vs. duplicates** — a set actively discards duplicate
  data to maintain uniqueness; if duplicates carry meaningful
  information, that information is genuinely gone once stored only in a
  set.
- **Preprocessing vs. repeated work** — building an index (a dictionary
  or set) costs memory and time up front, in exchange for avoiding
  repeated, more expensive work later (§10, §29's problem 2 and 3, and
  the Big-O chapter's §24 worked example).

## 35. Complexity Comparison

Connecting directly to
[Big-O, Time, and Space Complexity](03-big-o-time-and-space-complexity.md):

| Operation | List | Dict | Set | Deque | Stack (list) | Queue (deque) |
|---|---|---|---|---|---|---|
| Index access | O(1) | — | — | O(1) at ends; slower in the middle | O(1) (top = end) | — |
| Key lookup | — | O(1) avg-case | — | — | — | — |
| Membership (`in`) | O(n) worst case | O(1) avg-case (keys) | O(1) avg-case | O(n) worst case | — | — |
| Append/insert at end | O(1) amortized | O(1) avg-case (`d[k]=v`) | O(1) avg-case (`add`) | O(1) (`append`) | O(1) (push) | — |
| Prepend / insert at front | O(n) | — | — | O(1) (`appendleft`) | — | O(1) (enqueue via `append`) |
| Delete/pop at end | O(1) | O(1) avg-case (`pop`) | O(1) avg-case | O(1) (`pop`) | O(1) (pop) | — |
| Delete/pop at front | O(n) (`pop(0)`) | — | — | O(1) (`popleft`) | — | O(1) (dequeue via `popleft`) |

**Assumptions, stated explicitly, per the Big-O chapter's accuracy
standard (§18 there):** dictionary and set figures are **average-case**,
relying on hashing behaving well for the given keys; list `append` and
dictionary/set insertion are **amortized**, not a flat guarantee on
every single call (Big-O chapter's §34); deque's O(1) end-operations
are a property of its specific internal implementation, not a universal
law of "queues" in the abstract. None of these figures should be
treated as an unconditional guarantee independent of these assumptions.

## 36. Common Beginner Mistakes

**List**

1. *Using a list for repeated key lookup.* Scanning a list of records
   for a matching ID, over and over, when a dictionary index would
   answer in O(1) average-case (§10, §29 problem 2). **Lesson:** if you
   are searching by an identifier more than a couple of times, build an
   index.

2. *Using `pop(0)` as a queue.* Directly §21's central point —
   correct behavior, poor performance at scale. **Lesson:** use
   `deque.popleft()` instead.

3. *Confusing `append()` and `extend()`.* §6's worked example —
   `items.append([1, 2])` nests a list inside a list; `items.extend([1,
   2])` adds each element individually. **Lesson:** ask "am I adding one
   new item, or several?" before choosing.

4. *Confusing `remove()` and `pop()`.* `remove(value)` deletes by
   *value* and returns nothing; `pop(index)` deletes by *position* and
   returns the removed item. **Lesson:** decide whether you know the
   value or the position before choosing.

5. *Modifying a list while iterating over it.* Already covered in
   depth in the previous chapter's §32, mistake #3 — worth restating
   here because it commonly resurfaces specifically with `remove()`
   inside a loop.

**Dictionary**

6. *Using a list when key lookup is actually needed.* The mirror image
   of mistake #1 — reaching for a list of records and manually filtering
   by field, instead of recognizing the requirement is really "look up
   by key" and building a dictionary.

7. *Assuming missing keys return `None`.* `dict[key]` raises
   `KeyError` on a missing key — it does **not** silently return `None`.
   **Lesson:** use `.get(key)` (which *does* default to `None`) when a
   missing key is a real possibility.

8. *Confusing keys and values.* Especially when iterating — `for x in
   some_dict` iterates over **keys**, not values or pairs; forgetting
   this leads to confusing bugs. **Lesson:** be explicit — `.keys()`,
   `.values()`, or `.items()` — when the default (keys) is not what is
   intended.

9. *Using `dict.get()` without understanding its default behavior.*
   Assuming `dict.get(key)` raises an error like `dict[key]` does, or
   forgetting that its second argument controls the fallback value.
   **Lesson:** `get()`'s entire purpose is to *avoid* raising — know what
   it returns when the key is absent (`None`, unless a default is given).

**Set**

10. *Expecting indexes.* Writing `some_set[0]` — sets have no positional
    access at all. **Lesson:** if you need positions, you need a list,
    not a set.

11. *Expecting duplicates to be preserved.* Adding the same value twice
    and being surprised the set only holds it once. **Lesson:** this is
    a set's defining behavior, not a bug — if duplicates must be
    counted or kept, a set is the wrong structure (§15).

12. *Using `remove()` when the value might be missing.* Raises
    `KeyError` unexpectedly. **Lesson:** use `discard()` when "already
    gone" is an acceptable, unremarkable outcome (§14).

13. *Assuming a set is a drop-in replacement for every list.* A set
    solves uniqueness and membership — it does not solve "keep things in
    order" or "keep duplicates." **Lesson:** match the structure to the
    *specific* requirement, not to "this collection just needs to hold
    some values."

**Stack**

14. *Popping from the wrong end.* Calling `stack.pop(0)` instead of
    `stack.pop()` accidentally turns a stack into something else
    entirely (and reintroduces the O(n) cost from §8). **Lesson:**
    stack operations always happen at the **same** end — pick one (the
    list's end) and never touch the other.

15. *Peeking an empty stack.* `stack[-1]` on an empty list raises
    `IndexError`. **Lesson:** always check `is_empty` first (§18).

**Queue**

16. *Using `list.pop(0)`.* Restating §21 one final time, because it is
    common enough to warrant repetition across both the list and queue
    mistake lists: this is correct but slow at scale — use `deque`.

17. *Confusing FIFO and LIFO.* Implementing a queue with `stack.pop()`
    (removing the most recently added item) when FIFO (removing the
    *earliest* added item) was actually required. **Lesson:** re-check
    §25's side-by-side trace whenever "which end do I remove from?" is
    unclear.

**General**

18. *Choosing a structure because it "looks familiar."* Defaulting to a
    list for everything because lists are the first structure learned,
    rather than asking §29's operation-driven questions.

19. *Ignoring operation complexity.* Picking a structure without
    considering how many times each operation will actually run — a
    choice that is fine for 10 items can be disastrous for 10 million
    (the entire premise of the previous, Big-O chapter).

20. *Ignoring memory.* Reaching for a dictionary or set purely out of
    habit, even when a plain list would do, and paying unnecessary
    memory overhead (§34) for no real benefit.

21. *Choosing based on syntax rather than requirements.* Picking
    whichever structure has the most "convenient-looking" method for
    one specific line of code, without considering the *rest* of the
    workload's requirements.

## 37. Edge Cases

| Situation | List | Dict | Set | Stack (list) | Queue (deque) |
|---|---|---|---|---|---|
| Empty | `[]` — iterates zero times, `pop()`/`pop(0)` raise `IndexError` | `{}` — lookups raise `KeyError`, `.get()` returns default safely | `set()` — `.pop()` raises `KeyError` | `pop()`/`[-1]` raise `IndexError` — always check `is_empty` first (§18) | `popleft()`/`[0]` raise `IndexError`/similar — always check `is_empty` first (§23) |
| One item | Works normally; `items[0]` and `items[-1]` are the same item | One key-value pair; behaves normally | One element; behaves normally | Push/pop that one item behaves normally | Enqueue/dequeue that one item behaves normally |
| Duplicate values | Fully supported and preserved | Duplicate **keys** are impossible — a repeated key simply overwrites the previous value (§11); duplicate **values** are fine | Impossible by definition — duplicates silently collapse (§15, mistake #11) | Duplicates fully supported (it is just a list) | Duplicates fully supported (it is just a deque) |
| Missing dictionary keys | N/A | `dict[key]` raises `KeyError`; `dict.get(key)` returns `None`/default safely (§10) | N/A | N/A | N/A |
| Removing an absent value | `remove(value)` raises `ValueError` | `del dict[key]` raises `KeyError`; `dict.pop(key, default)` is safe | `remove(x)` raises `KeyError`; `discard(x)` is safe (§14) | N/A (stack only removes the top, which is always present unless empty) | N/A (queue only removes the front, which is always present unless empty) |
| `None` values | A list can hold `None` as a legitimate element | `None` can be a legitimate *value* (but never as a set element check confusion — see previous chapter's §16) | `None` is a valid, hashable set element | `None` can be pushed/popped like any other value | `None` can be enqueued/dequeued like any other value |
| Large collections | Indexed access and end-operations stay cheap; front operations get proportionally more expensive as size grows (§8) | Lookup/insert/delete stay O(1) average-case regardless of size | Membership/add/remove stay O(1) average-case regardless of size | Push/pop stay O(1) regardless of size | Enqueue/dequeue stay O(1) regardless of size |
| Mutation during iteration | Can silently skip or repeat items (previous chapter's §32, mistake #3) | Raises `RuntimeError: dictionary changed size during iteration` if keys are added/removed mid-loop | Same `RuntimeError` risk as dict, for the same underlying reason | Same list-mutation risk if iterating while pushing/popping | Same risk if iterating while enqueuing/dequeuing |

## 38. Data-Structure Selection Algorithm

A repeatable process for choosing a structure for a new problem:

1. **Identify what the data represents.** Records? Identifiers? Events?
   Tasks?
2. **Identify the most common operations.** Will this be searched?
   Looked up by key? Checked for membership? Iterated in order?
3. **Identify whether order matters.** Does the data need to preserve
   the sequence it arrived in, or is order irrelevant?
4. **Identify whether duplicates matter.** Must every occurrence be
   kept, or should repeats collapse to one?
5. **Identify whether key-based lookup is required.** Will you need to
   find an item by an identifier, rather than by position?
6. **Identify whether membership testing dominates.** Will "does X
   exist?" be asked often, without needing an associated value back?
7. **Identify whether LIFO or FIFO behavior is required.** Does the most
   recent or the earliest item need to come out first?
8. **Estimate input size.** Tens of items? Millions? (Recall the Big-O
   chapter's §2 — small input can hide a poor choice that only surfaces
   at scale.)
9. **Consider time complexity.** Given the operations from step 2 and
   the size from step 8, which structure keeps the dominant operations
   cheap?
10. **Consider memory.** Is the extra overhead of a dict/set (§34)
    justified by the operations it enables?
11. **Choose the simplest structure that satisfies the requirements.**
    Do not reach for a dictionary or set "just in case" if a plain list
    genuinely covers every actual requirement.
12. **Validate the choice against a realistic workload.** Would this
    choice still hold up if the input were 100x or 10,000x larger, or if
    a specific operation ran far more often than expected? If not,
    reconsider before committing.

This ordered list deliberately mirrors the shape of the Big-O chapter's
own step-by-step analysis method (§35 there) — data-structure selection
and complexity analysis are two faces of the same underlying skill.

## 39. Progressive Exercises

Solutions and full reasoning are in **§45 — Answer Key / Solutions**.

### Level 1 — Beginner

**1.** Store a list of names, add three more, and print the last one
added.

**2.** Build a dictionary mapping user IDs (`101`, `102`, `103`) to
names, then look up `102`'s name.

**3.** Given `numbers = [4, 2, 4, 1, 2, 3]`, remove duplicates using a
set.

**4.** Implement a stack using a list: push `"A"`, `"B"`, `"C"`, then pop
twice and print each popped value.

**5.** Implement a queue using `deque`: enqueue `"task1"`, `"task2"`,
`"task3"`, then dequeue twice and print each dequeued value.

### Level 2 — Intermediate

**6.** For each of the following ten scenarios, name the best-fit
structure and justify it in one sentence: (a) a shopping cart's items in
the order added; (b) a phone book, name to number; (c) tracking which
usernames are taken; (d) a printer's job queue; (e) an "undo" feature in
a text editor; (f) a leaderboard with duplicate scores allowed; (g)
checking whether an IP address is on a blocklist, frequently; (h)
grouping orders by customer; (i) a browser's back-button history; (j) a
set of currently-online user IDs.

**7.** Given a list of 100,000 users and a need to look up a user by ID
1,000 times, replace repeated linear search with a dictionary-based
approach, and state the complexity before and after.

**8.** Given a stream of incoming order IDs, use a set to flag any order
ID seen more than once.

**9.** Implement `undo(stack)` that pops and returns the most recent
action, returning `None` safely if the stack is empty.

**10.** Implement a simple task processor using `deque`: add three
tasks, then process (dequeue and print) them one at a time until the
queue is empty.

### Level 3 — Advanced

**11.** Build a `transactions_by_id` dictionary from a list of
transaction records, then use it to look up three different transaction
IDs.

**12.** Maintain a `processed_ids` set as you iterate over a stream of
incoming records, skipping any record whose ID has already been seen.

**13.** Build a FIFO queue of pending transactions using `deque`, then
process them in order, moving each processed ID into a separate
`processed_ids` set.

**14.** Combine a dictionary, a set, and a deque in one small program
that: indexes records by ID (dict), rejects duplicates (set), and
processes remaining records in arrival order (deque).

**15.** Implement "find a value in a collection" two ways — once using a
list and `in`, once using a set and `in` — and explain, using Big-O
reasoning from the previous chapter, why the two differ for large
inputs.

### Level 4 — Production-Oriented

**16.** Design (in code and in words) a small event-processing
structure that: accepts events in arrival order, rejects duplicate
event IDs, and processes events FIFO.

**17.** Design a log-processing data model that: groups log entries by
service (dictionary), and preserves each service's entries in arrival
order (list, as each group's value).

**18.** Design a banking transaction-processing structure combining at
least three of the five core structures from this chapter, and justify
each choice.

**19.** Design an AI document-processing queue that: enforces unique
document IDs, looks up document metadata by ID, and processes documents
FIFO.

**20.** For a data-ingestion pipeline receiving records from multiple
sources, choose structures for: deduplication, per-source metadata
lookup, and preserving a final ordered, processed output — and justify
each choice against the alternatives.

## 40. Mini Project — Transaction Processing Data-Structure Engine

### Requirements

The system receives transaction records and must:

1. Preserve arrival order.
2. Detect duplicate transaction IDs.
3. Store transaction lookup by ID.
4. Queue pending transactions.
5. Track processed transactions.
6. Support lookup by transaction ID.
7. Process transactions FIFO.
8. Support an "undo" concept for the latest processed action, using a
   stack.
9. Produce an ordered final result.

### Before implementing, document:

- **Problem** — build an engine that ingests transactions safely (no
  duplicates), processes them in the order received, and allows undoing
  the most recently *processed* transaction — a realistic mixture of
  ordering, lookup, uniqueness, FIFO, and LIFO requirements in one
  system.
- **Inputs** — a stream of transaction dictionaries, each with at least
  an `"id"` and an `"amount"`.
- **Outputs** — a final, ordered list of processed transactions; the
  ability to look up any received transaction by ID; the ability to undo
  the most recently processed transaction.
- **Constraints** — transaction IDs must be treated as unique; processing
  order must match arrival order; undo must reverse only the *most
  recently processed* transaction, not an arbitrary one.
- **Operations needed** — insert (on arrival), duplicate-check (on
  arrival), enqueue (on arrival), dequeue (on processing), lookup (by
  ID, at any time), push (on processing, for undo support), pop (on
  undo).
- **Data structures considered** — a single list for everything
  (rejected: O(n) lookup and O(n) FIFO removal, per §8 and §21); a
  dictionary alone (rejected: no natural ordering or FIFO/LIFO
  behavior).
- **Chosen structures** — `list` (arrival log), `dict` (ID lookup),
  `set` (duplicate detection), `deque` (FIFO pending queue), `list`
  used as a stack (undo history of processed transactions).
- **Why each was selected** — directly mirroring §31's banking example,
  with the stack added specifically to satisfy requirement 8.
- **Complexity** — ingestion: O(1) average-case per transaction (one set
  check, one dict insert, one list append, one deque append); processing:
  O(1) amortized per transaction (one deque popleft, one dict lookup, one
  stack push); undo: O(1) (one stack pop).
- **Edge cases** — a duplicate transaction ID on arrival (reject); an
  undo request when nothing has been processed yet (return `None`
  safely); processing when the queue is empty (return `None` safely).
- **Pseudocode:**
  ```
  on arrival:
      if id already seen: reject
      record id as seen
      append to arrival log
      store in lookup dict
      enqueue to pending queue

  on process_next:
      if pending queue is empty: return None
      dequeue the next transaction
      push it onto the processed-history stack
      append it to the final ordered result
      return it

  on undo_last_processed:
      if processed-history stack is empty: return None
      pop the most recently processed transaction
      remove it from the final ordered result
      return it
  ```
- **Dry run** — trace three transactions (`T1`, `T2`, a duplicate `T1`)
  through arrival, then process two, then undo one, confirming by hand
  that the duplicate is rejected, processing order matches arrival
  order, and undo reverses only the most recent processed item.

### Reference Implementation

```python
from collections import deque


class TransactionEngine:
    def __init__(self):
        self.arrival_log = []            # list — full arrival-order record
        self.transactions_by_id = {}     # dict — O(1) average-case lookup
        self.seen_ids = set()             # set — duplicate detection
        self.pending_queue = deque()      # deque — FIFO processing order
        self.processed_stack = []         # list-as-stack — undo support
        self.final_result = []            # list — ordered, processed output

    def receive(self, transaction):
        transaction_id = transaction["id"]
        if transaction_id in self.seen_ids:
            return False   # duplicate — reject

        self.seen_ids.add(transaction_id)
        self.arrival_log.append(transaction)
        self.transactions_by_id[transaction_id] = transaction
        self.pending_queue.append(transaction_id)
        return True

    def process_next(self):
        if not self.pending_queue:
            return None
        transaction_id = self.pending_queue.popleft()
        transaction = self.transactions_by_id[transaction_id]
        self.processed_stack.append(transaction)
        self.final_result.append(transaction)
        return transaction

    def undo_last_processed(self):
        if not self.processed_stack:
            return None
        transaction = self.processed_stack.pop()
        self.final_result.remove(transaction)
        return transaction

    def lookup(self, transaction_id):
        return self.transactions_by_id.get(transaction_id)
```

```python
engine = TransactionEngine()

engine.receive({"id": "T1", "amount": 100})
engine.receive({"id": "T2", "amount": 250})
engine.receive({"id": "T1", "amount": 999})   # duplicate — rejected

engine.process_next()   # processes T1
engine.process_next()   # processes T2

print(engine.final_result)
# [{'id': 'T1', 'amount': 100}, {'id': 'T2', 'amount': 250}]

engine.undo_last_processed()   # undoes T2 (the most recently processed)
print(engine.final_result)
# [{'id': 'T1', 'amount': 100}]

print(engine.lookup("T1"))
# {'id': 'T1', 'amount': 100}
```

**The lesson this project demonstrates concretely:** five distinct
requirements (ordering, lookup, uniqueness, FIFO, LIFO) were each
handled by the structure purpose-built for it — no single structure was
stretched to cover a job it was not designed for, and every operation in
the class stays cheap (O(1) or O(1) amortized/average-case) as a direct
result.

## 41. Interview Questions

**Foundational**

- What is a data structure, and how is it different from a data type?
- Why does choosing the right data structure matter for a program's
  performance?
- When would you choose a list? A dictionary? A set?
- What is the difference between a dictionary and a set?
- What is a stack? What is a queue?
- What is LIFO? What is FIFO?

**Intermediate**

- Why is `list.pop(0)` inefficient for a large queue? What would you use
  instead, and why?
- Why is `deque` appropriate for queue behavior when a plain list is
  not?
- What is the time complexity of list indexing? Of dictionary lookup?
  What qualifier should you attach to the dictionary answer, and why?
- Why are sets useful for membership tests? What is happening
  "underneath" that makes them fast, at a conceptual level?
- What is the difference between `append()` and `extend()`? Give an
  example where confusing them produces a bug.
- What is the difference between `remove()` and `pop()`, for both lists
  and sets?
- What happens when you access a missing dictionary key with `dict[key]`
  versus `dict.get(key)`?

**Advanced**

- What data structure would you choose to implement an undo system, and
  why specifically that one rather than a queue?
- What structure would you use for a job/task queue, and why would a
  plain list be a poor choice at scale?
- What structure(s) would you use for duplicate detection, and how does
  your answer change if you also need to preserve the original arrival
  order of the non-duplicate items?
- How would you design a transaction-processing data model that needs
  ordering, fast lookup, duplicate rejection, and FIFO processing all at
  once? Name the structure for each requirement.
- When would combining multiple data structures in a single system be
  the *right* design, rather than a sign of over-engineering?

**Scenario-based**

- "You're asked to check membership against a list of 2 million banned
  usernames, for every single signup attempt. What would you change,
  and what complexity improvement would you expect?"
- "A teammate implemented a task queue using `list.append()` and
  `list.pop(0)`. What would you point out, and what would you suggest
  instead?"
- "You need to both look up a customer by ID *and* iterate over all
  customers in the order they signed up. Would you use one structure or
  more than one? Justify your answer."
- "How would you detect whether two groups of customer IDs have any
  customers in common, and how would your approach's cost scale as both
  groups grow?"

## 42. Data-Structure Decision Table

| Requirement | Recommended structure | Why |
|---|---|---|
| Ordered, indexed sequence | `list` | Preserves order; supports O(1) positional access. |
| Key → value lookup | `dict` | O(1) average-case lookup by an arbitrary key. |
| Unique values only | `set` | Duplicates are structurally impossible; O(1) average-case membership. |
| LIFO (undo-like) behavior | `list` used as a stack | `append()`/`pop()` at the end are both O(1) — the cheap end (§8). |
| FIFO (arrival-order) processing | `deque` | O(1) at both ends, unlike a list's O(n) front operations (§21–§22). |
| Efficient operations at both ends | `deque` | Purpose-built for exactly this (§22). |
| Repeated membership tests | `set` | O(1) average-case, versus a list's O(n) worst case (§16). |
| Repeated lookup by identifier | `dict` | O(1) average-case, versus a list's O(n) worst case (§10, §29 problem 2). |
| Grouping | `dict` / `defaultdict` | A natural key → collection mapping (previous chapter's §4–§7). |
| Deduplication | `set`, or a dict-based strategy for records | O(n) average-case overall, versus a naive O(n²) list-based check (previous chapter's §12–§15; Big-O chapter's §41). |

**This is a starting point, not a universal rule. Workload and
operation frequency matter** — a list can outperform a set for tiny
collections checked rarely; a dictionary's memory overhead may not be
worth it if a key is only ever looked up once. Every row above assumes
the described operation happens *often enough* to matter — always
re-verify against §38's step-by-step process for the specific problem
at hand, rather than applying this table mechanically.

## 43. Pattern Recognition Cheat Sheet

```
ORDERED SEQUENCE?
    → LIST

KEY → VALUE?
    → DICTIONARY

UNIQUE MEMBERSHIP?
    → SET

LAST IN, FIRST OUT?
    → STACK (list, used carefully)

FIRST IN, FIRST OUT?
    → QUEUE (deque)
```

And the question that should always be asked last, as the final
tie-breaker whenever more than one structure seems plausible:

> **"What operation will happen most often?"**

Whichever structure makes *that* operation cheapest is very often the
right choice — everything else in this chapter exists to help you
answer that one question with confidence, for any new problem you
encounter.

## 44. Final Review

- A **data structure** determines how multiple values are organized and
  accessed — it is a different concept from a **data type**, which
  describes what kind of value one single item is.
- **Lists** are ordered, mutable, allow duplicates, and are strong at
  indexed access and end-appending; they are weak at repeated key
  lookup, uniqueness checks, and front-removal.
- **Dictionaries** map keys to values, with O(1) average-case lookup,
  insertion, update, and deletion — the structure of choice whenever a
  natural identifier and repeated lookup are both present.
- **Sets** guarantee uniqueness and answer "does this exist?" in O(1)
  average-case — but offer no positional access, no duplicate
  preservation, and no ordering guarantee.
- **Stacks** (LIFO) are naturally implemented with a plain list, always
  operating on the same end (`append()`/`pop()`), because that end is
  the cheap one.
- **Queues** (FIFO) should use `collections.deque`, not a plain list —
  `list.pop(0)` is a correct but O(n)-per-call anti-pattern at any real
  scale; `deque`'s `append()`/`popleft()` stay O(1).
- **`deque`** generalizes the queue idea to efficient operations at
  *either* end, and is the right tool whenever front-of-collection work
  needs to be cheap.
- Every complexity claim in this chapter carries the same caveats
  established in the Big-O chapter: **typical, average-case, or
  amortized** — never an unconditional guarantee independent of
  assumptions.
- Real systems almost always **combine multiple structures**, each
  responsible for exactly one requirement — this is the normal,
  expected shape of production code, demonstrated concretely across the
  banking, data-engineering, and AI/ML examples in this chapter.
- The core skill this chapter trains is not "know what five structures
  exist" — it is: **identify the operations a problem actually needs,
  then choose the structure that makes those operations cheap.**

## 45. Answer Key / Solutions

### Level 1

**1.** A list append operation, mirroring §5–§6 directly.
```python
names = ["Alice", "Bob"]
names.append("Charlie")
names.append("Diana")
names.append("Eve")
print(names[-1])   # "Eve"
```
Requirement: ordered sequence, duplicates allowed. Structure chosen:
list. Complexity: O(1) amortized per append.

**2.** A direct dictionary build-and-lookup, per §9–§10.
```python
users_by_id = {101: "Alice", 102: "Bob", 103: "Charlie"}
print(users_by_id[102])   # "Bob"
```
Requirement: key → value lookup. Alternative considered: a list of
tuples, rejected because lookup would be O(n) instead of O(1)
average-case.

**3.** A direct `set()` deduplication, per §13 and the previous
chapter's §12.
```python
numbers = [4, 2, 4, 1, 2, 3]
unique = set(numbers)
print(unique)   # {1, 2, 3, 4}
```
Requirement: uniqueness, order irrelevant. Edge case: if order mattered,
this would be the wrong tool (previous chapter's §12.2) — the seen-set
pattern would be needed instead.

**4.** Stack behavior via list `append`/`pop`, per §17–§18.
```python
stack = []
stack.append("A")
stack.append("B")
stack.append("C")

print(stack.pop())   # "C"
print(stack.pop())   # "B"
```
Requirement: LIFO. Complexity: O(1) per push/pop.

**5.** Queue behavior via `deque`, per §22–§23.
```python
from collections import deque

queue = deque()
queue.append("task1")
queue.append("task2")
queue.append("task3")

print(queue.popleft())   # "task1"
print(queue.popleft())   # "task2"
```
Requirement: FIFO. Complexity: O(1) per enqueue/dequeue — a plain list's
`pop(0)` would have worked identically here but degrades badly at scale
(§21), which is why `deque` is the better habit to build even for small
examples.

### Level 2

**6.**
(a) shopping cart items in order → **list** (order matters, duplicates
possible). (b) phone book → **dict** (key → value). (c) tracking taken
usernames → **set** (pure membership). (d) printer job queue → **deque**
(FIFO). (e) undo feature → **list-as-stack** (LIFO). (f) leaderboard
with duplicate scores → **list** (order/duplicates both matter; not a
set). (g) IP blocklist, frequent checks → **set** (O(1) average-case
membership at scale). (h) grouping orders by customer → **dict**
(specifically `defaultdict(list)`, previous chapter's §6). (i) browser
back-button history → **list-as-stack** (LIFO — most recent page first).
(j) currently-online user IDs → **set** (pure membership, no associated
data needed).

**7.** Directly the Big-O chapter's §24 pattern, restated here.
```python
users_by_id = {u["id"]: u for u in users}   # O(n) average-case, once

for target_id in target_ids:                  # 1,000 lookups
    found = users_by_id.get(target_id)          # O(1) average-case each
```
Before: O(1,000 × 100,000) in the worst case with linear search. After:
O(100,000 + 1,000) — a dramatic improvement, exactly matching §29
problem 2's reasoning.

**8.** A seen-set used specifically to *flag* repeats, rather than
silently discard them.
```python
seen = set()
duplicate_ids = []

for order_id in incoming_order_ids:
    if order_id in seen:
        duplicate_ids.append(order_id)
    else:
        seen.add(order_id)

print(duplicate_ids)
```

**9.** Directly mirroring §18's safe-pop pattern.
```python
def undo(stack):
    if not stack:
        return None
    return stack.pop()
```

**10.**
```python
from collections import deque

tasks = deque()
tasks.append("task1")
tasks.append("task2")
tasks.append("task3")

while tasks:
    current = tasks.popleft()
    print(f"Processing: {current}")
```

### Level 3

**11.**
```python
transactions = [{"id": "T1", "amount": 100}, {"id": "T2", "amount": 250}, {"id": "T3", "amount": 75}]
transactions_by_id = {t["id"]: t for t in transactions}

print(transactions_by_id["T1"])
print(transactions_by_id["T2"])
print(transactions_by_id["T3"])
```
Structure chosen: dict, for O(1) average-case repeated lookup — directly
§10 and §29 problem 2.

**12.**
```python
processed_ids = set()
unique_records = []

for record in incoming_records:
    if record["id"] not in processed_ids:
        processed_ids.add(record["id"])
        unique_records.append(record)
```
This is exactly the previous chapter's §13.1 seen-set pattern, applied
here as "processed tracking" rather than pure deduplication — the same
structure, a slightly different framing of the same underlying need.

**13.**
```python
from collections import deque

pending = deque(transactions)   # deque can be built directly from an iterable
processed_ids = set()

while pending:
    transaction = pending.popleft()
    processed_ids.add(transaction["id"])
    print(f"Processed {transaction['id']}")
```

**14.**
```python
from collections import deque

records_by_id = {}
seen_ids = set()
pending = deque()

for record in incoming_records:
    if record["id"] in seen_ids:
        continue   # reject duplicate
    seen_ids.add(record["id"])
    records_by_id[record["id"]] = record
    pending.append(record)

while pending:
    record = pending.popleft()
    print(f"Processing {record['id']}")
```
Three structures, three responsibilities — directly §30's principle,
worked as a standalone exercise.

**15.**
```python
def contains_list(collection, target):
    return target in collection   # O(n) worst case

def contains_set(collection, target):
    return target in collection   # O(1) average-case, IF collection is a set
```
For a large `collection`, `target in some_list` may scan every element
(O(n) worst case), while `target in some_set` uses hashing to check in
O(1) average-case — for repeated checks against the same collection,
this difference compounds directly, exactly as demonstrated numerically
in the Big-O chapter's §46 (exercise 15's worked answer there).

### Level 4

**16.**
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
Requirement mapping: uniqueness → set; FIFO order → deque — directly
§31's banking pattern, reduced to its two essential structures.

**17.**
```python
from collections import defaultdict

logs_by_service = defaultdict(list)

for entry in log_entries:
    logs_by_service[entry["service"]].append(entry)
```
Requirement mapping: grouping → dict (`defaultdict(list)`); each group's
internal arrival order → list (as the value type) — this is precisely
the previous chapter's §4–§6 grouping pattern, restated here as a
data-structure-selection exercise rather than a grouping-technique one.

**18.** This should closely resemble §31's worked example — a
reasonable minimum is `list` (arrival log) + `dict` (ID lookup) + `set`
(duplicate detection), with `deque` added if FIFO processing is also
required and a stack added if undo is also required, exactly as §40's
mini project demonstrates when all five requirements are present at
once.

**19.** This should closely resemble §33's worked example — `set` for
unique document IDs, `dict` for metadata lookup, `deque` for FIFO
processing, `list` for the final ordered output.

**20.** This should closely resemble §32's worked example — `set` for
deduplication (per-source or globally, depending on whether IDs are
unique across sources or only within one), `dict` for per-source
metadata lookup, and `list` for the final, ordered, processed output.
Alternatives considered and rejected: a single list for everything
(rejected — O(n) lookup and O(n²) naive deduplication, per the Big-O
chapter's §41 mini project); a dictionary alone (rejected — no natural
mechanism for preserving final output order without an accompanying
list).
