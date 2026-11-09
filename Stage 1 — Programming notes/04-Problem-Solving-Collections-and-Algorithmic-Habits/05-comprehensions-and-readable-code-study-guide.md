# 05 — Comprehensions and Readable Code: Complete Study Guide

**Source lesson:** `05-comprehensions-and-readable-code.md`  
**Learning position:** Stage 1 — Programming & Computational Thinking → Module 04 — Problem-Solving, Collections, and Algorithmic Habits  
**Purpose:** Understand every major concept and example in the lesson, practise all 20 exercises, and build the transaction-transformation mini-project.

---

# Part A — Chapter summary and teaching notes

## 1. What a comprehension is and why Python has it

A **comprehension** is concise syntax for building a new collection from an existing iterable. It can transform each item, filter items, or do both. It is not a new algorithm: it expresses a familiar loop in a compact form.

```python
numbers = [1, 2, 3, 4]

# Ordinary loop
result = []
for number in numbers:
    result.append(number * 2)

# Equivalent list comprehension
result = [number * 2 for number in numbers]
print(result)  # [2, 4, 6, 8]
```

Both versions make one pass, multiply each value once, and build the same list. Learn the loop first; the comprehension is simply another way to express that operation.

## 2. Basic list comprehensions

General form:

```python
[expression for item in iterable]
```

- **Expression:** the value to put in the result.
- **`for`:** starts iteration.
- **Item variable:** receives the current item.
- **Iterable:** the source collection or sequence.

Examples:

```python
numbers = [1, 2, 3]
[x * 2 for x in numbers]   # [2, 4, 6]
[x + 10 for x in numbers]  # [11, 12, 13]
[str(x) for x in numbers]  # ['1', '2', '3']
```

Trace `[x * 2 for x in numbers]`: first `x=1` adds `2`; then `x=2` adds `4`; then `x=3` adds `6`. The final list is `[2, 4, 6]`.

## 3. Filtering, transformation, and their order

A filter keeps or drops an item; it does not change the value. A transformation changes the value; it does not remove the item.

```python
numbers = [1, 2, 3, 4, 5, 6]

[x for x in numbers if x > 2]       # filter: [3, 4, 5, 6]
[x * 2 for x in numbers]            # transform: [2, 4, 6, 8, 10, 12]
[x * 2 for x in numbers if x > 2]   # filter, then transform: [6, 8, 10, 12]
```

The general form with a filter is `[expression for item in iterable if condition]`. The expression before `for` determines the output value. The condition after the iterable determines whether that item is included.

`%` is modulo: it gives the remainder after division. Therefore `x % 2 == 0` checks whether a number is even.

```python
[x % 2 == 0 for x in numbers]  # [False, False, True, True, False, True]
[x for x in numbers if x % 2 == 0]  # [2, 4, 6]
```

The first expression produces a Boolean for every input. The second filters and retains only even values.

When filtering and transforming are combined, the filter checks the **original** item first, then the expression transforms the surviving item. The equivalent loop makes the order explicit:

```python
result = []
for x in numbers:
    if x > 2:
        result.append(x * 2)
```

## 4. Conditional expressions: a different kind of `if`

Do not confuse a filter `if` with an `if/else` conditional expression.

```python
# Filter: some items are excluded
[x for x in numbers if x > 0]

# Conditional expression: every item remains, but its output can change
["positive" if x > 0 else "non-positive" for x in numbers]
```

The conditional expression has this form:

```python
value_if_true if condition else value_if_false
```

It can also be used outside a comprehension:

```python
number = 4
label = "even" if number % 2 == 0 else "odd"
print(label)  # even
```

Inside a comprehension:

```python
numbers = [1, 2, 3, 4]
labels = ["even" if number % 2 == 0 else "odd" for number in numbers]
# ['odd', 'even', 'odd', 'even']
```

Every input produces one output, so this is transformation (mapping), not filtering. Placement is important: the conditional expression goes before `for`; a filter `if` goes after the iterable and has no `else`.

## 5. Comprehensions with strings and dictionaries

Any valid Python expression can appear in the expression position, including string methods, dictionary access, and function calls.

```python
words = ["Python", "AI", "Data"]
[word.lower() for word in words]          # ['python', 'ai', 'data']
[word for word in words if len(word) > 3] # ['Python', 'Data']
[word.strip() for word in words]          # removes outer whitespace
```

For records stored as dictionaries:

```python
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 20},
]

[user["name"] for user in users]                 # ['Alice', 'Bob']
[user for user in users if user["age"] >= 18]    # both records
[user["name"].lower() for user in users]         # ['alice', 'bob']
```

`user["name"].lower()` combines dictionary lookup with a string method. If a key may be missing, direct indexing can raise `KeyError`; use the earlier lesson's `.get("name", default)` pattern when a missing key is genuinely possible. Do not assume every record has every field.

## 6. Set comprehensions

Syntax:

```python
{expression for item in iterable}
```

Example:

```python
words = ["cat", "dog", "elephant", "ant", "owl"]
unique_lengths = {len(word) for word in words}
print(unique_lengths)  # {3, 8}; order is not guaranteed
```

