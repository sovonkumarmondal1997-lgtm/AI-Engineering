# Module 04 Practice Questions — Problem-Solving, Collections, and Algorithmic Habits

This set covers exactly the concepts taught across the seven chapters
in this module:

1. Search, Count, Filter, Map, and Aggregate
2. Grouping, Deduplication, and Sorting
3. Big-O Time and Space Complexity
4. Choosing Lists, Dictionaries, Sets, Stacks, and Queues
5. Comprehensions and Readable Code
6. Recursion Basics
7. Basic Parsing and Regular Expressions

35 questions, difficulty increasing progressively:

- **Basic** — Questions 1–5
- **Moderate** — Questions 6–15
- **Hard** — Questions 16–25
- **Advanced** — Questions 26–35

Every question follows the same structure: **Problem → Solution →
Explanation → Complexity → Edge Cases.** Work through each problem
yourself before reading the solution.

---

## BASIC

---

# Question 1 — First Match, Count, and Total Above a Threshold

## Problem

Given a list of transaction amounts, write a function
`summarize_large(amounts, threshold)` that returns a tuple of:

1. the **first** amount strictly greater than `threshold` (or `None` if
   none exists),
2. **how many** amounts are strictly greater than `threshold`,
3. the **sum** of every amount strictly greater than `threshold`.

```python
amounts = [50, 120, 30, 200, 80]
summarize_large(amounts, 100)
# (120, 2, 320)
```

## Solution

### Step 1 — Identify the shapes involved

This is three questions over the same data: *search* ("first match"),
*count* ("how many match"), and *aggregate* ("total of matches") — the
three patterns from the module's first chapter, all sharing the same
underlying condition (`amount > threshold`).

### Step 2 — Implement

```python
def summarize_large(amounts, threshold):
    first_large = next((a for a in amounts if a > threshold), None)
    count_large = sum(a > threshold for a in amounts)
    total_large = sum(a for a in amounts if a > threshold)
    return first_large, count_large, total_large
```

## Explanation

`next((a for a in amounts if a > threshold), None)` pulls the first
matching value from a generator expression, stopping as soon as it is
found, with `None` as a safe default if nothing matches. `sum(a >
threshold for a in amounts)` works because `True`/`False` behave as
`1`/`0` in a numeric context — summing them counts how many are `True`.
The final `sum(a for a in amounts if a > threshold)` filters and
aggregates in one generator pass.

## Complexity

- **Time:** O(n) — each of the three sub-computations makes one pass
  over `amounts` (the `next()` call may terminate early in the best
  case, but the function overall is still O(n) since two full passes
  follow it).
- **Space:** O(1) additional — no intermediate list is built; each
  generator expression is consumed directly.

## Edge Cases

- Empty `amounts` list → `first_large` is `None`, `count_large` is `0`,
  `total_large` is `0` (the safe identity value for `sum()` on nothing).
- No amount exceeds `threshold` → same result as the empty-list case.
- Every amount exceeds `threshold` → `first_large` is `amounts[0]`.
- `threshold` itself present in the list → excluded, since the
  comparison is *strictly* greater than.

---

# Question 2 — Grouping Transactions by Customer

## Problem

Given a list of transaction dictionaries, each with `"customer"` and
`"amount"` keys, write a function `total_by_customer(transactions)`
that returns a dictionary mapping each customer to their total spend.

```python
transactions = [
    {"customer": "A", "amount": 100},
    {"customer": "B", "amount": 50},
    {"customer": "A", "amount": 30},
]
total_by_customer(transactions)
# {"A": 130, "B": 50}
```

## Solution

### Step 1 — Recognize the pattern

This is "group by customer, then sum the amount per group" — the most
common grouping-plus-aggregation shape.

### Step 2 — Implement with `defaultdict(int)`

```python
from collections import defaultdict

def total_by_customer(transactions):
    totals = defaultdict(int)
    for t in transactions:
        totals[t["customer"]] += t["amount"]
    return dict(totals)
```

## Explanation

`defaultdict(int)` gives every new key a starting value of `0`
automatically, so `totals[t["customer"]] += t["amount"]` works on the
very first transaction for a customer without a separate
initialization check. Wrapping the result in `dict(...)` returns a
plain dictionary rather than exposing the `defaultdict` type to the
caller.

## Complexity

- **Time:** O(n) — one pass over `transactions`; each dictionary
  update is O(1) average-case.
- **Space:** O(k) — where `k` is the number of distinct customers,
  bounded by `n`.

## Edge Cases

- Empty `transactions` list → returns `{}`.
- A single customer appearing in every transaction → one key, summed
  correctly across all occurrences.
- Negative amounts (e.g., refunds) → summed correctly; a customer's
  total can legitimately end up negative or zero.

---

# Question 3 — Tracing a Simple Recursive Function

## Problem

Given the function below, trace its execution by hand for
`count_down_sum(4)`, showing every call made and the value ultimately
returned, then implement it.

```python
def count_down_sum(n):
    if n == 0:
        return 0
    return n + count_down_sum(n - 1)
```

## Solution

### Step 1 — Identify base case and recursive case

Base case: `n == 0` returns `0` directly. Recursive case: add `n` to
the result of solving the same problem for `n - 1`.

### Step 2 — Trace the "going down" phase

| call | `n` | base case? | needs |
|---|---|---|---|
| 1 | 4 | no | `4 + count_down_sum(3)` |
| 2 | 3 | no | `3 + count_down_sum(2)` |
| 3 | 2 | no | `2 + count_down_sum(1)` |
| 4 | 1 | no | `1 + count_down_sum(0)` |
| 5 | 0 | **yes** | returns `0` |

### Step 3 — Trace the unwinding phase

```
call 5 returns 0
call 4 returns 1 + 0 = 1
call 3 returns 2 + 1 = 3
call 2 returns 3 + 3 = 6
call 1 returns 4 + 6 = 10
```

Final result: `10` (matching `4 + 3 + 2 + 1 + 0`).

## Explanation

Every recursive call is paused, waiting on the call it made, until the
base case is reached; then each paused call resumes in reverse order,
computing its own result using the value it just received. No addition
actually happens until `count_down_sum(0)` returns — everything is
computed during unwinding.

## Complexity

- **Time:** O(n) — exactly one call per integer from `n` down to `0`.
- **Space:** O(n) — every one of those `n + 1` calls is paused on the
  call stack simultaneously at the deepest point.

## Edge Cases

- `count_down_sum(0)` → returns `0` immediately, no recursive call made.
- Negative `n` → never reaches the base case (`n == 0`) since `n - 1`
  moves further away from `0`, eventually raising `RecursionError`;
  this function assumes non-negative input.

---

# Question 4 — Filtering and Transforming with a Comprehension

## Problem

Given a list of words, write a single list comprehension that produces
the **lowercased** version of every word **longer than 4 characters**.

```python
words = ["Python", "AI", "Data", "Engineering"]
# expected: ['python', 'engineering']
```

## Solution

### Step 1 — Separate filter from transform

Filter condition: `len(word) > 4`. Transform: `word.lower()`.

### Step 2 — Implement

```python
result = [word.lower() for word in words if len(word) > 4]
```

## Explanation

Filtering always happens first for each item — `if len(word) > 4` is
checked against the *original* word — and only words that pass are
then transformed by `word.lower()`, the expression before `for`. This
reads directly as "lowercase each word, for every word in words, but
only if it's longer than 4 characters."

## Complexity

- **Time:** O(n) — one length check and, for matching items, one
  `.lower()` call, per word.
- **Space:** O(k) — where `k` is the number of matching words, bounded
  by `n`.

## Edge Cases

- Empty `words` list → returns `[]`.
- No word longer than 4 characters → returns `[]`.
- A word of exactly length 4 (e.g., `"Data"`) → excluded, since the
  condition is strictly greater than.

---

# Question 5 — Parsing a Simple Delimited Line

## Problem

Given a raw line `"  John , 25 , India  "`, write a function
`parse_person_line(line)` that returns a dictionary
`{"name": "John", "age": 25, "country": "India"}`, correctly handling
the extra whitespace around each field.

## Solution

### Step 1 — Identify the delimiter and cleanup need

The delimiter is `,`; each field also needs its surrounding whitespace
stripped before use, and the age field needs converting to `int`.

### Step 2 — Implement

```python
def parse_person_line(line):
    name, age, country = line.split(",")
    return {
        "name": name.strip(),
        "age": int(age.strip()),
        "country": country.strip(),
    }
```

## Explanation

`.split(",")` breaks the raw line into three raw fields, each still
carrying stray whitespace. `.strip()` is applied to every field before
use — comparing or storing an un-stripped `" John"` against `"John"`
would silently fail. `int(age.strip())` performs the necessary type
conversion, since everything from `.split()` is still a string.

