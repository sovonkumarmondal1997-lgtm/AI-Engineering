# 03 — Big-O Time and Space Complexity
## Study Guide, Complete Chapter Summary, Exercise Solutions, and Mini-Project

**Source lesson:** `03-big-o-time-and-space-complexity.md`  
**Roadmap position:** Stage 1 — Programming & Computational Thinking → Module 04 — Problem-Solving, Collections, and Algorithmic Habits → Lesson 03  
**Learning approach:** beginner-friendly explanations, explicit operation counting, and solutions using the Python foundations already studied.

---

# Part A — Complete lesson summary and teaching notes

## 1. What this chapter teaches

Big-O analysis answers:

> When the input becomes larger, how does the amount of work or extra memory used by the program grow?

It is a way to reason about scalability before a program reaches production. Code may work perfectly for 20 records but become unusable with two million records. The algorithm—not just whether the code is correct—determines how well it scales.

Examples from data engineering include repeated customer lookups, transaction processing, log aggregation, deduplication, sorting, preparing ML training data, document search, and API request processing.

## 2. Identify the input size first

The symbol `n` usually represents the size of the input, but its meaning depends on the problem.

| Input | Meaning of size |
|---|---|
| List | Number of elements |
| String | Number of characters |
| Dictionary | Number of key-value pairs |
| Grid | Often `r` rows and `c` columns |
| Two lists | Use two sizes, such as `n` and `m` |
| Graph | Usually vertices `V` and edges `E` (introduced only) |

Do not force every problem into one variable. If a function receives 1,000 customers and 50,000 orders, those are two independent sizes. State what each variable means before classifying the code.

## 3. What counts as work?

We count meaningful operations whose number can grow: comparisons, arithmetic, assignments, dictionary lookups, list traversal steps, function calls, and loop-body executions.

We do **not** count exact CPU instructions or milliseconds. Big-O deliberately ignores many low-level details and focuses on the growth pattern.

For example:

```python
def option_a(numbers):
    first = numbers[0]
    second = numbers[0]
    return first

def option_b(numbers):
    return numbers[0]
```

`option_a` performs more individual operations, but neither function's work grows with the list length. Both are **O(1)**. Big-O describes growth, not the exact number of operations.

## 4. Main complexity classes

| Complexity | Meaning | Example |
|---|---|---|
| O(1) | Constant work | `numbers[0]` |
| O(log n) | Work grows by repeatedly halving or doubling | Binary search |
| O(n) | One pass over `n` items | A loop over a list |
| O(n log n) | Linear number of levels/steps with logarithmic work | Python sorting |
| O(n²) | Roughly every item compared with every other item | Two full nested loops |
| O(n³) | Three full dimensions of `n` | Three nested loops |
| O(2ⁿ) | Exponential growth | Naive recursive Fibonacci |
| O(n!) | Factorial growth | All permutations |

These are growth categories, not exact runtime promises.

## 5. O(1): constant time

```python
numbers = [10, 20, 30, 40, 50]
first = numbers[0]
last = numbers[-1]
```

A Python list supports direct indexing. Python can access a known position without scanning all previous elements. The operation count does not increase when the list grows, so indexing is O(1).

Dictionary lookup is typically **O(1) average-case**:

```python
users_by_id = {"u1": {"name": "Ada"}, "u2": {"name": "Bob"}}
user = users_by_id["u1"]
```

A dictionary uses hashing to find a key without normally scanning every key. It is not an unconditional guarantee: severe hash collisions can make an operation O(n) in the worst case.

O(1) does not mean “instant.” It means the cost does not grow with `n`. Also, O(1) does not guarantee correctness: `numbers[0]` on an empty list raises `IndexError`.

## 6. O(n): linear time

```python
numbers = [10, 20, 30, 40]
for number in numbers:
    print(number)
```

The loop body runs once per item. If the number of items doubles, the work approximately doubles: O(n).

`sum(numbers)` is also O(n), because it must visit every item even though its loop is hidden inside a built-in function.

A list membership test may scan every item:

```python
def contains_value(numbers, target):
    for number in numbers:
        if number == target:
            return True
    return False
```

If the target is first, the search ends quickly. If it is last or absent, all `n` items may be checked. Therefore, its **worst-case time is O(n)**.

## 7. Early termination

A `return` or `break` can stop a loop before it finishes. This improves some actual runs, especially when the match is near the beginning. However, if the target is absent, the loop still checks all items. Early termination changes best-case and possibly average-case work, but does not necessarily change worst-case complexity.