Curly braces without a `key: value` pair create a set. Duplicate results collapse into one value. Sets have no positional indexing, so `unique_lengths[0]` is invalid. Use a set comprehension when uniqueness or membership testing matters and ordering/duplicates do not.

## 7. Dictionary comprehensions

Syntax:

```python
{key_expression: value_expression for item in iterable}
```

Example:

```python
numbers = [1, 2, 3, 4]
squares = {number: number * number for number in numbers}
# {1: 1, 2: 4, 3: 9, 4: 16}
```

The expression before `:` becomes the key; the expression after `:` becomes the value.

```python
words = ["cat", "elephant", "dog"]
name_to_length = {word: len(word) for word in words}
# {'cat': 3, 'elephant': 8, 'dog': 3}

long_words = {word: len(word) for word in words if len(word) > 3}
# {'elephant': 8}
```

A dictionary comprehension is useful for reshaping or filtering data that already exists. For example, `.items()` produces `(key, value)` tuples. Tuple unpacking assigns the two parts directly to meaningful variables:

```python
prices = {"apple": 100, "banana": 50, "orange": 80}
expensive = {
    name: price
    for name, price in prices.items()
    if price > 60
}
# {'apple': 100, 'orange': 80}
```

Here `name, price` unpacks each pair; `name: price` preserves the pair; and the final `if` filters entries. This is a good use of a dictionary comprehension. It is not necessarily the right tool for accumulating grouped values, where a normal loop and dictionary updates are clearer.

## 8. Generator expressions and memory

A generator expression uses parentheses instead of square brackets:

```python
numbers = [1, 2, 3, 4]

[x * 2 for x in numbers]  # list: computes and stores all results now
(x * 2 for x in numbers)  # generator: computes each result when requested
```

A list comprehension eagerly builds the full list. A generator expression is lazy: it yields one value at a time when its consumer asks for it.

```python
total = sum(x * 2 for x in numbers)
print(total)  # 20
```

`sum()` requests each generated value, adds it to a running total, and does not need an intermediate list. When a generator expression is the only argument to a function, its extra parentheses are optional.

Complexity for `n` input items:

| Form | Time when fully consumed | Additional output/iteration space |
|---|---:|---:|
| List comprehension | O(n) | O(n), because the list stores all results |
| Generator expression | O(n) | Typically O(1) generator state, excluding input and whatever the consumer stores |

Laziness does not eliminate work or make the calculation automatically faster. Both compute every requested result. It changes *when* values are computed and how much output is materialized at once. If the consumer converts the generator to a list, that final list still costs O(n) space. This chapter covers generator expressions, not custom `yield` functions or infinite generator pipelines.

## 9. Comprehensions compared with `map()` and `filter()`

Equivalent examples:

```python
[x * 2 for x in numbers]
list(map(lambda x: x * 2, numbers))

[x for x in numbers if x > 10]
list(filter(lambda x: x > 10, numbers))
```

Both forms can produce the same results. A simple comprehension often reads more naturally and avoids an inline `lambda` and the extra `list()` conversion. `map()` and `filter()` are not bad or deprecated; a named function can make them clear:

```python
def is_valid_email(text):
    return "@" in text and "." in text

valid_emails = list(filter(is_valid_email, emails))
```

Choose based on clarity, not fashion.

## 10. Nested comprehensions and multiple `for` clauses

A nested comprehension can flatten a matrix:

```python
matrix = [[1, 2], [3, 4]]
flattened = [number for row in matrix for number in row]
# [1, 2, 3, 4]
```

Equivalent loop:

```python
flattened = []
for row in matrix:          # outer loop
    for number in row:      # inner loop
        flattened.append(number)
```

Read `for` clauses left to right: first clause is the outer loop, second is the inner loop. Add a filter at the end to keep selected values:

```python
matrix = [[1, 2, 3], [4, 5, 6]]
result = [
    number
    for row in matrix
    for number in row
    if number > 2
]
# [3, 4, 5, 6]
```

Two `for` clauses can also create a Cartesian product (every item paired with every item):

```python
numbers = [1, 2, 3]
pairs = [(x, y) for x in numbers for y in numbers]
# [(1,1), (1,2), (1,3), (2,1), (2,2), (2,3), (3,1), (3,2), (3,3)]
```

For `n` source items, there are `n²` pairs: O(n²) time and O(n²) space if the results are stored in a list. A one-line comprehension does not make nested-loop work disappear.

Nested comprehensions become hard to read when they combine several loops, multiple filters, and complex expressions. For example, this is valid but dense:

```python
result = [
    normalize(record["value"])
    for group in raw_groups
    for record in group["records"]
    if record["status"] == "active"
    if record["value"] is not None
    if len(str(record["value"])) > 0
]
```

Prefer naming the business rule and using explicit loops:

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

Now the rule can be understood and tested separately.

## 11. `enumerate()`, `zip()`, and unpacking

Use `enumerate()` when you need both an item's position and its value:

