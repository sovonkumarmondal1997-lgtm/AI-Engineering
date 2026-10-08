# Big-O Time and Space Complexity

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Answer, for any piece of Python code: *"how does the amount of work
  and memory this code uses change as the input grows?"* — without
  memorizing a table.
- Identify a program's **input size**, count its **meaningful
  operations**, and derive a **Big-O classification** from first
  principles, rather than pattern-matching code shapes to labels.
- Correctly analyze loops, nested loops, sequential operations, early
  termination, and recursive calls — including the common traps where
  intuition ("nested loop = O(n²)") is wrong.
- Distinguish **time complexity** from **space complexity**, and
  **auxiliary space** from **input space**.
- State the typical complexity of common Python list, dictionary, set,
  and string operations, with the correct caveats (average-case,
  amortized, worst-case) rather than absolute claims.
- Recognize **time-space trade-offs** and use them to make deliberate
  engineering decisions — e.g., building an index once to speed up many
  repeated lookups.
- Explain why Big-O is not the same thing as exact runtime, and why
  measurement (not just analysis) is the final word on real performance.
- Apply a repeatable, step-by-step method for analyzing unfamiliar code.

## 2. Why Complexity Matters

Consider:

```python
numbers = list(range(1, 11))   # n = 10
```

Running a loop over `numbers` ten times is trivial — instant, on any
computer built in the last several decades. Now consider the same loop
over:

```python
numbers = list(range(1, 1_000_001))   # n = 1,000,000
```

If the code inside that loop does a *fixed* amount of work per item,
the million-item version simply takes proportionally longer — still
fine. But if the code inside that loop does work that *itself* grows
with the size of `numbers` (for example, another loop, or a linear
search inside the outer loop), the ten-item version might finish
instantly while the million-item version takes minutes, hours, or never
finishes in practice. **The same code can behave completely differently
depending on how its cost grows with input size** — and that growth
pattern is exactly what this chapter teaches you to see.

This matters because **small input can hide an inefficient algorithm.**
Code that scans a list inside a loop works perfectly fine in a quick
test with twenty sample records, passes review, ships — and then falls
over in production when a customer's account has two million
transactions. Complexity analysis lets you reason about scalability
*before* you have that painful surprise, by asking not "does this work?"
but "how does this behave as the data grows?"

This shows up constantly in real engineering work:

- Searching customer records by ID, again and again, for every request.
- Processing a batch of financial transactions overnight.
- Reading and parsing gigabytes of log files.
- Deduplicating millions of ingested records (as in the previous
  chapter).
- Sorting a dataset with tens of millions of rows.
- Preparing training data for a machine learning model.
- Preprocessing a large corpus of documents for retrieval or search.
- Handling a spike in API requests without the service falling over.

In every one of these, the *approach* chosen (not just whether the code
is "correct") decides whether the system works at real scale.

## 3. What Is Input Size?

Before you can talk about how work "grows," you need to name the thing
it grows *with*. That quantity is almost always called **n**, and what
`n` actually represents depends on the problem:

| Data | What `n` means |
|---|---|
| A list | the number of elements |
| A string | the number of characters |
| A dictionary | the number of key-value pairs |
| A matrix / 2D grid | often `n × m` — rows times columns |
| Two separate lists | often two separate sizes, `n` and `m` |
| A graph | typically `V` (vertices) and `E` (edges) — kept only introductory here; graphs are not this chapter's focus |

**Not every problem has just one size variable.** A function that takes
two lists and compares every item in the first against every item in
the second grows with *both* list sizes — describing it with a single
`n` would hide what is actually happening. Always ask, explicitly,
*"what is getting bigger here, and what is it called?"* before trying to
classify anything.

## 4. What Is an Operation?

Big-O does not count individual CPU instructions, machine cycles, or
even individual Python bytecode steps. It reasons about **meaningful
units of work** — the operations whose *count* changes as `n` changes:

- a comparison (`a == b`, `a > b`)
- an arithmetic step (`+`, `*`)
- an assignment (`x = value`)
- a dictionary lookup
- one step of a list traversal
- a function call
- one pass through a loop body

Big-O is an **abstraction** — it deliberately throws away exact timing
detail to focus on *growth*. This means Big-O does not tell you exact
execution time. It also means that a difference in the *raw count* of
operations does not always matter:

```python
def option_a(numbers):
    first = numbers[0]
    second = numbers[0]
    return first

def option_b(numbers):
    return numbers[0]
```

`option_a` does more individual operations than `option_b` — but
neither one's operation count depends on the size of `numbers` at all.
Both are equally O(1): **100 operations and 200 operations are both
O(1)** as long as neither grows when `n` grows. Big-O only cares about
the *shape* of the growth curve, not the exact number of steps at any
one particular `n`.

## 5. What Big-O Means

With input size and "operation" defined, Big-O notation can finally be
introduced as the answer to one question:

> **"As the input size `n` grows, how does the required work grow along
> with it?"**

The common classes you will meet in this chapter, in increasing order of
how badly they scale:

| Notation | Growth intuition | A typical example |
|---|---|---|
| O(1) | stays exactly the same, no matter how big `n` gets | reading `numbers[0]` |
| O(log n) | grows, but very slowly — barely increases even for huge `n` | binary search in a sorted list |
| O(n) | grows in direct proportion to `n` | a single loop over every item |
| O(n log n) | a bit worse than linear, much better than quadratic | comparison-based sorting |
| O(n²) | grows with the *square* of `n` | comparing every item against every other item |
| O(n³) | grows with the *cube* of `n` | three nested loops, each over `n` items |
| O(2ⁿ) | doubles with every additional item | naive recursive Fibonacci (§30) |
| O(n!) | grows faster than any exponential | generating every permutation of `n` items |

This table is a *summary*, not the lesson — every one of these will be
derived from actual code, not memorized from this row, over the rest of
this chapter. If you only remember one thing from this section,
remember the question in bold above, because every classification in
this chapter is really just answering it for one specific piece of
code.

## 6. O(1) — Constant Time

### 6.1 Simple intuition

Some operations take the same amount of work regardless of how large
the input is. Reaching for the first book on a shelf takes the same
effort whether the shelf holds ten books or ten thousand — you already
know exactly where "first" is.

### 6.2 Code and why it is O(1)

```python
numbers = [10, 20, 30, 40, 50]

first = numbers[0]
last = numbers[-1]
```

Python lists store their elements so that any specific position can be
jumped to directly, without walking past the elements before it —
accessing `numbers[0]` does exactly the same thing whether `numbers` has
5 elements or 5 million. **Counting the work:** this is one lookup step,
regardless of `n` — no loop, no scanning. That is the definition of
O(1): the number of operations does not depend on `n` at all.

### 6.3 Dictionary lookup — a preview

```python
users_by_id = {"u1": {"name": "Ada"}, "u2": {"name": "Bob"}}
user = users_by_id["u1"]
```

Dictionary lookup is **typically O(1) average-case** — it does not
generally require scanning every key to find a match, the way a list
would (§7 and §20 explain why in more depth). Note the careful phrasing:
this is not "dictionary lookup is O(1)" as an unconditional law — it is
an average-case expectation under normal conditions, with worst-case
nuances covered later (§20).

### 6.4 What O(1) does *not* mean

**O(1) does not mean "instant."** A single O(1) operation could
still, in absolute terms, take longer than some other O(n) operation on
a tiny input — O(1) says nothing about the actual number of
milliseconds. It only says: *this operation's cost does not grow as `n`
grows.* An O(1) operation on a list of 5 elements and the same O(1)
operation on a list of 5 million elements cost roughly the same amount
— that is the entire claim.

### 6.5 Edge cases and mistakes

- `numbers[0]` on an **empty list** raises `IndexError` — O(1) describes
  cost, not correctness; always confirm the input is non-empty first
  when that matters.
- Do not assume every single-line operation is automatically O(1) —
  `numbers[-1]` is O(1), but `numbers.count(x)` (§18) is not, even
  though both look like "one line."

## 7. O(n) — Linear Time

### 7.1 The simplest growing loop

```python
numbers = [10, 20, 30, 40]

for number in numbers:
    print(number)
```

**Counting the work:** the loop body runs exactly once per item — 4
times for 4 items, 4,000,000 times for 4,000,000 items. If `n` doubles,
the number of loop-body executions roughly doubles too. That
proportional relationship — work scales directly with input size — is
the definition of **O(n)**, linear time.

`sum(numbers)` behaves the same way conceptually: at some level, it
still visits every item exactly once, so it is O(n), even though the
loop itself is hidden inside a fast, built-in implementation (§17 covers
why "built-in" and "fast" are not the same claim as "different Big-O").

### 7.2 List membership: `in`

```python
def contains_value(numbers, target):
    for number in numbers:
        if number == target:
            return True
    return False
```

Checking `x in numbers` on a plain list may, in the worst case, require
examining every single item before concluding the value is absent — this
is why the previous chapter (§17 there) noted that list membership is
generally O(n), in contrast to set membership.

### 7.3 Best case, worst case, and why they can differ

- If `target` is the **first** item, `contains_value` does almost no
  work — this is the **best case**.
- If `target` is the **last** item, or is **absent entirely**, the
  function must check every one of the `n` items — this is the **worst
  case**.

**Do not confuse Big-O with a single, exact best-case runtime.** Saying
"`contains_value` is O(n)" is a statement about how badly the work can
scale — specifically here, about the worst case (§30 covers best/
average/worst case as its own topic in more depth). A function that
happens to run fast on one lucky input is not thereby "O(1)" — you must
consider how it behaves across the full range of possible inputs,
especially the ones that stress it hardest.

## 8. Early Termination

```python
for number in numbers:
    if number == target:
        return True
```

A loop that can `return` (or `break`) before reaching the end of the
collection is said to have **early termination** — introduced as a
pattern already, in the previous module's chapter on search (§4 there).

- If `target` is found near the start, very little work happens.
- If `target` is found near the end — or is absent — the loop still must
  check up to `n` items.

**Early termination does not change the worst-case complexity.** The
function above is still classified as O(n), *because the worst case
still requires n comparisons* — early termination only affects the
best- and average-case behavior, which is why engineers usually still
describe such a function's complexity using its worst case, and treat
early termination as a *practical* speedup rather than a change in
classification (§30 returns to this distinction directly).

## 9. O(log n) — Logarithmic Time

### 9.1 A real-world analogy

Think of finding a word in a large paper dictionary. You do not start at
page one and flip forward one page at a time — you open to roughly the
middle, see whether your word comes before or after that point
alphabetically, and then repeat that "cut the remaining pages roughly in
half" process on whichever half remains. Each step throws away *half*
of what is left to search, so even a dictionary of 100,000 pages can be
searched in only about 17 such steps.

### 9.2 Binary search, conceptually

Given a **sorted** list, the same halving idea works directly:

```
n = 16
after step 1: 8 items remain
after step 2: 4 items remain
after step 3: 2 items remain
after step 4: 1 item remains
```

