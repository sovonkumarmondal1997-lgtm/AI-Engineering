# Comprehensions and Readable Code

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what a comprehension actually is — a concise way to build a
  new collection from an existing iterable — rather than "a shorter
  loop."
- Write and read list, set, and dictionary comprehensions, and
  generator expressions, confidently, including with filtering,
  transformation, conditional expressions, `enumerate()`, `zip()`, and
  tuple unpacking.
- Convert a plain loop into a comprehension, and just as importantly,
  convert a comprehension back into a plain loop when that improves
  clarity.
- Judge — deliberately, not by habit — when a comprehension improves
  readability and when a normal loop, a named helper function, or a
  multi-stage pipeline is the better choice.
- Recognize the specific situations where comprehensions actively hurt
  code quality: side effects, complex error handling, deeply nested
  logic, and overly long expressions.
- Refactor an unreadable comprehension into cleaner code using named
  functions, explicit loops, or staged transformations.
- Reason about a comprehension's memory and performance behavior, tying
  directly back to the Big-O chapter's treatment of time and space.
- Internalize, as a standing principle for all future Python code:
  **readable code is a production feature, and "Pythonic" does not mean
  "clever."**

## 2. Why Comprehensions Exist

Start with the simplest possible case:

```python
numbers = [1, 2, 3, 4]
```

**Goal:** build a new list containing every value doubled.

**The normal loop, first:**

```python
result = []
for number in numbers:
    result.append(number * 2)

print(result)   # [2, 4, 6, 8]
```

**The comprehension, second:**

```python
result = [number * 2 for number in numbers]
print(result)   # [2, 4, 6, 8]
```

These two pieces of code perform **the exact same logical operation** —
same input, same loop, same output. What differs is only the *syntax*
Python offers for expressing it. A **comprehension** is a compact way of
writing exactly this loop shape: *"build a new collection by taking each
item from an existing iterable, optionally transforming it, optionally
keeping only some of them."* This is precisely the shape the previous
chapters have already been using informally — the "filter → map"
comprehension in
[Search, Count, Filter, Map, and Aggregate](01-search-count-filter-map-and-aggregate.md)
§6.3 and §7.3 introduced exactly this syntax; this chapter now teaches
it fully, on its own terms, and — just as importantly — teaches when
*not* to reach for it.

**The comprehension does not change the underlying algorithm.** It is
still one pass over `numbers`, still one multiplication per item, still
one new list built up one element at a time. Comprehensions are a
*syntax* choice, not a different way of computing anything — this is
why understanding the loop version first is not optional busywork; it
is the actual logic the comprehension expresses more tersely.

## 3. Basic List Comprehension Syntax

### 3.1 The structure

```
[expression for item in iterable]
```

Four parts:

1. **output expression** — what to compute and collect for each item
   (`number * 2`)
2. **`for`** — marks the start of the iteration
3. **loop variable** — the name given to each item as it is visited
   (`number`)
4. **iterable** — the existing collection being walked through
   (`numbers`)

### 3.2 More examples, each with its logic named explicitly

```python
numbers = [1, 2, 3]

[x * 2 for x in numbers]     # multiply each item by 2
[x + 10 for x in numbers]    # add 10 to each item
[str(x) for x in numbers]    # convert each item to a string
```

### 3.3 Tracing execution by hand

```python
numbers = [1, 2, 3]
result = [x * 2 for x in numbers]
```

| step | current `x` | `x * 2` | collected so far |
|---|---|---|---|
| 1 | 1 | 2 | `[2]` |
| 2 | 2 | 4 | `[2, 4]` |
| 3 | 3 | 6 | `[2, 4, 6]` |

**Final result:** `[2, 4, 6]`. This trace is identical, step for step,
to tracing the equivalent `for` loop from §2 — the comprehension is not
doing anything the loop was not already doing; it is only spelling it
differently.

## 4. List Comprehensions with Filtering

### 4.1 Adding a condition

```
[expression for item in iterable if condition]
```

```python
numbers = [1, 2, 3, 4, 5, 6]

# Normal loop, first:
result = []
for x in numbers:
    if x > 2:
        result.append(x)

# Comprehension, second:
result = [x for x in numbers if x > 2]
print(result)   # [3, 4, 5, 6]
```

### 4.2 Expression vs. condition — the two different jobs

- The **expression** (`x`, before `for`) decides *what value* gets
  collected for each item.
- The **condition** (`x > 2`, after `if`) decides *whether* an item is
  collected at all.

```python
[x % 2 == 0 for x in numbers]        # EXPRESSION only — collects True/False for every item, nothing filtered
[x for x in numbers if x % 2 == 0]   # CONDITION — only even numbers are kept, unchanged
```

`%` is the **modulo** operator — it returns the *remainder* after
division. `x % 2 == 0` asks "does `x` divide evenly by 2, with nothing
left over?" — which is exactly the definition of an even number. This is
the same operator used without further introduction in the earlier
chapters of this module; it is worth stating explicitly here since this
chapter does not assume prior familiarity with the notation.

## 5. Filtering vs Transformation

This distinction was first established in the previous chapters
(notably §7.1 of
[Search, Count, Filter, Map, and Aggregate](01-search-count-filter-map-and-aggregate.md))
and is restated here specifically in comprehension terms, because
confusing the two inside one comprehension is a common source of bugs.

- **FILTER** — decides *whether* an item stays. It never changes the
  item's value.
- **TRANSFORM** — changes *what* an item becomes. It never removes an
  item.

```python
[x for x in numbers if x > 5]     # FILTER only — values unchanged, some removed
[x * 2 for x in numbers]          # TRANSFORM only — every value changed, none removed
[x * 2 for x in numbers if x > 5]  # BOTH — filter first, then transform what survives
```

**The equivalent explicit loop for the combined case:**

```python
result = []
for x in numbers:
    if x > 5:            # FIRST: decide whether this item passes the filter
        result.append(x * 2)   # THEN: transform only the items that passed
```

The order in the comprehension (`x * 2 for x in numbers if x > 5`) can
look, at first glance, like the transformation happens *before* the
filter — it does not. **Filtering always happens first**: for each item,
the `if` condition is checked against the *original* value; only items
that pass are then transformed by the expression before `for`. This is
directly visible in the loop version above, and is worth deliberately
re-checking whenever a comprehension's behavior seems surprising.

## 6. Conditional Expressions

### 6.1 Two different things that both use the word "if"

This is one of the most commonly confused features in this entire
chapter, so state it plainly, side by side:

```python
# FILTER CONDITION — the "if" decides whether an item is INCLUDED AT ALL.
[x for x in numbers if x > 0]
# → some items are dropped entirely; the ones kept are unchanged

# CONDITIONAL EXPRESSION — the "if/else" decides WHAT VALUE an item BECOMES.
["positive" if x > 0 else "non-positive" for x in numbers]
# → EVERY item is kept; each one becomes one of two possible values
```

### 6.2 The conditional expression's own syntax

```
value_if_true if condition else value_if_false
```

This is a complete expression on its own, usable anywhere a value is
expected — not only inside a comprehension:

```python
number = 4
label = "even" if number % 2 == 0 else "odd"
print(label)   # "even"
```

Inside a comprehension:

```python
numbers = [1, 2, 3, 4]

result = [
    "even" if number % 2 == 0 else "odd"
    for number in numbers
]
print(result)   # ['odd', 'even', 'odd', 'even']
```

### 6.3 Why this is transformation, not filtering