```python
names = ["Alice", "Bob", "Charlie"]
indexed_names = [(index, name) for index, name in enumerate(names)]
# [(0, 'Alice'), (1, 'Bob'), (2, 'Charlie')]

list(enumerate(names, start=1))
# [(1, 'Alice'), (2, 'Bob'), (3, 'Charlie')]
```

This is clearer than `[(i, names[i]) for i in range(len(names))]`, because `enumerate()` supplies index and value together. If you need only values, simply write `for name in names`.

Use `zip()` to pair corresponding positions in two iterables:

```python
names = ["Alice", "Bob"]
scores = [90, 85]
results = [(name, score) for name, score in zip(names, scores)]
# [('Alice', 90), ('Bob', 85)]
```

Important: `zip()` stops when the shortest input is exhausted. Thus `list(zip(["A", "B", "C"], [1, 2]))` produces `[('A', 1), ('B', 2)]`; `"C"` is ignored. This can hide an upstream length mismatch.

A dictionary can be built from parallel lists:

```python
scores_by_name = {
    name: score
    for name, score in zip(names, scores)
}
# {'Alice': 90, 'Bob': 85}
```

Tuple unpacking also works with dictionary `.items()`:

```python
dictionary = {"a": 1, "b": 2}
{key: value for key, value in dictionary.items()}
[(name, score) for name, score in zip(names, scores)]
```

Meaningful names (`name`, `score`) are clearer than `pair[0]` and `pair[1]`.

## 12. Function calls, side effects, exceptions, and mutation

A named function can keep a comprehension simple while moving complex work elsewhere:

```python
def normalize(value):
    return value.strip().lower()

values = ["  Alice ", "BOB", " Charlie  "]
results = [normalize(value) for value in values]
# ['alice', 'bob', 'charlie']
```

**Do not use comprehensions merely to cause side effects.** This is poor style:

```python
[print(x) for x in numbers]  # creates and discards a list of None values
```

Use a loop:

```python
for x in numbers:
    print(x)
```

Rule: comprehensions build results; loops perform actions such as printing, writing, network requests, or changing external state.

Comprehensions also have no clean place for a `try/except` statement. If a transformation may raise an exception that must be handled, use a loop:

```python
results = []
for value in values:
    try:
        results.append(transform(value))
    except ValueError:
        pass  # or log the error / append a default
```

A pre-check such as `transform(value) if is_safe(value) else None` is not equivalent to catching a particular exception.

A comprehension creates a new collection, but it can still mutate objects inside it, which is misleading:

```python
records = [{"count": 0}, {"count": 0}]

# Avoid: mutates existing dictionaries and discards the resulting Nones
[record.update(count=record["count"] + 1) for record in records]

# Clear version
for record in records:
    record["count"] += 1
```

## 13. Naming, brevity, and readability

Prefer domain-specific nouns for data and verbs for actions:

```python
# Less informative
[x for x in xs if x > 10]

# Better
[score for score in scores if score > 10]
```

Prefer `customer_id`, `total_amount`, and `transactions` over cryptic `c`, `t`, and `ts` when context is not obvious. Avoid unnecessary abbreviations. Use business/domain language (`customer`, not generic `record`) when accurate.

Shorter code is not automatically clearer:

```python
result = [f(x) for x in data if g(x)]
```

If `f` and `g` are opaque, this is hard to understand. An explicit loop with a meaningful condition can be better. Conversely, this is a good comprehension:

```python
active_user_names = [user["name"] for user in users if user["active"]]
```

A long expression with several conditions may be clearer as a loop with early `continue` statements:

```python
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

Use a comprehension for a short, obvious transformation/filter that builds a new collection and has no significant side effects. Avoid it when logic has multiple independent steps, confusing nesting, complex exceptions, side effects, hidden business rules, debugging requirements, too many conditions, or a very long expression.

## 14. Refactoring and staged data transformation

Three useful refactoring choices:

**Option 1 — name the condition:**

```python
def is_eligible(x):
    return (
        complicated_condition(x)
        and another_condition(x)
        and yet_another_condition(x)
    )

result = [transform(x) for x in data if is_eligible(x)]
```

**Option 2 — use a loop:**

```python
result = []
for x in data:
    if is_eligible(x):
        result.append(transform(x))