For the search above:
- Best case: O(1), if the first item matches.
- Worst case: O(n), if the item is last or absent.

Always state which case your complexity describes.

## 8. O(log n): logarithmic time and binary search

Binary search works on an **already sorted** list. It checks the middle item and discards half the remaining search area.

For 16 items:

```text
16 → 8 → 4 → 2 → 1
```

It takes four halving steps. The number of steps is proportional to `log₂(n)`. One million items need only about 20 halvings, compared with up to one million checks in linear search.

```python
def binary_search(numbers, target):
    left = 0
    right = len(numbers) - 1

    while left <= right:
        middle = (left + right) // 2

        if numbers[middle] == target:
            return middle
        elif numbers[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1
```

`left` and `right` define the remaining search range. `middle` selects its midpoint. If the middle value is too small, move `left` rightward; otherwise move `right` leftward. Each iteration removes about half the candidates. The example search for `23` in `[2, 5, 8, 12, 16, 23, 38, 45, 56, 72]` checks indices 4, 7, then 5 and returns index 5.

Time is O(log n); auxiliary space is O(1), because this iterative version uses only a few variables. On unsorted data, binary search is not valid.

## 9. O(n²): quadratic time

```python
numbers = [1, 2, 3, 4]
for i in numbers:
    for j in numbers:
        print(i, j)
```

For every one of the `n` outer items, the inner loop visits `n` items. Total work is `n × n = n²`. With four items, it prints 16 pairs.

A duplicate-pair check has the same worst-case shape:

```python
def has_duplicate_pair(numbers):
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i != j and numbers[i] == numbers[j]:
                return True
    return False
```

The worst case compares all pairs, so O(n²). Early return may reduce work for some inputs.

**Important: nested does not automatically mean O(n²).**

```python
for i in numbers:
    for j in range(10):
        do_something()
```

The outer loop runs `n` times, but the inner loop always runs 10 times. Total is `10n`, which simplifies to O(n). Check what each loop bound depends on.

## 10. O(n³) and more nested-loop patterns

```python
for i in numbers:
    for j in numbers:
        for k in numbers:
            do_something()
```

Each of three loops runs `n` times: `n × n × n = n³`. At `n = 1,000`, that is one billion inner executions.

Four useful loop patterns:

```python
# A: both bounds depend on n → O(n²)
for i in range(n):
    for j in range(n):
        pass

# B: inner bound is fixed → O(n)
for i in range(n):
    for j in range(10):
        pass

# C: inner bound grows with i → O(n²)
for i in range(n):
    for j in range(i):
        pass

# D: inner loop doubles j → O(n log n)
for i in range(n):
    j = 1
    while j < n:
        j *= 2
```

For C, the total is `0 + 1 + 2 + ... + (n-1) = n(n-1)/2`, which is O(n²). For D, the inner loop takes O(log n) steps and repeats for each of `n` outer iterations.

## 11. Sequential operations and dominant terms

Sequential loops add their work:

```python
for x in numbers:
    process_a(x)

for x in numbers:
    process_b(x)
```

The total is `n + n = 2n`, simplified to O(n). Nested loops multiply their work; separate sequential loops add it.

If an O(n) pass is followed by an O(n²) operation, the total is O(n + n²), simplified to O(n²), because the faster-growing term dominates.

Examples:
- O(n² + n) → O(n²)
- O(3n + 10) → O(n)
- O(5n² + 2n + 100) → O(n²)

Constants and lower-order terms are dropped for Big-O. They still matter in real execution: a high-constant O(n) implementation can be slower than a low-constant O(n log n) implementation for realistic input sizes.

## 12. Space complexity: time is not memory

Space complexity asks how much **additional memory** the function needs. Auxiliary space means new memory created by the function, excluding the input it was given.

```python
def first_item(numbers):
    return numbers[0]
```

This uses O(1) auxiliary space.

```python
def copy_numbers(numbers):
    result = []
    for number in numbers:
        result.append(number)
    return result
```

The new list grows with the input: O(n) auxiliary space.

A running total uses O(1) extra space:

```python
total = 0
for number in numbers:
    total += number
```

It takes O(n) time and O(1) auxiliary space.

A list comprehension creates a full result list:

```python
squares = [x * x for x in numbers]
```

Time O(n), additional space O(n).

A generator expression produces values one at a time:

```python
squares = (x * x for x in numbers)
total = sum(x * x for x in numbers)
```

The generator does not hold the entire result list. The second expression takes O(n) time and O(1) additional space for the running total and generator state. Time can remain O(n) while space falls from O(n) to O(1).

## 13. Typical Python operation costs