Every single input item produces exactly one output item — nothing is
dropped, only relabeled. This matches the previous chapters' definition
of mapping precisely (previous chapters' repeated emphasis: "map keeps
every item; filter drops some") — a conditional expression is simply a
map whose transformation logic branches into two possible outputs
instead of applying one uniform formula.

**Placement matters, and is the single most common syntax mistake here:**
the conditional expression (`value if condition else value`) goes
*before* the `for` keyword, in the expression position; the filter `if`
(with no accompanying `else`) goes *after* the iterable, at the end.
Mixing these up is a `SyntaxError` waiting to happen, or — worse — code
that runs but does something other than intended.

## 7. Comprehensions with Strings

```python
words = ["Python", "AI", "Data"]

[word.lower() for word in words]                # ['python', 'ai', 'data']
[word for word in words if len(word) > 3]        # ['Python', 'Data']
[word.strip() for word in words]                 # removes leading/trailing whitespace from each
```

Calling a **method** (`.lower()`, `.strip()`) inside the expression
position works exactly like calling it anywhere else in Python — the
comprehension does not know or care that `word.lower()` is a method
call rather than a simple arithmetic expression like `x * 2`. This
directly foreshadows §20's broader point: comprehensions can hold *any*
valid Python expression, including method and function calls, not just
arithmetic. (Full text processing with pattern matching belongs to the
later, dedicated chapter on parsing and regular expressions — these
examples deliberately stay at the level of simple, built-in string
methods.)

## 8. Comprehensions with Dictionaries

Working with a list of **records** (dictionaries), exactly the shape
used throughout the previous three chapters of this module:

```python
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 20},
]

[user["name"] for user in users]                     # ['Alice', 'Bob']
[user for user in users if user["age"] >= 18]          # both users, unchanged (both are 18+)
[user["name"].lower() for user in users]               # ['alice', 'bob']
```

The third example chains a dictionary field access (`user["name"]`)
with a string method (`.lower()`) — this is completely ordinary Python,
just written inside a comprehension's expression position. **A note on
safety:** if some records might be missing the `"name"` key, `user["name"]`
would raise `KeyError` mid-comprehension; the previous chapter's
guidance (`.get("name", default)` when a key might genuinely be
missing) still applies here — this chapter does not repeat that lesson
in depth, only flags that it is directly relevant whenever a
comprehension touches structured records.

## 9. Set Comprehensions

### 9.1 Syntax

```
{expression for item in iterable}
```

```python
words = ["cat", "dog", "bird", "ant", "owl"]
unique_lengths = {len(word) for word in words}
print(unique_lengths)   # {3} — every word here happens to be 3 letters... let's use a better example

words = ["cat", "dog", "elephant", "ant", "owl"]
unique_lengths = {len(word) for word in words}
print(unique_lengths)   # {3, 8}  (order not guaranteed — sets have no defined order)
```

### 9.2 What is different from a list comprehension

- The braces `{}` (instead of `[]`) signal a **set**, not a list.
- **Duplicates disappear** — if two words share the same length, that
  length only appears once in the result, exactly matching the set
  behavior taught in the previous data-structures chapter's §13.
- The result has **no indexing** — `unique_lengths[0]` is invalid;
  a set does not support positional access.

### 9.3 When to reach for a set comprehension

Use one exactly when the previous chapter's §15 criteria for choosing a
set apply: the result needs **uniqueness** (deduplicating transformed
values) or will primarily be used for **membership testing** ("is this
value among the results?"), and neither order nor duplicates matter for
the task at hand.

## 10. Dictionary Comprehensions

### 10.1 Syntax

```
{key_expression: value_expression for item in iterable}
```

```python
numbers = [1, 2, 3, 4]
squares = {number: number * number for number in numbers}
print(squares)   # {1: 1, 2: 4, 3: 9, 4: 16}
```

Every part named: `number` (before the colon) is the **key
expression** — what becomes each entry's key; `number * number` (after
the colon) is the **value expression** — what becomes each entry's
value; `for number in numbers` walks through the source values exactly
as in any other comprehension.

### 10.2 More examples

```python
words = ["cat", "elephant", "dog"]

name_to_length = {
    word: len(word)
    for word in words
}
print(name_to_length)   # {'cat': 3, 'elephant': 8, 'dog': 3}
```

**With a filter:**

```python
long_word_lengths = {
    word: len(word)
    for word in words
    if len(word) > 3
}
print(long_word_lengths)   # {'elephant': 8}
```

Exactly as with list comprehensions (§4), the `if` at the end filters
*which* items produce a key-value pair at all; it does not affect which
pairs' values are computed once an item passes.

## 11. Dictionary Comprehensions from Existing Dictionaries

```python
prices = {
    "apple": 100,
    "banana": 50,
    "orange": 80,
}

expensive = {
    name: price
    for name, price in prices.items()
    if price > 60
}
print(expensive)   # {'apple': 100, 'orange': 80}
```

Piece by piece:

- **`prices.items()`** — produces `(key, value)` tuples for every
  entry, exactly as first taught in the previous chapters (grouping
  chapter's §26).
- **`for name, price in ...`** — **tuple unpacking**: each `(key,
  value)` tuple is split directly into two named variables in one step,
  rather than accessing `pair[0]` and `pair[1]` separately.
- **`name: price`** (before `for`) — the key and value expressions,
  simply passing each surviving entry's original key and value straight
  through.
- **`if price > 60`** — the filter, deciding which entries survive into
  the new dictionary.

This is precisely the "filter a dictionary" pattern already used in the
grouping chapter's §9 (§9 there explicitly warned dictionary
comprehensions are a poor fit for *accumulating* grouped data, but a
good fit for exactly this: reshaping or filtering an *already-complete*
dictionary — this is that good case, worked in full).

## 12. Generator Expressions

### 12.1 Syntax and the core difference

```python
numbers = [1, 2, 3, 4]

[x * 2 for x in numbers]     # LIST COMPREHENSION — builds the whole list immediately
(x * 2 for x in numbers)     # GENERATOR EXPRESSION — produces values one at a time, on demand
```

The only syntactic difference is `[]` versus `()` — but the behavior
differs meaningfully: a list comprehension **creates a list immediately**,
computing and storing every value up front; a generator expression
**produces values lazily**, computing each one only when something
actually asks for the next value, and never materializing the generated
result values into a new collection all at once. This is exactly the distinction the previous
chapters already relied on (grouping chapter §36; Big-O chapter §17) —
this section is where it is formally introduced as its own named
feature.

### 12.2 A generator consumed directly

```python
total = sum(x * 2 for x in numbers)
print(total)   # 20
```

Note the parentheses around the generator expression are not even
doubled here — `sum(x * 2 for x in numbers)` is valid syntax, because a
generator expression passed as a function's *only* argument does not
need its own separate parentheses. `sum()` pulls one value from the
generator, adds it to a running total, and discards it, repeating until
the generator is exhausted — **no intermediate list of doubled values
is ever built.**

### 12.3 Why this saves memory — connecting to Big-O directly

From [Big-O, Time, and Space Complexity](03-big-o-time-and-space-complexity.md)
§17: `sum([x * 2 for x in numbers])` costs O(n) *additional space* (the
full intermediate list), while `sum(x * 2 for x in numbers)` costs
O(1) additional space (only the generator's internal state and the
running total). **Both cost the same O(n) time** — every value is still
computed exactly once either way. Laziness changes *when* values are
computed and *how much is held in memory at once* — it does not make
the underlying computation itself disappear or somehow become free.
This distinction — same time complexity, different space complexity —
is worth restating precisely, because it is easy to over-claim "lazy is
just faster," which is not accurate.

This chapter deliberately does not go further into generators as a
general Python feature (custom generator functions using `yield`,
infinite generators, generator pipelines beyond a single expression) —
that belongs to more advanced, dedicated material; the scope here is
specifically the **generator expression** as a comprehension sibling.

## 13. Comprehensions vs `map()` and `filter()`

Connecting directly to
[Search, Count, Filter, Map, and Aggregate](01-search-count-filter-map-and-aggregate.md)
§6.6 and §7.4, which already introduced this comparison — restated here
with comprehensions as the central topic rather than a side note:

```python
[x * 2 for x in numbers]                    # comprehension
list(map(lambda x: x * 2, numbers))          # map() equivalent

[x for x in numbers if x > 10]               # comprehension
list(filter(lambda x: x > 10, numbers))       # filter() equivalent
```

Both pairs produce identical results. **Readability, not correctness,
is the deciding factor:** the comprehension reads left-to-right as
ordinary English ("x times 2, for each x in numbers"); the `map()`/
`filter()` version requires understanding `lambda` syntax *and*
remembering that the result needs wrapping in `list()` before it can be
inspected or reused as a list. For this reason, **comprehensions are
often easier to read for simple transformations and filtering** — this
is a readability observation, not a claim that `map()`/`filter()` are
"bad" or deprecated.

**When a named function makes `map()`/`filter()` reasonable:**

```python
def is_valid_email(text):
    return "@" in text and "." in text

valid_emails = list(filter(is_valid_email, emails))
```

Here, `filter(is_valid_email, emails)` reads clearly — the function
name documents the intent, and no `lambda` is involved at all. This
mirrors the earlier chapter's own conclusion (§6.6 there): `map()`/
`filter()` are perfectly reasonable once a well-named function replaces
an inline `lambda` — the objection is specifically to `lambda`-heavy
`map()`/`filter()` chains, not to the functions themselves.

## 14. Nested Comprehensions

### 14.1 Flattening a matrix — the introductory example

```python
matrix = [
    [1, 2],
    [3, 4],
]

flattened = [number for row in matrix for number in row]
print(flattened)   # [1, 2, 3, 4]
```

### 14.2 The equivalent nested loop, to understand execution order

```python
flattened = []
for row in matrix:
    for number in row:
        flattened.append(number)
```

**Reading order matters:** in the comprehension, the `for` clauses read
*left to right in the same order they would appear as nested loops* —
`for row in matrix` is the **outer** loop (written first), `for number
in row` is the **inner** loop (written second). This is a genuinely
common point of confusion: the clause order in a comprehension mirrors
normal nested-loop order, not some other convention — always mentally
expand it into the loop form above if the order feels uncertain.

### 14.3 A caution, stated early and directly

**Nested comprehensions are valid Python, but they can become
difficult to understand quickly** — especially once more than two
levels of nesting, multiple conditions, or non-trivial expressions are
involved. This caution is developed fully in §16 and §28; it is flagged
here, at first introduction, so it is never treated as an afterthought.

## 15. Multiple `for` Clauses

### 15.1 Producing every combination — the Cartesian product

```python
numbers = [1, 2, 3]

pairs = [
    (x, y)
    for x in numbers
    for y in numbers
]
print(pairs)
# [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]
```

This is conceptually identical to a nested loop over the *same*
collection twice — every `x` is paired with every `y`, including pairs
like `(1, 1)` where both come from the same position. For `n` items in
`numbers`, this produces `n × n = n²` total pairs.

### 15.2 Connecting to complexity, briefly

Directly from the Big-O chapter's §10: this is a genuinely quadratic
operation — **O(n²)** in both time (n² pairs are generated) and space
(n² pairs are stored, if collected into a list rather than consumed
lazily via a generator expression). This chapter does not re-derive
that reasoning in depth — the previous chapter already did — it is
enough here to recognize that **a comprehension with two `for` clauses
over the same-sized collection is doing nested-loop work, with all the
same complexity consequences**, even though it is written on one line.

## 16. Nested Comprehensions with Conditions

### 16.1 Filtering a nested structure

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6],
]