```

**Option 3 — split the work into stages:**

```python
eligible_items = [x for x in data if is_eligible(x)]
result = [transform(x) for x in eligible_items]
```

The principle is **complexity should be named**. A function such as `is_eligible()` communicates intent and can be checked independently.

A readable data pipeline often follows:

```text
raw data → filter → transform → aggregate
```

```python
valid_records = [record for record in records if is_valid(record)]
normalized_records = [normalize(record) for record in valid_records]
total = sum(record["amount"] for record in normalized_records)
```

Named intermediate variables explain the state of the data and make each stage independently inspectable. The trade-off is memory: each intermediate list can require O(n) space. A combined generator feeding directly into an aggregate can reduce intermediate memory, but may be harder to debug. For small or moderate data, clarity often wins; optimize a large hot path only after measurement.

## 15. Time, space, and performance

For `n` items:

- List comprehension: O(n) time and O(n) additional space for the output list.
- Generator expression: O(n) time when fully consumed and typically O(1) generator iteration state, excluding input and consumer storage.
- Two nested loops over an `n`-item collection: O(n²) work; storing all pairs costs O(n²) space.

Do not claim comprehensions are always faster. In CPython, list comprehensions can have somewhat lower overhead than an equivalent append loop, but both are O(n) and perform the same algorithmic work. Actual speed depends on operation cost, function calls, input size, Python implementation/version, and memory allocation.

Engineering priority:

```text
CORRECTNESS → READABILITY → REASONABLE PERFORMANCE → MEASURE BEFORE OPTIMIZING
```

Use `timeit` for small comparisons and `cProfile` to locate bottlenecks in a larger program. Analyze, measure, identify the bottleneck, optimize, then measure again. Do not sacrifice clarity based on an untested assumption.

## 16. Common built-ins used with comprehensions

```python
[x for x in range(10)]                         # range values 0 through 9
[name for name in names if len(name) > 3]      # len() in a filter
[(i, value) for i, value in enumerate(values)] # index and value
[a + b for a, b in zip(first, second)]         # pairwise operation
sorted([x for x in numbers if x > 0])          # sorted() returns a new list
sorted(x for x in numbers if x > 0)            # generator accepted directly
list(reversed([1, 2, 3]))                      # [3, 2, 1]
sum(x for x in numbers if x > 0)
min(x for x in numbers if x > 0)
max(x for x in numbers if x > 0)
any(x > 100 for x in numbers)                  # stops at first True
all(x > 0 for x in numbers)                    # stops at first False
list(map(lambda x: x * 2, numbers))
list(filter(lambda x: x > 10, numbers))
users_by_id = {user["id"]: user for user in users}
users_by_id.items()
users_by_id.keys()
users_by_id.values()
{x for x in numbers}
set(x for x in numbers)                        # equivalent set construction
```

`range(10)` is a range object, not a generator expression. `sorted()` accepts any iterable and returns a list. `any()` and `all()` short-circuit and are often paired with generators to avoid building a temporary list. `map()` and `filter()` return iterators; wrap them in `list()` when a list is required. `set()` can consume a generator.

## 17. Beginner mistakes to recognize

1. Mixing up the output expression and filter condition.
2. Putting a filter-style `if` where a conditional `if/else` belongs. Correct: `[x if x > 0 else 0 for x in numbers]`.
3. Omitting the collection brackets/parentheses in a standalone comprehension.
4. Using `{}` when a list is required, or `[]` when a set is required.
5. Accidentally creating a dictionary with a colon: `{x: None for x in numbers}` is a dictionary; `{x for x in numbers}` is a set.
6. Expecting a generator to support indexing or to be reusable after it is exhausted.
7. Using nested comprehensions before being able to trace simple ones.
8. Using a comprehension for side effects.
9. Using cryptic names such as `x` and `xs` when domain names are clearer.
10. Writing extremely long one-liners.
11. Hiding business logic inside the expression instead of naming it.
12. Accidentally making a nested list: `[[x for x in numbers]]` is a list containing one list.
13. Expecting a lazy generator to execute before it is consumed.
14. Forgetting `map()`/`filter()` return iterators rather than lists.
15. Using `range(len(...))` unnecessarily instead of `enumerate()` or direct iteration.
16. Mutating original objects inside a comprehension that appears to build a new result.

## 18. Debugging and testing

When a comprehension is confusing or wrong:

1. Expand it into an ordinary loop.
2. Give meaningful names to intermediate values.
3. Print/inspect intermediate results.
4. Test the filter condition independently.
5. Test the transformation independently.
6. Rebuild it as a comprehension only if it remains readable.

```text
comprehension → expanded loop → debug → optionally refactor back
```

Test the same edge cases as any other function:

```python
def double_positive(numbers):
    return [n * 2 for n in numbers if n > 0]

def test_double_positive():
    assert double_positive([]) == []
    assert double_positive([5]) == [10]
    assert double_positive([1, 2, 3]) == [2, 4, 6]
    assert double_positive([-1, -2]) == []
    assert double_positive([2, 2, 2]) == [4, 4, 4]
```

For missing/`None` names:

```python
def names_from_records(records):
    return [r["name"] for r in records if r.get("name") is not None]

def test_names_from_records():
    assert names_from_records([]) == []
    assert names_from_records([{"name": "Ada"}]) == ["Ada"]
    assert names_from_records([{"name": None}, {"name": "Ada"}]) == ["Ada"]
    assert names_from_records([{}]) == []
```

For flattening:

```python
def flatten(matrix):
    return [n for row in matrix for n in row]

def test_flatten():
    assert flatten([]) == []
    assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]
    assert flatten([[], [1]]) == [1]