These are typical costs with important qualifiers:

| Operation | Typical complexity | Reason |
|---|---|---|
| `list[i]` | O(1) | Direct index |
| `list.append(x)` | O(1) amortized | Usually cheap; occasional resize is expensive |
| `list.pop()` | O(1) | Removes last item |
| `list.pop(0)` | O(n) | Remaining items shift |
| `list.insert(0, x)` | O(n) | Existing items shift |
| `x in list` | O(n) worst case | May scan all values |
| `list.count(x)` | O(n) | Must count all matches |
| `list.remove(x)` | O(n) | Search and shift |
| `list[a:b]` | O(k) | Copies `k` slice elements |
| `list_a + list_b` | O(n + m) | Builds a new combined list |
| `dict[key]`, insert, delete, membership | O(1) average-case | Hash-based |
| Set membership, `add`, `remove`, `discard` | O(1) average-case | Hash-based |
| `sorted(list)` / `list.sort()` | O(n log n) worst-case | Comparison sorting |

`dict` and `set` worst-case operations can degrade to O(n) in severe collision situations. Set `remove` raises `KeyError` if absent; `discard` does nothing if absent.

`sorted(numbers)` returns a new list and uses O(n) additional space. `numbers.sort()` changes the existing list in place and avoids a second full result list, although the implementation can still use working memory. Python sorting is stable and adaptive: already sorted or reverse-sorted data may need only O(n) comparisons, while worst-case time is O(n log n).

## 14. Why dictionaries and sets improve repeated work

Repeated list search:

```python
def find_user(users, target_id):
    for user in users:
        if user["id"] == target_id:
            return user
    return None
```

One search is O(n). Repeating it `m` times costs O(m × n).

Build an index once:

```python
users_by_id = {}
for user in users:
    users_by_id[user["id"]] = user

found = users_by_id.get(target_id)
```

Building the dictionary costs O(n) average-case; `m` lookups cost O(m) average-case. Total O(n + m), at the cost of extra memory O(n). This is the “pay once, save repeatedly” pattern.

A set similarly trades memory for fast membership. A seen-set can deduplicate `n` records in O(n) average-case instead of comparing every record against every other record in O(n²).

## 15. Combining costs in data pipelines

For:

```python
unique = set(numbers)
result = sorted(unique)
```

Creating the set costs O(n) average-case. If `k` unique values remain, sorting costs O(k log k). Total: **O(n + k log k)**. Since `k ≤ n`, O(n log n) is a valid upper bound. Keeping `k` visible is more informative when duplicates are common.

For a typical transaction pipeline:
1. Deduplicate by ID: O(n) average-case.
2. Filter completed records: O(n).
3. Group by customer: O(n) average-case.
4. Sum each customer's transactions: O(n) total across all groups.
5. Sort `k` customer totals: O(k log k).

Total: **O(n + k log k)**, where `n` is transactions and `k` is distinct customers. Grouping and aggregation before sorting reduces the size of the expensive sort.

Search, count, filter, map, and aggregate over a plain list are generally O(n), because they visit each item. A fused generator pipeline such as:

```python
total = sum(x * 2 for x in numbers if x > 10)
```

does one pass: O(n) time and O(1) additional space. It checks each item, doubles matching values, and adds them to a running total without building an intermediate list.

Dictionary-based grouping, set-based deduplication, and order-preserving seen-set deduplication are O(n) average-case. Sorting is O(n log n).

## 16. Time-space trade-offs and engineering examples

Sometimes more memory saves time; sometimes less memory requires more work.

- **Banking/customer lookup:** build a customer-ID dictionary once rather than scan all customers for every request.
- **Log aggregation:** count errors in one pass with a dictionary instead of scanning the entire log separately for every service.
- **Deduplication:** use a set of IDs rather than compare every pair.
- **Transaction ranking:** group and aggregate first, then sort the smaller customer summary.
- **Data-quality validation:** put reference IDs in a set, then check incoming IDs.
- **ETL lookup/join:** for a many-to-one lookup with unique keys in table B, index B in a dictionary; this is not a universal algorithm for all relational joins.
- **AI/ML preprocessing:** normalize or key examples and use a seen-set to remove duplicates.
- **Document search:** build an index mapping terms to documents; this costs memory and setup time but speeds repeated searches.
- **Caching/precomputation:** store results to avoid repeated calculations.
- **Generators/streaming:** process one value or chunk at a time to reduce memory, with the trade-off that values may need recomputation and may not be reusable automatically.

The correct choice depends on which resource is scarce and how often the operation is performed.