result = [
    number
    for row in matrix
    for number in row
    if number > 2
]
print(result)   # [3, 4, 5, 6]
```

Step by step: for each `row` in `matrix` (outer), for each `number` in
that `row` (inner), keep `number` only if it is greater than `2`. This
is the flattening pattern from §14, with a filter added at the end,
exactly as filters are added to any single-loop comprehension (§4).

### 16.2 When a valid comprehension is still a bad comprehension

```python
# Valid Python — but genuinely hard to read at a glance:
result = [
    normalize(record["value"])
    for group in raw_groups
    for record in group["records"]
    if record["status"] == "active"
    if record["value"] is not None
    if len(str(record["value"])) > 0
]
```

This compiles and runs correctly, but a reader must hold *three*
separate filter conditions, *two* levels of nesting, and a function call
in their head simultaneously just to know what ends up in `result`.
**Not every valid comprehension is a good comprehension.** The
readable alternative:

```python
def is_usable(record):
    return (
        record["status"] == "active"
        and record["value"] is not None
        and len(str(record["value"])) > 0
    )

result = []
for group in raw_groups:
    for record in group["records"]:
        if is_usable(record):
            result.append(normalize(record["value"]))
```

Naming the condition (`is_usable`) and returning to an explicit nested
loop makes each piece independently readable, and — crucially — the
condition function `is_usable` can now be tested and reasoned about on
its own, separate from the loop that uses it. This exact refactor
pattern is developed into a full, repeatable method in §28.

## 17. `enumerate()` with Comprehensions

```python
names = ["Alice", "Bob", "Charlie"]

indexed_names = [
    (index, name)
    for index, name in enumerate(names)
]
print(indexed_names)   # [(0, 'Alice'), (1, 'Bob'), (2, 'Charlie')]
```

`enumerate(iterable)` pairs each item with its position, producing
`(index, value)` tuples — `for index, name in enumerate(names)` then
unpacks each pair directly into two named variables (§19 develops this
unpacking idea further). `enumerate()` accepts an optional `start`
argument when numbering should not begin at `0`:

```python
list(enumerate(names, start=1))
# [(1, 'Alice'), (2, 'Bob'), (3, 'Charlie')]
```

**Why `enumerate()` beats `range(len(names))` when both index and value
are needed:**

```python
# Works, but requires a second lookup step and is easy to get subtly wrong:
[(i, names[i]) for i in range(len(names))]

# Clearer, and cannot go out of bounds by construction:
[(i, name) for i, name in enumerate(names)]
```

`range(len(names))` produces only positions, forcing a separate
`names[i]` lookup to get each value back — an extra, avoidable step that
also introduces the possibility of an off-by-one indexing mistake.
`enumerate()` produces the position *and* the value together, directly,
in one step — whenever both are genuinely needed, `enumerate()` is the
clearer, more idiomatic choice; when only the value is needed, plain
`for name in names` (no `enumerate()`, no `range()`) is simpler still.

## 18. `zip()` with Comprehensions

```python
names = ["Alice", "Bob"]
scores = [90, 85]

results = [
    (name, score)
    for name, score in zip(names, scores)
]
print(results)   # [('Alice', 90), ('Bob', 85)]
```

`zip(names, scores)` pairs items from both iterables **by position** —
the first item of `names` with the first item of `scores`, the second
with the second, and so on. **Stopping behavior:** if the two iterables
have different lengths, `zip()` stops as soon as the *shorter* one is
exhausted, silently ignoring any extra items in the longer one:

```python
list(zip(["A", "B", "C"], [1, 2]))   # [('A', 1), ('B', 2)]  — "C" is silently dropped
```

This silent truncation is worth remembering explicitly as a potential
source of subtle bugs if the two inputs were expected to be the same
length but, due to an upstream error, are not.

**A dictionary comprehension built from `zip()`:**

```python
scores_by_name = {
    name: score
    for name, score in zip(names, scores)
}
print(scores_by_name)   # {'Alice': 90, 'Bob': 85}
```

This is a genuinely common, practical pattern: pairing two
"parallel" lists (names and their corresponding scores, IDs and their
corresponding records) into a single lookup structure in one readable
line.

## 19. Unpacking in Comprehensions

Tuple unpacking — writing `for key, value in ...` instead of accessing
positions manually — was already covered in an earlier module and used
throughout the previous three Module 04 chapters (grouping chapter's
§4.1, §26). It is not re-taught in depth here; this section only
connects it explicitly to comprehension readability, since it appears
constantly inside them:

```python
for key, value in dictionary.items()   # unpacks each (key, value) pair directly
for name, score in zip(names, scores)   # unpacks each (name, score) pair directly
```

**Why unpacking improves readability, specifically inside
comprehensions:** compare `pair[0]` and `pair[1]` (which say nothing
about *what* those positions mean) against `name` and `score` (which
say everything). Since a comprehension is already a fairly dense single
line of code, giving its intermediate values meaningful names via
unpacking is one of the cheapest, highest-impact readability
improvements available — directly connecting to §24's broader naming
principles.

## 20. Function Calls Inside Comprehensions

```python
def normalize(value):
    return value.strip().lower()

values = ["  Alice ", "BOB", " Charlie  "]
results = [normalize(value) for value in values]
print(results)   # ['alice', 'bob', 'charlie']
```

Calling a function inside a comprehension's expression position is
entirely valid and, in fact, is an important, deliberate production
pattern: **if the transformation logic is complex, the comprehension
itself can remain simple and readable, because the complexity has been
moved into the named function.** The comprehension's job becomes purely
"apply this named operation to every item" — a single, clear idea — while
`normalize()` can be as involved as it needs to be, tested independently
of the comprehension that calls it. This is the same underlying
principle behind §16.2's refactor (`is_usable(record)`), stated here as
a positive pattern rather than only as a fix for an existing problem.

## 21. Side Effects and Comprehensions

### 21.1 What NOT to do

```python
# BAD — using a comprehension purely to trigger printing:
[print(x) for x in numbers]
```

This runs and does print every number — but it also builds and
immediately discards a list of `None` values (since `print()` always
returns `None`), for no reason at all. **This is poor style, not because
it fails, but because it misuses the tool:** a comprehension exists to
*build a result*; here, no result is wanted or used.

### 21.2 The correct alternative

```python
for x in numbers:
    print(x)
```

### 21.3 The rule, stated as strongly as it should be

**Comprehensions are for BUILDING RESULTS. Loops are appropriate for
SIDE EFFECTS** (printing, writing to a file, sending a network request,
appending to some structure defined *outside* the comprehension,
mutating an external object). This distinction should be treated as a
firm rule, not a stylistic suggestion: any comprehension whose "result"
is thrown away, and whose real purpose is something that *happens* on
each iteration, should be rewritten as a plain `for` loop.

## 22. Exception Handling and Comprehensions

### 22.1 The problem

Comprehensions do not provide a clean place to write a `try`/`except`
block — a `try` statement is not a valid expression, so it cannot simply
be dropped inside `[expression for item in iterable]`. A workaround
exists, but it is instructive to see why it is a poor one:

```python
# Technically possible, but cramped and hard to read:
results = [
    transform(value) if is_safe(value) else None
    for value in values
]
```

This *avoids* exceptions by pre-checking safety, but it cannot express
"try the transformation, and if it specifically raises `ValueError`, do
something different" — that requires an actual `try`/`except`, which a
comprehension has no room for.

### 22.2 The readable normal-loop approach

```python
results = []
for value in values:
    try:
        results.append(transform(value))
    except ValueError:
        pass   # or: log the error, append a default, etc.
```

**Why a loop is often better when error handling is part of the
logic:** the loop gives each step — the transformation attempt, the
specific exception being caught, and what happens when it is caught —
its own clear, separately readable line. Cramming this into a
comprehension would require either abandoning proper exception handling
entirely (as the workaround above does) or abandoning the comprehension
form. **When exception handling is a real part of an operation's logic,
prefer the explicit loop from the start**, rather than searching for a
clever way to force it into a comprehension.

## 23. Mutation and Comprehensions

A comprehension always **creates a new collection** — this is worth
stating explicitly, because it is easy to conflate with a different,
riskier pattern: **mutating objects that already exist**, from inside a
comprehension.

```python
records = [{"count": 0}, {"count": 0}]

# Risky — this "comprehension" exists ONLY for its side effect
# (mutating each dictionary in place); the resulting list of Nones is discarded:
[record.update(count=record["count"] + 1) for record in records]
```

This works, in the sense that `records` does end up mutated — but it is
exactly the side-effect misuse from §21, made worse because the mutation
is *hidden* inside what looks like it should be building a new,
independent result. A reader skimming `[record.update(...) for record in
records]` reasonably expects a new list of *something* — not a
side-effecting mutation of the original data.

```python
# Clear about what is happening, and about its consequence:
for record in records:
    record["count"] += 1
```

**The general warning:** be deliberate about the difference between
*building a new collection* (a comprehension's actual purpose) and
*mutating existing mutable objects* (a loop's job, stated plainly). A
comprehension that quietly mutates its inputs while appearing to build
something new is a maintenance hazard — the next reader (including a
future you) will likely assume it is side-effect-free, because
comprehensions almost always are, and that assumption is exactly what
this pattern violates.

## 24. Readable Variable Names

Having covered comprehension *mechanics* thoroughly, the chapter now
turns to the second, equally important half of its purpose: writing
readable Python generally, starting with naming.

```python
# Poor:
[x for x in xs if x > 10]