## Complexity

- **Time:** O(1) relative to a fixed, 3-field line (or O(m), where `m`
  is the line's length, if counting the underlying character scan).
- **Space:** O(1) — a fixed-size dictionary is produced.

## Edge Cases

- A line with the wrong number of fields (e.g., only 2 commas expected
  but 1 found) → `ValueError` from the unpacking; not handled by this
  simple version.
- A non-numeric age field → `ValueError` from `int()`.
- Extra whitespace anywhere around any field → correctly handled by
  `.strip()`.

---

## MODERATE

---

# Question 6 — Filter → Map → Aggregate with a Generator

## Problem

Given a list of transaction dictionaries with `"status"` and
`"amount"` keys, write a function `total_completed_amount(transactions)`
that returns the total amount of only the `"completed"` transactions,
using a **single generator expression** (no intermediate list).

## Solution

### Step 1 — Recognize the composition

This is filter (`status == "completed"`) → map (extract `"amount"`) →
aggregate (`sum`), fused into one pass.

### Step 2 — Implement

```python
def total_completed_amount(transactions):
    return sum(
        t["amount"]
        for t in transactions
        if t["status"] == "completed"
    )
```

## Explanation

The generator expression (no square brackets) never builds a list of
filtered transactions or extracted amounts — `sum()` pulls one value at
a time, filtering and extracting on the fly. Using `[t["amount"] for t
in transactions if t["status"] == "completed"]` inside `sum(...)`
would produce the identical *result* but would needlessly materialize a
full intermediate list first.

## Complexity

- **Time:** O(n) — one pass over `transactions`.
- **Space:** O(1) additional — the generator form avoids the O(n)
  intermediate list a list-comprehension version would require.

## Edge Cases

- No completed transactions → `sum()` of an empty generator returns
  `0`, not an error.
- Negative amounts among completed transactions (refunds) → summed
  correctly, potentially producing a lower or negative total.
- Empty `transactions` list → returns `0`.

---

# Question 7 — Grouping Then Ranking by Total

## Problem

Given a list of transaction dictionaries with `"customer"` and
`"amount"`, write a function `rank_customers(transactions)` that
returns a list of `(customer, total)` tuples, sorted from highest
total spend to lowest.

## Solution

### Step 1 — Group, then sort the much smaller result

Group by customer into totals first (cheap, O(n)); sort only the
resulting per-customer totals afterward (a much smaller collection than
the raw transaction list).

### Step 2 — Implement

```python
from collections import defaultdict

def rank_customers(transactions):
    totals = defaultdict(int)
    for t in transactions:
        totals[t["customer"]] += t["amount"]

    return sorted(totals.items(), key=lambda item: item[1], reverse=True)
```

## Explanation

`totals.items()` produces `(customer, total)` tuples; `key=lambda
item: item[1]` sorts by the total (the second tuple element);
`reverse=True` puts the highest spender first. Grouping first, then
sorting only the aggregated result, is deliberately cheaper than
sorting the raw transaction list before grouping.

## Complexity

- **Time:** O(n + k log k) — O(n) to build the grouped totals, O(k log
  k) to sort them, where `k` is the number of distinct customers
  (`k ≤ n`).
- **Space:** O(k) — one entry per distinct customer.

## Edge Cases

- Empty `transactions` list → returns `[]`.
- Two customers with exactly equal totals → both appear, in whichever
  relative order Python's stable sort preserves from `totals.items()`'s
  own order.
- A single customer → returns a one-element list.

---

# Question 8 — Deduplicating Records by a Composite Key

## Problem

Given a list of event dictionaries, each with `"user_id"`, `"day"`, and
`"action"` fields, write a function `deduplicate_events(events)` that
removes events sharing the same `(user_id, day, action)` combination,
keeping only the **first** occurrence of each.

## Solution

### Step 1 — Build a composite key

Use a tuple of the three identifying fields as the deduplication key,
tracked in a seen-set.

### Step 2 — Implement

```python
def deduplicate_events(events):
    seen = set()
    result = []
    for event in events:
        key = (event["user_id"], event["day"], event["action"])
        if key not in seen:
            seen.add(key)
            result.append(event)
    return result
```

## Explanation

A tuple of hashable values is itself hashable, so it can be stored in a
set — this is what makes a composite key possible, since a raw
dictionary cannot be placed in a set directly. Checking `key not in
seen` before appending implements first-write-wins deduplication while
preserving the original arrival order of the surviving events.

## Complexity

- **Time:** O(n) average-case — one set membership check and possible
  insertion per event.
- **Space:** O(n) worst case — if every event's composite key is
  unique, `seen` and `result` both grow to size `n`.

## Edge Cases

- Empty `events` list → returns `[]`.
- Every event sharing the same composite key → only the first survives.
- Two events with the same `user_id` and `day` but different `action`
  → both kept, since the full 3-part key differs.

---

# Question 9 — Choosing a Data Structure and Justifying Its Complexity

## Problem

You must repeatedly check whether an incoming order ID has already been
processed, for a stream of one million order IDs. Choose a data
structure for tracking "already processed" IDs, implement a function
`is_new_order(order_id, processed_ids)` using it, and justify your
choice with a complexity comparison against the alternative of using a
plain list.

## Solution

### Step 1 — Identify the operation that dominates

The dominant, repeated operation is a pure membership check — "have I
seen this ID before?" — with no need to retrieve any associated data.

### Step 2 — Choose the structure

A **set** is the correct choice: it answers exactly this kind of
membership question in O(1) average-case, versus a list's O(n) worst
case.

### Step 3 — Implement

```python
def is_new_order(order_id, processed_ids):
    if order_id in processed_ids:
        return False
    processed_ids.add(order_id)
    return True

processed_ids = set()
```

## Explanation

A dictionary would also work but would store an unused value for every
key, wasting memory for no benefit here, since no associated data is
needed — a set is the more precise fit. A list would require scanning
up to every existing ID before confirming absence, which is
correct but far slower at scale.

## Complexity

- **Set-based:** O(1) average-case per check, O(n) total for `n` order
  IDs.
- **List-based (rejected):** O(n) worst case per check, O(n²) total
  across `n` checks — a dramatic difference at the stated scale of one
  million IDs.
- **Space:** O(n) for either structure, proportional to the number of
  distinct IDs stored.

## Edge Cases

- The very first order ID seen → correctly identified as new.
- The same order ID submitted twice in a row → the second call
  correctly returns `False`.
- An empty `processed_ids` set passed in → works correctly, since a
  set starts empty by default.

---

# Question 10 — List Comprehension vs. Generator Expression Trade-off

## Problem

Given a large list of numbers, you need to compute the sum of every
number squared, but only for numbers greater than 100. Write **two**
implementations — one using a list comprehension inside `sum()`, one
using a generator expression inside `sum()` — and explain which one is
preferable and why.

## Solution

### Step 1 — Implement both versions

```python
def sum_of_squares_list(numbers):
    return sum([n * n for n in numbers if n > 100])

def sum_of_squares_generator(numbers):
    return sum(n * n for n in numbers if n > 100)
```

### Step 2 — Compare

Both produce identical results for identical input.

## Explanation

The list-comprehension version builds a full intermediate list of every
squared value before summing it; the generator-expression version
computes and adds each squared value one at a time, never holding more
than the running total and the generator's own internal state in
memory. Since the intermediate list is never needed for anything other
than being summed, the generator version is preferable — same time
complexity, meaningfully lower memory use for large inputs.

## Complexity

- **Both:** O(n) time — every number is inspected once.
- **List version:** O(k) additional space, where `k` is the count of
  numbers greater than 100.
- **Generator version:** O(1) additional space — no intermediate
  collection is ever materialized.

## Edge Cases

- No numbers greater than 100 → both return `0`.
- Empty `numbers` list → both return `0`.
- All numbers greater than 100 → the list version's intermediate list
  grows to the full input size, `n`, making the space difference most
  pronounced in exactly this case.

---

# Question 11 — Diagnosing a Nested Loop's True Complexity

## Problem

Given the following function, state its time complexity precisely, and
explain why it is **not** automatically O(n²) just because it contains
a nested loop.

```python
def print_windows(items):
    for i in range(len(items)):
        for j in range(5):
            print(items[i], j)
```

## Solution

### Step 1 — Examine each loop's bound

The outer loop runs `n` times (where `n = len(items)`). The inner
loop's bound is the fixed constant `5` — it never grows with `n`.

### Step 2 — Count the total work

Total iterations: `n × 5`, which simplifies to O(n) once the constant
`5` is dropped, as with any constant factor in Big-O.

## Explanation

A nested loop is only O(n²) when **both** loop bounds genuinely scale
with the input size. Here, only the outer loop does; the inner loop
always executes exactly 5 times regardless of how large `items` is —
this is a linear, not quadratic, function, despite its nested
appearance.

## Complexity

- **Time:** O(n).
- **Space:** O(1) additional — nothing is stored, only printed.

## Edge Cases

- Empty `items` list → the outer loop runs zero times; nothing is
  printed.
- A single item → the inner loop still runs exactly 5 times, printing
  5 lines.

---

# Question 12 — Recursively Summing a Nested List

## Problem

Write a recursive function `deep_sum(items)` that returns the sum of
every number in a list that may contain arbitrarily nested sublists.

```python
deep_sum([1, [2, 3], [4, [5, 6]], 7])   # 28
```

## Solution

### Step 1 — Identify the recursive shape

A nested list is either a plain number or another list — recurse when
an item is itself a list; add directly when it is a plain number.

### Step 2 — Implement

```python
def deep_sum(items):
    total = 0
    for item in items:
        if isinstance(item, list):
            total += deep_sum(item)
        else:
            total += item
    return total
```

## Explanation

The base case is implicit in the loop structure: for any item that is
not a list, no further recursive call happens, and its value is simply
added directly. For a nested list, `deep_sum` is called on that smaller
list, and its result is added in — the recursion depth corresponds to
how many levels deep the nesting goes, not how many numbers exist.

## Complexity

- **Time:** O(m) — where `m` is the total number of elements (numbers
  and sublists combined) across every level of nesting; every element
  is visited exactly once.
- **Space:** O(d) — where `d` is the maximum nesting depth, for the
  call stack at its deepest point.

## Edge Cases

- An empty list → returns `0`.
- A flat list with no nesting at all → behaves like a plain sum,
  never recursing.
- A list containing an empty sublist (e.g., `[1, []]`) → the empty
  sublist's `deep_sum` call returns `0` immediately, contributing
  nothing.

---

# Question 13 — Validating a Format with `re.fullmatch()`

## Problem

Write a function `is_valid_product_code(code)` that returns `True` if
`code` consists of exactly two uppercase letters, followed by a hyphen,
followed by exactly four digits (e.g., `"AB-1234"`), and `False`
otherwise.

## Solution

### Step 1 — Choose the right regex function

Because the *entire* string must conform to the shape (not merely
contain a matching substring), `re.fullmatch()` is the correct tool,
not `re.search()`.

### Step 2 — Build the pattern incrementally

Two uppercase letters: `[A-Z]{2}`. A literal hyphen: `-`. Four digits:
`\d{4}`.

### Step 3 — Implement

```python
import re

def is_valid_product_code(code):
    return re.fullmatch(r"[A-Z]{2}-\d{4}", code) is not None
```

## Explanation

`re.fullmatch()` requires the pattern to match from the very start to
the very end of the string — `"AB-1234extra"` would incorrectly pass
with `re.search()`, since that only requires the pattern to match
*somewhere* inside the string, but is correctly rejected by
`re.fullmatch()`.

## Complexity

- **Time:** O(m) — where `m` is the length of `code`; this is a
  simple, fixed-shape pattern with no nested quantifiers, so matching
  cost scales directly with input length.
- **Space:** O(1) additional, beyond the match object itself.

## Edge Cases

- `"ab-1234"` (lowercase letters) → `False`, since `[A-Z]` only matches
  uppercase.
- `"AB-123"` (only three digits) → `False`.
- `"AB-1234X"` (trailing extra character) → `False`, correctly rejected
  specifically because `fullmatch()` was used instead of `search()`.
- Empty string → `False`.

---

# Question 14 — Extracting Structured Fields from a Log Line

## Problem

Given a log line `"2026-01-15 10:30:00 ERROR: connection refused"`,
write a function `parse_log_line(line)` that returns a dictionary with
keys `"date"`, `"time"`, `"level"`, and `"message"`, using named
capturing groups.

## Solution

### Step 1 — Build the pattern piece by piece

Date: `\d{4}-\d{2}-\d{2}`. Time: `\d{2}:\d{2}:\d{2}`. Level: `\w+`.
Message: everything after `": "`, using `.+`.

### Step 2 — Implement with named groups

```python
import re

LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+): (?P<message>.+)"
)

def parse_log_line(line):
    match = LOG_PATTERN.search(line)
    return match.groupdict() if match else None
```

## Explanation

`(?P<name>...)` defines a named group, letting each captured piece be
retrieved by a meaningful name rather than a numeric position.
`match.groupdict()` returns every named group as a dictionary in one
call — directly producing the structured record this whole module has
worked toward. The pattern is compiled once, appropriate for reuse
across many log lines.

## Complexity

- **Time:** O(m) — where `m` is the length of `line`; a single,
  straightforward pattern with no dangerous nested quantifiers.
- **Space:** O(1) additional, beyond the resulting dictionary.

## Edge Cases

- A line that does not match the expected format at all → `match` is
  `None`, and the function returns `None` rather than raising.
- A message containing a colon of its own (e.g., `"ERROR: time: 10:00
  invalid"`) → still captured correctly as one whole message, since
  `.+` is greedy and consumes everything to the end of the line.
- Trailing whitespace at the end of the line → included as part of the
  captured message unless separately stripped.

---

# Question 15 — Reading a CSV File with Quoted Fields

## Problem

Given a raw CSV string where one field contains an embedded comma
inside quotes, write a function `parse_csv_rows(raw_csv)` that returns
a list of rows (each a list of fields), correctly handling the quoting.

```python
raw_csv = 'name,note\nJohn,"Prefers email, not calls"\nAda,None'
```

## Solution

### Step 1 — Recognize why manual splitting fails

`raw_line.split(",")` would incorrectly split `"Prefers email, not
calls"` into two separate pieces, since it has no awareness of quoting.

### Step 2 — Use the standard library's `csv` module

```python
import csv
import io

def parse_csv_rows(raw_csv):
    reader = csv.reader(io.StringIO(raw_csv))
    return list(reader)
```

## Explanation

`csv.reader` correctly implements the CSV format's quoting rules,
treating a comma inside a quoted field as part of that field's content
rather than a delimiter — exactly the behavior `.split(",")` cannot
provide. `io.StringIO` adapts the raw string into a file-like object
that `csv.reader` can iterate over line by line.

## Complexity

- **Time:** O(c) — where `c` is the total number of characters in
  `raw_csv`; every character is scanned once by the parser.
- **Space:** O(c) — the parsed rows collectively hold roughly the same
  amount of data as the original text.

## Edge Cases

- A field containing a literal quote character (properly doubled per
  CSV convention, e.g., `""`) → handled correctly by `csv.reader`,
  unlike a manual split.
- An empty input string → `csv.reader` produces no rows.
- A row with a different number of fields than the header → still
  parsed as-is; `csv.reader` does not enforce a fixed column count on
  its own (that would require additional validation).

---

## HARD

---

# Question 16 — A Deduplicate-Filter-Group-Aggregate-Sort Pipeline

## Problem

Given a list of transaction dictionaries with `"id"`, `"customer"`,
`"amount"`, and `"status"`, where some transaction IDs are duplicated
(later occurrences should be treated as corrections and win), write a
function `spending_report(transactions)` that returns a list of
`(customer, total)` tuples for **completed** transactions only, sorted
highest spender first.

## Solution

### Step 1 — Decompose into named stages

Deduplicate (last-write-wins, by `"id"`) → filter (`status ==
"completed"`) → group by customer, summing amounts → sort the result.

### Step 2 — Implement each stage explicitly

```python
from collections import defaultdict

def deduplicate_by_id(transactions):
    by_id = {}
    for t in transactions:
        by_id[t["id"]] = t   # last occurrence wins
    return list(by_id.values())

def spending_report(transactions):
    deduplicated = deduplicate_by_id(transactions)
    completed = [t for t in deduplicated if t["status"] == "completed"]

    totals = defaultdict(int)
    for t in completed:
        totals[t["customer"]] += t["amount"]

    return sorted(totals.items(), key=lambda item: item[1], reverse=True)
```

## Explanation

Plain dictionary assignment (`by_id[t["id"]] = t`) naturally implements
last-write-wins: whichever transaction with a given ID is processed
*last* overwrites any earlier one under that same key. Filtering
happens only after deduplication, ensuring a corrected transaction's
final status (not a stale, overwritten one) is what determines whether
it counts. Grouping and sorting then proceed exactly as in Question 7.

## Complexity

- **Time:** O(n + k log k) — O(n) for deduplication, filtering, and
  grouping combined (each a single pass), O(k log k) for the final
  sort, where `k` is the number of distinct customers among completed
  transactions.
- **Space:** O(n) — the deduplicated and filtered intermediate lists
  are each bounded by the original transaction count.

## Edge Cases

- A transaction ID appearing three times, with the last marked
  `"failed"` → correctly excluded, since deduplication resolves to the
  *last* record before filtering runs.
- No completed transactions at all → returns `[]`.
- Every transaction belonging to a single customer → returns a
  one-element list.

---

# Question 17 — Counting Errors Per Service from Raw Logs

## Problem

Given a block of raw multi-line log text where each line follows the
format `"YYYY-MM-DD HH:MM:SS SERVICE LEVEL: message"`, write a function
`error_counts_by_service(log_text)` that returns a dictionary mapping
each service name to how many `ERROR`-level lines it produced, silently
skipping any line that does not match the expected format.

## Solution

### Step 1 — Design the pipeline

Split into lines → parse each with a compiled, named-group regex,
collecting only successful matches → filter to `ERROR` level → count by
service.

### Step 2 — Implement

```python
import re
from collections import Counter

LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<service>\w+) (?P<level>\w+): (?P<message>.+)"
)

def error_counts_by_service(log_text):
    parsed = []
    for line in log_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = LOG_PATTERN.fullmatch(line)
        if match:
            parsed.append(match.groupdict())

    errors = [r for r in parsed if r["level"] == "ERROR"]
    return dict(Counter(r["service"] for r in errors))
```

## Explanation

`.splitlines()` correctly separates the multi-line text regardless of
line-ending style. `re.fullmatch()` ensures only lines matching the
*entire* expected shape are accepted — malformed lines from another
subsystem are silently skipped rather than crashing the pipeline.
`Counter` then tallies service names among the filtered error records
in one call, directly reusing the counting pattern from the module's
second chapter.

## Complexity

- **Time:** O(n) — where `n` is the total number of lines; each line is
  matched against the compiled pattern once.
- **Space:** O(s) — where `s` is the number of distinct services,
  bounded by `n`.

## Edge Cases

- A line that does not match the expected format at all → silently
  excluded from `parsed`, never crashing the function.
- No `ERROR`-level lines present → returns `{}`.
- An empty `log_text` string → `.splitlines()` returns `[]`, and the
  function returns `{}`.

---

# Question 18 — Cleaning and Validating Messy Monetary Values

## Problem

Given a list of raw, inconsistently formatted monetary strings (e.g.,
`"$1,200.50"`, `"  980.00  "`, `"invalid"`, `"€500"`), write a function
`clean_amounts(raw_values)` that returns a list of `float` values for
every entry that can be successfully cleaned and parsed, silently
skipping entries that cannot.

## Solution

### Step 1 — Decide what "cleanable" means

Strip every character that is not a digit or a decimal point, then
attempt a numeric conversion; if that conversion fails or produces an
empty result, skip the entry.

### Step 2 — Implement

```python
import re

def clean_amounts(raw_values):
    cleaned = []
    for value in raw_values:
        digits_only = re.sub(r"[^\d.]", "", value)
        if not digits_only:
            continue
        try:
            cleaned.append(float(digits_only))
        except ValueError:
            continue
    return cleaned
```

## Explanation

`re.sub(r"[^\d.]", "", value)` removes every character that is not a
digit or a period in one call — a negated character class — correctly
stripping currency symbols, commas, whitespace, and any other
punctuation regardless of which specific symbols appear. The `try`/
`except` guards against edge cases the regex alone cannot fully rule
out (for example, a string like `"1.2.3"` that survives the character
filter but still fails `float()` conversion).

## Complexity

- **Time:** O(n × m) — where `n` is the number of raw values and `m` is
  the average string length; each value undergoes one regex
  substitution pass.
- **Space:** O(n) — the cleaned list holds at most one entry per input
  value.

## Edge Cases

- `"$1,200.50"` → cleaned to `"1200.50"`, converts to `1200.5`.
- `"invalid"` → cleaned to `""` (no digits or periods present), skipped
  before even attempting conversion.
- `"1.2.3"` → cleaned to `"1.2.3"`, which still fails `float()` and is
  correctly skipped via the `try`/`except`.
- An empty list of raw values → returns `[]`.

---

# Question 19 — Recursively Flattening and Aggregating Nested Data

## Problem

Given a nested dictionary structure representing per-region,
per-category sales figures (arbitrarily nested, with numbers at the
leaves), write a function `total_sales(data)` that recursively sums
every numeric leaf value, regardless of nesting depth.

```python
data = {
    "north": {"food": 100, "electronics": {"phones": 50, "laptops": 200}},
    "south": {"food": 80},
}
total_sales(data)   # 430
```

## Solution

### Step 1 — Recognize the recursive shape

A value is either itself a nested dictionary (recurse into it) or a
plain number (add it directly) — the same "recurse when structure
repeats, collect when it bottoms out" template used for nested
configuration processing.

### Step 2 — Implement

```python
def total_sales(data):
    total = 0
    for value in data.values():
        if isinstance(value, dict):
            total += total_sales(value)
        else:
            total += value
    return total
```

## Explanation

The base case is implicit: once a value is a plain number rather than a
dictionary, no further recursive call is made, and it is added
directly. Each recursive call handles exactly one level of nesting,
regardless of how deep the overall structure goes, because the same
check is repeated at every level.

## Complexity

- **Time:** O(v) — where `v` is the total number of values (both
  container and leaf) across every level; each is visited exactly once.
- **Space:** O(d) — where `d` is the maximum nesting depth, for the
  call stack.

## Edge Cases

- An empty dictionary at any level → its `total_sales` call
  contributes `0`, since the loop over an empty `.values()` runs zero
  times.
- A completely flat dictionary (no nesting) → behaves like a plain
  `sum(data.values())`, never recursing.
- Negative leaf values (e.g., losses) → summed correctly, potentially
  reducing the overall total.

---

# Question 20 — Grouping Unique Values with `defaultdict(set)`

## Problem

Given a list of customer records with `"country"` and `"customer_id"`
fields, some customers appearing more than once for the same country,
write a function `unique_customers_by_country(customers)` that returns
a dictionary mapping each country to a **set** of its distinct customer
IDs.

## Solution

### Step 1 — Choose the per-group accumulator deliberately

Because duplicates within a country should collapse rather than
accumulate, the per-group accumulator must be a set, not a list.

### Step 2 — Implement

```python
from collections import defaultdict

def unique_customers_by_country(customers):
    result = defaultdict(set)
    for customer in customers:
        result[customer["country"]].add(customer["customer_id"])
    return dict(result)
```

## Explanation

`defaultdict(set)` gives every new country key an empty set
automatically, and `.add()` naturally discards duplicate customer IDs
within the same country's set. Choosing `set` instead of `list` as the
accumulator here changes the *meaning* of the result, not just its
type: the same customer appearing three times for one country
contributes only once to that country's set.

## Complexity

- **Time:** O(n) average-case — one pass over `customers`; each set
  insertion is O(1) average-case.
- **Space:** O(u) — where `u` is the total number of distinct
  `(country, customer_id)` combinations, bounded by `n`.

## Edge Cases

- Empty `customers` list → returns `{}`.
- The same customer ID appearing for two *different* countries → both
  counted, since each country's set is independent.
- A customer appearing five times for the same country → contributes
  exactly one entry to that country's set.

---

# Question 21 — Parsing a Nested, Multi-Level Delimited Record

## Problem

Given a single line `"T1|John|apple:2,banana:3|completed"`, write a
function `parse_transaction_line(line)` that returns a dictionary
`{"id": "T1", "customer": "John", "items": {"apple": 2, "banana": 3},
"status": "completed"}`.

## Solution

### Step 1 — Split at the outer level first

Split the whole line by `|` into four top-level fields.

### Step 2 — Parse the nested `items` field separately

Split the items field by `,`, then `partition` each piece on `:` to
separate the item name from its quantity.

### Step 3 — Implement

```python
def parse_transaction_line(line):
    transaction_id, customer, items_raw, status = line.split("|")

    items = {}
    for item in items_raw.split(","):
        name, _, quantity = item.partition(":")
        items[name] = int(quantity)

    return {
        "id": transaction_id,
        "customer": customer,
        "items": items,
        "status": status,
    }
```

## Explanation

This is a two-level parse: the outer `|`-delimited structure is split
first, and only the sub-field that itself contains further structure
(`items_raw`) is parsed with a second round of splitting and
partitioning. Each simple tool (`split`, `partition`) is applied
exactly where it fits, rather than attempting one single, overly
complex parsing expression.

## Complexity

- **Time:** O(m) — where `m` is the length of `line`; the string is
  scanned a small, constant number of times (once for the outer split,
  once for the items split, once per item for partitioning).
- **Space:** O(k) — where `k` is the number of items in the `items`
  field.

## Edge Cases

- A transaction with no items (`items_raw` is an empty string) →
  `"".split(",")` produces `[""]`, and partitioning `""` on `:`
  produces `("", "", "")`; this simple version would need an explicit
  empty-string check to handle a genuinely empty items field cleanly.
- A quantity that is not a valid integer → raises `ValueError` from
  `int(quantity)`.
- Extra `|` characters inside the customer name → would incorrectly
  shift every subsequent field, since `split("|")` has no awareness of
  quoting (a direct illustration of why real CSV-like formats need a
  proper parser, not ad hoc splitting, once such variability is
  possible).

---

# Question 22 — Combined Regex Extraction and Validation

## Problem

Given a list of raw contact strings like `"John Smith <john@example.com>"`,
write a function `extract_valid_contacts(raw_contacts)` that returns a
list of `(name, email)` tuples, but only for entries whose email
address matches a basic valid shape, silently skipping any entry that
does not parse or does not validate.

## Solution

### Step 1 — Design one pattern that both extracts and validates

A single regex with two named groups — `name` and `email` — anchored
with `fullmatch()`, ensures the entire string conforms to the expected
shape *and* extracts both pieces in one step.

### Step 2 — Implement

```python
import re

CONTACT_PATTERN = re.compile(
    r"(?P<name>[\w\s]+) <(?P<email>[\w.+-]+@[\w-]+\.[\w.-]+)>"
)

def extract_valid_contacts(raw_contacts):
    results = []
    for entry in raw_contacts:
        match = CONTACT_PATTERN.fullmatch(entry.strip())
        if match:
            results.append((match.group("name").strip(), match.group("email")))
    return results
```

## Explanation

Using `fullmatch()` rather than `search()` guarantees the *entire*
string — not just a portion of it — conforms to the `"Name
<email>"` shape, which doubles as both extraction and structural
validation in one call. Entries that are malformed (missing angle
brackets, an invalid email shape) simply fail to match and are skipped,
rather than raising an exception or extracting garbage.

## Complexity

- **Time:** O(n × m) — where `n` is the number of raw contact strings
  and `m` is their average length; each is matched against the pattern
  once.
- **Space:** O(n) — the result list holds at most one tuple per valid
  input entry.

## Edge Cases

- `"John Smith john@example.com"` (missing angle brackets) → does not
  match `fullmatch()`, silently skipped.
- `"J <not-an-email>"` → the name portion matches, but the email
  portion's shape fails, so the *entire* pattern fails to match, and the
  entry is skipped.
- Extra leading/trailing whitespace around an otherwise valid entry →
  handled by `.strip()` before matching.

---

# Question 23 — Recursive Tree Depth with Complexity Reasoning

## Problem

Given a tree represented as `{"value": ..., "children": [...]}` (each
child itself the same shape), write a recursive function
`tree_depth(node)` that returns the maximum depth of the tree (a single
node with no children has depth 1), and state its time and space
complexity in terms of the total number of nodes, `n`.

## Solution

### Step 1 — Identify the base case

A node with no children has depth 1 — no further recursion needed.

### Step 2 — Implement

```python
def tree_depth(node):
    if not node["children"]:
        return 1
    return 1 + max(tree_depth(child) for child in node["children"])
```

### Step 3 — Reason about complexity

Every node in the tree is visited exactly once, across the whole
recursive process (each call handles one node and delegates to its
children). The deepest simultaneous call-stack depth corresponds to the
tree's own longest root-to-leaf path.

## Explanation

`max(tree_depth(child) for child in node["children"])` recursively
computes the depth of every child subtree and takes the largest one,
then adds `1` for the current node itself — exactly matching the
definition of a tree's depth. The `not node["children"]` check acts as
the base case, since an empty children list means there are no
subtrees to recurse into.

## Complexity

- **Time:** O(n) — where `n` is the total number of nodes in the tree;
  each node's `tree_depth` call does O(1) work beyond its recursive
  calls into its own children, and every node is visited exactly once
  overall.
- **Space:** O(h) — where `h` is the tree's height (its longest
  root-to-leaf path), for the call stack at its deepest point — this
  can be much smaller than `n` for a wide, shallow tree, or close to
  `n` for a deep, narrow one.