## 17. Recursion, exponential growth, and factorial growth

A simple recursive countdown:

```python
def countdown(n):
    if n == 0:
        return
    countdown(n - 1)
```

It makes `n + 1` calls, so time is O(n). Calls wait for deeper calls to return, so the maximum call-stack depth is O(n) space.

Naive Fibonacci branches twice:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

The number of calls grows exponentially; O(2ⁿ) is a valid loose upper bound. The chapter gives 2,692,537 calls for `fibonacci(30)` and 331,160,281 for `fibonacci(40)`.

There are `n!` permutations of `n` distinct items. Producing all full permutations costs Θ(n × n!), because each output has `n` elements. O(2ⁿ) and O(n!) become impractical quickly. Recursion is introduced here only for complexity analysis; its full study is a later module.

## 18. Best, average, worst; Big-O, Theta, Omega

- **Best case:** least work for an input of size `n`.
- **Worst case:** most work for an input of size `n`.
- **Average case:** expected work over plausible inputs.

For linear search, best case is O(1); worst case is O(n). Big-O is not automatically synonymous with worst case: it can describe any growth bound, so say which case you mean.

Big-O is an upper bound; Big-Omega (Ω) is a lower bound; Big-Theta (Θ) is a tight bound when upper and lower growth match. Example: linear search's worst case is Θ(n), because it is both O(n) and Ω(n). Its best case is Θ(1). The chapter uses Big-O most often and keeps the formal treatment of Ω and Θ introductory.

## 19. Big-O is not exact runtime

Suppose A performs `100n` operations and B performs `n²`. At `n = 5`, A does 500 and B does 25, so B may be faster. At `n = 10,000`, A does one million and B does 100 million, so A wins. Big-O predicts eventual growth, not which implementation is faster for every finite input.

Actual runtime also depends on hardware, Python interpreter overhead, library implementation, constants, memory access, disk/network I/O, CPU/application caches, and system load.

## 20. Amortized complexity and list append

Most `list.append()` calls use already reserved capacity and are O(1). Occasionally the list grows its storage and copies existing references, an O(n) event. Such expensive resizing happens infrequently. Spread over a long sequence of appends, the average cost per append is O(1): **O(1) amortized**. It does not promise every individual append costs the same.

## 21. A repeatable analysis method

Use this checklist on unfamiliar code:

1. Define input size (`n`, or `n` and `m`).
2. Identify the repeated operation.
3. Count each loop's iterations.
4. Check nested loops and each loop's actual bound.
5. Add sequential operation costs.
6. Check early returns and breaks.
7. Include the cost of functions called inside loops.
8. Include list/dict/set operation costs.
9. Identify new intermediate collections.
10. Find the dominant growth term.
11. State time complexity and the case (best/average/worst).
12. State auxiliary space separately.

Worked examples:
- Direct first-item access: O(1) time, O(1) space.
- Print every item: O(n) time, O(1) space.
- Linear search: O(n) worst-case time, O(1) space.
- Two sequential passes: O(n) time, O(1) space.
- Two full nested loops: O(n²) time, O(1) space.
- Inner loop fixed at five: O(n) time, O(1) space.
- Triangular loop: O(n²) time, O(1) space.
- Repeated halving: O(log n) time, O(1) space.
- `n` loops each with a doubling inner loop: O(n log n), O(1) space.
- `sorted(numbers)`: O(n log n) time, O(n) space.
- `m` dictionary lookups: O(m) average-case time, O(m) if a result list is built.
- Filter with set membership: O(n) average-case time, O(n) worst-case result space.
- Generator filter/map/aggregate: O(n) time, O(1) space.
- `sorted(set(numbers))`: O(n + k log k) time, O(k) space.
- Build index and enrich records: O(n + m) time, O(n + m) space if both index and result are retained.

## 22. Common mistakes to avoid

1. Calling every loop O(n) without checking its bound.
2. Calling every nested loop O(n²).
3. Treating O(3n) as different from O(n).
4. Not defining what `n` represents.
5. Confusing time and space.
6. Forgetting that comprehensions build lists while generators stream values.
7. Assuming built-ins are O(1); `sum`, `count`, and `sorted` still process data.
8. Calling dictionary/set operations O(1) without “average-case.”
9. Assuming an O(n) algorithm always beats O(n²) for tiny inputs.
10. Confusing best-case with worst-case.
11. Ignoring sorting cost.
12. Ignoring the cost of building an index.
13. Ignoring expensive function calls inside loops.
14. Forgetting recursive call-stack memory.
15. Judging speed by code length.
16. Optimizing before identifying the bottleneck.
17. Memorizing labels without being able to count the work.