# Better:
[score for score in scores if score > 10]
```

Both lines are syntactically and behaviorally identical — the only
difference is naming, and yet the second is immediately more meaningful:
a reader instantly knows this is about *scores*, not an anonymous `x`.
Guidelines:

- Use **nouns for data** (`scores`, `users`, `transaction`) and **verbs
  for actions/functions** (`normalize`, `is_valid`, `calculate_total`).
- **Avoid unnecessary abbreviations** — `usr` saves four characters and
  costs a reader a moment of decoding, every single time they read it.
- **Avoid cryptic single-letter names**, except for very short, purely
  mechanical loop variables where the context makes the meaning
  obvious (e.g., `i` for a simple numeric index in a two-line loop) —
  even then, a descriptive name is rarely worse.
- **Use domain language** — if the business calls it a "customer," name
  the variable `customer`, not `record` or `item`, whenever the more
  specific term is available and accurate.

```python
# Prefer:
customer_id, total_amount, transactions

# Over, when the context is not immediately obvious:
c, t, ts
```

Meaningful names matter *especially* inside comprehensions, precisely
because comprehensions are already dense — a comprehension with poor
names compounds two sources of difficulty (dense syntax, unclear
intent) at once; a comprehension with excellent names can remain
readable even as its logic grows slightly more involved.

## 25. Readability vs Brevity

```python
# A short one-liner:
result = [f(x) for x in data if g(x)]

# A slightly longer but obvious loop:
result = []
for item in data:
    if is_within_range(item):
        result.append(transform(item))
```

If `f` and `g` are genuinely opaque (as written above, deliberately, to
make the point), the "shorter" version is *not* actually clearer — it
merely hides its lack of clarity behind fewer characters. **The
shortest code is not necessarily the clearest code.**

**Where the comprehension genuinely wins:**

```python
active_user_names = [user["name"] for user in users if user["active"]]
```

Here, the comprehension is both short *and* immediately clear — every
part is self-explanatory, and expanding it into a four-line loop would
add length without adding any clarity. **Where the loop genuinely
wins:**

```python
# Comprehension form — technically valid, already straining:
result = [
    process(item)
    for item in items
    if item.status == "ready" and item.owner in allowed_owners and not item.archived
]

# Loop form — each condition and step gets its own line, easy to scan:
result = []
for item in items:
    if item.status != "ready":
        continue
    if item.owner not in allowed_owners:
        continue
    if item.archived:
        continue
    result.append(process(item))
```

Both examples above will be revisited directly in §28's refactoring
workshop — the principle to take away here is simply: **judge each
case on its own readability, not on a fixed preference for either
form.**

## 26. When to Use Comprehensions

Use a comprehension when:

- You are **transforming** a collection (§7, §8, §20).
- You are **filtering** a collection (§4).
- You are **building a simple new collection** — list, set, or
  dictionary — from an existing iterable.
- The logic is **short** and **easy to understand at a glance** — a
  reader should not need to pause and mentally trace execution.
- There are **no significant side effects** (§21) — the comprehension's
  entire purpose is the collection it produces.

```python
[x * 2 for x in numbers]           # simple transformation
[x for x in numbers if x > 10]      # simple filter
{user["id"]: user for user in users}   # simple dictionary build from records
```

## 27. When Not to Use Comprehensions

Do **not** use a comprehension when:

- The logic requires **multiple independent steps** that do not
  collapse naturally into one expression.
- **Nested logic** becomes confusing to read in one line (§16.2).
- **Exception handling** is needed as part of the logic (§22).
- **Side effects dominate** the purpose of the code (§21).
- **Debugging individual steps matters** — a comprehension gives you no
  natural place to inspect an intermediate value mid-iteration (§34
  develops this into a full debugging strategy).
- **Multiple conditions** become difficult to read together (§5's
  earlier warning, restated here as a firm rule).
- The **expression becomes very long** — if it no longer fits
  comfortably, readably, on screen.
- **Business logic becomes hidden** inside a dense expression rather
  than expressed with a clear name (§16.2, §20, §28).

```python
# Prefer an explicit loop or named function whenever any of the above apply —
# concrete before/after examples are worked in full in §28.
```

## 28. Refactoring Unreadable Comprehensions

### 28.1 Starting from intentionally bad code

```python
result = [
    transform(x)
    for x in data
    if complicated_condition(x)
    and another_condition(x)
    and yet_another_condition(x)
]
```

Even with a helpful function name (`transform`), stacking three `and`-
joined conditions inline makes the *filter* logic itself hard to audit
at a glance — a reader must hold all three conditions in mind
simultaneously just to know what data reaches `transform` at all.

### 28.2 Option 1 — a named helper function for the condition

```python
def is_eligible(x):
    return (
        complicated_condition(x)
        and another_condition(x)
        and yet_another_condition(x)
    )

result = [transform(x) for x in data if is_eligible(x)]
```

The comprehension is now trivially readable; `is_eligible` carries the
complexity, with a name that documents its own purpose, and can be
tested in isolation.

### 28.3 Option 2 — an explicit loop

```python
result = []
for x in data:
    if is_eligible(x):
        result.append(transform(x))
```

Equivalent to Option 1's comprehension, but with each step (filter,
then transform, then collect) on its own visible line — preferable when
even more steps, or debugging visibility (§34), are anticipated.

### 28.4 Option 3 — breaking processing into stages

```python
eligible_items = [x for x in data if is_eligible(x)]
result = [transform(x) for x in eligible_items]
```

Two small, individually simple comprehensions, each doing exactly one
job — this is a preview of §29's multi-stage pattern, and is often the
most readable option of all once both the filter *and* the
transformation are individually non-trivial.

### 28.5 The core lesson

**COMPLEXITY SHOULD BE NAMED.** A function name (`is_eligible`,
`transform`) communicates intent far better than an equivalent inline
expression ever can, no matter how carefully that expression is
formatted. Whenever a comprehension's readability is in question, the
first, most broadly useful fix is almost always: **extract the
complicated part into a well-named function**, and let the
comprehension simply call it.

## 29. Multi-Stage Data Transformation

### 29.1 One giant expression vs. staged transformation

```python
# One giant, nested expression:
result = [normalize(record) for record in records if is_valid(record)]
```

This particular example is still perfectly readable — it is shown here
specifically as the *baseline* to contrast against a genuinely more
complex pipeline:

```python
raw_data → filter → transform → aggregate
```

```python
valid_records = [
    record
    for record in records
    if is_valid(record)
]

normalized_records = [
    normalize(record)
    for record in valid_records
]

