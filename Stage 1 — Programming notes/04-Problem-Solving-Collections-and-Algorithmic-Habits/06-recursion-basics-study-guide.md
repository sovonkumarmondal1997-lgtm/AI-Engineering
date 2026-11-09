# 06 — Recursion Basics: Complete Study Guide

**Source lesson:** `06-recursion-basics.md`  
**Roadmap position:** Stage 1 → Module 04 — Problem-Solving, Collections, and Algorithmic Habits  
**Scope:** Complete chapter summary, current-level assessment, all 5 debugging-workshop diagnoses, all 20 progressive exercises, and the nested-configuration mini-project.

---

# Part A — Complete chapter summary (under 5,000 words)

## 1. What recursion means

**Recursion** is a problem-solving technique in which a function calls itself to solve a smaller version of the same problem. Imagine asking the person ahead of you in a queue for their position; they ask the person ahead of them, until the first person can answer directly. The answer then travels back, with each person adding one.

A recursive function needs two things:

1. **Base case:** the smallest case that can be answered directly, without another recursive call.
2. **Recursive case:** performs a small part of the work and calls the same function with a smaller/simpler input.

Example:

```python
def countdown(n):
    if n == 0:             # base case
        print("Liftoff!")
        return
    print(n)               # work for this step
    countdown(n - 1)       # smaller problem

countdown(3)
```

Output: `3`, `2`, `1`, `Liftoff!`. This assumes a non-negative integer; a negative value would never reach `n == 0`.

Each call is a separate execution with its own local variables. `countdown(3)` pauses while `countdown(2)` runs; that call pauses for `countdown(1)`, and so on. The original call is not restarted or erased.

## 2. Why recursion exists — and when not to use it

Recursion is natural when a problem contains smaller versions of itself:

- Nested lists and dictionaries.
- Folder trees and nested configuration/API payloads.
- Tree traversal.
- Divide-and-conquer algorithms.
- Exploring combinations and backtracking.
- Parsing nested expressions.

Its benefit is that code structure can mirror data/problem structure. It is not automatically better than a loop. Recursion has function-call overhead, consumes call-stack memory, can be harder to debug, and can hit Python's recursion-depth limit. For flat tasks such as summing or filtering a large list, loops and built-ins are usually simpler and safer.

## 3. Recursion versus iteration

**Recursion** repeats by making nested function calls; each call waits for the next. **Iteration** repeats a loop body until its condition changes.

```python
def countdown_recursive(n):
    if n == 0:
        print("Liftoff!")
        return
    print(n)
    countdown_recursive(n - 1)

def countdown_iterative(n):
    while n > 0:
        print(n)
        n -= 1
    print("Liftoff!")
```

Both produce the same output for non-negative `n`.

Factorial example:

```python
def factorial_recursive(n):
    if n == 0:
        return 1
    return n * factorial_recursive(n - 1)

def factorial_iterative(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

Both assume non-negative integer input. `0!` is `1`.

List sum:

```python
def sum_recursive(numbers):
    if not numbers:
        return 0
    return numbers[0] + sum_recursive(numbers[1:])

def sum_iterative(numbers):
    total = 0
    for number in numbers:
        total += number
    return total
```

For a simple sum, production code should normally use `sum(numbers)`. These hand-written functions teach the two execution styles.

| Dimension | Recursion | Iteration |
|---|---|---|
| Best fit | Naturally nested/self-similar structures | Flat, sequential work |
| Memory | Call stack grows with depth | Often constant auxiliary space |
| Runtime | Function-call overhead | Usually less overhead |
| Risk | `RecursionError` at excessive depth | Incorrect loop can run forever |
| Maintainability | Often clear for trees/nested structures | Often clearer for simple sequences |

## 4. Base case and recursive case

A general pattern:

```python
def function(problem):
    if base_case_condition:
        return base_case_result
    smaller_problem = make_progress_toward(problem)
    return function(smaller_problem)
```

The base case must be reachable, directly answerable, and mathematically correct. The recursive call must make **provable progress** toward it.

Broken example:

```python
def broken_countdown(n):
    if n == 0:
        return
    print(n)
    broken_countdown(n)  # same input: no progress