16 → 8 → 4 → 2 → 1 took 4 steps. In general, the number of times you can
halve `n` before reaching 1 item is `log₂(n)` — for `n = 1,000,000`, that
is only about 20 steps, dramatically fewer than the million steps a
plain linear scan (§7) might need in the worst case.

### 9.3 Python implementation

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

- **`sorted input requirement`** — binary search *only* works correctly
  on data that is already sorted; on unsorted data, discarding "half"
  the remaining items based on one comparison is simply wrong, because
  the target could be anywhere.
- `left` and `right` mark the current boundaries of the region still
  worth searching.
- `middle` is the halfway point between them.
- If the middle value matches, the search is done. If the middle value
  is too small, the target (if present) must be to the right, so `left`
  moves past `middle`; otherwise, it moves `right` before `middle` —
  either way, **half the remaining region is eliminated** on every
  iteration.

### 9.4 Tracing a small example

Searching for `target = 23` in `numbers = [2, 5, 8, 12, 16, 23, 38, 45,
56, 72]` (`n = 10`, indices 0–9):

| step | left | right | middle | `numbers[middle]` | comparison | action |
|---|---|---|---|---|---|---|
| 1 | 0 | 9 | 4 | 16 | 16 < 23 | search right half: `left = 5` |
| 2 | 5 | 9 | 7 | 45 | 45 > 23 | search left half: `right = 6` |
| 3 | 5 | 6 | 5 | 23 | match! | return `5` |

Three steps found the target among ten items — this is the practical
payoff of O(log n).

This implementation is deliberately **iterative** (using a `while`
loop), not recursive — recursion is not required to achieve O(log n),
and an iterative version avoids adding call-stack considerations (§29)
before recursion has even been formally introduced.

### 9.5 Why this is O(log n)

Counting the work: the loop body runs once per halving step, and the
number of times `n` can be halved before reaching a single item is
`log₂(n)`. That is a direct, work-counted derivation of O(log n) — not a
fact to memorize, but a consequence of "cut the problem in half every
step."

## 10. O(n²) — Quadratic Time

### 10.1 Nested loops over the same input

```python
numbers = [1, 2, 3, 4]

for i in numbers:
    for j in numbers:
        print(i, j)
```

**Counting the work:** for *each* of the `n` values of `i`, the inner
loop runs all `n` values of `j` — that is `n` groups of `n`, or `n × n =
n²` total loop-body executions. For `n = 4`, that is 16 print
statements; tracing the first few pairs: `(1,1), (1,2), (1,3), (1,4),
(2,1), (2,2), ...` — every possible pairing of two items, including an
item paired with itself.

### 10.2 A realistic O(n²) problem: finding duplicate pairs

```python
def has_duplicate_pair(numbers):
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i != j and numbers[i] == numbers[j]:
                return True
    return False
```

Every item is compared against every other item — for `n = 4`, up to 16
comparisons in the worst case (fewer with early termination, but the
worst case is still proportional to `n²`).

### 10.3 Nested loops do NOT automatically mean O(n²)

This is one of the most important corrections in this chapter. Compare:

```python
# Nested loop, but the INNER loop's range is fixed, not tied to n.
for i in numbers:            # runs n times
    for j in range(10):      # ALWAYS runs exactly 10 times, no matter how big numbers is
        do_something()
```

**Counting the work:** the outer loop runs `n` times; the inner loop
always runs exactly 10 times, a **constant**, regardless of `n`. Total
work is `n × 10`, and since `10` does not grow with `n`, this is simply
**O(n)** — a nested loop, but linear, not quadratic. The lesson: **you
must check what each loop's bound actually depends on** — a nested loop
is only O(n²) when *both* loops' iteration counts genuinely grow with
`n`. A loop nested inside another loop, where the inner loop's range
depends on something *other* than the overall input size, does not
automatically inherit "quadratic" just because it is visually nested.

## 11. O(n³) — Cubic Time

```python
for i in numbers:
    for j in numbers:
        for k in numbers:
            do_something()
```

**Counting the work:** three nested loops, each iterating over all `n`
items independently, gives `n × n × n = n³` total executions. For `n =
10`, that is 1,000 iterations — manageable; for `n = 1,000`, it is
1,000,000,000 iterations — likely far too slow for most practical
programs. O(n³) is kept intentionally brief here: it is conceptually
identical to O(n²) with one more level of nesting, and it becomes
prohibitively expensive rapidly enough that it is rarely acceptable in
production code operating on non-trivial `n`.

## 12. Analyzing Nested Loops

The examples so far generalize into a repeatable method. Work through
each:

**Example A — both bounds are `n`:**
```python
for i in range(n):
    for j in range(n):
        ...
```
→ **O(n²)** — both loops scale with `n`, so `n × n`.

**Example B — the inner bound is constant:**
```python
for i in range(n):
    for j in range(10):
        ...
```
→ **O(n)** — `10` never grows, so total work is `n × 10`, which
simplifies to O(n) (§13 covers dropping constants formally).

**Example C — the inner bound depends on the outer loop's position:**
```python
for i in range(n):
    for j in range(i):
        ...
```
→ **O(n²)**. This one needs care: the inner loop runs `0` times when `i
= 0`, `1` time when `i = 1`, `2` times when `i = 2`, and so on, up to
`n - 1` times on the last iteration. Total work is the sum
`0 + 1 + 2 + ... + (n - 1)`. Intuitively, this sum is "roughly half of
`n` groups of roughly `n`" — and indeed its exact value is
`n(n-1)/2`, which is dominated by an `n²` term once the lower-order
parts are dropped (§13). This "triangular" loop shape is common enough
to be worth recognizing on sight.

**Example D — the inner loop shrinks geometrically:**
```python
for i in range(n):
    j = 1
    while j < n:
        j *= 2
```
→ **O(n log n)**. The outer loop runs `n` times. For *each* outer
iteration, the inner `while` loop doubles `j` starting from `1` until it
reaches `n` — exactly the halving idea from §9, run in reverse (growing
instead of shrinking), which takes `log₂(n)` steps. So the total work is
`n` outer iterations, each costing `log n` — `n × log n`.

The recurring lesson across all four examples: **always ask what each
loop's bound actually depends on**, rather than assuming a visual
pattern ("this is nested, so it must be n²") tells you the answer.

## 13. Sequential Operations

### 13.1 Two loops, one after another

```python
for x in numbers:
    process_a(x)

for x in numbers:
    process_b(x)
```

**Counting the work:** the first loop does `n` units of work; the
second, separately, does another `n` units of work. Total: `n + n =
2n`. Since `2` does not grow with `n`, this simplifies to **O(n)** — not
O(n²). This is a genuinely common point of confusion: **sequential**
loops (one after the other) add their costs; only **nested** loops
(one inside the other) multiply them.

### 13.2 Combining different complexity classes

```python
for x in numbers:            # O(n)
    process(x)

for i in numbers:            # O(n²)
    for j in numbers:
        compare(i, j)
```

Total cost is `O(n) + O(n²)`. When adding complexities of different
classes, the faster-growing term **dominates** the total as `n` gets
large — `n²` eventually swamps `n` regardless of any constants involved
— so this combination is simply described as **O(n²)**. The `O(n)` part
still does real, measurable work; it is just not the part that decides
how the *overall* cost scales for large `n`.

## 14. Dominant Terms

Formalizing what §13.2 just demonstrated:

```
O(n² + n)           → O(n²)
O(3n + 10)          → O(n)
O(5n² + 2n + 100)   → O(n²)
```

As `n` grows large, lower-order terms (`n` next to `n²`) and constant
multipliers (`5n²` vs. `n²`) become insignificant *relative to the
dominant term* — this is why they are dropped when stating a Big-O
classification. Big-O describes the **shape of the growth curve**, not
an exact formula for operation count.

**This does not mean constants are irrelevant to real-world
performance.** A carefully optimized O(n) algorithm with a large
constant factor (say, `1000n` operations) can genuinely run *slower*, in
real seconds, than an O(n log n) algorithm with a small constant factor
(say, `2n log n`), for any input size where `1000n > 2n log n` — which,
depending on the constants, might hold true for millions of items. Big-O
predicts which algorithm wins **eventually, as `n` grows without
bound** — it makes no promise about which one is faster for the input
sizes you actually have today. This distinction — asymptotic growth
versus real, measured performance — is a mark of engineering maturity,
and it reappears directly in §31 and §37.

## 15. Space Complexity

### 15.1 Time vs. space

So far, every "operation" counted has been about **time** — how much
*work* a piece of code performs. **Space complexity** asks a parallel
question: how much **additional memory** does the code need, beyond
what it was given?

```python
def first_item(numbers):
    return numbers[0]
```

This function creates no new data structures, no matter how large
`numbers` is — it needs exactly one extra "slot" of memory to hold the
returned value. This is **O(1) auxiliary space**.

```python
def copy_numbers(numbers):
    result = []
    for number in numbers:
        result.append(number)
    return result
```

This function builds a brand-new list, `result`, that grows by one
element for every element in `numbers` — for `n` input items, `result`
ends up holding `n` items too. This is **O(n) additional space**.

### 15.2 Input space vs. auxiliary space — be precise

`numbers` itself already occupies memory before either function is even
called — that is the **input space**, and it is not something the
function newly allocated. **Auxiliary space** refers specifically to
*extra* memory the function itself creates beyond its input. Unless a
discussion explicitly concerns *total memory footprint* (input plus
everything else), it is `copy_numbers`'s *new* list — not the pre-
existing `numbers` list it was given — that counts toward its auxiliary
space cost. This distinction matters in practice: a function that reads
its input without copying it is far cheaper in memory than one that
duplicates it, even if both eventually "use" the same amount of total
memory while running.

## 16. Space Used by Loops and Collections

```python
total = 0
for number in numbers:
    total += number
```

- **Time:** O(n) — one loop iteration per item.
- **Additional space:** O(1) — `total` is a single number, updated in
  place; no new per-item storage is created regardless of how large
  `numbers` is.

```python
result = [number * 2 for number in numbers]
```

- **Time:** O(n) — one computation per item.
- **Additional space:** O(n) — `result` holds one new entry per input
  item.

This is a genuine, recurring engineering trade-off: two pieces of code
can have *identical* time complexity, yet very different space
complexity, depending on whether they accumulate a single running value
or build up a whole new collection. Choosing between them is choosing
between memory and having the full result immediately available as a
concrete list.

## 17. Generators and Memory

Recall from the previous chapter's §7.4 and §8.7 the distinction between
a list comprehension and a generator expression:

```python
squares = [x * x for x in numbers]     # builds the WHOLE list right away
squares = (x * x for x in numbers)     # builds nothing yet — produces values one at a time, on demand
```

- The **list comprehension** has O(n) additional space — every squared
  value exists in memory simultaneously, inside `squares`.
- The **generator expression** has O(1) additional space for the
  generator object itself — it computes one squared value at a time,
  only when something asks for the next one, and never holds the whole
  sequence at once.