total = sum(record["amount"] for record in normalized_records)
```

### 29.2 Why staging can be more readable

Each named intermediate variable (`valid_records`, `normalized_records`)
documents *what stage of processing the data has reached* — a reader
scanning this code does not need to mentally simulate a single, dense,
combined expression; they can read top to bottom, trusting each named
variable's own name to describe its content. This also makes each stage
**independently debuggable** — you can inspect `valid_records` directly,
in isolation, to confirm filtering worked correctly, before ever looking
at normalization.

### 29.3 The trade-off, stated honestly

**More intermediate memory, in exchange for better readability and
debuggability.** Each staged list (`valid_records`, `normalized_records`)
is a full O(n) intermediate collection (Big-O chapter's §16), whereas a
single combined generator expression, feeding directly into `sum()`,
could do the same work with O(1) additional space (§12.3 of this
chapter). **This is a genuine trade-off, not a free improvement** — for
a small or moderate dataset processed occasionally, the readability gain
from staging is almost always worth the modest extra memory; for a
very large dataset processed as a tight, hot-path pipeline, the memory
cost of multiple full intermediate lists may become worth optimizing
away, once profiling (Big-O chapter's §38) actually confirms it matters.
In data engineering specifically, staged pipelines like this are the
normal, expected shape of real ETL code — clarity and debuggability
across each transformation step typically outweigh the cost of a few
intermediate lists, unless the data volume specifically demands
otherwise.

## 30. Memory and Performance

Connecting directly, and precisely, to
[Big-O, Time, and Space Complexity](03-big-o-time-and-space-complexity.md):

```python
[x * 2 for x in numbers]   # LIST COMPREHENSION
```
- **Time: O(n)** — one multiplication per item.
- **Additional space: O(n)** — the new list holds one entry per input
  item.

```python
(x * 2 for x in numbers)   # GENERATOR EXPRESSION
```
- **Time: O(n) when fully consumed** — exactly the same total work is
  eventually done, one item at a time.
- **Additional iteration space: typically O(1)**, excluding whatever
  the generator's *consumer* itself decides to store (if you build a
  list from the generator, e.g., `list(x * 2 for x in numbers)`, that
  final list is still O(n) — the O(1) claim is specifically about the
  generator machinery itself (the input iterable, e.g. an existing
  `numbers` list, may already be in memory), not about however its output is
  ultimately used).

**The precise, important point:** lazy evaluation does not make the
total computation disappear — it changes *when* values are computed
(on demand, rather than all at once) and *how much is materialized in
memory at any single moment* (one value at a time, rather than the
whole collection). If every value produced by a generator eventually
gets stored somewhere else in full, the total memory used over the
program's life is comparable either way — the savings come specifically
from avoiding a *redundant intermediate* list that nothing actually
needed to keep around, exactly as shown in the "filter → aggregate"
generator pattern first introduced in the earlier chapters (search/
count/filter/map/aggregate chapter's §8.7 and §11.2).

## 31. Comprehension Performance vs Loops

**Do not make the false claim "comprehensions are always faster."**
List comprehensions can be efficient — and in CPython specifically, they
often have somewhat lower overhead than an equivalent `for` loop with
explicit `.append()` calls, because of implementation details in how
each is executed — but this is *not* a Big-O difference: both represent
the same fundamental algorithmic work, one pass over `n` items, O(n)
time either way (per §30, and the Big-O chapter's §31–§32 caution about
conflating implementation speed with asymptotic complexity).

**What actually determines real-world speed** is a mix of factors this
chapter has already flagged individually:

- the specific **operation performed** per item (a cheap arithmetic op
  vs. an expensive function call)
- whether a **function call** happens on every iteration, and how
  expensive that function is
- the **data size** — the same code can behave very differently at
  `n = 10` versus `n = 10,000,000`
- **Python implementation details** — specifics of how comprehensions
  and loops are executed internally, which can change between Python
  versions
- **memory behavior** — whether intermediate collections are being
  built unnecessarily (§29's trade-off, §30)

**The correct order of priorities, restated directly from the Big-O
chapter's own engineering decision framework (§44 there):**

```
CORRECTNESS → READABILITY → REASONABLE PERFORMANCE → MEASURE BEFORE OPTIMIZING
```

Choosing between a comprehension and a loop should almost always be
decided by **readability first** — performance differences between the
two forms are, for the vast majority of real code, negligible compared
to the cost of getting the *algorithm* wrong (e.g., accidentally O(n²)
when O(n) was achievable — a data-structure or algorithm problem, not a
comprehension-vs-loop problem). Reach for `timeit`/`cProfile` (Big-O
chapter's §38) only once an actual, measured bottleneck is suspected —
never choose a less readable form purely on the unverified assumption
that it "should" be faster.

## 32. Common Python Functions Used with Comprehensions

Every function below is introduced specifically in terms of how it
interacts with comprehensions and readability — not as a generic
built-in reference.

```python
[x for x in range(10)]
```
`range(10)` represents the values `0` through `9` without materializing
them as a list up front, making it an efficient iterable for numeric
iteration (it is a `range` object, not a generator expression).

```python
[name for name in names if len(name) > 3]
```
`len()` inside a filter condition — a direct callback to the previous
chapters' repeated use of `len()` for size-based conditions.

```python
[(i, value) for i, value in enumerate(values)]
```
`enumerate()` — fully covered in §17; shown again here as part of this
consolidated reference.

```python
[a + b for a, b in zip(first, second)]
```
`zip()` — fully covered in §18; combining two parallel sequences
element-wise inside a comprehension is one of its most common uses.

```python
sorted([x for x in numbers if x > 0])
sorted(x for x in numbers if x > 0)   # equally valid — sorted() accepts any iterable, including a generator
```
`sorted()` — from the grouping chapter's §17–§18 — accepts the *result*
of a comprehension (or a generator expression directly, without the
list even being built first) and returns a new, ordered list.

```python
list(reversed([1, 2, 3]))
```
`reversed()` — produces items in reverse order; often combined with a
comprehension when the *reversed* order is itself the thing being
transformed or filtered.

```python
sum(x for x in numbers if x > 0)
min(x for x in numbers if x > 0)
max(x for x in numbers if x > 0)
```
`sum()`, `min()`, `max()` — from the aggregate chapter's §8 — each
naturally consumes a generator expression directly, exactly the
"filter → aggregate in one pass, O(1) extra space" pattern from §30 of
this chapter.

```python
any(x > 100 for x in numbers)
all(x > 0 for x in numbers)
```
`any()`, `all()` — from the search chapter's §4.9–§4.10 — both stop
early (the Big-O chapter's §8) and are almost always written with a
generator expression rather than a pre-built list, since nothing
downstream needs the intermediate values kept around.

```python
list(map(lambda x: x * 2, numbers))
list(filter(lambda x: x > 10, numbers))
```
`map()`, `filter()` — directly compared against comprehensions in §13.

```python
{user["id"]: user for user in users}.items()
{user["id"]: user for user in users}.keys()
{user["id"]: user for user in users}.values()
```
`dict.items()`, `dict.keys()`, `dict.values()` — from §11, used
whenever a comprehension needs to iterate over an *existing*
dictionary's contents rather than build a new one from scratch.

```python
{x for x in numbers}       # set comprehension
set(x for x in numbers)     # equivalent, using the set() constructor directly on a generator
```
`set()` — the constructor form is equivalent to a set comprehension for
this simple case; the comprehension form becomes clearer once a real
transformation (not just `x` unchanged) is involved.

## 33. Common Beginner Mistakes

1. **Confusing expression and condition.** Writing the filter condition
   where the expression belongs, or vice versa — always confirm: *before*
   `for` is what gets collected; *after* `if` (with no `else`) is what
   decides whether it is collected at all (§4.2).

2. **Placing `if`/`else` in the wrong location.**
   ```python
   # WRONG — a filter-style if cannot have an else at the end like this:
   [x for x in numbers if x > 0 else 0]   # SyntaxError!
   ```
   → **Correct:** a conditional expression's `if/else` goes *before*
   `for`, in the expression position (§6): `[x if x > 0 else 0 for x in
   numbers]`.

3. **Forgetting brackets** — writing `x * 2 for x in numbers` on its own
   (no `[]`, `{}`, or enclosing call) produces a `SyntaxError` outside of
   a function call context; always wrap the intended structure
   explicitly.

4. **Creating a set when a list was required**, or vice versa —
   `{x for x in numbers}` (a set) versus `[x for x in numbers]` (a
   list) look nearly identical; picking the wrong brackets silently
   changes both ordering and duplicate-handling behavior (§9).

5. **Accidentally creating a dictionary** when a set was intended, by
   mistyping a colon:
   ```python
   {x: None for x in numbers}   # a DICT, every value None — probably not what was wanted
   {x for x in numbers}          # a SET — probably what was actually wanted
   ```

6. **Misunderstanding generator expressions** — treating `(x for x in
   numbers)` as if it immediately produced a usable sequence, then being
   surprised that indexing it (`gen[0]`) fails, or that iterating over it
   *twice* silently produces nothing the second time (a generator is
   exhausted after one full pass).

7. **Using nested comprehensions too early**, before the single-level
   form is fully comfortable — leading to code the author themselves
   cannot confidently trace (§14, §16).

8. **Using a comprehension for side effects** — §21's central warning,
   restated here as a named mistake: `[print(x) for x in numbers]`
   instead of a plain loop.

9. **Using cryptic variable names** inside comprehensions specifically —
   `[x for x in xs if x > 10]` instead of `[score for score in scores if
   score > 10]` (§24).

10. **Creating extremely long one-liners** that no longer fit
    comfortably on screen, forcing horizontal scrolling or awkward line
    breaks in the middle of a condition.

11. **Putting too much business logic inside the expression itself**,
    rather than naming it via a helper function (§20, §28).

12. **Accidentally creating nested lists**, from an extra pair of
    brackets:
    ```python
    result = [[x for x in numbers]]   # a list containing ONE list, not a flat list!
    ```

13. **Forgetting that generators are lazy** — building a generator
    expression and expecting side effects or errors inside it to occur
    immediately, when in fact nothing happens until the generator is
    actually iterated.

14. **Confusing `map()`/`filter()` behavior** — forgetting they return
    iterators (not lists), and either trying to index them directly or
    forgetting to wrap them in `list()` when a list is actually needed
    (search/count/filter/map/aggregate chapter's §15, mistake #16).

15. **Using `range(len(...))` unnecessarily** when `enumerate()` (or
    plain iteration) would be clearer — §17's direct comparison.

16. **Modifying objects unexpectedly** inside what looks like a
    result-building comprehension, when the real effect is a hidden
    mutation of the original data (§23).

## 34. Debugging Comprehensions

A repeatable, six-step strategy for a comprehension that is producing
the wrong result or is simply hard to reason about:

1. **Expand it into a normal loop.** Write out the exact loop the
   comprehension represents (as every section of this chapter has
   done alongside each comprehension form) — this alone often reveals
   the bug immediately.
2. **Give intermediate values names.** If the comprehension involves
   more than one meaningful step (a filter *and* a transformation, or a
   nested loop), assign each step's result to its own clearly named
   variable in the expanded loop.
3. **Print or inspect intermediate results.** Add a `print()` inside
   the expanded loop to see exactly what each iteration produces —
   directly reusing the tracing technique already taught in the
   previous chapters (grouping chapter's §37).
4. **Test the condition separately.** If a filter's correctness is in
   doubt, call it directly against a few sample values outside the
   loop entirely: `is_eligible(sample_record)`.
5. **Test the transformation separately.** Likewise, call the
   transformation function directly against a sample value:
   `normalize(sample_value)`.
6. **Rebuild the comprehension only if readability remains good.** Once
   the bug is found and fixed in the loop form, decide — deliberately,
   using §26–§27's criteria — whether to convert back into a
   comprehension, or simply keep the now-working, now-well-understood
   loop.

```
comprehension → expanded loop → debug → (optionally) refactor back
```

Make this a genuine habit: reaching immediately for step 1 the moment a
comprehension's behavior is unclear, rather than staring at the dense
one-liner trying to trace it mentally, saves real debugging time and
avoids introducing further mistakes while guessing at a fix.

## 35. Testing Comprehensions

Since a comprehension is "just" a loop, it should be tested against the
same edge cases the earlier chapters have already established as
standard (search/count/filter/map/aggregate chapter's §16 and §20;
grouping chapter's §33):

```python
def double_positive(numbers):
    return [n * 2 for n in numbers if n > 0]


def test_double_positive():
    assert double_positive([]) == []                    # empty input
    assert double_positive([5]) == [10]                    # one item
    assert double_positive([1, 2, 3]) == [2, 4, 6]           # all items match
    assert double_positive([-1, -2]) == []                  # no items match
    assert double_positive([2, 2, 2]) == [4, 4, 4]           # duplicate values
```

```python
def names_from_records(records):
    return [r["name"] for r in records if r.get("name") is not None]


def test_names_from_records():
    assert names_from_records([]) == []
    assert names_from_records([{"name": "Ada"}]) == ["Ada"]
    assert names_from_records([{"name": None}, {"name": "Ada"}]) == ["Ada"]   # None handled
    assert names_from_records([{}]) == []                                       # missing key handled via .get()