## 23. Measuring performance

Analysis predicts scaling; measurement reports actual runtime in your environment.

```python
import timeit

def linear_search(numbers, target):
    return target in numbers

numbers = list(range(10_000))
duration = timeit.timeit(
    lambda: linear_search(numbers, -1),
    number=100
)
print(duration)
```

`timeit` repeats a small snippet and reports total elapsed seconds. It helps compare small alternatives.

```python
import cProfile

def run_pipeline():
    # Larger pipeline work goes here.
    pass

cProfile.run("run_pipeline()")
```

`cProfile` shows where a larger program spends time. The recommended workflow is:

**Analyze → Measure → Identify bottleneck → Optimize → Measure again.**

Do not optimize merely because code looks complex. Confirm that the code runs at meaningful scale and measure the actual bottleneck.

## 24. Engineering decision framework and final takeaways

Before changing code, ask: What are the input sizes? What happens once and what repeats? Are loops nested or sequential? What do the bounds depend on? Can early termination help? What do the data structures cost? Are collections being created? What are total time and auxiliary space? Could an index/set save time? Is optimization necessary for the real workload? Have you measured before and after?

The central ideas:
- Big-O describes growth in work or memory, not exact seconds.
- Define input size before counting.
- Sequential costs add; nested costs multiply.
- The dominant term determines the simplified Big-O.
- Time and auxiliary space are separate.
- Hash-based lookups are typically O(1) average-case.
- Python sorting is O(n log n) worst-case and adaptive.
- `append` is O(1) amortized.
- Indexes and sets trade memory and setup work for faster repeated operations.
- Analyze first, measure, then optimize the proven bottleneck.

---

# Part B — Your current Stage 1 learning level

## 1. Roadmap position

The roadmap places this file at:

`Stage 1 — Programming & Computational Thinking/04-Problem-Solving-Collections-and-Algorithmic-Habits/03-big-o-time-and-space-complexity.md`

The Stage 1 tree contains 24 modules, 212 numbered lessons, and four stage-level projects. The relevant earlier modules are:

- **Module 01 — Computational Thinking and Program Design:** algorithms, variables, input/process/output, sequence/selection/iteration, decomposition, preconditions, dry runs, and state.
- **Module 02 — Python Core Language and Data Types:** strings, lists, tuples, dictionaries, sets, mutability, and type conversion.
- **Module 03 — Control Flow, Functions, Scope and Errors:** conditionals, loops, functions, arguments, scope, pure functions, validation, and exceptions.
- **Module 04 — Problem-Solving Collections and Algorithmic Habits:** search/count/filter/map/aggregate; grouping/deduplication/sorting; this Big-O lesson; then later collection choices, comprehensions, recursion, and parsing.

The wider tree continues into files/CLI, modules and code quality, testing, OOP, advanced Python, profiling, packaging, internals, security, and code review. Those later folders are roadmap content, not proof that you have already completed them.

## 2. Current learning assessment

Your recorded progress places you at **beginner progressing toward intermediate**. The foundations relevant to this lesson are computational thinking, conditionals and Boolean logic, loops, collections, functions, parameters/returns, defaults/docstrings, scope, pure functions/side effects, validation, exceptions, and the preceding collection-processing lessons.

This Big-O chapter is the transition from writing correct Python loops and collection operations to reasoning about how they scale. Your most important skill to develop now is not memorizing a complexity table; it is explaining, step by step, how many times each operation runs.

**Scope respected in the solutions:** I use variables, `if`, `for`/`while`, functions, lists, dictionaries, sets, indexing, `append`, `sum`, `max`, `sorted`, and basic arithmetic. I do not require recursion, classes, file handling, testing frameworks, or advanced abstractions. Where the exercise itself supplies a comprehension or generator, I analyze what it does; equivalent solution code is written with ordinary loops where practical.

---

# Part C — All exercise solutions

## §39 — Testing complexity reasoning (Q1–Q7)

### Q1. Sum all numbers

```python
def total(numbers):
    result = 0
    for number in numbers:
        result += number
    return result
```

- `n = len(numbers)`.
- The loop visits each item once; each addition is constant work.
- **Time: O(n). Auxiliary space: O(1).**
- `result` is one running value, not a list that grows.

### Q2. Find a pair with the target sum

```python
def has_pair_summing_to(numbers, target):
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i != j and numbers[i] + numbers[j] == target:
                return True
    return False
```