## Edge Cases

- A single node with no children → returns `1`.
- A tree where every node has exactly one child (effectively a chain)
  → depth equals `n`, and the call stack also reaches depth `n` — the
  worst case for stack usage.
- A wide tree where the root has many children, each a leaf → depth is
  `2`, even though `n` may be large — a case where time is O(n) but
  space (stack depth) stays small.

---

# Question 24 — Optimizing a Naive O(n²) Duplicate Check

## Problem

The following function checks whether a list of transaction IDs
contains any duplicates. Identify its time complexity, explain the
specific line responsible for it, and rewrite it to run in O(n)
average-case time.

```python
def has_duplicate_naive(transaction_ids):
    seen = []
    for tid in transaction_ids:
        if tid in seen:
            return True
        seen.append(tid)
    return False
```

## Solution

### Step 1 — Diagnose the bottleneck

`if tid in seen` checks membership against a **list** that grows by one
element on every iteration — each check can scan up to every item
already collected, making the overall cost proportional to `n²` in the
worst case (no early duplicate found until near the end, or none at
all).

### Step 2 — Rewrite using a set

```python
def has_duplicate_optimized(transaction_ids):
    seen = set()
    for tid in transaction_ids:
        if tid in seen:
            return True
        seen.add(tid)
    return False
```

