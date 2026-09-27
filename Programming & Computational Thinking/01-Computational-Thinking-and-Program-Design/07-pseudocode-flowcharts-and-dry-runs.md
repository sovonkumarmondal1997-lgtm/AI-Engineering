# Pseudocode, Flowcharts, and Dry Runs

## Why this topic matters

The biggest difference between a beginner who struggles with every new
problem and one who solves problems confidently is usually not talent — it
is a habit: **thinking through a solution before typing any code, and
checking it by hand before trusting it.** This lesson teaches three
concrete tools for doing that: **pseudocode** (writing your plan in
simple, structured English), **flowcharts** (a simple text-based picture of
the steps and decisions), and **dry runs** (manually tracing what a
program does, step by step, using pen and paper or a notes file). These
tools cost only a few minutes but save far more time than they take,
because they catch mistakes in your thinking before those mistakes become
bugs in your code.

## Learning outcomes

By the end of this lesson, you will be able to:

- Write clear pseudocode for a small problem, before writing Python.
- Draw a simple text-based flowchart showing steps and decisions.
- Perform a dry run of a piece of code by hand, tracking variable values
  line by line.
- Use dry runs to find a bug without running the program.

## Prerequisites

- [Sequence, Selection, Iteration, and Abstraction](04-sequence-selection-iteration-and-abstraction.md)
- [Preconditions, Postconditions, and Edge Cases](06-preconditions-postconditions-and-edge-cases.md)

## Key terms

| Term | Plain-English definition |
|---|---|
| **Pseudocode** | A plan for a program written in plain, structured English (or a mix of English and code-like phrases), without worrying about exact programming syntax. |
| **Flowchart** | A diagram (here, drawn with plain text and arrows) that shows the steps of an algorithm and the decisions between them. |
| **Dry run** | Manually tracing through code line by line, writing down the value of each variable as it changes, without running it on a computer. |
| **Trace table** | A simple table used during a dry run, with one column per variable, and one row per step, to track how values change. |

## Step-by-step explanation

### 1. Why plan before coding?

Jumping straight into code often means solving the "how do I write this in
Python" problem and the "what is the actual logic" problem at the same
time, which is harder than solving them one at a time. Planning first
(with pseudocode and, if useful, a flowchart) lets you focus purely on the
logic, in a form that is quick to change your mind about, before you've
invested time in exact Python syntax.

### 2. Writing pseudocode

**Pseudocode** describes the steps of an algorithm in plain language, using
a loose, consistent structure, without worrying about Python's exact
rules (no colons required, no exact function syntax). A simple style, used
throughout this lesson, looks like this:

```text
START
  SET total TO 0
  FOR EACH expense IN expenses
    ADD expense TO total
  END FOR
  RETURN total
END
```

Notice this pseudocode reads almost like the Python it will become, but is
easier to sketch quickly, cross out, and rewrite, because you are not
fighting Python's exact grammar rules while you're still deciding on the
logic itself.

### 3. Drawing a simple text-based flowchart

A **flowchart** shows the same plan as a diagram: boxes for steps, diamond
shapes (described in text here) for decisions, and arrows for the order
things happen in. Since this lesson stays within plain text (no drawing
tools), a flowchart can be written using simple ASCII arrows and labels:

```text
[Start]
   |
   v
[Set total = 0]
   |
   v
[For each expense in expenses] <---------+
   |                                     |
   v                                     |
[Add expense to total] ------------------+
   |
   v
(all expenses processed)
   |
   v
[Return total]
   |
   v
[End]
```

The loop is shown by the arrow that curves back up to "For each expense" —
this is exactly the repeating behavior of a `for` loop. Flowcharts are most
useful for problems with several decision branches, where seeing the shape
of the branching helps you spot a missing or wrong path before you code
it.

### 4. Dry runs: tracing code by hand

A **dry run** means going through code line by line, as if you were the
computer, and writing down what each variable holds after each statement
runs. This is usually done with a simple **trace table**: one column per
variable of interest, one row per statement. Dry runs are extremely
effective for two purposes: predicting what unfamiliar code will do before
running it (part of the engineering loop in the module
[README](README.md)), and finding a bug by comparing what you *expected*
each variable to be against what a print statement (or the debugger, later
in Module 1.7) shows it actually is.

## Examples

### Example 1 — Pseudocode and Python side by side

**Problem:** Given a list of numbers, count how many are greater than 10.

**Pseudocode:**