- `n = len(numbers)`.
- For every outer item, the inner loop can visit all `n` items.
- **Time: O(n²) worst case. Space: O(1).**
- Early `return` can stop sooner, but no matching pair may force the full scan.

### Q3. Return the first ten items

```python
def first_ten(numbers):
    result = []
    for number in numbers:
        if len(result) >= 10:
            break
        result.append(number)
    return result
```

- `n = len(numbers)`, but at most 10 values are appended.
- The loop stops after a constant maximum number of iterations.
- **Time: O(1). Space: O(1).**
- The result never grows beyond 10 elements, regardless of `n`.

### Q4. Build an ID index

```python
def build_index(records):
    index = {}
    for record in records:
        index[record["id"]] = record
    return index
```

- `n = len(records)`.
- One dictionary insertion per record.
- **Time: O(n) average-case. Space: O(n).**
- The dictionary stores up to one entry per distinct ID.

### Q5. Count unique items

```python
def unique_count(items):
    unique_items = set(items)
    return len(unique_items)
```

- `n = len(items)`; let `k` be the unique item count.
- Building the set inserts each input item once; getting its length is O(1).
- **Time: O(n) average-case. Space: O(k), at most O(n).**

### Q6. Loop with a fixed inner bound

```python
def process(numbers):
    for x in numbers:
        for y in range(3):
            print(x, y)
```

- `n = len(numbers)`.
- The outer loop runs `n` times; inner loop always runs 3 times.
- **Time: O(3n) = O(n). Space: O(1).**
- The inner bound is constant, not `n`.

### Q7. Sum squares above 10

```python
def sum_of_squares_over_10(numbers):
    total = 0
    for x in numbers:
        if x > 10:
            total += x * x
    return total
```

- `n = len(numbers)`.
- One pass; comparison per item and constant arithmetic for matches.
- **Time: O(n). Space: O(1).**
- The source's generator expression also avoids an intermediate list.

## §40 — Progressive coding exercises (1–20)

### Level 1 — Foundation

**1. Identify input sizes**
- `process_users(user_list)`: `n = len(user_list)`, number of users.
- `count_characters(text)`: `n = len(text)`, number of characters.
- `compare_grids(grid_a, grid_b)`: use separate dimensions, such as `r1 × c1` and `r2 × c2`; do not assume both grids have the same size.

**2. Classify the snippets**
- `for x in items: print(x)` → O(n), one pass.
- `x = items[3]` → O(1), direct index.
- Loop over `items`, with inner `range(4)` → O(n), because 4 is constant.

**3. Get the middle item**

```python
def get_middle(items):
    middle = len(items) // 2
    return items[middle]
```

Length and index access are constant-time operations. **Time O(1), space O(1)**. Requires a non-empty list.

**4. Double all values**

```python
def double_all(items):
    result = []
    for x in items:
        result.append(x * 2)
    return result
```

One multiplication and append per item: **time O(n)**. The result holds `n` values: **space O(n)**.

**5. Print a grid**

```python
def print_grid(items):
    for row in items:
        for value in row:
            print(value)
```

Let `r` be rows and `c` columns. Work is **O(r × c)**. If `n` means the total number of values in the grid, this is **O(n)**, not automatically O(n²). Space O(1).

### Level 2 — Intermediate

**6. Compare each pair once**

```python
def compare_all(items):
    matches = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                matches += 1
    return matches
```

The inner loop runs `n-1`, `n-2`, ... down to zero times. Total comparisons are triangular: **time O(n²), space O(1)**.

**7. Sum and maximum**

```python
def summarize(items):
    total = sum(items)
    maximum = max(items)
    return total, maximum
```

`sum` scans once and `max` scans once. They are sequential: O(n + n) = **time O(n)**. **Space O(1)**.

**8. Look up IDs**

```python
def get_all(index, ids):
    result = []
    for item_id in ids:
        result.append(index.get(item_id))
    return result
```

Let `n = len(index)` and `m = len(ids)`. The index is already built; there are `m` average O(1) lookups. **Time O(m) average-case; result space O(m)**.

**9. Filter using a set**

```python
def filter_known(items, known):
    result = []
    for x in items:
        if x in known:
            result.append(x)
    return result
```

One pass over `n = len(items)`; set membership is O(1) average-case. **Time O(n) average-case; space O(n) worst case** if all items match.

**10. Sort then take three**

```python
def top_three(items):
    ordered = sorted(items, reverse=True)
    return ordered[:3]
```

Sorting costs O(n log n) time and O(n) space. Copying three items is constant work. **Overall time O(n log n), space O(n)**.

### Level 3 — Advanced