## Explanation

Replacing the growing list with a set changes only the membership
check's underlying cost, not the function's logic: `if tid in seen` is
now an O(1) average-case hashed lookup instead of an O(n) worst-case
scan, and `.add()` replaces `.append()` with the same O(1) average-case
cost. The overall algorithm's shape (one pass, checking membership on
each item) is unchanged — only the data structure backing that
membership check has been fixed.

## Complexity

- **Naive version:** O(n²) worst case — `n` iterations, each
  potentially scanning up to `n` items in the growing list.
- **Optimized version:** O(n) average-case — `n` iterations, each doing
  O(1) average-case set work.
- **Space:** O(n) for either version, since up to `n` IDs may need to
  be stored before a duplicate (if any) is found.

## Edge Cases

- No duplicates present → both versions correctly return `False`, but
  the naive version pays its full O(n²) cost since it never
  terminates early with a duplicate found.
- A duplicate as the very first two elements → both versions terminate
  almost immediately, minimizing the practical difference in that
  specific case.
- Empty `transaction_ids` list → both correctly return `False`.

---

# Question 25 — Designing a FIFO Transaction Processing Structure

## Problem

You are building a system that must: accept transactions in arrival
order, reject duplicate transaction IDs immediately on arrival, and
process accepted transactions strictly in the order they arrived.
Design (in code) the data structures needed, and justify each one's
role.