```

Defining a test function does not execute it. Call `test_double_positive()`, `test_names_from_records()`, and `test_flatten()`; if every assertion succeeds, print `"All tests passed."`. A failed assertion raises `AssertionError`. This is an introduction to edge-case testing, not the later testing-framework module.

## 19. Data engineering and AI/ML examples

**Data engineering examples:**

```python
transactions = [
    {"id": "T1", "amount": 100, "status": "completed"},
    {"id": "T2", "amount": -50, "status": "failed"},
    {"id": "T3", "amount": 200, "status": "completed"},
]

transaction_ids = [transaction["id"] for transaction in transactions]
completed = [t for t in transactions if t["status"] == "completed"]

documents = [{"text": "  Hello World  "}, {"text": "PYTHON rocks"}]
normalized_text = [document["text"].strip().lower() for document in documents]

records = [{"category": "food"}, {"category": "travel"}, {"category": "food"}]
unique_categories = {record["category"] for record in records}

docs = [
    {"id": "D1", "text": "hello world"},
    {"id": "D2", "text": "python is great"},
]
word_counts = {doc["id"]: len(doc["text"].split()) for doc in docs}
```

These demonstrate ID extraction, status filtering, text cleaning, unique categories, and ID-to-word-count mapping.

**AI/ML preprocessing examples** (plain Python; no pandas, NumPy, or ML framework):

```python
documents = [{"id": "D1", "text": "Hello"}, {"id": "D2", "text": "World"}]
texts = [doc["text"] for doc in documents]

examples = [{"text": "great!"}, {"text": ""}, {"text": "  "}]
valid_examples = [ex for ex in examples if ex["text"].strip()]
normalized = [ex["text"].strip().lower() for ex in valid_examples]

labeled_examples = [
    {"text": "great", "label": "positive"},
    {"text": "bad", "label": "negative"},
]
labels = [ex["label"] for ex in labeled_examples]

docs = [{"id": "D1", "source": "web"}, {"id": "D2", "source": "pdf"}]
metadata_by_id = {doc["id"]: doc["source"] for doc in docs}
```

A simple batching helper:

```python
def chunk(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]

batches = chunk(normalized, size=2)
```

These patterns support document text extraction, invalid-example filtering, normalization before tokenization, label extraction, metadata lookup, and basic batching.

## 20. Readability heuristics, style, type hints, and refactoring workshop

Quick heuristics:

- One simple transformation/filter: comprehension is often appropriate.
- Transformation plus one simple filter: often still appropriate.
- Multiple nested loops, complex branching, side effects, or complex exception handling: reconsider and usually use a loop/helper.
- If a reader must mentally decode it, simplify it.
- Optimize for maintainability, not line count.

PEP 8-related guidance in this lesson: use readable indentation and line breaks; split long comprehensions with one clause per line; use brackets/parentheses for multiline expressions rather than backslashes; put spaces after commas and around operators; separate pipeline stages with blank lines; use meaningful names; avoid semicolons and dense one-liners.

```python
# Cramped
result = [transform(record) for record in records if is_valid(record) and record["amount"] > 0]

# Clearer
result = [
    transform(record)
    for record in records
    if is_valid(record) and record["amount"] > 0
]
```

Type hints document interfaces without changing runtime behavior:

```python
def normalize_names(names: list[str]) -> list[str]:
    return [name.strip().lower() for name in names]