```

```python
def flatten(matrix):
    return [n for row in matrix for n in row]


def test_flatten():
    assert flatten([]) == []
    assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]     # nested data
    assert flatten([[], [1]]) == [1]                        # empty inner list handled
```

This is not a general testing tutorial (that belongs to a later,
dedicated module) — the point here is only that comprehension-based
functions deserve exactly the same systematic edge-case coverage as any
other function, no more and no less.

## 36. Real-World Data Engineering Examples

```python
transactions = [
    {"id": "T1", "amount": 100, "status": "completed"},
    {"id": "T2", "amount": -50, "status": "failed"},
    {"id": "T3", "amount": 200, "status": "completed"},
]
```

**1. Transaction preprocessing — extract transaction IDs.**
```python
transaction_ids = [transaction["id"] for transaction in transactions]
```

**2. Log normalization — filter successful transactions.**
```python
completed = [
    transaction
    for transaction in transactions
    if transaction["status"] == "completed"
]
```

**3. Customer data cleaning — normalize text fields.**
```python
documents = [{"text": "  Hello World  "}, {"text": "PYTHON rocks"}]
normalized_text = [
    document["text"].strip().lower()
    for document in documents
]
```

**4. Feature preparation — a set of unique categories.**
```python
records = [{"category": "food"}, {"category": "travel"}, {"category": "food"}]
unique_categories = {record["category"] for record in records}
```

**5. Document preprocessing — a dictionary of ID to word count.**
```python
docs = [{"id": "D1", "text": "hello world"}, {"id": "D2", "text": "python is great"}]
word_counts = {doc["id"]: len(doc["text"].split()) for doc in docs}
```

**Why these are readable and useful:** every example above is a single,
simple transformation or filter — exactly the case §26 recommends a
comprehension for — and each one reads, left to right, as a direct
restatement of its own comment. None of them hide business logic behind
an opaque expression, and none of them exceed two or three lines.

## 37. Real-World AI/ML Examples

All examples remain standard Python — no `pandas`, `numpy`, or ML
frameworks — because the goal here is Python reasoning, not a specific
library's API.

**Extracting text from documents:**
```python
documents = [{"id": "D1", "text": "Hello"}, {"id": "D2", "text": "World"}]
texts = [doc["text"] for doc in documents]
```

**Filtering invalid records:**
```python
examples = [{"text": "great!"}, {"text": ""}, {"text": "  "}]
valid_examples = [ex for ex in examples if ex["text"].strip()]
```

**Normalizing strings before tokenization:**
```python
normalized = [ex["text"].strip().lower() for ex in valid_examples]
```

**Extracting labels:**
```python
labeled_examples = [{"text": "great", "label": "positive"}, {"text": "bad", "label": "negative"}]
labels = [ex["label"] for ex in labeled_examples]
```

**Building a metadata mapping (ID → source):**
```python
docs = [{"id": "D1", "source": "web"}, {"id": "D2", "source": "pdf"}]
metadata_by_id = {doc["id"]: doc["source"] for doc in docs}
```

**Preparing batches, conceptually** (grouping already-cleaned examples
into fixed-size chunks, using plain Python — no framework-specific
batching API):
```python
def chunk(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]

batches = chunk(normalized, size=2)
```

Each example connects directly back to a pattern already established
earlier in this chapter: extraction is mapping (§8), filtering invalid
records is a filter condition (§4), normalization is a function call
inside a comprehension (§20), and the metadata mapping is a dictionary
comprehension built from records (§10).

## 38. Readability Heuristics

A concise set of practical rules, meant to be applied quickly, in
order, whenever "comprehension or loop?" is in question:

1. **One simple transformation** → a comprehension is often good.
2. **One simple filter** → a comprehension is often good.
3. **Transformation + simple filter** → often still good.
4. **Multiple nested loops** → reconsider (§14–§16).
5. **Complex branching** → use a loop or a named function.
6. **Side effects** → use a loop (§21).
7. **Complex exception handling** → use a loop (§22).
8. **If another engineer must mentally decode the expression** →
   simplify it.
9. **Name complicated logic with a function** (§20, §28).
10. **Optimize for maintainability, not line count** — this is the
    single rule every other rule in this list ultimately serves.

## 39. PEP 8 / Style / Formatting

Only the style principles most directly relevant to readable
comprehensions and general Python code are covered here — this is not
a full style-guide chapter (that groundwork belongs to Stage 0).

**Indentation and line length** — when a comprehension no longer fits
comfortably on one line, break it across multiple lines, aligning each
clause:

```python
# Cramped:
result = [transform(record) for record in records if is_valid(record) and record["amount"] > 0]

