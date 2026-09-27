# Preconditions, Postconditions, and Edge Cases

## Why this topic matters

Most beginner code is only ever tested with "normal," friendly data — and
then breaks the first time it meets an empty list, a duplicate value, or an
unexpected input. Professional programmers build a habit of asking, before
they even finish writing a function: "What do I assume is true before this
runs? What do I promise is true after it runs? And what unusual inputs
could break those promises?" This lesson teaches that habit directly, using
vocabulary (preconditions, postconditions, invariants, edge cases) that you
will keep using for the rest of your programming life, including in formal
testing (Module 1.7) and in production systems far beyond this course.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what a precondition and a postcondition are, in plain English.
- Explain what an invariant is, at a beginner level.
- List, for a given function, its normal cases and its edge cases:
  invalid input, empty input, duplicates, and boundary values.
- Write small Python functions that check their assumptions and handle
  unusual input sensibly.

## Prerequisites

- [Problem Decomposition](05-problem-decomposition.md)

## Key terms

| Term | Plain-English definition |
|---|---|
| **Precondition** | Something that must be true *before* a function runs, for it to work correctly. |
| **Postcondition** | Something that is guaranteed to be true *after* a function finishes running correctly. |
| **Invariant** | Something that stays true throughout a function's execution, or throughout the life of a piece of data, and is never allowed to become false. |
| **Normal case** | An input that is typical, expected, and well-behaved. |
| **Edge case** | An unusual input that sits at the "edge" of what a function was designed to handle, and is a common place for bugs to hide. |
| **Invalid input** | Input that does not meet a function's basic assumptions, such as text where a number was expected. |
| **Empty input** | Input with no items at all, such as an empty list or empty text. |
| **Duplicate** | An input value that appears more than once, when the code may have (wrongly) assumed all values were unique. |
| **Boundary value** | A value right at the edge of an allowed range, such as the smallest or largest accepted number. |

## Step-by-step explanation

### 1. Preconditions: what must be true before you start

A **precondition** is an assumption a function makes about its input,
which must hold for the function to behave correctly. For example, a
function that calculates an average by dividing by the number of items
assumes the list is not empty — dividing by zero would break it. Writing
down preconditions forces you to notice these hidden assumptions instead
of discovering them by crashing.

### 2. Postconditions: what you promise after you finish

A **postcondition** is a guarantee about the result, assuming the
preconditions were met. For a function `sorted_ascending(numbers)`, a
reasonable postcondition is "the returned list contains the same numbers as
the input, arranged from smallest to largest." Postconditions are what you
would check to convince yourself (or a test, in Module 1.7) that a function
actually did its job correctly, not just that it ran without crashing.

### 3. Invariants: what must never stop being true

An **invariant** is a condition that must remain true the entire time,
not just at the start or the end. For a running total of expenses, an
invariant might be "the total is never negative" (assuming expenses cannot
be negative amounts). For a bank account balance during a transfer, an
invariant might be "the total money across both accounts never changes."
Invariants are especially important once you study state in
[topic 8](08-state-and-state-modelling.md), where you must ensure certain
facts about a system's state remain true across many operations.

### 4. Edge cases: where bugs hide

Most bugs are not found in ordinary, well-behaved input — they are found at
the "edges" of what a function was designed to handle. A disciplined
programmer always asks about these categories of edge cases for any new
function:

- **Empty input** — an empty list, an empty string. What should happen?
- **Invalid input** — the wrong type or an impossible value, like a
  negative age or text where a number was expected.
- **Duplicates** — repeated values, when the logic assumed everything was
  unique.
- **Boundary values** — the smallest and largest values a function is
  meant to accept, and values just outside that range (for example, if
  ages 0–120 are valid, what about exactly `0`, exactly `120`, `-1`, and
  `121`?).

Asking these four questions about every function you write, *before*
calling it "done," is one of the most valuable habits in this entire
curriculum.

## Examples

### Example 1 — A function with an unstated precondition, and the crash it causes