```

`list[str]` says the input is a list of strings; `-> list[str]` says the output is a list of strings. Python does not enforce these annotations at runtime.

The lesson's refactoring workshop decisions:

1. `[x * 3 for x in values]` — keep: simple transformation.
2. `[x for x in values if x >= 0]` — keep: simple filter.
3. `[n for row in matrix for n in row]` — keep if flattening is clear.
4. Four chained conditions — extract `is_wanted(x, excluded)` and call it in the comprehension.
5. `[log.write(...) for x in values]` — rewrite as a loop because writing is a side effect.
6. Conditional conversion to `int` — can remain if the pre-check is sufficient; ASCII check matters because `"²".isdigit()` is true but `int("²")` raises `ValueError`. If specific exception handling is needed, use a loop with `try/except`.
7. `[str(round(x * 1.08, 2)) for x in prices]` — acceptable while readable; extract a named function if it grows.
8. `{user["id"]: user["email"] for user in users if user["email"]}` — keep: clear filtered lookup dictionary.
9. `{tuple(sorted(pair)) for pair in raw_pairs}` — keep if the intent is deduplicating unordered pairs; comment if the reason is not obvious.
10. `sum(record["amount"] for record in records if record["status"] == "completed")` — keep: a clear lazy filter-and-aggregate expression.

## 21. Final decision framework

Before using a comprehension, ask:

1. Am I building a new collection?
2. Is the transformation simple?
3. Is the filter simple?
4. Can it be understood immediately?
5. Are side effects involved?
6. Is complex error handling needed?
7. Are there multiple nested loops?
8. Would a named function help?
9. Would a loop be easier to debug?
10. Is the code readable without mentally executing it?

**Mental model:** list comprehension builds a list; set comprehension builds a set; dictionary comprehension builds a dictionary; generator expression produces values lazily. Good Python is clear, correct, maintainable, and reasonably efficient—not merely short or clever.

---

# Part B — Your current learning level and roadmap fit

The roadmap places this lesson in **Stage 1 → Module 04 — Problem-Solving, Collections, and Algorithmic Habits**, after collection processing, grouping/deduplication/sorting, and Big-O reasoning. The broader Stage 1 tree contains 24 modules, 212 numbered lessons, and four stage-level projects. Earlier foundations include:

- **Module 01 — Computational Thinking and Program Design:** algorithms, variables, input/process/output, sequence/selection/iteration, decomposition, preconditions, dry runs, and state.
- **Module 02 — Python Core Language and Data Types:** strings, lists, tuples, dictionaries, sets, mutability, and type conversion.
- **Module 03 — Control Flow, Functions, Scope and Errors:** conditionals, loops, functions, arguments, scope, pure functions, validation, and exceptions.
- **Module 04:** search/count/filter/map/aggregate; grouping/deduplication/sorting; Big-O; choosing data structures; comprehensions and readable code.

The wider roadmap continues into files/CLI, modules, testing, OOP, advanced Python, profiling, packaging, internals, security, and code review. Their presence in the tree does **not** mean they have already been completed.

**Assessment: beginner progressing toward intermediate.** The concepts relevant here build on your existing loops, conditions, collections, functions, dictionary operations, tuple unpacking, and complexity reasoning. This lesson introduces comprehension syntax, generators, nested iteration, `enumerate()`, `zip()`, type hints, and basic test assertions. The solutions below use the lesson's comprehension features because they are the topic being learned; they do not introduce pandas, NumPy, Spark, OOP, recursion, file handling, or external frameworks.

---

# Part C — All 20 progressive exercises with explanations

## Level 1 — Beginner

### 1. Triple each number

```python
numbers = [3, 6, 9]
result = [number * 3 for number in numbers]
print(result)  # [9, 18, 27]
```

- `for number in numbers` visits each value.
- `number * 3` is the output expression.
- The brackets build a new list.

### 2. Keep even numbers

```python
numbers = [1, 2, 3, 4, 5, 6]
evens = [number for number in numbers if number % 2 == 0]
print(evens)  # [2, 4, 6]
```

- `number % 2` calculates the remainder.
- `== 0` means the number is even.
- The filter keeps only matching values.

### 3. Convert strings to lowercase

```python
words = ["HELLO", "World", "PYTHON"]
lower_words = [word.lower() for word in words]
print(lower_words)  # ['hello', 'world', 'python']
```

Each `word` is transformed by `.lower()` and retained in the output list.

### 4. Find each word's length

```python
words = ["cat", "elephant", "dog"]
lengths = [len(word) for word in words]
print(lengths)  # [3, 8, 3]
```

`len(word)` is the expression, so every word produces its character count.

### 5. Find unique word lengths

```python
words = ["cat", "dog", "owl", "elephant"]
unique_lengths = {len(word) for word in words}
print(unique_lengths)  # {3, 8}
```

Curly braces create a set, so repeated length `3` appears only once. Set order is not guaranteed.

## Level 2 — Intermediate

### 6. Keep active users

```python
users = [
    {"name": "A", "active": True},
    {"name": "B", "active": False},
]
active_users = [user for user in users if user["active"]]
print(active_users)  # [{'name': 'A', 'active': True}]
```

- `user` is each dictionary.
- `user["active"]` is the filter condition.
- Only the active record is collected.

### 7. Extract user names

```python
names = [user["name"] for user in users]
print(names)  # ['A', 'B']
```

The expression extracts the `"name"` field from each user dictionary.

### 8. Map names to ages

```python
people = [
    {"name": "A", "age": 30},
    {"name": "B", "age": 20},
]
ages_by_name = {person["name"]: person["age"] for person in people}
print(ages_by_name)  # {'A': 30, 'B': 20}
```

- Before `:` is the key (`name`).
- After `:` is the value (`age`).
- Each person produces one dictionary entry.

### 9. Pair names and scores

```python
names = ["A", "B"]
scores = [90, 80]
pairs = [(name, score) for name, score in zip(names, scores)]
print(pairs)  # [('A', 90), ('B', 80)]
```

`zip()` pairs values by position; tuple unpacking assigns each pair to `name` and `score`.

### 10. Create one-based indexed items

```python
items = ["x", "y", "z"]
indexed_items = [
    (index, item)
    for index, item in enumerate(items, start=1)
]
print(indexed_items)  # [(1, 'x'), (2, 'y'), (3, 'z')]
```

`enumerate()` provides both the index and item. `start=1` makes numbering begin at one.

## Level 3 — Advanced

### 11. Flatten a matrix

```python
matrix = [[1, 2], [3, 4], [5]]
flat = [number for row in matrix for number in row]
print(flat)  # [1, 2, 3, 4, 5]
```

The first `for` visits each row; the second visits each number in that row. This is equivalent to nested loops.

### 12. Extract positive values from nested records

```python
groups = [
    {"items": [1, -2, 3]},
    {"items": [-4, 5]},
]
positive = [
    number
    for group in groups
    for number in group["items"]
    if number > 0
]
print(positive)  # [1, 3, 5]
```

- Outer loop visits each group.
- Inner loop visits that group's `"items"`.
- Filter retains only values greater than zero.

### 13. Map transaction IDs to amounts

```python
transactions = [
    {"id": "T1", "amount": 100},
    {"id": "T2", "amount": 200},
]
amount_by_id = {
    transaction["id"]: transaction["amount"]
    for transaction in transactions
}
print(amount_by_id)  # {'T1': 100, 'T2': 200}
```

Each transaction creates one key-value pair: ID as key and amount as value.

### 14. Sum even values with a generator

```python
numbers = [1, 2, 3, 4, 5]
total = sum(number for number in numbers if number % 2 == 0)
print(total)  # 6
```

The generator yields `2` and `4` on demand. `sum()` adds them. No intermediate list is created: O(n) time and typically O(1) additional generator space.

### 15. Refactor a difficult filter

Original:

```python
result = [f(x) for x in data if g(x) and h(x) and not k(x)]
```

Clearer version:

```python
def is_wanted(value):
    return g(value) and h(value) and not k(value)

