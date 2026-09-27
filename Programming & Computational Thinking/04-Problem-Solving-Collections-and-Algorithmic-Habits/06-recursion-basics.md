# Recursion Basics

## 1. What Recursion Is

### 1.1 A real-world analogy first

Imagine standing in a line and asking the person directly in front of
you, *"what is your position in this line?"* That person does not know
the answer outright — but they can ask the person in front of *them* the
same question, get an answer, and then add one to it. That person does
the same thing, asking the person in front of *them* — and so on, all
the way to the very front of the line, where the first person simply
knows, without needing to ask anyone: *"I am position 1."* Once that
answer travels back down the line, each person adds one and passes it
back, until you finally get your own answer.

Notice what happened: **the same question** ("what is my position?")
was asked repeatedly, each time to a *smaller* version of the same
line — until the question became so small it could be answered directly,
with no further asking needed. That is the entire idea behind
**recursion**.

### 1.2 The definition, built carefully

- A **recursive function** is a function that calls **itself** — this
  is called **self-reference**.
- Each time it calls itself, it does so on a **smaller subproblem** —
  a version of the original problem that is somehow simpler or closer
  to being finished.
- Eventually, the subproblem becomes small enough to answer directly,
  without calling itself again — this is the **stopping condition**
  (formally named the **base case** in §5).

**Recursion means solving a problem by having a function solve a
smaller version of the same problem.**

### 1.3 A tiny Python example: counting down

```python
def countdown(n):
    if n == 0:
        print("Liftoff!")
        return
    print(n)
    countdown(n - 1)


countdown(3)
```

```text
3
2
1
Liftoff!
```

**Explaining every line, assuming nothing:**

- `def countdown(n):` — defines a function named `countdown`, taking
  one argument, `n`.
- `if n == 0:` — checks whether the problem has become as small as
  possible: "count down from zero" needs no further counting.
- `print("Liftoff!")` and `return` — when the problem is that small,
  answer directly and stop; no further calls happen.
- `print(n)` — if the problem is *not* yet that small, do the useful
  work for this step (print the current number).
- `countdown(n - 1)` — this is the **recursive call**: `countdown`
  calls *itself*, but with a **smaller** argument (`n - 1` instead of
  `n`). This is self-reference, applied to a smaller version of the
  exact same problem ("count down from `n`" became "count down from
  `n - 1`").

**What actually happens when a function calls itself — the part
beginners most often gloss over:** calling `countdown(3)` does not
somehow "restart" the original call or lose track of where it was. Each
call to `countdown` is a **completely separate, independent execution**
of the same function body, with its own separate value of `n`. Python
keeps track of every one of these in-progress calls simultaneously —
`countdown(3)` is paused, waiting on `countdown(2)`, which is paused,
waiting on `countdown(1)`, which is paused, waiting on `countdown(0)`,
which finally finishes without waiting on anything. §7 and §8 dissect
exactly how Python tracks all of this "waiting."

## 2. Why Recursion Exists

### 2.1 Some problems naturally contain smaller versions of themselves

Recursion is not merely an alternative syntax for a loop — it exists
because certain problems have a structure where **the solution to the
whole problem is built directly out of solutions to smaller instances of
the same problem**. Examples where this is genuinely natural, previewed
here and developed fully later in this chapter:

- **Counting down** (§1) — "count down from `n`" is "print `n`, then
  count down from `n - 1`."
- **Traversing nested structures** (§15) — "process this nested list"
  is "process this item, then process this nested list's remaining,
  smaller nested structure."
- **Processing folders** — a folder containing files *and other
  folders* is naturally recursive: "list everything in this folder" is
  "list each file directly here, and for each subfolder, list
  everything in *that* folder" — the exact same operation, applied to a
  smaller piece of the whole.
- **Traversing trees** (§34) — a tree is *defined* in terms of smaller
  trees (its subtrees), making recursion the structure's most natural
  fit.
- **Divide-and-conquer algorithms** (§21, §40) — solve a big problem by
  splitting it into smaller pieces, solving each piece the same way, and
  combining the results.
- **Exploring combinations** (§36) — trying every possible choice at
  each step, and for each choice, trying every possible choice for what
  comes next, is naturally recursive.
- **Parsing nested structures** — code containing expressions nested
  inside other expressions (parentheses inside parentheses, for example)
  is naturally recursive to process, though full parsing is a later,
  dedicated topic.

In every one of these cases, recursion lets the code's *structure*
directly mirror the *problem's* structure — this is recursion's real
value: **making certain algorithms easier to express and reason about**,
not "recursion is a clever trick."

### 2.2 The disadvantages, stated honestly

Recursion is a genuine engineering trade-off, not a free upgrade over
loops:

- **Call-stack usage** — every recursive call that has not yet finished
  occupies memory (§8); deeply recursive code can use meaningfully more
  memory than an equivalent loop.
- **Recursion depth limits** — Python enforces a maximum call-stack
  depth (§26); a recursive function that goes too deep raises a
  `RecursionError` (§27), a failure mode loops simply do not have.
- **Debugging difficulty** — following execution through many nested,
  paused function calls can be harder to trace mentally than a single
  loop's straightforward, linear progression (§28 builds a systematic
  approach for this specifically).
- **Sometimes unnecessary complexity** — a problem that is naturally
  linear (like summing a list) does not *need* recursion's self-
  referential structure; using it anyway can make the code harder to
  read for no real benefit.
- **Iterative solutions may be simpler and more efficient** — this is
  explored directly and honestly in §3, §30, §31, and §32, rather than
  asserted once and left unexamined.

**The chapter's standing principle:** recursion is a **problem-solving
technique** to be reached for when a problem's structure calls for it —
not a habit to apply "whenever possible" just because it is available.

## 3. Recursion vs Iteration

### 3.1 Two different shapes of repeated work

```
RECURSION:  function → function → function → ... → base case → unwind
ITERATION:  loop → repeat → repeat → ... → condition becomes false
```

Recursion repeats by having a function call itself, with each call
"nested" inside the one before it, waiting for it to finish. Iteration
(the `for`/`while` loops from earlier modules) repeats by returning to
the top of the same loop body, with nothing nested and nothing waiting.

### 3.2 Countdown, side by side

```python
# Recursive
def countdown_recursive(n):
    if n == 0:
        print("Liftoff!")
        return
    print(n)
    countdown_recursive(n - 1)
```

```python
# Iterative
def countdown_iterative(n):
    while n > 0:
        print(n)
        n -= 1
    print("Liftoff!")
```

Both produce identical output for the same input. Neither is "wrong" —
this is the first of several examples in this chapter designed to make
that comparison concrete rather than abstract.

### 3.3 Factorial, side by side

```python
# Recursive
def factorial_recursive(n):
    if n == 0:
        return 1
    return n * factorial_recursive(n - 1)
```

```python
# Iterative
def factorial_iterative(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

### 3.4 Sum of a list, side by side

```python
# Recursive
def sum_recursive(numbers):
    if not numbers:
        return 0
    return numbers[0] + sum_recursive(numbers[1:])
```

```python
# Iterative
def sum_iterative(numbers):
    total = 0
    for number in numbers:
        total += number
    return total
```

### 3.5 Comparing along several axes

| | Recursion | Iteration |
|---|---|---|
| **Readability** | Can closely mirror a problem's natural, self-similar structure (trees, nested data) — sometimes clearer, sometimes more indirect for simple linear problems. | Usually more direct for simple, linear repeated work. |
| **Memory** | Uses call-stack space proportional to recursion depth (§8, §24). | Uses a fixed, small amount of memory regardless of how many iterations run (Big-O chapter's §16). |
| **Performance** | Function-call overhead is paid on every recursive call. | No function-call overhead between iterations. |
| **Stack usage** | Bounded by Python's recursion limit (§26) — deep recursion can fail outright. | Not limited by any call-stack constraint. |
| **Termination** | Requires a correctly reached base case (§5) — an incorrect one causes infinite recursion, eventually `RecursionError`. | Requires a correctly updated loop condition — an incorrect one causes an infinite loop. |
| **Maintainability** | Can be easier to extend correctly for genuinely recursive structures (trees, nested folders). | Can require extra manual bookkeeping (explicit stacks/queues) to handle the same recursive structures — previewed in §30. |

### 3.6 The honest conclusion

**Do not claim recursion is always slower or always worse — and do not
claim it is always clearer, either.** `sum_recursive` above is a
legitimate teaching example, but a working engineer would use Python's
built-in `sum()` (search/count/filter/map/aggregate chapter's §8) for
this exact task — the recursive version exists here purely to make the
recursion-vs-iteration comparison concrete on a problem simple enough to
hold entirely in your head. **The right choice depends on the specific
problem and its natural structure** — this entire chapter is built to
help you judge that, case by case, rather than defaulting to either
tool out of habit.

## 4. The Basic Structure of a Recursive Function

Every correct recursive function follows this shape:

```python
def function(problem):
    if base_case_condition:
        return base_case_result

    smaller_problem = make_progress_toward(problem)
    return function(smaller_problem)