## Solution

### Step 1 — Identify the distinct requirements

Three separate requirements: duplicate rejection (membership),
FIFO processing order, and (implicitly) a way to look up a stored
transaction later.

### Step 2 — Assign one structure per responsibility

```python
from collections import deque

seen_ids = set()                  # membership: reject duplicates
pending_queue = deque()            # FIFO: process in arrival order
transactions_by_id = {}            # lookup: retrieve a transaction by ID

def receive_transaction(transaction):
    tid = transaction["id"]
    if tid in seen_ids:
        return False
    seen_ids.add(tid)
    transactions_by_id[tid] = transaction
    pending_queue.append(tid)
    return True

def process_next():
    if not pending_queue:
        return None
    tid = pending_queue.popleft()
    return transactions_by_id[tid]
```

## Explanation

A `set` is used purely for the yes/no "is this ID new?" question — no
associated data needs to travel with that check. A `deque` is used for
FIFO ordering specifically because `.popleft()` is O(1), unlike a plain
list's `.pop(0)`, which would require shifting every remaining element
and cost O(n) per removal. A `dict` is used for O(1) average-case
lookup of a transaction's full data by ID. No single structure could
satisfy all three requirements as efficiently on its own.

## Complexity

- **`receive_transaction`:** O(1) average-case — one set check, one set
  insertion, one dictionary insertion, one deque append.
- **`process_next`:** O(1) — one deque `popleft()`, one dictionary
  lookup.
- **Space:** O(n) across all three structures combined, where `n` is
  the number of accepted transactions.

## Edge Cases

- A duplicate transaction ID submitted → `receive_transaction` returns
  `False` immediately, and the queue/dictionary remain unchanged.
- `process_next()` called with no pending transactions → returns
  `None` safely, rather than raising an error.
- The same transaction ID resubmitted after having already been fully
  processed → still rejected as a duplicate, since `seen_ids` is never
  cleared after processing (a deliberate design choice worth stating
  explicitly).

---

## ADVANCED

---

# Question 26 — A Complete Parsing-to-Report Pipeline with Regex and Grouping

## Problem

