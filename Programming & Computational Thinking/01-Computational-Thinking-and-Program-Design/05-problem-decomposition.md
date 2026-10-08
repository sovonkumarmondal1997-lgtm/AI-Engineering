# Problem Decomposition

## Why this topic matters

Beginners often try to solve a whole problem in one long, tangled block of
code. This works for tiny programs, but quickly falls apart as problems
grow: the code becomes hard to read, hard to test, and terrifying to
change. **Decomposition** is the skill of breaking one large problem into
several small, clearly named responsibilities — usually functions — each
doing one clear, cohesive responsibility well. This is one of the most valuable habits in all
of software engineering, and it is built directly on the abstraction idea
from the previous topic.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain why breaking a large task into small functions makes code easier
  to write, test, and fix.
- Identify separate responsibilities inside a plain-English problem.
- Give each responsibility a small function with a single, clear purpose
  and a meaningful name.
- Combine several small functions into a complete working program.

## Prerequisites

- [Sequence, Selection, Iteration, and Abstraction](04-sequence-selection-iteration-and-abstraction.md)

## Key terms

| Term | Plain-English definition |
|---|---|
| **Decomposition** | Breaking one large problem into several smaller, more manageable parts. |
| **Responsibility** | One clear job that a piece of code (usually a function) is in charge of, and nothing more. |
| **Single responsibility** | The idea that a function should have one clear, cohesive responsibility, so its name can honestly describe what it does. |
| **Composition (of functions)** | Building a bigger behavior by calling several small functions together. |
| **Coupling** | How much one piece of code depends on another; clear boundaries, well-defined inputs, and return values can help reduce unwanted coupling. |

## Step-by-step explanation

### 1. Why "one giant block of code" becomes a problem

Imagine writing a 40-line script that reads expenses, validates them,
calculates totals, and prints a report — all in one unbroken sequence of
statements with no functions. It works, but:

- To find a specific piece of logic (say, "how is the total calculated?"),
  you have to read the whole thing.
- To test just the calculation, you have to run the entire script,
  including the reading and printing parts.
- To reuse just the validation logic somewhere else, you'd have to copy and
  paste lines out of the middle of the script.
- A single typo or bug anywhere in the block can silently affect
  everything around it.

### 2. Decomposition: splitting one problem into small responsibilities

**Decomposition** means looking at a big task and asking: "What are the
separate jobs happening here?" For the expense script above, you might spot:

1. Reading/collecting the raw expense data.
2. Validating that each expense is a sensible value.
3. Calculating the total and the average.
4. Formatting and printing a report.

Each of these could become its own small function. This mirrors the
**Input → Process → Output** model from
[topic 3](03-input-process-output.md): decomposition is really the same
idea applied at a larger scale, where the "process" step itself gets
broken down into multiple smaller processes.

### 3. Giving each responsibility a function with one clear job

The goal is **single responsibility**: each function should have one
clear, cohesive responsibility, and its name should describe it accurately,
with no unrelated "and" hiding in the description. `calculate_total_and_print_report` is
doing two jobs and should probably be two functions:
`calculate_total` and `print_report`.

A useful warning sign: if you cannot describe what a function does in one
short sentence without using the word "and" to join two unrelated actions,
it is probably doing too much. This is a heuristic, not a strict rule.

### 4. Composing small functions into a full program

Once each responsibility has its own function, the main part of your
program becomes short and readable: it just calls the functions in the
right order, passing the result of one into the next. Combining small
functions by calling them together to build larger behavior is a simple
form of **composition**. This is related to the sequence idea from
[topic 4](04-sequence-selection-iteration-and-abstraction.md), where
operations are performed in an intentional order, just applied to functions
instead of individual statements.

### 5. A practical way to decompose: nouns and verbs