```

Two parts, and **both are mandatory**:

1. A **base case** — a condition simple enough to answer directly, with
   no further recursive calls (§5).
2. A **recursive case** — a call to the same function, on a
   *provably smaller* version of the problem, that eventually reaches
   the base case (§6).

Missing either part breaks the function: no base case means the
function never stops calling itself (§27); no genuine progress toward
the base case (e.g., calling the function with the *same* value, or a
value that never approaches the base case) has the identical effect,
even if a base case technically exists in the code.

## 5. Base Case

### 5.1 What it is

The **base case** is the smallest, simplest version of the problem —
one the function can answer immediately, without needing to call itself
again. In `countdown`, the base case is `n == 0`. In `factorial_recursive`,
it is `n == 0` (with the mathematically correct answer `1`, since `0!
= 1`). In `sum_recursive`, it is an empty list (`not numbers`), whose
sum is `0`.

### 5.2 Why a base case is necessary — not merely conventional

Every recursive call adds a new "waiting" function call to the
call stack (§8). Without a base case, a recursive function has no
condition under which it stops calling itself — it recurses forever,
consuming more and more call-stack space, until Python's built-in
recursion limit is hit and a `RecursionError` is raised (§27). The base
case is not a stylistic nicety; it is the **only** thing that makes a
recursive function ever finish.

### 5.3 Choosing the right base case

The base case must be:
- **Reachable** — every recursive call must eventually be able to reach
  it (§6.2 develops this as "provable progress").
- **Directly answerable** — no further recursive calls should be
  needed to produce its result.
- **Correct as a genuine instance of the problem**, not just a
  convenient stopping point — `factorial(0) = 1` is mathematically
  correct, not an arbitrary choice; getting a base case's actual value
  wrong is a subtle, common bug covered in §29.

## 6. Recursive Case

### 6.1 What it is

The **recursive case** is the part of the function that handles
everything *other* than the base case — it does some useful work for
the current step, and then calls the function again on a smaller
version of the problem.

```python
def factorial_recursive(n):
    if n == 0:            # base case
        return 1
    return n * factorial_recursive(n - 1)   # recursive case
```

Here, "some useful work" is the multiplication by `n`; "a smaller
version of the problem" is `n - 1`.

### 6.2 Provable progress toward the base case

Every recursive call must move **measurably closer** to the base case.
In `factorial_recursive`, `n - 1` is always strictly smaller than `n`
(for positive `n`), so repeated calls must eventually reach `n == 0`.
This is not a minor detail — it is the entire guarantee that recursion
terminates at all:

```python
# BROKEN — no progress toward the base case:
def broken_countdown(n):
    if n == 0:
        return
    print(n)
    broken_countdown(n)   # BUG: should be n - 1, not n!
```

`broken_countdown(3)` never reaches `n == 0` — every call passes the
*same* `n`, so this recurses forever (until `RecursionError`, §27).
**Always verify explicitly that the argument passed to a recursive call
is genuinely smaller/simpler than the current one, in a way that
provably reaches the base case** — this single check catches the most
common category of recursion bug (§29 covers this and related mistakes
in full).

## 7. How Recursive Calls Actually Execute

### 7.1 Nothing "magic" happens

When `factorial_recursive(3)` runs, Python does not somehow evaluate
all three levels "at once." It executes exactly as any function call
does: it runs the function body with `n = 3`, and when that body reaches
`return n * factorial_recursive(n - 1)`, Python must first **fully
evaluate** `factorial_recursive(n - 1)` — meaning `factorial_recursive(2)`
starts running, *while `factorial_recursive(3)` is paused, waiting for
that inner call's return value.*

### 7.2 Two distinct phases

Every recursive call has two distinct phases, worth naming explicitly:

- **The "going down" phase** — each call invokes the next, smaller
  call, and pauses, waiting for a return value. This continues until
  the base case is reached.
- **The "coming back up" phase** (formally, **stack unwinding**, §9) —
  once the base case returns a value, each paused call resumes exactly
  where it left off, uses that returned value to compute its own
  result, and returns *that* result to whichever call is waiting on it.

```python
factorial_recursive(3)
  → factorial_recursive(2)
      → factorial_recursive(1)
          → factorial_recursive(0)
              → returns 1                      (base case reached)
          → returns 1 * 1 = 1
      → returns 2 * 1 = 2
  → returns 3 * 2 = 6
```

Every arrow going down represents a paused call waiting for an answer;
every "returns" going back up represents that waiting call finally
getting its answer and computing its own.

## 8. Call Stack and Stack Frames

### 8.1 What a stack frame is

Every time a function is called — recursive or not — Python creates a
**stack frame**: a small record holding that specific call's local
variables (here, its own value of `n`), and *where in the code to
resume* once the call it is waiting on returns. This connects directly
to the LIFO **stack** structure from the data-structures chapter's §17:
Python itself uses a stack (the **call stack**) to track function calls.

### 8.2 The call stack during `factorial_recursive(3)`

At the deepest point of the "going down" phase (just as
`factorial_recursive(0)` is about to return), the call stack looks
like this, conceptually, from bottom (oldest, first called) to top
(newest, most recently called):

```
[ factorial_recursive(3) ]   ← waiting, at the bottom
[ factorial_recursive(2) ]   ← waiting
[ factorial_recursive(1) ]   ← waiting
[ factorial_recursive(0) ]   ← currently executing, about to return 1 — at the top
```

Four separate stack frames exist **simultaneously** — this is precisely
why recursion has a memory cost proportional to its depth (§24): each
paused call's frame must remain in memory for as long as it is waiting.

### 8.3 Why this is the same mechanism briefly noted earlier

The Big-O chapter's §29 already introduced this exact idea — "a
recursive function's call stack consumes space proportional to its
depth" — as a preview. This section is where that idea is fully
unpacked: the call stack is not an abstract metaphor; it is a real,
LIFO structure Python maintains as your program runs, and understanding
it precisely is the key to understanding recursion depth (§25),
`RecursionError` (§27), and the space complexity of recursive
algorithms (§24) — all covered ahead.

## 9. Stack Unwinding

**Stack unwinding** is the name for the "coming back up" phase from
§7.2: once the base case returns, each paused stack frame, starting
from the most recently added (the top of the stack), resumes execution,
computes its own result using the value it just received, returns that
result, and is then removed from the call stack entirely.

```
factorial_recursive(0) returns 1        → its frame is removed
factorial_recursive(1) resumes, computes 1 * 1 = 1, returns 1  → its frame is removed
factorial_recursive(2) resumes, computes 2 * 1 = 2, returns 2  → its frame is removed
factorial_recursive(3) resumes, computes 3 * 2 = 6, returns 6  → its frame is removed
```

By the time `factorial_recursive(3)` finally returns `6` to whoever
called it, the call stack is back to empty — every frame added during
the "going down" phase has been removed, one at a time, during
unwinding. **Nothing is computed until the base case is reached; then
everything is computed, one paused frame at a time, on the way back
out.** This two-phase mental model — first fully descend to the base
case, then fully unwind back out, computing as you go — is the single
most useful way to reason correctly about any recursive function's
behavior.

## 10. Tracing a Recursive Function

A systematic method, applied to `sum_recursive` from §3.4:

```python
def sum_recursive(numbers):
    if not numbers:
        return 0
    return numbers[0] + sum_recursive(numbers[1:])
```

Tracing `sum_recursive([3, 1, 4])`:

| call | `numbers` | base case? | what it needs | 
|---|---|---|---|
| 1 | `[3, 1, 4]` | no | `3 + sum_recursive([1, 4])` |
| 2 | `[1, 4]` | no | `1 + sum_recursive([4])` |
| 3 | `[4]` | no | `4 + sum_recursive([])` |
| 4 | `[]` | **yes** | returns `0` directly |

**Unwinding, from the base case back up:**

```
call 4 returns 0
call 3 returns 4 + 0 = 4
call 2 returns 1 + 4 = 5
call 1 returns 3 + 5 = 8
```

Final result: `8` (and indeed, `3 + 1 + 4 = 8`). This two-table method —
first trace every call *down* to the base case, listing each one's
unevaluated expression, then trace the returns *up*, substituting each
result in turn — is the recommended way to manually verify *any*
recursive function's correctness, and is reused throughout the rest of
this chapter's examples.

## 11. First Simple Recursive Examples

Three small, complete examples, each already introduced above, gathered
here as a single reference point before the chapter moves into
recursion applied to different data types.

```python
def countdown(n):
    if n == 0:
        print("Liftoff!")
        return
    print(n)
    countdown(n - 1)
```

```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
```

```python
def sum_list(numbers):
    if not numbers:
        return 0
    return numbers[0] + sum_list(numbers[1:])