```python
def average(numbers):
    total = 0
    for number in numbers:
        total = total + number
    return total / len(numbers)


print(average([10, 20, 30]))   # works fine
print(average([]))             # crashes
```

**Plain-English explanation:**

- `average(numbers)` has a hidden **precondition**: `numbers` must not be
  empty, because the last line divides by `len(numbers)`.
- The first call, `average([10, 20, 30])`, meets that precondition, and
  runs correctly, printing `20.0`.
- The second call, `average([])`, violates the precondition, because
  `len([])` is `0`, so `total / len(numbers)` becomes `total / 0`, which
  Python cannot do. It raises a `ZeroDivisionError` and the program stops.
- This example is the same crash you first saw in
  [topic 1](01-algorithms-programs-and-data.md), but now you have the
  vocabulary to describe *why* it happened precisely: an unstated
  precondition ("the list is not empty") was silently assumed, and never
  checked.

### Example 2 — Making the precondition explicit and defining a postcondition

```python
def average(numbers):
    if len(numbers) == 0:
        return None
    total = 0
    for number in numbers:
        total = total + number
    return total / len(numbers)


print(average([10, 20, 30]))   # 20.0
print(average([]))             # None
```

**Plain-English explanation:**

- The precondition ("`numbers` is not empty") is now **checked explicitly**
  with `if len(numbers) == 0:` rather than merely assumed.
- When the precondition is violated (empty list), the function returns
  `None` — Python's built-in value that represents "nothing" or "no
  result" — instead of crashing. This is a deliberate design decision: the
  **postcondition** of this function is now "returns the numeric average
  if the list has at least one number, or `None` if the list is empty,"
  and it never crashes on this particular kind of bad input.
- Whoever calls `average(...)` now must remember to check for `None` before
  using the result as a number — that's the trade-off of this design.
  (Module 1.3 introduces a different, often better, way to signal this
  kind of problem, using exceptions — but the underlying discipline of
  naming the precondition and deciding what happens when it's violated is
  identical.)
- Notice the *behavior on normal input hasn't changed at all* — only the
  behavior at the previously unhandled edge case has improved. This is the
  core benefit of thinking about edge cases: normal cases keep working
  exactly as before, while dangerous surprises are removed.

### Example 3 — A function tested against a full checklist of edge cases

This example defines a function to validate a simple password rule set,
and then deliberately runs it against normal cases *and* every edge-case
category from step 4 above, to show what a thorough check looks like.

```python
def validate_password(password):
    if not isinstance(password, str):
        return "invalid: not text"
    if len(password) == 0:
        return "invalid: empty"
    if len(password) < 8:
        return "invalid: too short"
    if len(password) > 64:
        return "invalid: too long"
    return "valid"


test_cases = [
    "hunter22",                 # normal case, meets the minimum length
    "",                         # empty input
    "short",                    # too short (below the boundary)
    "a" * 8,                    # boundary value: exactly the minimum length
    "a" * 64,                   # boundary value: exactly the maximum length
    "a" * 65,                   # just past the maximum boundary
    12345678,                   # invalid input: not text at all
]

for case in test_cases:
    print(repr(case), "->", validate_password(case))
```

**Plain-English explanation:**

- `validate_password(password)` checks its input step by step, from the
  most fundamental assumption (is it text at all?) to the most specific
  rule (is the length in the allowed range?). `isinstance(password, str)`
  asks Python directly "is this value of type text (`str`)?" — this
  guards against **invalid input** where something other than text is
  passed in, such as a number.
- The **postcondition** of this function is: it always returns one of a
  fixed, known set of text messages, and it never crashes, no matter what
  is passed in — a strong, clear guarantee that makes it safe to call with
  any data.
- `test_cases` is deliberately built to cover every edge-case category:
  a normal password; **empty input** (`""`); a **boundary value** just
  below the minimum (`"short"`, 5 characters); exact **boundary values**
  at both the minimum (8 characters, using `"a" * 8` to repeat the letter
  `"a"` eight times) and the maximum (64 characters); a value just past
  the boundary (65 characters); and **invalid input** that isn't even text
  (the plain number `12345678`).