```text
START
  SET count TO 0
  FOR EACH number IN numbers
    IF number > 10
      ADD 1 TO count
    END IF
  END FOR
  RETURN count
END
```

**Python:**

```python
def count_greater_than_10(numbers):
    count = 0
    for number in numbers:
        if number > 10:
            count = count + 1
    return count


print(count_greater_than_10([5, 15, 8, 20, 10]))
```

**Plain-English explanation:**

- Every line of the pseudocode maps almost directly onto one line of
  Python: `SET count TO 0` becomes `count = 0`; `FOR EACH number IN
  numbers` becomes `for number in numbers:`; `IF number > 10` becomes
  `if number > 10:`; `ADD 1 TO count` becomes `count = count + 1`;
  `RETURN count` becomes `return count`.
- This close mapping is exactly the point of writing pseudocode this way:
  it lets you settle *what* the algorithm should do, in a form that is
  easy to change, before worrying about Python's exact syntax rules (the
  colons, the indentation, the exact operator symbols).
- Running the Python version on `[5, 15, 8, 20, 10]` counts `15` and `20`
  as greater than 10 (`10` itself is not, since the condition is strictly
  `> 10`, not `>= 10`), giving a final result of `2`.

### Example 2 — A dry run using a trace table

Take this small, deliberately tricky piece of code and trace it by hand
**before** running it:

```python
total = 0
count = 0
for number in [4, 7, 2, 9]:
    total = total + number
    count = count + 1
    if number > 5:
        total = total + 1

average = total / count
print(average)
```

**Dry run (trace table):**

| Step | `number` | `total` | `count` | notes |
|---|---|---|---|---|
| start | — | 0 | 0 | before the loop begins |
| 1 | 4 | 4 | 1 | `4 > 5` is False, no bonus added |
| 2 | 7 | 11 | 2 | `7 + 4 = 11`; `7 > 5` is True, so `+1` bonus: `total` becomes `12` |
| 2 (bonus) | 7 | 12 | 2 | the `if` block adds 1 because `number > 5` |
| 3 | 2 | 14 | 3 | `12 + 2 = 14`; `2 > 5` is False, no bonus |
| 4 | 9 | 23 | 4 | `14 + 9 = 23`; `9 > 5` is True, so `+1` bonus: `total` becomes `24` |
| 4 (bonus) | 9 | 24 | 4 | the `if` block adds 1 because `number > 5` |
| after loop | — | 24 | 4 | loop has finished |

**Plain-English explanation:**

- Each row of the trace table represents the state of the important
  variables (`number`, `total`, `count`) right after one statement runs.
  Working through this by hand, one line of code at a time, is exactly
  what a dry run means.
- The tricky part of this example is the `if number > 5: total = total +
  1` line inside the loop — it's easy to skim past this while reading and
  assume `total` only ever gets the plain sum of the numbers. The dry run
  makes it impossible to skip: you can clearly see `total` gets an extra
  `+1` bonus each time a number is greater than 5 (which happens for `7`
  and `9` in this list).
- After the loop finishes, `total` is `24` and `count` is `4`, so
  `average = total / count` computes `24 / 4 = 6.0`.
- If you had only glanced at the code and guessed the average of
  `[4, 7, 2, 9]` (which is `22 / 4 = 5.5`), you would have been wrong,
  because you'd have missed the bonus logic. This is exactly why dry runs
  matter: they force you to account for every single line's effect,
  instead of skimming and guessing.

### Example 3 — Using a dry run to find a bug

This example shows the real payoff: using a dry run to find a bug in code
that looks correct at a glance, connecting back to the
source-code-versus-runtime-behavior idea from
[topic 1](01-algorithms-programs-and-data.md).

```python
def count_positive_and_negative(numbers):
    positive_count = 0
    negative_count = 0
    for number in numbers:
        if number > 0:
            positive_count = positive_count + 1
        if number < 0:
            positive_count = positive_count + 1
    return positive_count, negative_count


print(count_positive_and_negative([3, -1, 5, -2, 0]))
```

**Dry run (trace table), tracking `number`, `positive_count`, and `negative_count`:**

| Step | `number` | `positive_count` | `negative_count` | expected `negative_count` |
|---|---|---|---|---|
| start | — | 0 | 0 | 0 |
| 1 | 3 | 1 | 0 | 0 |
| 2 | -1 | 2 | 0 | 1 |
| 3 | 5 | 3 | 0 | 1 |
| 4 | -2 | 4 | 0 | 2 |
| 5 | 0 | 4 | 0 | 2 |