**11. Average values above a threshold**

```python
def average_over_threshold(items, threshold):
    total = 0
    count = 0
    for x in items:
        if x > threshold:
            total += x
            count += 1
    if count == 0:
        return 0
    return total / count
```

One pass, no intermediate result list: **time O(n), space O(1)**. The final condition avoids division by zero.

**12. Unique values, descending**

```python
def ranked_unique(items):
    unique_items = set(items)
    return sorted(unique_items, reverse=True)
```

Let `k` be the number of unique values. Set creation: O(n) average-case; sort: O(k log k). **Time O(n + k log k), space O(k)**.

**13. Index customers and enrich orders**

```python
def enrich_orders(orders, customers):
    index = {}
    for customer in customers:
        index[customer["id"]] = customer

    result = []
    for order in orders:
        customer = index.get(order["customer_id"])
        result.append({"order": order, "customer": customer})
    return result
```

Let `n = len(customers)` and `m = len(orders)`. Build index O(n), process orders O(m). **Time O(n + m) average-case; space O(n + m)** for index and result.

**14. Build and sort all ordered pairs**

```python
def build_pairs_report(items):
    pairs = []
    for i in items:
        for j in items:
            if i != j:
                pairs.append((i, j))
    return sorted(pairs)
```

There are O(n²) pairs. Sorting `n²` entries costs O(n² log(n²)) = O(n² log n). **Time O(n² log n); space O(n²)** for pairs and sorted output.

**15. Compare 1,000 searches in one million customers**

- Linear scans: `m = 1,000`, `n = 1,000,000`; total O(m × n), approximately 1,000,000,000 checks worst-case. Extra space O(1) if each result is processed without storing all results.
- Dictionary index: build O(n), then perform O(1) average-case per lookup; total O(n + m) ≈ 1,001,000 operations. Extra space O(n) for the index.
- The index uses more memory but is about 999 times fewer operations in this example.

### Level 4 — Production

**16. Transaction pipeline**

```python
def process_transactions(transactions):
    seen_ids = set()
    unique = []
    for transaction in transactions:
        if transaction["id"] not in seen_ids:
            seen_ids.add(transaction["id"])
            unique.append(transaction)

    completed = []
    for transaction in unique:
        if transaction["status"] == "completed":
            completed.append(transaction)

    total = 0
    for transaction in completed:
        total += transaction["amount"]
    return total
```

For `n` transactions, set membership/insertion is O(1) average-case per row, followed by two linear passes. **Time O(n) average-case; space O(n)** for `seen_ids`, `unique`, and `completed`.

**17. Count logs by service and severity**

```python
def count_by_service_and_severity(logs):
    counts = {}
    for log in logs:
        service = log["service"]
        severity = log["severity"]

        if service not in counts:
            counts[service] = {}

        if severity not in counts[service]:
            counts[service][severity] = 0

        counts[service][severity] += 1
    return counts
```

One pass over `n` logs; dictionary operations are O(1) average-case. **Time O(n) average-case.** Space is O(s × v), where `s` is distinct services and `v` is average/distinct severity categories; bounded by O(n).

**18. Customer lookup architecture**

Build a dictionary mapping customer ID to customer once: setup **O(n) average-case time and O(n) space**. Each request uses `.get(customer_id)`: **O(1) average-case per request**. For `m` requests between refreshes, lookup work is O(m), plus setup O(n).

**19. Deduplicate by customer and date**

```python
def deduplicate_by_composite_key(records):
    seen = set()
    result = []
    for record in records:
        key = (record["customer_id"], record["date"])
        if key not in seen:
            seen.add(key)
            result.append(record)
    return result
```

One pass; tuple keys are hashable if their components are hashable. **Time O(n) average-case; space O(n)** worst case. The first record for each customer/date pair is kept.

**20. Prepare AI/ML examples**

```python
def prepare_dataset(examples):
    cleaned = []
    for example in examples:
        if example["text"].strip():
            cleaned.append(example)

    seen_texts = set()
    unique = []
    for example in cleaned:
        normalized = example["text"].strip().lower()
        if normalized not in seen_texts:
            seen_texts.add(normalized)
            unique.append(example)

    return sorted(unique, key=lambda example: len(example["text"]))
```

Let `n` be examples and `u` be unique cleaned examples. Cleaning and set-backed deduplication are O(n) average-case (more precisely, text processing also depends on total characters). Sorting is O(u log u). **Time O(n + u log u) average-case; space O(n)**.

---

# Part D — Mini-project: transaction pipeline performance analysis