result = [f(value) for value in data if is_wanted(value)]
```

- The helper function groups the three conditions under a meaningful name.
- The comprehension now reads as “transform each wanted value.”
- The condition can be examined and tested independently.

## Level 4 — Production-oriented

### 16. Normalize transaction descriptions

```python
transactions = [
    {"description": "  Lunch OUT "},
    {"description": "coffee"},
]
normalized = [
    transaction["description"].strip().lower()
    for transaction in transactions
]
print(normalized)  # ['lunch out', 'coffee']
```

`strip()` removes whitespace at both ends; `lower()` converts letters to lowercase. The operations are applied to every description.

### 17. Remove DEBUG log events

```python
logs = [
    {"level": "DEBUG", "msg": "x"},
    {"level": "INFO", "msg": "y"},
]
non_debug = [log for log in logs if log["level"] != "DEBUG"]
print(non_debug)  # [{'level': 'INFO', 'msg': 'y'}]
```

The filter keeps records whose level is not `"DEBUG"`.

### 18. Map document IDs to authors

```python
docs = [
    {"id": "D1", "author": "Ada"},
    {"id": "D2", "author": "Grace"},
]
author_by_id = {doc["id"]: doc["author"] for doc in docs}
print(author_by_id)  # {'D1': 'Ada', 'D2': 'Grace'}
```

The dictionary key is the document ID; its value is the author.

### 19. Collect distinct document categories

```python
docs = [
    {"category": "news"},
    {"category": "sports"},
    {"category": "news"},
]
categories = {doc["category"] for doc in docs}
print(categories)  # {'news', 'sports'}
```

A set comprehension removes duplicate category values.

### 20. Build a readable multi-stage pipeline

```python
records = [
    {"status": "ok", "text": "  Hello  ", "amount": 10},
    {"status": "bad", "text": "skip", "amount": 5},
    {"status": "ok", "text": "World", "amount": 20},
]

valid_records = [record for record in records if record["status"] == "ok"]
normalized_text = [record["text"].strip().lower() for record in valid_records]
total_amount = sum(record["amount"] for record in valid_records)

print(normalized_text)  # ['hello', 'world']
print(total_amount)    # 30
```

- First stage filters valid records.
- Second stage normalizes text from those records.
- Third stage totals their amounts.
- The named stages make it easier to inspect and debug each result. The extra `valid_records` list uses O(n) memory, a deliberate clarity trade-off.

---

# Part D — Mini-project: Readable Transaction Data Transformation Pipeline

## 1. Problem and design

**Problem:** Convert a raw transaction list into useful, independently understandable summaries.

**Input fields:** `transaction_id`, `customer_id`, `amount`, `status`, `category`, `description`.

**Outputs:** all IDs, completed transactions, normalized descriptions, customer transaction counts, unique categories, a positive-amount generator, total positive amount, and customers ranked by count.

**Assumptions from the lesson:** amount is numeric; descriptions can have irregular whitespace/casing; status may be completed or failed; input may be empty.

**Edge cases:** empty input; missing or empty description; no completed transactions. `.get()` and `or ""` safely normalize a missing/`None` description. `sum()` of an empty generator returns `0`.

## 2. Implementation

```python
from collections import defaultdict


def extract_ids(transactions):
    return [transaction["transaction_id"] for transaction in transactions]


def filter_completed(transactions):
    return [
        transaction
        for transaction in transactions
        if transaction["status"] == "completed"
    ]


def normalize_descriptions(transactions):
    return [
        (transaction.get("description") or "").strip().lower()
        for transaction in transactions
    ]


def count_by_customer(transactions):
    counts = defaultdict(int)
    for transaction in transactions:
        counts[transaction["customer_id"]] += 1
    return dict(counts)


def unique_categories(transactions):
    return {transaction["category"] for transaction in transactions}


def positive_amounts(transactions):
    return (
        transaction["amount"]
        for transaction in transactions
        if transaction["amount"] > 0
    )