A simple, beginner-friendly starting heuristic: read the plain-English
problem description and underline the **verbs** (actions) — each verb is a
possible candidate for a function. Underline the **nouns** (things) — each
noun is a possible candidate for a variable or a piece of data passed
between functions. It still takes judgment to decide which ones really
deserve their own function. For "read expenses, validate each one, calculate the total, and
print a summary," the verbs (`read`, `validate`, `calculate`, `print`) map
almost directly onto the four functions from step 2.

## Examples

### Example 1 — One small responsibility

```python
def total_of(expenses):
    total = 0
    for expense in expenses:
        total = total + expense
    return total


expenses = [12, 45, 9, 20]
print(total_of(expenses))
```

**Plain-English explanation:**

- `total_of(expenses)` has exactly one responsibility: given a list of
  numbers, add them up and return the result. Its name (`total_of`)
  honestly describes everything it does — nothing more, nothing less.
- Inside, it uses the running-total pattern from earlier topics.
- Because this function does only one thing, it is easy to test on its
  own (`total_of([1, 2, 3])` should return `6`), and trivial to reuse
  anywhere a total is needed, without dragging along any input or output
  logic.

### Example 2 — Two responsibilities, kept separate

```python
def total_of(expenses):
    total = 0
    for expense in expenses:
        total = total + expense
    return total


def average_of(expenses):
    if len(expenses) == 0:
        return 0
    return total_of(expenses) / len(expenses)


def describe_spending(expenses):
    total = total_of(expenses)
    average = average_of(expenses)
    return "Total: " + str(total) + ", Average: " + str(average)


expenses = [12, 45, 9, 20]
print(describe_spending(expenses))
```

**Plain-English explanation:**

- `total_of` is unchanged from Example 1 — one responsibility, kept intact.
- `average_of(expenses)` has its own single responsibility: compute the
  average, guarding against dividing by zero when the list is empty (this
  guard is a small preview of
  [topic 6](06-preconditions-postconditions-and-edge-cases.md)). For this
  example, an empty list is assigned an average of `0` as a simple
  application policy so the function has a defined result; this is a design
  choice, not the mathematical average of an empty collection. Notice it
  **reuses** `total_of` rather than recalculating the sum itself — this is
  composition: a new function built partly out of an existing one, instead
  of duplicating logic.
- `describe_spending(expenses)` has yet another responsibility: formatting
  a human-readable message. It calls the other two functions to get the
  numbers it needs, then focuses only on building the text. `str(total)`
  and `str(average)` convert numbers into text so they can be joined with
  `+` onto other text, the opposite conversion direction from
  [topic 3](03-input-process-output.md)'s `int(...)`/`float(...)`.
- If the way totals are calculated ever needs to change, you only need to
  fix it in `total_of` — `average_of` and `describe_spending` will
  use the updated logic when they call `total_of`, because they reuse that
  function rather than duplicating the logic. This is the direct payoff of decomposition.

### Example 3 — A small decomposed program: password checker report

This example decomposes a slightly bigger problem — checking a list of
passwords against several rules and reporting the results — into four
small functions, each with one job, then composes them into a short main
sequence.

```python
def has_minimum_length(password):
    return len(password) >= 8


def has_a_digit(password):
    for character in password:
        if character.isdigit():
            return True
    return False


def check_password(password):
    if not has_minimum_length(password):
        return "too short"
    if not has_a_digit(password):
        return "needs a digit"
    return "OK"


def print_password_report(passwords):
    for password in passwords:
        result = check_password(password)
        print(password, "->", result)


passwords_to_check = ["hunter2", "abc", "correcthorsebattery9"]
print_password_report(passwords_to_check)
```

**Plain-English explanation:**

- `has_minimum_length(password)` and `has_a_digit(password)` are small,
  independent checks, each with one job. `has_a_digit` loops through every
  character in the password and returns `True` the moment it finds a digit
  (using the built-in `.isdigit()` check on a single character); if the
  loop finishes without finding one, it returns `False`.