```

Each follows §4's exact shape: one clearly identifiable base case, one
recursive case that does a small amount of work and calls itself on a
provably smaller problem (§6.2).

## 12. Recursion with Numbers

### 12.1 Fibonacci — introduced here, revisited in §22–§23 and §38

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

This differs from every prior example in one important way: it makes
**two** recursive calls, not one (§19 develops "multiple recursive
calls" as its own topic). Tracing `fibonacci(4)`:

```
fibonacci(4) = fibonacci(3) + fibonacci(2)
fibonacci(3) = fibonacci(2) + fibonacci(1)
fibonacci(2) = fibonacci(1) + fibonacci(0)
fibonacci(1) = 1   (base case)
fibonacci(0) = 0   (base case)
```

Unwinding: `fibonacci(2) = 1 + 0 = 1`; `fibonacci(3) = 1 + 1 = 2`;
`fibonacci(4) = 2 + 1 = 3`. This function is deliberately revisited
later in this chapter (§23 for its time complexity, §38 for how
memoization fixes its most serious inefficiency) — it is one of the
most instructive small examples in all of recursion.

### 12.2 Digit sum

```python
def digit_sum(n):
    if n < 10:
        return n
    return n % 10 + digit_sum(n // 10)
```

Base case: a single-digit number is its own digit sum. Recursive case:
take the last digit (`n % 10`) and add it to the digit sum of everything
else (`n // 10`, integer division dropping the last digit) — a smaller
number, provably closer to a single digit each time.

## 13. Recursion with Strings

### 13.1 Reversing a string

```python
def reverse_string(text):
    if len(text) <= 1:
        return text
    return reverse_string(text[1:]) + text[0]
```

Base case: a string of length 0 or 1 is already its own reverse.
Recursive case: reverse everything *after* the first character, then
place the first character at the *end*. Tracing `reverse_string("cat")`:

```
reverse_string("cat")  = reverse_string("at") + "c"
reverse_string("at")   = reverse_string("t") + "a"
reverse_string("t")    = "t"                          (base case)
```

Unwinding: `reverse_string("at") = "t" + "a" = "ta"`;
`reverse_string("cat") = "ta" + "c" = "tac"`.

### 13.2 Checking for a palindrome

```python
def is_palindrome(text):
    if len(text) <= 1:
        return True
    if text[0] != text[-1]:
        return False
    return is_palindrome(text[1:-1])
```

This example has **two** conditions before the recursive call: the base
case (a string of length 0 or 1 is trivially a palindrome), and an
**early-exit condition** (if the first and last characters do not
match, the whole string cannot be a palindrome — no need to check
further). The recursive case strips both ends and checks what remains.
This demonstrates that a recursive function can have more than one
"stopping" condition — not every early `return` is the *base* case in
the strict sense of "smallest version of the problem," but every early
`return` still must not call the function again.

## 14. Recursion with Lists

### 14.1 Finding the maximum recursively

```python
def find_max(numbers):
    if len(numbers) == 1:
        return numbers[0]
    rest_max = find_max(numbers[1:])
    return numbers[0] if numbers[0] > rest_max else rest_max
```

Base case: a list with exactly one item — its maximum is itself.
Recursive case: find the maximum of everything *except* the first item,
then compare that against the first item. (In production code, the
built-in `max()` from the aggregate chapter's §8.3 would always be
preferred — this example exists purely to practice the recursive
pattern on a familiar problem, exactly as `sum_recursive` did in §3.4.)

### 14.2 Counting occurrences recursively

```python
def count_occurrences(items, target):
    if not items:
        return 0
    first_match = 1 if items[0] == target else 0
    return first_match + count_occurrences(items[1:], target)
```

Base case: an empty list has zero occurrences of anything. Recursive
case: check whether the first item matches, then add that (`1` or `0`)
to the count from the rest of the list — directly mirroring the
accumulator pattern from the counting chapter (search/count/filter/
map/aggregate chapter's §5.2), expressed recursively instead of with a
loop-based running total.

## 15. Recursion with Nested Data

### 15.1 Why nested lists are naturally recursive

```python
nested = [1, [2, 3], [4, [5, 6]], 7]
```

A nested list is, by definition, a list whose items are *either* plain
values *or* more lists — this is exactly the kind of "smaller version of
the same structure" that makes recursion a natural fit (§2.1).

### 15.2 Flattening a nested list

```python
def flatten(items):
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


print(flatten([1, [2, 3], [4, [5, 6]], 7]))
# [1, 2, 3, 4, 5, 6, 7]
```

`isinstance(item, list)` checks whether `item` is itself a list. If it
is, `flatten` is called on *that* smaller list, and its (already
flattened) result is merged in with `.extend()` (list chapter's §6). If
it is not, the item is a plain value and is simply appended directly.
**The base case here is implicit in the loop's structure**: for any
individual item that is *not* a list, no further recursive call
happens — the "smaller problem" for a deeply nested list is "one level
less nested," and the recursion bottoms out the moment an item is a
plain value rather than another list.

## 16. Recursion with Dictionaries

### 16.1 Nested dictionaries

```python
nested_config = {
    "name": "app",
    "settings": {
        "debug": True,
        "limits": {"max_users": 100},
    },
}
```

### 16.2 Recursively collecting all leaf values

```python
def collect_values(data):
    values = []
    for value in data.values():
        if isinstance(value, dict):
            values.extend(collect_values(value))
        else:
            values.append(value)
    return values


print(collect_values(nested_config))
# ['app', True, 100]
```

Exactly the same shape as §15.2's `flatten`, applied to nested
dictionaries instead of nested lists: `data.values()` (dictionary
chapter's §10) walks each value; if a value is itself a dictionary,
recurse into it; otherwise, collect it directly. This pattern —
"recurse when the structure repeats, collect directly when it bottoms
out" — is the single most broadly reusable recursive idiom for
processing any real-world nested data (JSON-like configuration, nested
API responses, and similar structures all share this exact shape).

## 17. Recursion and Accumulators

### 17.1 The problem with the "natural" recursive style

`sum_recursive` (§3.4) computes its result entirely during **stack
unwinding** — nothing is added until the base case returns and each
frame resumes. An alternative style passes the running total *down*
through the recursive calls instead, as an extra argument:

```python
def sum_with_accumulator(numbers, running_total=0):
    if not numbers:
        return running_total
    return sum_with_accumulator(numbers[1:], running_total + numbers[0])
```

### 17.2 Why this matters

Here, the **base case simply returns the accumulator directly** — no
computation happens during unwinding at all; every bit of work
(`running_total + numbers[0]`) happens on the way *down*, before the
recursive call. This style, called **accumulator-passing** (or, in some
languages, a stepping stone toward **tail recursion** — Python does not
optimize tail calls the way some other languages do, so this style does
not reduce Python's call-stack usage, but it is still a genuinely
useful and common recursive pattern to recognize), mirrors the loop-
based accumulator pattern from the counting and aggregation chapters
(search/count/filter/map/aggregate chapter's §5.2, §8.2) — the running
total is threaded through, one step at a time, exactly as a loop's
accumulator variable is updated each iteration.

## 18. Returning Values from Recursive Calls

A recursive function that is meant to produce a result must **always
explicitly `return`** the value from its recursive call — a very common
mistake (developed fully in §29) is calling the function recursively but
forgetting to `return` (or use) its result:

```python
# BROKEN — the recursive call's result is computed and then discarded!
def broken_sum(numbers):
    if not numbers:
        return 0
    numbers[0] + broken_sum(numbers[1:])   # missing `return`!
    # implicitly returns None
```

```python
# CORRECT
def correct_sum(numbers):
    if not numbers:
        return 0
    return numbers[0] + correct_sum(numbers[1:])
```

`broken_sum` computes the correct expression every time — but because
it is never `return`ed, every call (except possibly the very last one,
depending on the function) implicitly returns `None`, and the entire
computed chain is thrown away. **Every recursive case that needs to
produce a usable result must explicitly `return` an expression that
includes the recursive call** — this is worth verifying deliberately
every time a recursive function is written, not just when something
already looks wrong.

## 19. Multiple Recursive Calls

### 19.1 Linear vs. branching recursion

Every example through §18 (except `fibonacci`, §12.1) made **exactly
one** recursive call per invocation — this is called **linear
recursion**, and its call-stack behavior is simple: one frame directly
waits on exactly one other frame, forming a single chain.

`fibonacci` makes **two** recursive calls per invocation (except at the
base case) — this is **branching recursion** (formalized next, in §20,
as **tree-style recursion**), and its behavior is meaningfully
different: a single call can spawn two entirely separate "chains" of
further calls, each of which must fully complete before the original
call can produce its result.

### 19.2 Why this distinction matters going forward

Linear recursion's call-stack depth is directly proportional to the
size of the input (§24, §25). Branching recursion's *total number of
calls* can grow far faster than the input size — this is exactly why
naive `fibonacci` is such a well-known example of a recursive function
whose performance surprises beginners (§23 works out precisely why),
and why §20's tree-style framing, and later §37–§38's memoization fix,
both matter specifically for this multiple-call case.

## 20. Tree-Style Recursion

### 20.1 Visualizing `fibonacci(4)`'s calls as a tree

```
                    fibonacci(4)
                   /            \
          fibonacci(3)          fibonacci(2)
          /        \             /        \
  fibonacci(2)  fibonacci(1)  fibonacci(1) fibonacci(0)
   /      \
fibonacci(1) fibonacci(0)
```

Every call that branches into two further calls forms exactly the
shape of a **tree**: `fibonacci(4)` is the tree's root; each recursive
call is a child; the base cases (`fibonacci(1)`, `fibonacci(0)`) are the
tree's **leaves** — where branching stops. This is not merely a
convenient diagram — it is the literal shape of the computation, and it
is exactly the same conceptual structure that real tree data structures
(§34) are traversed with.

### 20.2 A striking, important observation

Notice `fibonacci(2)` and `fibonacci(1)` each appear **more than once**
in this small tree, entirely independently recomputed each time,
without any memory of having been computed before. This repeated,
wasted work is the direct cause of naive Fibonacci's poor time
complexity (§23) — and is precisely the problem **memoization** (§37–
§39) is designed to solve, by remembering ("caching") each distinct
call's result the first time it is computed.

## 21. Divide-and-Conquer Thinking

### 21.1 The general pattern

**Divide-and-conquer** is a specific, powerful recursive strategy with
three named steps:

1. **Divide** — split the problem into smaller subproblems of the same
   kind.
2. **Conquer** — solve each subproblem recursively (or directly, if
   small enough to be a base case).
3. **Combine** — merge the subproblems' solutions into a solution for
   the original problem.

### 21.2 A first example: binary search, revisited recursively

The Big-O chapter's §9 introduced binary search **iteratively**.
Expressed recursively, its divide-and-conquer structure becomes
explicit:

```python
def binary_search(numbers, target, left=0, right=None):
    if right is None:
        right = len(numbers) - 1

    if left > right:
        return -1   # base case: search space is empty — not found

    middle = (left + right) // 2

    if numbers[middle] == target:
        return middle   # base case: found it
    elif numbers[middle] < target:
        return binary_search(numbers, target, middle + 1, right)   # search the right half
    else:
        return binary_search(numbers, target, left, middle - 1)    # search the left half
```

**Divide:** the search space is split at `middle`. **Conquer:** exactly
one of the two halves is searched recursively (never both — this is
what keeps binary search efficient, unlike the merge sort in §40, which
must conquer *both* halves). **Combine:** trivial here — whichever half's
recursive call finds the answer, that answer is simply passed straight
back up; there is no additional merging work needed. This is a fully
worked, direct comparison to the earlier chapter's iterative version,
demonstrating that the same algorithm can be expressed either way, with
identical O(log n) time complexity (§22–§23).

## 22. Recursion and Big-O

Connecting directly to
[Big-O, Time, and Space Complexity](03-big-o-time-and-space-complexity.md)
§29, which first introduced recursive time and space complexity as a
preview — this chapter now develops that fully.

**Counting the work for a recursive function means counting two
separate things**, exactly mirroring that earlier chapter's own
distinction:

- **Time complexity** — how many total calls are made, and how much
  work each one does independent of its recursive call(s).
- **Space complexity** — how deep the call stack gets at its deepest
  point, since every "waiting" frame occupies memory simultaneously
  (§8, §24).

These two numbers are **not always the same** for a given recursive
function — §23 and §24 work through concrete cases where they diverge.

## 23. Time Complexity of Recursive Algorithms

### 23.1 Linear recursion — one call per invocation

```python
def sum_list(numbers):
    if not numbers:
        return 0
    return numbers[0] + sum_list(numbers[1:])
```

Counting the work: one call is made per item in `numbers`, plus one
final call for the empty-list base case — `n + 1` calls total, each
doing a small, constant amount of work (one addition). **Time: O(n)** —
directly analogous to a single loop over `n` items.

**A caveat worth flagging explicitly:** `numbers[1:]` itself creates a
*new list* (a slice, list chapter's §6), which costs O(k) where `k` is
the remaining list's length — this means `sum_list` as written is
actually doing more work than a plain loop would, because of the
repeated slicing, not because of the recursion itself. This is worth
noticing precisely because it demonstrates that a recursive function's
complexity depends on *everything* inside its body, not merely on how
many times it calls itself — a lesson directly consistent with the
Big-O chapter's own repeated warning (§37 there) against classifying
code by its "shape" alone.

### 23.2 Branching recursion — naive Fibonacci

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

As shown in §20's tree diagram, each call (except at the leaves) spawns
**two** further calls. The total number of calls roughly **doubles**
with each increase in `n` — this is precisely the exponential growth
already introduced conceptually in the Big-O chapter's §30.1. **Time:
O(2ⁿ)** — restated here with the tree-diagram intuition from §20.2 fully
in hand: the explosive cost comes specifically from **repeated,
duplicated work** — `fibonacci(2)` being recomputed independently every
time it is needed, rather than being computed once and reused. This
exact inefficiency is what §37–§39 (backtracking's cousin, dynamic
programming, and memoization) directly address.

### 23.3 Divide-and-conquer recursion — binary search

From §21.2: each call examines the middle element (O(1) work) and then
makes **exactly one** recursive call on **half** the remaining search
space. This is the identical halving structure already derived in the
Big-O chapter's §9.5. **Time: O(log n)** — restated here specifically in
recursive terms: the recursion depth itself (how many nested calls occur
before reaching the base case) *is* the `log n` — each level of
recursion corresponds to one halving.

## 24. Space Complexity of Recursive Algorithms

### 24.1 The call stack is the space cost

As established in §8, every unfinished (paused) recursive call occupies
its own stack frame simultaneously. **A recursive function's auxiliary
space complexity is generally proportional to its maximum recursion
depth** — not to its total number of calls.

### 24.2 Linear recursion's space cost

`sum_list([1, 2, 3, 4])` reaches a depth of 5 (one call per item, plus
the base case) before any unwinding begins — all 5 frames exist
simultaneously at that deepest point. **Space: O(n)**, directly
matching the Big-O chapter's `countdown` example (§29 there).

### 24.3 Branching recursion's space cost — a genuine surprise

Despite making O(2ⁿ) **total calls** (§23.2), naive `fibonacci`'s
**maximum depth** at any one moment is only proportional to `n` itself
— because Python fully finishes exploring one branch (e.g., the entire
`fibonacci(n - 1)` chain) and unwinds it *before* starting the other
branch (`fibonacci(n - 2)`) — the two branches are never simultaneously
"deep" on the stack at once. **Space: O(n)**, even though **time: O(2ⁿ)**
— a clear, concrete case where a recursive algorithm's time and space
complexity genuinely differ, exactly as flagged as a possibility at the
end of §22.

### 24.4 Divide-and-conquer's space cost

Binary search's recursion depth is O(log n) (§23.3) — and since exactly
one recursive call is made per invocation (never two simultaneously
active branches), its stack depth at any moment is also O(log n).
**Space: O(log n)** — dramatically better than linear recursion's O(n),
directly because each level of recursion discards half the remaining
problem rather than reducing it by only one item at a time.

## 25. Recursion Depth

**Recursion depth** is the maximum number of stack frames present at
once during a recursive function's execution — precisely the quantity
§24 just analyzed for three different recursion shapes. It is a
property of *how a specific input is processed*, not a fixed property
of the function's source code alone: `sum_list([1])` has a much shallower
depth than `sum_list(list(range(100_000)))`, even though it is the exact
same function. This distinction — depth depends on input, not just on
the function definition — is essential background for §26 and §27,
which cover what happens when depth grows too large.

## 26. Python Recursion Limits

Python enforces a maximum recursion depth as a safety mechanism,
preventing runaway recursion from silently consuming unbounded memory
and crashing the entire program (or the machine) without warning.

```python
import sys

print(sys.getrecursionlimit())   # commonly 1000, though this can vary by Python version/environment
```

This limit can technically be changed:

```python
sys.setrecursionlimit(5000)
```

**This is rarely the right fix**, and should be treated with real
caution: raising the limit does not add more actual memory or make deep
recursion safe — it only delays the `RecursionError`, potentially
trading a controlled, early failure for a much less controlled crash
(e.g., an actual stack overflow at the operating-system level) once the
*new*, higher limit is eventually exceeded, or once available memory
runs out first. If a function is deep enough to need
`setrecursionlimit()`, that is a strong signal to reconsider the
algorithm itself — most often, by converting it to an iterative form
(§30) or by verifying whether the recursion depth can be reduced (e.g.,
divide-and-conquer's O(log n) depth versus linear recursion's O(n)
depth, per §24) — rather than simply raising the ceiling and hoping.

## 27. `RecursionError`

```python
def infinite_recursion(n):
    return infinite_recursion(n + 1)   # no base case reachable — grows forever

infinite_recursion(0)
```

```text
RecursionError: maximum recursion depth exceeded
```

**When this happens:** the function never reaches a base case (missing
entirely, as here, or unreachable due to a §6.2-style progress bug),
and the call stack grows past Python's configured limit (§26).

**How to prevent it, as a checklist:**
- Confirm a base case exists at all (§5).
- Confirm every recursive call makes genuine, provable progress toward
  that base case (§6.2) — the single most common root cause.
- Confirm the base case is actually reachable for **every** valid
  input, including edge cases (an empty list, zero, negative numbers if
  they are possible inputs) — §29 covers several concrete examples of
  this failing subtly.
- For inputs that are simply too large for the recursion's natural
  depth (e.g., linear recursion over a list with hundreds of thousands
  of items), consider converting to iteration (§30) rather than
  raising the recursion limit.

## 28. Debugging Recursive Programs

A systematic, repeatable method, deliberately mirroring the debugging
approach already established for comprehensions and grouping code
earlier in this module (comprehensions chapter's §34; grouping
chapter's §37):

1. **Confirm the base case is correct in isolation.** Call the function
   directly with a base-case input and verify the result by hand,
   before trusting anything about the recursive case.
2. **Add a print statement showing each call's input**, right at the
   top of the function body, so every call's argument is visible as
   execution proceeds:
   ```python
   def factorial(n, depth=0):
       print("  " * depth + f"factorial({n}) called")
       if n == 0:
           return 1
       result = n * factorial(n - 1, depth + 1)
       print("  " * depth + f"factorial({n}) returning {result}")
       return result
   ```
   The indentation (`"  " * depth`) visually reproduces the call-stack
   structure from §8.2 directly in the printed output — deeper calls
   print further indented, making the "going down, then coming back up"
   structure (§7.2, §9) visible at a glance.
3. **Trace by hand using §10's two-table method** for a small input,
   and compare against the actual printed output — any mismatch
   pinpoints exactly which call behaved unexpectedly.
4. **Check for the two most common root causes first**: a missing or
   incorrect `return` (§18), or a recursive call that does not make
   genuine progress toward the base case (§6.2, §27).
5. **If the recursive structure itself remains confusing**, temporarily
   rewrite the function as an explicit loop with a manual stack (§30) —
   sometimes seeing the "unrolled" version makes an otherwise-elusive
   bug immediately obvious.

## 29. Common Recursion Mistakes

1. **Missing base case entirely.**
```python
def broken(n):
    return n * broken(n - 1)   # never checks for a stopping condition!
```
→ **Why wrong:** recurses without limit until `RecursionError` (§27).
**Correct:** add `if n == 0: return 1` (or whatever the problem's true
base case is) before the recursive call. **Lesson:** every recursive
function needs an explicit, checked base case — never assume the
recursion will "just stop."

2. **Base case that is never reached.**
```python
def countdown_odd_only(n):
    if n == 0:
        return
    print(n)
    countdown_odd_only(n - 2)   # skips over 0 entirely if n starts odd!
```
→ **Why wrong:** `countdown_odd_only(5)` produces `5, 3, 1, -1, -3, ...`
forever — `n` skips straight past `0`. **Correct:** either use `n <= 0`
as the base case condition, or ensure the step size can actually land
exactly on the base case for every valid input. **Lesson:** verify the
base case is reachable for *every* input the function might realistically
receive, not just the ones tested first.

3. **Forgetting to `return` the recursive call's result.**
Directly §18's worked example — `numbers[0] + sum_list(numbers[1:])`
written as a bare expression statement instead of `return numbers[0] +
sum_list(numbers[1:])`. **Lesson:** double-check every recursive case
actually returns a value built from its recursive call.

4. **No progress toward the base case.**
Directly §6.2's `broken_countdown(n)` calling `broken_countdown(n)`
instead of `broken_countdown(n - 1)`. **Lesson:** explicitly verify the
argument passed to every recursive call is provably smaller/simpler.

5. **Off-by-one errors in the base case's boundary.**
```python
def factorial(n):
    if n == 1:      # should be n == 0!
        return 1
    return n * factorial(n - 1)

factorial(0)   # infinite recursion — n never equals 1 once it passes 0!
```
→ **Correct:** `if n <= 1: return 1` handles both `0` and `1` safely.
**Lesson:** think through the base case's exact boundary for every
edge-case input, not just the "typical" ones.

6. **Mutating a shared mutable default argument.**
```python
def collect(item, results=[]):   # DANGER: default list is created ONCE, shared across ALL calls!
    results.append(item)
    return results
```
→ **Why wrong:** this is a general Python pitfall (not unique to
recursion), but it appears often in recursive accumulator-style
functions (§17): the default `results=[]` list is created exactly once,
when the function is *defined*, and is silently **reused and
accumulated across every unrelated call** unless a fresh list is
explicitly passed each time. **Correct:**
```python
def collect(item, results=None):
    if results is None:
        results = []
    results.append(item)
    return results
```
**Lesson:** never use a mutable object (a list, dict, or set) as a
default argument value — use `None` and create the real default inside
the function body instead.

7. **Redundant, repeated work (the Fibonacci trap).**
Directly §20.2's observation — naive `fibonacci` recomputes the same
subproblems many times over, at real, measurable cost (§23.2).
**Lesson:** whenever a recursive function makes multiple calls that
might overlap in what they compute, check whether memoization (§37–§39)
is warranted.

8. **Using recursion where a simple loop or built-in already solves the
problem clearly and efficiently.**
`sum_list`, `find_max`, and `count_occurrences` in this chapter are all
genuinely better served by `sum()`, `max()`, and a comprehension with
`sum(condition for ...)` respectively, in real production code —
**Lesson:** recursion is a teaching and problem-structure tool, not an
automatic upgrade; §31–§32 give the actual decision criteria.

9. **Excessive recursion depth for the input size.**
Writing linear recursion (§23.1-style, O(n) depth) over an input that
can realistically be very large — risking `RecursionError` (§27) even
though the *logic* is entirely correct. **Lesson:** for genuinely large,
linear inputs, prefer iteration (§30) or a divide-and-conquer
restructuring that reduces depth to O(log n), if the problem allows it.

## 30. Converting Recursion to Iteration

### 30.1 Simple linear recursion — usually a direct loop conversion

```python
# Recursive
def factorial_recursive(n):
    if n == 0:
        return 1
    return n * factorial_recursive(n - 1)
```
```python
# Iterative — a direct, mechanical translation
def factorial_iterative(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

For **linear** recursion (one recursive call per invocation, §19.1),
converting to a loop is usually straightforward: the accumulator-passing
style from §17 makes this conversion especially mechanical, since the
accumulator argument becomes the loop's own running variable directly.

### 30.2 Branching or tree-style recursion — needs an explicit stack

Converting genuinely branching recursion (§19.1, §20) to iteration is
less mechanical — it requires an **explicit stack** (data-structures
chapter's §17–§18) to manually track the "waiting" work that the call
stack was previously tracking automatically:

```python
def flatten_iterative(items):
    result = []
    stack = list(reversed(items))   # push items in reverse so they pop in original order

    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(reversed(item))
        else:
            result.append(item)

    return result


print(flatten_iterative([1, [2, 3], [4, [5, 6]], 7]))
# [1, 2, 3, 4, 5, 6, 7]
```

This directly reimplements §15.2's recursive `flatten`, but replaces
Python's own call stack with an explicit `stack` list, manually pushed
and popped (data-structures chapter's §18). **Why this matters
practically:** an iterative version using an explicit stack has **no
Python recursion-depth limit** (§26) — it can process arbitrarily deeply
nested data, bounded only by available memory, not by
`sys.getrecursionlimit()`. This is a genuinely important, production-
relevant technique whenever recursion depth risk (§27, §29 mistake #9)
is a real concern for a given problem's expected input sizes.

## 31. When Recursion Is Better

Recursion tends to be the clearer, more maintainable choice when:

- The problem's data is **naturally recursive** — trees (§34), nested
  lists/dictionaries (§15–§16), nested folder structures.
- The algorithm is genuinely **divide-and-conquer** (§21, §40), where
  expressing "solve the same problem on a smaller piece" directly
  mirrors the algorithm's actual mathematical definition.
- The problem involves **exploring multiple possible choices** at each
  step, as in backtracking (§36), where a loop-based equivalent would
  need to manually manage significant bookkeeping that recursion
  handles automatically via the call stack.
- Recursion depth is **naturally bounded and small** relative to
  Python's recursion limit (§26) — e.g., processing a folder tree that
  is realistically only a few levels deep, or divide-and-conquer
  algorithms whose depth is O(log n) (§24.4).

## 32. When Iteration Is Better

Iteration tends to be the better choice when:

- The problem is **fundamentally linear** — one item after another,
  with no natural "smaller version of the same structure" (e.g.,
  summing a list, searching for a value) — exactly the search/count/
  filter/map/aggregate chapter's own five patterns, which are all
  naturally loop-based.
- **Input size can be large enough to risk `RecursionError`** (§26–§27,
  §29 mistake #9) under linear recursion's O(n) depth.
- **Performance is critical**, and the overhead of many nested function
  calls (§3.5) is measurably significant compared to a loop's lower
  per-iteration overhead — verified by actual measurement (Big-O
  chapter's §38), not assumed.
- A **standard library function or built-in already solves the problem
  directly and efficiently** — `sum()`, `max()`, `sorted()`, and the
  comprehension-based patterns from earlier chapters almost always beat
  a hand-written recursive equivalent in real production code (§29
  mistake #8).

**The decision, stated as a single question:** *does this specific
problem's structure genuinely contain smaller versions of itself, in a
way that a loop could only express with significant extra manual
bookkeeping?* If yes, recursion is likely to be the clearer tool. If
the problem is simply "do this once for every item," a loop is very
likely the more direct, appropriate choice.

## 33. Recursive Processing of Nested Structures

Generalizing §15 and §16 into one reusable, explicit template — the
single most practically useful pattern in this entire chapter for real
engineering work with real-world nested data (JSON-like API responses,
configuration files, arbitrarily nested user-generated content):

```python
def process(data):
    if isinstance(data, list):
        return [process(item) for item in data]
    if isinstance(data, dict):
        return {key: process(value) for key, value in data.items()}
    return transform_leaf(data)   # base case: a plain, non-nested value
```

This single function correctly handles **arbitrarily deep** mixtures of
lists, dictionaries, and plain values, because it checks, at every
level, "is this itself a nested structure, or is it a leaf value?" — and
recurses only in the first case. This directly reuses comprehensions
(comprehensions chapter's §8, §10) *inside* a recursive function — the
two techniques from this module combine naturally here, each doing the
part it is suited for: the comprehension expresses "apply this to every
item," and the recursion expresses "and handle however deep this goes."

## 34. Recursion and Tree Data Structures

### 34.1 A minimal tree, represented in plain Python

```python
tree = {
    "value": 1,
    "children": [
        {"value": 2, "children": []},
        {"value": 3, "children": [
            {"value": 4, "children": []},
        ]},
    ],
}
```

A **tree** is a structure made of **nodes**, each holding a value and a
collection of **children** — which are themselves trees (or empty, at
the tree's **leaves**, nodes with no children). This is exactly the
"defined in terms of smaller versions of itself" property flagged back
in §2.1 as recursion's most natural fit.

### 34.2 Recursively summing every value in a tree

```python
def tree_sum(node):
    total = node["value"]
    for child in node["children"]:
        total += tree_sum(child)
    return total


print(tree_sum(tree))   # 1 + 2 + 3 + 4 = 10
```

Base case: a node with no children (`node["children"] == []`) simply
contributes its own value — the `for` loop over an empty list runs zero
times, adding nothing further, which acts as the base case implicitly,
exactly as in §15.2's `flatten`. Recursive case: add this node's own
value to the sum of every child's subtree, each computed by the exact
same function.

### 34.3 Recursively finding a value in a tree (tree search)

```python
def tree_contains(node, target):
    if node["value"] == target:
        return True
    return any(tree_contains(child, target) for child in node["children"])
```

This reuses `any()` (search chapter's §4.9) directly inside the
recursive case — `any(tree_contains(child, target) for child in
node["children"])` asks "is `target` found in *any* of this node's
child subtrees?", short-circuiting (stopping early, per `any()`'s own
behavior) the moment a match is found anywhere in the tree. This is a
direct, worked example of §2.1's "traversing trees" use case, and is
conceptually identical to the depth-first search idea already flagged,
without full implementation, in the data-structures chapter's §19.

## 35. Recursion and Graph Concepts

A **graph** generalizes a tree by allowing nodes to connect to each
other in arbitrary ways — including cycles (a path that eventually
leads back to a node already visited), which trees, by definition,
cannot have. This has one critical, direct consequence for recursion:
**a naive recursive traversal that works perfectly on a tree can loop
forever on a graph with a cycle**, because nothing stops it from
revisiting the same node repeatedly.

```python
graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": ["A"],   # <-- a cycle back to A!
}


def visit_recursive(node, graph, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return   # base case: already visited — stop, preventing infinite recursion
    visited.add(node)
    print(node)
    for neighbor in graph[node]:
        visit_recursive(neighbor, graph, visited)
```

The `visited` **set** (data-structures chapter's §13, chosen precisely
for its O(1) average-case membership testing) is what makes this safe:
`if node in visited: return` is an *additional* base case, specifically
required because a graph's structure — unlike a tree's — does not
guarantee recursion will ever bottom out on its own. This chapter does
not implement full graph algorithms (breadth-first search, depth-first
search as formal, named algorithms, shortest-path algorithms) — those
belong to later, dedicated study — but this single, crucial adaptation
(tracking visited nodes to guarantee termination) is essential
background for that later material, and is a direct, practical
consequence of everything this chapter has already established about
base cases (§5) and provable progress (§6.2).

## 36. Introduction to Backtracking

### 36.1 The core idea

**Backtracking** is a recursive strategy for exploring choices: at each
step, try one possible choice, recurse to explore everything that
follows from it, and if that path does not lead anywhere useful,
**undo** the choice (this is the "backtrack" part) and try the next
possible choice instead.

### 36.2 A manageable example: generating all subsets

```python
def all_subsets(items):
    if not items:
        return [[]]   # base case: the only subset of an empty list is the empty list itself

    first, rest = items[0], items[1:]
    subsets_without_first = all_subsets(rest)
    subsets_with_first = [[first] + subset for subset in subsets_without_first]
    return subsets_without_first + subsets_with_first


print(all_subsets([1, 2]))
# [[], [2], [1], [1, 2]]
```

At each step, this explores **both** choices for the first item —
*exclude* it (`subsets_without_first`) or *include* it
(`subsets_with_first`) — and combines the results. This is a clean,
teaching-scale example of backtracking's essence ("try each choice, and
explore what follows from it") without needing an explicit "undo" step,
because each branch naturally builds its own independent result rather
than mutating shared state. This directly connects to §2.1's "exploring
combinations" use case, and demonstrates branching recursion (§19–§20)
applied to a genuinely different kind of problem than Fibonacci's pure
number computation. A full treatment of backtracking (with pruning,
constraint-checking, and classic problems like generating permutations
or solving puzzles) belongs to later, dedicated algorithmic study — this
section's goal is solely the conceptual introduction, on a manageable
example.

## 37. Introduction to Dynamic Programming

### 37.1 The core idea

**Dynamic programming** is an optimization technique for recursive (or
recursion-like) problems that have two specific properties:

- **Overlapping subproblems** — the same smaller subproblem is needed
  more than once (exactly what §20.2 observed in Fibonacci's call
  tree).
- **Optimal substructure** — the best solution to the whole problem can
  be built directly from the best solutions to its subproblems.

When both properties hold, **storing (rather than recomputing) each
subproblem's answer the first time it is solved** turns an exponential-
time naive recursive algorithm into a dramatically faster one.

### 37.2 Why Fibonacci is the textbook example

Naive `fibonacci` (§12.1, §20, §23.2) has *exactly* both properties:
`fibonacci(2)` is needed repeatedly (overlapping subproblems), and
`fibonacci(n)`'s answer is built directly from `fibonacci(n-1)` and
`fibonacci(n-2)`'s answers (optimal substructure). This is precisely why
it is used, throughout this chapter and throughout most introductions
to the subject, as the running example for dynamic programming's core
idea — the fix (§38) is almost mechanical once the diagnosis (§20.2) is
understood.

## 38. Memoization as a Recursive Optimization

### 38.1 The idea, implemented by hand

**Memoization** is dynamic programming's most direct technique: keep a
cache (a dictionary, mapping each input already seen to its already-
computed result) and check that cache **before** doing any recursive
work.

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

- `if n in cache: return cache[n]` — an **additional base case**: if
  this exact subproblem has already been solved, return the stored
  answer immediately, with **no further recursive calls at all** — this
  single check is what eliminates all of Fibonacci's repeated,
  duplicated work from §20.2.
- `cache[n] = result` — before returning, store this subproblem's
  answer, so any future call needing `fibonacci_memoized(n, ...)` again
  can simply look it up.
- The dictionary lookup and insertion here are each O(1) average-case
  (dictionary chapter's §10, Big-O chapter's §20) — cheap enough that
  adding this cache genuinely transforms the algorithm's overall time
  complexity, rather than merely shifting the cost elsewhere.

### 38.2 The complexity payoff

With memoization, each distinct value of `n` from `0` up to the
original input is computed **exactly once** — `n` distinct subproblems,
each doing O(1) work beyond its (now cache-hit, O(1)) recursive calls.
**Time: O(n)** — a dramatic improvement over naive Fibonacci's O(2ⁿ)
(§23.2), for the exact same problem, achieved purely by refusing to
recompute what has already been computed once.

## 39. Recursion with `functools.lru_cache`

### 39.1 Python's built-in memoization decorator

Writing a manual cache dictionary (§38.1) works, but Python's standard
library provides a ready-made tool for exactly this pattern:

```python
from functools import lru_cache


@lru_cache(maxsize=None)
def fibonacci_cached(n):
    if n <= 1:
        return n
    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)
```

`@lru_cache(maxsize=None)` is a **decorator** — it wraps
`fibonacci_cached` so that every call is automatically checked against
an internal cache (keyed by the function's arguments) before actually
running the function body, and every new result is automatically stored
in that cache afterward — precisely §38.1's manual technique, provided
for free, without needing to thread a `cache` argument through every
call by hand. `maxsize=None` means the cache can grow without a fixed
limit; a specific number instead limits how many distinct results are
kept before older ones are discarded (an "LRU" — least-recently-used —
eviction policy, useful when memory needs to be bounded, not covered
further here).

### 39.2 When to reach for `lru_cache` vs. a manual cache

`@lru_cache` is the right default choice for any recursive function
whose arguments are **hashable** (the same requirement introduced for
dictionary keys and set elements in the data-structures chapter's §9,
§13) and whose subproblems genuinely overlap (§37.1) — it is simpler,
less error-prone, and more idiomatic than threading a manual cache
dictionary through every call, as §38.1 did purely for teaching
transparency. A manual cache remains useful specifically when the cache
itself needs custom behavior `lru_cache` does not offer (for example,
caching based on only *part* of the arguments, or needing to inspect or
clear the cache under specific, non-default conditions).

## 40. Divide-and-Conquer Examples

### 40.1 Binary search — already fully worked in §21.2

Restated here as this section's first, simplest example, since §21
already developed it in complete detail: divide the search space in
half, conquer by recursing into exactly one half, combine trivially by
passing the found result straight back up.

### 40.2 Merge sort — divide-and-conquer applied to sorting

```python
def merge_sort(items):
    if len(items) <= 1:
        return items   # base case: a list of 0 or 1 items is already sorted

    middle = len(items) // 2
    left_half = merge_sort(items[:middle])     # conquer: sort the left half
    right_half = merge_sort(items[middle:])     # conquer: sort the right half
    return merge(left_half, right_half)          # combine: merge two sorted halves into one


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


print(merge_sort([5, 2, 9, 1, 5, 6]))
# [1, 2, 5, 5, 6, 9]
```

**Divide:** split the list into two roughly equal halves. **Conquer:**
recursively sort each half (the exact same operation, on half the
data). **Combine:** `merge()` walks both already-sorted halves
simultaneously, always taking whichever front item is smaller, until
one half is exhausted, then appends whatever remains of the other —
this is the step that does genuine, non-trivial combining work, unlike
binary search's trivial pass-through combine step. This connects
directly to the previous chapters' own treatment of sorting (grouping
chapter's §22, Big-O chapter's §22): merge sort is precisely how
Python's own highly optimized Timsort (Big-O chapter's §35) achieves
its O(n log n) guarantee — **unlike** binary search, this recursion
must conquer **both** halves (not just one), which is exactly why merge
sort costs O(n log n) rather than binary search's O(log n): at every
one of the O(log n) levels of recursion, `merge()` does O(n) total work
across all the merges at that level, giving O(n) × O(log n) = O(n log n)
overall — production Python code should still simply call the built-in
`sorted()` (grouping chapter's §17) rather than reimplementing merge
sort; this example exists to make divide-and-conquer's "combine" step
concrete on a second, meaningfully different problem from binary
search.

## 41. Production Engineering Considerations

- **Prefer the standard library's own solution first.** `sum()`,
  `max()`, `sorted()`, and comprehensions almost always outperform, and
  are more maintainable than, a hand-rolled recursive equivalent for
  problems that are not genuinely recursive in structure (§29 mistake
  #8, §32).
- **Guard against unbounded or attacker-influenced recursion depth.**
  If a recursive function processes external, untrusted input (e.g., a
  deeply nested JSON payload from an API request), an unexpectedly deep
  or maliciously crafted input could trigger `RecursionError` (§27) or
  exhaust memory — validate or bound depth explicitly, or use an
  iterative approach with an explicit stack (§30.2) when input depth
  cannot be trusted or controlled.
- **Use `@lru_cache` (§39) deliberately, not automatically.** It is
  excellent for pure functions (functions whose output depends only on
  their input, with no side effects — a concept from an earlier module)
  with genuinely overlapping subproblems; applying it to a function with
  side effects, or one whose arguments are rarely repeated, wastes
  memory for no benefit.
- **Document recursive functions' base case and progress argument
  explicitly**, especially for less obviously recursive problems (tree/
  graph traversal, backtracking) — a brief comment stating *why* the
  recursion is guaranteed to terminate (§6.2) saves the next engineer
  real debugging time.
- **Measure before assuming recursion is a performance problem.**
  Following the Big-O chapter's own standing principle (§31, §38, §44
  there): analyze first, then measure with `timeit`/`cProfile` if a
  recursive function is suspected to be a genuine bottleneck, rather
  than reflexively rewriting working recursive code into iteration on
  intuition alone.

## 42. Real-World Applied AI / Data Engineering Connections

- **Parsing nested configuration or API responses.** JSON-like data
  (nested dictionaries and lists, exactly §15–§16's shape) from
  external APIs or config files is naturally processed with the
  recursive template from §33 — extracting all values, validating
  every nested field, or reshaping deeply nested structures into a flat
  form for downstream use.
- **Directory/file-system traversal.** Preparing a dataset stored across
  a nested folder structure (e.g., a corpus of documents organized into
  subfolders by source or date) is a direct, practical instance of
  §2.1's "processing folders" example — recursively walking every
  subfolder to collect every file.
- **Document and tree-structured data processing.** Structured document
  formats (nested sections, nested comment threads, hierarchical
  category taxonomies) map directly onto §34's tree-processing pattern
  — recursively collecting, transforming, or aggregating values across
  an entire hierarchy.
- **Preprocessing pipelines with recursive normalization.** A pipeline
  that must recursively normalize deeply nested feature dictionaries
  (as in §33) before flattening them into a fixed feature vector for a
  model is a genuinely common preprocessing step in applied ML work.
- **Graph-shaped data.** Knowledge graphs, dependency graphs between
  documents or entities, and citation networks all require the
  visited-set safeguard from §35 the moment any recursive traversal is
  written over them, since real-world relationship graphs frequently
  contain cycles.
- **Where recursion is deliberately avoided in practice.** Most
  production data-engineering code processing large, flat datasets
  (the kind covered throughout Modules 04's earlier chapters — filtering
  and aggregating millions of transaction records, for example) uses
  iteration and the built-in patterns from those chapters, precisely
  because that data is not naturally recursive and the dataset sizes
  involved make deep recursion both unnecessary and risky (§26–§27,
  §32) — recursion's real home in applied AI engineering is
  specifically the *nested and hierarchical* data described above, not
  flat, tabular data processing.

## 43. Refactoring and Code-Quality Guidance

Directly applying the comprehensions chapter's own readability
principles (§24–§28 there) to recursive code specifically:

- **Name the base case and recursive case clearly**, even via comments,
  when they are not immediately obvious from the code's shape alone —
  this mirrors that chapter's "complexity should be named" principle
  (§28 there), applied here to recursion's two mandatory parts (§4–§6).
- **Extract a complicated recursive helper's non-trivial logic into its
  own named function**, exactly as `merge()` was kept separate from
  `merge_sort()` in §40.2 — this keeps the recursive structure itself
  (divide, conquer, combine) visible and uncluttered by the mechanical
  details of any one step.
- **Prefer accumulator-passing (§17) or memoization (§38–§39) over ad
  hoc mutable default arguments** for threading state through recursive
  calls — mutable default arguments are a well-known Python pitfall
  (§29 mistake #6) regardless of whether recursion is involved.
- **Add a docstring stating the function's base case and what "smaller"
  means for its argument**, for any recursive function whose recursive
  structure is not immediately obvious from its name — this is one of
  the few places in this module where a comment/docstring earns its
  place under the "non-obvious constraint" standard from this project's
  general coding guidance, since a base case's correctness is precisely
  the kind of subtle, easy-to-violate invariant worth stating explicitly.
- **Convert to iteration deliberately, not defensively** — per §30–§32,
  only when input size, depth risk, or measured performance actually
  warrants it, not merely because recursion "feels unfamiliar."

## 44. Debugging Workshop

Apply §28's method to each of the following broken functions. For each:
identify the bug, name which category from §29 it falls into, and state
the fix.

**Workshop 1.**
```python
def count_down_to_zero(n):
    print(n)
    count_down_to_zero(n - 1)
```

**Workshop 2.**
```python
def list_length(items):
    if items == []:
        return 0
    return list_length(items[1:])
```

**Workshop 3.**
```python
def power(base, exponent):
    if exponent == 0:
        return 1
    return base * power(base, exponent)
```

**Workshop 4.**
```python
def collect_evens(numbers, found=[]):
    if not numbers:
        return found
    if numbers[0] % 2 == 0:
        found.append(numbers[0])
    return collect_evens(numbers[1:], found)
```

**Workshop 5.**
```python
def tree_height(node):
    if not node["children"]:
        return 1
    return 1 + max(tree_height(child) for child in node["children"])
```

Work through each using §28's debugging method (trace the base case in
isolation, add indented call/return prints, compare against §10's
two-table trace) and confirm your diagnosis against §29's numbered
mistake categories: Workshop 1 is missing a base case entirely
(mistake #1); Workshop 2 never uses its recursive call's result and
never shrinks toward counting anything (mistakes #3 and #4 combined —
it always returns `0`); Workshop 3 does not shrink `exponent` on its
recursive call (mistake #4); Workshop 4 uses a mutable default argument
that is silently shared and accumulated across unrelated calls
(mistake #6); Workshop 5 is actually correct as written — a useful
reminder that not every function handed to you in a debugging exercise
is broken, and verifying correctness with a trace (§10) is as valuable
a skill as finding bugs.

## 45. Progressive Exercises

Work through each one using §10's two-table tracing method and §47's
review checklist to self-verify your solution before moving on — for
every exercise, first identify the base case and the recursive case
explicitly (§4–§6), then confirm genuine progress toward the base case
(§6.2) before running the code.

### Level 1 — Beginner

**1.** Write a recursive function `count_down(n)` that prints every
number from `n` down to `1`.

**2.** Write a recursive function `sum_to_n(n)` that returns the sum of
every integer from `1` to `n`.

**3.** Write a recursive function `power_of_two(n)` that returns `2`
raised to the power `n`.

**4.** Write a recursive function `count_items(items)` that returns how
many items are in a list, without using `len()`.

**5.** Trace, by hand, using §10's method, what `factorial(4)` computes
at every step, and what it returns during unwinding.

### Level 2 — Intermediate

**6.** Write a recursive function `reverse_list(items)` that returns a
new list with the items in reverse order.

**7.** Write a recursive function `is_sorted(numbers)` that returns
`True` if a list is sorted in non-decreasing order.

**8.** Write a recursive function `sum_of_digits(n)` that sums the
digits of a non-negative integer.

**9.** Write a recursive function `flatten_once(items)` that flattens
only **one level** of nesting (e.g., `[1, [2, 3], [4]]` becomes
`[1, 2, 3, 4]`, but a doubly nested list stays partially nested).

**10.** Convert your `sum_to_n(n)` from exercise 2 into an iterative
version, and confirm both produce identical results for several inputs.

### Level 3 — Advanced

**11.** Write a recursive function `tree_count_nodes(node)` that
returns the total number of nodes in a tree shaped like §34.1's
example.

**12.** Write a recursive function `tree_max_value(node)` that returns
the largest value anywhere in a tree.

**13.** Write `fibonacci_memoized` from scratch (without looking back at
§38.1), then verify it produces the same results as naive `fibonacci`
for `n` from `0` to `10`.

**14.** Rewrite `flatten` (§15.2) as an iterative function using an
explicit stack (following §30.2's pattern), and verify it produces
identical output to the recursive version for a deeply nested input.

**15.** Write a recursive function `all_permutations(items)` that
returns every possible ordering of a small list (hint: for each item,
consider it as the "first" item, and recursively permute the rest).

### Level 4 — Production-Oriented

**16.** Write a recursive function `deep_get(data, keys)` that safely
retrieves a value from an arbitrarily nested dictionary given a list of
keys representing a path (e.g., `deep_get({"a": {"b": {"c": 1}}}, ["a",
"b", "c"])` returns `1`), returning `None` if any key along the path is
missing.

**17.** Write a recursive function `count_files(tree)` that counts the
total number of files in a nested folder structure represented as
`{"files": [...], "folders": [nested folder dicts...]}`.

**18.** Using `@lru_cache`, write a memoized recursive function that
computes the `n`th value of a different simple recurrence of your
choice (not Fibonacci), and explain, in a sentence, why memoization
helps for that specific recurrence.

**19.** Write a recursive function that safely traverses a graph
represented as an adjacency dictionary (following §35's pattern),
printing every reachable node exactly once, even if the graph contains
a cycle.

**20.** Given a recursive function you consider genuinely necessary
(not better solved by a built-in or a simple loop), write a one-
paragraph justification for why recursion is the right tool for that
specific problem, referencing this chapter's decision criteria (§31–
§32).

## 46. Mini Project

**"Nested Configuration Validator and Flattener"**

### Requirements

Given an arbitrarily nested configuration structure (a mix of
dictionaries, lists, and plain values, exactly §15–§16 and §33's
shape), build a small tool that:

1. Recursively validates that every leaf value is one of an allowed set
   of types (`str`, `int`, `float`, `bool`).
2. Recursively counts the total number of leaf values in the structure.
3. Recursively flattens the structure into a single dictionary whose
   keys are dotted paths (e.g., `"settings.limits.max_users"`) and
   whose values are the corresponding leaf values.
4. Recursively finds the maximum nesting depth of the structure.
5. Reports any invalid leaf values found, along with their dotted path.

### Before implementing, document:

- **Problem** — build a small, general-purpose tool for validating and
  reshaping nested configuration data, of the kind a real application
  might load from a JSON or YAML config file.
- **Inputs** — an arbitrarily nested combination of `dict`, `list`, and
  plain leaf values.
- **Outputs** — a boolean (all valid?), an integer (leaf count), a
  flattened dictionary, an integer (max depth), and a list of invalid
  paths.
- **Assumptions** — dictionary keys are always strings; lists may
  contain further nested structures or plain values; the structure is
  finite (no cycles — unlike §35's graph case, a JSON-like config
  structure is guaranteed to be a tree, not a graph).
- **Edge cases** — an empty dictionary or list at any level; a
  completely flat (non-nested) structure (depth of 1); a `None` value
  as a leaf (decide explicitly whether `None` counts as valid — this
  project treats it as invalid, since it is not in the allowed type
  set).
- **Pseudocode:**
  ```
  to flatten(data, path=""):
      if data is a dict:
          for each key, value in data.items():
              recurse into value, with path extended by ".key"
      if data is a list:
          for each index, value in enumerate(data):
              recurse into value, with path extended by "[index]"
          otherwise (data is a leaf):
              record (path, data) in the flattened result

  to count_leaves(data): count entries in flatten(data)

  to max_depth(data):
      if data is a dict or list and non-empty:
          1 + max(max_depth(child) for child in data's children)
      otherwise: 1  (a leaf counts as depth 1)

  to validate(data):
      for each (path, value) in flatten(data):
          if type(value) not in allowed types: record path as invalid
  ```
- **Data transformations** — this project directly reuses §33's general
  nested-structure template, specialized four different ways (flatten,
  count, depth, validate) — each a small variation on the same
  underlying recursive shape.
- **Complexity** — every operation visits each leaf and each nesting
  level exactly once: **O(n)** time, where `n` is the total number of
  values (leaf and container) in the structure; **space** proportional
  to the structure's **maximum depth** for the call stack (§24), plus
  O(n) for the flattened output dictionary itself.

### Reference Implementation

```python
ALLOWED_TYPES = (str, int, float, bool)


def flatten_config(data, path=""):
    result = {}

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            result.update(flatten_config(value, new_path))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            new_path = f"{path}[{index}]"
            result.update(flatten_config(value, new_path))
    else:
        result[path] = data   # base case: a leaf value

    return result


def count_leaves(data):
    return len(flatten_config(data))


def max_depth(data):
    if isinstance(data, dict) and data:
        return 1 + max(max_depth(value) for value in data.values())
    if isinstance(data, list) and data:
        return 1 + max(max_depth(item) for item in data)
    return 1   # base case: a leaf, or an empty dict/list, counts as depth 1


def find_invalid_paths(data):
    flat = flatten_config(data)
    return [
        path
        for path, value in flat.items()
        if not isinstance(value, ALLOWED_TYPES) or isinstance(value, type(None))
    ]


def validate_and_report(data):
    return {
        "is_valid": len(find_invalid_paths(data)) == 0,
        "leaf_count": count_leaves(data),
        "flattened": flatten_config(data),
        "max_depth": max_depth(data),
        "invalid_paths": find_invalid_paths(data),
    }
```

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
print(report["leaf_count"])       # 5
print(report["max_depth"])         # 4
print(report["invalid_paths"])     # ['settings.limits.timeout']
print(report["flattened"])
# {'name': 'app', 'settings.debug': True, 'settings.limits.max_users': 100,
#  'settings.limits.timeout': None, 'tags[0]': 'prod', 'tags[1]': 'stable'}
```

**The lesson this project demonstrates concretely:** four seemingly
different requirements (validation, counting, flattening, depth-
measurement) all reduce to the *exact same* recursive traversal
template from §33, each simply doing something slightly different at
the leaf case — directly reinforcing that recognizing a problem's
recursive *shape* is more valuable than memorizing any single recursive
function by rote.

## 47. Review Checklist

Use this checklist to confirm mastery before moving on:

- [ ] I can state, in my own words, what a base case and a recursive
      case are, and why both are mandatory.
- [ ] I can trace a recursive function by hand, both the "going down"
      and "coming back up" (unwinding) phases, for a small input.
- [ ] I can explain what a stack frame is and why recursion depth has a
      memory cost.
- [ ] I can write simple recursive functions over numbers, strings,
      lists, and nested dictionaries/lists.
- [ ] I can identify and fix each of the mistakes in §29, given broken
      code.
- [ ] I can explain why naive Fibonacci is O(2ⁿ) in time but only O(n)
      in space, and why those two numbers differ.
- [ ] I can explain, precisely, what `RecursionError` means and how to
      prevent it.
- [ ] I can convert simple linear recursion into an equivalent loop,
      and explain why branching recursion needs an explicit stack to
      convert instead.
- [ ] I can state, without hedging, when recursion is the better choice
      and when iteration is, for a new problem I have not seen before.
- [ ] I can explain memoization's core idea and implement it either
      manually or with `@lru_cache`.
- [ ] I can explain, at a conceptual level, what divide-and-conquer and
      backtracking are, using binary search and merge sort as reference
      examples.
- [ ] I understand why a recursive graph traversal needs a visited set,
      while a tree traversal does not.
- [ ] I can look at an unfamiliar recursive function and correctly
      state its time and space complexity, showing my reasoning.

## 48. Interview Questions

**Foundational**

- What is recursion? What is a base case? What is a recursive case?
- Why must every recursive function have a base case?
- What is a stack frame, and what does it contain?
- What is the call stack, and how does it relate to recursion?
- What is stack unwinding?

**Intermediate**

- What is the difference between recursion and iteration? Is one always
  better than the other?
- Why does forgetting to `return` a recursive call's result cause a bug,
  even if the recursive call itself computes the right value?
- What happens if a recursive function's argument never gets closer to
  its base case?
- What is `RecursionError`, and what causes it?
- How would you convert a simple recursive function into an iterative
  one?
- Why is a mutable default argument (like `def f(x, acc=[])`) dangerous
  in a recursive accumulator function?

**Advanced**

- Why is naive recursive Fibonacci O(2ⁿ) in time, but only O(n) in
  space? Walk through the reasoning.
- What is memoization, and what two properties of a problem make it
  effective?
- How does `functools.lru_cache` work, conceptually, and when would you
  prefer a manual cache instead?
- What is divide-and-conquer? Name and explain its three steps, using
  either binary search or merge sort as your example.
- Why does a recursive graph traversal require tracking visited nodes,
  while a recursive tree traversal generally does not?
- What is backtracking, conceptually, and how does it differ from
  straightforward divide-and-conquer recursion?

**Scenario-based**

- "You're processing a deeply nested JSON payload from an external API,
  and occasionally it triggers a `RecursionError`. What would you
  investigate first, and what are two different ways you might fix
  it?"
- "A teammate wrote a recursive function to sum a list of a million
  numbers, and it crashes. What is the most likely cause, and what
  would you recommend instead?"
- "You need to compute the 40th Fibonacci number. The naive recursive
  version is far too slow. What would you change, and why does that fix
  the performance problem specifically?"
- "How would you decide whether a new problem you're given should be
  solved recursively or iteratively? Walk through your reasoning
  process."

## 49. Final Mental Model

**RECURSION = "solving a problem by having a function solve a smaller
version of the same problem, until the problem becomes small enough to
solve directly."**

```
PROBLEM
  → is it small enough to answer directly?  (BASE CASE)
      → yes: return the answer
      → no:  do a small amount of work, then solve a SMALLER version
             of the SAME problem (RECURSIVE CASE)
  → wait for that smaller call to finish (the call stack tracks this)
  → use its result to compute and return THIS call's own result
  → (this repeats, all the way back up, until the original call returns)
```

**Two questions to ask before writing any recursive function:**

1. *What is the smallest version of this problem I can answer directly?*
   (the base case)
2. *How do I turn this problem into a provably smaller version of
   itself?* (the recursive case, with guaranteed progress)

**Two questions to ask before choosing recursion over iteration for a
new problem:**

1. *Does this problem's data or structure naturally contain smaller
   versions of itself* (a tree, nested data, divide-and-conquer, or
   exploring choices)*, or is it fundamentally a flat, linear
   sequence of steps?*
2. *Is the expected recursion depth safely within Python's limits
   (§26), or would an iterative approach with an explicit stack (§30.2)
   be the safer, more scalable choice?*

And the chapter's final, standing reminder: **recursion is a
problem-solving technique to reach for deliberately, when a problem's
own structure calls for it — never a habit to apply simply because it
is available.**