**Plain-English explanation:**

- The pseudocode intention is clear: count positives in one counter and
  negatives in a separate counter. Reading the code quickly, it *looks*
  like it does that, because there are two separate `if` statements.
- Doing the dry run, tracking each variable after every statement, reveals
  the bug immediately: the second `if number < 0:` block also increases
  `positive_count`, not `negative_count`. This is a simple typo (the
  wrong variable name was used on the right side of the second `if`
  block), but it is exactly the kind of mistake that is easy to miss just
  by reading, and very easy to catch with a careful, line-by-line dry run.
- The "expected `negative_count`" column shows what the value *should* be
  at each step if the code were correct, based on the plain-English intent
  ("count negatives"). Comparing the actual traced value against the
  expected value at each step is precisely how a dry run finds a bug:
  the moment the two columns disagree (right at step 2, where `-1` should
  make `negative_count` become `1` but it stays `0`), you have located the
  exact line responsible.
- The fix is a one-word change: `negative_count = negative_count + 1`
  inside the second `if` block. This example demonstrates the whole
  point of this lesson: a careful dry run found a real bug **before
  running the program at all**, using nothing but pen, paper, and
  patience.

## Common beginner mistakes

- **Skipping pseudocode for anything but the simplest programs**, and then
  getting lost translating a half-formed idea directly into Python syntax.
- **Drawing a flowchart or writing pseudocode that is vague** ("do the
  calculation") instead of precise ("add each expense to a running
  total"). Vague pseudocode hides exactly the kind of thinking mistakes it
  is meant to catch.
- **Dry-running code too fast, skipping steps.** The value of a dry run
  comes from being slow and mechanical — writing down every single
  variable's value after every single statement, not just "the important
  ones" (as Example 3 shows, an "unimportant" variable can be exactly
  where the bug is hiding).
- **Only dry-running the normal case.** Just like testing, dry runs should
  sometimes be done on edge cases too (an empty list, a boundary value)
  to see whether the logic still behaves as expected.

## Try it yourself

1. Write pseudocode (using the `START` / `SET` / `FOR EACH` / `IF` /
   `RETURN` / `END` style from Example 1) for a function that returns the
   largest number in a list, without using Python's built-in `max()`.
   Only after the pseudocode looks right to you, translate it into Python.
2. Draw a text-based flowchart (using boxes and arrows, like the one in
   step 3 above) for a program that asks a user for a password and prints
   whether it is at least 8 characters long.
3. Perform a full dry run, using a trace table, of the following code, and
   predict its final printed output before running it to check:
   ```python
   values = [1, 2, 3, 4]
   result = 0
   for value in values:
       if value % 2 == 0:
           result = result + value
       else:
           result = result - value
   print(result)
   ```
4. This code has a bug. Do a dry run first, using a trace table, to find
   it — do not run the code until after you've found the bug by hand:
   ```python
   def count_words_longer_than(words, minimum_length):
       count = 0
       for word in words:
           if len(word) > minimum_length:
               count = count
       return count
   ```

## Summary

- **Pseudocode** lets you plan an algorithm's logic in plain, structured
  language before worrying about Python's exact syntax.
- A **flowchart** is a simple diagram of the steps and decisions in an
  algorithm, useful especially when there is meaningful branching.
- A **dry run** means manually tracing code, statement by statement,
  writing down how each variable's value changes, usually with a
  **trace table**.
- Dry runs are one of the most reliable ways to predict what code will do,
  and to find bugs, without needing to run the program at all.
- These tools are cheap (a few minutes with pen and paper) and catch
  mistakes early, before they become confusing runtime bugs.

## Completion checklist

- [ ] I have written pseudocode for a problem before writing the Python
      code for it.
- [ ] I have drawn a simple text-based flowchart for a problem with at
      least one decision.
- [ ] I have performed a dry run using a trace table and correctly
      predicted a program's output before running it.
- [ ] I have used a dry run to find a bug in code, without running it
      first.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

When you design an AI agent's decision loop or a multi-step tool workflow,
you will almost always sketch it first as pseudocode or a flowchart of
"what happens, in what order, and what decisions get made" — long before
any AI model is wired in. And when an agent produces an unexpected result,
the very first debugging step professionals use is the same dry-run habit
you practiced here: trace the sequence of steps and state changes by hand,
compare it against what should have happened, and find exactly where
reality and expectation diverge.