```

This never reaches zero. It eventually raises `RecursionError`. Passing `n - 1` fixes the progress defect for non-negative input.

## 5. What Python does: call stack and stack frames

Every function call creates a **stack frame**, containing that call's local state (such as its `n`) and where execution should resume. Python stores active calls in a LIFO **call stack**.

For `factorial_recursive(3)`, the stack at its deepest point conceptually contains:

```text
factorial_recursive(3)  waiting
factorial_recursive(2)  waiting
factorial_recursive(1)  waiting
factorial_recursive(0)  executing base case
```

Two phases occur:

- **Going down:** each call invokes a smaller call and pauses.
- **Unwinding / coming back up:** the base case returns; each paused call resumes, uses the returned value, computes its own result, returns, and its frame is removed.

For factorial:

```text
factorial(3)
  → factorial(2)
    → factorial(1)
      → factorial(0) returns 1
    → returns 1 * 1 = 1
  → returns 2 * 1 = 2
→ returns 3 * 2 = 6
```

The stack is empty again after the original call returns.

## 6. How to trace recursion

Trace all calls downward first, writing the expression each call is waiting to evaluate. Then substitute results upward.

```python
def sum_recursive(numbers):
    if not numbers:
        return 0
    return numbers[0] + sum_recursive(numbers[1:])