# Readable, one clause per line:
result = [
    transform(record)
    for record in records
    if is_valid(record) and record["amount"] > 0
]
```

**Parentheses/brackets for multiline expressions** — Python allows a
line break inside any unclosed `[`, `{`, `(` without a backslash
continuation; use this to your advantage for any comprehension spanning
more than one line, exactly as every multiline example in this chapter
has done.

**Whitespace and blank lines** — a single space after commas and around
operators (`x + 10`, not `x+10`); a blank line separating logically
distinct comprehensions or stages of a pipeline (§29), so the eye can
find each stage's boundary quickly.

**Meaningful names** — restating §24 as a formatting-adjacent concern,
because naming and formatting together determine how quickly a reader's
eye can parse a line.

**Avoiding unnecessary semicolons** — Python does not require semicolons
to end statements; using them to cram multiple statements onto one line
(`x = 1; y = 2`) actively hurts readability and has no benefit.

**Avoiding overly dense expressions** — a direct callback to §25 and
§27: if a single line requires slowing down and re-reading to parse,
that is a formatting and structure signal, not a personal failing on
the reader's part — restructure the code.

## 40. Type Hints and Readability

```python
def normalize_names(names: list[str]) -> list[str]:
    return [name.strip().lower() for name in names]
```

`names: list[str]` documents that the function expects a list of
strings; `-> list[str]` documents that it returns a list of strings.
Neither annotation changes what the function *does* — Python does not
enforce these hints at runtime — but they make the function's **interface**
immediately clear to a reader (or to an editor's autocomplete), without
needing to read the function body at all. This is a small, low-cost
readability improvement, especially valuable once a comprehension is
tucked inside a function whose name alone does not fully convey its
input/output shape. This chapter does not go further into the type
system (generics, `Optional`, complex nested hints) — that is a
dedicated typing topic in its own right; the point here is narrowly
that type hints are one more tool in service of the same overall goal
this chapter has pursued throughout: **making code easier for the next
reader to understand quickly and correctly.**

## 41. Refactoring Workshop

For each: **Original code → Decision → Reason → Improved version.**
Not every example below concludes "use a comprehension" — that is
deliberate; the point is to practice judgment, per §26–§27.

**1. Simple transformation.**
```python
result = [x * 3 for x in values]
```
Decision: **KEEP.** Reason: single, obvious transformation, no
conditions, no side effects — exactly §26's first rule.

**2. Filtering.**
```python
result = [x for x in values if x >= 0]
```
Decision: **KEEP.** Reason: single, simple filter condition.

**3. Nested data, simple case.**
```python
result = [n for row in matrix for n in row]
```
Decision: **KEEP.** Reason: a clean, standard flattening idiom (§14),
still easily traced.

**4. Complex condition.**
```python
result = [x for x in values if x > 0 and x < 100 and x % 3 == 0 and str(x) not in excluded]
```
Decision: **REWRITE**, extracting the condition.
```python
def is_wanted(x, excluded):
    return 0 < x < 100 and x % 3 == 0 and str(x) not in excluded

result = [x for x in values if is_wanted(x, excluded)]
```
Reason: four conditions chained with `and` exceed §5's readability
threshold; naming the condition restores clarity (§28).

**5. Side effect.**
```python
[log.write(f"{x}\n") for x in values]
```
Decision: **REWRITE as a loop.**
```python
for x in values:
    log.write(f"{x}\n")
```
Reason: this is a side effect, not a result-building operation — §21's
firm rule applies directly.

**6. Exception handling.**
```python
result = [int(x) if x.isdigit() else None for x in raw_values]
```
Decision: **KEEP for this simple case, but watch for growth.** Reason:
`isdigit()` cleanly avoids ever needing a `try`/`except` here — this is
a legitimate conditional expression (§6), not a workaround; if the
validation logic grows more nuanced (e.g., needing to catch a specific
parsing exception with custom handling), rewrite as a loop per §22.

**7. Multiple transformations.**
```python
result = [str(round(x * 1.08, 2)) for x in prices]
```
Decision: **KEEP, but consider naming if it grows.** Reason: three
chained operations (multiply, round, convert to string) are still
readable as one line for now; if a fourth step were added, extracting a
named `apply_tax_and_format(price)` function (§20) would be the next
step.

**8. Dictionary creation.**
```python
result = {user["id"]: user["email"] for user in users if user["email"]}
```
Decision: **KEEP.** Reason: a clean, standard "filter + build lookup"
pattern (§10–§11), fully self-explanatory.

**9. Set creation.**
```python
result = {tuple(sorted(pair)) for pair in raw_pairs}
```
Decision: **KEEP, with a short comment if the intent (deduplicating
unordered pairs) is not obvious from context.** Reason: this is a
legitimate, if slightly clever, use of a set comprehension for
deduplication — the previous chapter's guidance on comments (write one
only when the *why* is non-obvious) applies directly here, since
`tuple(sorted(pair))` is doing meaningful, non-obvious work (normalizing
`(1, 2)` and `(2, 1)` to compare as equal).

**10. Generator pipeline.**
```python
total = sum(record["amount"] for record in records if record["status"] == "completed")
```
Decision: **KEEP.** Reason: a single-pass filter-then-aggregate
generator expression, exactly §30's recommended, memory-efficient
pattern — rewriting this as a loop would add lines without adding
clarity.

## 42. Progressive Exercises

Solutions and full reasoning appear in **§48 — Answer Key / Solutions**.

### Level 1 — Beginner

**1.** Double every number in `[3, 6, 9]` using a list comprehension.

**2.** Extract the even numbers from `[1, 2, 3, 4, 5, 6]`.

**3.** Convert every string in `["HELLO", "World", "PYTHON"]` to
lowercase.

**4.** Calculate the length of every string in `["cat", "elephant",
"dog"]`.

**5.** Build a set of unique string lengths from `["cat", "dog", "owl",
"elephant"]`.

### Level 2 — Intermediate

**6.** Given `users = [{"name": "A", "active": True}, {"name": "B",
"active": False}]`, filter to only active users.

**7.** From the same `users`, extract just the names.

**8.** Build a dictionary mapping names to ages from `[{"name": "A",
"age": 30}, {"name": "B", "age": 20}]`.

**9.** Given `names = ["A", "B"]` and `scores = [90, 80]`, pair them
into a list of tuples using `zip()`.

**10.** Given `items = ["x", "y", "z"]`, produce a list of `(index,
item)` pairs using `enumerate()`, starting the index at `1`.

### Level 3 — Advanced

**11.** Flatten `matrix = [[1, 2], [3, 4], [5]]` into a single flat
list.

**12.** Given nested records `groups = [{"items": [1, -2, 3]}, {"items":
[-4, 5]}]`, extract only the positive values across all groups.

**13.** Build a dictionary mapping transaction ID to amount from
`transactions = [{"id": "T1", "amount": 100}, {"id": "T2", "amount":
200}]`.

**14.** Given `numbers = [1, 2, 3, 4, 5]`, use a generator expression
inside `sum()` to calculate the total of only the even numbers, without
building an intermediate list.

**15.** Refactor the following into readable code (your choice of
technique), and explain why your version is better:
```python
result = [f(x) for x in data if g(x) and h(x) and not k(x)]
```

### Level 4 — Production-Oriented

**16.** Given a list of transaction records with `"description"`
fields possibly containing extra whitespace and mixed case, normalize
every description (strip and lowercase).

**17.** Given a list of log event dictionaries, some with a `"level"`
of `"DEBUG"`, filter those out, keeping only non-debug events.

**18.** Given a list of document records with `"id"` and `"author"`
fields, build a dictionary mapping document ID to author.

**19.** Given a list of processed document records, build a set of all
distinct `"category"` values present.

**20.** Design a small, readable, multi-stage pipeline (per §29) that:
filters valid records, normalizes a text field, and calculates a total
from a numeric field — and explain, in a sentence, why you chose
staged comprehensions over one large combined expression (or vice
versa).

## 43. Mini Project — Readable Transaction Data Transformation Pipeline

### Requirements

Given a list of transaction dictionaries with fields `transaction_id`,
`customer_id`, `amount`, `status`, `category`, and `description`, build
a pipeline that:

1. Extracts transaction IDs.
2. Filters to completed transactions.
3. Normalizes descriptions (strip, lowercase).
4. Builds a customer → transaction-count mapping.
5. Builds a set of unique categories.
6. Produces a generator for positive transaction amounts.
7. Calculates the total positive amount.
8. Sorts selected results where appropriate.
9. Identifies any unreadable/overcomplicated comprehension in the draft
   and refactors it into a loop or helper function.
10. Keeps the final implementation readable and maintainable throughout.

### Before implementing, document:

- **Problem** — turn a raw transaction feed into several small, clean,
  independently useful summaries, while keeping every transformation
  step individually readable.
- **Inputs** — a list of transaction dictionaries.
- **Outputs** — a list of IDs; a list of completed transactions; a list
  of normalized descriptions; a customer-count dictionary; a set of
  categories; a total positive amount; a sorted view of one of the
  results.
- **Assumptions** — `"amount"` is always numeric; `"description"` may
  contain irregular whitespace/casing; `"status"` may be `"completed"`
  or `"failed"`; the list may be empty.
- **Edge cases** — an empty transaction list; a transaction with a
  missing or empty `"description"`; no completed transactions at all
  (customer-count and total should both handle this gracefully;
  `sum()` of an empty generator is `0`, per the aggregate chapter's
  §8.4).
- **Pseudocode:**
  ```
  ids = extract id from every transaction
  completed = filter transactions where status == "completed"
  normalized_descriptions = strip and lowercase every completed transaction's description
  customer_counts = count how many completed transactions each customer has
  categories = the set of every distinct category across completed transactions
  positive_amounts_generator = a generator of every completed transaction's amount, where amount > 0
  total_positive = sum of positive_amounts_generator
  ranked_customers = customer_counts, sorted by count, highest first
  ```
- **Data transformations** — extraction (map), filtering, normalization
  (map with a function call), grouping-style counting (dict), uniqueness
  (set), lazy filtering + aggregation (generator + `sum()`), sorting
  (§18 of the grouping chapter).
- **Complexity** — every stage is O(n) individually (Big-O chapter's
  §27–§28); the final sort of the customer ranking is O(k log k), where
  `k` is the number of distinct customers, typically far smaller than
  `n`.
- **Memory considerations** — the staged lists (`completed`,
  `normalized_descriptions`) each cost O(n) additional space, a
  deliberate readability trade-off per §29.3; the positive-amount
  generator deliberately avoids a redundant O(n) intermediate list,
  since its only consumer is `sum()`.

### Reference Implementation

```python
from collections import defaultdict


def extract_ids(transactions):
    return [t["transaction_id"] for t in transactions]


def filter_completed(transactions):
    return [t for t in transactions if t["status"] == "completed"]


def normalize_descriptions(transactions):
    return [(t.get("description") or "").strip().lower() for t in transactions]


def count_by_customer(transactions):
    counts = defaultdict(int)
    for t in transactions:
        counts[t["customer_id"]] += 1
    return dict(counts)


def unique_categories(transactions):
    return {t["category"] for t in transactions}


def positive_amounts(transactions):
    return (t["amount"] for t in transactions if t["amount"] > 0)


def total_positive_amount(transactions):
    return sum(positive_amounts(transactions))


def rank_customers_by_count(customer_counts):
    return sorted(customer_counts.items(), key=lambda item: item[1], reverse=True)


def build_summary(transactions):
    completed = filter_completed(transactions)

    return {
        "all_ids": extract_ids(transactions),
        "completed_transactions": completed,
        "normalized_descriptions": normalize_descriptions(completed),
        "customer_counts": count_by_customer(completed),
        "categories": unique_categories(completed),
        "positive_amounts": positive_amounts(completed),   # generator — consume once
        "total_positive_amount": total_positive_amount(completed),
        "ranked_customers": rank_customers_by_count(count_by_customer(completed)),
    }
```

**Requirement 9, applied — identifying and refactoring an
overcomplicated draft:** an early, tempting one-liner for the whole
pipeline might look like:

```python
# An overcomplicated draft — everything crammed into one expression:
summary_amount = sum(
    t["amount"]
    for t in transactions
    if t["status"] == "completed" and t["amount"] > 0 and t["description"].strip() != ""
)
```

This *works*, but it silently bundles three unrelated concerns
(completion status, positive amount, non-empty description) into one
filter condition, making it unclear which condition is actually
responsible if the result looks wrong. The refactored version above
separates `filter_completed` as its own named, reusable step, and keeps
`total_positive_amount`'s own filter condition focused on exactly one
thing (`amount > 0`) — directly applying §28's "complexity should be
named" lesson to this project's own draft, exactly as requirement 9
asks.

```python
transactions = [
    {"transaction_id": "T1", "customer_id": "C1", "amount": 100, "status": "completed", "category": "food", "description": "  Lunch  "},
    {"transaction_id": "T2", "customer_id": "C1", "amount": -20, "status": "completed", "category": "food", "description": "Refund"},
    {"transaction_id": "T3", "customer_id": "C2", "amount": 200, "status": "failed", "category": "travel", "description": "Flight"},
]

summary = build_summary(transactions)
print(summary["total_positive_amount"])   # 100 — only T1 (T2 is completed but negative; T3 isn't completed)
print(summary["categories"])               # {'food'} — only completed transactions' categories
```

## 44. Interview Questions

**Foundational**

- What is a list comprehension?
- Why do comprehensions exist, if a `for` loop can already do the same
  thing?
- What is the difference between the expression and the condition in a
  comprehension?
- How does filtering work inside a comprehension?
- What is a set comprehension, and how does its result differ from a
  list comprehension's?
- What is a dictionary comprehension?
- What is a generator expression?

**Intermediate**

- What is the difference between a list comprehension and a generator
  expression, in terms of both syntax and behavior?
- When should you avoid using a comprehension?
- Can you use `if`/`else` inside a comprehension? How does that differ
  from a filtering `if`?
- What is the difference between filtering and a conditional expression?
- What happens when comprehensions are nested — what order do the
  `for` clauses execute in?
- Why are side effects inside comprehensions discouraged?
- How would you debug a comprehension that is producing an unexpected
  result?
- When is a normal loop more readable than a comprehension?

**Advanced**

- What is the time complexity of a simple list comprehension over `n`
  items? What is its space complexity, and how does that compare to the
  equivalent generator expression?
- How does a generator expression's memory usage differ from a list
  comprehension's, and does that difference affect time complexity too?
- How can comprehensions be combined with `enumerate()`? Why would you
  prefer that over `range(len(...))`?
- How can comprehensions be combined with `zip()`? What happens if the
  two zipped iterables have different lengths?
- How would you refactor an unreadable, deeply nested comprehension
  with multiple conditions into clearer code? Name at least two
  distinct techniques.

**Code-based**

- "What does `[x if x > 0 else -x for x in [-3, 2, -1]]` produce, and
  why?" (Expect the learner to explain this is a conditional expression
  applied to every item — `[3, 2, 1]`.)
- "What does `{len(w) for w in ['cat', 'dog', 'elephant']}` produce?
  Why is the result a set rather than a list, and does the order of the
  result matter?"
- "Here is a comprehension with three nested `for` clauses and two `if`
  conditions. Would you keep it as-is, or refactor it? Justify your
  answer using this chapter's readability heuristics."

## 45. Comprehension Decision Framework

A final, direct set of questions to run through whenever deciding how
to write a piece of collection-building code:

1. Am I **building a new collection**? (If not — if the goal is a side
   effect — skip comprehensions entirely; see §21.)
2. Is the **transformation simple**?
3. Is the **filter simple**?
4. Can the expression be **understood immediately**, without mentally
   executing it?
5. Are there **side effects** involved?
6. Is there **complex error handling** needed?
7. Are there **multiple nested loops**?
8. Would a **named function** improve clarity?
9. Would a **normal loop** be easier to debug, given what this code
   does?
10. Is the code **readable without mentally executing it**?

**Resulting guidance:**

```
YES to simple transformation/filter → comprehension may be appropriate
COMPLEX LOGIC                        → normal loop / helper function
SIDE EFFECTS                          → normal loop
COMPLEX ERROR HANDLING                → normal loop
DIFFICULT TO READ                     → refactor (name it, stage it, or loop it)
```

## 46. Final Mental Model

**COMPREHENSION = "a concise way to build a collection from an
iterable."**

```
LIST COMPREHENSION   → build a list
SET COMPREHENSION    → build a set
DICT COMPREHENSION   → build a dictionary
GENERATOR EXPRESSION → produce values lazily
```

And the standard this entire chapter has been building toward:

```
GOOD PYTHON = CLEAR + CORRECT + MAINTAINABLE + REASONABLY EFFICIENT
```

**NOT:**

```
SHORT + CLEVER + HARD TO READ
```

## 47. Final Review

- A **comprehension** is a concise syntax for a specific, common loop
  shape — building a new collection from an existing iterable,
  optionally filtering and/or transforming each item — never a
  fundamentally different algorithm from the equivalent `for` loop.
- **Filtering** (§4) decides *whether* an item is kept; **transformation**
  (§7, §20) decides *what* an item becomes; a **conditional expression**
  (§6) is transformation that branches between two possible outputs, and
  is easily confused with a filter `if` because both use the same
  keyword.
- **Set comprehensions** (§9) build unique, unordered results; **dictionary
  comprehensions** (§10–§11) build key-value mappings; **generator
  expressions** (§12) produce values lazily, trading materialized memory
  for on-demand computation, at identical time complexity.
- **Nested comprehensions** (§14–§16) are valid but readability degrades
  quickly with depth and condition count — not every valid comprehension
  is a *good* one.
- `enumerate()` (§17) and `zip()` (§18), combined with **tuple unpacking**
  (§19), make many common comprehension patterns both correct and
  readable.
- Comprehensions are for **building results**; **side effects** (§21),
  **complex exception handling** (§22), and **hidden mutation** (§23)
  are all signs a plain loop is the better tool.
- **Readable naming** (§24) and **choosing clarity over brevity** (§25)
  apply to all Python code, not only comprehensions — the shortest
  version of a piece of code is not automatically the clearest.
- **Refactoring** an unreadable comprehension (§28) most often means
  naming its complexity via a helper function, returning to an explicit
  loop, or splitting it into a **multi-stage pipeline** (§29) — each
  trading a small amount of memory or verbosity for real gains in
  clarity and debuggability.
- Comprehension **time complexity matches the equivalent loop's**;
  their **space complexity** differs meaningfully between a materialized
  list/set/dict and a lazy generator — never assume a comprehension is
  "just faster" without measuring (§30–§31).
- The chapter's two standing principles, to be carried forward into all
  future Python work: **"Pythonic" does not mean "clever,"** and
  **readable code is a production feature**, not an optional nicety
  layered on top of "working" code.

## 48. Answer Key / Solutions

### Level 1

**1.** A direct transformation — §3.
```python
print([x * 3 for x in [3, 6, 9]])   # [9, 18, 27]
```
Comprehension appropriate: yes — single, simple transformation (§26).
Loop equivalent: `result = []; for x in [3, 6, 9]: result.append(x * 3)`.
Time: O(n). Space: O(n) for the new list.

**2.** A filter — §4.
```python
print([x for x in [1, 2, 3, 4, 5, 6] if x % 2 == 0])   # [2, 4, 6]
```
Appropriate: yes, single simple filter. Time: O(n). Space: O(n) worst
case (if every item matched).

**3.** A method call inside the expression — §7.
```python
print([s.lower() for s in ["HELLO", "World", "PYTHON"]])
# ['hello', 'world', 'python']
```

**4.** `len()` used as the expression — §7, §32.
```python
print([len(s) for s in ["cat", "elephant", "dog"]])   # [3, 8, 3]
```

**5.** A set comprehension collapses duplicate lengths — §9.
```python
print({len(s) for s in ["cat", "dog", "owl", "elephant"]})   # {3, 8}
```
Readability note: the result loses the information of *which* words
share a length, and has no guaranteed order — appropriate here only
because the exercise asked specifically for unique lengths, not a
mapping back to the original words.

### Level 2

**6.**
```python
users = [{"name": "A", "active": True}, {"name": "B", "active": False}]
print([u for u in users if u["active"]])   # [{'name': 'A', 'active': True}]
```

**7.**
```python
print([u["name"] for u in users])   # ['A', 'B']
```

**8.**
```python
people = [{"name": "A", "age": 30}, {"name": "B", "age": 20}]
print({p["name"]: p["age"] for p in people})   # {'A': 30, 'B': 20}
```

**9.**
```python
names, scores = ["A", "B"], [90, 80]
print([(n, s) for n, s in zip(names, scores)])   # [('A', 90), ('B', 80)]
```

**10.**
```python
items = ["x", "y", "z"]
print([(i, item) for i, item in enumerate(items, start=1)])
# [(1, 'x'), (2, 'y'), (3, 'z')]
```

### Level 3

**11.** Flattening — §14.
```python
matrix = [[1, 2], [3, 4], [5]]
print([n for row in matrix for n in row])   # [1, 2, 3, 4, 5]
```

**12.** Nested filtering — §16.
```python
groups = [{"items": [1, -2, 3]}, {"items": [-4, 5]}]
print([n for g in groups for n in g["items"] if n > 0])   # [1, 3, 5]
```

**13.** A dictionary comprehension over records — §10.
```python
transactions = [{"id": "T1", "amount": 100}, {"id": "T2", "amount": 200}]
print({t["id"]: t["amount"] for t in transactions})   # {'T1': 100, 'T2': 200}
```

**14.** Filter + aggregate as a single generator expression — §30.
```python
numbers = [1, 2, 3, 4, 5]
print(sum(n for n in numbers if n % 2 == 0))   # 6
```
No intermediate list of even numbers is ever built — O(n) time, O(1)
additional space.

**15.**
```python
def is_wanted(x):
    return g(x) and h(x) and not k(x)

result = [f(x) for x in data if is_wanted(x)]
```
Better because: the three-condition filter is named (`is_wanted`),
making the comprehension itself trivially readable, and the condition
can now be tested independently of the surrounding loop — directly
applying §28's core lesson.

### Level 4

**16.**
```python
transactions = [{"description": "  Lunch OUT "}, {"description": "coffee"}]
normalized = [t["description"].strip().lower() for t in transactions]
print(normalized)   # ['lunch out', 'coffee']
```

**17.**
```python
logs = [{"level": "DEBUG", "msg": "x"}, {"level": "INFO", "msg": "y"}]
non_debug = [log for log in logs if log["level"] != "DEBUG"]
print(non_debug)   # [{'level': 'INFO', 'msg': 'y'}]
```

**18.**
```python
docs = [{"id": "D1", "author": "Ada"}, {"id": "D2", "author": "Grace"}]
author_by_id = {doc["id"]: doc["author"] for doc in docs}
print(author_by_id)   # {'D1': 'Ada', 'D2': 'Grace'}
```

**19.**
```python
docs = [{"category": "news"}, {"category": "sports"}, {"category": "news"}]
categories = {doc["category"] for doc in docs}
print(categories)   # {'news', 'sports'}
```

**20.** A staged pipeline, following §29's pattern directly.
```python
records = [
    {"status": "ok", "text": "  Hello  ", "amount": 10},
    {"status": "bad", "text": "skip", "amount": 5},
    {"status": "ok", "text": "World", "amount": 20},
]

valid = [r for r in records if r["status"] == "ok"]
normalized = [r["text"].strip().lower() for r in valid]
total = sum(r["amount"] for r in valid)

print(normalized, total)   # ['hello', 'world'] 30
```
Reasoning for staging over one combined expression: three genuinely
distinct concerns (validity, text normalization, numeric total) are
each given their own line and their own name (`valid`, `normalized`,
`total`), matching §29.2's argument that staged, named intermediate
results are easier to read and to debug independently — the modest
extra memory of holding `valid` as its own list (§29.3) is a reasonable
trade for that clarity in a pipeline this size.