## 1. Understand the naive design

The source pipeline performs five tasks: repeated transaction lookup, deduplication, grouping by customer, totals, and ranking.

- Repeated list search: `m` lookups × O(n) each = O(mn).
- Deduplication with `any()` scanning a growing list: O(n²).
- Grouping and totals: O(n) total.
- Ranking `k` customers: O(k log k).

Overall: **O(mn + n² + k log k)**. The hidden quadratic deduplication and repeated linear searches are the bottlenecks.

## 2. Improved implementation using learned collections

```python
def improved_pipeline(transactions, lookup_ids):
    # Build an ID index once; keep the first record for each ID.
    by_id = {}
    for transaction in transactions:
        if transaction["id"] not in by_id:
            by_id[transaction["id"]] = transaction

    found = []
    for transaction_id in lookup_ids:
        found.append(by_id.get(transaction_id))

    # Deduplicate with a set.
    seen_ids = set()
    unique = []
    for transaction in transactions:
        if transaction["id"] not in seen_ids:
            seen_ids.add(transaction["id"])
            unique.append(transaction)

    # Group by customer using a normal dictionary.
    grouped = {}
    for transaction in unique:
        customer = transaction["customer"]
        if customer not in grouped:
            grouped[customer] = []
        grouped[customer].append(transaction)

    # Calculate one total per customer.
    totals = {}
    for customer in grouped:
        total = 0
        for transaction in grouped[customer]:
            total += transaction["amount"]
        totals[customer] = total

    # Rank the smaller customer summary.
    ranking = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return found, ranking
```

## 3. Complexity of the improved pipeline

Let:
- `n` = number of transactions,
- `m` = number of lookup IDs,
- `k` = number of distinct customers.

| Step | Time |
|---|---|
| Build ID index | O(n) average-case |
| Perform all lookups | O(m) average-case |
| Seen-set deduplication | O(n) average-case |
| Group transactions | O(n) average-case |
| Calculate all totals | O(n) total |
| Sort customer totals | O(k log k) |

**Overall: O(n + m + k log k)**. The index, seen-set, unique list, groups, totals, and lookup results require additional memory proportional to their stored records: **O(n + m)** overall in the broad upper bound.

## 4. Why the improved version is better

The naive version repeatedly scans lists, producing O(mn) and O(n²) work. The improved version uses a dictionary index and a set, converting those steps to O(n + m) and O(n) average-case. It spends extra memory to avoid repeated scans. For 100,000 transactions and 1,000 lookups, the chapter contrasts roughly 100 million-plus operations with roughly 101,000 operations.

**Important policy detail:** the dictionary index uses first-write-wins (`if id not in by_id`) so it agrees with the deduplication policy of keeping the first record. A direct assignment on every duplicate would instead overwrite earlier records.

---

# Part E — Interview revision and self-check

1. **What is Big-O?** A description of how time or memory grows as input size grows.
2. **Why not just measure?** Measurement shows current runtime; Big-O helps predict scaling to larger inputs.
3. **List membership vs set membership?** List: O(n) worst case; set: O(1) average-case.
4. **Dictionary lookup?** O(1) average-case due to hashing; pathological collisions can degrade it.
5. **Two sequential O(n) loops?** O(n + n) = O(n).
6. **Two full nested loops?** O(n²).
7. **Nested loop with `range(20)`?** O(n), because 20 is fixed.
8. **Auxiliary space?** Extra memory created beyond the input.
9. **Why is append amortized O(1)?** Occasional expensive resizing is spread across many cheap appends.
10. **Why index before repeated lookups?** Pay O(n) once, then O(1) average-case per lookup.
11. **Why group before sorting?** Sort only `k` aggregate rows rather than all `n` raw records.
12. **Does Big-O predict milliseconds?** No; benchmark in the actual environment.
13. **What is the workflow?** Analyze, measure, identify the bottleneck, optimize, measure again.

## Final practice checklist

- [ ] I can define `n` and `m` for a problem.
- [ ] I can count loop iterations rather than guess from indentation.
- [ ] I can distinguish sequential from nested loops.
- [ ] I can recognize a fixed inner bound.
- [ ] I can explain why list search is O(n) and dictionary/set lookup is O(1) average-case.
- [ ] I can state time and auxiliary space separately.
- [ ] I can identify when a new list, set, or dictionary consumes O(n) memory.
- [ ] I can combine O(n) preprocessing with O(k log k) sorting.
- [ ] I can explain the memory-for-time trade-off.
- [ ] I can justify optimization with both complexity analysis and measurement.

**End of study guide.**