```python
total = sum(x * x for x in numbers)
```

Here, `sum()` pulls one value from the generator, adds it to a running
total, and discards it, then repeats — an intermediate list of every
`x * x` is never built at all. This is why the previous chapter
recommended dropping the square brackets whenever a comprehension's
result feeds straight into `sum()`, `any()`, `all()`, `min()`, or
`max()`: the *time* complexity (O(n)) is identical either way, but the
*space* complexity drops from O(n) to O(1). This section deliberately
does not re-derive generators from scratch — that groundwork was laid
in the previous chapter; the point here is purely the memory
consequence of laziness.

## 18. Python Operation Complexity

The remaining sections (§19–§22) work through the complexity of
everyday Python operations. Throughout, expect — and use — careful
language: **"typically,"** **"average-case,"** **"depends on
implementation."** Python's built-in types are implemented in highly
optimized C code, but "implemented efficiently" is a separate claim from
"has a particular Big-O classification" — a slow-in-practice O(1)
operation and a fast-in-practice O(n) operation are both possible,
especially for small `n` (§31 returns to this).

## 19. List Complexity

| Operation | Typical complexity | Why |
|---|---|---|
| `numbers[i]` (indexing) | O(1) | Python lists store elements so any index can be jumped to directly. |
| `numbers.append(x)` | O(1) amortized | Usually just places the item in already-reserved space; occasionally the list must grow its underlying storage (§33 explains "amortized"). |
| `numbers.pop()` (from the end) | O(1) | Removing the last item needs no shifting of other elements. |
| `numbers.pop(0)` (from the front) | O(n) | Removing the first item requires shifting every remaining item one position to the left. |
| `numbers.insert(0, x)` | O(n) | Inserting at the front likewise requires shifting every existing item one position to the right. |
| `x in numbers` (membership) | O(n) worst case | May need to scan every item before concluding absence (§7.2). |
| `numbers.count(x)` | O(n) | Must inspect every item to count matches — no early termination possible for an exact count (mirroring the previous chapter's §5). |
| `numbers.remove(x)` | O(n) | Must first *find* `x` (a linear scan), then shift subsequent items left to close the gap. |
| `numbers[2:100]` (slicing) | O(k) | Where `k` is the slice length — slicing **creates a new list**, so its cost (in both time and space) is proportional to the size of the slice, not the original list. |
| `numbers + other_list` (concatenation) | O(n + m) | A new list is built containing every element of both inputs. |

**The key list lesson:** operations at the **end** of a list
(`append`, `pop()`) are typically cheap; operations at the
**beginning** or **middle** (`insert(0, ...)`, `pop(0)`, `remove(x)`)
typically require shifting other elements and cost O(n). This is a
direct, practical consequence of how Python lists are stored in
contiguous memory.

## 20. Dictionary Complexity

| Operation | Typical complexity | Caveat |
|---|---|---|
| `users[user_id]` (lookup) | O(1) average-case | Relies on hashing — see below. |
| `users[user_id] = value` (insertion/update) | O(1) average-case | Same mechanism as lookup. |
| `del users[user_id]` (deletion) | O(1) average-case | Same mechanism. |
| `user_id in users` (membership) | O(1) average-case | Checks keys, as covered in the previous chapter's §4.7. |

(These claims assume the keys are hashable, as `str`, `int`, and `tuple`
of those are.)

**Hash-table intuition, without the internals:** a dictionary computes a
number (a "hash") from a key and uses that number to jump almost
directly to where the corresponding value is stored — this is why
lookup does not typically require scanning every key, unlike list
membership. **Worst-case caveat, stated plainly:** in rare pathological
situations (for example, deliberately crafted keys designed to collide,
or certain adversarial inputs), dictionary operations can degrade from
O(1) average-case to O(n) worst-case when severe hash collisions occur —
this is a real, documented possibility, not just a
theoretical footnote, which is exactly why this chapter says
**"typically O(1) average-case under normal assumptions"** rather than
an unconditional "dictionary lookup is O(1)."

### 20.1 Why dictionaries replace repeated linear search

```python
# Repeated linear search — O(n) EVERY time this runs:
def find_user(users, target_id):
    for user in users:
        if user["id"] == target_id:
            return user
    return None
```

```python
# Build an index once, then look up in O(1) average-case:
users_by_id = {user["id"]: user for user in users}
found = users_by_id.get(target_id)
```

If `find_user` is called once, the linear scan is fine. If it is called
`m` times against the same `users` list, the *total* cost across all
calls is `O(m × n)` — potentially enormous for large `m` and `n`. Building
`users_by_id` once costs O(n), and each subsequent lookup then costs
O(1) average-case, for a total of `O(n + m)` — dramatically better once
`m` is more than a handful. **The trade-off:** building the index costs
time and memory up front, which is only worth it if the lookup will be
performed more than a few times (§23 develops this trade-off fully as
its own topic).

## 21. Set Complexity

| Operation | Typical complexity |
|---|---|
| `x in some_set` (membership) | O(1) average-case |
| `some_set.add(x)` | O(1) average-case |
| `some_set.remove(x)` | O(1) average-case (raises `KeyError` if `x` is absent) |
| `some_set.discard(x)` | O(1) average-case (does nothing if `x` is absent, no error) |

Sets use the same hashing mechanism as dictionaries (§20), which is
exactly why the previous chapter recommended sets for fast membership
testing, and why deduplication with `set()` (previous chapter, §12–§13)
is typically an O(n) average-case operation overall: `n` insertions,
each O(1) average-case, giving O(n) total. This directly connects two
of the biggest practical uses covered previously: **deduplication** and
**membership testing**, both of which rely on this same average-case
O(1) behavior.

## 22. Sorting Complexity

```python
sorted_list = sorted(numbers)     # returns a NEW list
numbers.sort()                    # sorts IN PLACE
```

Both `sorted()` and `list.sort()` have **O(n log n)** worst-case time —
the standard classification for Python sorting, and the well-known
bound for general comparison-based sorting on arbitrary input
(briefly touched on conceptually in the previous chapter's §35, and
revisited only as needed here; the algorithmic internals of sorting are
not this chapter's focus). Python's sort is also **adaptive**: already-
sorted or reverse-sorted input can need only O(n) comparisons, so not
every input requires the full O(n log n) work.

- `sorted()` additionally uses **O(n)** space, because it builds an
  entirely new list.
- `list.sort()` sorts the existing list's storage directly, so it does
  not create a second full result list the way `sorted()` does (though
  the implementation may still use auxiliary working memory internally,
  so do not assume strictly O(1) auxiliary space).
- Python's sort is **stable** (previous chapter, §24) — this does not
  change its Big-O classification, but it does affect the *result* when
  multiple items share a sort key.

**Sorting is more expensive than a single linear pass.** An O(n log n)
operation always eventually costs more than an O(n) operation as `n`
grows, because of that extra `log n` factor — which is precisely why the
previous chapter's §34 advised doing cheaper grouping/aggregation
*before* sorting whenever possible, shrinking the data that the more
expensive sort has to work on.

## 23. Combining Complexities

Real code rarely does just one thing — analyzing a short pipeline means
combining the complexities of each step.

```python
unique = set(numbers)       # O(n) average-case — one pass to insert everything
result = sorted(unique)     # O(k log k) — where k is the number of UNIQUE values
```

- Building `unique` costs O(n) average-case — every one of the `n`
  original items is inserted once.
- Sorting `unique` costs O(k log k), where `k` is the number of distinct
  values (`k = len(unique)`), **not** necessarily `n` — if there were
  many duplicates, `k` could be far smaller than `n`.
- **Total: O(n + k log k).**

Since `k` can never exceed `n` (there cannot be more unique values than
original values), it is also correct — and common — to simplify this to
**O(n log n)** as an overall upper bound. But when duplicates are
expected to be common, keeping the more precise `O(n + k log k)` form
communicates something real: if `k` turns out to be small, this pipeline
is actually much cheaper than a plain O(n log n) sort of the original
data would have been. **Retaining the more precise expression, when it
adds real insight, is a mark of more advanced analysis** — collapsing
everything to the loosest correct bound too early can hide useful
information about where a pipeline's cost is actually coming from.

## 24. Search and Data-Structure Trade-offs

This is one of the most directly useful applications of everything so
far. Consider needing to look up a customer by `customer_id`,
repeatedly, `m` times.

**Approach A — search a list every time:**

```python
def find_customer(customers, target_id):
    for customer in customers:
        if customer["id"] == target_id:
            return customer
    return None
```

Each individual search costs O(n). Performed `m` times, the total cost
is **O(m × n)**.

**Approach B — build a dictionary index once:**

```python
customers_by_id = {c["id"]: c for c in customers}   # O(n) average-case, done ONCE

for target_id in target_ids:                          # m lookups
    found = customers_by_id.get(target_id)             # O(1) average-case each
```

Building the index costs O(n) average-case, done a single time. Each of
the `m` subsequent lookups then costs O(1) average-case. **Total: O(n +
m)** — compare this against Approach A's O(m × n): for any reasonably
large `m`, `O(n + m)` is dramatically smaller than `O(m × n)`.

**The trade-off, stated explicitly:** Approach B costs more **memory**
(an entire second copy of references to every customer, organized by
ID) and a small amount of **upfront preprocessing time** (building the
dictionary), in exchange for making every subsequent lookup far
cheaper. This exact trade-off — pay once, save repeatedly — is one of
the single most common, practically important patterns in real
engineering, and it is worth being able to recognize and justify
explicitly, not just apply by habit.

## 25. Time-Space Trade-offs

Generalizing §24's specific example into a principle:

**"Sometimes we deliberately use more memory to reduce time."**

- A `set` used purely for membership testing (previous chapter, §13.1)
  trades the memory of the set for O(1) average-case lookups instead of
  an O(n) list scan.
- A dictionary index (§24) trades memory for O(1) average-case repeated
  lookups instead of O(n) linear searches.
- **Caching** — storing a computation's result so it does not need to be
  redone — trades memory for avoided recomputation (only the principle
  is introduced here; caching itself is not covered in depth in this
  chapter).
- Precomputed results (e.g., computing a report's totals once and
  storing them, rather than recalculating on every request) trade
  storage for lower repeated-request latency.

**And the reverse is just as real: "sometimes we deliberately use less
memory but perform more work."**

- Recomputing a value each time it is needed, instead of storing it,
  saves memory at the cost of repeated work.
- Generator-based processing (§17) avoids holding a full intermediate
  collection in memory, at the cost of being unable to iterate over the
  same generator twice without recomputation.
- **Streaming** — processing data one chunk at a time instead of loading
  it all into memory at once — trades some processing convenience (and
  sometimes speed) for a dramatically smaller memory footprint, which
  matters enormously when data is too large to fit in memory at all.

Neither direction is universally "better" — the correct choice depends
entirely on which resource (time or memory) is actually scarce for the
problem at hand, and that is an engineering judgment call, not a fixed
rule.

## 26. Real-World Data Engineering Examples

For each: **PROBLEM → NAIVE APPROACH → COMPLEXITY → BETTER APPROACH →
TRADE-OFF.**

**1. Banking — repeated customer lookup.**
PROBLEM: find a customer's account by ID, for every incoming request.
NAIVE: scan the full customer list per request — O(n) per lookup, O(mn)
total for `m` requests. BETTER: build a `customer_id → account`
dictionary once. TRADE-OFF: O(n) preprocessing and extra memory, in
exchange for O(1) average-case lookups afterward — essential once request
volume grows past a handful of lookups.

**2. Log processing — grouping error counts by service.**
PROBLEM: given millions of log lines, count errors per service. NAIVE:
for each service name, scan the entire log file separately — O(s × n)
for `s` services. BETTER: one pass building a `defaultdict(int)` keyed
by service (previous chapter, §6.3) — O(n) total, regardless of how many
distinct services exist. TRADE-OFF: minor extra memory for the
dictionary, in exchange for turning a multiplicative cost into a single
linear pass.

**3. Customer lookup at scale.**
Directly the §24 example — the trade-off there generalizes to any
"look something up by ID, repeatedly" problem, which is extremely
common across backend systems.

**4. Data deduplication.**
PROBLEM: remove duplicate records from a large ingested batch. NAIVE:
compare every record against every other record — O(n²). BETTER: use a
seen-set keyed by the record's identity field (previous chapter, §13–
§14) — O(n) average-case. TRADE-OFF: a set of identity keys costs memory
proportional to the number of unique records, in exchange for avoiding
a quadratic comparison.

**5. Sorting large transaction datasets.**
PROBLEM: rank millions of transactions by amount. NAIVE: sort the *raw*
dataset first, then group/aggregate. BETTER: aggregate/group first
(shrinking to one row per customer or category), then sort the much
smaller aggregated result (previous chapter, §34). TRADE-OFF: when
the requirement is specifically to aggregate/group and then rank the
aggregated result, there is no meaningful semantic trade-off — this
reordering of steps typically costs nothing and saves real time, since sorting (O(n log n)) is more expensive than a single
grouping pass (O(n)).

**6. Data-quality validation.**
PROBLEM: check whether any of a million incoming IDs already exist in a
million-row reference table. NAIVE: for each incoming ID, scan the
reference table — O(n × m). BETTER: load the reference table's IDs into
a set once, then check membership for each incoming ID — O(n + m).
TRADE-OFF: memory proportional to the reference table's size, in
exchange for turning a quadratic-feeling check into a linear one.

**7. ETL processing.**
PROBLEM: a nightly job joins two large tables by a shared key. NAIVE:
for every row in table A, scan all of table B looking for a match —
O(n × m). BETTER: for a many-to-one lookup where the join key is unique in
table B, index table B by that key in a dictionary first, then look up
each row of A against it — O(n + m). (This is a dictionary-index lookup
pattern, not a universal implementation of arbitrary relational joins.) TRADE-OFF: memory to
hold the index, in exchange for turning the join from quadratic to
linear.

**8. AI/ML preprocessing.**
PROBLEM: deduplicate training examples across a large dataset before
training. NAIVE: compare every example against every other example —
O(n²), infeasible for large datasets. BETTER: hash or key each example
(e.g., by normalized text) and use a seen-set — O(n) average-case.
TRADE-OFF: memory for the seen-set, in exchange for a preprocessing step
that would otherwise be completely impractical at real dataset sizes.

**9. Document processing.**
PROBLEM: search a large document collection repeatedly for documents
containing a given term. NAIVE: scan every document's full text on every
search — O(n × document length), every time. BETTER: build an index
once (mapping terms to the documents containing them), then look up a
term directly. TRADE-OFF: substantial memory and upfront indexing time,
in exchange for fast repeated search — the same underlying idea as §24,
scaled up to real search-engine architecture.

## 27. Complexity of Search/Count/Filter/Map/Aggregate

Connecting directly to
[Search, Count, Filter, Map, and Aggregate](01-search-count-filter-map-and-aggregate.md):
every one of those five patterns, in its general form over a plain
list, requires visiting items proportional to `n`:

| Pattern | Typical time | Why |
|---|---|---|
| Search (`in`, `any()`, `next()`) | O(n) worst case | May need to check every item; often better in practice due to early termination (§8). |
| Count (`sum(condition for ...)`, `.count()`) | O(n) | Must inspect every item — no early termination for an exact total. |
| Filter (comprehension, `filter()`) | O(n) | Every item is checked once. |
| Map (comprehension, `map()`) | O(n) | Every item is transformed once. |
| Aggregate (`sum()`, `min()`, `max()`) | O(n) | Every item contributes to the running result. |

Now analyze a composed expression from that chapter's §11:

```python
total = sum(x * 2 for x in numbers if x > 10)
```

**Counting the work:** this is a single pass over `numbers` — for each
item, one comparison (`x > 10`), and, for matching items, one
multiplication and one addition into the running total. All of this is
proportional to `n`, so **time complexity is O(n)**. Because this uses a
generator expression (no square brackets), no intermediate list of
filtered or doubled values is ever built — **additional space is
O(1)**, holding only the running total and the generator's internal
state, regardless of how large `numbers` is.

This is genuinely important: it demonstrates that filtering, mapping,
and aggregating can be **fused into a single O(n) time, O(1) space
pass**, rather than three separate O(n) time, O(n) space steps — a real,
practical performance benefit of the generator-expression style
introduced in the previous chapter, now explained precisely in Big-O
terms.

## 28. Complexity of Grouping/Deduplication/Sorting

Connecting directly to
[Grouping, Deduplication, and Sorting](02-grouping-deduplication-and-sorting.md):

| Pattern | Typical time | Why |
|---|---|---|
| Dictionary-based grouping (`defaultdict`) | O(n) average-case | One pass; each dictionary insert/lookup is O(1) average-case. |
| Set-based deduplication | O(n) average-case | One pass; each set insert/lookup is O(1) average-case. |
| Order-preserving (seen-set) deduplication | O(n) average-case | Same per-item cost, plus building the result list. |
| Sorting | O(n log n) typical | As derived in §22. |

Now analyze a combined pipeline, matching that chapter's §29:

```python
deduplicated = list({t["id"]: t for t in transactions}.values())          # O(n) average-case
completed = [t for t in deduplicated if t["status"] == "completed"]        # O(n)
grouped = defaultdict(list)
for t in completed:
    grouped[t["customer"]].append(t)                                       # O(n) average-case total
totals = {c: sum(t["amount"] for t in txns) for c, txns in grouped.items()}  # O(n) total across all groups
ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)    # O(k log k), k = number of customers
```

**Estimating the total:** every step before the final sort is O(n) (each
one is a single pass, possibly with O(1)-average-case dictionary/set
work per item). The final `sorted()` call costs O(k log k), where `k` is
the number of *distinct customers* — typically much smaller than `n`
(the number of transactions). **Total: O(n + k log k)**, which — since
`k ≤ n` — is bounded above by O(n log n), but in practice is often far
closer to O(n), because the expensive `log` factor only applies to the
small, already-aggregated `k`-sized result, not the full `n`-sized raw
input. This is a direct, worked illustration of the previous chapter's
advice: **group and aggregate before sorting, to shrink what the
expensive O(n log n) step has to operate on.**

## 29. Recursion and Complexity

A full treatment of recursion is a later, dedicated chapter — this
section introduces only what is needed to reason about a recursive
function's complexity.

```python
def countdown(n):
    if n == 0:
        return
    countdown(n - 1)
```

**Counting the work:** `countdown` calls itself once per decrement,
from `n` down to `0` — that is `n + 1` invocations in total
(`countdown(5)` invokes `countdown(5)` through `countdown(0)`, 6 calls),
which is proportional to `n`, so **time is O(n)**.
Each of those calls, though, does not finish and disappear before the
next one starts — a recursive call is placed on the **call stack**,
waiting for the call it made to return, and the calls stack up: calling
`countdown(5)` means there are, at the deepest point, 6 pending calls
sitting on the stack at once (`countdown(5)` waiting on `countdown(4)`
waiting on `countdown(3)`, and so on down to `countdown(0)`). **This
means recursive algorithms can have space complexity too** — here, the
stack depth grows with `n`, giving **O(n) space**, purely from the call
stack itself, even though `countdown` never builds an explicit list or
dictionary of its own.

This is the essential idea to carry forward: **a recursive function's
time complexity depends on how many calls happen; its space complexity
depends on how deep the call stack gets before any call returns** — and
those two numbers are not always the same, once branching recursion
(§30) is involved. The dedicated recursion chapter covers this in much
greater depth; this chapter only needs the connection to time and space
complexity established.

## 30. Exponential and Factorial Complexity

### 30.1 O(2ⁿ) — naive recursive Fibonacci

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

Each call to `fibonacci(n)` (for `n > 1`) makes **two** further
recursive calls, each of which makes two more, and so on. At a high
level (without requiring formal recurrence-relation mathematics): the
total number of calls roughly *doubles* with every additional increase
in `n`, because the branching factor is 2 at (almost) every level. This
gives **O(2ⁿ)** — exponential time. Concretely, `fibonacci(30)` already
requires over a million calls; `fibonacci(40)` requires well over a
billion — the *same* function, run on an input only 10 larger, needs
roughly a thousand times more work, because doubling repeatedly grows
explosively fast. This is exactly why naive recursive Fibonacci is a
classic textbook example of an algorithm that becomes infeasible far
sooner than intuition expects.

### 30.2 O(n!) — generating permutations

Generating every possible ordering ("permutation") of `n` distinct items
requires `n!` (`n` factorial: `n × (n-1) × (n-2) × ... × 1`) total
orderings. For `n = 5`, that is 120 permutations — trivial. For `n =
15`, that is over a trillion — utterly infeasible to generate in full.
Factorial growth is even faster than exponential growth, which is why
brute-force approaches that consider "every possible ordering" of
anything beyond a small `n` are almost never viable in production.

### 30.3 Why these classes matter

O(2ⁿ) and O(n!) both become infeasible so rapidly that recognizing an
algorithm falls into one of these classes is itself an important skill
— it tells you, immediately, that the *naive* approach cannot be used
as-is on any real-sized input, and that either a smarter algorithm
(often exploiting repeated sub-problems, as with Fibonacci — a subject
of later, dedicated study) or a fundamentally different approach is
required.

## 31. Best, Average, and Worst Case

Revisiting §7.3 and §8 more formally: the *same* algorithm can behave
differently depending on the specific arrangement of its input, not
just its size.

Using linear search as the running example:

- **Best case** — the target is the very first item checked; very
  little work is done.
- **Worst case** — the target is the last item checked, or entirely
  absent; the maximum possible amount of work is done.
- **Average case** — considering all the positions the target could
  plausibly be in (or its probability of being absent), the *expected*
  amount of work, on average, across many runs.

**Engineers typically emphasize worst-case guarantees** because they
represent an asymptotic upper bound on growth — the rate at which cost
grows will not be *worse* than this, no matter how unlucky the input is
(it is not an exact runtime guarantee or a fixed numeric ceiling). This
matters enormously for reliability: a system whose worst case is
acceptable will not have unpredictable performance cliffs in
production, even under adversarial or unusual input.

**Big-O notation itself is not synonymous with "worst case."** This is a
precise, important distinction: Big-O is a way of describing *any*
growth bound — you can meaningfully say "the best case is O(1)" (as in
early-termination search) just as validly as "the worst case is O(n)."
Big-O describes *a* growth rate; which case (best, average, or worst)
that growth rate is describing must always be stated separately and
explicitly, rather than assumed.

## 32. Big-O vs Exact Runtime

**Big-O does not equal milliseconds.** Consider two algorithms:

- Algorithm A: does `100n` operations.
- Algorithm B: does `n²` operations.

For small `n` (say, `n = 5`): A does 500 operations, B does 25 — **B is
faster here**, despite B's Big-O classification (O(n²)) being
"worse" than A's (O(n)). For large `n` (say, `n = 10,000`): A does
1,000,000 operations, B does 100,000,000 — now **A is dramatically
faster**. Big-O correctly predicts that A will eventually win as `n`
grows without bound — but it says nothing about which one wins at any
*particular*, finite `n`, and for small enough inputs, the "worse"
classification can easily be faster in practice.

Real, measured runtime is also affected by many factors Big-O
deliberately ignores entirely:

- the specific hardware being used
- the Python interpreter's own overhead per operation
- implementation details of a specific library or built-in
- constant factors hidden inside the "big picture" growth rate
- memory access patterns (some memory access is faster than others,
  independent of algorithmic complexity)
- I/O (disk, network) — often far slower than any in-memory computation
- caching effects (both hardware CPU caches and application-level
  caching)
- system load from other processes running at the same time

**Big-O describes asymptotic growth — how cost scales as input size
grows without bound — not a prediction of exact benchmark results on
your machine, today, for your specific data.** Analysis tells you how
an approach will *scale*; only measurement (§38) tells you how fast it
actually *is*, right now, in your environment.

## 33. Big-O vs Big-Theta vs Big-Omega

Big-O is not the only asymptotic notation, though it is by far the one
you will encounter most often in everyday engineering conversation.
Briefly, at a conceptual level, without formal proofs:

- **O (Big-O)** — describes an **upper bound** on growth: "this
  algorithm's cost grows *no faster than* this rate."
- **Ω (Big-Omega)** — describes a **lower bound** on growth: "this
  algorithm's cost grows *no slower than* this rate."
- **Θ (Big-Theta)** — describes a **tight bound**: growth that is
  *both* upper- and lower-bounded by the same rate — the algorithm's
  cost grows asymptotically at the same rate, not merely "at most" or
  "at least" (this is about growth rate, not exact operation counts).

For example, linear search's worst case is both O(n) (it never does
*more* than n comparisons) and Ω(1) (in the best case, it might do as
little as one comparison) — its best and worst cases differ, so its
*overall* behavior does not have a single tight Θ bound across all
inputs; only specific cases (e.g., "the worst case is Θ(n)") can be
described that tightly. This chapter, and the vast majority of everyday
software engineering discussion, focuses on **Big-O**, because it is the
notation most commonly used in practice for reasoning about "how bad can
this get" — a full, rigorous treatment of Ω and Θ belongs to a formal
algorithms course, not this chapter.