def total_positive_amount(transactions):
    return sum(positive_amounts(transactions))


def rank_customers_by_count(customer_counts):
    return sorted(
        customer_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )


def build_summary(transactions):
    completed = filter_completed(transactions)
    customer_counts = count_by_customer(completed)

    return {
        "all_ids": extract_ids(transactions),
        "completed_transactions": completed,
        "normalized_descriptions": normalize_descriptions(completed),
        "customer_counts": customer_counts,
        "categories": unique_categories(completed),
        "positive_amounts": positive_amounts(completed),
        "total_positive_amount": total_positive_amount(completed),
        "ranked_customers": rank_customers_by_count(customer_counts),
    }
```

## 3. Line-by-line design explanation

- `from collections import defaultdict`: imports a dictionary that can supply a default value for a missing key.
- `extract_ids()`: its list comprehension reads each transaction and collects its ID.
- `filter_completed()`: returns only records whose status is `"completed"`.
- `normalize_descriptions()`: `.get()` avoids a `KeyError` if description is missing; `or ""` handles `None`; `strip()` removes outer whitespace; `lower()` normalizes case.
- `count_by_customer()`: `defaultdict(int)` starts unseen customer counts at zero; each completed transaction increments its customer's count; `dict(counts)` returns a regular dictionary.
- `unique_categories()`: set comprehension retains each category once.
- `positive_amounts()`: generator expression lazily yields only positive amounts.
- `total_positive_amount()`: `sum()` consumes that generator without a separate list.
- `rank_customers_by_count()`: `.items()` supplies customer/count pairs; `key=lambda item: item[1]` sorts by count; `reverse=True` puts the highest count first.
- `build_summary()`: computes completed records and customer counts once, then returns all required outputs in one dictionary.

## 4. Run the pipeline

```python
transactions = [
    {
        "transaction_id": "T1",
        "customer_id": "C1",
        "amount": 100,
        "status": "completed",
        "category": "food",
        "description": "  Lunch  ",
    },
    {
        "transaction_id": "T2",
        "customer_id": "C1",
        "amount": -20,
        "status": "completed",
        "category": "food",
        "description": "Refund",
    },
    {
        "transaction_id": "T3",
        "customer_id": "C2",
        "amount": 200,
        "status": "failed",
        "category": "travel",
        "description": "Flight",
    },
]

summary = build_summary(transactions)

print(summary["all_ids"])                # ['T1', 'T2', 'T3']
print(summary["total_positive_amount"])  # 100
print(summary["categories"])             # {'food'}
print(summary["customer_counts"])        # {'C1': 2}
print(summary["ranked_customers"])       # [('C1', 2)]
```

The total is `100`: T1 is completed and positive; T2 is completed but negative; T3 is positive but failed. Categories are drawn from completed transactions only.

**Important generator note:** `summary["positive_amounts"]` is a one-pass generator. If you iterate over it or convert it to a list, it becomes exhausted; the separate `total_positive_amount` is already calculated by its own generator consumption.

## 5. Why the pipeline is staged

An overpacked expression could combine status, amount, and description conditions in one generator. That would make it difficult to identify which rule excluded a transaction. The named `filter_completed()` stage separates completion status from positive-amount calculation. This applies the lesson's principle: **name complexity rather than hiding it**.

## 6. Complexity and memory

Let `n` be the number of transactions and `k` the number of distinct customers.

- ID extraction: O(n) time and O(n) output space.
- Filtering completed records: O(n) time and up to O(n) space.
- Description normalization: O(n) time and O(n) output space.
- Customer counting: O(n) expected time and O(k) dictionary space.
- Unique categories: O(n) expected time and O(c) set space, where `c` is the number of categories.
- Positive amount generator and total: O(n) time and O(1) generator iteration space.
- Customer ranking: O(k log k) time and O(k) output space.

The staged lists intentionally trade some memory for readability. The positive amount generator avoids a redundant list because its consumer only needs the sum.

---

# Part E — Final revision checklist

- [ ] I can explain the four comprehension forms and their output types.
- [ ] I can distinguish a filter `if` from an `if/else` conditional expression.
- [ ] I can read filter-before-transform behavior correctly.
- [ ] I can trace nested `for` clauses in loop order.
- [ ] I can use `enumerate()`, `zip()`, and tuple unpacking.
- [ ] I understand that `zip()` truncates to the shorter iterable.
- [ ] I can explain eager list construction versus lazy generator evaluation.
- [ ] I can compare O(n) time with O(n) list space and O(1) generator iteration space.
- [ ] I avoid comprehensions for side effects, mutation, and complex exception handling.
- [ ] I can refactor dense logic with a helper function, a loop, or named stages.
- [ ] I use meaningful variable names and readable formatting.
- [ ] I test empty inputs, one item, duplicates, no matches, and missing/`None` fields.
- [ ] I can explain the transaction pipeline and its complexity.

**Core principle:** A comprehension is a tool for building a result, not a contest to write the shortest line. Choose the clearest correct implementation, then measure before optimizing.