Given raw multi-line transaction log text where each line follows the
format `"TXN:<id> CUST:<customer> AMT:<amount> STATUS:<status>"`, build
a function `build_customer_report(raw_text)` that: parses every valid
line using a regex with named groups, silently collects unparseable
lines separately, deduplicates by transaction ID (first occurrence
wins), filters to completed transactions, and returns a dictionary with
`"totals_by_customer"` (sorted highest first) and `"unparseable_count"`.

## Solution

### Step 1 — Design the pipeline as named stages

Parse (regex, collecting failures) → deduplicate (first-write-wins) →
filter (completed only) → group and total → sort → assemble the report.

### Step 2 — Implement

```python
import re
from collections import defaultdict

LINE_PATTERN = re.compile(
    r"TXN:(?P<id>\S+) CUST:(?P<customer>\S+) AMT:(?P<amount>\d+) STATUS:(?P<status>\S+)"
)

def parse_lines(raw_text):
    parsed, unparseable = [], []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = LINE_PATTERN.fullmatch(line)
        if match:
            data = match.groupdict()
            data["amount"] = int(data["amount"])
            parsed.append(data)
        else:
            unparseable.append(line)
    return parsed, unparseable

def deduplicate_first(records):
    seen = set()
    result = []
    for record in records:
        if record["id"] not in seen:
            seen.add(record["id"])
            result.append(record)
    return result

def build_customer_report(raw_text):
    parsed, unparseable = parse_lines(raw_text)
    deduplicated = deduplicate_first(parsed)
    completed = [r for r in deduplicated if r["status"] == "completed"]

    totals = defaultdict(int)
    for r in completed:
        totals[r["customer"]] += r["amount"]

    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)

    return {
        "totals_by_customer": ranked,
        "unparseable_count": len(unparseable),
    }
```

## Explanation

Parsing is kept strict (`fullmatch()`) and defensive — malformed lines
are collected rather than crashing the pipeline, mirroring the "collect
unparseable lines separately" approach used for realistic log
processing. Type conversion (`int(data["amount"])`) happens immediately
after extraction, before any downstream aggregation depends on numeric
comparison or summation. Deduplication is applied before filtering,
ensuring status is judged only once per genuine transaction. Grouping
and sorting follow the now-familiar pattern from Questions 7 and 16.

## Complexity

- **Time:** O(n + k log k) — O(n) for parsing, deduplication, filtering,
  and grouping (each a single pass over at most `n` lines), O(k log k)
  for the final sort, where `k` is the number of distinct customers
  among completed, deduplicated transactions.
- **Space:** O(n) — the parsed, deduplicated, and filtered intermediate
  collections are each bounded by the original line count.

## Edge Cases

- A line with a non-numeric amount (e.g., `"AMT:abc"`) → fails to match
  `\d+` for the amount group, so the entire line fails `fullmatch()`
  and is counted as unparseable rather than raising a conversion error.
- A duplicate transaction ID appearing with two different statuses →
  only the first-seen version is kept, per the deduplication rule
  chosen for this problem.
- An entirely empty `raw_text` → returns `{"totals_by_customer": [],
  "unparseable_count": 0}`.

---

# Question 27 — Reasoning About a Combined Deduplicate-Group-Sort Pipeline's Complexity

## Problem

Given the pipeline `sorted(set(deduplicated_customer_ids))` applied
after first building `deduplicated_customer_ids` via a seen-set loop
over `n` raw customer records, derive the overall time complexity of
the **entire** process, explaining each stage's contribution
separately, and state why expressing it as `O(n log n)` alone would
lose useful information.

## Solution

### Step 1 — Break the pipeline into its stages

1. The seen-set deduplication loop over `n` raw records: O(n)
   average-case, producing `k` unique customer IDs (`k ≤ n`).
2. `set(deduplicated_customer_ids)`: O(k) average-case — deduplicating
   an already-deduplicated list is redundant here, but still costs O(k)
   to build.
3. `sorted(...)`: O(k log k).

### Step 2 — Combine the stages

Total: **O(n + k + k log k)**, which simplifies to **O(n + k log k)**
since `k log k` dominates `k` for `k > 1`.

## Explanation

Collapsing this immediately to "O(n log n)" (valid, since `k ≤ n`) is a
correct but looser upper bound — it obscures the fact that the
expensive `log` factor applies only to `k`, the number of *distinct*
customers, not to the full `n` raw records. If duplicates are common
(`k` much smaller than `n`), the pipeline's real-world cost is
dominated by the cheap O(n) deduplication pass, not the sort — a fact
the loose `O(n log n)` bound does not communicate. Retaining the more
precise `O(n + k log k)` form preserves this insight.

## Complexity

- **Time:** O(n + k log k), as derived above.
- **Space:** O(k) — the deduplicated collection and its sorted form
  each hold at most `k` items.

## Edge Cases

- Every raw record having a distinct customer ID (`k = n`) → the bound
  reduces to O(n log n), with no benefit from deduplication.
- Massive duplication (`k` much smaller than `n`) → the pipeline's
  actual cost is dominated by the O(n) pass, and the sort's cost
  becomes comparatively negligible.
- Zero raw records → every stage operates on empty input, and the
  pipeline correctly returns an empty result.

---

# Question 28 — Memoizing a Recursive Nested-Config Depth Calculation

## Problem

Given a recursive function that computes the maximum nesting depth of a
configuration structure (dictionaries/lists nested arbitrarily), and
given that the **same** sub-structure object may be referenced multiple
times within a larger structure (e.g., a shared default sub-config
reused across several keys), explain whether memoization with
`functools.lru_cache` is an appropriate optimization here, and if not,
what would make it appropriate.

## Solution

### Step 1 — Check memoization's two requirements

Memoization helps when subproblems are **overlapping** (the same
subproblem is solved more than once) and results can be **safely
cached** by their input. Here, the "same input" would need to be the
same dictionary/list object, or a value that can act as a stable,
hashable cache key.

### Step 2 — Identify the actual obstacle

```python
def max_depth(data):
    if isinstance(data, dict) and data:
        return 1 + max(max_depth(v) for v in data.values())
    if isinstance(data, list) and data:
        return 1 + max(max_depth(v) for v in data)
    return 1
```