```

For `[3, 1, 4]`:

| Call | Input | Pending work |
|---|---|---|
| 1 | `[3, 1, 4]` | `3 + sum_recursive([1, 4])` |
| 2 | `[1, 4]` | `1 + sum_recursive([4])` |
| 3 | `[4]` | `4 + sum_recursive([])` |
| 4 | `[]` | Base case returns `0` |

Unwinding: call 3 returns `4`; call 2 returns `1 + 4 = 5`; call 1 returns `3 + 5 = 8`.

## 7. Core recursive examples

### Numbers

```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def digit_sum(n):
    if n < 10:
        return n
    return n % 10 + digit_sum(n // 10)
```

Factorial and digit sum assume non-negative integers. `fibonacci` is also intended for non-negative `n`; as written, negative input is not rejected and would be returned unchanged. `% 10` extracts the last digit; `// 10` removes it.

`fibonacci(4)` expands to `fibonacci(3) + fibonacci(2)`, then smaller calls, and returns `3`. Unlike the previous one-call examples, it makes two recursive calls and repeats work.

### Strings

```python
def reverse_string(text):
    if len(text) <= 1:
        return text
    return reverse_string(text[1:]) + text[0]

def is_palindrome(text):
    if len(text) <= 1:
        return True
    if text[0] != text[-1]:
        return False
    return is_palindrome(text[1:-1])
```

For `"cat"`, reverse the tail `"at"` first, then append `"c"` to produce `"tac"`. A palindrome check compares the first and last characters; mismatch returns `False` immediately; otherwise it removes both ends and checks the smaller string.

### Lists

```python
def find_max(numbers):
    if len(numbers) == 1:
        return numbers[0]
    rest_max = find_max(numbers[1:])
    return numbers[0] if numbers[0] > rest_max else rest_max

def count_occurrences(items, target):
    if not items:
        return 0
    first_match = 1 if items[0] == target else 0
    return first_match + count_occurrences(items[1:], target)
```

`find_max` requires a non-empty list; `max()` is preferable in production. Counting adds `1` if the first item matches, otherwise `0`, to the count of the remaining list.

### Nested lists and dictionaries

```python
def flatten(items):
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
```

For `[1, [2, 3], [4, [5, 6]], 7]`, output is `[1, 2, 3, 4, 5, 6, 7]`. A nested list is processed recursively; a plain value is appended. The loop's plain-item branch is the stopping point for each nested path.

```python
def collect_values(data):
    values = []
    for value in data.values():
        if isinstance(value, dict):
            values.extend(collect_values(value))
        else:
            values.append(value)
    return values
```

For a nested dictionary, recurse into dictionary values and collect plain leaf values. This is a reusable pattern for JSON-like payloads and configurations.

## 8. Accumulator-passing and returning results

Instead of doing all work during unwinding, pass a running result downward:

```python
def sum_with_accumulator(numbers, running_total=0):
    if not numbers:
        return running_total
    return sum_with_accumulator(numbers[1:], running_total + numbers[0])
```

The base case returns the accumulated total. This resembles a loop accumulator. It is related to tail-recursive style, but **Python does not optimize tail calls**, so it does not remove call-stack usage.

Always return the recursive result when it contributes to the answer:

```python
# Broken: computed expression is discarded; function returns None
numbers[0] + broken_sum(numbers[1:])

# Correct
return numbers[0] + correct_sum(numbers[1:])
```

A bare expression does not return its value.

## 9. Linear recursion, branching recursion, and tree-shaped calls

- **Linear recursion:** one recursive call per invocation; calls form one chain.
- **Branching recursion:** multiple recursive calls; one call creates multiple subproblems.
- Fibonacci is branching. Its call tree contains repeated `fibonacci(2)` and other repeated subproblems, recomputed independently.

A computation tree has a root (initial call), children (recursive calls), and leaves (base cases).

## 10. Divide and conquer

Three steps:

1. **Divide:** split a problem into smaller subproblems.
2. **Conquer:** solve each smaller problem recursively (or directly if it is a base case).
3. **Combine:** assemble the smaller answers.

Recursive binary search requires sorted ascending input:

```python
def binary_search(numbers, target, left=0, right=None):
    if right is None:
        right = len(numbers) - 1
    if left > right:
        return -1
    middle = (left + right) // 2
    if numbers[middle] == target:
        return middle
    elif numbers[middle] < target:
        return binary_search(numbers, target, middle + 1, right)
    else:
        return binary_search(numbers, target, left, middle - 1)
```

Each call examines the middle and searches exactly one half. Empty range returns `-1`; a match returns its index. Time is O(log n), stack space O(log n).

## 11. Time and space complexity

Count total calls/work for **time**; count maximum simultaneously active stack frames for **recursive auxiliary space**.

- Index-based linear recursion over `n` items: O(n) time, O(n) stack space.
- The slicing version `numbers[1:]` creates a new list at each level. Repeatedly copying the remaining list can make total copying O(n²). Complexity depends on work inside the function, not just the call count.
- Naive Fibonacci: O(2ⁿ) time due to repeated branching/recomputation, but O(n) stack space because one branch is completed/unwound before the other branch is explored.
- Recursive binary search: O(log n) time and O(log n) stack space.
- Merge sort: O(n log n) time. It recursively sorts both halves, then merges them in linear total work per recursion level.

For merge sort:

```python
def merge_sort(items):
    if len(items) <= 1:
        return items
    middle = len(items) // 2
    left_half = merge_sort(items[:middle])
    right_half = merge_sort(items[middle:])
    return merge(left_half, right_half)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

A list of zero or one item is already sorted. Split it, recursively sort both halves, and merge the sorted halves by repeatedly taking the smaller front item. Python's built-in `sorted()` should normally be used in production; it uses Timsort, not this teaching implementation.

## 12. Recursion depth, limits, and `RecursionError`

**Recursion depth** is the maximum number of active frames at one time; it depends on input size and structure.

```python
import sys
print(sys.getrecursionlimit())  # commonly around 1000; varies by environment
```

`sys.setrecursionlimit(5000)` can change the limit, but is rarely the right fix. Raising it does not add memory and can risk a lower-level stack crash. Prefer reducing depth or using iteration for large linear inputs.

```python
def infinite_recursion(n):
    return infinite_recursion(n + 1)
```

This never reaches a base case and eventually raises `RecursionError: maximum recursion depth exceeded`.

Prevention checklist: establish a base case; prove each call progresses; check reachability for every valid input (including empty/zero/negative cases); use iteration for very large linear inputs.

## 13. Debugging and common mistakes

Debug systematically:

1. Test the base case directly.
2. Print each call's input; optionally indent by a `depth` argument to visualize nesting.
3. Hand-trace downward and upward.
4. Check missing `return` and lack of progress first.
5. Temporarily convert to an explicit stack/loop if that clarifies execution.

Common mistakes:
1. No base case.
2. Base case unreachable for some inputs (e.g. subtracting 2 while checking only for zero from odd input).
3. Forgetting to return recursive result.
4. Recursive call makes no progress.
5. Off-by-one boundary (`n == 1` but input may be zero).
6. Mutable default argument (`results=[]`) shared across calls; use `None`, then create a new list inside.
7. Repeated overlapping work (naive Fibonacci).
8. Recursion where a loop/built-in is clearer (`sum`, `max`, `sorted`).
9. Excessive depth for large input.

## 14. Converting recursion to iteration

Linear recursion often converts directly to a loop. An accumulator argument often becomes a loop variable.

Branching/nested recursion needs an explicit stack to represent the pending work:

```python
def flatten_iterative(items):
    result = []
    stack = list(reversed(items))
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(reversed(item))
        else:
            result.append(item)
    return result
```

Reverse items before pushing so LIFO popping preserves original left-to-right order. This avoids Python's recursion-depth limit; memory remains bounded by available memory.

## 15. When recursion or iteration is the better engineering choice

Use recursion when data is inherently nested (trees, folders, nested JSON), divide-and-conquer naturally expresses the algorithm, or exploring choices would require substantial manual bookkeeping—and expected depth is safely bounded.

Use iteration when work is linear, input can be very large, measured function-call overhead matters, or a built-in/standard-library tool already solves the problem. Decide from the data structure and input constraints, not habit.

## 16. General nested-structure processing

```python
def process(data):
    if isinstance(data, list):
        return [process(item) for item in data]
    if isinstance(data, dict):
        return {key: process(value) for key, value in data.items()}
    return transform_leaf(data)
```

Lists and dictionaries are traversed recursively; plain values are leaves and go through `transform_leaf`. This combines comprehensions (apply to every item) with recursion (handle arbitrary nesting). In practice, Python's recursion limit still bounds nesting depth.

## 17. Trees and graphs

A tree has nodes, each with a value and children that are themselves subtrees:

```python
tree = {
    "value": 1,
    "children": [
        {"value": 2, "children": []},
        {"value": 3, "children": [
            {"value": 4, "children": []}
        ]}
    ]
}
```

Sum all values:

```python
def tree_sum(node):
    total = node["value"]
    for child in node["children"]:
        total += tree_sum(child)
    return total
```

Search a tree:

```python
def tree_contains(node, target):
    if node["value"] == target:
        return True
    return any(tree_contains(child, target) for child in node["children"])
```

`any()` short-circuits when a child subtree contains the target. Empty children naturally stop further calls.

A graph can contain cycles, unlike a tree. A recursive graph traversal needs a `visited` set:

```python
def visit_recursive(node, graph, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return
    visited.add(node)
    print(node)
    for neighbor in graph[node]:
        visit_recursive(neighbor, graph, visited)
```

The set prevents revisiting nodes and infinite recursion. This example assumes each neighbor is a key in `graph`; otherwise dictionary lookup raises `KeyError`. Full DFS/BFS and shortest-path algorithms are later topics.

## 18. Backtracking, dynamic programming, and memoization

**Backtracking** explores choices: choose an option, recursively explore what follows, and undo/try another choice when necessary. The chapter's subset example:

```python
def all_subsets(items):
    if not items:
        return [[]]
    first, rest = items[0], items[1:]
    subsets_without_first = all_subsets(rest)
    subsets_with_first = [[first] + subset for subset in subsets_without_first]
    return subsets_without_first + subsets_with_first
```

For `[1, 2]`, output is `[[], [2], [1], [1, 2]]`. Each item is excluded or included. There are 2ⁿ subsets, so output size is exponential. This example illustrates branching choice exploration; classic choose/recurse/undo backtracking and pruning are later topics.

**Dynamic programming** is an optimization approach for problems with:
- **Overlapping subproblems:** the same smaller problem is needed repeatedly.
- **Optimal substructure:** the full answer can be built from subproblem answers.

Fibonacci has both properties. **Memoization** stores a subproblem's answer after its first computation and reuses it later:

```python
def fibonacci_memoized(n, cache=None):
    if cache is None:
        cache = {}
    if n in cache:
        return cache[n]
    if n <= 1:
        return n
    result = fibonacci_memoized(n - 1, cache) + fibonacci_memoized(n - 2, cache)
    cache[n] = result
    return result
```

The cache lookup is checked before recursive work; newly computed answers are stored. Each `n` is computed once, reducing Fibonacci to O(n) time with O(n) cache/stack space.

The standard-library decorator provides memoization:

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_cached(n):
    if n <= 1:
        return n
    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)
```

`lru_cache` caches calls by argument values. Arguments must be hashable. `maxsize=None` means unbounded cache growth; a finite size uses least-recently-used eviction. Prefer it for pure functions with overlapping subproblems and safe-to-cache results. Use a manual cache for custom keying, inspection, or cache behavior.

## 19. Production engineering and industry applications

- Prefer built-ins (`sum`, `max`, `sorted`) when they fit.
- Bound/validate recursion depth on external or untrusted nested input; consider an explicit stack.
- Cache deliberately: memoization consumes memory and is useful when subproblems overlap and results are safe to reuse.
- Document base cases and why progress guarantees termination.
- Measure with `timeit`/`cProfile` before rewriting working code for assumed performance reasons.
- Data Engineering: traverse nested API/configuration data, directories, hierarchies, document trees, and dependency graphs.
- Applied AI: recursively normalize nested feature dictionaries before flattening for model input.
- Large flat transaction datasets generally call for iteration and built-in collection patterns, not deep recursion.

## 20. Refactoring, debugging workshop, and final mental model

Keep base/recursive cases visible; extract complex helper work (as `merge()` is separate from `merge_sort()`); use accumulator-passing or memoization instead of mutable defaults; document what “smaller” means; convert to iteration only when input size, depth, or measured performance warrants it.

The five workshop examples are solved in Part C. Key point: Workshop 5 (`tree_height`) is correct, so verify before changing code.

Before writing recursion, ask:
1. What is the smallest directly answerable input?
2. What exact change makes the next input smaller and guarantees it reaches the base case?
3. Is the structure naturally recursive?
4. Is the expected depth safely bounded, or is an explicit stack safer?

---

# Part B — Your current learning level and roadmap fit

Your project tree places this lesson in **Stage 1 → Module 04 — Problem-Solving, Collections, and Algorithmic Habits**, after search/count/filter/map/aggregate, grouping/deduplication/sorting, Big-O, data-structure selection, and comprehensions/readable code. The supplied Stage 1 tree has 24 modules and four stage-level projects. It progresses from computational thinking, Python types, control flow/functions/errors, and collection problem-solving into files/CLI, modules and code quality, testing, OOP, advanced Python, performance, packaging, CPython internals, security, and code review.

**Current level: beginner progressing toward intermediate.** Your relevant prerequisites are variables, conditionals, loops, functions, lists, dictionaries, sets, indexing/slicing, comprehensions, `isinstance`, `enumerate`, `any`, `sum`, and Big-O. This lesson introduces recursion, call-stack reasoning, trees/graphs, memoization, and divide-and-conquer. The following solutions use the current lesson's recursion concepts and previously covered Python structures; they do not jump into pandas, NumPy, Spark, or later OOP architecture.

---

# Part C — Debugging workshop and all 20 exercises

## Debugging workshop — five diagnoses and fixes

**Workshop 1 — missing base case.** It prints forever and eventually raises `RecursionError`. Add a base case, for non-negative input: `if n == 0: return`; then print and call `count_down_to_zero(n - 1)`.

**Workshop 2 — fails to count current item.** It reaches `[]`, but returns only the remaining list's length, so every non-empty input eventually returns `0`. Fix:

```python
def list_length(items):
    if items == []:
        return 0
    return 1 + list_length(items[1:])
```

**Workshop 3 — no progress.** `exponent` never decreases. Fix `return base * power(base, exponent - 1)` after the zero base case (for non-negative exponent).

**Workshop 4 — shared mutable default.** `found=[]` is created once and reused across separate calls. Fix:

```python
def collect_evens(numbers, found=None):
    if found is None:
        found = []
    if not numbers:
        return found
    if numbers[0] % 2 == 0:
        found.append(numbers[0])
    return collect_evens(numbers[1:], found)
```

**Workshop 5 — already correct.** Empty children return height `1`; otherwise the node height is one plus the maximum child height. No correction is needed.

## Level 1 — Beginner

### 1. `count_down(n)`

```python
def count_down(n):
    if n <= 0:
        return
    print(n)
    count_down(n - 1)
```

Base case stops at zero or below. Otherwise print the current number and recurse with one less. Input is assumed non-negative.

### 2. `sum_to_n(n)`

```python
def sum_to_n(n):
    if n == 0:
        return 0
    return n + sum_to_n(n - 1)
```

Zero contributes zero. For positive `n`, add `n` to the sum from `1` through `n-1`.

### 3. `power_of_two(n)`

```python
def power_of_two(n):
    if n == 0:
        return 1
    return 2 * power_of_two(n - 1)
```

\(2^0=1\). Each recursive step multiplies the smaller power by two.

### 4. `count_items(items)` without `len()`

```python
def count_items(items):
    if items == []:
        return 0
    return 1 + count_items(items[1:])
```

An empty list has zero items. Otherwise count the first item as one and count the tail.

### 5. Trace `factorial(4)`

```text
factorial(4) = 4 * factorial(3)
factorial(3) = 3 * factorial(2)
factorial(2) = 2 * factorial(1)
factorial(1) = 1 * factorial(0)
factorial(0) = 1
```

Unwind: `factorial(1)=1`; `factorial(2)=2`; `factorial(3)=6`; `factorial(4)=24`.

## Level 2 — Intermediate

### 6. `reverse_list(items)`

```python
def reverse_list(items):
    if len(items) <= 1:
        return items
    return reverse_list(items[1:]) + [items[0]]
```

Zero/one item is already reversed. Reverse the tail, then append the original first item. Returns a new list for longer input.

### 7. `is_sorted(numbers)`

```python
def is_sorted(numbers):
    if len(numbers) <= 1:
        return True
    if numbers[0] > numbers[1]:
        return False
    return is_sorted(numbers[1:])
```

A zero/one-item list is sorted. A descending adjacent pair fails immediately; otherwise check the tail. Equal neighbors are allowed (non-decreasing order).

### 8. `sum_of_digits(n)`

```python
def sum_of_digits(n):
    if n < 10:
        return n
    return n % 10 + sum_of_digits(n // 10)
```

A single digit is the base case. Add the last digit to the sum of the remaining digits. Assumes non-negative integer input.

### 9. `flatten_once(items)`

```python
def flatten_once(items):
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result
```

Visit each top-level item. Extend by one nested list's contents, but do not recursively flatten those contents; deeper lists remain nested.

### 10. Iterative `sum_to_n` and compare

```python
def sum_to_n_iterative(n):
    total = 0
    for number in range(1, n + 1):
        total += number
    return total

for value in [0, 1, 5, 10]:
    print(value, sum_to_n(value), sum_to_n_iterative(value))
```

The loop adds each integer to `total`. Both versions should return identical results: `0, 1, 15, 55`.

## Level 3 — Advanced

### 11. Count tree nodes

```python
def tree_count_nodes(node):
    total = 1
    for child in node["children"]:
        total += tree_count_nodes(child)
    return total
```

Count the current node as one. Add the node count of every child subtree. A leaf has no children, so returns one.

### 12. Maximum tree value

```python
def tree_max_value(node):
    largest = node["value"]
    for child in node["children"]:
        child_max = tree_max_value(child)
        if child_max > largest:
            largest = child_max
    return largest
```

Start with the current node's value. Compare each child's subtree maximum and retain the largest. Assumes a non-empty tree and comparable values.

### 13. Memoized Fibonacci and verification

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_memoized(n):
    if n <= 1:
        return n
    return fibonacci_memoized(n - 1) + fibonacci_memoized(n - 2)

for n in range(11):
    print(n, fibonacci(n), fibonacci_memoized(n))
```

Decorator caches each argument's result. Base cases return directly; other values combine the previous two. The loop compares both implementations for 0–10. (Use the chapter's naive `fibonacci` definition for the comparison.)

### 14. Iterative flatten with explicit stack

```python
def flatten_iterative(items):
    result = []
    stack = list(reversed(items))
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(reversed(item))
        else:
            result.append(item)
    return result

sample = [1, [2, [3, [4]]], 5]
print(flatten(sample) == flatten_iterative(sample))  # True
```

Reverse the initial items and each nested list before pushing, so LIFO popping preserves original order. Nested lists are expanded; plain values are appended. This avoids Python call-stack depth limits.

### 15. All permutations of distinct items

```python
def all_permutations(items):
    if not items:
        return [[]]
    result = []
    for index in range(len(items)):
        first = items[index]
        rest = items[:index] + items[index + 1:]
        for tail in all_permutations(rest):
            result.append([first] + tail)
    return result
```

Empty input has one ordering: the empty list. Choose each item as the first item, recursively permute the remaining items, and prepend the chosen item to every result. There are `n!` outputs, so this is only suitable for small lists.

## Level 4 — Production-oriented

### 16. Safe nested dictionary lookup

```python
def deep_get(data, keys):
    if not keys:
        return data
    if not isinstance(data, dict):
        return None
    key = keys[0]
    if key not in data:
        return None
    return deep_get(data[key], keys[1:])
```

No remaining keys means the current value is the answer. Non-dictionary or missing-key paths return `None`. Otherwise recurse into the value using the remaining path.

### 17. Count files in nested folders

```python
def count_files(tree):
    total = len(tree["files"])
    for folder in tree["folders"]:
        total += count_files(folder)
    return total
```

Count files directly in this folder, then add the count from every child folder. A folder with no subfolders stops naturally. Assumes both keys exist and have the specified list shapes.

### 18. Memoized recurrence other than Fibonacci

Use the recurrence `ways(n) = ways(n-1) + ways(n-2) + ways(n-3)` with base values `ways(0)=1`, and zero for negative arguments:

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def ways(n):
    if n == 0:
        return 1
    if n < 0:
        return 0
    return ways(n - 1) + ways(n - 2) + ways(n - 3)
```

This counts ways to reach step `n` using steps of 1, 2, or 3. The same smaller step counts are requested by many branches, so caching avoids recomputing overlapping subproblems.

### 19. Visit graph nodes exactly once

```python
def visit_graph(node, graph, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return
    visited.add(node)
    print(node)
    for neighbor in graph.get(node, []):
        visit_graph(neighbor, graph, visited)
```

Create one visited set for the traversal. Stop if already visited; otherwise mark before visiting neighbors, which prevents cycles. `.get(node, [])` safely treats missing adjacency entries as having no neighbors. Call once with the starting node.

### 20. Justify recursion

A recursive folder traversal is a suitable case: each folder contains files and zero or more subfolders, and every subfolder has the same structure as its parent. The same traversal can therefore process a folder and recursively process each child folder. The base case is a folder with no child folders; expected depth must be bounded. For untrusted or extremely deep folder structures, use an explicit stack instead.

---

# Part D — Mini-project: Nested Configuration Validator and Flattener

## 1. Problem contract

Build a tool for nested configuration made of dictionaries, lists, and leaf values.

- **Allowed leaf types:** `str`, `int`, `float`, `bool`. `None` is invalid.
- **Assumptions:** dictionary keys are strings; the structure is finite and has no cycles.
- **Outputs:** validity flag, leaf count, flattened path/value dictionary, maximum depth, invalid paths.
- **Paths:** dictionary keys use dots (`settings.limits.timeout`); list indexes use brackets (`tags[0]`).
- **Depth convention:** a bare leaf has depth 1; an empty container has depth 1; a container with leaf children has depth 2.
- **Edge cases:** empty dict/list, flat data, nested lists, and `None`.
- **Path caveat:** keys containing `.` can collide with nested paths; production code needs escaping or an unambiguous path format.

## 2. Implementation

```python
ALLOWED_TYPES = (str, int, float, bool)


def flatten_config(data, path="", result=None):
    if result is None:
        result = {}

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            flatten_config(value, new_path, result)
    elif isinstance(data, list):
        for index, value in enumerate(data):
            new_path = f"{path}[{index}]"
            flatten_config(value, new_path, result)
    else:
        result[path] = data

    return result


def count_leaves(data):
    return len(flatten_config(data))


def max_depth(data):
    if isinstance(data, dict) and data:
        return 1 + max(max_depth(value) for value in data.values())
    if isinstance(data, list) and data:
        return 1 + max(max_depth(item) for item in data)
    return 1


def find_invalid_paths(data):
    flat = flatten_config(data)
    return [
        path
        for path, value in flat.items()
        if not isinstance(value, ALLOWED_TYPES)
    ]


def validate_and_report(data):
    invalid_paths = find_invalid_paths(data)
    return {
        "is_valid": len(invalid_paths) == 0,
        "leaf_count": count_leaves(data),
        "flattened": flatten_config(data),
        "max_depth": max_depth(data),
        "invalid_paths": invalid_paths,
    }
```

## 3. Line-by-line explanation

- `ALLOWED_TYPES` stores the permitted Python types in a tuple.
- `flatten_config()` creates a fresh result dictionary only when none was supplied; this avoids a mutable default argument.
- For a dictionary, `.items()` provides each key/value pair. `new_path` joins the parent path and key; recursion processes the value.
- For a list, `enumerate()` supplies each index and value. The path adds `[index]`; recursion processes that value.
- Any other value is a leaf and is stored under its path.
- `count_leaves()` counts the flattened leaf entries.
- `max_depth()` returns one plus the deepest child depth for a non-empty dict/list; leaf and empty-container depth is one.
- `find_invalid_paths()` flattens the structure and returns paths whose values are not allowed types.
- `validate_and_report()` assembles the results into one report.

## 4. Run the example

```python
config = {
    "name": "app",
    "settings": {
        "debug": True,
        "limits": {"max_users": 100, "timeout": None},
    },
    "tags": ["prod", "stable"],
}

report = validate_and_report(config)
print(report["leaf_count"])       # 6
print(report["max_depth"])        # 4
print(report["invalid_paths"])    # ['settings.limits.timeout']
print(report["flattened"])
```

Flattened output:

```python
{
    "name": "app",
    "settings.debug": True,
    "settings.limits.max_users": 100,
    "settings.limits.timeout": None,
    "tags[0]": "prod",
    "tags[1]": "stable",
}
```

There are six leaves. The deepest path has four levels under the project's convention. `None` is the only invalid leaf.

## 5. Complexity and production notes

Let `n` be the total number of leaf and container values.

- Flattening: O(n) traversal time, plus path-string construction; O(n) output space and O(depth) call stack.
- Counting via flattening: O(n) time and O(n) temporary flattened space.
- Depth: O(n) time and O(depth) stack space.
- Validation via flattening: O(n) time and O(n) flattened space.
- The report calls a small constant number of O(n) traversals, so total asymptotic time remains O(n), but it is not a single pass.

For untrusted deeply nested input, validate a maximum depth or convert traversal to an explicit stack. A production validator should also decide how to handle unsupported container types, non-string dictionary keys, and delimiter escaping.

---

# Part E — Review checklist

- [ ] I can explain base case, recursive case, and guaranteed progress.
- [ ] I can trace calls downward and unwind return values upward.
- [ ] I understand stack frames, call-stack space, and recursion depth.
- [ ] I can implement recursion over numbers, strings, lists, dictionaries, and trees.
- [ ] I can explain linear versus branching recursion.
- [ ] I can explain why naive Fibonacci is O(2ⁿ) time but O(n) stack space.
- [ ] I can use memoization and `@lru_cache` when subproblems overlap.
- [ ] I know why graph traversal needs a visited set.
- [ ] I can convert linear recursion to a loop and nested recursion to an explicit stack.
- [ ] I can identify the common base-case, progress, return, and mutable-default bugs.
- [ ] I can justify when recursion is appropriate and when iteration is safer.

**Final principle:** Recursion is a deliberate tool for self-similar and nested problems. It is not a default replacement for loops. Correct base cases, provable progress, bounded depth, and readable code are mandatory.