- `check_password(password)` **composes** the two smaller checks into a
  single decision: it doesn't know or care *how* each check works
  internally, only *what* each one tells it (`True` or `False`). Its own
  responsibility is purely the decision logic — which rule fails first, or
  whether the password is fine.
- `print_password_report(passwords)` has its own separate responsibility:
  looping over a list and printing one line per password, using
  `check_password` to get each result. It contains no rule logic at all —
  if a new rule were added to `check_password`, `print_password_report`
  would not need to change.
- Running the code on the three example passwords produces:
  `hunter2 -> too short`, `abc -> too short`, and
  `correcthorsebattery9 -> OK`. Trace through each one yourself to confirm
  you understand why.
- Notice each function could be tested completely on its own (for example,
  calling `has_a_digit("abc")` directly should return `False`), which
  would be far harder if all this logic were mashed into a single
  40-line block.

## Common beginner mistakes

- **Writing one giant function that does everything.** This is the exact
  problem decomposition solves; if you notice a function description needs
  the word "and" to cover unrelated actions, split it.
- **Over-decomposing trivially small logic.** Creating a separate function
  for a single, one-line calculation used only once can sometimes add more
  complexity than it removes. Decomposition is a judgment call: aim for
  responsibilities that are genuinely separate ideas, not just an
  arbitrary line count.
- **Giving functions vague names** like `process()`, `handle()`, or
  `doStuff()`. A function name should describe exactly what it does; if
  you cannot summarize it clearly, the function may be doing too much (or
  you don't yet understand its job well enough to build it).
- **Letting functions quietly depend on details of other functions'
  internals**, instead of only on their inputs and return values. This
  creates unwanted **coupling**: changing one function's internal
  implementation shouldn't ever require changing another function that
  merely calls it.

## Try it yourself

1. Take the following plain-English problem and list the separate
   responsibilities you would turn into functions, before writing any
   code: "Read a list of exam scores, work out how many students passed
   (60 or above), calculate the class average, and print a short report."
2. Implement the functions you listed in step 1, then compose them into a
   short main sequence that prints the report.
3. Look back at Example 3 in
   [topic 4](04-sequence-selection-iteration-and-abstraction.md)
   (`is_password_long_enough` and `count_signs`). Add a third small,
   separate function of your own — for example, one that checks whether a
   password contains no spaces — and compose it into `check_password`
   from this topic's Example 3.
4. Take any one function you have written so far in this module and try to
   describe its job in a single sentence without using the word "and." If
   you cannot, decide how you would split it, and write the split version.

## Summary

- **Decomposition** means breaking a large problem into smaller, clearly
  separated **responsibilities**, usually implemented as functions.
- Each function should follow **single responsibility**: do one job, and
  have a name that accurately and fully describes that job.
- Small functions can be **composed** — called together in sequence — to
  build up more complex behavior, without duplicating logic.
- Good decomposition makes code easier to read, test, reuse, and fix,
  because a change or a bug is usually confined to one small, well-named
  place.
- Decomposition is a judgment skill, not a strict formula — the nouns/verbs
  technique is a useful starting point for spotting responsibilities.

## Completion checklist

- [ ] I can look at a plain-English problem and list its separate
      responsibilities before writing any code.
- [ ] I can write a function whose job I can describe in one sentence
      without using "and."
- [ ] I have composed at least two small functions together into a working
      program, where one function calls another.
- [ ] I can explain, using my own example, why splitting logic into
      functions made a change or a test easier.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

Agent systems are, at their heart, a collection of small, single-purpose
"tools" (functions) that an AI model decides how and when to call, plus a
small amount of logic composing those tools into a full task. If your
tools are not decomposed cleanly — each with one clear job, a clear input,
and a clear output — an agent cannot reliably decide which tool to use, and
you cannot test or trust any individual piece of the system. The
discipline you are building here, breaking a password checker or an
expense report into small, well-named functions, is exactly the discipline
that later makes an agent's tools understandable, testable, and safe to
compose.