`@lru_cache` requires its function's arguments to be **hashable**
(§39's own requirement) — but `data` here is a `dict` or `list`, both
of which are unhashable. Applying `@lru_cache` directly to `max_depth`
as written would raise a `TypeError` the moment it is called with a
dictionary or list argument.

### Step 3 — What would make it appropriate

Memoization would become appropriate if the *same, identical* nested
object were genuinely reused in a way that could be tracked by object
identity (`id(data)`, used as a cache key manually, since `id()` is
hashable even though the object itself is not) rather than by value —
this is a more advanced, manual caching technique, not a direct
`@lru_cache` application, precisely because `@lru_cache` relies on
its arguments being hashable and comparable by value, which nested
dictionaries and lists are not.

## Explanation

The presence of overlapping subproblems alone is not sufficient to
justify `@lru_cache` — the function's argument type must also be
hashable for the decorator to work at all. This scenario is a
deliberate contrast to the module's own Fibonacci example, where the
argument (`n`, an integer) is naturally hashable, making `@lru_cache`
a direct, correct fit.

## Complexity

- **Without memoization:** O(v) time, where `v` is the total number of
  values across the whole structure, since even repeated references to
  the same sub-structure are each fully re-traversed.
- **With a correctly designed manual cache (keyed by `id(data)`):**
  each *distinct* object is processed once, at the cost of the
  additional bookkeeping needed to manage such a cache correctly
  (including the risk of stale results if the underlying data is later
  mutated).

## Edge Cases

- A deeply nested structure with no repeated sub-structures at all →
  memoization would provide no benefit even if it could be applied
  directly, since no subproblem is genuinely overlapping.
- A shared sub-structure that is later mutated in place after being
  cached by identity → a correctness risk unique to identity-based
  caching, since the cached depth would become stale.
- An empty dictionary or list passed as `data` → returns `1` directly,
  the base case, with no recursion at all.

---

# Question 29 — Choosing Data Structures for a Multi-Access-Pattern Workload

## Problem

A system must support all of the following, ideally efficiently: (a)
checking whether a session ID is currently active, many times per
second; (b) retrieving a session's full data by its ID; (c) expiring
sessions in the exact order they were created, oldest first; and (d)
iterating over sessions in creation order for a periodic audit report.
Design the combination of data structures needed, and justify each
choice against the specific access pattern it serves.

## Solution

### Step 1 — Map each access pattern to its natural structure

(a) is pure membership → a **set**. (b) is lookup by key → a
**dictionary**. (c) is FIFO removal → a **deque**. (d) is ordered
iteration, matching creation order → the deque already provides this
directly, since it holds session IDs in the order they were enqueued.

### Step 2 — Implement the combination

```python
from collections import deque

active_session_ids = set()
sessions_by_id = {}
creation_order = deque()

def create_session(session_id, data):
    active_session_ids.add(session_id)
    sessions_by_id[session_id] = data
    creation_order.append(session_id)

def is_active(session_id):
    return session_id in active_session_ids

def get_session(session_id):
    return sessions_by_id.get(session_id)

def expire_oldest():
    if not creation_order:
        return None
    session_id = creation_order.popleft()
    active_session_ids.discard(session_id)
    sessions_by_id.pop(session_id, None)
    return session_id

def audit_report():
    return [sessions_by_id[sid] for sid in creation_order if sid in sessions_by_id]
```

## Explanation

No single structure satisfies all four requirements efficiently at
once: a list alone would make membership checks and lookups O(n); a
dictionary alone has no ordering guarantee suitable for FIFO expiry
without an additional structure; a set alone cannot store session data
or preserve creation order for iteration. Each of the three structures
here is assigned to exactly the requirement it is naturally efficient
at, following the module's own repeated principle that real systems
combine multiple structures rather than forcing one to serve every
purpose. `discard()` (not `remove()`) is used during expiry so that an
already-removed ID does not raise an error if expiry logic runs twice.

## Complexity

- **`create_session`:** O(1) average-case — one set insertion, one
  dictionary insertion, one deque append.
- **`is_active`:** O(1) average-case — one set membership check.
- **`get_session`:** O(1) average-case — one dictionary lookup.
- **`expire_oldest`:** O(1) average-case — one deque `popleft()`, one
  set discard, one dictionary pop.
- **`audit_report`:** O(m) — where `m` is the number of currently
  tracked sessions, since it must walk the full creation order.
- **Space:** O(m) across all three structures combined.

## Edge Cases

- `expire_oldest()` called with no active sessions → returns `None`
  safely.
- A session expired, then `get_session()` called for its ID afterward
  → returns `None`, since it was removed from `sessions_by_id`.
- `audit_report()` called after some sessions have been expired → the
  `if sid in sessions_by_id` guard prevents a `KeyError` for any ID
  still lingering in `creation_order` (which, in this design, should
  not normally happen given `expire_oldest`'s bookkeeping, but the
  guard makes the function robust regardless).

---

# Question 30 — Refactoring a Naive O(n²) List-Based Lookup Table into O(n)

## Problem

The following function repeatedly enriches a list of `m` orders with
customer names by scanning a list of `n` customers for each order.
Diagnose its complexity, and rewrite it to run in O(n + m) time.

```python
def enrich_orders_naive(orders, customers):
    enriched = []
    for order in orders:
        customer_name = None
        for customer in customers:
            if customer["id"] == order["customer_id"]:
                customer_name = customer["name"]
                break
        enriched.append({**order, "customer_name": customer_name})
    return enriched
```

## Solution

### Step 1 — Diagnose the complexity

For each of the `m` orders, the inner loop scans up to all `n`
customers in the worst case — total cost O(m × n), a hidden nested-loop
cost from repeated linear search, even though early termination
(`break`) softens it in the best case.

### Step 2 — Rewrite using a precomputed index

```python
def enrich_orders_optimized(orders, customers):
    customers_by_id = {c["id"]: c["name"] for c in customers}
    return [
        {**order, "customer_name": customers_by_id.get(order["customer_id"])}
        for order in orders
    ]
```

## Explanation

Building `customers_by_id` once, up front, costs O(n) average-case; each
of the `m` subsequent lookups then costs O(1) average-case via
`.get()`, which also safely returns `None` for an order referencing an
unknown customer ID rather than raising a `KeyError`. This is the same
"preprocess once, reuse many times" trade-off already established for
repeated lookups: a small amount of upfront memory and time in exchange
for eliminating a repeated linear scan.

## Complexity

- **Naive version:** O(m × n) worst case.
- **Optimized version:** O(n + m) average-case — O(n) to build the
  index, O(m) for the lookups.
- **Space:** O(n) additional for the index dictionary, in the
  optimized version (the naive version uses no such additional
  structure, trading memory for its far worse time complexity).

## Edge Cases

- An order referencing a `customer_id` not present in `customers` →
  the naive version leaves `customer_name` as `None` after exhausting
  the inner loop; the optimized version's `.get()` produces the same
  `None` result, preserving identical behavior.
- Duplicate customer IDs in `customers` → the optimized version's
  dictionary comprehension keeps whichever customer is processed
  *last* for a given ID (a subtle behavior difference worth noting
  explicitly, since the naive version would have matched whichever
  came *first* due to its `break`).
- Empty `orders` list → both versions return `[]`.

---

# Question 31 — Identifying a Hidden Bottleneck in a Filtering Pipeline

## Problem

The following function is reported as unexpectedly slow when
`records` is very large. Identify the specific bottleneck, and explain
why the surrounding filter/comprehension logic is not itself the
problem.

```python
def unique_valid_emails(records):
    valid_emails = []
    for record in records:
        email = record.get("email")
        if email and email not in valid_emails:
            valid_emails.append(email)
    return valid_emails
```

## Solution

### Step 1 — Examine each operation inside the loop

`email not in valid_emails` checks membership against a **list** that
grows by one item every time a new unique email is found — this is the
identical hidden-quadratic-cost pattern already diagnosed in Question
24, here disguised inside what otherwise looks like a simple filtering
loop.

### Step 2 — Fix it with a proper seen-set, preserving order

```python
def unique_valid_emails_fixed(records):
    seen = set()
    valid_emails = []
    for record in records:
        email = record.get("email")
        if email and email not in seen:
            seen.add(email)
            valid_emails.append(email)
    return valid_emails
```

## Explanation

The loop's overall *structure* — iterate once, filter, collect if new —
was never the problem; the specific choice of `valid_emails` (a list)
as the structure being checked for membership was. Adding a dedicated
`seen` set alongside the existing `valid_emails` list preserves the
exact same output (unique emails, in first-seen order) while reducing
the membership check itself from O(n) worst-case to O(1) average-case.

## Complexity

- **Original version:** O(n²) worst case — `n` records, each
  potentially checked against an `valid_emails` list that has grown up
  to `n` items.
- **Fixed version:** O(n) average-case — `n` records, each doing O(1)
  average-case set work.
- **Space:** O(u) for either version, where `u` is the number of
  unique valid emails — the fixed version simply adds one more O(u)
  structure (`seen`) alongside the existing result list.

## Edge Cases

- A record with a missing or empty `"email"` field → `record.get
  ("email")` returns `None` or `""`, both falsy, so `if email` correctly
  skips it in either version.
- Every record sharing the same email → only the first occurrence is
  kept, in both versions.
- An empty `records` list → both versions return `[]`.

---

# Question 32 — Converting Naive Recursive Fibonacci into a Scalable Version

## Problem

The following function is used to compute the `n`th Fibonacci number
but becomes impractically slow for `n` around 35 and beyond. Explain
precisely why, and rewrite it so it remains fast for much larger `n`,
justifying the fix's complexity improvement.

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

## Solution

### Step 1 — Diagnose the root cause

Each call (except at the base cases) makes two further recursive
calls, and the *same* smaller subproblems (e.g., `fibonacci(30)`) get
recomputed independently, many times over, at every branch of the call
tree that needs them — this repeated, duplicated work is what drives
the function's O(2ⁿ) time complexity.

### Step 2 — Fix it with memoization

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_fast(n):
    if n <= 1:
        return n
    return fibonacci_fast(n - 1) + fibonacci_fast(n - 2)
```

## Explanation

`@lru_cache` automatically stores each distinct call's result the
first time it is computed, and returns that stored result immediately
on any later call with the same argument, skipping the recursive work
entirely on a cache hit. Since `n` is a plain, hashable integer, it
satisfies `@lru_cache`'s requirement directly (in contrast to Question
28's unhashable-argument scenario). With this fix, each distinct value
of `n` from `0` up to the original input is computed exactly once.

## Complexity

- **Naive version:** O(2ⁿ) time, O(n) space (call-stack depth only,
  since branches are explored one at a time, not simultaneously).
- **Memoized version:** O(n) time — each of `n` distinct subproblems is
  computed once, with O(1) work beyond its now cache-hit recursive
  calls — and O(n) space, for the cache itself plus the call stack.

## Edge Cases

- `fibonacci_fast(0)` and `fibonacci_fast(1)` → both handled directly
  by the base case, with no recursion or caching needed.
- Calling `fibonacci_fast` for several different values of `n` in
  sequence within the same program run → later calls benefit from
  subproblems already cached by earlier calls, since `@lru_cache`'s
  cache persists across calls to the decorated function.
- A very large `n` → the memoized version avoids `RecursionError`
  concerns from repeated calls, but its own recursion depth is still
  O(n), so it remains subject to Python's recursion limit for
  sufficiently large `n`, just as the naive version's stack depth was.

---

# Question 33 — Debugging a Subtly Broken Recursive Function

## Problem

The following function is intended to return the total number of
leaves (non-list elements) in a possibly nested list, but it always
returns `0`. Find the bug, explain why it produces `0` in every case,
and fix it.

```python
def count_leaves(items):
    total = 0
    for item in items:
        if isinstance(item, list):
            count_leaves(item)
        else:
            total += 1
    return total
```

## Solution

### Step 1 — Trace the bug

For a nested item, `count_leaves(item)` is called recursively, but its
**return value is never used** — the call happens, computes a correct
count internally, and that result is simply discarded, since it is not
added to `total` or returned anywhere.

### Step 2 — Fix it by using the recursive call's result

```python
def count_leaves_fixed(items):
    total = 0
    for item in items:
        if isinstance(item, list):
            total += count_leaves_fixed(item)
        else:
            total += 1
    return total
```

## Explanation

This is a direct instance of the "forgetting to use a recursive call's
result" mistake: the recursive call's computation is entirely correct
in isolation, but because its result is never incorporated into
`total`, every nested list's contribution is silently lost — only
top-level, non-nested items ever get counted, and if every top-level
item happens to itself be a list (as in many realistic nested inputs),
the function returns `0` for the *entire* structure, exactly as
reported.

## Complexity

- **Time:** O(m) — where `m` is the total number of elements (leaves
  and sublists combined) across all nesting levels; unaffected by the
  fix, since the bug was about using a result, not about how much work
  was performed.
- **Space:** O(d) — where `d` is the maximum nesting depth, for the
  call stack.

## Edge Cases

- `count_leaves_fixed([1, 2, 3])` (no nesting at all) → returns `3`,
  matching the original buggy version's behavior for this specific
  case (which is exactly why the bug could easily go unnoticed if only
  flat inputs were tested).
- `count_leaves_fixed([[1, 2], [3, [4, 5]]])` → returns `5`, correctly
  counting leaves at every depth, unlike the original buggy version,
  which would incorrectly return `0`.
- An empty list at any level → contributes `0` leaves, correctly,
  since the loop over it runs zero times.

---

# Question 34 — Refactoring an Unreadable Nested Comprehension

## Problem

Refactor the following comprehension into clearer code, and explain
specifically what made the original hard to read.

```python
result = [
    process(x)
    for group in raw_groups
    for x in group["items"]
    if x["status"] == "active" and x["value"] is not None and x["value"] > 0
]
```

## Solution

### Step 1 — Identify the sources of difficulty

Two levels of nested iteration (`group`, then `x` within it) combined
with three separate `and`-joined conditions force a reader to hold five
distinct pieces of context in mind simultaneously just to know what
reaches `process()`.

### Step 2 — Name the condition, and consider staging the iteration

```python
def is_processable(item):
    return (
        item["status"] == "active"
        and item["value"] is not None
        and item["value"] > 0
    )

all_items = [x for group in raw_groups for x in group["items"]]
result = [process(x) for x in all_items if is_processable(x)]
```

## Explanation

Extracting the three-condition filter into a named function
(`is_processable`) immediately clarifies *what* qualifies an item,
independent of the surrounding loop structure, and makes that
condition independently testable. Separating the flattening step
(`all_items`) from the filter-and-transform step trades a small amount
of additional memory (one extra intermediate list) for a version where
each line answers exactly one question, rather than one dense
expression answering three questions at once. Both changes apply the
module's own standing principle that complexity should be named rather
than left as an unlabeled, inline expression.

## Complexity

- **Time:** O(m) for both versions, where `m` is the total number of
  items across all groups — refactoring here is a readability
  improvement, not a complexity change.
- **Space:** the refactored version adds one O(m) intermediate list
  (`all_items`) that the original, single combined comprehension did
  not require — a deliberate, small trade-off in favor of clarity.

## Edge Cases

- A group with an empty `"items"` list → contributes nothing to
  `all_items`, in either version.
- An item with `"value"` set to `0` → correctly excluded by `value >
  0`, in both the original and refactored condition.
- An item missing the `"value"` key entirely → raises `KeyError` in
  both versions equally, since neither uses `.get()`; this would be a
  separate, additional fix if missing keys were a genuine possibility
  in the real data.

---

# Question 35 — Designing a Robust End-to-End Log Processing Pipeline

## Problem

Design and implement a complete pipeline that: (1) accepts raw,
multi-line log text where lines may or may not conform to a known
format; (2) parses conforming lines into structured records using a
compiled, named-group regex; (3) deduplicates records by an embedded
transaction reference (first occurrence wins), extracted from the
message text using a secondary regex; (4) groups error-level records by
their transaction reference; (5) reports total records processed,
successfully parsed, deduplicated, and grouped by severity — and
justify every data-structure and algorithmic choice made.

## Solution

### Step 1 — Enumerate the requirements and map each to a tool

- Splitting lines → `str.splitlines()`.
- Parsing structured fields from otherwise free-form lines → a
  compiled regex with named groups.
- Extracting an embedded transaction reference from free text →
  a second, smaller regex applied to the message field.
- Deduplication, first-write-wins → a seen-set keyed by the extracted
  reference.
- Grouping error records by reference → `defaultdict(list)`.
- Counting records by severity → `collections.Counter`.

### Step 2 — Implement the full pipeline

```python
import re
from collections import defaultdict, Counter

LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+): (?P<message>.+)"
)
TRANSACTION_PATTERN = re.compile(r"TXN\d+")