- The `for case in test_cases:` loop calls the function once per case, and
  `repr(case)` prints the value in a form that makes empty strings and
  numbers visually easy to tell apart in the output (`''` for an empty
  string versus `12345678` for a number).
- Running this prints one line per test case, showing exactly how the
  function responds to each category. Trace through it by hand — for each
  line, decide what you expect *before* running it, exactly as the
  engineering loop in the module [README](README.md) describes.
- This example shows the complete discipline this topic teaches: identify
  the categories of edge cases first, deliberately construct a test input
  for each category, and confirm the function's behavior matches its
  stated postcondition for every single one — not just the cases that
  happen to come to mind by accident.

## Common beginner mistakes

- **Only testing the "happy path."** Running a function once with friendly,
  expected data and declaring it "done" without ever trying an empty list,
  invalid input, or a boundary value.
- **Assuming input is always well-formed.** Especially input from a user,
  a file, or (later) an external system — always **untrusted** until
  checked, as you'll see again in Module 1.5.
- **Not deciding, on purpose, what should happen for bad input.** Letting a
  program crash "by accident" rather than deliberately deciding — and
  documenting — that certain input is invalid and what should happen when
  it occurs.
- **Confusing "boundary value" with "any small number."** A boundary value
  is specifically a value at the exact edge of an allowed range (the
  smallest allowed, the largest allowed, and one step past each edge), not
  just any small or unusual number.
- **Forgetting invariants once a program has more moving parts.** A rule
  that always held true in a simple version of a program (for example,
  "total is never negative") can quietly break once more code paths are
  added, if it isn't checked or kept in mind deliberately.

## Try it yourself

1. For the function `total_of(expenses)` from
   [topic 5](05-problem-decomposition.md), write down its precondition(s)
   and postcondition in plain English. Does it currently handle an empty
   list correctly? What about a list containing a negative number (a
   refund)? Decide whether that should be considered valid or invalid, and
   why.
2. Write a function `first_positive(numbers)` that returns the first
   positive number in a list. Before coding, list at least four edge cases
   you should test (include an empty list and a list with no positive
   numbers at all). Then implement the function and test it against your
   list.
3. Write a function `remove_duplicates(items)` that returns a new list with
   duplicate values removed, keeping the first occurrence of each value.
   Test it on a list with no duplicates, a list that is all duplicates of
   one value, and an empty list.
4. Take `validate_password` from Example 3 and add one more rule of your
   choice (for example, requiring at least one digit). Update the test
   cases to include a new edge case that specifically targets your new
   rule.

## Summary

- A **precondition** is something that must be true before a function runs
  correctly; a **postcondition** is something guaranteed to be true after
  it finishes, assuming the precondition held.
- An **invariant** is a fact that must remain true throughout execution,
  not just at the start or end.
- **Edge cases** are unusual inputs where bugs commonly hide: empty input,
  invalid input, duplicates, and boundary values.
- Deliberately checking preconditions and testing every edge-case category
  turns "it seemed to work when I tried it" into a real, defensible claim
  that a function behaves correctly.
- Deciding, on purpose, how a function should behave on bad input (return
  a special value, or refuse to run) is a design choice, not an accident.

## Completion checklist

- [ ] I can state the precondition(s) and postcondition of a function I
      have written.
- [ ] I can explain, with my own example, what an invariant is.
- [ ] I can list the four edge-case categories from memory: empty input,
      invalid input, duplicates, and boundary values.
- [ ] I have written a function and deliberately tested it against all
      four edge-case categories, not just normal input.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

AI agents and tools regularly receive messy, unpredictable input: a user's
free-form message, a document with missing fields, or a tool result that
came back empty or malformed. An agent or tool built without deliberately
considering preconditions, postconditions, and edge cases will fail
unpredictably in production, often in ways that are hard to reproduce and
debug. Thinking about "what if the input is empty, invalid, duplicated, or
at a boundary" for a simple password checker now is the exact same
discipline you will need later to build agent tools that fail safely and
predictably instead of crashing or behaving unpredictably on real-world
input.