## 34. Amortized Complexity

### 34.1 Why `list.append()` is "O(1) amortized"

Python lists are stored in a block of memory with some extra reserved
capacity beyond their current length. Most calls to `.append()` simply
place the new item into that already-reserved space — genuinely O(1).
Occasionally, though, the reserved space runs out, and the list must
allocate a *larger* block of memory and copy every existing item into
it — an O(n) operation, but one that happens only rarely, and each time
it happens, it grows the reserved capacity by a proportional amount (in CPython,
a roughly constant factor — an implementation detail, not a language
guarantee), making the next resize much further away.

**Amortized analysis** spreads that occasional expensive resize evenly
across the many cheap appends that led up to it — averaged over a long
sequence of appends, the *cost per append* still works out to O(1),
even though a small number of individual appends are, in isolation,
more expensive than the rest. This is why `.append()` is described as
**"O(1) amortized"** rather than a flat, unconditional "O(1)" — the
distinction matters: it is not that every single append is equally
cheap, but that the *average* cost per append, over time, stays
constant. This chapter does not go further into the resizing mechanism
itself — the intuition ("occasional expensive work, spread thin across
many cheap operations") is what matters here.

## 35. How to Analyze Code Step by Step

A repeatable method for approaching unfamiliar code:

1. **Identify input size.** What is `n` here (or `n` and `m`, if there
   are two independent inputs)?
2. **Identify the main operation.** What is the piece of work being
   repeated?
3. **Look for loops.** How many loops are there, and what do they
   iterate over?
4. **Look for nested loops.** Is one loop genuinely inside another? (Not
   just visually indented — actually executed once per outer iteration.)
5. **Look for sequential loops.** Are there multiple loops running one
   after another, rather than nested?
6. **Check whether loops terminate early.** Does a `break` or `return`
   change the best/average case, and does the worst case still require
   the full pass?
7. **Check function calls.** Does the loop call a function whose own
   cost depends on `n`? (A function call inside a loop can hide a second
   source of growth.)
8. **Check data-structure operations.** Are there list, dict, or set
   operations inside the loop, and what does each one typically cost?
9. **Check intermediate collections.** Is a new list, set, or dictionary
   being built? That affects space complexity, and possibly time.
10. **Identify dominant growth.** Once every piece of work is counted,
    which term grows fastest as `n` increases?
11. **State time complexity**, in Big-O terms, including which case
    (best/average/worst) it describes if that is not obvious.
12. **State auxiliary space complexity**, separately from time.

This ordered checklist is deliberately the same shape as the worked
examples in the next section — apply it explicitly, in order, rather
than guessing from the code's general "shape."

## 36. Worked Complexity Examples

**1. Constant time**
```python
def first(numbers):
    return numbers[0]
```
Step 1: `n = len(numbers)`. Steps 3–9: no loop, no data-structure scan,
no intermediate collection — just one direct index access. **Time:
O(1). Space: O(1).**

**2. Linear loop**
```python
def print_all(numbers):
    for number in numbers:
        print(number)
```
One loop, running once per item, no early termination, no nested
work. **Time: O(n). Space: O(1)** (no new collection is built).

**3. Linear search**
```python
def contains(numbers, target):
    for number in numbers:
        if number == target:
            return True
    return False
```
One loop with early termination (§8) — best case can be as little as
one comparison, but the worst case (target absent, or last) requires
all `n` comparisons. **Time: O(n) worst case. Space: O(1).**

**4. Two sequential linear loops**
```python
def process(numbers):
    for x in numbers:
        step_one(x)
    for x in numbers:
        step_two(x)
```
Two separate loops, one after another (not nested), each O(n) — total
`2n`, which simplifies (§14) to **Time: O(n). Space: O(1)** (assuming
`step_one`/`step_two` do not themselves build growing collections).

**5. Nested loops (both bounds `= n`)**
```python
def all_pairs(numbers):
    for i in numbers:
        for j in numbers:
            print(i, j)
```
Inner loop genuinely runs `n` times for each of the `n` outer
iterations — `n × n`. **Time: O(n²). Space: O(1)**, since nothing is
stored — only printed.

**6. Nested loop with a fixed inner bound**
```python
def sample_each(numbers):
    for x in numbers:
        for i in range(5):
            print(x, i)
```
The inner loop's bound (`5`) never grows with `n` — total work is
`n × 5`. **Time: O(n)**, not O(n²) (§10.3). **Space: O(1).**

**7. Triangular nested loop**
```python
def pairs_once(numbers):
    n = len(numbers)
    for i in range(n):
        for j in range(i):
            print(numbers[i], numbers[j])
```
The inner loop's bound depends on `i`, running `0, 1, 2, ..., n-1` times
across the outer iterations — total `0 + 1 + ... + (n-1)`, which
simplifies to an `n²`-dominated expression (§12, Example C). **Time:
O(n²). Space: O(1).**

**8. Logarithmic loop**
```python
def count_halvings(n):
    steps = 0
    while n > 1:
        n = n // 2
        steps += 1
    return steps
```
Each iteration halves `n`; the number of halvings before reaching `1`
is `log₂(n)`. **Time: O(log n). Space: O(1).**

**9. `n log n` loop (nested, one dimension logarithmic)**
```python
def repeated_halving(n):
    for i in range(n):
        j = 1
        while j < n:
            j *= 2
```
Directly Example D from §12: the outer loop runs `n` times, and for
each of those, the inner loop runs `log n` times. **Time: O(n log n).
Space: O(1).**

**10. Sorting**
```python
def get_ranked(numbers):
    return sorted(numbers)
```
One call to `sorted()` — as derived in §22. **Time: O(n log n). Space:
O(n)** (a brand-new list is returned).

**11. Dictionary lookup**
```python
def lookup_many(users_by_id, target_ids):
    return [users_by_id.get(tid) for tid in target_ids]
```
Input size here is really `m = len(target_ids)` — the loop runs `m`
times, and each `.get()` call costs O(1) average-case (§20). **Time:
O(m) average-case. Space: O(m)** (the result list holds one entry per
target ID).

**12. Set membership**
```python
def keep_known(items, known_set):
    return [item for item in items if item in known_set]
```
One pass over `items` (length `n`); each `in known_set` check costs
O(1) average-case (§21, assuming hashable items), regardless of `known_set`'s own size. **Time:
O(n) average-case. Space: O(n)** in the worst case (if every item is
kept).

**13. Filter + map + aggregate (generator, one pass)**
```python
def total_large_doubled(numbers):
    return sum(x * 2 for x in numbers if x > 10)
```
Exactly §27's worked example. **Time: O(n). Space: O(1)** — no
intermediate list is built.

**14. Deduplicate + sort**
```python
def unique_sorted(numbers):
    return sorted(set(numbers))
```
Exactly §23's worked example. **Time: O(n + k log k)**, where `k =
len(set(numbers))` — often expressed loosely as O(n log n) since `k ≤
n`. **Space: O(k)** for the set, plus O(k) for the sorted result — O(k)
overall, since both are proportional to the number of unique values.

**15. Build dictionary + repeated lookup**
```python
def enrich(records, lookup_source):
    index = {item["id"]: item for item in lookup_source}   # O(n) average-case, n = len(lookup_source)
    return [index.get(r["id"]) for r in records]             # O(m) average-case, m = len(records)
```
Exactly §24's pattern, with two independent input sizes named
explicitly. Building `index` costs O(n) average-case; the subsequent
loop costs O(m) average-case. **Time: O(n + m) average-case. Space:
O(n)** for the index, plus O(m) for the result list — O(n + m) overall.

## 37. Common Mistakes

1. **Thinking every loop is O(n).** A loop's complexity depends on what
   it iterates over and how many times — a loop with a fixed, constant
   bound (`for j in range(10)`) is O(1), regardless of appearances.
   *Correction:* always check what the loop's bound actually depends on.

2. **Thinking every nested loop is O(n²).** As shown directly in §10.3
   and worked example 6 — a nested loop is only O(n²) if *both* loops'
   iteration counts genuinely scale with `n`. *Correction:* analyze each
   loop's bound independently.

3. **Counting constants incorrectly** — treating `O(3n)` as somehow
   different from `O(n)`, or assuming a constant factor changes the
   classification. *Correction:* constants are dropped in Big-O (§14),
   though they can still matter for real, measured performance (§32).

4. **Forgetting to define input size at all** before attempting to
   classify complexity — leading to vague or meaningless statements like
   "this is O(n)" without saying what `n` refers to. *Correction:*
   always state `n` (or `n` and `m`) explicitly, as step 1 of §35's
   method.

5. **Confusing memory with time** — describing a function's space
   requirements when asked about its time cost, or vice versa.
   *Correction:* always state both separately; they are frequently
   different for the exact same function (§15–§17).

6. **Ignoring intermediate lists** — believing a list comprehension and
   an equivalent generator expression have identical costs, because
   their *time* complexity happens to match. *Correction:* always check
   for intermediate collections when assessing space (§17, §27's
   `sum(generator)` example).

7. **Assuming built-ins are always O(1)** just because they are single
   function calls — `sum()`, `.count()`, `sorted()`, and many others are
   *not* O(1); they are fast, optimized implementations of operations
   that are still fundamentally O(n) or worse. *Correction:* classify
   the *operation* itself, independent of whether it happens to be
   spelled as one Python word.

8. **Assuming dictionary operations have no caveats** — stating "O(1)"
   unconditionally rather than "O(1) average-case." *Correction:*
   always include the average-case qualifier for hash-based structures
   (§20).

9. **Confusing Big-O with exact runtime** — assuming an O(n) algorithm
   is always faster in practice than an O(n²) one, for any input size.
   *Correction:* remember §32 — Big-O predicts eventual, large-`n`
   behavior, not performance at any specific, possibly small, `n`.

10. **Confusing best case with worst case** — quoting an algorithm's
    best-case behavior (e.g., "search is O(1) because I got lucky and
    found it first") as if it were its general classification.
    *Correction:* be explicit about which case is being described (§31).

11. **Ignoring sorting cost** in a pipeline — treating a `sorted()` call
    as "free" or trivial compared to the surrounding O(n) steps, when it
    is actually the pipeline's most expensive part (§22, §28).
    *Correction:* always account for sorting's O(n log n) cost
    explicitly when it appears.

12. **Ignoring preprocessing cost** — celebrating an O(1) average-case
    lookup while forgetting the O(n) cost of building the index that
    made it possible. *Correction:* always account for the full pipeline
    (§24), not just its cheapest step.

13. **Forgetting repeated function calls** inside a loop — a function
    call that looks like "one operation" inside a loop body can itself
    be O(n), silently turning an apparent O(n) loop into O(n²) overall.
    *Correction:* check the complexity of every function called inside a
    loop, not just the loop's own iteration count.

14. **Forgetting recursion's call-stack space** — analyzing only a
    recursive function's time complexity and overlooking that its call
    depth also consumes memory (§29). *Correction:* consider both time
    and stack-space cost for any recursive function.

15. **Assuming a shorter program is automatically faster.** A five-line
    nested-loop solution can be O(n²), while a longer solution using a
    dictionary index can be O(n) — line count says nothing about
    complexity. *Correction:* judge by growth behavior, not code length.

16. **Optimizing before measuring.** Rewriting code to "improve" its
    complexity when the actual bottleneck lies elsewhere (I/O, network,
    a different function entirely) wastes effort and adds needless
    complexity. *Correction:* measure first (§38), then optimize the
    confirmed bottleneck.

17. **Using Big-O labels without understanding the actual operation
    behind them** — reciting "O(1)" or "O(n log n)" from memory for a
    function without having actually counted its operations.
    *Correction:* always be able to explain *why* a classification
    holds, by walking through the code, as every section of this chapter
    has done.

## 38. Debugging and Measuring Performance

Complexity analysis **predicts how cost scales**; it does not tell you
the exact number of seconds your program will take on your machine,
today. That final answer requires **measurement**.

### 38.1 `timeit` — benchmarking small pieces of code

```python
import timeit

def linear_search(numbers, target):
    return target in numbers

numbers = list(range(10_000))
duration = timeit.timeit(lambda: linear_search(numbers, -1), number=100)
print(duration)   # total seconds for 100 runs
```

`timeit` runs a small snippet many times and reports how long it took
in total, averaging out noise from any single run — it is the right
tool for comparing two small alternative implementations directly
against each other.

### 38.2 `cProfile` — profiling a larger program

```python
import cProfile

def run_pipeline():
    # ... a larger sequence of operations ...
    pass

cProfile.run("run_pipeline()")
```

`cProfile` runs an entire program (or function) and reports how much
time was spent inside *each* function it called — useful for finding
*which part* of a larger, multi-step program is actually the slow part,
rather than guessing.

### 38.3 The workflow

```
ANALYZE FIRST → MEASURE → IDENTIFY BOTTLENECK → OPTIMIZE → MEASURE AGAIN
```

Complexity analysis (this entire chapter) tells you *where to look* and
*what to expect* as data grows. `timeit` and `cProfile` tell you *what is
actually happening*, right now, in your specific program. Neither
replaces the other: analysis without measurement risks optimizing the
wrong thing (mistake #16, §37); measurement without any complexity
understanding risks endlessly re-benchmarking small variations of a
fundamentally poor approach, without ever reaching for a genuinely
better algorithm or data structure. This chapter is not a profiling
tutorial — the goal here is only to know that these tools exist and
where they fit in the overall workflow.

## 39. Testing Complexity Reasoning

Attempt to answer each question *before* checking §46's answer key.

**Q1.**
```python
def total(numbers):
    result = 0
    for number in numbers:
        result += number
    return result
```
What is `n`? Time complexity? Auxiliary space? Why?

**Q2.**
```python
def has_pair_summing_to(numbers, target):
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i != j and numbers[i] + numbers[j] == target:
                return True
    return False
```
What is `n`? Time complexity? Auxiliary space? Why?

**Q3.**
```python
def first_ten(numbers):
    result = []
    for number in numbers:
        if len(result) >= 10:
            break
        result.append(number)
    return result
```
What is `n`? Time complexity (best and worst case)? Auxiliary space?
Why?

**Q4.**
```python
def build_index(records):
    return {r["id"]: r for r in records}
```
What is `n`? Time complexity? Auxiliary space? Why?

**Q5.**
```python
def unique_count(items):
    return len(set(items))
```
What is `n`? Time complexity? Auxiliary space? Why?

**Q6.**
```python
def process(numbers):
    for x in numbers:
        for y in range(3):
            print(x, y)
```
What is `n`? Time complexity? Auxiliary space? Why?

**Q7.**
```python
def sum_of_squares_over_10(numbers):
    return sum(x * x for x in numbers if x > 10)
```
What is `n`? Time complexity? Auxiliary space? Why?

## 40. Progressive Coding Exercises

Full solutions and reasoning appear in **§46 — Answer Key / Solutions**.

### Level 1 — Foundation

**1. Identify `n`.** For each snippet, state what `n` represents:
`process_users(user_list)`; `count_characters(text)`;
`compare_grids(grid_a, grid_b)`.

**2. Classify simple loops.** Classify each as O(1), O(n), or something
else: `for x in items: print(x)`; `x = items[3]`; `for x in items:
    for y in range(4): print(y)`.

**3. Identify O(1).**
```python
def get_middle(items):
    return items[len(items) // 2]
```
State the time and space complexity, with reasoning.

**4. Identify O(n).**
```python
def double_all(items):
    return [x * 2 for x in items]
```
State the time and space complexity, with reasoning.

**5. Identify O(n²).**
```python
def print_grid(items):
    for row in items:
        for value in row:
            print(value)
```
State `n` carefully — is this really O(n²), or something else? Hint:
think about what `items` actually contains.

### Level 2 — Intermediate

**6. Analyze nested loops.**
```python
def compare_all(items):
    matches = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                matches += 1
    return matches
```

**7. Analyze sequential loops.**
```python
def summarize(items):
    total = sum(items)
    maximum = max(items)
    return total, maximum
```

**8. Analyze dictionary lookup.**
```python
def get_all(index, ids):
    return [index.get(i) for i in ids]
```
Identify both input sizes involved.

**9. Analyze set membership.**
```python
def filter_known(items, known):
    return [x for x in items if x in known]
```

**10. Analyze sorting.**
```python
def top_three(items):
    return sorted(items, reverse=True)[:3]
```
Consider both the sort and the slice.

### Level 3 — Advanced

**11. Analyze generator-based pipelines.**
```python
def average_over_threshold(items, threshold):
    matching = (x for x in items if x > threshold)
    total = 0
    count = 0
    for x in matching:
        total += x
        count += 1
    return total / count if count else 0
```

**12. Analyze deduplication + sorting.**
```python
def ranked_unique(items):
    return sorted(set(items), reverse=True)
```

**13. Analyze dictionary indexing + repeated lookup.**
```python
def enrich_orders(orders, customers):
    index = {c["id"]: c for c in customers}
    return [
        {"order": o, "customer": index.get(o["customer_id"])}
        for o in orders
    ]
```
Identify both input sizes and state the total complexity in terms of
both.

**14. Analyze multiple nested operations.**
```python
def build_pairs_report(items):
    pairs = []
    for i in items:
        for j in items:
            if i != j:
                pairs.append((i, j))
    return sorted(pairs)
```

**15. Analyze time-space trade-offs.**
Compare, in both time and space: searching a list of one million
customer records `1,000` times using a plain linear scan each time,
versus building a dictionary index once and performing the same 1,000
lookups against it.

### Level 4 — Production

**16. Analyze a transaction-processing pipeline.**
```python
def process_transactions(transactions):
    seen_ids = set()
    unique = []
    for t in transactions:
        if t["id"] not in seen_ids:
            seen_ids.add(t["id"])
            unique.append(t)

    completed = [t for t in unique if t["status"] == "completed"]
    total = sum(t["amount"] for t in completed)
    return total
```

**17. Analyze log aggregation.**
```python
from collections import defaultdict

def count_by_service_and_severity(logs):
    counts = defaultdict(lambda: defaultdict(int))
    for log in logs:
        counts[log["service"]][log["severity"]] += 1
    return counts
```

**18. Analyze customer lookup architecture.**
Given a system that must serve `m` customer-lookup requests per minute
against a table of `n` customers that rarely changes, propose and
analyze an architecture, stating the complexity of both the setup step
and each request.

**19. Analyze data deduplication.**
```python
def deduplicate_by_composite_key(records):
    seen = set()
    result = []
    for r in records:
        key = (r["customer_id"], r["date"])
        if key not in seen:
            seen.add(key)
            result.append(r)
    return result
```

**20. Analyze a preprocessing pipeline for AI/ML data.**
```python
def prepare_dataset(examples):
    cleaned = [ex for ex in examples if ex["text"].strip()]
    seen_texts = set()
    unique = []
    for ex in cleaned:
        normalized = ex["text"].strip().lower()
        if normalized not in seen_texts:
            seen_texts.add(normalized)
            unique.append(ex)
    return sorted(unique, key=lambda ex: len(ex["text"]))
```

## 41. Mini Project — Performance Analysis of a Transaction Pipeline

### The naive implementation

```python
def naive_pipeline(transactions, lookup_ids):
    # 1. Search transactions repeatedly using a list.
    def find_transaction(transaction_id):
        for t in transactions:
            if t["id"] == transaction_id:
                return t
        return None

    found = [find_transaction(tid) for tid in lookup_ids]

    # 2. Deduplicate by transaction ID, keeping the first record
    #    (accidentally O(n²) here).
    unique = []
    for t in transactions:
        if not any(u["id"] == t["id"] for u in unique):   # linear scan of a growing LIST!
            unique.append(t)

    # 3. Group transactions by customer.
    grouped = {}
    for t in unique:
        customer = t["customer"]
        if customer not in grouped:
            grouped[customer] = []
        grouped[customer].append(t)

    # 4. Calculate totals.
    totals = {}
    for customer, txns in grouped.items():
        total = 0
        for t in txns:
            total += t["amount"]
        totals[customer] = total

    # 5. Sort customers by spending.
    ranking = sorted(totals.items(), key=lambda item: item[1], reverse=True)

    return found, ranking
```

### A. Analyze the naive implementation

- **Step 1 (repeated search):** `find_transaction` is O(n) per call; it
  is called once per ID in `lookup_ids` (size `m`). Total: **O(m × n)**.
- **Step 2 (deduplication):** the `any(u["id"] == t["id"] for u in unique)` check scans the
  *entire*, growing `unique` list for every single transaction — this is a
  disguised **O(n²)** operation, even though it does not look like a
  nested loop at first glance (each `.append` grows `unique`, and the
  membership check itself is a hidden linear scan performed once per outer
  transaction).
- **Steps 3–4 (grouping and totals):** each is a single pass, O(n)
  overall.
- **Step 5 (sorting):** O(k log k), where `k` is the number of distinct
  customers.
- **Overall naive complexity: O(m × n + n² + k log k)** — dominated by
  whichever of `m × n` or `n²` is larger, both of which scale poorly for
  large `n`.

### B. Identify bottlenecks

- **Time bottleneck:** step 2's linear scan of `unique` is the worst offender
  — it silently reintroduces O(n²) behavior into what should have been
  an O(n) deduplication pass (exactly the kind of hidden-quadratic-cost
  mistake this chapter has emphasized spotting).
- **Time bottleneck:** step 1's repeated linear search is O(m × n) — for
  any non-trivial `m`, this dwarfs everything else.
- **Space bottleneck:** none especially severe here, though `unique`,
  `grouped`, and `totals` each hold data proportional to `n` or fewer,
  which is expected and reasonable.

### C. A better approach

```python
from collections import defaultdict

def improved_pipeline(transactions, lookup_ids):
    # 1. Build an index ONCE for repeated lookups — O(n) average-case.
    #    Keep the FIRST record per ID, matching the deduplication below.
    by_id = {}
    for t in transactions:
        by_id.setdefault(t["id"], t)
    found = [by_id.get(tid) for tid in lookup_ids]           # O(m) average-case

    # 2. Deduplicate with a set-backed seen-check — O(n) average-case.
    seen_ids = set()
    unique = []
    for t in transactions:
        if t["id"] not in seen_ids:
            seen_ids.add(t["id"])
            unique.append(t)

    # 3. Group by customer with defaultdict — O(n).
    grouped = defaultdict(list)
    for t in unique:
        grouped[t["customer"]].append(t)

    # 4. Totals per group — O(n) total across all groups.
    totals = {
        customer: sum(t["amount"] for t in txns)
        for customer, txns in grouped.items()
    }

    # 5. Sort the much smaller, aggregated result — O(k log k).
    ranking = sorted(totals.items(), key=lambda item: item[1], reverse=True)

    return found, ranking
```

### D. Recalculated complexity

- Step 1: O(n) to build `by_id`, then O(m) average-case for all `m`
  lookups — **O(n + m)**, replacing the naive O(m × n).
- Step 2: O(n) average-case — replacing the naive O(n²).
- Steps 3–4: O(n), unchanged in shape from the naive version (these were
  never the problem).
- Step 5: O(k log k), unchanged.
- **Overall improved complexity: O(n + m + k log k)** — a dramatic
  improvement over O(m × n + n²) for any non-trivial `n` and `m`.

### E. The time-space trade-off

The improved pipeline uses **more memory**: `by_id` and `seen_ids` each
hold additional data proportional to `n`, on top of everything the
naive version already stored. In exchange, it converts two of the
naive version's costliest operations from `O(m × n)` and `O(n²)` down to
`O(n + m)` and `O(n)` respectively — for a dataset with, say, `n =
100,000` transactions and `m = 1,000` lookups, this is the difference
between roughly 100 million+ operations and roughly 101,000 operations.
**This mini project's core lesson:** complexity analysis is not an
academic exercise performed for its own sake — it directly informed a
concrete, justified engineering decision (spend a modest, bounded amount
of extra memory on two dictionaries/sets) that turned an approach which
would struggle badly at real production scale into one that scales
comfortably.

## 42. Interview Questions

**Foundational**

- What is Big-O, in your own words?
- Why do engineers use Big-O instead of just measuring runtime directly?
- What is O(1)? What is O(n)? What is O(log n)? What is O(n²)?
- What is the typical complexity of list membership (`in`)? Why?
- What is the typical complexity of dictionary lookup? Why is it phrased
  as "typical" or "average-case" rather than absolute?
- Why is set membership useful, and what is its typical complexity?
- What is the typical complexity of `sorted()`?

**Intermediate**

- What is auxiliary space, and how does it differ from input space?
- What is the difference between a function that is O(n) in time versus
  one that is O(n) in space? Can a function be both, independently?
- What is amortized complexity? Why is `list.append()` described as
  "O(1) amortized" rather than plain O(1)?
- What happens to overall complexity when two O(n) loops run one after
  another? What about when an O(n) operation and an O(n²) operation are
  combined?
- Why does early termination (e.g., a `break` inside a search loop) not
  necessarily change an algorithm's worst-case complexity?
- How can preprocessing (e.g., building an index) improve the total cost
  of many repeated lookups?
- What is a time-space trade-off? Give a concrete example.

**Advanced**

- What is the difference between Big-O, Big-Omega, and Big-Theta?
- Why doesn't a nested loop automatically imply O(n²)? Give an example
  where it does not.
- Compare `countdown(n)` (which calls itself once with `n - 1`) with a
  loop that counts from `n` down to `0`. Both do O(n) work in total, but
  how do their recursion depth / call-stack space differ, and why does
  the number of total calls not by itself determine space complexity?
- Why can an O(n) algorithm with a large constant factor be slower, in
  practice, than an O(n log n) algorithm for realistic input sizes? What
  does this imply about relying on Big-O alone when choosing between two
  specific implementations?

**Code-based**

- "Here is a function that checks `item not in growing_list` inside a
  loop that also appends to `growing_list`. What is its actual time
  complexity, and why is it worse than it might look at first glance?"
  (See §41's naive deduplication step.)
- "Given this nested loop, where the inner loop's range is `range(20)`
  regardless of the input, what is the time complexity, and why is it
  not O(n²)?"
- "Given `sorted(set(large_list))`, walk through the complexity of each
  step and give a combined expression, then simplify it to a single
  Big-O bound."

## 43. Complexity Cheat Sheet

| Notation | Intuition | Common example | Typical qualifier |
|---|---|---|---|
| O(1) | cost does not change as `n` grows | list indexing, dict lookup | average-case for dict/set |
| O(log n) | grows very slowly; halves the problem each step | binary search | typical, given sorted input |
| O(n) | grows directly proportional to `n` | a single loop over all items | worst-case commonly cited |
| O(n log n) | a bit worse than linear | comparison-based sorting | typical |
| O(n²) | grows with the square of `n` | comparing every item against every other item | — |
| O(n³) | grows with the cube of `n` | triple-nested loop over `n` | rarely acceptable in production |
| O(2ⁿ) | doubles with each additional item | naive recursive Fibonacci | infeasible beyond small `n` |
| O(n!) | grows faster than exponential | generating all permutations | infeasible beyond very small `n` |

**Practical Python operation reference** (see §19–§22 for full detail
and caveats):

| Operation | Typical complexity |
|---|---|
| `list[i]` | O(1) |
| `list.append(x)` | O(1) amortized |
| `list.pop()` | O(1) |
| `list.pop(0)` / `list.insert(0, x)` | O(n) |
| `x in list` | O(n) worst case |
| `list.count(x)` / `list.remove(x)` | O(n) |
| `list[a:b]` (slicing) | O(k), k = slice size |
| `dict[key]` / `key in dict` / insert / delete | O(1) average-case |
| `set` membership / `add` / `remove` / `discard` | O(1) average-case |
| `sorted(x)` / `x.sort()` | O(n log n) typical |
| `sum()` / `min()` / `max()` / `any()` / `all()` | O(n) |

Every entry above carries the qualifiers spelled out in its originating
section — this table is a *reminder*, not a substitute for
understanding *why* each value holds, per §18's opening caution.

## 44. Engineering Decision Framework

When you encounter unfamiliar code and need to judge whether — and how —
to act on its complexity:

1. What is the input size (or sizes)?
2. What work happens exactly once?
3. What work repeats, and how many times?
4. Are there nested loops, and do both bounds actually depend on `n`?
5. Are there sequential (not nested) operations whose costs simply add?
6. Can a loop stop early, and does that change the best/worst case
   differently?
7. What data structures are being used, and what does each relevant
   operation on them typically cost?
8. Are intermediate collections being created, and do they matter for
   this analysis?
9. What is the total time complexity, stated with the correct case
   (best/average/worst)?
10. What is the auxiliary space complexity?
11. Could spending more memory (a set, a dictionary index, caching)
    reduce the time cost meaningfully?
12. **Is optimization actually necessary right now?** Does this code run
    on data large enough, or often enough, for its complexity to matter
    in practice?
13. Have you benchmarked or profiled (§38) before changing anything, to
    confirm this actually is the bottleneck?

**Do not optimize only because something *looks* complex.** A nested
loop over a list of 20 items is not a production emergency. First
understand the actual workload (how large is `n`, realistically, in
production, and how often does this code run?); then measure, if there
is any doubt; only then optimize the confirmed bottleneck — and
re-measure afterward to confirm the change actually helped.

## 45. Final Review

- **Big-O** describes how the required work (time) or memory (space)
  grows as **input size (`n`)** grows — it is an abstraction over
  *meaningful operations*, not exact instruction counts or runtimes.
- **O(1)** — constant, does not grow with `n`. **O(log n)** — grows very
  slowly, typically from repeatedly halving a problem. **O(n)** — grows
  directly with `n`. **O(n log n)** — a bit worse than linear, typical
  of comparison-based sorting. **O(n²)** and **O(n³)** — grow with the
  square/cube of `n`, from (genuinely) nested loops. **O(2ⁿ)** and
  **O(n!)** — grow so explosively they are infeasible beyond small `n`.
- **Sequential** operations *add* their costs (and the dominant term
  wins); **nested** operations *multiply* theirs — confusing the two is
  a classic mistake, as is assuming every nested loop is automatically
  O(n²) without checking what each loop's bound actually depends on.
- Constants and lower-order terms are dropped when stating Big-O, but
  they still matter for real, measured performance at small or
  moderate `n` — Big-O predicts eventual, large-`n` behavior, not a
  benchmark result.
- **Best, average, and worst case** can differ for the same algorithm;
  Big-O is not synonymous with "worst case" — either can be described
  with Big-O, and which one is meant should always be stated.
- **Space complexity** (specifically **auxiliary space** — new memory
  beyond the input) is a separate question from time complexity; the
  same algorithm can have very different time and space costs, and
  generator expressions trade a list's O(n) space for O(1) space at
  identical O(n) time.
- Common Python operations have typical complexities — but nearly all
  hash-based ones (dict, set) carry an **average-case** qualifier, and
  list operations depend heavily on *where* in the list they act (end
  vs. beginning/middle).
- **Amortized complexity** (e.g., `list.append()`) describes average
  cost per operation over a long sequence, not a guarantee about any one
  individual call.
- **Time-space trade-offs** — spending memory (a set, a dictionary
  index) to save time, or vice versa — are one of the most practically
  important applications of this entire chapter, directly connecting to
  the grouping, deduplication, and sorting patterns from the previous
  chapter.
- The right process is **analyze, then measure, then optimize the
  confirmed bottleneck** — never optimize code just because it looks
  complicated, and never skip measurement in favor of analysis alone.

## 46. Answer Key / Solutions

### §39 — Testing Complexity Reasoning

**Q1.** `n = len(numbers)`. One loop, one addition
per item, no nesting, no early termination. **Time: O(n). Space: O(1)**
— `result` is a single accumulating number, not a growing collection.

**Q2.** `n = len(numbers)`. Two nested loops, both bounded by `range(len
(numbers))` — both genuinely scale with `n`. Early termination (`return
True`) can shorten the best case, but the worst case (no matching pair,
or the matching pair found last) still requires up to `n × n`
comparisons. **Time: O(n²) worst case. Space: O(1)** — no new collection
is built, only a boolean tracked implicitly via the return.

**Q3.** `n = len(numbers)`. The loop can `break` once `result` reaches
10 items — this is early termination bounded by a *constant* (10), not
by `n`. Best case *and* worst case both do at most 10 iterations,
regardless of how large `numbers` is. **Time: O(1)** — this is a subtle
but important case: even though the code contains a loop over
`numbers`, the loop's *effective* bound is capped at a constant, so
growth in `n` does not increase the work at all past a certain point.
**Space: O(1)** — `result` never holds more than 10 items, a constant
size independent of `n`.

**Q4.** `n = len(records)`. One dictionary comprehension, one insertion
per record, each O(1) average-case. **Time: O(n) average-case. Space:
O(n)** — the new dictionary holds one entry per record.

**Q5.** `n = len(items)`. `set(items)` costs O(n) average-case to build;
`len()` on the resulting set is O(1) (previous chapter's §5.3
established `len()` as a direct size query, not a scan). **Time: O(n)
average-case. Space: O(k)**, where `k` is the number of unique items
(bounded by `n`).

**Q6.** `n = len(numbers)`. The inner loop's bound (`range(3)`) is
constant, not tied to `n` — see §10.3 and worked example 6. **Time:
O(n)**, not O(n²). **Space: O(1)** — nothing is stored, only printed.

**Q7.** `n = len(numbers)`. A single generator expression consumed
directly by `sum()` — one pass, no intermediate list. **Time: O(n).
Space: O(1)** — matching §27's worked derivation exactly.

### §40 — Progressive Coding Exercises

**Level 1**

**1.** `process_users(user_list)`: `n = len(user_list)`.
`count_characters(text)`: `n = len(text)`. `compare_grids(grid_a,
grid_b)`: two independent sizes are really at play (e.g., rows/columns
of each grid) — do not collapse them into a single `n` if the grids can
differ in size; the exact naming would depend on the grid's dimensions.

**2.** `for x in items: print(x)` → O(n). `x = items[3]` → O(1) (direct
indexing). `for x in items: for y in range(4): print(y)` → O(n) — the
inner bound is the constant `4`, not tied to the input.

**3.** `items[len(items) // 2]` is one direct index computation and one
lookup — no scanning. **Time: O(1). Space: O(1).**

**4.** One comprehension, one multiplication per item, one new list
built. **Time: O(n). Space: O(n).**

**5.** `n` here should really be described more precisely: if `items` is
a list of `r` rows, each with `c` values, the total number of `print`
calls is `r × c` — the *total number of values across the whole grid*,
not `n²` in the sense of one single list's length squared. If the grid
is described as having `n` total values altogether, this is simply
**O(n)** — a single pass over every value, just organized as nested
loops over rows and columns. This is a direct illustration of §10.3's
warning: visually nested loops are not automatically quadratic —
here, they are iterating over two *different* dimensions of the same
total data, not the same collection twice.

**Level 2**

**6.** The inner loop's range (`i + 1` to `len(items)`) shrinks as `i`
grows, giving the triangular-loop shape from §12 Example C and worked
example 7 — the total comparisons are proportional to `n²`, just with a
smaller constant factor than a full `n × n` loop (since each pair is
only checked once, not twice). **Time: O(n²). Space: O(1).**

**7.** `sum(items)` and `max(items)` are two *sequential* O(n)
operations (not nested) — total `2n`, which simplifies to **O(n)**, per
§13.1. **Space: O(1).**

**8.** Two input sizes: `n` for `index` (already built, not rebuilt
here) and `m = len(ids)` for the loop. Each `.get()` is O(1)
average-case; the loop runs `m` times. **Time: O(m) average-case.
Space: O(m)** for the result list.

**9.** `n = len(items)`; each `in known` check is O(1) average-case,
independent of `known`'s size — one pass over `items`. **Time: O(n)
average-case. Space: O(n)** worst case, if every item is kept.

**10.** `sorted(items, reverse=True)` costs O(n log n) and O(n) space
(§22); the subsequent `[:3]` slice costs O(3), a constant, which
simplifies away. **Overall: Time: O(n log n). Space: O(n)** — the slice
does not change the classification, since the expensive sort has
already built the full O(n) intermediate list.

**Level 3**

**11.** The generator itself does not scan anything until consumed; the
`for x in matching` loop pulls one value at a time and performs O(1)
work per value. One effective pass over `items`. **Time: O(n). Space:
O(1)** — no intermediate list is built, matching §27's fused
filter-aggregate pattern.

**12.** `set(items)` is O(n) average-case; `sorted(..., reverse=True)`
on the resulting `k` unique values is O(k log k) — directly §23's
combined-complexity pattern. **Time: O(n + k log k)** (often stated as
O(n log n) since `k ≤ n`). **Space: O(k).**

**13.** Two input sizes: `n = len(customers)`, `m = len(orders)`.
Building `index` costs O(n) average-case; the comprehension over
`orders` runs `m` times, each doing one O(1)-average-case `.get()`.
**Time: O(n + m) average-case. Space: O(n)** for the index, plus O(m)
for the result — **O(n + m)** overall.

**14.** The nested loop is a genuine `n × n` (both bounds tied to
`len(items)`), giving O(n²) pairs; sorting those `n²` pairs afterward
costs O(n² log(n²)), which simplifies to O(n² log n) — the sort is
*not* negligible here, because the collection being sorted is itself
quadratic in size. **Time: O(n² log n). Space: O(n²)** for the `pairs`
list (and the sorted copy).

**15.** Linear-scan approach: each of the 1,000 lookups costs O(n) (`n =
1,000,000`), for a total of roughly `1,000 × 1,000,000 = 1,000,000,000`
comparisons in the worst case — **O(m × n)**. Index-based approach:
O(n) once to build the dictionary, then O(1) average-case per lookup —
**O(n + m)**, roughly `1,001,000` operations. The index approach costs
additional O(n) memory for the dictionary but is, in this concrete
case, on the order of a million times less work overall — a stark,
worked illustration of §24's trade-off with realistic numbers plugged
in.

**Level 4**

**16.** Deduplication uses a proper seen-**set** (not a growing list, in
contrast to §41's naive mistake) — O(n) average-case. The filter and
`sum()` are each O(n). **Overall time: O(n) average-case. Space: O(n)**
for `seen_ids` and `unique` combined, each proportional to the number of
transactions retained.

**17.** One pass over `logs` (`n = len(logs)`); each access into the
nested `defaultdict` structure is O(1) average-case. **Time: O(n)
average-case. Space: O(s × v)**, where `s` is the number of distinct
services and `v` the number of distinct severities per service — in
practice bounded by O(n) for `n` input records (and often much smaller).

**18.** Setup: build a `customer_id → customer` dictionary once, O(n)
average-case, paid a single time (or refreshed periodically if the
table changes). Each request: O(1) average-case lookup. For `m`
requests per minute against `n` customers, total ongoing cost is
O(m) average-case per minute, with the O(n) setup amortized across all
requests made before the next refresh — directly the pattern from §24,
applied at a system-architecture level.

**19.** A composite tuple key `(customer_id, date)` is used in a proper
seen-**set**, exactly mirroring the previous chapter's §15 approach.
**Time: O(n) average-case. Space: O(n)** worst case (if no duplicates
exist, `seen` and `result` both grow to size `n`).

**20.** Filtering (`ex["text"].strip()`) is O(n). The deduplication loop
uses a proper set (`seen_texts`), each check O(1) average-case, giving
O(n) average-case for that stage too — assuming string normalization
(`.strip().lower()`) itself is treated as O(length of that string),
which depends on the length of each individual string — typically short
and not tied to `n`, so it does not change the high-level conclusion. The final
`sorted(..., key=...)` costs O(u log u), where `u` is the number of
unique, cleaned examples. **Overall time: O(n + u log u) average-case**
(commonly simplified to O(n log n), since `u ≤ n`). **Space: O(n)** for
the intermediate `cleaned` list and the `seen_texts`/`unique`
structures, all bounded by the original dataset size.