def parse_lines(raw_text):
    parsed, unparseable = [], []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = LOG_PATTERN.fullmatch(line)
        if match:
            parsed.append(match.groupdict())
        else:
            unparseable.append(line)
    return parsed, unparseable

def deduplicate_by_transaction(records):
    seen = set()
    result = []
    for record in records:
        match = TRANSACTION_PATTERN.search(record["message"])
        key = match.group() if match else None
        if key is None or key not in seen:
            if key is not None:
                seen.add(key)
            result.append(record)
    return result

def build_full_report(raw_text):
    parsed, unparseable = parse_lines(raw_text)
    deduplicated = deduplicate_by_transaction(parsed)

    severity_counts = Counter(r["level"] for r in deduplicated)

    errors_by_transaction = defaultdict(list)
    for record in deduplicated:
        if record["level"] == "ERROR":
            match = TRANSACTION_PATTERN.search(record["message"])
            key = match.group() if match else "none"
            errors_by_transaction[key].append(record)

    return {
        "total_lines": len(raw_text.splitlines()),
        "parsed_count": len(parsed),
        "unparseable_count": len(unparseable),
        "deduplicated_count": len(deduplicated),
        "severity_counts": dict(severity_counts),
        "errors_by_transaction": dict(errors_by_transaction),
    }
```

## Explanation

Every tool was chosen to match exactly one requirement, following the
module's operation-driven selection principle throughout: `splitlines()`
handles line boundaries because that structure is fixed and known;
regex handles both the overall log-line shape and the embedded
transaction reference because both are pattern-based, variable-length
fields within otherwise simply structured text, not something a fixed
delimiter could extract; a set handles deduplication because the
question is purely "have I seen this reference before"; `defaultdict
(list)` handles grouping because it naturally accumulates a per-key
list without a manual initialization check; `Counter` handles the
severity tally directly. Records with no extractable transaction
reference are deliberately never deduplicated against each other (only
records that *do* have a reference are checked against `seen`),
reflecting the reasonable choice that "no reference present" is not
itself grounds for treating two records as duplicates of each other.

## Complexity

- **Time:** O(n) — where `n` is the number of lines; parsing,
  deduplication, severity counting, and grouping are each a single
  pass, with all regex operations and dictionary/set operations O(1)
  average-case per line (aside from the length of each individual line
  itself, which is bounded independently of `n`).
- **Space:** O(n) — the parsed, deduplicated, and grouped structures
  are each bounded by the original line count.

## Edge Cases

- A line that fails to match `LOG_PATTERN` at all → correctly collected
  into `unparseable`, and excluded from every subsequent stage.
- A parsed record whose message contains no `TXN\d+`-shaped reference
  → `key` is `None` during deduplication (never checked against
  `seen`, so it is always kept) and `"none"` during error grouping (a
  distinct, intentional convention chosen for the two different
  stages).
- Two error records sharing the same transaction reference → both
  land in `errors_by_transaction` under that key, since grouping (unlike
  the earlier deduplication stage) is intentionally designed to
  collect every matching record together, not to discard any of them.
- Completely empty `raw_text` → every count in the resulting report is
  `0`, and both dictionaries in the result are empty, with no errors
  raised.
